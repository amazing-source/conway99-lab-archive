# Conway-99 — working research memory (2026-09-21)

## Established (with source)
- Existence of srg(99,14,1,2) open (Brouwer `?`; Thakkar–Severini v2 18 Sep 2026; Reimbayev 19 Aug 2026).
- |Aut| ∈ {1, 2, 3}: Makhnev–Minakova 2004 (|G| | 2·3³·7·11, fixed subgraphs of prime-order elements:
  p=2 → single fixed vertex, a_1(t)=14; p=3 → empty or K_3; p=7 → single vertex; p=11 → empty);
  Behbahani (thesis 2009, Thm 4.14 / Table 21) & Behbahani–Lam 2011: NO orbit matrix for p=5,7,11 (all
  admissible fixed-point counts) and for p=3 with fixed points → primes 2,3 only, order 3 fixed-point-free;
  Crnković–Maksimović 2020: orders 6, 9 excluded; Cesarz–Woldar 2025 (computer-free): 2 | |G| ⇒ |G| | 6,
  7 | |G| ⇒ G ≅ Z7 (weaker than B–L for 7). ⇒ Thakkar–Severini's "single-fixed-point Z7 case remains open"
  and the dossier's framing are wrong: order 7 was excluded by computer in 2009/2011.
- Ishida arXiv:2606.29183 (June 2026): trace-rank identity; for Conway-99 gives a_1(x)=18 (order 3, FPF)
  or 6 (Fix=K_3), and recovers a_1(t)=14 for an involution. No exclusion.
- Repo YesterdaysLemon/conway-99-research: rigorous 708 ≤ n3 ≤ 4158 (repo-verified), full order-7 affine
  family (wave 23), three-centre compatibility attempted in wave 206 (unmerged branch; necessary condition
  only), waves 207–212 symbolic rank algebra, status UNKNOWN. Repo waves 69/72 (order 11) are redundant with B–L.
- Reimbayev 2608.19410 census correct modulo 4 typos (see AUDIT_reimbayev_order7.md); adds nothing on n3.

- PRIMARY SOURCE obtained: Makhnev–Minakova, Diskr. Mat. 16:1 (2004) 95–104, DOI 10.4213/dm144 (free on
  mathnet.ru; scratchpad/arxiv/makhnev_minakova_2004.pdf). Theorem 1 verbatim: prime-order g ⇒ Fix(g) is one
  vertex (|g|=2 or 7), empty (|g|=3 or 11), or a triangle (|g|=3). Corollary 1: involution ⇒ |G| | 42 or |G| | 6.
- Makhnev lecture notes (Bielefeld, makhnev.pdf, public): Prop. 2 lists 7 candidate Fix(t) for an involution
  (one vertex; triangle; 3 triangles; vertex+2 triangles; 4 vertices+triangle; n-coclique n=3,5,7; 3×3 grid),
  then "only case (1) makes χ₂(t) = (4α₀+α₁−18)/7 an integer" ⇒ Fix(t) = one vertex (Theorem 1 = M–M).
  Derived structure for the involution: t = σ (flip in every block), u ≁ σu (a₁=14); each outer u is adjacent
  to both members of exactly one σ-orbit D(u), and D is symmetric ⇒ a perfect matching on the 42 outer orbits
  (B_out has one 2 and ten 1's per row); signed quotient S has 10 outer ±1 and 2 inner ±1 per outer row.

- Orbit-level exact model of the involution case (z2_signed/orbit_sat.py, cpsat_orbit.py): variables
  (a,b)=(A[u,v],A[u,tv]) per orbit pair; constraints R/D/I/P exactly equivalent to the srg identity.
  Controls: k=4 SAT + lifted matrix verified as srg(9,4,1,2); k=6 UNSAT instantly (srg(19,6,1,2) does not exist).
  k=14: 666 183 vars / 1.51 M clauses. Sound case split on the double orbit of U0: sib (1,2,1) / one (1,3,0) /
  dis (3,4,0). Runs launched 2026-09-21 17:50: CaDiCaL ×3 (4 h cap, results in result_<case>.json) and
  CP-SAT case none (6 workers, 2 h, result_cpsat_none.json). Earlier probes (S-relaxation CP-SAT 25 min,
  99-vertex CNF) were UNKNOWN. Row-by-row DFS (joint_dfs.py, sout_dfs.py) stalls at rows 2–6: naive DFS infeasible.

- Decisive-ness assessment 18:50: row-fixed instances undecided (CaDiCaL ≥ 30 min CPU ×4; CP-SAT 15 min, 2 477 conflicts only)
  ⇒ neither exhaustive first-row splitting nor generic solving is within reach here. mod-7 structure (S_out−3I nilpotent index 2 on
  35-dim; rank_F7(S−3I) ≤ 22) is consistent with the repo's universal rank_F7(M) ≥ 27 (M ≡ −BᵀR₀B, R₀ = A−3I−4J nilpotent mod 7).
  Plan: overnight batch with native Linux cadical/kissat (Docker image `satbox`) on the 3 case CNFs, 6 threads.

## Tested this session (scope)
- Order-7 census intersected with n3 bounds: nothing new (exact, all n3).
- Literature: Z7 closed since 2009; involution (p=2) never computed by anyone found.

## Open / promising
- Involution case (G = Z2, unique fixed point x): in the rooted reduction the involution is forced to be the
  all-block flip σ ((i,s)↦(i,1−s)); H must be σ-invariant, σ fixed-point-free on the 84 labels, u ≁ σu.
  Equivalent to (B, S): ordinary quotient B (50×50, B²+B−12I=2N) and signed quotient S (49×49, S²+S=12I,
  entries {−1,0,1}, inner block prescribed, W=2S+I satisfies W²=49I). Two probes launched:
  (a) direct σ-invariant SAT/CP-SAT on H (z2_probe/), (b) S-stage relaxation (z2_signed/).
- Order-3 FPF: crowded (ibenarb 103 open types at τ=6; τ=27 excluded by infinityscroll; Lean C3 restriction).
- Asymmetric case: no known method; global searches (SAT/CP-SAT) hopeless per all evidence.

## Deferred
- 84-vertex canonical-augmentation benchmark (dossier rec. 2): low information value; not started.
