# p3_gnd_graph.py — parse .kicad_pcb (stdlib): GND TH pads + via nets + F<->B bridges
import math
import re

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
txt = open(BOARD, encoding="utf-8").read()

# ---- footprints with absolute origins + rotation ----
fps = []
for m in re.finditer(r'\(footprint "([^"]*)"\s*\(layer "(\w+\.Cu)"\)\s*\(uuid[^)]*\)\s*\(at ([\d.\-]+) ([\d.\-]+)(?: ([\d.\-]+))?\)', txt):
    fps.append({"name": m.group(1), "layer": m.group(2), "x": float(m.group(3)),
                "y": float(m.group(4)), "rot": float(m.group(5) or 0), "start": m.start()})
fps.sort(key=lambda f: f["start"])
# pads inside each footprint span
for i, fp in enumerate(fps):
    fp["end"] = fps[i + 1]["start"] if i + 1 < len(fps) else len(txt)


def to_abs(fp, dx, dy):
    r = math.radians(fp["rot"])
    x = dx * math.cos(r) + dy * math.sin(r)
    y = -dx * math.sin(r) + dy * math.cos(r)
    return fp["x"] + x, fp["y"] + y


gnd_th, gnd_f, gnd_b = [], [], []
for fp in fps:
    body = txt[fp["start"]:fp["end"]]
    for pm in re.finditer(r'\(pad "([^"]*)" (\w+) \w+\s*\(at ([\d.\-]+) ([\d.\-]+)[^)]*\)\s*\(size ([\d.]+) ([\d.]+)\)\s*\(layers "([^"]*)"[^)]*?\(net "([^"]*)"\)', body):
        name, kind, dx, dy, w, h, layers, net = pm.groups()
        if net != "/GND":
            continue
        ax, ay = to_abs(fp, float(dx), float(dy))
        both = ("*.Cu" in layers) or ("F.Cu" in layers and "B.Cu" in layers)
        row = ("%s.%s" % (fp["name"].split(":")[-1].split('"')[0], name), kind, round(ax, 2), round(ay, 2), layers.strip())
        if kind == "thru_hole" or both:
            gnd_th.append(row)
        elif "F.Cu" in layers:
            gnd_f.append(row)
        elif "B.Cu" in layers:
            gnd_b.append(row)

print("GND TH pads: %d" % len(gnd_th))
for r in sorted(gnd_th, key=lambda r: r[2]):
    print("   ", r)
print("GND SMD F-only: %d   B-only: %d" % (len(gnd_f), len(gnd_b)))

vias = re.findall(r'\(via\s*\(at ([\d.\-]+) ([\d.\-]+)\)\s*\(size ([\d.]+)\)\s*\(drill ([\d.]+)\)\s*\(layers "F.Cu" "B.Cu"\)\s*\(net "([^"]*)"\)', txt)
print("vias total:", len(vias))
for x, y, size, drill, net in sorted(vias, key=lambda v: (float(v[0]), float(v[1]))):
    print("   via (%6s,%6s) net=%s size=%s drill=%s" % (x, y, net, size, drill))
