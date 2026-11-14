# dump_nets_p25.py — route topology เต็มของ net ที่ต้องย้ายใน P2.5 (อ่านอย่างเดียว)
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
M = pcbnew.ToMM
b = pcbnew.LoadBoard(BOARD)
print('board loaded')

NETS = ['/LED_EN', '/LED_GPS', '/LED_4G', '/GPS_RX', '/M3V3', '/VBAT']
for name in NETS:
    ni = b.FindNet(name)
    if ni is None:
        print('== %s MISSING ==' % name)
        continue
    code = ni.GetNetCode()
    print('== %s (code %d) ==' % (name, code))
    for t in b.GetTracks():
        if t.GetNetCode() != code:
            continue
        typ = t.Type()
        if typ == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            print('  via (%.2f,%.2f)' % (M(p.x), M(p.y)))
        else:
            s, e = t.GetStart(), t.GetEnd()
            print('  trk %-5s w%.2f (%.2f,%.2f)->(%.2f,%.2f)' % (
                t.GetLayerName(), M(t.GetWidth()),
                M(s.x), M(s.y), M(e.x), M(e.y)))
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetNetCode() == code:
                pos = p.GetPosition()
                print('  pad %-5s.%-3s (%.2f,%.2f) %s' % (
                    fp.GetReference(), p.GetPadName(),
                    M(pos.x), M(pos.y), p.GetLayerName()))
print('done')
