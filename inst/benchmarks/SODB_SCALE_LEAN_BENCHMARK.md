# SODB scale benchmark

This table reports source-level configurations prepared after a complete representative-file audit of the downloadable SODB spatial-transcriptomics catalog. Multiple experiments from one publication remain one source ID.

- Completed configurations: **20**
- Completed source IDs: **20**
- Unique cells/spots: **201,107**
- Learned-neighborhood strict passes: **3/20**
- Context-specific strict passes: **1/20**

| dataset | task | cells/spots | labels | groups | marker F1 | learned F1 | learned strict | CSAE strict |
|---|---|---:|---:|---:|---:|---:|---|---|
| SODB:Allen2022Molecular_aging | cell type | 8,596 | 12 | 3 | 0.8697 | 0.8648 | no | no |
| SODB:Allen2022Molecular_lps | cell type | 8,840 | 12 | 3 | 0.8918 | 0.8864 | no | no |
| SODB:Booeshaghi2021Isoform | cell type | 3,502 | 19 | 3 | 0.8456 | 0.8426 | no | no |
| SODB:chen2021dissecting | cell type | 8,711 | 9 | 2 | 0.3101 | 0.3105 | no | no |
| SODB:chen2022spatiotemporal | spatial domain | 18,360 | 26 | 3 | 0.0675 | 0.0716 | no | no |
| SODB:codeluppi2018spatial | cell type | 5,328 | 32 | 34 | 0.4290 | 0.4409 | no | no |
| SODB:eng2019transcriptome | cell type | 1,826 | 10 | 8 | 0.4268 | 0.4232 | no | no |
| SODB:Fang2022Conservation | cell type | 11,648 | 18 | 3 | 0.8443 | 0.8496 | yes | no |
| SODB:he2020integrating | spatial domain | 2,000 | 2 | 45 | 0.7835 | 0.7875 | no | yes |
| SODB:Marshall2022High_human | cell type | 13,496 | 24 | 3 | 0.1031 | 0.1056 | no | no |
| SODB:Marshall2022High_mouse | cell type | 8,746 | 14 | 3 | 0.2146 | 0.2167 | no | no |
| SODB:seqFISH_VISp | spatial domain | 2,721 | 7 | 36 | 0.4565 | 0.4764 | no | no |
| SODB:Shi2022Spatial | cell type | 11,310 | 20 | 3 | 0.5134 | 0.5178 | no | no |
| SODB:Sun2021Integrating | spatial domain | 5,831 | 8 | 3 | 0.3326 | 0.3515 | no | no |
| SODB:Wang2018Three_1k | cell type | 872 | 10 | 16 | 0.6994 | 0.6984 | no | no |
| SODB:wang2021easi | cell type | 46,720 | 48 | 101 | 0.4641 | 0.4973 | yes | no |
| SODB:wang2022high | spatial domain | 8,589 | 10 | 36 | 0.6202 | 0.6240 | no | no |
| SODB:wei2022single | cell type | 14,710 | 31 | 3 | 0.0545 | 0.0558 | no | no |
| SODB:Wu2022spatial | cell type | 8,102 | 17 | 36 | 0.4661 | 0.4786 | no | no |
| SODB:Zeng2023Integrative | cell type | 11,199 | 13 | 3 | 0.7121 | 0.7369 | yes | no |
