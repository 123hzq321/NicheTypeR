# Label-Task Benchmark

This analysis treats each dataset-label pair as a validation task. It does not
increase the number of independent public datasets; instead it reports the
granularity at which annotation audit tools are actually used: whether a
specific label in a specific tissue dataset is rescued, harmed or supported
by context beyond matched null controls.

## Summary

| scale | dataset configs | label tasks | total support | learned improved | learned harmed | learned guardrail | context guardrail |
|---|---:|---:|---:|---:|---:|---:|---:|
| all | 48 | 941 | 1070222 | 263 | 133 | 83 | 22 |
| expanded | 36 | 724 | 1025118 | 186 | 89 | 38 | 11 |
| preview | 12 | 217 | 45104 | 77 | 44 | 45 | 11 |

## Support Bins

| scale | support bin | label tasks | learned improved | learned harmed | learned guardrail | context guardrail | median learned delta |
|---|---|---:|---:|---:|---:|---:|---:|
| expanded | 1-25 | 2 | 0 | 1 | 0 | 0 | -0.0271 |
| expanded | 101-500 | 178 | 55 | 26 | 15 | 6 | +0.0034 |
| expanded | 26-100 | 56 | 10 | 3 | 0 | 0 | +0.0015 |
| expanded | 501-1000 | 138 | 35 | 21 | 2 | 1 | +0.0023 |
| expanded | >1000 | 350 | 86 | 38 | 21 | 4 | +0.0020 |
| preview | 101-500 | 132 | 39 | 22 | 16 | 5 | +0.0006 |
| preview | 26-100 | 76 | 35 | 21 | 28 | 6 | +0.0090 |
| preview | 501-1000 | 8 | 2 | 1 | 1 | 0 | -0.0005 |
| preview | >1000 | 1 | 1 | 0 | 0 | 0 | +0.0173 |

## Top Learned-Neighborhood Label Tasks

| task | support | marker F1 | learned F1 | specific delta |
|---|---:|---:|---:|---:|
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Telencephalon.inhibitory.neurons | 100 | 0.492 | 0.597 | +0.105 |
| preview / SQUIDPY_SEQFISH / Presomitic mesoderm | 300 | 0.447 | 0.572 | +0.103 |
| expanded / GEO_GSE326743_GENERIC_XENIUM_EXPANDED / Vascular smooth muscle cells | 2500 | 0.471 | 0.555 | +0.081 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Excitatory.neurons.layer.2.3 | 100 | 0.343 | 0.424 | +0.078 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Astrocytes.thalamus.hypothalamus | 100 | 0.615 | 0.689 | +0.074 |
| preview / GSE202623_LESION / Endothelial | 65 | 0.570 | 0.652 | +0.069 |
| preview / SQUIDPY_VISIUM_HNE / Pyramidal_layer_dentate_gyrus | 68 | 0.483 | 0.667 | +0.059 |
| expanded / GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED / Telencephalon.inhibitory.neurons | 300 | 0.377 | 0.451 | +0.053 |
| expanded / GEO_GSE282127_GENERIC_H5AD_EXPANDED / 1 | 2500 | 0.107 | 0.236 | +0.050 |
| preview / SQUIDPY_VISIUM_FLUO / Lateral_ventricle | 47 | 0.448 | 0.525 | +0.046 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Granule.neurons | 100 | 0.725 | 0.791 | +0.045 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Inhibitory.neurons.reticular.nucleus | 100 | 0.549 | 0.596 | +0.044 |
| preview / SQUIDPY_VISIUM_FLUO / Hippocampus | 259 | 0.641 | 0.763 | +0.044 |
| expanded / GEO_GSE263450_GENERIC_H5AD_EXPANDED / 8 | 2094 | 0.220 | 0.298 | +0.042 |
| expanded / GEO_GSE280376_GENERIC_XENIUM_EXPANDED / FB_Postn_Thbs4 | 1074 | 0.165 | 0.206 | +0.041 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Excitatory.neurons.layer.1.piriform | 100 | 0.151 | 0.220 | +0.040 |
| preview / GEO_GSE240015_VISIUM_THYMUS_DOMAIN / d0_18mo::leiden_1.0_0 | 283 | 0.208 | 0.328 | +0.039 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Peptidergic.neurons | 100 | 0.490 | 0.528 | +0.038 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Excitatory.neurons.hippocampal.CA1 | 100 | 0.587 | 0.637 | +0.038 |
| expanded / GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED / Astrocytes.thalamus.hypothalamus | 300 | 0.672 | 0.709 | +0.037 |

## Top Context-Specific Label Tasks

| task | support | marker F1 | context F1 | specific delta |
|---|---:|---:|---:|---:|
| preview / SQUIDPY_IMC / apoptotic tumor cell | 300 | 0.307 | 0.404 | +0.088 |
| preview / SQUIDPY_VISIUM_HNE / Cortex_4 | 164 | 0.541 | 0.649 | +0.064 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Myelin.forming.oligodendrocytes | 100 | 0.150 | 0.224 | +0.060 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Excitatory.neurons.layer.5 | 100 | 0.194 | 0.266 | +0.035 |
| preview / SQUIDPY_VISIUM_HNE / Fiber_tract | 226 | 0.802 | 0.832 | +0.031 |
| expanded / GEO_GSE245263_GENERIC_H5AD_EXPANDED / 6 | 164 | 0.657 | 0.691 | +0.027 |
| expanded / SQUIDPY_SEQFISH_EXPANDED / 19 | 2620 | 0.437 | 0.466 | +0.026 |
| expanded / GEO_GSE282127_GENERIC_H5AD_EXPANDED / 22 | 1446 | 0.433 | 0.463 | +0.025 |
| expanded / GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED / Perivascular.macrophages | 300 | 0.209 | 0.251 | +0.025 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Inhibitory.interneurons | 100 | 0.784 | 0.823 | +0.021 |
| expanded / GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED / t | 2500 | 0.227 | 0.269 | +0.021 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Mature.oligodendrocytes | 100 | 0.000 | 0.019 | +0.019 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Vascular.leptomeningeal.cells | 100 | 0.724 | 0.742 | +0.019 |
| preview / GEO_GSE327581_COSMX_AD_BRAIN / Vascular.smooth.muscle.cells | 100 | 0.587 | 0.613 | +0.019 |
| expanded / GEO_GSE245263_GENERIC_H5AD_EXPANDED / 8 | 143 | 0.333 | 0.365 | +0.018 |
| preview / SQUIDPY_SLIDESEQV2 / Mural | 200 | 0.216 | 0.232 | +0.015 |
| expanded / GEO_GSE333479_H5AD_SIDECAR_EXPANDED / B cell | 2500 | 0.232 | 0.246 | +0.014 |
| expanded / GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED / Vascular.smooth.muscle.cells | 300 | 0.684 | 0.704 | +0.014 |
| expanded / GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED / Astrocytes.Bergmann.glia | 300 | 0.710 | 0.740 | +0.014 |
| expanded / GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED / C01_S | 358 | 0.312 | 0.326 | +0.014 |

## Interpretation

The label-task view increases validation granularity, but not the number of
independent cohorts. Positive label-level guardrails are useful for triage and
case-study selection; dataset-level guardrails remain the primary claim for
general performance.
