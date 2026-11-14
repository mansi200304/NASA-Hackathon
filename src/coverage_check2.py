import sys, h5py, numpy as np
from pyproj import Transformer
f = h5py.File(sys.argv[1], "r")
g = f["science/LSAR/GUNW/grids/frequencyA/unwrappedInterferogram/HH"]
x = g["xCoordinates"][:]; y = g["yCoordinates"][:]
ph = g["unwrappedPhase"][:]; cc = g["connectedComponents"][:]; coh = g["coherenceMagnitude"][:]; ion = g["ionospherePhaseScreen"][:]
valid = np.isfinite(ph) & (cc > 0) & (cc != 65535) & (ph != 0)
m = valid & np.isfinite(ion)
a, b = ph[m], ion[m]
print("valid&iono-finite:", m.sum(), "corr(phase, iono):", np.corrcoef(a, b)[0,1].round(3))
print("std phase %.2f | iono %.2f | phase+iono %.2f | phase-iono %.2f" % (a.std(), b.std(), (a+b).std(), (a-b).std()))
# detrend each by best plane to see if the ramp is shared
X, Y = np.meshgrid(x, y)
def planefit(v):
    A = np.c_[X[m]/1e5, Y[m]/1e5, np.ones(m.sum())]; c, *_ = np.linalg.lstsq(A, v, rcond=None); return v - A@c
ra, rb = planefit(a), planefit(b)
print("after plane removal: std phase %.2f rad (%.0f mm), std iono %.2f rad, corr %.3f" % (ra.std(), ra.std()*19.25, rb.std(), np.corrcoef(ra, rb)[0,1]))
to_ll = Transformer.from_crs(32612, 4326, always_xy=True)
to_utm = Transformer.from_crs(4326, 32612, always_xy=True)
pts = {"Eloy town": (-111.555, 32.745), "Eloy-Picacho (bowl)": (-111.45, 32.70), "Casa Grande": (-111.757, 32.879), "Stanfield": (-112.0, 32.88), "Willcox playa": (-109.84, 32.10), "Willcox town": (-109.83, 32.25)}
for n, (lo, la) in pts.items():
    px, py = to_utm.transform(lo, la)
    j = np.argmin(abs(x-px)); i = np.argmin(abs(y-py))
    if abs(x[j]-px) > 200 or abs(y[i]-py) > 200: print(f"{n}: outside grid"); continue
    w = valid[max(i-60,0):i+60, max(j-60,0):j+60]       # ~9.6 km window
    print(f"{n}: valid in 9.6 km window {w.mean()*100:.0f}%, coh {np.nanmean(coh[max(i-60,0):i+60, max(j-60,0):j+60][w]) if w.any() else float('nan'):.2f}")
# valid fraction by longitude strips across Eloy latitude band
for lo in np.arange(-111.9, -111.35, 0.1):
    xs0, ys0 = to_utm.transform(lo, 32.6); xs1, ys1 = to_utm.transform(lo+0.1, 33.0)
    xi = np.where((x>=xs0)&(x<=xs1))[0]; yi = np.where((y>=min(ys0,ys1))&(y<=max(ys0,ys1)))[0]
    print(f"  lon {lo:.1f}..{lo+0.1:.1f}: valid {valid[np.ix_(yi,xi)].mean()*100:.0f}%")
