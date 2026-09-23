# Exact spectrum forced by the `C4` Cartesian `K3` motif

Claim label: `DERIVED`; independent verification required.

## 1. Global resolvent

Let `A` be the adjacency matrix of a hypothetical
`srg(99,14,1,2)`. Its matrix equation and spectrum are

```text
A^2 = 12I-A+2J,
spec(A) = {14^1, 3^54, (-4)^44}.
```

Put `q=(x-3)(x+4)=x^2+x-12`. Direct multiplication in the basis
`I,A,J` gives

```text
(xI-A)^(-1)
  = ((x+1)I+A+2J/(x-14))/q.                         (1)
```

Indeed, the `I`, `A`, and `J` coefficients reduce respectively to
`x(x+1)-12=q`, `x-(x+1)+1=0`, and
`2x/(x-14)-2-28/(x-14)=0`.

## 2. Jacobi identity

Order the vertices so the 12 motif vertices come first:

```text
A = [H   P^T]
    [P    D ].
```

Jacobi's complementary-minor identity says

```text
det(xI-D) = det(xI-A) det(((xI-A)^(-1))_H).          (2)
```

The motif is `H=C4` Cartesian `K3`. The Cartesian-product eigenvalue
rule gives

```text
spec(H) = {4^1, 2^2, 1^2, 0^1, (-1)^4, (-3)^2}.
```

It is 4-regular, so `J` acts by 12 on its all-ones eigenspace and by
zero on the other eigenspaces. Equations (1) and (2) therefore give

```text
det(xI-D)
 = (x-3)^42 (x+4)^32
   (x^2-9x-46)
   (x+3)^2 (x+2)^2 (x+1) x^4 (x-2)^2.              (3)
```

The quadratic comes from

```text
(x-14)(x+5+24/(x-14))
  = (x-14)(x+5)+24
  = x^2-9x-46.
```

The exact checker independently evaluates the determinant of `xI-H` at
13 integer points and the degree-13 Jacobi residual at 14 integer points.
All determinants are computed with rational Gaussian elimination.

## 3. Refutation of the proposed `-38` factor

Wave 105 forces motif-degree counts

```text
3 of degree 0, 48 of degree 1, 36 of degree 2.
```

Their outside degrees are therefore `14,13,12`, and

```text
tr(D^2) = sum_v deg_D(v)
        = 3*14+48*13+36*12
        = 1098.                                     (4)
```

If the quadratic were `x^2-9x-38`, its two roots would contribute
`9^2-2(-38)=157` to the second spectral moment. Together with the other
factors, this gives `tr(D^2)=1082`, contradicting (4). The corrected
quadratic contributes `9^2-2(-46)=173`, giving exactly 1098.

## 4. Perron structure and connectedness

Let `s=P one` be the vector of motif degrees, with entries `0,1,2`.
The Wave 105 linear block equation implies

```text
D one = 14 one-s,
D s   = 24 one-5s.
```

Thus `span{one,s}` is invariant, and the matrix of `D` on the ordered
basis `(one,s)` has columns

```text
[14  24]
[-1  -5].
```

Its characteristic polynomial is `x^2-9x-46`. Let

```text
rho = (9+sqrt(265))/2.
```

The vector `(rho+5)one-s` is a `rho`-eigenvector. Since
`16^2<265<17^2`, `rho` lies between `12.5` and `13`; every coordinate
of that vector is strictly positive. Equation (3) shows that `rho` is
the simple largest eigenvalue. If `D` had two or more connected
components, the positive restriction to each component would make `rho`
an eigenvalue of every component, contradicting simplicity. Hence every
full extension has connected outside graph.

## 5. Further exact consequences

The first four spectral moments are

```text
tr(D)   = 0,
tr(D^2) = 1098,
tr(D^3) = 1002,
tr(D^4) = 37518.
```

Therefore `D` has 549 edges and `1002/6=167` triangles. Also

```text
sum_v binom(deg_D(v),2)
  = 3*binom(14,2)+48*binom(13,2)+36*binom(12,2)
  = 6393.
```

Using

```text
tr(D^4)=2|E|+4 sum_v binom(deg_D(v),2)+8 C4(D)
```

gives exactly `C4(D)=1356`.

Finally, (3) forces

```text
nullity_Q(D)   = 4,
rank_Q(D-3I)   = 45,
rank_Q(D+4I)   = 55.
```

The two irrational eigenvalues are approximately `12.6394` and
`-3.6394`, both compatible with principal-submatrix interlacing.

## 6. Boundary

The corrected spectrum is internally consistent. It supplies exact
candidate-rejection invariants and suggests a two-main-eigenvalue or
star-complement formulation, but it does not exclude the motif or solve
the full nonlinear extension equations. The extension and Conway-99
statuses remain `UNKNOWN`.
