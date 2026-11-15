"""Scan a whole OPERA DISP-S1 frame for sinking clusters (data-driven hotspot search).
Per block: displacement - solid_earth_tide - ionospheric_delay, recommended_mask==1, 10x10 block-mean to 300 m, reference = frame-wide median
(assumes most of the frame is stable; a few mm/yr bias possible). Chain blocks, per-pixel OLS rate over all years, label clusters."""
import argparse, glob, json, re, sys, os, numpy as np, h5py
from pyproj import Transformer
from scipy import ndimage
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser(); ap.add_argument("--frame", type=int, required=True); ap.add_argument("--name", required=True)
ap.add_argument("--min-km2", type=float, default=1.0); ap.add_argument("--min-rate", type=float, default=1.0); a = ap.parse_args()
files = {}
for p in glob.glob(f"{ROOT}/data/raw/opera/OPERA_L3_DISP-S1_IW_F{a.frame:05d}_*.nc"):
    m = re.search(r"VV_(\d{8})T\d+Z_(\d{8})T\d+Z", p); files[(m.group(1), m.group(2))] = p
blocks = {}
for (r, s), p in files.items():
    if r not in blocks or s > blocks[r][0]: blocks[r] = (s, p)
order = sorted(blocks); F = 10; D = []; dates = [order[0]]
for r in order:
    s, p = blocks[r]
    with h5py.File(p, "r") as f:
        x = f["x"][:]; y = f["y"][:]; ny, nx = (len(y) // F) * F, (len(x) // F) * F
        _w = f["spatial_ref"].attrs["crs_wkt"]; _w = _w.decode() if isinstance(_w, bytes) else _w; EPSG = int(re.findall(r'ID\["EPSG",(\d+)\]', _w)[-1])
        d = (f["displacement"][:ny, :nx] - f["corrections/solid_earth_tide"][:ny, :nx] - f["corrections/ionospheric_delay"][:ny, :nx]) * 1000
        d[f["recommended_mask"][:ny, :nx] != 1] = np.nan
    c = d.reshape(ny // F, F, nx // F, F); cnt = np.isfinite(c).sum((1, 3)); dm = np.where(cnt >= 30, np.nanmean(c, (1, 3)), np.nan).astype("float32")
    D.append(dm - np.nanmedian(dm)); dates.append(s); print("block", r, "->", s, "valid", f"{np.isfinite(dm).mean()*100:.0f}%", flush=True)
xs = x[:nx].reshape(-1, F).mean(1); ys = y[:ny].reshape(-1, F).mean(1)
D = np.stack(D); cum = np.concatenate([np.zeros((1,) + D.shape[1:], "float32"), np.nancumsum(D, 0)]); ok = np.all(np.isfinite(D), 0)
import datetime as dt
t = np.array([(dt.date(int(q[:4]), int(q[4:6]), int(q[6:])) - dt.date(int(dates[0][:4]), int(dates[0][4:6]), int(dates[0][6:]))).days for q in dates]) / 365.25
tc = t - t.mean(); rate = np.full(ok.shape, np.nan, "float32"); cp = cum[:, ok]; rate[ok] = (tc[:, None] * (cp - cp.mean(0))).sum(0) / (tc ** 2).sum() / 10
res = np.full(ok.shape, np.nan, "float32"); fit = (tc[:, None] * 0 + 1) * 0
rv = rate[ok]; med = np.median(rv); sig = 1.4826 * np.median(abs(rv - med))
print(f"{ok.sum()} px ({ok.mean()*100:.0f}% of frame at 300 m); rate median {med:.2f}, robust sigma {sig:.2f} cm/yr; 1st pct {np.percentile(rv,1):.2f}, 99th {np.percentile(rv,99):.2f}")
thr = min(-a.min_rate, med - 4 * sig); print("sinking threshold (cm/yr):", round(float(thr), 2))
lab, n = ndimage.label(np.nan_to_num(rate, nan=0) <= thr, structure=np.ones((3, 3)))
print("frame CRS EPSG:", EPSG); tr = Transformer.from_crs(EPSG, 4326, always_xy=True); px_km2 = (F * 30 / 1000) ** 2; rows = []
for i in range(1, n + 1):
    m = lab == i; area = m.sum() * px_km2
    if area < a.min_km2: continue
    yy, xx = np.where(m); lon, lat = tr.transform(xs[xx].mean(), ys[yy].mean()); r = rate[m]
    rows.append(dict(id=i, lon=round(lon, 4), lat=round(lat, 4), area_km2=round(area, 1), median_rate=round(float(np.median(r)), 2), p5_rate=round(float(np.percentile(r, 5)), 2), min_rate=round(float(r.min()), 2),
                     bbox=[round(c, 4) for c in (*tr.transform(xs[xx].min(), ys[yy].max()), *tr.transform(xs[xx].max(), ys[yy].min()))]))
rows.sort(key=lambda q: q["area_km2"] * -q["median_rate"], reverse=True)
json.dump(dict(frame=a.frame, period=[dates[0], dates[-1]], ref="frame-wide median", threshold_cm_yr=float(thr), clusters=rows), open(f"{ROOT}/data/processed/hotspot_candidates_{a.name}.json", "w"), indent=1)
os.makedirs(f"{ROOT}/data/processed/cache", exist_ok=True); np.savez_compressed(f"{ROOT}/data/processed/cache/scan_{a.name}.npz", rate=rate, x=xs, y=ys, cum=cum.astype("float32"), t=t, dates=np.array(dates), ok=ok, epsg=EPSG)
print(f"{len(rows)} clusters >= {a.min_km2} km2")
for q in rows[:30]: print(f"  ({q['lat']:.3f}, {q['lon']:.3f}) area {q['area_km2']:6.1f} km2 | median {q['median_rate']:5.2f} | p5 {q['p5_rate']:5.2f} | fastest {q['min_rate']:5.2f} cm/yr")
