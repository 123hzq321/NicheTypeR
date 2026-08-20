# Local GEO Ingestion Audit

This audit re-scans downloaded or partially downloaded GEO candidates for
expression-like files, coordinate-like fields and supervised label/domain
columns. A dataset is only considered benchmark-ready when all three are
present in locally available files.

## Readiness Summary

| accession | files | expression | coordinate cols | label-like cols | usable labels | ready | blocker |
|---|---:|---|---:|---:|---:|---|---|
| GSE300613 | 9 | True | 4 | 0 | 0 | False | no usable supervised label/domain column detected |
| GSE282124 | 5 | True | 6 | 0 | 0 | False | no usable supervised label/domain column detected |
| GSE303162 | 8 | True | 0 | 0 | 0 | False | no coordinate-like columns detected |
| GSE305735 | 3 | False | 0 | 0 | 0 | False | no expression-like file detected |
| GSE325911 | 150 | True | 74 | 0 | 0 | False | no usable supervised label/domain column detected |
| GSE278614 | 2 | False | 0 | 1 | 1 | False | no expression-like file detected |

## Candidate Label Columns

### GSE300613

No label-like columns detected in scanned local files.

### GSE282124

No label-like columns detected in scanned local files.

### GSE303162

No label-like columns detected in scanned local files.

### GSE305735

No label-like columns detected in scanned local files.

### GSE325911

No label-like columns detected in scanned local files.

### GSE278614

| file | column | role | unique sample count | example values |
|---|---|---|---:|---|
| GSE278614_summary.txt.gz | # Example of a matrix table for a single channel (non-Affymetrix) submission including platform annotation (header 1-header 3). Only column headers are shown. | label_like | 7 | # The Matrix table should include normalized (scaled) signal count data., # Values that should be disregarded may either be left blank or labeled as "null"., 1_ |
