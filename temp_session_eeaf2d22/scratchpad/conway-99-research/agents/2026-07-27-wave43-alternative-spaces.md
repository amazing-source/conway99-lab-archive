# Wave 43 alternative-space assessment

```yaml
role: orchestrator
date_utc: 2026-07-27T16:02:00Z
git_commit: e28f90464d00b98d37672b0b2b23dba15399a6f2
claim_label: DERIVED
scope: qualitative route comparison plus exact order-seven endpoint count witness
inputs:
  - attempts/wave43-seven-deck-endpoint/exact-results.json
  - attempts/wave43-joint-completion/pairing-reduction.json
method: compare which reformulations add genuinely new constraints, then execute the smallest exact alternative
outputs:
  - attempts/wave43-seven-deck-endpoint/exact-results.json
limitations:
  - route rankings are research judgments, not mathematical theorems
  - the order-seven witness is a count vector, not a graph
  - Conway-99 and novelty remain UNKNOWN
```

## Decision

The useful question is not whether the problem can be translated, but whether
the translation creates constraints that were absent in the graph model.
Several attractive languages merely rename the same local equations. The
following ranking favors routes with a smaller exact object and a realistic
certificate boundary.

## 1. Three-index design and transportation polytope

**Priority: highest immediate.**

For the canonical rank-33 core, a full outside incidence matrix is a
three-partite perfect hypermatching of sixty pairs in each fibre. The exact
Gram equations turn this into a sparse binary transportation problem:

```text
45032 binary variables
180 pair-partition equalities
432 cross-fibre concurrence equalities
675480 nonzeros.
```

This is genuinely smaller than the direct SAT cardinality expansion and is
well suited to MILP, branch-and-price, exact cover, and polyhedral cuts.
A feasible point supplies sixty explicit blocks and can be checked without a
solver. A negative result needs a proof trace or exact cutting-plane/Farkas
certificate.

The limitation is structural: even a full `B` still needs an eight-regular
outside graph `H` satisfying the mixed and quadratic equations.

## 2. Rooted flag or finite moment matrices

**Priority: highest next proof lane.**

The ordinary order-seven deck has now been tested exactly at the prism-free
endpoint. It is feasible with

```text
h11=16632
99 positive classes among 208
all three prism-containing seven-classes zero.
```

Thus unrooted counts through order seven are too coarse. The next count-space
attack should not simply add more published scalar identities. It should add
overlap information by fixing a vertex, edge, or triangle and forming a
positive-semidefinite moment matrix of rooted flags. A negative semidefinite
program can potentially be converted to an exact rational sum-of-squares or
Farkas certificate.

Order-eight unrooted deletion variables are a useful control, but rooted flags
are more likely to expose the missing compatibility between overlapping local
blocks.

## 3. Polynomial calculus on the 33 endpoint cases

**Priority: medium-high.**

The rooted adjacency constraints are quadratic Boolean equations. The
prism-free condition adds squarefree monomial exclusions. Instead of CNF
resolution, one can seek a bounded-degree Nullstellensatz or polynomial
calculus refutation over `F_2`, `F_3`, or `F_7`.

This is a genuinely different proof system. Symmetry reduction within each
frozen branch and linear algebra on low-degree monomials may derive relations
that unit propagation misses. A successful result has a compact algebraic
certificate. The obstacle is monomial growth over 3,486 primary edge
variables, so the first experiment should use branch 15 and degree at most
three or four.

## 4. Two-block rank and Schur moment coupling

**Priority: medium-high, mathematically decisive if found.**

One local 39-point block cannot contradict the global rank ceiling 44. The
needed bridge is a theorem that two or more overlapping blocks contribute
enough independent quotient directions after the universal three-dimensional
vertex-star kernel is removed.

Raw overlap signatures are known to survive and give only rank 35. A useful
version must impose pairwise column Gram equations, `BH`, and
`B^T B+H^2`, or encode a complete overlap class. This route is difficult but
would convert the new endpoint rank-28 theorem into a global contradiction.

## 5. Finite orthogonal geometry and code classification

**Priority: medium.**

At the ternary boundary the 231 triangle vectors form a projective
self-orthogonal code and a regular induced set in an orthogonal polar graph.
Basic Delsarte transforms are already nonnegative, so another scalar
eigenvalue bound is unlikely to help. The fruitful upgrade would be a
classification or nonexistence theorem for the exact regular point set,
using triple intersection numbers, complete weight enumerators, or higher
Terwilliger modules.

This is attractive because a classification theorem could be short and
global. It is risky because the ambient polar space is large and no current
constraint is close to equality in a known bound.

## 6. Star complements

**Priority: exploratory only.**

The original graph has spectrum

```text
14^1, 3^44, (-4)^54.
```

Star-complement theory can reconstruct the graph from an induced 55-vertex
complement for eigenvalue 3 or a 45-vertex complement for eigenvalue -4.
For a fixed complement, remaining vertices become a clique problem in a
compatibility graph.

The present obstacle is that no small canonical star complement is known;
enumerating the complement is almost as hard as enumerating the graph. This
route becomes competitive only if the endpoint forces a highly constrained
45- or 55-vertex induced subgraph.

## Orchestrator recommendation

Continue the sparse full-`B` construction and independent rank-28
verification now. In the next proof wave, prioritize a rooted
triangle-flag moment matrix or low-degree polynomial-calculus experiment on
branch 15. Keep star complements as a scouting lane, not the main search.

No route in this report resolves the endpoint or Conway-99, and no novelty or
priority claim is made.
