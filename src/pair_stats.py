import sys, json, numpy as np
from gunw import read_window, ref_median
path = sys.argv[1]
# Hotspot windows (from AGENTS.md) and a UNVERIFIED hand-picked reference point (mountain bedrock) per hotspot.
H = {"eloy": ((-111.9, 32.6, -111.4, 33.0), (-111.3, 32.75)),   # Picacho/Silver Bell area east edge: placeholder reference, unverified
     "willcox": ((-110.1, 31.9, -109.6, 32.4), (-109.98, 31.95))}  # Dragoon Mountains (unverified coordinates)
out = {}
for name, (box, refpt) in H.items():
    for iono in (False, True):
        w = read_window(path, box, subtract_iono=iono)
        if w is None: print(name, "outside grid"); continue
        v = w["valid"]; d = w["disp_mm"]
        r, nref = ref_median(w, refpt)
        dd = d - r if np.isfinite(r) else d
        print(f"{name:8s} iono_subtracted={iono!s:5s} valid {v.mean()*100:5.1f}% ({v.sum()} px) | raw mean {np.nanmean(d):8.1f} mm std {np.nanstd(d):6.1f} | "
              f"ref pixels {nref} median {r:7.1f} | after ref: mean {np.nanmean(dd):6.1f} std {np.nanstd(dd):5.1f} mm")
    out[name] = dict(pair=f"{w['ref_date']}..{w['sec_date']}", days=w["temporal_days"], track=f"{w['track']}{w['direction'][0]}")
print(out)
