import asf_search as asf, re, collections
w = "POLYGON((-110.1 31.9, -109.6 31.9, -109.6 32.4, -110.1 32.4, -110.1 31.9))"
res = [r for r in asf.search(dataset=asf.DATASET.OPERA_S1, processingLevel="DISP-S1", intersectsWith=w, maxResults=2000) if r.properties["frameNumber"] == 34478]
rows = []
for r in res:
    m = re.search(r"F(\d+)_VV_(\d{8})T\d+Z_(\d{8})T\d+Z", r.properties["fileName"]); rows.append((m.group(2), m.group(3)))
rows.sort(); refs = collections.Counter(a for a, b in rows)
print(len(rows), "granules; distinct reference dates:", len(refs))
for a, n in sorted(refs.items()): print(" ref", a, "->", n, "secondary dates", min(b for x, b in rows if x == a), "..", max(b for x, b in rows if x == a))
