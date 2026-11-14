# Extract text + coordinates per page using pypdf visitor_text (fast, standard-compliant)
import os, re
from pypdf import PdfReader

D = r"D:\Tracker\ST909B-4G\Datasheet"
OUT = os.path.join(D, "pdf_text")
os.makedirs(OUT, exist_ok=True)

for f in ["A7670_Series_Hardware_Design_V1.00_dec.pdf", "C2916234_dec.pdf",
          "9ef59010dead2bec7b1790c4ccc94de7_dec.pdf"]:
    r = PdfReader(os.path.join(D, f))
    base = f.replace("_dec.pdf", "")
    for pi, page in enumerate(r.pages, 1):
        rows = []
        def vis(text, cm, tm, fd, fs):
            t = text.strip()
            if t:
                x, y = tm[4], tm[5]
                rows.append((round(y, 1), round(x, 1), t))
        try:
            page.extract_text(visitor_text=vis)
        except Exception as e:
            print(f"{base} p{pi}: ERR {repr(e)[:60]}")
        if not rows:
            continue
        with open(os.path.join(OUT, f"{base}_p{pi:02d}.txt"), "w", encoding="utf-8") as fh:
            for y, x, t in sorted(rows, key=lambda r: (-r[0], r[1])):
                fh.write(f"{y:9.1f} {x:9.1f} | {t}\n")
    print("done", base, "pages", len(r.pages))
