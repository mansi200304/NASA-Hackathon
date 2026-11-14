import numpy as np, json, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pyproj import Transformer
from scipy import ndimage
z = np.load("../data/processed/cache/scan_central.npz"); rate, xs, ys = z["rate"], z["x"], z["y"]
tr = Transformer.from_crs(4326, 32612, always_xy=True); back = Transformer.from_crs(32612, 4326, always_xy=True)
places = {"Eloy": (-111.555, 32.745), "Casa Grande": (-111.757, 32.879), "Coolidge": (-111.52, 32.98), "Florence": (-111.39, 33.03), "Maricopa": (-112.05, 33.06),
          "Buckeye": (-112.58, 33.37), "Goodyear": (-112.36, 33.43), "Surprise": (-112.37, 33.63), "Sun City": (-112.27, 33.60), "Glendale": (-112.19, 33.54),
          "Phoenix": (-112.07, 33.45), "Mesa": (-111.83, 33.42), "Queen Creek": (-111.63, 33.25), "Gila Bend": (-112.72, 32.95), "Tonopah": (-112.94, 33.48)}
print("rate within 3 km of place (cm/yr; median / 5th pct / valid 300 m px) -- negative = sinking (LOS)")
for n, (lo, la) in places.items():
    cx, cy = tr.transform(lo, la); X, Y = np.meshgrid(xs, ys); m = (np.hypot(X - cx, Y - cy) <= 3000) & np.isfinite(rate)
    print(f"  {n:12s} {np.median(rate[m]):5.2f} / {np.percentile(rate[m],5):5.2f} / {m.sum():3d}px" if m.sum() > 5 else f"  {n:12s} no valid pixels")
# lower threshold list
for thr in (-0.6,):
    lab, n = ndimage.label(np.nan_to_num(rate) <= thr, structure=np.ones((3, 3))); px = 0.09; out = []
    for i in range(1, n + 1):
        m = lab == i; ar = m.sum() * px
        if ar < 4: continue
        yy, xx = np.where(m); lo, la = back.transform(xs[xx].mean(), ys[yy].mean()); out.append((ar, la, lo, np.median(rate[m]), np.percentile(rate[m], 5)))
    out.sort(reverse=True); print(f"\nclusters <= {thr} cm/yr and >= 4 km2: {len(out)}")
    for ar, la, lo, md, p5 in out[:20]: print(f"  ({la:.3f}, {lo:.3f}) {ar:6.1f} km2 median {md:5.2f} p5 {p5:5.2f}")
fig, ax = plt.subplots(figsize=(11, 8)); lo0, la0 = back.transform(xs[0], ys[-1]); lo1, la1 = back.transform(xs[-1], ys[0])
im = ax.imshow(rate, extent=[xs[0], xs[-1], ys[-1], ys[0]], cmap="RdBu", vmin=-2, vmax=2); plt.colorbar(im, label="LOS rate cm/yr (blue = away from satellite = sinking?)")
for n, (lo, la) in places.items():
    cx, cy = tr.transform(lo, la); ax.plot(cx, cy, "k.", ms=4); ax.text(cx + 1500, cy + 1500, n, fontsize=7)
ax.set_title("Sentinel-1 (OPERA) 2016-2026 LOS rate, frame 7091; ref = frame median; UTM 12N (m)"); fig.tight_layout(); fig.savefig("../docs/central_az_sentinel1_rate_map.png", dpi=120)
