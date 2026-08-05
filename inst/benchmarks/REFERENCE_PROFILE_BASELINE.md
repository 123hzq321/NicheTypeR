# Reference-Profile Baseline Add-On

This add-on benchmark adds a dependency-free reference-profile baseline
to the existing blocked 12-dataset benchmark. Label centroids are learned
inside training spatial blocks and scored on held-out blocks by cosine
similarity. This is a lightweight reference-style comparator, not a claim
that NicheTypeR reimplements SingleR, Seurat label transfer, CellTypist or
scmap.

Models:

- `reference_profile`: reference centroid similarity only
- `marker_reference_profile`: fixed fusion of marker and reference evidence
- `reference_profile_learned_neighborhood`: reference evidence audited with a learned neighborhood prior

## Summary

| dataset | model | accuracy | macro-F1 | conflict rate |
|---|---|---:|---:|---:|
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_reference_profile | 0.3939 | 0.3318 | 0.7685 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | 0.3621 | 0.3008 | 0.7560 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile_learned_neighborhood | 0.3604 | 0.2961 | 0.8192 |
| GEO_GSE284005_MERSCOPE_MS | marker_reference_profile | 0.4289 | 0.4062 | 0.6432 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile | 0.3460 | 0.3365 | 0.4417 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile_learned_neighborhood | 0.3421 | 0.3227 | 0.6228 |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_reference_profile | 0.4791 | 0.4614 | 0.6582 |
| GEO_GSE327581_COSMX_AD_BRAIN | reference_profile | 0.2615 | 0.2427 | 0.7204 |
| GEO_GSE327581_COSMX_AD_BRAIN | reference_profile_learned_neighborhood | 0.2747 | 0.2411 | 0.8445 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | marker_reference_profile | 0.7696 | 0.7671 | 0.1567 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | reference_profile | 0.7704 | 0.7683 | 0.1583 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | reference_profile_learned_neighborhood | 0.7254 | 0.7219 | 0.6229 |
| GSE202623_LESION | marker_reference_profile | 0.6612 | 0.5490 | 0.4805 |
| GSE202623_LESION | reference_profile | 0.5127 | 0.4030 | 0.4620 |
| GSE202623_LESION | reference_profile_learned_neighborhood | 0.5441 | 0.4169 | 0.6499 |
| SQUIDPY_IMC | marker_reference_profile | 0.4106 | 0.4160 | 0.6204 |
| SQUIDPY_IMC | reference_profile | 0.3985 | 0.3620 | 0.6302 |
| SQUIDPY_IMC | reference_profile_learned_neighborhood | 0.3928 | 0.3604 | 0.7403 |
| SQUIDPY_MERFISH | marker_reference_profile | 0.7256 | 0.6641 | 0.2109 |
| SQUIDPY_MERFISH | reference_profile | 0.7007 | 0.7271 | 0.1422 |
| SQUIDPY_MERFISH | reference_profile_learned_neighborhood | 0.7169 | 0.6991 | 0.3940 |
| SQUIDPY_MIBITOF | marker_reference_profile | 0.5631 | 0.5238 | 0.3260 |
| SQUIDPY_MIBITOF | reference_profile | 0.5517 | 0.5064 | 0.4314 |
| SQUIDPY_MIBITOF | reference_profile_learned_neighborhood | 0.5293 | 0.4831 | 0.5716 |
| SQUIDPY_SEQFISH | marker_reference_profile | 0.6407 | 0.5739 | 0.4053 |
| SQUIDPY_SEQFISH | reference_profile | 0.5611 | 0.5216 | 0.3477 |
| SQUIDPY_SEQFISH | reference_profile_learned_neighborhood | 0.5890 | 0.5559 | 0.5417 |
| SQUIDPY_SLIDESEQV2 | marker_reference_profile | 0.3832 | 0.3493 | 0.6257 |
| SQUIDPY_SLIDESEQV2 | reference_profile | 0.3154 | 0.2621 | 0.5721 |
| SQUIDPY_SLIDESEQV2 | reference_profile_learned_neighborhood | 0.3121 | 0.2565 | 0.6496 |
| SQUIDPY_VISIUM_FLUO | marker_reference_profile | 0.5714 | 0.5019 | 0.4679 |
| SQUIDPY_VISIUM_FLUO | reference_profile | 0.5358 | 0.4835 | 0.5151 |
| SQUIDPY_VISIUM_FLUO | reference_profile_learned_neighborhood | 0.5271 | 0.4849 | 0.6302 |
| SQUIDPY_VISIUM_HNE | marker_reference_profile | 0.5692 | 0.5344 | 0.5699 |
| SQUIDPY_VISIUM_HNE | reference_profile | 0.5874 | 0.5614 | 0.6518 |
| SQUIDPY_VISIUM_HNE | reference_profile_learned_neighborhood | 0.6094 | 0.5893 | 0.7020 |

## Paired Comparisons vs Marker-Only

| dataset | comparator | accuracy diff | marker wrong, comparator right | marker right, comparator wrong | McNemar p |
|---|---|---:|---:|---:|---:|
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_reference_profile | +0.0542 | 475 | 263 | 5.255e-15 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | +0.0225 | 776 | 688 | 0.02295 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile_learned_neighborhood | +0.0207 | 800 | 719 | 0.04007 |
| GEO_GSE284005_MERSCOPE_MS | marker_reference_profile | -0.0707 | 828 | 1492 | 1.094e-43 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile | -0.1536 | 926 | 2369 | 5.23e-144 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile_learned_neighborhood | -0.1576 | 915 | 2395 | 6.088e-151 |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_reference_profile | -0.0149 | 296 | 378 | 0.001788 |
| GEO_GSE327581_COSMX_AD_BRAIN | reference_profile | -0.2325 | 345 | 1624 | 7.599e-198 |
| GEO_GSE327581_COSMX_AD_BRAIN | reference_profile_learned_neighborhood | -0.2193 | 379 | 1585 | 8.587e-175 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | marker_reference_profile | +0.0100 | 67 | 43 | 0.02785 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | reference_profile | +0.0108 | 119 | 93 | 0.08574 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | reference_profile_learned_neighborhood | -0.0342 | 126 | 208 | 8.46e-06 |
| GSE202623_LESION | marker_reference_profile | -0.0431 | 72 | 179 | 1.085e-11 |
| GSE202623_LESION | reference_profile | -0.1915 | 79 | 555 | 5.301e-89 |
| GSE202623_LESION | reference_profile_learned_neighborhood | -0.1602 | 136 | 534 | 1.327e-56 |
| SQUIDPY_IMC | marker_reference_profile | +0.0178 | 80 | 49 | 0.008008 |
| SQUIDPY_IMC | reference_profile | +0.0057 | 124 | 114 | 0.5597 |
| SQUIDPY_IMC | reference_profile_learned_neighborhood | +0.0000 | 120 | 120 | 1 |
| SQUIDPY_MERFISH | marker_reference_profile | -0.0578 | 101 | 334 | 3.456e-30 |
| SQUIDPY_MERFISH | reference_profile | -0.0826 | 128 | 461 | 4.403e-45 |
| SQUIDPY_MERFISH | reference_profile_learned_neighborhood | -0.0665 | 170 | 438 | 3.267e-28 |
| SQUIDPY_MIBITOF | marker_reference_profile | +0.0134 | 87 | 60 | 0.03165 |
| SQUIDPY_MIBITOF | reference_profile | +0.0020 | 162 | 158 | 0.8668 |
| SQUIDPY_MIBITOF | reference_profile_learned_neighborhood | -0.0204 | 159 | 200 | 0.03462 |
| SQUIDPY_SEQFISH | marker_reference_profile | -0.0080 | 407 | 450 | 0.1513 |
| SQUIDPY_SEQFISH | reference_profile | -0.0876 | 478 | 950 | 2.69e-36 |
| SQUIDPY_SEQFISH | reference_profile_learned_neighborhood | -0.0598 | 516 | 838 | 1.872e-18 |
| SQUIDPY_SLIDESEQV2 | marker_reference_profile | -0.0121 | 169 | 203 | 0.08695 |
| SQUIDPY_SLIDESEQV2 | reference_profile | -0.0800 | 252 | 476 | 8.025e-17 |
| SQUIDPY_SLIDESEQV2 | reference_profile_learned_neighborhood | -0.0832 | 258 | 491 | 1.27e-17 |
| SQUIDPY_VISIUM_FLUO | marker_reference_profile | +0.0120 | 130 | 97 | 0.03345 |
| SQUIDPY_VISIUM_FLUO | reference_profile | -0.0236 | 219 | 284 | 0.004276 |
| SQUIDPY_VISIUM_FLUO | reference_profile_learned_neighborhood | -0.0323 | 257 | 346 | 0.0003313 |
| SQUIDPY_VISIUM_HNE | marker_reference_profile | +0.0543 | 204 | 58 | 3.152e-20 |
| SQUIDPY_VISIUM_HNE | reference_profile | +0.0725 | 415 | 220 | 8.519e-15 |
| SQUIDPY_VISIUM_HNE | reference_profile_learned_neighborhood | +0.0945 | 458 | 204 | 2.32e-23 |

## Best Reference-Style Add-On Per Dataset

| dataset | best model | accuracy | macro-F1 |
|---|---|---:|---:|
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_reference_profile | 0.3939 | 0.3318 |
| GEO_GSE284005_MERSCOPE_MS | marker_reference_profile | 0.4289 | 0.4062 |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_reference_profile | 0.4791 | 0.4614 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | reference_profile | 0.7704 | 0.7683 |
| GSE202623_LESION | marker_reference_profile | 0.6612 | 0.5490 |
| SQUIDPY_IMC | marker_reference_profile | 0.4106 | 0.4160 |
| SQUIDPY_MERFISH | reference_profile | 0.7007 | 0.7271 |
| SQUIDPY_MIBITOF | marker_reference_profile | 0.5631 | 0.5238 |
| SQUIDPY_SEQFISH | marker_reference_profile | 0.6407 | 0.5739 |
| SQUIDPY_SLIDESEQV2 | marker_reference_profile | 0.3832 | 0.3493 |
| SQUIDPY_VISIUM_FLUO | marker_reference_profile | 0.5714 | 0.5019 |
| SQUIDPY_VISIUM_HNE | reference_profile_learned_neighborhood | 0.6094 | 0.5893 |