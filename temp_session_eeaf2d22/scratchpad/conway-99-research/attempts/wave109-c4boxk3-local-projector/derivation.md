# Local projector derivation

Claim label: `DERIVED`; independent verification required.

## 1. The forced incidence lattice

Let `H` be the adjacency matrix of `C4` Cartesian `K3`, and let `P` be the
`87 x 12` outside-to-motif incidence matrix forced in Wave 105. Rebuilding
the multiset gives three zero rows, four copies of every singleton row, and
36 pair rows. Put

```text
Q=[one P].
```

Choose one zero row and one copy of each of the twelve singleton rows. The
corresponding `13 x 13` minor of `Q` consists of `[1,0]` and the rows
`[1,e_i]`, so its determinant is one. Therefore `Q` has rank 13 and all
thirteen nonzero Smith factors are one. In particular its column lattice is
primitive in `Z^87`.

The orthogonal kernel

```text
Lambda=ker_Z(Q^T)
```

has rank 74. The checker constructs an explicit integral basis: for every
unselected row with pattern `a`, put `1` at that row, `-1` at each selected
singleton in `a`, and `|a|-1` at the selected zero row. It checks both
`Q^T L=0` and

```text
det(L^T L)=det(Q^T Q)=6191736422400
          =2^22 3^10 5^2.                            (1)
```

The equality of discriminants also follows abstractly because a primitive
integral sublattice and its orthogonal complement in a unimodular lattice
have isomorphic discriminant groups.

## 2. The characteristic-seven type

Equation (1) is `4 mod 7`, so the reduced form on
`Lambda/7Lambda` is nondegenerate and has square determinant. For a
nondegenerate symmetric space of dimension `2m` over an odd finite field,
the split space has determinant square class `(-1)^m`. Here `m=37`, and
`-1` is a nonsquare in `F_7`. Thus the split determinant class is nonsquare,
whereas (1) is square. Consequently

```text
Lambda/7Lambda = O^-(74,7),       Witt index 36.       (2)
```

This corrects the tempting but wrong `O^+` assignment obtained by ignoring
the odd half-dimension.

## 3. The invariant local projector

Write the hypothetical global adjacency matrix in motif-first order:

```text
A = [H  P^T]
    [P   D ].
```

Let `s=P one`. The SRG block equations give

```text
D one = 14 one-s,
D P   = 2J-P-PH.                                      (3)
```

If `x in Lambda`, then `one^T x=P^T x=0`. Equation (3) gives
`one^T D x=P^T D x=0`, so `D` preserves `Lambda`.

Set `T=A+4I` globally and `B=D+4I` locally. From
`A^2=12I-A+2J`,

```text
T^2=7T+2J.                                             (4)
```

For `x in Lambda`, the motif block of `T(0,x)` is `P^T x=0`, and
`J(0,x)=0`. Restricting (4) therefore gives

```text
B^2=7B on Lambda.                                      (5)
```

Over the rationals, `T` has rank 55: its eigenvalues are
`18^1,7^54,0^44`.

## 4. Rational rank through the motif Schur complement

Put `C=H+4I`. The checker obtains

```text
det(C)=2332800 = 1 mod 7,
P^T P=12I-H+2J-H^2,
C^(-1) P^T P=3I-H+J/4.                                (6)
```

The Schur complement is

```text
R=B-P C^(-1) P^T.
```

It equals `B` on `Lambda`. Let `W=span_Q(Q)`, the orthogonal complement of
`Lambda`. Direct use of (3) and (6) gives, with
`u=2 one-(P one)/4`,

```text
R one=9u,       R P=u one^T.                           (7)
```

Thus `R|W` has rank one. Since `rank(T)=55` and `C` has rank 12,
`rank(R)=43`; hence

```text
rank_Q(B|Lambda)=42,       nullity_Q(B|Lambda)=32.      (8)
```

## 5. Characteristic-seven rank transfer

Let

```text
S=2A-J+I,       r=rank_F7(S).
```

Modulo seven, `T=(S+J)/2`. Also `S one=0`, while
`one^T one=99=1 mod 7`. Splitting the domain into `one^perp` and
`span(one)` shows

```text
rank_F7(T)=r+1.                                         (9)
```

Because `C` remains invertible, Schur complementation gives
`rank(T)=12+rank(R)`. The Gram matrix `Q^TQ` is also invertible modulo seven,
so `F_7^87=Lambda direct_sum W` orthogonally. Equations (6)--(7) reduce to

```text
R one=4(one-P one),
R P=2(one-P one) one^T,
```

and again `rank(R|W)=1`. Since `R|Lambda=B`,

```text
rank_F7(B|Lambda)=r-12.                                (10)
```

For the imported global rows `r=28,30,...,42`, the local rows are
`k=16,18,...,30`.

## 6. Isotropy, Smith factors, and indices

Symmetry and (5) imply, for all `x,y in Lambda`,

```text
(Bx,By)=x^T B^2 y=7 x^T B y.
```

Thus the mod-seven image of `B` is totally isotropic. By (2), its dimension
`k` is at most 36. Every imported value `16<=k<=30` survives.

Let

```text
U=Lambda intersect im_Q(B),       K=Lambda intersect ker_Q(B).
```

Both are saturated. Equation (5) gives

```text
7U subset B Lambda subset U.
```

Therefore the 42 nonzero Smith factors of `B` are only `1` or `7`. If
`k=rank_F7(B)`, they are exactly

```text
1^k, 7^(42-k), followed by 0^32,
[U:B Lambda]=7^(42-k).                                (11)
```

The map `x -> Bx mod 7U` has kernel `U direct_sum K`, so

```text
[Lambda:U direct_sum K]=7^k.                           (12)
```

Since `U` and `K` are rationally orthogonal, (1) and (12) give

```text
det(U)det(K)=7^(2k)det(Lambda).                         (13)
```

Peeling off the totally isotropic `k`-space leaves
`O^-(74-2k,7)`. These exact consequences produce no contradiction in any
row.

## 7. Boundary

The Wave 105 linear witness is not used as an SRG. No outside graph is
constructed, no global rank row is removed, and no nonexistence conclusion
follows. The full motif extension, Conway-99, and literature novelty remain
`UNKNOWN`.
