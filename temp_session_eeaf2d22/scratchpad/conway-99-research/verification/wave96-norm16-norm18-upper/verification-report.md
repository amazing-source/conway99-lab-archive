# Wave 96 adversarial verification report

Claim label: `VERIFIED_WITH_CLARIFICATION`

## Frozen input

The discovery manifest hashes to
`1d1e7d01edfbfcd2871683390b56e16dc36a18cfc899f301f15a0fce3b246a73`.
All ten listed discovery files and all six imported verifier manifests
match their frozen SHA-256 values.

## Findings

### Weighted rank-28 implication: PASS

Substitution of `N14<=4950` into the frozen positive identity gives

```text
407*N16+43*N18 >= 2,165,002.
```

The independently recomputed alternating-C4 minima are `20,18,26`. On
antipodal supports the objective/incidence ratios are
`407/10,43/9,43/13`, so `407/10` is the maximum. A cap of 25 gives rational
upper bound `4,230,765/2`; evenness sharpens this to `2,115,382`, a
contradiction. A cap of 26 gives even upper bound `2,199,996` and does not
close this relaxation. The cap of 25 is sufficient and remains unproved.

### Fixed-cycle projector and positive control: PASS

The polynomial `(27I-9A+J)/63` takes values `0,0,1` on the `14,3,-4`
eigenspaces. Its induced-C4 principal block is invertible, and the
alternating coordinate interpolant has squared norm `28/5`. The norm-16
residual sphere therefore has dimension 40 and squared radius `52/5`.

An independently enumerated 40-dimensional cross-polytope has 80 points
and minimum squared distance `104/5`, greater than 14. This is a valid
positive control against any proof using only the common coordinate
projector, residual dimension/radius, and minimum distance. It is not a
lattice or graph construction.

### Norm-20 dictionary: PASS WITH WORDING CLARIFICATION

The frozen nonintegral energy floor is 22, so norm 20 remains in the
integer `-4`-eigenvector class. The coordinate equation gives
`|t_i|<=2`; parity and the frozen binary-code distance give at most three
magnitude-two coordinates. Independent enumeration yields exactly the six
submitted profiles up to global sign.

The five mixed profiles are excluded:

- both `m=3` profiles lack enough negative mass for a `+2` equation;
- in the same-sign `m=2` profile the two nonadjacent `+2` vertices share
  all eight negative units, contradicting `mu=2`;
- in the mixed `m=2` profile the `+2` meets the `-2` and all six negative
  units, and every positive unit shares at least three of those neighbours;
- in the `m=1` profile the `+2` has at least eight negative-unit neighbours
  and each positive unit has at least four, forcing intersection at least
  three whether the pair is adjacent or nonadjacent.

For the mixed `m=2` bullet, the submitted prose says every positive unit
meets the `-2`. More precisely, if it does not, it shares at least four
negative-unit neighbours with the nonadjacent `+2`, already contradicting
`mu=2`; after that subcase is removed, adjacency to `-2` is forced and
still yields at least three common neighbours. This is a clarification,
not a change to the theorem.

Thus only ten `+1` and ten `-1` coordinates survive.

### Alternating cycles and rank 30: PASS

The restricted-eigenvalue edge bound is `5170/99`, while a unit norm-20
support has `40+4h` edges, hence `h<=3`. Exhaustion of all graphs with up
to three edges on one ten-point sign side gives minimum degree-square sums
`0,2,4,6`. The corresponding alternating-C4 lower bounds are
`15,23,31,39`.

The frozen `q=14` prefix `x7+x8+x9+x10>=6842`, together with the dictionary
through `x10=N20`, gives at least `102,630` oriented vector-C4 incidences.
A universal cap of 24 antipodal extensions has capacity only
`2079*48=99,792`, so it would contradict the prefix. The cap is unproved.

### Jacobi continuation: HONEST UNKNOWN

All induced C4s have the checked common principal Gram matrix. At `q^8`
and `q^9`, summing both alternating Laurent monomials over all C4s has the
claimed oriented-incidence interpretation. For a rank-44 lattice, the
degree-eight C4 polynomial decomposes into harmonic weights
`22,24,26,28,30`.

No exact rational-characteristic/coset transformation law or positivity
control for signed harmonic coefficients is supplied. Accordingly this is
a plausible continuation route, not a bound or certificate.

## Verdict boundary

Finite scoped claims: `VERIFIED_WITH_CLARIFICATION`.

Pointwise caps 25 and 24: `UNKNOWN`.

Rank 28, rank 30, `N16/N18` upper bounds, Conway-99, and novelty:
`UNKNOWN`.
