# Waves 135--147 integration audit

Date (UTC): 2026-07-28

Role: verifier/integrator

Target: existence of `srg(99,14,1,2)`

Verdict: **PASS_SCOPED; target UNKNOWN**

## Audit boundary

This audit integrates the independently checked alternative-space packages
from the tightened quaternary face through the two-root/order-eight flag
model.  It does not certify a graph, code, strict `n3` upper bound, or
nonexistence proof.

The rigorous interval remains

```text
708 <= n3 <= 4158.
```

## Integrated verdicts

| wave | exact content retained | integration verdict |
|---|---|---|
| 135 | corrected `Z/4Z` equality rank 146 after the independent torsion-shell row | `PASS_UNKNOWN_WALL` |
| 136 | binary Arf/Gauss split and additive-`GF(4)` graph-state transform | `PASS_WITH_SCOPE_CORRECTION` |
| 137 | rational witnesses for both Arf signs through signed degree five | `PASS_FORMAL_RATIONAL` |
| 140 | two-adic determinant/Arf bridge and opposite-sign local controls | `PASS_WITH_SCOPE_CORRECTION` |
| 141 | bivariate `D8` graph-code transform, exact low rows, `S6/n3`, and `B[6,56]>=n3` | `PASS` |
| 142 | interlace/isotropic rows and kernel moment | `PARTIAL_PASS_WITH_TOP_BAND_VETO` |
| 143 | binary endpoint/Arf witnesses and equality-lattice projection | `PASS_WITH_SCOPE_CORRECTION` |
| 144 | all six-set outside-profile supports and integer endpoint aggregate | `PASS_NULL_BOUNDARY` |
| 145 | corrected `GF(4)` lower-bound merge, pure-`Y` zeros, and shadow transform | `PASS_WITH_WAVE139_VETO` |
| 146 | exact rational one-root six-to-seven endpoint witness | `PASS_RATIONAL_RELAXATION` |
| 147 | finite two-root/order-eight flag coefficient model and positive control | `PASS_WITH_SCOPE` |

## Material corrections and vetoes

1. **Wave 142 top band.**  The target proves binary image minimum eight, not
   fourteen.  Principal-submatrix sizes 86--91 are not forced; only 92--99
   remain.
2. **Wave 143 formal distance.**  Its rational points impose image minimum
   14 and dual minimum 15.  These are stronger formal assumptions, not target
   theorems.  No target implication may use them.
3. **Wave 139 aggregation.**  Five collided states must be summed rather than
   maximized.  The corrected totals are `198`, `8316`, `149688`, `55440`,
   and `462`.
4. **Wave 139 pure-`Y` zeros.**  Weights 8, 10, and 12 are unsupported.
   The corrected forced set is `{2,4,6,94,96,98}`.
5. **Wave 146 numerical status.**  Unscaled and naively row-scaled HiGHS
   infeasibility records are rejected.  The promoted evidence is the stored
   rational vector and exact replay of every integer equation.

## Wave 146 certificate boundary

The independently reconstructed one-root model has

```text
six-class/output-weight cells:   343
rooted orbit types:              944
variables:                    13,973
equalities:                    8,981
integer matrix nonzeros:     110,269
positive rational entries:     2,998
maximum denominator:                4
h11:                           16,632.
```

All 3,968 class/pattern pairs pass the direct rooted seven-vertex
admissibility comparison.  The sparse rational support replays every row
exactly.  This proves only feasibility of the aggregate one-root relaxation.
It does not make the profiles on two overlapping rooted seven-sets agree on
their eight-vertex union.

## Wave 147 continuation boundary

The verified finite two-root model has flag bases of sizes 66 and 87,
complete locally admissible class streams `21/62/208/916`, 2,414 class
coefficient matrices, 272,054 nonzero upper entries, and 208 ordinary
seven-to-eight deletion rows.  Both root families contain explicit moment
entries with `n3` coefficient four and prism coefficient zero.  The
`3 x 3` rook graph supplies exact positive-semidefinite controls.
Independent reconstruction covers the flag/class streams, full deletion
layer, complete `N3` and prism matrices, 24 representative class matrices,
and full artifact integrity/counts; it does not recompute every stored
coefficient.

The stronger marked degree/common-neighbor order-eight rows have not been
built.  No endpoint SDP was run and no rational dual certificate exists.

## Separation and resource audit

- Discovery packages did not verify themselves.
- Wave 144 uses a different clean-room verifier from its discovery author.
- Waves 143, 145, 146, and 147 have independent implementations and hostile
  or semantic controls.
- Numerical solver statuses are not promoted.
- No putative graph automorphism is assumed.
- Host free memory stayed well above the requested 15% reserve.

## Conclusion

The alternative-space work is exact and materially narrows the next
mathematical task: standalone code and six-set marginals are insufficient,
and even complete one-root six-to-seven compatibility survives.  The
two-root/order-eight PSD model is the first current lane that retains the
missing overlap information while carrying `n3` directly.

It has not yet produced a bound.  Conway-99, the prism-free endpoint, a
strict upper bound below 4,158, and external novelty all remain `UNKNOWN`.
