# check_p25_clearance.py — ตรวจ clearance ของ route ที่วางแผนไว้ใน p25_move_traces.py
# กับ copper จริงทุกชิ้นบนบอร์ด (pad/track/via) ชั้นเดียวกัน + แผนใหม่ด้วยกันเอง (อ่านอย่างเดียว)
# อ่านรายการ ADD/DEL/MOVE จาก p25_move_traces.py ด้วย ast
import ast
import math
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
PLAN = r"D:\Tracker\ST909B-4G\scripts\p25_move_traces.py"
REQ = 0.20   # copper clearance ที่ DRC ใช้จริง

src = open(PLAN, encoding='utf-8').read()
tree = ast.parse(src)
lists = {}
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id in ('ADD_TRACKS', 'ADD_VIAS', 'DEL_TRACKS', 'DEL_VIAS', 'MOVE_FP'):
                lists[t.id] = ast.literal_eval(node.value)
ADD_TRACKS, ADD_VIAS = lists['ADD_TRACKS'], lists['ADD_VIAS']
DEL_TRACKS, DEL_VIAS = lists['DEL_TRACKS'], lists['DEL_VIAS']
MOVE_FP = lists['MOVE_FP']

b = pcbnew.LoadBoard(BOARD)
M = pcbnew.ToMM
moves = {ref: (x, y) for ref, x, y in MOVE_FP}


def seg_dist(a1, a2, b1, b2):
    def d(p, s, e):
        vx, vy = e[0] - s[0], e[1] - s[1]
        L2 = vx * vx + vy * vy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - s[0]) * vx + (p[1] - s[1]) * vy) / L2))
        dx, dy = s[0] + t * vx - p[0], s[1] + t * vy - p[1]
        return math.hypot(dx, dy)
    return min(d(a1, b1, b2), d(a2, b1, b2), d(b1, a1, a2), d(b2, a1, a2))


def seg_rect(s, e, r):
    cx, cy, hx, hy = r
    if (r[0] <= s[0] <= r[1] if False else False):
        pass
    # segment-AABB distance
    px0, px1 = sorted((s[0], e[0]))
    py0, py1 = sorted((s[1], e[1]))
    if px0 <= cx + hx and px1 >= cx - hx and py0 <= cy + hy and py1 >= cy - hy:
        # overlap in bbox: check if segment actually crosses rect interior via corner test
        inside = all((cx - hx <= x <= cx + hx and cy - hy <= y <= cy + hy) for x, y in (s, e))
        if inside:
            return 0.0
        # Liang-Barsky
        x0, y0, x1, y1 = s[0], s[1], e[0], e[1]
        rx0, ry0, rx1, ry1 = cx - hx, cy - hy, cx + hx, cy + hy
        dx, dy = x1 - x0, y1 - y0
        t0, t1 = 0.0, 1.0
        for p, q in ((-dx, x0 - rx0), (dx, rx1 - x0), (-dy, y0 - ry0), (dy, ry1 - y0)):
            if p == 0:
                if q < 0:
                    break
            else:
                rr = q / p
                if p < 0:
                    if rr > t1:
                        break
                    if rr > t0:
                        t0 = rr
                else:
                    if rr < t0:
                        break
                    if rr < t1:
                        t1 = rr
        else:
            return 0.0
    # nearest point on segment to rect
    return min(seg_dist(s, e, (cx - hx, cy - hy), (cx + hx, cy - hy)),
               seg_dist(s, e, (cx + hx, cy - hy), (cx + hx, cy + hy)),
               seg_dist(s, e, (cx + hx, cy + hy), (cx - hx, cy + hy)),
               seg_dist(s, e, (cx - hx, cy + hy), (cx - hx, cy - hy)))


def seg_seg_gap(p1, p2, w1, q1, q2, w2):
    return seg_dist(p1, p2, q1, q2) - w1 / 2 - w2 / 2


# ---- collect existing items (exclude planned deletions) ----
def del_match_trk(net, lay, seg, t):
    if t.GetNetname() != net or t.GetLayerName() != lay:
        return False
    s, e = t.GetStart(), t.GetEnd()
    x1, y1, x2, y2 = seg[0][0], seg[0][1], seg[1][0], seg[1][1]
    return (abs(M(s.x) - x1) < 0.06 and abs(M(s.y) - y1) < 0.06 and
            abs(M(e.x) - x2) < 0.06 and abs(M(e.y) - y2) < 0.06) or \
           (abs(M(e.x) - x1) < 0.06 and abs(M(e.y) - y1) < 0.06 and
            abs(M(s.x) - x2) < 0.06 and abs(M(s.y) - y2) < 0.06)


pads = []
for fp in b.GetFootprints():
    ref = fp.GetReference()
    dx = dy = 0.0
    if ref in moves:
        p0 = fp.GetPosition()
        dx, dy = moves[ref][0] - M(p0.x), moves[ref][1] - M(p0.y)
    for p in fp.Pads():
        pos = p.GetPosition()
        cx, cy = M(pos.x) + dx, M(pos.y) + dy
        sz = p.GetSize()
        hx, hy = M(sz.x) / 2, M(sz.y) / 2
        if hx == 0 and hy == 0:
            continue
        layers = set()
        try:
            for L in p.GetLayerSet().Seq():
                layers.add(pcbnew.LayerName(L))
        except Exception:
            layers.add(p.GetLayerName())
        drill = 0.0
        try:
            dsz = p.GetDrillSize()
            drill = M(min(dsz.x, dsz.y))
        except Exception:
            pass
        if drill > 0:
            layers.add('F.Cu'); layers.add('B.Cu')
        pads.append((ref + '.' + p.GetPadName(), p.GetNetname(), cx, cy, hx, hy,
                     sorted(layers), drill / 2))

tracks = []
for t in b.GetTracks():
    typ = t.Type()
    s, e = t.GetStart(), t.GetEnd()
    item = None
    if typ == pcbnew.PCB_TRACE_T:
        item = ('trk', t.GetNetname(), t.GetLayerName(),
                (M(s.x), M(s.y)), (M(e.x), M(e.y)), M(t.GetWidth()))
    elif typ == pcbnew.PCB_VIA_T:
        item = ('via', t.GetNetname(), 'F.Cu+B.Cu', (M(s.x), M(s.y)), (M(s.x), M(s.y)), 0.6)
    if item:
        # skip planned deletions
        skip = False
        if item[0] == 'trk':
            for net, lay, seg in DEL_TRACKS:
                if del_match_trk(net, lay, seg, t):
                    skip = True
                    break
        else:
            for net, x, y in DEL_VIAS:
                if t.GetNetname() == net and abs(M(s.x) - x) < 0.06 and abs(M(s.y) - y) < 0.06:
                    skip = True
                    break
        if not skip:
            tracks.append(item)

# planned items (tracks + vias) as checkable geometry
plan = []
for net, lay, w, seg in ADD_TRACKS:
    plan.append(('trk', net, lay, tuple(seg[0]), tuple(seg[1]), w))
for net, x, y in ADD_VIAS:
    plan.append(('via', net, 'F.Cu+B.Cu', (x, y), (x, y), 0.6))

# planned-vs-planned + planned-vs-existing
rows = []
for i, a in enumerate(plan):
    kind, net, lay, p1, p2, w = a
    others = [(o[0], o[1], o[2], o[3], o[4], o[5]) for j, o in enumerate(plan) if j != i]
    others += [(t[0], t[1], t[2], t[3], t[4], t[5]) for t in tracks]
    for okind, onet, olay, q1, q2, ow in others:
        if okind == 'trk':
            if olay != lay:
                continue
            gap = seg_seg_gap(p1, p2, w, q1, q2, ow)
            desc = '%s %s (%.2f,%.2f)-(%.2f,%.2f)' % (okind, onet, q1[0], q1[1], q2[0], q2[1])
        else:
            if olay != lay and olay != 'F.Cu+B.Cu':
                continue
            gap = seg_dist((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2,
                           (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2) if False else \
                math.hypot((p1[0] + p2[0]) / 2 - q1[0], (p1[1] + p2[1]) / 2 - q1[1]) - w / 2 - ow / 2
            desc = 'via %s (%.2f,%.2f)' % (onet, q1[0], q1[1])
        if net == onet:
            tag = 'SAME-NET'
        elif gap < 0:
            tag = 'SHORT!'
        elif gap < REQ:
            tag = 'TOO-CLOSE'
        else:
            continue
        rows.append((tag, '%s %s (%.2f,%.2f)-(%.2f,%.2f) w%.2f' % (kind, net, p1[0], p1[1], p2[0], p2[1], w),
                     desc, gap))
    # pads on same layer
    for name, pnet, cx, cy, hx, hy, layers, dr in pads:
        if lay not in layers:
            continue
        gap = seg_rect(p1, p2, (cx, cy, hx, hy)) - w / 2
        desc = 'pad %s [%s] (%.2f,%.2f) %.1fx%.1f' % (name, pnet or '-', cx, cy, 2 * hx, 2 * hy)
        if net == pnet:
            if -0.05 < gap < 0.0:
                pass
            elif gap > 0.05:
                tag = 'SAME-NET-gap'
            else:
                tag = 'CONTACT'
            rows.append((tag, '%s %s (%.2f,%.2f)-(%.2f,%.2f) w%.2f' % (kind, net, p1[0], p1[1], p2[0], p2[1], w),
                         desc, gap))
            continue
        if gap < 0:
            tag = 'SHORT!'
        elif gap < REQ:
            tag = 'TOO-CLOSE'
        else:
            continue
        rows.append((tag, '%s %s (%.2f,%.2f)-(%.2f,%.2f) w%.2f' % (kind, net, p1[0], p1[1], p2[0], p2[1], w),
                     desc, gap))
        # hole clearance vs TH pads
        if kind == 'via' and dr > 0:
            hg = math.hypot((p1[0] + p2[0]) / 2 - cx, (p1[1] + p2[1]) / 2 - cy) - 0.15 - dr
            if hg < 0.25:
                rows.append(('HOLE-CLOSE', 'via %s (%.2f,%.2f)' % (net, (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2),
                             'drill %s r%.2f' % (name, dr), hg))

sev = {'SHORT!': 0, 'TOO-CLOSE': 1, 'HOLE-CLOSE': 2, 'CONTACT': 3, 'SAME-NET': 4, 'SAME-NET-gap': 5}
rows.sort(key=lambda r: (sev.get(r[0], 9), r[3]))
print('planned tracks %d, vias %d; existing tracks %d, pads %d' % (
    sum(1 for p in plan if p[0] == 'trk'), sum(1 for p in plan if p[0] == 'via'),
    len(tracks), len(pads)))
print('--- flags ---')
n = 0
for tag, who, other, gap in rows:
    if tag in ('SAME-NET-gap',):
        continue
    print('%-10s gap=%+.3f | %s | vs %s' % (tag, gap, who, other))
    n += 1
    if n > 60:
        print('... (truncated)')
        break
print('total flagged rows: %d' % n)
print('done')
