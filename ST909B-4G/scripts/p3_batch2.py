# p3_batch2.py — P3 batch 2: route (2)(3) /VBAT + (10) /ANT_4G_RF
# Edge-clearance rule confirmed 0.5mm (kicad_pro min_copper_edge_clearance), board
# Edge.Cuts rect is 0..35 x 0..74 -> west edge x=0 (0.5005 seen in zone poly is the
# pour inset, NOT the board edge). Via pads at x=1.00 reach x=0.70, gap 0.70 >= 0.5 PASS.
# (2)(3) /VBAT U6.3 (5.94,44.15) -> U1 pads 57/56/55 (16/17/18, y6.10):
#   existing: F h y=44.15 (1.00->5.94 into U6.3) + F v x=1.00 (44.15->65.00 to J5)
#   via (1.00,44.15) lands on that F corner (same net; pad 0.70..1.30 x 43.85..44.45;
#   edge gap 0.70; U6.1 west edge 3.32; TP4 y-gap 2.65; spine x-gap 0.825)
#   B v x=1.00 w0.30 north 44.15->2.00 (west edge 0.85 gap 0.85; east edge 1.15,
#   GPS_RX spine west edge 2.125 gap 0.975; 8b B h y=34.50 starts x=2.25 no overlap;
#   spine B h y=33.00 starts x=2.25 no overlap)
#   via (1.00,2.00) (top edge y=0 gap 1.70; ANT1.1 x-gap 1.20)
#   F h y=2.00 w0.30 east 1.00->16.00 (ANT1.1/1.2 pads north edge y=2.40, y-gap 0.25;
#   U1 north pads y 5.70 far; can interior starts y=6.60)
#   F v x=16.00 w0.30 south 2.00->6.10 ends in U1.57 pad (12.70..13.30 pad60 col
#   x=16: 15.70..16.30 in-pad; pad56 16.70..17.30 gap 0.55; pad58 14.70..15.30 gap 0.55;
#   y<=6.10 < can top 6.60)
#   F h y=6.10 w0.30 east 16.00->18.00 in-pad through 57/56/55 (all same net)
# (10) /ANT_4G_RF ANT1.1 (3.25,3.00) -> U1.60 (13.00,6.10): F-only, no vias, no B hop
#   (B escape impossible: keepout; simplification vs original plan)
#   F v x=3.25 w0.30 south 3.00->4.00 starts in pad1 (2.50..4.00 x 2.40..3.60)
#   F h y=4.00 w0.30 east 3.25->13.00 (ANT1.2 south edge y=3.60, y-gap 0.25; nothing
#   else on F in x 3.25..13.00 at y=4.00; outside can interior y<6.60)
#   F v x=13.00 w0.30 south 4.00->6.10 ends in pad60 (pad59 13.70..14.30 gap 0.55;
#   pad61 11.70..12.30 gap 0.55)
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
    # (2)(3) /VBAT
    ('/VBAT', 'B', 0.30, [(1.00, 44.15), (1.00, 2.00)]),
    ('/VBAT', 'F', 0.30, [(1.00, 2.00), (16.00, 2.00)]),
    ('/VBAT', 'F', 0.30, [(16.00, 2.00), (16.00, 6.10)]),
    ('/VBAT', 'F', 0.30, [(16.00, 6.10), (18.00, 6.10)]),
    # (10) /ANT_4G_RF
    ('/ANT_4G_RF', 'F', 0.30, [(3.25, 3.00), (3.25, 4.00)]),
    ('/ANT_4G_RF', 'F', 0.30, [(3.25, 4.00), (13.00, 4.00)]),
    ('/ANT_4G_RF', 'F', 0.30, [(13.00, 4.00), (13.00, 6.10)]),
]
ADD_VIAS = [
    ('/VBAT', 1.00, 44.15),
    ('/VBAT', 1.00, 2.00),
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
