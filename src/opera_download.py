"""Download the block-final OPERA DISP-S1 granule of each reference block (one per ~6 months) for one frame.
Usage: python opera_download.py --frame 7091 [--dry-run]   Token from .env, never printed."""
import argparse, re, sys, pathlib, shutil
import asf_search as asf
ROOT = pathlib.Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser(); ap.add_argument("--frame", type=int, required=True); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--near", nargs=2, type=float, help="lon lat of a point inside the frame"); a = ap.parse_args()
WK = "POLYGON((-112.9 31.8, -109.5 31.8, -109.5 33.8, -112.9 33.8, -112.9 31.8))"
if a.near: WK = f"POINT({a.near[0]} {a.near[1]})"
res = [r for r in asf.search(dataset=asf.DATASET.OPERA_S1, processingLevel="DISP-S1", intersectsWith=WK, maxResults=4000) if r.properties["frameNumber"] == a.frame]
best = {}
for r in res:
    m = re.search(r"VV_(\d{8})T\d+Z_(\d{8})T\d+Z_v1.0_(\d{8}T\d+Z)", r.properties["fileName"]); ref, sec, proc = m.groups()
    if (ref, sec) not in best or proc > best[(ref, sec)][0]: best[(ref, sec)] = (proc, r)
last = {}
for (ref, sec), (_, r) in best.items():
    if ref not in last or sec > last[ref][0]: last[ref] = (sec, r)
sel = [last[k][1] for k in sorted(last)]
out = ROOT / "data" / "raw" / "opera"; out.mkdir(parents=True, exist_ok=True)
print(f"frame {a.frame}: {len(res)} granules, {len(last)} reference blocks -> {len(sel)} block-final files (~{len(sel)*0.38:.1f} GB); disk free {shutil.disk_usage(out).free/1e9:.0f} GB")
for k in sorted(last): print("  ref", k, "-> final secondary", last[k][0])
if a.dry_run: sys.exit()
tok = [l.split("=", 1)[1].strip().strip('"') for l in (ROOT / ".env").read_text().splitlines() if l.startswith("EARTHDATA_TOKEN=")][0]
session = asf.ASFSession().auth_with_token(tok)
import h5py
for i, r in enumerate(sel, 1):
    f = out / r.properties["fileName"]
    if f.exists():
        try:
            with h5py.File(f, "r"): continue
        except Exception: f.unlink()
    for attempt in range(4):
        try: r.download(path=str(out), session=session); print(f"[{i}/{len(sel)}] ok", flush=True); break
        except Exception as e:
            print("  retry", attempt + 1, type(e).__name__, flush=True)
            if f.exists(): f.unlink()
    else: print("  FAILED", r.properties["fileName"][:70], flush=True)
print("done")
