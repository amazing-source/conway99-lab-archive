# Wave 47 clean-room verification protocol

Freeze time: 2026-07-27, after reading only the sealed
`verifier-protocol.md` specification and before opening discovery code,
results, or claimed relation streams.

Role: verifier. This lane writes only under
`verification/wave47-branch15-polynomial/` and
`agents/2026-07-27-wave47-polynomial-calculus-verifier.md`. Discovery
implementation will not be imported. No file will be staged, committed, or
published.

## Frozen scope

The scoped object is seven mate-coordinate window subtheories reconstructed
from four frozen OPB/propagation inputs. Each window is claimed to have:

- 24 vertices;
- 276 primary edge variables;
- exactly 48 complete coordinate-incidence exact-count blocks;
- a squarefree polynomial-calculus calculation over `F_2` truncated at
  degree two.

The supplied target claims are 13 new affine XOR relations, per-window rank
increments `[2,1,2,2,2,2,2]`, equality with an exact-block-only control,
zero contradiction, the zero assignment, and a degree-four barrier
partitioning all 34,340 active Wave 43 cuts.

These are untrusted until the independent implementation and output are
frozen.

## Input and parsing rules

1. Verify every path and SHA-256 in the four-line discovery
   `input-freeze.sha256` before mathematical work.
2. Implement OPB parsing independently, including signed coefficients,
   equality/inequality operators, integer right-hand sides, comments, and
   literal polarities.
3. Reconstruct the Wave 42 propagated closure from frozen assignments and
   clauses rather than trusting a simplified discovery stream.
4. Use a canonical variable key derived from the parsed primary edge
   endpoints. Reject unknown variables, loops, reversed-map inconsistencies,
   duplicate labels, and any mismatch between 24 vertices and
   `binom(24,2)=276` variables.
5. Reconstruct the seven windows from the 84 residual mate-coordinate labels.
   The partition must be disjoint and complete. No relation crossing two
   windows may enter a local calculation silently.

## Exact-count block semantics

After applying frozen propagation, every complete coordinate-incidence block
must simplify to

```text
sum_{x in S} x = t
```

on Boolean variables, with an explicitly checked integer target `t`.
Contradictory targets, repeated variables, incomplete blocks, or a fixed
literal counted with the wrong sign are rejected.

For a block with `m` active variables, enumerate the complete Hamming slice

```text
{a in {0,1}^m : sum a_i=t}.
```

Build every squarefree monomial of degree at most two and evaluate it on the
slice. The exact degree-two vanishing space is the kernel over `F_2` of that
evaluation map. This kernel, not a guessed parity reduction, is the block's
polynomial axiom space.

## Clause semantics

Only active residual clauses of width at most two may enter the degree-two
window theory. Translate a clause by the polynomial of its unique falsifying
assignment:

- positive literal `x` contributes `1+x`;
- negative literal `not x` contributes `x`;
- multiply all factors and set the resulting squarefree polynomial to zero.

Unit clauses yield linear polynomials and binary clauses yield quadratic
polynomials. Tautologies are removed explicitly. Clauses wider than two and
clauses using variables outside one window are catalogued as omitted scope,
not partially projected.

## Squarefree degree-two polynomial calculus

Represent a polynomial by its coefficient vector on the canonical basis

```text
1; x_i; x_i*x_j for i<j.
```

Arithmetic is XOR. Multiplication uses the Boolean quotient `x_i^2=x_i` and
rejects products whose squarefree degree exceeds two.

Start with all exact-slice vanishing rows and eligible clause rows. Compute
exact `F_2` row space by deterministic pivot reduction. Then iterate:

1. extract every derived row of degree at most one;
2. multiply it by every free variable in the window;
3. squarefree-reduce the product;
4. add every new degree-at-most-two row;
5. row-reduce and repeat to a fixed point.

The final affine-linear subspace is obtained by intersecting the saturated
row space with the span of `1,x_i`. Its deterministic RREF fixes constants
and variable ordering. A row equal to constant one is an exact
contradiction. A claimed zero assignment requires every final affine row to
have constant zero.

## Independent commitments before comparison

For each window, freeze:

- variable and label maps;
- exact-block and eligible-clause catalogs;
- every Hamming-slice vanishing-space basis;
- initial and saturated echelon streams;
- final affine-linear RREF;
- ranks and canonical SHA-256 values.

Only after these artifacts and hostile tests are frozen may discovery
`degree2_windows.py`, `degree2-window-result.json`, or claimed relation files
be opened.

## Exact-block-only equality control

Repeat the entire saturation with eligible clauses removed. Compare final
affine-linear row spaces by mutual exact reduction, not merely by rank or
hash. Equality in all seven windows means the width-at-most-two clauses add
no final linear consequence in this scoped calculation; it does not make
omitted clauses redundant globally.

## Degree-four barrier

Independently parse every active Wave 43 cut. Require:

- exactly 34,340 rows;
- a disjoint and complete assignment to the seven windows;
- exactly four distinct active variables per row;
- all four literals negative;
- falsifying polynomial equal to the squarefree degree-four monomial formed
  by those variables.

Such rows lie outside a degree-two calculation. The verifier will not infer
that they are useless at degree four or after cross-window multiplication.

## Hostile tests

The verifier will reject:

- one swapped endpoint or mate-coordinate label;
- one flipped literal polarity;
- one altered affine constant;
- one exact-count target changed by one;
- one omitted Hamming-slice assignment;
- one row-space pivot or coefficient mutation;
- one missing multiplication of a derived linear row;
- one cross-window constraint silently localized;
- one Wave 43 row assigned to two windows or none;
- one degree-four row with the wrong sign, width, or repeated variable;
- any hash mismatch.

## Status wall

Agreement may receive `VERIFIED_SCOPED` only for the seven frozen local
degree-two calculations and the exact degree-four partition. A discrepancy
is `REFUTED`; missing completeness remains `UNKNOWN`.

No local relation, zero contradiction, degree-four barrier, or finite
closure result proves branch UNSAT, excludes `n3=4158`, improves a global
upper bound, constructs a graph, resolves Conway-99, or establishes novelty.

Available physical memory must stay at least 20% free. This lane starts no
persistent background process.
