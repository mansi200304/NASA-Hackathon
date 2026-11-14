# Arizona Is Sinking — NASA Space Apps 2026, "Dancing with the SARs" (NISAR)

Solo entry by Reshma Panibhate (Earthdata user: raypanibhate). Locked in Nov 14 2026.

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

### 3.1 Main deliverable: an interactive web map ("Arizona Is Sinking")
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
- Vertex, Eloy box, NISAR GUNW, production: **49 scenes** across **3 tracks**: 128 descending (frame 072), 056 descending (frame 072), 077 ascending (frame 018). ~16 per track. Every product is a consecutive **12-day pair**.
- Downloaded one test file into this folder (2,378,170,368 bytes, valid HDF5):
  `NISAR_L2_PR_GUNW_032_128_D_072_033_4000_SH_20261009T020749_20261009T020824_20261021T020749_20261021T020824_P05023_N_F_J_001.h5`
  Name: L2 / PR (production) / GUNW / ref cycle 032 / track 128 / D (descending) / frame 072 / secondary cycle 033 / SH (single pol, HH confirmed) / Oct 9 → Oct 21 2026 / CRID P05023 / Provisional.

## 7. Method (pipeline)
1. **Inspect** the HDF5 tree: find unwrapped phase, coherence, connected components, coordinate grids, wavelength, sign convention, reference/secondary times.
2. **Phase → displacement:** `d = -(λ / 4π) · φ` (L-band λ ≈ 0.24 m). Read λ and sign convention from metadata; don't assume.
3. **Mask** low coherence and unreliable connected components.
4. **Reference** to a stable area (bedrock/mountains) set to zero.
5. **Stack:** single 12-day pairs are mostly noise (Eloy moves a few mm in 12 days). Chain consecutive pairs on **one track** (128 D first) into a cumulative time series; fit a linear rate with uncertainty. Never mix ascending and descending directly.
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
| 3 | Track-128 stack | Cumulative displacement at Eloy center over the full record |
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

## 10. How I want to work (instructions for Claude)
- Teach step by step; explain the "why" before the code. Don't build everything at once.
- Every stage ends in a real measured number, not just a working demo.
- Real processing pipeline; no hardcoded or ground-truth shortcuts.
- Debug from first principles; check environment activation/sourcing before assuming deeper problems.
- My input is often voice-transcribed; ask when something is unclear.

## 11. Immediate next step
Print the HDF5 group tree of the downloaded `.h5` file and explain what each group is.
