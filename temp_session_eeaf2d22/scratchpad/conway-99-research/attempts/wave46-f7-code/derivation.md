# Exact derivation and null boundary

## 1. Correct object and endpoint data

The live object is the integral triangle projector

```text
M=21E_0 in Z^(231 x 231).
```

At the conditional endpoint `n3=4158`, the supplied exact identities are

```text
M^2=21M,             M*1=0,
M_ii=4,              M_ij in {0,+1,-1} for i != j,
row(M): 4^1, 1^32, (-1)^36, 0^162.
```

The previously verified rank window is

```text
28 <= rank_F7(M) <= rank_Q(M)=44.
```

All conclusions below are conditional on this endpoint package.

An initial assignment phrase named `A+3I`. That is a different 99 by 99
matrix and is quarantined in Section 8.

## 2. The row code

Reduce modulo seven and set

```text
C=row_F7(M),  dim(C)=r7.
```

Because `21=0` in `F7`,

```text
M^2=0.
```

The matrix is symmetric, so the inner product of row `i` with row `j` is
the `(i,j)` entry of `M^2`. Hence every two rows are orthogonal and

```text
C subset C^perp.                                  (1)
```

The zero row sum also gives

```text
C subset 1^perp.                                  (2)
```

Every column is nonzero because its diagonal entry is four. No two columns
are projectively proportional. Indeed, suppose column `i` equals `a` times
column `j`. At coordinate `i`,

```text
4=a*M_ij,
```

so `M_ij` is `+1` or `-1`. At coordinate `j`,

```text
M_ij=4a.
```

Combining gives `M_ij^2=16=2 mod 7`, contradicting
`M_ij^2=1`. Thus a generator matrix for `C` has 231 nonzero, pairwise
nonproportional columns. Equivalently,

```text
d(C^perp)>=3,                                     (3)
```

and `C` is an orthogonal array of strength two.

## 3. Distinguished weight-69 codewords

In symbols `0,...,6`, one endpoint row has composition

```text
(n0,n1,n2,n3,n4,n5,n6)=(162,32,0,0,1,0,36).
```

Its coordinate sum and squared norm are

```text
32+4-36=0,
32+16+36=84=0 mod 7.
```

Multiplication by each scalar in `F7^*` produces six distinct symbol
compositions. The 231 matrix rows lie on 231 distinct projective lines by
the column argument above, applied to the symmetric matrix. Therefore all
six multiples of all rows are distinct, and

```text
A_69 >= 6*231 = 1386.                             (4)
```

For the complete weight enumerator, every one of the six scalar
compositions has coefficient at least 231.

## 4. What sum and norm say about ordinary weights

Every `x in C` obeys

```text
sum_i x_i=0,              sum_i x_i^2=0 mod 7.    (5)
```

An exact dynamic program tracks the pair of residues in (5) while adding
one nonzero coordinate. For weights from zero through 231, the only
infeasible values are

```text
1, 2, 4.
```

Every other weight has at least one sequence of nonzero symbols satisfying
the two congruences. This is only a congruence feasibility statement, not a
claim that the endpoint code contains every remaining weight.

## 5. Ordinary MacWilliams identities do not close

For ordinary weight distributions `A_i` of `C` and `B_j` of `C^perp`,

```text
B_j=7^(-r7) sum_i A_i K_j^(231,7)(i).
```

Self-orthogonality gives `B_j>=A_j`; projectivity gives `B_1=B_2=0`.
These constraints, (4), and the forbidden weights still cannot produce an
ordinary-enumerator contradiction. The reason is stronger than a feasible
linear-programming vector: there are actual generic codes satisfying all
of them for every `r7` in the endpoint window.

### Explicit positive controls

In `F7^4`, take the 21 columns on the three affine lines

```text
e0+t e1,
e2+t e3,
e0+e2+t(e1+e3),           t in F7.                (6)
```

They are nonzero and projectively distinct. For any line `v+t w`,

```text
sum_t (v+t w)=0,
sum_t (v+t w)(v+t w)^T=0
```

because `sum 1=sum t=sum t^2=0` in `F7`. Thus (6) generates a projective,
self-orthogonal `[21,4]_7` code in `1^perp`. Exact enumeration gives

```text
W_21(z)=1+126z^12+18z^14+1470z^18+756z^19+30z^21.
```

Take eleven direct-sum blocks. Keep the first four blocks, of dimension 16,
fixed. The coefficient of `z^69` in `W_21(z)^4` is

```text
668653683264.                                     (7)
```

The last seven blocks have dimension 28 and length 147. For each target
`r=28,...,44`, let `d=r-16` and left-multiply their generator by an archived
full-rank `d by 28` matrix whose 147 resulting columns remain nonzero and
projectively distinct. Direct-summing this tail with the first four blocks
gives a projective, self-orthogonal `[231,r]_7` code in `1^perp`.

The full projection matrices, their individual SHA-256 hashes, and hashes of
the resulting generator-column streams are in `exact-results.json`. The
checker reconstructs every generator and verifies rank, Gram matrix, row
sums, projectivity, and (7) exactly.

These are separation controls only. They do not reproduce the six exact
endpoint row compositions and do not satisfy the projector identity.
Therefore they show:

```text
generic ordinary code constraints survive,
endpoint generator geometry remains untested by that relaxation.
```

## 6. Low-degree complete-enumerator moments

Property (3) makes `C` an orthogonal array of strength two. For a code of
dimension `r`, summing over all codewords gives, for every symbol `a` and
every ordered symbol pair `(a,b)`,

```text
sum_x n_a(x) = 231*7^(r-1),
sum_x n_a(x)(n_b(x)-[a=b]) = 231*230*7^(r-2).     (8)
```

The smallest code, `r=28`, gives the strongest comparison. The 1,386 known
row multiples contribute strictly less than every required moment:

```text
minimum first-moment slack  =
15179555705976418712009901,

minimum second-moment slack =
498756830339225186222981718.
```

The complete degree-zero, one, and two moment tests therefore pass. This
does not construct the remaining `7^r-1-1386` codewords or a valid complete
weight enumerator. Higher complete MacWilliams data are underdetermined.

## 7. Third Schur power

Let `M^(o3)` mean entrywise cubing. The endpoint alphabet gives

```text
M^(o3)=M+4I mod 7.
```

Using `M^2=0`,

```text
(M+4I)(3M+2I)=I.
```

Hence `M^(o3)` has rank 231. Its rows are coordinatewise cubes of rows of
`M`, so the third Schur power of `C` is all of `F7^231`. Since the symmetric
cube of an `r7`-space has dimension at most `binom(r7+2,3)`,

```text
binom(r7+2,3)>=231,
r7>=11.
```

This exact identity is useful structural information, but its rank floor is
strictly weaker than the independently verified endpoint floor `r7>=28`.

## 8. Quarantined prompt-error control

For the 99 by 99 adjacency matrix `A` with eigenvalues

```text
14^1, 3^54, (-4)^44,
```

the different matrix `A+3I` has eigenvalues `17,6,-1`. Its determinant is
`3 mod 7`, so its row code is the full `F7^99`. It is not `M=21E_0` and is
not used in any live conclusion. The checker retains this calculation only
to prevent recurrence of the object mismatch.

## 9. Exact boundary

This lane establishes no endpoint contradiction and no stronger rank floor.
The missing information is:

1. the symbol compositions, or equivalent character sums, of the other
   `7^r7-1-1386` nonzero codewords;
2. higher dual composition coefficients or a proved stronger dual-distance
   exclusion;
3. constraints retaining the distinguished 231 rows and their mutual
   coordinatewise products, which the ordinary row span forgets.

Accordingly:

```text
ordinary weight-enumerator contradiction: false
low-degree complete-enumerator contradiction: false
strict n3 upper bound below 4158:             not proved
n3=4158:                                      UNKNOWN
Conway-99:                                    UNKNOWN
novelty:                                      UNKNOWN
```
