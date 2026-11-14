# p3_fixb.py — P3 batch 1b: fix 5 errors from batch 1
# E1+E5 shorting_items/solder_mask_bridge @(4.15,58.80): F3 v x=4.15 ran through netless
#   U2.9 pad (3.25..5.05 x 56.00..56.80). Fix: hop east of pad9 col:
#   via (5.60,58.80) -> F v x=5.60 (55.30..58.80; pad9 east edge 5.05 gap 0.425)
#   -> F h y=55.30 west into U2.8 east edge (pad7 gap 0.575)
# E4 clearance @(1.62,58.80): via pad west edge 1.325 vs /VBAT F v x=1.00 which is
#   0.30 WIDE (band 0.85..1.15, not 0.875..1.125) -> gap 0.175. Fix: via x 1.625->1.65
#   (pad 1.35..1.95, gap 0.20 exact; still overlaps F2 v x=1.625 band 1.50..1.75 -> connected).
#   F2 stays x=1.625 (0.20 exact to 8's via pad west edge 1.95, 0.35 to VBAT v).
#   B1 west end moves 1.625->1.65.
# E2+E3 tracks_crossing: 8's F h y=34.50 (9.50->7.20) crossed USB_DP_F v x=8.50 and
#   GPS_TX v x=7.90 (both F verticals y-span covers 34.50). Fix: move the F->B hop to
#   x=9.50: via (9.50,34.50) (DM_F v x=10.50 gap 0.575; DM_F h y=33.40 y-gap 0.675;
#   TP2 pad y-gap 1.60) + B h y=34.50 (9.50->2.25) passing UNDER DP_F v / GPS_TX v /
#   6's F v x=6.55 / 6's F v x=5.55 (B under F legal; 6's vias (7.25/9.15,30.15)
#   y-gap 3.75+) -> spine T-junction at (2.25,34.50).
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
    ('/G3V3', 'B', [(1.625, 58.80), (4.15, 58.80)]),
    ('/G3V3', 'F', [(4.15, 58.80), (4.15, 55.30)]),
    ('/GPS_RX', 'F', [(9.50, 34.50), (7.20, 34.50)]),
    ('/GPS_RX', 'B', [(7.20, 34.50), (2.25, 34.50)]),
]
DEL_VIAS = [
    ('/G3V3', 1.625, 58.80),
    ('/G3V3', 4.15, 58.80),
    ('/GPS_RX', 7.20, 34.50),
]
ADD_TRACKS = [
    ('/G3V3', 'B', 0.25, [(1.65, 58.80), (5.60, 58.80)]),
    ('/G3V3', 'F', 0.25, [(5.60, 58.80), (5.60, 55.30)]),
    ('/G3V3', 'F', 0.25, [(5.60, 55.30), (4.15, 55.30)]),
    ('/GPS_RX', 'B', 0.25, [(9.50, 34.50), (2.25, 34.50)]),
]
ADD_VIAS = [
    ('/G3V3', 1.65, 58.80),
    ('/G3V3', 5.60, 58.80),
    ('/GPS_RX', 9.50, 34.50),
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
