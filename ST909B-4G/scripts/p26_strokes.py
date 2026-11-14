# Inspect stroke colors on p26 to find green pad rects (top view)
import json, os
from collections import Counter

OUT = r"D:\Tracker\ST909B-4G\Datasheet\pdf_vec"
recs = json.load(open(os.path.join(OUT, "C2916234_p26_drawings.json"), encoding="utf-8"))
strokes = [r for r in recs if r["type"] == "s"]
print("strokes:", len(strokes))
print(Counter(tuple(r["color"]) for r in strokes).most_common(10))
# print small-ish strokes near left half of page (top view area x<145)
cands = [r for r in strokes if r["x0"] < 145 and 0.3 < r["w"] < 3.5 and 0.3 < r["h"] < 3.5]
print("small rect strokes in top-view area:", len(cands))
for r in sorted(cands, key=lambda r: (round(r["x0"], 1), round(r["y0"], 1)))[:40]:
    print(f"x {r['x0']:7.2f}..{r['x1']:7.2f}  y {r['y0']:7.2f}..{r['y1']:7.2f}   w {r['w']:6.3f} h {r['h']:6.3f} color {r['color']}")
