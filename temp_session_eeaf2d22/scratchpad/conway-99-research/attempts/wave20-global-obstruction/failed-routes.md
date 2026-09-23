# Wave 20 retained global routes that did not improve the endpoint

These are exact or bounded calculations, but none is used as evidence for the
`n3>=699` conditional derivation.

## Opposite-edge compression

Let `J` be the 12-regular opposite-edge graph on the 693 graph edges and let
`R` be unsigned vertex-edge incidence. Exact counting gives

```text
R R^T   = A + 14 I,
R J R^T = 10 A + 2 J_99 - 2 I.
```

The normalized compression of `J` to `im(R^T)` therefore has Ritz values

```text
12^1, (28/17)^54, (-21/5)^44.
```

Interlacing and trace-moment optimization did not beat the elementary
`0<=n3<=4158`. In particular, the compression has too few dimensions to
control the negative spectral mass of the other 594 directions. This route
is retained because the exact compression may be useful later.

## Other primitive-projector Schur triples

All four spectral projectors of the triangle-intersection graph were
reconstructed. The checker evaluates all mixed quantities

```text
tr(E_z (E_x o E_y)).
```

The only lower endpoint in the feasible interval is the zero-eigenspace
triple, which gives `n3>=693`. The closest other direct upper endpoint is
`17010`, weaker than `n3<=4158`. Nonnegative combinations cannot improve this
while every mixed term is already nonnegative throughout `[693,4158]`.

## Gegenbauer / spherical-code inequalities

Normalizing the zero-projector rows gives 231 unit vectors in dimension 44
with inner products

```text
1/4, 0, -1/4, -1/2.
```

Their complete ordered pair distribution is affine in `n3`. Exact
Gegenbauer inequalities through degree 60 reproduce the degree-three lower
bound `n3>=693`; all later lower bounds are weaker, and the best nonnegative
upper endpoint remains above 4158.

## Fourth-moment pinching

For `S=E_0 o E_0`, pinching `S` into the four eigenspaces of `Gamma` and using
rank-wise Cauchy--Schwarz yields an upper endpoint about `5354.06`. It is
strictly weaker than the combinatorial maximum 4158 and is not used.

## Integral-lattice refinements after `n3>=705`

The scaled projector

```text
M=21E_0
```

is an integral Gram matrix of rank 44 with norm-four rows, off-diagonal
entries in `{0,1,-1,-2}`, row sum zero, and `M^2=21M`. Its reduction modulo
two is a symmetric hollow idempotent of rank 44. The matrix
`A=M(M o M)M` is an integral Gram matrix with positive diagonal divisible by
four and `A mod 2=M`.

Root-system, Smith, determinant, and iterated-Hadamard observations did not
yet force a trace larger than the rigorous `4*231=924`. Thus they do not
exclude the first surviving endpoint `n3=705`. No lattice classification or
unstated minimum-norm premise is used.

## Boundary

All routes are conditional on a putative `srg(99,14,1,2)`. They make no
construction, nonexistence, or novelty claim. Target and novelty remain
`UNKNOWN`.
