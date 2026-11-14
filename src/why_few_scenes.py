"""Compare what NISAR acquired (L1 RSLC) vs what exists as GUNW over the Eloy box, per track."""
import asf_search as asf, collections
eloy = "POLYGON((-111.9 32.6, -111.4 32.6, -111.4 33.0, -111.9 33.0, -111.9 32.6))"
def get(level):
    res = asf.search(dataset=asf.DATASET.NISAR, processingLevel=level, intersectsWith=eloy, maxResults=1000)
    d = collections.defaultdict(set)
    for r in res:
        p = r.properties; d[(p["pathNumber"], p["flightDirection"][0])].add(p["startTime"][:10])
    return res, d
for level in ("RSLC", "GUNW", "GCOV"):
    try:
        res, d = get(level)
    except Exception as e:
        print(level, "error", e); continue
    print(f"\n{level}: {len(res)} granules")
    for k, v in sorted(d.items()):
        v = sorted(v); print(f"  track {k}: {len(v)} dates, {v[0]}..{v[-1]}")
        if level in ("RSLC",): print("     ", v)
