# GEO Direct Dataset Expansion

This report records datasets found and downloaded directly from NCBI GEO, rather
than through packaged example datasets.

## Benchmark-Ready GEO Datasets

| dataset | GEO | modality/context | full cells | preview | label column | result in current benchmark |
|---|---|---|---:|---:|---|---|
| GEO_GSE240015_VISIUM_THYMUS_DOMAIN | GSE240015 | mouse thymus aging Visium spatial domains | 3,910 | 3,910 x 2,000 | sample-prefixed Leiden 1.0 domains | smoothing guardrail pass |
| GEO_GSE284005_MERSCOPE_MS | GSE284005 | human multiple sclerosis lesion MERSCOPE/MERFISH | 401,794 | 9,393 x 500 | `clean_sub` | no context guardrail pass |
| GEO_GSE333737_MERSCOPE_PANCREAS_VASCULAR | GSE333737 | human pancreas vascular-associated MERSCOPE/MERFISH | 24,222 | 2,400 x 300 | `cell_type_final` | no context guardrail pass |
| GEO_GSE327581_COSMX_AD_BRAIN | GSE327581 | 3xTg-AD mouse brain CosMx SMI | 738,722 | 5,500 x 1,207 | InSituType clusters | learned-neighborhood guardrail pass |

All benchmark-ready datasets were converted into the common preview contract:

- `*_preview_expression.tsv.gz`
- `*_preview_metadata.tsv`
- `*_metadata.tsv`
- `*_summary.json`
- `*_manifest.md`

For `GSE333737`, the GEO file list exposes a large RAW archive of sample ZIP
files. This pass used the downloaded `GSE333737_allvascular_cells.h5ad` summary
object under `GEO_DIRECT/GSE333737` for benchmark construction rather than
expanding the full 30 GB RAW archive.

For `GSE327581`, the 451 MB RAW archive was downloaded and extracted locally.
The benchmark uses the author-provided InSituType cell-typing cluster column,
global cell coordinates, and five biological sample groups.

For `GSE240015`, the two processed Visium h5ad files were downloaded directly.
This dataset is used as a spatial-domain benchmark, not as a manual single-cell
type benchmark. Labels are sample-prefixed Leiden 1.0 domains, and validation
uses 3 x 3 spatial blocks within each sample.

## Downloaded Candidates Not Yet Benchmark-Ready

| GEO | status | reason |
|---|---|---|
| GSE300613 | downloaded candidate | processed Visium h5ad files are readable, but obs only contains spot coordinates and no usable label column |
| GSE278614 | partial download candidate | CosMx h5ad files are inside a 1.3 GB RAW archive; 357 MB was downloaded before timeout, not yet benchmark-ready |
| GSE282124 | downloaded candidate | cell-by-gene and metadata available, but no explicit cell type label found in downloaded metadata header |
| GSE325911 | downloaded candidate | counts and cell coordinates available across ROIs, but no explicit cell type label file found |
| GSE303162 | downloaded candidate | Visium spot data with coordinates, but no cell type/domain labels in downloaded files |
| GSE305735 | downloaded candidate | expression-like FPKM files only; not benchmark-ready for spatial cell type annotation |
| GSE307719 | manifest-only candidate | cell-by-gene and metadata exist, but files are packaged in a 228 GB RAW archive; not downloaded in this pass |

## Files And Scripts

- `GEO_DIRECT_DATASETS.csv`: machine-readable screening table
- `GEO_EXPANDED_SEARCH_CANDIDATES.csv`: broader automated GEO candidate search
- `GEO_EXPANDED_SEARCH_CANDIDATES.md`: readable top-candidate summary
- `GEO_CANDIDATES/`: GEO `filelist.txt` snapshots for screened accessions
- `GEO_DIRECT/`: downloaded raw GEO supplements and extracted files
- `prepare_geo_direct_datasets.py`: converter for benchmark-ready GEO datasets
- `prepare_geo_h5ad_domain_datasets.py`: converter for processed h5ad spatial-domain GEO datasets
- `search_geo_validation_candidates.py`: reusable NCBI GEO candidate search script

## Interpretation

The GEO-direct panel is now mixed in an informative way. GSE284005 and GSE333737
remain negative controls for broad claims: neither supports a strong
learned-neighborhood or null-corrected context-specific improvement under the
current guardrail. GSE327581 is positive for learned-neighborhood specificity:
marker + learned neighborhood improves macro-F1 over marker-only and over both
random-graph and permuted-prior null controls. GSE240015 is a domain-control
case: simple spatial smoothing, not learned neighborhood, explains the gain.
The null-corrected residual still does not pass the strict guardrail, so it
remains an audit statistic rather than the predictive method core.
