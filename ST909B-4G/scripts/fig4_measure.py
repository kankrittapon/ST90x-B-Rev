# Definitive pad measurement of A7670 fig4 land pattern (600dpi render).
# Module outline: x 1171..3281, y 1180..3290 -> 24.00 mm, scale 87.917 px/mm.
import numpy as np
from PIL import Image
from scipy import ndimage

im = Image.open(r'D:\Tracker\ST909B-4G\Datasheet\pdf_render\a7670_p20_fig600.png').convert('RGB')
a = np.array(im).astype(int)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
dark = (R < 130) & (G < 130) & (B < 130)

S = (3281.0 - 1171.0) / 24.0
X0, Y0 = 1171.0, 1180.0   # module top-left px
def mx(px): return (px - X0) / S - 12.0   # module-x (center 0)
def my(py): return (py - Y0) / S - 12.0   # module-y (center 0, +down)

# erode to split adjacent pads
er = ndimage.binary_erosion(dark, structure=np.ones((7, 7)))
lab, n = ndimage.label(er)
sl = ndimage.find_objects(lab)
pads = []
for i, s in enumerate(sl, 1):
    y0, y1 = s[0].start, s[0].stop
    x0, x1 = s[1].start, s[1].stop
    area = int((lab[s] == i).sum())
    if area < 400:
        continue
    cx = (x0 + x1) / 2.0 + 3.0   # erode offset 3
    cy = (y0 + y1) / 2.0 + 3.0
    pads.append((cx, cy, (x1 - x0 + 6) / S, (y1 - y0 + 6) / S))
print('pads found:', len(pads))

# classify
rows = {}
for cx, cy, w, h in pads:
    yc = my(cy)
    xc = mx(cx)
    if yc < -9.5:
        rows.setdefault('top', []).append((xc, yc, w, h))
    elif yc > 9.5:
        rows.setdefault('bot', []).append((xc, yc, w, h))
    elif xc < -9.5:
        rows.setdefault('left', []).append((xc, yc, w, h))
    elif xc > 9.5:
        rows.setdefault('right', []).append((xc, yc, w, h))
    else:
        rows.setdefault('inner', []).append((xc, yc, w, h))

for k in ('top', 'bot', 'left', 'right', 'inner'):
    arr = sorted(rows.get(k, []))
    print('\n==', k, len(arr))
    if k in ('top', 'bot'):
        cs = [p[0] for p in arr]
        print('  sizes w: %.3f..%.3f h: %.3f..%.3f' % (min(p[2] for p in arr), max(p[2] for p in arr), min(p[3] for p in arr), max(p[3] for p in arr)))
        print('  centers-x:', ['%.3f' % v for v in cs])
        if len(cs) > 1:
            print('  pitch:', ['%.3f' % (b - a) for a, b in zip(cs, cs[1:])])
        print('  center-y: %.3f' % np.mean([p[1] for p in arr]))
    elif k in ('left', 'right'):
        cs = [p[1] for p in arr]
        print('  sizes w: %.3f..%.3f h: %.3f..%.3f' % (min(p[2] for p in arr), max(p[2] for p in arr), min(p[3] for p in arr), max(p[3] for p in arr)))
        print('  centers-y:', ['%.3f' % v for v in cs])
        if len(cs) > 1:
            print('  pitch:', ['%.3f' % (b - a) for a, b in zip(cs, cs[1:])])
        print('  center-x: %.3f' % np.mean([p[0] for p in arr]))
    else:
        for p in sorted(arr, key=lambda t: (t[1], t[0])):
            print('  x %7.3f y %7.3f  w %.3f h %.3f' % p)

# the two ext lines of 1.50 PITCH below module: vertical dark lines y in [12.5..17] mm, x in [-1..6]
print('\n== 1.50 PITCH ext lines (below module) ==')
ya, yb = int(Y0 + S * 24.9), int(Y0 + S * 29.5)
xa, xb = int(X0 + S * 10.0), int(X0 + S * 19.5)
reg = dark[ya:yb, xa:xb]
colsum = reg.sum(axis=0)
xs = np.nonzero(colsum > (yb - ya) * 0.6)[0]
gr = []
for x in xs:
    if gr and x - gr[-1][-1] <= 3:
        gr[-1].append(x)
    else:
        gr.append([x])
for g in gr:
    x = int(np.mean(g))
    # top extent of the line (does it reach pads?)
    col = dark[ya - 900:yb, xa + x]
    ys2 = np.nonzero(col)[0]
    print('  ext line module-x %.3f (top extent y %.3f)' % (mx(xa + x), my(ya - 900 + ys2.min()) if len(ys2) else -99))
