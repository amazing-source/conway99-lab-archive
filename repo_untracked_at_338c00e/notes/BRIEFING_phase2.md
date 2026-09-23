# Briefing for phase-2 exploration agents (2026-09-22)

Read this first; then `NOTE_involution_case.md`, `report/conway99_involution_report.tex` (English) or `report/involution_notes_fr.tex`,
`results/BATCH_2026-09-21_overnight.md`, `RESEARCH_MEMORY.md`. Code in `code/z2/` (models, solvers, annealers). Public repository with 240 prior
attempts (waves 1–212) is cloned at `C:\Users\RESEARCHER\AppData\Local\Temp\claude\C--Users-RESEARCHER-Desktop\eeaf2d22-69e1-42a1-97c8-376f05816a6c\scratchpad\conway-99-research`
(read `STATUS.yaml`, `agents/`, `attempts/` if you need what was already tried globally). Primary sources (PDF/TeX) are in
`...\scratchpad\arxiv\` (Makhnev–Minakova 2004, Makhnev lecture, Behbahani thesis, Cesarz–Woldar, Ishida 2606.29183, Reimbayev, Thakkar–Severini).

## The problem
srg(99,14,1,2) (Conway 99-graph): does it exist? Adjacency A must satisfy A² + A − 12I = 2J. Eigenvalues 14¹, 3⁵⁴, (−4)⁴⁴.
Known: |Aut| ∈ {1,2,3} (Makhnev–Minakova 2004; Behbahani–Lam 2011: orders 5,7,11 impossible, order 3 fixed-point-free; Crnković–Maksimović 2020:
no groups of order 6, 9). The **involution branch (|Aut| = 2)** has never been computed by anyone; the order-3 branch is being attacked by
several public projects (ibenarb, infinityscroll, Lundle22, Kuberwastaken); the asymmetric case has no known method.

## Established facts about the involution branch (proved, see the report)
- Involution t fixes exactly one vertex x. Root at x: N(x) = 7 matched pairs (blocks) B_i = {(i,0),(i,1)}; the 84 outer vertices = labels
  {(i,s),(j,e)}, i<j; inner–outer adjacency forced; unknown = the 12-regular outer graph H.
- t = σ = flip of every block: σ{a,b} = {a′,b′}, fixed-point-free on labels. No vertex outside N(x) is adjacent to its image (u ≁ σu).
- D(u) := N(u) ∩ N(σu) is a σ-orbit; D is a perfect matching on the 42 σ-orbits of outer vertices. Each outer u is adjacent to both members of
  exactly one orbit (Q=2) and to exactly one member of ten orbits (Q=1).
- Orbit-level exact model: for orbits U≠V, bits (a_UV, b_UV) = (A[u,v], A[u,σv]) (symmetric). Constraints (R) Σ(a+b)=12; (D) exactly one (1,1);
  (I) for each inner c: #neighbours of u containing c = 1 if c∈u or c′∈u else 2; (P) Σ_W(a_UW a_VW + b_UW b_VW) + a_UV = 2 − |u∩v| and
  Σ_W(a_UW b_VW + b_UW a_VW) + b_UV = 2 − |u∩σv|. Exactly equivalent to the srg identity. 1722 primary bits.
- Quotients: Q (50×50) with Q² + Q − 12I = 2N; Q_out = Γ₁ + 2D, Q_out² + Q_out = 12I + 4J − Sh (Sh = shared blocks).
  Signed S (49×49): S² + S = 12I, spectrum 3²⁷,(−4)²²; S_out (42×42, entries 0/±1, ten nonzeros per row), Cᵀ S_out = 0 (CᵀC = 12I₇),
  S_out² + S_out = 12I − CCᵀ, spectrum 0⁷ 3²⁰ (−4)¹⁵; (S_out + 4I − CCᵀ/3)/7 is a rank-20 projector.
- F₂ theorem: Γ̄ (single-adjacency graph mod 2) satisfies Γ̄² + Γ̄ = NbNbᵀ and rank_F2(Γ̄ + NbNbᵀ) = 20 (Nb = orbit/block incidence).
- Label symmetry group: 2⁷ ⋊ S₇ (order 645 120) acts on labels, commutes with σ; acts on the orbit-level variables by permutation with an a/b swap
  where the representative gauge flips. Sound case split: D(U₀) ∈ {sibling (1,2,1), one shared block (1,3,0), disjoint (3,4,0)}.

## What has been tried on the involution branch (all inconclusive)
- CNF (666 183 vars, 1.51 M clauses) with CaDiCaL/Kissat: 8 h each on 3 cases (+2 subcases): all UNKNOWN. CP-SAT 25 min on the signed
  relaxation: UNKNOWN. With the whole row of U₀ fixed: CaDiCaL ≥30 min ×4 undecided; CP-SAT 15 min UNKNOWN (only 2 477 conflicts: propagation is slow).
- Row-by-row DFS (entry by entry, with balance/Gram bounds): stalls at rows 2–6. Candidate rows per orbit are ~10⁷–10⁹: enumeration infeasible.
- Simulated annealing (bit-flip; structured Q_out = Γ + 2D moves): plateau at energy ≈ 1550–1650, dominated by (P) violations.
- No symmetry breaking was used in any run. No solver statistics were collected (quiet mode). No cube-and-conquer. No orderly generation.

## Constraints for your experiments
Python: `C:\Users\RESEARCHER\AppData\Local\Temp\claude\C--Users-RESEARCHER-Desktop\eeaf2d22-69e1-42a1-97c8-376f05816a6c\scratchpad\.venv\Scripts\python.exe`
(numpy, sympy, python-sat with cadical195, ortools). Docker Desktop is currently stopped; `Start-Process 'C:\Program Files\Docker\Docker\Docker Desktop.exe'`
then wait for `docker info`; image `satbox` has native kissat/cadical (mount the CNF directory as /work). Keep the machine under ~70% CPU:
at most ONE solver process per agent, each run ≤ 10 minutes. Regenerate CNFs with `code/z2/orbit_sat.py --m 7 --case <sib|one|dis> --out file.cnf`
(2 s). Controls: `--m 2` must be SAT (lift verifies srg(9,4,1,2)), `--m 3` must be UNSAT.
Do not claim anything you did not verify; label every statement as PROVED / COMPUTED / CONJECTURED / CITED with the source.
