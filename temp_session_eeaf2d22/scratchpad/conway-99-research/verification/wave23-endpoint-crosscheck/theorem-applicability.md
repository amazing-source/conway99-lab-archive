# Theorem applicability for the Wave 23 endpoint cross-check

## Even-unimodular signature obstruction

The imported theorem and primary bibliography were already audited in:

```text
verification/wave21-lattice-extension/theorem-sources.md
sha256 7f70a36ad124a94d983771274cb7b925a4f2560d835b0f607563045110107f8f
```

The theorem states that the signature of an even unimodular integral
symmetric form is divisible by eight.  It applies twice here:

1. `det(Q)=1` would make the even positive-definite rank-44 Gram matrix `Q`
   unimodular.
2. `h=1` would make the even positive-definite rank-44 scaled-dual Gram
   matrix `S=21G^{-1}` unimodular.

Both would have signature 44, which is 4 modulo eight.  No root-system,
minimum-norm, or lattice-classification premise is used.

## Odd alternating matrices

Over a field, every alternating bilinear form has even rank: repeatedly
split off a hyperbolic pair until the form vanishes.  Consequently an
alternating matrix of odd order is singular.  This applies to each
43-by-43 principal submatrix of the even Gram matrix `G` after reduction
modulo two.

## Odd determinant of an even Gram matrix

If an even integral symmetric matrix has rank `2m` and odd determinant, its
reduction modulo two is a nonsingular alternating form.  After a lifted
symplectic change of basis, write the matrix modulo four as `J+2R`, where
`J` is a sum of `m` hyperbolic blocks and `R` is symmetric.  Then

```text
det(J+2R)
 = det(J)(1+2 tr(JR))
 = (-1)^m (mod 4),
```

because `tr(JR)` is even.  At rank 44, `m=22`, so the residue is one.

## The needed Maclaurin case

No external form of Maclaurin's inequalities is needed.  For positive
numbers `lambda_1,...,lambda_n`, apply ordinary AM--GM to the
`binomial(n,2)` pair products `lambda_i lambda_j`.  Their arithmetic mean
is `e2/binomial(n,2)`, while their geometric mean is

```text
(product_i lambda_i)^((n-1)/binomial(n,2))
 = det(B)^(2/n).
```

At `n=44`, this is exactly

```text
det(B)^(1/22) <= e2/binomial(44,2).
```
