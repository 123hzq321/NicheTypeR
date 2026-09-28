# Fold-Label Task Benchmark

This analysis decomposes each benchmark into fold-level dataset-label tasks.
It asks whether a label-level context gain appears in held-out folds rather
than only after aggregation. Fold-label tasks are validation units, not
independent public datasets.

Guardrail counts use fold-label tasks with support >= 10.

## Fold-Label Summary

| scale | dataset configs | fold-label tasks | total support | learned improved | learned harmed | learned guardrail | context guardrail |
|---|---:|---:|---:|---:|---:|---:|---:|
| all | 48 | 2984 | 1069270 | 916 | 577 | 349 | 206 |
| expanded | 36 | 2083 | 1024798 | 605 | 345 | 154 | 103 |
| preview | 12 | 901 | 44472 | 311 | 232 | 195 | 103 |

## Reproducible Dataset-Label Tasks

| scale | eligible dataset-label tasks | learned reproducible | context reproducible | median eligible folds |
|---|---:|---:|---:|---:|
| all | 940 | 54 | 12 | 3.0 |
| expanded | 724 | 25 | 9 | 3.0 |
| preview | 216 | 29 | 3 | 5.0 |

## Top Fold-Level Learned-Neighborhood Tasks

| task | support | marker F1 | learned F1 | specific delta |
|---|---:|---:|---:|---:|
| preview / GEO_GSE327581_COSMX_AD_BRAIN / fold 4 / Telencephalon.inhibitory.neurons | 41 | 0.174 | 0.453 | +0.279 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / fold 2 / Neurogliaform.cells | 14 | 0.500 | 0.727 | +0.227 |
| preview / SQUIDPY_SEQFISH / fold 3 / Erythroid | 21 | 0.636 | 0.933 | +0.221 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / fold 4 / Perivascular.macrophages | 23 | 0.077 | 0.294 | +0.217 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / fold 1 / Astrocytes.thalamus.hypothalamus | 13 | 0.333 | 0.500 | +0.167 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / fold 2 / Vascular.smooth.muscle.cells | 10 | 0.571 | 0.762 | +0.162 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / fold 1 / Olfactory.ensheathing.cells | 12 | 0.000 | 0.154 | +0.154 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / fold 4 / Astrocytes.thalamus.hypothalamus | 24 | 0.632 | 0.773 | +0.141 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / fold 1 / Microglia | 14 | 0.160 | 0.300 | +0.140 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / fold 4 / Excitatory.neurons.layer.2.3 | 43 | 0.275 | 0.406 | +0.132 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / fold 1 / Telencephalon.inhibitory.neurons | 12 | 0.429 | 0.560 | +0.131 |
| preview / SQUIDPY_SEQFISH / fold 3 / Presomitic mesoderm | 270 | 0.527 | 0.684 | +0.127 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / fold 1 / Serotonergic.neurons | 20 | 0.571 | 0.698 | +0.126 |
| preview / GEO_GSE240015_VISIUM_THYMUS_DOMAIN / fold 2 / d0_18mo::leiden_1.0_0 | 113 | 0.197 | 0.520 | +0.120 |
| expanded / GEO_GSE326743_GENERIC_XENIUM_EXPANDED / fold 2 / Vascular smooth muscle cells | 1254 | 0.470 | 0.598 | +0.117 |
| expanded / GEO_GSE280376_GENERIC_XENIUM_EXPANDED / fold 1 / FB_Postn_Thbs4 | 522 | 0.018 | 0.153 | +0.117 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / fold 1 / Neurogliaform.cells | 19 | 0.348 | 0.462 | +0.114 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / fold 1 / Oligodendrocyte.precursor.cells | 12 | 0.629 | 0.741 | +0.112 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / fold 4 / Olfactory.ensheathing.cells | 20 | 0.261 | 0.370 | +0.110 |
| preview / SQUIDPY_SEQFISH / fold 5 / Gut tube | 35 | 0.762 | 0.886 | +0.104 |
| preview / SQUIDPY_VISIUM_FLUO / fold 1 / Cortex_1 | 117 | 0.331 | 0.515 | +0.102 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / fold 5 / Perivascular.macrophages | 18 | 0.000 | 0.100 | +0.100 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / fold 4 / Granule.neurons | 36 | 0.714 | 0.813 | +0.098 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / fold 2 / Inhibitory.neurons.habenula.hypothalamus | 17 | 0.385 | 0.483 | +0.098 |
| preview / SQUIDPY_SEQFISH / fold 3 / Haematoendothelial progenitors | 54 | 0.434 | 0.557 | +0.097 |

## Top Reproducible Dataset-Label Tasks

| task | eligible folds | learned guardrail folds | median learned specific delta | total support |
|---|---:|---:|---:|---:|
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Telencephalon.inhibitory.neurons | 4 | 4 | +0.093 | 94 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Astrocytes.thalamus.hypothalamus | 5 | 4 | +0.090 | 100 |
| preview / SQUIDPY_SEQFISH / Erythroid | 5 | 4 | +0.033 | 300 |
| preview / SQUIDPY_SEQFISH / Gut tube | 5 | 4 | +0.017 | 300 |
| expanded / GEO_GSE326743_GENERIC_XENIUM_EXPANDED / Vascular smooth muscle cells | 3 | 3 | +0.043 | 2500 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Excitatory.neurons.hippocampal.CA1 | 5 | 3 | +0.033 | 100 |
| expanded / GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED / Astrocytes.thalamus.hypothalamus | 3 | 3 | +0.032 | 300 |
| preview / SQUIDPY_SEQFISH / Dermomyotome | 5 | 3 | +0.029 | 300 |
| expanded / GEO_GSE282127_GENERIC_H5AD_EXPANDED / 0 | 3 | 3 | +0.028 | 2500 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / D1.medium.spiny.neurons | 5 | 3 | +0.024 | 100 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Inhibitory.neurons.habenula.hypothalamus | 5 | 3 | +0.023 | 100 |
| preview / SQUIDPY_IMC / apoptotic tumor cell | 5 | 3 | +0.019 | 300 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Excitatory.neurons.hippocampal.CA3 | 4 | 3 | +0.018 | 93 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Vascular.endothelial.cells | 5 | 3 | +0.018 | 100 |
| preview / GEO_GSE240015_VISIUM_THYMUS_DOMAIN / d0_02mo::leiden_1.0_0 | 4 | 3 | +0.017 | 746 |
| preview / SQUIDPY_MERFISH / Endothelial 2 | 5 | 3 | +0.017 | 300 |
| preview / SQUIDPY_SEQFISH / Splanchnic mesoderm | 5 | 3 | +0.014 | 300 |
| preview / GEO_GSE284005_MERSCOPE_MS / Micro Homeo | 5 | 3 | +0.013 | 250 |
| preview / GEO_GSE284005_MERSCOPE_MS / DA.Astro | 5 | 3 | +0.012 | 250 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Excitatory.neurons.layer.2.3 | 3 | 2 | +0.078 | 93 |
| expanded / GEO_GSE263450_GENERIC_H5AD_EXPANDED / 8 | 3 | 2 | +0.055 | 2094 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Olfactory.ensheathing.cells | 4 | 2 | +0.055 | 91 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Excitatory.neurons.layer.4 | 2 | 2 | +0.046 | 90 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Neurogliaform.cells | 4 | 2 | +0.043 | 92 |
| expanded / GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED / Telencephalon.inhibitory.neurons | 3 | 2 | +0.034 | 300 |

## Interpretation

Fold-label analysis is useful for stress-testing whether label-level context
signals recur across blocked splits. It strengthens audit evidence for
candidate case studies, but dataset-level guardrails remain the primary
generalization claim.
