# p25d_clean.py — ลบเส้นผี /LED_GPS F.Cu (23.60,58.00)->(23.60,30.10)
# สาเหตุ: p25b DEL ใส่ layer เป็น 'B' แต่ของจริงเป็น 'F' (จึงลบได้แค่ 33/34)
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
M = pcbnew.ToMM
TOL = pcbnew.FromMM(0.06)

b = pcbnew.LoadBoard(BOARD)
code = b.FindNet('/LED_GPS').GetNetCode()
target = (pcbnew.FromMM(23.60), pcbnew.FromMM(58.00), pcbnew.FromMM(23.60), pcbnew.FromMM(30.10))
nd = 0
for t in list(b.GetTracks()):
    if t.Type() != pcbnew.PCB_TRACE_T or t.GetNetCode() != code:
        continue
    if t.GetLayerName() != 'F.Cu':
        continue
    s, e = t.GetStart(), t.GetEnd()
    if ((abs(s.x - target[0]) < TOL and abs(s.y - target[1]) < TOL and
         abs(e.x - target[2]) < TOL and abs(e.y - target[3]) < TOL) or
        (abs(s.x - target[2]) < TOL and abs(s.y - target[3]) < TOL and
         abs(e.x - target[0]) < TOL and abs(e.y - target[1]) < TOL)):
        b.Delete(t)
        nd += 1
print('deleted ghost tracks: %d' % nd)
b.Save(BOARD)
print('saved')

b2 = pcbnew.LoadBoard(BOARD)
left = 0
for t in b2.GetTracks():
    if t.GetNetname() == '/LED_GPS' and t.Type() == pcbnew.PCB_TRACE_T and t.GetLayerName() == 'F.Cu':
        s, e = t.GetStart(), t.GetEnd()
        print('remaining F.Cu /LED_GPS: (%.2f,%.2f)->(%.2f,%.2f)' % (
            M(s.x), M(s.y), M(e.x), M(e.y)))
        left += 1
print('remaining count: %d (ต้องเป็น 0)' % left)
