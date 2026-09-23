# Wave 109 independent verification

Verdict: `VERIFIED_SCOPED`.

The sealed Wave 109 claims are correct in their stated conditional scope:
if a hypothetical `srg(99,14,1,2)` contains the induced `C4` Cartesian
`K3` motif, then the claimed primitive lattice, characteristic-seven
orthogonal type, local projector, rank transfer, and Smith/index formulas
follow. No imported rank row is excluded. Motif occurrence, a full
extension, Conway-99, and literature novelty remain `UNKNOWN`.

## Input separation

The discovery package-manifest SHA-256 is
`6d54d48dbb6b1ffd3f7da845792fc12ee490471c02cc8137ebd1b03c21f5347e`.
The verifier froze all ten discovery files before inspection, did not import
the discovery module, and rebuilt the calculation in
`independent_verify.py`. Only after the independent result and its nine
tests passed was the discovery checker rerun; all nine discovery tests also
passed.

## Incidence lattice

The verifier rebuilt the motif in its product coordinates. For each motif
pair it subtracted the number of common neighbors already inside the motif
from the required SRG value, one for an edge and two for a nonedge. The
remaining pair rows, motif degrees, and total outside order force

```text
3 empty rows, 48 singleton rows, 36 pair rows.
```

Thus `P` is `87 x 12` and `Q=[one P]` is `87 x 13`. Rather than accepting
the discovery row indices, the verifier searched row contents for an empty
pattern and the twelve unit patterns. The resulting `13 x 13` minor has
determinant one. Therefore `Q` has rank 13, its column lattice is primitive,
and all thirteen nonzero Smith factors are one.

Using that unit minor as a general integral pivot block, the verifier solved
for every free coordinate and obtained a complete 74-column integral basis
of

```text
Lambda = ker_Z(Q^T).
```

Two independent Bareiss computations give

```text
det(Q^T Q) = det(Lambda)
           = 6191736422400
           = 2^22 3^10 5^2.
```

This verifies the lattice determinant directly, without relying only on the
abstract primitive-complement theorem.

## Orthogonal type over `F_7`

The reduced Gram determinant is `4 mod 7`, a square, and the Gram matrix has
full rank 74 modulo seven. For a nondegenerate symmetric space of dimension
`2m` over a finite field of odd order, the split determinant square class is
`(-1)^m`. Here `m=37`, so the split class is `-1=6 mod 7`, a nonsquare.
The actual square class is different. Hence the space is

```text
O^-(74,7), with Witt index 36.
```

The discovery sign is therefore correct; no sign correction is needed.

## Conditional invariance and projector

The conditional SRG block equations can be written exactly as

```text
DQ = QE
```

for an integral `13 x 13` matrix `E` reconstructed by the verifier. Thus
`D` preserves the orthogonal kernel of `Q^T`. Expanding
`A^2=12I-A+2J` for `T=A+4I` gives

```text
T^2 = 7T + 2J.
```

On the embedded subspace `(0,Lambda)`, the motif block and the `J` term
vanish, so for `B=D+4I`,

```text
B^2 = 7B.
```

The verifier computed `C=H+4I` independently:

```text
det(C)=2332800=1 mod 7.
```

It then formed `RQ`, where
`R=B-PC^(-1)P^T`, solely from the known block actions. Its rank on
`W=span(Q)` is exactly one over both the rationals and `F_7`.

The SRG eigenvalue multiplicities are independently recovered as
`3^54` and `(-4)^44`, so `rank_Q(A+4I)=55`. Schur complementation and the
rank-one action on `W` yield

```text
rank_Q(B|Lambda)=42, nullity_Q(B|Lambda)=32.
```

## Full mod-seven rank transfer

Let `S=2A-J+I` and `r=rank_F7(S)`. Modulo seven,
`2T=S+J`, `S one=0`, and `one^T one=99=1`. Consequently
`rank_F7(T)=r+1`. Since `C` is invertible and the Schur complement has
rank one on `W`,

```text
rank_F7(B|Lambda)=r-12.
```

The complete imported table is:

```text
r: 28 30 32 34 36 38 40 42
k: 16 18 20 22 24 26 28 30
```

Self-adjointness and `B^2=7B` give
`(Bx,By)=7(x,By)`, so the mod-seven image is totally isotropic. Every listed
`k` is at most the Witt index 36. Removing its hyperbolic planes leaves
`O^-(74-2k,7)` in every row, so the residual sign also supplies no
obstruction.

## Smith and index formulas

Let

```text
U = Lambda intersect im_Q(B),
K = Lambda intersect ker_Q(B).
```

Both are saturated. On `U`, `B` acts rationally as seven, giving

```text
7U subset B Lambda subset U.
```

Thus every nonzero Smith factor is one or seven. If the mod-seven rank is
`k`, the exact Smith pattern and first index are

```text
1^k, 7^(42-k), 0^32,
[U:B Lambda]=7^(42-k).
```

The map `x -> Bx mod 7U` has kernel `U direct_sum K` and image of size
`7^k`, hence

```text
[Lambda:U direct_sum K]=7^k.
```

The two rational eigenspaces are orthogonal, so the determinant-index
identity gives

```text
det(U)det(K)=7^(2k)det(Lambda).
```

All exponents are nonnegative in all eight rows, and the residual
orthogonal sign is compatible. These formulas are necessary conditional
consequences, not constructions of an outside adjacency matrix.

## Obstruction search and boundary

The verifier separately tested Witt capacity, residual orthogonal sign,
Smith exponents, and determinant/index compatibility. No additional
obstruction was found. At the level of the finite orthogonal space this is
expected: `O^-(74,7)` contains totally isotropic subspaces of every
dimension from zero through 36, including all eight local ranks.

This verification does not use the Wave 105 linear witness as a graph and
does not construct `D`. It proves no motif occurrence or exclusion, no full
extension or nonextension, and no resolution of Conway-99.
