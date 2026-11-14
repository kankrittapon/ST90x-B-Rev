# dump_nets.py — track/via ปัจจุบันของ /VBAT /LED_4G /SOS /BOOT (ground truth ก่อนเขียน p25c)
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
M = pcbnew.ToMM

b = pcbnew.LoadBoard(BOARD)
NETS = ['/VBAT', '/LED_4G', '/SOS', '/BOOT']
for netname in NETS:
    print('== ' + netname)
    for t in b.GetTracks():
        if t.GetNetname() != netname:
            continue
        if t.Type() == pcbnew.PCB_TRACE_T:
            s, e = t.GetStart(), t.GetEnd()
            print('  trk %-5s w%.3f (%.3f,%.3f)->(%.3f,%.3f)' % (
                t.GetLayerName(), M(t.GetWidth()),
                M(s.x), M(s.y), M(e.x), M(e.y)))
        else:
            p = t.GetPosition()
            print('  via %-5s drill%.3f (%.3f,%.3f)' % (
                t.GetLayerName(), M(t.GetDrill()), M(p.x), M(p.y)))
print('done')
