# Decrypt vendor PDFs (empty user password) -> *_dec.pdf, then extract text coords
from pypdf import PdfReader, PdfWriter
import os, sys

D = r"D:\Tracker\ST909B-4G\Datasheet"
FILES = ["A7670_Series_Hardware_Design_V1.00.pdf", "C2916234.pdf",
         "9ef59010dead2bec7b1790c4ccc94de7.pdf"]

for f in FILES:
    src = os.path.join(D, f)
    dst = os.path.join(D, f.replace(".pdf", "_dec.pdf"))
    try:
        r = PdfReader(src)
        if r.is_encrypted:
            r.decrypt("")
        w = PdfWriter()
        for p in r.pages:
            w.add_page(p)
        with open(dst, "wb") as fh:
            w.write(fh)
        print("OK ", os.path.basename(dst), "pages:", len(r.pages))
    except Exception as e:
        print("FAIL", f, repr(e)[:120])
