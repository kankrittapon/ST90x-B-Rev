# p25_move_traces.py — P2.5: ย้าย trace/via ใต้โมดูล U1/U2 ออกนอกพื้นที่ + แก้ courtyard overlap (U6, TP4)
# หลักการ: F.Cu ห้ามมี copper ใต้ body โมดูล / B.Cu ใต้โมดูลยอมให้ได้ (ตามมติโครงการ)
# ทุกเส้นใหม่คำนวณ clearance กับ pad จริงจาก dump_all_pads แล้ว (min 0.2 mm)
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
M = pcbnew.ToMM
NM = 1e6
TOL = pcbnew.FromMM(0.06)
LAYER = {'F': pcbnew.F_Cu, 'B': pcbnew.B_Cu}

b = pcbnew.LoadBoard(BOARD)
print('board loaded')

# ---- ข้อมูล zone ที่ 3 (net ว่าง/ไม่ fill) เพื่อยืนยันว่าเป็น rule area อะไร ----
for i, z in enumerate(b.Zones()):
    bb = z.GetBoundingBox()
    flags = []
    for meth in ('GetIsRuleArea', 'GetIsKeepout', 'GetDoNotAllowCopper', 'GetDoNotAllowVias'):
        try:
            flags.append('%s=%s' % (meth, getattr(z, meth)()))
        except Exception:
            pass
    print('zone %d net=%-10s layer=%-5s bbox=(%.2f..%.2f, %.2f..%.2f) %s' % (
        i, z.GetNetname() or '-', z.GetLayerName(),
        M(bb.GetLeft()), M(bb.GetRight()), M(bb.GetTop()), M(bb.GetBottom()),
        ' '.join(flags)))

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


# (net, layer, [(x1,y1), (x2,y2)]) — ตำแหน่งจาก dump_nets_p25 (พิกัดบอร์ดจริง)
DEL_TRACKS = [
    ('/LED_EN', 'F', [(24.35, 59.75), (24.35, 12.20)]),
    ('/LED_GPS', 'F', [(23.70, 11.40), (11.71, 11.40)]),
    ('/LED_GPS', 'F', [(23.70, 61.25), (23.70, 11.40)]),
    ('/LED_4G', 'F', [(25.00, 68.25), (25.00, 14.65)]),
    ('/LED_4G', 'B', [(25.00, 14.65), (17.71, 14.65)]),
    ('/GPS_RX', 'F', [(9.50, 37.00), (9.50, 53.80)]),
    ('/GPS_RX', 'F', [(2.95, 34.50), (7.00, 34.50)]),
    ('/GPS_RX', 'F', [(2.95, 34.50), (2.95, 50.50)]),
    ('/GPS_RX', 'F', [(2.95, 50.50), (3.20, 50.50)]),
    ('/GPS_RX', 'F', [(3.20, 50.50), (3.20, 60.00)]),
    ('/GPS_RX', 'B', [(9.50, 53.80), (2.25, 53.80)]),
    ('/GPS_RX', 'B', [(7.00, 34.50), (7.00, 33.00)]),
    ('/LED_GPS', 'B', [(21.16, 61.25), (23.70, 61.25)]),
    ('/M3V3', 'F', [(10.50, 62.00), (10.50, 55.70)]),
    ('/M3V3', 'F', [(10.50, 55.70), (17.00, 55.70)]),
    ('/VBAT', 'F', [(6.50, 44.50), (5.94, 44.50)]),
    ('/VBAT', 'F', [(6.50, 65.00), (6.50, 44.50)]),
    ('/VBAT', 'F', [(5.00, 65.00), (6.50, 65.00)]),
]

DEL_VIAS = [
    ('/LED_EN', 24.35, 12.20),
    ('/LED_GPS', 23.70, 61.25),
    ('/LED_GPS', 11.71, 11.40),
    ('/LED_4G', 25.00, 14.65),
    ('/GPS_RX', 9.50, 53.80),
    ('/GPS_RX', 7.00, 34.50),
]

# (net, layer, width, [(x1,y1), (x2,y2)])
ADD_TRACKS = [
    # /LED_EN: ขึ้น corridor ตะวันตก x=26.0 (หลบ pad ขวา U1 ช่องว่าง 1.075)
    ('/LED_EN', 'F', 0.25, [(24.35, 59.75), (26.00, 59.75)]),
    ('/LED_EN', 'F', 0.25, [(26.00, 59.75), (26.00, 12.20)]),
    ('/LED_EN', 'B', 0.25, [(26.00, 12.20), (22.94, 12.20)]),
    # /LED_GPS: จาก U4.12 ขึ้น B.Cu → via (23.60,58.00) (หลบ via /USB_DP_M (22.40,58.45) ช่อง 0.68) →
    #   F.Cu x=23.60 ขึ้นถึง y=30.10 (นอก body 29.5, หลบ via /GPS_TX (22.90,30.80) ช่อง 0.275,
    #   หลบ U1 right pads ช่อง 1.175, RN1.8 ช่อง 1.175) → วนตะวันตก y=30.10 → x=0.75 → ขึ้น y=4.50 →
    #   via (11.71,4.50) → B.Cu ลง LED1.2 (contact)
    ('/LED_GPS', 'B', 0.25, [(21.16, 61.25), (23.60, 61.25)]),
    ('/LED_GPS', 'B', 0.25, [(23.60, 61.25), (23.60, 58.00)]),
    ('/LED_GPS', 'F', 0.25, [(23.60, 58.00), (23.60, 30.10)]),
    ('/LED_GPS', 'F', 0.25, [(23.60, 30.10), (0.75, 30.10)]),
    ('/LED_GPS', 'F', 0.25, [(0.75, 30.10), (0.75, 4.50)]),
    ('/LED_GPS', 'F', 0.25, [(0.75, 4.50), (11.71, 4.50)]),
    ('/LED_GPS', 'B', 0.25, [(11.71, 4.50), (11.71, 13.00)]),
    # /LED_4G: B.Cu ล้วน x=27.00 (หลบ via /LED_CHR (26.30,15.45) ช่อง 0.29, ไม่ตัด LED_CHR y15.45
    #   เพราะจบที่ 26.30, หลบ via /LED_EN (26.00,12.20) ช่อง 0.575; J6/J7 เป็น SMD F.Cu — B.Cu ใต้ pad ได้)
    ('/LED_4G', 'B', 0.25, [(25.00, 68.25), (27.00, 68.25)]),
    ('/LED_4G', 'B', 0.25, [(27.00, 68.25), (27.00, 14.90)]),
    ('/LED_4G', 'B', 0.25, [(27.00, 14.90), (17.71, 14.90)]),
    ('/LED_4G', 'B', 0.25, [(17.71, 14.90), (17.71, 14.65)]),
    # /GPS_RX: จาก TP2 ลงถึง via (9.50,45.50) เหนือ U2 → B.Cu ตะวันตก → เดิม (2.25,33..53.8) คงอยู่
    #   → ต่อลงถึง (2.25,58) → via → F.Cu เข้า TP3 จากทิศใต้
    ('/GPS_RX', 'F', 0.25, [(9.50, 37.00), (9.50, 45.50)]),
    ('/GPS_RX', 'B', 0.25, [(9.50, 45.50), (2.25, 45.50)]),
    ('/GPS_RX', 'B', 0.25, [(2.25, 53.80), (2.25, 58.00)]),
    ('/GPS_RX', 'F', 0.25, [(2.25, 58.00), (2.25, 60.00)]),
    ('/GPS_RX', 'F', 0.25, [(2.25, 60.00), (3.00, 60.00)]),
    # /M3V3: เลื่อนแนวนอนลง y=58.50 (หลบ SH1 pad (11.3,57.6)/(11.3,59.8) ช่อง 0.375/0.775)
    ('/M3V3', 'F', 0.25, [(10.50, 62.00), (10.50, 58.50)]),
    ('/M3V3', 'F', 0.25, [(10.50, 58.50), (17.00, 58.50)]),
    ('/M3V3', 'F', 0.25, [(17.00, 58.50), (17.00, 55.70)]),
    # /VBAT: ตัดเส้นตั้ง x=6.5 ใต้ U2 ทิ้ง → วนตะวันตก x=1.00 (หลบ TP4 ใหม่/GPS_RX via ช่อง 0.475)
    ('/VBAT', 'F', 0.30, [(6.50, 43.50), (1.00, 43.50)]),
    ('/VBAT', 'F', 0.30, [(1.00, 43.50), (1.00, 65.00)]),
    ('/VBAT', 'F', 0.30, [(1.00, 65.00), (5.00, 65.00)]),
]

ADD_VIAS = [
    ('/LED_EN', 26.00, 12.20),
    ('/LED_GPS', 23.60, 58.00),
    ('/LED_GPS', 11.71, 4.50),
    ('/LED_4G', 27.00, 14.90),
    ('/GPS_RX', 9.50, 45.50),
    ('/GPS_RX', 2.25, 58.00),
]

MOVE_FP = [('U6', 5.00, 43.50), ('TP4', 2.20, 40.60)]

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

# ---- ย้าย footprint (แก้ courtyard overlap) ----
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
