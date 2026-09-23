# Wave 7 triangle-side incidence and the `n3` gap

```yaml
role: proof_b
date_utc: 2026-07-23T00:41:44Z
git_commit: 0728b260e1282afdbaeaa9215659a4175cab25de
claim_label: DERIVED
scope: conditional strengthening of the induced-N3 and induced-C6 lower bounds
inputs:
  STRUCTURE.md: 0b30b92d1ab19fc4d80209e116f5ba1afc2284fddd6cfcb4a9091967483292a8
  agents/2026-07-22-wave6-opposite-edge-graph.md: 4197c40e1b43d72d5a2ad9a6203099ffed2e1dbf4f0b3c07186aaad54cae4fa2
  verification/n3-side-incidence/verify.py: ec51e5245a886f4f10520393ed06140fb4f9f07531f5461c9fc89f04c5654441
  verification/n3-side-incidence/audit_generic.py: cf37f75ad033cb2f9d839e7fa85d6bac2e6d113cfdfc07bc78a043e453482f98
  lou_murin_2014_prior_art_pdf: 5df5b96709419c6168430c58601ee98ec26e6c08036034bd755247311c2fb211
method: exact triangle-partner counts, local two-matching structure, an active-triangle incidence reduction, extremal graph theory, and two exhaustive finite checks
command: |
  python verification/n3-side-incidence/verify.py
  python verification/n3-side-incidence/audit_generic.py
outputs:
  global_n3_lower_bound: 30
  global_induced_C6_lower_bound: 209316
  branch_n3_lower_bounds: [30, 33, 42, 48, 48, 30, 42, 48, 33, 48, 42, 48]
limitations: conditional on target existence and the previously established target-specific N3 occurrence; no graph or nonexistence proof is produced
```

> **Prior-art attribution (added 2026-07-23):** Lou and Murin's 2014 MIT
> PRIMES-USA report, Section 5, pages 7--8, gives the equivalent fixed-triangle
> partner equations in variables `(alpha,beta,gamma)=(a1,a2,a3)` and excludes
> `gamma=11`, which is `q=1`. The profile and `q`-gap below are therefore
> independent rederivations of prior art, not project novelty. See
> `agents/2026-07-22-wave8-status-search.md` for the exact translation and
> source hash. The later global support exclusions and exact project bound had
> no checked prior-art hit, but novelty is not claimed for them either.

## Triangle-pair arithmetic

Let `G` be a putative `srg(99,14,1,2)`, and let `mathcal T` be its 231
graph-triangles. Write `Gamma` for their intersection graph. As recorded in
[STRUCTURE.md](../STRUCTURE.md), `Gamma` is 18-regular with spectrum

```text
18^1, 7^54, 0^44, (-3)^132.
```

The exact integer matrix

```text
C = Gamma^2 - 5 Gamma - 18 I
```

has a useful combinatorial interpretation. Its diagonal entries and entries
on intersecting triangle pairs are zero. If `T,U` are disjoint triangles,
then `C[T,U]` is exactly the number `r(T,U)` of graph edges between them.
Indeed, a common `Gamma`-neighbor of two disjoint triangles is the unique
graph-triangle on one of their cross-edges, and conversely. In particular,
`C` has forced spectrum

```text
216^1, (-4)^54, (-18)^44, 6^132.
```

Fix a triangle `T`, and let `a_r(T)` count disjoint triangles joined to `T`
by exactly `r` cross-edges. The cross-edges form a matching: two sharing an
endpoint would give an edge inside one side two common neighbors. Hence
`0 <= r <= 3`.

There are 212 triangles disjoint from `T`. Exact double counts give

```text
sum_r a_r = 212,
sum_r r a_r = 216,
sum_r binom(r,2) a_r = 36.
```

For the first moment, take one of the 36 graph edges `xu` leaving `T`. Its
external endpoint `u` lies in exactly six graph-triangles disjoint from `T`,
so `xu` is a cross-edge to each of those six triangles. For the second
binomial moment, choose an ordered pair of distinct vertices `x,y` of `T` and
one of the twelve external neighbors `u` of `x`. The nonedge `u,y` has `x` and
one unique other common neighbor, producing a unique paired cross-edge at
`y`. The 72 ordered instances count each unordered cross-edge pair twice.

Let `p(T)=a_3(T)` be the number of triangular-prism partners and put

```text
q(T) = 12 - p(T).
```

Solving the three equations gives

```text
(a_0,a_1,a_2,a_3)
  = (20+q, 180-3q, 3q, 12-q).
```

## The triangle-side graph `L`

Define `L` on `mathcal T`, joining two graph-triangles exactly when their six
vertices induce `N3`, two triangles with exactly two independent cross-edges.
Thus

```text
d_L(T) = 3 q(T),
|E(L)| = n3,
sum_T q(T) = 2 n3 / 3.
```

The following local gap is decisive:

```text
q(T) = 0 or q(T) >= 2.
```

To prove it, fix `T={x,a,b}`. Let `H_T` be the subgraph of the Wave 6 graph
`H` formed by the `N3` edges having `T` as one side, with isolated potential
cross-edge vertices discarded. This is a subgraph, not necessarily an
induced subgraph, of triangle-free `H`.

For a potential cross-edge `xu`, the two possibilities using `a` and `b` are
controlled by the two local perfect matchings from the Wave 6 argument. Either
the relevant pair is common to those matchings and both completions are
prisms, or it is not common and both completions are `N3`s. Every nonisolated
vertex of `H_T` therefore has degree two. Moreover,

```text
|E(H_T)| = d_L(T) = 3 q(T).
```

If `q(T)=1`, the simple 2-regular graph `H_T` would have three edges and hence
would be a triangle, contradicting triangle-freeness of `H`.

Call a triangle active when `q(T)>0`. For each graph vertex `u`, define

```text
S_u = {active graph-triangles containing u}.
```

Every `S_u` is independent in `L`, since its triangles intersect at `u`. For
every actual graph edge `uv`, there is an exact support identity

```text
d_H(uv) = e_L(S_u,S_v),
```

where each `L`-edge crossing the possibly overlapping sets is counted once.
An `H`-edge incident with `uv` is an induced `N3` whose side triangles contain
`u` and `v`, respectively; the converse associates each such `L`-edge to the
cross-edge `uv`. This is a bijection.

The Wave 6 local-matching calculation remains in force:

```text
d_H(uv) in {0,4,6,8,10,12}.
```

## Excluding `n3=24`

If `n3=24`, then `sum q=16`. Every active `q` is at least two, so there are at
most eight active triangles. An active `q>=3` would give `L`-degree at least
nine, impossible on at most eight active vertices. Hence there are exactly
eight active triangles, all with `q=2`.

The active subgraph of `L` is 6-regular on eight vertices, so

```text
L = K_8 - M
```

for a perfect matching `M`. Consequently each `S_u` has size at most two, and
a size-two set is one of the four pairs in `M`. For a support vertex `uv` of
`H`, the support identity and allowed-degree set force

```text
d_H(uv)=4,
```

with `S_u,S_v` two distinct matching pairs. Two graph-triangles share at most
one graph vertex, so the four matching pairs supply at most four possible
endpoint vertices and therefore at most `binom(4,2)=6` support vertices of
`H`. But a 4-regular graph with 24 edges needs twelve support vertices. This
is a contradiction.

## Excluding `n3=27`

Now `sum q=18`. The same degree argument forces exactly nine active triangles,
again all with `q=2`. Thus `L` is 6-regular and its complement `K` on the
active triangles is 2-regular. Its possible component types are exactly

```text
C9, C4+C5, C3+C6, 3C3.
```

Each `S_u` is a clique in `K`. If every `S_u` has size at most two, every
positive `H`-degree is at most four and hence exactly four. This is impossible
because the degree sum `2|E(H)|=54` is not divisible by four. Therefore some
`S_u` has size three, and `K` must contain a `C3`.

Three pairwise-intersecting graph-triangles must share one common graph
vertex. If their three pairwise intersections were distinct, those three
intersection points would form another graph-triangle, putting one of its
edges in two graph-triangles. Thus a realized `C3` is either one central
size-three point or has at most two separately realized pair-intersection
points. A `K`-edge need not be an intersection at all; unused edges are
allowed throughout the argument and both checkers.

For `C3+C6`, the necessary size-three point consumes the `C3`. Each of the six
cycle edges supplies at most one size-two point. The central point can form at
most six support vertices with them, of `H`-degree six. Among the six cycle
edge-points, only the three opposite pairs have an allowed positive crossing
count, namely four. Thus `H` has at most nine support vertices.

For `3C3`, each component is central, supplying one size-three point, or
noncentral, supplying at most two size-two points. Between components the
possible crossing counts are

```text
2*2=4, 3*2=6, 3*3=9.
```

The last is not an allowed `H`-degree. At least one component is central, and
the maximum is attained by one central and two noncentral components:

```text
2 + 2 + 4 = 8
```

possible support vertices.

Finally, a simple triangle-free graph with 27 edges needs at least eleven
nonisolated vertices by Mantel's theorem:

```text
27 <= floor(s^2/4).
```

The upper bounds nine and eight are both too small. This excludes `n3=27`.

## Consequences and boundary of the result

Wave 6 established `n3>=24`, and the six-vertex identity gives
`n3=0 (mod 3)`. Excluding 24 and 27 therefore yields

```text
n3 >= 30,
induced_C6_count = 209,286 + n3 >= 209,316.
```

The twelve normalized branch bounds strengthen to

```text
30,33,42,48,48,30,42,48,33,48,42,48.
```

Two standard-library programs exhaust the finite point-incidence cases. The
first follows the component analysis directly; the second generically
enumerates all cliques in `K`, permits unused complement edges, enforces
disjoint edge consumption and the `K3` common-point rule, and adds singleton
fillers until every active triangle has three graph vertices.

The attempted next step, excluding `n3=30`, remains open. At that value the
same arithmetic forces ten active `q=2` triangles, so `L` is 6-regular and its
complement is cubic. No complete classification or contradiction has been
proved. The present result is a conditional necessary bound, assumes no
automorphism of a completed graph, and does not resolve Conway-99.
