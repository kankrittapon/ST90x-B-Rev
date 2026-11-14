import json

j = json.load(open(r'D:\Tracker\ST909B-4G\Datasheet\pdf_vec\C2916234_p26_drawings.json', encoding='utf-8'))

def is_green(it):
    c = it.get('color') or []
    f = it.get('fill') or []
    return (len(c) >= 3 and abs(c[0]) < 0.05 and c[1] > 0.9) or (len(f) >= 3 and abs(f[0]) < 0.05 and f[1] > 0.9)

green = [it for it in j if is_green(it)]
print('green items:', len(green))
for it in sorted(green, key=lambda a: (a['y0'], a['x0'])):
    kind = 'FILL  ' if it['type'] == 'f' else 'stroke'
    print('%s x %8.2f..%8.2f (w%7.2f)  y %8.2f..%8.2f (h%7.2f)' % (
        kind, it['x0'], it['x1'], it['w'], it['y0'], it['y1'], it['h']))
