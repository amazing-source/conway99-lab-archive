# Wave 17 structural analysis of the conditional `n3=54` frontier

Verdict: **`n3=54` is not excluded.**  The equality chain is sharp and
forces a much smaller exact residual.

Five of the six `d_K>=4` profiles have `r<=17` and are excluded by the
audited dense-subset inequality.  The last profile has

```text
r=18,  q=2^18,  |X|=27.
```

Equality then forces all 27 active points to have size two,
`G[X]` to be 6-regular, and the cut `(X,V(G)-X)` to be equitable with
quotient matrix

```text
[[6,8],
 [3,11]].
```

The residual is described exactly by a cubic triangle-free point graph `F`
on 18 active labels and a 2-factor `R` on its 27 edges.  If `N` is the
18-by-27 incidence matrix of `F`, then

```text
N A_R N^T = 2 A_L,
A_X = N^T N - 2I + A_R.
```

The point graph has no nonadjacent pair with exactly two common neighbors.
Consequently every component is either `K3,3` or has girth at least five.
An exact parity argument newly excludes the option `F=3K3,3`.  The two
remaining point-graph types are:

```text
connected cubic girth-at-least-five graph of order 18;
K3,3 plus a connected cubic girth-at-least-five graph of order 12.
```

The nonisolated auxiliary graph also has a canonical closed hexagonal
surface structure with

```text
V=27, E=54, F=18, chi=-9.
```

Thus every equality-case lift has a nonorientable surface component.  No
valid argument was found that the surface must be orientable, so this is a
residual characterization rather than a contradiction.

```yaml
role: proof_a
date_utc: 2026-07-23T12:03:19Z
git_commit: 025946ab523e1429245fd88e48956f9ae6d4112d
claim_label: DERIVED
scope: conditional structural reduction of n3=54 for a putative srg(99,14,1,2), including exclusion of the F=3K3,3 residual branch
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  agents/2026-07-23-wave16-n3-51-structural.md: 95d04a774397332417c9613718fe6699a5392ef5222fef1cfa00b12e2860af3f
  verification/2026-07-23-wave16-n3-51-structural-audit.md: 99203a15db2646a759edbb2241eb4bd5e6001733ac862952c9db57446c58ead6
  verification/2026-07-23-wave15-global-lift-audit.md: edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036
  verification/2026-07-23-wave15-algebraic-audit.md: b0541d05d2c1c359152b86223e2ebbdbd002b2ff42deb699f6a0b21d149a5b45
  attempts/wave16-n3-51-structural/exact_check.py: 5aef211ea7d457543fc3f494eea125bbd0fd6fae2533fd566b475ff3f971c5cf
method: audited active-triangle framework, exact q-profile enumeration, equality analysis in the SRG subset bound, point/support incidence matrices, exact twofold N3 coverage, binary parity and rank, auxiliary-surface reconstruction, and SRG block moments
command: |
  .venv\Scripts\python.exe -B attempts\wave17-n3-54-structural\exact_check.py
  .venv\Scripts\python.exe -B -m unittest -v attempts\wave17-n3-54-structural\test_exact_check.py
  .venv\Scripts\python.exe -B attempts\wave17-n3-54-structural\restricted_k33_sat.py
  .venv\Scripts\python.exe -B attempts\wave17-n3-54-structural\restricted_k33_sat.py --omit-matching
  .venv\Scripts\python.exe -B attempts\wave17-n3-54-structural\unrestricted_active_sat.py
outputs:
  attempts/wave17-n3-54-structural/exact_check.py: 8f4f8c27e486cd67b29028911ec101fdcb6e812e6ac12b5572a896d3fa84155a
  attempts/wave17-n3-54-structural/test_exact_check.py: 3ee410014dc80cedb78a63869d738168668f1e8bfb54e7e2e24c64d0f5ec3034
  attempts/wave17-n3-54-structural/restricted_k33_sat.py: 405f5ac2714bf4fd74856cb6b153de9d4602989456c82132efcf8640f654613a
  attempts/wave17-n3-54-structural/unrestricted_active_sat.py: 54cb7878f7ea50dc119f6420a0d9d1d784e5a41a6238dea35f0c7f37eae6ab15
  exact_checker: PASS
  focused_tests: "7/7 PASS"
  restricted_F_equals_3K3,3_sat_status: UNSAT_WITHOUT_PROOF_CERTIFICATE
  restricted_matching_omitted_control: UNSAT_WITHOUT_PROOF_CERTIFICATE
  unrestricted_active_sat: TIMEOUT_AFTER_60_SECONDS_NON_EVIDENTIARY
  conditional_n3_54_exclusion: UNKNOWN
  conway_99_target: UNKNOWN
  novelty: UNKNOWN
limitations: the structural derivation imports the audited H/L/indexed-point framework rather than reconstructing it from a raw 99-by-99 adjacency matrix; this discovery lane cannot verify its own bridges; the SAT statuses have no proof certificate and are not used as proof; the residual omits a complete outside-triple realization or full 99-vertex completion; no target resolution or novelty conclusion is claimed
```

The commit was read directly from `.git/HEAD` and its referenced file.  No
Git command or Git mutation was used.  The unrestricted SAT command exceeded
60 seconds; its two exact child processes were identified by their full
command line and stopped.  Its timeout is retained only as a failed approach.

## 1. Audited premises used

Assume `G` is an `srg(99,14,1,2)` and `n3=54`.  I imported only the
following previously audited statements.

1. The graph `L` on graph-triangles has

   ```text
   q(T)=d_L(T)/3,
   q(T)=0 or q(T)>=2,
   sum_T q(T)=2n3/3=36.
   ```

2. If `A` is the set of active triangles, `r=|A|`, and
   `K=complement(L[A])`, then the nonempty indexed sets

   ```text
   S_u={T in A:u in T}
   ```

   have size at least two, are linear `K`-cliques, cover every active label
   exactly three times, and contain no three points meeting pairwise at
   three distinct labels.
3. Every active label has

   ```text
   d_K(T)=r-1-3q(T)>=4.
   ```

   The strict lower bound is the audited repeated-degree-three obstruction.
4. At a size-two point `P`, every actual graph edge has endpoint-local
   `H`-degree zero or four.  A positive edge joins disjoint active points and
   gives a complete `2`-by-`2` rectangle in `L`.
5. The fixed-point identity is

   ```text
   sum_{v:uv in E(G)} d_H(uv)=2 sum_{T in S_u}q(T).
   ```

6. If an induced vertex set in `G` has minimum degree at least six, then it
   has at least 27 vertices.  Equivalently, for `m=|X|`,

   ```text
   average_degree(G[X]) <= 3+m/9.
   ```

No Wave 14 size cap, candidate, catalog non-hit, automorphism, or global
`H`-degree restriction is imported.

## 2. The six profiles and the sharp boundary

Nondecreasing integer partitioning of 36 subject to

```text
q>=2,  3q<=r-1
```

gives 23 raw profiles.  The exact `d_K>=4` filter leaves:

| `r` | `q` multiset | `K`-degree multiset | `|X|<=floor(3r/2)` |
|---:|---|---|---:|
| 14 | `2^6 3^8` | `7^6 4^8` | 21 |
| 15 | `2^9 3^6` | `8^9 5^6` | 22 |
| 16 | `2^12 3^4` | `9^12 6^4` | 24 |
| 17 | `2^16 4` | `10^16 4` | 25 |
| 17 | `2^15 3^2` | `10^15 7^2` | 25 |
| 18 | `2^18` | `11^18` | 27 |

The active-set incidence count is

```text
sum_{u in X}|S_u|=3r,
```

and every summand is at least two, giving the displayed upper bound.

The Wave 16 minimum-degree bridge extends through `q=4`.  If `|S_u|>=3`,
the active triangles through `u` already supply at least six distinct
neighbors in `X`.  If `S_u={i,j}`, the endpoint-local crossing lemma and
the fixed sum give

```text
4 times (number of positive support neighbors)
  =2(q(i)+q(j)).
```

An odd `q(i)+q(j)` is impossible.  If it is even, the number of positive
neighbors is `(q(i)+q(j))/2>=2`.  These neighbors are distinct, active, and
different from the four triangle neighbors.  Hence

```text
delta(G[X])>=6
```

for all six profiles.  The first five have `|X|<=25`, contradicting the
audited lower bound 27.

For `r=18`, both bounds are equal:

```text
|X|=27.
```

All 54 point incidences must therefore be 27 points of size two.  The sole
profile is `q=2^18`, so every point has fixed sum eight and exactly two
positive support neighbors.

## 3. Spectral equality makes the cut equitable

At `m=27`, minimum degree six and the exact subset inequality give

```text
162 <= 2e(G[X]) <= 3*27+27^2/9=162.
```

Thus `G[X]` is exactly 6-regular.

Let `x=1_X` and write

```text
x=(3/11)1+y,  y perpendicular to 1.
```

Equality in the restricted-eigenvalue-three Rayleigh bound forces `y` to
lie in the eigenvalue-three eigenspace.  Therefore

```text
A x = 3x+3*1.
```

Each vertex in `X` has six neighbors in `X`; every vertex outside `X` has
exactly three neighbors in `X`.  The outside set has order 72, each `X`
vertex has eight outside neighbors, and the partition is equitable:

```text
          into X   into outside
X            6          8
outside      3         11
```

Every nonprincipal eigenvalue of `G[X]` lies in `[-4,3]`.  In particular
`G[X]` is connected: a second 6-regular component would supply a
sum-zero eigenvector of eigenvalue six.

## 4. Exact point/support residual

Because all active points have size two, regard them as edges of a graph
`F` whose vertices are the 18 active labels.  Each label belongs to three
points, so `F` is a simple cubic graph with 27 edges.  It is triangle-free
by the audited common-point rule.  Every `F`-edge lies in `K`.

The four meeting neighbors of a point-edge are exactly its neighbors in
the line graph of `F`.  Its two positive support neighbors define a simple
2-factor `R` on `E(F)`.  Meeting and support neighbors are disjoint, and the
6-regular equality leaves no room for any other active-active edge.  Thus

```text
G[X]=line(F) union R
```

as an edge-disjoint union.

An `R`-edge pairs two disjoint `F`-edges and its four endpoint pairs all lie
in `L`.  Conversely, every `L`-edge is one induced `N3` and has exactly its
two independent cross graph-edges, both in `R`.  If `N` denotes the
vertex-edge incidence matrix of `F`, exact coverage is precisely

```text
N A_R N^T=2A_L.                                      (1)
```

Also

```text
A_X=N^T N-2I+A_R.                                    (2)
```

Equation (1) includes both the zero coverage of `K`-pairs and exact
twofold coverage of `L`-pairs.  The inherited independent-cross-edge rule
further says that the two covers at an `L`-edge use distinct `F`-edges on
each side.

## 5. Point-graph component reduction and the `3K3,3` parity obstruction

No nonadjacent pair of vertices of `F` has exactly two common neighbors.
Indeed, suppose labels `a,b` had exactly two common `F`-neighbors.  The two
corresponding meeting edges between the disjoint graph-triangles `a,b` are
independent.  Since `a,b` share an `F`-neighbor, the point-clique rule puts
`ab` in `K`; hence no `R`-rectangle crosses their stars.  Equality leaves
exactly the two meeting cross-edges, which would make `ab` an `L`-edge, a
contradiction.

If a component of the cubic triangle-free graph `F` has a 4-cycle, opposite
vertices have at least two common neighbors and hence exactly three.  Their
three common neighbors also cannot have codegree two; cubicity then closes
the entire component to `K3,3`.  Every other component has girth at least
five and therefore order at least ten.  Since `|V(F)|=18`, the only component
profiles are:

```text
connected girth>=5 graph of order 18;
K3,3 plus a connected girth>=5 graph of order 12;
3K3,3.
```

The last profile is impossible.  Let its three components be `A,B,C`, and
let `x_AB` count `R`-edges between the nine point-edges in components `A`
and `B`.  Every label pair within a `K3,3` component lies in `K`, so an
`R`-rectangle cannot pair two point-edges in the same component.  Since
each point-edge has `R`-degree two,

```text
x_AB+x_AC=x_AB+x_BC=x_AC+x_BC=18,
```

and hence

```text
x_AB=x_AC=x_BC=9.                                    (3)
```

Work over `F_2`.  Let `N_A,N_B` be the `6`-by-`9` incidence matrices of the
two copies of `K3,3`, and let `M_AB` be the `9`-by-`9` bipartite adjacency
matrix of the selected `R`-edges between their point-edge sets.  The
`A,B` block of (1) gives

```text
N_A M_AB N_B^T=0.                                    (4)
```

Let `s_B` be the indicator of one bipartition class of the second `K3,3`.
Every edge crosses that class, so

```text
N_B^T s_B=1.
```

Multiplying (4) by `s_B` gives

```text
N_A p=0,  where p=M_AB 1.
```

Thus the `A`-point-edges having odd `AB`-degree form an Eulerian subgraph of
the bipartite graph `K3,3`.  Such a subgraph is a union of even cycles, so
the Hamming weight of `p` is even.  On the other hand,

```text
weight(p) mod 2
 = sum(p) mod 2
 = x_AB mod 2
 =1
```

by (3), a contradiction.  This proof uses neither the SAT status nor the
independent-cross-edge matching refinement.

## 6. Binary restrictions on the remaining two profiles

Let `P` be the vertex-edge incidence matrix of the 2-factor `R`, and let
`c_F,c_R` be the numbers of components of `F,R`.  Over `F_2`,

```text
P P^T=A_R,
(NP)(NP)^T=N A_R N^T=0.
```

The row space of `NP` is therefore self-orthogonal in `F_2^27`, so it has
dimension at most 13.  The exact incidence ranks and Sylvester's inequality
give

```text
rank(NP) >= (18-c_F)+(27-c_R)-27,
c_F+c_R>=5.                                          (5)
```

There is a second form.  Equation (1) modulo two says `A_R` maps the
`(18-c_F)`-dimensional row space of `N` into its
`(9+c_F)`-dimensional orthogonal complement.  Hence

```text
nullity_F2(A_R)>=9-2c_F.                              (6)
```

For a disjoint union of cycles, an odd cycle contributes one to this
nullity and an even cycle contributes two.  Thus, writing `o_R,e_R` for
the numbers of odd and even `R`-components,

```text
o_R+2e_R>=9-2c_F.
```

For the two surviving point-graph profiles:

```text
c_F=1: c_R>=4 and o_R+2e_R>=7;
c_F=2: c_R>=3 and o_R+2e_R>=5.
```

These are genuine restrictions but not contradictions.

## 7. Canonical nonorientable hexagonal surface

Let `H+` be the nonisolated part of the audited auxiliary graph `H`.  Its
vertices are the 27 actual support edges, equivalently the edges of `R`.
Every such vertex has `H`-degree four, and the 54 induced `N3` copies are
the edges of `H+`.  Thus `H+` is a simple triangle-free 4-regular graph on
27 vertices.

For an active triangle `T`, the side subgraph `H_T` is simple, 2-regular,
triangle-free, and has

```text
|E(H_T)|=3q(T)=6.
```

It is therefore a single 6-cycle.  Attach one hexagonal face along each of
the 18 cycles `H_T`.  Each edge of `H+` lies in exactly its two side faces.

At a vertex of `H+`, the underlying support edge joins two disjoint points

```text
{a,b} and {c,d}.
```

Its four incident `H+`-edges are labeled

```text
ac, ad, bc, bd.
```

The four incident faces pair these half-edges as

```text
a: ac-ad,  d: ad-bd,  b: bd-bc,  c: bc-ac.
```

Hence the vertex link is a 4-cycle.  The face attachments therefore form a
closed, possibly disconnected, 2-manifold with

```text
chi=27-54+18=-9.
```

Every closed orientable surface has even Euler characteristic, so at least
one component here is nonorientable.  The tempting next step, that the
construction is naturally orientable, was not justified: orienting original
graph edges or active triangles does not make the face orientations
automatically agree across every `N3` edge.  Treating odd Euler
characteristic alone as a contradiction would be invalid.

## 8. Outside incidence and SRG moments

Let `C` be the 27-by-72 incidence matrix of the equitable cut and let `A_Y`
be the outside adjacency matrix.  It has row sum eight and column sum three.
The SRG block equations are

```text
C C^T = 12I-A_X-A_X^2+2J,                            (7)
A_X C+C A_Y = -C+2J,                                 (8)
C^T C+A_Y^2 = 12I-A_Y+2J.                            (9)
```

Each outside vertex has a three-element neighborhood in `X`.  Those three
point-edges form a matching in `F`, because an outside vertex cannot be a
second common neighbor of two vertices in an active triangle.  They induce
at most one `R`-edge, because an adjacent `X`-outside pair has only one
common neighbor.

Let `c` be the number of triangular components of the 2-factor `R`.
Every triangle of `G[X]` is either one of the 18 active triangles or a
triangular `R`-component: a meeting edge already has its unique active
triangle.  Counting unique graph-triangles by their number of vertices in
`X` gives:

| vertices in `X` | triangle count |
|---:|---:|
| 0 | `105-c` |
| 1 | `81+3c` |
| 2 | `27-3c` |
| 3 | `18+c` |

Exactly `27-3c` outside three-neighborhoods contain one `R`-edge, and the
remaining `45+3c` are independent in `G[X]`.

The active-triangle intersection moments give no further obstruction.  For
the 213 inactive graph-triangles, the number of meeting active triangles is
twice the number of their `X`-vertices.  For every `0<=c<=9`,

```text
sum m_T=270,
sum m_T^2=756.
```

Together with the 18 active terms `m_T=3`, this gives the exact spectral
moment `sum_T m_T^2=918`.  The constancy in `c` shows why the first two
triangle-intersection moments cannot distinguish the remaining residuals.

## 9. Computation boundary and failed approaches

The standard-library exact companion reconstructs all 23 raw profiles, the
six survivors, every size-two `q` parity row, the equality arithmetic,
surface counts, triangle-type moments, and binary cycle nullities.  Its
seven focused tests pass.

The fixed `F=3K3,3` SAT scout returned `UNSAT` both with and without the
independent-cross-edge matching clauses.  It emitted no proof trace, so
neither solver status is evidence.  The human parity proof in Section 5 is
the claimed exclusion.

The unrestricted labeled active-incidence/support SAT scout did not finish
within 60 seconds.  It omits the 72 outside vertices, full SRG equations,
global auxiliary-`H` triangle-freeness, and active common-neighbor caps even
if it eventually finds a model.  Its timeout is not a nonexistence result.

Retained failed routes:

1. The dense-subset inequality is exactly sharp at order 27.
2. Equitable-cut block moments are consistent for every possible number of
   triangular `R`-components.
3. Odd Euler characteristic forces nonorientability, not impossibility.
4. Binary rank forces several `R`-components but permits both remaining
   point-graph profiles.
5. A computational non-hit without a checked proof certificate is not used.

The strongest objection to publication status is the semantic chain from
the audited endpoint-local crossing lemma to exact twofold rectangle
coverage and then to the surface vertex links.  Each bridge has been written
explicitly above, but this lane cannot independently promote its own
derivation to `VERIFIED`.

Final boundary:

```text
five r<=17 profiles:                         EXCLUDED / DERIVED
r=18 equality/equitable-cut reduction:       DERIVED
F=3K3,3 branch:                              EXCLUDED / DERIVED
remaining F component profiles:              2
conditional n3=54 exclusion:                 UNKNOWN
stronger conditional n3 lower bound:         NOT CLAIMED
Conway srg(99,14,1,2):                       UNKNOWN
novelty:                                     UNKNOWN
```
