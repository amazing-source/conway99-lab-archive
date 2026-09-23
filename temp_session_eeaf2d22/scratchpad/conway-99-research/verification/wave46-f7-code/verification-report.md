# Wave 46 exact verification report

## Separation chronology

1. `protocol-freeze.md` was written before any Wave 46 artifact was opened.
2. Only the frozen verifier request was then read to identify the exact
   statement.
3. `independent_algebra.py`, `independent-results.json`, and eight tests were
   completed and hashed in `independent-freeze.sha256`.
4. Only after that freeze were discovery code, results, derivation, and
   generators inspected.
5. `compare_sealed.py` independently rebuilt all controls and downstream
   quantities without importing discovery functions.

## Algebraic verification

From symmetry and `M^2=21M`, reduction modulo seven makes every pair of rows
orthogonal. Zero row sums independently place the code in `1^perp`.

The projective-column proof was reconstructed directly from the diagonal and
off-diagonal alphabet. It proves exactly `d(C^perp)>=3`; no stronger
dual-distance statement is promoted.

The row composition has length 231, weight 69, coordinate sum zero, and
squared norm zero. Its six scalar images are distinct. Symmetry transfers
the projective-column result to the rows, proving 1,386 distinct weight-69
codewords.

The exact weight-state recursion reaches residue `(0,0)` for weights zero,
three, and every weight from five through 231. It does not reach `(0,0)` for
weights one, two, or four.

## Complete moments

For a projective `[231,r]_7` code, every coordinate is uniformly distributed
and every pair of distinct coordinates is jointly uniform. Thus

```text
sum_x n_a(x) = 231*7^(r-1),
sum_x n_a(x)(n_b(x)-[a=b]) = 231*230*7^(r-2).
```

All seven first moments and all 49 ordered second moments were evaluated at
the worst rank `r=28`. The known 1,386 scalar row multiples have strict
slack in every case.

The frozen clean implementation originally expressed degree two in the raw
monomial basis `n_a n_b`, adding the degree-one diagonal contribution. The
sealed request uses falling derivative moments. The post-freeze comparison
records both exact minima and reproduces the discovery falling-moment arrays
entry-for-entry. The strict-pass verdict is unchanged.

## Generic controls

The local 21-column block was rebuilt from its three affine-line formulae,
not copied from discovery. Its row sums and complete Gram matrix vanish, all
columns are projectively distinct, and exhaustive enumeration of `7^4`
coefficient vectors reproduces the six-term local weight enumerator.

For each archived rank `r`, the verifier:

1. checked the projection shape `(r-16) x 28` and exact rank `r-16`;
2. applied it to seven block-diagonal copies of the local columns;
3. combined that tail with four fixed copies;
4. transposed the 231 columns into an `r x 231` generator;
5. recomputed row rank, all row sums, the complete Gram matrix, and every
   normalized projective column;
6. recomputed projection and generator-column-stream SHA-256 values;
7. checked scalar compositions of every generator row and its six nonzero
   multiples against the endpoint compositions.

All 17 controls pass, and every endpoint-composition intersection is empty.
The inherited weight-69 lower bound follows from the exact coefficient of
`z^69` in the fourth power of the local enumerator.

## Hostile checks

- Changing entry `(0,0)` of the rank-44 identity projection from one to zero
  destroys projection rank and is rejected.
- A length- and weight-preserving endpoint-composition mutation violates its
  linear residue and is rejected.
- Changing the Schur inverse coefficient of `M` from three to two leaves a
  nonzero product coefficient and is rejected.
- Flipping the prompt quarantine flag to live use is rejected.
- Relabelling the rank-28 control as rank 29 is rejected.
- Noncanonical entries, ragged matrices, zero columns, and proportional
  columns are covered by unit tests.

## Exact boundary

The package supplies a verified null result: ordinary code constraints are
consistent across the entire rank interval, the degree-two moment relaxation
has enormous slack, and the Schur-cube floor is too weak.

The endpoint, a stricter global bound, Conway-99, a complete weight
enumerator, and novelty remain `UNKNOWN`.
