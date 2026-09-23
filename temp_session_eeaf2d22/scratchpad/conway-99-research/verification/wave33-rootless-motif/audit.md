# Wave 33 rootless-motif candidate audit

## Verdict

`PASS_SCOPED_WITH_NONBLOCKING_WORDING_QUALIFIER`

The candidate's exact local mathematics reproduces independently.  It does
not prove a global motif-forcing or motif-avoidance theorem, a rootless
endpoint, `n3=708`, Conway-99, or novelty.  Every such status remains
`UNKNOWN`.

The one sustained objection is a scope correction.  The report sentence

> all two-leg spectral/incidence contractions are locally blind to the motif

is too broad when read literally.  The verified replacement is:

> At a formally allowed `q(T)=q(U)=2` `R2` pair, every bilinear
> `Q[Gamma]` contraction and every `N^T p(A) N` contraction is blind to the
> displayed null trade.

This is nonblocking because the candidate separately and explicitly excludes
uncontracted three-leg incidence, full projector/Schur compatibility, and
global compatibility.

## Independence and provenance

- The six-file precomparison package was frozen before any candidate byte was
  inspected.  Its manifest SHA-256 remains
  `b76da4963b9588102b657e04dfd9195bb4a5d9bbe7a365ae255023b6385863e8`.
- The released nine-entry candidate freeze has SHA-256
  `8cca06d858a401c6c4f054daae8e35fb4796fabb0f15877547a6c943971c32e0`;
  every entry matches.
- The candidate's eight-entry artifact manifest and twelve-entry input freeze
  both match, and the result JSON input map is exactly the frozen input map.
- Candidate Python was read statically only.  It was never imported or
  executed.  All arithmetic was reproduced by verifier-owned standard-library
  code.
- The candidate's two formal tables differ from the independently frozen
  precomparison tables, while yielding the same required contractions.  This
  is positive evidence against accidental byte reuse.

## Verified scoped findings

### Fused triangle algebra

The independent spectral evaluation gives

`Q[Gamma] = span{I,J,Gamma,C}`, with
`C=Gamma^2-5 Gamma-18 I`, dimension four, and evaluation determinant `48510`.
The submitted multiplication identities reproduce:

```text
Gamma^2 = 18 I + 5 Gamma + C
Gamma C = -18 I + 18 J - 2 Gamma - C
C^2     = 72 I + 216 J - 16 Gamma - 14 C
```

The `Gamma`, `C`, and scaled-projector spectra also match independently.

### Formal local-table non-forcing

Both submitted `6 x 6` tables are exactly nonnegative integral, symmetric,
have margins

`(1,18,22,174,6,10)`,

and have the fixed `R2` cells `D,R2=1`, `R2,D=1`, and
`Gamma,Gamma=2`.  Their common `Q[Gamma]` contraction matrix is

```text
0   1   0    2
1 231  18  216
0  18   2   16
2 216  16  188
```

The one-minus-zero trade has zero margins and zero contraction against all
sixteen ordered basis pairs, but changes the `R3,R3` cell from zero to one.
Both tables give the required local `M^2` entry `-21`.

This verifies a formal local obstruction only.  Neither table is certified as
a globally realizable triangle-relation tensor, and global occurrence of the
formal `q(T)=q(U)=2` `R2` pair is not established here.

### Incidence transport and its boundary

For every nonnegative integer `k`,

`N^T A^k N = (Gamma+3I)(Gamma-4I)^k`,

so every such matrix belongs to `Q[Gamma]`.  The verifier reproduced the first
six submitted spectral rows and checked the polynomial identity independently.
Individual `R2` and `R3` relation matrices do not belong to `Q[Gamma]`; hence
the common-`R3` statistic is not determined by the fused algebra alone.

The reduction covers matrix-multiplication words reducible to
`N^T p(A) N`.  It does not cover arbitrary statistics merely described as
"two-leg", uncontracted vertex labels, genuine three-leg incidence, or global
projector/Schur compatibility.

### Actual `R2` board and partial controls

Starting from the normalized cross edges `t0-u0` and `t1-u1`, direct
`lambda=1`, `mu=2`, degree-`14` subtraction gives the weighted board

```text
1 0 1
0 1 1
1 1 2
```

with eight both-side witnesses, row-only and column-only counts
`(9,9,8)`, and `33` witnesses on neither side.  Exhaustive weighted
three-by-three transversal enumeration gives exactly four candidates:

```text
(b00_0,b11_0,b22_0)
(b00_0,b11_0,b22_1)
(b00_0,b12_0,b21_0)
(b02_0,b11_0,b20_0)
```

Thus `708` unordered `R2` pairs would index `2832` candidates, with
multiplicity.  This is not a count of distinct realized graph triangles.

The verifier independently rebuilt both submitted 99-vertex partial edge
assignments.  They have base degree `14`, exact base-pair `lambda/mu` counts,
no current common-neighbor cap violation, and respectively close zero and one
of the four candidates.  Most outside-outside edges, outside degrees, and
parameter equations remain unset, so these objects are neither graphs nor
extension certificates.

### Mixed-trace normalization and status wall

A three-object witness with one unordered `R2`-`R3`-`R3` motif gives
`tr(A_R2 A_R3^2)=2`, verifying the candidate's factor of two between unordered
motifs and ordered `R2` orientations.  Rootlessness would require this trace
to vanish, but neither positivity nor vanishing is established for a target.

The verifier rejects any promotion of the global statuses.  The final wall is:

```text
global table realizability       UNKNOWN
partial-control extendibility    UNKNOWN
actual motif forcing             UNKNOWN
actual motif avoidance           UNKNOWN
rootless endpoint                UNKNOWN
n3=708                           UNKNOWN
Conway-99                        UNKNOWN
novelty                          UNKNOWN
```

## Reproduction

From the repository root:

```powershell
python -B verification/wave33-rootless-motif/candidate_static_check.py --output verification/wave33-rootless-motif/comparison-results.json
python -B -m unittest discover -s verification/wave33-rootless-motif -p "test_*.py" -v
```

The verifier suite contains 48 tests and uses only the Python standard
library.
