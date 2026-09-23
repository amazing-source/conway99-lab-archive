# Wave 170 clean-room audit

## Verdict

The block profiles, clique theorem, and ternary ranks are
`VERIFIED_WITH_SCOPE`. No star-complement or code classification is present.

## Block profiles

For a fixed triangle block, the verifier independently obtains

```text
sum n_j=212,
sum j*n_j=216,
sum binomial(j,2)*n_j=36.
```

The terms respectively count disjoint blocks, boundary-edge/block incidences,
and the three exact 12-edge sector matchings. Solving gives

```text
(n0,n1,n2,n3)
 =(32-p_L,144+3*p_L,36-3*p_L,p_L),
0<=p_L<=12.
```

Summing over blocks and dividing by two gives the unordered-pair counts

```text
N0=3696-P,
N1=16632+3*P,
N2=4158-3*P,
N3=P.
```

The `N2` block pairs are exactly the existing six-vertex `N3` motif, so
`N2=n3`. No ordered-pair factor is missing.

## Clique geometry

A clique in `K` is a pairwise-intersecting linear family of triples. If all
blocks share a point, point degree bounds its size by seven. Otherwise,
fixing a maximum-degree point and a block avoiding it forces distinct
intersection points and bounds the family by

```text
1+3*(3-1)=7.
```

The seven blocks through an original point attain the bound. Hence

```text
omega(K)=7.
```

This is a combinatorial proof, not an assumed association-scheme or generic
Delsarte bound.

## Ternary rank

Over `F_3`, let `M=A+I=B*B^T`. The SRG relation gives

```text
M^2=M-J,
M^3=M^2,
chi_M(t)=t^45*(t-1)^54.
```

Thus `M^2` is the projection onto the 54-dimensional generalized
one-eigenspace. Since `M-M^2=J` has rank one and its image is disjoint from
the image of `M^2`,

```text
rank_F3(M)=55.
```

Therefore `rank_F3(B)>=55`. Every column of `B` has coordinate sum three,
which is zero over `F_3`, so the column space lies in a 98-dimensional
hyperplane and

```text
55<=rank_F3(B)<=98.
```

The argument handles the zero-primary Jordan component; it does not assume
that `M` itself is diagonalizable.

## Boundary

At `P=0`, the uniform profile `(32,144,36,0)` is consistent with all derived
identities. The clique and rank data have not been combined into a
star-complement classification or contradiction. The rigorous interval
remains `708<=n3<=4158`.
