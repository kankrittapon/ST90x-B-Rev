# p4_text_probe.py — text_height limit + real LED text bbox measurement (no save)
import json
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
NM = 1000000
d = json.load(open(r"D:\Tracker\ST909B-4G\ST909B-4G_drc_violations.json", encoding="utf-8-sig"))

print("== text_height violation details")
for v in d["violations"]:
    if v["type"] == "text_height":
        print("   desc:", v["description"])

b = pcbnew.LoadBoard(BOARD)


def mm(v):
    return round(v / NM, 3)


def tb(f):
    for name in ("GetTextBox", "GetBoundingBox"):
        if hasattr(f, name):
            try:
                box = getattr(f, name)()
                l, r = box.GetLeft(), box.GetRight()
                t, bo = box.GetTop(), box.GetBottom()
                return name, (mm(r) - mm(l)), (mm(bo) - mm(t))
            except Exception as ex:
                print("   (%s failed: %s)" % (name, ex))
    return "none", 0, 0


print("== LED ref text boxes at current size")
for fp in b.GetFootprints():
    if fp.GetReference() in ("LED1", "LED2", "LED3"):
        for f in fp.GetFields():
            if f.GetName() == "Reference":
                m, w, h = tb(f)
                print("   %-5s h=%.2f %s width=%.2f height=%.2f" % (fp.GetReference(), mm(f.GetTextHeight()), m, w, h))

print("== simulate size 0.8 (in-memory)")
for fp in b.GetFootprints():
    if fp.GetReference() in ("LED1", "LED2", "LED3"):
        for f in fp.GetFields():
            if f.GetName() == "Reference":
                if hasattr(f, "SetTextSize"):
                    f.SetTextSize(pcbnew.VECTOR2I(int(0.8 * NM), int(0.8 * NM)))
                m, w, h = tb(f)
                print("   %-5s @0.8 %s width=%.2f height=%.2f" % (fp.GetReference(), m, w, h))

print("== U6 ref box + neighbors")
for fp in b.GetFootprints():
    if fp.GetReference() == "U6":
        for f in fp.GetFields():
            if f.GetName() == "Reference":
                m, w, h = tb(f)
                p = f.GetPosition()
                print("   U6 ref @ (%.2f,%.2f) %s width=%.2f height=%.2f" % (mm(p.x), mm(p.y), m, w, h))

print("== silk segment stroke widths of U6 (bbox sanity)")
for fp in b.GetFootprints():
    if fp.GetReference() == "U6":
        for dd in fp.GraphicalItems():
            if dd.GetLayer() == pcbnew.F_SilkS:
                bb = dd.GetBoundingBox()
                print("   seg bbox y %.3f..%.3f w=%.3f" % (mm(bb.GetTop()), mm(bb.GetBottom()), mm(dd.GetWidth())))
