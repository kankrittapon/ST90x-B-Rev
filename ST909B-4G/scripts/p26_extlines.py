# Find vertical extension lines of the 8.80 dim (above module) and 9.35/10.10 dims (left side).
import numpy as np
from PIL import Image

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

# 8.80 dim: ext lines between dim line (~y1544) and module top (y1631): columns with tall dark runs
reg = dark[1546:1631, 840:1520]
colsum = reg.sum(axis=0)
xs = np.nonzero(colsum > 60)[0]
print('8.80 ext-line columns (module-x mm):', ['%.3f' % mx(x + 840 - X0) for x in xs])

# dim line y position: find the horizontal line row in y 1520..1570
for y in range(1520, 1575):
    row = dark[y, 840:1520].sum()
    if row > 300:
        print('dim line row y=%d len=%d' % (y, row))

# 9.35 dim (left, vertical): horizontal ext lines running from dim line to module edge
# search rows in y 1615..2350, x 700..862: rows where dark spans widely
reg = dark[1615:2350, 700:862]
rowsum = reg.sum(axis=1)
ys = np.nonzero(rowsum > 60)[0]
print('9.35/10.10 ext-line rows (module-y mm):', ['%.3f' % my(y + 1615 - Y0) for y in ys])

# 10.10 dim: ext lines further left (x 480..700)
reg = dark[1615:2350, 480:700]
rowsum = reg.sum(axis=1)
ys = np.nonzero(rowsum > 60)[0]
print('10.10 ext-line rows (module-y mm):', ['%.3f' % my(y + 1615 - Y0) for y in ys])
