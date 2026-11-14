"""Download NISAR GUNW granules for one track/frame over a hotspot. Token comes from .env (EARTHDATA_TOKEN); it is never printed.
Usage: python download.py --hotspot willcox --track 128 --frame 72 [--dry-run] [--max N]"""
import argparse, os, sys, pathlib
import asf_search as asf
ROOT = pathlib.Path(__file__).resolve().parent.parent
WKT = {"eloy": "POLYGON((-111.9 32.6, -111.4 32.6, -111.4 33.0, -111.9 33.0, -111.9 32.6))",
       "buckeye": "POLYGON((-112.8 33.3, -112.2 33.3, -112.2 33.6, -112.8 33.6, -112.8 33.3))",
       "willcox": "POLYGON((-110.1 31.9, -109.6 31.9, -109.6 32.4, -110.1 32.4, -110.1 31.9))"}
ap = argparse.ArgumentParser()
ap.add_argument("--hotspot", required=True, choices=WKT); ap.add_argument("--track", type=int, required=True)
ap.add_argument("--frame", type=int, required=True); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--max", type=int)
a = ap.parse_args()
res = [r for r in asf.search(dataset=asf.DATASET.NISAR, processingLevel="GUNW", intersectsWith=WKT[a.hotspot], maxResults=500)
       if r.properties["pathNumber"] == a.track and r.properties["frameNumber"] == a.frame]
res.sort(key=lambda r: r.properties["startTime"])
import re
best = {}   # one granule per pair: prefer production CRID (P...) over early/uncalibrated (X...)
for r in res:
    name = r.properties["fileName"]; key = re.sub(r"_[PX]\d{5}_", "_", name)
    if key not in best or (re.search(r"_P\d{5}_", name) and re.search(r"_X\d{5}_", best[key].properties["fileName"])):
        best[key] = r
res = sorted(best.values(), key=lambda r: r.properties["startTime"])
raw = ROOT / "data" / "raw"; raw.mkdir(parents=True, exist_ok=True)
import h5py
def ok(path):
    if not path.exists(): return False
    try:
        with h5py.File(path, "r") as f: f["science/LSAR/GUNW/grids/frequencyA/unwrappedInterferogram/HH/unwrappedPhase"]
        return True
    except Exception:
        print("removing incomplete file", path.name[:60]); path.unlink(); return False
todo = [r for r in res if not ok(raw / r.properties["fileName"])]
if a.max: todo = todo[:a.max]
print(f"{len(res)} granules for track {a.track} frame {a.frame}; {len(todo)} not yet on disk; ~{len(todo)*2.4:.0f} GB")
free = __import__("shutil").disk_usage(raw).free / 1e9; print(f"free disk {free:.0f} GB")
if a.dry_run: [print(" ", r.properties["startTime"][:10], r.properties["fileName"]) for r in todo]; sys.exit()
if free < len(todo) * 2.4 + 20: sys.exit("not enough free disk")
tok = None
env = ROOT / ".env"
if env.exists():
    for line in env.read_text().splitlines():
        if line.startswith("EARTHDATA_TOKEN="): tok = line.split("=", 1)[1].strip().strip('"')
if not tok: sys.exit("EARTHDATA_TOKEN not found in .env")
session = asf.ASFSession().auth_with_token(tok)
for i, r in enumerate(todo, 1):
    print(f"[{i}/{len(todo)}] {r.properties['startTime'][:10]}", flush=True)
    for attempt in range(4):
        try: r.download(path=str(raw), session=session); break
        except Exception as e:
            print("  retry", attempt + 1, type(e).__name__, flush=True)
            f = raw / r.properties["fileName"]
            if f.exists(): f.unlink()
    else: print("  FAILED", r.properties["fileName"][:60], flush=True)
print("done")
