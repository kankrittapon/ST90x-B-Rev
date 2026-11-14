# fix_pin_types.py — แก้ pin electrical type ที่เลือกผิดตอนสร้าง symbol
# ทำใน 2 ไฟล์: (lib_symbols ...) ฝังใน .kicad_sch (ERC ใช้ตัวนี้) และ lib\ST909B.kicad_sym
import re, shutil

EDITS = {  # symbol -> {pin_name: new_type}
    "U2_L76KB": {"TX": "output"},
    "U5_LEVELSHIFT": {"A1": "bidirectional", "A2": "bidirectional", "GND": "passive"},
    "U1_A7670SA": {"GND": "passive", "VBUS": "passive", "SIM_VDD": "passive"},
    "U4_MCU_LQFP48": {"GND": "passive"},
}

FILES = [
    (r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_sch", "ST909B:{name}"),
    (r"D:\Tracker\ST909B-4G\lib\ST909B.kicad_sym", "{name}"),
]


def paren_block(s, start):
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


for path, namepat in FILES:
    TXT = open(path, encoding="utf-8").read()
    changed = []
    for sym, pins in EDITS.items():
        token = namepat.format(name=sym)
        m = re.search(r'\(symbol "' + re.escape(token) + '"', TXT)
        if not m:
            print(f"!! ไม่เจอ symbol {token} ใน {path}")
            continue
        blk_start = m.start()
        blk, blk_end = paren_block(TXT, blk_start)
        newblk = blk
        for pinname, newtype in pins.items():
            # หา pin block ที่ (name "<pinname>" อยู่ข้างใน
            pm = re.search(r'\(pin (\w+) (\w+)(?=[\s\r\n])', newblk)
            found = False
            for p in re.finditer(r'\(pin (\w+) (\w+)', newblk):
                pb, pend = paren_block(newblk, p.start())
                if re.search(r'\(name "' + re.escape(pinname) + '"', pb):
                    newpb = re.sub(r'^\(pin \w+ ', f"(pin {newtype} ", pb, count=1)
                    newblk = newblk[:p.start()] + newpb + newblk[pend:]
                    changed.append(f"{sym}/{pinname}: {p.group(1)} -> {newtype}")
                    found = True
                    break
            if not found:
                print(f"!! ไม่เจอ pin {sym}/{pinname}")
        TXT = TXT[:blk_start] + newblk + TXT[blk_end:]
    open(path, "w", encoding="utf-8", newline="\n").write(TXT)
    print(path, "->", changed)

print("done")
