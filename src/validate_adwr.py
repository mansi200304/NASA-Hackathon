"""Validate our Sentinel-1 rates against ADWR's published InSAR products (downloaded to data/raw/adwr/, untrusted input, read-only).
 - ADWR Sentinel-1 deformation 2017-02 to 2026-05 (same satellite, different processing): consistency check.
 - ADWR RADARSAT-2 deformation 2010-05 to 2026-05 (independent sensor, longer period).
 - ADWR 'Arizona Active Land Subsidence Areas' polygons (May 2026): does our sinking area fall inside the official features?
ADWR does not document the raster units, so the unit is INFERRED from the regression slope against our own line-of-sight displacement.
Usage: python validate_adwr.py [--unit-cm-per-value X]   (run once without --unit to print the diagnostic)"""
import argparse, glob, json, os, datetime as dt, numpy as np, rasterio, shapefile
from rasterio.enums import Resampling
from rasterio.features import rasterize
from affine import Affine
from pyproj import Transformer
import export_web as ew

ROOT = ew.ROOT; ADWR = f"{ROOT}/data/raw/adwr"; OUT = f"{ROOT}/data/processed"
ap = argparse.ArgumentParser(); ap.add_argument("--unit-cm-per-value", type=float, default=None); a = ap.parse_args()
S1_YEARS = (dt.date(2026, 5, 8) - dt.date(2017, 2, 24)).days / 365.25      # ADWR Sentinel-1 product: 2017-02 to 2026-05
RS2_YEARS = (dt.date(2026, 5, 8) - dt.date(2010, 5, 15)).days / 365.25      # ADWR RADARSAT-2 product: 2010-05 to 2026-05
F = 15                                                                       # 20 m -> 300 m, matches our 300 m grid

def coarse(tif):
    with rasterio.open(tif) as ds:
        h, w = ds.height, ds.width; oh, ow = -(-h // F), -(-w // F)
        arr = ds.read(1, out_shape=(oh, ow), resampling=Resampling.average, masked=True).astype("float64").filled(np.nan)
        tr = ds.transform * Affine.scale(w / ow, h / oh)
    return arr, tr

def at(arr, tr, X, Y):
    ix = np.floor((X - tr.c) / tr.a).astype(int); iy = np.floor((Y - tr.f) / tr.e).astype(int)
    ok = (ix >= 0) & (ix < arr.shape[1]) & (iy >= 0) & (iy < arr.shape[0]); out = np.full(X.shape, np.nan)
    out[ok] = arr[iy[ok], ix[ok]]; return out

s1_arr, s1_tr = coarse(glob.glob(f"{ADWR}/AZdeformation_2017to2026/*.tif")[0])
rs_arr, rs_tr = coarse(glob.glob(f"{ADWR}/AZDeformation_2010to2026/*.tif")[0])
print("ADWR coarse grids:", s1_arr.shape, rs_arr.shape)
cache = {n: ew.load(n) for n in ["central", "southeast", "f5125"]}
shp = shapefile.Reader(glob.glob(f"{ADWR}/updatedlandsubsidenceshapefile/*.shp")[0])

def masks(h):
    D = cache[h["D"]]; X, Y = np.meshgrid(D["x"], D["y"]); lo, la = ew.lonlat_grid(D); w, s, e, n = h["bbox"]
    inbox = (lo >= w) & (lo <= e) & (la >= s) & (la <= n) & D["ok"]
    return D, X, Y, inbox & (D["rate"] <= ew.THR)

# --- unit diagnostic: slope of ADWR value vs OUR cumulative LOS displacement (cm, over the ADWR period)
xs, ys = [], []
for h in ew.HOTSPOTS:
    if h["D"] not in cache: continue
    D, X, Y, m = masks(h); v = at(s1_arr, s1_tr, X[m], Y[m]); ours_cm = D["rate"][m] * S1_YEARS
    ok = np.isfinite(v); xs.append(ours_cm[ok]); ys.append(v[ok])
xs, ys = np.concatenate(xs), np.concatenate(ys)
slope = np.polyfit(xs, ys, 1)[0]; med_ratio = np.median(ys / xs)
print(f"UNIT DIAGNOSTIC (n={xs.size}): ADWR value = {slope:.4f} x our cumulative LOS cm (OLS); median ratio {med_ratio:.4f}; corr {np.corrcoef(xs, ys)[0,1]:.3f}")
print("  slope ~0.01 means ADWR is in metres (x100 -> cm) ; ~0.033 feet (x30.48) ; ~0.39 inches (x2.54) ; ~1 cm ; ~10 mm.  A vertical-vs-LOS factor of about 1.2 can sit on top of any of these.")
if a.unit_cm_per_value is None:
    raise SystemExit("rerun with --unit-cm-per-value <cm per ADWR value> after reading the diagnostic")
U = a.unit_cm_per_value

# --- per-hotspot comparison
res = {}
for h in ew.HOTSPOTS:
    if h["D"] not in cache: continue
    D, X, Y, m = masks(h)
    ours = D["rate"][m]; adwr_s1 = at(s1_arr, s1_tr, X[m], Y[m]) * U / S1_YEARS; adwr_rs2 = at(rs_arr, rs_tr, X[m], Y[m]) * U / RS2_YEARS
    both = np.isfinite(adwr_s1); both2 = np.isfinite(adwr_rs2)
    r = dict(n_px=int(m.sum()), ours_median=round(float(np.median(ours)), 2))
    if both.sum() >= 20:
        r.update(adwr_s1_median=round(float(np.median(adwr_s1[both])), 2), adwr_s1_n=int(both.sum()), corr_s1=round(float(np.corrcoef(ours[both], adwr_s1[both])[0, 1]), 3),
                 diff_s1=round(float(np.median(ours[both]) - np.median(adwr_s1[both])), 2))
    if both2.sum() >= 20:
        r.update(adwr_rs2_median=round(float(np.median(adwr_rs2[both2])), 2), adwr_rs2_n=int(both2.sum()), corr_rs2=round(float(np.corrcoef(ours[both2], adwr_rs2[both2])[0, 1]), 3))
    res[h["id"]] = r; print(h["id"], r)

# --- extent check against ADWR polygons (rasterised on our 300 m grid)
to_ll = Transformer.from_crs(32612, 4326, always_xy=True); feats = []; names = []
for sr in shp.shapeRecords():
    gj = sr.shape.__geo_interface__; nm = sr.record["Comments"].replace(" Feature", "").strip(); names.append(nm)
    def conv(c):
        return [list(to_ll.transform(*p)) for p in c] if isinstance(c[0][0], float) else [conv(x) for x in c]
    feats.append({"type": "Feature", "geometry": {"type": gj["type"], "coordinates": conv(gj["coordinates"])}, "properties": {"name": nm, "period": sr.record["Comment"], "source": "ADWR Arizona Active Land Subsidence Areas, May 2026"}})
json.dump({"type": "FeatureCollection", "features": feats}, open(f"{OUT}/adwr_subsidence.geojson", "w"))
ext = {}
for fr_name in ["central", "southeast"]:
    D = cache[fr_name]; X, Y = np.meshgrid(D["x"], D["y"]); px = D["x"][1] - D["x"][0]; tr = Affine(px, 0, D["x"][0] - px / 2, 0, -px, D["y"][0] + px / 2)
    uniq = sorted(set(names)); nid = {n: i + 1 for i, n in enumerate(uniq)}
    shapes = [(sr.shape.__geo_interface__, nid[names[i]]) for i, sr in enumerate(shp.shapeRecords())]
    ids = rasterize(shapes, out_shape=D["rate"].shape, transform=tr, fill=0, dtype="int32")
    sink = np.isfinite(D["rate"]) & (D["rate"] <= ew.THR); inside = ids > 0
    ext[fr_name] = dict(our_sinking_px=int(sink.sum()), pct_inside_adwr=round(float((sink & inside).sum() / max(sink.sum(), 1) * 100), 1),
                        adwr_px_with_data=int((inside & np.isfinite(D["rate"])).sum()), pct_of_adwr_area_we_flag=round(float((sink & inside).sum() / max((inside & np.isfinite(D["rate"])).sum(), 1) * 100), 1))
    per = {}
    for nm in uniq:
        mm = ids == nid[nm]
        if mm.sum() >= 5 and (mm & np.isfinite(D["rate"])).sum() >= 5:
            vm = mm & np.isfinite(D["rate"]); r = D["rate"][vm]; a1 = at(s1_arr, s1_tr, X[vm], Y[vm]) * U / S1_YEARS; a2 = at(rs_arr, rs_tr, X[vm], Y[vm]) * U / RS2_YEARS
            per[nm] = dict(px=int(mm.sum()), median_rate=round(float(np.median(r)), 2), pct_sinking=round(float((r <= ew.THR).mean() * 100), 1),
                           adwr_s1_median=round(float(np.nanmedian(a1)), 2) if np.isfinite(a1).any() else None, adwr_rs2_median=round(float(np.nanmedian(a2)), 2) if np.isfinite(a2).any() else None)
    ext[fr_name]["features"] = per; print(fr_name, {k: v for k, v in ext[fr_name].items() if k != "features"})
    for nm, v in sorted(per.items(), key=lambda kv: kv[1]["median_rate"])[:14]: print(f"   {nm:24s} {v}")
# --- which official ADWR feature does each of our hotspots sit in? (share of our sinking pixels per feature)
overlap = {}
for h in ew.HOTSPOTS:
    if h["D"] not in cache: continue
    D, X, Y, m = masks(h); px = D["x"][1] - D["x"][0]; tr = Affine(px, 0, D["x"][0] - px / 2, 0, -px, D["y"][0] + px / 2)
    uniq = sorted(set(names)); nid = {n: i + 1 for i, n in enumerate(uniq)}
    ids = rasterize([(sr.shape.__geo_interface__, nid[names[i]]) for i, sr in enumerate(shp.shapeRecords())], out_shape=D["rate"].shape, transform=tr, fill=0, dtype="int32")
    got = ids[m]; tot = int(m.sum()); row = {"outside_any_feature": round(float((got == 0).sum() / tot * 100), 1)}
    for nm in uniq:
        f = float((got == nid[nm]).sum() / tot * 100)
        if f >= 3: row[nm] = round(f, 1)
    overlap[h["id"]] = row; print("OVERLAP", h["id"], row)
# --- unbiased comparison over EVERY valid pixel of each frame (not only where we already see sinking)
allpx = {}
for fr_name in ["central", "southeast"]:
    D = cache[fr_name]; X, Y = np.meshgrid(D["x"], D["y"]); v = np.isfinite(D["rate"]); a1 = at(s1_arr, s1_tr, X[v], Y[v]) * U / S1_YEARS; a2 = at(rs_arr, rs_tr, X[v], Y[v]) * U / RS2_YEARS
    o = D["rate"][v]; k1 = np.isfinite(a1); k2 = np.isfinite(a2); sink = o <= ew.THR
    allpx[fr_name] = dict(n=int(k1.sum()), corr_s1=round(float(np.corrcoef(o[k1], a1[k1])[0, 1]), 3), rmse_s1_cm_yr=round(float(np.sqrt(np.mean((o[k1] - a1[k1]) ** 2))), 3),
                          median_abs_diff_s1=round(float(np.median(abs(o[k1] - a1[k1]))), 3), corr_rs2=round(float(np.corrcoef(o[k2], a2[k2])[0, 1]), 3),
                          corr_rs2_on_sinking=round(float(np.corrcoef(o[k2 & sink], a2[k2 & sink])[0, 1]), 3) if (k2 & sink).sum() > 20 else None)
    print("ALL PIXELS", fr_name, allpx[fr_name])
mines = {"Sierrita Mine area": (-111.130, 31.861), "Mission Complex area": (-111.058, 31.983), "Ray Mine area": (-110.968, 33.148), "Morenci area": (-109.346, 33.127)}
mine_res = {}
tr_ll = Transformer.from_crs(4326, 32612, always_xy=True)
from shapely.geometry import shape as shp_shape, Point
polys = [(sr.record["Comments"], shp_shape(sr.shape.__geo_interface__)) for sr in shp.shapeRecords()]
for nm, (lo, la) in mines.items():
    x0, y0 = tr_ll.transform(lo, la); X, Y = np.meshgrid(np.arange(x0 - 1500, x0 + 1501, 300.0), np.arange(y0 - 1500, y0 + 1501, 300.0))
    a1 = at(s1_arr, s1_tr, X, Y) * U / S1_YEARS; inside = [c for c, p in polys if p.distance(Point(x0, y0)) < 1500]
    mine_res[nm] = dict(adwr_s1_median_3km=round(float(np.nanmedian(a1)), 2) if np.isfinite(a1).any() else None, adwr_features_within_1p5km=inside)
    print("MINE", nm, mine_res[nm])
json.dump(dict(unit_cm_per_value=U, unit_note="INFERRED from regression against our line-of-sight displacement; ADWR does not document the raster units", s1_years=round(S1_YEARS, 2), rs2_years=round(RS2_YEARS, 2),
               hotspots=res, extent=ext, feature_overlap=overlap, all_pixels=allpx, mines=mine_res, unit_slope=round(float(slope), 4)), open(f"{OUT}/adwr_validation.json", "w"), indent=1)
