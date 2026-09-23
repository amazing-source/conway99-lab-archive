# Query ledger

All counts are service-reported totals where available. `Inspected` is
capped at ten. A dash means the service supplied no usable total.

## Crossref

| id | total | inspected | qualifying result |
|---|---:|---:|---|
| C01 | 4,876,611 | 10 | none in top ten |
| C02 | 1,755,374 | 10 | none |
| C03 | 700,448 | 10 | none |
| C04 | 1,117,257 | 10 | none |
| C05 | 404,744 | 10 | none |
| C06 | 666,536 | 10 | none |
| C07 | 294,074 | 10 | none |
| C08 | 270,056 | 10 | none |
| C09 | 490,471 | 10 | none |
| C10 | 755,448 | 10 | none |
| R00 | 3,132,295 | 10 | none; all lexical false positives |

Crossref's `query` totals are broad corpus matches, not counts of exact
phrase matches.

## OpenAlex

| id | total | inspected | qualifying result |
|---|---:|---:|---|
| O01 | 85 | 10 | Reimbayev 2024; Cesarz--Woldar 2023/2025 |
| O02 | 6 | 6 | Cesarz--Woldar 2025; Keramatipour 2026 |
| O03 | 0 | 0 | none |
| O04 | 1 | 1 | unrelated heterotic compactification |
| O05 | 1 | 1 | unrelated quaternionic tight frames |
| O06 | 4 | 4 | none |
| O07 | 4 | 4 | none |
| O08 | 0 | 0 | none |
| O09 | 770 | 10 | none direct; type-`E6` quadratic forms are not the root-lattice target |
| O10 | 89 | 10 | no direct comparison |
| R00 | 0 | 0 | none |

## zbMATH Open

| id | HTTP | total | inspected | qualifying result |
|---|---:|---:|---:|---|
| Z01 | 200 | 2 | 2 | Reimbayev 2024; Crnkovic--Maksimovic 2020 |
| Z02 | 200 | 4 | 4 | Cesarz--Woldar 2025; two other partial/conditional papers |
| Z03 | 404 | - | 0 | endpoint returned `Entry not found!...` |
| Z04 | 404 | - | 0 | same |
| Z05 | 404 | - | 0 | same |
| Z06 | 404 | - | 0 | same |
| Z07 | 404 | - | 0 | same |
| Z08 | 404 | - | 0 | same |
| Z09 | 404 | - | 0 | same |
| Z10 | 404 | - | 0 | same |
| R00 | 404 | - | 0 | same |

The 404 rows are failures, not zero-result searches.

## arXiv

| id | total | inspected | qualifying result |
|---|---:|---:|---|
| X01 | 1 | 1 | Cesarz--Woldar 2023 |
| X02 | 0 | 0 | none |
| X03 | 0 | 0 | none |
| X04 | 0 | 0 | none |
| X05 | 0 | 0 | none |
| R00 | 0 | 0 | none |

## General web

The eleven exact queries were first issued in three batches and then
replayed individually because batch attribution was ambiguous. Only the
first ten individually attributable results were coded.

| id | attempts | inspected | qualifying result or disposition |
|---|---:|---:|---|
| G01 | 2 | 10 | Reimbayev 2024; Crnkovic--Maksimovic 2020; Ibrahim et al. 2025 |
| G02 | 2 | 10 | leads to Keramatipour 2026 and other partial work |
| G03 | 2 | 10 | none |
| G04 | 2 | 10 | none |
| G05 | 2 | 10 | no rank-six `E6` tight-frame result |
| G06 | 2 | 10 | Lie-group/Jordan cubic false positives; no lattice result |
| G07 | 2 | 10 | Nebe--Sloane `A6` table; no tight-frame result |
| G08 | 2 | 10 | none |
| G09 | 2 | 10 | none |
| G10 | 2 | 10 | none |
| R00 | 2 | 0 | empty result page |

Exact query strings and endpoints are in `query-log.jsonl`; the frozen
wording remains in `protocol.md` and `protocol-correction.md`.

## Late A20 addendum

These six pairs were frozen separately at 2026-07-24T00:57:55Z, after the
base protocol and correction. They do not alter the original freeze.

| id | HTTP/status | total | inspected | qualifying result or disposition |
|---|---|---:|---:|---|
| A20-C01 | 200 | 1,145,459 | 10 | none; all lexical false positives |
| A20-O01 | 200 | 0 | 0 | none |
| A20-Z01 | 404 | - | 0 | `Entry not found!...`; failure, not a zero-result certificate |
| A20-G01 | tool ok | - | 10 | no exact trace identity |
| A20-G02 | tool ok | - | 10 | no exact A20 summand use |
| A20-G03 | tool ok | - | 10 | Chattopadhyaya--Manschot 2026 gives only the standard `A_n` Cartan matrix |

The addendum inspected 40 records. Across the base protocol, correction, and
addendum, the audit therefore covers 56 unique service-query pairs and 303
inspected records.
