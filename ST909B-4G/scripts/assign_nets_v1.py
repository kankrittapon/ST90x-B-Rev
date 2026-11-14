# assign_nets_v1.py — กำหนด net ให้ pad บนบอร์ด ST909B-4G โดยตรง (reconstruction v1)
# ใช้: D:\KiCad\10.0\bin\python.exe assign_nets_v1.py
# net ตามสันนิษฐานใน Front_PCB.md / Back_PCB.md (ทุก net ถูกกำกับสถานะใน README)
import pcbnew
import collections

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"

# net -> [(ref, pad_number), ...]  (components แบบ block ไม่มี pad เช่น U1/U2/U3/C1/J1 จึงไม่ปรากฏ)
PLAN = {
    "/VBAT": [("U6", "3"), ("J5", "1"), ("TP7", "1")],
    "/GND": [("U5", "4"), ("U6", "1"), ("U7", "2"), ("SW1", "2"), ("SW2", "2"),
             ("TP6", "1"), ("ANT1", "2"), ("J7", "3"), ("J2", "1"), ("U4", "2")],
    "/+5V": [("J2", "4")],
    "/4G_TXD_1V8": [("U5", "2")],
    "/4G_RXD_1V8": [("U5", "3")],
    "/4G_TXD_3V3": [("U5", "6"), ("J2", "2")],
    "/4G_RXD_3V3": [("U5", "5"), ("J2", "3")],
    "/MCU_UTX4G": [("U4", "10")],
    "/MCU_URX4G": [("U4", "11")],
    "/USB_DP_F": [("RN1", "1"), ("J3", "2")],
    "/USB_DP_M": [("RN1", "2"), ("U4", "5")],
    "/USB_DM_F": [("RN1", "3"), ("J3", "3")],
    "/USB_DM_M": [("RN1", "4"), ("U4", "6")],
    "/USB_VBUS": [("J3", "1")],
    "/G3V3": [("U6", "2")],
    "/VDD_EXT": [("U5", "1")],
    "/GPS_TX": [("TP1", "1"), ("U4", "3")],
    "/GPS_RX": [("TP2", "1"), ("TP3", "1"), ("U4", "4")],
    "/M3V3": [("J4", "1"), ("J4", "2"), ("J4", "3"), ("U4", "1")],
    "/PKEY": [("SW1", "1"), ("TP8", "1"), ("U4", "7")],
    "/SOS": [("SW2", "1"), ("U4", "8")],
    "/LED_EN": [("U7", "1")],
    "/LED_K": [("U7", "3"), ("LED1", "1"), ("LED2", "1"), ("LED3", "1")],
    "/LED_GPS": [("LED1", "2"), ("U4", "12")],
    "/LED_CHR": [("LED2", "2"), ("U4", "13")],
    "/LED_4G": [("LED3", "2"), ("U4", "14")],
    "/PROG": [("R3", "1")],
    "/QUECTEL_TP": [("TP4", "1")],
    "/MIC_P": [("TP5", "1")],
    "/SPK_P": [("J6", "1")],
    "/SPK_N": [("J6", "2")],
    "/BOOT": [("U4", "15"), ("J7", "1"), ("J7", "2")],
    "/R1_A": [("R1", "1")],
    "/R1_B": [("R1", "2")],
    "/R2_A": [("R2", "1")],
    "/R2_B": [("R2", "2")],
    "/ANT_4G_RF": [("ANT1", "1")],
}

b = pcbnew.LoadBoard(BOARD)
pads = {}
for fp in b.GetFootprints():
    for p in fp.Pads():
        pads[(fp.GetReference(), str(p.GetNumber()))] = p


def net_item(name):
    ni = b.FindNet(name)
    if ni is None:
        ni = pcbnew.NETINFO_ITEM(b, name)
        b.Add(ni)
    return ni


assigned, missing = 0, []
for netname, pairs in PLAN.items():
    ni = net_item(netname)
    for ref, pad in pairs:
        p = pads.get((ref, pad))
        if p is None:
            missing.append(f"{ref}/{pad}")
            continue
        try:
            p.SetNet(ni)
        except AttributeError:
            p.SetNetCode(ni.GetNetCode())
        assigned += 1

b.Save(BOARD)
print("assigned:", assigned)
print("missing pads:", missing if missing else "none")

# ตรวจซ้ำโดยโหลดใหม่
b2 = pcbnew.LoadBoard(BOARD)
nets = collections.defaultdict(list)
for fp in b2.GetFootprints():
    for p in fp.Pads():
        n = p.GetNetname()
        if n and not n.startswith("unconnected"):
            nets[n].append(f"{fp.GetReference()}/{p.GetNumber()}")
print("nets:", len(nets), "pads:", sum(len(v) for v in nets.values()))
for k in sorted(nets):
    print(" ", k, len(nets[k]), "->", ",".join(nets[k][:8]))
