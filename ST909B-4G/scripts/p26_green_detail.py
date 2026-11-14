# Detailed green-band measurement of L76K top view (left/right pad strips, top strip, bottom stubs, circle)
import numpy as np
from PIL import Image

im = Image.open(r'D:\Tracker\ST909B-4G\Datasheet\pdf_render\C2916234_p26_300dpi.png').convert('RGB')
a = np.array(im).astype(int)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
green = (G > 120) & (R < 120) & (B < 120)

SX = 636 / 9.70   # px/mm horizontal
SY = 680 / 10.10  # px/mm vertical
X0, Y0 = 860, 1631  # green rect TL in page-px
print('scale X %.2f Y %.2f px/mm' % (SX, SY))

def mm_x(px): return (px - X0) / SX
def mm_y(px): return (px - Y0) / SY

tv = green[Y0:Y0 + 681, X0:X0 + 637]

# 1) vertical strips: column profile in x 0..2mm and 8..9.7mm
for name, xa, xb in [('LEFT  x 0..2.5mm', 0, int(2.5 * SX)), ('RIGHT x 7..9.7mm', int(7.0 * SX), 637)]:
    prof = tv[:, xa:xb].sum(axis=0)
    on = np.nonzero(prof > 0)[0]
    if len(on):
        print('%s: green cols px %d..%d -> x %.3f..%.3f mm (w %.3f)' % (
            name, xa + on.min(), xa + on.max(), mm_x(xa + on.min()), mm_x(xa + on.max()),
            (on.max() - on.min() + 1) / SX))

# 2) row extent of the left strip (x 0..0.8mm band): find green row-runs
strip = tv[:, 0:int(0.8 * SX)]
rowsum = strip.sum(axis=1)
rr = []
inr = False
for y, v in enumerate(rowsum):
    if v > 3 and not inr:
        st = y; inr = True
    elif v <= 3 and inr:
        rr.append((st, y)); inr = False
if inr:
    rr.append((st, len(rowsum)))
print('LEFT strip row runs (y mm):', [('%.3f..%.3f (len %.3f)' % (mm_y(s), mm_y(e), (e - s) / SY)) for s, e in rr])

strip = tv[:, 637 - int(0.8 * SX):]
rowsum = strip.sum(axis=1)
rr = []
inr = False
for y, v in enumerate(rowsum):
    if v > 3 and not inr:
        st = y; inr = True
    elif v <= 3 and inr:
        rr.append((st, y)); inr = False
if inr:
    rr.append((st, len(rowsum)))
print('RIGHT strip row runs (y mm):', [('%.3f..%.3f (len %.3f)' % (mm_y(s), mm_y(e), (e - s) / SY)) for s, e in rr])

# 3) horizontal green bands: top (y 0..0.8mm) and bottom (y 9..10.1mm) row profiles
for name, ya, yb in [('TOP  y 0..1.0mm', 0, int(1.0 * SY)), ('BOT  y 9.0..10.1mm', int(9.0 * SY), 681)]:
    prof = tv[ya:yb, :].sum(axis=1)
    on = np.nonzero(prof > 0)[0]
    if len(on):
        print('%s: green rows px %d..%d -> y %.3f..%.3f mm (h %.3f)' % (
            name, ya + on.min(), ya + on.max(), mm_y(ya + on.min()), mm_y(ya + on.max()),
            (on.max() - on.min() + 1) / SY))
    # column runs inside that band
    band = tv[ya:yb, :]
    colsum = band.sum(axis=0)
    cr = []
    inr = False
    for x, v in enumerate(colsum):
        if v > 2 and not inr:
            st = x; inr = True
        elif v <= 2 and inr:
            cr.append((st, x)); inr = False
    if inr:
        cr.append((st, len(colsum)))
    print('   col runs x(mm):', [('%.3f..%.3f (w %.3f)' % (mm_x(s), mm_x(e), (e - s) / SX)) for s, e in cr])

# 4) circle: find green circle bbox in interior (x 0.5..2.5, y 0.5..2.5)
cx0, cx1 = int(0.4 * SX), int(2.6 * SX)
cy0, cy1 = int(0.4 * SY), int(2.6 * SY)
reg = tv[cy0:cy1, cx0:cx1]
ys, xs = np.nonzero(reg)
if len(ys):
    print('circle bbox: x %.3f..%.3f (d %.3f) y %.3f..%.3f (d %.3f)' % (
        mm_x(cx0 + xs.min()), mm_x(cx0 + xs.max()), (xs.max() - xs.min()) / SX,
        mm_y(cy0 + ys.min()), mm_y(cy0 + ys.max()), (ys.max() - ys.min()) / SY))
