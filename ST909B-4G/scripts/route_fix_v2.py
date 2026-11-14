# Route v2: delete ALL v1 tracks/vias (keep GPS_RF via 11.5,44), drop SH1 pad8,
# re-add corrected routes. Widths: signal 0.25, VBAT 0.3. GND = zones only.
import pcbnew

PATH = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
W = 0.25

ROUTES = [
    ("/VBAT", 0.3, [
        ("F", [(5, 67), (5, 65.0), (6.5, 65.0), (6.5, 44.5), (5.94, 44.5)]),
        ("B", [(5, 67), (5, 69.5), (33.3, 69.5), (33.3, 72.8), (22.5, 72.8), (22.5, 71.5)]),
    ]),
    ("/M3V3", W, [
        ("F", [(9.5, 62), (10.5, 62), (10.5, 55.7), (17.0, 55.7)]),
        ("B", [(5.5, 62), (9.5, 62)]),
        ("B", [(17.0, 55.7), (23.0, 55.7)]),
    ]),
    ("/GPS_TX", W, [
        ("F", [(7, 37), (7.5, 37), (7.5, 54.9)]),
        ("B", [(7.5, 54.9), (23.05, 54.9), (23.05, 56.75), (21.16, 56.75)]),
    ]),
    ("/GPS_RX", W, [
        ("F", [(9.5, 36.0), (9.5, 54.2)]),
        ("F", [(3, 60), (2.9, 60), (2.9, 59.0)]),          # TP3 branch
        ("B", [(2.9, 59.0), (2.9, 54.2), (23.7, 54.2), (23.7, 57.25), (21.16, 57.25)]),
    ]),
    ("/USB_DP_F", W, [("F", [(8.5, 40.5), (8.5, 31.8), (20.1, 31.8)])]),
    ("/USB_DM_F", W, [("F", [(10.5, 40.5), (10.5, 33.4), (20.1, 33.4)])]),
    ("/USB_DP_M", W, [
        ("F", [(20.1, 32.6), (21.16, 32.6), (21.16, 57.75), (22.9, 57.75)]),
        ("B", [(22.9, 57.75), (21.16, 57.75)]),
    ]),
    ("/USB_DM_M", W, [
        ("F", [(20.1, 34.2), (20.7, 34.2), (20.7, 58.0), (19.9, 58.0)]),
        ("B", [(19.9, 58.0), (19.9, 58.25), (21.16, 58.25)]),
    ]),
    ("/PKEY", W, [
        ("F", [(17.75, 71.5), (17.75, 57.875)]),
        ("B", [(17.75, 57.875), (17.75, 58.75), (21.16, 58.75)]),
        ("B", [(17.75, 70.4), (25.4, 70.4), (25.4, 71.5)]),  # TP8 branch
    ]),
    ("/SOS", W, [
        ("B", [(19.6, 8), (19.6, 10), (32.3, 10), (32.3, 59.1), (22.4, 59.1), (22.4, 59.25), (21.16, 59.25)]),
    ]),
    ("/LED_EN", W, [
        ("B", [(21.16, 59.75), (24.35, 59.75)]),
        ("F", [(24.35, 59.75), (24.35, 12.2)]),
        ("B", [(24.35, 12.2), (22.94, 12.2)]),
    ]),
    ("/LED_GPS", W, [
        ("B", [(21.16, 61.25), (32.9, 61.25), (32.9, 11.4), (11.71, 11.4), (11.71, 13.0)]),
    ]),
    ("/LED_4G", W, [
        ("B", [(19.25, 62.66), (19.25, 68.25), (25.0, 68.25)]),
        ("F", [(25.0, 68.25), (25.0, 14.65)]),
        ("B", [(25.0, 14.65), (17.71, 14.65), (17.71, 13.0)]),
    ]),
    ("/LED_CHR", W, [
        ("B", [(19.75, 62.66), (19.75, 67.6), (26.3, 67.6)]),
        ("F", [(26.3, 67.6), (26.3, 15.45)]),
        ("B", [(26.3, 15.45), (14.71, 15.45), (14.71, 13.0)]),
    ]),
    ("/BOOT", W, [
        ("B", [(18.75, 62.66), (18.75, 68.9), (34.0, 68.9), (34.0, 27.2), (33.0, 27.2)]),
        ("F", [(33.0, 27.2), (27.0, 27.2), (27.0, 25.5), (29.0, 25.5)]),
    ]),
    ("/4G_TXD_3V3", W, [("F", [(8.73, 71.5), (8.73, 73.05), (33.7, 73.05), (33.7, 32.05), (30.64, 32.05)])]),
    ("/4G_RXD_3V3", W, [("F", [(11.27, 71.5), (11.27, 72.6), (33.0, 72.6), (33.0, 33.0), (30.64, 33.0)])]),
    ("/LED_K", W, [("B", [(13.29, 13), (13.29, 12.0), (21.06, 12.0), (21.06, 13)])]),
]

VIAS = [
    ("/M3V3", 5.5, 62), ("/M3V3", 7.5, 62), ("/M3V3", 9.5, 62), ("/M3V3", 17.0, 55.7),
    ("/GPS_TX", 7.5, 54.9),
    ("/GPS_RX", 2.9, 59.0), ("/GPS_RX", 9.5, 54.2), ("/GPS_RX", 23.7, 57.25),
    ("/USB_DP_M", 22.9, 57.75), ("/USB_DM_M", 19.9, 58.0),
    ("/PKEY", 17.75, 57.875), ("/PKEY", 17.75, 70.4),
    ("/LED_EN", 24.35, 59.75), ("/LED_EN", 24.35, 12.2),
    ("/LED_4G", 25.0, 68.25), ("/LED_4G", 25.0, 14.65),
    ("/LED_CHR", 26.3, 67.6), ("/LED_CHR", 26.3, 15.45),
    ("/LED_GPS", 32.9, 61.25),
    ("/BOOT", 33.0, 27.2),
    ("/VBAT", 5.0, 67.0),
]

LAYER = {"F": pcbnew.F_Cu, "B": pcbnew.B_Cu}
b = pcbnew.LoadBoard(PATH)

# 1) delete all old tracks/vias except GPS_RF via at (11.5,44)
kept = 0
for t in list(b.GetTracks()):
    if (t.Type() == pcbnew.PCB_VIA_T and abs(t.GetPosition().x - pcbnew.FromMM(11.5)) < 1000
            and abs(t.GetPosition().y - pcbnew.FromMM(44.0)) < 1000):
        kept += 1
        continue
    b.Delete(t)

# 2) drop SH1 fence pad at (18.4, 66.4) (pad "8") -> BOOT lane x=18.75 free
fp = b.FindFootprintByReference("SH1")
removed_pads = []
for p in list(fp.Pads()):
    c = p.GetCenter()
    if abs(c.x / 1e6 - 18.4) < 0.01 and abs(c.y / 1e6 - 66.4) < 0.01:
        fp.Remove(p)
        removed_pads.append(p.GetPadName())

def nc(name):
    n = b.FindNet(name)
    assert n, f"net {name} missing"
    return n.GetNetCode()

n_tracks = n_vias = 0
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
            n_tracks += 1
for net, x, y in VIAS:
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    v.SetWidth(pcbnew.FromMM(0.6))
    v.SetDrill(pcbnew.FromMM(0.3))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNetCode(nc(net))
    b.Add(v)
    n_vias += 1

# clear stale fills (refill happens later / via MCP run_drc)
for z in b.Zones():
    try:
        z.UnFill()
    except Exception:
        z.SetIsFilled(False)
pcbnew.SaveBoard(PATH, b)
print(f"deleted old routes (kept {kept} GPS_RF via); removed fence pads {removed_pads}")
print(f"added {n_tracks} tracks, {n_vias} vias; zones refilled; saved")
