# Public Spatial Dataset Catalog

This catalog is an expansion layer for NicheTypeR validation. It is not
claimed as a completed benchmark. It records public GEO spatial-omics
datasets that appear to contain expression, coordinate and/or label evidence
and assigns readiness tiers for future ingestion.

- total GEO GSE candidates screened: 1,259
- high-priority candidates with automated score >= 7: 81
- prioritized catalog released with submission: 200 datasets

## Readiness Tiers

| tier | n |
|---|---:|
| screened_low_priority | 741 |
| tier4_candidate_manual_review | 415 |
| tier3_high_priority_manual_review | 62 |
| expanded_scale_validation | 29 |
| benchmark_ready_processed | 5 |
| downloaded_candidate | 5 |
| partial_download_candidate | 1 |
| manifest_only_candidate | 1 |

## Top 50 Prioritized Datasets

| rank | accession | tier | score | samples | size GB | h5ad | title |
|---:|---|---|---:|---:|---:|---|---|
| 1 | GSE240015 | benchmark_ready_processed | 8 | 2 | 0.87 | yes | Age-related epithelial defects limit thymic function and regeneration [visium] |
| 2 | GSE327581 | benchmark_ready_processed | 8 | 5 | 0.947 | yes | Single-cell spatial transcriptomic profiling of 3xTg-AD mouse brains following fecal micro |
| 3 | GSE333737 | benchmark_ready_processed | 6 | 12 | 60.1 | yes | MERFISH spatial transcriptomic profiling of extracellular matrix and vascular-associated p |
| 4 | GSE202623 | benchmark_ready_processed | 3 | 3 | 0 | no | Spatial Transcriptomics correlated Electron Microscopy [MERFISH] |
| 5 | GSE284005 | benchmark_ready_processed | 3 | 17 | 0 | no | A single-cell resolution spatial transcriptomics atlas of human multiple sclerosis lesion  |
| 6 | GSE263450 | expanded_scale_validation | 10 | 6 | 21 | yes | Spatial transcriptomic mapping of the mouse brain in chronic stress |
| 7 | GSE279181 | expanded_scale_validation | 8 | 18 | 12.9 | yes | Cell type mapping reveals tissue niches and interactions in subcortical multiple sclerosis |
| 8 | GSE333479 | expanded_scale_validation | 8 | 21 | 239 | yes | A unified spatial transcriptome profiling of ten mouse organs |
| 9 | GSE294759 | expanded_scale_validation | 8 | 9 | 114 | yes | Application of spatial transcriptomics across organoids for a high-resolution spatial whol |
| 10 | GSE308167 | expanded_scale_validation | 8 | 10 | 2.22 | yes | Integration of Imaging-based and Sequencing-based Spatial Omics Mapping on the Same Tissue |
| 11 | GSE301435 | expanded_scale_validation | 8 | 2 | 0.5 | yes | A parabrachial hub for the prioritization of survival behavior during pain |
| 12 | GSE330849 | expanded_scale_validation | 8 | 2 | 4.77 | yes | MERFISH spatial transcriptomic profiling of Sst+ interneurons in the postnatal mouse brain |
| 13 | GSE308952 | expanded_scale_validation | 8 | 1 | 8.5 | yes | Peripheral glia constitute a pro-reparative niche triggering skin wound healing [Spatial T |
| 14 | GSE273952 | expanded_scale_validation | 7 | 19 | 1.78 | no | GABA promotes resistance to immunotherapy of patients with TLS-positive tumors [Spatial Tr |
| 15 | GSE302502 | expanded_scale_validation | 7 | 12 | 179 | no | Spatial immune profiling defines a subset of human gliomas with functional tertiary lympho |
| 16 | GSE280376 | expanded_scale_validation | 7 | 8 | 18.9 | no | Spatiotemporal dynamics of the cardioimmune niche during lesion repair [spatial] |
| 17 | GSE311681 | expanded_scale_validation | 7 | 1 | 13.4 | no | An immunobiliary single-cell atlas resolves crosstalk between type 2 conventional dendriti |
| 18 | GSE278766 | expanded_scale_validation | 7 | 1 | 5.95 | no | Comparison of CosMx and GeoMx profiling performed on the same human kidney tissues [CosMx] |
| 19 | GSE291308 | expanded_scale_validation | 7 | 1 | 15.1 | no | Site-specific phosphorylation of ERα determines sex-dependent metabolic, reproductive, and |
| 20 | GSE336633 | expanded_scale_validation | 6 | 16 | 68.5 | yes | Spatial Transcriptomics of MHC Expression in Mauritian Cynomolgus Macaque Tissues |
| 21 | GSE317755 | expanded_scale_validation | 6 | 12 | 15 | yes | A spatial transcriptomics comparison of the adult versus metamorphosed axolotl brain |
| 22 | GSE327129 | expanded_scale_validation | 6 | 2 | 14.7 | yes | Subcellular mRNA localization patterns across tissues resolved with spatial transcriptomic |
| 23 | GSE310129 | expanded_scale_validation | 6 | 3 | 72.1 | yes | Spatial transcriptome sequencing of chicken and duck beaks |
| 24 | GSE328481 | expanded_scale_validation | 6 | 11 | 13.2 | yes | Uncovering ectopic GC-like niches for tumor reactive lymphocyte priming in lung adenocarci |
| 25 | GSE245263 | expanded_scale_validation | 6 | 1 | 4.27 | yes | Spatial transcriptomics of brains from tumor-bearing C57BL/6 mice |
| 26 | GSE282127 | expanded_scale_validation | 6 | 2 | 0 | yes | Spatial transcriptomics of P35 septum |
| 27 | GSE308624 | expanded_scale_validation | 6 | 71 | 0 | yes | Spatial and functional dissection of cancer-associated fibroblasts-mediated immune modulat |
| 28 | GSE325587 | expanded_scale_validation | 6 | 17 | 0 | yes | Spatial transcriptomics identifies IL-32 as a lipid droplet-associated cytokine linked to  |
| 29 | GSE273530 | expanded_scale_validation | 5 | 1 | 0 | no | Programmed cell death-1 receptor deficiency enhances CD30+ T regulatory cell function in M |
| 30 | GSE292268 | expanded_scale_validation | 3 | 2 | 0 | no | Spatial single-cell transcriptomics of MASLD-affected liver biopsy samples. |
| 31 | GSE305393 | expanded_scale_validation | 3 | 2 | 0 | no | Microbial signals in primary and metastatic brain tumors [CosMx] |
| 32 | GSE307588 | expanded_scale_validation | 3 | 25 | 0 | no | Spatial profiling of hypoxic injury in human kidney organoids |
| 33 | GSE326743 | expanded_scale_validation | 3 | 7 | 0 | no | Identity, ontogeny, and age-related changes in splenic white pulp macrophages in mouse and |
| 34 | GSE337336 | expanded_scale_validation | 3 | 16 | 0 | no | Genomic and spatial transcriptomics identify fibroblast-associated microenvironment in ear |
| 35 | GSE300613 | downloaded_candidate | 8 | 2 | 0.231 | yes | Spatial transcriptomics dataset of primary tumours from MDA-MB-231 xenograft model |
| 36 | GSE282124 | downloaded_candidate | 7 | 1 | 0.062 | no | Single-cell spatial transcriptomics of formalin-fixed, paraffin-embedded biopsies reveals  |
| 37 | GSE303162 | downloaded_candidate | 5 | 2 | 0.11 | no | A novel CAF population coordinates hyper-suppressive regulatory T cell recruitment and loc |
| 38 | GSE305735 | downloaded_candidate | 3 | 2 | 0 | no | Whole-transcriptome-scale isoform-resolved spatial imaging of single cells in tissues |
| 39 | GSE325911 | downloaded_candidate | 3 | 37 | 0 | no | Type-I Interferon drives T-cell responses to amyloid-beta in the central nervous system |
| 40 | GSE278614 | partial_download_candidate | 6 | 3 | 2.75 | yes | Single-Cell Spatial Mapping of Human Kidney Development Reveals Cellular Niches and Lineag |
| 41 | GSE307719 | manifest_only_candidate | 7 | 8 | 457 | no | Cellular and molecular signatures of the vascular microenvironment define the pre-metastat |
| 42 | GSE313918 | tier3_high_priority_manual_review | 8 | 246 | 21.2 | yes | Differential Cellular Mechanisms Underlie Language and Executive Decline in Amyotrophic La |
| 43 | GSE307215 | tier3_high_priority_manual_review | 8 | 104 | 7.97 | yes | Spatiotemporal Single-Cell Profiling Reveals T Cell Clonal Dynamics and Phenotypic Plastic |
| 44 | GSE236660 | tier3_high_priority_manual_review | 8 | 63 | 22 | yes | Effect of Aging on the Human Myometrium at Single-Cell Resolution |
| 45 | GSE260801 | tier3_high_priority_manual_review | 8 | 25 | 3.43 | yes | Spatially defined multicellular functional units in colorectal cancer revealed from single |
| 46 | GSE279507 | tier3_high_priority_manual_review | 8 | 5 | 0.685 | yes | Mapping the Evolution of Acinar cell derived Pancreatic Preneoplastic Lesions in a Mouse M |
| 47 | GSE216542 | tier3_high_priority_manual_review | 8 | 22 | 6 | yes | scRNA-seq, snATAC-seq, and spatial transcriptomics analysis of mammary glands of aged fema |
| 48 | GSE251926 | tier3_high_priority_manual_review | 8 | 27 | 75.4 | yes | Open-ST: High-resolution spatial transcriptomics in 3D |
| 49 | GSE290361 | tier3_high_priority_manual_review | 8 | 17 | 6.2 | yes | DynaST-seq: A Transcriptome-wide Spatio-temporal Approach for Profiling Gene Expression Dy |
| 50 | GSE269695 | tier3_high_priority_manual_review | 8 | 5 | 0.094 | yes | Patient-derived lymphomoids preserve the tumor architecture and allow testing response to  |

## Interpretation

The catalog is deliberately separated from benchmark results. A dataset is
counted as benchmark-ready only after expression, spatial coordinates, labels
and blocked validation groups are parsed and aligned. Candidate datasets can
support scale claims about data discovery, but not performance claims until
they pass that ingestion step.
