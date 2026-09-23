# Symbolic cube/Wagner covariance inequality

## Statement

Let:

- `n3` be the number of induced `N3` six-vertex subgraphs;
- `C8` be the number of induced cube graphs, canonical mask `2022000`;
- `W8` be the number of induced Wagner graphs (the eight-vertex Möbius
  ladder), canonical mask `5683824`.

Every hypothetical `srg(99,14,1,2)` satisfies

```text
41580 - n3 + 12*C8 - 4*W8 >= 0.                 (1)
```

Equivalently,

```text
n3 <= 41580 + 12*C8 - 4*W8.
```

This package labels (1) `DERIVED`, not independently `VERIFIED`.

## 1. Root type and the two flags

Use four pointwise-labelled roots `0,1,2,3`. Root mask `12` has exactly
the edges

```text
03, 12,
```

so the roots induce two disjoint edges.

The two nonzero six-vertex flags use free vertices `4,5`:

```text
v(21812) = +1:
03, 05, 12, 15, 24, 34, 45

v(22708) = -1:
03, 05, 12, 14, 25, 34, 45.
```

Swapping free vertices `4,5` does not change the flag class. Forgetting the
root labels, both flags are the same six-vertex class: `N_9`, canonical mask
`1884`.

## 2. The number of ordered roots

There are `99*14=1386` choices of an ordered first root edge `(0,3)`.
Fix one such edge with endpoints `u,v`, and let `c` be its unique common
neighbor.

The vertices nonadjacent to both `u` and `v` number

```text
99 - (2*14 - 1) = 72.
```

Exactly `14-2=12` of those vertices are adjacent to `c`: every neighbor of
`c` other than `u,v` is nonadjacent to both endpoints, because an additional
adjacency would give an adjacent pair more than one common neighbor.

If `x` is one of these 12 vertices, the `mu=2` equations for the nonedges
`xu` and `xv` show that `x` has three neighbors outside the 72-set: `c`,
one additional neighbor shared with `u`, and one shared with `v`. Hence its
degree inside the 72-set is `14-3=11`.

For each of the remaining 60 vertices, the two pairs of common neighbors
with `u` and `v` are disjoint, so it has four neighbors outside the set and
degree `14-4=10` inside it.

Thus the number of ordered second edges `(1,2)` inside the common
nonneighbor set is

```text
12*11 + 60*10 = 732.
```

The number of ordered pointwise-labelled root embeddings is therefore

```text
R = 1386*732 = 1014552.                         (2)
```

## 3. Cauchy-Schwarz covariance

For each ordered root embedding `r`, let

```text
z_r = sum_p v(flag induced by r and the unordered free pair p),
```

where `p` ranges over all free vertex pairs outside the roots. Cauchy-Schwarz
gives

```text
R * sum_r z_r^2 - (sum_r z_r)^2 >= 0.          (3)
```

Expanding `z_r^2` uses ordered pairs of free pairs. Their union with the four
roots has order 6, 7, or 8.

## 4. Exhaustive union table

The finite enumeration fixes the roots, tries both orientations of each
nonzero flag under the free-vertex swap, tries every ordered covering pair,
fills every edge unseen by either flag, enforces the `lambda<=1` and
`mu<=2` local caps, and canonically quotients the result.

The complete nonzero table is:

| union order | class | first coefficient | quadratic coefficient |
|---:|---|---:|---:|
| 6 | `N_9`, mask `1884` | 0 | 8 |
| 7 | none | 0 | 0 |
| 8 | cube, mask `2022000` | 0 | 96 |
| 8 | Wagner/Möbius ladder, mask `5683824` | 0 | -32 |

The small integer counts can also be checked directly:

- `N_9` has eight matching ordered root embeddings: four evaluate to `+1`
  and four to `-1`. The first moment is zero and the eight squares sum to 8.
- The cube has 48 root embeddings. Across their six ordered covering pairs,
  96 products are `+1` and 192 are zero.
- The Wagner graph has 16 root embeddings. Across their six ordered covering
  pairs, 32 products are `-1` and 64 are zero.
- No compatible order-seven union of two nonzero flags exists.

Consequently,

```text
sum_r z_r     = 0,
sum_r z_r^2   = 8*N_9 + 96*C8 - 32*W8.         (4)
```

Substituting (4) into (3), using positive `R`, and dividing by `8R` gives

```text
N_9 + 12*C8 - 4*W8 >= 0.                       (5)
```

## 5. Substitute the independent six-set formula

In the frozen Wave43 independent transcription, `N_9` is the ninth formula:

```text
N_9 = b/4 - n3,
b   = n*k*(k-2)*(k-4).
```

At `n=99`, `k=14`,

```text
b/4 = 99*14*12*10/4 = 41580,
N_9 = 41580 - n3.                              (6)
```

Equations (5) and (6) give (1).

## 6. Recover the stored endpoint constant

At `n3=4158`,

```text
N_9 = 41580 - 4158 = 37422.
```

The integer specialization of (1) is

```text
37422 + 12*C8 - 4*W8 >= 0.
```

Every coefficient now has an additional common factor two, so its primitive
endpoint form is

```text
18711 + 6*C8 - 2*W8 >= 0.
```

Thus the stored endpoint constant `18711` is recovered without assuming it.
The symbolic raw divisor is `8R`; the endpoint's extra factor two makes the
stored divisor `16R=16232832`.

## 7. Does this improve the upper bound?

Not by itself. At `n3=4158`, the nonnegative assignment `C8=W8=0` leaves
the left side of (1) equal to `37422`, so this inequality alone does not
exclude the endpoint.

It identifies a precise possible companion target. At the endpoint, an
independent theorem

```text
4*W8 - 12*C8 >= 37424
```

would make the right side of the rearranged bound at most `4156`. Since the
known structural identity gives `n3` divisible by three, that would imply
`n3<=4155`. No such cube/Wagner comparison is proved here.

The present statuses therefore remain:

```text
strict_upper_bound_below_4158: NOT_PROVED
endpoint_n3_4158: UNKNOWN
graph_constructed: false
Conway_99: UNKNOWN
```

