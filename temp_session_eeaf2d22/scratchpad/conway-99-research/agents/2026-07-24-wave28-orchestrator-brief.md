# Wave 28 orchestrator brief: beyond full orthogonal ADE

Frozen on 2026-07-24 from public branch head
`d76d030f6d74e2e1b7ca2b2f0f97536241b3a10b`.

Claim label: `UNKNOWN`

## Target

Attack the `n3=708` endpoint without assuming that the rank-44 scaled-dual
form is a root lattice, an orthogonal sum, strongly modular, or endowed with
any nontrivial automorphism.

The verified inherited endpoint package is:

```text
X in Z^(231 x 44), with full column rank
G=X^T X
S=21G^(-1)
M=XSX^T
W=M o M
Q=X^T W X
B=SQ=I+2C

S,Q,G positive definite
S,Q,G integral and even
B integral and G-self-adjoint
tr(B)=60
tr(C)=8
tr(C^2)>=10
det(B)<=6525
```

The determinant bookkeeping is:

```text
h=det(S) in {9,21,49,81,189,441,729,1029}
det(B)=h det(Q)
h=1 (mod 4)
det(Q)=1 (mod 4)
det(Q)>=5
21S^(-1)=G is even integral
```

The frame/Schur package additionally gives:

```text
M 1=0
diag(M)=4
offdiag(M) in {0,1,-1,-2}
K=S^(1/2) Q S^(1/2) positive definite
tr(K)=60
```

Wave 27 proves only the following conditional classification statement:

```text
if S is a full orthogonal sum of irreducible ADE root lattices,
then no endpoint package exists.
```

It leaves general glued, non-root, and otherwise nonorthogonal even lattices
untouched.

## Parallel lanes

1. **Glue/discriminant lane.** Derive local discriminant-form, root-sublattice,
   and glue constraints from the exact level and determinant data. A root
   subsystem is not an orthogonal summand. No classification theorem may be
   invoked without checking all hypotheses and conventions.
2. **Theta/modular lane.** Use scalar or vector-valued theta series only after
   proving the relevant modular transformation law. The containment
   `21S^(-1)` integral does not by itself make `S` strongly 21-modular.
3. **Construction lane.** Seek complete exact hostile controls or refutations
   outside the full orthogonal ADE class. Every construction must emit all
   matrices and hashes; every negative finite search must disclose its search
   space and a complete certificate.

## Status walls

- An abstract arithmetic package is not a primitive `Z^231` embedding.
- A primitive embedding is not a 231-row projector-frame realization.
- A projector frame is not a Schur-square certificate unless `Q=X^T(M o M)X`
  is checked.
- Failure to find an object is not nonexistence.
- Solver exit status, floating-point residuals, and model agreement are not
  certificates.
- Discovery agents may label results only `DERIVED`, `CANDIDATE`, `REFUTED`,
  or `UNKNOWN`; a separate verifier controls any promotion.
- `n3=708`, Conway-99 existence, and novelty remain `UNKNOWN`.
