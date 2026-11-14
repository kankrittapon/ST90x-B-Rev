# Find the black module outline rect (long straight lines) vs green rect in L76K top view.
import numpy as np
from PIL import Image

im = Image.open(r'D:\Tracker\ST909B-4G\Datasheet\pdf_render\C2916234_p26_300dpi.png').convert('RGB')
a = np.array(im).astype(int)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
green = (G > 120) & (R < 120) & (B < 120)
dark = (R < 210) & (G < 210) & (B < 210) & ~green

# horizontal dark lines in the figure area
print('--- horizontal dark lines (rows with >400 px in x 780..1580), y 1560..2400 ---')
for y in range(1560, 2400):
    n = dark[y, 780:1580].sum()
    if n > 400:
        xs = np.nonzero(dark[y, 780:1580])[0]
        print('y=%d n=%d x %d..%d' % (y, n, 780 + xs.min(), 780 + xs.max()))

print('--- horizontal green lines (rows with >400 px), y 1560..2400 ---')
for y in range(1560, 2400):
    n = green[y, 780:1580].sum()
    if n > 400:
        xs = np.nonzero(green[y, 780:1580])[0]
        print('y=%d n=%d x %d..%d' % (y, n, 780 + xs.min(), 780 + xs.max()))

print('--- vertical dark lines (cols with >300 px in y 1590..2350), x 780..1580 ---')
for x in range(780, 1580):
    n = dark[1590:2350, x].sum()
    if n > 300:
        ys = np.nonzero(dark[1590:2350, x])[0]
        print('x=%d n=%d y %d..%d' % (x, n, 1590 + ys.min(), 1590 + ys.max()))

print('--- vertical green lines (cols with >300 px), x 780..1580 ---')
for x in range(780, 1580):
    n = green[1590:2350, x].sum()
    if n > 300:
        ys = np.nonzero(green[1590:2350, x])[0]
        print('x=%d n=%d y %d..%d' % (x, n, 1590 + ys.min(), 1590 + ys.max()))
