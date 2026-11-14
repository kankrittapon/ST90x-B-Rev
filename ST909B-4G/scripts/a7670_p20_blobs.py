# Render A7670 p20 figure region at 600 dpi + blob analysis of pads
# -> exact pad positions in mm (calibrated by inner grid pitch 3.80)
import pymupdf, os
import numpy as np
from PIL import Image

D = r"D:\Tracker\ST909B-4G\Datasheet"
OUT = r"D:\Tracker\ST909B-4G\Datasheet\pdf_render"

doc = pymupdf.open(os.path.join(D, "A7670_Series_Hardware_Design_V1.00_dec.pdf"))
page = doc[19]  # p20
# find the big content image (Im2)
info = page.get_images(full=True)
rect = None
for im in info:
    xref = im[0]
    for r in page.get_image_rects(xref):
        if r.width > 300:  # content image
            rect = r
print("figure rect (pt):", rect)

pix = page.get_pixmap(dpi=600, clip=rect)
fig_path = os.path.join(OUT, "a7670_p20_fig600.png")
pix.save(fig_path)
doc.close()
print("rendered:", pix.width, "x", pix.height, "->", fig_path)

# ---- blob analysis ----
img = np.array(Image.open(fig_path).convert("L"))
bw = img < 128  # dark
H, W = bw.shape
print("binarized", W, "x", H, "dark px:", int(bw.sum()))

# connected components via simple two-pass labeling (union-find)
labels = np.zeros((H, W), dtype=np.int32)
parent = [0]

def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x

def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[max(ra, rb)] = min(ra, rb)

nxt = 1
for y in range(H):
    row = bw[y]
    lab = labels[y]
    up = labels[y - 1] if y else None
    for x in range(W):
        if not row[x]:
            continue
        nb = []
        if x and lab[x - 1]:
            nb.append(lab[x - 1])
        if up is not None:
            if up[x]:
                nb.append(up[x])
            if x and up[x - 1]:
                nb.append(up[x - 1])
            if x < W - 1 and up[x + 1]:
                nb.append(up[x + 1])
        if nb:
            m = min(find(v) for v in nb)
            lab[x] = m
            for v in nb:
                union(v, m)
        else:
            lab[x] = nxt
            parent.append(nxt)
            nxt += 1

# resolve labels + collect bbox/centroid/area
n_labels = nxt
areas = np.bincount(labels.ravel(), minlength=n_labels)
minx = [W] * n_labels; maxx = [0] * n_labels
miny = [H] * n_labels; maxy = [0] * n_labels
sumx = np.zeros(n_labels); sumy = np.zeros(n_labels)
ys, xs = np.nonzero(labels)
ls = labels[ys, xs]
np.minimum.at(minx, ls, xs); np.maximum.at(maxx, ls, xs)
np.minimum.at(miny, ls, ys); np.maximum.at(maxy, ls, ys)
np.add.at(sumx, ls, xs); np.add.at(sumy, ls, ys)

# pads: dark-filled solid blobs with reasonable size (crosshatch pads are solid-ish after threshold?)
# first pass: list all blobs > 200 px area with bbox dims
blobs = []
for i in range(1, n_labels):
    a = areas[i]
    if a < 150:
        continue
    w = maxx[i] - minx[i] + 1
    h = maxy[i] - miny[i] + 1
    fill = a / (w * h)
    blobs.append((minx[i], miny[i], w, h, a, round(fill, 2), sumx[i] / a, sumy[i] / a))
blobs.sort(key=lambda b: (b[1], b[0]))
print(f"blobs>150px: {len(blobs)}")
for b in blobs[:80]:
    print(f"x {b[0]:5d} y {b[1]:5d} w {b[2]:4d} h {b[3]:4d} area {b[4]:7d} fill {b[5]}  cx {b[6]:7.1f} cy {b[7]:7.1f}")
