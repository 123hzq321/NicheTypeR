# Input Schema

`NicheTypeR` separates observed data from biological priors.

## Observed Data

Expression:

- rows: genes
- columns: cells
- values: normalized expression or log-normalized expression

Coordinates:

- `cell_id`: cell ID matching `colnames(expr)`
- `x`: spatial x coordinate
- `y`: spatial y coordinate

Metadata:

- `cell_id`: cell ID matching `colnames(expr)`
- optional: cluster ID, sample ID, batch, preliminary label, truth label

## Prior Tables

Marker database:

- `cell_type`
- `gene`
- `direction`: `positive` or `negative`
- `weight`
- optional `evidence_note`

Label-pathway table:

- `cell_type`
- `pathway`
- `weight`
- optional `evidence_note`

Pathway set table:

- `pathway`
- `gene`
- optional `weight`

Spatial niche table:

- `cell_type`
- `neighbor_type`
- `weight`
- optional `evidence_note`

Ligand-receptor table:

- `sender_type`
- `receiver_type`
- `ligand`
- `receptor`
- `weight`
- optional `evidence_note`

## Data Preparation Principle

Start conservative. A small, high-confidence prior table is better than a large
uncurated table because the package is designed to expose biological conflicts,
not hide them behind many weak priors.
