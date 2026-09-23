# A local four-cycle multiplicity target for the rank-28 row

Claim label: `DERIVED`; independent verification required.

## 1. The target has 2,079 induced four-cycles

The target has `99*14/2=693` edges and therefore 4,158 nonedges. Each
nonedge has exactly two common neighbors. Those common neighbors cannot be
adjacent, because then that adjacent pair would already have the two
nonedge endpoints as common neighbors, contradicting `lambda=1`.

Thus every nonedge is one diagonal of a unique induced four-cycle. Every
four-cycle has two diagonals, so

```text
C4(G)=4158/2=2079.                                      (1)
```

## 2. Four-cycles inside short-vector supports

Count only alternating four-cycles between the positive and negative sign
sides.

For an `s+s` four-regular bipartite support, let `c_ij` be the number of
common opposite-side neighbors of a pair on one sign side. The pair is
nonadjacent in the target, so `c_ij<=2`, and

```text
sum_{i<j} c_ij = s*C(4,2)=6s.
```

Every pair with `c_ij=2` gives one alternating four-cycle. Distributing a
sum of `6s` among `C(s,2)` entries in `{0,1,2}` therefore forces at least

```text
6s-C(s,2)
```

entries equal to two. This gives:

```text
norm 14, s=7: exactly 21 alternating C4s,
norm 16, s=8: at least 20 alternating C4s,
norm 18, h=0, s=9: at least 18 alternating C4s.          (2)
```

In the norm-18 `h=1` branch, one same-sign pair is adjacent and has
codegree at most one. The two opposite-side endpoints of the same-sign edge
have cross degree five, while the other seven vertices have degree four.
Hence

```text
sum c_ij = 2*C(5,2)+7*C(4,2)=62.
```

After assigning one unit to the adjacent pair, 61 units remain on 35
nonadjacent pairs of capacity two. At least 26 of those pairs have codegree
two:

```text
norm 18, h=1: at least 26 alternating C4s.               (3)
```

These are lower bounds. Extra four-cycles only strengthen the next count.

## 3. A cap of 25 antipodal extensions would exclude rank 28

In the rank-28 row, verified modular forms give

```text
N14+N16+N18 >= 5868.
```

Using only the weakest coefficient in (2)--(3), the number of incidences
between oriented short vectors and their alternating four-cycles is at
least

```text
18*5868=105624.                                         (4)
```

Dividing by (1) gives an average oriented multiplicity

```text
105624/2079 = 50.805...
```

Each occurrence is paired with the antipodal vector, so some target
four-cycle occurs in at least 52 oriented vectors, equivalently 26
antipodal support pairs.

Consequently, the following local statement would close the hardest row:

> Every induced four-cycle extends to at most 25 antipodal norm-14,
> norm-16, or norm-18 signed supports in total.

Indeed, such a cap would give at most

```text
2079*50=103950
```

oriented incidences, contradicting (4).

The cap is a target for future work. It is not proved here.

## 4. Exact fixed-cycle partition

Normalize a four-cycle with same-sign diagonals `P={p1,p2}` and
`N={n1,n2}`. No outside vertex can meet both `P` anchors or both `N`
anchors, because each nonedge already has its two opposite anchors as all
common neighbors.

Each of the four cycle edges has one distinct external common neighbor.
The remaining outside vertices split exactly as

```text
51 adjacent to no anchor,
20 adjacent to one P anchor only,
20 adjacent to one N anchor only,
4 adjacent to one P and one N anchor.
```

For an `h=0` support of side size `s=7,8,9`, the remaining vertices on one
sign side must include four vertices adjacent to one opposite anchor and
respectively `1,2,3` vertices adjacent to neither anchor. This is the
starting domain for a local cap proof by exact extension, finite-field
coding, or a rooted flag/SDP inequality.

## 5. Boundary

This package proves a reduction, not the local cap. It does not exclude rank
28 or resolve Conway-99. Literature novelty remains `UNKNOWN`.
