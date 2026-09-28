# Expanded-Scale Lean Blocked Benchmark

This stress test uses larger train/test splits than the preview benchmark.
It keeps the core marker, reference-profile, learned-neighborhood, random-graph,
permuted-prior and context-specific residual comparisons, with fixed evidence weights
to avoid turning the scale-control experiment into another tuning benchmark.

## Dataset Scale

| dataset | source | cells/spots | features | labels | spatial groups | sampling |
|---|---|---:|---:|---:|---:|---|
| GSE202623_CELLTYPE_EXPANDED | GSE202623 | 33760 | 287 | 42 | 3337 | balanced non-doublet cell.type_manual labels, min_per_label=50, max_per_label=1000 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | GSE333737 | 24222 | 300 | 4 | 12 | all labeled cells |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | GSE284005 | 34350 | 500 | 38 | 17 | balanced clean_sub labels, min_per_label=25, max_per_label=1000 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | GSE327581 | 16371 | 1207 | 55 | 5 | balanced InSituType labels, min_per_label=25, max_per_label=300 |
| SQUIDPY_MERFISH_EXPANDED | SQUIDPY_MERFISH | 73655 | 161 | 16 | 12 | all clean labels with >= 25 cells |
| SQUIDPY_SEQFISH_EXPANDED | SQUIDPY_SEQFISH | 19416 | 351 | 22 | 63 | all clean labels with >= 25 cells |
| SQUIDPY_SLIDESEQV2_EXPANDED | SQUIDPY_SLIDESEQV2 | 18842 | 1500 | 14 | 64 | balanced clean labels, min_per_label=25, max_per_label=1500, top mean features=1500 |
| GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED | GSE302502 | 23570 | 541 | 10 | 12 | balanced coarse_cell_type labels from 12 TLS patient samples, max_per_label=2500 |
| GEO_GSE282127_GENERIC_H5AD_EXPANDED | GSE282127 | 53108 | 550 | 26 | 42 | balanced labels, max_per_label applied; label_col=leiden_0.8 |
| GEO_GSE245263_GENERIC_H5AD_EXPANDED | GSE245263 | 2158 | 2000 | 15 | 61 | balanced labels, max_per_label applied; label_col=leiden |
| GEO_GSE263450_GENERIC_H5AD_EXPANDED | GSE263450 | 36521 | 2000 | 24 | 63 | balanced labels, max_per_label applied; label_col=leiden |
| GEO_GSE294759_GENERIC_H5AD_EXPANDED | GSE294759 | 44137 | 2000 | 32 | 64 | balanced labels, max_per_label applied; label_col=leiden |
| GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED | GSE301435 | 57937 | 1201 | 26 | 617 | balanced labels, max_per_label applied; label_col=RNA_nbclust_719bacdb.ea30.4c91.8f6f.d838e95062e8_1_clusters |
| GEO_GSE308624_GENERIC_H5AD_EXPANDED | GSE308624 | 18032 | 1000 | 8 | 64 | balanced labels, max_per_label applied; label_col=cell_type |
| GEO_GSE310129_GENERIC_H5AD_EXPANDED | GSE310129 | 22522 | 2000 | 28 | 63 | balanced labels, max_per_label applied; label_col=leiden |
| GEO_GSE317755_GENERIC_H5AD_EXPANDED | GSE317755 | 3188 | 2000 | 14 | 61 | balanced labels, max_per_label applied; label_col=seurat_clusters |
| GEO_GSE327129_GENERIC_H5AD_EXPANDED | GSE327129 | 7303 | 2000 | 3 | 61 | balanced labels, max_per_label applied; label_col=Classification |
| GEO_GSE328481_GENERIC_H5AD_EXPANDED | GSE328481 | 15000 | 2000 | 6 | 58 | balanced labels, max_per_label applied; label_col=bin50 structural annotation |
| GEO_GSE330849_GENERIC_H5AD_EXPANDED | GSE330849 | 52701 | 478 | 23 | 64 | balanced labels, max_per_label applied; label_col=leiden |
| GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED | GSE325587 | 20386 | 1008 | 29 | 194 | balanced labels, max_per_label applied; label_col=GSE325587_processed_metadata.csv.gz:cell_types_full |
| GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED | GSE273530 | 8976 | 1196 | 10 | 29 | balanced labels, max_per_label applied; label_col=nn_233be8c1.6622.4cb9.83e9.1c261ca737c7_1_cluster_cluster_e901c776.a68c.4ffe.828e.b95c25440e02_1 |
| GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED | GSE273952 | 5000 | 2000 | 2 | 566 | balanced labels, max_per_label applied; label_col=TumoralZone_annotation:Tumor_zone |
| GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED | GSE337336 | 20000 | 1000 | 8 | 559 | balanced labels, max_per_label applied; label_col=InSituTypeIDs2 |
| GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED | GSE307588 | 3713 | 380 | 16 | 62 | balanced labels, max_per_label applied; label_col=Cluster |
| GEO_GSE326743_GENERIC_XENIUM_EXPANDED | GSE326743 | 64284 | 1000 | 30 | 3 | balanced labels, max_per_label applied; label_col=Level_4_Annotations |
| GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED | GSE305393 | 19039 | 1000 | 21 | 73 | balanced labels, max_per_label applied; label_col=cell_type |
| GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED | GSE291308 | 17655 | 1000 | 8 | 53 | balanced labels, max_per_label applied; label_col=ct |
| GEO_GSE311681_GENERIC_XENIUM_EXPANDED | GSE311681 | 33574 | 541 | 25 | 36 | balanced labels, max_per_label applied; label_col=_resolved_label |
| GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED | GSE292268 | 28166 | 1000 | 16 | 127 | balanced labels, max_per_label applied; label_col=RNA_nbclust_ee1320c5.9f48.455c.b54e.1fbfd34347ab_1_clusters |
| GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED | GSE278766 | 32011 | 1000 | 13 | 205 | balanced labels, max_per_label applied; label_col=RNA_nbclust_9d7145a9.f10b.453d.960e.322d9aecddcb_1_clusters |
| GEO_GSE333479_H5AD_SIDECAR_EXPANDED | GSE333479 | 20448 | 2000 | 14 | 5 | balanced labels, max_per_label applied; label_col=sidecar:annotation |
| GEO_GSE279181_H5AD_COMPOSITION_EXPANDED | GSE279181 | 11677 | 2000 | 9 | 18 | balanced labels, max_per_label applied; label_col=obsm:argmax(ctype_props) |
| GEO_GSE280376_GENERIC_XENIUM_EXPANDED | GSE280376 | 92321 | 540 | 65 | 7 | balanced labels, max_per_label applied; label_col=_resolved_label |
| GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED | GSE308167 | 11775 | 2000 | 11 | 3 | balanced labels, max_per_label applied; label_col=obs:cell_type |
| GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED | GSE308952 | 3720 | 2000 | 7 | 28 | balanced labels, max_per_label applied; label_col=obs:manual_anno |
| GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED | GSE336633 | 75580 | 2000 | 34 | 3 | balanced labels, max_per_label applied; label_col=obs:predicted_labels |

## Fold Size

| dataset | folds | mean train | mean test | min test | max test | mean train groups | mean test groups |
|---|---:|---:|---:|---:|---:|---:|---:|
| GEO_GSE245263_GENERIC_H5AD_EXPANDED | 3 | 1439 | 719 | 648 | 775 | 40.7 | 20.3 |
| GEO_GSE263450_GENERIC_H5AD_EXPANDED | 3 | 24347 | 12174 | 11907 | 12527 | 42.0 | 21.0 |
| GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED | 3 | 5984 | 2992 | 2847 | 3202 | 19.3 | 9.7 |
| GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED | 3 | 3333 | 1667 | 1622 | 1695 | 377.3 | 188.7 |
| GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED | 3 | 21341 | 10670 | 9973 | 11132 | 136.7 | 68.3 |
| GEO_GSE279181_H5AD_COMPOSITION_EXPANDED | 3 | 7785 | 3892 | 2714 | 4889 | 12.0 | 6.0 |
| GEO_GSE280376_GENERIC_XENIUM_EXPANDED | 3 | 61547 | 30774 | 24459 | 42256 | 4.7 | 2.3 |
| GEO_GSE282127_GENERIC_H5AD_EXPANDED | 3 | 35405 | 17703 | 14039 | 24461 | 28.0 | 14.0 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | 3 | 22900 | 11450 | 9025 | 13699 | 11.3 | 5.7 |
| GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED | 3 | 11770 | 5885 | 5521 | 6175 | 35.3 | 17.7 |
| GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED | 3 | 18777 | 9389 | 8415 | 10094 | 84.7 | 42.3 |
| GEO_GSE294759_GENERIC_H5AD_EXPANDED | 3 | 29425 | 14712 | 13813 | 16502 | 42.7 | 21.3 |
| GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED | 3 | 38625 | 19312 | 18664 | 20472 | 411.3 | 205.7 |
| GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED | 3 | 15713 | 7857 | 6315 | 10373 | 8.0 | 4.0 |
| GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED | 3 | 12693 | 6346 | 5959 | 6905 | 48.7 | 24.3 |
| GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED | 3 | 2475 | 1238 | 1201 | 1291 | 41.3 | 20.7 |
| GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED | 3 | 7850 | 3925 | 2334 | 5803 | 2.0 | 1.0 |
| GEO_GSE308624_GENERIC_H5AD_EXPANDED | 3 | 12021 | 6011 | 5513 | 6978 | 42.7 | 21.3 |
| GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED | 3 | 2480 | 1240 | 814 | 1551 | 18.7 | 9.3 |
| GEO_GSE310129_GENERIC_H5AD_EXPANDED | 3 | 15015 | 7507 | 6731 | 8757 | 42.0 | 21.0 |
| GEO_GSE311681_GENERIC_XENIUM_EXPANDED | 3 | 22383 | 11191 | 10094 | 13038 | 24.0 | 12.0 |
| GEO_GSE317755_GENERIC_H5AD_EXPANDED | 3 | 2125 | 1063 | 912 | 1229 | 40.7 | 20.3 |
| GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED | 3 | 13591 | 6795 | 4585 | 8562 | 129.3 | 64.7 |
| GEO_GSE326743_GENERIC_XENIUM_EXPANDED | 3 | 42856 | 21428 | 16980 | 23846 | 2.0 | 1.0 |
| GEO_GSE327129_GENERIC_H5AD_EXPANDED | 3 | 4869 | 2434 | 2139 | 2787 | 40.7 | 20.3 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | 3 | 10914 | 5457 | 2585 | 7229 | 3.3 | 1.7 |
| GEO_GSE328481_GENERIC_H5AD_EXPANDED | 3 | 10000 | 5000 | 3614 | 6190 | 38.7 | 19.3 |
| GEO_GSE330849_GENERIC_H5AD_EXPANDED | 3 | 35134 | 17567 | 16192 | 19359 | 42.7 | 21.3 |
| GEO_GSE333479_H5AD_SIDECAR_EXPANDED | 3 | 13632 | 6816 | 3607 | 9100 | 3.3 | 1.7 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | 3 | 16148 | 8074 | 5645 | 10115 | 8.0 | 4.0 |
| GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED | 3 | 50387 | 25193 | 8574 | 37195 | 2.0 | 1.0 |
| GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED | 3 | 13333 | 6667 | 5731 | 7624 | 372.7 | 186.3 |
| GSE202623_CELLTYPE_EXPANDED | 3 | 22507 | 11253 | 11160 | 11301 | 2224.7 | 1112.3 |
| SQUIDPY_MERFISH_EXPANDED | 3 | 49103 | 24552 | 24399 | 24739 | 8.0 | 4.0 |
| SQUIDPY_SEQFISH_EXPANDED | 3 | 12944 | 6472 | 6111 | 6916 | 42.0 | 21.0 |
| SQUIDPY_SLIDESEQV2_EXPANDED | 3 | 12561 | 6281 | 5610 | 7043 | 42.7 | 21.3 |

## Model Summary

| dataset | model | accuracy | macro-F1 | conflict rate |
|---|---|---:|---:|---:|
| GEO_GSE245263_GENERIC_H5AD_EXPANDED | learned_permuted_prior | 0.4708 | 0.4432 | 0.8170 |
| GEO_GSE245263_GENERIC_H5AD_EXPANDED | learned_random_graph | 0.4425 | 0.4040 | 0.7743 |
| GEO_GSE245263_GENERIC_H5AD_EXPANDED | marker_context_specific_neighborhood | 0.4398 | 0.4047 | 0.7952 |
| GEO_GSE245263_GENERIC_H5AD_EXPANDED | marker_learned_neighborhood | 0.4106 | 0.3816 | 0.7215 |
| GEO_GSE245263_GENERIC_H5AD_EXPANDED | marker_only | 0.4486 | 0.4143 | 0.6603 |
| GEO_GSE245263_GENERIC_H5AD_EXPANDED | marker_reference_profile | 0.4347 | 0.3994 | 0.7614 |
| GEO_GSE245263_GENERIC_H5AD_EXPANDED | reference_profile | 0.3568 | 0.3200 | 0.8522 |
| GEO_GSE263450_GENERIC_H5AD_EXPANDED | learned_permuted_prior | 0.3169 | 0.2781 | 0.7605 |
| GEO_GSE263450_GENERIC_H5AD_EXPANDED | learned_random_graph | 0.3274 | 0.2865 | 0.7365 |
| GEO_GSE263450_GENERIC_H5AD_EXPANDED | marker_context_specific_neighborhood | 0.3334 | 0.2922 | 0.7422 |
| GEO_GSE263450_GENERIC_H5AD_EXPANDED | marker_learned_neighborhood | 0.3349 | 0.2931 | 0.7246 |
| GEO_GSE263450_GENERIC_H5AD_EXPANDED | marker_only | 0.3169 | 0.2789 | 0.6480 |
| GEO_GSE263450_GENERIC_H5AD_EXPANDED | marker_reference_profile | 0.4213 | 0.3415 | 0.7588 |
| GEO_GSE263450_GENERIC_H5AD_EXPANDED | reference_profile | 0.3769 | 0.2895 | 0.7529 |
| GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED | learned_permuted_prior | 0.2760 | 0.2693 | 0.6366 |
| GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED | learned_random_graph | 0.2743 | 0.2688 | 0.6385 |
| GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED | marker_context_specific_neighborhood | 0.2754 | 0.2686 | 0.6776 |
| GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED | marker_learned_neighborhood | 0.2758 | 0.2709 | 0.6369 |
| GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED | marker_only | 0.2767 | 0.2683 | 0.4297 |
| GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED | marker_reference_profile | 0.2793 | 0.2782 | 0.6417 |
| GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED | reference_profile | 0.1576 | 0.1631 | 0.9327 |
| GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED | learned_permuted_prior | 0.7996 | 0.7996 | 0.1740 |
| GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED | learned_random_graph | 0.7996 | 0.7996 | 0.1836 |
| GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED | marker_context_specific_neighborhood | 0.6890 | 0.6878 | 0.2882 |
| GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED | marker_learned_neighborhood | 0.7996 | 0.7996 | 0.1740 |
| GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED | marker_only | 0.7934 | 0.7934 | 0.0892 |
| GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED | marker_reference_profile | 0.7762 | 0.7754 | 0.2576 |
| GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED | reference_profile | 0.6842 | 0.6842 | 0.0622 |
| GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED | learned_permuted_prior | 0.6487 | 0.6363 | 0.5947 |
| GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED | learned_random_graph | 0.6522 | 0.6409 | 0.6229 |
| GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED | marker_context_specific_neighborhood | 0.6546 | 0.6435 | 0.5949 |
| GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED | marker_learned_neighborhood | 0.6558 | 0.6446 | 0.5713 |
| GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED | marker_only | 0.6531 | 0.6417 | 0.3654 |
| GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED | marker_reference_profile | 0.6494 | 0.6375 | 0.5443 |
| GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED | reference_profile | 0.5175 | 0.5129 | 0.5840 |
| GEO_GSE279181_H5AD_COMPOSITION_EXPANDED | learned_permuted_prior | 0.5649 | 0.4141 | 0.5890 |
| GEO_GSE279181_H5AD_COMPOSITION_EXPANDED | learned_random_graph | 0.5600 | 0.4090 | 0.5597 |
| GEO_GSE279181_H5AD_COMPOSITION_EXPANDED | marker_context_specific_neighborhood | 0.5485 | 0.3975 | 0.5405 |
| GEO_GSE279181_H5AD_COMPOSITION_EXPANDED | marker_learned_neighborhood | 0.5611 | 0.4080 | 0.4629 |
| GEO_GSE279181_H5AD_COMPOSITION_EXPANDED | marker_only | 0.5436 | 0.3988 | 0.3666 |
| GEO_GSE279181_H5AD_COMPOSITION_EXPANDED | marker_reference_profile | 0.5531 | 0.4058 | 0.5802 |
| GEO_GSE279181_H5AD_COMPOSITION_EXPANDED | reference_profile | 0.5006 | 0.3224 | 0.5388 |
| GEO_GSE280376_GENERIC_XENIUM_EXPANDED | learned_permuted_prior | 0.0713 | 0.0563 | 0.8046 |
| GEO_GSE280376_GENERIC_XENIUM_EXPANDED | learned_random_graph | 0.0677 | 0.0554 | 0.7989 |
| GEO_GSE280376_GENERIC_XENIUM_EXPANDED | marker_context_specific_neighborhood | 0.0712 | 0.0584 | 0.8085 |
| GEO_GSE280376_GENERIC_XENIUM_EXPANDED | marker_learned_neighborhood | 0.0695 | 0.0571 | 0.8127 |
| GEO_GSE280376_GENERIC_XENIUM_EXPANDED | marker_only | 0.0721 | 0.0586 | 0.7044 |
| GEO_GSE280376_GENERIC_XENIUM_EXPANDED | marker_reference_profile | 0.0991 | 0.0590 | 0.7891 |
| GEO_GSE280376_GENERIC_XENIUM_EXPANDED | reference_profile | 0.0979 | 0.0524 | 0.5970 |
| GEO_GSE282127_GENERIC_H5AD_EXPANDED | learned_permuted_prior | 0.6990 | 0.6397 | 0.4323 |
| GEO_GSE282127_GENERIC_H5AD_EXPANDED | learned_random_graph | 0.6975 | 0.6407 | 0.4707 |
| GEO_GSE282127_GENERIC_H5AD_EXPANDED | marker_context_specific_neighborhood | 0.7031 | 0.6456 | 0.4852 |
| GEO_GSE282127_GENERIC_H5AD_EXPANDED | marker_learned_neighborhood | 0.7017 | 0.6441 | 0.4685 |
| GEO_GSE282127_GENERIC_H5AD_EXPANDED | marker_only | 0.6945 | 0.6353 | 0.2289 |
| GEO_GSE282127_GENERIC_H5AD_EXPANDED | marker_reference_profile | 0.6924 | 0.6298 | 0.2635 |
| GEO_GSE282127_GENERIC_H5AD_EXPANDED | reference_profile | 0.6615 | 0.5890 | 0.2968 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | learned_permuted_prior | 0.4919 | 0.4746 | 0.7336 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | learned_random_graph | 0.5050 | 0.4855 | 0.7018 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | marker_context_specific_neighborhood | 0.5093 | 0.4900 | 0.7155 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | marker_learned_neighborhood | 0.5060 | 0.4876 | 0.7420 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | marker_only | 0.5080 | 0.4889 | 0.5885 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | marker_reference_profile | 0.4511 | 0.4190 | 0.6880 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | reference_profile | 0.3478 | 0.3081 | 0.4831 |
| GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED | learned_permuted_prior | 0.6922 | 0.6841 | 0.5664 |
| GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED | learned_random_graph | 0.6950 | 0.6878 | 0.5580 |
| GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED | marker_context_specific_neighborhood | 0.6954 | 0.6882 | 0.5474 |
| GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED | marker_learned_neighborhood | 0.6935 | 0.6852 | 0.4783 |
| GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED | marker_only | 0.6998 | 0.6934 | 0.2461 |
| GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED | marker_reference_profile | 0.7059 | 0.6952 | 0.2889 |
| GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED | reference_profile | 0.6676 | 0.6448 | 0.3017 |
| GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED | learned_permuted_prior | 0.6914 | 0.6189 | 0.5998 |
| GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED | learned_random_graph | 0.6924 | 0.6193 | 0.5839 |
| GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED | marker_context_specific_neighborhood | 0.6959 | 0.6224 | 0.5892 |
| GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED | marker_learned_neighborhood | 0.6952 | 0.6221 | 0.5788 |
| GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED | marker_only | 0.6955 | 0.6219 | 0.3001 |
| GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED | marker_reference_profile | 0.6903 | 0.6120 | 0.5117 |
| GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED | reference_profile | 0.5346 | 0.4296 | 0.4671 |
| GEO_GSE294759_GENERIC_H5AD_EXPANDED | learned_permuted_prior | 0.1681 | 0.1106 | 0.8168 |
| GEO_GSE294759_GENERIC_H5AD_EXPANDED | learned_random_graph | 0.1693 | 0.1100 | 0.7977 |
| GEO_GSE294759_GENERIC_H5AD_EXPANDED | marker_context_specific_neighborhood | 0.1698 | 0.1106 | 0.8155 |
| GEO_GSE294759_GENERIC_H5AD_EXPANDED | marker_learned_neighborhood | 0.1710 | 0.1105 | 0.8024 |
| GEO_GSE294759_GENERIC_H5AD_EXPANDED | marker_only | 0.1618 | 0.1063 | 0.7286 |
| GEO_GSE294759_GENERIC_H5AD_EXPANDED | marker_reference_profile | 0.2391 | 0.1239 | 0.8392 |
| GEO_GSE294759_GENERIC_H5AD_EXPANDED | reference_profile | 0.2239 | 0.0906 | 0.7287 |
| GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED | learned_permuted_prior | 0.5997 | 0.5699 | 0.6581 |
| GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED | learned_random_graph | 0.5983 | 0.5674 | 0.6397 |
| GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED | marker_context_specific_neighborhood | 0.5963 | 0.5652 | 0.6289 |
| GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED | marker_learned_neighborhood | 0.6021 | 0.5704 | 0.6067 |
| GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED | marker_only | 0.5946 | 0.5654 | 0.4858 |
| GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED | marker_reference_profile | 0.5775 | 0.5588 | 0.6757 |
| GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED | reference_profile | 0.3455 | 0.3245 | 0.8562 |
| GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED | learned_permuted_prior | 0.7310 | 0.7249 | 0.5080 |
| GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED | learned_random_graph | 0.7226 | 0.7153 | 0.5849 |
| GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED | marker_context_specific_neighborhood | 0.7280 | 0.7210 | 0.5478 |
| GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED | marker_learned_neighborhood | 0.7326 | 0.7254 | 0.4802 |
| GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED | marker_only | 0.7264 | 0.7190 | 0.2208 |
| GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED | marker_reference_profile | 0.7236 | 0.7145 | 0.2975 |
| GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED | reference_profile | 0.6443 | 0.6281 | 0.2471 |
| GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED | learned_permuted_prior | 0.5382 | 0.4119 | 0.5840 |
| GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED | learned_random_graph | 0.5531 | 0.4287 | 0.5207 |
| GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED | marker_context_specific_neighborhood | 0.5420 | 0.4220 | 0.5784 |
| GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED | marker_learned_neighborhood | 0.5527 | 0.4290 | 0.5027 |
| GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED | marker_only | 0.5360 | 0.4149 | 0.3832 |
| GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED | marker_reference_profile | 0.5386 | 0.4094 | 0.5808 |
| GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED | reference_profile | 0.4307 | 0.3187 | 0.5181 |
| GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED | learned_permuted_prior | 0.3162 | 0.3011 | 0.7735 |
| GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED | learned_random_graph | 0.2984 | 0.2857 | 0.7379 |
| GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED | marker_context_specific_neighborhood | 0.2973 | 0.2758 | 0.7797 |
| GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED | marker_learned_neighborhood | 0.3038 | 0.2877 | 0.7242 |
| GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED | marker_only | 0.2981 | 0.2883 | 0.5594 |
| GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED | marker_reference_profile | 0.3334 | 0.3536 | 0.7226 |
| GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED | reference_profile | 0.2876 | 0.3205 | 0.8082 |
| GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED | learned_permuted_prior | 0.3896 | 0.3552 | 0.6749 |
| GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED | learned_random_graph | 0.4009 | 0.3634 | 0.6792 |
| GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED | marker_context_specific_neighborhood | 0.3985 | 0.3623 | 0.6996 |
| GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED | marker_learned_neighborhood | 0.3933 | 0.3581 | 0.6761 |
| GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED | marker_only | 0.4055 | 0.3676 | 0.4202 |
| GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED | marker_reference_profile | 0.4217 | 0.3961 | 0.6684 |
| GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED | reference_profile | 0.4042 | 0.4174 | 0.6660 |
| GEO_GSE308624_GENERIC_H5AD_EXPANDED | learned_permuted_prior | 0.7564 | 0.7222 | 0.5545 |
| GEO_GSE308624_GENERIC_H5AD_EXPANDED | learned_random_graph | 0.7544 | 0.7218 | 0.5866 |
| GEO_GSE308624_GENERIC_H5AD_EXPANDED | marker_context_specific_neighborhood | 0.7564 | 0.7248 | 0.5501 |
| GEO_GSE308624_GENERIC_H5AD_EXPANDED | marker_learned_neighborhood | 0.7584 | 0.7262 | 0.5003 |
| GEO_GSE308624_GENERIC_H5AD_EXPANDED | marker_only | 0.7572 | 0.7244 | 0.1779 |
| GEO_GSE308624_GENERIC_H5AD_EXPANDED | marker_reference_profile | 0.7503 | 0.7297 | 0.2076 |
| GEO_GSE308624_GENERIC_H5AD_EXPANDED | reference_profile | 0.7126 | 0.6900 | 0.1888 |
| GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED | learned_permuted_prior | 0.4317 | 0.4193 | 0.5392 |
| GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED | learned_random_graph | 0.4341 | 0.4222 | 0.6005 |
| GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED | marker_context_specific_neighborhood | 0.4325 | 0.4235 | 0.6266 |
| GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED | marker_learned_neighborhood | 0.4444 | 0.4328 | 0.5608 |
| GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED | marker_only | 0.4239 | 0.4143 | 0.2941 |
| GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED | marker_reference_profile | 0.4938 | 0.4701 | 0.4718 |
| GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED | reference_profile | 0.4780 | 0.4322 | 0.5116 |
| GEO_GSE310129_GENERIC_H5AD_EXPANDED | learned_permuted_prior | 0.4969 | 0.4788 | 0.6333 |
| GEO_GSE310129_GENERIC_H5AD_EXPANDED | learned_random_graph | 0.4865 | 0.4695 | 0.6778 |
| GEO_GSE310129_GENERIC_H5AD_EXPANDED | marker_context_specific_neighborhood | 0.4665 | 0.4502 | 0.6966 |
| GEO_GSE310129_GENERIC_H5AD_EXPANDED | marker_learned_neighborhood | 0.4860 | 0.4674 | 0.6066 |
| GEO_GSE310129_GENERIC_H5AD_EXPANDED | marker_only | 0.4589 | 0.4426 | 0.4535 |
| GEO_GSE310129_GENERIC_H5AD_EXPANDED | marker_reference_profile | 0.5568 | 0.5354 | 0.5136 |
| GEO_GSE310129_GENERIC_H5AD_EXPANDED | reference_profile | 0.5897 | 0.5642 | 0.4461 |
| GEO_GSE311681_GENERIC_XENIUM_EXPANDED | learned_permuted_prior | 0.6831 | 0.6187 | 0.6047 |
| GEO_GSE311681_GENERIC_XENIUM_EXPANDED | learned_random_graph | 0.6882 | 0.6190 | 0.4874 |
| GEO_GSE311681_GENERIC_XENIUM_EXPANDED | marker_context_specific_neighborhood | 0.6922 | 0.6225 | 0.5195 |
| GEO_GSE311681_GENERIC_XENIUM_EXPANDED | marker_learned_neighborhood | 0.6933 | 0.6225 | 0.4891 |
| GEO_GSE311681_GENERIC_XENIUM_EXPANDED | marker_only | 0.6912 | 0.6230 | 0.3905 |
| GEO_GSE311681_GENERIC_XENIUM_EXPANDED | marker_reference_profile | 0.6724 | 0.5924 | 0.4714 |
| GEO_GSE311681_GENERIC_XENIUM_EXPANDED | reference_profile | 0.5529 | 0.4617 | 0.5523 |
| GEO_GSE317755_GENERIC_H5AD_EXPANDED | learned_permuted_prior | 0.6578 | 0.6170 | 0.5063 |
| GEO_GSE317755_GENERIC_H5AD_EXPANDED | learned_random_graph | 0.6581 | 0.6120 | 0.5643 |
| GEO_GSE317755_GENERIC_H5AD_EXPANDED | marker_context_specific_neighborhood | 0.6446 | 0.6034 | 0.6653 |
| GEO_GSE317755_GENERIC_H5AD_EXPANDED | marker_learned_neighborhood | 0.6631 | 0.6165 | 0.5254 |
| GEO_GSE317755_GENERIC_H5AD_EXPANDED | marker_only | 0.6449 | 0.6001 | 0.3783 |
| GEO_GSE317755_GENERIC_H5AD_EXPANDED | marker_reference_profile | 0.6543 | 0.6094 | 0.4862 |
| GEO_GSE317755_GENERIC_H5AD_EXPANDED | reference_profile | 0.5345 | 0.4672 | 0.5389 |
| GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED | learned_permuted_prior | 0.3859 | 0.2982 | 0.6863 |
| GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED | learned_random_graph | 0.3879 | 0.3009 | 0.6533 |
| GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED | marker_context_specific_neighborhood | 0.3859 | 0.2985 | 0.6895 |
| GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED | marker_learned_neighborhood | 0.3889 | 0.3015 | 0.6557 |
| GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED | marker_only | 0.3883 | 0.3004 | 0.5095 |
| GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED | marker_reference_profile | 0.3671 | 0.2805 | 0.6937 |
| GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED | reference_profile | 0.2470 | 0.1898 | 0.7107 |
| GEO_GSE326743_GENERIC_XENIUM_EXPANDED | learned_permuted_prior | 0.5772 | 0.5255 | 0.4943 |
| GEO_GSE326743_GENERIC_XENIUM_EXPANDED | learned_random_graph | 0.5780 | 0.5249 | 0.4456 |
| GEO_GSE326743_GENERIC_XENIUM_EXPANDED | marker_context_specific_neighborhood | 0.5838 | 0.5311 | 0.4785 |
| GEO_GSE326743_GENERIC_XENIUM_EXPANDED | marker_learned_neighborhood | 0.5828 | 0.5303 | 0.4974 |
| GEO_GSE326743_GENERIC_XENIUM_EXPANDED | marker_only | 0.5801 | 0.5272 | 0.3298 |
| GEO_GSE326743_GENERIC_XENIUM_EXPANDED | marker_reference_profile | 0.5719 | 0.5193 | 0.5676 |
| GEO_GSE326743_GENERIC_XENIUM_EXPANDED | reference_profile | 0.3941 | 0.3769 | 0.6757 |
| GEO_GSE327129_GENERIC_H5AD_EXPANDED | learned_permuted_prior | 0.4958 | 0.4814 | 0.3006 |
| GEO_GSE327129_GENERIC_H5AD_EXPANDED | learned_random_graph | 0.4961 | 0.4822 | 0.3311 |
| GEO_GSE327129_GENERIC_H5AD_EXPANDED | marker_context_specific_neighborhood | 0.4990 | 0.4843 | 0.4175 |
| GEO_GSE327129_GENERIC_H5AD_EXPANDED | marker_learned_neighborhood | 0.4958 | 0.4813 | 0.2999 |
| GEO_GSE327129_GENERIC_H5AD_EXPANDED | marker_only | 0.5039 | 0.4901 | 0.1547 |
| GEO_GSE327129_GENERIC_H5AD_EXPANDED | marker_reference_profile | 0.5092 | 0.4906 | 0.2986 |
| GEO_GSE327129_GENERIC_H5AD_EXPANDED | reference_profile | 0.4898 | 0.4798 | 0.2487 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | learned_permuted_prior | 0.5322 | 0.5046 | 0.6135 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | learned_random_graph | 0.5285 | 0.5007 | 0.5742 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | marker_context_specific_neighborhood | 0.5411 | 0.5121 | 0.5960 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | marker_learned_neighborhood | 0.5412 | 0.5129 | 0.6004 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | marker_only | 0.5319 | 0.5040 | 0.4127 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | marker_reference_profile | 0.5077 | 0.4721 | 0.6507 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | reference_profile | 0.2614 | 0.2129 | 0.7693 |
| GEO_GSE328481_GENERIC_H5AD_EXPANDED | learned_permuted_prior | 0.4860 | 0.4684 | 0.5031 |
| GEO_GSE328481_GENERIC_H5AD_EXPANDED | learned_random_graph | 0.4771 | 0.4573 | 0.5633 |
| GEO_GSE328481_GENERIC_H5AD_EXPANDED | marker_context_specific_neighborhood | 0.4595 | 0.4429 | 0.5813 |
| GEO_GSE328481_GENERIC_H5AD_EXPANDED | marker_learned_neighborhood | 0.4833 | 0.4647 | 0.5003 |
| GEO_GSE328481_GENERIC_H5AD_EXPANDED | marker_only | 0.4523 | 0.4369 | 0.2717 |
| GEO_GSE328481_GENERIC_H5AD_EXPANDED | marker_reference_profile | 0.4561 | 0.4340 | 0.5265 |
| GEO_GSE328481_GENERIC_H5AD_EXPANDED | reference_profile | 0.3859 | 0.3514 | 0.5107 |
| GEO_GSE330849_GENERIC_H5AD_EXPANDED | learned_permuted_prior | 0.7940 | 0.7903 | 0.4624 |
| GEO_GSE330849_GENERIC_H5AD_EXPANDED | learned_random_graph | 0.7908 | 0.7854 | 0.5349 |
| GEO_GSE330849_GENERIC_H5AD_EXPANDED | marker_context_specific_neighborhood | 0.7908 | 0.7863 | 0.4601 |
| GEO_GSE330849_GENERIC_H5AD_EXPANDED | marker_learned_neighborhood | 0.7928 | 0.7876 | 0.4230 |
| GEO_GSE330849_GENERIC_H5AD_EXPANDED | marker_only | 0.7886 | 0.7844 | 0.2357 |
| GEO_GSE330849_GENERIC_H5AD_EXPANDED | marker_reference_profile | 0.7956 | 0.7866 | 0.2335 |
| GEO_GSE330849_GENERIC_H5AD_EXPANDED | reference_profile | 0.7779 | 0.7631 | 0.2212 |
| GEO_GSE333479_H5AD_SIDECAR_EXPANDED | learned_permuted_prior | 0.3688 | 0.2963 | 0.7011 |
| GEO_GSE333479_H5AD_SIDECAR_EXPANDED | learned_random_graph | 0.3588 | 0.2919 | 0.7324 |
| GEO_GSE333479_H5AD_SIDECAR_EXPANDED | marker_context_specific_neighborhood | 0.3569 | 0.2885 | 0.8015 |
| GEO_GSE333479_H5AD_SIDECAR_EXPANDED | marker_learned_neighborhood | 0.3584 | 0.2899 | 0.7352 |
| GEO_GSE333479_H5AD_SIDECAR_EXPANDED | marker_only | 0.3575 | 0.2893 | 0.6336 |
| GEO_GSE333479_H5AD_SIDECAR_EXPANDED | marker_reference_profile | 0.3406 | 0.2852 | 0.8040 |
| GEO_GSE333479_H5AD_SIDECAR_EXPANDED | reference_profile | 0.2478 | 0.1933 | 0.8706 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | learned_permuted_prior | 0.7560 | 0.6848 | 0.5778 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | learned_random_graph | 0.7563 | 0.6786 | 0.6341 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | marker_context_specific_neighborhood | 0.7584 | 0.6866 | 0.5861 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | marker_learned_neighborhood | 0.7588 | 0.6866 | 0.5501 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | marker_only | 0.7632 | 0.6870 | 0.1868 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | marker_reference_profile | 0.7719 | 0.6997 | 0.1829 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | reference_profile | 0.7724 | 0.7034 | 0.1801 |
| GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED | learned_permuted_prior | 0.3092 | 0.2291 | 0.6079 |
| GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED | learned_random_graph | 0.3092 | 0.2290 | 0.6173 |
| GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED | marker_context_specific_neighborhood | 0.3120 | 0.2305 | 0.5845 |
| GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED | marker_learned_neighborhood | 0.3119 | 0.2305 | 0.5902 |
| GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED | marker_only | 0.3129 | 0.2325 | 0.4334 |
| GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED | marker_reference_profile | 0.2875 | 0.2340 | 0.6779 |
| GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED | reference_profile | 0.1442 | 0.1571 | 0.8422 |
| GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED | learned_permuted_prior | 0.5938 | 0.5807 | 0.5738 |
| GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED | learned_random_graph | 0.5923 | 0.5785 | 0.5982 |
| GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED | marker_context_specific_neighborhood | 0.5961 | 0.5825 | 0.6249 |
| GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED | marker_learned_neighborhood | 0.5951 | 0.5812 | 0.5895 |
| GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED | marker_only | 0.5958 | 0.5816 | 0.2962 |
| GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED | marker_reference_profile | 0.6129 | 0.6014 | 0.4838 |
| GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED | reference_profile | 0.5363 | 0.5356 | 0.6558 |
| GSE202623_CELLTYPE_EXPANDED | learned_permuted_prior | 0.6264 | 0.5755 | 0.6047 |
| GSE202623_CELLTYPE_EXPANDED | learned_random_graph | 0.6397 | 0.5877 | 0.5681 |
| GSE202623_CELLTYPE_EXPANDED | marker_context_specific_neighborhood | 0.6354 | 0.5856 | 0.5797 |
| GSE202623_CELLTYPE_EXPANDED | marker_learned_neighborhood | 0.6402 | 0.5881 | 0.5674 |
| GSE202623_CELLTYPE_EXPANDED | marker_only | 0.6346 | 0.5854 | 0.4451 |
| GSE202623_CELLTYPE_EXPANDED | marker_reference_profile | 0.6339 | 0.5744 | 0.5394 |
| GSE202623_CELLTYPE_EXPANDED | reference_profile | 0.5512 | 0.4562 | 0.5937 |
| SQUIDPY_MERFISH_EXPANDED | learned_permuted_prior | 0.5857 | 0.4853 | 0.6669 |
| SQUIDPY_MERFISH_EXPANDED | learned_random_graph | 0.5911 | 0.5006 | 0.6735 |
| SQUIDPY_MERFISH_EXPANDED | marker_context_specific_neighborhood | 0.5867 | 0.4936 | 0.6530 |
| SQUIDPY_MERFISH_EXPANDED | marker_learned_neighborhood | 0.5876 | 0.4867 | 0.6552 |
| SQUIDPY_MERFISH_EXPANDED | marker_only | 0.5960 | 0.5122 | 0.4335 |
| SQUIDPY_MERFISH_EXPANDED | marker_reference_profile | 0.6008 | 0.4717 | 0.5096 |
| SQUIDPY_MERFISH_EXPANDED | reference_profile | 0.5716 | 0.4325 | 0.4994 |
| SQUIDPY_SEQFISH_EXPANDED | learned_permuted_prior | 0.6136 | 0.5142 | 0.6015 |
| SQUIDPY_SEQFISH_EXPANDED | learned_random_graph | 0.6125 | 0.5068 | 0.5962 |
| SQUIDPY_SEQFISH_EXPANDED | marker_context_specific_neighborhood | 0.6034 | 0.4978 | 0.5919 |
| SQUIDPY_SEQFISH_EXPANDED | marker_learned_neighborhood | 0.6152 | 0.5064 | 0.4992 |
| SQUIDPY_SEQFISH_EXPANDED | marker_only | 0.6060 | 0.5028 | 0.3976 |
| SQUIDPY_SEQFISH_EXPANDED | marker_reference_profile | 0.5569 | 0.4733 | 0.5306 |
| SQUIDPY_SEQFISH_EXPANDED | reference_profile | 0.4069 | 0.3587 | 0.4806 |
| SQUIDPY_SLIDESEQV2_EXPANDED | learned_permuted_prior | 0.4192 | 0.3962 | 0.6418 |
| SQUIDPY_SLIDESEQV2_EXPANDED | learned_random_graph | 0.4151 | 0.3921 | 0.6658 |
| SQUIDPY_SLIDESEQV2_EXPANDED | marker_context_specific_neighborhood | 0.4148 | 0.3936 | 0.6878 |
| SQUIDPY_SLIDESEQV2_EXPANDED | marker_learned_neighborhood | 0.4189 | 0.3964 | 0.6354 |
| SQUIDPY_SLIDESEQV2_EXPANDED | marker_only | 0.4170 | 0.3952 | 0.5092 |
| SQUIDPY_SLIDESEQV2_EXPANDED | marker_reference_profile | 0.4016 | 0.3649 | 0.6230 |
| SQUIDPY_SLIDESEQV2_EXPANDED | reference_profile | 0.3482 | 0.2920 | 0.6117 |

## Specificity Guardrail

| dataset | context delta macro-F1 | context pass | learned delta macro-F1 | learned pass | interpretation |
|---|---:|---|---:|---|---|
| GEO_GSE245263_GENERIC_H5AD_EXPANDED | -0.0384 | no | -0.0616 | no | context signal is not specific under null controls |
| GEO_GSE263450_GENERIC_H5AD_EXPANDED | -0.0009 | no | +0.0066 | yes | learned neighborhood passes null guardrail |
| GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED | -0.0023 | no | +0.0016 | no | context signal is not specific under null controls |
| GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED | -0.1118 | no | -0.0000 | no | context signal is not specific under null controls |
| GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED | -0.0011 | no | +0.0029 | no | context signal is not specific under null controls |
| GEO_GSE279181_H5AD_COMPOSITION_EXPANDED | -0.0167 | no | -0.0061 | no | context signal is not specific under null controls |
| GEO_GSE280376_GENERIC_XENIUM_EXPANDED | -0.0003 | no | -0.0015 | no | context signal is not specific under null controls |
| GEO_GSE282127_GENERIC_H5AD_EXPANDED | +0.0015 | no | +0.0033 | no | context signal is not specific under null controls |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | +0.0011 | no | -0.0013 | no | context signal is not specific under null controls |
| GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED | -0.0052 | no | -0.0083 | no | context signal is not specific under null controls |
| GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED | +0.0003 | no | +0.0003 | no | context signal is not specific under null controls |
| GEO_GSE294759_GENERIC_H5AD_EXPANDED | +0.0000 | no | -0.0001 | no | context signal is not specific under null controls |
| GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED | -0.0052 | no | +0.0005 | no | context signal is not specific under null controls |
| GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED | -0.0045 | no | +0.0006 | no | context signal is not specific under null controls |
| GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED | -0.0070 | no | +0.0003 | no | context signal is not specific under null controls |
| GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED | -0.0253 | no | -0.0134 | no | context signal is not specific under null controls |
| GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED | -0.0053 | no | -0.0094 | no | context signal is not specific under null controls |
| GEO_GSE308624_GENERIC_H5AD_EXPANDED | -0.0014 | no | +0.0019 | no | context signal is not specific under null controls |
| GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED | -0.0093 | no | +0.0106 | yes | learned neighborhood passes null guardrail |
| GEO_GSE310129_GENERIC_H5AD_EXPANDED | -0.0286 | no | -0.0113 | no | context signal is not specific under null controls |
| GEO_GSE311681_GENERIC_XENIUM_EXPANDED | -0.0006 | no | -0.0005 | no | context signal is not specific under null controls |
| GEO_GSE317755_GENERIC_H5AD_EXPANDED | -0.0136 | no | -0.0005 | no | context signal is not specific under null controls |
| GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED | -0.0031 | no | +0.0006 | no | context signal is not specific under null controls |
| GEO_GSE326743_GENERIC_XENIUM_EXPANDED | +0.0008 | no | +0.0030 | no | context signal is not specific under null controls |
| GEO_GSE327129_GENERIC_H5AD_EXPANDED | -0.0058 | no | -0.0088 | no | context signal is not specific under null controls |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | -0.0008 | no | +0.0083 | yes | learned neighborhood passes null guardrail |
| GEO_GSE328481_GENERIC_H5AD_EXPANDED | -0.0256 | no | -0.0037 | no | context signal is not specific under null controls |
| GEO_GSE330849_GENERIC_H5AD_EXPANDED | -0.0040 | no | -0.0027 | no | context signal is not specific under null controls |
| GEO_GSE333479_H5AD_SIDECAR_EXPANDED | -0.0078 | no | -0.0064 | no | context signal is not specific under null controls |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | -0.0004 | no | -0.0004 | no | context signal is not specific under null controls |
| GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED | -0.0020 | no | -0.0020 | no | context signal is not specific under null controls |
| GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED | +0.0009 | no | -0.0004 | no | context signal is not specific under null controls |
| GSE202623_CELLTYPE_EXPANDED | -0.0025 | no | +0.0003 | no | context signal is not specific under null controls |
| SQUIDPY_MERFISH_EXPANDED | -0.0186 | no | -0.0255 | no | context signal is not specific under null controls |
| SQUIDPY_SEQFISH_EXPANDED | -0.0164 | no | -0.0078 | no | context signal is not specific under null controls |
| SQUIDPY_SLIDESEQV2_EXPANDED | -0.0028 | no | +0.0002 | no | context signal is not specific under null controls |

## Paired Comparisons vs Marker-Only

| dataset | comparator | accuracy diff | McNemar p |
|---|---|---:|---:|
| GEO_GSE245263_GENERIC_H5AD_EXPANDED | learned_permuted_prior | +0.0222 | 0.003479 |
| GEO_GSE245263_GENERIC_H5AD_EXPANDED | learned_random_graph | -0.0060 | 0.402 |
| GEO_GSE245263_GENERIC_H5AD_EXPANDED | marker_context_specific_neighborhood | -0.0088 | 0.1903 |
| GEO_GSE245263_GENERIC_H5AD_EXPANDED | marker_learned_neighborhood | -0.0380 | 6.971e-06 |
| GEO_GSE245263_GENERIC_H5AD_EXPANDED | marker_reference_profile | -0.0139 | 0.152 |
| GEO_GSE245263_GENERIC_H5AD_EXPANDED | reference_profile | -0.0918 | 5.379e-13 |
| GEO_GSE263450_GENERIC_H5AD_EXPANDED | learned_permuted_prior | +0.0000 | 1 |
| GEO_GSE263450_GENERIC_H5AD_EXPANDED | learned_random_graph | +0.0106 | 4.272e-25 |
| GEO_GSE263450_GENERIC_H5AD_EXPANDED | marker_context_specific_neighborhood | +0.0166 | 5.138e-56 |
| GEO_GSE263450_GENERIC_H5AD_EXPANDED | marker_learned_neighborhood | +0.0181 | 1.312e-72 |
| GEO_GSE263450_GENERIC_H5AD_EXPANDED | marker_reference_profile | +0.1044 | 0 |
| GEO_GSE263450_GENERIC_H5AD_EXPANDED | reference_profile | +0.0600 | 1.237e-91 |
| GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED | learned_permuted_prior | -0.0008 | 0.7604 |
| GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED | learned_random_graph | -0.0025 | 0.3157 |
| GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED | marker_context_specific_neighborhood | -0.0013 | 0.587 |
| GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED | marker_learned_neighborhood | -0.0009 | 0.7381 |
| GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED | marker_reference_profile | +0.0026 | 0.3929 |
| GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED | reference_profile | -0.1191 | 3.9e-99 |
| GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED | learned_permuted_prior | +0.0062 | 0.002654 |
| GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED | learned_random_graph | +0.0062 | 0.003854 |
| GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED | marker_context_specific_neighborhood | -0.1044 | 4.066e-65 |
| GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED | marker_learned_neighborhood | +0.0062 | 0.002654 |
| GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED | marker_reference_profile | -0.0172 | 0.001119 |
| GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED | reference_profile | -0.1092 | 1.042e-47 |
| GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED | learned_permuted_prior | -0.0044 | 0.001195 |
| GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED | learned_random_graph | -0.0009 | 0.4431 |
| GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED | marker_context_specific_neighborhood | +0.0016 | 0.153 |
| GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED | marker_learned_neighborhood | +0.0027 | 0.01584 |
| GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED | marker_reference_profile | -0.0037 | 0.09663 |
| GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED | reference_profile | -0.1355 | 0 |
| GEO_GSE279181_H5AD_COMPOSITION_EXPANDED | learned_permuted_prior | +0.0212 | 2.544e-30 |
| GEO_GSE279181_H5AD_COMPOSITION_EXPANDED | learned_random_graph | +0.0164 | 6.67e-17 |
| GEO_GSE279181_H5AD_COMPOSITION_EXPANDED | marker_context_specific_neighborhood | +0.0049 | 0.002825 |
| GEO_GSE279181_H5AD_COMPOSITION_EXPANDED | marker_learned_neighborhood | +0.0175 | 1.15e-26 |
| GEO_GSE279181_H5AD_COMPOSITION_EXPANDED | marker_reference_profile | +0.0095 | 0.00126 |
| GEO_GSE279181_H5AD_COMPOSITION_EXPANDED | reference_profile | -0.0431 | 8.892e-17 |
| GEO_GSE280376_GENERIC_XENIUM_EXPANDED | learned_permuted_prior | -0.0008 | 0.1225 |
| GEO_GSE280376_GENERIC_XENIUM_EXPANDED | learned_random_graph | -0.0044 | 3.72e-20 |
| GEO_GSE280376_GENERIC_XENIUM_EXPANDED | marker_context_specific_neighborhood | -0.0009 | 0.06066 |
| GEO_GSE280376_GENERIC_XENIUM_EXPANDED | marker_learned_neighborhood | -0.0026 | 4.209e-08 |
| GEO_GSE280376_GENERIC_XENIUM_EXPANDED | marker_reference_profile | +0.0270 | 1.43e-187 |
| GEO_GSE280376_GENERIC_XENIUM_EXPANDED | reference_profile | +0.0258 | 4.752e-126 |
| GEO_GSE282127_GENERIC_H5AD_EXPANDED | learned_permuted_prior | +0.0044 | 4.853e-10 |
| GEO_GSE282127_GENERIC_H5AD_EXPANDED | learned_random_graph | +0.0030 | 7.131e-06 |
| GEO_GSE282127_GENERIC_H5AD_EXPANDED | marker_context_specific_neighborhood | +0.0086 | 3.087e-38 |
| GEO_GSE282127_GENERIC_H5AD_EXPANDED | marker_learned_neighborhood | +0.0072 | 1.546e-24 |
| GEO_GSE282127_GENERIC_H5AD_EXPANDED | marker_reference_profile | -0.0021 | 0.04392 |
| GEO_GSE282127_GENERIC_H5AD_EXPANDED | reference_profile | -0.0330 | 8.327e-108 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | learned_permuted_prior | -0.0161 | 1.346e-25 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | learned_random_graph | -0.0030 | 0.005091 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | marker_context_specific_neighborhood | +0.0014 | 0.2506 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | marker_learned_neighborhood | -0.0020 | 0.06625 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | marker_reference_profile | -0.0569 | 6.068e-96 |
| GEO_GSE284005_MERSCOPE_MS_EXPANDED | reference_profile | -0.1601 | 0 |
| GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED | learned_permuted_prior | -0.0076 | 2.464e-08 |
| GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED | learned_random_graph | -0.0048 | 0.0001591 |
| GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED | marker_context_specific_neighborhood | -0.0044 | 0.0006873 |
| GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED | marker_learned_neighborhood | -0.0063 | 4.767e-07 |
| GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED | marker_reference_profile | +0.0061 | 0.003702 |
| GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED | reference_profile | -0.0322 | 1.537e-25 |
| GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED | learned_permuted_prior | -0.0042 | 0.000222 |
| GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED | learned_random_graph | -0.0031 | 0.001747 |
| GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED | marker_context_specific_neighborhood | +0.0004 | 0.7023 |
| GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED | marker_learned_neighborhood | -0.0003 | 0.7692 |
| GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED | marker_reference_profile | -0.0053 | 0.005594 |
| GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED | reference_profile | -0.1609 | 0 |
| GEO_GSE294759_GENERIC_H5AD_EXPANDED | learned_permuted_prior | +0.0063 | 9.134e-11 |
| GEO_GSE294759_GENERIC_H5AD_EXPANDED | learned_random_graph | +0.0075 | 1.251e-32 |
| GEO_GSE294759_GENERIC_H5AD_EXPANDED | marker_context_specific_neighborhood | +0.0080 | 3.066e-34 |
| GEO_GSE294759_GENERIC_H5AD_EXPANDED | marker_learned_neighborhood | +0.0092 | 4.555e-45 |
| GEO_GSE294759_GENERIC_H5AD_EXPANDED | marker_reference_profile | +0.0773 | 0 |
| GEO_GSE294759_GENERIC_H5AD_EXPANDED | reference_profile | +0.0622 | 6.515e-158 |
| GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED | learned_permuted_prior | +0.0050 | 6.602e-08 |
| GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED | learned_random_graph | +0.0037 | 2.006e-06 |
| GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED | marker_context_specific_neighborhood | +0.0016 | 0.05626 |
| GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED | marker_learned_neighborhood | +0.0074 | 2.162e-21 |
| GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED | marker_reference_profile | -0.0171 | 1.132e-28 |
| GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED | reference_profile | -0.2491 | 0 |
| GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED | learned_permuted_prior | +0.0046 | 0.0005323 |
| GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED | learned_random_graph | -0.0038 | 0.001286 |
| GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED | marker_context_specific_neighborhood | +0.0017 | 0.1535 |
| GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED | marker_learned_neighborhood | +0.0062 | 1.856e-07 |
| GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED | marker_reference_profile | -0.0028 | 0.1572 |
| GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED | reference_profile | -0.0821 | 2.369e-175 |
| GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED | learned_permuted_prior | +0.0022 | 0.1486 |
| GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED | learned_random_graph | +0.0171 | 1.577e-44 |
| GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED | marker_context_specific_neighborhood | +0.0060 | 1.406e-05 |
| GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED | marker_learned_neighborhood | +0.0167 | 2.626e-42 |
| GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED | marker_reference_profile | +0.0026 | 0.362 |
| GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED | reference_profile | -0.1053 | 2.881e-151 |
| GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED | learned_permuted_prior | +0.0180 | 8.535e-06 |
| GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED | learned_random_graph | +0.0003 | 1 |
| GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED | marker_context_specific_neighborhood | -0.0008 | 0.8806 |
| GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED | marker_learned_neighborhood | +0.0057 | 0.05716 |
| GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED | marker_reference_profile | +0.0353 | 1.002e-10 |
| GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED | reference_profile | -0.0105 | 0.2135 |
| GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED | learned_permuted_prior | -0.0159 | 3.557e-17 |
| GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED | learned_random_graph | -0.0046 | 0.02248 |
| GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED | marker_context_specific_neighborhood | -0.0070 | 0.0001961 |
| GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED | marker_learned_neighborhood | -0.0122 | 1.309e-11 |
| GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED | marker_reference_profile | +0.0162 | 4.255e-08 |
| GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED | reference_profile | -0.0013 | 0.8212 |
| GEO_GSE308624_GENERIC_H5AD_EXPANDED | learned_permuted_prior | -0.0008 | 0.6057 |
| GEO_GSE308624_GENERIC_H5AD_EXPANDED | learned_random_graph | -0.0028 | 0.04004 |
| GEO_GSE308624_GENERIC_H5AD_EXPANDED | marker_context_specific_neighborhood | -0.0008 | 0.578 |
| GEO_GSE308624_GENERIC_H5AD_EXPANDED | marker_learned_neighborhood | +0.0012 | 0.3908 |
| GEO_GSE308624_GENERIC_H5AD_EXPANDED | marker_reference_profile | -0.0069 | 0.0004603 |
| GEO_GSE308624_GENERIC_H5AD_EXPANDED | reference_profile | -0.0446 | 2.789e-60 |
| GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED | learned_permuted_prior | +0.0078 | 0.0242 |
| GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED | learned_random_graph | +0.0102 | 0.0007408 |
| GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED | marker_context_specific_neighborhood | +0.0086 | 0.01851 |
| GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED | marker_learned_neighborhood | +0.0204 | 1.52e-10 |
| GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED | marker_reference_profile | +0.0699 | 1.181e-29 |
| GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED | reference_profile | +0.0540 | 2.488e-09 |
| GEO_GSE310129_GENERIC_H5AD_EXPANDED | learned_permuted_prior | +0.0380 | 8.66e-121 |
| GEO_GSE310129_GENERIC_H5AD_EXPANDED | learned_random_graph | +0.0276 | 1.456e-82 |
| GEO_GSE310129_GENERIC_H5AD_EXPANDED | marker_context_specific_neighborhood | +0.0075 | 1.102e-08 |
| GEO_GSE310129_GENERIC_H5AD_EXPANDED | marker_learned_neighborhood | +0.0271 | 9.344e-80 |
| GEO_GSE310129_GENERIC_H5AD_EXPANDED | marker_reference_profile | +0.0979 | 0 |
| GEO_GSE310129_GENERIC_H5AD_EXPANDED | reference_profile | +0.1308 | 2.513e-311 |
| GEO_GSE311681_GENERIC_XENIUM_EXPANDED | learned_permuted_prior | -0.0080 | 2.012e-09 |
| GEO_GSE311681_GENERIC_XENIUM_EXPANDED | learned_random_graph | -0.0030 | 0.0005163 |
| GEO_GSE311681_GENERIC_XENIUM_EXPANDED | marker_context_specific_neighborhood | +0.0010 | 0.2667 |
| GEO_GSE311681_GENERIC_XENIUM_EXPANDED | marker_learned_neighborhood | +0.0021 | 0.009196 |
| GEO_GSE311681_GENERIC_XENIUM_EXPANDED | marker_reference_profile | -0.0188 | 1.974e-22 |
| GEO_GSE311681_GENERIC_XENIUM_EXPANDED | reference_profile | -0.1383 | 0 |
| GEO_GSE317755_GENERIC_H5AD_EXPANDED | learned_permuted_prior | +0.0129 | 0.001647 |
| GEO_GSE317755_GENERIC_H5AD_EXPANDED | learned_random_graph | +0.0132 | 0.00023 |
| GEO_GSE317755_GENERIC_H5AD_EXPANDED | marker_context_specific_neighborhood | -0.0003 | 1 |
| GEO_GSE317755_GENERIC_H5AD_EXPANDED | marker_learned_neighborhood | +0.0182 | 3.734e-07 |
| GEO_GSE317755_GENERIC_H5AD_EXPANDED | marker_reference_profile | +0.0094 | 0.1449 |
| GEO_GSE317755_GENERIC_H5AD_EXPANDED | reference_profile | -0.1104 | 3.709e-30 |
| GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED | learned_permuted_prior | -0.0024 | 0.1105 |
| GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED | learned_random_graph | -0.0004 | 0.7729 |
| GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED | marker_context_specific_neighborhood | -0.0024 | 0.07056 |
| GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED | marker_learned_neighborhood | +0.0006 | 0.645 |
| GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED | marker_reference_profile | -0.0212 | 1.845e-21 |
| GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED | reference_profile | -0.1413 | 0 |
| GEO_GSE326743_GENERIC_XENIUM_EXPANDED | learned_permuted_prior | -0.0029 | 0.0003484 |
| GEO_GSE326743_GENERIC_XENIUM_EXPANDED | learned_random_graph | -0.0021 | 5.737e-05 |
| GEO_GSE326743_GENERIC_XENIUM_EXPANDED | marker_context_specific_neighborhood | +0.0037 | 6.464e-10 |
| GEO_GSE326743_GENERIC_XENIUM_EXPANDED | marker_learned_neighborhood | +0.0027 | 2.297e-05 |
| GEO_GSE326743_GENERIC_XENIUM_EXPANDED | marker_reference_profile | -0.0082 | 3.042e-08 |
| GEO_GSE326743_GENERIC_XENIUM_EXPANDED | reference_profile | -0.1860 | 0 |
| GEO_GSE327129_GENERIC_H5AD_EXPANDED | learned_permuted_prior | -0.0081 | 8.566e-06 |
| GEO_GSE327129_GENERIC_H5AD_EXPANDED | learned_random_graph | -0.0078 | 5.925e-05 |
| GEO_GSE327129_GENERIC_H5AD_EXPANDED | marker_context_specific_neighborhood | -0.0049 | 0.03104 |
| GEO_GSE327129_GENERIC_H5AD_EXPANDED | marker_learned_neighborhood | -0.0081 | 9.688e-06 |
| GEO_GSE327129_GENERIC_H5AD_EXPANDED | marker_reference_profile | +0.0053 | 0.1874 |
| GEO_GSE327129_GENERIC_H5AD_EXPANDED | reference_profile | -0.0141 | 0.02025 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | learned_permuted_prior | +0.0002 | 0.9071 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | learned_random_graph | -0.0034 | 0.006532 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | marker_context_specific_neighborhood | +0.0092 | 1.515e-12 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | marker_learned_neighborhood | +0.0093 | 7.502e-13 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | marker_reference_profile | -0.0243 | 3.082e-22 |
| GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED | reference_profile | -0.2705 | 0 |
| GEO_GSE328481_GENERIC_H5AD_EXPANDED | learned_permuted_prior | +0.0337 | 2.345e-80 |
| GEO_GSE328481_GENERIC_H5AD_EXPANDED | learned_random_graph | +0.0247 | 2.524e-46 |
| GEO_GSE328481_GENERIC_H5AD_EXPANDED | marker_context_specific_neighborhood | +0.0072 | 5.124e-06 |
| GEO_GSE328481_GENERIC_H5AD_EXPANDED | marker_learned_neighborhood | +0.0309 | 1.04e-84 |
| GEO_GSE328481_GENERIC_H5AD_EXPANDED | marker_reference_profile | +0.0037 | 0.1444 |
| GEO_GSE328481_GENERIC_H5AD_EXPANDED | reference_profile | -0.0665 | 5.184e-51 |
| GEO_GSE330849_GENERIC_H5AD_EXPANDED | learned_permuted_prior | +0.0053 | 5.688e-10 |
| GEO_GSE330849_GENERIC_H5AD_EXPANDED | learned_random_graph | +0.0022 | 0.005269 |
| GEO_GSE330849_GENERIC_H5AD_EXPANDED | marker_context_specific_neighborhood | +0.0021 | 0.006948 |
| GEO_GSE330849_GENERIC_H5AD_EXPANDED | marker_learned_neighborhood | +0.0041 | 3.915e-07 |
| GEO_GSE330849_GENERIC_H5AD_EXPANDED | marker_reference_profile | +0.0069 | 1.658e-09 |
| GEO_GSE330849_GENERIC_H5AD_EXPANDED | reference_profile | -0.0108 | 2.399e-12 |
| GEO_GSE333479_H5AD_SIDECAR_EXPANDED | learned_permuted_prior | +0.0113 | 1.238e-15 |
| GEO_GSE333479_H5AD_SIDECAR_EXPANDED | learned_random_graph | +0.0012 | 0.3194 |
| GEO_GSE333479_H5AD_SIDECAR_EXPANDED | marker_context_specific_neighborhood | -0.0007 | 0.5881 |
| GEO_GSE333479_H5AD_SIDECAR_EXPANDED | marker_learned_neighborhood | +0.0009 | 0.4891 |
| GEO_GSE333479_H5AD_SIDECAR_EXPANDED | marker_reference_profile | -0.0169 | 1.11e-08 |
| GEO_GSE333479_H5AD_SIDECAR_EXPANDED | reference_profile | -0.1097 | 8.806e-142 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | learned_permuted_prior | -0.0073 | 6.993e-07 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | learned_random_graph | -0.0070 | 6.198e-06 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | marker_context_specific_neighborhood | -0.0049 | 0.001019 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | marker_learned_neighborhood | -0.0044 | 0.002344 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | marker_reference_profile | +0.0087 | 6.191e-13 |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED | reference_profile | +0.0092 | 7.294e-08 |
| GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED | learned_permuted_prior | -0.0037 | 3.442e-11 |
| GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED | learned_random_graph | -0.0036 | 8.746e-12 |
| GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED | marker_context_specific_neighborhood | -0.0008 | 0.1254 |
| GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED | marker_learned_neighborhood | -0.0010 | 0.07522 |
| GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED | marker_reference_profile | -0.0254 | 3.705e-166 |
| GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED | reference_profile | -0.1687 | 0 |
| GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED | learned_permuted_prior | -0.0019 | 0.213 |
| GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED | learned_random_graph | -0.0034 | 0.0122 |
| GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED | marker_context_specific_neighborhood | +0.0003 | 0.8336 |
| GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED | marker_learned_neighborhood | -0.0006 | 0.6673 |
| GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED | marker_reference_profile | +0.0172 | 1.592e-16 |
| GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED | reference_profile | -0.0594 | 3.427e-54 |
| GSE202623_CELLTYPE_EXPANDED | learned_permuted_prior | -0.0082 | 1.673e-10 |
| GSE202623_CELLTYPE_EXPANDED | learned_random_graph | +0.0052 | 3.436e-08 |
| GSE202623_CELLTYPE_EXPANDED | marker_context_specific_neighborhood | +0.0009 | 0.4322 |
| GSE202623_CELLTYPE_EXPANDED | marker_learned_neighborhood | +0.0056 | 2.352e-09 |
| GSE202623_CELLTYPE_EXPANDED | marker_reference_profile | -0.0007 | 0.7542 |
| GSE202623_CELLTYPE_EXPANDED | reference_profile | -0.0834 | 5.413e-208 |
| SQUIDPY_MERFISH_EXPANDED | learned_permuted_prior | -0.0103 | 1.657e-35 |
| SQUIDPY_MERFISH_EXPANDED | learned_random_graph | -0.0049 | 9.916e-12 |
| SQUIDPY_MERFISH_EXPANDED | marker_context_specific_neighborhood | -0.0093 | 2.991e-31 |
| SQUIDPY_MERFISH_EXPANDED | marker_learned_neighborhood | -0.0084 | 1.81e-29 |
| SQUIDPY_MERFISH_EXPANDED | marker_reference_profile | +0.0048 | 9.965e-07 |
| SQUIDPY_MERFISH_EXPANDED | reference_profile | -0.0244 | 2.399e-77 |
| SQUIDPY_SEQFISH_EXPANDED | learned_permuted_prior | +0.0076 | 3.001e-06 |
| SQUIDPY_SEQFISH_EXPANDED | learned_random_graph | +0.0065 | 1.789e-05 |
| SQUIDPY_SEQFISH_EXPANDED | marker_context_specific_neighborhood | -0.0026 | 0.07021 |
| SQUIDPY_SEQFISH_EXPANDED | marker_learned_neighborhood | +0.0092 | 3.821e-11 |
| SQUIDPY_SEQFISH_EXPANDED | marker_reference_profile | -0.0491 | 4.884e-54 |
| SQUIDPY_SEQFISH_EXPANDED | reference_profile | -0.1991 | 0 |
| SQUIDPY_SLIDESEQV2_EXPANDED | learned_permuted_prior | +0.0022 | 0.1523 |
| SQUIDPY_SLIDESEQV2_EXPANDED | learned_random_graph | -0.0019 | 0.1415 |
| SQUIDPY_SLIDESEQV2_EXPANDED | marker_context_specific_neighborhood | -0.0022 | 0.1107 |
| SQUIDPY_SLIDESEQV2_EXPANDED | marker_learned_neighborhood | +0.0019 | 0.0981 |
| SQUIDPY_SLIDESEQV2_EXPANDED | marker_reference_profile | -0.0154 | 1.434e-10 |
| SQUIDPY_SLIDESEQV2_EXPANDED | reference_profile | -0.0688 | 1.52e-88 |

## Dataset Configs

```json
[
  {
    "dataset_id": "GSE202623_CELLTYPE_EXPANDED",
    "source_dataset_id": "GSE202623",
    "modality": "MERFISH_RNA_single_cell",
    "biological_context": "large balanced Huntington disease MERFISH cell-type benchmark",
    "sampling": "balanced non-doublet cell.type_manual labels, min_per_label=50, max_per_label=1000",
    "n_cells_full": 280176,
    "n_features_full": 287,
    "expanded_cells": 33760,
    "expanded_features": 287,
    "n_labels": 42,
    "n_fov_groups": 3337,
    "expression_path": "GSE202623_CELLTYPE_EXPANDED\\GSE202623_CELLTYPE_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "GSE202623_CELLTYPE_EXPANDED\\GSE202623_CELLTYPE_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED",
    "source_dataset_id": "GSE333737",
    "modality": "MERSCOPE_MERFISH_RNA_single_cell",
    "biological_context": "adult human pancreas vascular-associated populations, all cells",
    "sampling": "all labeled cells",
    "n_cells_full": 24222,
    "n_features_full": 300,
    "expanded_cells": 24222,
    "expanded_features": 300,
    "n_labels": 4,
    "n_fov_groups": 12,
    "expression_path": "GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED\\GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED\\GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE284005_MERSCOPE_MS_EXPANDED",
    "source_dataset_id": "GSE284005",
    "modality": "MERSCOPE_MERFISH_RNA_single_cell",
    "biological_context": "human multiple sclerosis lesion atlas, balanced large subset",
    "sampling": "balanced clean_sub labels, min_per_label=25, max_per_label=1000",
    "n_cells_full": 401794,
    "n_features_full": 500,
    "expanded_cells": 34350,
    "expanded_features": 500,
    "n_labels": 38,
    "n_fov_groups": 17,
    "expression_path": "GEO_GSE284005_MERSCOPE_MS_EXPANDED\\GEO_GSE284005_MERSCOPE_MS_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "GEO_GSE284005_MERSCOPE_MS_EXPANDED\\GEO_GSE284005_MERSCOPE_MS_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED",
    "source_dataset_id": "GSE327581",
    "modality": "CosMx_spatial_molecular_imaging",
    "biological_context": "3xTg-AD mouse brain after fecal microbiota transplant, balanced large subset",
    "sampling": "balanced InSituType labels, min_per_label=25, max_per_label=300",
    "n_cells_full": 738722,
    "n_features_full": 1207,
    "expanded_cells": 16371,
    "expanded_features": 1207,
    "n_labels": 55,
    "n_fov_groups": 5,
    "expression_path": "GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED\\GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED\\GEO_GSE327581_COSMX_AD_BRAIN_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "SQUIDPY_MERFISH_EXPANDED",
    "source_dataset_id": "SQUIDPY_MERFISH",
    "modality": "spatial_transcriptomics_single_cell",
    "biological_context": "MERFISH mouse hypothalamus/preoptic region, all clean cells",
    "sampling": "all clean labels with >= 25 cells",
    "n_cells_full": 73655,
    "n_features_full": 161,
    "expanded_cells": 73655,
    "expanded_features": 161,
    "n_labels": 16,
    "n_fov_groups": 12,
    "expression_path": "SQUIDPY_MERFISH_EXPANDED\\SQUIDPY_MERFISH_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "SQUIDPY_MERFISH_EXPANDED\\SQUIDPY_MERFISH_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "SQUIDPY_SEQFISH_EXPANDED",
    "source_dataset_id": "SQUIDPY_SEQFISH",
    "modality": "spatial_transcriptomics_single_cell",
    "biological_context": "seqFISH mouse organogenesis, all clean cells",
    "sampling": "all clean labels with >= 25 cells",
    "n_cells_full": 19416,
    "n_features_full": 351,
    "expanded_cells": 19416,
    "expanded_features": 351,
    "n_labels": 22,
    "n_fov_groups": 63,
    "expression_path": "SQUIDPY_SEQFISH_EXPANDED\\SQUIDPY_SEQFISH_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "SQUIDPY_SEQFISH_EXPANDED\\SQUIDPY_SEQFISH_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "SQUIDPY_SLIDESEQV2_EXPANDED",
    "source_dataset_id": "SQUIDPY_SLIDESEQV2",
    "modality": "spatial_transcriptomics_bead",
    "biological_context": "Slide-seqV2 mouse hippocampus, balanced large subset",
    "sampling": "balanced clean labels, min_per_label=25, max_per_label=1500, top mean features=1500",
    "n_cells_full": 41786,
    "n_features_full": 4000,
    "expanded_cells": 18842,
    "expanded_features": 1500,
    "n_labels": 14,
    "n_fov_groups": 64,
    "expression_path": "SQUIDPY_SLIDESEQV2_EXPANDED\\SQUIDPY_SLIDESEQV2_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "SQUIDPY_SLIDESEQV2_EXPANDED\\SQUIDPY_SLIDESEQV2_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED",
    "source_dataset_id": "GSE302502",
    "modality": "Xenium_spatial_transcriptomics_single_cell",
    "biological_context": "human glioma tertiary lymphoid structures with coarse immune/stromal cell labels",
    "sampling": "balanced coarse_cell_type labels from 12 TLS patient samples, max_per_label=2500",
    "n_cells_full": 74830,
    "n_features_full": 541,
    "expanded_cells": 23570,
    "expanded_features": 541,
    "n_labels": 10,
    "n_fov_groups": 12,
    "expression_path": "GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED\\GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED\\GEO_GSE302502_XENIUM_GLIOMA_TLS_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE282127_GENERIC_H5AD_EXPANDED",
    "source_dataset_id": "GSE282127",
    "modality": "generic_h5ad_spatial_label_parser",
    "biological_context": "GSE282127 prepared by generic h5ad parser",
    "sampling": "balanced labels, max_per_label applied; label_col=leiden_0.8",
    "n_cells_full": 88406,
    "n_features_full": 550,
    "expanded_cells": 53108,
    "expanded_features": 550,
    "n_labels": 26,
    "n_fov_groups": 42,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE282127_GENERIC_H5AD_EXPANDED\\GEO_GSE282127_GENERIC_H5AD_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE282127_GENERIC_H5AD_EXPANDED\\GEO_GSE282127_GENERIC_H5AD_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE245263_GENERIC_H5AD_EXPANDED",
    "source_dataset_id": "GSE245263",
    "modality": "generic_h5ad_spatial_label_parser",
    "biological_context": "GSE245263 prepared by generic h5ad parser",
    "sampling": "balanced labels, max_per_label applied; label_col=leiden",
    "n_cells_full": 2158,
    "n_features_full": 32272,
    "expanded_cells": 2158,
    "expanded_features": 2000,
    "n_labels": 15,
    "n_fov_groups": 61,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE245263_GENERIC_H5AD_EXPANDED\\GEO_GSE245263_GENERIC_H5AD_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE245263_GENERIC_H5AD_EXPANDED\\GEO_GSE245263_GENERIC_H5AD_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE263450_GENERIC_H5AD_EXPANDED",
    "source_dataset_id": "GSE263450",
    "modality": "generic_h5ad_spatial_label_parser",
    "biological_context": "GSE263450 prepared by generic h5ad parser",
    "sampling": "balanced labels, max_per_label applied; label_col=leiden",
    "n_cells_full": 37036,
    "n_features_full": 35032,
    "expanded_cells": 36521,
    "expanded_features": 2000,
    "n_labels": 24,
    "n_fov_groups": 63,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE263450_GENERIC_H5AD_EXPANDED\\GEO_GSE263450_GENERIC_H5AD_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE263450_GENERIC_H5AD_EXPANDED\\GEO_GSE263450_GENERIC_H5AD_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE294759_GENERIC_H5AD_EXPANDED",
    "source_dataset_id": "GSE294759",
    "modality": "generic_h5ad_spatial_label_parser",
    "biological_context": "GSE294759 prepared by generic h5ad parser",
    "sampling": "balanced labels, max_per_label applied; label_col=leiden",
    "n_cells_full": 60932,
    "n_features_full": 35209,
    "expanded_cells": 44137,
    "expanded_features": 2000,
    "n_labels": 32,
    "n_fov_groups": 64,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE294759_GENERIC_H5AD_EXPANDED\\GEO_GSE294759_GENERIC_H5AD_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE294759_GENERIC_H5AD_EXPANDED\\GEO_GSE294759_GENERIC_H5AD_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED",
    "source_dataset_id": "GSE301435",
    "modality": "generic_cosmx_csv_metadata_expression",
    "biological_context": "GSE301435 prepared by generic CosMx CSV expression+metadata parser",
    "sampling": "balanced labels, max_per_label applied; label_col=RNA_nbclust_719bacdb.ea30.4c91.8f6f.d838e95062e8_1_clusters",
    "n_cells_full": 394364,
    "n_features_full": 1201,
    "expanded_cells": 57937,
    "expanded_features": 1201,
    "n_labels": 26,
    "n_fov_groups": 617,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED\\GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED\\GEO_GSE301435_GENERIC_COSMX_CSV_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE308624_GENERIC_H5AD_EXPANDED",
    "source_dataset_id": "GSE308624",
    "modality": "generic_h5ad_spatial_label_parser",
    "biological_context": "GSE308624 prepared by generic h5ad parser",
    "sampling": "balanced labels, max_per_label applied; label_col=cell_type",
    "n_cells_full": 200182,
    "n_features_full": 1000,
    "expanded_cells": 18032,
    "expanded_features": 1000,
    "n_labels": 8,
    "n_fov_groups": 64,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE308624_GENERIC_H5AD_EXPANDED\\GEO_GSE308624_GENERIC_H5AD_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE308624_GENERIC_H5AD_EXPANDED\\GEO_GSE308624_GENERIC_H5AD_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE310129_GENERIC_H5AD_EXPANDED",
    "source_dataset_id": "GSE310129",
    "modality": "generic_h5ad_spatial_label_parser",
    "biological_context": "GSE310129 prepared by generic h5ad parser",
    "sampling": "balanced labels, max_per_label applied; label_col=leiden",
    "n_cells_full": 22522,
    "n_features_full": 20845,
    "expanded_cells": 22522,
    "expanded_features": 2000,
    "n_labels": 28,
    "n_fov_groups": 63,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE310129_GENERIC_H5AD_EXPANDED\\GEO_GSE310129_GENERIC_H5AD_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE310129_GENERIC_H5AD_EXPANDED\\GEO_GSE310129_GENERIC_H5AD_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE317755_GENERIC_H5AD_EXPANDED",
    "source_dataset_id": "GSE317755",
    "modality": "generic_h5ad_spatial_label_parser",
    "biological_context": "GSE317755 prepared by generic h5ad parser",
    "sampling": "balanced labels, max_per_label applied; label_col=seurat_clusters",
    "n_cells_full": 3188,
    "n_features_full": 20406,
    "expanded_cells": 3188,
    "expanded_features": 2000,
    "n_labels": 14,
    "n_fov_groups": 61,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE317755_GENERIC_H5AD_EXPANDED\\GEO_GSE317755_GENERIC_H5AD_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE317755_GENERIC_H5AD_EXPANDED\\GEO_GSE317755_GENERIC_H5AD_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE327129_GENERIC_H5AD_EXPANDED",
    "source_dataset_id": "GSE327129",
    "modality": "generic_h5ad_spatial_label_parser",
    "biological_context": "GSE327129 prepared by generic h5ad parser",
    "sampling": "balanced labels, max_per_label applied; label_col=Classification",
    "n_cells_full": 17586,
    "n_features_full": 14703,
    "expanded_cells": 7303,
    "expanded_features": 2000,
    "n_labels": 3,
    "n_fov_groups": 61,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE327129_GENERIC_H5AD_EXPANDED\\GEO_GSE327129_GENERIC_H5AD_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE327129_GENERIC_H5AD_EXPANDED\\GEO_GSE327129_GENERIC_H5AD_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE328481_GENERIC_H5AD_EXPANDED",
    "source_dataset_id": "GSE328481",
    "modality": "generic_h5ad_spatial_label_parser",
    "biological_context": "GSE328481 prepared by generic h5ad parser",
    "sampling": "balanced labels, max_per_label applied; label_col=bin50 structural annotation",
    "n_cells_full": 97923,
    "n_features_full": 33157,
    "expanded_cells": 15000,
    "expanded_features": 2000,
    "n_labels": 6,
    "n_fov_groups": 58,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE328481_GENERIC_H5AD_EXPANDED\\GEO_GSE328481_GENERIC_H5AD_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE328481_GENERIC_H5AD_EXPANDED\\GEO_GSE328481_GENERIC_H5AD_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE330849_GENERIC_H5AD_EXPANDED",
    "source_dataset_id": "GSE330849",
    "modality": "generic_h5ad_spatial_label_parser",
    "biological_context": "GSE330849 prepared by generic h5ad parser",
    "sampling": "balanced labels, max_per_label applied; label_col=leiden",
    "n_cells_full": 135495,
    "n_features_full": 478,
    "expanded_cells": 52701,
    "expanded_features": 478,
    "n_labels": 23,
    "n_fov_groups": 64,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE330849_GENERIC_H5AD_EXPANDED\\GEO_GSE330849_GENERIC_H5AD_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE330849_GENERIC_H5AD_EXPANDED\\GEO_GSE330849_GENERIC_H5AD_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED",
    "source_dataset_id": "GSE325587",
    "modality": "generic_csv_expression_metadata_pair",
    "biological_context": "GSE325587 prepared by generic CSV expression+metadata pair parser",
    "sampling": "balanced labels, max_per_label applied; label_col=GSE325587_processed_metadata.csv.gz:cell_types_full",
    "n_cells_full": 383258,
    "n_features_full": 1008,
    "expanded_cells": 20386,
    "expanded_features": 1008,
    "n_labels": 29,
    "n_fov_groups": 194,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED\\GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED\\GEO_GSE325587_GENERIC_CSV_PAIR_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED",
    "source_dataset_id": "GSE273530",
    "modality": "generic_cosmx_csv_metadata_expression",
    "biological_context": "GSE273530 prepared by generic CosMx CSV expression+metadata parser",
    "sampling": "balanced labels, max_per_label applied; label_col=nn_233be8c1.6622.4cb9.83e9.1c261ca737c7_1_cluster_cluster_e901c776.a68c.4ffe.828e.b95c25440e02_1",
    "n_cells_full": 9231,
    "n_features_full": 1196,
    "expanded_cells": 8976,
    "expanded_features": 1196,
    "n_labels": 10,
    "n_fov_groups": 29,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED\\GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED\\GEO_GSE273530_GENERIC_COSMX_CSV_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED",
    "source_dataset_id": "GSE273952",
    "modality": "generic_visium_10x_h5_annotation",
    "biological_context": "GSE273952 prepared by generic Visium 10x h5 + annotation parser",
    "sampling": "balanced labels, max_per_label applied; label_col=TumoralZone_annotation:Tumor_zone",
    "n_cells_full": 33692,
    "n_features_full": 17943,
    "expanded_cells": 5000,
    "expanded_features": 2000,
    "n_labels": 2,
    "n_fov_groups": 566,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED\\GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED\\GEO_GSE273952_GENERIC_VISIUM_H5_ANNOTATION_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED",
    "source_dataset_id": "GSE337336",
    "modality": "generic_csv_expression_metadata_pair",
    "biological_context": "GSE337336 prepared by generic CSV expression+metadata pair parser",
    "sampling": "balanced labels, max_per_label applied; label_col=InSituTypeIDs2",
    "n_cells_full": 65717,
    "n_features_full": 1000,
    "expanded_cells": 20000,
    "expanded_features": 1000,
    "n_labels": 8,
    "n_fov_groups": 559,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED\\GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED\\GEO_GSE337336_GENERIC_CSV_PAIR_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED",
    "source_dataset_id": "GSE307588",
    "modality": "generic_cosmx_counts_cells_clusters_tsv",
    "biological_context": "GSE307588 prepared by generic CosMx TSV triple parser",
    "sampling": "balanced labels, max_per_label applied; label_col=Cluster",
    "n_cells_full": 3734,
    "n_features_full": 380,
    "expanded_cells": 3713,
    "expanded_features": 380,
    "n_labels": 16,
    "n_fov_groups": 62,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED\\GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED\\GEO_GSE307588_GENERIC_COSMX_TSV_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE326743_GENERIC_XENIUM_EXPANDED",
    "source_dataset_id": "GSE326743",
    "modality": "generic_xenium_matrix_annotation",
    "biological_context": "GSE326743 prepared by generic Xenium matrix+annotation parser",
    "sampling": "balanced labels, max_per_label applied; label_col=Level_4_Annotations",
    "n_cells_full": 750744,
    "n_features_full": 9749,
    "expanded_cells": 64284,
    "expanded_features": 1000,
    "n_labels": 30,
    "n_fov_groups": 3,
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\geo100_prepared\\GEO_GSE326743_GENERIC_XENIUM_EXPANDED\\GEO_GSE326743_GENERIC_XENIUM_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\geo100_prepared\\GEO_GSE326743_GENERIC_XENIUM_EXPANDED\\GEO_GSE326743_GENERIC_XENIUM_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED",
    "source_dataset_id": "GSE305393",
    "modality": "generic_cosmx_csv_metadata_expression",
    "biological_context": "GSE305393 prepared by generic CosMx CSV expression+metadata parser",
    "sampling": "balanced labels, max_per_label applied; label_col=cell_type",
    "n_cells_full": 94642,
    "n_features_full": 6524,
    "expanded_cells": 19039,
    "expanded_features": 1000,
    "n_labels": 21,
    "n_fov_groups": 73,
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\geo100_prepared\\GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED\\GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\geo100_prepared\\GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED\\GEO_GSE305393_GENERIC_COSMX_CSV_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED",
    "source_dataset_id": "GSE291308",
    "modality": "generic_csv_expression_metadata_pair",
    "biological_context": "GSE291308 prepared by generic CSV expression+metadata pair parser",
    "sampling": "balanced labels, max_per_label applied; label_col=ct",
    "n_cells_full": 126436,
    "n_features_full": 1000,
    "expanded_cells": 17655,
    "expanded_features": 1000,
    "n_labels": 8,
    "n_fov_groups": 53,
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\geo100_prepared\\GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED\\GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\geo100_prepared\\GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED\\GEO_GSE291308_GENERIC_CSV_PAIR_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE311681_GENERIC_XENIUM_EXPANDED",
    "source_dataset_id": "GSE311681",
    "modality": "generic_xenium_matrix_annotation",
    "biological_context": "GSE311681 prepared by generic Xenium matrix+annotation parser",
    "sampling": "balanced labels, max_per_label applied; label_col=_resolved_label",
    "n_cells_full": 100330,
    "n_features_full": 541,
    "expanded_cells": 33574,
    "expanded_features": 541,
    "n_labels": 25,
    "n_fov_groups": 36,
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\geo100_prepared\\GEO_GSE311681_GENERIC_XENIUM_EXPANDED\\GEO_GSE311681_GENERIC_XENIUM_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\geo100_prepared\\GEO_GSE311681_GENERIC_XENIUM_EXPANDED\\GEO_GSE311681_GENERIC_XENIUM_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED",
    "source_dataset_id": "GSE292268",
    "modality": "generic_cosmx_csv_metadata_expression",
    "biological_context": "GSE292268 prepared by generic CosMx CSV expression+metadata parser",
    "sampling": "balanced labels, max_per_label applied; label_col=RNA_nbclust_ee1320c5.9f48.455c.b54e.1fbfd34347ab_1_clusters",
    "n_cells_full": 107256,
    "n_features_full": 1207,
    "expanded_cells": 28166,
    "expanded_features": 1000,
    "n_labels": 16,
    "n_fov_groups": 127,
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\geo100_prepared\\GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED\\GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\geo100_prepared\\GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED\\GEO_GSE292268_GENERIC_COSMX_CSV_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED",
    "source_dataset_id": "GSE278766",
    "modality": "generic_cosmx_csv_metadata_expression",
    "biological_context": "GSE278766 prepared by generic CosMx CSV expression+metadata parser",
    "sampling": "balanced labels, max_per_label applied; label_col=RNA_nbclust_9d7145a9.f10b.453d.960e.322d9aecddcb_1_clusters",
    "n_cells_full": 283682,
    "n_features_full": 1207,
    "expanded_cells": 32011,
    "expanded_features": 1000,
    "n_labels": 13,
    "n_fov_groups": 205,
    "expression_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\geo100_prepared\\GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED\\GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "C:\\Users\\user\\Documents\\Codex\\2026-07-23\\si\\outputs\\datasets\\geo100_prepared\\GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED\\GEO_GSE278766_GENERIC_COSMX_CSV_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE333479_H5AD_SIDECAR_EXPANDED",
    "source_dataset_id": "GSE333479",
    "modality": "multi_h5ad_sidecar_annotation",
    "biological_context": "GSE333479 prepared by multi-H5AD sidecar-annotation parser",
    "sampling": "balanced labels, max_per_label applied; label_col=sidecar:annotation",
    "n_cells_full": 77924,
    "n_features_full": 19632,
    "expanded_cells": 20448,
    "expanded_features": 2000,
    "n_labels": 14,
    "n_fov_groups": 5,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE333479_H5AD_SIDECAR_EXPANDED\\GEO_GSE333479_H5AD_SIDECAR_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE333479_H5AD_SIDECAR_EXPANDED\\GEO_GSE333479_H5AD_SIDECAR_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE279181_H5AD_COMPOSITION_EXPANDED",
    "source_dataset_id": "GSE279181",
    "modality": "multi_h5ad_composition_argmax",
    "biological_context": "GSE279181 prepared by multi-H5AD composition-argmax parser",
    "sampling": "balanced labels, max_per_label applied; label_col=obsm:argmax(ctype_props)",
    "n_cells_full": 67851,
    "n_features_full": 13905,
    "expanded_cells": 11677,
    "expanded_features": 2000,
    "n_labels": 9,
    "n_fov_groups": 18,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE279181_H5AD_COMPOSITION_EXPANDED\\GEO_GSE279181_H5AD_COMPOSITION_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE279181_H5AD_COMPOSITION_EXPANDED\\GEO_GSE279181_H5AD_COMPOSITION_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE280376_GENERIC_XENIUM_EXPANDED",
    "source_dataset_id": "GSE280376",
    "modality": "generic_xenium_matrix_annotation",
    "biological_context": "GSE280376 prepared by generic Xenium matrix+annotation parser",
    "sampling": "balanced labels, max_per_label applied; label_col=_resolved_label",
    "n_cells_full": 225696,
    "n_features_full": 540,
    "expanded_cells": 92321,
    "expanded_features": 540,
    "n_labels": 65,
    "n_fov_groups": 7,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE280376_GENERIC_XENIUM_EXPANDED\\GEO_GSE280376_GENERIC_XENIUM_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE280376_GENERIC_XENIUM_EXPANDED\\GEO_GSE280376_GENERIC_XENIUM_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED",
    "source_dataset_id": "GSE308167",
    "modality": "multi_h5ad_internal_label",
    "biological_context": "GSE308167 prepared by multi-H5AD internal-label parser",
    "sampling": "balanced labels, max_per_label applied; label_col=obs:cell_type",
    "n_cells_full": 20774,
    "n_features_full": 9188,
    "expanded_cells": 11775,
    "expanded_features": 2000,
    "n_labels": 11,
    "n_fov_groups": 3,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED\\GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED\\GEO_GSE308167_H5AD_INTERNAL_LABEL_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED",
    "source_dataset_id": "GSE308952",
    "modality": "multi_h5ad_internal_label",
    "biological_context": "GSE308952 prepared by multi-H5AD internal-label parser",
    "sampling": "balanced labels, max_per_label applied; label_col=obs:manual_anno",
    "n_cells_full": 3720,
    "n_features_full": 14761,
    "expanded_cells": 3720,
    "expanded_features": 2000,
    "n_labels": 7,
    "n_fov_groups": 28,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED\\GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED\\GEO_GSE308952_H5AD_INTERNAL_LABEL_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  },
  {
    "dataset_id": "GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED",
    "source_dataset_id": "GSE336633",
    "modality": "multi_h5ad_internal_label",
    "biological_context": "GSE336633 prepared by multi-H5AD internal-label parser",
    "sampling": "balanced labels, max_per_label applied; label_col=obs:predicted_labels",
    "n_cells_full": 388407,
    "n_features_full": 9115,
    "expanded_cells": 75580,
    "expanded_features": 2000,
    "n_labels": 34,
    "n_fov_groups": 3,
    "expression_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED\\GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED_expanded_expression.tsv.gz",
    "metadata_path": "D:\\NicheTypeR_GEO_100_QUEUE\\prepared\\GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED\\GEO_GSE336633_H5AD_INTERNAL_LABEL_EXPANDED_expanded_metadata.tsv",
    "cell_id_col": "cell_id",
    "label_col": "label",
    "group_col": "fov_group",
    "x_col": "x",
    "y_col": "y"
  }
]
```
