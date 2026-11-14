import asf_search as asf, collections
from shapely.geometry import shape, box
from shapely.ops import unary_union
areas = {"Buckeye/Goodyear box": box(-112.8, 33.3, -112.2, 33.6),
         "ADWR West Valley area (Sun City/Surprise/Peoria/Glendale, approx box, unverified)": box(-112.45, 33.50, -112.15, 33.68)}
res = asf.search(dataset=asf.DATASET.NISAR, processingLevel="GUNW", intersectsWith="POLYGON((-112.9 33.2, -112.0 33.2, -112.0 33.8, -112.9 33.8, -112.9 33.2))", maxResults=1000)
g = collections.defaultdict(list)
for r in res:
    p = r.properties; g[(p["pathNumber"], p["flightDirection"][0], p["frameNumber"])].append(r)
for an, a in areas.items():
    print(f"\n{an}")
    for k, rs in sorted(g.items(), key=lambda kv: str(kv[0])):
        poly = shape(rs[0].geometry); f = poly.intersection(a).area / a.area
        n = len({r.properties['startTime'][:10] for r in rs})
        print(f"  track {k}: footprint covers {f*100:.0f}% | {n} GUNW dates")
