# Hostile controls

- **Frozen bytes first.** Fifteen Wave 74 and imported Wave 71 files were
  SHA-256 frozen before claim checking. The test suite rechecks every byte.
- **No discovery-code reuse.** The verifier does not import or execute
  `attempts/wave74-short-vector-closure/exact_check.py`.
- **Independent enumeration order.** The verifier searches
  \(n_2,\ldots,n_7\) by a Cartesian product and solves for \(n_1,n_0\);
  discovery recursively searches counts beginning at \(d=0\).
- **Both two-edge shapes.** All 630 pairs of distinct edges on nine labeled
  vertices are classified. Only adjacent and disjoint shapes occur.
- **Shape asymmetry allowed.** One adjacent side is already impossible by
  applying its 71 incidences to the other side's capacity 70; equality of
  the two shapes is never assumed.
- **Same-support common neighbors retained.** The general verifier subtracts
  both opposite-support and same-support contributions. For the adjacent
  shape the opposite-support term already contradicts capacity; the formal
  full residual is \(-2\), not the discovery JSON's opposite-only sentinel
  \(-1\). For the disjoint shape the same-support term is exactly zero.
- **Per-side meaning of \(d_x\).** The zero-coordinate equation makes
  \(d_x\) the count in each sign side; total support degree is \(2d_x\).
- **Tight pigeonhole perturbation.** With 81 vertices, pair moment zero, and
  incidence sum 81, the unique histogram is \(n_1=81\). Increasing the
  incidence sum to the claimed 82 produces no histogram.
- **Complete degree range.** Since total support degree is \(2d_x\le14\),
  the range \(0\le d_x\le7\) loses no cases.
- **Exact arithmetic only.** No floating point, optimization status,
  randomized search, automorphism, or transitivity enters the result.
- **No realization inflation.** The 4/20/6 histograms are labeled necessary
  aggregate conditions only. They are not incidence matrices or graphs.
- **Conditional wall.** Wave 71 is not independently verified by this
  package. Conway-99 and novelty remain `UNKNOWN`.
