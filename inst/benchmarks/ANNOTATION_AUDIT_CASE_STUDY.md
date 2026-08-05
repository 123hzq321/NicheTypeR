# Annotation Audit Case Study

This report translates per-cell benchmark calls into audit-style cases.
A `context_rescue` is a held-out cell or spot where marker-only annotation
is wrong but a comparator that adds reference or context evidence is
correct. A `context_harm` is the opposite: marker-only is correct but the
comparator changes the call to an incorrect label.

The point is not to claim universal accuracy gains. The point is to show
where NicheTypeR can surface actionable annotation conflicts and where
context evidence should be treated cautiously.

## Net Rescue Summary

| dataset | comparator | rescue | harm | net | rescue rate | harm rate |
|---|---|---:|---:|---:|---:|---:|
| SQUIDPY_VISIUM_HNE | marker_context_specific_neighborhood | 195 | 112 | +83 | 0.0725 | 0.0417 |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_context_specific_neighborhood | 144 | 88 | +56 | 0.0262 | 0.0160 |
| SQUIDPY_VISIUM_FLUO | marker_context_specific_neighborhood | 46 | 20 | +26 | 0.0167 | 0.0073 |
| SQUIDPY_SEQFISH | marker_context_specific_neighborhood | 48 | 29 | +19 | 0.0089 | 0.0054 |
| SQUIDPY_IMC | marker_context_specific_neighborhood | 41 | 23 | +18 | 0.0235 | 0.0132 |
| GEO_GSE284005_MERSCOPE_MS | marker_context_specific_neighborhood | 170 | 156 | +14 | 0.0181 | 0.0166 |
| SQUIDPY_MERFISH | marker_context_specific_neighborhood | 33 | 21 | +12 | 0.0082 | 0.0052 |
| GSE202623_LESION | marker_context_specific_neighborhood | 32 | 22 | +10 | 0.0129 | 0.0089 |
| SQUIDPY_SLIDESEQV2 | marker_context_specific_neighborhood | 27 | 22 | +5 | 0.0096 | 0.0079 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | marker_context_specific_neighborhood | 11 | 15 | -4 | 0.0046 | 0.0063 |
| SQUIDPY_MIBITOF | marker_context_specific_neighborhood | 25 | 36 | -11 | 0.0124 | 0.0179 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_context_specific_neighborhood | 32 | 57 | -25 | 0.0082 | 0.0146 |
| SQUIDPY_VISIUM_FLUO | marker_learned_neighborhood | 222 | 61 | +161 | 0.0806 | 0.0222 |
| SQUIDPY_VISIUM_HNE | marker_learned_neighborhood | 158 | 59 | +99 | 0.0588 | 0.0219 |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | 203 | 138 | +65 | 0.0369 | 0.0251 |
| SQUIDPY_SEQFISH | marker_learned_neighborhood | 148 | 90 | +58 | 0.0275 | 0.0167 |
| GSE202623_LESION | marker_learned_neighborhood | 71 | 39 | +32 | 0.0286 | 0.0157 |
| SQUIDPY_MERFISH | marker_learned_neighborhood | 36 | 21 | +15 | 0.0089 | 0.0052 |
| GEO_GSE284005_MERSCOPE_MS | marker_learned_neighborhood | 149 | 137 | +12 | 0.0159 | 0.0146 |
| SQUIDPY_SLIDESEQV2 | marker_learned_neighborhood | 6 | 4 | +2 | 0.0021 | 0.0014 |
| SQUIDPY_IMC | marker_learned_neighborhood | 26 | 28 | -2 | 0.0149 | 0.0161 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | marker_learned_neighborhood | 16 | 19 | -3 | 0.0067 | 0.0079 |
| SQUIDPY_MIBITOF | marker_learned_neighborhood | 23 | 33 | -10 | 0.0114 | 0.0164 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_learned_neighborhood | 217 | 265 | -48 | 0.0555 | 0.0678 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_reference_profile | 475 | 263 | +212 | 0.1215 | 0.0673 |
| SQUIDPY_VISIUM_HNE | marker_reference_profile | 204 | 58 | +146 | 0.0759 | 0.0216 |
| SQUIDPY_VISIUM_FLUO | marker_reference_profile | 130 | 97 | +33 | 0.0472 | 0.0352 |
| SQUIDPY_IMC | marker_reference_profile | 80 | 49 | +31 | 0.0459 | 0.0281 |
| SQUIDPY_MIBITOF | marker_reference_profile | 87 | 60 | +27 | 0.0432 | 0.0298 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | marker_reference_profile | 33 | 16 | +17 | 0.0305 | 0.0148 |
| SQUIDPY_SLIDESEQV2 | marker_reference_profile | 169 | 203 | -34 | 0.0604 | 0.0725 |
| SQUIDPY_SEQFISH | marker_reference_profile | 407 | 450 | -43 | 0.0755 | 0.0835 |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_reference_profile | 296 | 378 | -82 | 0.0538 | 0.0687 |
| GSE202623_LESION | marker_reference_profile | 72 | 179 | -107 | 0.0290 | 0.0720 |
| SQUIDPY_MERFISH | marker_reference_profile | 101 | 334 | -233 | 0.0251 | 0.0829 |
| GEO_GSE284005_MERSCOPE_MS | marker_reference_profile | 828 | 1492 | -664 | 0.0882 | 0.1588 |
| SQUIDPY_VISIUM_HNE | marker_spatial_smoothing | 194 | 45 | +149 | 0.0722 | 0.0167 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_spatial_smoothing | 133 | 60 | +73 | 0.0340 | 0.0153 |
| SQUIDPY_VISIUM_FLUO | marker_spatial_smoothing | 105 | 42 | +63 | 0.0381 | 0.0153 |
| SQUIDPY_SEQFISH | marker_spatial_smoothing | 58 | 20 | +38 | 0.0108 | 0.0037 |
| GEO_GSE284005_MERSCOPE_MS | marker_spatial_smoothing | 188 | 153 | +35 | 0.0200 | 0.0163 |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_spatial_smoothing | 64 | 42 | +22 | 0.0116 | 0.0076 |
| SQUIDPY_MERFISH | marker_spatial_smoothing | 51 | 35 | +16 | 0.0127 | 0.0087 |
| SQUIDPY_IMC | marker_spatial_smoothing | 57 | 42 | +15 | 0.0327 | 0.0241 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | marker_spatial_smoothing | 18 | 16 | +2 | 0.0075 | 0.0067 |
| SQUIDPY_SLIDESEQV2 | marker_spatial_smoothing | 27 | 27 | +0 | 0.0096 | 0.0096 |
| GSE202623_LESION | marker_spatial_smoothing | 10 | 11 | -1 | 0.0040 | 0.0044 |
| SQUIDPY_MIBITOF | marker_spatial_smoothing | 29 | 37 | -8 | 0.0144 | 0.0184 |
| SQUIDPY_VISIUM_HNE | reference_profile | 415 | 220 | +195 | 0.1544 | 0.0818 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | 776 | 688 | +88 | 0.1985 | 0.1760 |
| SQUIDPY_IMC | reference_profile | 124 | 114 | +10 | 0.0711 | 0.0654 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | reference_profile | 45 | 37 | +8 | 0.0413 | 0.0340 |
| SQUIDPY_MIBITOF | reference_profile | 162 | 158 | +4 | 0.0805 | 0.0785 |
| SQUIDPY_VISIUM_FLUO | reference_profile | 219 | 284 | -65 | 0.0795 | 0.1032 |
| SQUIDPY_SLIDESEQV2 | reference_profile | 252 | 476 | -224 | 0.0900 | 0.1700 |
| SQUIDPY_MERFISH | reference_profile | 128 | 461 | -333 | 0.0318 | 0.1144 |
| SQUIDPY_SEQFISH | reference_profile | 478 | 950 | -472 | 0.0887 | 0.1763 |
| GSE202623_LESION | reference_profile | 79 | 555 | -476 | 0.0318 | 0.2233 |
| GEO_GSE327581_COSMX_AD_BRAIN | reference_profile | 345 | 1624 | -1279 | 0.0627 | 0.2953 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile | 926 | 2369 | -1443 | 0.0986 | 0.2522 |
| SQUIDPY_VISIUM_HNE | reference_profile_learned_neighborhood | 458 | 204 | +254 | 0.1704 | 0.0759 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile_learned_neighborhood | 800 | 719 | +81 | 0.2046 | 0.1839 |
| SQUIDPY_IMC | reference_profile_learned_neighborhood | 120 | 120 | +0 | 0.0688 | 0.0688 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | reference_profile_learned_neighborhood | 39 | 62 | -23 | 0.0495 | 0.0787 |
| SQUIDPY_MIBITOF | reference_profile_learned_neighborhood | 159 | 200 | -41 | 0.0790 | 0.0994 |
| SQUIDPY_VISIUM_FLUO | reference_profile_learned_neighborhood | 257 | 346 | -89 | 0.0934 | 0.1257 |
| SQUIDPY_SLIDESEQV2 | reference_profile_learned_neighborhood | 258 | 491 | -233 | 0.0921 | 0.1754 |
| SQUIDPY_MERFISH | reference_profile_learned_neighborhood | 170 | 438 | -268 | 0.0422 | 0.1087 |
| SQUIDPY_SEQFISH | reference_profile_learned_neighborhood | 516 | 838 | -322 | 0.0958 | 0.1555 |
| GSE202623_LESION | reference_profile_learned_neighborhood | 136 | 534 | -398 | 0.0547 | 0.2149 |
| GEO_GSE327581_COSMX_AD_BRAIN | reference_profile_learned_neighborhood | 379 | 1585 | -1206 | 0.0689 | 0.2882 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile_learned_neighborhood | 915 | 2395 | -1480 | 0.0974 | 0.2550 |

## Highest Net Rescue Settings

| dataset | comparator | net rescue minus harm | guardrail interpretation |
|---|---|---:|---|
| SQUIDPY_VISIUM_HNE | reference_profile_learned_neighborhood | +254 | context signal is not specific under null controls |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_reference_profile | +212 | simple spatial smoothing beats marker and random smoothing |
| SQUIDPY_VISIUM_HNE | reference_profile | +195 | context signal is not specific under null controls |
| SQUIDPY_VISIUM_FLUO | marker_learned_neighborhood | +161 | simple spatial smoothing beats marker and random smoothing |
| SQUIDPY_VISIUM_HNE | marker_spatial_smoothing | +149 | context signal is not specific under null controls |
| SQUIDPY_VISIUM_HNE | marker_reference_profile | +146 | context signal is not specific under null controls |
| SQUIDPY_VISIUM_HNE | marker_learned_neighborhood | +99 | context signal is not specific under null controls |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | +88 | simple spatial smoothing beats marker and random smoothing |
| SQUIDPY_VISIUM_HNE | marker_context_specific_neighborhood | +83 | context signal is not specific under null controls |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile_learned_neighborhood | +81 | simple spatial smoothing beats marker and random smoothing |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_spatial_smoothing | +73 | simple spatial smoothing beats marker and random smoothing |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | +65 | learned neighborhood beats marker and null controls |

## Example Audit Events

| dataset | comparator | change | truth | marker label | comparator label | marker conf. | comparator conf. |
|---|---|---|---|---|---|---:|---:|
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | changed_but_still_wrong | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_6 | d0_18mo::leiden_1.0_3 | 0.320 | 0.900 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | changed_but_still_wrong | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_4 | d0_18mo::leiden_1.0_3 | 0.355 | 0.875 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | changed_but_still_wrong | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_4 | d0_18mo::leiden_1.0_3 | 0.325 | 0.853 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | changed_but_still_wrong | d0_18mo::leiden_1.0_4 | d0_18mo::leiden_1.0_6 | d0_02mo::leiden_1.0_1 | 0.466 | 0.782 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | changed_but_still_wrong | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_4 | d0_18mo::leiden_1.0_3 | 0.376 | 0.778 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | changed_but_still_wrong | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_4 | d0_18mo::leiden_1.0_3 | 0.333 | 0.722 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | changed_but_still_wrong | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_6 | d0_18mo::leiden_1.0_3 | 0.343 | 0.766 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | changed_but_still_wrong | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_4 | d0_18mo::leiden_1.0_3 | 0.455 | 0.698 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | context_rescue | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_4 | d0_02mo::leiden_1.0_1 | 0.511 | 0.857 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | context_rescue | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_4 | d0_02mo::leiden_1.0_1 | 0.437 | 0.822 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | context_rescue | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_3 | d0_02mo::leiden_1.0_1 | 0.391 | 0.841 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | context_rescue | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_3 | d0_02mo::leiden_1.0_1 | 0.487 | 0.831 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | context_rescue | d0_18mo::leiden_1.0_3 | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_3 | 0.281 | 0.767 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | context_rescue | d0_18mo::leiden_1.0_3 | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_3 | 0.301 | 0.783 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | context_rescue | d0_18mo::leiden_1.0_3 | d0_18mo::leiden_1.0_6 | d0_18mo::leiden_1.0_3 | 0.322 | 0.757 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | context_rescue | d0_18mo::leiden_1.0_3 | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_3 | 0.428 | 0.777 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | context_harm | d0_02mo::leiden_1.0_1 | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_3 | 0.327 | 0.907 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | context_harm | d0_02mo::leiden_1.0_1 | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_3 | 0.328 | 0.899 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | context_harm | d0_02mo::leiden_1.0_1 | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_3 | 0.377 | 0.888 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | context_harm | d0_02mo::leiden_1.0_1 | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_3 | 0.326 | 0.884 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | context_harm | d0_02mo::leiden_1.0_1 | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_3 | 0.454 | 0.886 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | context_harm | d0_02mo::leiden_1.0_1 | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_3 | 0.323 | 0.879 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | context_harm | d0_02mo::leiden_1.0_1 | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_3 | 0.322 | 0.860 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | reference_profile | context_harm | d0_02mo::leiden_1.0_1 | d0_02mo::leiden_1.0_1 | d0_18mo::leiden_1.0_3 | 0.463 | 0.853 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile | changed_but_still_wrong | Micro Homeo | Micro SPP1 | Micro Foamy | 0.248 | 0.980 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile | changed_but_still_wrong | Micro Stress | Micro SPP1 | Micro Foamy | 0.351 | 0.980 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile | changed_but_still_wrong | Micro Homeo | Micro Stress | Micro IL1B | 0.283 | 0.975 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile | changed_but_still_wrong | Micro Homeo | Micro SPP1 | Micro Foamy | 0.237 | 0.963 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile | changed_but_still_wrong | Micro Homeo | Micro SPP1 | Micro Foamy | 0.255 | 0.960 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile | changed_but_still_wrong | Micro VEGFA | Micro SPP1 | Micro Foamy | 0.374 | 0.959 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile | changed_but_still_wrong | Micro Homeo | Micro SPP1 | Micro Foamy | 0.292 | 0.958 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile | changed_but_still_wrong | Micro VEGFA | Micro SPP1 | Micro IL1B | 0.302 | 0.967 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile | context_rescue | DAOPC | OPC | DAOPC | 0.823 | 0.992 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile | context_rescue | DAOPC | OPC | DAOPC | 0.836 | 0.989 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile | context_rescue | DAOPC | OPC | DAOPC | 0.939 | 0.987 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile | context_rescue | DAOPC | OPC | DAOPC | 0.830 | 0.987 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile | context_rescue | DAOPC | OPC | DAOPC | 0.794 | 0.985 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile | context_rescue | DAOPC | OPC | DAOPC | 0.727 | 0.985 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile | context_rescue | DAOPC | OPC | DAOPC | 0.864 | 0.980 |
| GEO_GSE284005_MERSCOPE_MS | reference_profile | context_rescue | Micro Foamy | Micro Homeo | Micro Foamy | 0.246 | 0.968 |

## Manuscript Use

This report supports a focused claim: NicheTypeR is an annotation-audit
layer. It can quantify where reference/context evidence rescues a marker
call, where it harms a correct marker call, and where a conflict should be
sent back to expert review rather than silently accepted.
