# NicheTypeR 100-source portfolio

- Processed public source IDs: **100**
- Label-bearing validation sources: **61** across **68** configurations
- Cluster-only calibration sources: **39** across **39** configurations
- Total processed configurations: **107**
- Total configuration-level observation units: **1,386,473**
- Source-deduplicated units in the validation panel: **1,239,332**

## Results kept separate

- Label-bearing validation: learned-neighborhood strict pass **9/68**; CSAE strict pass **1/68**.
- Cluster-only calibration: learned-neighborhood strict pass **8/39**; CSAE strict pass **0/39**.

The 39 calibration sources use SODB-standardized Leiden clusters. They test ingestion, blocked execution and matched-null behavior, but they are not biological cell-type ground truth and are excluded from the primary efficacy denominator. The 100-source figure is therefore a processing-coverage statement, not a claim of 100 independent gold-standard cohorts. The validation panel contains 61 named sources and 59 known publication families; donor/slide/FOV independence is reported separately.

## Panel table

| source ID | panel | configurations | units | claim role |
|---|---|---:|---:|---|
| SODB:10x | cluster_only_calibration | 1 | 2,673 | operational and matched-null calibration only |
| SODB:Barkley2022Cancer | cluster_only_calibration | 1 | 1,847 | operational and matched-null calibration only |
| SODB:Biermann2022Dissecting | cluster_only_calibration | 1 | 3,563 | operational and matched-null calibration only |
| SODB:Borm2022Scalable | cluster_only_calibration | 1 | 6,500 | operational and matched-null calibration only |
| SODB:Buzzi2022Spatial | cluster_only_calibration | 1 | 2,427 | operational and matched-null calibration only |
| SODB:Dhainaut2022Spatial | cluster_only_calibration | 1 | 1,244 | operational and matched-null calibration only |
| SODB:Dixon2022Spatially | cluster_only_calibration | 1 | 2,219 | operational and matched-null calibration only |
| SODB:Fu2021Unsupervised | cluster_only_calibration | 1 | 10,248 | operational and matched-null calibration only |
| SODB:Garcia2021Mapping | cluster_only_calibration | 1 | 2,508 | operational and matched-null calibration only |
| SODB:Gouin2021An | cluster_only_calibration | 1 | 814 | operational and matched-null calibration only |
| SODB:Juntaro2022MEK | cluster_only_calibration | 1 | 2,429 | operational and matched-null calibration only |
| SODB:Kadur2022Human | cluster_only_calibration | 1 | 1,167 | operational and matched-null calibration only |
| SODB:Konieczny2022Interleukin | cluster_only_calibration | 1 | 505 | operational and matched-null calibration only |
| SODB:Lebrigand2022The | cluster_only_calibration | 1 | 902 | operational and matched-null calibration only |
| SODB:Melo2021Integrating | cluster_only_calibration | 1 | 3,007 | operational and matched-null calibration only |
| SODB:Merfish_Visp | cluster_only_calibration | 1 | 2,399 | operational and matched-null calibration only |
| SODB:Misra2021Characterizing | cluster_only_calibration | 1 | 959 | operational and matched-null calibration only |
| SODB:Pascual2021Dietary | cluster_only_calibration | 1 | 1,269 | operational and matched-null calibration only |
| SODB:Ratz2022Clonal | cluster_only_calibration | 1 | 3,264 | operational and matched-null calibration only |
| SODB:Vickovic2019high_update | cluster_only_calibration | 1 | 14,064 | operational and matched-null calibration only |
| SODB:Visium_Allen | cluster_only_calibration | 1 | 2,492 | operational and matched-null calibration only |
| SODB:Zhang2023Amolecularly_rawcount | cluster_only_calibration | 1 | 3,886 | operational and matched-null calibration only |
| SODB:backdahl2021spatial | cluster_only_calibration | 1 | 1,597 | operational and matched-null calibration only |
| SODB:bergenstrahle2021super | cluster_only_calibration | 1 | 2,361 | operational and matched-null calibration only |
| SODB:berglund2018spatial | cluster_only_calibration | 1 | 469 | operational and matched-null calibration only |
| SODB:chen2020spatial | cluster_only_calibration | 1 | 447 | operational and matched-null calibration only |
| SODB:chen2021decoding | cluster_only_calibration | 1 | 7,288 | operational and matched-null calibration only |
| SODB:fawkner2021spatiotemporal | cluster_only_calibration | 1 | 2,448 | operational and matched-null calibration only |
| SODB:guilliams2022spatial | cluster_only_calibration | 1 | 532 | operational and matched-null calibration only |
| SODB:hunter2021spatially | cluster_only_calibration | 1 | 2,393 | operational and matched-null calibration only |
| SODB:ji2020multimodal | cluster_only_calibration | 1 | 608 | operational and matched-null calibration only |
| SODB:kvastad2021the | cluster_only_calibration | 1 | 997 | operational and matched-null calibration only |
| SODB:liu2022spatiotemporal | cluster_only_calibration | 1 | 4,670 | operational and matched-null calibration only |
| SODB:mantri2021spatiotemporal | cluster_only_calibration | 1 | 747 | operational and matched-null calibration only |
| SODB:maynard2021trans | cluster_only_calibration | 1 | 2,908 | operational and matched-null calibration only |
| SODB:parigi2022the | cluster_only_calibration | 1 | 3,382 | operational and matched-null calibration only |
| SODB:rodriques2019slide | cluster_only_calibration | 1 | 3,760 | operational and matched-null calibration only |
| SODB:stickels2020highly | cluster_only_calibration | 1 | 9,545 | operational and matched-null calibration only |
| SODB:xia2019spatial | cluster_only_calibration | 1 | 606 | operational and matched-null calibration only |
| GSE202623 | label_bearing_validation | 2 | 33,760 | eligible for task-appropriate validation with label-evidence caveats |
| GSE240015 | label_bearing_validation | 1 | 3,910 | eligible for task-appropriate validation with label-evidence caveats |
| GSE245263 | label_bearing_validation | 1 | 2,158 | eligible for task-appropriate validation with label-evidence caveats |
| GSE263450 | label_bearing_validation | 1 | 36,521 | eligible for task-appropriate validation with label-evidence caveats |
| GSE273530 | label_bearing_validation | 1 | 8,976 | eligible for task-appropriate validation with label-evidence caveats |
| GSE273952 | label_bearing_validation | 1 | 5,000 | eligible for task-appropriate validation with label-evidence caveats |
| GSE278766 | label_bearing_validation | 1 | 32,011 | eligible for task-appropriate validation with label-evidence caveats |
| GSE279181 | label_bearing_validation | 1 | 11,677 | eligible for task-appropriate validation with label-evidence caveats |
| GSE280376 | label_bearing_validation | 1 | 92,321 | eligible for task-appropriate validation with label-evidence caveats |
| GSE282127 | label_bearing_validation | 1 | 53,108 | eligible for task-appropriate validation with label-evidence caveats |
| GSE284005 | label_bearing_validation | 2 | 34,350 | eligible for task-appropriate validation with label-evidence caveats |
| GSE291308 | label_bearing_validation | 1 | 17,655 | eligible for task-appropriate validation with label-evidence caveats |
| GSE292268 | label_bearing_validation | 1 | 28,166 | eligible for task-appropriate validation with label-evidence caveats |
| GSE294759 | label_bearing_validation | 1 | 44,137 | eligible for task-appropriate validation with label-evidence caveats |
| GSE301435 | label_bearing_validation | 1 | 57,937 | eligible for task-appropriate validation with label-evidence caveats |
| GSE302502 | label_bearing_validation | 1 | 23,570 | eligible for task-appropriate validation with label-evidence caveats |
| GSE305393 | label_bearing_validation | 1 | 19,039 | eligible for task-appropriate validation with label-evidence caveats |
| GSE307588 | label_bearing_validation | 1 | 3,713 | eligible for task-appropriate validation with label-evidence caveats |
| GSE308167 | label_bearing_validation | 1 | 11,775 | eligible for task-appropriate validation with label-evidence caveats |
| GSE308624 | label_bearing_validation | 1 | 18,032 | eligible for task-appropriate validation with label-evidence caveats |
| GSE308952 | label_bearing_validation | 1 | 3,720 | eligible for task-appropriate validation with label-evidence caveats |
| GSE310129 | label_bearing_validation | 1 | 22,522 | eligible for task-appropriate validation with label-evidence caveats |
| GSE311681 | label_bearing_validation | 1 | 33,574 | eligible for task-appropriate validation with label-evidence caveats |
| GSE317755 | label_bearing_validation | 1 | 3,188 | eligible for task-appropriate validation with label-evidence caveats |
| GSE325587 | label_bearing_validation | 1 | 20,386 | eligible for task-appropriate validation with label-evidence caveats |
| GSE326743 | label_bearing_validation | 1 | 64,284 | eligible for task-appropriate validation with label-evidence caveats |
| GSE327129 | label_bearing_validation | 1 | 7,303 | eligible for task-appropriate validation with label-evidence caveats |
| GSE327581 | label_bearing_validation | 2 | 16,371 | eligible for task-appropriate validation with label-evidence caveats |
| GSE328481 | label_bearing_validation | 1 | 15,000 | eligible for task-appropriate validation with label-evidence caveats |
| GSE330849 | label_bearing_validation | 1 | 52,701 | eligible for task-appropriate validation with label-evidence caveats |
| GSE333479 | label_bearing_validation | 1 | 20,448 | eligible for task-appropriate validation with label-evidence caveats |
| GSE333737 | label_bearing_validation | 2 | 24,222 | eligible for task-appropriate validation with label-evidence caveats |
| GSE336633 | label_bearing_validation | 1 | 75,580 | eligible for task-appropriate validation with label-evidence caveats |
| GSE337336 | label_bearing_validation | 1 | 20,000 | eligible for task-appropriate validation with label-evidence caveats |
| SODB:Allen2022Molecular_aging | label_bearing_validation | 1 | 8,596 | eligible for task-appropriate validation with label-evidence caveats |
| SODB:Allen2022Molecular_lps | label_bearing_validation | 1 | 8,840 | eligible for task-appropriate validation with label-evidence caveats |
| SODB:Booeshaghi2021Isoform | label_bearing_validation | 1 | 3,502 | eligible for task-appropriate validation with label-evidence caveats |
| SODB:Fang2022Conservation | label_bearing_validation | 1 | 11,648 | eligible for task-appropriate validation with label-evidence caveats |
| SODB:Marshall2022High_human | label_bearing_validation | 1 | 13,496 | eligible for task-appropriate validation with label-evidence caveats |
| SODB:Marshall2022High_mouse | label_bearing_validation | 1 | 8,746 | eligible for task-appropriate validation with label-evidence caveats |
| SODB:Shi2022Spatial | label_bearing_validation | 1 | 11,310 | eligible for task-appropriate validation with label-evidence caveats |
| SODB:Sun2021Integrating | label_bearing_validation | 1 | 5,831 | eligible for task-appropriate validation with label-evidence caveats |
| SODB:Wang2018Three_1k | label_bearing_validation | 1 | 872 | eligible for task-appropriate validation with label-evidence caveats |
| SODB:Wu2022spatial | label_bearing_validation | 1 | 8,102 | eligible for task-appropriate validation with label-evidence caveats |
| SODB:Zeng2023Integrative | label_bearing_validation | 1 | 11,199 | eligible for task-appropriate validation with label-evidence caveats |
| SODB:chen2021dissecting | label_bearing_validation | 1 | 8,711 | eligible for task-appropriate validation with label-evidence caveats |
| SODB:chen2022spatiotemporal | label_bearing_validation | 1 | 18,360 | eligible for task-appropriate validation with label-evidence caveats |
| SODB:codeluppi2018spatial | label_bearing_validation | 1 | 5,328 | eligible for task-appropriate validation with label-evidence caveats |
| SODB:eng2019transcriptome | label_bearing_validation | 1 | 1,826 | eligible for task-appropriate validation with label-evidence caveats |
| SODB:he2020integrating | label_bearing_validation | 1 | 2,000 | eligible for task-appropriate validation with label-evidence caveats |
| SODB:seqFISH_VISp | label_bearing_validation | 1 | 2,721 | eligible for task-appropriate validation with label-evidence caveats |
| SODB:wang2021easi | label_bearing_validation | 1 | 46,720 | eligible for task-appropriate validation with label-evidence caveats |
| SODB:wang2022high | label_bearing_validation | 1 | 8,589 | eligible for task-appropriate validation with label-evidence caveats |
| SODB:wei2022single | label_bearing_validation | 1 | 14,710 | eligible for task-appropriate validation with label-evidence caveats |
| SQUIDPY_IMC | label_bearing_validation | 1 | 1,744 | eligible for task-appropriate validation with label-evidence caveats |
| SQUIDPY_MERFISH | label_bearing_validation | 2 | 73,655 | eligible for task-appropriate validation with label-evidence caveats |
| SQUIDPY_MIBITOF | label_bearing_validation | 1 | 2,012 | eligible for task-appropriate validation with label-evidence caveats |
| SQUIDPY_SEQFISH | label_bearing_validation | 2 | 19,416 | eligible for task-appropriate validation with label-evidence caveats |
| SQUIDPY_SLIDESEQV2 | label_bearing_validation | 2 | 18,842 | eligible for task-appropriate validation with label-evidence caveats |
| SQUIDPY_VISIUM_FLUO | label_bearing_validation | 1 | 2,753 | eligible for task-appropriate validation with label-evidence caveats |
| SQUIDPY_VISIUM_HNE | label_bearing_validation | 1 | 2,688 | eligible for task-appropriate validation with label-evidence caveats |
