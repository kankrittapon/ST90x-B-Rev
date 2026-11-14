# Measure green features in L76K p26 top view from the 300dpi render.
# Calibrate: green outer rect = 9.70 x 10.10 mm. Then report all green bands.
import numpy as np
from PIL import Image

im = Image.open(r'D:\Tracker\ST909B-4G\Datasheet\pdf_render\C2916234_p26_300dpi.png').convert('RGB')
a = np.array(im).astype(int)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
green = (G > 120) & (R < 120) & (B < 120)

# restrict to the figure area (top view + side view), exclude page furniture
sub = green[600:2500, 300:2200]
ys, xs = np.nonzero(sub)
y0g, y1g = ys.min() + 600, ys.max() + 600
x0g, x1g = xs.min() + 300, xs.max() + 300
print('green bbox page-px: x %d..%d (w %d)  y %d..%d (h %d)' % (x0g, x1g, x1g - x0g, y0g, y1g, y1g - y0g))

# The green bbox includes top view AND side view. Split: find the gap between views.
colsum = sub.sum(axis=0)
runs = []
inr = False
for x, v in enumerate(colsum):
    if v > 0 and not inr:
        st = x; inr = True
    elif v == 0 and inr:
        runs.append((st + 300, x + 300)); inr = False
if inr:
    runs.append((st + 300, len(colsum) + 300))
print('green column runs (page-px):', runs)

# For each run region, report row bands too
for (xa, xb) in runs:
    reg = green[600:2500, xa:xb + 1]
    rowsum = reg.sum(axis=1)
    rruns = []
    inr = False
    for y, v in enumerate(rowsum):
        if v > 0 and not inr:
            st = y; inr = True
        elif v == 0 and inr:
            rruns.append((st + 600, y + 600)); inr = False
    if inr:
        rruns.append((st + 600, 2500 + 600))
    print('region x %d..%d row runs:' % (xa, xb), rruns)
