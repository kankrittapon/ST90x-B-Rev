# dump_wires.py — สรุป wire/label ทั้งไฟล์: นับ + ช่วงพิกัด + กลุ่มที่ซ้ำกัน
import re, collections

SCH = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_sch"
TXT = open(SCH, encoding="utf-8").read()

def blocks(tok):
    out, i = [], 0
    while True:
        i = TXT.find("(" + tok, i)
        if i < 0:
            break
        if TXT[i + len(tok) + 1] not in " \t\r\n":
            i += len(tok)
            continue
        depth, j = 0, i
        while j < len(TXT):
            if TXT[j] == "(":
                depth += 1
            elif TXT[j] == ")":
                depth -= 1
                if depth == 0:
                    out.append(TXT[i:j+1])
                    break
            j += 1
        i = j + 1
    return out

wires = blocks("wire")
labels = {k: blocks(k) for k in ("label", "global_label")}
print("wires:", len(wires), "| labels:", len(labels["label"]), "| global:", len(labels["global_label"]))

xs, ys = [], []
for w in wires:
    for a, b in re.findall(r'\(xy ([\d.-]+) ([\d.-]+)\)', w):
        xs.append(float(a)); ys.append(float(b))
if xs:
    print(f"wire coords: x {min(xs):.1f}..{max(xs):.1f}, y {min(ys):.1f}..{max(ys):.1f}")

lab_pts = collections.defaultdict(list)
for kind in labels:
    for lab in labels[kind]:
        m = re.search(r'\(at ([\d.-]+) ([\d.-]+)', lab)
        t = re.search(r'\s"([^"]*)"', lab)
        if m:
            lab_pts[(float(m.group(1)), float(m.group(2)))].append((kind, t.group(1) if t else "?"))

print("label positions:", len(lab_pts))
for pt, items in sorted(lab_pts.items()):
    tag = " *** ซ้ำ ***" if len(items) > 1 else ""
    print(f"  ({pt[0]:.2f},{pt[1]:.2f}): {items}{tag}")
