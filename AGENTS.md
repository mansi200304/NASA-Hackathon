# Sinkronized — NASA Space Apps 2026, "Dancing with the SARs" (NISAR)

## Current radar decision — November 14, 2026

The original track-128 Eloy plan is superseded by the coverage findings recorded in section 14. Test a provisional **track 077 ascending / frame 018** file over Eloy first; **track 056 descending / frame 072** is the alternative. Final selection depends on valid pixels, coherence, correction checks and a usable reference area. Track 128 descending / frame 072 remains a **Willcox candidate**, not the Eloy MVP track.

See [the track-selection handoff](docs/track_selection.md) for acquisition-pair counts, connected date ranges, duplicate handling and the next checkpoint. These changes are based on the committed scene list and Reshma's status log; they are not a new inspection of the raw HDF5 file.

Team of three: Reshma Panibhate, Mansi, Ritam. Repo: github.com/mansi200304/NASA-Hackathon. Locked in Nov 14 2026.

---

## 1. One-line pitch
Arizona's aquifers are being pumped faster than they refill, and the ground is sinking.
NISAR's L-band radar can measure it to the millimetre. This project maps where central Arizona is sinking, how fast, and what sits on top of it: farms, new data centers, and wildlife habitat.

## 2. Why it matters (the story)
- Groundwater depletion is invisible. You can't see the aquifer drop, but when it does, the clay layers compact and the land surface sinks. Some of this compaction is permanent: the aquifer loses storage it never gets back.
- Sinking cracks canals, wells, roads and foundations, and opens earth fissures.
- Central Arizona is under pressure from three sides: long-term farm pumping, fast urban growth, and a new wave of water-hungry data centers in the West Valley.
- Wildlife depends on the same groundwater: springs, riparian corridors, and wetlands like Willcox Playa (sandhill crane wintering grounds).
- Satellite radar turns this slow crisis into a measured number, over the whole region, every 12 days.

**Who it's for:** city/county planners, water managers (ADWR, Active Management Areas), conservation groups and wildlife biologists, and the public.

## 3. The end product: what it looks like

### 3.1 Main deliverable: an interactive web map ("Sinkronized")
A single-page web app that opens on a full-screen map of central Arizona.

**Layout**
- **Map (center):** dark/satellite basemap, centered on the Phoenix valley + south box.
- **Layer panel (left):** toggles and opacity sliders for every layer.
- **Info panel (right, slides in):** opens when you click a hotspot or any point on the map.
- **Time slider (bottom):** steps through NISAR acquisition dates; the map shows cumulative sinking up to that date.
- **Header:** title, one-line explainer, links to "How we measured" and "Limits".

**Map layers**
| Layer | What it shows | Source |
|---|---|---|
| Subsidence rate (headline layer) | Sinking speed in cm/year, color ramp from stable (neutral) to fast sinking (deep red); low-coherence pixels hidden | NISAR GUNW stacks (this project) |
| Cumulative displacement | Total sinking since the first NISAR date, driven by the time slider | NISAR GUNW stacks |
| Multi-year background | Longer-term sinking pattern for context | Sentinel-1 (OPERA DISP-S1 or ASF HyP3 InSAR) |
| Coherence / data quality | Where the radar measurement is trustworthy | NISAR GUNW |
| ADWR subsidence features | Official mapped subsidence areas, for comparison | ADWR |
| Active Management Areas | Groundwater management boundaries (incl. Willcox AMA, Dec 2024) | ADWR |
| Farmland | Irrigated cropland | USDA NASS Cropland Data Layer |
| Data centers | Points for existing and planned sites; popup with operator, status, size, water use if published | Compiled from public sources (labelled "compiled") |
| Protected & riparian areas | Protected lands, rivers, riparian corridors, Willcox Playa | PAD-US, NHD, AZ Game & Fish where available |
| Hotspot outlines | The three study boxes | This project |

**Click a hotspot → info panel shows:**
- Name, one-paragraph story of the place.
- **Headline number:** e.g. "Sinking X ± Y cm/year (NISAR, track 128 descending, Oct 2025–Nov 2026)".
- **Time-series chart:** cumulative line-of-sight displacement vs date, one point per NISAR pass, with the stable reference area for comparison.
- **Validation box:** our rate vs ADWR's published rate for the same area, and the difference.
- **What's on top:** acres of farmland, number of data centers, protected/riparian areas inside the sinking zone.
- Data badge: "NISAR Provisional data — preliminary".

**Click any other point → popup:** rate at that pixel, coherence, and land use there.

### 3.2 The three hotspot stories
1. **Eloy / Casa Grande — "The long sink."** Decades of farm pumping; one of the best-documented subsidence areas in the US. This is the **validation site**: if our numbers match ADWR here, the method is trustworthy everywhere else.
2. **Buckeye / Goodyear — "The new pressure."** Where data centers are being built in the West Valley. Fewer published measurements, so this is where NISAR adds something new. Framed carefully: we show what's sinking and what's being built, not who caused it.
3. **Willcox — "The fastest sink, and the cranes."** Fastest subsidence in Arizona, intensive agricultural pumping, and Willcox Playa sandhill crane habitat. Newly an Active Management Area (Dec 2024). The conservation centerpiece.

### 3.3 Supporting pages / sections
- **How we measured:** plain-language radar explainer (radar measures distance to the ground; compare two passes; the phase change = movement; add up many pairs to beat noise), with a diagram.
- **Limits:** the honest-limits list from section 7, written for the public.
- **Sidebar: Sedona / Flagstaff flood (Nov 1 2026):** short context piece on water in Arizona swinging between too little and too much. No NISAR post-storm pass over Sedona, so no measurement claimed.
- **Data & code:** links to the GitHub repo, data sources and citations.

### 3.4 Space Apps submission package
- Project page text (pitch, story, method, limits, team).
- Demo: short video or slide deck walking through the map. Check the current Space Apps rules for exact format and length.
- Public GitHub repo with the processing pipeline and the web app.
- Links to the live map.

## 4. Study areas (WKT, lon/lat)
- Region (Phoenix valley + south): `POLYGON((-112.6 32.5, -111.4 32.5, -111.4 33.8, -112.6 33.8, -112.6 32.5))`
- Eloy / Casa Grande: `POLYGON((-111.9 32.6, -111.4 32.6, -111.4 33.0, -111.9 33.0, -111.9 32.6))`
- Buckeye / Goodyear: `POLYGON((-112.8 33.3, -112.2 33.3, -112.2 33.6, -112.8 33.6, -112.8 33.3))`
  (ADWR's West Valley feature is Sun City/Surprise/Peoria/Glendale, north of this box.)
- Willcox: `POLYGON((-110.1 31.9, -109.6 31.9, -109.6 32.4, -110.1 32.4, -110.1 31.9))`

## 5. Data
- **NISAR GUNW** (L2 geocoded unwrapped interferograms), ASF Vertex / `asf_search`. Archive from about Oct 2025. Newest = Provisional, earliest = Uncalibrated. State this on the map.
- **Sentinel-1** for multi-year history (OPERA DISP-S1 displacement product if it covers the area, otherwise ASF HyP3 InSAR).
- **Validation:** ADWR InSAR land subsidence maps.
- **Overlays:** USDA Cropland Data Layer, PAD-US, NHD, ADWR AMA boundaries, data center list compiled from public sources (with source per point).

## 6. Status (Nov 14 2026)
- Earthdata account working; "Alaska Satellite Facility Data Access" approved.
- Vertex, Eloy box, NISAR GUNW, production: **49 scenes** across **3 tracks**: 128 descending (frame 072), 056 descending (frame 072), 077 ascending (frame 018). **Corrected Nov 14 evening:** scenes per track in the Eloy search are 128 D = 29, 056 D = 8, 077 A = 12 (not ~16 each). Every product is a 12-day pair, but there are gaps in the record.
- Downloaded one test file into this folder (2,378,170,368 bytes, valid HDF5):
  `NISAR_L2_PR_GUNW_032_128_D_072_033_4000_SH_20261009T020749_20261009T020824_20261021T020749_20261021T020824_P05023_N_F_J_001.h5`
  Name: L2 / PR (production) / GUNW / ref cycle 032 / track 128 / D (descending) / frame 072 / secondary cycle 033 / SH (single pol, HH confirmed) / Oct 9 → Oct 21 2026 / CRID P05023 / Provisional.

## 7. Method (pipeline)
1. **Inspect** the HDF5 tree: find unwrapped phase, coherence, connected components, coordinate grids, wavelength, sign convention, reference/secondary times.
2. **Phase → displacement:** `d = -(λ / 4π) · φ` (L-band λ ≈ 0.24 m). Read λ and sign convention from metadata; don't assume.
3. **Mask** low coherence and unreliable connected components.
4. **Reference** to a stable area (bedrock/mountains) set to zero.
5. **Stack:** single short-baseline pairs may be dominated by noise. Deduplicate processing versions and chain only connected acquisition pairs on **one track/frame**, using actual reference/secondary dates (12- and 24-day baselines occur in the current scene list). First inspect 077 A frame 018 over Eloy, with 056 D frame 072 as the alternative; select using valid coverage, coherence and a reference area. Do not bridge the track-077 December 2025–June 2026 gap. Fit a rate with uncertainty over the actual supported interval. Never mix ascending and descending directly.
6. **Validate** at Eloy against ADWR rates.
7. **Repeat** for Buckeye and Willcox (check which tracks cover each).
8. **Regional mosaic** of rates → map tiles.
9. **Overlay analysis:** farmland acres, data centers, protected areas inside sinking zones (spatial joins).
10. **Web app:** export rasters as Cloud-Optimized GeoTIFF or PNG tiles, vectors as GeoJSON; frontend in MapLibre GL JS (or Leaflet) with a charting library for time series; host as a static site (e.g. GitHub Pages).

**Tools:** Python (h5py / xarray, numpy, rasterio, geopandas, matplotlib), `asf_search` with an Earthdata token (tokens expire; regenerate from the profile page), MapLibre GL JS frontend.

**Suggested repo layout**
```
data/raw/        # downloaded .h5 (gitignored)
data/processed/  # stacks, rate maps, GeoJSON
notebooks/       # exploration, one per stage
src/             # download, read_gunw, stack, rate, overlay, export
web/             # the map app
docs/            # method + limits text
```

## 8. Milestones — each ends in a measured number
| # | Stage | Measured number at the end |
|---|---|---|
| 1 | Open the test file | Array shapes, pixel spacing, wavelength, % pixels above coherence threshold |
| 2 | One-pair displacement | Mean/std of 12-day LOS displacement over Eloy vs stable reference (expect ≈ noise) |
| 3 | Selected Eloy-track stack | Cumulative displacement at Eloy over a connected, quality-checked observation interval |
| 4 | Rate + validation | Eloy rate ± uncertainty vs ADWR rate, difference in cm/yr |
| 5 | Other hotspots | Rates for Buckeye and Willcox |
| 6 | Overlays | Acres of farmland, # data centers, km² of habitat inside sinking zones |
| 7 | Web map | Live map with all layers and the three hotspot panels |

## 9. Honest limits (show these in the product)
- About one year of NISAR is short for subsidence; results come from stacks, not single pairs.
- Sinking indicates groundwater stress; it does **not** prove which user (farms, cities, data centers) caused it.
- Radar loses coherence over plowed fields and construction; L-band helps but doesn't fix it.
- Radar measures line-of-sight motion, not purely vertical; we assume mostly vertical motion in subsidence areas and say so.
- Radar cannot see wildlife; habitat links come from outside maps.
- Data is Provisional / Uncalibrated; numbers are preliminary.
- Data center water use is often not published; where unknown, we say so.

## 10. How I want to work (instructions for the AI assistant)
- Teach step by step; explain the "why" before the code. Don't build everything at once.
- Every stage ends in a real measured number, not just a working demo.
- Real processing pipeline; no hardcoded or ground-truth shortcuts.
- Debug from first principles; check environment activation/sourcing before assuming deeper problems.
- My input is often voice-transcribed; ask when something is unclear.

## 11. Immediate next step
The track-128 test-file inspection is already recorded in the README and section 14. Open one provisional track-077 ascending / frame-018 GUNW file over Eloy; 056 descending / frame-072 is the alternative. Inspect its HDF5 groups and metadata, verify actual valid coverage over Eloy/Casa Grande and a suitable reference area, and report crop shape, valid/coherent pixel fractions, acquisition dates, polarisation, CRS, wavelength and correction metadata before bulk downloads. `src/coverage_check2.py` currently hardcodes HH and EPSG:32612: verify/adapt those assumptions for the replacement file. The raw HDF5 on the Windows drive is not accessible through the GitHub connector. See `docs/track_selection.md`.

## 12. HARD TIME LIMIT: 12 hours total (started ~1:40 PM Sat Nov 14 2026, Arizona time; done by ~1:40 AM)
This section overrides the scope above. The guiding rule: **one excellent hotspot plus a working map beats three half-done ones.**

**Must ship (MVP)**
- Eloy: a NISAR stack from a coverage-verified track/frame (test 077 A first; 056 D alternative), then a rate in cm/yr ± uncertainty and comparison against an appropriately matched ADWR reference. Track 128 does not cover the Eloy core in the recorded test. This is the core result.
- A single-page web map (Leaflet or MapLibre, static, no backend) with: a rate raster overlay (PNG + bounds), hotspot outlines, ADWR subsidence features, a small hand-compiled data-center GeoJSON, one protected/riparian layer, and a click-panel with Eloy's time-series chart and headline number.
- A Limits section, a short How-we-measured section, and the submission package.

**Ship if time allows (in this order)**
1. Willcox and Buckeye rates. Willcox is a separate track-128 D / frame-072 candidate; it does not come from the selected Eloy stack. Buckeye may share the Eloy candidate's footprint, but usable pixels and a compatible reference still need checking before claiming a rate.
2. Farmland overlay (USDA Cropland Data Layer).
3. Sedona flood sidebar (one paragraph).

**Cut**
- Sentinel-1 multi-year history (cite ADWR for the long-term history instead).
- Time slider and animation.
- Farmland-vs-desert coherence study.

**Time plan (approximate)**
| Hours | Work |
|---|---|
| 0–1 | Inspect one candidate 077 A / 018 Eloy file (056 D / 072 alternative), valid-pixel rule, ionosphere/sign check and reference coverage. Start only the selected track's downloads after this checkpoint. |
| 1–4 | Stack the selected Eloy track/frame over a connected interval: stable reference, cumulative series, linear rate, ADWR comparison |
| 4–5 | Buckeye usable-pixel check on the selected Eloy track; Willcox separate 128 D stack only if time allows |
| 5–6 | Export: rate PNG/COG, GeoJSON overlays, time-series JSON |
| 6–9 | Web map |
| 9–11 | Write-up, Limits, demo video/slides, repo README, deploy (GitHub Pages) |
| 11–12 | Buffer: fixes and submit |

**Speed rules**
- Disk: D: has ~220 GB free according to the team. Do not use the old ~16-file track-128 estimate for the Eloy download plan. The current scene list has nine connected provisional 077 A pairs or eight 056 D pairs; select one track and check current file sizes. The first test-file download reportedly took ~1 minute.
- Before downloading full files, check whether h5py over HTTPS (fsspec/earthaccess) can read just the Eloy window. If that's not quick to set up, just download the full files.
- Downloads run in the background while other work continues.
- Explain the "why" briefly at each step, but don't stop and wait unless there's a decision, a surprise, or a download/cost gate.
- If a step runs more than ~30 min over its slot, stop and tell Reshma, with a cut option.

## 13. Team and work split (3 people, 12 hours)
The three tracks run **in parallel from hour 0**. They connect only through the file contracts below, so nobody waits on anyone. The frontend starts with mock files in the same format and swaps in the real ones when they land.

| Person | Track | Owns |
|---|---|---|
| **Reshma** | Radar processing | NISAR downloads, valid-pixel rule, ionosphere, Eloy stack, rate ± uncertainty, ADWR validation, Willcox/Buckeye if in frame, export of rate raster + time series |
| **Mansi** | Web map | Static map app (MapLibre or Leaflet), layer panel, hotspot click-panel with time-series chart, How-we-measured + Limits pages, deploy on GitHub Pages |
| **Ritam** | Overlays + story | ADWR subsidence features + AMA boundaries, hand-compiled data-center GeoJSON (with sources), protected/riparian layer, hotspot outline GeoJSON, ADWR validation rates for Eloy/Willcox, write-up, demo video/slides, submission form |

(Swap roles if skills fit differently; keep the contracts.)

**File contracts (all in `data/processed/`, committed to the repo, small files only)**
- `rate_<hotspot>.png` + `rate_<hotspot>.json`: color-mapped rate image; JSON = `{"bounds": [[south, west], [north, east]], "units": "cm/yr", "vmin": .., "vmax": .., "colormap": "..", "track": "<actual track and direction>", "dates": ["YYYY-MM-DD", ".."]}` (lat/lon, EPSG:4326)
- `timeseries_<hotspot>.json`: `{"hotspot": "eloy", "units": "cm", "reference": "<stable area>", "dates": [...], "displacement": [...], "rate_cm_yr": .., "rate_sigma": .., "adwr_rate_cm_yr": .. | null}`
- `hotspots.geojson`: polygons with `name`, `slug`, `story`
- `datacenters.geojson`: points with `name`, `operator`, `status` (operating/planned/under construction), `mw` | null, `water_use` | null, `source_url`
- `adwr_subsidence.geojson`, `ama.geojson`, `habitat.geojson`: as downloaded, simplified to stay < 5 MB each
- Hotspot slugs: `eloy`, `buckeye`, `willcox`

**Repo rules**
- Never commit `.h5` or raw data. `.gitignore`: `data/raw/`, `*.h5`, `*.tif` over 5 MB.
- Each person works on their own branch (`radar`, `web`, `overlays`) and merges into `main` at checkpoints.
- **Sync checkpoints:** hour 4 (Eloy number + mock-free map shell), hour 8 (all real data in the map), hour 11 (freeze, submit).


## 14. Status log (newest first)

### Nov 14: catalogue audit and updated Eloy next step
- Coverage figures below are Reshma's recorded test-file findings, not a second raw-file measurement by this audit.
- `scene_list.json`: track 128 has 29 records but **25 unique acquisition-date pairs**; four extra records are processing-version duplicates. Some baselines are **24 days**, so not every pair is 12 days.
- Track 077 A / 018: **nine connected provisional pairs, June 19–October 17, 2026**. Three older pairs form a separate November 3–December 21, 2025 segment. No listed pair connects those segments.
- Track 056 D / 072: **eight connected pairs, June 30–October 16, 2026**. Its July 24–August 17 pair bridges a 24-day interval.
- Test 077 A over Eloy first; 056 D is the alternative. Neither is selected on footprint alone. Validate per-pixel coverage, reference area, correction conventions and quality before downloading the full stack.
- Keep 128 D for Willcox; do not assume all hotspots share one stack. Use the actual selected track and supported dates in the web exports.
- Detailed provenance and checks: `docs/track_selection.md`.

### Nov 14, ~3:30 PM AZ: first findings (measured on the test file, track 128 D frame 072, Oct 9 to Oct 21 2026)
- **Valid-pixel rule:** valid = finite phase AND connectedComponents > 0 AND phase != 0. The 53.7% vs 49.7% gap was 4.1% of pixels that are in a component but have phase exactly 0.0 (mean coherence 0.53 vs 0.68 elsewhere, scattered across the frame, so unwrapping fill, not real zero motion). Dropped.
- **Ionosphere:** unwrappedPhase still contains the ionosphere. corr(phase, ionospherePhaseScreen) = 0.983; std 7.47 rad falls to 1.38 rad after subtracting the screen. The file's `*CorrectionApplied = True` flags are in `processingInformation/parameters/geocoding` and are NOT evidence the phase is corrected (unverified reading: they describe geolocation). Subtract the screen. Caveat: the screen was filled by nearest-neighbour over a large area (mask bit 24 set on ~49% of pixels); its uncertainty layer must be carried into the error budget.
- **Troposphere / solid-earth tides:** separate screens exist in `metadata/radarGrid` (hydrostatic, wet, solid-earth-tide). Whether to subtract them is still to be tested.
- **Wavelength:** 24.20 cm (1.2390 GHz). 1 rad = 19.25 mm LOS. Sign convention: still to be checked against the NISAR product spec before any rate is published.
- **COVERAGE PROBLEM:** track 128 D frame 072 covers only 20.5% of the Eloy box (mean coherence 0.45) and 0% around Eloy town and Casa Grande. It covers Willcox well (93.9% of the box valid, coherence 0.57). It does not reach Buckeye at all.
- By footprint (ASF search): 077 A frame 018 and 056 D frame 072 both contain Eloy town, Casa Grande, Stanfield, Buckeye and Goodyear. Buckeye is also in 157 D frame 071 (12 scenes). Willcox also in 149 A frame 018 (9 scenes).
- Scene dates: 077 A = Nov 3, Nov 15, Dec 9 2025, then Jun 19, Jul 1, Jul 13, Jul 25, Aug 18, Aug 30, Sep 11, Sep 23, Oct 5 2026. 056 D = Jun 30 to Oct 4 2026 (8 scenes). 128 D = 29 scenes Oct 26 2025 to Oct 9 2026 with gaps.
- Scene list saved in `data/processed/scene_list.json`. Scripts in `src/`.

### Nov 14, evening: why so few scenes, and West Valley coverage (footprint-level, pixel check pending)
- Few scenes is real, not a search artifact: RSLC acquisition dates over Eloy match the GUNW dates. 077 A has no acquisitions Dec 21 2025 to Jun 19 2026; 056 D starts Jun 30 2026; 128 D has the full year with skipped cycles. Newest acquisitions (Oct 16 to Nov 14) have no GUNW yet; re-search later. Check `temporalBaseline` per file, some pairs may be 24 days.
- West Valley (Buckeye/Goodyear box, and an approximate Sun City/Surprise/Peoria/Glendale area, unverified box): 056 D frame 72 covers ~100% (8 dates, Jun 30 to Oct 4 2026); 077 A frame 18 covers 98% / 95% (12 dates, gap Dec 2025 to Jun 2026). Full-year tracks cover little: 157 D frame 71 covers 46% of the Buckeye box (13 dates), 5 A frame 18 covers 0% (26 dates). Footprints are frame outlines; real valid pixels will be smaller (track 128 lost most of the Eloy box this way).

### Nov 14, evening: Willcox time series v0 (track 128 D frame 072, 25 consecutive pairs Oct 26 2025 to Oct 21 2026)
- Method: valid pixels (coh >= 0.4, component > 0, phase != 0), subtract ionosphere screen, phase to mm (sign UNVERIFIED), reference each pair to a 5 km circle at the Dragoon Mountains (coordinates from memory, UNVERIFIED), chain-sum pairs, region mean over the 142,535 pixels valid in all pairs (34.2% of the box).
- Baselines are 11, 12, 23 and 24 days (not all 12: skipped cycles). Chain is unbroken.
- Rate: OLS -3.44 +/- 1.23 cm/yr; Theil-Sen -2.52 (95% CI -4.73 to -1.04); without the Sep 15 date -2.37 +/- 0.93; through Aug 22 only -0.55 +/- 1.01. NOT a result: the rate depends on the last 2 months.
- Why: residual rms 17.8 mm; pair-to-pair jumps std 23 mm, max 72 mm (Sep 15 to Sep 27). Lag-1 correlation of consecutive pairs is -0.39, which is what independent errors on single acquisition dates look like (a bad date contaminates both pairs that use it). Troposphere and solid-earth-tide screens are NOT yet removed, and the ionosphere screen was nearest-neighbour filled. Consecutive-only chaining has no redundancy to average these errors out.
- Next: remove troposphere + solid-earth tides (radarGrid), test whether per-date noise falls; use redundant pairs if possible; check reference sensitivity; map the rate to see whether the signal is in the playa basin.
- Plot: docs/willcox_timeseries_v0.png

### Nov 14, evening: Sentinel-1 background layer (OPERA DISP-S1) and NISAR Eloy
- Periods: Sentinel-1 frame 7091 (Eloy + West Valley) Jul 16 2016 to Feb 6 2026, 17 blocks (~6-month steps, one 15-month block in 2018-19). Frame 34478 (Willcox) Jul 23 2016 to Apr 14 2026, 19 blocks. NISAR track 128 D (Willcox) Oct 26 2025 to Oct 21 2026, 25 pairs. NISAR track 077 A (Eloy/West Valley): only Jun 19 to Oct 17 2026 (9 chained pairs, 3.9 months) is usable; the 3 pairs from Nov to Dec 2025 cannot be chained across the Dec 2025 to Jun 2026 gap.
- OPERA product facts (from the file): displacement is LOS metres, positive toward the satellite; solid_earth_tide and ionospheric_delay are separate layers to subtract; troposphere not corrected.
- Sentinel-1 LOS rate, 2016-2026, point windows (1.5 km), spread over 3 reference sites (references hand-picked, UNVERIFIED): Eloy-Picacho -0.90 to -1.03 cm/yr; Eloy town -0.71 to -0.84; Casa Grande -0.05 to -0.18 (about zero); Stanfield -0.63 to -0.76. White-noise OLS sigma 0.1 cm/yr is optimistic. Fastest 1% of pixels in the Eloy box: about -1.3 cm/yr.
- Willcox playa (-109.84, 32.10): -1.45 to -1.68 cm/yr over 10 years, last 3 years -1.69 to -2.74 (reference-sensitive). Fastest 1% of pixels about -5.6 to -5.8 cm/yr. Willcox town about -0.1 to -0.3; area north of the playa about 0.
- NISAR 077 A at Eloy: -3.92 +/- 3.00 cm/yr over 3.9 months, NOT significant; consistent with Sentinel-1 (about -1) within 1 sigma. Residual rms 9.2 mm vs the few mm expected over this span.
- All values are LOS, not vertical. Not yet compared with ADWR (no sourced ADWR value yet).

### Nov 14, night: Sentinel-1 vs NISAR cross-check at Willcox playa (overlap Oct 26 2025 to Apr 12/14 2026, 168 days)
- Sentinel-1 (frame 34478, track 129 D) change Oct 28 to Apr 14: -21.4 mm (3,600 px). NISAR (track 128 D) change Oct 26 to Apr 12: -12.9 mm, but from only 20 pixels valid in all 10 pairs (playa coherence is patchy in NISAR). Same sign, not the same size; difference (8.5 mm) is within the single-date noise (Sentinel-1 itself moves +20.5 mm between Oct 4 and Oct 28). Only a consistency check, not a validation.
- Eloy/West Valley: no Sentinel-1 overlap with usable NISAR (Sentinel-1 ends Feb 2026, NISAR 077 A usable from Jun 2026).

### Nov 14, night: data-driven hotspot search (Sentinel-1 OPERA, whole frames, 300 m, reference = frame median, 2016-2026, LOS cm/yr, negative = sinking)
- Central frame 7091: robust noise sigma 0.21 cm/yr. Strongest cluster is the Eloy-Picacho belt: 177 km2 below -0.6 cm/yr (median -0.87, 5th pct -1.7); densest 22 km2 core at (32.650, -111.591) median -1.38, fastest -2.8. Other clusters, all UNVERIFIED as to cause: (33.162, -112.661) 7 km2 median -1.28 (south of Buckeye, farmland?); (33.384, -111.602) 22 km2 median -0.78 (possible terrain/atmosphere artefact near the Superstitions); (33.148, -110.968) 4.5 km2, 5th pct -6.2 (probably mining, not groundwater).
- West Valley towns are FLAT (median within 3 km, cm/yr): Buckeye -0.03, Goodyear 0.00, Surprise -0.12, Sun City -0.22, Glendale -0.03, Phoenix -0.07. No detectable long-term sinking above about 0.5 cm/yr there in 2016-2026 Sentinel-1. The Buckeye/Goodyear story must be reframed (what is being built vs no detectable sinking yet).
- Southeast frame 34478: Willcox basin 457 km2 median -2.74, fastest -10.4 cm/yr; (32.213, -109.168) 191 km2 median -2.09; (32.310, -109.419) 140 km2 median -2.57; (31.727, -109.698) 103 km2 median -3.01. Place names for these coordinates NOT yet checked.
- Candidate files: data/processed/hotspot_candidates_central.json and _southeast.json; map: docs/central_az_sentinel1_rate_map.png.

### Nov 14, night: team decisions
- DROPPED: the Buckeye/Goodyear hotspot (Sentinel-1 shows no detectable sinking above about 0.5 cm/yr there; a short note on the map can say so). ADDED: southeast areas around Willcox (Sulphur Springs Valley), pending place-name check.
- Layers: NISAR on top (2025-2026, short record, labelled), Sentinel-1 OPERA below (2016-2026 trend, 6-month steps).
- HyP3 on-demand Sentinel-1 InSAR cost (from hyp3-docs.asf.alaska.edu/using/credits/): free allowance 8,000 credits per user per month; InSAR 80 m = 10 credits per pair, 40 m = 15. About 10 pairs for Jun-Oct 2026 at Eloy = about 100 credits (1.3% of the monthly allowance). Over the allowance, HyP3+ credits cost $0.05 each (derived from the table). Nothing submitted yet.
- Cleanup: deleted 3 unusable NISAR 077 A pairs (Nov-Dec 2025, isolated chain) and 1 extra OPERA granule; results unchanged.
- More Sentinel-1 frames downloading: 7092 D (Tucson/Avra Valley/Sahuarita), 34477 D (Safford), 5125 A (ascending, Tucson to Willcox, cross-check), 26691 D (Yuma/Wellton/Gila Bend).

### Nov 14, night: four more Sentinel-1 frames scanned; both-direction check; OSM land-use check
- Frames: 7092 D (Tucson/Avra Valley/Sahuarita), 34477 D (Safford), 5125 A (ascending, Tucson to Willcox), 26691 D (Yuma/Wellton/Gila Bend). All LOS cm/yr over 2016-2026, referenced to each frame's median, negative = sinking, clusters >= 2 km2. Lists in data/processed/hotspot_candidates_*.json.
- CONFIRMED IN BOTH LOOK DIRECTIONS (descending and ascending agree):
  - Willcox basin core (about 32.10, -109.78): D 457 km2 median -2.74; A 130 km2 median -2.92. Farmland all around (24 OSM polygons), no mines within 3 km.
  - North of Willcox (about 32.40-32.52, -109.93 to -110.01, Graham County): D medians -2.3 to -6.8 (fastest -9.8); A 86 km2 median -3.63. Land use unchecked (Overpass failed).
  - South, Elfrida/McNeal area? (31.73, -109.70, Cochise County): D 103 km2 median -3.01; A 68 km2 median -2.91. Farmland (19 polygons), no mines.
  - Eloy-Picacho (32.65, -111.59): D -1.2 to -1.4; A -1.56. Farmland (60 polygons), no mines.
- ONE DIRECTION ONLY: East basin (32.21, -109.17) D 191 km2 median -2.09 and (32.31, -109.42) D 140 km2 median -2.57; ascending frame does not reach them. Little farmland nearby (2 and 0 polygons), cause unclear. (33.16, -112.66) near Buckeye: two descending tracks, 4-7 km2, about -1.3 to -1.7.
- NOT GROUNDWATER (per OpenStreetMap): Sahuarita A = Sierrita Mine, Sahuarita B = Mission Complex, (33.15, -110.97) = Ray Mine, (33.13, -109.35) geocodes to Morenci (mining town; mine features not retrieved). OUT OF ARIZONA: (32.41, -115.26) is Cerro Prieto geothermal field, Mexicali; (31.14, -112.89) is Caborca, Sonora.
- FLAT (no cluster above 1 cm/yr): Tucson, Avra Valley, Marana, Yuma, Phoenix valley, West Valley.
- Caveat for all: single-sensor LOS rates, frame-median reference (a few mm/yr bias possible), tropospheric/topographic artefacts not corrected, not validated against ADWR.

### Nov 14, night: web map v0 built (web/, data from src/export_web.py)
- Two layers: NISAR rate rasters (Willcox 128 D, Eloy 077 A) and Sentinel-1 descending mosaic (frames southeast, 34477, central, 7092, 7090) plus ascending cross-check (frame 5125). Hotspots: Eloy-Picacho, Willcox basin, North of Willcox, South of Willcox (Elfrida/McNeal area?), East of Willcox. Probable-mine markers and checked-flat markers from the same cubes.
- DECISION TO REVIEW: the NISAR rate rasters are OFF by default and drawn relative to the box median. Reason: shown raw, each NISAR box turned uniformly dark red (about -3 cm/yr common drift from a short, noisy record), which would misread as fast sinking. Flip the default in web/index.html if the team disagrees.
- Hotspot stats (sinking pixels <= -1 cm/yr in each box, Sentinel-1 descending; ascending median at the same pixels): Eloy-Picacho 85 km2 median -1.23 (asc -1.43, only 153 px); Willcox 386 km2 median -2.38 (asc -1.63); North of Willcox 116 km2 median -4.66 (asc -3.55); South 127 km2 median -2.86 (asc -1.91); East 337 km2 median -2.17 (no ascending coverage).
- In three of the four areas that have an ascending check (Willcox, Fort Grant Road, Elfrida) the ascending median is about a quarter to a third smaller than the descending one; at Eloy (only 153 pixels) it is about 16% larger. Not explained yet (different look geometry, horizontal motion, reference). Treat the two directions as agreeing in sign and ranking, not in size.
- Blue (rising) patch on the Willcox Playa floor: probably wet or swelling soil, unverified.
- Not done: click-any-point values, ADWR comparison, farmland acres, data centers, time slider, GitHub Pages deploy (needs repo owner's OK).
- Basemap: Esri World Dark Gray / World Imagery (CARTO tiles now require an API key). CDN scripts pinned with integrity hashes.
- More frames in the background: north/west chain (7090 done and included; 26690, 46289, 34476 downloading/scanning).
