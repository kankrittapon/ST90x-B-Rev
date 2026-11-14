# p3_fix.py — P3 batch 1: route unconnected items (1)(5)(6)(8)
# Rules honored: B keepout rect (2.5,35)-(20.5,53) tracks forbidden (vias allowed);
# U1 can interior F tracks forbidden (none of these enter it); via w0.6/d0.3.
# (1) /G3V3  U6.2 (4.06,45.10) -> U2.8 (4.15,55.30):
#     F h y=45.10 west to x=1.625 (VBAT via pad east edge 1.30 gap 0.20 exact; VBAT F v x=1.00 gap 0.375)
#     F v x=1.625 south to y=58.80 (GPS_RX spine west edge 2.125 gap 0.375;
#     U2.2 via (2.25,48.70) pad west edge 1.95 gap 0.20 exact)
#     via (1.625,58.80) [B] (GPS_RX via (2.25,58.00) center dist 1.016 - 0.6 = 0.416)
#     B h y=58.80 east to 4.15 (spine via south edge 58.30 gap 0.375)
#     via (4.15,58.80) -> F v x=4.15 north into U2.8 pad (same net)
#     NOTE: B route inside keepout impossible (U6.2 is inside keepout; F escape south of y=53 then B hop).
# (5) /GPS_TX U2.3 (4.15,49.80) -> TP1 (7.00,37.00):
#     F h y=49.80 east to x=7.45 (U2 pad2 gap 0.575; 1's v x=1.625 far west)
#     F v x=7.45 north to y=37.00 ending inside TP1 pad (pad 6.40..7.60 x 36.40..37.60, same net)
#     (J3.1 east edge 7.10 gap 0.225; J3.2 west edge 7.90 gap 0.325; NOT B: original spine-join
#     idea was a net short (spine=GPS_RX) and keepout-illegal)
# (6) /USB_VBUS J3.1 (6.50,40.50) -> U1.24 (11.00,28.90):
#     TP1 pad (6.40..7.60 x 36.40..37.60) blocks v x=6.50; original plan crossed TP1+GPS_TX twice.
#     F v x=6.50 north 40.50->38.00 (TP1 pad south edge 37.60 gap 0.275)
#     F h y=38.00 west to x=5.55 (north of TP1 pad, gap 0.275)
#     F v x=5.55 north 38.00->35.60 (J3.1 west edge 5.90 gap 0.225)
#     F h y=35.60 east to x=6.55 (TP1 pad gap 0.675)
#     F v x=6.55 north 35.60->30.15 (8 via (7.20,34.50) pad west edge 6.90 gap 0.225)
#     F h y=30.15 east to via (7.25,30.15) [GPS_TX v x=7.90 gap 0.40]
#     via (7.25,30.15) -> B h y=30.15 east to via (9.15,30.15)  [hop UNDER GPS_TX v x=7.90
#     (B legal: y<35 outside keepout; vias 0.225 from GPS_TX v band; via y-band 29.85..30.45
#     gap 0.225 to GPS_TX h y=30.80)]
#     via (9.15,30.15) -> F h y=30.15 east to x=11.00 (GPS_TX h gap 0.40)
#     F v x=11.00 north 30.15->28.90 into U1.24 (pad23/25 gaps 0.575; outside can interior)
# (8) /GPS_RX  a) U2.2: via (2.25,48.70) directly on spine (B v x=2.25 y 33..58)
#     + F h y=48.70 east to pad2 (pad1/3 gaps 0.575)
#     b) TP2 (9.50,37.00): F v x=9.50 north 37->34.50 (between USB_DP_F v x=8.50 and
#     USB_DM_F v x=10.50, gaps 0.75; USB h's north gaps 0.75/0.85)
#     F h y=34.50 west to via (7.20,34.50) (TP1 pad gap 1.775; 5's v x=7.45 starts y=37, gap 2.375)
#     via (7.20,34.50) -> B h y=34.50 west to x=2.25 JOINS spine T-junction
#     (outside keepout: band y 34.375..34.625 < 35; GPS_RX B h y=33.00 gap 1.25)
#     (replaces original via (2.50,45.00) + F h y=45.00 plan: F h y=45.00 would cross 5/6 lanes)
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
TOL = pcbnew.FromMM(0.06)
LAYER = {'F': pcbnew.F_Cu, 'B': pcbnew.B_Cu}

b = pcbnew.LoadBoard(BOARD)
print('board loaded')
codes = {}


def nc(name):
    if name not in codes:
        n = b.FindNet(name)
        assert n, 'net %s missing' % name
        codes[name] = n.GetNetCode()
    return codes[name]


ADD_TRACKS = [
    # (1) /G3V3
    ('/G3V3', 'F', 0.25, [(4.06, 45.10), (1.625, 45.10)]),
    ('/G3V3', 'F', 0.25, [(1.625, 45.10), (1.625, 58.80)]),
    ('/G3V3', 'B', 0.25, [(1.625, 58.80), (4.15, 58.80)]),
    ('/G3V3', 'F', 0.25, [(4.15, 58.80), (4.15, 55.30)]),
    # (5) /GPS_TX
    ('/GPS_TX', 'F', 0.25, [(4.15, 49.80), (7.45, 49.80)]),
    ('/GPS_TX', 'F', 0.25, [(7.45, 49.80), (7.45, 37.00)]),
    # (6) /USB_VBUS
    ('/USB_VBUS', 'F', 0.25, [(6.50, 40.50), (6.50, 38.00)]),
    ('/USB_VBUS', 'F', 0.25, [(6.50, 38.00), (5.55, 38.00)]),
    ('/USB_VBUS', 'F', 0.25, [(5.55, 38.00), (5.55, 35.60)]),
    ('/USB_VBUS', 'F', 0.25, [(5.55, 35.60), (6.55, 35.60)]),
    ('/USB_VBUS', 'F', 0.25, [(6.55, 35.60), (6.55, 30.15)]),
    ('/USB_VBUS', 'F', 0.25, [(6.55, 30.15), (7.25, 30.15)]),
    ('/USB_VBUS', 'B', 0.25, [(7.25, 30.15), (9.15, 30.15)]),
    ('/USB_VBUS', 'F', 0.25, [(9.15, 30.15), (11.00, 30.15)]),
    ('/USB_VBUS', 'F', 0.25, [(11.00, 30.15), (11.00, 28.90)]),
    # (8) /GPS_RX
    ('/GPS_RX', 'F', 0.25, [(2.25, 48.70), (4.15, 48.70)]),
    ('/GPS_RX', 'F', 0.25, [(9.50, 37.00), (9.50, 34.50)]),
    ('/GPS_RX', 'F', 0.25, [(9.50, 34.50), (7.20, 34.50)]),
    ('/GPS_RX', 'B', 0.25, [(7.20, 34.50), (2.25, 34.50)]),
]
ADD_VIAS = [
    ('/G3V3', 1.625, 58.80),
    ('/G3V3', 4.15, 58.80),
    ('/USB_VBUS', 7.25, 30.15),
    ('/USB_VBUS', 9.15, 30.15),
    ('/GPS_RX', 2.25, 48.70),
    ('/GPS_RX', 7.20, 34.50),
]

na = 0
for net, lay, width, seg in ADD_TRACKS:
    (x1, y1), (x2, y2) = seg
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
    t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
    t.SetWidth(pcbnew.FromMM(width))
    t.SetLayer(LAYER[lay])
    t.SetNetCode(nc(net))
    b.Add(t)
    na += 1
va = 0
for net, x, y in ADD_VIAS:
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetWidth(pcbnew.FromMM(0.6))
    v.SetDrill(pcbnew.FromMM(0.3))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNetCode(nc(net))
    assert v.GetNetname() == net, (net, v.GetNetname())
    b.Add(v)
    va += 1
print('added tracks %d/%d, vias %d/%d' % (na, len(ADD_TRACKS), va, len(ADD_VIAS)))

b.Save(BOARD)
print('saved')
