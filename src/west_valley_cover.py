import asf_search as asf, collections
from shapely.geometry import shape, Point
box = "POLYGON((-112.9 33.2, -112.0 33.2, -112.0 33.8, -112.9 33.8, -112.9 33.2))"
pts = {"Buckeye": (-112.58, 33.37), "Goodyear": (-112.36, 33.43), "Litchfield Pk": (-112.36, 33.49), "Glendale": (-112.19, 33.54),
       "Peoria": (-112.24, 33.58), "Surprise": (-112.37, 33.63), "Sun City": (-112.27, 33.60), "Tonopah(west)": (-112.94, 33.48)}
for level in ("GUNW", "RSLC"):
    res = asf.search(dataset=asf.DATASET.NISAR, processingLevel=level, intersectsWith=box, maxResults=1000)
    g = collections.defaultdict(list)
    for r in res:
        p = r.properties; g[(p["pathNumber"], p["flightDirection"][0], p["frameNumber"])].append(r)
    print(f"\n{level}: {len(res)} granules")
    for k, rs in sorted(g.items(), key=lambda kv: str(kv[0])):
        poly = shape(rs[0].geometry); hit = [n for n, (lo, la) in pts.items() if poly.contains(Point(lo, la))]
        d = sorted({r.properties['startTime'][:10] for r in rs})
        print(f"  track {k}: {len(d)} dates {d[0]}..{d[-1]}; contains {hit}")
