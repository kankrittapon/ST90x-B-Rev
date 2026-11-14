import json

j = json.load(open(r'D:\Tracker\ST909B-4G\Datasheet\pdf_vec\C2916234_p26_drawings.json', encoding='utf-8'))
print('total', len(j))
for i, it in enumerate(j):
    f = it.get('fill') or []
    c = it.get('color') or []
    def fmt(v):
        return ','.join('%0.2f' % t for t in v) if v else '-'
    print('%3d %s fill[%s] col[%s] x %8.2f..%8.2f (w%7.2f) y %8.2f..%8.2f (h%7.2f)' % (
        i, it['type'], fmt(f), fmt(c), it['x0'], it['x1'], it['w'], it['y0'], it['y1'], it['h']))
