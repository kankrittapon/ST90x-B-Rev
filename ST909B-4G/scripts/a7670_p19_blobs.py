# Blob-analyze A7670 p19 Bot View at 600dpi -> exact module pad layout (mm, relative to module center)
import pymupdf, os
import numpy as np
from PIL import Image
from scipy import ndimage

D = r"D:\Tracker\ST909B-4G\Datasheet"
doc = pymupdf.open(os.path.join(D, "A7670_Series_Hardware_Design_V1.00_dec.pdf"))
page = doc[18]  # p19
rect = None
for im in page.get_images(full=True):
    for r in page.get_image_rects(im[0]):
        if r.width > 300:
            rect = r
print("fig rect:", rect)
pix = page.get_pixmap(dpi=600, clip=rect)
p = os.path.join(D, "pdf_render", "a7670_p19_fig600.png")
pix.save(p)
doc.close()

img = np.array(Image.open(p).convert("L"))
bw = img < 128
H, W = bw.shape
print("img", W, "x", H)
lab, n = ndimage.label(bw)
sl = ndimage.find_objects(lab)
blobs = []
for i, s in enumerate(sl, 1):
    a = int((lab[s] == i).sum())
    if a < 120:
        continue
    y0, y1 = s[0].start, s[0].stop
    x0, x1 = s[1].start, s[1].stop
    w, h = x1 - x0, y1 - y0
    fill = a / (w * h)
    # pads = small solid squares/rects
    if 6 < w < 40 and 6 < h < 40 and fill > 0.55:
        blobs.append((x0, y0, w, h, round(fill, 2)))
blobs.sort(key=lambda b: (b[1], b[0]))
print(f"pad-like blobs: {len(blobs)}")
for b in blobs:
    print(f"x {b[0]:5d} y {b[1]:5d} w {b[2]:3d} h {b[3]:3d} fill {b[4]}")
