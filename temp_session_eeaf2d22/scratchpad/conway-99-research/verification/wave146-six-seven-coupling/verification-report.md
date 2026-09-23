# Wave146 six-to-seven coupling: independent verification

## Verdict

**PASS_RATIONAL_RELAXATION**, with claim label **VERIFIED** for the exact
relaxation statement only.

The sealed sparse vector is an exact nonnegative rational solution of the
complete Wave146 one-root system at `n3=4158`. Therefore this six-to-seven
aggregate lift does not improve the rigorous upper cap. The earlier unscaled
HiGHS infeasibility was a numerical false lead and carries no evidentiary
weight.

The final discovery manifest was frozen before the new certificate was read.
Its SHA-256 is
`6a4f1125d877f4bc1dfcfe522dea66e95216416bd09550fa36aadbcbeb1f2b17`;
all 14 entries pass. The earlier two-file freeze with hash
`a783701cd4b1dd1b20c60f16985444836950a56e33b5b39de336d27efe06c88b`
is retained but explicitly superseded.

## Root condition

Let `H` be the graph on a six-set `S`, and let `P` be the neighbors in `S` of
an outside root `x`. For every `u` in `S`, the common neighbors of `x` and
`u` already visible in `S` are `N_H(u) intersect P`. Thus:

- if `u` is in `P`, the pair `xu` is an edge and this count is at most
  `lambda=1`;
- if `u` is not in `P`, the pair `xu` is a nonedge and this count is at most
  `mu=2`;
- if both `u,v` are in `P`, root `x` adds one common neighbor to the old pair,
  so that pair's residual common-neighbor budget must be positive.

The verifier compared this formula directly with local admissibility of the
constructed rooted seven-vertex graph for all `62*64=3,968` class/pattern
pairs. Every comparison agreed.

## Exact results

- Independently regenerated the seven-extendable support of every six-class.
  Exactly 25 weight cells are removed across 16 classes.
- All 65 positive cells in the Wave144 endpoint aggregate remain locally
  supported.
- Reconstructed the fixed repaired profiles. Their rooted counts violate the
  columnwise deck identity `R_(38,8)=2 R_(37,12)` by exactly
  `3,076,026,288`. This refutes only that deterministic fixed profile.
- Revalidated the frozen upstream list of 208 order-seven canonical classes,
  then independently rebuilt every deletion and rooted-pattern multiplicity.
- Reconstructed 944 rooted automorphism-orbit types, 343 six-class/weight
  cells, 13,973 variables, 8,981 equalities, and 110,269 integer matrix
  nonzeros.
- Parsed the discovery support without importing any Wave146 model builder.
  All 2,998 positive rational coordinates, with maximum denominator four,
  satisfy every rebuilt equation exactly. The support digest is
  `f0596655578f0d09807b31a0aa339658f8a51f5ae4f98a82157002a3ac4c21d0`.
- The certificate has `h11/4=4158`, hence `h11=16632`.
- Three focused tests passed, including rejection of a changed certificate
  coordinate. Free host memory remained above the required 20% threshold.

## Semantic audit

The equations are necessary for any actual graph. `X_(H,w,P)` counts oriented
pairs `(S,x)`. Summing by total, vertex incidence, pair incidence, and odd
pattern gives the local rows. Each seven-set supplies seven distinguished
deletions, giving the rooted-link rows by double counting.

There is no missing automorphism-orbit factor. A chosen isomorphism from an
actual six-set to the canonical representative can permute `P` inside
`Aut(H)`, but the link equation sums every pattern in that full orbit. The
right side directly counts deletions in the same orbit, so both sides count
the same oriented objects without division by an orbit or stabilizer size.

The verifier reused the hash-frozen Wave22 list of 208 seven-class
representatives, then independently checked their canonicality and local
admissibility and rebuilt all coefficients. It did not rerun the historical
exhaustive proof that this upstream list is complete.

## Boundary

Exact rational feasibility is not a graph construction. The aggregate `X`
values need not decompose into compatible integer profiles for every
individual six-set, and two rooted seven-set views are not required to agree
on their eight-vertex union. The next materially stronger space is therefore
a two-root/order-eight coupling that retains the relationship between both
outside vertices.
