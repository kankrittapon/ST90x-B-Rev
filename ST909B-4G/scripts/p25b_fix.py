# p25b_fix.py — P2.5b: แก้ 12 DRC error ที่เหลือ
# 1) items_not_allowed (9.50,45.50)  : ลบ /GPS_RX B.Cu ใน rule area zone2 + F.Cu/via ที่เกี่ยว
# 2) crossing (23.60,61.25)          : /LED_GPS ย้ายไป corridor x=32.80 (B.Cu ล้วน)
# 3) crossing (32.30,59.10)          : /LED_4G ย้ายไป corridor x=34.60
# 4-5,7-9) /LED_CHR zigzag ชน /LED_EN: LED_CHR เส้นตรง v x=25.40, LED_EN ขึ้น x=26.05 (via ใหม่ทั้งคู่ปลาย)
# 6) courtyards_overlap U6-J3        : U6 -> (5.00,44.90)
# 11-12) starved_thermal U1 pad1/2   : ลบ /LED_GPS F.Cu ฝั่งตะวันตก (โซน GND เชื่อมกลับ) — มาพร้อมข้อ 2
# + /BOOT: ตัด B.Cu loop เดิม (กั้น corridor x=32.80/34.60) → ใหม่ h y=68.90 จบ x=23.55, via (23.55,68.80)
#   F.Cu (23.55,68.80)->(27.00,68.80)->(27.00,27.20) ต่อเดิมเข้า J7.1
# + /LED_4G ช่วงเหนือข้าม x=32.80 ด้วย F.Cu hop (via (33.90,6.60)+(26.70,6.60)) เพราะ h y=6.00/6.60
#   ต้องข้าม LED_GPS v x=32.80 (ทั้งคู่ B.Cu ข้ามกันไม่ได้)
# ทุกช่องว่างตรวจกับ pad/track จริงแล้ว (min 0.2): รายละเอียดในไฟล์บันทึก P2.5b
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
M = pcbnew.ToMM
NM = 1e6
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


# (net, layer, [(x1,y1), (x2,y2)]) — พิกัดจาก dump_p25d (ground truth ปัจจุบัน)
DEL_TRACKS = [
    # /LED_GPS เดิม (F.Cu ใต้โมดูล + B.Cu x=23.60 ตัด LED_EN)
    ('/LED_GPS', 'B', [(21.16, 61.25), (23.60, 61.25)]),
    ('/LED_GPS', 'B', [(23.60, 61.25), (23.60, 58.00)]),
    ('/LED_GPS', 'B', [(23.60, 58.00), (23.60, 30.10)]),
    ('/LED_GPS', 'F', [(23.60, 30.10), (0.75, 30.10)]),
    ('/LED_GPS', 'F', [(0.75, 30.10), (0.75, 4.50)]),
    ('/LED_GPS', 'F', [(0.75, 4.50), (11.71, 4.50)]),
    ('/LED_GPS', 'B', [(11.71, 4.50), (11.71, 13.00)]),
    ('/LED_GPS', 'B', [(11.71, 11.40), (11.71, 13.00)]),
    # /LED_4G เดิม (v x=27.00 ตัด SOS y=59.10)
    ('/LED_4G', 'B', [(19.25, 68.25), (25.00, 68.25)]),
    ('/LED_4G', 'B', [(25.00, 68.25), (27.00, 68.25)]),
    ('/LED_4G', 'B', [(27.00, 68.25), (27.00, 14.90)]),
    ('/LED_4G', 'B', [(27.00, 14.90), (17.71, 14.90)]),
    ('/LED_4G', 'B', [(17.71, 14.90), (17.71, 14.65)]),
    ('/LED_4G', 'B', [(17.71, 14.65), (17.71, 13.00)]),
    # /LED_CHR zigzag F.Cu (ชน/ข้าม LED_EN) + B.Cu ปลาย x=26.30
    ('/LED_CHR', 'F', [(26.30, 23.00), (26.30, 15.45)]),
    ('/LED_CHR', 'F', [(25.50, 23.00), (26.30, 23.00)]),
    ('/LED_CHR', 'F', [(25.50, 28.00), (25.50, 23.00)]),
    ('/LED_CHR', 'F', [(26.30, 28.00), (25.50, 28.00)]),
    ('/LED_CHR', 'F', [(26.30, 67.60), (26.30, 28.00)]),
    ('/LED_CHR', 'B', [(26.30, 15.45), (14.71, 15.45)]),
    ('/LED_CHR', 'B', [(19.75, 62.66), (19.75, 67.60)]),
    ('/LED_CHR', 'B', [(19.75, 67.60), (26.30, 67.60)]),
    # /LED_EN เดิม (v x=26.00 ช่อง 0.05 กับ LED_CHR x=26.30 + ผ่าน via 26.30,15.45)
    ('/LED_EN', 'B', [(21.16, 59.75), (24.35, 59.75)]),
    ('/LED_EN', 'B', [(24.35, 12.20), (22.94, 12.20)]),   # ชิ้นค้าง (ปลาย x=24.35 ลอย)
    ('/LED_EN', 'B', [(26.00, 12.20), (22.94, 12.20)]),
    ('/LED_EN', 'F', [(24.35, 59.75), (26.00, 59.75)]),
    ('/LED_EN', 'F', [(26.00, 59.75), (26.00, 12.20)]),
    # /BOOT เดิม (h y=27.20 + v x=34.00 กั้น corridor ตะวันออก)
    ('/BOOT', 'B', [(18.75, 68.90), (34.00, 68.90)]),
    ('/BOOT', 'B', [(34.00, 27.20), (33.00, 27.20)]),
    ('/BOOT', 'B', [(34.00, 68.90), (34.00, 27.20)]),
    ('/BOOT', 'F', [(33.00, 27.20), (27.00, 27.20)]),
    # /GPS_RX: B.Cu ใน rule area zone2 + สายเข้า + via
    ('/GPS_RX', 'F', [(9.50, 37.00), (9.50, 45.50)]),
    ('/GPS_RX', 'B', [(9.50, 45.50), (2.25, 45.50)]),
    # /VBAT เดิม (y=43.50 ที่ตาม U6 เก่า)
    ('/VBAT', 'F', [(6.50, 43.50), (1.00, 43.50)]),
]

DEL_VIAS = [
    ('/LED_GPS', 23.60, 58.00),
    ('/LED_GPS', 11.71, 4.50),
    ('/LED_4G', 25.00, 68.25),
    ('/LED_4G', 27.00, 14.90),
    ('/LED_CHR', 26.30, 15.45),
    ('/LED_CHR', 26.30, 67.60),
    ('/LED_EN', 24.35, 59.75),
    ('/LED_EN', 26.00, 12.20),
    ('/BOOT', 33.00, 27.20),
    ('/GPS_RX', 9.50, 45.50),
]

# (net, layer, width, [(x1,y1), (x2,y2)])
ADD_TRACKS = [
    # /LED_GPS: B.Cu ล้วน — U4.12 → h y=61.90 → v x=32.80 (ช่องระหว่าง SOS v2 32.425 กับ VBAT 33.15)
    #   → h y=4.80 ลอดใต้ SOS v2 (เริ่ม 9.875)/SW2 (เริ่ม 6.90) → v x=11.71 ลง LED1.2
    ('/LED_GPS', 'B', 0.25, [(21.16, 61.25), (21.16, 61.90)]),
    ('/LED_GPS', 'B', 0.25, [(21.16, 61.90), (32.80, 61.90)]),
    ('/LED_GPS', 'B', 0.25, [(32.80, 61.90), (32.80, 4.80)]),
    ('/LED_GPS', 'B', 0.25, [(32.80, 4.80), (11.71, 4.80)]),
    ('/LED_GPS', 'B', 0.25, [(11.71, 4.80), (11.71, 13.00)]),
    # /LED_4G: U4.14 → h y=68.10 (ช่อง LED_CHR 67.40 กับ /BOOT 68.90) → v x=34.60 (ช่อง /BOOT 34.125 กับขอบ 35.0)
    #   → ลดถึง y=6.60 → via (33.90,6.60) ขึ้น F.Cu ข้าม LED_GPS v x=32.80 → via (26.70,6.60) ลง B.Cu
    #   → v x=26.70 ลง 14.90 → h y=14.90 ไป LED3.2 (17.71)
    ('/LED_4G', 'B', 0.25, [(19.25, 62.66), (19.25, 68.10)]),
    ('/LED_4G', 'B', 0.25, [(19.25, 68.10), (34.60, 68.10)]),
    ('/LED_4G', 'B', 0.25, [(34.60, 68.10), (34.60, 6.60)]),
    ('/LED_4G', 'B', 0.25, [(34.60, 6.60), (33.90, 6.60)]),
    ('/LED_4G', 'F', 0.25, [(33.90, 6.60), (26.70, 6.60)]),
    ('/LED_4G', 'B', 0.25, [(26.70, 6.60), (26.70, 14.90)]),
    ('/LED_4G', 'B', 0.25, [(26.70, 14.90), (17.71, 14.90)]),
    # /LED_CHR: F.Cu เส้นตรง v x=25.40 (นอก body U1 ขอบ 25.00, ช่อง 0.40 กับ LED_EN x=26.05,
    #   0.875 กับ J7.1, 0.475 กับ pad U1 24.80) ต่อ via ปลายบน (25.40,15.70) [เว้น 0.375 จาก LED_4G y=14.90]
    #   ปลายล่าง via (25.40,67.40) [ช่อง 0.275 จาก LED_4G y=68.10]
    ('/LED_CHR', 'F', 0.25, [(25.40, 15.70), (25.40, 67.40)]),
    ('/LED_CHR', 'B', 0.25, [(25.40, 15.45), (14.71, 15.45)]),
    ('/LED_CHR', 'B', 0.25, [(19.75, 62.66), (19.75, 67.40)]),
    ('/LED_CHR', 'B', 0.25, [(19.75, 67.40), (25.40, 67.40)]),
    # /LED_EN: U4.9 B.Cu h y=59.75 ตรงถึง x=26.05 (ช่อง 0.25 จาก SOS stub y=59.25) → via (26.05,59.75)
    #   → F.Cu v x=26.05 ขึ้น (ช่อง 0.225 กับ J7.1, 1.125 กับ pad U1, 0.70 กับ /BOOT v x=27.00)
    #   → via (26.05,12.20) → B.Cu h y=12.20 เข้า U7.1
    ('/LED_EN', 'B', 0.25, [(21.16, 59.75), (26.05, 59.75)]),
    ('/LED_EN', 'F', 0.25, [(26.05, 59.75), (26.05, 12.20)]),
    ('/LED_EN', 'B', 0.25, [(26.05, 12.20), (22.94, 12.20)]),
    # /BOOT: B.Cu v x=18.75 เดิมค้าง → h y=68.90 จบ x=23.55 → via (23.55,68.80)
    #   [ช่อง 0.275 จาก LED_4G y=68.10 และ VBAT y=69.50] → F.Cu ขึ้น x=27.00 ถึง 27.20 ต่อเดิมเข้า J7.1
    ('/BOOT', 'B', 0.25, [(18.75, 68.90), (23.55, 68.90)]),
    ('/BOOT', 'F', 0.25, [(23.55, 68.80), (27.00, 68.80)]),
    ('/BOOT', 'F', 0.25, [(27.00, 68.80), (27.00, 27.20)]),
    # /VBAT: จากแนว v x=1.00 เดิม ตรง y=44.90 เข้า U6.3 (ตำแหน่งใหม่)
    ('/VBAT', 'F', 0.30, [(1.00, 43.50), (1.00, 44.90)]),
    ('/VBAT', 'F', 0.30, [(1.00, 44.90), (5.94, 44.90)]),
]

ADD_VIAS = [
    ('/LED_4G', 33.90, 6.60),
    ('/LED_4G', 26.70, 6.60),
    ('/LED_CHR', 25.40, 15.70),
    ('/LED_CHR', 25.40, 67.40),
    ('/LED_EN', 26.05, 59.75),
    ('/LED_EN', 26.05, 12.20),
    ('/BOOT', 23.55, 68.80),
]

MOVE_FP = [('U6', 5.00, 44.90)]

# ---- ลบ ----
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

# ---- ย้าย footprint ----
for ref, x, y in MOVE_FP:
    fp = b.FindFootprintByReference(ref)
    assert fp is not None, ref
    old = fp.GetPosition()
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    print('moved %s (%.2f,%.2f) -> (%.2f,%.2f)' % (ref, M(old.x), M(old.y), x, y))

# ---- เพิ่มใหม่ ----
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

# ---- ตรวจซ้ำโดยโหลดใหม่: F.Cu ใต้ body โมดูลต้อง = 0 ----
b2 = pcbnew.LoadBoard(BOARD)
U1 = b2.FindFootprintByReference('U1').GetPosition()
U2 = b2.FindFootprintByReference('U2').GetPosition()
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
    for t in b2.GetTracks():
        if t.Type() == pcbnew.PCB_TRACE_T:
            lay = t.GetLayerName()
            if seg_hits(t.GetStart(), t.GetEnd(), r):
                if lay == 'F.Cu':
                    s, e = t.GetStart(), t.GetEnd()
                    hits_f.append('%s (%.2f,%.2f)->(%.2f,%.2f)' % (
                        t.GetNetname(), M(s.x), M(s.y), M(e.x), M(e.y)))
                else:
                    hits_b += 1
        elif t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            if r[0] <= p.x <= r[2] and r[1] <= p.y <= r[3]:
                hits_f.append('VIA %s (%.2f,%.2f)' % (t.GetNetname(), M(p.x), M(p.y)))
    print('== %s: F.Cu hits %d (ต้องเป็น 0), B.Cu tracks %d (อนุญาต)' % (rname, len(hits_f), hits_b))
    for h in hits_f:
        print('   !! ' + h)

for ref in ('U6', 'TP4'):
    fp = b2.FindFootprintByReference(ref)
    p = fp.GetPosition()
    print('%s at (%.2f,%.2f)' % (ref, M(p.x), M(p.y)))
print('done')
