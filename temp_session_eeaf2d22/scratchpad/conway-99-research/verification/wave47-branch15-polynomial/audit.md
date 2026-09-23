# Wave 47 branch-15 polynomial-calculus audit

## Verdict

`VERIFIED_SCOPED`, with one noncomputational README correction required.

The sealed seven-window degree-two calculation and its degree-four barrier
census were reproduced clean-room. There are no mismatches among the sealed
computational claims or hashes. The status is restricted to this local
algebraic calculation.

## Independence and freeze

The verifier first read only the supplied verifier protocol and four frozen
input paths. It then independently implemented and ran:

1. strict OPB parsing with explicit weights, operators, and literal polarity;
2. generalized-unit propagation over the Wave 37 and Wave 42 OPBs;
3. the 84-label and 3,486-primary-edge bijections;
4. seven mate-coordinate windows and their complete incidence blocks;
5. exhaustive Hamming-slice evaluation and kernel computation over `F_2`;
6. clause falsifying-assignment polynomials;
7. highest-pivot squarefree degree-two polynomial-calculus saturation;
8. exact intersection with the affine-linear subspace; and
9. a mutually reduced exact-block-only control.

The resulting implementation and output were sealed before the discovery
result or implementation was opened. The frozen result SHA-256 is
`5cf6b0312274794681456ee7ccb1eb404b2930e4f63d13cfade56ba0c2dcf5f7`.

## Evidence

The closure is exactly the frozen 830 assignments: 174 primary variables,
seven positive primary values, and 167 negative primary values. The 2,352
OPB rows encoding all 1,176 complete incidence equalities were found exactly
once.

| pair | free vars | eligible width <=2 clauses | initial affine rank | Macaulay rank | final affine rank | new rank |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 232 | 10 | 43 | 11,165 | 45 | 2 |
| 1 | 191 | 60 | 34 | 7,582 | 35 | 1 |
| 2 | 251 | 18 | 45 | 12,641 | 47 | 2 |
| 3 | 252 | 0 | 45 | 12,704 | 47 | 2 |
| 4 | 252 | 0 | 45 | 12,704 | 47 | 2 |
| 5 | 252 | 0 | 45 | 12,704 | 47 | 2 |
| 6 | 252 | 0 | 45 | 12,704 | 47 | 2 |

All 13 quotient representatives agree term-for-term with the sealed result,
including constants, primary-variable numbers, decoded residual endpoints
and labels, common-coordinate support, and individual row hashes. No affine
row is constant one and no final row isolates a new single variable.

For every window the full theory and the exact-block-only control reduce each
other to zero. Thus the eligible width-at-most-two imported clauses do not
change the final affine consequence space in this calculation.

The independently simplified Wave 43 catalogue has 6,460 closure-satisfied
rows and 34,340 active rows. The active rows partition uniquely by window as
`[4141,0,5959,6060,6060,6060,6060]`. Each is an all-negative clause on four
distinct primary variables, hence its falsifying polynomial is a squarefree
degree-four monomial and cannot be inserted directly into an unassumed
degree-two matrix.

The comparison independently regenerated and matched, in every window:

- the per-block slice-relation catalogue hash;
- the full axiom catalogue hash;
- the deterministic Macaulay echelon hash;
- the final affine RREF hash; and
- the new-relation catalogue hash.

The sealed discovery result SHA-256 is
`d4689f7c9e469bf722d7553da700b47d98642c4404c566a0abc5a78149df4a3f`.
`comparison.json` records zero mismatches.

## Hostile checks

Seven focused tests cover parser signs/operators, a flipped clause literal,
an altered affine constant, a changed exact-count target, an omitted Hamming
slice point, a missing linear multiplication, ambiguous cross-window support,
the exact Wave 43 partition, and all comparison commitments. All pass.

The explicit cross-window test exhibits a primary edge lying in two
overlapping vertex windows; it is rejected as a uniquely local clause rather
than silently projected. The seven mate pairs partition the 14 coordinates,
but the 24-vertex windows themselves overlap: every residual label belongs to
two windows.

## Documentation discrepancy

The discovery README describes each window as having 24 exact-one and 24
exact-two blocks. Direct endpoint-label reconstruction gives full target one
for all 48 local blocks. The implementation does not hard-code the inaccurate
description: it groups the exact OPB row pairs, simplifies their actual
targets, and its axiom hashes agree with the clean-room reconstruction. This
is therefore a required prose correction, not a refutation of the sealed
calculation.

Likewise, “zero assignment” in the verifier checklist is interpreted against
the sealed claim as zero *newly forced single-variable assignments*. The
literal all-zero vector does not satisfy the exact-one affine relations.

## Scope wall

Nothing here establishes branch satisfiability or unsatisfiability. The local
window union omits wider clauses, constraints whose complete support leaves a
window, all cross-window multiplication, and direct use of the degree-four
Wave 43 rows. No endpoint case is closed, no general upper bound is improved,
no graph is constructed, and Conway-99 remains `UNKNOWN`.
