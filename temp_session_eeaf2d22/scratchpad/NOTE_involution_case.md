# The involution case of Conway's 99-graph: exact reduction, new necessary conditions, first computations
(working note, 2026-09-21; all statements below are either cited to a primary source or derived here with proof sketches; computational claims point to reproducible scripts in `scratchpad/z2_signed/`)

## 1. Status of the symmetry programme (verified against primary sources)
Let Γ be a putative srg(99,14,1,2), G = Aut(Γ).
- Makhnev–Minakova 2004 (Diskr. Mat. 16:1, 95–104, DOI 10.4213/dm144; verbatim Theorem 1): for g ∈ G of prime order, Fix(g) is
  one vertex (|g| ∈ {2,7}), empty (|g| ∈ {3,11}) or a triangle (|g| = 3). |G| divides 2·3³·7·11.
- Behbahani 2009 (thesis, Concordia; Theorem 4.14, Table 21) = Behbahani–Lam 2011: no orbit matrix exists for p = 5, 7, 11
  (all admissible fixed-point counts) nor for p = 3 with fixed points ⇒ prime divisors of |G| are 2 and 3, order 3 is fixed-point-free.
  p = 2 was **not** computed (the table starts at p = 3).
- Crnković–Maksimović 2020: no G of order 6 or 9. Cesarz–Woldar 2025 (computer-free): 2 | |G| ⇒ |G| | 6; 7 | |G| ⇒ G ≅ Z7.
- Hence |G| ∈ {1, 2, 3}. The order-3 (fixed-point-free) branch is being attacked by several public projects; the **involution branch has
  never been computed**. Thakkar–Severini (arXiv:2608.11211v2) and the Deep-Research dossier call the one-fixed-point Z7 case "open";
  this is a misreading — it was closed at the orbit-matrix level in 2009/2011.
- Ishida (arXiv:2606.29183) recovers a₁(t) = 14 for an involution t from his trace–rank identity (no exclusion).

## 2. Rigidity of the involution (elementary, with proofs)
Let t ∈ G be an involution; Fix(t) = {x} (M–M). Root Γ at x: N(x) = 7K₂ with blocks B_i = {(i,0),(i,1)}; the 84 outer vertices
are the labels {(i,s),(j,e)}, i<j (Thakkar–Severini reduction; every inner–outer adjacency forced). Unknown: the 12-regular outer graph H.
(a) t preserves N(x) and its matching and fixes no inner vertex. If t swapped two inner vertices a,b of different blocks it would fix the
    label {a,b} (an outer vertex) — impossible. Hence t = σ := the flip (i,s) ↦ (i,1−s) in every block, and on labels σ{a,b} = {a′,b′}.
(b) No vertex u ≠ inner is adjacent to tu: if u ~ tu, the edge {u,tu} is t-invariant, so the unique common neighbour of u and tu
    (λ = 1) is t-fixed, hence equals x, hence u ∈ N(x). Thus a₁(t) = 14 exactly (as in M–M / Ishida), and no outer u is adjacent to σu.
    Consequently χ₃(t) = (6/11)·1 + (9/77)·14 − (2/77)·84 = 0 and χ₋₄(t) = 0.
(c) For outer u: N(u) ∩ N(σu) = {v, σv} is a σ-orbit (μ = 2, σ-invariance, and (b)); write D(u) = {v,σv}. D is symmetric, so
    D is a **perfect matching on the 42 σ-orbits of outer vertices**. Each outer vertex is adjacent to both members of exactly one orbit.
(d) Orbit-level exact model. For orbits U ≠ V with representatives u,v let (a_UV, b_UV) = (A[u,v], A[u,σv]); the pair is symmetric in U,V.
    Then A² + A − 12I = 2J ⇔ (R) Σ_V(a+b) = 12; (D) exactly one V with a=b=1; (I) for every inner c: #{H-neighbours of u containing c}
    = 1 if c ∈ u or c′ ∈ u, else 2; (P) for U≠V: Σ_W(a_UW a_VW + b_UW b_VW) + a_UV = 2 − |u∩v| and Σ_W(a_UW b_VW + b_UW a_VW) + b_UV = 2 − |u∩σv|.
    (Proof: enumerate the pair types of the 99 vertices; inner pairs are forced; the four pairs (u,v),(u,σv),(σu,v),(σu,σv) reduce to two by σ.)
(e) Quotients. Ordinary quotient Q (50×50, orbits x, A_i, U): Q² + Q − 12I = 2N; on outer orbits Q_out = Γ₁ + 2D with Γ₁ 10-regular,
    Q_out² + Q_out = 12I + 4J − Sh (Sh_UV = number of shared blocks, Sh_UU = 2). Signed quotient S (49×49, basis e_u − e_σu):
    S² + S = 12I exactly, spectrum 3²⁷,(−4)²²; inner block −I₇, inner–outer block C (C^T C = 12I₇), S_out ∈ {0,±1}, ten nonzeros per row,
    C^T S_out = 0, S_out² + S_out = 12I − CC^T; hence Spec(S_out) = 0⁷ ∪ 3²⁰ ∪ (−4)¹⁵ and (S_out + 4I − CC^T/3)/7 is a rank-20 projector.

## 3. A new exact necessary condition from the 2-adic module structure (proof sketch)
E₃ = (4I + A)/7 − 2J/77 and E₋₄ = (3I − A)/7 + J/63 are 2-integral, so Z₂⁹⁹ = L₁₄ ⊕ L₃ ⊕ L₋₄ as Z₂[⟨t⟩]-lattices (ranks 1, 54, 44).
Each L_θ is a direct summand of the permutation lattice Z₂⁹⁹ (E_θ commutes with t), hence a p-permutation lattice for the 2-group
⟨t⟩, hence a permutation lattice (Broué 1985: for a p-group every p-permutation lattice over Z_p is a permutation lattice),
i.e. L_θ ≅ Z₂^{a_θ} ⊕ Z₂[C₂]^{c_θ} with a_θ = tr(t|L_θ) = χ_θ(t). By §2(b), χ₃(t) = χ₋₄(t) = 0. Therefore **L₃ ≅ Z₂[C₂]²⁷ and L₋₄ ≅ Z₂[C₂]²² are free**. Reducing mod 2 on the anti-fixed
lattice M = (1−t)Z₂⁹⁹ (in which A acts as S) gives rank_F₂(S mod 2) = 27, i.e. with Γ̄ := Γ₁ mod 2 (the 10-regular "single" graph on the
42 orbits) and Nb = the 42×7 orbit/block incidence:
      rank_F₂(Γ̄ + Nb Nbᵀ) = 20,  and (from the mod-2 Gram identities)  Γ̄² + Γ̄ = Nb Nbᵀ  over F₂.
Consequently K := Γ̄² is a symmetric idempotent of rank exactly 20 with K Nb = 0, and Γ̄ = K + Nb Nbᵀ. The rank statement is not
implied by the pairwise counting identities (which only give K² = K and rank K even); it is genuinely extra information.

## 4. Computations (all reproducible; controls included)
- `orbit_sat.py` (CNF, pysat/CaDiCaL) and `cpsat_orbit.py` (OR-Tools CP-SAT) implement (d) for general k=2m.
  Controls: k=4 → SAT, lifted 9×9 matrix verified as srg(9,4,1,2) (Paley(9) has such an involution); k=6 → UNSAT at once
  (srg(19,6,1,2) does not exist). k=14: 1722 primary variables, 666 183 CNF variables, 1.51 M clauses.
- Sound case split on the double orbit of the reference orbit U₀=(1,2,0): D(U₀) ∈ {(1,2,1) sibling, (1,3,0) one shared block,
  (3,4,0) disjoint} (all other choices are Stab(U₀)-equivalent; |Stab(U₀)| = 15 360).
- Results: S-relaxation (49×49 signed quotient) CP-SAT 25 min: UNKNOWN. Joint model, whole row of U₀ fixed to a random valid
  neighbourhood: CaDiCaL undecided after ≥ 30 min CPU on 4 instances (so an exhaustive first-row case split, ~10⁴–10⁵ cases, is
  out of reach with this encoding). Three global CaDiCaL runs (sib/one/dis) launched 17:50; see result_*.json.
  A timeout is not evidence either way.

## 5. Assessment and what would settle the branch
The involution branch is fully rigid and reduces to a 42-orbit problem with strong algebraic structure (two coupled quotients with
prescribed spectra, a perfect matching D, and the F₂-rank invariant of §3). Generic SAT/CP-SAT does not decide it in minutes/hours.
A decision would need an orderly generator on the 42 orbits with (i) eigenvalue interlacing of the partial symmetrized quotient
against {14, 3²⁷, (−4)²²}, (ii) the D-matching and block constraints, (iii) the F₂ rank invariant as a late filter, and the
label group 2⁷⋊S₇ (order 645 120) for isomorph rejection — a well-defined project (days of expert engineering), with a certifiable
outcome either way: "no involutions ⇒ |Aut| ∈ {1,3}", or a Conway 99-graph.
