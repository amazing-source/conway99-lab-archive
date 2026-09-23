# Wave 147: two-root order-eight flag lift

Status: **DERIVED exact model; strict upper bound UNKNOWN**.

This package realizes the smallest genuine flag/Terwilliger lift beyond the
order-seven PSD systems already present in the repository.  Fix an ordered
edge or ordered nonedge root.  A flag consists of that root and three
unordered free vertices, so it has order five.  Products of two flags have
union order five through eight.

The exact finite Gram matrices are

```text
ordered-edge root:       66 x 66,
ordered-nonedge root:    87 x 87.
```

For every root embedding `theta`, let `c(theta)` be the integer vector of
flag-extension counts.  Then

```text
M_sigma = sum_theta c(theta)c(theta)^T >= 0
```

without a graph automorphism assumption or an asymptotic limit.

## Exact package

The checker constructs:

- the complete locally admissible class streams of orders five through eight,
  with counts `21, 62, 208, 916`;
- all `2,414` class coefficient matrices for the two PSD blocks;
- `272,054` nonzero upper-triangular integer coefficients;
- all `208` ordinary order-seven-to-eight deletion equations, containing
  `5,333` nonzero terms; and
- a deterministic compressed coefficient artifact.

The induced `N3` graph is two disjoint triangles joined by exactly two
independent matching edges.  In both root families there is an explicit
matrix entry whose order-six contribution is

```text
4*n3
```

while its triangular-prism coefficient is zero.  Thus the lift does not lose
the target parameter.  Other induced classes also contribute to that entry,
so this is a coefficient identity, not an isolated formula for `n3`.

The `3 x 3` rook graph, `srg(9,4,1,2)`, is an exact positive control.  Its
direct pair-root moment matrices are explicit sums of 36 integer outer
products.  The checker also reproduces its induced counts `n3=0` and
`P=6`.

## What remains

For a general upper bound, retain `n3` as a variable, import the exact
order-six affine count formulas and verified order-seven equations, add the
stronger order-eight degree/common-neighbor extension rows, and maximize
`n3` subject to the two PSD blocks and count nonnegativity.

A strict result requires an exact rational dual certificate.  A suitable
certificate has rational PSD multiplier matrices, nonnegative rational
count multipliers, and an exact combination of count identities equaling
`U-n3` for some `U<4158`.  A floating SDP status is not evidence.

This package does not run that SDP.  It proves that the finite model and the
full coefficient layer are available and records the remaining obstruction
honestly.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave147-alternative-lane\exact_check.py `
  --verify attempts\wave147-alternative-lane\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest `
  attempts.wave147-alternative-lane.test_exact_check -v
```

The full replay uses exact integer/rational arithmetic and checks a 15% free
physical-memory floor during the order-eight class construction.

