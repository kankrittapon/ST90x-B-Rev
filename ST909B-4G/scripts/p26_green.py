# p26 green pad outlines WITH rotation applied -> exact L76K pad coords
import pymupdf, os, json

D = r"D:\Tracker\ST909B-4G\Datasheet"
doc = pymupdf.open(os.path.join(D, "C2916234_dec.pdf"))
page = doc[25]  # p26
print("page.rect:", page.rect, "rotation:", page.rotation)
S = 25.4 / 72.0
M = page.rotation_matrix

pads = []
for d in page.get_drawings():
    if tuple(round(c, 1) for c in (d["color"] or ())) == (0.0, 1.0, 0.0) or \
       (d["fill"] and tuple(round(c, 1) for c in d["fill"]) == (0.0, 1.0, 0.0)):
        r = (d["rect"] if page.rotation == 0 else d["rect"] * M) * S
        pads.append((round(r.x0, 3), round(r.y0, 3), round(r.x1, 3), round(r.y1, 3)))
doc.close()
pads.sort(key=lambda p: (p[0], p[1]))
print("green rects:", len(pads))
for p in pads:
    print(f"x {p[0]:7.2f}..{p[2]:7.2f} (w {p[2]-p[0]:6.3f})   y {p[1]:7.2f}..{p[3]:7.2f} (h {p[3]-p[1]:6.3f})")
