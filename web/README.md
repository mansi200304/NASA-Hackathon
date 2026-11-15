# Sinkronized — web map

A buildless, map-first field atlas using Sonoran Sand, with a plain-language Overview introducing subsidence, the evidence and its limitations. The map and study selection work immediately. Measurements and context overlays stay pending until real exports are available.

## Run it

From the **repository root**, run:

    python -m http.server 8000

Open http://localhost:8000/web/ . Serve the root, rather than only web/, because the app reads ../data/processed/.

No npm install, build step, API key or Earthdata credential is required. Leaflet 1.9.4 is vendored under vendor/ with its license. Esri basemap tiles require internet access.

## Portable design preview

    node web/build-preview.mjs

Open web/preview.html in a browser. This generated single HTML file embeds the current app, Leaflet and available processed JSON/GeoJSON/PNG files. It works without a local server; internet is still required for basemap tiles. Rebuild after source or data changes. The preview is a snapshot, not a live feed of repository changes.

The original app in index.html remains the source of truth. No fabricated measurement fixtures are shipped.

## What works

- Select any area supplied in `hotspots.geojson`; names, order, study numbers, file paths and outlines come from that file. There is no fixed location list or required count.
- View all study areas, fit the selected area, pan and zoom, or switch satellite/terrain basemaps. Satellite imagery is the default. The dark basemap was removed from the interface.
- Toggle available overlays and adjust their opacity. On phones, Layers opens the controls while leaving room for the map.
- Read a fitted rate, uncertainty, interactive observation chart (hover, focus, tap or click a measured point), accessible observation table and reference metadata when supplied.
- Scroll from the Overview into the full atlas, or jump directly to it with the header navigation. The Overview explains ascending and descending satellite passes in an expandable scientific note.
- Tap study areas, context features or the map background to open a bottom field note, and use Explain actions beside measurements, charts and comparisons. Coordinate clicks never invent pixel values.
- Open How we measured, Limits and Sources dialogs. Dialogs support Escape; controls have visible keyboard focus.
- Inspect a map coordinate. Pixel-level rate/coherence sampling is explicitly unavailable: a coloured PNG is not a numeric raster.

Study boxes are pipeline-defined extents from `data/processed/hotspots.geojson`. They are not ADWR subsidence features or mapped sinking zones. The first feature is the initial selection; tentative names and question marks are preserved.

## Add real data

All paths below are relative to data/processed/. Refresh the page after adding files.

| File | Behaviour |
| --- | --- |
| hotspots.geojson | Required: project study polygons with name, slug, story; optional tagline and county. |
| timeseries_\<slug\>.json | Details and chart for the matching study slug. |
| rate_\<slug\>.json + rate_\<slug\>.png | Georeferenced colour image for the matching study slug. |
| adwr_subsidence.geojson | Optional official subsidence context. |
| rate_sentinel1_descending / _ascending, rate_nisar_willcox / _eloy (.json + .png) | Region-wide rate images, listed as layers (NISAR ones are provisional and start hidden). |
| mines_excluded.geojson, checked_flat.geojson | Marker layers: probable mines (not groundwater) and places checked with no sinking found. |

Missing optional files are normal. They produce pending states and disabled controls. Malformed files produce Review file, not a zero result.

### Time series

Required fields follow the project contract: hotspot, units (cm), reference, dates, displacement, rate_cm_yr, rate_sigma, adwr_rate_cm_yr. Empty arrays and null rates are allowed for pending records. Numeric observations require a nonempty reference description. Dates must be valid, unique and increasing; displacement may contain null gaps. A true numeric zero remains zero.

Optional metadata displayed when provided: track (include frame in the string if needed), data_release, sign_convention. Do not set these from a guess. Without a sign convention the app calls the number a reported displacement rate, not vertical sinking. With no uncertainty, it says uncertainty was not supplied.

The chart uses actual acquisition dates on the horizontal axis and breaks at null gaps. It does not add synthetic observations, fit rates or draw uncertainty that the pipeline has not exported.

The reported uncertainty uses `rate_sigma` unchanged, including the pipeline's
systematic component. Its `rate_sigma_note` appears beside the rate so a
conservative proxy is distinguished from a measured cross-direction check.
Each study displays exported `caveats`, provisional NISAR `status_note` (without
presenting its unreliable rate as a result), and `land_use_note` when supplied.
These explanations are rendered as text; absent optional notes add no claims.

The ADWR value is contextual only. The interface does not subtract it from a LOS rate or claim validation until direction, reference, period and spatial footprint are comparable.

The current ADWR comparison displays the pipeline's sinking-pixel median,
ADWR Sentinel-1 and RADARSAT-2 medians, correlations and exported median
difference. It never subtracts an ADWR median from the fitted rate. ADWR's
units are labelled inferred; Sentinel-1 is a consistency check and RADARSAT-2
is an independent sensor over a longer period. The comparison links to the
team's method and explicitly preserves the weak Eloy result.

Official ADWR boundaries load from `adwr_subsidence.geojson`, with unfilled
outlines and source/period popups. Each study's confirmation is visible, with
single-direction results marked unconfirmed. When exported, stable-ground
observations appear as a dashed slate chart line and a table column; null
gaps remain gaps. The fitted rate and full pipeline uncertainty stay intact.

### Rate image

Required: bounds as [[south, west], [north, east]], units cm/yr, finite vmin < vmax, and dates containing at least a start and end date. Bounds must be geographic EPSG:4326. Optional crs must be EPSG:4326 (or 4326).

Additional metadata: track, colormap, data_release, sign_convention. Optional colors is an ordered array of hex stops matching the exported PNG, from vmin to vmax. A gradient legend is drawn only if valid colors are supplied; otherwise the range is printed without inventing a ramp. The app checks image loading before showing its legend.

The pipeline's documented custom red/transparent/blue ramp uses a categorical
key rather than an invented linear gradient. Track and acquisition range appear
in the map legend. Thin, unfilled study outlines and hover labels leave the
measurement raster visible. Raster colours and numerical results are unchanged.

Low-coherence/no-data pixels must be transparent in the exported PNG. This UI cannot verify the processing masks from image colours.

### Context GeoJSON

Use a WGS84 FeatureCollection. Marker popups read name plus reason or note. Source links accept only HTTP(S). Imported text is inserted as text, never HTML. The current UI does not calculate exposure areas, counts, water use or causal responsibility.

### Plain-language insights

`timeseries_<slug>.json` carries an `insights` block (summary, two confidence ratings, and headed paragraphs) written for readers who are not experts. The panel opens with it under "In plain terms"; `cleanInsights()` in `model.mjs` drops anything malformed. Confidence ratings follow fixed rules in `src/insights.py`. Data centers and habitat are no longer layers: there is no sourced data for them.

## Logo and icons

The original logo is `docs/brand/sinkronized-logo-original.png`. `python src/make_logo_assets.py` trims it and writes `web/assets/` (header logo, 512 px version, browser-tab icon, phone icon). To change the logo, replace the original and re-run that command. The header image is decorative (the name beside it is the accessible label).

## Design

Ivory canvas #F4EFE6, sand #E4D9C9, ink #2D2A25, rust #A64B2A and olive #52664B. Secondary text uses a darker slate #626D76 for legibility. Place names use Georgia; controls and measurements use Arial/Helvetica. System fonts keep loading predictable. Fine rules and sentence case carry the hierarchy.

Brand colours are separate from the measurement ramp. Changing the UI theme must not change the scientific meaning of a raster.

## Checks

    node --test web/tests/model.test.mjs
    node --check web/app.js

Tests cover pending vs zero, observation gaps, references, units, dates, uncertainty, geographic bounds and source-link protocols.

Contract checks cover arbitrary new study identities, file order, duplicate/unsafe slugs and every currently exported study's measured time-series/raster metadata, in addition to the checks above.

The map update was browser-checked against all current study selections, real
rate PNGs, basemap switching and the portable preview. A 390px phone review
confirmed study selection, Layers disclosure and no horizontal overflow.

The atlas remains a three-column data-driven layout with a widened study panel and more readable study-details typography. A responsive introductory section appears above the atlas. Sonoran Sand has distinct
roles: ivory canvas, sand sidebar, ink masthead/footer, rust selection and reported
rate, olive study count/status and slate metadata headers. Small light text uses
the darker slate variant for contrast. Scientific raster colours are independent
of these UI colours.

NASA Worldview, ISRO Bhuvan and Copernicus Browser informed the map treatment:
restrained controls, imagery as geographic context, thin outlines and visible
dataset provenance. No agency affiliation is implied.

## Scope

This is the first UI for team review. It does not deploy GitHub Pages or change the radar processing pipeline. For eventual Pages hosting, publish an artifact containing web/ and data/processed/ together so relative paths remain valid. Keep raw HDF5 and large rasters out of Git.


## Interface continuation (November 14–15, 2026)

The Overview, bottom field notes and interactive chart points are all presentation-layer changes; they do not alter measured values, map rasters, study geometries or scientific assumptions. The number, names and order of studies still come from `hotspots.geojson`. No fabricated observations or per-pixel measurements are added.

To test: open `/web/` from a repository-root server, select every available study, inspect a point in each chart, open and close a field note, toggle satellite/terrain imagery, and review the layout at desktop and phone widths. `node web/build-preview.mjs` recreates the distributable data-snapshot page after later pipeline changes.

## Why Arizona? Research-backed Overview

The new opening story explains why this Arizona-based team chose to study groundwater-related land subsidence and who can benefit from the atlas (residents, planners, water managers, researchers and conservation groups). The Overview includes three **historical evidence cards** with direct source links: the USGS compaction mechanism, the 1.09 m 1965–1983 Eloy measurement, and ADWR's estimated 155,805 acre-feet of agricultural water use in Willcox in 2022. The latter is supported by a peer-reviewed 2023 Willcox land-use/groundwater paper.

The Resources dialog includes an annotated bibliography of the agency reports, peer-reviewed research, processing data and mapping sources. **`docs/overview_evidence.md` maps each claim to a publication, year, geographic scope and limitation.** Historical agency and research results are explicitly distinct from the team's satellite-exported measurements. In particular, regional groundwater pumping and farming pressures do not identify the operator or activity responsible for any individual map pixel.
