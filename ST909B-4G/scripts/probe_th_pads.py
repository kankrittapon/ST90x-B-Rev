# probe_th_pads.py — หา pad ที่มี drill (through-hole) ทั้งหมด + ชั้น copper จริงของ pad สำคัญ (อ่านอย่างเดียว)
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
M = pcbnew.ToMM
b = pcbnew.LoadBoard(BOARD)
print('board loaded')
n = 0
for fp in b.GetFootprints():
    rows = []
    for p in fp.Pads():
        try:
            dsz = p.GetDrillSize()
            d = M(min(dsz.x, dsz.y))
        except Exception:
            d = 0.0
        if d > 0:
            pos = p.GetPosition()
            rows.append('%s@d%.2f(%0.2f,%0.2f)' % (p.GetPadName(), d, M(pos.x), M(pos.y)))
            n += 1
    if rows:
        print('%-4s %s' % (fp.GetReference(), '  '.join(rows)))
print('total TH pads:', n)
# ชั้นจริงของ pad ตัวอย่าง (GetLayerSet)
for ref, nums in (('J7', ['1', '3']), ('J6', ['1']), ('SH1', ['1']), ('TP3', ['1']), ('TP4', ['1']), ('U4', ['9']), ('AE2', None), ('J1', None), ('C1', None), ('U3', None)):
    fp = b.FindFootprintByReference(ref)
    if fp is None:
        continue
    info = []
    for p in fp.Pads():
        nums_ = [p.GetPadName()] if nums is None else ([nums[0]] if p.GetPadName() == nums[0] else [])
        if not nums_:
            continue
        lay = []
        try:
            lay = [pcbnew.LayerName(x) for x in p.GetLayerSet().Seq()]
        except Exception:
            lay = ['?']
        info.append('pad%s layers=%s drill=%.2f' % (p.GetPadName(), ','.join(lay), M(min(p.GetDrillSize().x, p.GetDrillSize().y))))
    print('%-4s %s' % (ref, ' | '.join(info) if info else '(no pads)'))
print('done')
