# fix_sch_layout.py — ซ่อม .kicad_sch หลังบั๊ก batch_add_and_connect:
# อาการ: symbol instance ทั้งหมดถูกวางที่ (0,0) ทับกัน + label อยู่แถว origin → net หลอมรวม
# วิธี: ย้าย instance ไปเลย์เอาต์ใหม่ (A4 portrait), ลบ label เก่า, สร้าง label ใหม่ที่ pin endpoint
#       (sheet = (X + libx, Y - liby) ยืนยันจากไฟล์เดิมแล้ว), ย้าย no-connect ตาม pin ของมัน
import re, uuid, shutil

SCH = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_sch"
BAK = r"D:\Tracker\ST909B-4G\scripts\ST909B-4G.sch.bak-pre-layout"
TXT = open(SCH, encoding="utf-8").read()
shutil.copyfile(SCH, BAK)

# ---------- ข้อมูล pin (lib coords, Y-up) ยืนยันกับ label เดิม 17+5+8+17+6+3+3+8+6+2+2 จุดแล้ว ----------
PINS = {
    "ST909B:U1_A7670SA": {1: (-11.54, -10), 2: (-11.54, -7.5), 3: (-11.54, -5), 4: (-11.54, -2.5),
                          5: (-11.54, 0), 6: (-11.54, 2.5), 7: (11.54, -11.25), 8: (11.54, -9.25),
                          9: (11.54, -7.25), 10: (11.54, -5.25), 11: (11.54, -3.25), 12: (11.54, -1.25),
                          13: (11.54, 0.75), 14: (11.54, 2.75), 15: (11.54, 4.75), 16: (11.54, 6.75),
                          17: (11.54, 8.75)},
    "ST909B:U2_L76KB": {1: (-8.54, -3), 2: (-8.54, 0), 3: (-8.54, 3), 4: (8.54, -2.5), 5: (8.54, 2.5)},
    "ST909B:U3_TP4056": {1: (-9.54, -5.25), 2: (-9.54, -1.75), 3: (-9.54, 1.75), 4: (-9.54, 5.25),
                         5: (9.54, -5.25), 6: (9.54, -1.75), 7: (9.54, 1.75), 8: (9.54, 5.25)},
    "ST909B:U4_MCU_LQFP48": {1: (-13.54, -12), 2: (-13.54, -9), 3: (-13.54, -6), 4: (-13.54, -3),
                             5: (-13.54, 0), 6: (-13.54, 3), 7: (-13.54, 6), 8: (-13.54, 9),
                             9: (-13.54, 12), 10: (13.54, -10.5), 11: (13.54, -7.5), 12: (13.54, -4.5),
                             13: (13.54, -1.5), 14: (13.54, 1.5), 15: (13.54, 4.5), 16: (13.54, 7.5),
                             17: (13.54, 10.5)},
    "ST909B:U5_LEVELSHIFT": {1: (-8.54, -3), 2: (-8.54, 0), 3: (-8.54, 3),
                             4: (8.54, -3), 5: (8.54, 0), 6: (8.54, 3)},
    "ST909B:U6_LDO_SOT23": {3: (-7.54, 0), 2: (7.54, 0), 1: (0, 6.04)},
    "ST909B:U7_LEDDRV": {1: (-7.54, 0), 3: (7.54, 0), 2: (0, 6.04)},
    "ST909B:RN1_ARRAY4": {1: (-8.54, -2.625), 3: (-8.54, -0.875), 5: (-8.54, 0.875), 7: (-8.54, 2.625),
                          2: (8.54, -2.625), 4: (8.54, -0.875), 6: (8.54, 0.875), 8: (8.54, 2.625)},
    "ST909B:J1_SIM6": {"C1": (-8.54, -4.5), "C2": (-8.54, -1.5), "C3": (-8.54, 1.5), "C6": (-8.54, 4.5),
                       "C5": (8.54, -3), "C7": (8.54, 3)},
    "ST909B:J2_SERVICE4": {1: (-7.54, -3.375), 2: (-7.54, -1.125), 3: (-7.54, 1.125), 4: (-7.54, 3.375)},
    "ST909B:J6_SPK2": {1: (-6.54, -1.27), 2: (-6.54, 1.27)},
    "ST909B:PADS_ROW3": {1: (-7.54, -2), 2: (-7.54, 0), 3: (-7.54, 2)},
    "ST909B:ANT1_ANT4G": {1: (-6.54, -1.27), 2: (-6.54, 1.27)},
    "Device:R": {1: (0, 3.81), 2: (0, -3.81)},
    "Device:C_Polarized": {1: (0, 3.81), 2: (0, -3.81)},
    "Device:LED": {1: (-3.81, 0), 2: (3.81, 0)},
    "Switch:SW_Push": {1: (-5.08, 0), 2: (5.08, 0)},
    "Connector:TestPoint": {1: (0, 0)},
    "power:PWR_FLAG": {1: (0, 0)},
}

# ---------- net ต่อขา (ตาม PLAN ที่บอร์ดยืนยันแล้ว) ----------
NETS = {
    "U1": {1: "VBAT", 2: "VDD_EXT", 3: "MIC_P", 4: "MIC_N", 5: "SPK_P", 6: "SPK_N", 7: "ANT_4G_RF",
           8: "GND", 9: "4G_TXD_1V8", 10: "4G_RXD_1V8", 11: "USB_DP_F", 12: "USB_DM_F", 13: "USB_VBUS",
           14: "SIM_VDD", 15: "SIM_RST", 16: "SIM_CLK", 17: "SIM_DATA"},
    "U2": {1: "G3V3", 2: "GND", 3: "GPS_TX", 4: "GPS_RX", 5: "GPS_RF"},
    "U3": {1: "TEMP", 2: "PROG", 3: "GND", 4: "+5V", 5: "VBAT"},
    "U4": {1: "M3V3", 2: "GND", 3: "GPS_TX", 4: "GPS_RX", 5: "USB_DP_M", 6: "USB_DM_M", 7: "PKEY",
           8: "SOS", 9: "LED_EN", 10: "MCU_UTX4G", 11: "MCU_URX4G", 12: "LED_GPS", 13: "LED_CHR",
           14: "LED_4G", 15: "BOOT"},
    "U5": {1: "VDD_EXT", 2: "4G_TXD_1V8", 3: "4G_RXD_1V8", 4: "GND", 5: "4G_RXD_3V3", 6: "4G_TXD_3V3"},
    "U6": {3: "VBAT", 2: "G3V3", 1: "GND"},
    "U7": {1: "LED_EN", 3: "LED_K", 2: "GND"},
    "RN1": {1: "USB_DP_F", 2: "USB_DP_M", 3: "USB_DM_F", 4: "USB_DM_M"},
    "J1": {"C1": "SIM_VDD", "C2": "SIM_RST", "C3": "SIM_CLK", "C6": "SIM_VPP", "C5": "GND", "C7": "SIM_DATA"},
    "J2": {1: "GND", 2: "4G_TXD_3V3", 3: "4G_RXD_3V3", 4: "+5V"},
    "J3": {1: "USB_VBUS", 2: "USB_DP_F", 3: "USB_DM_F"},
    "J4": {1: "M3V3", 2: "M3V3", 3: "M3V3"},
    "J5": {1: "VBAT"},
    "J6": {1: "SPK_P", 2: "SPK_N"},
    "J7": {1: "BOOT", 2: "BOOT", 3: "GND"},
    "SW1": {1: "PKEY", 2: "GND"},
    "SW2": {1: "SOS", 2: "GND"},
    "ANT1": {1: "ANT_4G_RF", 2: "GND"},
    "AE2": {1: "GPS_RF"},
    "C1": {1: "VBAT", 2: "GND"},
    "TP1": {1: "GPS_TX"}, "TP2": {1: "GPS_RX"}, "TP3": {1: "GPS_RX"}, "TP4": {1: "QUECTEL_TP"},
    "TP5": {1: "MIC_P"}, "TP6": {1: "GND"}, "TP7": {1: "VBAT"}, "TP8": {1: "PKEY"},
    "R1": {1: "R1_A", 2: "R1_B"}, "R2": {1: "R2_A", 2: "R2_B"}, "R3": {1: "PROG", 2: "GND"},
    "LED1": {1: "LED_K", 2: "LED_GPS"}, "LED2": {1: "LED_K", 2: "LED_CHR"}, "LED3": {1: "LED_K", 2: "LED_4G"},
    "#FLG1": {1: "+5V"}, "#FLG2": {1: "GND"}, "#FLG3": {1: "VBAT"},
    "#FLG4": {1: "VDD_EXT"}, "#FLG5": {1: "SIM_VDD"}, "#FLG6": {1: "USB_VBUS"},
}

# ---------- เลย์เอาต์ใหม่ (A4 portrait 210x297) ----------
LAYOUT = {
    "U1": (30, 50), "U2": (30, 110), "U3": (30, 165), "U4": (30, 235),
    "J1": (95, 35), "J2": (95, 75), "J3": (95, 110), "J4": (95, 145), "J5": (95, 175),
    "J6": (95, 205), "J7": (95, 235),
    "U5": (150, 35), "U6": (150, 80), "U7": (150, 115), "RN1": (150, 150),
    "SW1": (150, 185), "SW2": (150, 215), "ANT1": (150, 245), "AE2": (150, 270),
    "C1": (190, 35), "TP1": (190, 60), "TP2": (190, 75), "TP3": (190, 90), "TP4": (190, 105),
    "TP5": (190, 125), "TP6": (190, 140), "TP7": (190, 155), "TP8": (190, 170),
    "R1": (190, 195), "R2": (190, 215), "R3": (190, 235),
    "LED1": (190, 255), "LED2": (190, 270), "LED3": (190, 283),
    "#FLG1": (30, 270), "#FLG2": (50, 270), "#FLG3": (70, 270),
    "#FLG4": (90, 270), "#FLG5": (110, 270), "#FLG6": (130, 270),
}

NC_PIN_SET = [("RN1", "5"), ("RN1", "6"), ("RN1", "7"), ("RN1", "8"),
              ("U4", "16"), ("U4", "17"), ("U3", "6"), ("U3", "7"), ("U3", "8")]

REF2LIB = {}


def fmt(v):
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return s if s else "0"


def paren_block(s, start):
    """start = index of '(' — return (block_text, end_index_after_close)"""
    depth, j = 0, start
    while j < len(s):
        if s[j] == "(":
            depth += 1
        elif s[j] == ")":
            depth -= 1
            if depth == 0:
                return s[start:j + 1], j + 1
        j += 1
    raise ValueError("unbalanced")


# ---------- 1) ย้าย symbol instances ----------
inst_spans = []  # (block_start, block_end, lib_id, ref, cx, cy)
for m in re.finditer(r'\(symbol\s+\(lib_id "([^"]+)"\)', TXT):
    blk, end = paren_block(TXT, m.start())
    refm = re.search(r'\(property "Reference" "([^"]+)"', blk)
    at = re.search(r'\(lib_id "[^"]+"\)\s*\(at ([\d.-]+) ([\d.-]+) ([\d.-]+)\)', blk)
    if not refm or not at:
        continue
    inst_spans.append((m.start(), end, m.group(1), refm.group(1),
                       float(at.group(1)), float(at.group(2)), at.group(3)))

print("instances found:", len(inst_spans))
missing = [s[3] for s in inst_spans if s[3] not in LAYOUT]
if missing:
    raise SystemExit("ไม่มีเลย์เอาต์สำหรับ: " + ",".join(missing))

new_txt = TXT
for start, end, lib_id, ref, cx, cy, rot in sorted(inst_spans, key=lambda x: -x[0]):
    blk = TXT[start:end]
    nx, ny = LAYOUT[ref]
    REF2LIB[ref] = lib_id
    newblk = re.sub(
        r'(\(lib_id "[^"]+"\)\s*\(at )([\d.-]+) ([\d.-]+)( ' + re.escape(rot) + r'\))',
        lambda mm: mm.group(1) + fmt(nx) + " " + fmt(ny) + mm.group(4),
        blk, count=1)
    new_txt = new_txt[:start] + newblk + new_txt[end:]
TXT = new_txt

# ---------- 2) ลบ label เดิมทั้งหมด (top-level, indent 1 tab) ----------
label_spans = []
i = 0
while True:
    i = TXT.find('\n\t(label "', i)
    if i < 0:
        break
    blk_start = i + 1  # ตัด \n ออก ให้ชี้ที่ '('
    blk, end = paren_block(TXT, blk_start)
    label_spans.append((i, end))
    i = end
print("labels to delete:", len(label_spans))
for a, b in sorted(label_spans, key=lambda x: -x[0]):
    TXT = TXT[:a] + TXT[b:]

# ---------- 3) ย้าย no-connect ----------
cur_pos = {}   # (ref, pin) -> (x,y) ณ ตำแหน่งเดิม
new_pos = {}   # (ref, pin) -> (x,y) ตำแหน่งใหม่
for ref, lib_id in REF2LIB.items():
    cx, cy = 0.0, 0.0  # ทุก instance เดิมอยู่ (0,0) — ยืนยันจากไฟล์
    nx, ny = LAYOUT[ref]
    for pin, (lx, ly) in PINS[lib_id].items():
        cur_pos[(ref, str(pin))] = (cx + lx, cy - ly)
        new_pos[(ref, str(pin))] = (nx + lx, ny - ly)

nc_spans = []
i = 0
while True:
    i = TXT.find("(no_connect", i)
    if i < 0:
        break
    blk, end = paren_block(TXT, i)
    nc_spans.append((i, end))
    i = end
print("no_connects:", len(nc_spans))
for start, end in sorted(nc_spans, key=lambda x: -x[0]):
    blk = TXT[start:end]
    am = re.search(r'\(at ([\d.-]+) ([\d.-]+)\)', blk)
    px, py = float(am.group(1)), float(am.group(2))
    owner = None
    for key, pos in cur_pos.items():
        if abs(pos[0] - px) < 1e-6 and abs(pos[1] - py) < 1e-6 and key in [(r, p) for r, p in NC_PIN_SET]:
            owner = key
            break
    if owner is None:
        print("  !! ไม่เจอเจ้าของ no_connect ที่", (px, py), "— ข้าม")
        continue
    nx, ny = new_pos[owner]
    newblk = blk.replace(am.group(0), f"(at {fmt(nx)} {fmt(ny)})", 1)
    TXT = TXT[:start] + newblk + TXT[end:]
    print(f"  moved NC {owner}: ({px},{py}) -> ({fmt(nx)},{fmt(ny)})")

# ---------- 4) สร้าง label ใหม่ ----------
def label_item(name, x, y, just):
    return (f'\t(label "{name}"\n'
            f'\t\t(at {fmt(x)} {fmt(y)} 0)\n'
            f'\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n'
            f'\t\t\t(justify {just} bottom)\n\t\t)\n'
            f'\t\t(uuid "{uuid.uuid4()}")\n\t)\n')

items = []
for ref, lib_id in REF2LIB.items():
    nx, ny = LAYOUT[ref]
    nets = NETS.get(ref, {})
    for pin, (lx, ly) in sorted(PINS[lib_id].items(), key=lambda kv: str(kv[0])):
        net = nets.get(pin)
        if not net:
            continue
        x, y = nx + lx, ny - ly
        just = "right" if lx < 0 else "left"
        items.append(label_item(net, x, y, just))
print("labels to create:", len(items))

# แทรกก่อนวงเล็บปิดท้ายไฟล์
close = TXT.rstrip()
assert close.endswith(")")
TXT = close[:-1] + "\n" + "\n".join(items) + ")\n"

open(SCH, "w", encoding="utf-8", newline="\n").write(TXT)
print("saved. backup at", BAK)
