# Wave 61 independent audit

## Verdict

`VERIFIED_WITH_CORRECTION` for the frozen finite-field and parity-relaxation
claims.  The exact numerical census reproduces independently.  The
correction is a scope correction to the cubic wording, not a new
contradiction: the pair-margin identity and its scalar totals are verified,
but feasibility of a nonnegative integral third-order tensor was not tested.

The conditional `kappa=3` incidence lane, the prism-free endpoint, and
Conway-99 all remain `UNKNOWN`.

## Input and independence audit

- The preinspection freeze was written before opening Wave 61 discovery
  implementation, tests, results, protocol, or report.
- All frozen Wave 61, Wave 58, and Wave 60 bytes still match that freeze.
- The discovery package manifest resolves with no missing or mismatched file.
- The verifier imports no Wave 60 or Wave 61 implementation.
- All 18 supplied component records were checked from their edge lists.
  They are cubic, connected, triangle-free, obey the fixed-fibre and
  cross-fibre matching conditions and codegree caps, have the stated
  four-cycle counts, and have 18 distinct canonical signatures under
  `S4 x S4 x S4` with fibres fixed.
- Exactly `C(20,3)=1140` unordered triples with repetition were visited.
- No automorphism of a completed graph, triangle, fibre system, component
  system, row set, or column set was assumed.  Fibre-preserving coordinate
  permutations were used only to audit the supplied type classification.

## Exact replay

The independent `F2` Gram-rank histogram is

| rank | 14 | 16 | 18 | 20 | 22 | 24 |
|---:|---:|---:|---:|---:|---:|---:|
| triples | 67 | 415 | 412 | 185 | 51 | 10 |

The six fibre/component indicators have one relation and span a
five-dimensional subspace of `ker(B^T)` over `F2`.  Thus
`rank_F2(B)<=31`; because the target Gram matrix is alternating,
`rank_F2(G)` is even and at most 30.  Every observed rank is at most 24.

The local 198-bit generator ranks are

```text
140:56, 144:189, 148:333, 152:327, 156:171, 160:54, 164:10.
```

The full 630-bit generator ranks are

```text
438:56, 442:189, 446:333, 450:327, 454:171, 458:54, 462:10.
```

All 1,140 local and full parity targets lie in their respective spans, so
both filters eliminate zero triples.  Candidate supports range from 15,936
to 27,200 six-sets.

The independent 21-pattern enumeration has six zero images, nine weight-four
images, and six weight-six images, covering all 16 binary `3 x 3` matrices
with even row and column sums.  Its augmented moment rank is 11, and all
1,140 targets pass this parity relaxation.

Over odd primes the maximum Gram rank is 32.  At `p=7` all 1,140 targets
have rank 32; the complete rank, discriminant, and anisotropic-dimension
histograms in `independent-results.json` exactly match discovery.  A
complement of dimension at least 28 can absorb either finite-field
discriminant class, so this yields no unrestricted Gram-factor obstruction.
It does not produce the required binary weight-profile columns.

## Quadratic and Witt audit

For `E_60`, the even-weight subspace of `F2^60`, the radical is the
all-ones line and `q(v)=wt(v)/2 mod 2` descends to a 58-dimensional
minus-type quotient.  Independently,

```text
sum_{v in E_60} (-1)^q(v) = Re((1+i)^60) = -2^30,
```

so the quotient has Arf invariant one.

The discovery's radical classes and reported slack histogram reproduce
exactly.  When `q` is nonzero on the pulled-back radical, its formula counts
that line as one occupied dimension; because the nondegenerate quotient
ambient is even-dimensional, an explicit parity adjustment consumes one
additional dimension.  The adjusted slack histogram is

```text
10:67, 12:415, 14:412, 16:185, 18:51, 20:10.
```

It remains nonnegative for every target.  Thus the wording convention does
not change the discovery's substantive conclusion.  After splitting off the
totally singular radical directions, the remaining complement has dimension
at least ten; both Arf types can be absorbed in such a complement.  The
quadratic/Witt screen therefore finds no obstruction.

## Cubic correction

For a hypothetical six-uniform column design, if `T_ijk` counts columns
containing three distinct rows, then every column containing a fixed pair
supplies four choices of a third row:

```text
sum_{k not in {i,j}} T_ijk = 4 G_ij.
```

The target Gram matrices have row pair-sums 50 and total pair count 900, so
the derived scalar totals are 100 triples through each row and 1,200 triples
overall.  Seven pair-margin histograms occur, exactly as discovery reports.

This is not a feasibility proof for `T`.  Neither checker solves the system
for a nonnegative integral symmetric tensor satisfying all 630 pair margins,
much less a tensor realized by the same 60 distinct six-subsets.  Therefore
the report phrase “pass all consequences determined by `G`” must be read only
as “pass the displayed scalar consequences of the pair-margin identity.”

## Hostile controls

- deleting a component edge is rejected by structural validation;
- a one-bit mutation of the triple-zero 198-bit RHS is outside its span;
- a one-bit mutation of the corresponding 630-bit RHS is outside its span;
- a one-bit mutation of a pattern-moment RHS is outside its span;
- odd-prime congruence elimination reproduces the rank and square class of a
  hyperbolic plane over each tested prime;
- frozen-byte mutations change their SHA-256 digest;
- independent and discovery focused test suites pass.

These controls show that the checkers can reject malformed inputs and false
targets; their all-positive census is not a vacuous solver-status test.

## Reproduction and determinism

The discovery manifest matches every listed file, and its seven focused tests
pass.  The independent focused and hostile suite passes.  A fresh exhaustive
`--verify` replay reconstructed all 1,140 records and exited cleanly against
the stable saved result
`a18c6f8343b480a6fd278dc53509aa6f4a85b193aae2400efe1fb151e93a15c1`.

An earlier determinism attempt failed because a delayed legacy-schema writer
changed the target while comparison was in flight.  That operational failure,
its two hashes, and the correction are retained in `failed-routes.md`; it was
not suppressed or treated as mathematical evidence.

## Boundary

No simultaneous integer `B`, compatible `A_Y`, endpoint graph, endpoint
exclusion, general `n3` upper-bound improvement, or Conway-99 resolution is
supplied.  The exact missing layer is nonnegative integer and
distinct-column coupling with realizable third- and higher-order overlaps.
