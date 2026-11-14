# p3_islands2.py — dump fill outline vertex lists to see island shapes
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
b = pcbnew.LoadBoard(BOARD)
MM = 1e6
for z in b.Zones():
    for layer in z.GetLayerSet().Seq():
        if layer not in (pcbnew.F_Cu, pcbnew.B_Cu):
            continue
        ps = z.GetFilledPolysList(layer)
        ln = "F" if layer == pcbnew.F_Cu else "B"
        for i in range(ps.OutlineCount()):
            chain = ps.COutline(i)
            pts = [(round(chain.GetPoint(j).x / MM, 2), round(chain.GetPoint(j).y / MM, 2))
                   for j in range(chain.PointCount())]
            print("net=%s layer=%s poly#%d verts=%d holes=%d" %
                  (z.GetNetname(), ln, i, len(pts), ps.HoleCount(i)))
            for k in range(0, len(pts), 12):
                print("   [%4d] " % k + " ".join("(%s,%.2f)" % (x, y) for x, y in pts[k:k + 12]))
