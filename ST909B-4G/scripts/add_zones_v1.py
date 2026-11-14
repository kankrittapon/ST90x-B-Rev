# add_zones_v1.py — โซน GND สองด้าน + rule area (keepout) ครอบพื้นที่เสาอากาศ GPS ฝั่ง B.Cu
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
b = pcbnew.LoadBoard(BOARD)

def find_net(base_name):
    for n in b.GetNetsByName().values():
        if n.GetNetname().lstrip("/") == base_name:
            return n
    return None

gnd = find_net("GND")
assert gnd is not None, "ไม่พบ net GND"
print("GND netcode =", gnd.GetNetCode())

NM = 1_000_000

def rect_zone(zone, x0, y0, x1, y1):
    ol = zone.Outline()
    ol.NewOutline()
    for (x, y) in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
        ol.Append(int(x * NM), int(y * NM))

# ---- 1) โซน GND ฝั่ง F.Cu และ B.Cu (ขอบเขต 0.5 จากขอบบอร์ด = edge clearance พอดี 0.5)
for layer, name in [(pcbnew.F_Cu, "GND_zone_F"), (pcbnew.B_Cu, "GND_zone_B")]:
    z = pcbnew.ZONE(b)
    z.SetLayer(layer)
    z.SetNetCode(gnd.GetNetCode())
    rect_zone(z, 0.5, 0.5, 34.5, 73.5)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(int(0.3 * NM))
    z.SetThermalReliefSpokeWidth(int(0.3 * NM))
    z.SetLocalClearance(int(0.2 * NM))
    z.SetIsFilled(False)
    b.Add(z)
    print("added zone", name)

# ---- 2) rule area ฝั่ง B.Cu ครอบแผ่นเสาอากาศ GPS (AE2) — ห้ามทองแดง fill/track/pad แต่ยอมให้ via (GPS_RF)
k = pcbnew.ZONE(b)
k.SetLayer(pcbnew.B_Cu)
k.SetIsRuleArea(True)
k.SetDoNotAllowZoneFills(True)
k.SetDoNotAllowTracks(True)
k.SetDoNotAllowPads(True)
k.SetDoNotAllowVias(False)
k.SetDoNotAllowFootprints(False)
rect_zone(k, 2.5, 35.0, 20.5, 53.0)
b.Add(k)
print("added rule area (B.Cu keepout) 2.5..20.5 x 35..53")

# ---- 3) เติมทองแดง
ok = pcbnew.ZONE_FILLER(b).Fill(b.Zones())
print("fill ok =", ok)
b.Save(BOARD)
print("saved")

# รายงานผล
for z in b.Zones():
    if z.GetIsRuleArea():
        continue
    print(f"zone net={z.GetNetname()} layer={pcbnew.LayerName(z.GetLayer())} filled={z.GetIsFilled()}")
