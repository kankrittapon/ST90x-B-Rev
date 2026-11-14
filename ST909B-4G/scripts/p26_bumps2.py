# Measure L76K castellation bumps with gray mask + locate 8.80 dim extension lines.
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

def comps(reg, oy, ox, min_area=15):
    lab, n = ndimage.label(reg)
    sl = ndimage.find_objects(lab)
    out = []
    for i, s in enumerate(sl, 1):
        y0, y1 = s[0].start, s[0].stop
        x0, x1 = s[1].start, s[1].stop
        area = int((lab[s] == i).sum())
        if area < min_area:
            continue
        out.append((y0 + oy, y1 + oy, x0 + ox, x1 + ox, area))
    return out

print('=== LEFT bumps (region x 815..862, y 1620..2340) ===')
for b in sorted(comps(dark[1620:2340, 815:862], 1620, 815)):
    print('  y %d..%d (%.3f mm) cx %.3f | x %d..%d (w %.3f mm) area %d' % (
        b[0], b[1], (b[1] - b[0]) / SY, my((b[0] + b[1]) / 2 - Y0), b[2], b[3], (b[3] - b[2]) / SX, b[4]))

print('=== RIGHT bumps (region x 1490..1540, y 1620..2340) ===')
for b in sorted(comps(dark[1620:2340, 1490:1540], 1620, 1490)):
    print('  y %d..%d (%.3f mm) cy %.3f | x %d..%d (w %.3f mm) area %d' % (
        b[0], b[1], (b[1] - b[0]) / SY, my((b[0] + b[1]) / 2 - Y0), b[2], b[3], (b[3] - b[2]) / SX, b[4]))

print('=== dim extension lines above module (y 1480..1631, x 880..1520): vertical lines ===')
reg = dark[1480:1631, 880:1520]
colsum = reg.sum(axis=0)
xs = np.nonzero(colsum > 25)[0]
groups = []
for x in xs:
    if groups and x - groups[-1][-1] <= 2:
        groups[-1].append(x)
    else:
        groups.append([x])
for g in groups:
    print('  ext line at page-x %d -> module-x %.3f mm (n=%d)' % (880 + int(np.mean(g)), mx(np.mean(g)), len(g)))
