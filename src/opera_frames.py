import asf_search as asf, collections
from shapely.geometry import shape, Point
wk = "POLYGON((-112.9 31.8, -109.5 31.8, -109.5 33.8, -112.9 33.8, -112.9 31.8))"
pts = {"Eloy town": (-111.555, 32.745), "Eloy-Picacho": (-111.45, 32.70), "Casa Grande": (-111.757, 32.879), "Buckeye": (-112.58, 33.37),
       "Goodyear": (-112.36, 33.43), "Sun City": (-112.27, 33.60), "Surprise": (-112.37, 33.63), "Willcox playa": (-109.84, 32.10), "Willcox town": (-109.83, 32.25)}
res = asf.search(dataset=asf.DATASET.OPERA_S1, processingLevel="DISP-S1", intersectsWith=wk, maxResults=4000)
g = collections.defaultdict(list)
for r in res: g[(r.properties["pathNumber"], r.properties["frameNumber"], r.properties["flightDirection"][0])].append(r)
for k, rs in sorted(g.items(), key=lambda kv: str(kv[0])):
    poly = shape(rs[0].geometry); hit = [n for n, (lo, la) in pts.items() if poly.contains(Point(lo, la))]
    if hit: print(k, len(rs), "granules", "->", hit)
