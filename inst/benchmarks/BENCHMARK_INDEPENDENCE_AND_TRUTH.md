# Benchmark Independence And Reference-Label Model

This note documents how NicheTypeR separates benchmark configurations from
independent biological sources, and how held-out labels are interpreted.

## Independence accounting

The completed primary performance snapshot contains 68 benchmark
configurations from 61 named public source IDs. These are not treated as 68
independent cohorts. A source ID is an accession or named repository dataset,
not an assertion of donor-level independence; publication family, donor,
slide, FOV and generated spatial block are tracked separately where available.

| Unit | Count | Interpretation |
|---|---:|---|
| Processed public source IDs | 100 | total processing coverage |
| Label-bearing validation sources | 61 | primary efficacy panel |
| Known validation publication families | 59 | two known shared-provenance merges |
| Preview configurations | 12 | compact reproducible matrices used for the main blocked benchmark |
| Expanded validation configurations | 56 | larger and cross-sample views |
| Sources with both preview and expanded configurations | 7 | paired analysis views, not independent cohorts |
| Primary validation configurations | 68 | analysis configurations, not a cohort count |
| Cluster-only calibration sources/configurations | 39 | operational/null calibration only |
| All processed configurations | 107 | validation plus calibration |
| Validation configuration-level observations | 1,271,329 | includes repeated preview views |
| Source-deduplicated validation observations | 1,239,332 | preview subset removed where expanded view exists |

The seven source datasets represented by both preview and expanded views are:
GSE202623, GSE333737, GSE284005, GSE327581, SQUIDPY_MERFISH,
SQUIDPY_SEQFISH and SQUIDPY_SLIDESEQV2.

The complete source list, known publication-family merges and source-level unit
counts are released in `SOURCE_INDEPENDENCE_REGISTRY.csv`. The tiered
100-source accounting is released in `HUNDRED_SOURCE_PORTFOLIO.csv`. The 39
calibration sources use SODB-standardized Leiden clusters. They test ingestion,
blocked execution and matched-null behavior, but do not constitute semantic
cell-type ground truth and are excluded from all primary efficacy fractions.

## Reference-label model

Held-out author or expert labels are treated as reference labels for benchmark
evaluation, not as flawless biological truth. A wrong call means discordance
between a model prediction and the held-out reference label. This definition is
useful for quantitative benchmarking, but it does not prove that every flagged
conflict is a true biological correction.

This distinction is central to the audit framing. When NicheTypeR reports a
conflict, the result should be interpreted as a review hypothesis with explicit
evidence: marker support, negative-marker evidence, reference profile support,
neighborhood compatibility, ligand-receptor evidence, margin, confidence and
matched-null controls. A conflict can mean either that the model is wrong, or
that the original annotation deserves re-examination.

The current manuscript therefore reports three levels of support:

| Evidence level | What it supports | What it does not prove |
|---|---|---|
| Held-out reference labels | quantitative wrong-call detection and rescue/harm accounting | absolute biological truth |
| Local-neighborhood summaries | biological inspectability of prioritized cases | prospective expert adjudication |
| External mapper stress tests | utility downstream of reference-style annotation outputs | package-native superiority over all atlas tools |

Prospective pathology review, manual expert adjudication with raw images, or
orthogonal wet-lab validation would be required to turn prioritized audit events
into confirmed new biological discoveries.
