# Quaternary code and symmetrized-enumerator derivation

All statements are conditional on a hypothetical
`srg(99,14,1,2)`. No rank endpoint, automorphism, motif, or `n3`
assumption is used.

## 1. Smith form and the two quaternary code types

The independently audited full-matrix data are

```text
rank_F2(A)=54,  rank_F3(A)=45,  rank_F7(A)=98,
|det A|=2^89 3^54 7,
every Smith factor divides 84.
```

There are therefore 45 even invariant factors. Their total 2-adic
valuation is 89 and each valuation is at most two, so one has valuation
one and 44 have valuation two. There are 54 factors divisible by three,
each exactly once, and one factor divisible by seven. Divisibility order
then uniquely gives

```text
SNF(A)=diag(1^45,3^9,6,12^43,84).
```

Reducing this diagonal map modulo four shows

```text
C=row_Z4(A)       has type 4^54 2^1 and order 2^109,
Cperp             has type 4^44 2^1 and order 2^89.
```

## 2. The extra order-two word

Let `j` be the all-one vector. Since every row sum is 14,

```text
j A = 14 j = 2j mod 4,
```

so `2j` belongs to `C`. It is not in `2C`: otherwise reduction modulo
two would put `j` in the binary row space `R=im_F2(A)`, but `R` is even
and `wt(j)=99` is odd.

Also `2j` is orthogonal modulo four to every adjacency row because
`2*14=28=0 mod 4`, so `2j` belongs to `Cperp`. If it were in
`2Cperp`, a lift `y=j+2z` in `Cperp` would imply

```text
0=A y=14j+2Az=2(j+Az) mod 4,
```

and hence `Az=j mod 2`, the same contradiction.

Thus `2j` represents the extra order-two factor in both code types.
Translation by it swaps symbols zero and two while swapping one and
three. For the symmetrized composition

```text
(n0,nodd,n2),
```

both enumerators consequently satisfy

```text
E(n0,nodd,n2)=E(n2,nodd,n0).
```

The binary residue/torsion chains are

```text
Res(C)=R,
Tor(C)=R+<j>,
Res(Cperp)=(R+<j>)perp,
Tor(Cperp)=Rperp.
```

Wave132 gives primal residue weights `0,8,10,...,92`. The primal torsion
code may have weight seven as the complement of a residue word of weight
92. For the dual residue, `Res(Cperp)=D intersect j^perp`. If a nonzero
even word `d` lies there, then `j+d` is another nonzero word of `D`.
Since `d(D)>=8`, both weights are at least eight, so `wt(d)<=91`;
evenness sharpens this to `wt(d)<=90`. The dual torsion code itself has
minimum weight eight.

## 3. Exact symmetrized MacWilliams transform

Write

```text
S_C(x,y,z)=sum_(a+b+c=99) A_(a,b,c) x^a y^b z^c,
```

where `y` combines symbols one and three. The quaternary MacWilliams
identity is

```text
S_Cperp(x,y,z)
 = |C|^-1 S_C(x+2y+z, x-z, x-2y+z).
```

There are

```text
binom(101,2)=5050
```

raw compositions. The extra torsion word and even residue codes reduce
the primal to 1,119 independent orbits and the allowed dual to 1,114.
Another 161 even-parity dual orbits are fixed to zero by the binary
minimum-distance and high-weight consequences. Odd `nodd` rows cancel
identically.

For a source `(a,b,c)` and target `(*,r,s)`, the transform coefficient
factors exactly:

```text
2^r
[t^r](1+t)^a(1-t)^c
[t^s](1+t)^(99-r-b)(1-t)^b.
```

The package computes the two bracketed factors as integer Krawtchouk
coefficients. It never constructs a dense 5,050-square matrix.

## 4. Forced primal words

For a vertex `u`, let `r_u` be its adjacency row. The one-row words are

```text
±r_u:       (85,14,0),  198 words,
2r_u:       (85,0,14),   99 words,
```

and translation by `2j` supplies the swapped compositions.

For two rows with intersection `t`, the sum and difference types are

```text
r_u+r_v: (71+t,28-2t,t),
r_u-r_v: (71+2t,28-2t,0).
```

Here `t=1` on the 693 edges and `t=2` on the 4,158 nonedges. Each
odd-coefficient type has both global signs. The doubled pair has type
`(71+2t,0,28-2t)` and only one sign because `+2=-2 mod 4`.

For a triple with `e` induced edges and `c` common neighbors, every
all-odd sign orbit has

```text
nodd=30+2e+4c.
```

The all-plus orbit has `n2=6-e-3c`. If one vertex is negative, `n2`
equals `t_uv-c` for the positive pair, with `t_uv=1` on an edge and two
on a nonedge. The six exact triple types and counts are imported from
Wave131 and replayed locally.

The final table is stronger than these named families: it enumerates every
coefficient pattern in `{1,2,3}^S` for every support `|S|<=3`.
Membership-mask counts reconstruct all mixed odd/even patterns. Including
torsion translates gives

```text
2 sum_(s=0)^3 binom(99,s) 3^s = 8,557,760
```

distinct words in 84 expanded compositions, or 42 torsion-symmetry
orbits.

Collision-freeness uses no graph automorphism. Reduction modulo two
recovers the injective maps on coefficient supports of size at most
three. For a fixed support, changing signs changes the word by twice a
nonzero binary row combination. Translation collisions would put `j`
in `R`, already excluded above.

## 5. Forced dual words

Let `q_u=e_u+r_u` be the closed-neighborhood row. A single `q_u` is not
in the quaternary dual, but coefficient vectors of even sum are.
Specifically, `2q_u` is dual, and for distinct vertices both
`q_u+q_v` and `q_u-q_v` are dual because their pairing with any
adjacency row is one of

```text
14+2, 14-2, 2+2, 2-2,
```

all divisible by four.

Closed neighborhoods intersect in three points on an edge and two on a
nonedge. Hence

```text
edge:
  q_u+q_v  (72,24,3),   q_u-q_v  (75,24,0);
nonedge:
  q_u+q_v  (71,26,2),   q_u-q_v  (73,26,0).
```

Sum and difference are distinct and both are counted. Only their doubles
coincide. More generally, a nonzero coefficient pattern on closed rows is
dual exactly when its coefficient sum is even modulo two. Supports of size
zero through three therefore have `1,1,5,13` patterns.

For triples, the intersection of the three closed neighborhoods is `c`
plus the number of induced-degree-two vertices: zero for independent and
one-edge triples, one for paths, and three for triangles. Thus the complete
support-at-most-three table has

```text
2 sum_(s=0)^3 binom(99,s) (1,1,5,13)_s = 4,126,784
```

distinct words in 44 expanded compositions, or 22 torsion-symmetry
orbits.

## 6. Logical boundary

Feasibility of these coefficients is only feasibility of a symmetrized
weight-enumerator relaxation. It does not couple the forced words as
labelled vectors and cannot construct a quaternary code, adjacency
matrix, or graph. Integrality is a separate, stronger question.
