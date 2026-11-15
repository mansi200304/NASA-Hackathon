# UI data contract

For whoever builds the front end (`web/`). All data is produced by our pipeline (`src/export_contract.py`) into `data/processed/`. The UI only reads files; it never computes rates.
The files below already pass the validators in `web/model.mjs` on the `ui/sonoran-sand` branch (checked with node), apart from the one change in section 1.

## 1. Required UI changes (small)

1. **Study areas changed.** Buckeye was dropped (no sinking above about 0.5 cm/yr found there) and the southeast areas were added. The slugs are now:
   `eloy`, `willcox`, `north_willcox`, `south`, `east`.
   In `web/app.js`: update `SLUGS` (line 5) and the check that requires exactly three features (around line 346). Read the slug list from `hotspots.geojson` instead of hard-coding it. "Study 01" numbering should follow the file order.
2. `hotspots.geojson` features carry `slug`, `name`, `tagline`, `county`, `story`, `confirmation`, `land_use_note`, `source_note`. Polygons are the **study boxes**, not the sinking areas.

## 2. Files in `data/processed/`

| File | Content |
|---|---|
| `hotspots.geojson` | one Polygon feature per study area (properties above) |
| `timeseries_<slug>.json` | contract fields: `hotspot`, `units` ("cm"), `reference`, `dates`, `displacement`, `rate_cm_yr`, `rate_sigma`, `adwr_rate_cm_yr` (null). Extra fields: `track`, `median_rate_cm_yr`, `p5_rate_cm_yr`, `fastest_rate_cm_yr`, `area_km2`, `ascending_check`, `confirmation`, `stable_ground_displacement`, `nisar` (object or null), `caveats` (list of strings), `source` |
| `rate_<slug>.png` + `.json` | Sentinel-1 rate over the study box, EPSG:4326, `bounds` [[s,w],[n,e]], `units` "cm/yr", `vmin` -6, `vmax` 2, `dates` [first, last] |
| `rate_sentinel1_descending.png/.json` | region-wide Sentinel-1 rate mosaic (southern and central Arizona), same fields |
| `rate_sentinel1_ascending.png/.json` | ascending-track cross-check, one frame, same fields |
| `rate_nisar_willcox.png/.json`, `rate_nisar_eloy.png/.json` | NISAR rate relative to the box median. PRELIMINARY, see section 4 |
| `mines_excluded.geojson` | Points where the signal is probably mining, not groundwater (`name`, `reason`, `source`) |
| `checked_flat.geojson` | Points we checked and found no sinking (`name`, `median_rate_cm_yr`, `p5_rate_cm_yr`) |

Now provided: `adwr_subsidence.geojson` (the 32 official ADWR subsidence-area polygons, May 2026; the existing ADWR layer picks it up) and `adwr_rate_cm_yr` in each time series (ADWR's own Sentinel-1 deformation raster averaged over our sinking pixels). Also in each series: `adwr_rs2_rate_cm_yr` (ADWR RADARSAT-2, independent sensor), `adwr_feature`, `adwr_comparison`, `adwr_note`. Still not provided, so keep the "Pending" state: `datacenters.geojson`, `habitat.geojson`.

## 3. Sign and units

- Everything is **line of sight** (LOS), in cm or cm/yr. **Negative = ground moving away from the satellite = sinking.** Positive = rising (usually wet or swelling soil, not real uplift).
- `rate_cm_yr` is a straight-line fit to the average of the sinking pixels. `median_rate_cm_yr` is the median of the sinking pixels and is the better headline number. Sinking pixels are those faster than `sinking_threshold_cm_yr` (-1).
- `rate_sigma` is the uncertainty the UI shows next to `rate_cm_yr`. It combines the straight-line fit error with half the difference between the descending and ascending satellite medians (`rate_sigma_fit_only` and `rate_sigma_systematic` give the two parts; `rate_sigma_note` explains it). For `east`, which has no ascending check, the systematic part is a conservative proxy. Do not replace it with the fit-only value: that is about 0.1 cm/yr and overstates precision.
- `displacement` is cumulative since the first date, about 6-month steps, 2016 to 2026.
- Do not present these as vertical subsidence. Say "line of sight" where numbers appear.

## 4. NISAR: how to show it honestly

- NISAR started in late 2025. Willcox has about 1 year of data and Eloy has under 4 months. Both are Provisional, with gaps.
- In `timeseries_<slug>.json`, `nisar` is an object for `eloy` and `willcox` and null elsewhere. It always has `"reliable": false`. Show its numbers with that label and the `scope` text, and do not present its rate as a result.
- The NISAR raster layers must be **off by default**. Drawn raw they paint the whole box red; the files are already relative to the box median. Badge: "Provisional, short record".
- Layer order: NISAR above Sentinel-1.

## 5. Display rules the data depends on

- `confirmation` is one of: "both look directions", "single look direction", "weak in second direction". Show it as a visible chip. "single look direction" must look unconfirmed.
- Show `caveats` in every panel (collapsed is fine, but present).
- Show `stable_ground_displacement` as a second line in the chart when present: it shows the measurement noise.
- Do not invent numbers. `null` means unknown. The ADWR comparison reads "not yet compared".
- Mines and out-of-state areas are marked; do not label them as groundwater subsidence.
- Study-area names use ADWR's official feature names (verified: every area's sinking pixels lie inside the matching ADWR feature).

## 6. Regenerating

`python src/export_contract.py` rewrites every file above from the processed cubes. Do not edit these files by hand.

## 7. Fields the app does not show yet (recommended before submission)

The current app validates all files but only shows `rate_cm_yr`, `rate_sigma`, `reference`, `track`, the chart and `confirmation` (map tooltip). These carry the honesty of the story and are worth adding:

- `caveats` (list of strings): show in every study panel.
- `nisar` (object or null, always `"reliable": false`): show with its `status_note`, or leave out. Do not show its rate as a result.
- `median_rate_cm_yr`, `p5_rate_cm_yr`, `area_km2`: a better headline than the straight-line fit.
- `ascending_check`: the second-direction number.
- `stable_ground_displacement`: second chart line, to show measurement noise.
- `land_use_note` (in `hotspots.geojson`): what is nearby, with its source.
- Layers: `rate_sentinel1_descending`, `rate_sentinel1_ascending` (cross-check), `rate_nisar_*` (off by default), `mines_excluded.geojson`, `checked_flat.geojson`.

## 8. ADWR comparison: how to word it

- `adwr_rate_cm_yr` comes from the same satellite (Sentinel-1) as our rate, processed separately by ADWR. It is a **consistency check, not independent validation**. `adwr_rs2_rate_cm_yr` is an independent sensor over a longer period (2010 to 2026).
- ADWR does not document its raster units. We inferred metres from a regression against our own data (see `docs/adwr_validation.md`); say "inferred" wherever units matter.
- Eloy (Picacho) agrees only weakly: do not claim it is validated. See the table in `docs/adwr_validation.md`.
