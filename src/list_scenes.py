import asf_search as asf, collections, json, sys
wkt = {"eloy": "POLYGON((-111.9 32.6, -111.4 32.6, -111.4 33.0, -111.9 33.0, -111.9 32.6))",
       "willcox": "POLYGON((-110.1 31.9, -109.6 31.9, -109.6 32.4, -110.1 32.4, -110.1 31.9))"}
want = {("eloy", 77, 18), ("eloy", 56, 72), ("eloy", 128, 72), ("willcox", 128, 72)}
out = {}
for h, w in wkt.items():
    for r in asf.search(dataset=asf.DATASET.NISAR, processingLevel="GUNW", intersectsWith=w, maxResults=300):
        p = r.properties
        k = (h, p["pathNumber"], p["frameNumber"])
        if k in want:
            out.setdefault(f"{k[0]}_{k[1]}_{k[2]}", []).append((p["startTime"][:10], None, p["fileID"], p.get("processingLevel"), p.get("pgeVersion")))
for k, v in out.items():
    v.sort(key=lambda t: t[0])
    tot = sum((b if isinstance(b,(int,float)) else 0) for _, b, *_ in v) / 1e9
    print(f"{k}: {len(v)} scenes, {tot:.1f} GB")
    print("   ", [d for d, *_ in v])
json.dump(out, open(r"d:/PROJECTS/NASA Hackathon/data/processed/scene_list.json", "w"), indent=1)
