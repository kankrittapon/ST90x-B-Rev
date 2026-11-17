# p4_silk_dump.py — inventory: per footprint: fields (ref/value), silk graphics (bbox), pads
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
b = pcbnew.LoadBoard(BOARD)
MM = 1e6


def mm(v):
    return round(v / MM, 3)


for fp in sorted(b.GetFootprints(), key=lambda f: f.GetReference()):
    ref = fp.GetReference()
    side = "F" if fp.GetLayer() == pcbnew.F_Cu else "B"
    p = fp.GetPosition()
    print("== %s  side=%s  pos=(%.2f,%.2f) rot=%.1f" % (ref, side, mm(p.x), mm(p.y), fp.GetOrientationDegrees()))
    for pad in fp.Pads():
        pp = pad.GetPosition()
        sz = pad.GetSize()
        nets = pad.GetNetname()
        ly = "F" if pad.IsOnLayer(pcbnew.F_Cu) else "B"
        print("   pad %-3s %-14s @(%7.2f,%7.2f) size=(%.2f,%.2f) %s" % (
            pad.GetPadName(), nets, mm(pp.x), mm(pp.y), mm(sz.x), mm(sz.y), ly))
    for f in fp.GetFields():
        fp2 = f.GetPosition()
        if f.GetName() == "Reference":
            print("   REF  @(%7.2f,%7.2f) h=%.2f th=%.2f layer=%d  '%s'" % (
                mm(fp2.x), mm(fp2.y), mm(f.GetTextHeight()), mm(f.GetTextThickness()), f.GetLayer(), f.GetShownText(False)))
    for d in fp.GraphicalItems():
        if not (d.GetLayer() == pcbnew.F_SilkS or d.GetLayer() == pcbnew.B_SilkS):
            continue
        bb = d.GetBoundingBox()
        sl = "F" if d.GetLayer() == pcbnew.F_SilkS else "B"
        print("   silk %-9s %-5s bbox x %.2f..%.2f  y %.2f..%.2f" % (
            d.GetShape(), sl, mm(bb.GetLeft()), mm(bb.GetRight()), mm(bb.GetTop()), mm(bb.GetBottom())))
        if d.GetShape() == "POLY":
            poly = d.GetPolyShape()
            for oi in range(poly.OutlineCount()):
                ch = poly.Outline(oi)
                pts = ["(%.2f,%.2f)" % (mm(ch.GetPoint(i).x), mm(ch.GetPoint(i).y)) for i in range(ch.PointCount())]
                print("      poly pts: %s" % " ".join(pts))

print("== via (16.5,58.5) check")
for t in b.GetTracks():
    if t.GetClass() == "VIA":
        vp = t.GetPosition()
        if abs(mm(vp.x) - 16.5) < 0.01 and abs(mm(vp.y) - 58.5) < 0.01:
            print("   found via net=%s" % t.GetNetname())
