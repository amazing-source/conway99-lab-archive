# Wave 34 rootless global overlap: clean-room Stage 1 derivation

```yaml
role: verifier
date_utc: 2026-07-24T20:52:23Z
git_commit: 0fa5b8161baf8b2a5404a67051b7d61cbc906da3
claim_label: DERIVED
scope: >-
  Clean-room necessary consequences of actual vertex-triangle incidence,
  the rank-44 projector Gram M, n3=708, and the rootless mixed-trace-zero
  premise. The four formal Wave 33 R2-board candidates are reduced to at
  most one globally compatible closure per R2 pair; exact fibre holonomy,
  local matching, projector-codegree, and global R0-overlap constraints are
  derived. No motif-forcing contradiction or endpoint construction is obtained.
inputs:
  verification/wave34-rootless-global/precomparison/input-freeze.sha256: cfbcb169878e4616af213e22e6b79dfe749025f12134666eda13c976e8f691f7
method: >-
  Exact one-leg incidence transport; triangle-centred 12-point fibre
  normalization; permutation holonomy; three perfect-matching overlap
  arithmetic; exact Gram Schur complements; integer determinant checks;
  endpoint double counts; and hostile local controls.
command: >-
  python -B -m unittest discover -s
  verification/wave34-rootless-global/precomparison -p test_*.py -v
outputs:
  verification/wave34-rootless-global/precomparison/results.json: 450f01d15b8eaaad2ca7e9f8114c028b96f06bdf4b3944dc69e70525931ec8f9
  verification/wave34-rootless-global/precomparison/independent_check.py: cab9b140a8b64d6bfdfd070ac8a31c1683af21ecf58d71cca608235e902daa6f
  verification/wave34-rootless-global/precomparison/test_independent_check.py: 6268ff04ce8dac6b61b6b5c68a394e39430126e4f4a98622f44340c02e411095
limitations:
  - The fibre controls are local matching systems, not target graphs.
  - The sharp scalar endpoint profile is not a globally compatible q-profile certificate.
  - The codegree and four-cycle bounds are necessary and remain numerically feasible.
  - No Wave 34 discovery artifact was inspected before this Stage 1 freeze.
  - Actual motif forcing, the rootless endpoint, n3=708, Conway-99, and novelty remain UNKNOWN.
```

The `git_commit` field records the public base frozen by the continuation
protocol. Git was not queried or used in this task.

## Result

Under the frozen conditional endpoint premises, let `H=A_R3` be the graph on
the 231 graph triangles whose edges join disjoint triangles with three cross
edges. The strongest clean-room conclusions are:

```text
one-leg labelled incidence transport K=NM:              DERIVED
triangle-centred holonomy and q != 1:                   DERIVED
deg_R2(T)=3q(T), deg_R3(T)=12-q(T):                     DERIVED
Wave 33 four candidates / actual closures per R2 pair:  at most 1
projector common-R3 caps for R0,R1,R2,R3 pairs:         5,3,1,1
actual-incidence caps for Gamma,R0,R1,R2,R3 pairs:      0,5,1,1,1
rootless local normalization:                           no double matching edge
sum of R0-centred H-wedges at n3=708:                   at least 6860
R0 pairs with H-codegree at least 1,2,3:                at least 1372,1079,590
four-cycles in H at n3=708:                             at least 3041
actual motif forcing:                                   UNKNOWN
```

The global overlap bounds do not by themselves use rootlessness; rootlessness
adds the exclusion of the local double-matching edge and sets every `R2`
codegree to zero. Thus Stage 1 strictly shrinks the actual-incidence domain,
but it does not close it.

## Frozen assumptions and notation

The imported verified identities are

```text
N N^T = 7I+A,
N^T N = 3I+Gamma,
M=21E_0,
M^2=21M,
M_TT=4.
```

Here `E_0` is the projector onto the `Gamma=0` eigenspace. For distinct
triangles,

```text
M_TU = 0                         if T,U intersect,
M_TU = 1-r(T,U)                  if T,U are disjoint,
```

so the values on `R0,R1,R2,R3` are `1,0,-1,-2`. At `n3=708`,

```text
sum_T q(T)=472,
unordered pair counts:
Gamma=2079, R0=2546, R1=20082, R2=708, R3=1150.
```

The rootless endpoint premise is

```text
tr(A_R2 A_R3^2)=0.                                      (1)
```

Every count used below is for actual graph triangles, not a formal relation
table.

## Lemma 1: exact one-leg labelled incidence transport

Let

```text
K=NM.
```

The intertwining `AN=N(Gamma-4I)` sends the `Gamma=0` space to the graph
`A=-4` space. With

```text
P_-4=(27I-9A+J)/63,
```

one obtains

```text
K=21P_-4 N
 =9N-3AN+J.                                             (2)
```

For a graph vertex `x` and graph triangle `T`, an outside vertex is adjacent
to at most one vertex of `T`. Equation (2) therefore gives

```text
K_xT =
 4   if x is in T,
-2   if x is outside T and adjacent to one vertex of T,
 1   if x is outside T and adjacent to none of T.        (3)
```

Each column has the exact census

```text
4^3, (-2)^36, 1^60.
```

Unlike `N^T p(A)N`, (2) retains the graph-vertex label. Its exact Gram
identities are

```text
K^T K=63M,
K K^T=21(27I-9A+J).                                    (4)
```

Thus the projector vectors can be represented by the explicit labelled
columns `K_T/sqrt(63)`. This is the bridge used in the local PSD checks; it
does not contract the vertex leg back to `Q[Gamma]`.

## Lemma 2: the 12-point fibre holonomy

Fix a graph triangle

```text
T={t0,t1,t2}.
```

For `i=0,1,2`, let `F_i` be the outside vertices adjacent to `t_i`, and let
`Z` be the vertices adjacent to none of `T`. Then

```text
|F_0|=|F_1|=|F_2|=12,   |Z|=60.                        (5)
```

There are two exact matching structures.

1. `G[F_i]=6K2`. This is the part of `G[N(t_i)]=7K2` left after deleting
   the edge on the other two vertices of `T`.
2. Between every two distinct fibres `F_i,F_j`, the edges form a perfect
   matching. For `x in F_i`, the nonedge `x,t_j` has the two common
   neighbours `t_i` and one unique vertex of `F_j`.

Normalize labels so that

```text
F_0={a_i}, F_1={b_i}, F_2={c_i},  i in {0,...,11},
a_i-b_i and a_i-c_i are edges,
b_i-c_{pi(i)} is an edge.                              (6)
```

The third cross-fibre matching is a permutation `pi` of twelve labels.
A triangle in relation `R3` with `T` must be

```text
V_i={a_i,b_i,c_i},
```

and it exists exactly when `pi(i)=i`. If `i` is not fixed, each of the three
cross-fibre edges indexed by `i` closes through a vertex of `Z` and gives one
distinct `R2` triangle. Consequently, with

```text
q(T)=12-|Fix(pi)|,
```

the exact degrees are

```text
deg_R3(T)=12-q(T),
deg_R2(T)=3q(T).                                       (7)
```

A permutation cannot move exactly one point, so

```text
q(T) != 1,  equivalently deg_R3(T) != 11.              (8)
```

Every other value `q in {0,2,3,...,12}` occurs in an explicit local
permutation-and-matching control. These controls establish the exact local
domain only; they are not graph extensions.

At the endpoint, `sum q=472` is ten above the all-`q=2` total. Hence at
least one triangle has `q>=3` (and therefore `R3` degree at most nine), but
this observation alone gives no contradiction.

## Lemma 3: motif normalization by three same-fibre matchings

Let `alpha,beta,gamma` be the fixed-point-free involutions supplied by the
`6K2` matchings inside `F_0,F_1,F_2`. If `i,j` are two distinct fixed points
of `pi`, then `V_i,V_j` are disjoint and

```text
r(V_i,V_j)
 =1_{alpha(i)=j}+1_{beta(i)=j}+1_{gamma(i)=j}.          (9)
```

No cross-fibre edge can join two different fixed transversals, so (9) lists
all cross edges. It follows that:

- `R1`, `R2`, and `R3` among the `R3` neighbours of `T` mean that the pair
  is used by exactly one, two, or three of the same-fibre matchings;
- the forbidden `R2-R3-R3` motif centred at `T` is exactly a double edge
  among these three matchings;
- (1) is equivalent to the absence of every such double edge at every
  centre.

If `x_T,x_i` are projector-frame rows with Gram `M`, put

```text
y_i=x_i+x_T/2
```

for `i in Fix(pi)`. Then

```text
<y_i,y_i>=3,
<y_i,y_j>=-r(V_i,V_j).                                (10)
```

Hence the local projected Gram is

```text
3I-L_F,
```

where `L_F` is the sum of the three matching adjacencies restricted to the
fixed-point set `F`. Its positivity is exact:

```text
3I-L_F
 =sum_delta (I-A_delta)[F],  delta in {alpha,beta,gamma}, (11)
```

and each full matching block `I-A_delta` is a sum of squares
`(z_u-z_v)^2`. This explains why the local projector PSD condition does not
by itself contradict rootlessness: three pairwise edge-disjoint perfect
matchings give a zero-double-edge control for every permitted `q`.

## Lemma 4: projector caps every common-`R3` codegree

Take two frame rows `x,y` with norm four and inner product

```text
s in {1,0,-1,-2}.
```

Let `z_1,...,z_m` be common `R3` neighbours, so

```text
<x,z_i>=<y,z_i>=-2.
```

Project each `z_i` orthogonally off `span{x,y}`. The squared norm of its
projection onto the base span is

```text
p_s=8/(4+s).
```

The residual vectors have diagonal

```text
d_s=4-p_s
```

and, because every distinct endpoint Gram entry is at most one, pairwise
inner product at most

```text
c_s=1-p_s<0.
```

Therefore

```text
0 <= ||sum_i w_i||^2
   <= m d_s + m(m-1)c_s.                              (12)
```

Exact rational evaluation gives:

| base relation | `s` | `d_s` | `c_s` upper bound | common `R3` cap |
|---|---:|---:|---:|---:|
| `R0` | 1 | `12/5` | `-3/5` | 5 |
| `R1` or intersecting | 0 | 2 | -1 | 3 |
| `R2` | -1 | `4/3` | `-5/3` | 1 |
| `R3` | -2 | 0 | -3 | 1 |

In particular,

```text
c_H(T,U)<=1 for every R2 pair.                         (13)
```

Thus the four Wave 33 board selections cannot produce two distinct actual
common `R3` triangles under the projector package.

For an `R0` pair with five common `R3` neighbours, equality in (12) forces
all five common neighbours to be pairwise `R0` and gives the exact dependency

```text
2x+2y+z_1+...+z_5=0.                                  (14)
```

The exact Gram determinants for `m=0,...,6` are

```text
15,36,81,162,243,0,-2187.
```

The negative sixth determinant independently detects the cap.

## Lemma 5: actual incidence sharpens the caps and locates the unique candidate

Two distinct `R3` neighbours of any centre are fixed transversals with
different labels, so they are disjoint. Hence intersecting triangles have no
common `R3` triangle.

Now let `T,U` be disjoint with at least one cross edge, and choose a vertex
`u in U intersect F_i`. Among vertices belonging to `R3` triangles of `T`
that are disjoint from `U`, the only possible neighbour of `u` is its unique
same-fibre mate:

- its two cross-fibre matching neighbours belong to the transversal with
  the corresponding holonomy label;
- if `u` has a fixed label, that transversal contains `u` and is not
  disjoint from `U`;
- if `u` has a nonfixed label, permutation injectivity prevents either
  cross-fibre neighbour from lying in a different fixed transversal.

Therefore `u` can meet at most one eligible fixed transversal, giving

```text
c_H(T,U)<=1 for R1,R2,R3 pairs.                        (15)
```

For an `R0` pair, each vertex of `U` lies in `Z` and has exactly two
neighbours in each `F_i`, so incidence alone gives six; the projector cap
improves this to five. Combining all information:

| pair type | common `R3` cap |
|---|---:|
| intersecting | 0 |
| `R0` | 5 |
| `R1` | 1 |
| `R2` | 1 |
| `R3` | 1 |

For an `R2` pair normalized so that its two fibre vertices are `a_i,b_i`,
any common `R3` triangle must have the single label

```text
j=alpha(i)=beta(i) in Fix(pi),                         (16)
```

and its third vertex `c_j` must be adjacent to the `Z`-vertex of `U`.
Thus (16) identifies the only globally compatible member of the four-board
list. A local matching package attaining this index cap is included in the
result JSON; choosing the required `Z-c_j` edge would close the motif, so it
is not a rootless global object.

## Lemma 6: endpoint overlap is forced into `R0`

If a pair has two common `R3` neighbours, the cap table shows that the pair
must be `R0`. The two common neighbours themselves share the original pair
as two common `R3` neighbours, so they too must be `R0`. Consequently:

> Every pair with `H`-codegree at least two is an `R0` pair, and its full
> common-neighbour set is an `R0` clique.

For a centre `T`, put

```text
b_T=deg_H(T)=12-q(T).
```

Among the `binom(b_T,2)` pairs in `H(T)`, each non-`R0` pair consumes at
least one edge from the three same-fibre matchings. Each matching has at most
`floor(b_T/2)` edges internal to the fixed set. Hence the number `e_0(T)` of
`R0` pairs in `H(T)` satisfies

```text
e_0(T) >= g(b_T)
         := max(0, binom(b_T,2)-3 floor(b_T/2)).        (17)
```

The checker verifies for every `0<=b<=12` that

```text
g(b)>=7b-40.                                           (18)
```

At the endpoint,

```text
sum_T b_T=2300.
```

Summing (18) over 231 centres gives the exact global lower bound

```text
sum_T e_0(T)
 =sum_{R0 pairs {U,V}} c_H(U,V)
 >=7*2300-40*231
 =6860.                                                (19)
```

The scalar bound is sharp: 226 values `b=10` and five values `b=8` attain
6860. This is not a globally compatible graph certificate.

There are 2546 `R0` pairs and each has codegree at most five. Equation (19)
therefore forces at least

```text
1372 R0 pairs with codegree >=1,
1079 R0 pairs with codegree >=2,
 590 R0 pairs with codegree >=3.                       (20)
```

Convexity of `c -> binom(c,2)` gives

```text
sum_{R0 pairs} binom(c_H(U,V),2) >=6082.
```

Every four-cycle of `H` is counted from its two opposite pairs, so

```text
#C4(H)>=3041.                                          (21)
```

The degree sum of `H` is 2300, and convexity gives at least 10305 centred
wedges in total. Using the exact fourth-walk identity,

```text
tr(H^4)
 =2|E(H)|+4 sum_T binom(deg_H(T),2)+8 #C4(H)
 >=67848.                                              (22)
```

Equations (19)--(22) are actual global-overlap constraints. They do not
assume an automorphism, transitivity, orbit structure, or a restricted graph
search.

## Lemma 7: exact rootless trace normalization

By (13), every unordered `R2` pair has `H`-codegree zero or one. Therefore

```text
tr(A_R2 A_R3^2)
 =2 * #{unordered R2 pairs with their unique closure realized}. (23)
```

At `n3=708`, the unrestricted endpoint trace is an even integer in

```text
{0,2,...,1416}.
```

The rootless premise sets it to zero. Equivalently, all 708 `R2` pairs must
omit their unique globally compatible closure. This is strictly stronger
than saying that all 2832 pair-indexed Wave 33 board selections remain open:
three of the four selections at each pair cannot coexist with the full
fibre/projector package as actual common `R3` triangles.

## Complete versus restricted coverage

The derivations are complete for every actual endpoint satisfying the frozen
premises:

- the fibre partition and all six perfect matchings are forced by
  `lambda=1,mu=2`;
- the holonomy permutation covers all twelve labels without symmetry
  assumptions;
- the PSD cap checks the full endpoint Gram alphabet;
- the endpoint sums use all 231 triangles and every unordered pair.

The explicit controls are deliberately restricted:

- they specify permutations and perfect matchings only;
- they do not specify the `Z`-fibre edges, graph degrees, all
  `lambda/mu` equations, a 99-vertex graph, or a rank-44 integral lift;
- the scalar profile attaining (19) is only an arithmetic sharpness witness.

## Strongest self-objection and conclusion

The blocking objection remains:

> The cap-one theorem says each `R2` edge has only one possible actual
> closure, but it does not show that any of the 708 unique closures must be
> present. The forced `R0` overlap and 3041 four-cycles remain compatible
> with all proved local PSD and matching inequalities.

The exact Stage 1 conclusion is therefore:

```text
actual-incidence/projector domain: strictly reduced
actual motif forcing:              UNKNOWN
actual motif avoidance:            UNKNOWN
rootless indecomposable endpoint:  UNKNOWN
n3=708:                            UNKNOWN
Conway-99:                         UNKNOWN
novelty:                           UNKNOWN
```
