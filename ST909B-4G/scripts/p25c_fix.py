# p25c_fix.py — P2.5b รอบ 2: แก้ 6 DRC error ที่เหลือ
# 1-3) copper_edge_clearance x3: /LED_4G เส้นใหม่ v x=34.30 (ขอบตะวันออก 34.425, เว้นขอบ 0.575)
#      แทน 34.60 (ล้ำขอบ 0.275) — คงเส้นเดิมจาก U4.14 ถึงมุม (19.25,68.10)
# 4) tracks_crossing: ลด x=26.70 ตัด SOS h_top y=10.00 → เลี่ยงด้วย F.Cu hop:
#      B.Cu v x=34.30 ถึง y=6.90 → via (33.90,6.90) → F.Cu h y=6.90 (33.90→25.40)
#      [north row U1 pad52-60 อยู่ x 13..21 ไม่รบกวน] → F.Cu v x=25.40 (6.90→14.80)
#      [โครidor ระหว่าง U1 east pads 24.80 กับ J7 pad1 26.40; LED_EN v x=26.05 เว้น 0.40]
#      → via (25.40,14.80) → B.Cu h y=14.80 → v x=17.71 ลง LED3.2 (13.00)
#      (via x=25.40 ไม่ใช่ 25.55 เพราะ 25.55 ชน LED_EN v x=26.05 เหลือ 0.075 < 0.2)
# 5) courtyards_overlap U6xU2: U6 CrtYd จริง 43.20..46.59 ล้ำ U2 CrtYd 46.10 อยู่ 0.49
#      → ย้าย U6 (5.00,44.90)→(5.00,44.15): CrtYd 42.45..45.84 เว้น U2 0.26 / J3 0.44
#      + ปรับ /VBAT: ลบ v(1.00,43.50→44.90) h(y=44.90) v(1.00,43.50→65.00)
#        เพิ่ม v(1.00,44.15→65.00) h(y=44.15 เข้า U6.3) — pad1/2 เว้น 0.50
#      + ลบเส้นค้างซ้ำ (19.25,62.66)→(19.25,68.25)
# 6) starved_thermal pad39: U1 pad39 ล้อมรอบด้วย pad ไร้เน็ต (ช่อง 0.40 กลืนด้วย clearance 0.2x2)
#      และ E โดน LED_CHR/LED_EN ปิด → spoke ได้แค่ W (1/2) → ตั้ง zone connection ของ pad39
#      เป็น FULL (แผ่นทองแดงเชื่อมตรง — มาตรฐาน RF module GND) ไม่ต้องมี spoke
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
M = pcbnew.ToMM
TOL = pcbnew.FromMM(0.06)
LAYER = {'F': pcbnew.F_Cu, 'B': pcbnew.B_Cu}

b = pcbnew.LoadBoard(BOARD)
print('board loaded')
codes = {}


def nc(name):
    if name not in codes:
        n = b.FindNet(name)
        assert n, 'net %s missing' % name
        codes[name] = n.GetNetCode()
    return codes[name]


def seg_match(t, net, lay, seg):
    if t.GetNetCode() != nc(net) or t.GetLayer() != LAYER[lay]:
        return False
    (x1, y1), (x2, y2) = seg
    x1, y1, x2, y2 = (pcbnew.FromMM(x1), pcbnew.FromMM(y1),
                      pcbnew.FromMM(x2), pcbnew.FromMM(y2))
    s, e = t.GetStart(), t.GetEnd()
    return ((abs(s.x - x1) < TOL and abs(s.y - y1) < TOL and abs(e.x - x2) < TOL and abs(e.y - y2) < TOL) or
            (abs(s.x - x2) < TOL and abs(s.y - y2) < TOL and abs(e.x - x1) < TOL and abs(e.y - y1) < TOL))


DEL_TRACKS = [
    ('/LED_4G', 'F', [(33.90, 6.60), (26.70, 6.60)]),
    ('/LED_4G', 'B', [(34.60, 68.10), (34.60, 6.60)]),
    ('/LED_4G', 'B', [(34.60, 6.60), (33.90, 6.60)]),
    ('/LED_4G', 'B', [(26.70, 6.60), (26.70, 14.90)]),
    ('/LED_4G', 'B', [(26.70, 14.90), (17.71, 14.90)]),
    ('/LED_4G', 'B', [(19.25, 62.66), (19.25, 68.25)]),   # เส้นค้างซ้ำ
    ('/LED_4G', 'B', [(19.25, 68.10), (34.60, 68.10)]),
    ('/VBAT', 'F', [(1.00, 43.50), (1.00, 44.90)]),
    ('/VBAT', 'F', [(1.00, 44.90), (5.94, 44.90)]),
    ('/VBAT', 'F', [(1.00, 43.50), (1.00, 65.00)]),
]
DEL_VIAS = [
    ('/LED_4G', 33.90, 6.60),
    ('/LED_4G', 26.70, 6.60),
]
ADD_TRACKS = [
    ('/LED_4G', 'B', 0.25, [(19.25, 68.10), (34.30, 68.10)]),
    ('/LED_4G', 'B', 0.25, [(34.30, 68.10), (34.30, 6.90)]),
    ('/LED_4G', 'B', 0.25, [(34.30, 6.90), (33.90, 6.90)]),
    ('/LED_4G', 'F', 0.25, [(33.90, 6.90), (25.40, 6.90)]),
    ('/LED_4G', 'F', 0.25, [(25.40, 6.90), (25.40, 14.80)]),
    ('/LED_4G', 'B', 0.25, [(25.40, 14.80), (17.71, 14.80)]),
    ('/LED_4G', 'B', 0.25, [(17.71, 14.80), (17.71, 13.00)]),
    ('/VBAT', 'F', 0.30, [(1.00, 44.15), (1.00, 65.00)]),
    ('/VBAT', 'F', 0.30, [(1.00, 44.15), (5.94, 44.15)]),
]
ADD_VIAS = [
    ('/LED_4G', 33.90, 6.90),
    ('/LED_4G', 25.40, 14.80),
]
MOVE_FP = [('U6', 5.00, 44.15)]

nd = 0
for t in list(b.GetTracks()):
    if t.Type() != pcbnew.PCB_TRACE_T:
        continue
    for net, lay, seg in DEL_TRACKS:
        if seg_match(t, net, lay, seg):
            b.Delete(t)
            nd += 1
            break
vd = 0
for t in list(b.GetTracks()):
    if t.Type() != pcbnew.PCB_VIA_T:
        continue
    for net, x, y in DEL_VIAS:
        if (t.GetNetCode() == nc(net) and abs(t.GetPosition().x - pcbnew.FromMM(x)) < TOL
                and abs(t.GetPosition().y - pcbnew.FromMM(y)) < TOL):
            b.Delete(t)
            vd += 1
            break
print('deleted tracks %d/%d, vias %d/%d' % (nd, len(DEL_TRACKS), vd, len(DEL_VIAS)))

for ref, x, y in MOVE_FP:
    fp = b.FindFootprintByReference(ref)
    assert fp is not None, ref
    old = fp.GetPosition()
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    print('moved %s (%.2f,%.2f) -> (%.2f,%.2f)' % (ref, M(old.x), M(old.y), x, y))

# pad39: zone connection FULL
conn = None
for nm in ('ZONE_CONNECTION_FULL', 'PAD_ZONE_CONN_FULL'):
    if hasattr(pcbnew, nm):
        conn = getattr(pcbnew, nm)
        break
assert conn is not None, 'no FULL enum'
u1 = b.FindFootprintByReference('U1')
p39 = None
for pad in u1.Pads():
    if pad.GetName() == '39':
        p39 = pad
        break
assert p39 is not None
p39.SetLocalZoneConnection(conn)
print('pad39 zone conn set, readback=%s' % p39.GetLocalZoneConnection())

na = 0
for net, lay, width, seg in ADD_TRACKS:
    (x1, y1), (x2, y2) = seg
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
    t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
    t.SetWidth(pcbnew.FromMM(width))
    t.SetLayer(LAYER[lay])
    t.SetNetCode(nc(net))
    b.Add(t)
    na += 1
va = 0
for net, x, y in ADD_VIAS:
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetWidth(pcbnew.FromMM(0.6))
    v.SetDrill(pcbnew.FromMM(0.3))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNetCode(nc(net))
    assert v.GetNetname() == net, (net, v.GetNetname())
    b.Add(v)
    va += 1
print('added tracks %d/%d, vias %d/%d' % (na, len(ADD_TRACKS), va, len(ADD_VIAS)))

b.Save(BOARD)
print('saved')
