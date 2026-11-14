# p25b_checken.py — dump track/via ของ net /LED_EN /LED_CHR ปัจจุบันละเอียด
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
b = pcbnew.LoadBoard(BOARD)
for netname in ('/LED_EN', '/LED_CHR'):
    print('== ' + netname)
    for t in b.GetTracks():
        if t.GetNetname() != netname:
            continue
        if t.Type() == pcbnew.PCB_TRACE_T:
            s, e = t.GetStart(), t.GetEnd()
            print('  trk %-5s w%.3f (%.3f,%.3f)->(%.3f,%.3f)' % (
                t.GetLayerName(), pcbnew.ToMM(t.GetWidth()),
                pcbnew.ToMM(s.x), pcbnew.ToMM(s.y), pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)))
        else:
            p = t.GetPosition()
            print('  via %-5s drill%.3f (%.3f,%.3f)' % (
                t.GetLayerName(), pcbnew.ToMM(t.GetDrill()), pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)))
print('done')
