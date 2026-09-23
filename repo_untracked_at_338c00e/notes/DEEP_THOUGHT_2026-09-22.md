# Deep-thought notes (Claude, 2026-09-22, while the phase-2 exploration workflow runs)

Goal: is there a better route than "symmetry breaking → cube-and-conquer → orderly generation" to decide the involution branch?
Everything below is derived by hand and checked on the k=4 control where indicated. Labels: PROVED / COMPUTED / CONJECTURED.

## 1. Spectral structure of the outer quotient is fully explained by the block sums (PROVED, no new information)
Q_out² + Q_out = R := 12I + 4J − Sh with Sh = M₇ ⊗ J₂, M₇ = A(T(7)) + 2I (T(7) = triangular graph, eigenvalues 10, 3⁶, (−2)¹⁴).
Hence Q_out commutes with R and preserves its eigenspaces: 1 (all-ones), E₂ (6-dim, eigenvalue 2 of R), E₁₂ (35-dim).
On E₂: x² + x = 2 ⇒ eigenvalues ∈ {1, −2}; on E₁₂: x² + x = 12 ⇒ {3, −4}. Traces (tr Q_out = 0, tr Q_out² = 588) force
Spec(Q_out) = {12, (−2)⁶, 3²⁰, (−4)¹⁵}. The condition Q_out|E₂ = −2·I is exactly the Q-block-sum constraints (I) (vectors z_{ij} = f(i)+f(j), Σf = 0),
so it adds nothing to the model. Same phenomenon for S_out (kernel span(C) = S-balance = (I)). The genuine content of the problem sits in the 35-dim
spaces where Q_out and S_out are "two-eigenvalue operators" (3²⁰, (−4)¹⁵): Q_out = 7P_Q − 4I + 2Π_{E₂} + 8J/21 and S_out = 7P_S − 4I + CCᵀ/3 with P_Q, P_S rank-20
projectors — the same "projector/lattice" shape the public repository attacked for ~150 waves at the 231-triangle level without deciding anything.

## 2. Spectrum of the outer graph H of ANY Conway 99-graph (PROVED; involution not needed)
H² + H = 12I + 2J − MMᵀ (M = 84×14 label incidence). Vectors y_f(u) = f(i)+f(j) (Σf = 0; 6-dim) satisfy H y_f = −2 y_f because every u has exactly 2
neighbours on each of its own blocks and 4 on every other block; vectors g(u) = ε(a)+ε(b) with ε antisymmetric in blocks (7-dim) satisfy H g = 0.
With tr H = 0, tr H² = 1008 this forces Spec(H) = {12, (−2)⁶, 0⁷, 3⁴⁰, (−4)³⁰} (the 8 a-priori multiplicity patterns collapse to one).
Checked on k=4 (H = C4: 2, 0, 0, −2 = pattern k−2, (−2)^{m−1}, 0^m with m = 2). Probably known implicitly (senamakel "interlacing-84-vertex-rigidity");
recorded here as a clean statement. Consequence: the involution adds no spectral information at the H level — its content is combinatorial (σ-invariance, D).

## 3. The s=1 / s=0 dichotomy is a natural search skeleton (PROVED structure; search value CONJECTURED, being measured by the workflow)
- Each outer u has exactly 2 edges with |u∩v| = 1 (s=1), one per element of its label; the 84 s=1 edges form, for each inner c, a perfect matching M_c on the
  12 labels containing c; σ maps M_c to M_{c′}. So the s=1 structure = 7 independent matchings of 12-point sets (10395 each before constraints).
- The other 10 edges at u (s=0) lie in outer triangles; the s=0 neighbourhood N₀(u) induces a perfect matching 5K₂ (each s=0 edge u–v lies in a unique
  triangle {u,v,w} and u–w is then also s=0). So the s=0 part is a partial linear space (84 points, 140 lines of size 3, 5 lines per point) with μ-conditions.
- Cubing/orderly variables: the isomorphism TYPE of M_c under the stabiliser of block c (2⁶ ⋊ S₆, order 46 080) — a handful of types (vertical / cross edges);
  then M for the next block modulo the residual stabiliser, etc. This is a far more compact and symmetry-aware case tree than bit-level cubes.
  Caveat (COMPUTED yesterday): fixing the whole neighbourhood of one vertex (12 edges) did not make the SAT instance easy; a cube fixing one M_c (6 edges)
  will not either — the value must come from the count of cubes × per-cube time, to be measured.

## 4. Things that do not help (checked)
- LP/SDP relaxations of degree 2: the spectral/quotient conditions are already satisfiable by real matrices; no infeasibility expected.
- Enumerating D first: perfect matchings on 42 points modulo the group ≈ 10¹⁹ classes.
- "Kneser 2-lift" viewpoint (n₀ ∈ {8,9,10} disjoint-pair neighbours per orbit): suggestive, but no identity beyond the Q-Gram was found.

## 5. Side notes (order 3, asymmetric)
- Order 3 FPF: quotient spectrum {14, 3¹⁸, (−4)¹⁴} (from a₁(g) = 18 ⇒ χ₃(g) = 0, χ₋₄(g) = −1); 6 triangular + 27 independent orbits; the third-party
  hexagon lemma is saturated (see notes/third_party). Remaining angles are the full lifting problem per O3 type (compute-heavy, already pursued publicly).
- Asymmetric: no method; the involution machinery (σ-quotients, D) has no analogue.

## 6. Verdict of this deep-thought pass
No shortcut found. The plan stands, with one refinement: organise cubes / orderly generation around the s=1 matching types (§3) rather than raw variables,
and always run solvers with statistics and symmetry breaking. Whether this changes the picture is an empirical question the workflow is measuring.
