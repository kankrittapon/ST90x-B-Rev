# assign_nets_fix1.py — แก้ 2 pad ที่ SetNet ไม่ติดจากรอบก่อน
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
FIX = {("/GND"): [("R3", "2")], ("/LED_EN"): [("U4", "9")]}

b = pcbnew.LoadBoard(BOARD)
pads = {}
for fp in b.GetFootprints():
    for p in fp.Pads():
        pads[(fp.GetReference(), str(p.GetNumber()))] = p

for netname, pairs in FIX.items():
    ni = b.FindNet(netname)
    print("FindNet", netname, "->", ni, "code", ni.GetNetCode() if ni else None)
    if ni is None:
        ni = pcbnew.NETINFO_ITEM(b, netname)
        b.Add(ni)
        print("  created, new code", ni.GetNetCode())
    for ref, pad in pairs:
        p = pads[(ref, pad)]
        print("before:", ref + "/" + pad, repr(p.GetNetname()))
        try:
            p.SetNet(ni)
        except AttributeError:
            p.SetNetCode(ni.GetNetCode())
        print("after in-memory:", ref + "/" + pad, repr(p.GetNetname()))

b.Save(BOARD)
b2 = pcbnew.LoadBoard(BOARD)
for fp in b2.GetFootprints():
    if fp.GetReference() in ("R3", "U4"):
        for p in fp.Pads():
            n = p.GetNetname()
            if n and not n.startswith("unconnected"):
                print("disk:", fp.GetReference() + "/" + str(p.GetNumber()), repr(n))
