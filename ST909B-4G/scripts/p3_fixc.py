# p3_fixc.py — P3 batch 1c: fix last clearance error (1's via vs GPS_RX F stub x=2.25 y 58..60)
# No 0.6 via fits between VBAT F v (x=1.00 w0.30, east edge 1.15) and x=2.25 tracks
# (window 0.975 < via 0.6 + 2*0.2). Move the F->B hop south to y=60.80 (below the
# spine F stub's south end y=60.125):
#   via (1.75,60.80): VBAT F v gap 0.30 (pad west edge 1.45); spine F v x=2.25 dist 0.47;
#   TP3 pad dist 0.38; spine via dist 2.24
#   B h y=60.80 east 1.75->5.60 (J4.1 y-gap 0.475; M3V3 via y-gap 0.775)
#   via (5.60,60.80) (J4.1 dist 0.30; M3V3 via dist 0.60)
#   F v x=5.60 north 60.80->55.30 -> F h y=55.30 west into U2.8 (pad9 netless y-gap 0.575)
# F2 v x=1.625 extended 58.80->60.80 (spine F stub x-gap 0.375; TP3 pad x-gap 0.65;
# spine via pad x-gap 0.20 exact; VBAT F v gap 0.35)
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


def seg_match(t, net, lay, seg):
    if t.GetNetCode() != nc(net) or t.GetLayer() != LAYER[lay]:
        return False
    (x1, y1), (x2, y2) = seg
    x1, y1, x2, y2 = (pcbnew.FromMM(x1), pcbnew.FromMM(y1),
                      pcbnew.FromMM(x2), pcbnew.FromMM(y2))
    s, e = t.GetStart(), t.GetEnd()
    return ((abs(s.x - x1) < TOL and abs(s.y - y1) < TOL and abs(e.x - x2) < TOL and abs(e.y - y2) < TOL) or
            (abs(s.x - x2) < TOL and abs(s.y - y2) < TOL and abs(e.x - x1) < TOL and abs(e.y - y1) < TOL))


DEL_TRACKS = [
    ('/G3V3', 'F', [(1.625, 45.10), (1.625, 58.80)]),
    ('/G3V3', 'B', [(1.65, 58.80), (5.60, 58.80)]),
    ('/G3V3', 'F', [(5.60, 58.80), (5.60, 55.30)]),
    ('/G3V3', 'F', [(5.60, 55.30), (4.15, 55.30)]),
]
DEL_VIAS = [
    ('/G3V3', 1.65, 58.80),
    ('/G3V3', 5.60, 58.80),
]
ADD_TRACKS = [
    ('/G3V3', 'F', 0.25, [(1.625, 45.10), (1.625, 60.80)]),
    ('/G3V3', 'B', 0.25, [(1.75, 60.80), (5.60, 60.80)]),
    ('/G3V3', 'F', 0.25, [(5.60, 60.80), (5.60, 55.30)]),
    ('/G3V3', 'F', 0.25, [(5.60, 55.30), (4.15, 55.30)]),
]
ADD_VIAS = [
    ('/G3V3', 1.75, 60.80),
    ('/G3V3', 5.60, 60.80),
]

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
print('deleted tracks %d/%d, vias %d/%d' % (nd, len(DEL_TRACKS), vd, len(DEL_VIAS)))

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
