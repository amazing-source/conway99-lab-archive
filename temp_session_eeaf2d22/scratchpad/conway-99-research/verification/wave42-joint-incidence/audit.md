# Independent audit

## Verdict

The canonical mask-51739 joint-incidence reduction is independently
reproduced and may be promoted from discovery `DERIVED` to
`VERIFIED_SCOPED_CONDITIONAL_REDUCTION`.

The result is useful because it turns any 60-column completion of this one
canonical local block into an exact 45,032-candidate three-way matching with
strong aggregate constraints.  It does not solve that matching and therefore
does not exclude the branch.

## Independence

`protocol-freeze.md`, the standard-library implementation, hostile tests, the
complete precomparison result, and an independently generated two-fibre
positive certificate were frozen in `implementation-freeze.sha256` before
the discovery package was opened.  The verifier imports no discovery code.

The independent two-fibre certificate is not the discovery certificate.
Both distinct permutations reconstruct the same complete `12 x 12`
concurrence target.  This is a positive control only: neither permutation
chooses fibre-2 pairs.

## Mathematical checks

The frozen Wave 41 edge list reconstructs a cubic, triangle-free core and the
39-vertex `K=J-I-2A` principal block.  Direct Gaussian elimination over
`F_7` gives ranks 32 for `3I-A_core` and 33 for `K39`.

For core vertices `u,v`, the verifier derives the outside concurrence
`Q_uv` by subtracting already visible common neighbours from the SRG total
`lambda=1` or `mu=2`.  It obtains diagonal 10, row sum 60, and the exact
matrix digest recorded in `independent-results.json`.

The core components have orders 12 and 24.  For the small component, the
60 hypothetical column intersections have first moment 120 and second
moment 240.  Cauchy gives the same lower bound `120^2/60=240`; equality
forces all intersections to equal 2.  The analogous large-component
calculation forces 4.

Within each fibre the six matching pairs have concurrence zero and the other
60 pairs have concurrence one.  Since every outside column uses exactly two
vertices in each fibre, all 60 nonmatching pairs are used exactly once.  The
small-component pair inventory `24,32,4` at sizes `0,1,2` uniquely forces
the six column-pattern multiplicities `4,4,4,16,16,16`.

The verifier exhausts all `60^3` pair triples.  Exact Gram support leaves
118,718; component equality leaves 49,736; pointwise SRG
common-neighbour feasibility leaves 45,032.  The last condition is the
independently expressed equivalent of discovery's mixed-`BH` nonnegativity
test.

Finally, the Gram moments force column overlap counts
`458,1004,308`.  Local matching structure at every core vertex forces a
hypothetical eight-regular outside graph to use `96,144,0` edges at overlap
sizes `0,1,2`.  The SRG common-neighbour equation then forces 32 triangles
and 181 four-cycles.

## Adversarial controls

Fifteen verifier tests pass.  Hostile tests reject:

- a removed canonical core edge;
- a duplicate entry in either two-fibre certificate;
- a changed frozen input hash;
- a changed six-set count;
- an inflated endpoint status.

The discovery package's nine tests also pass, and every entry of its package
manifest matches.

## Scope wall

The verified result is conditional on `n3=4158`, `r3=12`, all edges having
local type `2+2+2`, and occurrence of the canonical mask-51739 rank-33
triangle block.  It covers neither the other rank-33 lifts nor all
triangle-free lifts.

No full 60-column `B` was constructed or excluded.  No compatible
eight-regular `H` was constructed or excluded.  The endpoint, a strict
general upper bound below 4158, Conway-99, and novelty/priority all remain
unknown.

