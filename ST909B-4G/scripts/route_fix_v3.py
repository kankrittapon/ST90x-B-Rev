# Route v3: targeted patch — delete only broken v2 items, add corrected routes.
# Key fixes: GPS_TX/GPS_RX rerouted around U4 top pads + R1/R2; M3V3 B tail trimmed;
# USB_DP_M via moved to (22.40,58.45); LED_GPS F-hop around SOS/4G_RXD walls;
# LED_CHR jog around J7/1; LED_K stubs; 1 GND stitch via.
import pcbnew

PATH = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
W = 0.25
LAYER = {"F": pcbnew.F_Cu, "B": pcbnew.B_Cu}

DEL_TRACKS = [
    ("/GPS_TX", "F", (7, 37, 7.5, 37)), ("/GPS_TX", "F", (7.5, 37, 7.5, 54.9)),
    ("/GPS_TX", "B", (7.5, 54.9, 23.05, 54.9)), ("/GPS_TX", "B", (23.05, 54.9, 23.05, 56.75)),
    ("/GPS_TX", "B", (23.05, 56.75, 21.16, 56.75)),
    ("/GPS_RX", "F", (9.5, 36.0, 9.5, 54.2)), ("/GPS_RX", "F", (3, 60, 2.9, 60)),
    ("/GPS_RX", "F", (2.9, 60, 2.9, 59.0)),
    ("/GPS_RX", "B", (2.9, 59.0, 2.9, 54.2)), ("/GPS_RX", "B", (2.9, 54.2, 23.7, 54.2)),
    ("/GPS_RX", "B", (23.7, 54.2, 23.7, 57.25)), ("/GPS_RX", "B", (23.7, 57.25, 21.16, 57.25)),
    ("/USB_DP_M", "F", (21.16, 57.75, 22.9, 57.75)), ("/USB_DP_M", "B", (22.9, 57.75, 21.16, 57.75)),
    ("/LED_GPS", "B", (21.16, 61.25, 32.9, 61.25)), ("/LED_GPS", "B", (32.9, 61.25, 32.9, 11.4)),
    ("/LED_GPS", "B", (32.9, 11.4, 11.71, 11.4)), ("/LED_GPS", "B", (11.71, 11.4, 11.71, 13.0)),
    ("/LED_CHR", "F", (26.3, 67.6, 26.3, 15.45)),
    ("/M3V3", "B", (17.0, 55.7, 23.0, 55.7)),
]
DEL_VIAS = [
    ("/GPS_TX", 7.5, 54.9), ("/GPS_RX", 2.9, 59.0), ("/GPS_RX", 9.5, 54.2),
    ("/GPS_RX", 23.7, 57.25), ("/USB_DP_M", 22.9, 57.75), ("/LED_GPS", 32.9, 61.25),
]

ROUTES = [
    ("/GPS_TX", W, [
        ("F", [(7, 37), (7.5, 37), (7.5, 44.0), (8.3, 44.0), (8.3, 54.5), (20.5, 54.5)]),
        ("B", [(20.5, 54.5), (22.25, 54.5), (22.25, 56.75), (21.16, 56.75)]),
    ]),
    ("/GPS_RX", W, [
        ("F", [(9.5, 37), (20.7, 37), (20.7, 53.5), (20.5, 53.5)]),   # TP2
        ("F", [(3, 60), (3.4, 60), (3.4, 34.5), (7.5, 34.5)]),        # TP3
        ("B", [(20.5, 53.5), (23.55, 53.5)]),
        ("B", [(7.5, 34.5), (7.5, 33.0), (23.55, 33.0)]),
        ("B", [(23.55, 33.0), (23.55, 57.25), (21.16, 57.25)]),
    ]),
    ("/USB_DP_M", W, [
        ("F", [(21.16, 57.75), (21.16, 58.45), (22.40, 58.45)]),
        ("B", [(22.40, 58.45), (22.40, 57.75), (21.16, 57.75)]),
    ]),
    ("/LED_GPS", W, [
        ("B", [(21.16, 61.25), (25.65, 61.25)]),
        ("F", [(25.65, 61.25), (25.65, 11.4), (11.71, 11.4)]),
        ("B", [(11.71, 11.4), (11.71, 13.0)]),
    ]),
    ("/LED_CHR", W, [
        ("F", [(26.3, 67.6), (26.3, 23.0), (25.5, 23.0), (25.5, 24.5), (26.3, 24.5), (26.3, 15.45)]),
    ]),
    ("/LED_K", W, [
        ("B", [(16.29, 12.0), (16.29, 13.0)]),
        ("B", [(19.29, 12.0), (19.29, 13.0)]),
    ]),
    ("/M3V3", W, [("B", [(17.0, 55.7), (21.16, 55.7)])]),
]
ADD_VIAS = [
    ("/GPS_TX", 20.5, 54.5), ("/GPS_RX", 20.5, 53.5), ("/GPS_RX", 7.5, 34.5),
    ("/USB_DP_M", 22.40, 58.45), ("/LED_GPS", 25.65, 61.25), ("/LED_GPS", 11.71, 11.4),
    ("/GND", 22.0, 45.0),
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


# 1) delete broken tracks (match net + layer + endpoints either direction)
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

# 2) add corrected tracks/vias
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

# 3) zones: clear stale fills (refill runs in a separate process)
for z in b.Zones():
    try:
        z.UnFill()
    except Exception:
        z.SetIsFilled(False)
pcbnew.SaveBoard(PATH, b)
print(f"deleted {nd} tracks + {vd} vias; added {na} tracks + {va} vias; saved (zones unfilled)")
