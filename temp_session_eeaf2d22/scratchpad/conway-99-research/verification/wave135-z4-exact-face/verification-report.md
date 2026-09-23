# Wave135 independent verification report

## Verdict

The sealed Wave135 exact-face checkpoint is independently verified. The
forbidden transform matrix has exact rational rank 143 and nullity 976.
Adding identity and total-size equations gives affine rank 145 and dimension
974; the independent primal torsion-shell equality gives rank 146 and
dimension 973.

This is an exact representation reduction, not a feasibility result.
Rational feasibility remains `UNKNOWN_WALL`; integral feasibility, code and
graph realizability, novelty, and Conway-99 remain `UNKNOWN`.

## Clean-room rank proof

For source `(a,b,c)` and forbidden dual target `(*,r,s)`, the verifier removes
the common nonzero factor `2^(r+1)` and uses

```text
K_r(a+c,c) K_s(99-r,b).
```

Splitting the 161 rows by `r` bounds their ranks by

```text
r:       0   2   4   6  92  94  96  98
rank:    7  44  44  44   1   1   1   1
```

for a total upper bound of 143. A deterministically selected 143-by-143
integer minor is nonzero modulo `1,000,000,007`, proving the matching lower
bound over the rationals. Separate modular minors certify the two affine rows
and the torsion row.

## Sealed artifact replay

The discovery manifest has 16 entries. The independent verifier:

- replays all 18 sealed primitive left-kernel relations against its own
  matrix and verifies that those relations have rank 18;
- verifies the sealed selection of 143 target rows has rank 143;
- matches the FLINT and independent-prime ranks 143, 145, and 146;
- matches coefficient and augmented rank 146, proving equality consistency;
- verifies the torsion equality raises rank by exactly one; and
- checks both bounded search objects contain only an `UNKNOWN_WALL` trace.

The shifted trace ends after six replays with 521 violated rows. The earlier
unshifted trace ends after five replays with 451 violated rows. Neither
contains a terminal witness, Farkas certificate, or negative inference.

## Torsion shells and fibre sizes

The frozen code types imply

```text
sum_(source nodd=0) A_source = 2^54,
sum_(dual nodd=0) B_target   = 2^44.
```

The second equation is redundant after the first and the seven forbidden
dual `nodd=0` rows. The exact row identity is

```text
dual_allowed_b0_numerator + sum_(7 forbidden b0 rows)
  = 2^98 * primal_b0_indicator.
```

For nonzero residue weights, constant fibres give integer divisibility rather
than new fixed rational equations: primal orbit-shell sums are multiples of
`2^54`, and dual orbit-shell sums are multiples of `2^44`.

## Candidate verification boundary

The package includes hostile exact validators for a future dense rational
primal or sparse Farkas certificate. They check every coordinate, exact
rational encoding, lower bound, zero row, affine equation, allowed dual row,
multiplier sign, stationarity coordinate, and strict Farkas margin.

A passing rational enumerator would still not be an integral enumerator,
`Z4` code, adjacency matrix, graph, or Conway-99 resolution.

## Reproduction

- Independent result replay: pass.
- Independent hostile tests: 13/13 pass.
- Discovery exact checker: pass.
- Discovery tests: 4/4 pass.
- Free physical memory after parallel checks: 45.9 percent.
