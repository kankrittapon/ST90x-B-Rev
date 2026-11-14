# net_check.py — parse kicad-cli netlist export แล้วเทียบกับ PLAN (assign_nets_v1.py)
import re, collections, importlib.util

TXT = open(r"D:\Tracker\ST909B-4G\scripts\net_check.kicad_nlt", encoding="utf-8").read()

nets = collections.defaultdict(list)
i = 0
while True:
    i = TXT.find("(net", i)
    if i < 0:
        break
    # ต้องเป็น token จริง: ตามด้วยช่องว่าง/ขึ้นบรรทัด
    if TXT[i+4] not in " \t\r\n":
        i += 4
        continue
    depth = 0
    j = i
    while j < len(TXT):
        if TXT[j] == "(":
            depth += 1
        elif TXT[j] == ")":
            depth -= 1
            if depth == 0:
                blocks = TXT[i:j+1]
                nm = re.search(r'\(name "([^"]+)"\)', blocks)
                if nm:
                    for n in re.finditer(
                        r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)',
                        blocks, re.S,
                    ):
                        nets[nm.group(1)].append(n.group(1) + "/" + n.group(2))
                break
        j += 1
    i = j + 1

print("nets:", len(nets))
for k in sorted(nets):
    print(" ", k, len(nets[k]), "->", ",".join(nets[k][:12]))

# --- เทียบกับ PLAN ---
spec = importlib.util.spec_from_file_location(
    "assign_nets_v1", r"D:\Tracker\ST909B-4G\scripts\assign_nets_v1.py")
# อ่าน PLAN โดยไม่รัน pcbnew: ดึง dict ด้วย regex จากไฟล์ script
src = open(r"D:\Tracker\ST909B-4G\scripts\assign_nets_v1.py", encoding="utf-8").read()
plan = {}
for m in re.finditer(r'"(/[^"]+)":\s*\[((?:\s*\("[^"]+",\s*"[^"]+"\),?)+)\]', src):
    name = m.group(1)
    pairs = re.findall(r'\("([^"]+)",\s*"([^"]+)"\)', m.group(2))
    plan[name] = [(r, p) for r, p in pairs]

schem = {k.lstrip("/"): set(v) for k, v in nets.items()}
want = {k.lstrip("/"): set(f"{r}/{p}" for r, p in v) for k, v in plan.items()}

print()
print("=== เทียบกับ PLAN ===")
ok = diff = extra = 0
for name in sorted(set(schem) | set(want)):
    a, b = schem.get(name, set()), want.get(name, set())
    if name not in want:
        extra += 1
        print(f"  เกินจาก PLAN: {name} -> {sorted(a)}")
    elif name not in schem:
        diff += 1
        print(f"  หายจาก schematic: {name} (PLAN: {sorted(b)})")
    elif a == b:
        ok += 1
    else:
        diff += 1
        print(f"  ต่าง: {name}\n    sch-only: {sorted(a - b)}\n    plan-only: {sorted(b - a)}")
print(f"ตรง {ok} | ต่าง {diff} | เกิน {extra}")
