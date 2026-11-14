# swap_assign_p2.py — เปลี่ยน U1/U2 จาก block footprint เป็น footprint จริง + assign nets ตาม pin_table
# ตามแผน P2; จบด้วย UnFill zones (refill คนละ process) + สำรวจ track/via ใต้โมดูล (P2.5)
import pcbnew
import csv
import collections

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
LIB = r"D:\Tracker\ST909B-4G\lib\ST909B.pretty"

TABLES = {
    'U1': (LIB + r'\A7670SA_LGA88.kicad_mod', 'A7670SA_LGA88',
           r"D:\Tracker\ST909B-4G\pin_table\U1_A7670SA_pins.csv", 'A7670SA'),
    'U2': (LIB + r'\L76KB_LGA18.kicad_mod', 'L76KB_LGA18',
           r"D:\Tracker\ST909B-4G\pin_table\U2_L76KB_pins.csv", 'L76KB'),
}


def load_table(path):
    rows = {}
    with open(path, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            pin = row['pin_number'].strip()
            net = (row.get('net_name') or '').strip()
            rows[pin] = net
    return rows


def net_item(b, name):
    ni = b.FindNet(name)
    if ni is None:
        ni = pcbnew.NETINFO_ITEM(b, name)
        b.Add(ni)
    return ni


def set_lib_id(fp, lib, name):
    for attempt in ('two', 'one', 'setter'):
        try:
            if attempt == 'two':
                fp.SetFPID(pcbnew.LIB_ID(lib, name))
            elif attempt == 'one':
                fp.SetFPID(pcbnew.LIB_ID(lib + ':' + name))
            else:
                lid = fp.GetFPID()
                lid.SetLibNickname(lib)
                lid.SetLibItemName(name)
                fp.SetFPID(lid)
            return attempt
        except Exception:
            continue
    return 'failed'


def seg_hits_rect(p1, p2, rx0, ry0, rx1, ry1):
    x0, y0, x1, y1 = p1.x, p1.y, p2.x, p2.y
    dx, dy = x1 - x0, y1 - y0
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x0 - rx0), (dx, rx1 - x0), (-dy, y0 - ry0), (dy, ry1 - y0)):
        if p == 0:
            if q < 0:
                return False
        else:
            r = q / p
            if p < 0:
                if r > t1:
                    return False
                if r > t0:
                    t0 = r
            else:
                if r < t0:
                    return False
                if r < t1:
                    t1 = r
    return True


b = pcbnew.LoadBoard(BOARD)
M = pcbnew.ToMM
print('pads before:', sum(len(fp.Pads()) for fp in b.GetFootprints()))

old_pos = {}
for ref, (path, name, table_path, defval) in TABLES.items():
    old = b.FindFootprintByReference(ref)
    assert old is not None, ref
    pos = old.GetPosition()
    deg = old.GetOrientationDegrees()
    val = (old.GetValue() or defval).replace('_MODULE', '').replace('MODULE', '') or defval
    print('%s old: pos (%.2f, %.2f) rot %.1f value "%s" fp "%s"' % (
        ref, M(pos.x), M(pos.y), deg, val, old.GetFPIDAsString()))
    old_pos[ref] = (pos, deg)

    new = pcbnew.FootprintLoad(LIB, name)
    assert new is not None, name
    new.SetPosition(pos)
    new.SetOrientationDegrees(deg)
    print('  lib_id:', set_lib_id(new, 'ST909B', name))
    new.SetValue(val)
    new.SetReference(ref)
    try:
        ds = old.GetProperty('Datasheet')
        if ds:
            new.SetProperty('Datasheet', ds)
    except Exception:
        pass

    b.Remove(old)
    b.Add(new)

    pins = load_table(table_path)
    assigned, netless, missing = 0, [], []
    for pin, net in pins.items():
        p = new.FindPadByNumber(pin)
        if p is None:
            missing.append(pin)
            continue
        if not net:
            netless.append(pin)
            continue
        try:
            p.SetNet(net_item(b, net))
        except AttributeError:
            p.SetNetCode(net_item(b, net).GetNetCode())
        assigned += 1
    print('  assigned %d, netless %d, missing pads %s' % (
        assigned, len(netless), missing if missing else 'none'))

b.Save(BOARD)
print('saved.')

# ---- ตรวจซ้ำโดยโหลดใหม่ ----
b2 = pcbnew.LoadBoard(BOARD)
print('pads after:', sum(len(fp.Pads()) for fp in b2.GetFootprints()))
for ref in ('U1', 'U2'):
    fp = b2.FindFootprintByReference(ref)
    nets = collections.Counter(p.GetNetname() or '(none)' for p in fp.Pads())
    print('%s: %s pads=%d rot %.1f' % (ref, fp.GetFPIDAsString(), len(fp.Pads()),
                                       fp.GetOrientationDegrees()))
    for n, c in sorted(nets.items()):
        print('   %-16s %d' % (n, c))

# ---- สำรวจ track/via ใต้โมดูล (สำหรับ P2.5) ----
U1 = b2.FindFootprintByReference('U1').GetPosition()
U2 = b2.FindFootprintByReference('U2').GetPosition()
rects = {
    'U1': (U1.x - 12_000_000, U1.y - 12_000_000, U1.x + 12_000_000, U1.y + 12_000_000),
    'U2': (U2.x - 4_850_000, U2.y - 5_050_000, U2.x + 4_850_000, U2.y + 5_050_000),
}
for rname, (rx0, ry0, rx1, ry1) in rects.items():
    print('\n== tracks/vias under %s (module body rect) ==' % rname)
    hits = []
    for t in b2.GetTracks():
        if t.Type() == pcbnew.PCB_TRACE_T:
            if seg_hits_rect(t.GetStart(), t.GetEnd(), rx0, ry0, rx1, ry1):
                s, e = t.GetStart(), t.GetEnd()
                hits.append('  trk %-14s %-5s w%.2f (%.2f,%.2f)->(%.2f,%.2f)' % (
                    t.GetNetname() or '(none)', t.GetLayerName()[:5], M(t.GetWidth()),
                    M(s.x), M(s.y), M(e.x), M(e.y)))
        elif t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            if rx0 <= p.x <= rx1 and ry0 <= p.y <= ry1:
                hits.append('  via %-14s at (%.2f,%.2f) OD%.2f' % (
                    t.GetNetname() or '(none)', M(p.x), M(p.y), M(t.GetWidth())))
    print('\n'.join(hits) if hits else '  (none)')
