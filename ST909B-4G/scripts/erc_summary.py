# erc_summary.py — สรุป ERC json (โครงสร้าง violations อยู่ใต้ sheets)
import json, collections

d = json.load(open(r"D:\Tracker\ST909B-4G\scripts\erc.json", encoding="utf-8"))
v = d.get("violations") or []
for s in d.get("sheets", []):
    v += s.get("violations", [])
c = collections.Counter((x["severity"], x["type"]) for x in v)
for k, n in c.most_common():
    print(k, n)
print("total", len(v))
print()
for x in v:
    if x["severity"] == "error" or x["type"] == "pin_to_pin":
        print(x["type"], "|", x["description"][:60])
        for it in x.get("items", []):
            print("   ", it.get("description", "")[:70])
print()
print("--- isolated_pin_label nets ---")
for x in v:
    if x["type"] == "isolated_pin_label":
        print(" ", "; ".join(it.get("description", "")[:40] for it in x.get("items", [])[:2]))
