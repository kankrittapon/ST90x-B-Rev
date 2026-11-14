# Row-profile bump extraction + dim arrow tips for L76K top view.
import numpy as np
from PIL import Image
from scipy import ndimage

im = Image.open(r'D:\Tracker\ST909B-4G\Datasheet\pdf_render\C2916234_p26_300dpi.png').convert('RGB')
a = np.array(im).astype(int)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
green = (G > 120) & (R < 120) & (B < 120)
dark = (R < 210) & (G < 210) & (B < 210) & ~green

SX = 636 / 9.70
SY = 680 / 10.10
X0, Y0 = 860, 1631
def mx(i): return i / SX
def my(i): return i / SY

# LEFT bumps: dark in x [838..859] (protrusion zone, excl dim lines further left)
zone = dark[1615:2345, 838:860]
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
            runs.append((y + 1615, j + 1615))
        y = j
    else:
        y += 1
print('LEFT bump row-runs (module-y mm):')
ys = []
for (s, e) in runs:
    yc = (s + e) / 2 - Y0
    ys.append(yc)
    print('  %.3f..%.3f (len %.3f) center %.3f' % (my(s - Y0), my(e - Y0), (e - s) / SY, yc))
print('  pitches:', ['%.3f' % (b - a) for a, b in zip(ys, ys[1:])])
print('  first-center..last-center span: %.3f mm' % (ys[-1] - ys[0]) if len(ys) > 1 else '')
print('  first-run top edge y=%.3f, last-run bottom edge y=%.3f' % (my(runs[0][0] - Y0), my(runs[-1][1] - Y0)))

# RIGHT bumps: mirror at x [1497..1519] (module right edge x=1496)
zone = dark[1615:2345, 1497:1519]
rows = zone.sum(axis=1)
on = rows > 0
runs2 = []
y = 0
while y < len(on):
    if on[y]:
        j = y
        while j < len(on) and on[j]:
            j += 1
        if j - y >= 4:
            runs2.append((y + 1615, j + 1615))
        y = j
    else:
        y += 1
ys2 = [(s + e) / 2 - Y0 for (s, e) in runs2]
print('RIGHT bump centers:', ['%.3f' % v for v in ys2])
print('  pitches:', ['%.3f' % (b - a) for a, b in zip(ys2, ys2[1:])])

# bump x-extent (left side): for the middle bump rows, min/max dark x in [820..862]
if len(runs) >= 3:
    s, e = runs[len(runs) // 2]
    sub = dark[s:e, 815:862]
    xs = np.nonzero(sub.any(axis=0))[0]
    print('middle LEFT bump x-extent: page-x %d..%d -> module-x %.3f..%.3f' % (
        815 + xs.min(), 815 + xs.max(), mx(815 + xs.min() - X0), mx(815 + xs.max() - X0)))

# dim arrows above module: solid dark comps y 1500..1630 x 840..1520
reg = dark[1500:1630, 840:1520]
lab, n = ndimage.label(reg)
sl = ndimage.find_objects(lab)
print('=== solid comps above module (arrow candidates) ===')
for i, s in enumerate(sl, 1):
    y0, y1 = s[0].start, s[0].stop
    x0, x1 = s[1].start, s[1].stop
    area = int((lab[s] == i).sum())
    if area < 25:
        continue
    fill = area / ((y1 - y0) * (x1 - x0))
    print('  y %d..%d x %d..%d (w %.3f mm) area %d fill %.2f -> module-x %.3f..%.3f' % (
        y0 + 1500, y1 + 1500, x0 + 840, x1 + 840, (x1 - x0) / SX, area, fill,
        mx(x0 + 840 - X0), mx(x1 + 840 - X0)))
