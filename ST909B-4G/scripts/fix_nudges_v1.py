# fix_nudges_v1.py — แก้ DRC courtyard/clearance 5 คู่ด้วยการขยับตำแหน่ง (คำนวณจาก courtyard ที่วัดได้จริง)
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
b = pcbnew.LoadBoard(BOARD)

def by_ref(ref):
    for fp in b.GetFootprints():
        if fp.GetReference() == ref:
            return fp
    raise KeyError(ref)

def set_pos(fp, x, y, rot=None):
    v = pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6))
    fp.SetPosition(v)
    if rot is not None:
        fp.SetOrientationDegrees(rot)

# --- R2: หมุน 90° + เลื่อนขวาเล็กน้อย ให้พ้นทั้ง R1 (courtyard ถึง x=10.01) และ U4 (เริ่ม x=11.82)
# หมุนแล้ว courtyard กลายเป็น x ±0.75, y ±1.51 ที่ (10.95,54.8) -> x 10.20..11.70, y 53.29..56.31
#   R1 ขวาสุด 10.01 (ช่องว่าง 0.19) / U4 ซ้ายสุด 11.82 (ช่องว่าง 0.12) / AE2 keepout y<=53 (pad ลึกสุด 53.97)
set_pos(by_ref("R2"), 10.95, 54.80, rot=90)

# --- TP4: 2.5 -> 2.2 (U2 courtyard เริ่ม x=3.62, TP4 จบที่ 3.43)
set_pos(by_ref("TP4"), 2.2, 52.0)

# --- แถว TP ด้านล่าง (B.Cu, y=71.5): pitch >= 2.9 ทุกคู่
# TP6 19.6 | TP7 22.5 (คงเดิม) | TP8 25.4 | TP5 28.3
set_pos(by_ref("TP6"), 19.6, 71.5)
set_pos(by_ref("TP8"), 25.4, 71.5)
set_pos(by_ref("TP5"), 28.3, 71.5)

b.Save(BOARD)
print("saved. moved: R2(rot90,(10.95,54.8)) TP4(2.2,52) TP6(19.6,71.5) TP8(25.4,71.5) TP5(28.3,71.5)")
