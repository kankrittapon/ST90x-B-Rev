# Extract vector drawings (pads are filled rects) from L76K PDF pages -> exact pad coords in mm
import pymupdf
import os, json

D = r"D:\Tracker\ST909B-4G\Datasheet"
OUT = r"D:\Tracker\ST909B-4G\Datasheet\pdf_vec"
os.makedirs(OUT, exist_ok=True)

for pno in (13, 26):
    doc = pymupdf.open(os.path.join(D, "C2916234_dec.pdf"))
    page = doc[pno - 1]
    # pdf unit = 1/72 inch; page likely A4 595x842 pt. Convert to mm: *25.4/72
    S = 25.4 / 72.0
    recs = []
    for d in page.get_drawings():
        r = d["rect"]
        recs.append({
            "type": d["type"],           # f=fill, s=stroke, fs=both
            "fill": [round(c, 2) for c in (d["fill"] or ())],
            "color": [round(c, 2) for c in (d["color"] or ())],
            "x0": round(r.x0 * S, 3), "y0": round(r.y0 * S, 3),
            "x1": round(r.x1 * S, 3), "y1": round(r.y1 * S, 3),
            "w": round((r.x1 - r.x0) * S, 3), "h": round((r.y1 - r.y0) * S, 3),
        })
    doc.close()
    with open(os.path.join(OUT, f"C2916234_p{pno}_drawings.json"), "w", encoding="utf-8") as f:
        json.dump(recs, f, indent=1)
    # summarize: fill colors histogram + sizes
    from collections import Counter
    hist = Counter((r["type"], tuple(r["fill"])) for r in recs)
    print(f"page {pno}: {len(recs)} drawings")
    for k, v in hist.most_common(12):
        print("   ", k, v)
print("done ->", OUT)
