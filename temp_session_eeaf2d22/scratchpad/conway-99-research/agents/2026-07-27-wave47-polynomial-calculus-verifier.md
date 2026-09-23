# Wave 47 polynomial-calculus verifier

Role: verifier
Status: `VERIFIED_SCOPED`
Git baseline: `e4394aa9172fa97a6dafa9158148c2183603a01b`

I independently reproduced the sealed seven-window squarefree degree-two
calculation without importing the discovery implementation. The
precomparison result was frozen at SHA-256
`5cf6b0312274794681456ee7ccb1eb404b2930e4f63d13cfade56ba0c2dcf5f7`
before the discovery result or code was opened.

The verifier reproduced the 830-assignment closure, all seven
24-vertex/276-variable/48-block windows, complete Hamming-slice ideals, final
rank increments `[2,1,2,2,2,2,2]`, all 13 equations, zero contradictions,
zero newly forced single-variable assignments, and exact-block-only equality
by mutual row reduction. Every sealed slice, axiom, echelon, affine-RREF, and
relation hash matches. Relation constants, primary-variable lists, decoded
edges and residual labels, common-coordinate supports, and row hashes also
match exactly.

The 34,340 active Wave 43 rows partition uniquely as
`[4141,0,5959,6060,6060,6060,6060]`; every row remains an all-negative
width-four clause with a squarefree degree-four falsifying monomial.

One documentation correction was required: the discovery README called the
48 local blocks "24 exact-one" plus "24 exact-two." Direct reconstruction
gives unsimplified target one for all 48. The implementation parses the
correct OPB blocks, so this does not alter any computational result or hash.
Also, "zero assignment" means zero new unary consequences; the all-zero
vector is not a solution of the affine exact-one equations.

Seven hostile tests pass, including altered polarity/constant/target, omitted
slice point, missing multiplication, ambiguous cross-window support, and the
full comparison commitments. Available memory remained safely above the 20%
guard, and no verifier process remains running.

Evidence:

- `verification/wave47-branch15-polynomial/independent-result.json`
- `verification/wave47-branch15-polynomial/comparison.json`
- `verification/wave47-branch15-polynomial/audit.md`
- `verification/wave47-branch15-polynomial/run-report.yaml`

Scope wall: branch 15, endpoint exclusion, any strict upper-bound improvement,
graph existence, novelty, and Conway-99 all remain `UNKNOWN`.
