# Wave 195 proof A: a Hilton--Milner flag-diversity bound

## Verdict

`DERIVED_PENDING_INDEPENDENT_VERIFICATION`.

Under the frozen conditional prism-free rank-11 endpoint assumptions,

```text
Q>=6980,
```

where `Q` is the number of projective short circuits cross-realizing at
least one graph nonedge.

The proof converts every selected or raw exact-three companion pair into a
three-subset of the seven graph triangles through its flag center. Dual
distance makes the local three-subset family intersecting. Hilton--Milner
then controls a family with no common star block; `k=14` and `lambda=1`
control a family with a common star block. The resulting oriented-label
diversity row combines exactly with the verified Wave194 inequalities.

No graph, code, cover, SAT, LP, configuration, enumeration, or isomorphism
search is used.

```yaml
role: proof_a
date_utc: 2026-07-29T03:36:17Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Conditional prism-free rank-11 endpoint: map all selected and raw
  exact-three flags to local intersecting three-subset families, derive
  an oriented-label Hilton--Milner slack, combine it with the independently
  verified Wave194 rows, and prove Q>=6980.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave174-no-weight3-dual/package-manifest.sha256: ac34c8a3b045bec70e3a2080cb4365c0ea43cc732b313ecb3cec355a28f23450
  verification/wave180-capacity3-companion/package-manifest.sha256: 28788edf010292a2c17763a744dfcf1a90a6343c5f72981e82e1aeb5853b7bc5
  verification/wave186-star-translation-cover-verifier/package-manifest.sha256: edb833cbed8706f164199d4ecab8ff26757c54dfc46915819e150e17d73fef76
  verification/wave189-degree7-star-orbit-verifier/package-manifest.sha256: fc17484bd8c32a5886ecdcc65d153903cef5f3b60a3de1c9905ed96697c273c4
  verification/wave191-exact-three-residual-verifier/package-manifest.sha256: a14f43310fb5ead05c4bd50b376f3d9d90ec77a92bc00f8c3b7326013f975ab2
  verification/wave194-five-thirds-verifier/package-manifest.sha256: 236facbec2539a87e197fd0b2b8ca66bc0d53b12415fdf216acf410064d7ca64
method: >-
  Canonical flag geometry, ternary relation cancellation, dual-distance
  rigidity, local lambda-one incidence counting, the Hilton--Milner
  theorem, oriented-label diversity, and an exact rational dual
  certificate. No graph, code, cover, SAT, LP, configuration, enumeration,
  or isomorphism search.
command: >-
  .\.venv\Scripts\python.exe -B
  attempts\wave195-leaf-packet-intersection-proof-a\exact_check.py --verify
  attempts\wave195-leaf-packet-intersection-proof-a\exact-results.json;
  .\.venv\Scripts\python.exe -B -m unittest -v
  attempts\wave195-leaf-packet-intersection-proof-a\test_exact_check.py
outputs:
  - agents/2026-07-29-wave195-leaf-packet-intersection-proof-a.md
  - attempts/wave195-leaf-packet-intersection-proof-a/
limitations:
  - This is a proof-agent derivation, not verifier promotion.
  - It is conditional on the frozen prism-free rank-11 endpoint and the
    independently verified Wave194 bookkeeping and separation theorems.
  - The Hilton--Milner theorem is cited with its exact hypotheses and
    specialization; its original 1967 proof is not reproduced.
  - No endpoint graph, code, cover, flag system, or circuit family is
    constructed.
  - The rational null row is arithmetic only and is not an object.
  - Rank 11, endpoint existence, strict original n3 improvement, external
    novelty, and Conway-99 remain UNKNOWN.
```

## 1. Frozen Wave194 bookkeeping

Retain the verified Wave194 variables and raw identities

```text
a1+a2+a3=n1,
b1+b3=2*p2,
c1+c2=p3,
r1=a1+b1+c1.                                    (1)
```

Here `n_i` counts selected circuits of private-label multiplicity `i`;
`p_i` counts raw assignments from selected type-two/type-three sources;
`a_i,b_i,c_i` split raw assignments from selected type-one, type-two, and
type-three sources by the exact multiplicity of their target circuit;
`r_i,h,y,g,W` are the verified old and residual pool counts.

The selected-incidence and certified circuit counts are

```text
I =2*n1+2*n2+3*n3+p2+p3,
Q0=n1+n2+2*n3+r1+r2+2*h+y+2*g+W.                (2)
```

Wave194 proves that all terms in `Q0` count distinct nonedge-realizing
projective short circuits, so

```text
Q>=Q0.                                           (3)
```

It also verifies the following nonnegative slacks:

```text
SI =I-2*C,
S2 =p2-n2,
SE2=2*r2-a2-c2,
RA =3*h+y+3*g-a2-a3-2*b3-c2,
SL =n1+2*n2+c1+2*r2+y+2*W-C.                   (4)
```

The new work is one additional nonnegative slack.

## 2. Exact-three flags give simple intersecting families

There are

```text
F=n3+h                                             (5)
```

distinct exact-three companion-pair flags: one for every selected
exact-three member and one for every old raw exact-three pair. The verified
pool separation prevents a selected pair from being reused as a raw pair.

Wave180 identifies each pair with a canonical flag

```text
(x,T={y,u,v}),  x anticomplete to T,
```

where `T` is a graph triangle. Let `S_x` be the seven graph-triangle
blocks through `x`. The flag determines a three-subset

```text
A_x(T) subset S_x,  |A_x(T)|=3,
```

consisting of the `x`-star blocks having exactly two cross edges to `T`.
Its weight-four member is the true relation

```text
z_T+2*sum_(S in A_x(T)) z_S=0.                  (6)
```

Fix `x`. The map `T -> A_x(T)` is injective. Equal `A`-sets for distinct
leaf triangles would subtract in (6) to

```text
z_T-z_T'=0,
```

a forbidden weight-two relation. Distinct exact-three flags cannot have
the same `(x,T)` by the canonical companion uniqueness. Thus the local
family

```text
F_x={A_x(T): (x,T) is one of the F flags}
```

is an ordinary set family. Write

```text
c_x=|F_x|.
```

It is also pairwise intersecting. If `A,A'` were disjoint, they would use
six of the seven blocks in `S_x`; call the last block `L`. Adding their
two relations (6) to the full star relation

```text
sum_(S in S_x) z_S=0
```

over `F_3` gives

```text
z_T+z_T'+z_L=0.                                 (7)
```

The three block columns are distinct, so (7) is a forbidden weight-three
relation. Both contradictions use only the independently verified dual
distance at least four.

## 3. Local Hilton--Milner versus common-star diversity

Let `j_x` be the number of distinct oriented labels `x -> y` occurring
among the flags centered at `x`. Equivalently, `j_x` is the number of
distinct leaf vertices in their leaf triangles.

There are two cases.

### Nontrivial intersecting family

We use the exact classical Hilton--Milner theorem:

> If `n>2k` and `F` is a pairwise-intersecting family of `k`-subsets of
> an `n`-set with empty total intersection, then
>
> ```text
> |F|<=C(n-1,k-1)-C(n-k-1,k-1)+1.
> ```

For `(n,k)=(7,3)`,

```text
c_x<=C(6,2)-C(3,2)+1=13,
j_x<=3*c_x<=39.                                 (8)
```

The source is A. J. W. Hilton and E. C. Milner, *Some Intersection
Theorems for Systems of Finite Sets*, Quarterly Journal of Mathematics
18 (1967), 369--384, DOI `10.1093/qmath/18.1.369`.

### Common-star family

Suppose instead that all members of `F_x` contain one common star block

```text
S={x,p,q}.
```

For every flag `(x,T)` in the family, `S in A_x(T)` means exactly two
edges run from `S` to `T`. Since `x` is anticomplete to `T`, the edges
start at `p,q`. Neither endpoint can have two neighbors in `T`: if `p`
were adjacent to two vertices of the graph triangle `T`, their edge would
have both `p` and the third vertex of `T` as common neighbors, contrary to
`lambda=1`. Thus each flag contributes exactly one `p`-neighbor and one
`q`-neighbor in `T`. They are distinct: a common neighbor of `p,q` in
`T`, together with `x`, would give the edge `pq` two common neighbors.

Across the whole family there are at most 12 distinct `p`-neighbors and,
symmetrically, at most 12 distinct `q`-neighbors. Every leaf triangle has
one remaining third vertex. Simplicity also gives

```text
c_x<=C(6,2)=15,
```

because there are only 15 three-subsets of a seven-set through a fixed
point. Therefore

```text
j_x<=12+12+c_x<=39.                             (9)
```

Thus both cases, including the empty family, satisfy the uniform local
union bound

```text
j_x<=39.                                        (10)
```

The unrestricted 13 in (8) is sharp: the 12 triples containing a fixed
point and meeting a fixed disjoint triple, together with that disjoint
triple, form the standard Hilton--Milner family. Thus the use of 13 is the
correct nontrivial stability threshold.

## 4. The global flag-diversity slack

Let

```text
J=sum_x j_x
```

be the number of distinct oriented center-to-leaf labels across all
exact-three flags. Summing (10) over the 99 possible centers gives

```text
J<=99*39=3861.                                  (11)
```

Now let `U` be the union of the labels on the selected exact-three
members. Every label outside `U` is a private label of a selected type-one
or type-two member, so the verified cover accounting gives

```text
|U|>=C-n1-2*n2.                                 (12)
```

Every label in `U` supplies at least one oriented label counted by `J`.
In addition, the `a3+b3` raw exact-three assignments come from distinct
private source labels outside `U`. Type-one sources contribute one raw
orientation. A type-two source has two raw translates for the same
undirected private nonedge, one in each endpoint direction; when both are
exact three, they are the two opposite oriented labels. Private nonedges
are distinct across selected sources, and opposite orientations are
distinct within a type-two source. Within a canonical exact-three flag, a
realized nonedge has only its center-to-leaf orientation. Thus the
`a3+b3` assignments give `a3+b3` distinct oriented labels, even when
several assignments land in the same one of the `h` raw exact-three pairs,
and none can collide with the labels supplied by `U`.
Hence

```text
J>=|U|+a3+b3
 >=C-n1-2*n2+a3+b3.                             (13)
```

Combining (11)--(13) proves the new nonnegative slack

```text
SG=3861-C+n1+2*n2-a3-b3>=0.                    (14)
```

This is a theorem about distinct oriented labels, not a count with
multiplicity.

## 5. Exact rational certificate

After substituting the four raw identities (1), direct coefficient
comparison gives

```text
Q0-(11*C-3861)/6

 =(2/3)*SI
  +(4/3)*S2
  +(1/6)*SE2
  +(2/3)*RA
  +(1/3)*SL
  +(1/6)*SG
  +a1/6+b3/2+c2/6+W/3.                         (15)
```

Every term on the right is nonnegative by (4), (14), and variable
nonnegativity. Therefore

```text
Q>=Q0>=(11*C-3861)/6.                           (16)
```

At `C=4158`,

```text
(11*C-3861)/6=13959/2=6979.5.
```

Since `Q` is integral,

```text
Q>=6980.                                        (17)
```

Adding the 693 independently verified edge-isolated projective circuits
gives at least

```text
7673
```

projective short circuits in total, or 15,346 nonzero scalar circuit
words.

The exact checker expands (15) over `Q`, verifies every coefficient, and
replays a rational arithmetic null row with all six slacks zero:

```text
n2=p2=297/2,
n3=2673/2,
p3=c1=3861,
b1=297,
r1=4158,
all other split/pool variables zero.
```

It has `Q0=13959/2`. This row proves only scalar sharpness of the displayed
linear certificate; fractional counts are not a graph, cover, code, or
circuit system.

## 6. Direct exclusion of the old Wave194 equality face

The original requested equality analysis is a transparent corollary.
Wave194 equality has

```text
a3=n1=3*h,
p3=c1=r1=3*n3,
h+n3=C/3=1386,
all other split/pool variables zero.             (18)
```

The `n3` selected exact-three triples are disjoint. The `a3=3h` raw
assignments saturate every raw exact-three pair's three distinct label
slots with the `n1=3h` singleton source labels. Verified pool disjointness
separates the two orientations. Hence the `h+n3=1386` exact-three label
triples partition all 4,158 nonedges.

At a fixed center, their leaf triangles are therefore pairwise disjoint.
In the common-star case of Section 3, each flag then consumes a distinct
neighbor of `p`, so `c_x<=12`; in the nontrivial case Hilton--Milner gives
`c_x<=13`. Thus every center has `c_x<=13`, whereas

```text
1386=sum_x c_x<=99*13=1287,
```

a contradiction. Equivalently, substituting (18) into (14) gives

```text
SG=3861-4158=-297,
```

which is impossible.

This full-face argument requires no classification of the packet's three
exact-one circuit supports.

## Boundary

```text
canonical exact-three flag geometry:        VERIFIED input
local A-family simple/intersecting:          DERIVED
Hilton--Milner nontrivial cap:               13
common-star oriented-label row:              DERIVED
SG>=0:                                       DERIVED
exact certificate (15):                      exact replay PASS
Q>=6980:                                     DERIVED
independent Wave195 verification:            pending
rational null row is an object:              no
rank 11 / endpoint excluded:                 no
Conway-99 / external novelty:                UNKNOWN
```

The earlier attempted route through canonical exact-one leaf supports and
one-dimensional nonedge star-space intersections is not used: its
type-one orientation had an unresolved elimination collision. That gap is
preserved explicitly in the package's `failed-routes.md`.
