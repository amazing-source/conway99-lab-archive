# Hostile human-proof audit: Wave 19 `m=27` residual

## Verdict

| item | verdict | status boundary |
|---|---|---|
| reconstruction of the `r=20`, `m=27` residual | **PASS** | conditional on the already audited active-triangle framework |
| triangular-prism case for `J` | **PASS / EXCLUDED** | human contradiction |
| `J=K3,3` case | **PASS / EXCLUDED** | human contradiction, after supplying the omitted grid-injectivity lemma |
| complete Wave 19 equality exclusion | **UNKNOWN here** | the separate `m=30` residual is outside this audit |
| Conway-99 | **UNKNOWN** | no target resolution is claimed |
| novelty | **UNKNOWN** | no novelty conclusion is claimed |

The terse candidate arguments are sound only after distinguishing two facts
that were both informally called “0-or-2”:

1. **local crossing rule:** after deleting a common active label, every
   remaining row and column of an actual-edge `L`-crossing has degree zero or
   two; and
2. **global witness multiplicity:** an `L`-edge joins two graph-triangles
   inducing an `N3`, so it has exactly two original graph cross-edges.

The local rule alone does not forbid three different rectangles from
witnessing one `L`-edge. Both case contradictions use the global fact.

```yaml
role: verifier
date_utc: 2026-07-23T14:47:15Z
git_commit: d4e8b9df7800ec1aeda599f2bd90f49cf75d8d81
claim_label: DERIVED
audit_verdict: PASS_FOR_CONDITIONAL_M27_RESIDUAL_EXCLUSION
scope: >-
  Hostile proof-only audit of both simple-cubic possibilities for the six
  size-three points in the conditional Wave 19 r=20, m=27 residual.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  CONJECTURE.md: 7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58
  agents/2026-07-22-wave7-triangle-side-incidence.md: 7b4693420eae7e6f13ce0d66c786424c18863a1b1c350da83097f8e982ebe324
  verification/2026-07-23-wave15-global-lift-audit.md: edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036
  agents/2026-07-23-wave16-n3-51-structural.md: 95d04a774397332417c9613718fe6699a5392ef5222fef1cfa00b12e2860af3f
  verification/2026-07-23-wave16-n3-51-structural-audit.md: 99203a15db2646a759edbb2241eb4bd5e6001733ac862952c9db57446c58ead6
  agents/2026-07-23-wave19-n3-60-structural.md: b2f90af07f34a6525ea35cdf4d392d95aea10fc319633cd17037d00145690744
  verification/2026-07-23-wave19-n3-60-structural-audit.md: f6f318aa187fe5790a14dcbf7eeded7c296b1d6734c710b4569ede690e0c762a
method: >-
  Reconstruct the indexed-point semantics and prove both cases directly from
  linearity, no-Berge, exact six-regularity, local crossing rectangles, and
  the defining two-cross-edge semantics of L. No computational closure file,
  alternate-frontier file, solver result, or automorphism restriction was
  inspected or used.
command: "none (proof-only audit; SHA-256 computed with Get-FileHash)"
outputs:
  verification/n3-60-closure/2026-07-23-wave19-m27-human-proof-audit.md: >-
    pinned by the adjacent .sha256 sidecar
limitations: >-
  Conditional on the previously audited active H/L/indexed-point framework,
  rather than a fresh derivation from a 99-by-99 adjacency matrix. This
  verifier does not promote its own derived closure to VERIFIED. The m=30
  residual, Conway-99, and novelty are not decided.
```

## 1. Exact premises and their consequences

Assume the conditional `n3=60` profile with twenty active graph-triangle
labels, all having `q=2`. Let

```text
S_u = {active graph-triangle labels containing the original vertex u},
X   = {u : S_u is nonempty}.
```

The audited framework supplies:

1. every active label occurs in exactly three indexed points, namely the
   three original vertices of that graph-triangle;
2. the point family is linear: two distinct indexed points share at most one
   active label;
3. three points which pairwise meet either share one common label or would
   form a forbidden Berge triangle;
4. labels within one point are nonadjacent in `L`, because their
   graph-triangles intersect;
5. every active label has `L`-degree `3q=6`;
6. an actual edge `uv`, after deletion of the possible common label, has an
   `L`-crossing in which every remaining row and column has degree zero or
   two; and
7. the fixed-point identity is

   ```text
   sum_{v adjacent to u} d_H(uv) = 2 sum_{T in S_u} q(T).
   ```

The global witness fact used below follows directly from the definition of
`L`, not from a solver or a residual certificate:

> If `TU` is an `L`-edge, the distinct graph-triangles `T,U` induce an
> `N3`; hence exactly two original graph edges join them. Every occurrence
> of `TU` in the crossing for an actual edge `uv` is precisely one such
> graph edge. Therefore `TU` can occur in exactly two actual-edge crossing
> rectangles.

The minimum-degree step can also be seen directly here. A point of size at
least three has at least six distinct triangle-neighbors. A size-two point
has four triangle-neighbors; its fixed sum is eight, while its endpoint-local
crossings are zero or four, so it has two further positive neighbors. Meeting
crossings at that size-two endpoint are zero, hence the two groups are
disjoint and every point has induced degree at least six.

At `m=|X|=27`, the minimum-degree argument and the target spectral subset
bound meet at equality, so `G[X]` is exactly 6-regular. The incidence total is
`3*20=60`. Since every point has size at least two, the excess over size two
is six. A point of size at least four would already have at least eight
distinct triangle-neighbors, contradicting 6-regularity. Thus the point-size
profile is forced:

```text
21 points of size two, 6 points of size three.            (1)
```

For a size-three point `P`, its three active triangles give exactly six
distinct meeting neighbors, which exhaust its neighbors in `G[X]`. Its
fixed-point sum is `12`. A meeting size-two endpoint has zero crossing. A
meeting size-three endpoint leaves a `2`-by-`2` crossing, which is either
empty or the full four-edge rectangle. Hence `P` has exactly three positive
meeting edges to other size-three points.

Let `J` be this positive-meeting graph on the six size-three points. It is
simple and cubic. Its complement is simple 2-regular on six vertices, hence
is `C6` or `C3+C3`. Consequently

```text
J is the triangular prism or K3,3.                         (2)
```

For later use, a size-two point has fixed sum eight. Every positive incident
crossing has value four and is disjoint at the size-two endpoint. A positive
edge to a disjoint size-three point would give that size-three point a seventh
neighbor, impossible. Therefore the positive edges on the twenty-one
size-two points form a simple spanning 2-factor `R`: every size-two point has
two distinct, disjoint, size-two `R`-neighbors.

## 2. Triangular-prism case

Write the two triangular faces of the prism as

```text
A_0,A_1,A_2     and     B_0,B_1,B_2,
```

with matching edges `A_i B_i`.

Every `J`-edge is a meeting edge. In either triangular face the three points
therefore meet pairwise. No-Berge rules out three distinct pairwise
intersection labels; linearity then forces one common label. Call the two
face labels `alpha` and `beta`. Each active label occurs in exactly three
points, so `alpha` occurs precisely in the three `A_i`, `beta` occurs
precisely in the three `B_i`, and `alpha != beta`. In particular, their
graph-triangles are disjoint.

Fix a matching edge `A_i B_i`, and let `gamma_i` be its unique common label.
After deleting `gamma_i`, the residual pair for `A_i` still contains
`alpha`, and the residual pair for `B_i` still contains `beta`. Positivity
forces the full `2`-by-`2` rectangle, so `alpha beta` is an `L`-edge.
Moreover, the actual edge `A_i B_i` is one cross-edge between the
graph-triangles `alpha` and `beta`.

The three matching edges give three distinct such cross-edges. But an
`L`-edge has exactly two original cross-edge witnesses. Contradiction.

```text
triangular-prism branch: PASS / EXCLUDED.
```

## 3. `K3,3` case

Write the bipartition as

```text
A_0,A_1,A_2     and     B_0,B_1,B_2.
```

For each cross pair, let `t_ij` be the unique active label in
`A_i intersect B_j`. The uniqueness follows from point-family linearity.

### 3.1 Grid-injectivity lemma

The nine labels `t_ij` are distinct. This is not automatic merely from
`J=K3,3`, so it must be proved.

Suppose, for example, that two edges incident with `B_j` had the same label:

```text
t_ij = t_kj = t,     i != k.
```

Then `t` occurs in `A_i,A_k,B_j`, exhausting its three point occurrences.
Choose `l != j` and put

```text
x=t_il,   y=t_kl.
```

Neither is `t`. Also `x != y`: equality to a new label would make
`A_i,A_k` share both `t` and that label, while equality to `t` would give
four occurrences of `t`.

Now inspect the positive edge `A_k B_l`, whose common label is `y`. After
deleting `y`, its residual rectangle contains the pair `t,x`, so positivity
forces `tx` to be an `L`-edge. But both `t` and `x` occur in `A_i`; their
graph-triangles intersect and therefore cannot be adjacent in `L`.
Contradiction. The transposed argument forbids repetition at an `A_i`.

Finally, one label cannot occur on two vertex-disjoint `K3,3` edges, because
that would put it in four distinct points. Thus all nine `t_ij` are distinct,
and size three now gives

```text
A_i={t_i0,t_i1,t_i2},     B_j={t_0j,t_1j,t_2j}.          (3)
```

### 3.2 Exact coverage of the grid `L`-edges

Take `t_ij,t_kl` in different rows and different columns. The positive
rectangle for `A_i B_l` contains this label pair, as does the positive
rectangle for `A_k B_j`. Thus it is an `L`-edge with two distinct original
cross-edge witnesses. The global witness multiplicity says these two already
exhaust it.

For fixed `t_ij`, the four different-row/different-column grid labels are
therefore four `L`-neighbors, each already covered twice. Grid labels in the
same row or column meet at `A_i` or `B_j` and are not `L`-neighbors. Since
`d_L(t_ij)=6`, exactly two further `L`-neighbors remain, both outside the
grid. Denote them by `p,q`.

### 3.3 The forced duplicate endpoint pair

The label `t_ij` occurs in the two size-three points `A_i,B_j`. Its third
point, call it `e`, must therefore be one of the twenty-one size-two points.
Let `f,g` be the two distinct `R`-neighbors of `e`.

The positive size-two crossings `ef` and `eg` are full `2`-by-`2`
rectangles. Hence both endpoint labels of each of `f` and `g` are
`L`-neighbors of `t_ij`.

No endpoint can be one of the four grid `L`-neighbors of `t_ij`: each such
grid pair already has its exact two witnesses from Section 3.2, whereas
`ef` or `eg` would be a third, distinct original edge. Same-row and
same-column grid labels are not `L`-neighbors at all. Consequently all four
endpoint appearances from `f` and `g` lie in the two-label set `{p,q}`.

Each size-two point contains two distinct labels, so

```text
f={p,q}=g.                                                (4)
```

This is impossible in both relevant senses:

- `R` is simple and `e` has two distinct neighbors, so `f` and `g` cannot be
  the same indexed point; and
- two distinct indexed points cannot both contain `p,q`, because that
  violates point-family linearity (equivalently, two graph-triangles would
  share two original vertices and one graph edge would lie in two
  triangles).

Therefore

```text
K3,3 branch: PASS / EXCLUDED.
```

## 4. Hostile findings and exact boundary

1. **The grid sentence needed proof.** `K3,3` by itself permits repeated
   edge labels. The positive rectangle on an opposite corner is what rules
   them out.
2. **Local and global “0-or-2” are not interchangeable.** Local row/column
   parity produces the rectangles; the definition of `L` as an induced
   `N3` supplies the exact global multiplicity two.
3. **An abstract 2-factor is insufficient by itself.** The endpoint-pair
   contradiction also needs disjoint positive size-two crossings and
   point-family linearity.
4. **No hidden automorphism is used.** The labels of the prism and `K3,3`
   are arbitrary; only their elementary graph structure is used.
5. **No target status inflation.** This audit closes only the conditional
   Wave 19 `m=27` residual at label `DERIVED`. The separate `m=30` residual,
   the Conway-99 existence question, and novelty remain `UNKNOWN` here.
