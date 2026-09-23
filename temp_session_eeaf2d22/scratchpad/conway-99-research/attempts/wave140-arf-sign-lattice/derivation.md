# Arf sign, the 3-eigenlattice, and the missing two-adic plane

Claim labels: `DERIVED` for the exact lattice bridge,
`REFUTED_BY_CONTROL` for determination by the listed coarse invariants, and
`UNKNOWN` for the full integral target.

## 1. The binary quadratic space

Let

```text
H={x in F_2^99 : wt(x) is even},
q(x)=wt(x)/2 mod 2.
```

Its polar form is the dot product. Since the length is odd, this form on
`H` is nondegenerate. Reduction of the target identity modulo two gives

```text
A^2=A,
R=im(A),
E=ker(A) intersect H,
H=R orthogonal_sum E,
dim(R)=54,
dim(E)=44.
```

The total Gauss sign on `H` is negative:

```text
sum_(x in H) (-1)^q(x)=Re((1+i)^99)=-2^49.
```

Consequently the signs on `R` and `E` are opposite, but this alone does
not select either one.

## 2. Integral two-adic splitting

Work over `Z_2`. Put

```text
K={x in Z_2^99 : x dot 1=0}.
```

This is an even unimodular two-adic lattice of rank 98. On `K`, the
adjacency operator has only the rational eigenvalues `3` and `-4`. Their
difference is seven, a two-adic unit, so the usual spectral projectors are
integral over `Z_2`. Therefore

```text
K=U orthogonal_sum W,
A|U=3,
A|W=-4,
rank(U)=54,
rank(W)=44.
```

Both `U` and `W` are even unimodular over `Z_2`, and their reductions are
`R` and `E`.

An even unimodular two-adic plane has one of the two basic Gram forms

```text
H_2 = [[0,1],[1,0]],
E_2 = [[2,1],[1,2]].
```

Directly enumerating their four reductions gives

```text
det(H_2)=-1=7 mod 8,  Gauss sign +1,
det(E_2)= 3 mod 8,   Gauss sign -1.
```

Splitting off such planes proves the exact bridge

```text
epsilon_R = (2/det(U)),
```

where the right side is the quadratic character of two on the odd
two-adic determinant unit. Thus:

```text
det(U)=1 or 7 mod 8  => epsilon=+1,
det(U)=3 or 5 mod 8  => epsilon=-1.
```

The missing datum is the determinant square class of `U`, equivalently
the parity of the number of `E_2` planes assigned to the `3`-eigenlattice.

## 3. Why the Smith form does not select the plane

The verified parameter-forced Smith form is

```text
SNF(A)=diag(1^45,3^9,6,12^43,84).
```

The checker reconstructs it from:

```text
rank_2(A)=54,
rank_3(A)=45,
rank_7(A)=98,
|det(A)|=14*3^54*4^44,
every invariant factor divides 84.
```

At two this records only

```text
1^54,2,4^44.
```

That is exactly what the spectral splitting gives: multiplication by
three on `U`, by fourteen on the all-one line, and by minus four on `W`.
It contains no determinant-unit information for `U`.

The exact controls make the omission concrete. A deterministic symplectic
reduction of `H` gives 25 `E_2` planes and 24 `H_2` planes. Two allocations
are:

| control | planes in `U` | `det(U) mod 8` | `epsilon_R` | `det(W) mod 8` |
|---|---:|---:|---:|---:|
| plus | `4 E_2 + 23 H_2` | 7 | +1 | 5 |
| minus | `3 E_2 + 24 H_2` | 3 | -1 | 1 |

Both have ranks `(54,44)`, total determinant unit three, total Gauss sign
minus, the target spectrum, the target two-primary Smith factors, and the
operator identity on the orthogonal spectral decomposition.

The package additionally constructs two explicit 99-coordinate binary
projections. Both are symmetric, idempotent, zero-diagonal, kill the
all-one vector, and have rank 54, while their image quadratic spaces have
opposite Arf signs. This proves that the complete binary projection data
at the rank/idempotent level do not select the sign.

These controls are not integral zero-one adjacency matrices and are not
14-regular. They therefore do not prove that the full entrywise SRG
identities allow both signs.

## 4. What the adjacency discriminant form would add

Let `L=A Z^99` with the inherited Euclidean form. Locally at two,

```text
L_2 = U orthogonal_sum 14*<1> orthogonal_sum 4W.
```

The two-primary discriminant group is consequently

```text
D(L)_2 = Z/4 orthogonal_sum (Z/16)^44
```

for both controls. The group structure therefore does not determine the
sign.

The full finite quadratic form is stronger. Its `(Z/16)^44` block retains
the determinant unit of `W`; the two controls have units five and one
modulo eight. Since the determinant square class of `K` is fixed, knowing
the `W` form recovers `det(U)` and hence `epsilon_R`.

No verified full target two-primary discriminant form is available in the
current package. Smith factors provide only its abelian group. Milgram's
formula for the whole positive rank-99 lattice does not repair this gap
unless the required primary quadratic forms, with conventions and local
phases, are actually supplied.

## 5. Boundary

Spectrum, modular ranks, Smith factors, and the two-primary discriminant
group do not force the Arf sign. A full two-primary discriminant quadratic
form would be sufficient, but it has not been derived from the target
identities. It remains possible that the entrywise zero-one,
zero-diagonal, and constant-row-sum constraints force the missing plane
allocation by a finer argument.

Therefore the target sign remains `UNKNOWN`; no graph or Conway-99 result
follows.

