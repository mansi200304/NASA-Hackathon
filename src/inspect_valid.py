"""Stage 1b: explain the valid-pixel mismatch and read attributes (units, sign, ionosphere)."""
import sys, h5py, numpy as np
f = h5py.File(sys.argv[1], "r")
G = "science/LSAR/GUNW/grids/frequencyA/"
u = f[G + "unwrappedInterferogram/HH"]
for k in ["unwrappedPhase", "coherenceMagnitude", "connectedComponents", "ionospherePhaseScreen", "ionospherePhaseScreenUncertainty"]:
    print(k, {a: (v.decode() if isinstance(v, bytes) else v) for a, v in u[k].attrs.items() if a not in ("DIMENSION_LIST","_Netcdf4Dimid")})
mk = f[G + "unwrappedInterferogram/mask"]
print("mask attrs", {a: (v.decode() if isinstance(v, bytes) else v) for a, v in mk.attrs.items()})
ph = u["unwrappedPhase"][:]; coh = u["coherenceMagnitude"][:]; cc = u["connectedComponents"][:]
m = mk[:]; ion = u["ionospherePhaseScreen"][:]
fin = np.isfinite(ph); nz = ph != 0
N = ph.size
print(f"total {N}; finite {fin.mean()*100:.2f}%; finite&!=0 {(fin&nz).mean()*100:.2f}%; NaN {(~fin).mean()*100:.2f}%; exact zero {(fin&~nz).mean()*100:.2f}%")
print(f"cc>0 {(cc>0).mean()*100:.2f}%; cc>0 & finite {((cc>0)&fin).mean()*100:.2f}%; cc==0 & finite {((cc==0)&fin).mean()*100:.2f}%; cc>0 & NaN {((cc>0)&~fin).mean()*100:.2f}%")
print("mask values:", dict(zip(*[x.tolist() for x in np.unique(m, return_counts=True)])))
print(f"coh==0: {(coh==0).mean()*100:.2f}%; coh NaN {np.isnan(coh).mean()*100:.2f}%")
print(f"ion finite {np.isfinite(ion).mean()*100:.2f}%, ion nonzero {(np.isfinite(ion)&(ion!=0)).mean()*100:.2f}%")
v = fin & (cc > 0)
for t in (0.3, 0.5, 0.7):
    print(f"valid(cc>0&finite) & coh>={t}: {(v&(coh>=t)).mean()*100:.1f}% of all pixels, {(v&(coh>=t)).sum()/v.sum()*100:.1f}% of valid")
print(f"ion screen over valid (rad): mean {np.nanmean(ion[v]):.2f} std {np.nanstd(ion[v]):.2f} -> {np.nanstd(ion[v])*19.25:.0f} mm std")
