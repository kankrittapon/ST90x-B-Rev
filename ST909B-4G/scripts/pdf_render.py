# Render key PDF pages to high-res PNG (vector figures -> pixels for blob analysis)
import pymupdf
import os

D = r"D:\Tracker\ST909B-4G\Datasheet"
OUT = os.path.join(D, "pdf_render")
os.makedirs(OUT, exist_ok=True)

JOBS = [
    ("C2916234_dec.pdf", [13, 26], 300),
    ("A7670_Series_Hardware_Design_V1.00_dec.pdf", [19, 20, 21, 13], 300),
]

for f, pages, dpi in JOBS:
    doc = pymupdf.open(os.path.join(D, f))
    base = f.replace("_dec.pdf", "").replace(".pdf", "")
    for pno in pages:
        page = doc[pno - 1]
        pix = page.get_pixmap(dpi=dpi)
        name = f"{base}_p{pno:02d}_{dpi}dpi.png"
        pix.save(os.path.join(OUT, name))
        print(name, pix.width, "x", pix.height)
    doc.close()
print("done")
