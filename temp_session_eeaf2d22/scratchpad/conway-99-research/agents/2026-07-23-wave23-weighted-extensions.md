---
role: construction
date_utc: 2026-07-23T20:02:20Z
git_commit: a6771108ec00bddfcc8ae5b41779760673fef22e
claim_label: DERIVED
scope: complete orbit-refined one-vertex extension equations through order seven at n3=705, for every allowed h11
inputs:
  - path: attempts/wave21-six-vertex-lp/exact-results.json
    sha256: 5e7b6f526985fb719754145944579aacb0e8f38e9e14a54d2075552a3756ff2b
  - path: attempts/wave22-full-seven-deck/exact-results.json
    sha256: ca5d9d116f6a9d6e355600429652e2bf4474b73dcf281bbcb564420d820acbd2
method: exhaustive locally admissible graph census, exact automorphism-orbit coefficients, independent lower-order transition gate, discovery-only normalized LP at two adjacent parameter values, and standard-library exact affine replay
command: python attempts/wave23-weighted-extensions/exact_check.py --output attempts/wave23-weighted-extensions/exact-results.json
outputs:
  - path: attempts/wave23-weighted-extensions/affine-witness.json
    sha256: 16ade54a77589b91478b3426dc3dbe57ebb2a5e0f7d209602ca282e42ac3ec77
  - path: attempts/wave23-weighted-extensions/exact-results.json
    sha256: 83a41b78eac02d845650ccdcb5b9782aba80caff9bdb7be983ec3f9e91c65b4c
  - path: attempts/wave23-weighted-extensions/exact_check.py
    sha256: ab959ded2357af8e5d62e18fc9136af538e302a127838be590baeaa71528f37a
limitations: necessary aggregate counts only; no overlap consistency or adjacency matrix; source H-panel alignment is a pinned human interpretation; independent verifier review pending
---

# Wave 23: all orbit-refined weighted extensions remain feasible

## Verdict

`DERIVED_INCONCLUSIVE`.

The proposed obstruction within the frozen 712-row weighted-extension
relaxation is exactly contradicted.  At `n3=705`, this complete orbit-refined
`6->7` one-vertex extension system has a nonnegative integer solution for every
allowed

```text
h11 = 1412, 1416, ..., 2820.
```

More strongly, all 208 seven-vertex counts form an exactly checked affine
integer family in `z=h11/4`.  This closes the route negatively: it does not
improve the conditional bound `n3>=705`, construct a graph, or change
Conway-99's `UNKNOWN` status.

## Exact weighted equations

Let `F` be one of the 62 locally admissible six-vertex classes, let `n_F` be
its count, and let `x_J` count the seven-vertex class `J`.  For every deletion
root `r` of `J` with `J-r` isomorphic to `F`, identify the card with the
canonical representative of `F`.  The relevant vertex and pair orbit is
independent of the chosen isomorphism because any two choices differ by an
automorphism of `F`.

For a vertex orbit `O` of `Aut(F)`, and a pair orbit `P`, define:

```text
d_F(J)     = number of roots r for which J-r is isomorphic to F;
a_F,O(J)   = sum over those roots of |N_J(r) intersect O|;
b_F,P(J)   = sum over those roots of the number of pairs in orbit P whose
             two vertices are both adjacent to r.
```

Double counting gives the complete equations

```text
sum_J d_F(J) x_J   = 93 n_F,

sum_J a_F,O(J) x_J = |O| (14 - deg_F(O)) n_F,

sum_J b_F,P(J) x_J = |P| (c(P) - cn_F(P)) n_F,
```

where `c(P)=1` for an edge orbit and `c(P)=2` for a nonedge orbit.  No
automorphism, transitivity, or support restriction is imposed on the target
graph.  Automorphisms are used only to partition equivalent distinguished
vertices and pairs within each small class.

The exhaustive system has:

```text
deletion rows:                 62
vertex-orbit rows:            207
edge-pair-orbit rows:         180
nonedge-pair-orbit rows:      263
total rows:                   712
seven-class columns:          208
```

The exact census independently regenerates all labeled masks and finds
`394020` locally admissible labeled order-seven graphs and `208` unlabeled
classes.

## Independent source-six gate

Before using the published six-count vector as a right-hand side, I rebuilt
the analogous orbit-refined transitions from smaller orders.

Starting only from `n=99`, the exact chain has class counts

```text
order:                1   2   3   4   5
unlabeled classes:    1   2   4   9  21
```

The transition matrices have full column rank, certified respectively over
`F_3`, `F_2`, `F_5`, and `F_3`.  Thus their checked nonnegative integer count
vectors are uniquely forced over the rationals by `(n,k,lambda,mu)`.

The source order-six vector then passes all 171 exact orbit-refined `5->6`
rows.  That matrix has rank 61 over `F_7`; adding the source coordinate
`n3=705` raises the rank to 62.  Therefore the six-count right-hand side used
in Wave 23 is independently forced by the SRG parameters plus the stated
`n3`, rather than merely assumed from the source table.

## Exact affine family

Let `A` be the `712 x 208` integer extension matrix.  Exact modular elimination
gives

```text
rank over F_5 = 207.
```

The frozen nonzero integer vector `delta` satisfies `A delta=0`, so the
rational rank is exactly 207.  Adding the single coordinate row for the pinned
class `H_11` raises the rank over `F_5` to 208.

Discovery fixed only

```text
H_11 = h11 = 4z
```

at the adjacent admissible values `z=353` and `z=354`.  The numerical points
were rounded, and the rounded vectors were accepted only after exact integer
replay.  Writing the first vector as `base` and their difference as `delta`
gives

```text
x(z) = base + (z-353) delta.
```

The standard-library exact checker proves

```text
A base  = b;
A delta = 0;
sum(base) = binom(99,7);
sum(delta) = 0.
```

Every coordinate is integral for integer `z`.  At the interval endpoints,

```text
z=353: minimum count 2, support 208;
z=705: minimum count 0, support 207.
```

Every coordinate is affine, so endpoint nonnegativity proves nonnegativity on
the entire real interval `[353,705]`, and hence for all 353 allowed integer
values.

## Hamiltonian formulas: comparison, not hidden assumptions

The source figure's `H_i`-to-canonical-mask alignment is a pinned, cited input.
Only `H_11=4z` was used to choose a coordinate on the forced one-dimensional
family.  The other 18 published formulas were not solver constraints.

After deriving the family, all 19 aligned Hamiltonian coordinates match the
published affine formulas at `z=353` and `z=354`.  Since both sides are affine
in `z`, they agree identically.  The correct classification is therefore:

```text
CITED source formulas; DERIVED_EXACT_REPLAY_PENDING_INDEPENDENT_VERIFIER
within the pinned alignment; not an independent proof of the figure
transcription.
```

## Exact replay and hostile tests

Reproduce with:

```text
python attempts/wave23-weighted-extensions/exact_check.py \
  --output attempts/wave23-weighted-extensions/exact-results.json

python -m unittest discover \
  -s attempts/wave23-weighted-extensions \
  -p test_exact_check.py -v
```

The exact checker uses only the Python standard library, rebuilds every
census, automorphism orbit, transition coefficient, modular rank, lower-order
gate, affine row, endpoint inequality, and Hamiltonian comparison.  All 18
hostile tests pass, including mutations of parameters, lower counts, masks,
ordering, affine bases and slopes, H disclosures, integer types, completeness,
and private absolute paths.

## Retained failures and scope wall

The failure ledger preserves the missing-SciPy run, the aborted dependency
locator, the inadmissible interpolation helper, and the false HiGHS
infeasibility caused by shrinking matrix coefficients during row scaling.
Solver exit codes were never treated as certificates.

The affine count family does not assign types consistently to overlapping
subsets and does not encode a `99 x 99` adjacency matrix.  It is evidence only
that this complete set of necessary order-seven counting equations cannot
exclude the incumbent.
