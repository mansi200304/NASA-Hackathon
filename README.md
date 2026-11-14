# Arizona Is Sinking

NASA Space Apps 2026 — **Dancing with the SARs** (NISAR). 

Arizona's aquifers are being pumped faster than they refill, and the ground is sinking. NISAR's L-band radar can measure that motion to the millimetre. This project maps where central Arizona is sinking, how fast, and what sits on top of it: farms, new data centers, and wildlife habitat.

## Study areas

| Hotspot | Story |
|---|---|
| Eloy / Casa Grande | Decades of farm pumping. Validation site: our rates are checked against ADWR's published values. |
| Buckeye / Goodyear | Data-center growth in the West Valley, where few measurements are published. |
| Willcox | Fastest subsidence in Arizona, next to Willcox Playa sandhill crane habitat. |

## Method

1. Read NISAR L2 GUNW (geocoded unwrapped interferogram) products from ASF.
2. Convert unwrapped phase to line-of-sight displacement: `d = -(λ / 4π) · φ`, with λ and the sign convention read from the file metadata.
3. Mask low-coherence pixels and unreliable connected components.
4. Reference to a stable area.
5. Chain consecutive 12-day pairs from one track into a cumulative time series and fit a rate with uncertainty.
6. Validate at Eloy against ADWR InSAR rates, then repeat for the other hotspots.
7. Overlay farmland, data centers and protected areas, and publish an interactive web map.

## Progress

- [x] Stage 1: opened a test GUNW file (track 128, descending, Oct 9 → Oct 21 2026). Grid: EPSG:32612, 80 m pixels, wavelength 24.2 cm (1 rad ≈ 19.25 mm of line-of-sight motion), mean coherence 0.68 over valid pixels.
- [ ] Stage 2: one-pair displacement over Eloy
- [ ] Stage 3: track-128 stack
- [ ] Stage 4: rate and validation against ADWR
- [ ] Stage 5: other hotspots
- [ ] Stage 6: overlays
- [ ] Stage 7: web map

## Limits

- About one year of NISAR data is short for subsidence, so results come from stacks, not single pairs.
- Sinking indicates groundwater stress. It does not prove which user caused it.
- Radar loses coherence over plowed fields and construction.
- Radar measures line-of-sight motion; we assume motion is mostly vertical.
- Radar cannot see wildlife; habitat links come from outside maps.
- NISAR data is Provisional / Uncalibrated, so numbers are preliminary.

## Data

NISAR GUNW (ASF), Sentinel-1 (OPERA DISP-S1 / ASF HyP3) for history, ADWR subsidence maps, USDA Cropland Data Layer, PAD-US, NHD.

See [CLAUDE.md](CLAUDE.md) for the full project brief.
