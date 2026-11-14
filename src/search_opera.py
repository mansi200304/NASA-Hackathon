import asf_search as asf, collections
boxes = {"eloy": "POLYGON((-111.9 32.6, -111.4 32.6, -111.4 33.0, -111.9 33.0, -111.9 32.6))",
         "buckeye": "POLYGON((-112.8 33.3, -112.2 33.3, -112.2 33.6, -112.8 33.6, -112.8 33.3))",
         "willcox": "POLYGON((-110.1 31.9, -109.6 31.9, -109.6 32.4, -110.1 32.4, -110.1 31.9))"}
print([d for d in dir(asf.DATASET) if "OPERA" in d or "S1" in d][:12])
for h, w in boxes.items():
    try:
        res = asf.search(dataset=asf.DATASET.OPERA_S1, processingLevel="DISP-S1", intersectsWith=w, maxResults=2000)
    except Exception as e:
        print(h, "search error:", type(e).__name__, str(e)[:200]); continue
    g = collections.defaultdict(list)
    for r in res: g[(r.properties.get("pathNumber"), r.properties.get("frameNumber"), r.properties.get("flightDirection"))].append(r)
    print(f"\n{h}: {len(res)} DISP-S1 granules")
    for k, rs in sorted(g.items(), key=lambda kv: str(kv[0])):
        ds = sorted(r.properties["startTime"][:10] for r in rs)
        print(f"  {k}: {len(rs)} granules {ds[0]}..{ds[-1]}")
    if res: print("  example:", res[0].properties["fileName"], res[0].properties.get("bytes"), list(res[0].properties.keys())[:0])
