# Analyze black-filled rects on C2916234 p26 -> L76K pad rectangles
import json, os

OUT = r"D:\Tracker\ST909B-4G\Datasheet\pdf_vec"
recs = json.load(open(os.path.join(OUT, "C2916234_p26_drawings.json"), encoding="utf-8"))
blacks = [r for r in recs if r["type"] == "f" and r["fill"] == [0.0, 0.0, 0.0]]
print("black fills:", len(blacks))
for r in sorted(blacks, key=lambda r: (round(r["x0"], 1), round(r["y0"], 1))):
    print(f"x {r['x0']:7.2f}..{r['x1']:7.2f}  y {r['y0']:7.2f}..{r['y1']:7.2f}   w {r['w']:6.3f} h {r['h']:6.3f}")
