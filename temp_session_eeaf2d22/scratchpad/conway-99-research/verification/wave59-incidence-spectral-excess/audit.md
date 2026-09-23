# Wave 59 independent audit

Verdict: `VERIFIED` for the stated finite conditional consequences only.
Conway-99 and the prism-free endpoint remain `UNKNOWN`.

The verifier hashed the sealed package before reading it, did not open,
import, or execute either discovery implementation or discovery tests, and
recomputed the result from the frozen `srg(99,14,1,2)` parameters plus the
explicit prism-free endpoint hypothesis.

## 1. Incidence arithmetic and spectra

The SRG identity is

```text
A^2 = 12I - A + 2J,
sp(A) = 14^1, 3^54, (-4)^44.
```

Because every edge is in its unique triangle, there are `693/3=231`
triangles and seven triangles through each point. For the `99 x 231`
point--triangle incidence matrix,

```text
N N^T = A + 7I.
```

Therefore `rank(N)=99`, and its nonzero squared singular values are
`21^1,10^54,3^44`. This independently gives

```text
sp(L) = +/-sqrt(21)^1, +/-sqrt(10)^54,
        +/-sqrt(3)^44, 0^132
```

for `L=[[0,N],[N^T,0]]`, and

```text
sp(K) = 18^1, 7^54, 0^44, (-3)^132
```

for `K=N^T N-3I`. The trace-square check for `L` is
`2(21+54*10+44*3)=1386=2*693`.

## 2. Girth, diameter, layers, and relations

Two distinct triangles share at most one point, so `L` has no four-cycle.
A six-cycle would represent three graph points whose three edges lie in
three distinct triangles, contradicting uniqueness of the triangle on a
graph triangle. A nonedge has exactly two common neighbors, yielding a graph
four-cycle and hence an incidence eight-cycle. Thus `girth(L)=8`.

For an arbitrary root triangle, not using transitivity:

```text
K = 3(7-1) = 18,
B+C+D = 231-1-18 = 212,
2B+C = 3(14-2)(7-1) = 216.
```

For each pair of the three 12-point outside-neighbor sectors, the `mu=2`
condition supplies a perfect matching of size 12. At the prism-free endpoint,
the unique triangle on a matching edge cannot have a third root cross edge.
The 36 matching edges therefore give 36 distinct `B` triangles. Hence

```text
B=36, C=144, D=32.
```

This proves the exact root layers

```text
point root:    1,7,14,84,84,140
triangle root: 1,3,18,36,180,60,32.
```

The point-root intersection array is
`{7,2,6,2,5;1,1,1,2,3}`. At triangle-root distance four, a `B` line has two
predecessor points while a `C` line has one. Both classes are nonempty, so
that partition is not equitable. Consequently `diameter(L)=6`, every
point-root partition is equitable, and `L` is not distance-biregular.

The source check confirms that Fiol's semiregular theorem is indeed in case
6(c): `d=6` is even and `m(0)=132=231-99`. The ordinary regular
spectral-excess theorem is not applied to `L`.

In the regular triangle graph, `K`, the distance layers are
`1,18,180,32`. A `B` or `C` pair has a common triangle-graph neighbor
arising from a cross edge, whereas a `D` pair has none; the corresponding
incidence path gives distance three. Hence `K` is connected and regular,
has diameter three, and has four distinct eigenvalues. These are the
hypotheses needed for the ordinary spectral-excess theorem.

## 3. Predistance polynomials and exact walk tables

Exact Gram--Schmidt orthogonalization for

```text
<f,g> = (f(18)g(18)+54f(7)g(7)+44f(0)g(0)+132f(-3)g(-3))/231
```

with `||p_i||^2=p_i(18)` gives

```text
p0 = 1
p1 = x
p2 = 3x^2/4 - 15x/4 - 27/2
p3 = x^3/18 - 35x^2/36 + 19x/12 + 25/2.
```

The common-neighbor and cross-edge counts independently give

| relation | `I` | `K` | `B` | `C` | `D` |
|---|---:|---:|---:|---:|---:|
| `K^2` | 18 | 5 | 2 | 1 | 0 |
| `N^T A N` | 6 | 4 | 2 | 1 | 0 |

The spectrum gives the exact Hoffman/minimal-polynomial identity

```text
K^3 - 4K^2 - 21K = 18J,
```

so the independently obtained `K^3` row is

| relation | `I` | `K` | `B` | `C` | `D` |
|---|---:|---:|---:|---:|---:|
| `K^3` | 90 | 59 | 26 | 22 | 18 |

It follows that `p3(18)=50`, while the actual distance-three valency is
`32`. Equality in the spectral-excess theorem therefore fails, certifying
only that `K` is not distance-regular.

## 4. Defect, projection, and Gram matrix

Substitution in the relation tables gives

```text
p3(K)-A_D = (A_C-2A_B)/4,
||p3(K)||^2 = 50,
||A_D||^2 = <p3(K),A_D> = 32,
||p3(K)-A_D||^2 = 18.
```

Since `A_D` is orthogonal to `p0,p1,p2`, its polynomial-algebra projection is
`(32/50)p3(K)=(16/25)p3(K)`. The residual norm is

```text
32 - 32^2/50 = 288/25,
```

and the angle cosine is `4/5`. For `F=A_C-2A_B`, the verifier also obtains
row sum `72`, trace `0`, and `trace(F^2)=66528`; its positive row
eigenvalue and zero trace make it indefinite, not PSD.

For each triangle, index the unordered pairs of its 18 `K`-neighbors. The
row Gram entry for roots `R,S` is

```text
binom((K^2)_{R,S},2).
```

The `K^2` table therefore yields exactly

```text
153I + 10K + A_B.
```

Weyl's inequality and the elementary adjacency bound
`lambda_min(A_B)>=-36` give

```text
lambda_min >= 153 + 10(-3) - 36 = 87.
```

Thus the Gram matrix is positive definite and has rank 231. This is
consistent because the feature space is larger than 231.

## 5. Ihara--Bass and short cycles

For the 330-vertex, 693-edge biregular incidence graph, the verifier
specialized

```text
det(I-uH) = (1-u^2)^(693-330)
            det(I-uA_L+u^2(D-I)).
```

Taking the Schur complement with the squared singular values
`21,10,3` gives

```text
(1-u^2)^363
* (1+2u^2)^132
* (1-13u^2+12u^4)
* (1-2u^2+12u^4)^54
* (1+5u^2+12u^4)^44,
```

A fresh exact formal-log expansion gives

```text
tr(H^2), tr(H^4), tr(H^6) = 0,0,0
tr(H^8), tr(H^10)         = 33264,665280
tr(H^12),tr(H^14)         = 6020784,69854400.
```

For length below `2*girth=16`, a repeated-vertex tailless nonbacktracking
closed walk would split into two closed nonbacktracking walks, each of
length at least the girth; repeated traversal also needs length at least 16.
Division by `2l` is therefore valid for `l=8,10,12,14`, giving

```text
C8=2079, C10=33264, C12=250866, C14=2494800.
```

Independently, the `4158` graph nonedges each index a four-cycle by their two
common neighbors, and every graph four-cycle has two nonedge diagonals.
Thus `4158/2=2079` reconfirms `C8`.

## 6. Cage comparison and corrections

The girth-eight edge-root tree has

```text
points = 1+2+12+24 = 39,
lines  = 1+6+12+72 = 91,
total  = 130.
```

It satisfies the required balance `7*39=3*91`. Equality would have
generalized-quadrangle order `(2,6)` and diameter four. The target has 330
vertices and diameter six, an excess of 200, so the comparison supplies no
contradiction.

All mathematical fields selected from the sealed result matched. Two
source-metadata details should be corrected:

1. the official author form is `Miquel Àngel Fiol`, not the unaccented
   `Miquel Angel Fiol`;
2. Theorem 6's statement is on printed page 6; its proof continues beyond
   page 7, so `printed pages 6-7` is imprecise as a complete location.

Neither correction affects the mathematics.

## Boundary

This package verifies implications of the hypothetical prism-free graph. It
does not provide such a graph, exclude the endpoint, improve `n3<4158`,
establish novelty, or resolve Conway-99.
