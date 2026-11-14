import asf_search as asf, collections
from shapely.geometry import shape, Point
wk = "POLYGON((-114.9 31.3, -109.0 31.3, -109.0 35.0, -114.9 35.0, -114.9 31.3))"
pts = {"Tucson": (-110.93, 32.22), "Marana": (-111.22, 32.44), "Avra Valley": (-111.35, 32.35), "Sahuarita": (-110.96, 31.96), "Sierra Vista": (-110.30, 31.55),
       "Safford": (-109.71, 32.83), "Douglas": (-109.55, 31.34), "Yuma": (-114.62, 32.69), "Wellton": (-114.14, 32.67), "Gila Bend": (-112.72, 32.95),
       "Eloy": (-111.555, 32.745), "Phoenix": (-112.07, 33.45), "Willcox": (-109.83, 32.25), "Kingman": (-114.05, 35.19)}
res = asf.search(dataset=asf.DATASET.OPERA_S1, processingLevel="DISP-S1", intersectsWith=wk, maxResults=6000)
g = collections.defaultdict(list)
for r in res: g[(r.properties["pathNumber"], r.properties["frameNumber"], r.properties["flightDirection"][0])].append(r)
print(len(res), "granules,", len(g), "frames")
for k, rs in sorted(g.items(), key=lambda kv: str(kv[0])):
    poly = shape(rs[0].geometry); hit = [n for n, (lo, la) in pts.items() if poly.contains(Point(lo, la))]
    ds = sorted(r.properties["startTime"][:7] for r in rs)
    if hit: print(k, len(rs), "granules", ds[0], "..", ds[-1], "->", hit)
