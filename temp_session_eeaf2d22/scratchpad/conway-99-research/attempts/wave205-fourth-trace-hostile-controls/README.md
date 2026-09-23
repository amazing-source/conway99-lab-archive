# Wave 205 literature and hostile fourth-trace controls

## Status

```text
claim label:          CANDIDATE_RELAXED_CONTROL
Conway-99:            UNKNOWN
rank-11 endpoint:     UNKNOWN
n3=4158 endpoint:     UNKNOWN
automorphism assumed: NONE
```

This package does not construct or exclude `srg(99,14,1,2)`. It supplies:

1. a theorem-by-theorem primary-source audit for proposed fourth-moment,
   projector-design, trace-tensor, and association-scheme transfers; and
2. a stronger exact relaxed control in which endpoint-shaped star projectors
   are coupled to a linear `99 by 231` triple incidence.

The two exact realizations have the same full pairwise trace matrix

```text
g_xy=tr(P_x P_y)
```

and agree on

```text
h_xy=tr(P_x P_y P_x P_y)
```

on every edge of their 14-regular point graph. Nevertheless, their `h`
matrices differ on 3,888 ordered nonedge pairs.

## What the construction adds beyond Wave 204

The control now has all of the following simultaneously:

- 99 rank-six trace-zero self-adjoint idempotents in a nondegenerate
  11-space over `F_3`;
- 231 labelled singular columns spanning dimension 11;
- rank-11 square-zero centered Gram matrices;
- seven simplex columns at every star and
  `P_x=-sum_{T contains x}(z_T tensor z_T)`;
- a binary linear triple incidence `B` with row degree 7 and column degree 3;
- a simple 14-regular point graph `A`;
- `BB^T=A+7I` over the integers and `BB^T=A+I` over `F_3`;
- an exact seven-color factorization in which every point sees each color
  once; and
- fourth-trace separation confined entirely to nonedges.

The incidence is constructed independently in this lane. The local projector
triple is reconstructed from the frozen Wave 204 formulas in a self-contained
checker.

## Why it is still only a relaxed control

- The 231 labelled columns use only 21 projective directions.
- The point graph has connected components of orders `27,36,36`.
- Its 231 designated blocks partition all edges into triangles, but the graph
  has 1,098 additional triangles.
- Adjacent common-neighbor counts range from 4 to 9 instead of being 1.
- Nonedge common-neighbor counts are not uniformly 2; 3,240 cross-component
  nonedges have zero common neighbors.
- The selected-orthogonality relation profiles, outer-cycle types,
  prism-free endpoint statistic, code distance, and cover conditions are not
  imposed.

Thus the construction proves only that the verified linear/projector
identities plus a substantially stronger incidence coupling and complete edge
fourth-trace agreement still do not determine the nonedge fourth traces.

## Files

- `exact_check.py` — self-contained exact construction and verifier.
- `test_exact_check.py` — six replay tests.
- `certificate.json` — complete matrices, simplices, incidence matrix,
  blocks, vertex types, and block vectors.
- `exact-results.json` — machine-readable summary and premise ledger.
- `derivation.md` — mathematical construction and rank ledger.
- `literature-audit.md` — primary-source hypothesis audit.
- `literature-sources.json` — machine-readable source ledger.
- `package-manifest.sha256` — SHA-256 manifest.

## Replay

From the repository root:

```powershell
python attempts/wave205-fourth-trace-hostile-controls/exact_check.py `
  --verify-results attempts/wave205-fourth-trace-hostile-controls/exact-results.json `
  --verify-certificate attempts/wave205-fourth-trace-hostile-controls/certificate.json

python -m pytest -q `
  attempts/wave205-fourth-trace-hostile-controls/test_exact_check.py
```

Expected:

```text
PASS: Wave205 hostile fourth-trace controls
6 passed
```
