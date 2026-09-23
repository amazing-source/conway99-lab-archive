# Finite-primary split of the rank-74 incidence kernel

Claim label: `DERIVED`; independent verification required.

## 1. The complementary lattice and its discriminant presentation

Let `Q=[one P]` be the primitive `87 x 13` matrix from Wave 109, and put

```text
Lambda=ker_Z(Q^T),              W=im_Z(Q).
```

The unit `13 x 13` minor of `Q` makes `W` primitive in the odd unimodular
lattice `Z^87`.  Thus `Lambda=W^perp`, and their discriminant bilinear
groups are anti-isometric.  In the displayed basis of `W`,

```text
G=Q^T Q,
A_W = W*/W = Z^13/G Z^13,
det(G)=2^22 3^10 5^2.
```

The exact local Smith valuations of `G` are

```text
p=2:  2,3,3,3,3,8
p=3:  1,1,1,1,2,2,2
p=5:  1,1
p=7:  none.
```

## 2. The unknown graph acts explicitly on the discriminant group

Although the outside adjacency matrix `D` is unknown, its action on
`W=span(one,P)` is fixed by the linear block equations:

```text
B one = 18 one-P one,
B P   = 2J+3P-PH,                 B=D+4I.
```

Let `C` be the resulting `13 x 13` coordinate matrix, so `BQ=QC`.
Self-adjointness is the exact identity

```text
G C = C^T G.
```

On the presentation `A_W=Z^13/GZ^13`, the induced action is `C^T`.
The checker produces an integral matrix `X` satisfying

```text
(C^T)^2-7C^T = G X.                         (1)
```

Thus the projector relation, which Wave 109 established on `Lambda`, also
holds on its discriminant group.  At `p=2,3,5`, seven is a unit and

```text
E=C^T/7
```

is an idempotent.  Its image is the discriminant contribution of the
`3`-eigenlattice `U`; its complementary image is that of the
`-4`-eigenlattice `K`.

## 3. Exact local presentation split

For `p != 7`, quotienting `A_W` by `im(1-E)` leaves the `U` component,
while quotienting by `im(E)` leaves the `K` component.  Since seven is a
unit, these have the exact presentation matrices

```text
A_U,p = coker [G | 7I-C^T],
A_K,p = coker [G | C^T].
```

Exact Smith elimination over `Z_p` gives

```text
A_U,2 = Z/256 + Z/4
A_U,3 = (Z/9)^2 + (Z/3)^2
A_U,5 = (Z/5)^2

A_K,2 = (Z/8)^4
A_K,3 = Z/9 + (Z/3)^2
A_K,5 = 0.
```

The orders partition the complete non-seven determinant:

```text
|A_U,(7')| = 2^10 3^6 5^2,
|A_K,(7')| = 2^12 3^4.
```

## 4. Exact quadratic Gauss phases

The group split can be refined without pretending that the odd lattice
`W` is even.  The ambient lattice `Z^87` has characteristic vector
`one=Qe_0`, and `one` lies in `W`.  If

```text
x=a/p^e in W*,                 y=Gx in Z^13,
```

then the corresponding class in the even complementary lattice has

```text
q_Lambda(x) = (y_0-x^T G x)/2 mod Z.                 (2)
```

Indeed, choose an ambient integral lift `z` whose projection to `W` is
`x`.  The complementary vector has norm `z^2-x^2`, while
`z^2 = <z,one> = <x,one> = y_0 mod 2`.

For each primary component, the checker enumerates the exact kernel modulo
the exponent:

```text
G a=0,
(C-7I)a=0       for U,
C a=0           for K.
```

It evaluates (2) on every element and reduces the resulting sum exactly
modulo the relevant cyclotomic polynomial.  No floating-point phase
recognition is used.  The normalized Gauss phases are

```text
          p=2    p=3    p=5      product away from 7
U         -i     -1     -1       -i
K         +1     -1     +1       -1.
```

Milgram's formula gives total phases `i` in rank 42 and `+1` in rank 32.
Consequently the seven-primary phase is `-1` for both `U` and `K`.

## 5. Characteristic-seven gluing

Write

```text
k=rank_F7(B|Lambda)=r-12.
```

Wave 109 gives

```text
[Lambda:U+K]=7^k.
```

Because `Lambda` is unimodular over `Z_7` and `U,K` are saturated
orthogonal complements, their seven-primary discriminant groups are
anti-isometric and have the same order.  The determinant product therefore
forces

```text
v7(det U)=v7(det K)=k.
```

Moreover, locally at seven,

```text
B Lambda = 7 U*,
(7I-B) Lambda = 7 K*.
```

This follows by self-adjointness and equality of the indices
`7^(42-k)` and `7^(32-k)`, respectively.  Hence both seven-primary groups
are elementary:

```text
A_U,7 = (Z/7)^k,             A_K,7 = (Z/7)^k.         (3)
```

Combining the primes yields the exact formulas

```text
det(U)=2^10 3^6 5^2 7^k,
det(K)=2^12 3^4 7^k.                                (4)
```

They hold for every imported row `k=16,18,...,30`.

For an elementary `k`-dimensional quadratic form over `F_7`, with `k`
even, the normalized Gauss phase is

```text
(-1)^(k/2) Legendre(det,7).
```

The phase `-1` therefore forces

```text
Legendre(det,7)=(-1)^(k/2+1).
```

This is the non-split type `O^-(k,7)` for every live row.  The type is
sharp but compatible with all of them.

## 6. A rootless consequence

Both eigenlattices are even because they lie in
`Lambda subset one^perp`.  A norm-two vector in `Lambda` must be
`+/- (e_i-e_j)`.  At coordinate `i`,

```text
(D(e_i-e_j))_i = -D_ij in {0,-1}.
```

This is neither `3`, required in `U`, nor `-4`, required in `K`.
Consequently

```text
min(U)>=4,                 min(K)>=4.                 (5)
```

## 7. Boundary

The finite-primary shift fixes much more than the determinant product: it
determines every non-seven invariant factor and Gauss phase of both
rational eigenlattices, makes their seven parts elementary non-split forms,
and proves both are rootless.  All eight rank rows nevertheless satisfy
these necessary local conditions.  No lattice `U` or `K`, outside graph,
motif extension, or target strongly regular graph is constructed.

```text
rank row excluded:       NO
motif excluded:          NO
Conway-99:               UNKNOWN
literature novelty:      UNKNOWN
```
