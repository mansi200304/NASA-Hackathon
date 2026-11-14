import json, sys, datetime as dt, numpy as np
from scipy.stats import theilslopes
j = json.load(open(sys.argv[1])); d = j["dates"]; y = np.array(j["displacement_mm"])
t = np.array([(dt.date.fromisoformat(s) - dt.date.fromisoformat(d[0])).days for s in d]) / 365.25
def ols(t, y):
    A = np.c_[t, np.ones_like(t)]; c, *_ = np.linalg.lstsq(A, y, rcond=None); r = y - A @ c
    se = np.sqrt((r**2).sum() / (len(t)-2) / ((t-t.mean())**2).sum()); return c[0]/10, se/10
print("OLS all dates          : %.2f +/- %.2f cm/yr" % ols(t, y))
s, i, lo, hi = theilslopes(y, t); print("Theil-Sen (robust)     : %.2f cm/yr (95%% CI %.2f..%.2f)" % (s/10, lo/10, hi/10))
k = np.array([x != "2026-09-15" for x in d]); print("OLS without Sep-15     : %.2f +/- %.2f cm/yr" % ols(t[k], y[k]))
k = np.array([x < "2026-09-01" for x in d]); print("OLS through Aug-22     : %.2f +/- %.2f cm/yr" % ols(t[k], y[k]))
dy = np.diff(y); print("pair-to-pair jumps (mm): std %.1f, max |jump| %.1f on %s" % (dy.std(), abs(dy).max(), d[1+int(abs(dy).argmax())]))
# does noise look like per-date errors? corr of consecutive jumps (strongly negative => single-date outliers)
print("lag-1 correlation of consecutive pair displacements: %.2f (about -0.5 means independent errors on each acquisition date)" % np.corrcoef(dy[:-1], dy[1:])[0, 1])
