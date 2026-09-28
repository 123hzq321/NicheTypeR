# Sodb Calibration Lean Benchmark

This table reports source-level configurations prepared after a complete representative-file audit of the downloadable SODB spatial-transcriptomics catalog. Multiple experiments from one publication remain one source ID.

- Completed configurations: **39**
- Completed source IDs: **39**
- Unique cells/spots: **115,144**
- Learned-neighborhood strict passes: **8/39**
- Context-specific strict passes: **0/39**

| dataset | task | cells/spots | labels | groups | marker F1 | learned F1 | learned strict | CSAE strict |
|---|---|---:|---:|---:|---:|---:|---|---|
| SODB:10x | cell type | 2,673 | 7 | 36 | 0.4191 | 0.4307 | yes | no |
| SODB:backdahl2021spatial | cell type | 1,597 | 9 | 34 | 0.3710 | 0.3735 | no | no |
| SODB:Barkley2022Cancer | cell type | 1,847 | 9 | 36 | 0.3546 | 0.3644 | no | no |
| SODB:bergenstrahle2021super | cell type | 2,361 | 11 | 36 | 0.4622 | 0.4714 | no | no |
| SODB:berglund2018spatial | cell type | 469 | 9 | 9 | 0.2994 | 0.3036 | no | no |
| SODB:Biermann2022Dissecting | cell type | 3,563 | 8 | 36 | 0.4619 | 0.4556 | no | no |
| SODB:Borm2022Scalable | cell type | 6,500 | 13 | 36 | 0.6515 | 0.6607 | yes | no |
| SODB:Buzzi2022Spatial | cell type | 2,427 | 15 | 36 | 0.5496 | 0.5432 | no | no |
| SODB:chen2020spatial | cell type | 447 | 6 | 9 | 0.5981 | 0.6269 | no | no |
| SODB:chen2021decoding | cell type | 7,288 | 18 | 36 | 0.3857 | 0.4030 | yes | no |
| SODB:Dhainaut2022Spatial | cell type | 1,244 | 12 | 25 | 0.4974 | 0.5149 | no | no |
| SODB:Dixon2022Spatially | cell type | 2,219 | 11 | 36 | 0.5357 | 0.5449 | no | no |
| SODB:fawkner2021spatiotemporal | cell type | 2,448 | 9 | 34 | 0.5138 | 0.5148 | no | no |
| SODB:Fu2021Unsupervised | cell type | 10,248 | 24 | 36 | 0.4614 | 0.4579 | no | no |
| SODB:Garcia2021Mapping | cell type | 2,508 | 6 | 36 | 0.5110 | 0.5121 | no | no |
| SODB:Gouin2021An | cell type | 814 | 7 | 16 | 0.4768 | 0.4939 | no | no |
| SODB:guilliams2022spatial | cell type | 532 | 6 | 9 | 0.4846 | 0.4905 | yes | no |
| SODB:hunter2021spatially | cell type | 2,393 | 13 | 36 | 0.4571 | 0.4784 | no | no |
| SODB:ji2020multimodal | cell type | 608 | 9 | 9 | 0.4302 | 0.4391 | no | no |
| SODB:Juntaro2022MEK | cell type | 2,429 | 15 | 35 | 0.4086 | 0.4207 | no | no |
| SODB:Kadur2022Human | cell type | 1,167 | 11 | 18 | 0.4775 | 0.4945 | yes | no |
| SODB:Konieczny2022Interleukin | cell type | 505 | 8 | 9 | 0.5821 | 0.5813 | no | no |
| SODB:kvastad2021the | cell type | 997 | 9 | 16 | 0.3367 | 0.3369 | no | no |
| SODB:Lebrigand2022The | cell type | 902 | 7 | 16 | 0.7991 | 0.8181 | no | no |
| SODB:liu2022spatiotemporal | cell type | 4,670 | 15 | 30 | 0.3397 | 0.3396 | no | no |
| SODB:mantri2021spatiotemporal | cell type | 747 | 8 | 14 | 0.6307 | 0.6424 | yes | no |
| SODB:maynard2021trans | cell type | 2,908 | 8 | 36 | 0.5103 | 0.5220 | no | no |
| SODB:Melo2021Integrating | cell type | 3,007 | 13 | 36 | 0.4823 | 0.4925 | no | no |
| SODB:Merfish_Visp | cell type | 2,399 | 16 | 35 | 0.6818 | 0.6945 | no | no |
| SODB:Misra2021Characterizing | cell type | 959 | 9 | 16 | 0.3551 | 0.3517 | no | no |
| SODB:parigi2022the | cell type | 3,382 | 12 | 36 | 0.5343 | 0.5477 | no | no |
| SODB:Pascual2021Dietary | cell type | 1,269 | 11 | 25 | 0.4602 | 0.4556 | no | no |
| SODB:Ratz2022Clonal | cell type | 3,264 | 10 | 36 | 0.6496 | 0.6583 | no | no |
| SODB:rodriques2019slide | cell type | 3,760 | 34 | 36 | 0.5647 | 0.5607 | no | no |
| SODB:stickels2020highly | cell type | 9,545 | 28 | 36 | 0.3569 | 0.3521 | no | no |
| SODB:Vickovic2019high_update | cell type | 14,064 | 63 | 36 | 0.5257 | 0.5236 | no | no |
| SODB:Visium_Allen | cell type | 2,492 | 7 | 36 | 0.4191 | 0.4311 | yes | no |
| SODB:xia2019spatial | cell type | 606 | 11 | 16 | 0.5474 | 0.5820 | yes | no |
| SODB:Zhang2023Amolecularly_rawcount | cell type | 3,886 | 26 | 36 | 0.8264 | 0.8222 | no | no |
