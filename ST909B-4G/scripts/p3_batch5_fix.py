# p3_batch5_fix.py — P3 batch 5: island repair + PKEY F lane shift
# 1) Delete old PKEY F lane (x=0.80 set) that starved U1.2 /GND west thermal spoke:
#      F h y=9.50  (1.70->0.80) w0.25
#      F v x=0.80  (9.50->29.35) w0.20
#      F h y=29.35 (0.80->1.65) w0.25
#    Replace with x=0.60 w0.20 lane (west copper edge 0.50 = exact edge clearance;
#    west spoke stub of U1.2 keeps full 0.30 length at 0.20 exact clearance).
# 2) Add 2 GND stitching vias 0.6/0.3 (verified by p3_verify.py, 44 candidates 0 viol):
#      (2.50,71.20)  F main(poly#0) + B island(poly#0) -> B island <-> F main
#      (30.00,15.00) F island(poly#1) + B main(poly#1) -> F island <-> B main
#    F island = NE block (25.73..34.5 x 7.2..31.7) + east strip (34.03..34.5 x 32..73.4),
#    only pad J7.3 (F-SMD); B island = south band + threads, only pad TP6.1 (B).
#    After both vias all 4 GND fills merge through GPS_RF via (11.50,44.00).
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
b = pcbnew.LoadBoard(BOARD)
print('board loaded')
codes = {}


def nc(name):
    if name not in codes:
        n = b.FindNet(name)
        assert n, 'net %s missing' % name
        codes[name] = n.GetNetCode()
    return codes[name]


MM = 1e6
TOL_NM = 1000  # 1 um match tolerance

OLD_SEGS = [
    (1.70, 9.50, 0.80, 9.50, 0.25),
    (0.80, 9.50, 0.80, 29.35, 0.20),
    (0.80, 29.35, 1.65, 29.35, 0.25),
]

matched = [False] * len(OLD_SEGS)
to_del = []
for t in list(b.GetTracks()):
    if t.GetClass() != 'PCB_TRACK' or t.GetNetname() != '/PKEY':
        continue
    if t.GetLayer() != pcbnew.F_Cu:
        continue
    s, e = t.GetStart(), t.GetEnd()
    x1, y1, x2, y2 = s.x / MM, s.y / MM, e.x / MM, e.y / MM
    w = t.GetWidth() / MM
    for i, (ax, ay, bx, by, aw) in enumerate(OLD_SEGS):
        if matched[i]:
            continue
        fwd = (abs(x1 - ax) < 0.001 and abs(y1 - ay) < 0.001
               and abs(x2 - bx) < 0.001 and abs(y2 - by) < 0.001)
        rev = (abs(x1 - bx) < 0.001 and abs(y1 - by) < 0.001
               and abs(x2 - ax) < 0.001 and abs(y2 - ay) < 0.001)
        if (fwd or rev) and abs(w - aw) < 0.001:
            to_del.append(t)
            matched[i] = True
            break
for i, m in enumerate(matched):
    if not m:
        print('WARNING: old seg %d not found' % i)
for t in to_del:
    b.Remove(t)
print('deleted old PKEY F tracks: %d/3' % len(to_del))

ADD_TRACKS = [
    ('/PKEY', 0.20, [(1.70, 9.50), (0.60, 9.50)]),
    ('/PKEY', 0.20, [(0.60, 9.50), (0.60, 29.35)]),
    ('/PKEY', 0.20, [(0.60, 29.35), (1.65, 29.35)]),
]
ADD_VIAS = [
    ('/GND', 2.50, 71.20),
    ('/GND', 30.00, 15.00),
]

na = 0
for net, width, seg in ADD_TRACKS:
    (x1, y1), (x2, y2) = seg
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
    t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
    t.SetWidth(pcbnew.FromMM(width))
    t.SetLayer(pcbnew.F_Cu)
    t.SetNetCode(nc(net))
    b.Add(t)
    na += 1
print('added tracks %d/%d' % (na, len(ADD_TRACKS)))

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
print('added vias %d/%d' % (va, len(ADD_VIAS)))

b.Save(BOARD)
print('saved')
