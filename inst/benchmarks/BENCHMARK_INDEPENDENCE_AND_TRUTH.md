# Benchmark Independence And Reference-Label Model

This note documents how NicheTypeR separates benchmark configurations from
independent biological sources, and how held-out labels are interpreted.

## Independence accounting

The completed performance snapshot contains 34 benchmark configurations, but
these are not treated as 34 independent cohorts. The biological independence
unit is the source dataset or source accession.

| Unit | Count | Interpretation |
|---|---:|---|
| Source datasets | 27 | primary biological independence unit |
| Preview configurations | 12 | compact reproducible matrices used for the main blocked benchmark |
| Expanded configurations | 22 | larger stress-test views for scale and robustness |
| Sources with both preview and expanded configurations | 7 | paired analysis views, not independent cohorts |
| Expanded-only source datasets | 15 | additional independent public sources |
| Total benchmark configurations | 34 | analysis configurations, not a cohort count |

The seven source datasets represented by both preview and expanded views are:
GSE202623, GSE333737, GSE284005, GSE327581, SQUIDPY_MERFISH,
SQUIDPY_SEQFISH and SQUIDPY_SLIDESEQV2.

The expanded-only source datasets are: GSE302502, GSE282127, GSE245263,
GSE263450, GSE294759, GSE301435, GSE308624, GSE310129, GSE317755, GSE327129,
GSE328481, GSE330849, GSE325587, GSE273530 and GSE273952.

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
