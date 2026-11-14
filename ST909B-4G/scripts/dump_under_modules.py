# dump_under_modules.py — รายงาน track/arc/via ใต้ U1/U2 สำหรับวางแผน P2.5 (อ่านอย่างเดียว)
# via ห้ามเรียก GetWidth() ไม่ใส่ layer -> ใช้เฉพาะตำแหน่ง/net
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
M = pcbnew.ToMM

b = pcbnew.LoadBoard(BOARD)
print('board loaded')

U1 = b.FindFootprintByReference('U1').GetPosition()
U2 = b.FindFootprintByReference('U2').GetPosition()
rects = {
    'U1': (U1.x - pcbnew.FromMM(12.0), U1.y - pcbnew.FromMM(12.0),
           U1.x + pcbnew.FromMM(12.0), U1.y + pcbnew.FromMM(12.0)),
    'U2': (U2.x - pcbnew.FromMM(4.85), U2.y - pcbnew.FromMM(5.05),
           U2.x + pcbnew.FromMM(4.85), U2.y + pcbnew.FromMM(5.05)),
}


def seg_hits(s, e, r):
    x0, y0, x1, y1 = s.x, s.y, e.x, e.y
    rx0, ry0, rx1, ry1 = r
    dx, dy = x1 - x0, y1 - y0
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x0 - rx0), (dx, rx1 - x0), (-dy, y0 - ry0), (dy, ry1 - y0)):
        if p == 0:
            if q < 0:
                return False
        else:
            rr = q / p
            if p < 0:
                if rr > t1:
                    return False
                if rr > t0:
                    t0 = rr
            else:
                if rr < t0:
                    return False
                if rr < t1:
                    t1 = rr
    return True


for name, r in rects.items():
    print('== %s ==' % name)
    n_trk = n_via = n_arc = 0
    for t in b.GetTracks():
        try:
            typ = t.Type()
            if typ == pcbnew.PCB_TRACE_T:
                if not seg_hits(t.GetStart(), t.GetEnd(), r):
                    continue
                n_trk += 1
                s, e = t.GetStart(), t.GetEnd()
                print('  trk %-14s %-6s w%.2f (%.2f,%.2f)->(%.2f,%.2f)' % (
                    t.GetNetname() or '(none)', t.GetLayerName(), M(t.GetWidth()),
                    M(s.x), M(s.y), M(e.x), M(e.y)))
            elif typ == pcbnew.PCB_ARC_T:
                if not seg_hits(t.GetStart(), t.GetEnd(), r):
                    continue
                n_arc += 1
                print('  arc %-14s %-6s w%.2f (%.2f,%.2f)->(%.2f,%.2f)' % (
                    t.GetNetname() or '(none)', t.GetLayerName(), M(t.GetWidth()),
                    M(t.GetStart().x), M(t.GetStart().y), M(t.GetEnd().x), M(t.GetEnd().y)))
            elif typ == pcbnew.PCB_VIA_T:
                p = t.GetPosition()
                if r[0] <= p.x <= r[2] and r[1] <= p.y <= r[3]:
                    n_via += 1
                    print('  via %-14s at (%.2f,%.2f)' % (
                        t.GetNetname() or '(none)', M(p.x), M(p.y)))
        except Exception as ex:
            print('  ERR item skipped:', ex)
    print('  totals: tracks %d arcs %d vias %d' % (n_trk, n_arc, n_via))
print('done')
