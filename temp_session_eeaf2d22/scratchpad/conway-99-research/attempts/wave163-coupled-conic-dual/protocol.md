# Wave163 protocol

## Frozen mathematical target

Seek an exact identity coupling the root-3 and root-12 covariance pencils:

```text
<Z3,B3(x)> + <Z12,B12(x)> + lambda^T(Ax-b) = c,
Z3 >= 0,
Z12 >= 0.
```

Depending on the sign convention and the other nonnegative primal terms:

- `c=0` can expose a forced face;
- a strict impossible sign can certify infeasibility.

Every coefficient, constant, and PSD claim must be replayed exactly.

## Direction spaces

- `U3` contains the five retained root-3 directions plus the recurrent
  post-fifteen-cut root-3 separator.
- `U12` contains the seven retained root-12 directions plus the recurrent
  post-fifteen-cut root-12 separator.
- Root-13 directions are outside this first compressed lane and must not be
  silently folded into either block.

Duplicate or dependent columns must be removed only after an exact rank
calculation.

## Affine systems

Two systems must be reported separately:

### Universal endpoint system

Only graph-valid endpoint equalities:

- Wave44 aggregate rooted equations;
- ordinary seven-to-eight deletion equations;
- Wave148 marked-vertex and marked-pair equations;
- exact normalizations and the frozen `n3=4158` substitution.

### Diagnostic fixed slice

The stronger reconstruction slice may additionally fix `x7` and impose
pair-root covariance equality.  A result here is conditional and cannot be
promoted to an endpoint theorem.

## Exact decision gates

1. Build all 57 symmetric compressed-pencil coefficient rows on
   `(1,x7,x8)`.
2. Compute their rank modulo each affine row space over at least two suitable
   primes.
3. Recover the rational kernel and verify it by exact multiplication.
4. Interpret a kernel vector as symmetric `Y3,Y12`.
5. Certify PSD using exact `LDL^T`, exact Gram factors, or all required
   principal-minor data; numerical eigenvalues are diagnostic only.
6. Reconstruct the full coefficient identity, including its constant.
7. If count nonnegativity multipliers are used, store every slack coefficient
   and check its sign exactly.
8. Have a separate verifier rebuild the coefficient maps without importing
   discovery code.

## Negative-result scope

Full quotient rank of the 57 rows rules out only a compressed exposing
identity that uses those covariance blocks and affine rows.  It does not
rule out:

- a Farkas certificate using nonnegative count slacks;
- multipliers outside `span(U3)` or `span(U12)`;
- other covariance blocks;
- higher-order count variables.

## Resource gate

Do not run reconstruction, rank, or optimization below 18 percent free host
memory.  Abort before the user floor of 15 percent.

