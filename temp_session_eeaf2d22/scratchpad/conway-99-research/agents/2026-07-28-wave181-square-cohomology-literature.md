# Wave 181 square-cohomology literature audit

## Verdict

`UNKNOWN`.

No checked primary theorem turns the Wave 181 alternating square relations
into an unsigned vertex-potential representation.

## Exact partial-quadrangle identification

The hypothetical graph is the point graph of

```text
PQ(2,6,2).
```

Mohammadian and Tayfeh-Rezaie record the standard partial-quadrangle
parameter formula; substituting `(s,t,mu)=(2,6,2)` gives
`(99,14,1,2)`.

Makhnev and Nirova's low-`t` classification explicitly retains a graph with
these parameters among its exceptional possibilities.  It supplies
automorphism restrictions, not existence, nonexistence, or homology of a
filled triangle--square complex.

Primary sources:

- A. Mohammadian and B. Tayfeh-Rezaie,
  [*Star Complements in Strongly Regular Graphs: Old and New*](https://arxiv.org/abs/1303.0473).
- A. A. Makhnev and M. S. Nirova,
  [*On Graphs of Partial Quadrangles with Triads*](https://www.mathnet.ru/eng/al161).

## Rectagraph and generalized-quadrangle mismatch

A rectagraph is connected and triangle-free, with every 2-arc in a unique
quadrangle; equivalently `a_1=0,c_2=2`.  The Conway-99 target has
`a_1=lambda=1` and 231 edge-triangles.  Cube-cover results for rectagraphs
therefore do not apply.

Generalized-quadrangle cover theorems assume an actual `GQ(s,t)`.  The
present object is a proper partial quadrangle with `mu=2<t+1=7`, and an
incidence-geometric cover is not automatically a topological cover of the
2-complex obtained by filling point-graph triangles and induced squares.

Primary sources:

- Alice Devillers, Wei Jin, Cai Heng Li, and Cheryl E. Praeger,
  [*Locally Triangular Graphs and Rectagraphs with Symmetry*](https://doi.org/10.1016/j.jcta.2015.01.006).
- John Bamberg and Joseph A. Thas,
  [*Covers of Generalized Quadrangles*](https://biblio.ugent.be/publication/8589083).

## The signless differential is not ordinary cohomology

Ordinary cellular cohomology uses the oriented coboundary

```text
(delta p)(u->v)=p_v-p_u.
```

The hoped-for expression `ell_uv=p_u+p_v` is the transpose of the
**unsigned** vertex--edge incidence matrix.  Switching sums to differences
by vertex signs requires a bipartite graph.  Here every edge lies in a
triangle.

Equivalently, transport `-1` across each edge has holonomy `(-1)^3=-1`
around a triangle, so in characteristic three it does not extend across a
filled triangle.  The usual theorem "closed on a simply connected complex
implies exact" is therefore not a theorem about this signless differential.

Let `B_edge` be the `99 by 693` unsigned incidence matrix over `F_3`, and
let `Q_square` be the span of the alternating vectors on the 2,079 induced
squares.  Then

```text
ell_uv=p_u+p_v
  iff ell in image(B_edge^T)=(ker B_edge)^perp.
```

The square equations give only `ell in Q_square^perp`.  The precise missing
statement is

```text
Q_square=ker(B_edge).                              (1)
```

Because the graph is connected and nonbipartite,
`rank_F3(B_edge)=99`; equation (1) asks for

```text
rank_F3(Q_square)=693-99=594.
```

No checked theorem derives this rank from the SRG or partial-quadrangle
parameters.

If (1) were proved, triangle-equal labels would collapse: on a triangle,
`p_u+p_v=p_v+p_w=p_w+p_u` forces `p_u=p_v=p_w`, and connectedness makes
every edge label constant.  Thus (1) would contradict the nonconstant
Wave 181 column labels, but (1) remains unproved.

```yaml
role: literature
date_utc: 2026-07-28T23:39:36Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: UNKNOWN
scope: >-
  Applicability of square-complex, rectagraph, partial-quadrangle, and
  generalized-quadrangle cover theorems to the Wave181 checkerboard
  labelling.
inputs:
  - attempts/wave181-c4-conic-equality/package-manifest.sha256
method: >-
  Primary-source theorem and hypothesis audit followed by a direct signed
  versus unsigned cochain comparison.
command: primary-source PDF inspection and exact incidence-rank reduction
outputs:
  - agents/2026-07-28-wave181-square-cohomology-literature.md
limitations:
  - No directly applicable theorem was found.
  - This is not an exhaustive bibliography.
  - No H1 or fundamental-group value is promoted.
  - The endpoint and Conway-99 remain UNKNOWN.
```
