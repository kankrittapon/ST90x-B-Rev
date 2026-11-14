# Measure castellation bump positions on left/right edges of L76K top view + 8.80 dim lines.
import numpy as np
from PIL import Image
from scipy import ndimage

im = Image.open(r'D:\Tracker\ST909B-4G\Datasheet\pdf_render\C2916234_p26_300dpi.png').convert('RGB')
a = np.array(im).astype(int)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
black = (R < 100) & (G < 100) & (B < 100)
green = (G > 120) & (R < 120) & (B < 120)

SX = 636 / 9.70   # px/mm, module TL at (860, 1631)
SY = 680 / 10.10
X0, Y0 = 860, 1631
def mx(i): return i / SX
def my(i): return i / SY

# --- left edge bumps: black comps in region x [820..875] (module edge at 860), y [1600..2360]
reg = black[1600:2360, 815:876]
lab, n = ndimage.label(reg)
sl = ndimage.find_objects(lab)
bumps = []
for i, s in enumerate(sl, 1):
    y0, y1 = s[0].start, s[0].stop
    x0, x1 = s[1].start, s[1].stop
    area = int((lab[s] == i).sum())
    if area < 20:
        continue
    bumps.append((y0 + 1600, y1 + 1600, x0 + 815, x1 + 815, area))
print('LEFT edge black comps (page-px):')
for b in sorted(bumps):
    print('  y %d..%d (len %d = %.3f mm) x %d..%d (w %d = %.3f mm) area %d' % (
        b[0], b[1], b[1] - b[0], (b[1] - b[0]) / SY, b[2], b[3], b[3] - b[2], (b[3] - b[2]) / SX, b[4]))

# --- right edge bumps
reg = black[1600:2360, 1490:1545]
lab, n = ndimage.label(reg)
sl = ndimage.find_objects(lab)
bumps = []
for i, s in enumerate(sl, 1):
    y0, y1 = s[0].start, s[0].stop
    x0, x1 = s[1].start, s[1].stop
    area = int((lab[s] == i).sum())
    if area < 20:
        continue
    bumps.append((y0 + 1600, y1 + 1600, x0 + 1490, x1 + 1490, area))
print('RIGHT edge black comps:')
for b in sorted(bumps):
    print('  y %d..%d (len %.3f mm) x %d..%d (w %.3f mm) area %d' % (
        b[0], b[1], (b[1] - b[0]) / SY, b[2], b[3], (b[3] - b[2]) / SX, b[4]))

# --- 8.80 dim: horizontal dim line ~y 1560..1590 area above module; find vertical extension lines
# dim line was at y~ (page) 1546..1556 per full-page look; find black vertical lines x 900..1500, y 1500..1640
reg = black[1490:1640, 880:1520]
colsum = reg.sum(axis=0)
on = np.nonzero(colsum > 40)[0]
print('8.80 dim vertical ext lines at page-x:', [(x + 880, '%.3f mm' % mx(x + 880 - X0)) for x in on])
