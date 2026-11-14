# drc_detail.py — print full details of selected violation types
import json
d = json.load(open(r"ST909B-4G_drc_violations.json", encoding="utf-8"))
want = ("via_dangling", "unconnected_items", "starved_thermal")
buckets = [("violations", d["violations"]), ("unconnected", d.get("unconnected_items", []))]
for bname, arr in buckets:
    for v in arr:
        if not isinstance(v, dict) or v.get("type") not in want:
            continue
        print(bname, v["severity"], v["type"], "items:", len(v["items"]))
        for it in v["items"]:
            pos = it.get("pos", {})
            print("   %-28s %s @ (%.2f, %.2f)" % (
                it.get("description", "")[:28], it.get("type", "?"),
                pos.get("x", -1), pos.get("y", -1)))
        print("---")
