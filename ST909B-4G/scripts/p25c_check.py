# p25c_check.py — ตรวจหลังแก้: F.Cu body gate, U6 CrtYd, /LED_4G, pad39
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
M = pcbnew.ToMM

b = pcbnew.LoadBoard(BOARD)
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


for rname, r in rects.items():
    hits_f = []
    hits_b = 0
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_TRACE_T:
            if seg_hits(t.GetStart(), t.GetEnd(), r):
                if t.GetLayerName() == 'F.Cu':
                    s, e = t.GetStart(), t.GetEnd()
                    hits_f.append('%s (%.2f,%.2f)->(%.2f,%.2f)' % (
                        t.GetNetname(), M(s.x), M(s.y), M(e.x), M(e.y)))
                else:
                    hits_b += 1
        elif t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            if r[0] <= p.x <= r[2] and r[1] <= p.y <= r[3]:
                hits_f.append('VIA %s (%.2f,%.2f)' % (t.GetNetname(), M(p.x), M(p.y)))
    print('== %s: F.Cu hits %d (ต้องเป็น 0), B.Cu tracks %d' % (rname, len(hits_f), hits_b))
    for h in hits_f:
        print('   !! ' + h)

u6 = b.FindFootprintByReference('U6')
p = u6.GetPosition()
cy = u6.GetCourtyard(pcbnew.F_CrtYd)
xs, ys = [], []
for ci in range(cy.OutlineCount()):
    o = cy.COutline(ci)
    for pi in range(o.PointCount()):
        pt = o.GetPoint(pi)
        xs.append(M(pt.x))
        ys.append(M(pt.y))
print('U6 at (%.2f,%.2f) CrtYd=(%.2f..%.2f, %.2f..%.2f)' % (
    M(p.x), M(p.y), min(xs), max(xs), min(ys), max(ys)))

for netname in ('/LED_4G', '/VBAT'):
    print('== ' + netname)
    for t in b.GetTracks():
        if t.GetNetname() != netname:
            continue
        if t.Type() == pcbnew.PCB_TRACE_T:
            s, e = t.GetStart(), t.GetEnd()
            print('  trk %-5s (%.3f,%.3f)->(%.3f,%.3f)' % (
                t.GetLayerName(), M(s.x), M(s.y), M(e.x), M(e.y)))
        else:
            pp = t.GetPosition()
            print('  via %-5s (%.3f,%.3f)' % (t.GetLayerName(), M(pp.x), M(pp.y)))

u1 = b.FindFootprintByReference('U1')
for pad in u1.Pads():
    if pad.GetName() == '39':
        print('U1 pad39 zone conn = %s' % pad.GetLocalZoneConnection())
print('done')
