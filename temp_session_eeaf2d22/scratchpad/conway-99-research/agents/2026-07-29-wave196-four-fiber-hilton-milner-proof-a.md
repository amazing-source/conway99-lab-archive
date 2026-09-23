# Wave 196 proof A: four-fiber Hilton--Milner rigidity

## Verdict

`DERIVED_PENDING_INDEPENDENT_VERIFICATION`.

Under the frozen conditional prism-free rank-11 endpoint assumptions,

```text
Q>=7029,
```

where `Q` is the number of projective short circuits cross-realizing at
least one graph nonedge.

Wave195 bounded the oriented exact-three label union at each center by 39.
The present proof uses the four-element fibers of the local nonedge
geometry to improve that bound to 36:

```text
j_x<=36 for every graph vertex x.
```

This yields a new global slack and an exact rational certificate. No
graph, code, cover, SAT, LP, configuration, enumeration, or isomorphism
search is used.

```yaml
role: proof_a
date_utc: 2026-07-29T04:47:00Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Conditional prism-free rank-11 endpoint: refine the local
  Hilton--Milner exact-three flag bound using the four-element
  two-star-block fibers, derive J<=3564 and the new global slack, and
  prove Q>=7029 by an exact rational certificate.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave174-no-weight3-dual/package-manifest.sha256: ac34c8a3b045bec70e3a2080cb4365c0ea43cc732b313ecb3cec355a28f23450
  verification/wave180-capacity3-companion/package-manifest.sha256: 28788edf010292a2c17763a744dfcf1a90a6343c5f72981e82e1aeb5853b7bc5
  verification/wave186-star-translation-cover-verifier/package-manifest.sha256: edb833cbed8706f164199d4ecab8ff26757c54dfc46915819e150e17d73fef76
  verification/wave189-degree7-star-orbit-verifier/package-manifest.sha256: fc17484bd8c32a5886ecdcc65d153903cef5f3b60a3de1c9905ed96697c273c4
  verification/wave191-exact-three-residual-verifier/package-manifest.sha256: a14f43310fb5ead05c4bd50b376f3d9d90ec77a92bc00f8c3b7326013f975ab2
  verification/wave194-five-thirds-verifier/package-manifest.sha256: 236facbec2539a87e197fd0b2b8ca66bc0d53b12415fdf216acf410064d7ca64
method: >-
  SRG local matching geometry, four-element two-block fibers, canonical
  exact-three flags, ternary dual-distance cancellation, the
  Hilton--Milner equality classification for 3-subsets of a 7-set,
  oriented-label counting, and an exact rational dual certificate. No
  graph, code, cover, SAT, LP, configuration, enumeration, or
  isomorphism search.
command: >-
  .\.venv\Scripts\python.exe -B
  attempts\wave196-four-fiber-hilton-milner-proof-a\exact_check.py --verify
  attempts\wave196-four-fiber-hilton-milner-proof-a\exact-results.json;
  .\.venv\Scripts\python.exe -B -m unittest -v
  attempts\wave196-four-fiber-hilton-milner-proof-a\test_exact_check.py
outputs:
  - agents/2026-07-29-wave196-four-fiber-hilton-milner-proof-a.md
  - attempts/wave196-four-fiber-hilton-milner-proof-a/
limitations:
  - This is a proof-agent derivation, not verifier promotion.
  - It is conditional on the frozen prism-free rank-11 endpoint and the
    independently verified Wave194 bookkeeping and pool separation.
  - The Hilton--Milner theorem and its k=3 equality classification are
    cited; their original proof is not reproduced.
  - No endpoint graph, code, cover, flag system, or circuit family is
    constructed.
  - The exact integer null row is arithmetic only and is not an object.
  - Rank 11, endpoint existence, strict original n3 improvement, external
    novelty, and Conway-99 remain UNKNOWN.
```

## 1. The full exact-three flag pool

Use the verified Wave194 variables and raw identities

```text
a1+a2+a3=n1,
b1+b3=2*p2,
c1+c2=p3,
r1=a1+b1+c1.                                    (1)
```

The selected-incidence and certified circuit counts are

```text
I =2*n1+2*n2+3*n3+p2+p3,
Q0=n1+n2+2*n3+r1+r2+2*h+y+2*g+W.                (2)
```

The selected exact-three members, the `h` old raw exact-three companion
pairs, and the `g` genuinely new residual exact-three companion pairs are
pairwise separated by the verified pool construction. They therefore
give

```text
F=n3+h+g                                           (3)
```

distinct canonical exact-three flags.

For each graph vertex `x`, let `F_x` be the flags centered at `x`, let
`c_x=|F_x|`, and let `j_x` be the number of distinct oriented nonedges
`x -> y` appearing as their center-to-leaf labels. Put

```text
J=sum_x j_x.
```

## 2. The four-element two-star-block fibers

Fix `x`. The graph induced by its 14 neighbors is a matching of seven
edges. Indeed, every neighbor of `x` has exactly `lambda=1` neighbor in
`N(x)`, namely its partner in the unique graph triangle through the edge
to `x`. Denote the seven triangle blocks through `x` by

```text
S_1,...,S_7.
```

For every nonneighbor `y` of `x`, the common-neighbor set

```text
N(x) intersect N(y)
```

has size `mu=2`. Its two vertices lie in distinct matching edges. If they
were adjacent, their graph edge would have both `x` and `y` as common
neighbors, contradicting `lambda=1`. Define the two-block type

```text
P_x(y)={S_i,S_j}.
```

Every type `{S_i,S_j}` has exactly four vertices. To see this, choose one
endpoint from each of the two matching edges. The four endpoint pairs are
graph nonedges because there are no edges between distinct matching
edges. Each pair has exactly two common neighbors: `x` and one further
vertex `y`. That further vertex is not adjacent to `x`, and different
endpoint pairs give different `y` because a nonneighbor of `x` has only
two common neighbors with `x`. Thus

```text
|{y: P_x(y)={S_i,S_j}}|=4.                      (4)
```

These 21 fibers partition the 84 nonneighbors of `x`.

## 3. A flag is a triangle of fiber types

Wave180 identifies an exact-three pair centered at `x` with a flag

```text
(x,T={y,u,v}),
```

where `T` is a graph triangle anticomplete to `x`. Its weight-four
relation is

```text
z_T+2*sum_(S in A_x(T)) z_S=0,  |A_x(T)|=3.     (5)
```

The six incidences from `N(x)` to `T` are all distinct. No neighbor of
`x` can meet two vertices of `T`, because their graph edge would then
have both that neighbor and the third vertex of `T` as common neighbors.
The three blocks in `A_x(T)` each contain two of the six incidences.
Consequently, if

```text
A_x(T)={S_i,S_j,S_k},
```

then, in some order,

```text
P_x(y)={S_i,S_j},
P_x(u)={S_i,S_k},
P_x(v)={S_j,S_k}.                               (6)
```

Thus every flag whose `A`-set contains a fixed pair `{S_i,S_j}` uses one
leaf vertex from the corresponding four-element fiber (4).

As in Wave195, the local family

```text
A_x={A_x(T):(x,T) in F_x}
```

is simple and intersecting:

- equal `A`-sets for distinct `T,T'` subtract in (5) to the forbidden
  weight-two relation `z_T-z_T'=0`; and
- disjoint `A,A'`, together with the unused seventh star block and the
  full `x`-star relation, give a forbidden weight-three relation.

Both exclusions use the independently verified dual distance at least
four.

## 4. Nontrivial local families have at most 36 leaf labels

Suppose `A_x` has empty total intersection. Hilton--Milner gives

```text
c_x<=13.                                         (7)
```

If `c_x<=12`, then immediately

```text
j_x<=3*c_x<=36.
```

It remains to treat `c_x=13`. The `k=3` equality classification in the
Hilton--Milner theorem has exactly two isomorphism types. This is stated
explicitly as Theorem 11 in the frozen Hurlbert--Kamat readable proof:

```text
H:
  {X} union { {s} union E :
              E is a 2-subset of the other six points,
              E intersects X },
  where |X|=3 and s is outside X;

K:
  { A : |A intersect X|>=2 },
  where |X|=3.
```

In `H`, each of the three pairs `{s,t}` with `t in X` belongs to five
members. In `K`, each of the three pairs contained in `X` belongs to five
members. Thus either equality family has three distinct block-pairs of
degree five.

By (4)--(6), the five flags through any one of those pairs draw leaf
vertices from a fiber containing only four vertices. Each of the three
distinct fibers therefore causes at least one repeated leaf occurrence.
There are `3*13=39` leaf occurrences in total, so

```text
j_x<=39-3=36.                                    (8)
```

## 5. A common-star family has at most twelve flags

Now suppose all members of `A_x` contain a common star block

```text
S_0={x,p,q}.
```

For a flag `(x,T)` in the family, `S_0 in A_x(T)` means that `T` contains
exactly one neighbor `y` of `p` and one neighbor `z` of `q`. They are
distinct: a vertex adjacent to both `p,q`, together with `x`, would give
the edge `pq` two common neighbors.

The flag is uniquely determined by its `p`-neighbor `y`:

1. `yq` is a graph nonedge. Its two common neighbors are `p` and the
   `q`-neighbor `z` in `T`, so `mu=2` determines `z` uniquely.
2. The edge `yz` has the third vertex of `T` as its common neighbor, so
   `lambda=1` determines that vertex uniquely.

There are only

```text
14-2=12
```

possible choices for `y`, since the known neighbors `x,q` of `p` cannot
belong to a leaf triangle anticomplete to `x`. Distinct flags have
distinct leaf triangles by the canonical uniqueness in Section 3.
Therefore

```text
c_x<=12,
j_x<=3*c_x<=36.                                  (9)
```

Equations (8)--(9) prove the universal local theorem

```text
c_x<=13 and j_x<=36 for every x.                (10)
```

## 6. Global slack and exact certificate

Summing (10) over all 99 centers gives both

```text
F=sum_x c_x<=99*13=1287,
J<=99*36=3564.                                  (11)
```

Let `U` be the union of labels on selected exact-three members. The
verified cover accounting gives

```text
|U|>=C-n1-2*n2.
```

Every label in `U` supplies an oriented label in the full flag pool. The
`a3+b3` old raw exact-three assignments add distinct oriented private
labels outside `U`: type one supplies one orientation, while the two raw
translates of one type-two private nonedge supply its two opposite
orientations. Hence

```text
J>=C-n1-2*n2+a3+b3.
```

Together with (11), this proves the new nonnegative slack

```text
S36=3564-C+n1+2*n2-a3-b3>=0.                   (12)
```

Retain the independently verified Wave194 slacks

```text
SI =I-2*C,
S2 =p2-n2,
SE2=2*r2-a2-c2,
RA =3*h+y+3*g-a2-a3-2*b3-c2,
SL =n1+2*n2+c1+2*r2+y+2*W-C.                  (13)
```

After substituting (1), exact coefficient comparison gives

```text
Q0-(11*C-3564)/6

 =(2/3)*SI
  +(4/3)*S2
  +(1/6)*SE2
  +(2/3)*RA
  +(1/3)*SL
  +(1/6)*S36
  +a1/6+b3/2+c2/6+W/3.                         (14)
```

All terms on the right are nonnegative. Since the Wave194 pool separation
proves `Q>=Q0`,

```text
Q>=(11*C-3564)/6.
```

For `C=4158`,

```text
(11*C-3564)/6=7029,
```

and therefore

```text
Q>=7029.                                        (15)
```

Adding the 693 independently verified edge-isolated projective circuits
gives at least 7,722 projective short circuits in total, or 15,444
nonzero scalar circuit words.

The certificate is scalar-sharp on the integer arithmetic row

```text
n2=p2=297,
n3=1287,
p3=c1=3564,
b1=594,
r1=4158,
all other split/pool variables zero.
```

Every displayed slack vanishes and `Q0=7029`. This row is not a graph,
cover, code, flag system, or circuit construction.

## Boundary

```text
four vertices in every two-block fiber:       DERIVED
flag fiber-triangle rule:                     DERIVED
Hilton--Milner equality templates:            CITED
nontrivial local cap j_x<=36:                 DERIVED
common-star local cap c_x<=12:                DERIVED
F<=1287, J<=3564, and S36>=0:                  DERIVED
exact certificate (14):                       exact replay PASS
Q>=7029:                                       DERIVED
independent Wave196 verification:             pending
arithmetic null row is an object:              no
rank 11 / endpoint excluded:                  no
Conway-99 / external novelty:                 UNKNOWN
```
