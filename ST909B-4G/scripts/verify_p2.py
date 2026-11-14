# verify_p2.py — ตรวจสถานะบอร์ดหลัง swap (อ่านอย่างเดียว, ไม่มี call ที่ assert ได้)
# ที่มาปัญหา: PCB_VIA::GetWidth() ไม่ใส่ layer -> wx assert -> ค้าง; สคริปต์นี้ไม่แตะ GetWidth ของ via
import pcbnew
import collections

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
M = pcbnew.ToMM

b = pcbnew.LoadBoard(BOARD)
print('board loaded')

total = 0
refs = collections.Counter()
for fp in b.GetFootprints():
    refs[fp.GetReference()] += 1
    total += len(list(fp.Pads()))
print('total pads:', total)
dup = {k: v for k, v in refs.items() if v > 1}
print('duplicate refs:', dup if dup else 'none')

for ref in ('U1', 'U2'):
    fp = b.FindFootprintByReference(ref)
    if fp is None:
        print(ref, 'MISSING')
        continue
    pos = fp.GetPosition()
    nets = collections.Counter(p.GetNetname() or '(none)' for p in fp.Pads())
    print('%s fp=%s value=%s pads=%d pos=(%.2f,%.2f) rot=%.1f' % (
        ref, fp.GetFPIDAsString(), fp.GetValue(), len(list(fp.Pads())),
        M(pos.x), M(pos.y), fp.GetOrientationDegrees()))
    for n, c in sorted(nets.items()):
        print('   %-18s %d' % (n, c))
    p1 = fp.FindPadByNumber('1')
    if p1 is not None:
        print('   pad1 abs (%.3f, %.3f)' % (M(p1.GetPosition().x), M(p1.GetPosition().y)))

print('new nets exist:')
for w in ('/USB_BOOT', '/UART_LOG_RX', '/UART_LOG_TX', '/SIM_VDD',
          '/SIM_DATA', '/SIM_CLK', '/SIM_RST', '/SIM_DET'):
    ni = b.FindNet(w)
    print('   %-14s %s' % (w, 'ok' if ni is not None else 'MISSING'))

zones = list(b.Zones())
print('zones:', len(zones))
for z in zones:
    try:
        filled = z.IsFilled()
    except Exception:
        filled = '?'
    try:
        net = z.GetNetname()
    except Exception:
        net = '?'
    print('   net %-12s filled=%s' % (net, filled))
print('done')
