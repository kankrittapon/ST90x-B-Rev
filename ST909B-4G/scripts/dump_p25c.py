# dump_p25c.py — tracks/vias ปัจจุบันของ nets สำคัญ + ขนาด via จริง (อ่านอย่างเดียว)
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
M = pcbnew.ToMM
b = pcbnew.LoadBoard(BOARD)
print('board loaded')
WANT = ('/LED_EN', '/LED_CHR', '/LED_GPS', '/LED_4G', '/SOS', '/GPS_RX',
        '/USB_DP_M', '/USB_DM_M', '/LED_K', '/VBAT', '/M3V3')
for t in b.GetTracks():
    net = t.GetNetname()
    if net not in WANT:
        continue
    if t.Type() == pcbnew.PCB_TRACE_T:
        s, e = t.GetStart(), t.GetEnd()
        print('%-9s trk %-5s w%.2f (%.2f,%.2f)->(%.2f,%.2f)' % (
            net, t.GetLayerName(), M(t.GetWidth()), M(s.x), M(s.y), M(e.x), M(e.y)))
    else:
        p = t.GetPosition()
        print('%-9s via %-10s drill%.2f (%.2f,%.2f)' % (
            net, t.GetLayerName(), M(t.GetDrill()), M(p.x), M(p.y)))
print('done')
