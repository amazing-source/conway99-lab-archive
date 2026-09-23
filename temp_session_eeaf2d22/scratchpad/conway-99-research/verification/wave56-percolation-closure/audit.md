# Wave 56 independent audit

Verdict: **VERIFIED**, conditional and scoped.

This audit verifies the cited closure classification, its target-parameter
specialization, the stated incidence identities and inequalities, and the
finite rooted endpoint census. It does not verify the existence or
nonexistence of `srg(99,14,1,2)`, complete any of the 35 local profiles, or
improve the global upper bound `n3<=4158`.

## Independence

The verifier froze `protocol.md` and upstream hashes before opening the Wave
56 discovery package. `independent_check.py` imports no discovery module and
reconstructs its graphs, masks, multicovers, and formal label actions from
definitions. Comparison with `exact-results.json` occurs only after the
independent result has been built.

The primary PDF was retrieved from the Australasian Journal of Combinatorics
and hashed as

```text
3bcbb35f6bac46bf943970fa53918fa2b126684375a325efff308371e785fb0f
```

The relevant source statements are:

- Lemma 4.9: a 2-bootstrap closure in a strongly regular graph is
  `K_(lambda+2)`, an irregular `(lambda,mu)`-graph, or a strongly regular
  graph with the same `lambda,mu`;
- Theorem 4.8: the irregular alternative requires `mu=0` or `mu=1`;
- Theorem 4.19: the published target-specific statement gives the 231
  `K3 square K3` bound and the percolation equivalences.

## Closure classification and parameter arithmetic

For a nonedge seed in a hypothetical `srg(99,14,1,2)`, the complete `K3`
branch is impossible and `mu=2` excludes the irregular branch. A proper
closure must therefore be an `srg(n',k',1,2)`. The standard parameter
equation gives

```text
n' = 1 + k' + k'(k'-2)/2 = 1 + k'^2/2.
```

Thus `k'` is even. For `2<=k'<=14`, the restricted-eigenvalue
discriminant is `4k'-7`. Independent exact multiplicity arithmetic leaves
only degrees `2,4,14`, corresponding to orders `3,9,99`. The degree-two
case is the excluded `K3`; the degree-four case is the unique
`srg(9,4,1,2)`, reconstructed and checked as the 3-by-3 rook graph; the
degree-fourteen case is the ambient target. Hence the claimed nonedge
closure dichotomy is correct:

```text
all 99 vertices, or an induced K3 square K3.
```

No target-graph transitivity or other automorphism is used.

## Channel and closure double counts

There are

```text
C(99,2) - 99*14/2 = 4158
```

nonedges. Each nonedge produces two opposite-tip channels. An induced
`N3` has exactly two central-channel nonedges, while a triangular prism has
six. Therefore

```text
2*4158 = 2*n3 + 6*P,
n3 + 3*P = 4158.
```

A terminology trap was tested explicitly: the six-vertex `N3` has six
nonedges that percolate inside that small graph, but only two of them are
the central diagonals counted by the channel incidence. The discovery uses
the central-channel multiplicity two, so its identity is correct.

The rook graph has 18 nonedges, six induced prisms, and no induced `N3`.
It is closed in the ambient target: an outside vertex with two rook
neighbors would exceed the already saturated `lambda` or `mu` common-
neighbor count of that pair. Every rook nonedge closes to all nine rook
vertices. Consequently, closure/nonedge incidence is bijective and

```text
R = 18*H.
```

Each rook closure supplies six prisms. A prism cannot lie in two distinct
rook closures, because those closures would share a nonedge and hence be
the same closure. Thus

```text
6*H <= P.
```

The remaining claims follow exactly:

```text
R = 18H <= 3P = 4158-n3,
S = 4158-R >= n3.
```

Equality `R=3P` is equivalent to `P=6H`, i.e. every prism is accounted for
by a rook closure. The discovery correctly does not assert this in
general.

At `n3=4158`, the first identity gives `P=0`; then `6H<=P` gives `H=0`,
so `R=0` and `S=4158`. Therefore every nonedge percolates at the
prism-free endpoint. This is conditional on the hypothetical target and
does not exclude the endpoint.

## Exact finite census

The independent checker reproduced:

```text
all labeled four-tip graphs                 64
lambda/mu-cap-admissible tip graphs          4
prism-free admissible tip graphs             1
endpoint pair deficits             14*0+12*1+2*2 = 16
allowed endpoint masks                       23
exact pair-deficit multicover profiles        35
formal D4 label-orbits                        11
new wave-three vertices                    8..16
infected vertices after wave three         16..24
```

The exact 23-mask list, all 35 multiplicity profiles, and the full
11-orbit partition agree with the discovery artifact. The arity histogram
also agrees:

```text
(x2,x3,x4): multiplicity
(16,0,0): 1
(13,1,0): 8
(10,2,0): 16
(7,3,0): 8
(4,4,0): 1
(10,0,1): 1
```

Every profile satisfies

```text
x2 + 3*x3 + 6*x4 = 16,
```

because a mask of size `r` covers `C(r,2)` pair deficits. All profiles also
pass the immediate visible common-neighbor caps between new vertices and
the remaining degree caps at the eight rooted vertices.

`D4` is used only to relabel the formal four-cycle and its named tips. The
checker applies all eight label permutations and confirms that the exact
profile set is invariant. This is not an automorphism assumption about a
completed target graph.

## Hostile tests and boundary

The test suite rejects altered multiplicities `17H`, five prisms per rook,
three central seeds per `N3`, and five central seeds per prism. It also
checks exact graph parameters, all 64 tip masks, the complete profile list,
the orbit partition, the pair-deficit equation, profile-level visible caps,
and endpoint arithmetic.

The 35 profiles are exact solutions only to the stated local multicover.
They do not assign edges among wave-three vertices, finish their degrees,
provide later common neighbors, synchronize different seeds, or complete a
99-vertex graph. The discovery states this limitation and does not promote
the profiles to constructions. Global completability remains `UNKNOWN`.

## Final status

- Source classification and scoped use: `VERIFIED`.
- Target parameter/eigenvalue census: `VERIFIED`.
- `n3+3P=4158`, `R=18H`, `6H<=P`, `R<=3P`, `S>=n3`:
  `VERIFIED`.
- Exact 64-tip and 35-profile census: `VERIFIED`.
- Implicit target symmetry: none found.
- Profile completability: `UNKNOWN` and not claimed.
- Target existence, endpoint exclusion, strict upper-bound improvement, and
  novelty: `UNKNOWN` / not obtained.

