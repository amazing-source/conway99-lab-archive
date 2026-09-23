# Attempt ledger

Record proof and search attempts here, including failures. Each entry should
state its scope, assumptions, result, evidence label, and the smallest known
obstruction. Do not overwrite failed attempts when a method evolves.

## Wave 15: global lift of the `n3=48` residual

- Scope: the independently audited Wave 14 active-point residual, conditional
  on a putative `srg(99,14,1,2)` with `n3=48`.
- Result: `VERIFIED` conditional equality exclusion, so `n3>=51` and
  `induced_C6_count>=209337`.
- Smallest obstruction: the nonempty active original vertices form an induced
  set of order at most 24 and minimum degree at least six, while the target
  spectrum requires every such set to have order at least 27.
- Independent evidence: `wave15-global-lift/` gives spectral and outside-degree
  moment certificates; `wave15-algebraic/` independently reconstructs the
  spectral route and retained triangle moments.
- Retained failures: active common-neighbor caps and the first two
  triangle-intersection moments do not obstruct the residual; an ambiguous
  algebraic JSON key and a CRLF/public-LF certificate mismatch were repaired
  transparently and re-audited.
- Boundary: this is a necessary count bound, not a proof or counterexample for
  Conway-99; target and novelty remain `UNKNOWN`.

## Wave 16: conditional `n3=51`

- Structural scope: all sixteen `sum q=34` profiles under the audited
  active-triangle framework.
- Structural result: `VERIFIED` conditional equality exclusion, hence
  `n3>=54` and `induced_C6_count>=209340`.
- Smallest obstruction: the four surviving profiles give at most 25 active
  original vertices, endpoint-local crossing arithmetic forces minimum
  induced degree six, and the target spectrum requires at least 27 vertices.
- Computational scope: a separate seven-branch active-local relaxation with
  exact CNF hashes and one raw positive candidate.
- Computational result: `PASS_FOR_CONDITIONAL_ACTIVE_LOCAL_ARCHIVE_ONLY`;
  one proofless UNSAT, five timeouts, and one historical budget stop are
  explicitly non-evidentiary.
- Retained failure: discovery baseline `09c20e6` pinned a transient Wave 15
  audit hash; repair `7530cae` pins the final public input and an independent
  re-audit preserves all historical hashes.
- Boundary: neither lane resolves Conway-99 or establishes novelty.

## Wave 33: rooted extension and rootless motif boundary

- `wave33-rooted-extension/` derives the forced `14+70+15` quotient,
  simple `2-(15,3,2)` O-Q design, exact induced-70 spectrum, and the full
  six-block binary graph-extension criterion. Its 15-test discovery suite
  supplies no satisfying pair and no infeasibility certificate.
- `wave33-rootless-motif/` gives two formal local third-triangle tables
  invisible to the checked fused algebra while changing the common-R3 count,
  plus the actual eight-vertex R2 board with four transversal candidates.
  Its 14-test suite does not prove global realization, motif forcing, or
  motif avoidance. The independent audit narrows the headline to the formal
  `q=2` R2 and bilinear `Q[Gamma]` / `N^T p(A)N` scope.
- `wave33-rooted-construction/` retains an exact hostile O-Q certificate,
  a deterministic search replay, and a bounded MILP record for all `70!`
  assignments of one fixed simple design. The certificate fails ten
  central-notation `F B=2J` entries with squared defect ten and supplies no
  O-O layer. The
  status-1 timeout, heuristic nonhits, and every missing layer are explicitly
  non-evidentiary. Because its input freeze predates the mutable central
  Wave 33 exposition, replay the unchanged 14-test package through
  `verification/wave33-rooted-construction-chronology/`, not directly
  against the integrated root. That clone-independent chronology replays 36
  of 37 verifier cases, separately passes the portable half of the sole
  omitted composite test, and labels the solver-environment half, which
  depends on ignored local files, `NOT_REPLAYED_NONBLOCKING`; it opens zero
  such files and observes zero environment hashes.
- The full correction and nonpromotion chronology is in
  `verification/2026-07-24-wave33-orchestrator-corrections.md`.

## Wave 34: exact rooted formula and rootless actual-incidence continuation

- `wave34-rooted-structural/` records the discovery-side support/SNF,
  projector, and Pb-only 2-factor census candidate. Its five-file manifest
  is frozen; independent verification and a structurally different
  pair-census crosscheck live under `verification/`.
- `wave34-rooted-encoding/` contains the complete labeled CNF publication
  package. The tracked deterministic gzip expands to an 89,546,779-byte raw
  formula with 1,233,001 variables and 4,323,943 clauses. The raw CNF is
  ignored locally; no solver result or proof is claimed.
- `wave34-rootless-global/` contains the candidate local-fibre model,
  restricted factor scan, and partial 45-vertex control. It is not a target
  graph and supplies no global motif-forcing or avoidance result.
- `wave34-current-literature/` freezes the bounded search and six source
  records. No exact unrestricted Wave 34 prior result was found in the
  searched windows, which is not a novelty or openness claim.
- Corrections, failed routes, and the unchanged target wall are collected in
  `verification/2026-07-24-wave34-orchestrator-corrections.md`.

## Wave 35: prism-free upper endpoint

- `wave35-n3-upper-spectral/` records exact endpoint signed-projector, Smith,
  Schur, compression, incidence-scalar, and local-PSD routes. The submitted
  14-test suite and an independent 10-test suite pass, but every tested
  obstruction survives and `n3<=4158` is unchanged.
- `wave35-n3-4158-combinatorial/` records the exact one-triangle
  `3+36+60` incidence reduction, finite restricted block census, one
  pairwise positive control, and failed parity/heuristic/proofless-solver
  routes. It does not construct or exclude a simultaneous block system.
- `wave35-n3-upper-triple-overlap/` records the 84 rooted prism-forbidding
  units, exact reduction from twelve normalized `N3` branches to five,
  deterministic OPB files for four local seed partitions, and every bounded
  solver stop. All timeouts and conflict-budget stops are `UNKNOWN`.

## Wave 36: modular, ternary-polar, and mixed-block restrictions

- `wave36-modular-reflection/` derives reciprocal Smith factors, modular-rank
  constraints, and the characteristic-seven pure-cube ceiling. Its submitted
  11-test suite does not construct a surviving endpoint matrix.
- `wave36-ternary-polar-bound/` converts the endpoint rows into a regular
  induced set of ternary norm-two projective points and checks the exact
  finite orthogonal parameter table. Its submitted 10-test suite leaves the
  square rank-twelve class and all larger allowed ranks alive.
- `wave36-block-compatibility/` derives the mixed block equations, restricted
  individual-column and fixed-pair censuses, component balance, and spectral
  transfer to `H`. Its 10-test suite supplies no simultaneous 60-column
  design.
- `wave36-literature-audit/` freezes the bounded source/query metadata and
  exact Evans substitutions. No search nonhit is treated as novelty evidence.

## Wave 37: endpoint clause catalogs, polar strengthening, and OPB handoff

- `wave36-rooted-branches/` is the delayed publication of the exact
  fixed-triangle `P=0` clause construction. Each surviving parent branch has
  282,774 deduplicated active clauses. The retained branch-4 MiniCard result
  is `BUDGET_UNKNOWN`; the nonterminal 33-case sweep is ignored locally and
  excluded from every claim.
- `wave37-polar-strengthen/` records the projective self-orthogonal ternary
  code consequences, the corrected balanced-degenerate-triple count, and an
  exact characteristic-seven rank-eleven association-scheme test. The
  tempting collinearity shortcut is retained as refuted, and every tested
  rank boundary survives.
- `wave37-proof-producing-endpoint/` publishes a deterministic compressed OPB
  formula for refined branch 15, its metadata, stream audit, parser record,
  test suite, and correction ledger. Parser acceptance is syntax-only. Even
  a future checked `UNSAT` proof for this artifact would close only one of 33
  refined endpoint cases.

No Wave 37 solver telemetry, formula export, finite-field survivor, or bounded
nonhit improves the general interval `708<=n3<=4158`.

## Wave 38: public live-run boundary and exact continuation

- `wave38-solver-harvest/` records a sanitized, read-only snapshot of the two
  inherited live scouts and freezes the exact 33-case, 231-artifact
  proof-producing queue. Both terminal JSON files were absent; current proof
  coverage is `0/33`.
- `wave38-complete-endpoint/` supplies the exact all-prism static schema,
  decoded-candidate oracle, candidate-bound cut catalogs, source-bound cut
  pools, and guarded OPB exporters. The exact residual-only subfamily has
  24,388,892,640 clauses, so the practical route is finite
  solve--cut--check. No target formula was generated or solved.
- `wave38-coclique-rank/` combines a public 13-coclique construction with the
  incidence-projector identity to prove `rank_F7(M)>=13`. A separate verifier
  promotes this scoped implication and leaves 528 arithmetic endpoint rank
  pairs.
- `wave38-higher-order/` derives the signed support-four-cycle imbalance
  200,277, a ternary fixed-triangle rank bridge, and a rank-ten local positive
  control. It exposes simultaneous `B/H` or cross-base compatibility as the
  missing lemma; it does not prove `P>=1`.

All solver activity, partial pools, local controls, and arithmetic survivors
remain nonterminal. The endpoint, upper-bound improvement, Conway-99, and
novelty are `UNKNOWN`.

## Wave 39: edge-local rank, proof shard, and compatibility restrictions

- `wave39-edge-local-rank/` derives the eleven edge-local cycle normal forms
  and the characteristic-seven rank formula
  `25-2*(number of even parts)`. Independent verification promotes the
  universal necessity `rank_F7(M)>=19`.
- `wave39-proof-solver/` exports the `branch15 AND x187=1` OPB shard and
  retains raw, elaborated, and kernel pseudo-Boolean proofs. Independent
  VeriPB replay accepts the raw and kernel proofs. The other polarity shard
  is open, so branch 15 and endpoint proof coverage remain unresolved.
- `wave39-cross-base-rank/` records conditional projection collisions and
  explicit support-four/six dependencies, together with controls refuting a
  universal local rank-twelve shortcut.
- `wave39-simultaneous-bh/` records conditional centered-code and compatible
  `H` overlap restrictions. Its Delsarte transforms are nonnegative and it
  supplies no completion or exclusion.

The Wave 39 packages do not construct a graph, force a prism, close a complete
endpoint case, improve `n3<=4158`, or establish novelty.

## Wave 40: third-fibre rank completion and global edge coupling

- `wave40-rank19-equality/` records the discovery route from the Wave 39
  rank-19 equality type through third-fibre quotient syndromes. It proves the
  conditional stepping stone `n3=4158 => rank_F7(M)>=22`, retains the exact
  `0,4,8,12` matching boundary, and is independently verified.
- `wave40-exact-coupling-model/` extends the third-fibre argument to all
  eleven edge partitions. Its complete subspace certificate and matching
  census give the candidate universal theorem `rank_F7(M)>=25`; a separate
  clean-room implementation promotes that theorem to `VERIFIED`. The
  full-39-block scout is explicitly bounded and non-evidentiary.
- `wave40-edge-type-coupling/` glues the four prism-free edge types into a
  closed incidence complex, exhausts the 4,050 normalized all-`222`
  one-triangle quotients, proves the exact cubic-core Laplacian rank identity,
  and exhausts all `2^18` lifts of one boundary quotient. The resulting
  rank-33 controls survive and do not exclude the endpoint.
- `wave40-rank25-literature/` freezes a bounded primary-source search for the
  exact rank-25 theorem and equivalent formulations. Search nonhits do not
  establish novelty or priority.

Wave 40 raises the verified universal characteristic-seven rank floor from
19 to 25 and reduces conditional endpoint arithmetic from 429 to 330 pairs.
It does not construct a graph, force a prism, close an endpoint case, or
improve the general upper bound `n3<=4158`.

## Wave 43: conditional endpoint rank 28 and alternative-space controls

- `wave43-rank28-motif/` and `wave43-type33-rank2/` exhaust the two local
  rank-27 mechanisms for all four endpoint edge types. A clean-room verifier
  promotes `n3=4158 => rank_F7(M)>=28`.
- `wave43-all-rank33-lifts/` extends the exact component and six-set reduction
  to all 264 canonical rank-33 lifts. Every lift survives.
- `wave43-branch15-two-triangle/` adds 40,800 exact width-four prism cuts to
  branch 15; 34,340 remain active and no probe closes the branch.
- `wave43-joint-completion/` records exact compact CNF and sparse MILP
  formulations for the canonical 45,032-candidate three-way matching.
  Both retained solver runs are `UNKNOWN`.
- `wave43-seven-deck-endpoint/` gives an independently verified exact
  99-support solution of every unrooted count equation through order seven.

The conditional rank theorem removes 16 endpoint arithmetic pairs but does
not exclude `n3=4158`. Count feasibility is a positive control for the
relaxation only, not graph evidence.

## Wave 44: aggregate rooted order-seven control

- `wave44-rooted-flags/` adds every vertex-root, ordered-edge-root, and
  ordered-nonedge-root category equation to the order-seven deck.
- The 170-row system is strictly stronger than the unrooted 81-row system
  but has an exact nonnegative 91-support integer witness at `h11=16632`.
- A floating-point HiGHS `infeasible` report is retained as a refuted
  numerical false negative. Only the exact witness and direct substitution
  are evidentiary.

This closes the aggregate rooted-count lane as a null result. A useful next
step must impose overlapping-subset compatibility, a PSD flag moment matrix,
order-eight variables, or the full simultaneous `B/H` equations.

## Wave 45: positive-semidefinite rooted-flag checkpoint

- `wave45-flag-moment/checkpoint-v1-*` is the immutable discovery checkpoint
  accepted by the clean-room verifier. It contains the exact rooted-moment
  coefficient stream, the two stored-witness attacks, and 17 cuts against 15
  successive exact count witnesses.
- `wave45-flag-moment/README-v1.md`, `replay-v1.py`, and
  `package-manifest-v1.sha256` provide the versioned discovery replay and
  nine-entry package boundary.
- Mutable cutting-plane files and later solver runs in the same directory are
  work in progress and are not part of checkpoint-v1 evidence.

The checkpoint refutes the stored Wave 43 and Wave 44 count vectors, not the
endpoint. Its next solver call timed out, so the full PSD-constrained region
remains `UNKNOWN`.

## Waves 46--49: code, polynomial, and higher rooted moments

- `wave46-f7-code/` records the ordinary characteristic-seven row-code
  consequences and generic positive controls in every rank 28 through 44.
  Independent verification confirms a null obstruction: the distinguished
  projector-row geometry is not captured by the ordinary code constraints.
- `wave47-three-root-moment/` constructs eight exact three-root/two-free Gram
  families. A clean-room verifier reproduces 2,664 exact negative directions
  and 2,657 distinct cuts against the 17 stored witnesses.
- `wave47-branch15-polynomial/` computes the complete stated degree-two
  squarefree Macaulay closure in seven branch-15 windows. Independent replay
  verifies 13 local XOR relations, zero contradictions, zero new unary
  assignments, and the degree-four representation barrier for all 34,340
  active Wave 43 cuts.
- `wave48-conic-moment/` combines the 170 count equations with eleven moment
  families. A clean-room verifier confirms exact affine rank 93, nullity 116,
  and all universal kernels; floating Clarabel/SCS points remain
  non-evidentiary and no exact feasible point or infeasibility witness is
  retained.
- `wave49-five-root-moment/` constructs all 21 canonical five-root/one-free
  Gram families without a target-graph automorphism. Independent comparison
  verifies all 2,520 root relabellings, 42 known-graph controls, and 357 exact
  stored-witness refutations.

These lanes strengthen the finite relaxations and preserve useful failure
information. None solves the complete PSD-constrained count region, closes an
endpoint SAT branch, constructs a graph, or proves `n3<4158`.

## Wave 51: alternative algebra and aggregate controls

- `wave51-global-triple-tensor/` gives an explicit nonnegative symmetric
  triple-count tensor for the five triangle-pair relations. Independent replay
  verifies the aggregate control and refutes its interpretation as an
  association scheme.
- `wave51-seidel-smith/` derives a candidate conditional Smith normal form
  and a symmetric-square rank bound. Its independent verifier corrects the
  discovery spectrum and verifies the unaffected scoped theorem.

Both discovery packages are necessary-condition or relaxation work. Neither
constructs a graph, supplies pair-specific quadruple compatibility, excludes
the endpoint, or improves `n3<=4158`.

## Wave 52: one-root coherent closure

- `wave52-coherent-closure/` derives the forced 19-triangle `3K6` root and
  `B2/C4/D0` cross-sector caps, then applies exact 2-WL to both the partial
  relation structure and a completion-free 163-node incidence lift.
- Explicit integral cap completions survive. Sixty-four canonical
  two-factor-profile diagnostics produce 39 different closure fingerprints,
  proving that completed colors depend on arbitrary local choices.

This is a discovery null result. Independent verification accepts the finite
arithmetic and color refinement only; no graph or improved bound follows.

## Waves 53--55: proof cover, two-root lift, cut correction, and bounded search

- `wave53-proof-cover/` freezes the exact normalized 33-case endpoint cover
  and exports `branch15 AND x187=0`. Its bounded proof-tool transcripts end
  with `UNKNOWN` or `VERIFIED NO CONCLUSION`; none is a terminal proof.
- `wave53-multi-root-wl/` merges two rooted cap systems for relations
  `K,B,C,D`. It derives one forced-true shared candidate in relation `B` and
  exact 2-WL/folklore-3-WL closures. Positive local controls survive in every
  relation.
- `wave53-exact-cut-loop/` records four exact rational witnesses and three
  retained Wave 49 cuts. Its headline that all 128 tested matrices are
  indefinite is refuted by independent replay: eight Wave 45 matrices are
  positive semidefinite, due to a doubled-off-diagonal source defect.
- `wave54-centered-enumerator/` constructs an exact seven-weight formal
  ordinary enumerator satisfying the frozen integral MacWilliams system.
  It is not a realized ternary code.
- `wave55-branch15-remainder-search/` retains the exact solver transcript and
  metadata from a 120-second run on the open branch-15 shard. Exact returns
  `UNKNOWN`; the ignored 488 MB nonterminal proof prefix is not evidence.

The corrected fixed 177-cut rational relaxation and formal enumerator remain
feasible, while endpoint proof coverage remains `0/33`. No graph, endpoint
exclusion, strict upper bound below 4158, or novelty claim follows.

## Waves 56--59: alternative closure, incidence, and spectral spaces

- `wave56-percolation-closure/` derives the nonedge closure dichotomy,
  `n3+3P=4158`, `R=18H`, `6H<=P`, and the exact 23-mask/35-profile endpoint
  multicover. Independent verification accepts the finite conditional scope.
- `wave57-star-complement/` derives correct projector and star-set formulas
  but overstates the live parameter space. Its verifier retains a
  `REFUTED_IN_PART` verdict: prior Wave 36 leaves three live rows and cubic
  wedge counting sharpens the four-cycle ceiling from 89 to 27.
- `wave58-cross-incidence-rank/` combines the corrected rank transfer with
  exact normalized `m=4` and `m=6` component censuses. Independent replay
  verifies the three-row synthesis and all exact-set-versus-bound wording.
- `wave59-incidence-spectral-excess/` recasts the endpoint as a
  `(7,3)`-biregular point--triangle incidence graph and an 18-regular
  triangle graph. It derives exact spectra, distance layers, predistance
  defects, pair-neighborhood Gram rank, and short Ihara cycle counts.
  Independent verification accepts every scoped finite claim.

None of these packages constructs or excludes the simultaneous `B,A_Y`
system. Non-distance-regularity is not nonexistence. The endpoint, strict
upper-bound improvement, Conway-99, and novelty remain `UNKNOWN`.

## Waves 60--63: integer information beyond scalar incidence geometry

- `wave60-c3-incidence-design/` classifies the 18 fibre-preserving
  twelve-vertex component types, all 1,140 triples, 275 safe coordinate
  orbits, and their allowed six-set columns. Its bounded searches are
  `UNKNOWN`.
- `wave61-c3-finite-field/` tests the complete triple set in several finite
  fields and pair-coordinate parity spaces. No triple is eliminated. The
  cubic section is limited to its displayed identities and scalar totals.
- `wave62-terwilliger-sdp/` diagonalizes the one-root signed-edge invariant
  projector SDP and a degree-24 Schur family exactly. All endpoint parameters
  survive.
- `wave63-c3-integer-cone/` stores exact rational pair-cone witnesses for a
  fixed 74-lane stress subset. Every coefficient is at most one, but none of
  the witnesses is a zero-one design.

Independent verification accepts each finite scope, with the Wave 61 wording
correction and Wave 62 tautology-count clarification. Integer and higher-order
compatibility, a compatible `A_Y`, endpoint exclusion, and Conway-99 remain
`UNKNOWN`.

## Waves 64--65: rooted transition design and hypergraph algebra

- `wave64-rooted-transition-design/` identifies the 84 residual labels with
  the edges of `K14-7K2`, enumerates 35,560 matching blocks and 840 allowed
  transitions, stores a 140-block relaxation witness, and gives an exact
  rational point of the stronger linear master. Its complete binary
  codegree closure is specified but unsolved.
- `wave65-rooted-hypergraph-algebra/` studies `B=T+D` through the incidence
  factorization `D+5I=ZZ^T`, the 140-vertex block graph, trace and four-cycle
  identities, scalar spectral coupling, averaged PSD lanes, and an exact
  local positive control that fails the target moments.

Independent verification accepts both finite scopes. Neither package supplies
an integral strong witness, endpoint exclusion, graph, or strict upper bound
below 4158.

## Wave 66: spherical-code and difference-lattice shift

- `wave66-spherical-code-shift/` lifts the negative-eigenspace embedding to
  99 equiangular lines of common angle `1/7` in `R^45`, centers it to an even
  rank-44 lattice `M`, and derives exact dual-denominator, determinant,
  discriminant-group, dual-minimum, and Milgram restrictions.
- The independent verifier records three discovery corrections: the imported
  universal lower rank was 27 rather than the endpoint-only 28; one listed
  weight-eight fact is unused; and only eight, not all 17, imported rank rows
  survive.
- With those corrections, the universal conclusion is
  `rank_F7(2A-J+I) in {28,30,32,34,36,38,40,42}`.

No lattice realization, graph, norm-14 exclusion, endpoint contradiction, or
literature-priority result is supplied. Conway-99 remains `UNKNOWN`.

## Waves 69 and 72: order-11 symmetry and cyclic-cover shift

- `wave72-order11-automorphism/` proves that every exact order-11
  automorphism of a hypothetical target is fixed-point-free. The fixed set
  has size divisible by 11, induced degrees in `{3,14}`, and exact
  common-neighbor closure; the only positive cases `11,22,99` reduce to
  contradictions or the identity.
- `wave69-cyclic-cover-shift/` derives the 9-by-9 quotient equation
  `Q^2+Q=12I+22J`, all seven row shapes, and all three diagonal cases. Its
  label-complete search visits 1,108,533 nodes and finds zero quotients; an
  independent canonical search visits 8,980 nodes and also finds zero.
- The combination excludes order-11 automorphisms and vertex-transitive
  realizations. An independent abelian-character argument excludes Cayley
  realizations on both groups of order 99.

Both discoveries have clean-room verification. The result is restricted:
it does not exclude asymmetric targets and does not improve
`708<=n3<=4158`. Conway-99 remains `UNKNOWN`.

## Waves 71, 74, and 78: level-seven theta and short-vector packing

- `wave71-modular-theta-extension/` removes the order-nine discriminant
  factor by an index-three even overlattice, forms the exact level-seven
  scaled dual `K`, and applies Skoruppa's mod-seven theta reduction.
  For `q=16`, equivalently `rank_F7(2A-J+I)=28`, it forces
  `N14+N16+N18=2 mod 14` for integer `-4` eigenvectors.
- The short vectors reduce to signed unit supports: complementary-Fano
  `7+7` at norm 14, 4-regular bipartite `8+8` at norm 16, and `9+9`
  structures at norm 18. Independent verification corrects Wave 71 by
  excluding the norm-18 `h=2` branch.
- `wave74-short-vector-closure/` records the exact outside-incidence
  contradiction and the remaining aggregate histograms.
- `wave78-short-vector-packing/` proves `d<=2` at norm 16 and `d<=3` at
  norm 18, reducing histogram counts from `4/20/6` to `1/7/4`.

All three packages have clean-room verification. Surviving histograms are
necessary conditions, not labelled designs or graphs. Conway-99 and novelty
remain `UNKNOWN`.

## Waves 80--82: coding, labelled design, and integral-orthogonal shifts

- `wave80-f7-overlattice-code/` turns the marked lattice into an injective
  `[99,44]_7` evaluation code. It derives the exact hull
  `row_F7(2A-J+I)`, dual distance at least six, orthogonal-array strength
  five, and the non-split rank-28 quotient `O^-(16,7)`.
- `wave81-norm16-labeled-design/` enumerates 1,800 anchored `8+8`
  4-regular bipartite supports, five support orbits, and 4,985 exact
  deficiency-coupling multisets. Necessary flow and spectrum tests retain
  every support orbit.
- `wave82-seidel-orthogonal/` gives the exact equivalent matrix problem
  `T=18A-2J+9I`, with `T1=63*1`, `T^2=3969I`, alphabet
  `{7,16,-2}`, and a complete conditional Smith form for every surviving
  characteristic-seven rank.

Independent verification accepts each scoped theorem. None of the finite
orthogonal spaces, labelled supports, Smith profiles, or local code moments
constructs or excludes a target graph.

## Wave 84: complete-domain SAT portfolio

- `wave84-rooted-sat-portfolio/` records three CaDiCaL configurations and
  one independently built Kissat configuration against the byte-matched
  Wave 34 rooted CNF.
- Every 900-second run stopped without a model or an UNSAT proof. The
  package is retained as `UNKNOWN` chronology, not promoted evidence.

## Wave 86: full level-seven modular-form squeeze

- `wave86-level7-exact/` works in the complete 15-dimensional space
  `M_22(Gamma0(7))`, uses the exact Fricke exchange and Sturm bound 14,
  and derives, in the `q=16` or rank-28 row,
  `N14+N16+N18>=5868`.
- An exact formal scalar pair attains 5,868 through the Sturm range and
  stays integral, even, and nonnegative through degree 50. It is not a
  lattice, marked frame, or graph.

The independent verifier confirms the inequality and records a source
normalization correction: the printed cited equation omits a ratio, while
the factors actually used follow from the source's preceding definitions
and transformation equation. Rank 28 and Conway-99 remain `UNKNOWN`.

## Waves 90, 94, 99, and 100: rooted norm-14 shell bounds

- `wave90-short-vector-count-upper/` maps every oriented norm-14 vector to
  one of 560 rooted complementary-Fano seeds. At the prism-free endpoint,
  transition incidence gives `N14<=5544`.
- `wave94-general-n3-norm14-bound/` counts rooted prisms and extends the
  first-moment argument to every compatible row:
  `N14<=floor((55440-4*n3)/7)`.
- `wave99-transition-pair-moment/` adds an exact second moment and sharpens
  the endpoint to `N14<=4950`. In the additional rank-28 row this combines
  with Wave 86 to force `407*N16+43*N18>=2165002`.
- `wave100-general-pair-moment/` proves the rank-free general strengthening
  `N14<=2*floor((55440-5*n3)/14)`.

All four shell bounds have separate clean-room verification. They bound
`N14`, not `n3`; no `N16` or `N18` upper bound, endpoint exclusion, or graph
resolution follows.

## Wave 97: characteristic-seven exterior and matroid shift

- `wave97-f7-exterior-matroid/` derives `R*R*R=F7^99`, `C*C=F7^99`, and a
  projective self-orthogonal second-compound `[4851,378]_7` code.
- At rank 28 its exact Smith form is
  `1^378,7^1204,49^1687,343^1204,2401^280,24010^98`.
- The finite orthogonal orbit reduction shows that norm-16 and norm-18
  short classes occupy the same square-anisotropic projective orbit, so
  abstract orthogonal geometry alone cannot distinguish them.

Independent verification accepts the mathematics with a provenance
correction: `R*R=1_perp` and the quadratic circuit were already immediate
consequences of Wave 51. No obstruction or graph follows.

## Wave 98: scalar-theta long-prefix probe

- `wave98-scalar-positivity-probe/` independently reconstructs the Wave 86
  formal scalar pair and finds no negative, odd, or nonintegral coefficient
  through degree 1,000.

This is an `UNKNOWN` finite null result. It is not an all-orders theorem and
does not realize a lattice, frame, or graph.

## Wave 101: all-rank level-seven scalar theta LP

- `wave101-all-rank-level7-lp/` repeats the complete
  `M_22(Gamma0(7))` calculation for all seven surviving rank rows. Exact
  rational primal/dual certificates give parity-rounded lower bounds
  `182,1584,11400,80110,561084,189901474,1831606638` on the total shell
  through norm 28.
- Every row nevertheless has an exact scalar control with
  `N14=N16=N18=0`. The graph-specific signed-unit dictionary therefore
  cannot yet be applied to the forced mass.

Independent verification accepts the scoped bounds and sharpens one generic
mod-two upper estimate by a factor of eight. The sharpened estimate still
excludes no rank row.

## Wave 102: rooted prism-incidence code

- `wave102-prism-incidence-code/` factors the rooted-prism parity vector
  through the binary triangle-incidence code and retains its exact odd-root
  defect:
  `7*N14<=55440-5*n3-O/2`.
- It proves the two-prism overlap cap and small-prism parity controls.
  Independent verification strengthens the latter to `P=3 => O>=4`.
- The 12-vertex `C4 box K3` motif contains four prisms with zero rooted
  parity and passes the local cap and interlacing tests.

The motif is not a 99-vertex construction. The code constraints do not force
`O>0` in general, so no strict upper bound on `n3` follows.

## Wave 105: `C4 box K3` conditional extension

- `wave105-c4boxk3-extension/` expands the SRG equation into exact
  motif/outside blocks. Conditional on the motif, the 87 outside vertices
  have types `3,48,36`, span 549 outside edges, and leave 34 separately
  graphical aggregate degree rows.
- A checked 549-edge graph satisfies all degrees and all 1,044 linear
  motif-incidence entries. It is a linear witness only.
- A complete 321,726-variable nonlinear encoding covers all four
  three-vertex `X0` graph branches. Four 45-second runs remain
  `UNKNOWN_TIMEOUT`.

Independent verification supplies the triangle-free support argument,
checks encoding completeness, and confirms that the linear witness fails
2,525 nonlinear pair equations. Full extension remains `UNKNOWN`.

## Waves 96 and 112: four-cycle shell incidence and norm 20

- `wave112-c4-short-vector-incidence/` proves that the target has exactly
  2,079 induced four-cycles and that every live norm-14, norm-16, and
  norm-18 support contains at least `21,20,18,26` alternating cycles in the
  four respective lanes.
- The rank-28 shell lower bound then forces at least 52 oriented extensions,
  or 26 antipodal support pairs, through some cycle. A universal cap of 25
  pairs would exclude rank 28; the cap is not proved.
- `wave96-norm16-norm18-upper/` verifies the sharper weighted implication
  and shows why a projector-plus-distance proof cannot suffice: its
  fixed-cycle relaxation contains an exact 80-point cross-polytope.
- The same package extends the graph dictionary to norm 20. Every integer
  norm-20 `-4` eigenvector has ten `+1` and ten `-1` coordinates, at most
  three same-sign edges, and at least 15 alternating four-cycles. A
  universal cap of 24 pairs through norm 20 would exclude rank 30.

Both caps remain `UNKNOWN`. No general `N16` or `N18` upper bound, rank
exclusion, or graph resolution follows.

## Waves 107, 109, and 110: motif spectrum, local lattice, and safe SAT symmetry

- `wave107-c4boxk3-spectrum/` derives the exact characteristic polynomial
  of the conditional 87-vertex outside graph. It corrects the tentative
  quadratic factor to `x^2-9x-46` and forces 549 edges, 167 triangles,
  1,356 four-cycles, connectedness, and nullity four.
- `wave109-c4boxk3-local-projector/` constructs the primitive rank-74
  incidence-kernel lattice. Modulo seven it is `O^-(74,7)`, and the local
  projector transfers the eight global ranks to `16,18,...,30`; all remain
  feasible.
- `wave110-c4boxk3-symmetry-sat/` proves simultaneous external row-lex
  symmetry breaking by one shared orbit potential, without assuming a
  target automorphism. The four invariant `e(X0)=0,1,2,3` branches cover the
  complete encoding.

All four fresh 45-second Wave 110 runs return `UNKNOWN_TIMEOUT`. No spectrum,
local rank, or bounded solver result extends or excludes the motif.

## Wave 116: corrected aggregate C4 Jacobi route

- `wave116-c4-jacobi-theta/` verifies the common four-coordinate projector
  Gram matrix for every induced cycle.
- It rejects the proposed small scalar index: the corresponding marking is
  outside the required dual lattice.
- The valid markings give paired indices `G_K/2` and `G_L/2`, with
  `G_K=7G_L` and `det(G_K)=1,023,942,465`.
- The selected Fourier coefficient counts antipodal short-vector/cycle
  incidences exactly. Rank 28 forces at least 52,812, while a cap-25 upper
  certificate would be 51,975.
- A degree-32 harmonic interpolation is exact on the three short shells,
  but its coefficients are signed.

No Jacobi basis, Sturm bound, positivity cone, or dual upper certificate was
obtained. The route is a corrected reduction, not a rank exclusion.

## Wave 118: subjective strategy estimate

- `wave118-strategy-estimate/` records conservative, central, and liberal
  six-month judgments for the C4-incidence program.
- Its central estimates are 55% for a useful verified theorem, 20% for
  excluding one hard rank row with a C4 variant, and 1% for a complete
  Conway-99 resolution by this strategy alone.
- The report recommends aggregate Jacobi/harmonic-theta bounds over the
  pointwise cap route.

These numbers are subjective research judgments, not mathematical evidence,
calibrated forecasts, or deadlines.

## Waves 123 and 127--131: projector, Jacobi, discriminant, and binary shifts

- `wave123-fixedc4-threepoint/` applies the actual `-4` eigenspace
  projector to the Wave 120 coordinate supports.  The displayed 40-record
  family has 46 leverage violations.  An alternate 26-record subset passes
  diagonal leverage and 2,340 exact rooted feature-Gram tests but fails 352
  graph-valued two-by-two completion rows.  Its bounded subset search is
  explicitly nonexhaustive.
- `wave127-independent-jacobi-certificate/` and
  `wave129-jacobi-stress/` independently reconstruct the 239-dimensional
  index-10/index-70 level-seven Jacobi relaxation.  Exact rational feasible
  points replay at cutoffs `10,12,14,16,18,20`.  At that checkpoint cutoff
  28 was `UNKNOWN`; Wave 130 below subsequently supplied an exact rational
  feasible point.
- `wave128-alternative-spaces/` splits the conditional Wave 109
  incidence-kernel lattice into finite-primary rational eigenlattices.  It
  fixes their non-seven discriminant groups, Gauss phases, rootlessness,
  and nonsplit `O^-(k,7)` seven-primary type.  Every imported row survives.
- `wave131-binary-lcd-enumerator/` derives the complete codeword counts
  forced by vertex subsets of size at most three.  An exact rational
  MacWilliams witness permits image/dual distances `14/15`; it is
  nonintegral, and the bounded integral scout remains `UNKNOWN`.

All four lanes have separate clean-room verification.  They are finite or
conditional necessary-condition results, not a code, lattice, graph,
rank exclusion, or Conway-99 resolution.

## Waves 130 and 132--134: exact boundaries beyond the first alternatives

- `wave130-cdd-exact-lp/` gives an exact rational cutoff-28 Jacobi point.
  It replays all 454 original equalities and 1,686 inequalities with zero
  failures and 506 tight rows.  This refutes the earlier numerical
  cutoff-28 infeasibility diagnostic, not rank 28 or Conway-99.
- `wave132-distinguished-biweight/` retains intersections with the 99
  distinguished neighborhood and closed-neighborhood rows.  It forces
  `A94=A96=A98=0` and refutes the Wave 131 rational witness, but a stronger
  exact rational split-enumerator witness survives.  Integral and full
  genus-two feasibility remain `UNKNOWN`.
- `wave133-triangle-holonomy-topology/` derives
  `product_T sign(h_T)=(-1)^(chi+E-F)`.  Both local signs survive, and an
  endpoint-scale connected nonorientable surface control realizes the
  aggregate parity data.  A future topological obstruction must constrain
  orientability or the edge-twist class using additional point-level
  equations.
- `wave134-z4-symmetrized-enumerator/` lifts the full adjacency row code to
  `Z/4Z`.  It derives the exact code types, torsion symmetry, sparse
  symmetrized MacWilliams transform, 8,557,760 forced primal words and
  4,126,784 forced dual words.  Independent verification twice vetoed
  incomplete prepublication models; the corrected transform has 1,119
  primal, 1,114 allowed dual, and 161 forbidden dual orbits.  Corrected
  rational and integral feasibility are `UNKNOWN_NOT_RUN`.

All four packages have independent clean-room verification.  They are
finite-relaxation, conditional-enumerator, or abstract-control results, not a
graph, lattice, realized code, rank exclusion, strict `n3` upper bound, or
Conway-99 resolution.

## Waves 135--142: alternative-space continuation

- `wave135-z4-exact-face/` adds the independent primal torsion-shell equality
  to the corrected quaternary face.  Exact row generation remains
  `UNKNOWN_WALL`; no primal or Farkas certificate was produced.
- `wave136-alternative-spaces/` derives the binary Arf/Gauss split and the
  self-dual additive-`GF(4)` graph-state formulation.
- `wave137-z4-arf-branches/` stores exact rational witnesses for both Arf
  signs through signed Krawtchouk degree five and all approved shadow bounds.
  The quaternary numerical branches remain non-evidentiary.
- `wave139-gf4-n3-bound/` records the three-class invariant-space dimension
  and an inconclusive numerical scout.  Its lower-bound aggregation and
  pure-`Y` zero rows require the separate Wave 145 audit before use.
- `wave140-arf-sign-lattice/` proves the two-adic determinant/Arf bridge and
  supplies opposite-sign local controls with an explicit non-graph scope
  wall.
- `wave141-bivariate-graph-code/` derives the `D8` bivariate transform,
  exact low input rows, and
  `S6=2024484+(512/3)n3`.  Its floating row-generation scout is
  `UNKNOWN_NUMERICAL`.
- `wave142-interlace-isotropic/` derives exact local interlace and isotropic
  rows.  Its sizes 86--91 top-band claim is rejected by the verifier; only
  sizes 92--99 are target-forced.

These attempts change the representation and expose new exact constraints,
but none improves `n3<=4158`, constructs a code or graph, or resolves
Conway-99.

## Waves 143--146: projection and rooted overlap

- `wave143-binary-s6-projection/` substitutes the exact `S6/n3` identity
  into the binary enumerator and equality lattice.  Rational endpoint
  witnesses survive both Arf signs.  The target does not justify the
  stronger formal dual-distance-15 slice, and the equality projection gives
  only `n3=0 mod 3`.
- `wave144-sixset-odd-profile/` enumerates exact 64-cell outside-neighborhood
  profiles for all 62 six-vertex classes.  A 65-cell nonnegative integer
  aggregate survives at `n3=4158`, but it does not glue overlapping
  six-sets.
- `wave139-gf4-n3-bound/` is superseded in part by the Wave 145 audit.  Its
  five collided lower bounds must be summed, not maximized, and its pure-`Y`
  zero rows 8, 10, and 12 are vetoed.  Corrected feasibility is `UNKNOWN`.
- `wave146-six-seven-coupling/` filters every outside pattern through exact
  rooted seven-vertex admissibility and glues all rooted orbit totals to the
  complete 208-class order-seven deck.  It removes 25 local weight cells and
  refutes the selected Wave 144 witness, but a full exact rational endpoint
  witness survives all 8,981 equations with denominator at most four.
- `wave147-alternative-lane/` builds the two-root/order-eight flag space:
  66 and 87 rooted flags, 916 admissible order-eight classes, 2,414 exact
  coefficient matrices, and 208 deletion rows.  Its moment entries expose
  `4*n3` with zero prism coefficient.  No endpoint SDP or dual certificate
  is claimed.

Wave 146 is the first exact overlap lift in this sequence.  Its surviving
certificate shows that one outside root is still too coarse; two-root or
order-eight compatibility is the next boundary, and Wave 147 supplies the
finite coefficient model for that computation.

## Waves 148--152: order-eight execution and alternative roots

- `wave148-marked-order8/` adds 944 marked-vertex and 4,440 ordered-pair
  identities between order-seven and order-eight class counts.  All 5,384
  rows and 28,654 stored coefficients have an independent semantic replay.
- `wave150-order8-sdp-scout/` combines Wave44, ordinary deletion, Wave148, and
  both Wave147 centered pair-root blocks.  Its exact rational `n3=4158`
  witness has order-7/8 supports `204/874`, denominators at most four, and
  passes 10,310 nontrivial exact equations.  Both pair-root covariance blocks
  are exactly zero.  This retires that finite relaxation as a standalone
  endpoint-exclusion route.
- `wave149-terwilliger-triple/` roots at a triangle and produces an explicit
  zero-prism permutation system whose forced 36-by-36 Gram matrix has exact
  spectrum `0^4,6^9,10^9,12^13,60^1` and rank 32.
- `wave151-triangle-root-factor/` realizes the first two 12-row fibres as an
  exact binary 24-by-60 factor.  The third fibre is not constructed; the
  fixed-first-factor `UNSAT` status has no proof artifact and remains a
  branch-scoped diagnostic.
- `wave154-triangle-factor-portfolio/` constructs a second exact 24-by-60
  factor outside all 384 conjugates of the first.  The complete joint model
  has 69,270 allowed triples in 292 centralizer orbits, 612 rows, and
  1,039,050 incidence nonzeros.  No full 36-by-60 factor or checkable
  impossibility proof was found.
- `wave152-four-root-order8/` uses four pointwise-labeled roots and an
  unordered free pair.  Clean-room verification confirms exact negative
  covariance directions for root masks 3 and 12, so the Wave150 vector is
  not a graph-compatible moment sequence.  Four primitive cutting planes
  still admit exact rational replacement vectors on the old zero-covariance
  face.  The four-cut replacement adds an exact mask-13 violation in a
  two-by-two principal minor; its sparse fifth cut also leaves an exact
  rational control.  Wave156 verifies that eight directions and a ninth
  simplified mask-12 inequality retain an exact rational control.  The next
  equal-diagonal minor yields the sparse endpoint theorem
  `N_Wagner <= 3*N_cube+9355`; it separates that control.  Its candidate
  symbolic lift is
  `4*N_Wagner <= 41580-n3+12*N_cube`.  Thirteen cuts admit an exact rational
  control with support `204/887` and rank 887.
- `wave159-four-root-cut-loop/` adds exact root-mask-3 and root-mask-12 cuts
  to that control.  The resulting fifteen-cut relaxation still has an exact
  nonnegative rational witness with support `204/887`, all 10,313 rows
  passing, and modular rank 887.  Full four-root reevaluation again finds
  exact negative directions at precisely masks 3 and 12.  Wave161 verifies
  this finite-relaxation result independently.  It is a cutting-plane loop,
  not endpoint infeasibility.
- `wave162-four-root-facial-reduction/` tests whether the three active
  Wave159 cuts expose a forced positive-semidefinite face.  Exact replay on
  six fixed-slice witnesses shows that every active functional varies on the
  common stored affine slice, while the newest negative directions are
  independent of the active spans.  Thus no unconditional face follows from
  the stored data.  A true next step requires a coupled exact conic-dual
  exposing certificate, not more sampled rank-one cuts.
- `wave153-alternative-compatibility/` tests the complete bounded rational
  pair-correlation projection for all 275 safe coordinate orbits covering
  all 1,140 triangle-component triples.  A clean-room verifier replays all
  173,250 pair equations and 9,900 row margins exactly.  Every rational
  projection survives, locating the remaining obstruction in binary
  integrality, common higher-order coupling, or residual-graph compatibility.
- `wave157-general-cube-wagner/` independently expands the sparse mask-12
  covariance direction before endpoint substitution and derives
  `41580-n3+12*N_cube-4*N_Wagner>=0`.  Its endpoint specialization exactly
  matches the Wave156-verified primitive cut.  Wave158 independently verifies
  the complete symbolic derivation.  The theorem does not by itself imply
  `n3<4158`.
- `wave165-general-cube-upper/` moves to fixed-four-cycle extension space.
  Exact nine-or-ten boundary matchings and a marked-square/prism bijection
  give `12*N_cube<=37422+3*P=41580-n3`, hence `N_cube<=3465` generally and
  `N_cube<=3118` at the prism-free endpoint.  The proof assumes no graph
  automorphism; it does not by itself improve `n3<=4158`.
- `wave166-rooted-wagner-spaces/` derives exact fixed-square shell equations,
  supplies a shell null model, counts 40 marked induced five-cycles at every
  nonedge, and reduces endpoint exclusion to at most four failed Wagner marks
  per nonedge.  That four-failure lemma is explicitly `UNPROVED`.  The package
  also records the exact pair-root pseudowitness obstruction and the
  root-3/root-12 or order-eleven continuation.
- `wave167-nonedge-core-fringe/` corrects and sharpens that target.  At `P=0`
  each nonedge has exactly 36 core and four fringe marks, all four fringe
  marks fail, and completion is unique when it exists.  Hence
  `F=166320-8*N_Wagner` and the extra defect is
  `E=8*(18711-N_Wagner)`.  Endpoint exclusion needs only the global bound
  `E<=8`; a checked abstract shell proves the current one-root equations
  cannot establish the stronger pointwise equality.
- `wave168-incidence-minor-energy/` moves to the partial linear geometry of
  the 231 unique edge-triangles.  It translates `P=0` to block codegree at
  most two and derives a Cauchy-Binet minor energy whose values on cube and
  Wagner point sets differ by 15,360.  Bounding the other eight-point
  configuration contributions remains an unexecuted strategy.
- `wave169-failure-hypergraph/` proves completion uniqueness is already an
  order-eight event, then gives a checked five-failure local gadget.  Thus a
  pairwise incompatibility graph using the current clauses cannot prove
  independence number at most four; the retained target is a five-way
  failure hypergraph, overlapping-root closure, or lifted exact dual.
- `wave170-block-profile-ternary-code/` derives the exact pointwise profile
  `(32-p,144+3p,36-3p,p)`, recovers `n3+3P=4158` in block space, proves
  block-intersection clique number seven, and obtains
  `rank_F3(B*B^T)=55`.  The proposed star-complement/code classification is
  not executed and no new numerical bound follows.
- `wave171-pq-centered-code/` reframes the graph as the point graph of
  `PQ(2,6,2)` and the triangle-block geometry as the square-zero ternary
  polynomial `X=K-K^2`.  Every row has weight 198 with exact composition
  `(33,36-3*p_L,162+3*p_L)`, the 99 point-stars are intrinsic in `K`, and
  `rank_F3(X)=rank_F3(C)-1`.  Independent verification shows
  `X=2(C+J)`: this is exactly the earlier centered code in a cleaner
  geometric language, not a new obstruction.  No search was used.
- `wave172-weight3-dual-rigidity/` adds a marked complete-weight constraint
  at `P=0`.  Every weight-three word in the dual centered code has equal
  nonzero coefficients, is supported on three mutually nonadjacent triangle
  blocks inducing `3K3`, and forces joint row counts
  `000^15,111^144,222^18,(012 permutations)^54`.  Mixed signs are excluded
  by exact integer reflection norms.  This does not determine whether such
  a dual word exists or exclude the endpoint.
- `wave173-complete-enumerator-lift/` uses the resulting mixed
  weight-three zeros to refute the Wave54 ordinary enumerator as a possible
  complete endpoint enumerator.  Exact degree-two and degree-three moments
  force a required contribution larger than its maximum by
  `149881671/2`.  A separate six-cell rational control satisfies the general
  projective marked moments through degree three, so the refutation is
  specific to Wave54's distribution and is not an endpoint exclusion.
- `wave174-no-weight3-dual/` eliminates every weight-three dual word at
  `P=0`.  A block dependence becomes a ternary line-sum coloring; exact
  five-cell interlacing leaves `c=8,9`, common-neighbor convexity eliminates
  eight, and equality at nine forces three new triangles forming a forbidden
  prism.  The verifier found and repaired the initially omitted empty-cell
  case `c=18` with the exact quadratic value `-1152`.  Thus
  `d(W^perp)>=4`, with no rank assumption and no graph search.
- `wave175-polar-cap-boundary/` moves the smallest surviving centered rank
  `k=11` into the parabolic quadric `Q(10,3)`.  Exact polar spectral energies,
  the mod-three refined outside-point second moment, and standard polar-cap
  bounds all fail to contradict the 231-point set.  The quadratic Veronese
  map does impose
  `rank_F3(J-I-R)<=65` and `rank_F3(I+R)<=66`.  These are verified
  new-to-repository necessary conditions, not an endpoint exclusion; the
  ordinary polar-cap definition is inapplicable because the set has 3,696
  orthogonal pairs.
- `wave176-star-projector-circuits/` restores the 99 labelled point-stars
  as nondegenerate six-spaces in the conditional rank-11 polar model.  Their
  canonical trace-zero projectors give `rank_F3(BLB^T)<=65`.  Dimension
  forces a cross-star dual relation for every nonedge, while an exact
  four-cycle-type calculation proves the same for every edge.  The adjacent
  Gram ranks are `10,10,8,9`; only the two rank-10 cases promote exact
  non-star support minima 8 and 4.  This finite-algebra calculation searches
  no graph or code and does not exclude the endpoint.
- `wave177-relation-averaging-conic/` averages over the true ternary
  relation codes after removing the complete individual-star subcodes.
  Every edge thereby indexes a genuine cross-star relation of weight `4..8`
  and every nonedge one of weight `4..9`; no distinctness across pairs is
  claimed.  The type `4+2` weight-four word is exactly a complete
  `Q(2,3)` conic, whose frame contribution is canceled by the other nine
  points of `PG(2,3)`.  This is a verified analytic short-circuit theorem and
  a local divisibility null control, not an endpoint exclusion.
- `wave178-edge-circuit-injection/` closes the edge-multiplicity gap with a
  `lambda=1` triangle-incidence proof.  The 693 edges inject into distinct
  projective dual circuits.  A tiny classification of four derived local
  Gram kernels shows that the chosen circuits have weights `4,6,8`, equal
  support on the two outer stars, and equal coefficient counts `1,2`.
  Consequently `B_4+B_6+B_8>=1386`.  No graph, code, SAT, or isomorphism
  search is used, and the endpoint remains unexcluded.
- `wave179-global-transversal-circuits/` treats every cross circuit support
  as an exact two-transversal of graph triangles.  One support cross-realizes
  at most three vertex pairs; disjoint realizations have multiplicity two
  and both pairs are nonedges.  Wave178 balance globally isolates all 693
  edge circuits, while the 4,158 nonedges need at least 1,386 additional
  projective circuits.  Hence there are at least 2,079 projective circuits
  of weights `4..9` and `B_4+...+B_9>=4158`.  This is a verified conditional
  rank-11 necessity, not an endpoint contradiction.
- `wave180-capacity3-companion/` classifies the three-nonedge equality case
  inside one nondegenerate finite-polar star space.  The seven local
  cross-edge counts and star projector leave one marked triple, producing a
  weight-four `Q(2,3)` conic circuit and a weight-five complementary circuit
  with exactly the same three labels.  A minimal-cover companion involution
  forces at least 2,079 nonedge-realizing and 2,772 total projective circuits,
  hence `B_4+...+B_9>=5544`.  The theorem is independently verified and uses
  no graph, code, SAT, configuration, or isomorphism search.  It strengthens
  the rank-11 endpoint boundary without excluding it.
- `wave181-c4-conic-equality/` excludes shared-center multiplicity-two
  circuits and identifies every surviving twice-used support with the four
  edge-triangles of the canonical induced quadrilateral on a paired
  nonedge.  Its unique checkerboard relation is a `Q(2,3)` conic.  Equality
  in Wave180's nonedge lower bound therefore requires all 2,079 canonical
  quadrilaterals to be conics.  The signed square--triangle matrix then has
  conditional rank at most 220 and exact Gram `2K+L` over `F_3`. At that
  checkpoint, proving rank at least 221 was the exposed continuation. The
  first global conic-projector sum is a verified characteristic-three null
  boundary; Wave186 later excludes the equality face by a different
  star-translation argument.

- `wave182-a6-root-gluing/` recasts Wave181 equality as 99 glued local
  21-point negative-`A6` root systems. The two local root sets attached to
  nonadjacent stars meet in exactly their canonical norm-one root, every
  root color induces a 4-regular graph in the complement, and exact edge
  capacities plus second moments give
  support sizes `5..10` and `231..415` global roots.  The all-nine lower
  boundary has incidence Gram `20I+5A+J`; its positive spectrum and first
  characteristic-three frame sum are verified null tests, not feasibility.
- `wave183-root-support-girth/` strengthens the same equality face without
  a construction search.  Opposite canonical-square roots are orthogonal,
  so no pair in one root support can have two internal common neighbors.
  An internal two-path injection excludes support multiplicities nine and
  ten, and a cubic triangle-packing argument excludes eight.  The remaining
  induced support graphs are exactly `5K1`, `3K2`, and `C7`, giving the
  verified conditional root interval `297..415` and a split finite-polar
  frame identity. This argument alone does not exclude Wave181 equality;
  Wave186 later does so by star translation.
- `wave184-root-support-intersections/` proves that distinct root supports
  meet in at most two vertices, with every two-point intersection a graph
  edge.  Root/internal-edge incidences inject into distinct projective
  weight-four edge circuits.  The exact count `3*n_6+7*n_7` is at least 12,
  so Wave181 equality conditionally forces at least 2,091 projective
  weight-four circuits and `B_4>=4182`. This theorem is independently
  verified; no incompatible upper bound on `B_4` is known, while Wave186
  later excludes the equality face by a different invariant.
- `wave185-local-a6-transition-collapse/` finishes the local transition
  analysis on that former equality face. Prism-free cell geometry forces
  `n_7=0`; the exact type-5 and type-6 transition profiles are
  `(0,2,2,8)` and `(1,2,0,9)`. Consequently `n_5>=15`, the conditional
  global-root interval is `349..415`, and the root complement contains at
  least 94,264 rainbow triangles. The theorem is independently verified.
- `wave186-star-translation-cover/` leaves the equality face and acts
  directly on a minimum short-circuit cover of the 4,158 nonedges.
  Endpoint-star translations give two distinct external short circuits for
  each private label on a multiplicity-two support; multiplicity-three
  supports also have two distinct companions. Exact cover accounting then
  gives `9Q>=8*4158`, hence `Q>=3696`, at least 4,389 total projective
  circuits of weights four through nine, and
  `B_4+B_5+B_6+B_7+B_8+B_9>=8778`. This independently verified theorem
  excludes `Q=2079` and closes the Waves181--185 equality branch, but it
  does not exclude rank 11 or improve the global `n_3` interval.
- `wave187-code-geometry-proof-b/` supplies an exact rational hostile
  control for the stronger code-theoretic lane. It has `B1=B2=B3=0`,
  fixes the 231 marked weight-198 scalar pairs, satisfies every ordinary
  MacWilliams inequality, all complete coefficients through degree six,
  and the typed quadratic moments through degree three. Its short dual-word
  count greatly exceeds 18,018. The control is not a code; its first
  negative complete coefficient occurs in degree seven. These claims were
  reconstructed independently in exact arithmetic.
- `wave188-affine-star-word-amplification/` counts actual translated dual
  words rather than circuits. The affine `3 by 3` two-star orbit has at
  least three short projective words; support capacity and the one-block
  projector classification separate the private-label contributions.
  Exact accounting gives at least 8,316 nonedge-realizing and 9,009 total
  projective dual words of weights four through nine, hence
  `B_4+B_5+B_6+B_7+B_8+B_9>=18018`. The theorem is independently
  verified but does not exclude rank 11 or the endpoint.
- `wave189-orbit-closed-star-translations/` closes the raw extraction pool
  under the exact-three companion involution and uses private-label
  ownership plus the `6+2` versus `2+6` common-center orientation to cut
  orbit capacity. A checkerboard subtraction excludes the sole scalar
  equality face. The independently verified conditional conclusion is
  `Q>=4852`; its 13,860-flag Hoffman calculation is a sharp design null
  boundary, not an integral construction.
- `wave189-degree7-star-complete/` gives an exact 16-cell rational control
  satisfying the one-star polygon, complete MacWilliams rows through degree
  seven with `B_(7,0)=B_(0,7)=99`, the forced star-pair rows in degrees
  12--14, ordinary rows, and typed moments. This independently verified
  feasibility result is not a code, point set, graph, or endpoint.
- `wave190-residual-stability-proof-b/` charges raw and residual assignments
  to the same three-label companion-orbit capacity. Its exact slack identity
  and coefficient certificate `6Q>=8*4158` give the independently verified
  conditional circuit bound `Q>=5544`, at least 6,237 projective short
  circuits after adjoining the edge family, and the circuit-only scalar
  bound `B_4+...+B_9>=12474`. The sharp row is arithmetic only.
- `wave191-exact-three-residual-proof-a/` and
  `wave191-global-star-module-proof-b/` exclude exact-three private-leaf raw
  extraction and couple the residual capacities, giving the independently
  verified conditional bound `Q>=6237`.
- `wave192-equality-face-proof-a/` and `wave192-c4-cohomology-proof-b/`
  reconstruct and exclude equality in Wave 191 by canonical-square
  checkerboard translations, giving the verified strict bound `Q>=6238`.
- `wave193-global-low-target-proof-a/` and its aggregate proof-B audit combine
  the raw-assignment and residual pools in the exact row `117Q>=177C`, hence
  the verified conditional bound `Q>=6291`.
- `wave194-type2-residual-low-u-proof-a/` and its five-thirds proof-B audit
  prove the doubled type-two residual and joint leaf-capacity rows. Their
  exact certificate gives the verified conditional bound `Q>=6930`.
- `wave195-leaf-packet-intersection-proof-a/` and
  `wave195-packet-cohomology-proof-b/` recast fixed-center flags as simple
  intersecting 3-subset families of a seven-set. Hilton--Milner and the
  common-star case give the verified conditional bound `Q>=6980`.
- `wave196-four-fiber-hilton-milner-proof-a/` and its proof-B audit use the
  four vertices in each of the 21 local pair fibers and the two
  Hilton--Milner equality templates to prove `c_x<=13`, `j_x<=36`, and the
  verified conditional bound `Q>=7029`.
- `wave197-degree10-flag-cap-proof-a/` and its hostile audit retain the five
  flags per oriented nonedge, private-label degree one, and full-pool
  headroom. The verified exact certificate gives `Q>=7033`.
- `wave198-orientation-lift-proof-b/` and its hostile proof-A audit keep the
  two orientations separate and prove the weighted row
  `S5=17820-3n3-4p3-5a3-5b3>=0`, yielding the verified bound `Q>=7037`.
- `wave199-near-face-gluing-proof-a/` and its proof-B audit exclude the first
  integer face above the Wave 198 rational target. They are subsumed by the
  independently verified Wave 200 theorem.
- `wave200-two-face-gluing-proof-a/` and its proof-B audit prove additive
  loss for multiplicity-five labels in distinct four-point fibers and
  exclude both `Q0=7037,7038`, giving the verified bound `Q>=7039`.
- `wave201-multiplicity-weighted-fiber-loss-proof-a/` and its proof-B audit
  handle arbitrary same-fiber multiplicity profiles, including multiplicity
  one. The row `delta>=3q-epsilon` and exact certificate give the verified
  conditional bound `Q>=7059`, or 7,752 projective short circuits after
  adjoining the edge-isolated family.
- `wave202-three-unit-equality-face-proof-a/` characterizes all symbolic
  partitions and local zero conditions at `Q0=7059`. It records the honest
  stopping point: its one-center rows do not exclude the face, so no
  `Q>=7060` or endpoint exclusion is claimed.
- `wave203-two-center-incidence-proof-b/` and its hostile proof-A audit prove
  that the two orientations of one nonedge share five third-block slots. A
  matched reverse pair would force the all-equal word on the canonical
  quadrilateral, contrary to its verified checkerboard Gram kernel. Thus the
  combined directional flag multiplicity is at most five and
  `epsilon>=5b` for `b` both-oriented labels. Since no checked row forces
  `b>0`, the conditional bound remains `Q>=7059`.

Every promoted theorem or finite-feasibility statement above has a separate
verifier; Wave162 remains a clearly labeled `DERIVED` strategy audit.  The
full four-root PSD feasibility problem, complete triangle-root binary factor,
strict `n3<4158` bound, and Conway-99 remain `UNKNOWN`.

Wave 204 attempts:

- `wave204-literature-hostile-controls/` gives an exact relaxed 99-center
  `b=0` certificate and a focused primary-source hypothesis audit. The
  certificate refutes only the frozen local-interface force-`b>0` lemma; it
  is not an SRG, ternary code, or endpoint.
- `wave204-global-slot-holonomy-proof-a/` identifies the true triangle-block
  gain as a coboundary and uses exact relaxed rank-11 controls to refute
  center-walk chaining and determined total-`S_5` transport from Wave 203's
  partial slots.
- `wave204-projector-fourth-order-proof-b/` proves the conditional adjacent
  fourth-trace detector for the four outer edge types and records exact
  controls showing that pair trace plus intersection dimension does not fix
  the fourth trace.

All promoted claims pass `wave204-global-compatibility-verifier/`. The next
route is a graph-specific classification of nonedge fourth traces and a
global identity for the full `99 by 99` fourth-trace matrix. The conditional
bound remains `Q>=7059`, the rigorous interval remains `708<=n3<=4158`, and
Conway-99 remains `UNKNOWN`.

Wave 205 attempts:

- `wave205-fourth-trace-globalization/` freezes the branch, evidence
  boundary, and inflection criteria.
- `wave205-nonedge-fourth-trace-proof-a/` derives the exact nonedge
  cross-Gram profiles, exhausts the normalized `t=6,7` frontier, and gives
  four 28-vertex rank-11 local certificates. These controls refute only
  pair-local implications.
- `wave205-global-fourth-moment-proof-b/` proves `H=U K_D U^T`,
  `rank(U)=99`, and the row-localizer contractions, while recording why
  ambient rank and first-moment shortcuts fail.
- `wave205-fourth-trace-hostile-controls/` gives a stronger relaxed
  99-projector/231-column incidence control whose nonedge fourth traces vary,
  while explicitly failing projective distinctness and the target
  `lambda/mu` laws.

The independently verified inflection is that pair-local fourth-order data
cannot decide the endpoint. Further work must control simultaneous
99-center extension, the crossing kernel on `row(U)`, or an equivalent
three-center invariant. No endpoint or Conway-99 claim is promoted.
