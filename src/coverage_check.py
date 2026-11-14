"""Coverage + correction checks on one GUNW (valid pixels per hotspot box; is unwrappedPhase already iono-corrected?)."""
import sys, h5py, numpy as np
from pyproj import Transformer
f = h5py.File(sys.argv[1], "r")
G = "science/LSAR/GUNW/grids/frequencyA/unwrappedInterferogram/HH"
g = f[G]; x = g["xCoordinates"][:]; y = g["yCoordinates"][:]
ph = g["unwrappedPhase"][:]; cc = g["connectedComponents"][:]; coh = g["coherenceMagnitude"][:]; ion = g["ionospherePhaseScreen"][:]
valid = np.isfinite(ph) & (cc > 0) & (cc != 65535)
to_utm = Transformer.from_crs(4326, 32612, always_xy=True)
boxes = {"eloy": (-111.9, 32.6, -111.4, 33.0), "buckeye": (-112.8, 33.3, -112.2, 33.6), "willcox": (-110.1, 31.9, -109.6, 32.4)}
for n, (w, s, e, nn) in boxes.items():
    x0, y0 = to_utm.transform(w, s); x1, y1 = to_utm.transform(e, nn)
    # use all four corners' extents
    xs = [to_utm.transform(a, b)[0] for a in (w, e) for b in (s, nn)]; ys = [to_utm.transform(a, b)[1] for a in (w, e) for b in (s, nn)]
    xi = np.where((x >= min(xs)) & (x <= max(xs)))[0]; yi = np.where((y >= min(ys)) & (y <= max(ys)))[0]
    if len(xi) == 0 or len(yi) == 0:
        print(f"{n}: outside grid extent entirely"); continue
    sub = valid[np.ix_(yi, xi)]; c = coh[np.ix_(yi, xi)]
    print(f"{n}: grid cells in box {sub.size}, valid {sub.mean()*100:.1f}%, mean coh(valid) {np.nanmean(c[sub]) if sub.any() else float('nan'):.3f}")
# is the unwrapped phase already iono-corrected? correlate with iono screen over valid pixels, after removing means
a = ph[valid]; b = ion[valid]
print("corr(unwrappedPhase, ionosphereScreen) over valid:", np.corrcoef(a, b)[0, 1].round(3))
print("std phase", a.std().round(2), "std iono", b.std().round(2), "std(phase+iono)", (a+b).std().round(2), "std(phase-iono)", (a-b).std().round(2))
# zero-phase pixels: where are they?
z = np.isfinite(ph) & (ph == 0) & (cc > 0)
print("exact-zero pixels:", z.sum(), "; mean coh there", np.nanmean(coh[z]).round(3), "vs valid-nonzero", np.nanmean(coh[valid & (ph != 0)]).round(3))
rows = np.where(z.any(1))[0]; cols = np.where(z.any(0))[0]
print("zero pixels span rows", rows.min(), rows.max(), "cols", cols.min(), cols.max())
