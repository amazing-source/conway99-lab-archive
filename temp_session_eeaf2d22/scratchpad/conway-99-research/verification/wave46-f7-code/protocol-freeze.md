# Wave 46 clean-room verification protocol

Freeze time: 2026-07-27, before opening any file under
`attempts/wave46-f7-code/` or its discovery agent report.

Role: verifier. This lane writes only under `verification/wave46-f7-code/`
and `agents/2026-07-27-wave46-f7-code-verifier.md`. Discovery code will not be
imported, and discovery matrices, hashes, solver statuses, or prose will not
be trusted as evidence.

## Supplied scope, not yet accepted

The orchestrator asks for verification of finite-field consequences attached
to an actual `231 x 231` projector-derived code over `F_7`, including:

- self-orthogonality;
- orthogonality to the all-ones vector;
- projective generator columns and the corresponding dual-distance bound;
- a Schur-cube rank bound;
- scalar-composition identities and low-degree complete moments;
- explicit positive-control codes for every rank `r=28,...,44`;
- quarantine of a reported prompt error.

The exact discovery formulation and artifacts remain unopened until the
independent derivation and checker are frozen.

## Independent finite-field conventions

All arithmetic is performed on ordinary integers reduced to the canonical
representatives `0,...,6`. Rank is computed by explicit Gaussian elimination
over `F_7`, with modular inverses checked by multiplication.

For a generator matrix `G` with `r` rows and length `n=231`, its code is

```text
C = {u G : u in F_7^r}.
```

The clean verifier will never infer a rank from a declared shape. It will
recompute row rank and reject any noncanonical entry, ragged row, duplicate
field encoding, or inconsistent dimension.

## Consequences to reconstruct

### Self-orthogonality

The exact condition is

```text
G G^T = 0 over F_7,
```

equivalently every two generator rows, including a row with itself, have dot
product zero. The checker will compute every entry independently.

### All-ones orthogonality

The exact condition is

```text
G 1^T = 0 over F_7,
```

so every codeword has coordinate sum zero. This is distinct from
self-orthogonality unless the all-ones word is separately proved to lie in
the code.

### Projective columns and dual distance

Every column of `G` will be normalized to its first nonzero entry equal to
one. The verifier will reject zero columns and repeated normalized columns.
For a full-rank generator, these two checks establish that no one or two
columns are linearly dependent, hence

```text
d(C^perp) >= 3.
```

No stronger dual-distance claim is accepted without an independently checked
search or certificate for larger dependent column sets.

### Schur products

For vectors `x,y,z` of length 231, `x*y*z` denotes coordinatewise
multiplication. The verifier will construct the span of all distinct
generator-row triple products

```text
g_i * g_j * g_k,  i <= j <= k,
```

and recompute its exact `F_7` rank. Any claimed upper bound will be derived
from the actual projector/code identities and compared to this explicit
rank; a numerical rank or a subset of triples is insufficient.

### Scalar compositions and complete moments

For every checked codeword `c`, its scalar composition is

```text
(N_0(c),...,N_6(c)),
N_a(c) = number of coordinates equal to a.
```

The seven counts must be nonnegative integers summing to 231. Multiplication
of a codeword by a nonzero field scalar must permute the six nonzero
composition coordinates exactly.

Complete moments are sums of monomials in these composition counts over the
specified codeword ensemble. The clean implementation will derive the
claimed low-degree formulas from explicit coordinate and column incidences,
state whether the zero word and scalar multiples are included, and evaluate
all arithmetic exactly. It will not enumerate `7^r` codewords for
`r>=28`; formulas must be justified by finite-field counting or a complete
smaller control.

## Positive-control family `r=28,...,44`

Only after the independent checker is frozen may the sealed explicit
generators be read. For every one of the 17 ranks, the verifier will require:

1. exact shape `r x 231` and canonical `F_7` entries;
2. exact row rank `r`;
3. `G G^T=0` and `G 1^T=0`;
4. 231 nonzero, pairwise nonproportional columns;
5. the independently derived Schur-cube rank bound;
6. every declared scalar composition and low-degree complete moment;
7. recomputed canonical hashes for generator rows, normalized columns, and
   derived records.

Passing controls prove consistency and nonvacuity of the necessary code
conditions only. They do not construct the graph or establish that the
projector-derived code comes from a graph.

## Projector reconstruction

The clean implementation will reconstruct the `231 x 231` finite-field
matrix from the mathematical definition or frozen raw combinatorial input,
not from a discovery-computed matrix. It will verify its shape, symmetry or
other declared structural identities, exact rank, and the map from the
projector object to a full-rank generator.

Every downstream code claim must be replayed from that independently
reconstructed generator. A mismatch is recorded as a discovery failure; the
verifier will not silently replace the supplied artifact.

## Prompt-error quarantine

After the independent freeze, the verifier will identify the exact alleged
prompt error and test it directly. Any false premise, wrong dimension,
incorrect implication, or inconsistent scalar convention must remain
explicitly quarantined:

- it is never used as an assumption;
- derived artifacts identify whether they predate or depend on it;
- no corrected statement is silently attributed to the original prompt;
- valid claims are rederived from uncontaminated inputs.

## Hostile tests

The verifier will reject at least:

- one changed matrix entry;
- one dependent or zero generator row;
- one nonzero self-dot product or pairwise dot product;
- one row whose coordinate sum is nonzero;
- one zero column and one proportional column;
- one omitted or altered Schur triple;
- one altered composition coordinate or moment;
- one rank label exchanged between positive controls;
- one generator hash or normalized-column hash mutation;
- any attempt to promote a bounded rank calculation into a graph theorem.

## Status wall

The verified code consequences are necessary conditions. Existence of
positive-control codes in ranks 28 through 44 shows that this finite-field
package alone is not contradictory.

Absent a complete exact bridge back to the graph or a complete infeasibility
certificate, the endpoint, a stricter upper bound, Conway-99, novelty, and
priority remain `UNKNOWN`. A null or incomplete result is retained as such.

Memory must remain at least 15% free. This lane starts no persistent
background process.
