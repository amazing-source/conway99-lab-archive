# Wave 2 structural track: endpoint-fiber bijections

```yaml
role: proof_a
date_utc: 2026-07-22T20:32:47Z
git_commit: eb61bf3d89f4af217a4af624b28edc71977a51a0
claim_label: VERIFIED
scope: necessary consequences of a putative rooted srg(99,14,1,2)
automorphism_assumption: none
verification: verification/2026-07-22-wave2-audit.md
limitations: no contradiction; literature novelty unknown
```

Let `a` be one of the 14 root-neighbor coordinates, let `bar(a)` be
its fixed mate, and put

```text
F_a = {residual labels containing a},
W_a = {residual labels containing neither a nor bar(a)}.
```

Then `|F_a|=12`, `B[F_a]` is a perfect matching, and `|W_a|=60`.

## Bijection

For every `w` in `W_a`, the endpoint-profile equation gives exactly two
neighbors of `w` in `F_a`. Those two vertices cannot be adjacent: coordinate
`a` and residual vertex `w` would otherwise be two common neighbors of an
intersecting-label residual edge, whose required residual common-neighbor
count is zero.

Conversely, two nonadjacent vertices `u,v` in `F_a` are intersecting-label
nonneighbors, so they have exactly one common residual neighbor in addition to
the root-neighbor coordinate `a`. The endpoint profiles exclude that residual
neighbor from both `F_a` and `F_bar(a)`, placing it in `W_a`.

There are exactly

```text
binom(12,2) - 6 = 60
```

nonedges of the matching `B[F_a]`. It follows that

```text
w -> N_B(w) intersection F_a
```

is a bijection from `W_a` to the edge set of `K_12` minus a perfect matching.
Equivalently, the bipartite graph between `F_a` and `W_a` is the
vertex-edge incidence graph of that 10-regular graph. It has degrees 10 and 2
and contains no four-cycle.

The proof uses the full residual common-neighbor axioms. Endpoint profiles
alone are insufficient; the verifier produced small profile-only assignments
violating both injectivity and the nonedge-image conclusion.

## Coupled mate fibers

Apply the bijection to both `F_a` and `F_bar(a)`. Each `w` in `W_a` now labels
one edge in each of two copies of `H=K_12-6K_2`. Define the 12-by-12 integer
matrix

```text
R[u,v] = number of w whose F_a edge contains u
                     and whose F_bar(a) edge contains v.
```

Every `w` contributes four incidences, so

```text
sum R[u,v] = 60 * 4 = 240.
```

Because `R` has 144 nonnegative-integer entries, convexity gives

```text
sum binom(R[u,v],2) >= 240 - 144 = 96.
```

Two distinct edges of `H` share at most one endpoint. Therefore each term
counts an unordered pair `w,w'` exactly once. Such a pair has common residual
neighbors `u` and `v`; the exact common-neighbor table forces both opposite
pairs to be disjoint-label nonedges. Hence each root-matched coordinate pair
forces at least 96 distinct residual four-cycles whose opposite fiber vertices
use `a` and `bar(a)`.

Across all seven root-matched pairs this gives at least 672 separation
incidences, not 672 distinct four-cycles: one residual four-cycle may be
separated by more than one root group. The known total of 1,071 residual
four-cycles therefore yields no contradiction.

For the generalized `pair_count=m` scaffold the same convexity calculation
gives

```text
max(0, 4 * (m-1) * (m-3)),
```

which specializes to 96 at `m=7`.
