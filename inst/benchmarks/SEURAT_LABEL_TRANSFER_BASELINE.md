# Seurat Label Transfer External Baseline

This report adds a true external-method comparator to the NicheTypeR benchmark.
Seurat label transfer is run on the same preview expression matrices and on
the same held-out spatial blocks used by `MULTIDATASET_BLOCKED_BENCHMARK_calls.csv`.
Training cells come only from training spatial blocks; held-out FOV/slide blocks
are never used for reference labels.

This is not a claim that NicheTypeR reimplements Seurat. The output table is
stored in the same `cell_id`, `label`, `confidence` schema accepted by
`score_external_labels()`, so Seurat calls can be audited as external reference
evidence by NicheTypeR.

Protein-only stress-test datasets are skipped for this RNA label-transfer
baseline.

## Summary

| dataset | n | accuracy | macro-F1 | mean confidence | conflict rate | sec/fold |
|---|---:|---:|---:|---:|---:|---:|
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | 3910 | 0.6110 | 0.5146 | 0.6242 | 0.1394 | 4.0 |
| GEO_GSE284005_MERSCOPE_MS | 9393 | 0.4315 | 0.4229 | 0.4860 | 0.3224 | 5.0 |
| GEO_GSE327581_COSMX_AD_BRAIN | 5500 | 0.4936 | 0.4743 | 0.4631 | 0.3124 | 4.1 |
| GSE202623_LESION | 2485 | 0.9272 | 0.7347 | 0.9175 | 0.0133 | 2.1 |
| SQUIDPY_MERFISH | 4030 | 0.7529 | 0.7483 | 0.7143 | 0.0998 | 2.5 |
| SQUIDPY_SEQFISH | 5389 | 0.6717 | 0.5909 | 0.6723 | 0.1188 | 3.1 |
| SQUIDPY_SLIDESEQV2 | 2800 | 0.3646 | 0.3503 | 0.4000 | 0.4329 | 2.8 |
| SQUIDPY_VISIUM_FLUO | 2753 | 0.8463 | 0.8339 | 0.8145 | 0.0527 | 3.9 |
| SQUIDPY_VISIUM_HNE | 2688 | 0.8568 | 0.8482 | 0.7936 | 0.0543 | 3.4 |

## Paired Comparison vs Marker-Only

| dataset | accuracy diff | marker wrong, Seurat right | marker right, Seurat wrong |
|---|---:|---:|---:|
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | +0.2714 | 1425 | 364 |
| GEO_GSE284005_MERSCOPE_MS | -0.0681 | 1271 | 1911 |
| GEO_GSE327581_COSMX_AD_BRAIN | -0.0004 | 923 | 925 |
| GSE202623_LESION | +0.2229 | 653 | 99 |
| SQUIDPY_MERFISH | -0.0305 | 352 | 475 |
| SQUIDPY_SEQFISH | +0.0230 | 700 | 576 |
| SQUIDPY_SLIDESEQV2 | -0.0307 | 301 | 387 |
| SQUIDPY_VISIUM_FLUO | +0.2870 | 904 | 114 |
| SQUIDPY_VISIUM_HNE | +0.3419 | 1050 | 131 |

## Status

| dataset | fold | status | reason |
|---|---:|---|---|
| GSE202623_LESION | 1 | completed | n=367; elapsed=2.3 sec |
| GSE202623_LESION | 2 | completed | n=529; elapsed=2.1 sec |
| GSE202623_LESION | 3 | completed | n=574; elapsed=2.1 sec |
| GSE202623_LESION | 4 | completed | n=478; elapsed=2.1 sec |
| GSE202623_LESION | 5 | completed | n=537; elapsed=2.1 sec |
| SQUIDPY_SEQFISH | 1 | completed | n=1137; elapsed=3.3 sec |
| SQUIDPY_SEQFISH | 2 | completed | n=927; elapsed=3.0 sec |
| SQUIDPY_SEQFISH | 3 | completed | n=1279; elapsed=3.1 sec |
| SQUIDPY_SEQFISH | 4 | completed | n=921; elapsed=3.1 sec |
| SQUIDPY_SEQFISH | 5 | completed | n=1125; elapsed=3.1 sec |
| SQUIDPY_MERFISH | 1 | completed | n=730; elapsed=2.6 sec |
| SQUIDPY_MERFISH | 2 | completed | n=626; elapsed=2.4 sec |
| SQUIDPY_MERFISH | 3 | completed | n=623; elapsed=2.4 sec |
| SQUIDPY_MERFISH | 4 | completed | n=1044; elapsed=2.5 sec |
| SQUIDPY_MERFISH | 5 | completed | n=1007; elapsed=2.5 sec |
| SQUIDPY_SLIDESEQV2 | 1 | completed | n=497; elapsed=2.7 sec |
| SQUIDPY_SLIDESEQV2 | 2 | completed | n=616; elapsed=3.0 sec |
| SQUIDPY_SLIDESEQV2 | 3 | completed | n=493; elapsed=2.8 sec |
| SQUIDPY_SLIDESEQV2 | 4 | completed | n=520; elapsed=2.9 sec |
| SQUIDPY_SLIDESEQV2 | 5 | completed | n=674; elapsed=2.8 sec |
| SQUIDPY_MIBITOF | NA | skipped | non-RNA modality |
| SQUIDPY_VISIUM_FLUO | 1 | completed | n=548; elapsed=4.4 sec |
| SQUIDPY_VISIUM_FLUO | 2 | completed | n=547; elapsed=3.8 sec |
| SQUIDPY_VISIUM_FLUO | 3 | completed | n=515; elapsed=3.8 sec |
| SQUIDPY_VISIUM_FLUO | 4 | completed | n=576; elapsed=3.7 sec |
| SQUIDPY_VISIUM_FLUO | 5 | completed | n=567; elapsed=3.6 sec |
| SQUIDPY_VISIUM_HNE | 1 | completed | n=582; elapsed=3.6 sec |
| SQUIDPY_VISIUM_HNE | 2 | completed | n=563; elapsed=3.2 sec |
| SQUIDPY_VISIUM_HNE | 3 | completed | n=527; elapsed=3.2 sec |
| SQUIDPY_VISIUM_HNE | 4 | completed | n=534; elapsed=3.3 sec |
| SQUIDPY_VISIUM_HNE | 5 | completed | n=482; elapsed=3.4 sec |
| SQUIDPY_IMC | NA | skipped | non-RNA modality |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | 1 | completed | n=1131; elapsed=3.9 sec |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | 2 | completed | n=906; elapsed=3.9 sec |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | 3 | completed | n=410; elapsed=4.1 sec |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | 4 | completed | n=878; elapsed=3.9 sec |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | 5 | completed | n=585; elapsed=3.9 sec |
| GEO_GSE284005_MERSCOPE_MS | 1 | completed | n=2469; elapsed=5.0 sec |
| GEO_GSE284005_MERSCOPE_MS | 2 | completed | n=1603; elapsed=4.9 sec |
| GEO_GSE284005_MERSCOPE_MS | 3 | completed | n=1984; elapsed=5.0 sec |
| GEO_GSE284005_MERSCOPE_MS | 4 | completed | n=1605; elapsed=4.9 sec |
| GEO_GSE284005_MERSCOPE_MS | 5 | completed | n=1732; elapsed=5.2 sec |
| GEO_GSE327581_COSMX_AD_BRAIN | 1 | completed | n=839; elapsed=4.4 sec |
| GEO_GSE327581_COSMX_AD_BRAIN | 2 | completed | n=875; elapsed=4.1 sec |
| GEO_GSE327581_COSMX_AD_BRAIN | 3 | completed | n=718; elapsed=4.0 sec |
| GEO_GSE327581_COSMX_AD_BRAIN | 4 | completed | n=1583; elapsed=4.0 sec |
| GEO_GSE327581_COSMX_AD_BRAIN | 5 | completed | n=1485; elapsed=4.2 sec |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | 1 | skipped | too few test cells |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | 2 | failed | too few train or test cells |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | 3 | failed | too few train or test cells |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | 4 | skipped | too few test cells |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | 5 | skipped | too few test cells |

## Files

- `SEURAT_LABEL_TRANSFER_BASELINE_calls.csv`
- `SEURAT_LABEL_TRANSFER_BASELINE_summary.csv`
- `SEURAT_LABEL_TRANSFER_BASELINE_pairwise.csv`
- `SEURAT_LABEL_TRANSFER_BASELINE_status.csv`
