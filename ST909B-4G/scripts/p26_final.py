# Final L76K top-view measurement with black-rect calibration.
import numpy as np
from PIL import Image

im = Image.open(r'D:\Tracker\ST909B-4G\Datasheet\pdf_render\C2916234_p26_300dpi.png').convert('RGB')
a = np.array(im).astype(int)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
green = (G > 120) & (R < 120) & (B < 120)
dark = (R < 210) & (G < 210) & (B < 210) & ~green

# calibration: black rect x 827..1527 (9.70), y 1604..2339 (10.10)
SX = (1527.5 - 827.5) / 9.70
SY = (2339.5 - 1604.5) / 10.10
BX, BY = 827.5, 1604.5   # module (black rect) TL
GX, GY = 860, 1631       # green rect TL
print('cal: SX=%.2f SY=%.2f px/mm; black rect w=%.2f h=%.2f' % (SX, SY, 700 / SX, 735 / SY))

def bx(x): return (x - BX) / SX   # module-x
def by(y): return (y - BY) / SY   # module-y

# --- bump rows (left edge): zone x 830..859 (between black edge and green edge)
zone = dark[1610:2345, 831:859]
rows = zone.sum(axis=1)
on = rows > 0
runs = []
y = 0
while y < len(on):
    if on[y]:
        j = y
        while j < len(on) and on[j]:
            j += 1
        if j - y >= 4:
            runs.append((y + 1610, j + 1610))
        y = j
    else:
        y += 1
print('LEFT bump runs (module-y):')
cs = []
for (s, e) in runs:
    cs.append((s + e) / 2)
    print('  %.3f..%.3f (len %.3f) center %.3f' % (by(s), by(e), (e - s) / SY, by((s + e) / 2)))
print('  pitches:', ['%.3f' % ((b - a) / SY) for a, b in zip(cs, cs[1:])])
if len(cs) >= 2:
    print('  center span: %.3f mm' % ((cs[-1] - cs[0]) / SY))

# bump1 top edge, bump9 bottom edge
print('  row extent: %.3f..%.3f' % (by(runs[0][0]), by(runs[-1][1])))

# --- green rect edges in module coords
print('green rect: x %.3f..%.3f (w %.3f) y %.3f..%.3f (h %.3f)' % (
    bx(860), bx(1496), (1496 - 860) / SX, by(1631), by(2300), (2300 - 1631) / SY))

# --- 9.35 dim ext lines: horizontal dark segments in x 640..826
reg = dark[1580:2380, 640:826]
rowsum = reg.sum(axis=1)
ys = np.nonzero(rowsum > 15)[0]
groups = []
for y in ys:
    if groups and y - groups[-1][-1] <= 3:
        groups[-1].append(y)
    else:
        groups.append([y])
print('left-dim area horizontal segments:')
for g in groups:
    xs = np.nonzero(dark[1580 + g[0]:1580 + g[-1] + 1, 640:826].any(axis=0))[0]
    print('  y %d..%d (module-y %.3f..%.3f) x %d..%d (module-x %.3f..%.3f)' % (
        1580 + g[0], 1580 + g[-1], by(1580 + g[0]), by(1580 + g[-1]),
        640 + xs.min(), 640 + xs.max(), bx(640 + xs.min()), bx(640 + xs.max())))
