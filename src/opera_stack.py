"""Long-term (2016-2026) Sentinel-1 LOS displacement from OPERA DISP-S1 block-final granules for one frame.
Each granule = displacement from its reference date to its date; the last granule of each ~6-month block is chained (blocks are contiguous).
Per block: displacement - solid_earth_tide - ionospheric_delay (product says: subtract to apply), mask = recommended_mask==1,
subtract median over a reference circle, then cumulative sum. Sign (OPERA): positive = toward satellite, so sinking is negative.
Usage: python opera_stack.py --name eloy --frame 7091 --box -111.9 32.6 -111.4 33.0 --ref -111.40 32.64 --points "Eloy-Picacho:-111.45,32.70" ..."""
import argparse, glob, json, os, re, sys, datetime as dt, numpy as np, h5py
from pyproj import Transformer
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--name", required=True); ap.add_argument("--frame", type=int, required=True)
ap.add_argument("--box", nargs=4, type=float, required=True); ap.add_argument("--ref", nargs=2, type=float, required=True)
ap.add_argument("--ref-km", type=float, default=3.0); ap.add_argument("--points", nargs="*", default=[]); ap.add_argument("--tag", default="")
a = ap.parse_args()
files = {}
for p in glob.glob(f"{ROOT}/data/raw/opera/OPERA_L3_DISP-S1_IW_F{a.frame:05d}_*.nc"):
    m = re.search(r"VV_(\d{8})T\d+Z_(\d{8})T\d+Z", p); files[(m.group(1), m.group(2))] = p
blocks = {}
for (ref, sec), p in files.items():
    if ref not in blocks or sec > blocks[ref][0]: blocks[ref] = (sec, p)
order = sorted(blocks)
for r0, r1 in zip(order, order[1:]):
    if blocks[r0][0] != r1: sys.exit(f"chain broken between block {r0} (ends {blocks[r0][0]}) and next ref {r1}")
print(f"frame {a.frame}: {len(order)} contiguous blocks, {order[0]} -> {blocks[order[-1]][0]}")
tr = Transformer.from_crs(4326, 32612, always_xy=True)
w, s, e, n = a.box; allx = [w, e, a.ref[0]] + [float(q.split(':')[1].split(',')[0]) for q in a.points]; ally = [s, n, a.ref[1]] + [float(q.split(':')[1].split(',')[1]) for q in a.points]
m_ = 0.06; X0, Y0 = tr.transform(min(allx) - m_, min(ally) - m_); X1, Y1 = tr.transform(max(allx) + m_, max(ally) + m_)
D = []; dates = [dt.date.fromisoformat(f"{order[0][:4]}-{order[0][4:6]}-{order[0][6:]}")]
for r0 in order:
    sec, p = blocks[r0]
    with h5py.File(p, "r") as f:
        x = f["x"][:]; y = f["y"][:]
        xi = np.where((x >= X0) & (x <= X1))[0]; yi = np.where((y >= min(Y0, Y1)) & (y <= max(Y0, Y1)))[0]
        sl = (slice(yi[0], yi[-1] + 1), slice(xi[0], xi[-1] + 1))
        d = f["displacement"][sl] - f["corrections/solid_earth_tide"][sl] - f["corrections/ionospheric_delay"][sl]
        good = f["recommended_mask"][sl] == 1
    d = np.where(good & np.isfinite(d), d, np.nan).astype("float32") * 1000.0   # mm
    xs, ys = x[xi], y[yi]; XX, YY = np.meshgrid(xs, ys)
    cx, cy = tr.transform(*a.ref); rm = (np.hypot(XX - cx, YY - cy) <= a.ref_km * 1000) & np.isfinite(d)
    if rm.sum() < 50: sys.exit(f"reference circle has {rm.sum()} valid pixels in block {r0}; pick another reference")
    D.append(d - np.nanmedian(d[rm])); dates.append(dt.date.fromisoformat(f"{sec[:4]}-{sec[4:6]}-{sec[6:]}"))
D = np.stack(D); cum = np.concatenate([np.zeros((1,) + D.shape[1:], "float32"), np.nancumsum(D, 0)])
t = np.array([(d_ - dates[0]).days for d_ in dates]) / 365.25
valid_all = np.all(np.isfinite(D), 0); print(f"window {D.shape[1]}x{D.shape[2]} px; valid in all {len(order)} blocks: {valid_all.sum()} px ({valid_all.mean()*100:.1f}%)")
def fit(tt, yy):
    A = np.c_[tt, np.ones_like(tt)]; c, *_ = np.linalg.lstsq(A, yy, rcond=None); r = yy - A @ c
    se = np.sqrt((r ** 2).sum() / max(len(tt) - 2, 1) / ((tt - tt.mean()) ** 2).sum()); return c[0] / 10.0, se / 10.0, r.std()
out = dict(name=a.name, frame=a.frame, source="OPERA DISP-S1 (Sentinel-1)", units="mm", sign="positive = toward satellite (OPERA); sinking is negative",
           dates=[d_.isoformat() for d_ in dates], reference=dict(lonlat=a.ref, radius_km=a.ref_km, note="hand-picked, unverified"), points={}, notes=[
           "solid earth tide and ionosphere subtracted; troposphere NOT corrected", "block-final granules only (~6 month steps)"])
for q in a.points:
    nm, ll = q.split(":"); lon, lat = map(float, ll.split(",")); cx, cy = tr.transform(lon, lat)
    mk = (np.hypot(XX - cx, YY - cy) <= 1500) & valid_all
    if mk.sum() < 20: print(f"{nm}: only {mk.sum()} valid pixels within 1.5 km, skipped"); continue
    ser = np.nanmean(cum[:, mk], axis=1); r_all = fit(t, ser); r_rec = fit(t[t > t[-1] - 3.0], ser[t > t[-1] - 3.0])
    print(f"{nm:14s} px={mk.sum():4d} | all-years rate {r_all[0]:6.2f} +/- {r_all[1]:.2f} cm/yr (resid {r_all[2]:.1f} mm) | last 3 yr {r_rec[0]:6.2f} +/- {r_rec[1]:.2f}")
    out["points"][nm] = dict(lonlat=[lon, lat], n_pixels=int(mk.sum()), displacement_mm=np.round(ser, 2).tolist(), rate_cm_yr=round(float(r_all[0]), 3), rate_sigma_cm_yr=round(float(r_all[1]), 3),
                             rate_last3y_cm_yr=round(float(r_rec[0]), 3), rate_last3y_sigma=round(float(r_rec[1]), 3))
tc = t - t.mean(); rate = np.full(valid_all.shape, np.nan, "float32"); cp = cum[:, valid_all]
rate[valid_all] = (tc[:, None] * (cp - cp.mean(0))).sum(0) / (tc ** 2).sum() / 10.0
rv = rate[valid_all]; print(f"per-pixel LOS rate (cm/yr), {rv.size} px: median {np.median(rv):.2f}, 5th pct {np.percentile(rv,5):.2f}, 1st pct {np.percentile(rv,1):.2f}, 95th pct {np.percentile(rv,95):.2f}")
json.dump(out, open(f"{ROOT}/data/processed/opera_{a.name}{a.tag}.json", "w"), indent=1)
os.makedirs(f"{ROOT}/data/processed/cache", exist_ok=True); np.savez_compressed(f"{ROOT}/data/processed/cache/opera_rate_{a.name}{a.tag}.npz", rate=rate, x=xs, y=ys)
