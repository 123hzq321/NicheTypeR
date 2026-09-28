# NicheTypeR GEO100 Expansion Progress

Updated: 2026-09-28 China Standard Time

## Verified scale

- Completed independent source datasets: **41**
- Completed benchmark configurations: **48**
- Preview configurations: **12**
- Expanded configurations: **36**
- Unique benchmark cells/spots across configurations: **1,070,222**
- Sources still needed for the 100-source target: **59**

Only datasets that completed expression, coordinate and label reconciliation plus a blocked benchmark are counted. GEO candidates, file lists, partially downloaded accessions and cluster-only metadata are excluded from this total.

## Added in this pass

| Accession | Tissue/platform | Validation unit | Cells | Labels | Marker F1 | Learned F1 | Random-graph F1 | Learned strict pass | CSAE strict pass |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| GSE326743 | human spleen, Xenium | 3 held-out samples | 64,284 | 30 | 0.5272 | 0.5303 | 0.5249 | no | no |
| GSE305393 | glioma and brain metastasis, CosMx | 73 held-out FOVs | 19,039 | 21 | 0.4149 | 0.4290 | 0.4287 | no | no |
| GSE291308 | mouse uterus, CosMx | 53 held-out FOVs | 17,655 | 8 | 0.6934 | 0.6852 | 0.6878 | no | no |
| GSE311681 | mouse liver, imaging spatial transcriptomics | 36 within-slide spatial blocks | 33,574 | 25 | 0.6230 | 0.6225 | 0.6191 | no | no |
| GSE292268 | human liver, CosMx | 127 held-out FOVs | 28,166 | 16 | 0.6219 | 0.6221 | 0.6193 | no | no |
| GSE278766 | human kidney, CosMx | 205 held-out FOVs | 32,011 | 13 | 0.6417 | 0.6446 | 0.6409 | no | no |

The six sources add **194,729** benchmark cells. `GSE311681` contains one physical specimen; its 36 groups are spatial blocks and must not be described as independent donors or slides.

## Latest additions

| Accession | Tissue/platform | Validation unit | Cells | Labels | Marker F1 | Learned F1 | Random-graph F1 | Learned strict pass | CSAE strict pass |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| GSE333479 | ten mouse organs, Stereo-seq bins | 5 held-out samples | 20,448 | 14 | 0.2893 | 0.2899 | 0.2919 | no | no |
| GSE279181 | human multiple-sclerosis brain, Visium | 18 held-out donors/slides | 11,677 | 9 | 0.3988 | 0.4080 | 0.4090 | no | no |
| GSE308167 | human lymphoma, DBiT/CODEX-aligned observations | 3 held-out samples | 11,775 | 11 | 0.3676 | 0.3581 | 0.3634 | no | no |
| GSE308952 | mouse wound skin, spatial transcriptomics | 28 within-slide blocks | 3,720 | 7 | 0.4143 | 0.4328 | 0.4222 | yes | no |
| GSE280376 | mouse heart, Xenium | 7 held-out slides | 92,321 | 65 | 0.0586 | 0.0571 | 0.0554 | no | no |
| GSE336633 | macaque lung, annotated spatial H5AD | 3 held-out whole samples | 75,580 | 34 | 0.2325 | 0.2305 | 0.2290 | no | no |

These six sources add **215,521** benchmark cells/spots. Their labels are not all equivalent forms of truth: GSE333479 uses external cell2location mappings, GSE279181 uses the argmax of author-provided cell-type proportions, GSE308167 contains CODEX-aligned conditional-expression observations, and GSE336633 uses author/model `predicted_labels`. They are external-annotation audit tasks, not independent gold-standard cell identities. GSE308952 contains one biological sample and therefore tests within-slide spatial transfer rather than donor generalization. GSE280376 has official mapped labels across seven slides.

## Aggregate evidence

- Learned-neighborhood passes the prespecified dataset-level strict guardrail in **6/48** configurations.
- Context-specific residual passes in **0/48** configurations.
- Expanded-only learned-neighborhood passes occur in **3/36** configurations:
  - `GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED`
  - `GEO_GSE263450_GENERIC_H5AD_EXPANDED`
  - `GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED`
- Expanded-only context-specific residual passes occur in **0/36** configurations.

Among the latest six datasets, GSE308952 adds one learned-neighborhood strict pass. The other five either fail to beat the expression baseline or remain too close to the random-graph/permuted-prior controls. The larger benchmark improves coverage and precision; it does not justify a universal efficacy claim.

## Ingestion improvements

- Added native 10x H5 Xenium ingestion with `annotations.csv + cells.parquet` joins.
- Added Matrix Market plus polygon-boundary centroids and cluster-name mapping.
- Added CosMx `metadata_for_seurat` support and composite cell-ID normalization.
- Added automatic recognition of gene-by-cell matrices whose columns use `cellID_FOV` rather than `FOV::cellID`.
- Added rejection of `Low quality`, `other` and unnamed one-letter clusters.
- Audited 102 remote metadata tables by streamed header inspection. Only 12 tables from 7 sources contained both a usable label field and coordinates.
- Added multi-file H5AD parsing for internal labels, sidecar annotations and composition matrices, with explicit annotation-evidence typing.
- Added an H5AD metadata audit covering 215 local files and a compatibility copier that removes only unsupported optional null-encoded `/uns` entries while recording source/output SHA256 hashes.
- Refreshed the NCBI GEO search on 2026-09-28: 1,259 GSE candidates were retrieved and 600 supplement file lists were screened.
- Fixed GEO sample URL construction for eight-digit GSM accessions by replacing the final three digits with `nnn` rather than slicing at a fixed character position.
- Rebuilt all call-level aggregates as exactly seven model calls per unique expanded cell/spot (7,175,826 rows for 1,025,118 units) and recomputed macro-F1 with `zero_division=0`; zero-recall labels are no longer silently omitted.

## Excluded candidates found in this pass

- `GSE263591`, `GSE287472`, `GSE274042`, `GSE277441` and `GSE292394` provide expression and coordinates but no supervised cell-type label.
- `GSE318797` contains only unnamed letter/numeric clusters and is not counted as cell-type validation.
- `GSE291539` contains numeric clusters and location categories rather than cell-type truth.
- `GSE333693` contains RCTD-derived labels but requires a multi-gigabyte Stereo-seq matrix; it remains a lower-priority external-annotation audit candidate.
- `GSE300434` provides Seurat spatial clusters rather than biological cell-type labels and is not counted in the primary cell-type benchmark.
- `GSE215305`, `GSE266933`, `GSE286452`, `GSE293043`, `GSE295222`, `GSE296429` and `GSE297667` contain spatial objects or coordinates but no usable semantic cell-type labels.
- Eleven inspected CosMx accessions (`GSE286935`, `GSE328460`, `GSE253439`, `GSE297091`, `GSE299786`, `GSE299368`, `GSE282721`, `GSE326904`, `GSE262162`, `GSE312698` and `GSE306111`) provide expression and coordinates but no semantic cell-type labels.
- `GSE348619` is a small Pyxa barcode demonstration; its six labels are synthetic `Barcode_A`--`Barcode_F` groups rather than biological cell types.
- `GSE324903` contains 740,571 spatial observations and coordinates but only 31 numeric Seurat clusters, with no semantic cell-type annotation.
- `GSE336159` contains six semantic immune annotations in single-cell metadata but no spatial coordinates, so it is not a spatial annotation benchmark.

## Reproducible outputs

- Queue: `HUNDRED_DATASET_EXPANSION_QUEUE.csv`
- Queue report: `HUNDRED_DATASET_EXPANSION_QUEUE_report.json`
- Expanded registry: `EXPANDED_SCALE_DATASETS.csv`
- Aggregate guardrail: `EXPANDED_SCALE_LEAN_BENCHMARK_guardrail.csv`
- Remote metadata audit: `REMOTE_METADATA_HEADER_AUDIT.csv`
- Local H5AD metadata audit: `LOCAL_H5AD_METADATA_AUDIT.csv`
- GSE336633 compatibility manifest: `GSE336633_CY1008_H5AD_COMPATIBILITY_MANIFEST.json`
- Updated parsers/auditors: `prepare_geo100_generic_dataset.py`, `audit_local_h5ad_metadata.py`, `make_h5ad_anndata_compatible.py`
- Metric rebuild script: `recompute_benchmark_metrics_from_calls.py`
- Per-dataset outputs: `GEO100_GSE*_LEAN_BENCHMARK_*`

## Current interpretation

The project has reached 41 independent public source IDs and 48 completed configurations, but it has not reached 100 sources. The larger benchmark strengthens the positioning of NicheTypeR as an annotation-audit framework: context can be informative in selected datasets, yet the present neighborhood and CSAE mechanisms do not consistently add specific predictive value over expression evidence and matched null controls.
