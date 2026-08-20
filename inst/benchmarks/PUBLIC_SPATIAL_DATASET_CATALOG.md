# Public Spatial Dataset Catalog

This catalog is an expansion layer for NicheTypeR validation. It is not
claimed as a completed benchmark. It records public GEO spatial-omics
datasets that appear to contain expression, coordinate and/or label evidence
and assigns readiness tiers for future ingestion.

- total GEO GSE candidates screened: 1,215
- high-priority candidates with automated score >= 7: 513
- prioritized catalog released with submission: 200 datasets

## Readiness Tiers

| tier | n |
|---|---:|
| tier3_high_priority_manual_review | 399 |
| tier4_candidate_manual_review | 394 |
| screened_low_priority | 306 |
| tier2_likely_benchmark_ready_files | 86 |
| tier1_likely_benchmark_ready_h5ad | 18 |
| benchmark_ready_processed | 5 |
| downloaded_candidate | 5 |
| manifest_only_candidate | 1 |
| partial_download_candidate | 1 |

## Top 50 Prioritized Datasets

| rank | accession | tier | score | samples | size GB | h5ad | title |
|---:|---|---|---:|---:|---:|---|---|
| 1 | GSE240015 | benchmark_ready_processed | 10 | 2 | 0.87 | yes | Age-related epithelial defects limit thymic function and regeneration [visium] |
| 2 | GSE327581 | benchmark_ready_processed | 10 | 5 | 0.947 | yes | Single-cell spatial transcriptomic profiling of 3xTg-AD mouse brains following fecal micro |
| 3 | GSE333737 | benchmark_ready_processed | 8 | 12 | 0 | yes | MERFISH spatial transcriptomic profiling of extracellular matrix and vascular-associated p |
| 4 | GSE202623 | benchmark_ready_processed | 5 | 3 | 0 | no | Spatial Transcriptomics correlated Electron Microscopy [MERFISH] |
| 5 | GSE284005 | benchmark_ready_processed | 5 | 17 | 0 | no | A single-cell resolution spatial transcriptomics atlas of human multiple sclerosis lesion  |
| 6 | GSE300613 | downloaded_candidate | 10 | 2 | 0.231 | yes | Spatial transcriptomics dataset of primary tumours from MDA-MB-231 xenograft model |
| 7 | GSE282124 | downloaded_candidate | 7 | 1 | 0 | no | Single-cell spatial transcriptomics of formalin-fixed, paraffin-embedded biopsies reveals  |
| 8 | GSE303162 | downloaded_candidate | 7 | 2 | 0 | no | A novel CAF population coordinates hyper-suppressive regulatory T cell recruitment and loc |
| 9 | GSE305735 | downloaded_candidate | 7 | 2 | 0 | no | Whole-transcriptome-scale isoform-resolved spatial imaging of single cells in tissues |
| 10 | GSE325911 | downloaded_candidate | 7 | 37 | 0 | no | Type-I Interferon drives T-cell responses to amyloid-beta in the central nervous system |
| 11 | GSE278614 | partial_download_candidate | 10 | 3 | 2.75 | yes | Single-Cell Spatial Mapping of Human Kidney Development Reveals Cellular Niches and Lineag |
| 12 | GSE307719 | manifest_only_candidate | 7 | 8 | 0 | no | Cellular and molecular signatures of the vascular microenvironment define the pre-metastat |
| 13 | GSE249405 | tier1_likely_benchmark_ready_h5ad | 10 | 38 | 14.3 | yes | Spatial mapping of RNA turnover kinetics in the mouse brain |
| 14 | GSE314765 | tier1_likely_benchmark_ready_h5ad | 10 | 32 | 41.8 | yes | Novel Acinar Metaplastic States Uncovered in Exocrine Pancreas Disease |
| 15 | GSE333479 | tier1_likely_benchmark_ready_h5ad | 10 | 21 | 239 | yes | A unified spatial transcriptome profiling of ten mouse organs |
| 16 | GSE336633 | tier1_likely_benchmark_ready_h5ad | 10 | 16 | 68.5 | yes | Spatial Transcriptomics of MHC Expression in Mauritian Cynomolgus Macaque Tissues |
| 17 | GSE306852 | tier1_likely_benchmark_ready_h5ad | 10 | 13 | 60 | yes | Spatial Analysis of T Cell Clonality in Autoimmune Kidney Disease Using TRV Probes |
| 18 | GSE279507 | tier1_likely_benchmark_ready_h5ad | 10 | 5 | 0.685 | yes | Mapping the Evolution of Acinar cell derived Pancreatic Preneoplastic Lesions in a Mouse M |
| 19 | GSE249752 | tier1_likely_benchmark_ready_h5ad | 10 | 4 | 3.05 | yes | Age-related epithelial defects limit thymic function and regeneration [single cell; Foxn1L |
| 20 | GSE249753 | tier1_likely_benchmark_ready_h5ad | 10 | 3 | 2.94 | yes | Age-related epithelial defects limit thymic function and regeneration [single cell; Foxn1L |
| 21 | GSE290367 | tier1_likely_benchmark_ready_h5ad | 10 | 90 | 56.4 | yes | Single-cell multiomic integration identifies widespread, cell-type resolved fetal reactiva |
| 22 | GSE249398 | tier1_likely_benchmark_ready_h5ad | 10 | 18 | 4.34 | yes | Spatial mapping of RNA turnover kinetics in the mouse brain [scNT-seq2] |
| 23 | GSE316007 | tier1_likely_benchmark_ready_h5ad | 10 | 30 | 1.2 | yes | Single-cell sequencing and spatial transcriptomics revealed that the coacervate–cell–drug  |
| 24 | GSE211785 | tier1_likely_benchmark_ready_h5ad | 10 | 80 | 2.48 | yes | Spatially resolved human kidney multi-omics single cell atlas highlights the key role of f |
| 25 | GSE290361 | tier1_likely_benchmark_ready_h5ad | 10 | 17 | 6.2 | yes | DynaST-seq: A Transcriptome-wide Spatio-temporal Approach for Profiling Gene Expression Dy |
| 26 | GSE281096 | tier1_likely_benchmark_ready_h5ad | 10 | 6 | 0.272 | yes | Single-cell and spatial transcriptomics identify COL6A3 as a prognostic biomarker in undif |
| 27 | GSE240016 | tier1_likely_benchmark_ready_h5ad | 10 | 29 | 0 | yes | Age-related epithelial defects limit thymic function and regeneration [single cell] |
| 28 | GSE240271 | tier1_likely_benchmark_ready_h5ad | 10 | 8 | 0 | yes | High-resolution spatial transcriptomics of hormone-induced ovulation in mice |
| 29 | GSE282127 | tier1_likely_benchmark_ready_h5ad | 10 | 2 | 0 | yes | Spatial transcriptomics of P35 septum |
| 30 | GSE325587 | tier1_likely_benchmark_ready_h5ad | 10 | 17 | 0 | yes | Spatial transcriptomics identifies IL-32 as a lipid droplet-associated cytokine linked to  |
| 31 | GSE307403 | tier2_likely_benchmark_ready_files | 9 | 63 | 5.59 | no | Schizophrenia-linked gene expression changes across cortical layers and cellular microenvi |
| 32 | GSE328048 | tier2_likely_benchmark_ready_files | 9 | 116 | 15.9 | no | Single-cell transcriptome reveals keratinocyte subclusters that contribute to altered diff |
| 33 | GSE300146 | tier2_likely_benchmark_ready_files | 9 | 56 | 430 | no | Single-cell multidimensional profiling of tumor cell heterogeneity in supratentorial epend |
| 34 | GSE312932 | tier2_likely_benchmark_ready_files | 9 | 10 | 65.6 | no | Spatial analyses of early, untreated SSc skin identify a proinflammatory vascular niche of |
| 35 | GSE250346 | tier2_likely_benchmark_ready_files | 9 | 45 | 351 | no | Image-based spatial transcriptomics identifies molecular niche dysregulation associated wi |
| 36 | GSE297945 | tier2_likely_benchmark_ready_files | 9 | 34 | 150 | no | A spatial transcriptomic atlas of acute neonatal lung injury across development and diseas |
| 37 | GSE307404 | tier2_likely_benchmark_ready_files | 9 | 24 | 468 | no | Schizophrenia-linked gene expression changes across cortical layers and cellular microenvi |
| 38 | GSE299494 | tier2_likely_benchmark_ready_files | 9 | 14 | 21.4 | no | Spatial transcriptomic sequencing of fresh frozen canine osteosarcoma tumor samples |
| 39 | GSE176092 | tier2_likely_benchmark_ready_files | 9 | 1118 | 1.64 | no | Spatiotemporal transcriptome analysis reveals critical roles for mechano-sensing genes at  |
| 40 | GSE295974 | tier2_likely_benchmark_ready_files | 9 | 64 | 3.52 | no | Single-cell multi-omics reveal coordinated neoplastic and immune remodeling following KRAS |
| 41 | GSE302502 | tier2_likely_benchmark_ready_files | 9 | 12 | 179 | no | Spatial immune profiling defines a subset of human gliomas with functional tertiary lympho |
| 42 | GSE311100 | tier2_likely_benchmark_ready_files | 9 | 13 | 0.565 | no | Decoding the Cell-Type and Spatial Roles of H19 in Cholestatic Liver Injury Through Single |
| 43 | GSE246611 | tier2_likely_benchmark_ready_files | 9 | 88 | 0.946 | no | An integrated toolkit for the analysis of synthetic cellular barcodes in the genome and tr |
| 44 | GSE311383 | tier2_likely_benchmark_ready_files | 9 | 3 | 20.4 | no | High-resolution spatial transcriptomics of human liver with VisiumHD |
| 45 | GSE301720 | tier2_likely_benchmark_ready_files | 9 | 8 | 0.855 | no | Integrated single-cell and spatial analysis identifies context-dependent myeloid-T cell in |
| 46 | GSE318590 | tier2_likely_benchmark_ready_files | 9 | 8 | 9.76 | no | Spatial transcriptomics data of the wild-type and App NL-G-F mouse posterior cortex |
| 47 | GSE300023 | tier2_likely_benchmark_ready_files | 9 | 8 | 0.685 | no | Multi-omics uncovers the immune landscape and molecular signatures associated with antibod |
| 48 | GSE173651 | tier2_likely_benchmark_ready_files | 9 | 6 | 0.226 | no | Single-cell and spatial transcriptomic analysis of homeostatic adult human skin |
| 49 | GSE336556 | tier2_likely_benchmark_ready_files | 9 | 9 | 31.2 | no | Spatial transcriptomics reveals differences in bronchus-associated lymphoid tissue composi |
| 50 | GSE297388 | tier2_likely_benchmark_ready_files | 9 | 8 | 1.43 | no | Spatial transcriptomics and scRNA-sequencing on gastrocnemius muscle form B6-mdx and D2-md |

## Interpretation

The catalog is deliberately separated from benchmark results. A dataset is
counted as benchmark-ready only after expression, spatial coordinates, labels
and blocked validation groups are parsed and aligned. Candidate datasets can
support scale claims about data discovery, but not performance claims until
they pass that ingestion step.
