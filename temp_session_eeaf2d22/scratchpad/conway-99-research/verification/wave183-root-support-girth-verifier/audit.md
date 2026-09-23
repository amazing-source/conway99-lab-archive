# Hostile proof audit

## Verdict

**VERIFIED_WITH_SCOPE.**  Each stated Wave 183 deduction follows from the
frozen Wave 181/182 assumptions.  The deductions do not settle whether the
equality regime exists.

## 1. Common-neighbor rule inside a support

Fix a projective root `r` and let `X_r` be its support.

If `u,v in X_r` are adjacent, the strongly regular parameter `lambda=1`
already says that they have exactly one common neighbor in the whole graph,
so at most one in `X_r`.

Now suppose `u,v` are nonadjacent.  Their two graph-common neighbors are
`c,d`, and exact nonedge-root uniqueness gives `rho_uv=r`.  The vertices
`c,d` cannot be adjacent: otherwise the edge `cd` would have both `u` and
`v` as common neighbors, contradicting `lambda=1`.  If both `c,d` belonged
to `X_r`, uniqueness for the nonedge `cd` would also give `rho_cd=r`.
But `uv` and `cd` are the opposite nonedges of their canonical 4-cycle, so
Wave 182 gives `rho_uv` orthogonal to `rho_cd`.  This would make the
norm-one projective root `r` orthogonal to itself, impossible.  Thus at most
one of `c,d` lies in `X_r`.

This proves that every unordered pair in `X_r`, adjacent or not, has at most
one common neighbor inside `X_r`.  The argument is projectively
well-defined: rescaling either root does not change whether their inner
product vanishes.

## 2. Unordered two-path injection

The 4-regular complement from Wave 182 makes `G[X_r]` regular of degree
`d=m-5`, where `m=|X_r|` and `5<=m<=10`.  Choosing the middle vertex and an
unordered pair of its neighbors counts

`m * binom(d,2)`

unordered internal length-two paths.  Mapping such a path to its unordered
endpoint pair is injective, because two distinct middle vertices for the
same pair would violate the common-neighbor rule.  Therefore

`m * binom(m-5,2) <= binom(m,2)`,

equivalently `(m-5)(m-6)<=m-1`.  At `m=9`, this is `54<=36`, false; at
`m=10`, it is `100<=45`, false.  The pair bound leaves only
`m=5,6,7,8`.

## 3. The cubic case `m=8`

Here `G[X_r]` is cubic.  It has
`8*binom(3,2)=24` distinct unordered endpoint pairs of internal two-paths.
Its 4-regular complement has `8*4/2=16` edges, so at most 16 of those pairs
are graph nonedges.  At least 8 endpoint pairs are therefore graph edges.

An adjacent endpoint pair of a two-path is precisely an edge lying in a
triangle.  Conversely, each triangle contributes its three edges.  Since
`lambda=1`, no edge lies in two triangles, so the number of adjacent
endpoint pairs is exactly three times the number of triangles.  Being a
multiple of 3 and at least 8, it is at least 9; hence at least three
triangles exist.

Distinct triangles are vertex-disjoint.  They cannot share an edge by
`lambda=1`.  If two shared exactly one vertex, their other four incident
triangle edges would give that vertex degree at least 4, contradicting
cubicity.  Three vertex-disjoint triangles require nine vertices, more than
the available eight.  Thus `m=8` is impossible.

## 4. Remaining support graphs

- `m=5`: degree 0, hence `5K1`.
- `m=6`: degree 1, hence a perfect matching `3K2`.
- `m=7`: degree 2, hence a disjoint union of cycles of length at least 3.
  The only partitions of 7 into such cycle lengths are `7` and `3+4`.
  A `C4` has opposite vertices with two internal common neighbors, violating
  the common-neighbor rule.  Therefore the support is `C7`.

No classification-by-enumeration is used.

## 5. Root counts and frame

Let `n_i` count projective roots of support size `i`.  The 2,079 incidences
give

`5n5+6n6+7n7=2079`.

For `R=n5+n6+n7`, the support bounds give
`ceil(2079/7)=297 <= R <= floor(2079/5)=415`.  Subtracting the incidence
equation from `7R` gives the exact defect equation
`7R-2079=2n5+n6`.

Reducing the Wave 182 frame coefficients modulo 3 gives
`5=2`, `6=0`, and `7=1`.  Hence

`2 sum_(m=5) r tensor r + sum_(m=7) r tensor r = 0`,

or, because `-2=1` in `F_3`,

`sum_(m=7) r tensor r = sum_(m=5) r tensor r`.

This identity is a valid split, not a contradiction.  Further progress
needs a new structural argument about the two sides.

## Limitations

- Wave 181 equality and all Wave 182 premises are assumed, not re-proved
  from the original graph axioms in this package.
- The admissible multiplicities and support shapes are necessary
  conditions, not constructions or existence proofs.
- Rank 11 and the original endpoint remain `UNKNOWN`.
