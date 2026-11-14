# place_fence_via_fill_v1.py — วางรั้งชิลด์ SH1 (GND) + via GPS_RF + เติมโซนใหม่
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
LIB = r"D:\Tracker\ST909B-4G\lib\ST909B.pretty"
NM = 1_000_000

b = pcbnew.LoadBoard(BOARD)

def find_net(base_name):
    for n in b.GetNetsByName().values():
        if n.GetNetname().lstrip("/") == base_name:
            return n
    return None

gnd = find_net("GND")
gps = find_net("GPS_RF")
assert gnd is not None, "ไม่พบ GND"
if gps is None:
    gps = pcbnew.NETINFO_ITEM(b, "GPS_RF")
    b.Add(gps)
    print("สร้าง net GPS_RF ใหม่ (netcode", gps.GetNetCode(), ")")

# ---- วางรั้ง (ถ้ามี SH1 อยู่แล้ว ให้ข้าม)
existing = [fp for fp in b.GetFootprints() if fp.GetReference() == "SH1"]
if not existing:
    fp = pcbnew.FootprintLoad(LIB, "SHIELD_FENCE")
    assert fp is not None, "โหลด SHIELD_FENCE ไม่ได้"
    b.Add(fp)
    fp.SetPosition(pcbnew.VECTOR2I(int(11.3 * NM), int(57.6 * NM)))
    try:
        fp.SetReference("SH1")
    except Exception as e:
        print("SetReference failed:", e)
    for p in fp.Pads():
        p.SetNet(gnd)
    print("placed SH1 at (11.3,57.6), pads:", len(list(fp.Pads())))
else:
    fp = existing[0]
    print("SH1 มีอยู่แล้ว")

# ตรวจพิกัด pad บนบอร์ด
print("SH1 pads:", " ".join(f"{p.GetNumber()}:({p.GetPosition().x / NM:.2f},{p.GetPosition().y / NM:.2f})" for p in fp.Pads()))

# ---- via GPS_RF ที่กึ่งกลางแผ่นเสาอากาศ (11.5,44) Ø0.6/เจาะ0.3
has = any(v.GetPosition().x == int(11.5 * NM) and v.GetPosition().y == int(44.0 * NM) for v in b.GetTracks() if isinstance(v, pcbnew.VIA))
if not has:
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(pcbnew.VECTOR2I(int(11.5 * NM), int(44.0 * NM)))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetWidth(int(0.6 * NM))
    v.SetDrill(int(0.3 * NM))
    v.SetNetCode(gps.GetNetCode())
    b.Add(v)
    print("added via GPS_RF at (11.5,44)")
else:
    print("via มีอยู่แล้ว")

# ---- เติมโซนใหม่ (รั้งต้องต่อ GND โซนด้าน B)
ok = pcbnew.ZONE_FILLER(b).Fill(b.Zones())
print("fill ok =", ok)
b.Save(BOARD)
print("saved")
