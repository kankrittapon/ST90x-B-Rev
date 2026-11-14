# dump_p25b.py — ข้อมูลตัดสินสำหรับแก้ 12 errors (อ่านอย่างเดียว)
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
M = pcbnew.ToMM
b = pcbnew.LoadBoard(BOARD)
print('board loaded')

print('=== zones ===')
for i, z in enumerate(b.Zones()):
    flags = []
    for meth in ('GetIsRuleArea', 'GetDoNotAllowCopper', 'GetDoNotAllowVias',
                 'GetDoNotAllowTracks', 'GetDoNotAllowPads', 'GetDoNotAllowFootprints'):
        try:
            flags.append('%s=%s' % (meth.replace('GetDoNotAllow', 'no'), getattr(z, meth)()))
        except Exception:
            pass
    print('zone %d net=%s layer=%s' % (i, z.GetNetname() or '-', z.GetLayerName()))
    poly = z.Outline()
    pts = []
    try:
        for ci in range(poly.OutlineCount()):
            ch = poly.COutline(ci)
            for pi in range(ch.PointCount()):
                p = ch.GetPoint(pi)
                pts.append('(%.2f,%.2f)' % (M(p.x), M(p.y)))
    except Exception as ex:
        pts.append('ERR:%s' % ex)
    print('   outline:', ' '.join(pts))
    print('   flags:', ' '.join(flags))

print('=== courtyard bboxes ===')
for ref in ('U1', 'U2', 'U6', 'J1', 'J3', 'TP1', 'TP2', 'TP3', 'TP4', 'RN1', 'J4'):
    fp = b.FindFootprintByReference(ref)
    if fp is None:
        continue
    for layname, lay in (('F', pcbnew.F_CrtYd), ('B', pcbnew.B_CrtYd)):
        x0 = y0 = 1e9
        x1 = y1 = -1e9
        n = 0
        for d in fp.GraphicalItems():
            if d.GetLayer() == lay:
                bb = d.GetBoundingBox()
                x0 = min(x0, M(bb.GetLeft())); y0 = min(y0, M(bb.GetTop()))
                x1 = max(x1, M(bb.GetRight())); y1 = max(y1, M(bb.GetBottom()))
                n += 1
        if n:
            print('%-4s %s.CrtYd n=%d (%.2f..%.2f, %.2f..%.2f)' % (ref, layname, n, x0, x1, y0, y1))
print('done')
