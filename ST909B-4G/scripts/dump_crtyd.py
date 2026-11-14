# dump_crtyd.py — ข้อมูลจริงสำหรับแก้ 6 error: CrtYd U6/U2/J3, U1 pads 34-60, zone fill รอบ pad39
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
M = pcbnew.ToMM

b = pcbnew.LoadBoard(BOARD)


def poly_dump(poly, label):
    xs = []
    ys = []
    for ci in range(poly.OutlineCount()):
        o = poly.COutline(ci)
        pts = []
        for pi in range(o.PointCount()):
            pt = o.GetPoint(pi)
            x, y = M(pt.x), M(pt.y)
            pts.append('(%.2f,%.2f)' % (x, y))
            xs.append(x)
            ys.append(y)
        print('   %s outline %d pts=%d: %s' % (label, ci, o.PointCount(), ' '.join(pts)))
    if xs:
        print('   %s bbox=(%.2f..%.2f, %.2f..%.2f)' % (label, min(xs), max(xs), min(ys), max(ys)))


for ref in ('U6', 'U2', 'J3'):
    fp = b.FindFootprintByReference(ref)
    p = fp.GetPosition()
    print('== %s center=(%.2f,%.2f)' % (ref, M(p.x), M(p.y)))
    poly_dump(fp.GetCourtyard(pcbnew.F_CrtYd), 'CrtYd')
    for pad in fp.Pads():
        print('   pad %s net=%-10s (%.2f,%.2f) size %.2fx%.2f' % (
            pad.GetName(), pad.GetNetname() or '-',
            M(pad.GetPosition().x), M(pad.GetPosition().y),
            M(pad.GetSize().x), M(pad.GetSize().y)))

fp = b.FindFootprintByReference('U1')
print('== U1 pads 34..60')
for pad in fp.Pads():
    try:
        n = int(pad.GetName())
    except Exception:
        continue
    if 34 <= n <= 60:
        print('   pad %d net=%-12s (%.2f,%.2f) size %.2fx%.2f' % (
            n, pad.GetNetname() or '-', M(pad.GetPosition().x), M(pad.GetPosition().y),
            M(pad.GetSize().x), M(pad.GetSize().y)))
print('done')
