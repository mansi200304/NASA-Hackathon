# Status log

Newest first. The earlier log is at the end of AGENTS.md (section 14 and the dated entries after it); new entries go here to avoid merge conflicts with other edits to AGENTS.md and README.md.

## Nov 14 2026, late night: website review and plain-language insights

- Ran the real front end (unchanged) against our data in a simulated page and listed exactly what a visitor sees. Found: two "not supplied" values (sign convention, data release), two permanently empty layers (Data centers, Habitat), and several things we built but never displayed.
- Fixed: `sign_convention` and `data_release` now exported for every study and region layer (NISAR's sign convention is stated as unverified).
- Removed the Data centers and Habitat layers from the UI: no sourced data exists and the data-center story belonged to the dropped Buckeye area. Dialog text updated to match.
- Added to the layer panel: Sentinel-1 region map and cross-check, NISAR Willcox/Eloy (provisional, hidden by default), probable-mine markers, "checked, no sinking found" markers.
- Added "In plain terms" to every study panel: summary, two confidence ratings (fixed rules, `src/insights.py`), six short headed paragraphs, about US grade 7. Eloy rates medium (where) and low (speed) because its independent-satellite match is weak; Willcox, Fort Grant Road and Elfrida rate high/high; Bowie-San Simon medium/medium (one look direction).
- "How we measured" rewritten in plain language and now describes both satellites; Limits gained mines, blue patches and gaps; Sources gained ADWR GIS and OpenStreetMap.
- Renamed again: the site is now **SlowSink** with the tagline “Arizona’s groundwater is draining. Its ground is sinking.” (page title, header, dialog heading, README, AGENTS.md, search description). The first tagline named NISAR; it was changed because every number on the site comes from Sentinel-1 and NISAR's record is still too short to give a reliable rate.
- Project renamed **The Slow Sink** with the tagline "Arizona is sinking." (Mansi's title and tagline, re-applied onto Rhythm's UI: page title, header, dialog heading, README headings). Mansi's other UI changes on the `web` branch were not adopted; Rhythm's UI is the one we ship.
- Prototype map (`web/map-v0`) removed; export intermediates now live in the gitignored `data/processed/cache/web/`.

## Nov 14 2026, night: ADWR validation built

- ADWR's own published InSAR data downloaded and compared with ours: official subsidence polygons (May 2026), a Sentinel-1 deformation raster (2017 to 2026, same satellite) and a RADARSAT-2 raster (2010 to 2026, independent sensor). Full results and caveats: `docs/adwr_validation.md`.
- ADWR does not document the raster units. Inferred as metres from a regression against our data (slope 0.0093, correlation 0.98).
- Southeast: our medians within 0.01 to 0.11 cm/yr of ADWR's Sentinel-1 and correlation 0.98 to 0.99; against independent RADARSAT-2 correlation 0.94 to 0.98 (medians 0.07 to 0.45 cm/yr apart).
- Eloy (Picacho): weak. Pixel correlation 0.59 (Sentinel-1) and 0.18 (RADARSAT-2). NOT validated; the signal (1 to 2 cm/yr) is near the noise.
- All five study areas' sinking pixels fall 100% inside one matching official ADWR feature (Picacho; Kansas Settlement and Fort Grant Rd; Fort Grant Rd; Elfrida; Bowie-San Simon). Area names now use ADWR's names; the earlier "Elfrida?" guess is confirmed.
- Measured reference offset: ADWR's Sentinel-1 is 0.2 to 0.4 cm/yr more negative than ours over areas with little motion (reference choice). Now part of the published uncertainty: willcox -2.73 +/- 0.38, north -4.89 +/- 0.57, south -3.12 +/- 0.49, east -2.58 +/- 0.57, eloy -1.33 +/- 0.36 cm/yr.
- ADWR's Sentinel-1 raster has no data within 3 km of the four excluded mine points; no ADWR feature there.
- New contract fields in `timeseries_<slug>.json`: `adwr_rate_cm_yr`, `adwr_rs2_rate_cm_yr`, `adwr_feature`, `adwr_comparison`, `adwr_note`. New layer file `adwr_subsidence.geojson` (the existing ADWR layer picks it up).
- Not validated at all: NISAR (too new for ADWR products).
