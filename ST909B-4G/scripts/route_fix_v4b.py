# Route v4b: fix the 4 remaining v4 errors.
#  1. clearance TP4/1 (east edge 2.80) vs GPS_RX F vertical x=2.95 (gap 0.025)
#     -> jog: x=2.95 down to y=50.5, over to x=3.2 (clears TP4 by 0.275), up into TP3 pad (same net).
#  2. unconnected GPS_RX via (7.0,34.5): B lane is at y=33.0 -> add B stub (7.0,34.5)-(7.0,33.0).
#  3. starved_thermal U4/2: pad2 (x 20.4255..21.9005) had only a W spoke (GPS_TX B vertical x=22.25
#     blocked E fill: gap 0.2245 < 0.4). Move GPS_TX via+vertical to x=22.9 -> E fill sliver
#     x 22.1005..22.575 -> 2 spokes. (Via east edge 23.2 clears GPS_RX vertical 23.425 by 0.225.)
#  4. Zone GND B x F unconnected + mystery /GPS_TX via at (22.0,45.0) (dangling, overlaps B vertical):
#     delete it; add /GND stitches (16.5,58.5) [U4 interior island <-> F] and (29.5,45.0) [main F<->B].
import pcbnew

PATH = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
W = 0.25
LAYER = {"F": pcbnew.F_Cu, "B": pcbnew.B_Cu}

DEL_TRACKS = [
    ("/GPS_RX", "F", (3, 60, 2.95, 60)), ("/GPS_RX", "F", (2.95, 60, 2.95, 34.5)),
    ("/GPS_TX", "F", (7.9, 30.8, 22.25, 30.8)),
    ("/GPS_TX", "B", (22.25, 30.8, 22.25, 56.75)), ("/GPS_TX", "B", (22.25, 56.75, 21.16, 56.75)),
]
DEL_VIAS = [
    ("/GPS_TX", 22.0, 45.0),
    ("/GPS_TX", 22.25, 30.8),
]

ROUTES = [
    ("/GPS_RX", W, [
        ("F", [(2.95, 34.5), (2.95, 50.5), (3.2, 50.5), (3.2, 60.0)]),
        ("B", [(7.0, 34.5), (7.0, 33.0)]),
    ]),
    ("/GPS_TX", W, [
        ("F", [(7.9, 30.8), (22.9, 30.8)]),
        ("B", [(22.9, 30.8), (22.9, 56.75), (21.16, 56.75)]),
    ]),
]
ADD_VIAS = [
    ("/GPS_TX", 22.9, 30.8),
    ("/GND", 16.5, 58.5),
    ("/GND", 29.5, 45.0),
]

TOL = pcbnew.FromMM(0.06)
b = pcbnew.LoadBoard(PATH)
codes = {}


def nc(name):
    if name not in codes:
        n = b.FindNet(name)
        assert n, f"net {name} missing"
        codes[name] = n.GetNetCode()
    return codes[name]


def seg_match(t, net, lay, seg):
    if t.GetNetCode() != nc(net) or t.GetLayer() != LAYER[lay]:
        return False
    s, e = t.GetStart(), t.GetEnd()
    x1, y1, x2, y2 = (pcbnew.FromMM(v) for v in seg)
    return ((abs(s.x - x1) < TOL and abs(s.y - y1) < TOL and abs(e.x - x2) < TOL and abs(e.y - y2) < TOL) or
            (abs(s.x - x2) < TOL and abs(s.y - y2) < TOL and abs(e.x - x1) < TOL and abs(e.y - y1) < TOL))


nd = 0
for t in list(b.GetTracks()):
    if t.Type() != pcbnew.PCB_TRACE_T:
        continue
    for net, lay, seg in DEL_TRACKS:
        if seg_match(t, net, lay, seg):
            b.Delete(t)
            nd += 1
            break

vd = 0
for t in list(b.GetTracks()):
    if t.Type() != pcbnew.PCB_VIA_T:
        continue
    for net, x, y in DEL_VIAS:
        if (t.GetNetCode() == nc(net) and abs(t.GetPosition().x - pcbnew.FromMM(x)) < TOL
                and abs(t.GetPosition().y - pcbnew.FromMM(y)) < TOL):
            b.Delete(t)
            vd += 1
            break

na = 0
for net, width, polys in ROUTES:
    code = nc(net)
    for layer, pts in polys:
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(b)
            t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
            t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
            t.SetWidth(pcbnew.FromMM(width))
            t.SetLayer(LAYER[layer])
            t.SetNetCode(code)
            b.Add(t)
            na += 1

va = 0
for net, x, y in ADD_VIAS:
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    v.SetWidth(pcbnew.FromMM(0.6))
    v.SetDrill(pcbnew.FromMM(0.3))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    code = nc(net)
    v.SetNetCode(code)
    got = v.GetNetname()
    assert got == net, f"net mismatch at add: wanted {net}, got {got!r} (code {code})"
    b.Add(v)
    va += 1

for z in b.Zones():
    try:
        z.UnFill()
    except Exception:
        z.SetIsFilled(False)
pcbnew.SaveBoard(PATH, b)
print(f"deleted {nd} tracks + {vd} vias; added {na} tracks + {va} vias; saved (zones unfilled)")

# verify nets survive save+reload
b2 = pcbnew.LoadBoard(PATH)
bad = []
for t in b2.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T:
        p = t.GetPosition()
        mx, my = pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)
        for net, x, y in ADD_VIAS:
            if abs(mx - x) < 0.06 and abs(my - y) < 0.06 and t.GetNetname() != net:
                bad.append((net, x, y, t.GetNetname()))
print("via net check after reload:", "OK" if not bad else bad)
