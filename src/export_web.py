"""Export everything the web map needs into web/data/ from the processed cubes (scan_*.npz) and NISAR stacks.
All Sentinel-1 numbers (map raster, hotspot stats, chart series) come from the SAME cube, so map and panel agree.
Usage: python export_web.py"""
import json, os, glob, datetime as dt, numpy as np
from pyproj import Transformer
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = f"{ROOT}/data/processed/cache"; OUT = f"{ROOT}/web/data"; os.makedirs(OUT, exist_ok=True)
THR = -1.0                      # cm/yr: "sinking" threshold used for all hotspot masks
RES = 0.0025                    # degrees per web-raster pixel (~250 m)
AZ = (-114.85, 31.30, -109.00, 37.00)   # lon/lat window for the web raster

def load(name):
    p = f"{CACHE}/scan_{name}.npz"
    if not os.path.exists(p): return None
    z = np.load(p)   # plain arrays only (dates are fixed-width strings), no pickle needed
    if "cum" not in z.files: return None          # old cache without the cube
    return dict(rate=z["rate"], x=z["x"], y=z["y"], cum=z["cum"], t=z["t"], dates=[str(d) for d in z["dates"]], ok=z["ok"], epsg=int(z["epsg"]) if "epsg" in z.files else 32612)

def lonlat_grid(fr):
    X, Y = np.meshgrid(fr["x"], fr["y"]); lo, la = Transformer.from_crs(fr["epsg"], 4326, always_xy=True).transform(X, Y); return lo, la

def sample(fr, lon, lat):
    """nearest-pixel rate of frame `fr` at lon/lat arrays (NaN outside)."""
    X, Y = Transformer.from_crs(4326, fr["epsg"], always_xy=True).transform(lon, lat)
    dx = fr["x"][1] - fr["x"][0]; dy = fr["y"][0] - fr["y"][1]
    ix = np.round((X - fr["x"][0]) / dx).astype(int); iy = np.round((fr["y"][0] - Y) / dy).astype(int)
    inside = (ix >= 0) & (ix < len(fr["x"])) & (iy >= 0) & (iy < len(fr["y"]))
    out = np.full(lon.shape, np.nan, "float32"); out[inside] = fr["rate"][iy[inside], ix[inside]]; return out

def ramp(rate):
    """cm/yr -> RGBA. Sinking (negative) red, stable transparent, rising light blue."""
    stops = [(-6, (103, 0, 13, 235)), (-3, (203, 24, 29, 225)), (-1.5, (252, 146, 114, 205)), (-0.6, (254, 224, 210, 110)), (0, (255, 255, 255, 0)), (1.0, (158, 202, 225, 90)), (2.0, (66, 146, 198, 170))]
    xs = [s[0] for s in stops]; rgba = np.zeros(rate.shape + (4,), "uint8"); r = np.clip(np.nan_to_num(rate, nan=0), xs[0], xs[-1])
    for c in range(4): rgba[..., c] = np.interp(r, xs, [s[1][c] for s in stops]).astype("uint8")
    rgba[~np.isfinite(rate), 3] = 0; return rgba

def mosaic(names, fname, bounds=AZ):
    """first frame in `names` that has data wins at each pixel."""
    w, s, e, n = bounds; lons = np.arange(w, e, RES) + RES / 2; lats = np.arange(n, s, -RES) - RES / 2
    LO, LA = np.meshgrid(lons, lats); rate = np.full(LO.shape, np.nan, "float32"); used = []
    for nm in names:
        fr = load(nm)
        if fr is None: continue
        v = sample(fr, LO, LA); fill = np.isnan(rate) & np.isfinite(v)
        if fill.any(): used.append(nm)
        rate[fill] = v[fill]
    rows = np.where(np.isfinite(rate).any(1))[0]; cols = np.where(np.isfinite(rate).any(0))[0]
    if len(rows) == 0: return None
    r0, r1, c0, c1 = rows[0], rows[-1] + 1, cols[0], cols[-1] + 1; rate = rate[r0:r1, c0:c1]
    Image.fromarray(ramp(rate), "RGBA").save(f"{OUT}/{fname}.png", optimize=True)
    b = dict(bounds=[[float(lats[r1 - 1] - RES / 2), float(lons[c0] - RES / 2)], [float(lats[r0] + RES / 2), float(lons[c1 - 1] + RES / 2)]], frames=used)
    json.dump(b, open(f"{OUT}/{fname}.json", "w")); return b

def ols(t, y):
    A = np.c_[t, np.ones_like(t)]; c, *_ = np.linalg.lstsq(A, y, rcond=None); r = y - A @ c
    se = np.sqrt((r ** 2).sum() / max(len(t) - 2, 1) / ((t - t.mean()) ** 2).sum()); return float(c[0] / 10), float(se / 10)   # cm/yr

HOTSPOTS = [
    dict(id="eloy", name="Eloy – Picacho", D="central", A="f5125", bbox=(-111.70, 32.55, -111.40, 32.82), nisar="eloy",
         place="Pinal County", land="Farmland all around (60 OpenStreetMap polygons within 3 km of the core); no mines nearby.",
         story="A long-known farm-pumping subsidence area. The sinking belt is real but modest in this record."),
    dict(id="willcox", name="Willcox basin", D="southeast", A="f5125", bbox=(-110.10, 31.90, -109.60, 32.34), nisar="willcox",
         place="Cochise County (Sulphur Springs Valley)", land="Farmland all around (24 OpenStreetMap polygons within 3 km); no mines nearby.",
         story="The largest sinking area we found, in a valley with heavy irrigation pumping and the Willcox Playa crane habitat."),
    dict(id="north_willcox", name="North of Willcox", D="southeast", A="f5125", bbox=(-110.15, 32.36, -109.85, 32.60), nisar=None,
         place="Graham County", land="Not checked (map-service lookup failed).",
         story="A fast-sinking patch north of the Willcox basin, seen by three different satellite tracks."),
    dict(id="south", name="South of Willcox (Elfrida / McNeal area?)", D="southeast", A="f5125", bbox=(-109.85, 31.55, -109.55, 31.90), nisar=None,
         place="Cochise County", land="Farmland all around (19 OpenStreetMap polygons within 3 km); no mines nearby. The place name is a guess.",
         story="A second sinking area in the same valley system, confirmed from two look directions."),
    dict(id="east", name="East of Willcox", D="southeast", A=None, bbox=(-109.55, 32.10, -109.05, 32.45), nisar=None,
         place="Cochise County", land="Little farmland nearby (0 to 2 polygons); the cause is unclear.",
         story="Large sinking area seen from one look direction only, so it is shown as unconfirmed."),
]

def hotspot_stats(h, cache):
    D = cache[h["D"]]; lo, la = lonlat_grid(D); w, s, e, n = h["bbox"]
    inbox = (lo >= w) & (lo <= e) & (la >= s) & (la <= n) & D["ok"]
    mask = inbox & (D["rate"] <= THR); stable = inbox & (np.abs(D["rate"]) <= 0.15)
    px_km2 = 0.3 * 0.3
    if mask.sum() < 5: return None
    ser = np.nanmean(D["cum"][:, mask], axis=1); r, se = ols(D["t"], ser)
    out = dict(n_px=int(mask.sum()), area_km2=round(float(mask.sum() * px_km2), 1), median_rate=round(float(np.median(D["rate"][mask])), 2),
               p5_rate=round(float(np.percentile(D["rate"][mask], 5)), 2), fastest=round(float(D["rate"][mask].min()), 2),
               series_rate=round(r, 2), series_sigma=round(se, 2), dates=[f"{d[:4]}-{d[4:6]}-{d[6:]}" for d in D["dates"]], series_mm=np.round(ser, 1).tolist(),
               stable_series_mm=np.round(np.nanmean(D["cum"][:, stable], axis=1), 1).tolist() if stable.sum() > 20 else None,
               stable_px=int(stable.sum()), centroid=[round(float(la[mask].mean()), 4), round(float(lo[mask].mean()), 4)],
               bounds=[[round(float(la[mask].min()), 4), round(float(lo[mask].min()), 4)], [round(float(la[mask].max()), 4), round(float(lo[mask].max()), 4)]],
               track=h["D"], period=[f"{D['dates'][0][:4]}-{D['dates'][0][4:6]}-{D['dates'][0][6:]}", f"{D['dates'][-1][:4]}-{D['dates'][-1][4:6]}-{D['dates'][-1][6:]}"])
    A = cache.get(h["A"]) if h["A"] else None
    if A is not None:
        v = sample(A, lo[mask], la[mask]); v = v[np.isfinite(v)]
        if v.size >= 20: out["ascending"] = dict(n_px=int(v.size), median_rate=round(float(np.median(v)), 2), p5_rate=round(float(np.percentile(v, 5)), 2))
    return out

def nisar_block(key):
    if key is None: return None
    p = {"eloy": "stack_eloy_77A.json", "willcox": "stack_willcox_128D.json"}[key]; j = json.load(open(f"{ROOT}/data/processed/{p}"))
    return dict(track=j["track"], dates=j["dates"], series_mm=j["displacement_mm"], rate_cm_yr=j["rate_cm_yr"], rate_sigma=j["rate_sigma_cm_yr"], n_px=j["n_pixels"],
                scope="Average over the whole study box (not only the sinking area), from consecutive pairs; very noisy.")

def nisar_raster(key, box, file_glob, fname, ref, ref_km):
    """NISAR per-pixel rate (stack.py cache) -> 400 m blocks -> lat/lon PNG."""
    import sys; sys.path.insert(0, f"{ROOT}/src"); from gunw import read_window
    rp = f"{CACHE}/rate_{key}.npy"
    if not os.path.exists(rp): return None
    w = read_window(sorted(glob.glob(file_glob))[0], box, coh_min=0.4); rate = np.load(rp)
    if rate.shape != w["disp_mm"].shape: return None
    F = 5; ny, nx = (rate.shape[0] // F) * F, (rate.shape[1] // F) * F; c = rate[:ny, :nx].reshape(ny // F, F, nx // F, F)
    cnt = np.isfinite(c).sum((1, 3)); dec = np.where(cnt >= 10, np.nanmean(c, (1, 3)), np.nan).astype("float32")
    dec = dec - np.float32(np.nanmedian(dec))   # show rate RELATIVE to the box median: removes the common drift that a short noisy record picks up
    xs = w["x"][:nx].reshape(-1, F).mean(1); ys = w["y"][:ny].reshape(-1, F).mean(1)
    fr = dict(rate=dec, x=xs, y=ys, epsg=w["epsg"]); W, S, E, N = box; lons = np.arange(W, E, RES) + RES / 2; lats = np.arange(N, S, -RES) - RES / 2
    LO, LA = np.meshgrid(lons, lats); v = sample(fr, LO, LA)
    Image.fromarray(ramp(v), "RGBA").save(f"{OUT}/{fname}.png", optimize=True)
    json.dump(dict(bounds=[[S, W], [N, E]], valid_pct=round(float(np.isfinite(v).mean() * 100), 1)), open(f"{OUT}/{fname}.json", "w")); return True

if __name__ == "__main__":
    names = ["central", "southeast", "f34477", "f7092", "f5125", "f7090", "f26691", "f46289", "f34476"]
    cache = {n: load(n) for n in names}; cache = {k: v for k, v in cache.items() if v is not None}; print("cubes available:", sorted(cache))
    # Sentinel-1 mosaics: descending frames (priority order) and the ascending cross-check
    desc = [n for n in ["southeast", "f34477", "central", "f7092", "f7090", "f26691", "f46289", "f34476"] if n in cache]
    print("descending mosaic:", mosaic(desc, "s1_rate_desc"))
    print("ascending mosaic:", mosaic([n for n in ["f5125"] if n in cache], "s1_rate_asc"))
    hs = []
    for h in HOTSPOTS:
        st = hotspot_stats(h, cache) if h["D"] in cache else None
        if st is None: print("skip", h["id"]); continue
        hs.append(dict(id=h["id"], name=h["name"], place=h["place"], land=h["land"], story=h["story"], bbox=h["bbox"], s1=st, nisar=nisar_block(h["nisar"]),
                       confirmed=("both look directions" if st.get("ascending") and st["ascending"]["median_rate"] <= THR else ("single look direction" if not st.get("ascending") else "weak in second direction")),
                       adwr=None))
        print(f"{h['id']:14s} {st['area_km2']:7.1f} km2 | median {st['median_rate']:5.2f} p5 {st['p5_rate']:5.2f} | series {st['series_rate']:5.2f}+/-{st['series_sigma']:.2f} | asc {st.get('ascending')}")
    json.dump(hs, open(f"{OUT}/hotspots.json", "w"), indent=1)
    print("NISAR Willcox raster:", nisar_raster("willcox_128D", (-110.1, 31.9, -109.6, 32.4), f"{ROOT}/data/raw/NISAR_L2_*_128_D_072_*.h5", "nisar_willcox", (-109.98, 31.95), 5.0))
    print("NISAR Eloy raster:", nisar_raster("eloy_77A", (-111.9, 32.6, -111.4, 33.0), f"{ROOT}/data/raw/NISAR_L2_*_077_A_018_*.h5", "nisar_eloy", (-111.42, 32.65), 3.0))
    # excluded / checked-flat markers
    excl = [dict(name="Sierrita Mine area", lat=31.861, lon=-111.130, why="Open-pit copper mine (OpenStreetMap). Ground motion here is mining, not groundwater."),
            dict(name="Mission Complex area", lat=31.983, lon=-111.058, why="Copper mine complex (OpenStreetMap). Mining, not groundwater."),
            dict(name="Ray Mine area", lat=33.148, lon=-110.968, why="Open-pit copper mine (OpenStreetMap). Mining, not groundwater."),
            dict(name="Morenci area", lat=33.127, lon=-109.346, why="Placed at the mining town of Morenci; mine features not retrieved. Likely mining, not groundwater.")]
    json.dump(excl, open(f"{OUT}/excluded.json", "w"), indent=1)
    flat = []; places = {"Buckeye": (-112.58, 33.37), "Goodyear": (-112.36, 33.43), "Surprise": (-112.37, 33.63), "Sun City": (-112.27, 33.60), "Glendale": (-112.19, 33.54),
                         "Phoenix": (-112.07, 33.45), "Mesa": (-111.83, 33.42), "Casa Grande": (-111.757, 32.879)}
    if "central" in cache:
        C = cache["central"]; lo, la = lonlat_grid(C); cx, cy = Transformer.from_crs(4326, C["epsg"], always_xy=True).transform(*zip(*places.values()))
        X, Y = np.meshgrid(C["x"], C["y"])
        for (n, (lon, lat)), px, py in zip(places.items(), cx, cy):
            m = (np.hypot(X - px, Y - py) <= 3000) & np.isfinite(C["rate"])
            if m.sum() > 5: flat.append(dict(name=n, lat=lat, lon=lon, median_rate=round(float(np.median(C["rate"][m])), 2), p5_rate=round(float(np.percentile(C["rate"][m], 5)), 2)))
    json.dump(flat, open(f"{OUT}/flat.json", "w"), indent=1); print("flat markers:", len(flat))
