# Wave142 derivation: interlace and isotropic-matroid shift

Status: `DERIVED_INCONCLUSIVE`.

All statements are conditional on the frozen hypothetical adjacency matrix.
No graph, formal global interlace enumerator, or nonexistence certificate is
constructed.

## 1. Principal nullity as an isotropic transversal rank

For `S subset V`, choose the `chi` column of `IAS(G)=[I|A|I+A]` at vertices
in `S` and the `phi` column elsewhere. Eliminating the `I` columns outside
`S` leaves `A[S]`, so

```text
rank(phi_(V\S) union chi_S) = 99-|S|+rank(A[S]),
transversal nullity          = nullity(A[S]).
```

Thus the vertex-nullity interlace polynomial is exactly a restricted
isotropic-transversal rank enumerator. Allowing `psi` at `T subset S`
replaces `A[S]` by `A[S]+diag(1_T)`.

The three constant transversals have nullities

```text
all phi: 0,
all chi: 45,
all psi: 54,
```

because `rank(A)=54` and `rank(I+A)=45`.

## 2. Exact size-refined rows through six vertices

Write

```text
I_(t,nu)=#{S subset V: |S|=t, nullity_F2(A[S])=nu}.
```

Every `A[S]` is alternating, so its rank is even and
`nu == t (mod 2)`. Replaying the frozen Wave21 class alignment gives:

```text
t=4:
  I_(4,0)=226611
  I_(4,2)=2068605
  I_(4,4)=1469160

t=5:
  I_(5,1)=16020081
  I_(5,3)=40833639
  I_(5,5)=14669424

t=6:
  I_(6,0)= 45845415 + (4/3)n3
  I_(6,2)=470213205 - 3n3
  I_(6,4)=503184528 + (4/3)n3
  I_(6,6)=101286108 + (1/3)n3.
```

The slopes sum to zero, as required by
`sum_nu I_(6,nu)=binom(99,6)`. Nonnegativity of the only decreasing row gives

```text
n3 <= 156737735,
```

which is much weaker than `n3<=4158`.

The kernel-size moment is

```text
sum_|S|=6 2^nullity(A[S]) = 16459961595 + 32n3.       (1)
```

It is exact but has no useful one-sided inequality.

## 3. The precise lift missing from Wave141

For fixed `S`,

```text
2^nullity(A[S])
 = #{x supported in S : supp(Ax) is disjoint from S}.
```

Double counting `(S,x)` yields

```text
sum_|S|=t 2^nullity(A[S])
 = sum_(x: supp(x) disjoint supp(Ax))
     binom(99-wt(x)-wt(Ax), t-wt(x)).                 (2)
```

Wave141 records only `(wt(x),wt(Ax))`. Equation (2) also needs

```text
h=|supp(x) intersect supp(Ax)|
```

and specifically its `h=0` slice. The exact control `K3 disjoint_union K1`
has six vectors in the same Wave141 cell `B[2,2]`, split as three with
`h=0` and three with `h=2`. Consequently the interlace moment is not a new
linear row in the existing `B[i,j]` coordinates; it requires an
intersection-refined lift

```text
C[i,j,h],  B[i,j]=sum_h C[i,j,h].
```

No exact elimination of that lift back to a stronger `B`-only inequality
was found.

## 4. A forced top band

Let `C=V\S` with `|C|<14`. If `x` is supported in `S` and lies in the
kernel of `A[S]`, then `Ax` is supported in `C`. But `Ax in im(A)`, whose
minimum nonzero weight is at least fourteen, so `Ax=0`.

The coordinate restriction `ker(A)->F2^C` is onto: otherwise a nonzero
annihilator would be an `im(A)` word supported in `C`. Hence

```text
nullity(A[S])=45-|C|,
rank(A[S])=54
```

for every `86<=|S|<=99`. This fixes fourteen high-degree size-refined
interlace rows. It does not involve `n3`.

## 5. Diagonal-toggle/isotropic rows

The checker also aggregates all `A[S]+diag(1_T)` for the 62 six-vertex
types and all 64 choices of `T`. The strongest decreasing coefficient is
the cell

```text
|T|=3, nullity=5:
5072760 - (2/3)n3 >= 0,
```

giving only

```text
n3 <= 7609140.
```

All ordinary and diagonal-toggle cells are strictly positive at `n3=4158`.
There is no new congruence beyond the already known `3|n3`.

## Conclusion

The interlace/isotropic translation exposes a real missing statistic:
support overlap between `x` and `Ax`. It also yields exact local rows and a
large forced complement band. However, none supplies a strict upper bound,
endpoint exclusion, or contradiction. A meaningful continuation would need
an exact feasible/infeasible intersection-refined enumerator, not another
scalar specialization of Wave141.

Conway-99 and novelty remain `UNKNOWN`.
