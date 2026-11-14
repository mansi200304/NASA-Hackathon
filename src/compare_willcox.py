"""Cross-check at Willcox playa over the overlap period: Sentinel-1 (OPERA) vs NISAR, same-direction descending tracks (S1 129 D, NISAR 128 D)."""
import asf_search as asf, re, glob, os, sys, datetime as dt, numpy as np, h5py, pathlib
from pyproj import Transformer
from gunw import read_window, ref_median
ROOT = pathlib.Path(__file__).resolve().parent.parent
WK = "POLYGON((-110.1 31.9, -109.6 31.9, -109.6 32.4, -110.1 32.4, -110.1 31.9))"
PLAYA, REF = (-109.84, 32.10), (-109.98, 31.95)
res = [r for r in asf.search(dataset=asf.DATASET.OPERA_S1, processingLevel="DISP-S1", intersectsWith=WK, maxResults=2000) if r.properties["frameNumber"] == 34478]
cand = {}
for r in res:
    m = re.search(r"VV_(\d{8})T\d+Z_(\d{8})T\d+Z_v1.0_(\d{8}T\d+Z)", r.properties["fileName"]); ref, sec, proc = m.groups()
    if ref == "20251004" and (sec not in cand or proc > cand[sec][0]): cand[sec] = (proc, r)
print("S1 secondaries in block ref 2025-10-04:", sorted(cand))
d = lambda s: dt.date(int(s[:4]), int(s[4:6]), int(s[6:]))
pick = lambda target: min(cand, key=lambda s: abs((d(s) - target).days))
s_a, s_b = pick(dt.date(2025, 10, 26)), pick(dt.date(2026, 4, 12)); print("using S1 dates", s_a, s_b)
out = ROOT / "data/raw/opera"; tok = [l.split("=", 1)[1].strip() for l in (ROOT / ".env").read_text().splitlines() if l.startswith("EARTHDATA_TOKEN=")][0]
sess = asf.ASFSession().auth_with_token(tok)
paths = {}
for s in (s_a, s_b):
    r = cand[s][1]; p = out / r.properties["fileName"]
    if not p.exists(): r.download(path=str(out), session=sess)
    paths[s] = p
tr = Transformer.from_crs(4326, 32612, always_xy=True)
def s1_at(p):
    with h5py.File(p, "r") as f:
        x, y = f["x"][:], f["y"][:]; cx, cy = tr.transform(*PLAYA); rx, ry = tr.transform(*REF)
        xi = np.where((x > min(cx, rx) - 6000) & (x < max(cx, rx) + 6000))[0]; yi = np.where((y > min(cy, ry) - 6000) & (y < max(cy, ry) + 6000))[0]
        sl = (slice(yi[0], yi[-1] + 1), slice(xi[0], xi[-1] + 1))
        dd = (f["displacement"][sl] - f["corrections/solid_earth_tide"][sl] - f["corrections/ionospheric_delay"][sl]) * 1000
        dd = np.where((f["recommended_mask"][sl] == 1) & np.isfinite(dd), dd, np.nan)
    XX, YY = np.meshgrid(x[xi], y[yi]); pm = (np.hypot(XX - cx, YY - cy) <= 1500) & np.isfinite(dd); rm = (np.hypot(XX - rx, YY - ry) <= 3000) & np.isfinite(dd)
    return np.nanmean(dd[pm]) - np.nanmedian(dd[rm]), pm.sum()
va, na = s1_at(paths[s_a]); vb, nb = s1_at(paths[s_b])
print(f"S1 displacement vs ref date 2025-10-04 at playa: {s_a}: {va:.1f} mm ({na} px) | {s_b}: {vb:.1f} mm ({nb} px)")
s1_change = vb - va; s1_days = (d(s_b) - d(s_a)).days
# NISAR: chain track 128 D pairs, same reference
files = {}
for p in glob.glob(str(ROOT / "data/raw/NISAR_L2_*_128_D_072_*.h5")):
    k = re.sub(r"_[PX]\d{5}_", "_", os.path.basename(p))
    if k not in files or "_P0" in p: files[k] = p
pairs = []
for k, p in sorted(files.items()):
    w = read_window(p, (-110.1, 31.9, -109.6, 32.4), coh_min=0.4)
    r, _ = ref_median(w, REF, 5.0); X, Y = np.meshgrid(w["x"], w["y"]); cx, cy = Transformer.from_crs(4326, w["epsg"], always_xy=True).transform(*PLAYA)
    pm = np.hypot(X - cx, Y - cy) <= 1500; pairs.append((w["ref_date"], w["sec_date"], (w["disp_mm"] - r), pm))
pairs.sort(); pairs = [q for q in pairs if q[1] <= "2026-04-12"]; pm = pairs[0][3]; allv = np.all([np.isfinite(q[2]) for q in pairs], 0) & pm
print("NISAR pairs used:", len(pairs), "| circle px:", int(pm.sum()), "| valid in all:", int(allv.sum()))
cum = {pairs[0][0]: 0.0}; c = 0.0
for q in pairs: c += np.nanmean(q[2][allv]); cum[q[1]] = c
na_, nb_ = "2025-10-26", "2026-04-12"; n_change = cum[nb_] - cum[na_]; n_days = (d(nb_.replace("-", "")) - d(na_.replace("-", ""))).days
print(f"NISAR cumulative at playa ({allv.sum()} px valid in all pairs): {na_}: {cum[na_]:.1f} mm | {nb_}: {cum[nb_]:.1f} mm")
print(f"CHANGE over overlap: Sentinel-1 {s1_change:.1f} mm in {s1_days} d ({s1_change/s1_days*365.25/10:.2f} cm/yr equiv) | NISAR {n_change:.1f} mm in {n_days} d ({n_change/n_days*365.25/10:.2f} cm/yr equiv)")
