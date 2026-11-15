# Radar track selection and immediate next checkpoint

This handoff updates the original track-128-at-Eloy plan without changing the 12-hour Eloy-first MVP.

## Evidence and provenance

Reviewed repository snapshot: [54a66b8](https://github.com/mansi200304/NASA-Hackathon/commit/54a66b87649333a0ef3de4b28db4a4b7dbb216e6), November 14, 2026.

- [CLAUDE.md, section 14](../CLAUDE.md): Reshma's recorded results from the track-128 D / frame-072 October 9–21, 2026 test file.
- [scene_list.json](../data/processed/scene_list.json): committed catalogue records audited here.
- [coverage_check2.py](../src/coverage_check2.py): existing coverage diagnostics.

The raw HDF5 file is on the team's Windows machine, not in GitHub. Coverage measurements below are attributed to the status log; this audit did not independently run them or derive a subsidence rate.

## Coverage decision

| Track/frame | Recorded evidence | Action |
|---|---|---|
| 128 D / 072 | Test-file log reports 20.5% valid coverage of the Eloy box, none around Eloy town/Casa Grande, 93.9% of the Willcox box, and no Buckeye coverage | Do not use this test file for the Eloy core. Retain as a separate Willcox candidate. |
| 077 A / 018 | Catalogue footprint contains Eloy/Casa Grande and Buckeye/Goodyear; pixel quality not yet checked here | First candidate to inspect for the Eloy MVP |
| 056 D / 072 | Catalogue footprint contains Eloy/Casa Grande and Buckeye/Goodyear; pixel quality not yet checked here | Alternative Eloy candidate |

Footprint overlap does not establish usable pixels. Coverage and reference checks must be repeated for the chosen file and across the stack.

## Acquisition-pair audit

The scene list's secondary-date column is null. The reference and secondary acquisition dates can still be recovered from the product IDs: four timestamp tokens describe reference start/stop and secondary start/stop. Do not use the first-date column alone to assess temporal connectivity.

| Track/frame | Listed records | Unique acquisition-date pairs | Connected intervals |
|---|---:|---:|---|
| 128 D / 072 | 29 | 25 | October 26, 2025–October 21, 2026 after deduplicating versions |
| 077 A / 018 | 12 | 12 | November 3–December 21, 2025 (3 older pairs); June 19–October 17, 2026 (9 provisional pairs), with no listed bridge between them |
| 056 D / 072 | 8 | 8 | June 30–October 16, 2026 |

The same 128 D records are listed under both Eloy and Willcox keys; they are not additional independent scenes.

Examples showing why the original all-12-day assumption fails:
- 077 A: July 25–August 18, 2026 is a 24-day pair.
- 056 D: July 24–August 17, 2026 is a 24-day pair.
- 128 D also includes 24-day pairs.

Missing intermediate acquisitions do not necessarily break a chain if a listed longer-baseline pair connects the dates. Conversely, do not invent a bridge across the December 2025–June 2026 gap on 077 A.

Four 128 D pairs occur in both older X05010 and P05023 processing versions. Select a consistent appropriate processing collection after checking metadata and quality; do not count both versions as separate observations. Product-name PR means production, not proof of provisional/validated maturity: inspect the collection and processing metadata.

## Next step: one replacement Eloy file

1. Inspect one provisional 077 A / 018 GUNW file, initially one from the June–October 2026 component. Use 056 D / 072 if the first candidate fails coverage or reference checks.
2. Verify identification metadata, reference/secondary dates, actual polarisation, CRS, coordinate grids, wavelength and phase/correction conventions.
3. Check usable pixels over the actual Eloy/Casa Grande target and a plausible stable reference area. A whole-footprint percentage is insufficient.
4. Report crop shape, pixel spacing, finite/valid/coherent fractions and reference coverage. State the coherence threshold and mask/fill semantics used.
5. Only then select the track and start its stack downloads. Use the supported connected interval in rate estimates and map metadata.

Existing coverage_check2.py assumes HH polarisation and EPSG:32612. Its point checks use approximately 9.6 km windows. Verify/adapt those assumptions for the replacement product. Exact-zero phase is currently excluded by the team's exploratory rule; check fill attributes and quality flags before generalising that rule to every product.

## Handoff to processing and the web app

- Use actual elapsed time for cumulative series and rate fitting.
- Do not combine ascending/descending series directly or treat independently referenced components as one series.
- The proposed 077 A provisional series is about four months, not a continuous year. An annualised rate needs that observation interval and uncertainty stated.
- Willcox on 128 D is a separate processing task. Buckeye can share the selected Eloy stack only if actual usable coverage and referencing support it.
- Keep the existing export filenames and hotspot slugs. Populate track, dates, rate and uncertainty from real processing; do not retain a 128D placeholder for an Eloy result derived from another track.
- Match ADWR comparison area, time interval and displacement direction where possible. A comparison at one site does not establish accuracy everywhere.
- No new measured rate, validation result or uncertainty is supplied by this documentation update.

## Audit method

For each scene-list row, extract the first and third timestamp tokens from its product ID, group duplicate acquisition-date pairs, and sort by reference date. Check whether a pair's secondary date joins the next pair's reference date. Counts above are date-pair counts, not counts of independent pixels or guarantees of scientific usability.
