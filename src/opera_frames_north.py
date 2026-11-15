import asf_search as asf, collections
from shapely.geometry import shape, Point
wk = "POLYGON((-114.9 33.6, -109.0 33.6, -109.0 36.0, -114.9 36.0, -114.9 33.6))"
pts = {"Prescott": (-112.47, 34.54), "Chino Valley": (-112.45, 34.75), "Flagstaff": (-111.65, 35.20), "Kingman": (-114.05, 35.19), "Bullhead City": (-114.57, 35.13),
       "Lake Havasu": (-114.32, 34.48), "Parker": (-114.29, 34.15), "Payson": (-111.33, 34.23), "Show Low": (-110.03, 34.25), "Wickenburg": (-112.73, 33.97),
       "Cottonwood": (-112.01, 34.73), "Winslow": (-110.70, 35.02), "Holbrook": (-110.16, 34.90), "Page": (-111.46, 36.91)}
res = asf.search(dataset=asf.DATASET.OPERA_S1, processingLevel="DISP-S1", intersectsWith=wk, maxResults=4000)
g = collections.defaultdict(list)
for r in res: g[(r.properties["pathNumber"], r.properties["frameNumber"], r.properties["flightDirection"][0])].append(r)
print(len(res), "granules (cap 4000),", len(g), "frames")
for k, rs in sorted(g.items(), key=lambda kv: str(kv[0])):
    poly = shape(rs[0].geometry); hit = [n for n, (lo, la) in pts.items() if poly.contains(Point(lo, la))]
    ds = sorted(r.properties["startTime"][:7] for r in rs)
    if hit: print(k, len(rs), ds[0], "..", ds[-1], "->", hit)
