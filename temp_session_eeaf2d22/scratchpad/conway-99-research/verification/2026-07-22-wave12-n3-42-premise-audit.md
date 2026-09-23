# Wave 12 `n3=42` premise audit

Verdict: the established Wave 6--11 framework has been reconstructed, and a
new conditional reduction to one active profile is `DERIVED`. A subsequent
fixed-point repair excluding size-three points in that profile has passed an
independent adversarial audit. A direct repetition of the Wave 11 *local*
equality proof is still `REFUTED` by an explicit abstract premise model. The
remaining all-size-two branch and the Conway-99 target remain `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T06:26:58Z
git_commit: 4d561fb8b5e0b335d430c2ac93962cbf0ae40184
claim_label: DERIVED
scope: conditional n3=42 active profiles, the r=14 size-three branch, and the exact boundary of the Wave 11 local premises
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  CONJECTURE.md: 7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58
  CLAIMS.yaml: 8c3bd7c98006cf89a495461dd696b2247668e4c735c9ca02dc5d002bc9afdda6
  OBLIGATIONS.yaml: c9e7677014757dbe947eb830ceeafbd30d2a03786d1b29110f2030c59028c702
  agents/2026-07-22-wave6-opposite-edge-graph.md: 4197c40e1b43d72d5a2ad9a6203099ffed2e1dbf4f0b3c07186aaad54cae4fa2
  agents/2026-07-22-wave7-triangle-side-incidence.md: 7b4693420eae7e6f13ce0d66c786424c18863a1b1c350da83097f8e982ebe324
  agents/2026-07-22-wave8-n3-equality.md: 010fe1e2a9752ac18067b44c9e6cf1114e2d1651364c49a574adbe22fe5461f3
  agents/2026-07-22-wave9-n3-33-equality.md: b2fe46cce67440d1a730d6f56b48a512952624d79afa9835ffc772c050c94555
  agents/2026-07-22-wave10-n3-36-equality.md: 9a1e2ad7cac5e26f9fe4117c8ced2390ca15a4dfda7b1e67faa02b8e90ba507e
  agents/2026-07-22-wave11-n3-39-equality.md: 0119df513027d9f895eabc9746ac6efd4f5a779366638603b5dc0dfa81b80e82
  verification/2026-07-22-n3-count-bound-audit.md: 773321e8b9934d658f810c6c2eef0e00a339414d98be330ca273d3f9b8bd7753
  verification/2026-07-22-n3-side-incidence-audit.md: 9b6ff3cc9ec8bec13ffd93a8abe0bf0f35398c99f676d00064d6bf5fe6db6787
  verification/2026-07-22-n3-equality-audit.md: 066be6c97bf93cfb331a03b387487e72f0a42095d44ac818c2dcd569c186e32d
  verification/2026-07-22-n3-33-equality-audit.md: 0df19a68e48ffa3ff8a4e434598e72dac449af8462ddd765f8c6bcb5bd038e1e
  verification/2026-07-22-n3-36-equality-audit.md: bbe748d8ad62d05e04891eec4d9726859892547970933dd406497a7e699bc824
  verification/2026-07-22-n3-39-equality-audit.md: 159b1746b715984749f3efc790c56be5b2624e889901412ad0bcf8e2cc9497b9
method: independent integer-profile enumeration, proof reconstruction, adversarial boundary analysis, hostile replay of the fixed-point size-three repair, a closed-form diagnostic model, and a modular exact-coverage obstruction
command: N/A; the deductions and diagnostic object below are closed-form, and no solver exit code is used as evidence
outputs:
  inherited_wave6_11_premises: VERIFIED
  surviving_active_profile: "r=14, q=(2^14), K 7-regular"
  mixed_r13_profile: "DERIVED impossible"
  direct_wave11_reuse: REFUTED
  r14_size_three_branch: "VERIFIER PASS: impossible once the fixed-original-point identity is used"
  r14_remaining_point_profile: "all active point sets have size two"
  abstract_local_premise_survivor: "C7 Cartesian-product K2 point graph with K equal to its simple square"
  target_result: UNKNOWN
limitations: the size-three exclusion has one adversarial verifier pass but no machine certificate or ledger promotion; the abstract model is not a partial or complete Conway graph; no n3=42 exclusion or n3>=45 bound is claimed
```

## Label boundary

The Wave 6--11 inputs named above retain their ledger labels. In particular,
the complement bridge, singleton exclusion, linear point-hypergraph premise,
common-point rule, and labeled crossing rule are inherited `VERIFIED`
conditional premises.

The deductions first appearing in this report are only `DERIVED`. The
heptagonal-prism object below `REFUTES` a plausible shortcut, not the target.
Nothing here constructs or excludes `srg(99,14,1,2)`.

## Exact active profiles at `n3=42`

Assume a putative target graph has `n3=42`. The established identities give

```text
sum q(T) = 2 n3 / 3 = 28,
q(T) >= 2 on every active triangle,
3 q(T) <= r-1,
```

where `r` is the number of active graph-triangles. Exact integer enumeration
leaves:

```text
r=14: (2^14)
r=13: (2^12,4) or (2^11,3^2)
r=12: (2^8,3^4)
r=11: (2^5,3^6)
r=10: (2^2,3^8).
```

For the complement `K=overline(L[A])`,

```text
d_K(T)=r-1-3q(T).
```

Every active triangle lies in three non-singleton point cliques. Their
incident consumed `K`-edges are distinct, so every active triangle needs
`d_K>=3`. This immediately rejects:

- the `q=4` isolate in the first `r=13` profile;
- the `q=3` vertices of `K`-degree two in the `r=12` profile;
- the `q=3` vertices of degree one in the `r=11` profile; and
- the `q=3` vertices of degree zero in the `r=10` profile.

Only two profiles survive this first audit:

```text
A: r=14, q=(2^14),       d_K=7^14;
B: r=13, q=(2^11,3^2),  d_K=6^11,3^2.                 (1)
```

No connectedness or completed-graph automorphism is used.

## What does and does not generalize

The logical mechanisms have different boundaries at 42:

| Wave 11 mechanism | `n3=42` audit |
|---|---|
| `K=overline(L[A])` | Generalizes exactly. Empty `L`-crossings imply `K`-edges only through this explicit bridge. |
| Point-clique and linearity premises | Generalize exactly. |
| Common-point/Berge-triangle rule | Generalizes exactly. |
| Labeled crossing degrees `0` or `2` | Generalizes exactly. In particular, a singleton crossing side is empty. |
| Expansion | Generalizes as `2s<=r-s`, hence `s<=4` for both profiles in (1). |
| Size-four flower | Still impossible, but the regular degree-seven case needs an extra saturation argument given below. |
| `F/U` accounting | The symbolic edge count generalizes; the Wave 11 numerical capacity does not. |
| Type `233` contradiction | Works in profile B, but fails in profile A: four forced `U`-edges exactly meet capacity four. |
| Size-three propagation | Works in profile B. In profile A it forces a `233` occurrence instead of a contradiction. |
| Final parity | Works after reducing profile B to size two because `3r=39` is odd. It vanishes in profile A because `3r=42` is even. |

Thus copying the Wave 11 text while replacing `13` by `14` is unsound.

## Size four is still impossible

The expansion argument is unchanged. If `P` is a point set of size four, its
eight other point sets, called petals, have pairwise-disjoint external parts.

In profile B there are nine external active triangles. The Wave 11 count
therefore applies verbatim: no petal has size four, at most one has size
three, and at least three occurrences of `P` are type `224`. Two such
occurrences give four distinct endpoints adjacent in `K` to all of `P`.
Every member of `P` would have at least

```text
3 internal + 4 external = 7
```

`K`-neighbors, exceeding its degree six. A degree-three vertex cannot lie in
`P` in the first place, since `P` and the other two point sets through it
would consume at least five incident `K`-edges.

Profile A has ten external places, so the old strict degree contradiction
becomes equality. Nevertheless, the flower still closes. The eight petals
use at least eight external places and have only two units of excess
capacity. Hence at least two occurrences are type `224`. Choose two. Their
four endpoints are distinct and adjacent in `K` to every member of `P`.
Every member of `P` now has all seven of its `K`-neighbors accounted for:
the other three members of `P` and those four endpoints.

The two petals at either of the remaining two occurrences of `P` require
external representatives distinct from the four chosen endpoints. Point
cliques require those representatives to be `K`-adjacent to their base
member of `P`, but that base has no remaining `K`-degree. This contradiction
excludes size four in profile A as well.

Consequently every active point set has size two or three in both surviving
profiles.

## The mixed `r=13` profile is impossible

Let `F` be the union of point-clique edges and `U=K-E(F)`. If `t_i` is the
number of size-three point sets through active triangle `i`, then

```text
d_F(i)=3+t_i.
```

In profile B this gives

```text
q(i)=2: d_U(i)=3-t_i,
q(i)=3: t_i=0 and d_U(i)=0.                                (2)
```

In particular every vertex has `U`-degree at most three.

At a type `233` occurrence, the size-two endpoint has four forced `K`-edges
to the external sides of the two size-three points. The common-point rule
forbids an `F`-owner for each edge, so all four lie in `U`, contrary to (2).
There is no type `233`.

Let `P={i,j,k}` be a size-three point. All its vertices have `q=2`, since
the two degree-three vertices have `t=0`. If all three occurrences of `P`
were type `333`, the other six size-three points would require twelve
pairwise-distinct external triangles, while only ten lie outside `P`.
Therefore `P` has a type `223` occurrence, say at `i`, with endpoints
`a,b`.

Singleton crossings and the common-point owner veto force

```text
aj, ak, bj, bk, ab in U.
```

Vertices `j,k` each have two `U`-neighbors and already lie in `P`. Equation
(2) gives `t_j=t_k=1`, so both remaining occurrences of `P` are also type
`223`. Let their four endpoints be `c,d,e,f`. Expansion makes
`a,b,c,d,e,f` distinct. Repeating the same crossing argument forces

```text
ic, id, ie, if in U.
```

But `t_i=1`, so (2) gives `d_U(i)=2`, a contradiction. No size-three point
exists.

Only size-two point sets remain, but the total point incidence is

```text
13 * 3 = 39,
```

which cannot be a sum of even sizes. This eliminates profile B. The sole
remaining active profile is therefore

```text
r=14, q=(2^14), K 7-regular.                               (3)
```

This is a new conditional reduction, not a target resolution.

## The local degree-seven frontier

After excluding size four in (3), the correct degree table is

```text
d_F(i)=3+t_i,
d_U(i)=4-t_i.                                               (4)
```

Two Wave 11 contradictions now become propagation rules:

1. At a type `233` occurrence, its size-two endpoint `a` receives exactly
   four forced `U`-edges. Equation (4) implies `t_a=0`; triangle `a` is type
   `222`, and those four edges exhaust `N_U(a)`.
2. A size-three point cannot have three type-`333` occurrences: its six
   other size-three points would need twelve external triangles, but only
   eleven are available.
3. At a type-`223` occurrence of `P={i,j,k}`, the vertices `j,k` each
   receive two forced `U`-neighbors. They may now have `t=1` or `t=2`.
   If both had `t=1`, their two type-`223` flowers would force four distinct
   `U`-edges at `i`, exceeding `d_U(i)=3`. Hence at least one of the other
   two occurrences is type `233`.

It follows that every size-three point has at least one `233` occurrence. If
it has a `223` occurrence, then it also has a `233` occurrence. The possible
occurrence signatures are

```text
233/333/333,
233/233/333,
233/233/233,
223/233/333,
223/233/233,
223/223/233.
```

These are necessary propagation constraints, not a contradiction under the
generalized local premise list alone. The following repair uses the global
fixed-original-point identity, which is absent from that list.

## Adversarial audit of the size-three repair: `PASS`

The proposed repair was replayed without relying on its discovery path. No
counterexample survives the stated premises, and the earliest-gap search
found no gap.

Let `P={i,j,k}` be a size-three point. Since `P` itself is one of the
size-three points through each of its labels, at a label `x in P` its two
other point sets comprise

```text
3-t_x size-two petals and t_x-1 size-three petals.          (5)
```

Every size-two petal at `j` has the form `{j,a}`. Its labeled crossing with
`P-{j}` is empty, so complementarity gives the two `K`-edges `ai,ak`.
Neither edge can have a point-clique owner: such an owner, the petal, and
`P` would meet pairwise at three distinct labels. Thus both edges lie in
`U`. The same holds at `k`.

All endpoints counted this way are distinct. Endpoints from petals at one
base are distinct by linearity. If petals based at two different members of
`P` shared an external endpoint, those two petals and `P` would form the same
forbidden three-distinct-intersections configuration. Hence

```text
4-t_i >= (3-t_j)+(3-t_k),                                  (6)
```

and cyclically. There is no hidden reuse in this lower bound.

The six petal external parts are also pairwise disjoint. At base `x`, (5)
uses

```text
(3-t_x) + 2(t_x-1) = t_x+1
```

external labels. Only eleven labels lie outside `P`, so

```text
t_i+t_j+t_k <= 8.                                          (7)
```

Here each `t` lies in `{1,2,3}`. If `S=t_i+t_j+t_k`, the three inequalities
in (6) are `S>=2t_x+2`. If some `t_x=3`, then (7) forces `S=8`, giving
`(2,3,3)` up to order. If the maximum is two, the inequality at a value two
forces `S>=6`, giving `(2,2,2)`. The all-one case fails. These are exactly
the two advertised triples.

### Excluding `(2,3,3)` without crossing overcount

Suppose `t_i=2` and `t_j=t_k=3`. At `i`, the other two points are one
size-three point `Q` and one size-two point `{i,a}`. The empty singleton
crossing with `P` and the owner veto above put

```text
aj, ak in U.
```

Since `d_U(j)=d_U(k)=1`, both `j` and `k` are saturated by their edge to
`a`.

For two size-three co-points through one active label, deletion of the common
labeled copy leaves a `2`-by-`2` crossing. The degree-`0`-or-`2` law makes
this crossing either empty or all four edges. If it were empty in `L`, all
four cross-pairs would lie in `K`; the common-point owner veto prevents any
of them from lying in `F`, so all four would lie in `U`.

Apply this first to `P,Q` at `i`: its `P`-side contains the saturated labels
`j,k`, so the crossing cannot be `L`-empty. It is `L`-full. At each of the
two size-three co-points through `j`, the `P`-side contains saturated `k`, so
those crossings are also `L`-full. The two crossings at `k` are `L`-full
because their `P`-side contains saturated `j`.

These five co-points are distinct. Two at the same base are distinct original
vertices, while a repetition at different bases would give a point set
meeting `P` in two active labels, contrary to linearity. Each is an actual
graph neighbor of the original point represented by `P`, because the pair
shares a graph-triangle. For each pair the overlap label contributes no
`L`-edge, and the full external `2`-by-`2` crossing gives

```text
d_H=4.
```

The five distinct terms already contribute `20` to the fixed-point sum, but

```text
sum_{v:uv in E(G)} d_H(uv)
  = 2 sum_{T in P} q(T)
  = 12.                                                     (8)
```

All terms in (8) are nonnegative. This excludes `(2,3,3)` with no orientation,
overlap, or actual-edge ambiguity.

### The cubic intersection graph

It follows that every label lying in a size-three point has `t=2`. Assume
there is at least one such point, and form `R` whose vertices are the
size-three points and whose edge labeled `i` joins the two of them through
each `t_i=2` label.

The graph `R` is simple: two point sets cannot share two labels. It is cubic:
the three labels in a size-three point lead to three different neighboring
points. It is triangle-free: a triangle of point sets would have three
distinct pairwise-intersection labels and violate the common-point rule.

Write

```text
m=|V(R)|,  e=|E(R)|=3m/2.
```

There are exactly `e` labels with `t=2` and `14-e` labels with `t=0`. At a
`t=2` label `i`, the third point has the form `{i,a_i}`. Singleton forcing
against the two size-three points gives four distinct `U`-neighbors of
`a_i`; equation (4) therefore gives

```text
t(a_i)=0.                                                   (9)
```

The `e` resulting size-two points are distinct: one of them cannot contain
two `t=2` labels because its endpoint in (9) has `t=0`. They consume `e`
incidences among the `3(14-e)` incidences available at the `t=0` labels.
Consequently

```text
e <= 3(14-e),  so e<=10.                                   (10)
```

A nonempty simple cubic graph has even `m>=4`. From (10), `m<=6`, so
`m=4` or `m=6`. The first case is `K4` and has a triangle. In the second
case the complement is a simple `2`-regular graph on six vertices. Its only
cycle partitions are `C6` and `2C3`; the complement of `C6` is the triangular
prism and has triangles, while the complement of `2C3` is `K3,3`. Hence the
only surviving possibility is

```text
R=K3,3,  e=9,
```

leaving five `t=0` labels.

For an edge `i=PQ` of `R`, the four forced neighbors of `a_i` are precisely
the other two edge-labels at `P` and the other two at `Q`. They are distinct,
and (9) gives `d_U(a_i)=4`, so there are no additional neighbors:

```text
N_U(a_i)=N_{L(R)}(i).                                      (11)
```

The line graph of `K3,3` has no equal open neighborhoods. Label its vertices
by the nine cells `(r,c)`. The open neighborhood of `(r,c)` consists of the
other two cells in row `r` and the other two in column `c`. Two cells sharing
a row or column are adjacent and therefore cannot be open twins. For two
cells in different rows and columns, a third cell in the first row and a
column different from both displayed columns is adjacent to the first but
not the second.

If `a_i=a_j`, equation (11) would therefore make `i,j` equal. Thus
`i -> a_i` injects the nine edges of `R` into only five `t=0` labels, a
contradiction. No size-three point exists.

This closes only the size-three branch. All active point sets in (3) must now
have size two; it does not exclude the `n3=42` equality case.

## Diagnostic model for the generalized local premises

The failure is genuine rather than a loose inequality. There is a closed-form
abstract object satisfying every generalized local premise listed in the
Wave 11 audit.

Take the fourteen active labels

```text
A = Z_7 x Z_2.
```

Let `F=C7 Cartesian-product K2`, the heptagonal prism:

```text
(i,e)--(i+1,e),  and  (i,0)--(i,1).
```

Use the 21 edges of `F` as the active point sets, all of size two. Let `U`
join vertices at distance exactly two in `F`, namely

```text
(i,e)--(i+2,e),
(i,e)--(i-2,e),
(i,e)--(i+1,1-e),
(i,e)--(i-1,1-e),
```

and put

```text
K = F union U,
L = complement(K).
```

The exact checks are:

```text
d_F=3, |E(F)|=21,
d_U=4, |E(U)|=28,
d_K=7, |E(K)|=49,
d_L=6, |E(L)|=42.
```

Each active label lies in exactly three point sets. The point family is
linear. Because `F` is triangle-free, three size-two point sets cannot meet
pairwise at three distinct labels, so the common-point rule holds. Every
point set is a `K`-clique.

Finally, two point sets meeting at label `x` are two incident `F`-edges.
Their other endpoints are at distance two in `F`, hence adjacent in `K`.
Their singleton `L`-crossing is empty, so every labeled crossing degree is
zero. Complementarity is explicit. Thus the model satisfies the exact
generalized premise list and the all-size-two parity count `14*3=42`.

This object is not a Conway-graph candidate. It proves only:

> The Wave 11 local premises, with the arity and degree changed from 13/6 to
> 14/7, do not by themselves exclude `n3=42`.

## The global support layer rejects this one diagnostic

The prism model also clarifies the next missing premise. An `L`-edge is one
`N3` and must be covered by exactly two cross graph-edges. With all point sets
of size two, a positive cross graph-edge must join two disjoint `F`-edges
whose four endpoint pairs all lie in `L`.

For this prism, the 42 `L`-edges split into three 14-edge orbits:

```text
S3: same layer, cyclic offset 3,
X2: opposite layers, cyclic offset 2,
X3: opposite layers, cyclic offset 3.
```

Give these orbits weights `1,3,4` modulo five. A direct two-case check of
every eligible pair of point sets gives:

```text
rung-rung or cycle-rung: 2 S3 + 2 X3, weight 2+8 = 0 mod 5;
cycle-cycle:              1 X2 + 3 X3, weight 3+12 = 0 mod 5.
```

Thus every eligible cross graph-edge covers total weight zero. Exact
two-fold coverage of every `L`-edge would instead have weight

```text
2 * 14 * (1+3+4) = 224 = 4 mod 5,
```

a contradiction. The prism model therefore does not lift through the
global exact-two support identity.

This modular obstruction is specific to the diagnostic object. It does not
exclude other 7-regular complements, point families containing size-three
points, the full `n3=42` equality case, or the target.

## Safe next obligation

The fixed-point identity, which is absent from the generalized Wave 11 local
list, now excludes size-three points. Any complete Wave 12 exclusion must
still reject the remaining all-size-two branch. The most immediate exact
layer is:

1. every `L`-edge receives exactly two selected cross graph-edges;
2. the resulting graph `H` on those graph-edges is simple, triangle-free,
   and has nonzero degrees in `{4,6,8,10}`;
3. the fixed-point sums hold for every point object; and
4. the selected actual graph edges respect `lambda=1` and `mu=2` saturation,
   including inactive original vertices.

The five normalized branches with local lower bound 48 cannot realize
`n3=42`; the remaining branch indices are `1,2,3,6,7,9,11`. This is only a
conditional search split. No branch is solved, and the target remains
`UNKNOWN`.
