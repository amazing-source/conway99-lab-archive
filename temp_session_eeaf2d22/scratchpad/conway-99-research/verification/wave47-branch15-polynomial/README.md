# Wave 47 clean-room polynomial-calculus verification

Status: `VERIFIED_SCOPED` for the seven frozen local degree-two calculations
and the Wave 43 degree-four partition only.

The verifier imports no discovery implementation. Before opening the sealed
result or code, it froze an independent parser, propagation replay, Hamming
slice enumerator, `F_2` row reducer, and squarefree degree-two saturation.
The independent result was then SHA-bound in `precomparison-freeze.sha256`.

## Verified result

- all four frozen input hashes and three decompressed OPB hashes match;
- generalized-unit propagation reproduces all 830 frozen assignments,
  including 174 primary variables;
- each of seven mate-coordinate windows has 24 residual vertices, 276 primary
  variables, and 48 complete coordinate-incidence blocks;
- complete Hamming-slice enumeration produces the exact degree-at-most-two
  vanishing spaces;
- the new affine ranks are exactly `[2,1,2,2,2,2,2]`, for 13 relations total;
- every claimed relation, decoded edge/label map, constant, row hash, and
  common-coordinate support matches;
- no constant-one contradiction and no new single-variable assignment is
  derived;
- the exact-block-only and full final affine spaces are mutually equal in all
  seven windows;
- all 34,340 active Wave 43 rows have a unique window, four distinct primary
  variables, negative polarity, and a degree-four falsifying monomial;
- all sealed slice-catalog, axiom-catalog, echelon, final-linear-RREF, and
  relation-catalog hashes match.

The discovery README sentence calling these “24 exact-one” plus “24
exact-two” blocks per window is inaccurate: direct reconstruction gives
unsimplified target one for all 48 local blocks. This is a prose error, not an
implementation error; the sealed computation parses and uses the correct OPB
blocks, and every committed computational hash still matches.

“Zero assignments” means zero newly forced one-variable assignments. It does
not mean that the literal all-zero vector satisfies the affine exact-count
space.

## Reproduce

```powershell
python verification\wave47-branch15-polynomial\independent_check.py `
  --validate verification\wave47-branch15-polynomial\independent-result.json

python verification\wave47-branch15-polynomial\comparison_check.py `
  --validate verification\wave47-branch15-polynomial\comparison.json

python -m unittest `
  verification\wave47-branch15-polynomial\test_independent_check.py -v
```

## Scope wall

This does not prove branch 15 SAT or UNSAT, exclude the endpoint, improve the
general upper bound, construct a graph, or resolve Conway-99. The seven
vertex windows overlap, wider and cross-window constraints are omitted from
the degree-two theory, and the Wave 43 cuts begin at degree four.
