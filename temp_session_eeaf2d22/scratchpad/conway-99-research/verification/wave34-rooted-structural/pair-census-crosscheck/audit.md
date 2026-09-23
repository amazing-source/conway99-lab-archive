# Wave 34 rooted pair-census independent crosscheck

Date: 2026-07-24

Role: verifier

Verdict: `PASS`.

This audit is deliberately limited to the verifier-authored Stage 1 rooted
O-pair census and the duplicate-free single-`Pb`-column refinement cited by
Stage 2. It does not audit the rest of either structural verifier package.

No Wave 34 structural verifier script was imported or executed. The pair
census was reconstructed by direct triangular elimination from the frozen
Wave 33 block criterion. The column total was reconstructed by a
relative-permutation and weighted-permanent identity, not by the released
point/remaining-degree dynamic program.

## 1. Frozen inputs and notation

All ten files in `input-freeze.sha256` match. The complete Stage 1
precomparison manifest and the complete Stage 2 comparison manifest also
match their contents. No file outside `pair-census-crosscheck/` was changed.

Use the Stage 1 notation on the 70 O-vertices:

```text
F : fixed 14 x 70 support-to-O incidence
D : unknown symmetric hollow 9-regular O graph
B : unknown 70 x 15 O-Q incidence
T = F^T F
R = B B^T

g_ij = T_ij
r_ij = R_ij
h_ij = D_ij
c_ij = (D^2)_ij
```

For distinct O-vertices, the frozen O-O equation is

```text
g_ij + r_ij + h_ij + c_ij = 2.                   (1)
```

The frozen Wave 33 incidence has 28 support-edge columns and 42
support-nonedge-copy columns. Direct multiplication of its 14-by-70 matrix
gives:

```text
row degree of F                            10
column degree of F                          2

support-edge O row:       #g=1 = 18, #g=2 = 0
support-nonedge-copy row: #g=1 = 16, #g=2 = 1
```

The fixed S-O block independently gives

```text
diag(DT) = 0 on support-edge rows
diag(DT) = 2 on support-nonedge-copy rows.         (2)
```

## 2. The nine-state domain is complete

Equation (1), nonnegativity, `g,r in {0,1,2}`, and `h in {0,1}` leave
exactly:

```text
(g,r,h,c) =
(0,0,0,2), (0,0,1,1), (0,1,0,1), (0,1,1,0),
(0,2,0,0), (1,0,0,1), (1,0,1,0), (1,1,0,0),
(2,0,0,0).
```

There is no tenth nonnegative state.

For a row of the simple `2-(15,3,2)` B-design:

```text
#r=2 = 3
#r=1 = 33
#r=0 = 33.                                        (3)
```

Indeed, the three Q-pairs inside its triple each occur in one other block.
Those three blocks are distinct because the design has no repeated block.
The total off-diagonal intersection multiplicity is
`3*(14-1)=39`, giving `#r=1+2#r=2=39`.

The other row constraints are:

```text
#h=1                  = 9
sum c_ij              = 9*8 = 72
sum h_ij g_ij         = diag(DT) = 0 or 2
sum h_ij r_ij         = diag(DR) = 3
sum g_ij r_ij         = diag(TR)-T_ii R_ii
                         = 12-2*3 = 6.             (4)
```

Because of the nine-state support, equations (2)-(4) solve in a triangular
nine-pivot order:

```text
g2, r2, hg, hr, gr, remaining r1,
remaining g1, remaining h1, remaining r0.
```

No generic solver or copied 9-by-9 matrix is used.

The unique row distributions reproduce exactly:

| `(g,r,h,c)` | support-edge row | support-nonedge-copy row |
|---|---:|---:|
| `(0,0,0,2)` | 15 | 18 |
| `(0,0,1,1)` | 6 | 4 |
| `(0,1,0,1)` | 24 | 24 |
| `(0,1,1,0)` | 3 | 3 |
| `(0,2,0,0)` | 3 | 3 |
| `(1,0,0,1)` | 12 | 8 |
| `(1,0,1,0)` | 0 | 2 |
| `(1,1,0,0)` | 6 | 6 |
| `(2,0,0,0)` | 0 | 1 |

Aggregating 28 rows of the first type and 42 of the second, then dividing
ordered counts by two, gives:

| state | unordered pairs |
|---|---:|
| `(0,0,0,2)` | 588 |
| `(0,0,1,1)` | 168 |
| `(0,1,0,1)` | 840 |
| `(0,1,1,0)` | 105 |
| `(0,2,0,0)` | 105 |
| `(1,0,0,1)` | 336 |
| `(1,0,1,0)` | 42 |
| `(1,1,0,0)` | 210 |
| `(2,0,0,0)` | 21 |

The total is `2415=C(70,2)`.

## 3. Duplicate-pair and X11 consequences

If `g=2`, equation (1) immediately forces

```text
r=h=c=0.
```

The 42 duplicated support-label O-vertices therefore form 21 fixed twin
pairs in state `(2,0,0,0)`. Each pair has disjoint B rows (`r=0`), is
nonadjacent in D (`h=0`), and has no common O-neighbour (`c=0`). The
duplicate pairs form a fixed matching on those 42 vertices.

The state `(1,1,0,0)` occurs six times in every row. Its relation graph
`X11` is consequently:

```text
vertices: 70
degree:    6
edges:   210
```

Its `h=0` coordinate makes it edge-disjoint from D. Its `c=0` coordinate
makes it disjoint from the off-diagonal support of `D^2`. These are labeled,
unrestricted consequences; no orbit or automorphism assumption is used.

## 4. Structurally different Pb-column enumeration

The frozen support incidence is the vertex-edge incidence of a bipartite
multigraph on seven point vertices and seven line vertices. Its 7-by-7 edge
capacity matrix has:

```text
21 entries of capacity 2
28 entries of capacity 1
every row and column of total capacity 10.
```

A binary column satisfying `Pb=2*1` selects a spanning 2-factor of this
multigraph.

The crosscheck counts these factors through ordered alternating perfect
matchings. Let `alpha` be the first matching and let a permutation `pi` on
the seven point vertices define the second by

```text
beta(p) = alpha(pi(p)).
```

The cycles of `pi` are exactly the half-cycle lengths of the bipartite
2-factor. For fixed `pi`, the weighted sum over all `alpha` is a 7-by-7
permanent:

```text
W_pi(q,l) = m(q,l) m(pi^-1(q),l)       if pi(q) != q,
W_pi(q,l) = 2                           if pi(q)=q and m(q,l)=2,
W_pi(q,l) = 0                           otherwise.
```

Here `m(q,l)` is the frozen edge capacity. The fixed-point value two records
the two ordered allocations of the two parallel copies. A factor with `k`
cycles has exactly `2^k` ordered alternating decompositions, so its class
count is

```text
sum_pi permanent(W_pi) / 2^k,
```

with the sum taken over the relevant cycle type. All `7!=5040` relative
permutations are evaluated exactly. Every class numerator is divisible by
the required `2^k`.

This independently reproduces the complete labeled census:

```text
underlying capacity-bounded 2-factors       4,946,952
all labeled Pb=2*1 columns                574,118,037
```

The duplicate-pair rule forbids using both parallel copies of an edge.
Equivalently, it forbids fixed points of `pi`, or half-cycle type `1`.
The remaining partitions of seven are exactly:

| half-cycle type | labeled columns |
|---|---:|
| `7` | 262,332,336 |
| `5+2` | 91,117,740 |
| `4+3` | 76,574,904 |
| `3+2+2` | 18,854,388 |

Their sum is

```text
448,879,368.
```

The eleven types containing a `1` contribute

```text
125,238,669,
```

and `448,879,368+125,238,669=574,118,037`.

## 5. Hostile checks

The independent suite includes:

1. exact validation of both frozen structural manifests without importing or
   executing their scripts;
2. reconstruction of the `g` profiles and `diag(DT)` directly from the
   frozen Wave 33 matrices;
3. a hostile change of the duplicate-row `diag(DT)` value from two to one,
   which changes the unique row census;
4. permanent controls on the identity, all-ones, and zero-row matrices;
5. cycle-type controls for a 7-cycle and a `3+2+2` permutation;
6. divisibility checks for every alternating-decomposition class; and
7. deliberate reintroduction of half-cycle type `1`, recovering exactly the
   125,238,669 columns excluded by the duplicate-pair rule.

All 24 tests pass.

## 6. Scope wall

The exact count `448,879,368` is a necessary single-column domain only. It
does not count compatible 15-column B-designs. It does not impose all
pairwise column intersections, D, `D^2`, the projector equations, or binary
compatibility with the remaining blocks.

Final statuses:

```text
pair-state census:                       VERIFIED_SCOPED
duplicate-pair rule:                     VERIFIED_SCOPED
X11 6-regular 210-edge relation:         VERIFIED_SCOPED
duplicate-free Pb-column total:          VERIFIED_SCOPED

compatible 15-column design:             UNKNOWN
binary (D,B) solution:                    UNKNOWN
rooted graph extension or exclusion:     UNKNOWN
rooted endpoint:                          UNKNOWN
n3=708:                                  UNKNOWN
Conway-99:                               UNKNOWN
novelty:                                 UNKNOWN
```

No discrepancy was found in the four claims assigned for cross-verification.
