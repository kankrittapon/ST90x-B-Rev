# fig4 pad measurement v2: strip long straight lines, then close+label pad blobs.
import numpy as np
from PIL import Image
from scipy import ndimage

im = Image.open(r'D:\Tracker\ST909B-4G\Datasheet\pdf_render\a7670_p20_fig600.png').convert('RGB')
a = np.array(im).astype(int)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
dark = (R < 130) & (G < 130) & (B < 130)

S = (3281.0 - 1171.0) / 24.0
X0, Y0 = 1171.0, 1180.0
def mx(px): return (px - X0) / S - 12.0
def my(py): return (py - Y0) / S - 12.0

# remove long straight lines (module outline, dim/ext/center lines) but keep pad borders (<= ~2.2mm)
L = 300
lines = np.zeros_like(dark)
for k in (np.ones((1, L), bool), np.ones((L, 1), bool),
          np.eye(L, dtype=bool), np.fliplr(np.eye(L, dtype=bool))):
    lines |= ndimage.binary_opening(dark, structure=k)
dark2 = dark & ~lines

# close to solidify each pad
blobs = ndimage.binary_closing(dark2, structure=np.ones((11, 11)))
lab, n = ndimage.label(blobs)
sl = ndimage.find_objects(lab)
pads = []
for i, s in enumerate(sl, 1):
    y0, y1 = s[0].start, s[0].stop
    x0, x1 = s[1].start, s[1].stop
    area = int((lab[s] == i).sum())
    if area < 1200:
        continue
    pads.append(((x0 + x1) / 2.0, (y0 + y1) / 2.0, (x1 - x0) / S, (y1 - y0) / S))
print('pads found:', len(pads))

rows = {}
for cx, cy, w, h in pads:
    yc, xc = my(cy), mx(cx)
    if yc < -10.0:
        rows.setdefault('top', []).append((xc, yc, w, h))
    elif yc > 10.0:
        rows.setdefault('bot', []).append((xc, yc, w, h))
    elif xc < -10.0:
        rows.setdefault('left', []).append((xc, yc, w, h))
    elif xc > 10.0:
        rows.setdefault('right', []).append((xc, yc, w, h))
    else:
        rows.setdefault('inner', []).append((xc, yc, w, h))

for k in ('top', 'bot', 'left', 'right', 'inner'):
    arr = sorted(rows.get(k, []))
    print('\n==', k, len(arr))
    if not arr:
        continue
    if k in ('top', 'bot'):
        cs = [p[0] for p in arr]
        print('  w %.3f..%.3f  h %.3f..%.3f  center-y %.3f' % (
            min(p[2] for p in arr), max(p[2] for p in arr), min(p[3] for p in arr), max(p[3] for p in arr),
            np.mean([p[1] for p in arr])))
        print('  x:', ['%.3f' % v for v in cs])
        print('  pitch:', ['%.3f' % (b - c) for c, b in zip(cs, cs[1:])])
    elif k in ('left', 'right'):
        cs = [p[1] for p in arr]
        print('  w %.3f..%.3f  h %.3f..%.3f  center-x %.3f' % (
            min(p[2] for p in arr), max(p[2] for p in arr), min(p[3] for p in arr), max(p[3] for p in arr),
            np.mean([p[0] for p in arr])))
        print('  y:', ['%.3f' % v for v in cs])
        print('  pitch:', ['%.3f' % (b - c) for c, b in zip(cs, cs[1:])])
    else:
        for p in sorted(arr, key=lambda t: (t[1], t[0])):
            print('  x %7.3f y %7.3f  w %.3f h %.3f' % p)

# 1.50 PITCH ext lines below module
ya, yb = int(Y0 + S * 24.8), int(Y0 + S * 30.0)
xa, xb = int(X0 + S * 9.0), int(X0 + S * 20.0)
reg = dark[ya:yb, xa:xb]
vlines = ndimage.binary_opening(reg, structure=np.ones((150, 1)))
lab2, n2 = ndimage.label(vlines)
sl2 = ndimage.find_objects(lab2)
print('\n== vertical ext lines below module (y %.1f..%.1f) ==' % (my(ya), my(yb)))
for i, s in enumerate(sl2, 1):
    x0, x1 = s[1].start, s[1].stop
    y0, y1 = s[0].start, s[0].stop
    print('  x %.3f..%.3f (c %.3f)  y-top %.3f  y-bot %.3f' % (
        mx(xa + x0), mx(xa + x1), mx(xa + (x0 + x1) / 2.0), my(ya + y0), my(ya + y1)))
