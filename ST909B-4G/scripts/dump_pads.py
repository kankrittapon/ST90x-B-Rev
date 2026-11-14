# dump_pads.py — พิกัด pad จริงของ nets ที่ต้อง route + รายการ DRC courtyard/clearance ฉบับเต็ม
import pcbnew, json, collections

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
b = pcbnew.LoadBoard(BOARD)

SKIP = ("unconnected",)
wants = ["GND", "VBAT", "+5V", "4G_TXD_3V3", "4G_RXD_3V3", "USB_DP_F", "USB_DP_M",
         "USB_DM_F", "USB_DM_M", "GPS_TX", "GPS_RX", "M3V3", "PKEY", "SOS",
         "LED_EN", "LED_K", "LED_GPS", "LED_CHR", "LED_4G", "BOOT"]
out = collections.defaultdict(list)
for fp in b.GetFootprints():
    for p in fp.Pads():
        n = p.GetNetname()
        if not n:
            continue
        base = n.lstrip("/")
        if base in wants or base.startswith("unconnected") is False and base in wants:
            pass
        if base in wants:
            c = p.GetCenter()
            out[base].append(f"{fp.GetReference()}/{p.GetNumber()}@({c.x/1e6:.2f},{c.y/1e6:.2f},{pcbnew.B_Cu if p.IsOnLayer(pcbnew.B_Cu) else 'F'},{p.GetSizeX()/1e6:.1f}x{p.GetSizeY()/1e6:.1f})")
for k in wants:
    print(k, "=", " ".join(sorted(out[k])))

print()
print("U4 pad positions (1-17):")
for fp in b.GetFootprints():
    if fp.GetReference() == "U4":
        pads = {int(p.GetNumber()): p for p in fp.Pads() if str(p.GetNumber()).isdigit()}
        for i in sorted(pads)[:24]:
            c = pads[i].GetCenter()
            print(f"  {i}: ({c.x/1e6:.2f},{c.y/1e6:.2f}) {pads[i].GetSizeX()/1e6:.2f}x{pads[i].GetSizeY()/1e6:.2f} {'B' if pads[i].IsOnLayer(pcbnew.B_Cu) else 'F'}")
        print("  orient:", fp.GetOrientationDegrees(), " pos:", fp.GetPosition().x/1e6, fp.GetPosition().y/1e6)

print()
for fp in b.GetFootprints():
    if fp.GetReference() in ("RN1", "U5", "U6", "U7", "R3"):
        print(fp.GetReference(), "pads:", " ".join(
            f"{p.GetNumber()}:({p.GetCenter().x/1e6:.2f},{p.GetCenter().y/1e6:.2f})" for p in fp.Pads()))
