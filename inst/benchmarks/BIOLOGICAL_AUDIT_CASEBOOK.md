# Biological Audit Casebook

This casebook converts benchmark errors into reviewable biological audit events.
A case is included when NicheTypeR or an external annotation output is flagged
by the audit layer and the held-out author/expert label confirms that the
predicted label is wrong.

Across all call tables, 256,941 predictions were audit-flagged and
153,847 of them were expert-confirmed model-call errors
(precision 0.599).
These correspond to 29,480 unique dataset-cell or dataset-spot
events after removing duplicate model calls.
The released example table contains 300 high-priority cases;
300 have local metadata and 189 show local
neighborhood evidence that either favors the expert label or makes the
predicted label spatially implausible.

## Highest-Precision Dataset/Model Strata

| dataset | model | calls | audit flagged | confirmed flagged errors | precision | wrong-call rate |
|---|---|---:|---:|---:|---:|---:|
| SQUIDPY_SLIDESEQV2 | seurat_label_transfer | 2800 | 1212 | 999 | 0.824 | 0.635 |
| GEO_GSE327581_COSMX_AD_BRAIN | reference_profile | 5500 | 3962 | 3190 | 0.805 | 0.739 |
| SQUIDPY_SLIDESEQV2 | reference_profile | 2800 | 1602 | 1285 | 0.802 | 0.685 |
| SQUIDPY_SLIDESEQV2 | reference_profile_learned_neighborhood | 2800 | 1819 | 1417 | 0.779 | 0.688 |
| SQUIDPY_SLIDESEQV2 | marker_only | 2800 | 1397 | 1084 | 0.776 | 0.605 |
| SQUIDPY_SLIDESEQV2 | marker_spatial_smoothing | 2800 | 1426 | 1104 | 0.774 | 0.605 |
| SQUIDPY_SLIDESEQV2 | marker_spatial_smoothing_random_graph | 2800 | 1444 | 1104 | 0.765 | 0.603 |
| GEO_GSE327581_COSMX_AD_BRAIN | reference_profile_learned_neighborhood | 5500 | 4645 | 3548 | 0.764 | 0.725 |
| GEO_GSE284005_MERSCOPE_MS | seurat_label_transfer | 9393 | 3028 | 2271 | 0.750 | 0.569 |
| SQUIDPY_SLIDESEQV2 | marker_reference_profile | 2800 | 1752 | 1296 | 0.740 | 0.617 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_only | 3910 | 2391 | 1723 | 0.721 | 0.660 |
| GEO_GSE327581_COSMX_AD_BRAIN | seurat_label_transfer | 5500 | 1718 | 1230 | 0.716 | 0.506 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_learned_neighborhood | 3910 | 2932 | 2085 | 0.711 | 0.673 |
| SQUIDPY_MERFISH | marker_reference_profile | 4030 | 850 | 601 | 0.707 | 0.274 |
| SQUIDPY_SLIDESEQV2 | learned_random_graph | 2800 | 1791 | 1258 | 0.702 | 0.605 |
| SQUIDPY_SLIDESEQV2 | marker_learned_neighborhood | 2800 | 1801 | 1263 | 0.701 | 0.604 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_spatial_smoothing_random_graph | 3910 | 2396 | 1680 | 0.701 | 0.657 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | learned_permuted_prior | 3910 | 2852 | 1996 | 0.700 | 0.647 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_context_specific_neighborhood | 3910 | 2766 | 1931 | 0.698 | 0.667 |
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | marker_spatial_smoothing | 3910 | 2486 | 1734 | 0.698 | 0.642 |

## Representative Expert-Confirmed Flagged Errors

| dataset | model | expert label | predicted label | reason | local interpretation |
|---|---|---|---|---|---|
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Excitatory.neurons.telencephalon | Excitatory.neurons.hippocampal.CA3 | learned_neighborhood_conflict | local context flags conflict but does not resolve label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Excitatory.neurons.hippocampal.CA2 | Excitatory.neurons.hippocampal.CA3 | learned_neighborhood_conflict | local majority supports expert label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Myelin.forming.oligodendrocytes | Committed.oligodendrocytes | learned_neighborhood_conflict | predicted label absent from local neighbors |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Excitatory.neurons.amygdala | Excitatory.neurons.hippocampal.CA3 | learned_neighborhood_conflict | local context flags conflict but does not resolve label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Astrocytes.thalamus.hypothalamus | Excitatory.neurons.di.mesencephalon | learned_neighborhood_conflict | local context flags conflict but does not resolve label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Mature.oligodendrocytes | Committed.oligodendrocytes | learned_neighborhood_conflict | predicted label absent from local neighbors |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Excitatory.neurons.amygdala | Excitatory.neurons.hippocampal.CA3 | learned_neighborhood_conflict | local context flags conflict but does not resolve label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Excitatory.neurons.layer.4 | Hindbrain.excitatory.neurons | learned_neighborhood_conflict | local context flags conflict but does not resolve label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Astrocytes.Bergmann.glia | Purkinje.cells | learned_neighborhood_conflict | local neighbors favor expert label over prediction |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Excitatory.neurons.hippocampal.CA1 | Excitatory.neurons.hippocampal.CA3 | learned_neighborhood_conflict | local majority supports expert label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Excitatory.neurons.amygdala | Excitatory.neurons.hippocampal.CA3 | learned_neighborhood_conflict | local context flags conflict but does not resolve label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Excitatory.neurons.layer.4 | Hindbrain.excitatory.neurons | learned_neighborhood_conflict | local context flags conflict but does not resolve label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Mature.oligodendrocytes | Committed.oligodendrocytes | learned_neighborhood_conflict | predicted label absent from local neighbors |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Inhibitory.neurons.habenula.thalamus | Excitatory.neurons.di.mesencephalon | learned_neighborhood_conflict | local majority supports expert label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Myelin.forming.oligodendrocytes | Committed.oligodendrocytes | learned_neighborhood_conflict | predicted label absent from local neighbors |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Excitatory.neurons.layer.4 | Hindbrain.excitatory.neurons | learned_neighborhood_conflict | local neighbors favor expert label over prediction |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Excitatory.neurons.amygdala | Excitatory.neurons.hippocampal.CA3 | learned_neighborhood_conflict | local majority supports expert label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Excitatory.neurons.hippocampal.CA2 | Excitatory.neurons.hippocampal.CA3 | learned_neighborhood_conflict | local majority supports expert label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Excitatory.neurons.hippocampal.CA2 | Excitatory.neurons.hippocampal.CA3 | learned_neighborhood_conflict | local majority supports expert label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Mature.oligodendrocytes | Committed.oligodendrocytes | learned_neighborhood_conflict | local context flags conflict but does not resolve label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Excitatory.neurons.layer.4 | Hindbrain.excitatory.neurons | learned_neighborhood_conflict | predicted label absent from local neighbors |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Newly.formed.oligodendrocytes | Hypendymal | learned_neighborhood_conflict | local context flags conflict but does not resolve label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Excitatory.neurons.layer.4 | Hindbrain.excitatory.neurons | learned_neighborhood_conflict | local context flags conflict but does not resolve label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Perivascular.macrophages | Microglia | learned_neighborhood_conflict | local context flags conflict but does not resolve label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Excitatory.neurons.hippocampal.CA2 | Excitatory.neurons.hippocampal.CA3 | learned_neighborhood_conflict | local majority supports expert label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Hindbrain.inhibitory.neurons | Hindbrain.excitatory.neurons | learned_neighborhood_conflict | local context flags conflict but does not resolve label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Myelin.forming.oligodendrocytes | Committed.oligodendrocytes | learned_neighborhood_conflict | local context flags conflict but does not resolve label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Excitatory.neurons.layer.4 | Hindbrain.excitatory.neurons | learned_neighborhood_conflict | local context flags conflict but does not resolve label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Excitatory.neurons.layer.4 | Hindbrain.excitatory.neurons | learned_neighborhood_conflict | local context flags conflict but does not resolve label |
| GEO_GSE327581_COSMX_AD_BRAIN | marker_learned_neighborhood | Excitatory.neurons.layer.4 | Hindbrain.excitatory.neurons | learned_neighborhood_conflict | local majority supports expert label |

## Interpretation

This is not a prospective pathology re-annotation experiment. The independent
evidence is the held-out author/expert label, with local-neighborhood summaries
added when metadata are available. The result supports a narrower but testable
claim: NicheTypeR can prioritize concrete, biologically inspectable annotation
problems rather than only reporting aggregate F1 changes.
