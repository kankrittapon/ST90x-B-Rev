# Export board data to CSV (Excel-ready, UTF-8 BOM for Thai in Excel)
import pcbnew, json, csv, os

PATH = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
OUT = r"D:\Tracker\ST909B-4G\export"
os.makedirs(OUT, exist_ok=True)
b = pcbnew.LoadBoard(PATH)
M = pcbnew.ToMM


def layer_name(l):
    return {"F": "F.Cu", "B": "B.Cu"}.get("FB"[b.GetLayerName(l).startswith("F.") and 0 or 1], b.GetLayerName(l))


# 1) components
with open(os.path.join(OUT, "components.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["Ref", "Value", "Footprint", "X_mm", "Y_mm", "Rot_deg", "Side"])
    for fp in b.GetFootprints():
        p = fp.GetPosition()
        w.writerow([fp.GetReference(), fp.GetValue(), fp.GetFPIDAsString(),
                    round(M(p.x), 3), round(M(p.y), 3), round(fp.GetOrientationDegrees(), 1),
                    fp.GetLayerName()])

# 2) pads -> nets
with open(os.path.join(OUT, "nets_pads.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["Net", "Pad", "Ref", "X_mm", "Y_mm", "SizeX_mm", "SizeY_mm", "Side"])
    rows = []
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            p = pad.GetPosition()
            sz = pad.GetSize()
            lay = []
            for l, nm in ((pcbnew.F_Cu, "F"), (pcbnew.B_Cu, "B")):
                if pad.GetLayerSet().Contains(l):
                    lay.append(nm)
            rows.append([pad.GetNetname(), pad.GetPadName(), fp.GetReference(),
                         round(M(p.x), 3), round(M(p.y), 3), round(M(sz.x), 3), round(M(sz.y), 3),
                         "+".join(lay)])
    rows.sort(key=lambda r: (r[0], r[2], r[1]))
    w.writerows(rows)

# 3) routes inventory
tr = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T]
vi = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
with open(os.path.join(OUT, "routes.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["Kind", "Net", "Layer", "X1", "Y1", "X2", "Y2", "Width_mm"])
    for t in sorted(tr, key=lambda t: (t.GetNetname(), t.GetLayerName())):
        s, e = t.GetStart(), t.GetEnd()
        w.writerow(["track", t.GetNetname(), t.GetLayerName(),
                    round(M(s.x), 3), round(M(s.y), 3), round(M(e.x), 3), round(M(e.y), 3), round(M(t.GetWidth()), 3)])
    for v in sorted(vi, key=lambda v: (v.GetNetname(), M(v.GetPosition().x), M(v.GetPosition().y))):
        p = v.GetPosition()
        w.writerow(["via", v.GetNetname(), "F<->B", round(M(p.x), 3), round(M(p.y), 3), "", "",
                    f"OD {round(M(v.GetWidth(pcbnew.F_Cu)), 2)} / drill {round(M(v.GetDrill()), 2)}"])

# 4) DRC violations
with open(os.path.join(OUT, "drc_violations.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["Type", "Severity", "X_mm", "Y_mm", "Description"])
    d = json.load(open(r"D:\Tracker\ST909B-4G\ST909B-4G_drc_violations.json", encoding="utf-8"))
    for v in d["violations"]:
        loc = v.get("location", {})
        desc = " | ".join(i["description"] for i in v["items"])
        w.writerow([v["type"], v["severity"], loc.get("x"), loc.get("y"),
                    (v.get("message", "") + " || " + desc)[:300]])

print("CSV written to", OUT)
print("tracks", len(tr), "vias", len(vi), "footprints", len(list(b.GetFootprints())))
