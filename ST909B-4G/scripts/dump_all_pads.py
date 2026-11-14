# dump_all_pads.py — dump ข้อมูลครบทุก footprint: pad (เลข, net, ตำแหน่ง, ขนาด), bbox, side
# + zone3 outline + TP4 net/traces ใกล้เคียง (อ่านอย่างเดียว)
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
M = pcbnew.ToMM
b = pcbnew.LoadBoard(BOARD)
print('board loaded')

for fp in sorted(b.GetFootprints(), key=lambda f: f.GetReference()):
    pos = fp.GetPosition()
    bb = fp.GetBoundingBox()
    print('== %-4s %-18s side=%-5s center=(%.2f,%.2f) rot=%.0f bbox=(%.2f..%.2f, %.2f..%.2f)' % (
        fp.GetReference(), fp.GetValue(), fp.GetLayerName(), M(pos.x), M(pos.y),
        fp.GetOrientationDegrees(),
        M(bb.GetLeft()), M(bb.GetRight()), M(bb.GetTop()), M(bb.GetBottom())))
    for p in sorted(fp.Pads(), key=lambda q: q.GetPadName()):
        pp = p.GetPosition()
        sz = p.GetSize()
        print('   pad %-3s net %-14s (%.2f,%.2f) size (%.2f x %.2f)' % (
            p.GetPadName(), p.GetNetname() or '-', M(pp.x), M(pp.y),
            M(sz.x), M(sz.y)))

print('== zones ==')
for i, z in enumerate(b.Zones()):
    bb = z.GetBoundingBox()
    try:
        pts = []
        o = z.Outline()
        for pi in range(o.OutlineCount()):
            for vi in range(o.VertexCount(pi)):
                pt = o.CPoint(pi, vi)
                pts.append('(%.2f,%.2f)' % (M(pt.x), M(pt.y)))
        print('zone %d net=%-10s layer=%s bbox=(%.2f..%.2f, %.2f..%.2f) verts=%d' % (
            i, z.GetNetname() or '-', z.GetLayerName(),
            M(bb.GetLeft()), M(bb.GetRight()), M(bb.GetTop()), M(bb.GetBottom()), len(pts)))
        print('   pts:', ' '.join(pts[:40]))
    except Exception as ex:
        print('zone %d outline err: %s' % (i, ex))

print('== TP4 net + tracks near TP4 ==')
tp4 = b.FindFootprintByReference('TP4')
p4 = tp4.FindPadByNumber('1')
print('TP4.1 net:', p4.GetNetname() or '-', 'pos (%.2f,%.2f)' % (M(p4.GetPosition().x), M(p4.GetPosition().y)))
code = p4.GetNetCode()
for t in b.GetTracks():
    if t.GetNetCode() != code or t.Type() == pcbnew.PCB_VIA_T:
        continue
    s, e = t.GetStart(), t.GetEnd()
    print('   trk %-5s (%.2f,%.2f)->(%.2f,%.2f)' % (t.GetLayerName(), M(s.x), M(s.y), M(e.x), M(e.y)))
print('done')
