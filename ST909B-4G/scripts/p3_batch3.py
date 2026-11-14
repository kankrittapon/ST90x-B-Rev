# p3_batch3.py — P3 batch 3: route (7) /PKEY + (11) /VDD_EXT + (12) /4G_TXD_1V8 + (13) /4G_RXD_1V8
# LOCKED geometry (verified 0 violations by scripts/p3_verify.py, 42 candidates).
# Design notes:
#  (7) PKEY: via-in-pad U1.1 (1.70,9.50) -> F lane x=0.80 (w0.20, outside can x<2.10,
#     0.30 to U1 west pads) -> via (1.65,29.35) -> B descent x=1.625 (exact 0.65 slot
#     between VBAT via (1.00,44.15) pad east 1.30 and GPS_RX via pads west 1.95 -> 0.20
#     each) -> east at y=60.10 (north of G3V3 B h y=60.80) -> descent x=10.15 (clears
#     M3V3 via pad east 9.80 by 0.225) -> dip to y=66.30 (north of VBAT h y=69.50) ->
#     x=4.00 (west of VBAT h west cap 4.875) -> y=70.40 -> island via (17.75,70.40).
#     B descent avoids keepout (x<=2.375 legal) and /LED_4G B v x=34.30 wall.
#  (11) VDD: via-in-pad U1.15 (1.70,23.50) -> B v x=1.70 (23.50..25.00) -> B h y=25.00
#     (0.45 above RXD lane y=24.30, clears VBUS B h y=30.15 + U1.18 pad (5.00,28.90))
#     -> B v x=27.70 (25.00..32.05; 0.55/0.60 to RXD/TXD east cols) -> via (27.70,32.05)
#     lands on U5.1 pad copper x 27.70..29.02.
#  (12) TXD: via-in-pad U1.9 (1.70,17.50) -> B h y=17.50 -> B v x=2.80 (0.20 to RXD v
#     x=2.35 east edge 2.475) -> B h y=22.00 -> B v x=29.35 (22.00..33.00) -> via
#     (29.35,33.00) -> F stub h y=33.00 to U5.2 (28.36,33.00).
#  (13) RXD: via-in-pad U1.10 (1.70,18.50) -> B h y=18.50 -> B v x=2.35 (0.225 to VDD
#     via pad east 2.00) -> B h y=24.30 -> B v x=28.50 (24.30..33.95) -> via (28.50,33.95)
#     via-in-pad U5.3 (copper x 27.70..29.02).
# All w0.25 unless noted. Vias 0.6/0.3. min clearance 0.20 (razor-thin gaps are exact 0.20).
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
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
    # (7) /PKEY
    ('/PKEY', 'F', 0.25, [(1.70, 9.50), (0.80, 9.50)]),
    ('/PKEY', 'F', 0.20, [(0.80, 9.50), (0.80, 29.35)]),
    ('/PKEY', 'F', 0.25, [(0.80, 29.35), (1.65, 29.35)]),
    ('/PKEY', 'B', 0.25, [(1.625, 29.35), (1.625, 60.10)]),
    ('/PKEY', 'B', 0.25, [(1.625, 60.10), (10.15, 60.10)]),
    ('/PKEY', 'B', 0.25, [(10.15, 60.10), (10.15, 66.30)]),
    ('/PKEY', 'B', 0.25, [(10.15, 66.30), (4.00, 66.30)]),
    ('/PKEY', 'B', 0.25, [(4.00, 66.30), (4.00, 70.40)]),
    ('/PKEY', 'B', 0.25, [(4.00, 70.40), (17.75, 70.40)]),
    # (11) /VDD_EXT
    ('/VDD_EXT', 'B', 0.25, [(1.70, 23.50), (1.70, 25.00)]),
    ('/VDD_EXT', 'B', 0.25, [(1.70, 25.00), (27.70, 25.00)]),
    ('/VDD_EXT', 'B', 0.25, [(27.70, 25.00), (27.70, 32.05)]),
    # (12) /4G_TXD_1V8
    ('/4G_TXD_1V8', 'B', 0.25, [(1.70, 17.50), (2.80, 17.50)]),
    ('/4G_TXD_1V8', 'B', 0.25, [(2.80, 17.50), (2.80, 22.00)]),
    ('/4G_TXD_1V8', 'B', 0.25, [(2.80, 22.00), (29.35, 22.00)]),
    ('/4G_TXD_1V8', 'B', 0.25, [(29.35, 22.00), (29.35, 33.00)]),
    ('/4G_TXD_1V8', 'F', 0.25, [(29.35, 33.00), (28.36, 33.00)]),
    # (13) /4G_RXD_1V8
    ('/4G_RXD_1V8', 'B', 0.25, [(1.70, 18.50), (2.35, 18.50)]),
    ('/4G_RXD_1V8', 'B', 0.25, [(2.35, 18.50), (2.35, 24.30)]),
    ('/4G_RXD_1V8', 'B', 0.25, [(2.35, 24.30), (28.50, 24.30)]),
    ('/4G_RXD_1V8', 'B', 0.25, [(28.50, 24.30), (28.50, 33.95)]),
]

ADD_VIAS = [
    ('/PKEY', 1.70, 9.50),
    ('/PKEY', 1.65, 29.35),
    ('/VDD_EXT', 1.70, 23.50),
    ('/VDD_EXT', 27.70, 32.05),
    ('/4G_TXD_1V8', 1.70, 17.50),
    ('/4G_TXD_1V8', 29.35, 33.00),
    ('/4G_RXD_1V8', 1.70, 18.50),
    ('/4G_RXD_1V8', 28.50, 33.95),
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
