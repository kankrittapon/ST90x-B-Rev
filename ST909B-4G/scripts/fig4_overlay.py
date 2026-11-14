# Overlay candidate geometries on fig4 render to verify by eye.
from PIL import Image, ImageDraw

im = Image.open(r'D:\Tracker\ST909B-4G\Datasheet\pdf_render\a7670_p20_fig600.png').convert('RGB')
S = (3281.0 - 1171.0) / 24.0
X0, Y0 = 1171.0, 1180.0
def px(x, y): return (X0 + S * (x + 12.0), Y0 + S * (y + 12.0))

d = ImageDraw.Draw(im)
def rect(x0, y0, x1, y1, col, w=6):
    d.rectangle([px(x0, y0), px(x1, y1)], outline=col, width=w)
def circle(cx, cy, r, col, w=6):
    x, y = px(cx, cy)
    rp = r * S
    d.ellipse([x - rp, y - rp, x + rp, y + rp], outline=col, width=w)

# middle forbidden area candidates
rect(1.31, 1.88, 3.72, 4.29, (0, 160, 0))    # candidate A (dims 2.40 / 8.30->edge / 7.70->edge)
rect(0.70, 1.30, 3.10, 3.70, (255, 0, 0))    # candidate B (old estimate)
circle(1.85, 2.45, 0.65, (0, 0, 255))        # fiducial dia1.30 from fig3 (r=0.65)
# TL forbidden area candidate
rect(-10.90, -8.75, -9.40, -7.25, (255, 0, 255))

for name, (mx0, my0, mx1, my1) in {
    'a7670_fig4_mid_ov.png': (-1.0, -0.5, 5.8, 6.0),
    'a7670_fig4_tl_ov.png': (-13.5, -11.0, -7.0, -5.5),
}.items():
    a = px(mx0, my0); b = px(mx1, my1)
    c = im.crop((int(a[0]), int(a[1]), int(b[0]), int(b[1])))
    c = c.resize((int(c.width * 1.6), int(c.height * 1.6)), Image.LANCZOS)
    c.save(r'D:\Tracker\ST909B-4G\Datasheet\pdf_img\crop' + '\\' + name)
    print(name, c.size)
