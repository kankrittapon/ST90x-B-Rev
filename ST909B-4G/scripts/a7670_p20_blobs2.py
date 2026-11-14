# Blob analysis of A7670 p20 recommended footprint (600dpi render)
import numpy as np
from PIL import Image
from scipy import ndimage
import os

fig_path = r"D:\Tracker\ST909B-4G\Datasheet\pdf_render\a7670_p20_fig600.png"
img = np.array(Image.open(fig_path).convert("L"))
bw = img < 128
H, W = bw.shape
print("img", W, "x", H, "dark", int(bw.sum()))

# dilate slightly to merge crosshatch into solid pads
bw_d = ndimage.binary_dilation(bw, structure=np.ones((5, 5)))
lab, n = ndimage.label(bw_d)
print("components:", n)
sl = ndimage.find_objects(lab)
res = []
for i, s in enumerate(sl, 1):
    a = int((lab[s] == i).sum())
    if a < 400:
        continue
    y0, y1 = s[0].start, s[0].stop
    x0, x1 = s[1].start, s[1].stop
    w, h = x1 - x0, y1 - y0
    res.append((x0, y0, w, h, a))
res.sort(key=lambda b: (b[1], b[0]))
print(f"blobs>=400px: {len(res)}")
for b in res:
    print(f"x {b[0]:5d} y {b[1]:5d} w {b[2]:4d} h {b[3]:4d} area {b[4]:7d}")
