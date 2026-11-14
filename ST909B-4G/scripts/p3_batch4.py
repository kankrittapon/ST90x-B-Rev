# p3_batch4.py — P3 batch 4: route (14) /USB_DP_M + (15) /USB_DM_M to the USB island
# LOCKED geometry (verified 0 violations by scripts/p3_verify.py).
#  (14) DP_M: via-in-pad U1.27 (14.00,28.90) -> B v x=14.00 (28.90..27.70) -> B h y=27.70
#      (14.00..25.00; 0.25 over DM_M lane y=28.20) -> B v x=25.00 (27.70..57.75; clears
#      GPS_RX v x=23.55 / GPS_TX v x=22.90, SOS v x=32.30, LED_EN via (26.05,59.75))
#      -> B h y=57.75 (25.00..22.40, joins island B h; 0.25 to GPS_RX B v cap 57.375).
#  (15) DM_M: via-in-pad U1.28 (15.00,28.90) -> B v x=15.00 (28.90..28.20) -> B h y=28.20
#      (15.00..24.10) -> B v x=24.10 (28.20..57.00; 0.30 to GPS_RX v x=23.55) -> B h
#      y=57.00 (24.10..24.30) -> via (24.30,57.00) -> F v x=24.30 (57.00..59.50) ->
#      F h y=59.50 (24.30..19.90) -> F v x=19.90 (59.50..58.00) joins island via
#      (19.90,58.00) (via join chosen: island F v x=20.70 too close to DP_M F v x=21.16).
# All w0.25. Vias 0.6/0.3. min clearance 0.20.
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
    # (14) /USB_DP_M
    ('/USB_DP_M', 'B', 0.25, [(14.00, 28.90), (14.00, 27.70)]),
    ('/USB_DP_M', 'B', 0.25, [(14.00, 27.70), (25.00, 27.70)]),
    ('/USB_DP_M', 'B', 0.25, [(25.00, 27.70), (25.00, 57.75)]),
    ('/USB_DP_M', 'B', 0.25, [(25.00, 57.75), (22.40, 57.75)]),
    # (15) /USB_DM_M
    ('/USB_DM_M', 'B', 0.25, [(15.00, 28.90), (15.00, 28.20)]),
    ('/USB_DM_M', 'B', 0.25, [(15.00, 28.20), (24.10, 28.20)]),
    ('/USB_DM_M', 'B', 0.25, [(24.10, 28.20), (24.10, 57.00)]),
    ('/USB_DM_M', 'B', 0.25, [(24.10, 57.00), (24.30, 57.00)]),
    ('/USB_DM_M', 'F', 0.25, [(24.30, 57.00), (24.30, 59.50)]),
    ('/USB_DM_M', 'F', 0.25, [(24.30, 59.50), (19.90, 59.50)]),
    ('/USB_DM_M', 'F', 0.25, [(19.90, 59.50), (19.90, 58.00)]),
]

ADD_VIAS = [
    ('/USB_DP_M', 14.00, 28.90),
    ('/USB_DM_M', 15.00, 28.90),
    ('/USB_DM_M', 24.30, 57.00),
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
