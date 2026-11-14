"""List NISAR GUNW scenes over each hotspot and test which track/frame footprints contain key points."""
import asf_search as asf, json, collections
from shapely.geometry import shape, Point
boxes = {"eloy": "POLYGON((-111.9 32.6, -111.4 32.6, -111.4 33.0, -111.9 33.0, -111.9 32.6))",
         "buckeye": "POLYGON((-112.8 33.3, -112.2 33.3, -112.2 33.6, -112.8 33.6, -112.8 33.3))",
         "willcox": "POLYGON((-110.1 31.9, -109.6 31.9, -109.6 32.4, -110.1 32.4, -110.1 31.9))"}
pts = {"Eloy town": (-111.555, 32.745), "Eloy-Picacho": (-111.45, 32.70), "Casa Grande": (-111.757, 32.879), "Stanfield": (-112.0, 32.88),
       "Buckeye": (-112.58, 33.37), "Goodyear": (-112.36, 33.43), "Willcox playa": (-109.84, 32.10)}
for name, wkt in boxes.items():
    res = asf.search(dataset=asf.DATASET.NISAR, processingLevel="GUNW", intersectsWith=wkt, maxResults=300)
    groups = collections.defaultdict(list)
    for r in res:
        p = r.properties
        key = (p.get("pathNumber"), p.get("flightDirection"), p.get("frameNumber"))
        groups[key].append(r)
    print(f"\n== {name}: {len(res)} scenes")
    for key, rs in sorted(groups.items(), key=lambda kv: str(kv[0])):
        poly = shape(rs[0].geometry)
        hit = [n for n, (lo, la) in pts.items() if poly.contains(Point(lo, la))]
        dates = sorted(r.properties["startTime"][:10] for r in rs)
        print(f"  track/dir/frame {key}: {len(rs)} scenes {dates[0]}..{dates[-1]}; contains: {hit}")
