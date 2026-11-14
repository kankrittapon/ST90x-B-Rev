# Extract embedded images from decrypted PDFs -> Datasheet\pdf_img\
import os
from pypdf import PdfReader

D = r"D:\Tracker\ST909B-4G\Datasheet"
OUT = os.path.join(D, "pdf_img")
os.makedirs(OUT, exist_ok=True)

TARGETS = {
    "A7670_Series_Hardware_Design_V1.00_dec.pdf": [13, 14, 8, 19, 21, 20, 22],
    "C2916234_dec.pdf": list(range(1, 36)),
    "9ef59010dead2bec7b1790c4ccc94de7_dec.pdf": [1, 2],
}

for f, pages in TARGETS.items():
    r = PdfReader(os.path.join(D, f))
    base = f.replace("_dec.pdf", "")
    for pi, page in enumerate(r.pages, 1):
        if pages and pi not in pages:
            continue
        try:
            imgs = page.images
        except Exception as e:
            print(f"{base} p{pi}: ERR {repr(e)[:60]}")
            continue
        for im in imgs:
            try:
                name = f"{base}_p{pi:02d}_{im.name}"
                # sanitize
                bad = '<>:"/\\|?*'
                name = "".join(c for c in name if c not in bad)
                path = os.path.join(OUT, name)
                with open(path, "wb") as fh:
                    fh.write(im.data)
                print(f"{base} p{pi}: {name}  {len(im.data)//1024} KB")
            except Exception as e:
                print(f"{base} p{pi}: SAVE-ERR {repr(e)[:60]}")
print("done ->", OUT)
