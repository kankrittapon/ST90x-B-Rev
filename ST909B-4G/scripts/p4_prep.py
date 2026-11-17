# p4_prep.py — edge clearance value, U1 poly points, real via scan (stdlib+pcbnew)
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
b = pcbnew.LoadBoard(BOARD)
MM = 1e6


def mm(v):
    return round(v / MM, 3)


ds = b.GetDesignSettings()
for attr in ("m_CopperEdgeClearance", "m_EdgeClearance", "m_HoleToHoleMin",
             "m_SilkMinResolution", "m_MinSilkClearance"):
    try:
        print("DS %s = %s" % (attr, mm(getattr(ds, attr)) if isinstance(getattr(ds, attr), int) and abs(getattr(ds, attr)) > 100 else getattr(ds, attr)))
    except AttributeError:
        print("DS %s : (n/a)" % attr)

print("== U1 silk polys")
for fp in b.GetFootprints():
    if fp.GetReference() != "U1":
        continue
    for d in fp.GraphicalItems():
        if d.GetLayer() != pcbnew.F_SilkS:
            continue
        poly = d.GetPolyShape()
        for oi in range(poly.OutlineCount()):
            ch = poly.Outline(oi)
            pts = ["(%.3f,%.3f)" % (mm(ch.GetPoint(i).x), mm(ch.GetPoint(i).y)) for i in range(ch.PointCount())]
            print("   uuid=%s pts: %s" % (d.m_Uuid.AsString(), " ".join(pts)))

print("== via scan: class-name probe + M3V3 nets + near (16.5,58.5)")
n_via = 0
for t in b.GetTracks():
    cls = t.GetClass()
    is_via = isinstance(t, pcbnew.PCB_VIA)
    if is_via:
        n_via += 1
        p = t.GetPosition()
        net = t.GetNetname()
        if "/M3V3" in net or (abs(mm(p.x) - 16.5) < 1.0 and abs(mm(p.y) - 58.5) < 1.0):
            print("   via cls=%s net=%-10s @ (%.2f,%.2f) drill=%.2f" % (
                cls, net, mm(p.x), mm(p.y), mm(t.GetDrillValue())))
print("total vias:", n_via)
