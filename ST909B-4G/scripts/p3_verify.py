# p3_verify.py — numeric Euclidean clearance verifier for P3 batch-3+4 candidates.
# Loads board, extracts tracks/vias/pads/Edge.Cuts as primitives, checks candidates
# against existing items (layer-aware, net-aware) + new-vs-new + structural rules.
# Vias assumed 0.6/0.3 (all vias in this project). min clearance 0.20, edge 0.50.
import math
import pcbnew

TOL = 0.195          # flag clearance < this (board min 0.20)
EDGE_MIN = 0.4995    # min_copper_edge_clearance 0.50
BOARD_FILE = "ST909B-4G.kicad_pcb"
VIA_R = 0.30
CAN = (2.10, 6.60, 23.90, 28.40)      # U1 shield can interior (F tracks forbidden)
KEEPOUT = (2.50, 35.00, 20.50, 53.00) # B.Cu keepout rect
def _cs(b):  # bounds -> (cx, cy, sx, sy)
    return ((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0, b[2] - b[0], b[3] - b[1])
CAN_C = _cs(CAN)
KEEPOUT_C = _cs(KEEPOUT)

# ---------------- geometry helpers ----------------
def d_pt_seg(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    l2 = vx * vx + vy * vy
    if l2 == 0.0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * vx + (py - ay) * vy) / l2
    t = 0.0 if t < 0 else (1.0 if t > 1 else t)
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))

def orient(ax, ay, bx, by, cx, cy):
    v = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
    return 0 if abs(v) < 1e-12 else (1 if v > 0 else -1)

def on_seg(ax, ay, bx, by, px, py):
    return (min(ax, bx) - 1e-12 <= px <= max(ax, bx) + 1e-12 and
            min(ay, by) - 1e-12 <= py <= max(ay, by) + 1e-12)

def d_seg_seg(a, b):
    x1, y1, x2, y2 = a
    x3, y3, x4, y4 = b
    o1 = orient(x1, y1, x2, y2, x3, y3)
    o2 = orient(x1, y1, x2, y2, x4, y4)
    o3 = orient(x3, y3, x4, y4, x1, y1)
    o4 = orient(x3, y3, x4, y4, x2, y2)
    if o1 != o2 and o3 != o4:
        return 0.0
    if o1 == 0 and on_seg(x1, y1, x2, y2, x3, y3):
        return 0.0
    if o2 == 0 and on_seg(x1, y1, x2, y2, x4, y4):
        return 0.0
    if o3 == 0 and on_seg(x3, y3, x4, y4, x1, y1):
        return 0.0
    if o4 == 0 and on_seg(x3, y3, x4, y4, x2, y2):
        return 0.0
    return min(d_pt_seg(x3, y3, x1, y1, x2, y2), d_pt_seg(x4, y4, x1, y1, x2, y2),
               d_pt_seg(x1, y1, x3, y3, x4, y4), d_pt_seg(x2, y2, x3, y3, x4, y4))

def d_pt_rect(px, py, cx, cy, sx, sy):
    dx = max(0.0, abs(px - cx) - sx / 2.0)
    dy = max(0.0, abs(py - cy) - sy / 2.0)
    return math.hypot(dx, dy)

def d_rect_seg(cx, cy, sx, sy, seg):
    # 0 if segment penetrates rect interior, else dist to boundary
    if d_pt_rect((seg[0] + seg[2]) / 2, (seg[1] + seg[3]) / 2, cx, cy, sx, sy) == 0.0:
        return 0.0
    edges = ((cx - sx/2, cy - sy/2, cx + sx/2, cy - sy/2),
             (cx + sx/2, cy - sy/2, cx + sx/2, cy + sy/2),
             (cx + sx/2, cy + sy/2, cx - sx/2, cy + sy/2),
             (cx - sx/2, cy + sy/2, cx - sx/2, cy - sy/2))
    return min(d_seg_seg(seg, e) for e in edges)

def d_rect_rect(a, b):
    gx = (a[2] + b[2]) / 2 - abs(a[0] - b[0])
    gy = (a[3] + b[3]) / 2 - abs(a[1] - b[1])
    if gx > 0 and gy > 0:
        return 0.0
    return math.hypot(max(0.0, -gx), max(0.0, -gy))

def shape_dist(i1, i2):
    k1, s1, r1 = i1[0], i1[3], i1[4]
    k2, s2, r2 = i2[0], i2[3], i2[4]
    # kinds: trk = seg + halfwidth; via = point + radius; pad = rect + 0
    if k1 == "trk" and k2 == "trk":
        base = d_seg_seg(s1, s2)
    elif k1 == "trk" and k2 == "via":
        base = d_pt_seg(s2[0], s2[1], *s1)
    elif k1 == "trk" and k2 == "pad":
        base = d_rect_seg(s2[0], s2[1], s2[2], s2[3], s1)
    elif k1 == "via" and k2 == "trk":
        base = d_pt_seg(s1[0], s1[1], *s2)
    elif k1 == "via" and k2 == "via":
        base = math.hypot(s1[0] - s2[0], s1[1] - s2[1])
    elif k1 == "via" and k2 == "pad":
        base = d_pt_rect(s1[0], s1[1], *s2)
    elif k1 == "pad" and k2 == "pad":
        base = d_rect_rect(s1, s2)
    else:
        base = shape_dist(i2, i1)
    return max(0.0, base - r1 - r2)

def interact(l1, l2):
    return "EDGE" in (l1, l2) or "FB" in (l1, l2) or l1 == l2

# ---------------- load board primitives ----------------
def mm(v):
    return pcbnew.ToMM(int(v))

def load_items():
    brd = pcbnew.LoadBoard(BOARD_FILE)
    items = []
    for t in brd.GetTracks():
        if t.GetClass() == "PCB_VIA":
            p = t.GetPosition()
            items.append(("via", "FB", t.GetNetname(), (mm(p.x), mm(p.y)), VIA_R, "existing"))
        else:
            s, e = t.GetStart(), t.GetEnd()
            lay = "F" if t.IsOnLayer(pcbnew.F_Cu) else "B"
            items.append(("trk", lay, t.GetNetname(),
                          (mm(s.x), mm(s.y), mm(e.x), mm(e.y)), t.GetWidth() / 2 / 1e6 * 1e0, "existing"))
    for fp in brd.GetFootprints():
        for pad in fp.Pads():
            p = pad.GetPosition()
            sz = pad.GetSize()
            f = pad.IsOnLayer(pcbnew.F_Cu)
            b = pad.IsOnLayer(pcbnew.B_Cu)
            lay = "FB" if (f and b) else ("F" if f else "B")
            items.append(("pad", lay, pad.GetNetname(),
                          (mm(p.x), mm(p.y), mm(sz.x) , mm(sz.y)), 0.0, "existing"))
    for d in brd.GetDrawings():
        if d.GetClass() == "PCB_SHAPE" and d.IsOnLayer(pcbnew.Edge_Cuts):
            s, e = d.GetStart(), d.GetEnd()
            if d.GetShape() == pcbnew.SHAPE_T_RECT:
                x1, y1, x2, y2 = mm(s.x), mm(s.y), mm(e.x), mm(e.y)
                for seg in ((x1, y1, x2, y1), (x2, y1, x2, y2),
                            (x2, y2, x1, y2), (x1, y2, x1, y1)):
                    items.append(("trk", "EDGE", "", seg, 0.0, "existing"))
            else:
                items.append(("trk", "EDGE", "", (mm(s.x), mm(s.y), mm(e.x), mm(e.y)), 0.0, "existing"))
    return items

# fix track width units (GetWidth returns nm; ToMM already applied to coords)
# ---------------- candidates (batch-3 + batch-4) ----------------
def T(lay, net, x1, y1, x2, y2, w=0.25):
    return ("trk", lay, net, (x1, y1, x2, y2), w / 2.0, "new")

def V(net, x, y):
    return ("via", "FB", net, (x, y), VIA_R, "new")

PKEY, VDD, TXD, RXD = "/PKEY", "/VDD_EXT", "/4G_TXD_1V8", "/4G_RXD_1V8"
DPM, DMM = "/USB_DP_M", "/USB_DM_M"

CANDIDATES = [
    # --- PKEY: F west lane x=0.80 -> via (1.65,29.35) -> B v x=1.625 -> h y=60.10
    #     -> v x=10.15 -> h y=66.30 -> v x=4.00 -> h y=70.40 -> island via ---
    T("F", PKEY, 1.70, 9.50, 0.60, 9.50, w=0.20),
    T("F", PKEY, 0.60, 9.50, 0.60, 29.35, w=0.20),
    T("F", PKEY, 0.60, 29.35, 1.65, 29.35, w=0.20),
    V(PKEY, 1.65, 29.35),
    T("B", PKEY, 1.625, 29.35, 1.625, 60.10),
    T("B", PKEY, 1.625, 60.10, 10.15, 60.10),
    T("B", PKEY, 10.15, 60.10, 10.15, 66.30),
    T("B", PKEY, 10.15, 66.30, 4.00, 66.30),
    T("B", PKEY, 4.00, 66.30, 4.00, 70.40),
    T("B", PKEY, 4.00, 70.40, 17.75, 70.40),
    # --- VDD: via-in-pad U1.15 -> B v x=1.70 -> h y=25.00 -> east v x=27.70 ---
    V(VDD, 1.70, 23.50),
    T("B", VDD, 1.70, 23.50, 1.70, 25.00),
    T("B", VDD, 1.70, 25.00, 27.70, 25.00),
    T("B", VDD, 27.70, 25.00, 27.70, 32.05),
    V(VDD, 27.70, 32.05),
    # --- TXD: via-in-pad U1.9 -> h y=17.50 -> v x=2.80 -> lane y=22.00 -> east v x=29.35 ---
    V(TXD, 1.70, 17.50),
    T("B", TXD, 1.70, 17.50, 2.80, 17.50),
    T("B", TXD, 2.80, 17.50, 2.80, 22.00),
    T("B", TXD, 2.80, 22.00, 29.35, 22.00),
    T("B", TXD, 29.35, 22.00, 29.35, 33.00),
    V(TXD, 29.35, 33.00),
    T("F", TXD, 29.35, 33.00, 28.36, 33.00),
    # --- RXD: via-in-pad U1.10 -> h y=18.50 -> v x=2.35 -> lane y=24.30 -> east v x=28.50 ---
    V(RXD, 1.70, 18.50),
    T("B", RXD, 1.70, 18.50, 2.35, 18.50),
    T("B", RXD, 2.35, 18.50, 2.35, 24.30),
    T("B", RXD, 2.35, 24.30, 28.50, 24.30),
    T("B", RXD, 28.50, 24.30, 28.50, 33.95),
    V(RXD, 28.50, 33.95),
    # --- DP_M: via-in-pad U1.27 -> B -> island B v x=22.40 ---
    V(DPM, 14.00, 28.90),
    T("B", DPM, 14.00, 28.90, 14.00, 27.70),
    T("B", DPM, 14.00, 27.70, 25.00, 27.70),
    T("B", DPM, 25.00, 27.70, 25.00, 57.75),
    T("B", DPM, 25.00, 57.75, 22.40, 57.75),
    # --- DM_M: via-in-pad U1.28 -> B -> via 24.30 -> F -> island via (19.90,58.00) ---
    V(DMM, 15.00, 28.90),
    T("B", DMM, 15.00, 28.90, 15.00, 28.20),
    T("B", DMM, 15.00, 28.20, 24.10, 28.20),
    T("B", DMM, 24.10, 28.20, 24.10, 57.00),
    T("B", DMM, 24.10, 57.00, 24.30, 57.00),
    V(DMM, 24.30, 57.00),
    T("F", DMM, 24.30, 57.00, 24.30, 59.50),
    T("F", DMM, 24.30, 59.50, 19.90, 59.50),
    T("F", DMM, 19.90, 59.50, 19.90, 58.00),
    # --- batch 5: GND stitching vias (island repair) ---
    # (2.50,71.20): F main (poly#0) + B island (poly#0) -> bridges B island to F main.
    #   Hand-check: 1.175 to PKEY B h y=70.40 west cap, 1.138 to PKEY B v x=4.00,
    #   2.45 to VBAT B h y=69.50 west cap, 2.41 to J5 VBAT F pad corner.
    V("/GND", 2.50, 71.20),
    # (30.00,15.00): F island (poly#1 NE block) + B main (poly#1) -> bridges F island
    #   to B main. Hand-check: 2.875 to BOOT F v x=27.00, 2.175 to SOS B v x=32.30,
    #   4.5 to LED_CHR B h y=15.45 east cap, 4.85 to LED_EN via (26.05,12.20).
    V("/GND", 30.00, 15.00),
]

# ---------------- run checks ----------------
def main():
    ex = load_items()
    viol = 0
    # new vs existing
    for ci, c in enumerate(CANDIDATES):
        for e in ex:
            if e[5] != "existing":
                continue
            if not interact(c[1], e[1]):
                continue
            n1, n2 = c[2], e[2]
            if n1 == n2 or n1 == "" or n2 == "":
                # same net / no-net: still check EDGE + short (overlap = 0) separately below
                if n1 != n2 and (n1 == "" or n2 == ""):
                    pass  # no-net: skip clearance
                if e[1] != "EDGE":
                    continue
            d = shape_dist(c, e)
            if e[1] == "EDGE":
                lim = EDGE_MIN
            else:
                lim = TOL
            if d < lim:
                print("VIOL n-vs-e [%d] %s %s  vs  %s %s %s  d=%.4f" %
                      (ci, c[2], c[3], e[2], e[1], e[3], d))
                viol += 1
    # new vs new
    for i in range(len(CANDIDATES)):
        for j in range(i + 1, len(CANDIDATES)):
            a, b = CANDIDATES[i], CANDIDATES[j]
            if not interact(a[1], b[1]):
                continue
            if a[2] == b[2] or a[2] == "" or b[2] == "":
                continue
            d = shape_dist(a, b)
            if d < TOL:
                print("VIOL n-vs-n [%d] %s %s  vs  [%d] %s %s  d=%.4f" %
                      (i, a[2], a[3], j, b[2], b[3], d))
                viol += 1
    # structural: F tracks must not enter can interior; via centers outside can
    for ci, c in enumerate(CANDIDATES):
        if c[0] == "trk" and c[1] == "F":
            seg = c[3]
            if d_rect_seg(*CAN_C, seg) < c[4] - 1e-6:
                print("VIOL F-can [%d] %s %s" % (ci, c[2], seg))
                viol += 1
        if c[0] == "via":
            x, y = c[3]
            if CAN[0] < x < CAN[2] and CAN[1] < y < CAN[3]:
                print("VIOL via-in-can [%d] %s (%.2f,%.2f)" % (ci, c[2], x, y))
                viol += 1
        if c[0] == "trk" and c[1] == "B":
            if d_rect_seg(*KEEPOUT_C, c[3]) < c[4] - 1e-6:
                print("VIOL keepout-B [%d] %s %s" % (ci, c[2], c[3]))
                viol += 1
    print("candidates=%d  violations=%d" % (len(CANDIDATES), viol))

main()
