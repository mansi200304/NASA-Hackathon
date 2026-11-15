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

Not provided yet, so the UI should keep its existing "Pending" state: `adwr_subsidence.geojson`, `datacenters.geojson`, `habitat.geojson`, and `adwr_rate_cm_yr` (all null or absent, never 0).

## 3. Sign and units

- Everything is **line of sight** (LOS), in cm or cm/yr. **Negative = ground moving away from the satellite = sinking.** Positive = rising (usually wet or swelling soil, not real uplift).
- `rate_cm_yr` is a straight-line fit to the average of the sinking pixels. `median_rate_cm_yr` is the median of the sinking pixels and is the better headline number. Sinking pixels are those faster than `sinking_threshold_cm_yr` (-1).
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
- The `name` of `south` contains "Elfrida / McNeal area?" on purpose, because the place name is a guess; keep the question mark.

## 6. Regenerating

`python src/export_contract.py` rewrites every file above from the processed cubes. Do not edit these files by hand.
