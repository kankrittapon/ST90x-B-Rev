# Fix SH1 shield fence: Ø0.8 pads, pitch 2.2 (10 pads), keep origin (11.3,57.6)
import pcbnew

PATH = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
FP_X, FP_Y = 11.3, 57.6
SIZE = 0.8
# local offsets (lx, ly) for pads 1..10; pad 11 deleted
POS = {
    "1": (0.0, 0.0), "2": (0.0, 2.2), "3": (0.0, 4.4), "4": (0.0, 6.6),
    "5": (0.0, 8.8),                      # corner
    "6": (2.7, 8.8), "7": (4.9, 8.8), "8": (7.1, 8.8),
    "9": (9.3, 8.8), "10": (11.5, 8.8),
}

b = pcbnew.LoadBoard(PATH)
fp = b.FindFootprintByReference("SH1")
assert fp, "SH1 not found"
done, removed = [], []
for pad in list(fp.Pads()):
    name = pad.GetPadName()
    if name == "11":
        fp.Remove(pad); removed.append(name); continue
    lx, ly = POS[name]
    pad.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(FP_X + lx), pcbnew.FromMM(FP_Y + ly)))
    pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(SIZE), pcbnew.FromMM(SIZE)))
    pad.SetNetCode(b.FindNet("/GND").GetNetCode())
    done.append((name, round(FP_X + lx, 2), round(FP_Y + ly, 2)))
pcbnew.SaveBoard(PATH, b)
print("fence pads:", done)
print("removed:", removed)
