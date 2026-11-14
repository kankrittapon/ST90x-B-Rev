# v4 diag: vias inventory + key pad geometry + dangling via details
import pcbnew, json

PATH = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
b = pcbnew.LoadBoard(PATH)
M = pcbnew.ToMM

print("=== ALL VIAS ===")
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T:
        n = t.GetNetname()
        p = t.GetPosition()
        print(f"{n:14s} ({M(p.x):7.3f}, {M(p.y):7.3f})")

print("=== PAD GEOMETRY ===")
for ref in ("TP3", "TP4", "U6", "U4"):
    fp = b.FindFootprintByReference(ref)
    if not fp:
        print(ref, "MISSING")
        continue
    for pad in fp.Pads():
        num = pad.GetPadName()
        if ref == "U4" and num not in ("1", "2", "3", "4"):
            continue
        if ref == "U6" and num not in ("1", "2"):
            continue
        p = pad.GetPosition()
        sz = pad.GetSize()
        dr = pad.GetDrillSize()
        print(f"{ref}/{num} net={pad.GetNetname():12s} c=({M(p.x):.3f},{M(p.y):.3f}) "
              f"size=({M(sz.x):.3f}x{M(sz.y):.3f}) drill=({M(dr.x):.3f}x{M(dr.y):.3f}) "
              f"layers={pad.GetLayerSet().FmtBin() if False else [pcbnew.LayerName(l) for l in (pcbnew.F_Cu, pcbnew.B_Cu) if pad.GetLayerSet().Contains(l)]}")

print("=== TRACKS near x=22.0..22.5 on B (GPS_TX vertical check) ===")
for t in b.GetTracks():
    if t.Type() != pcbnew.PCB_TRACE_T:
        continue
    s, e = t.GetStart(), t.GetEnd()
    if t.GetLayer() == pcbnew.B_Cu and 21.9 < M(s.x) < 22.6 and 21.9 < M(e.x) < 22.6:
        print(f"{t.GetNetname():10s} ({M(s.x):.3f},{M(s.y):.3f})-({M(e.x):.3f},{M(e.y):.3f})")

print("=== via_dangling from JSON ===")
d = json.load(open(r"D:\Tracker\ST909B-4G\ST909B-4G_drc_violations.json", encoding="utf-8"))
for v in d["violations"]:
    if v["type"] == "via_dangling":
        loc = v.get("location", {})
        items = " | ".join(i["description"][:90] for i in v["items"])
        print(f"({loc.get('x')}, {loc.get('y')}) {items}")
