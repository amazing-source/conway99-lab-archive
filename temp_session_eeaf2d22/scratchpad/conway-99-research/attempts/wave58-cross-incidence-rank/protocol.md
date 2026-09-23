# Wave 58 cross-incidence rank protocol

Frozen: 2026-07-27T20:55:37Z

Repository baseline: `4bb1989e9e286b2ec753a855db58ad584e31f63a`

Status policy: discovery work remains `DERIVED`; the fixed-triangle endpoint
and Conway-99 remain `UNKNOWN` unless a complete independently checkable
contradiction is obtained. This protocol was written before reading the Wave
57 derivation, checker, or exact result.

## Frozen conditional scope

Assume the prism-free `n3=4158` endpoint and fix a graph triangle. Use its
local triangle-relation partition with `|X|=36` and `|Y|=60`, and let `B` be
the `36 x 60` cross-incidence matrix specified by the endpoint relations.
Let `A_X,A_Y` be the induced relation adjacency matrices and let the three
12-vertex sectors of `X` be fixed only as forced local incidence classes.
No sector permutation or graph automorphism is assumed.

## Claims to derive and check

1. Derive entrywise, from the exact common-neighbor counts,

   `B^T B = 12 I - A_Y + 2 J - A_Y^2`

   and

   `B B^T = 12 I - A_X + 2 J - blockdiag(J12,J12,J12) - A_X^2`.

2. Decompose `ker(B^T)` without spectral handwaving:
   - two sector-constant vectors with total sector sum zero;
   - every `A_X` eigenvalue-3 vector in the within-sector-zero subspace;
   - no other vectors.
   Record why eigenvalue `-4` cannot occur for cubic `A_X`.
3. If `c` is the number of connected components of `A_X`, test and prove the
   exact identity `rank(B)=35-c`.
4. For `a=mult_Y(3)` and `b=mult_Y(-4)`, combine the two Gram kernels to
   derive `a+b=25+c`.
5. Read the sealed Wave 57 candidate rows only after these formulas are fixed,
   retain exactly the rows satisfying the new identity, and emit the complete
   survivor table.

## Structural component audit

Treat `A_X` as the union of its three forced perfect-matchings/edge colors,
without identifying the colors by symmetry. Derive every justified component
restriction from:

- cubicity and connected-component kernel multiplicity;
- triangle-free and prism-free constraints;
- parity, size divisibility, and sector-balance equations;
- exact Wave 40 component and lift ledgers.

Restricted enumerations must list all restrictions, especially sector
balance, simplicity, connectedness, edge-color preservation, and any size
cutoff. A null restricted search is not nonexistence evidence.

## Exactness and hostile checks

- Use integer/rational polynomial arithmetic; do not infer a kernel from
  floating-point eigenvalues.
- Check dimensions, traces, row/column sums, and both Gram nullities.
- Reject sign errors, omitted sector blocks, a noncubic `A_X`, an illegal
  `-4` eigenvalue, altered Wave 57 rows, and inflated endpoint status.
- Keep at least 15 percent physical RAM free.
- Preserve failed routes and distinguish universal deductions from
  restrictions that require a component/lift ledger.

## Addendum after upstream routing message

Received: 2026-07-27T20:57:00Z, after the original freeze and before reading
the Wave 36 or Wave 57 contents.

`STRUCTURE.md` and the independently verified Wave 36 block-compatibility
package already establish the component partitions
`[12]`, `[4,8]`, `[6,6]`, `[4,4,4]`, hence `c in {1,2,3}`, as well as
`rank(B)=35-c`, `mult_Y(3)=18`, and `mult_Y(-4)=7+c`. Wave 58 must not claim
these as new. It will freeze the Wave 36 package hashes, independently replay
the relevant claims, intersect them with Wave 57's rows, and focus novelty on
whether Wave 57 order-four/moment conditions or the Wave 40 component/lift
ledgers further exclude `c=2` or `c=3`.
