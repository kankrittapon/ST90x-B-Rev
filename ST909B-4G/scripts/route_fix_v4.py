# Route v4: targeted patch — delete broken v3 items only, add corrected routes.
# Fixes (from v3 DRC triage):
#  - GPS_TX: F lane y=30.8 (clear of USB_DP_M x=21.16 vertical + USB_DM_M x=20.7 wall), via (22.25,30.8)
#  - GPS_RX: TP2 F drop x=9.5 to via (9.5,53.8); TP3 F at x=2.95 (clears U6/1 pad gap 0.245);
#            B lane y=33.0 with west vertical x=2.25 (hugs keepout west edge), jog y=30.1 clears TX via 0.275
#  - LED_GPS: F trunk x=23.7 (clears LED_EN via 0.225, LED_CHR jog 1.55, 4G_RXD 9.3)
#  - LED_CHR: jog at y=28.0 (south of J7/1 pad) instead of y=23.0/24.5 (crossed LED_GPS F trunk)
import pcbnew

PATH = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
W = 0.25
LAYER = {"F": pcbnew.F_Cu, "B": pcbnew.B_Cu}

DEL_TRACKS = [
    # GPS_TX all v3
    ("/GPS_TX", "F", (7, 37, 7.5, 37)), ("/GPS_TX", "F", (7.5, 37, 7.5, 44.0)),
    ("/GPS_TX", "F", (7.5, 44.0, 8.3, 44.0)), ("/GPS_TX", "F", (8.3, 44.0, 8.3, 54.5)),
    ("/GPS_TX", "F", (8.3, 54.5, 20.5, 54.5)),
    ("/GPS_TX", "B", (20.5, 54.5, 22.25, 54.5)), ("/GPS_TX", "B", (22.25, 54.5, 22.25, 56.75)),
    ("/GPS_TX", "B", (22.25, 56.75, 21.16, 56.75)),
    # GPS_RX all v3
    ("/GPS_RX", "F", (9.5, 37, 20.7, 37)), ("/GPS_RX", "F", (20.7, 37, 20.7, 53.5)),
    ("/GPS_RX", "F", (20.7, 53.5, 20.5, 53.5)),
    ("/GPS_RX", "F", (3, 60, 3.4, 60)), ("/GPS_RX", "F", (3.4, 60, 3.4, 34.5)),
    ("/GPS_RX", "F", (3.4, 34.5, 7.5, 34.5)),
    ("/GPS_RX", "B", (20.5, 53.5, 23.55, 53.5)),
    ("/GPS_RX", "B", (7.5, 34.5, 7.5, 33.0)), ("/GPS_RX", "B", (7.5, 33.0, 23.55, 33.0)),
    ("/GPS_RX", "B", (23.55, 33.0, 23.55, 57.25)), ("/GPS_RX", "B", (23.55, 57.25, 21.16, 57.25)),
    # LED_GPS all v3
    ("/LED_GPS", "B", (21.16, 61.25, 25.65, 61.25)),
    ("/LED_GPS", "F", (25.65, 61.25, 25.65, 11.4)), ("/LED_GPS", "F", (25.65, 11.4, 11.71, 11.4)),
    ("/LED_GPS", "B", (11.71, 11.4, 11.71, 13.0)),
    # LED_CHR v3 jog (wrong side of J7/1)
    ("/LED_CHR", "F", (26.3, 67.6, 26.3, 23.0)), ("/LED_CHR", "F", (26.3, 23.0, 25.5, 23.0)),
    ("/LED_CHR", "F", (25.5, 23.0, 25.5, 24.5)), ("/LED_CHR", "F", (25.5, 24.5, 26.3, 24.5)),
    ("/LED_CHR", "F", (26.3, 24.5, 26.3, 15.45)),
]
DEL_VIAS = [
    ("/GPS_TX", 20.5, 54.5),
    ("/GPS_RX", 20.5, 53.5), ("/GPS_RX", 7.5, 34.5),
    ("/LED_GPS", 25.65, 61.25), ("/LED_GPS", 11.71, 11.4),
]

ROUTES = [
    ("/GPS_TX", W, [
        ("F", [(7, 37), (7.9, 37), (7.9, 30.8), (22.25, 30.8)]),
        ("B", [(22.25, 30.8), (22.25, 56.75), (21.16, 56.75)]),
    ]),
    ("/GPS_RX", W, [
        ("F", [(9.5, 37), (9.5, 53.8)]),
        ("F", [(3, 60), (2.95, 60), (2.95, 34.5), (7.0, 34.5)]),
        ("B", [(9.5, 53.8), (2.25, 53.8), (2.25, 33.0), (20.3, 33.0), (20.3, 30.1),
               (23.55, 30.1), (23.55, 57.25), (21.16, 57.25)]),
    ]),
    ("/LED_GPS", W, [
        ("B", [(21.16, 61.25), (23.7, 61.25)]),
        ("F", [(23.7, 61.25), (23.7, 11.4), (11.71, 11.4)]),
        ("B", [(11.71, 11.4), (11.71, 13.0)]),
    ]),
    ("/LED_CHR", W, [
        ("F", [(26.3, 67.6), (26.3, 28.0), (25.5, 28.0), (25.5, 23.0), (26.3, 23.0), (26.3, 15.45)]),
    ]),
]
ADD_VIAS = [
    ("/GPS_TX", 22.25, 30.8),
    ("/GPS_RX", 9.5, 53.8), ("/GPS_RX", 7.0, 34.5),
    ("/LED_GPS", 23.7, 61.25), ("/LED_GPS", 11.71, 11.4),
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
    v.SetNetCode(nc(net))
    b.Add(v)
    va += 1

for z in b.Zones():
    try:
        z.UnFill()
    except Exception:
        z.SetIsFilled(False)
pcbnew.SaveBoard(PATH, b)
print(f"deleted {nd} tracks + {vd} vias; added {na} tracks + {va} vias; saved (zones unfilled)")
