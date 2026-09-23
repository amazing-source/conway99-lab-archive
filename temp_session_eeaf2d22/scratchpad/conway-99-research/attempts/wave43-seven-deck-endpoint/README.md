# Wave 43 order-seven endpoint deck

Status: **EXACT FEASIBLE NECESSARY-COUNT SYSTEM; endpoint UNKNOWN**.

This package shifts the prism-free endpoint into the space of induced
subgraph counts. It uses all 208 locally admissible unlabeled graphs on seven
vertices, all 62 exact six-to-seven vertex-deletion equations, and all 19
published Hamiltonian seven-vertex formulas.

The Hamiltonian parameter is not fixed in advance. The integer variable is
`y=h11/4`, with the complete endpoint interval

```text
2079 <= y <= 4158.
```

At `n3=4158`, the first six-vertex count is zero. Nonnegativity and the
deletion equations therefore force every seven-vertex class containing that
prism type to have count zero.

## Exact outcome

HiGHS found a candidate that the standard-library integer checker then
reconstructed exactly:

```text
h11:                              16632
seven-vertex classes:               208
positive classes:                    99
zero classes:                       109
seven-subset total:         14887031544 = binom(99,7)
prism-containing classes:             3
positive prism-containing classes:    0
deletion equations checked:          62
Hamiltonian equations checked:       19
```

The support digest is

```text
b8217a567509036c84d0cab74d9f3ef57f69f97e9ad909b30446a73134e3c487
```

This is a rigorous positive control for the count relaxation. It proves that
ordinary induced-subgraph counts through order seven do **not** exclude the
prism-free endpoint.

## What it does not mean

The variables are aggregate isomorphism-class counts. They do not assign a
type to each seven-subset and do not enforce consistency between overlapping
subsets. The certificate is not a 99-vertex graph and is not evidence that
one exists.

A stronger continuation must add at least one of:

1. complete order-eight deletion-deck variables;
2. rooted/flag overlap equations distinguishing embeddings, not just types;
3. a positive-semidefinite moment matrix; or
4. direct adjacency/incidence compatibility.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave43-seven-deck-endpoint\endpoint_deck.py `
  --verify attempts\wave43-seven-deck-endpoint\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave43-seven-deck-endpoint -p "test_*.py" -v
```
