# dump_p25d.py — dump track/via ทุก net ทั้งสองเลเยอร์ (ยืนยันเส้นใหม่ไม่ชนอะไร)
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
M = pcbnew.ToMM
b = pcbnew.LoadBoard(BOARD)
print('board loaded')
rows = []
for t in b.GetTracks():
    net = t.GetNetname()
    if t.Type() == pcbnew.PCB_TRACE_T:
        s, e = t.GetStart(), t.GetEnd()
        rows.append('%-12s trk %-5s w%.2f (%.2f,%.2f)->(%.2f,%.2f)' % (
            net, t.GetLayerName(), M(t.GetWidth()), M(s.x), M(s.y), M(e.x), M(e.y)))
    else:
        p = t.GetPosition()
        rows.append('%-12s via %-10s drill%.2f (%.2f,%.2f)' % (
            net, t.GetLayerName(), M(t.GetDrill()), M(p.x), M(p.y)))
for r in sorted(rows):
    print(r)
print('total=%d' % len(rows))
