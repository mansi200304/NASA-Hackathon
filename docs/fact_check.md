# Fact-check log

Rule from the team (Nov 15 2026): any information added to the site or docs is checked against real sources first. Each line: the claim, what was checked, the result. "Unverified" claims are labelled as such wherever they appear.

| Claim | Checked against | Result |
|---|---|---|
| NISAR GUNW Provisional DOI is 10.5067/NIL2GUNW-P1 | The DOI resolver: it redirects (302) to the Earthdata catalog entry "NISAR Provisional Geocoded Unwrapped Interferogram Product (Version 1)", ASF DAAC. The catalog text itself prints "NIL1GUNW-P1", which returns 404: a typo in their metadata. | Correct as used. |
| OPERA DISP-S1 DOI is 10.5067/SNWG/OPL3DISPS1-V1 | The DOI resolver redirects to the Earthdata catalog entry for OPERA L3 DISP-S1 V1; JPL's OPERA product page describes DISP-S1 (30 m, line of sight, from CSLC-S1, ASF DAAC). | Correct. Site link now points to the DOI. |
| NISAR does not remove the troposphere / solid-earth-tide / ionosphere phase from the unwrapped phase | nisar-docs.asf.alaska.edu/gunw: tables "are not removed from the interferometric data"; the ionosphere screen is "included in the product but not applied ... by default". | Verified. Our subtraction is needed. |
| Sign to apply the screens | The ASF page does not state it (and does not say which weather model produced the tables). | Not verifiable from the docs. We tested both signs on 25 real pairs and kept the one that reduces scatter (docs/STATUS.md, src/nisar_noise_test.py). The site says "we tested it both ways". The wording "NISAR ships with a model" was wrong and was replaced. |
| Provisional data = exploration and process studies, partially validated | Earthdata catalog entry for the GUNW Provisional collection. | Verified, matches the site's "preliminary" labels. |
| NASA data are open without restrictions | NASA Earth science data and information policy pages. | Verified for access. A citation requirement was not found; we cite anyway. |
| Copernicus GLO-30 is free, EGM2008-referenced | Copernicus Data Space and Earth Engine catalog pages. | Verified. It is a surface model (includes vegetation). Public distribution needs a source notice (we do not redistribute it). |
| Geoid offset used: -28 m for Arizona | EGM2008 grid through pyproj (EPSG:4979 to EPSG:3855). | -27.8 m at Willcox, -30.5 m at Eloy. Negligible against the 500 m layer spacing. |
| NISAR GCOV is dual-pol (HH, HV) at Willcox, about 7 GB per file | asf_search listing (file names say DHDH, sizes 7.0 to 7.3 GB); ASF docs and the GCOV product spec (JPL D-102274) describe HHHH/HVHV diagonal terms with gamma0 normalisation. | Verified for naming and sizes. Exact layer details are read from the files themselves. |
