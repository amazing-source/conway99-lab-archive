# Wave 59 proof-B report: incidence spectral-excess space

Status: `DERIVED`, pending independent verification.

## Assignment

Recast the prism-free endpoint as a point--triangle incidence graph, check
its semiregular spectral and distance structure, square to the regular
triangle graph, and test spectral-excess, predistance, Ihara--Bass, PSD/rank,
and cage routes without assuming an automorphism.

## Exact results

The incidence graph is conditionally a connected `(7,3)`-biregular graph on
`99+231` vertices with spectrum

```text
+/-sqrt(21)^1, +/-sqrt(10)^54, +/-sqrt(3)^44, 0^132.
```

It has girth eight and diameter six. Point roots have the equitable distance
layers

```text
1,7,14,84,84,140
```

with intersection array

```text
{7,2,6,2,5; 1,1,1,2,3}.
```

Triangle roots have layers

```text
1,3,18,36,180,60,32.
```

At distance four, the 36 relation-`B` triangles have two predecessors while
the 144 relation-`C` triangles have one. The incidence graph is therefore
not distance-biregular. Fiol's semiregular theorem is in its even-diameter
case (c), since `m(0)=132=231-99`; the ordinary regular theorem was not
misapplied to this graph.

The 18-regular triangle graph has spectrum

```text
18^1, 7^54, 0^44, (-3)^132
```

and diameter three. Its degree-three predistance polynomial is

```text
p3(x)=x^3/18-35x^2/36+19x/12+25/2.
```

Its spectral excess is 50 and its actual excess is 32. Exact relation walk
counts are

```text
K^3: I=90, K=59, B=26, C=22, D=18.
```

The exact defect is

```text
p3(K)-A_D=(A_C-2A_B)/4,
||p3(K)-A_D||^2=18.
```

The orthogonal projection of `A_D` onto the polynomial adjacency algebra is
`(16/25)p3(K)` and its residual normalized squared norm is `288/25`.
The signed defect is indefinite, so it gives no PSD contradiction.

The binary pair-of-common-neighbors Gram matrix is

```text
153I+10K+A_B.
```

It is at least `87I`, hence positive definite of rank 231. This is a new
exact rank condition but is compatible with the available feature space.

Ihara--Bass gives

```text
C8=2079, C10=33264, C12=250866, C14=2494800.
```

All counts are exact, integral, and consistent. The `(7,3;8)` Moore lower
bound is only 130 vertices, far below 330.

## Boundary

- No target automorphism or relation transitivity is assumed.
- The `B/C/D` matrices are not assumed to commute with the triangle graph.
- Strict spectral-excess inequality proves non-distance-regularity, not
  nonexistence.
- The result supplies no graph, endpoint exclusion, strict `n3` upper bound,
  or novelty claim.
- Conway-99 and the prism-free endpoint remain `UNKNOWN`.

The exact envelope is
`attempts/wave59-incidence-spectral-excess/exact-result.json`.
