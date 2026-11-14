# p3_dump.py — สถานะบอร์ดล่าสุดสำหรับวางแผน P3: pad ทุกตัว + track/via ทุกเน็ต
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
M = pcbnew.ToMM

b = pcbnew.LoadBoard(BOARD)

for fp in b.GetFootprints():
    ref = fp.GetReference()
    p = fp.GetPosition()
    side = 'F' if fp.GetLayer() == pcbnew.F_Cu else 'B'
    pads = sorted(fp.Pads(), key=lambda pd: (pd.GetPosition().y, pd.GetPosition().x))
    print('== %s side=%s center=(%.2f,%.2f) pads=%d' % (ref, side, M(p.x), M(p.y), len(pads)))
    for pad in fp.Pads():
        pp = pad.GetPosition()
        print('   pad %-4s net=%-14s (%.2f,%.2f) %.2fx%.2f %s' % (
            pad.GetName(), pad.GetNetname() or '-',
            M(pp.x), M(pp.y), M(pad.GetSize().x), M(pad.GetSize().y),
            'F' if pad.GetLayerName().startswith('F') else 'B'))

print('==== TRACKS/VIAS ====')
bynet = {}
for t in b.GetTracks():
    bynet.setdefault(t.GetNetname() or '-', []).append(t)
for netname in sorted(bynet):
    print('== %s' % netname)
    for t in bynet[netname]:
        if t.Type() == pcbnew.PCB_TRACE_T:
            s, e = t.GetStart(), t.GetEnd()
            print('  trk %-5s (%.3f,%.3f)->(%.3f,%.3f)' % (
                t.GetLayerName(), M(s.x), M(s.y), M(e.x), M(e.y)))
        else:
            pp = t.GetPosition()
            print('  via %-5s (%.3f,%.3f)' % (t.GetLayerName(), M(pp.x), M(pp.y)))
print('done')
