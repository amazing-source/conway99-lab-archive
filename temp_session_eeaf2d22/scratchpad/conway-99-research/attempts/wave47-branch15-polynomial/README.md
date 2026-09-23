# Wave 47 branch-15 polynomial-calculus scout

Status: `CANDIDATE_RELATIONS`; no contradiction, assignment, branch closure,
endpoint exclusion, or graph was obtained. Branch 15 and Conway-99 remain
`UNKNOWN`.

## Alternative space

The Boolean endpoint formula is viewed in the squarefree quotient

```text
F2[x_1,...,x_m] / <x_i^2-x_i>.
```

For each matched coordinate pair `(2k,2k+1)`, take the 24 residual labels
containing one of those coordinates and all 276 residual-edge variables among
them. The frozen OPB contains exactly 48 complete coordinate-incidence blocks
inside this window:

- 24 exact-one blocks describing the two internal perfect matchings; and
- 24 exact-two blocks describing the row and column degrees of the cross
  bipartite graph.

After applying the SHA-bound Wave 42 closure, the calculation inserts the
complete vector space of degree-at-most-two polynomials which vanishes on each
exact local Hamming slice. It also inserts every active imported clause with
complete residual support in the window and residual width at most two.
Gaussian elimination is then saturated by multiplying every derived linear
row by every free window variable. This is the complete degree-two Macaulay
closure of the stated local semantic encoding, not a heuristic sample.

## Exact result

Across the seven windows:

```text
free variables per window:                 191--252
degree <= 2 monomial columns:          18,337--31,879
Macaulay input rows:                    8,621--14,292
contradictions:                                      0
new forced assignments:                              0
new independent linear F2 relations:                13
relations by window:                     2,1,2,2,2,2,2
```

The 13 relations have 25--40 terms. Their complete variable lists, decoded
residual edges and labels, constants, and row hashes are in
`degree2-window-result.json`. Each relation is supported inside a single
coordinate fibre. These are candidate XOR strengthenings which ordinary
generalized-unit propagation did not record.

An exact-block-only control omitting every imported clause produces the same
final linear subspace in all seven windows. Thus the 13 relations arise from
the integral exact-count/matching slices, not from the prism clauses. This
also means they are sound candidate consequences of a subset of the full
branch constraints, but they require clean-room replay before any promotion.

## Degree barrier for the Wave 43 cuts

The seven windows partition all 34,340 active Wave 43 cuts. Every one is an
all-negative width-four clause, hence its squarefree falsifying polynomial is
a degree-four monomial. Therefore none can enter an unassumed
degree-at-most-three polynomial-calculus Macaulay matrix. Degree three can see
one only after an additional true controller assumption; degree four, a
branch-conditioned degree-three attack, or a different encoding is required.

This is an exact representation barrier, not evidence that the branch is
satisfiable or that the cuts are weak.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave47-branch15-polynomial\degree2_windows.py

.\.venv\Scripts\python.exe -B `
  attempts\wave47-branch15-polynomial\degree2_windows.py --verify

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave47-branch15-polynomial -p "test_*.py" -v
```

Exact replay result:

```text
PASS_EXACT_REPLAY
sha256=d4689f7c9e469bf722d7553da700b47d98642c4404c566a0abc5a78149df4a3f
windows=7
```

All heavier steps enforce a 20% free-physical-memory stop guard, above the
user's requested 15% host reserve.

## Promotion boundary

- The package is discovery work and is not independently verified.
- It is a union of seven local subtheories, not a full-branch matrix.
- Constraints leaving a window and clauses above the degree cap are omitted.
- The semantic exact-count axioms are sound low-degree consequences, but the
  package does not claim a degree bound for another chosen PB encoding.
- A null contradiction/assignment result is not a SAT witness.
- The 13 XORs should be clean-room reproduced before being added to a solver.
- Branch 15, all 33 endpoint cases, the strict upper bound, and Conway-99
  remain `UNKNOWN`.
