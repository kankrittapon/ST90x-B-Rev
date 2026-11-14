# gen_footprints.py — เขียน footprint จริงของ U1 (A7670SA LGA-88) และ U2 (L76KB LGA-18)
# geometry ล็อกจาก datasheet แล้ว cross-check ด้วยการวัดพิกเซล + overlay:
#   U1: A7670 HW Design V1.00 fig.4 (p20, recommended PCB footprint) + fig.2 (p13, top view)
#       - module 24x24, edge pads 17/side pitch 1.0 span 16.0 (centers +-8 along edge),
#         center 0.60 from module edge (radial +-11.40), pad 0.60(along) x 0.80(deep)
#       - inner grid 2.10x2.10 pitch 3.80 (rows/cols 0, +-3.80, +-7.60), 20 pads (69-88)
#       - Forbidden Area TL: 1.50x1.50 ที่ 1.10 จากขอบซ้าย / 3.25 จากขอบบน (center -10.15,-8.00)
#       - Forbidden Area MID: 2.40x2.40 (8.30 จากขอบขวา / 7.70 จากขอบล่าง -> x +1.30..+3.70, y +1.90..+4.30)
#         (ยืนยันด้วย overlay + การวัดขอบจริง 1.31..3.72 / 1.88..4.29)
#       - fiducial dia1.30 ที่ (+1.85,+2.45) จาก fig.3 Bot View (9.50/8.90 จาก pad ซ้าย/ล่าง, mirror x)
#       - Keep out Area 25x00x25.00 (dashed) = courtyard +-12.5
#   U2: L76K HW Design V1.1 fig.15 (p28, recommended footprint)
#       - pad obround 1.8x0.8, 9/side, pitch 1.1, pad centers บนขอบโมดูล (span 9.70),
#         แถวสมมาตร +-4.40, module 9.70x10.10
import uuid

LIB = r"D:\Tracker\ST909B-4G\lib\ST909B.pretty"
PAD_LAYERS = '"F.Cu" "F.Paste" "F.Mask"'


def u():
    return str(uuid.uuid4())


def fmt(v):
    s = '%.4f' % v
    s = s.rstrip('0').rstrip('.')
    return s if s else '0'


def pad(num, x, y, w, h, shape='rect'):
    return ('  (pad "%s" smd %s\n'
            '    (at %s %s)\n'
            '    (size %s %s)\n'
            '    (layers %s)\n'
            '    (uuid "%s")\n'
            '  )\n') % (num, shape, fmt(x), fmt(y), fmt(w), fmt(h), PAD_LAYERS, u())


def rect(x0, y0, x1, y1, layer, width):
    return ('  (fp_rect (start %s %s) (end %s %s)\n'
            '    (stroke (width %s) (type default)) (fill none)\n'
            '    (layer "%s") (uuid "%s")\n'
            '  )\n') % (fmt(x0), fmt(y0), fmt(x1), fmt(y1), fmt(width), layer, u())


def line(x0, y0, x1, y1, layer, width):
    return ('  (fp_line (start %s %s) (end %s %s)\n'
            '    (stroke (width %s) (type default))\n'
            '    (layer "%s") (uuid "%s")\n'
            '  )\n') % (fmt(x0), fmt(y0), fmt(x1), fmt(y1), fmt(width), layer, u())


def circle(cx, cy, r, layer, width):
    return ('  (fp_circle (center %s %s) (end %s %s)\n'
            '    (stroke (width %s) (type default)) (fill none)\n'
            '    (layer "%s") (uuid "%s")\n'
            '  )\n') % (fmt(cx), fmt(cy), fmt(cx + r), fmt(cy), fmt(width), layer, u())


def poly(pts, layer, width=0):
    p = ' '.join('(xy %s %s)' % (fmt(x), fmt(y)) for x, y in pts)
    return ('  (fp_poly\n'
            '    (pts %s)\n'
            '    (stroke (width %s) (type default)) (fill solid)\n'
            '    (layer "%s") (uuid "%s")\n'
            '  )\n') % (p, fmt(width), layer, u())


def text(s, x, y, layer, size, thick, rot=0):
    return ('  (fp_text user "%s" (at %s %s %s)\n'
            '    (layer "%s") (uuid "%s")\n'
            '    (effects (font (size %s %s) (thickness %s)))\n'
            '  )\n') % (s, fmt(x), fmt(y), fmt(rot) if rot else '0', layer, u(),
                        fmt(size), fmt(size), fmt(thick))


def prop(name, val, x, y, layer, size):
    return ('  (property "%s" "%s" (at %s %s 0)\n'
            '    (layer "%s") (uuid "%s")\n'
            '    (effects (font (size %s %s) (thickness 0.15)))\n'
            '  )\n') % (name, val, fmt(x), fmt(y), layer, u(), fmt(size), fmt(size))


def write_fp(fname, body):
    path = LIB + '\\' + fname
    with open(path, 'w', encoding='utf-8') as f:
        f.write(body)
    print('wrote', path, len(body), 'bytes')


# ---------------------------------------------------------------- U1
inner = [
    (69, -7.6, -7.6), (84, -3.8, -7.6), (83, 0.0, -7.6), (82, 3.8, -7.6), (81, 7.6, -7.6),
    (70, -7.6, -3.8), (88, 0.0, -3.8), (80, 7.6, -3.8),
    (71, -7.6, 0.0), (85, -3.8, 0.0), (87, 3.8, 0.0), (79, 7.6, 0.0),
    (72, -7.6, 3.8), (86, 0.0, 3.8), (78, 7.6, 3.8),
    (73, -7.6, 7.6), (74, -3.8, 7.6), (75, 0.0, 7.6), (76, 3.8, 7.6), (77, 7.6, 7.6),
]
assert len(inner) == 20

pads_u1 = []
for i in range(17):   # ซ้าย: 1..17 บน->ล่าง
    pads_u1.append(pad(1 + i, -11.4, -8.0 + i, 0.8, 0.6))
for i in range(17):   # ล่าง: 18..34 ซ้าย->ขวา
    pads_u1.append(pad(18 + i, -8.0 + i, 11.4, 0.6, 0.8))
for i in range(17):   # ขวา: 35..51 ล่าง->บน
    pads_u1.append(pad(35 + i, 11.4, 8.0 - i, 0.8, 0.6))
for i in range(17):   # บน: 52..68 ขวา->ซ้าย
    pads_u1.append(pad(52 + i, 8.0 - i, -11.4, 0.6, 0.8))
for n, x, y in inner:
    pads_u1.append(pad(n, x, y, 2.1, 2.1))
assert len(pads_u1) == 88

body_u1 = (
    '(footprint "A7670SA_LGA88"\n'
    '  (version 20241229)\n'
    '  (generator "kicad-mcp")\n'
    '  (generator_version "9.0")\n'
    '  (layer "F.Cu")\n'
    '  (descr "SIMCom A7670SA LGA-88 4G module land pattern, module 24.0x24.0mm; '
    'edge pads 17/side 0.6x0.8 pitch 1.0 (centers +-8 along edge, 0.60 from module edge), '
    'inner grid 2.10x2.10 pitch 3.80 (20 pads); per A7670 HW Design V1.00 fig.4 (p20) + fig.2 (p13); '
    '2x Forbidden Area marked on F.Fab (no copper/vias); keep-out 25x25 = courtyard (fig.4 dashed); '
    'pin map per pin_table/U1_A7670SA_pins.csv (V1.00 generic, verify V1.03 SA)")\n'
    '  (tags "A7670SA SIMCom LGA88 4G module land pattern")\n'
    '\n'
    + prop('Reference', 'REF**', 0, -13.6, 'F.SilkS', 1.2)
    + prop('Value', 'A7670SA_LGA88', 0, 0, 'F.Fab', 2.0)
    + prop('Datasheet', '', 0, 0, 'F.Fab', 1.0)
    + '\n'
    # module outline (Mold Area) 24x24
    + rect(-12, -12, 12, 12, 'F.Fab', 0.1)
    # Forbidden Area มุมซ้ายบน 1.50x1.50 (1.10 จากขอบซ้าย, 3.25 จากขอบบน)
    + rect(-10.9, -8.75, -9.4, -7.25, 'F.Fab', 0.12)
    + text('Forbidden Area', -10.15, -6.15, 'F.Fab', 0.7, 0.1)
    # Forbidden Area กลาง 2.40x2.40 (8.30 จากขอบขวา, 7.70 จากขอบล่าง)
    + rect(1.3, 1.9, 3.7, 4.3, 'F.Fab', 0.12)
    + text('Forbidden Area', 2.5, 5.5, 'F.Fab', 0.7, 0.1)
    # fiducial dia 1.30 (fig.3 Bot View) เอกสารเท่านั้น
    + circle(1.85, 2.45, 0.65, 'F.Fab', 0.1)
    + line(0.95, 2.45, 2.75, 2.45, 'F.Fab', 0.1)
    + line(1.85, 1.55, 1.85, 3.35, 'F.Fab', 0.1)
    + text('1', -10.7, -9.8, 'F.Fab', 0.8, 0.12)
    + '\n'
    # pin-1 triangle (นอกโมดูล ชี้ที่ pad 1)
    + poly([(-13.1, -8.6), (-13.1, -7.4), (-12.15, -8.0)], 'F.SilkS')
    + '\n'
    # courtyard = Keep out Area 25x00x25.00 (fig.4 dashed)
    + rect(-12.5, -12.5, 12.5, 12.5, 'F.CrtYd', 0.05)
    + '\n'
    + ''.join(pads_u1)
    + ')\n'
)
write_fp('A7670SA_LGA88.kicad_mod', body_u1)

# ---------------------------------------------------------------- U2
pads_u2 = []
for k in range(9):    # ซ้าย: 1..9 บน->ล่าง
    pads_u2.append(pad(1 + k, -4.85, -4.4 + 1.1 * k, 1.8, 0.8, 'oval'))
for k in range(9):    # ขวา: 10..18 ล่าง->บน
    pads_u2.append(pad(10 + k, 4.85, 4.4 - 1.1 * k, 1.8, 0.8, 'oval'))
assert len(pads_u2) == 18

body_u2 = (
    '(footprint "L76KB_LGA18"\n'
    '  (version 20241229)\n'
    '  (generator "kicad-mcp")\n'
    '  (generator_version "9.0")\n'
    '  (layer "F.Cu")\n'
    '  (descr "Quectel L76KB (L76K package) GNSS module land pattern, module 9.7x10.1mm; '
    '18 castellated pads 1.8x0.8 pitch 1.1, pad centers ON module edges (span 9.70), rows +-4.40; '
    'per L76K HW Design V1.1 fig.15 (p28, 6.2 recommended footprint); '
    'pin map per pin_table/U2_L76KB_pins.csv (L76K cn V1.1, verify L76KB-A58)")\n'
    '  (tags "L76KB L76K Quectel GNSS module castellated land pattern")\n'
    '\n'
    + prop('Reference', 'REF**', 0, -7.0, 'F.SilkS', 1.0)
    + prop('Value', 'L76KB_LGA18', 0, 0, 'F.Fab', 1.2)
    + prop('Datasheet', '', 0, 0, 'F.Fab', 1.0)
    + '\n'
    + rect(-4.85, -5.05, 4.85, 5.05, 'F.Fab', 0.1)
    + '\n'
    + poly([(-4.55, -5.85), (-5.15, -5.85), (-4.85, -5.15)], 'F.SilkS')
    + '\n'
    + rect(-6.0, -5.9, 6.0, 5.9, 'F.CrtYd', 0.05)
    + '\n'
    + ''.join(pads_u2)
    + ')\n'
)
write_fp('L76KB_LGA18.kicad_mod', body_u2)

# ---------------------------------------------------------------- sanity: โหลดกลับด้วย pcbnew
import pcbnew
for fn, want in (('A7670SA_LGA88.kicad_mod', 88), ('L76KB_LGA18.kicad_mod', 18)):
    fp = pcbnew.FootprintLoad(LIB, fn[:-10])
    pads = list(fp.Pads())
    nums = sorted(int(p.GetPadName()) for p in pads)
    assert len(pads) == want, (fn, len(pads))
    assert nums == list(range(1, want + 1)), fn
    bb = fp.GetBoundingBox()
    print('%s OK: pads=%d bbox %.2f x %.2f mm' % (
        fn, len(pads), pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight())))
    p1 = fp.FindPadByNumber('1')
    print('   pad1 at (%.3f, %.3f) size (%.3f, %.3f)' % (
        pcbnew.ToMM(p1.GetPosition().x), pcbnew.ToMM(p1.GetPosition().y),
        pcbnew.ToMM(p1.GetSize().x), pcbnew.ToMM(p1.GetSize().y)))
