# Independent audit of the frozen Wave 13 computation

```yaml
role: verifier
date_utc: 2026-07-23T08:27:19Z
git_commit: 066d9c7fcf593c3b9d35cfef1031dbd9daab4145
claim_label: VERIFIED
scope: >
  Arithmetic, local-mode, branch-cover, CNF-semantic, formula-hash, and
  positive-witness reconstruction for the frozen conditional n3=45
  active-local computation. VERIFIED is restricted to those artifact
  properties. No negative SAT answer or n3=45 exclusion is verified.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  agents/2026-07-22-wave13-n3-45-computational.md: f1ace31438aa147018cb8210fa92cd940a0a4795e698bc09d34f3537debf8904
  code/wave13_n3_45_profiles.py: 7685a370166c0caa41460d5cbfab3b3a51d28da52441db63f5befeb396e4cf7c
  code/wave13_n3_45_active_sat.py: ad4b0c41e7aeebb3f9b9c5d1253c317e59b96d69f3d782f2ea83de655bf052e7
  code/wave13_n3_45_test.py: 0d2d4d868618ce714599c014ab0f8ac247c2f240a521848433fe94298bfbd3d3
  attempts/wave13-computation/n3-45-local-census.json: f0fcbd3457e5b39f56e68492d2a29ae2f45a5deeff99cc30803178d3f3ee2019
  attempts/wave13-computation/n3-45-active-local-sat-scan.json: d526bc59b4000a59ff8cc607be89744072a8845763883c8f60af65075bfdd933
  attempts/wave13-computation/n3-45-no-common-point-m5-111.json: e32486506a5da0607c0deddaced42ff77f059b39abc3ba29923cd5d056762bb0
  post_reconstruction_human_cross_check:
    agents/2026-07-22-wave13-n3-45-proof-a.md: e721614256f003d7266d0b3d1bb2f884febbdec33893f92ed18bf8961c6958e8
method: >
  Independent standard-library partition, flower, rooted-mode, cubic-graph,
  incidence, branch, and witness enumeration; a separately written PySAT
  CNF builder; exact deterministic DIMACS-stream comparison for every
  branch; clause-by-clause checking of a completed positive assignment;
  hostile mutation of the frozen diagnostic validator; and only then a
  comparison with the frozen human proof.
command: |
  python verification/n3-45-computation/independent_audit.py
  .venv/Scripts/python.exe verification/n3-45-computation/independent_formula_audit.py
  .venv/Scripts/python.exe -m unittest discover -s verification/n3-45-computation -p test_*.py -v
  $env:PYTHONPATH='code'; .venv/Scripts/python.exe code/wave13_n3_45_test.py -v
  $env:PYTHONPATH='code'; .venv/Scripts/python.exe code/wave13_n3_45_active_sat.py --validate attempts/wave13-computation/n3-45-no-common-point-m5-111.json
outputs:
  verification/n3-45-computation/independent_audit.py: b2241fe21f0dee7f390f5935577a553eb2537a4642f0f707d087393997f0dcb7
  verification/n3-45-computation/independent_formula_audit.py: c2a1fae2f74e2420d4e89acae627cf40de06ca5301ccffbbb7d19268a045b3c5
  verification/n3-45-computation/test_independent_audit.py: a2a370758c486dc4f5b5914773a283e0557b37f6179635939d7b36f88a85ac0e
  arithmetic_and_restricted_model_semantics: PASS
  independent_17_branch_cover: PASS
  exact_formula_rebuilds: 17/17 PASS
  frozen_bundle_self_validation: FAIL
  negative_solver_status: UNSAT_UNVERIFIED
  target_result: UNKNOWN
  novelty_status: UNKNOWN
limitations: >
  The PASS results concern the declared active-local order-fifteen model and
  the independently reconstructed reductions leading to it. The CNFs are
  not a 99-vertex Conway-graph encoding. No DRAT, FRAT, LRAT, or other
  negative proof trace was present or checked. The stronger frozen human
  proof was compared only on claims already reconstructed here and is not
  promoted by this report.
```

## Verdict

The frozen report has the required SHA-256
`f1ace31438aa147018cb8210fa92cd940a0a4795e698bc09d34f3537debf8904`.

| Question | Verdict | Boundary |
|---|---|---|
| Arithmetic and local semantics | **PASS** | Nine profiles, flower reductions, four rooted modes, 59 aggregate signatures, and the mixed-profile contradiction reconstruct independently. |
| Coverage by the 17 encoded branches | **PASS** | Complete for the declared all-\(q=2\), point-size-\(2/3\), active-local model, conditional on the stated prior reductions. |
| Exact CNF reproduction | **PASS** | All 17 variable counts, clause counts, and full SHA-256 DIMACS-stream hashes match. |
| Positive weakened witness | **PASS** | A total assignment satisfies all 1,141,796 clauses of the independent no-common-point formula; the core has exactly the 18 stated Berge violations. |
| Frozen bundle as a self-validating executable package | **FAIL** | The profile program omits a relevant mixed-root subcase while labeling its result broadly, the weakened validator leaves material metadata/root claims unbound, and the archived witness statistics are stale against the frozen source. |
| Seventeen negative solver answers | **`UNSAT_UNVERIFIED`** | There is no emitted and independently checked proof trace. Solver agreement, conflict counts, and exit codes are not certificates. |
| Exclusion of \(n_3=45\), project target, novelty | **UNKNOWN** | This audit makes none of those promotions. |

The three FAIL findings do not falsify the archived witness core or the
independently reconstructed 17-branch cover. They do prevent treating the
frozen programs and their built-in validator as self-sufficient
certificates.

## Independent arithmetic reconstruction

From the frozen premises,

\[
\sum_Tq(T)=30,\qquad q(T)\ge2,\qquad 3q(T)\le r-1,
\]

and \(d_K(T)=r-1-3q(T)\). Independent nondecreasing partition generation
gives exactly:

| \(r\) | \(q\)-profile | \(K\)-degree profile | disposition |
|---:|---|---|---|
| 15 | \(2^{15}\) | \(8^{15}\) | survives |
| 14 | \(2^{12}3^2\) | \(7^{12}4^2\) | survives |
| 14 | \(2^{13}4\) | \(7^{13}1\) | degree below three |
| 13 | \(2^9 3^4\) | \(6^9 3^4\) | frozen degree-three obstruction |
| 13 | \(2^{11}4^2\) | \(6^{11}0^2\) | degree below three |
| 13 | \(2^{10}3^2 4\) | \(6^{10}3^2 0\) | degree below three |
| 12 | \(2^6 3^6\) | \(5^6 2^6\) | degree below three |
| 11 | \(2^3 3^8\) | \(4^3 1^8\) | degree below three |
| 10 | \(3^{10}\) | \(0^{10}\) | degree below three |

Three distinct non-singleton point cliques through a label use three
distinct \(K\)-edges, so \(d_K\ge3\). This leaves three rows. Replaying the
frozen degree-three argument removes the \(r=13\) row, leaving the two rows
shown as survivors.

The independent flower census obtains:

| active order/root size | words | capacity-feasible | degree survivors |
|---|---:|---:|---:|
| \(15/5\) | \(4^{10}=1{,}048{,}576\) | 1 | 0 |
| \(15/4\) | \(3^8=6{,}561\) | 157 | 0 |
| \(14/4\) | \(3^8=6{,}561\) | 45 | 0 |

For the mixed \(r=14\) profile, the independent checker explicitly tests
all ordered \(q\)-assignments on a size-three root. Every assignment
containing a \(q=3\) label has zero local modes. The all-\(q=2\) root has
only \(t=(2,2,2)\). The resulting cubic intersection graph has order four
or six; there are zero labeled triangle-free cubic graphs at order four and
ten at order six, all copies of \(K_{3,3}\). Their line graphs have no open
twins, forcing an impossible injection of nine edge labels into three
available \(q=2,t=0\) labels. The all-size-two residual forces at least five
\(K\)-neighbors at a \(q=3\) label of capacity four. Thus the mixed-profile
reduction itself reconstructs.

There is nevertheless a frozen-code coverage defect:
`mixed_order14_reduction()` invokes only permutations of `(2,2,3)` and
stores the result under the broad name `q3_containing_local_modes`. It does
not invoke the relevant permutations of `(2,3,3)`. The latter also have no
survivor, as the independent checker and the later human argument both
show, but the frozen program did not perform that advertised exhaustive
subcheck.

## Four local modes, 59 signatures, and the branch cover

For an order-fifteen size-three root, let \(t_i\) count size-three points
through occurrence \(i\), and let \(z_i\) count its other size-three petals
whose crossing with the root is empty in \(L\). Independent enumeration of
external-label capacity, \(U\)-degree capacity, and the fixed-point cap gives
eight ordered modes in four permutation classes:

| sorted \(t\) | aligned \(z\) | full-\(L\) contribution | remaining support |
|---|---|---:|---:|
| 111 | 000 | 0 | 12 |
| 122 | 000 | 8 | 4 |
| 222 | 000 | 12 | 0 |
| 223 | 001, with \(z=1\) at the \(t=3\) occurrence | 12 | 0 |

Write \(a,b,c,d\) for the numbers of points of types
111, 122, 222, 223. The aggregate label counts are

\[
n_1=3a+b,\qquad
n_2=\frac{2b+3c+2d}{2},\qquad
n_3=\frac d3,
\]

with \(a+b+c+d=m\), integrality, and \(n_1+n_2+n_3\le15\). These are
aggregate incidence signatures, not asserted hypergraphs. Independent
enumeration gives:

| \(m\) | signatures |
|---:|---:|
| 1 | 2 |
| 3 | 7 |
| 5 | 16 |
| 7 | 21 |
| 9 | 12 |
| 11 | 1 |
| 13 | 0 |
| 15 | 0 |

This totals 59. Before the 15-label cap is applied, an integral \(m=13\)
type count uses at least 18 labels and an integral \(m=15\) type count uses
at least 20. This is the direct reason those two values are impossible.
Also \(2x_2+3m=45\), so \(m\) is odd.

A root of mode \(t_1t_2t_3\) requires

\[
1+\sum_i(t_i-1)
\]

distinct size-three points: respectively 1, 3, 4, and 5 for 111, 122, 222,
and 223. Distinctness follows from linearity for co-points at the same root
label and from the common-point rule for co-points at different root labels.
The sole \(m=11\) aggregate signature has

```text
type111=0, type122=0, type222=2, type223=9.
```

Consequently the exact rooted cover is:

| \(m\) | rooted modes |
|---:|---|
| 1 | 111 |
| 3 | 111, 122 |
| 5 | 111, 122, 222, 223 |
| 7 | 111, 122, 222, 223 |
| 9 | 111, 122, 222, 223 |
| 11 | 222, 223 |

These are the archived 17 branches.

The normalization is sound label naming, not a graph automorphism
assumption. Odd incidence supplies a selected size-three point, and the
full \(S_{15}\) action on anonymous active labels names it
\(\{0,1,2\}\). Its setwise stabilizer permutes the root occurrences and
outside labels to the displayed representatives. For 111 with \(m>1\), any
other size-three point is disjoint from the root and may be named
\(\{3,4,5\}\). For \(m=1\), linearity and the common-point rule make the six
size-two root mates distinct, so the stabilizer may name them as archived.
No automorphism of a completed 99-vertex graph is assumed.

## CNF semantic audit and exact rebuild

The independent builder does not import either discovery module. It uses
PySAT 1.9.dev7 sequential counters only to reproduce the deterministic
auxiliary-variable and DIMACS format. The primary variables are:

| class | count | meaning |
|---|---:|---|
| selected points | \( {15\choose2}+{15\choose3}=560\) | one variable for every size-two or size-three active point |
| \(K\)-edges | \( {15\choose2}=105\) | active-label complement edge |
| \(F\)-edges | 105 | exact union of selected point-clique edges |
| full-\(L\) overlap witnesses | 45,045 when \(m\ge5\) | reification for pairs of triples meeting once |
| sequential-counter auxiliaries | branch-dependent | exact/upper cardinalities |

Clause-family inspection confirms:

1. exactly three selected points contain each active label;
2. exactly \(m\) selected points have size three;
3. pair ownership is at most one, and \(F_{ij}\) is equivalent to the
   disjunction of all selected owners of \(\{i,j\}\);
4. every selected point is a \(K\)-clique;
5. \(F_{ab}\wedge F_{ac}\wedge F_{bc}\) implies selection of
   \(\{a,b,c\}\), exactly the common-point/Berge rule under linearity;
6. a selected singleton-side meeting crossing is empty in \(L\), while a
   selected 2-by-2 crossing is either empty or full in \(L\);
7. the full-\(L\) witness is equivalent to
   `selected(left) and selected(right) and not K(first_cross_edge)`, and at
   most three such witnesses touch any selected size-three point; and
8. every active label has exact \(K\)-degree eight.

The m=1 interaction optimization is semantic only: every non-root
size-three variable is already fixed false. The 122, 222, and 223 root
crossing signs agree with the independently reconstructed \((t,z)\) table.

Every complete formula rebuild matches:

| \(m\) | root | variables | clauses | independent and archived CNF SHA-256 |
|---:|---:|---:|---:|---|
| 1 | 111 | 13,209 | 32,224 | `584e4c7b7f8d366496729dc71da3bbb207e7344fee3d9f59a59fe99fd064580d` |
| 3 | 111 | 15,467 | 338,785 | `445366fc33eccbf5f86daedf6d3678c1cf64cb753f97991a7534157f018f90e0` |
| 3 | 122 | 15,467 | 338,792 | `6eaabc69cae2c83f33b5f8851287527dfdbf6e9616805a74c15b399ee9c41df9` |
| 5 | 111 | 328,475 | 1,142,251 | `613726bf378c1c3d78abdca387e4dbdb686309b228fa3f73ca621d9a77564f34` |
| 5 | 122 | 328,475 | 1,142,258 | `687abee000cf9e3603ac71c1f13fc3544e8afe1af87af443b307cfbc59bd6cad` |
| 5 | 222 | 328,475 | 1,142,262 | `a22446e091fcd382b6089da239a5f1a5d9a7a6a048788c91ea69edaa49e329fd` |
| 5 | 223 | 328,475 | 1,142,266 | `b34c9a5b18f78dd3ed9d232fd150808978bea9a60d12402a2d2e151d7bbf3395` |
| 7 | 111 | 330,247 | 1,145,795 | `c66c51e9c27bd16a47f3c523923a4c8f84f7359b91d8495ed7140dcf3658a174` |
| 7 | 122 | 330,247 | 1,145,802 | `de43df31f717eedbaa566b8278c827f80e4d952fe2e72abaeb1ff0a6ec283e32` |
| 7 | 222 | 330,247 | 1,145,806 | `e00aaef09785d119aec27499d642437387c3e2e445c9dd19aef5e7ca2b3ddeff` |
| 7 | 223 | 330,247 | 1,145,810 | `ba13ba49f105d7cf2ea51ee00b68e1612f2c001c8f7a810751397a61ff0ea99f` |
| 9 | 111 | 332,003 | 1,149,307 | `ab5bf8a6caebd6b8b22d4e19248c884d84695436f12141cbcaab221cbba6a4a7` |
| 9 | 122 | 332,003 | 1,149,314 | `d7934da69aa58fe545363e7e70039f281dfcad5fbf75840e18ce873695b1ed1c` |
| 9 | 222 | 332,003 | 1,149,318 | `5a6ee86c4ac0354814098dd0061a59b84a42b719de1e6dcdca315369544ff8a1` |
| 9 | 223 | 332,003 | 1,149,322 | `de887573e63a96ec7c74b392e5f0c5a6c138c71f9f7132924fd73940ca9e075a` |
| 11 | 222 | 333,743 | 1,152,798 | `7d03e957abf1d2b8993a0cd7c41337b3a05abceaa9b3565947360d0c6ecf40b2` |
| 11 | 223 | 333,743 | 1,152,802 | `6f73c69537a1cfd57dff985a083efa4d547db1da20c8d592951babc3ff11c6a5` |

All 17 hashes are distinct. Recomputing the scan's stable semantic object
gives the archived digest
`6325eb4958a850289baede0ba8663317e3a1189bd508c09749a6960e0cefbe49`.

No proof file or trace field accompanies any negative branch. Therefore all
17 answers remain exactly:

```text
UNSAT_UNVERIFIED
```

## Independent positive-witness validation

The archived no-common-point object independently has:

```text
15 labels
15 size-two points + 5 size-three points
incidence degree 3 at every label
no repeated pair owner
60 K-edges and K-degree 8 at every label
all point-clique pairs in K
45 meeting crossings checked, 0 violations
one full-L overlap, between point indices 17 and 18
maximum full-L overlap degree 1
t histogram 0^2 1^12 3^1
size-three local types 111^2 113^3
```

The independently rebuilt \(m=5\), root-111, no-common-point formula has
328,475 variables, 1,141,796 clauses, and SHA-256
`8260378538dccf0b3b3355619ceb237d7d6f89e1f3b26d86ea316f7e593df146`.
Fixing all 560 point and 105 \(K\)-edge variables from the archive extends
to a total assignment. The independent checker then evaluates every one of
the 1,141,796 clauses and finds zero false clauses. This is a checked
positive certificate, not reliance on a SAT exit code.

With \(F\) reconstructed as the exact point-clique union, the same core
falsifies exactly the following 18 full-model common-point clauses. Owner
sets are listed in pair order \(ab,ac,bc\); the three owners are distinct in
every row.

| triple | owners of its three pairs |
|---|---|
| 0,1,6 | {0,1,2}; {0,6}; {1,6} |
| 0,2,11 | {0,1,2}; {0,11}; {2,11} |
| 0,6,11 | {0,6}; {0,11}; {6,9,11} |
| 1,2,9 | {0,1,2}; {1,9}; {2,9} |
| 1,6,9 | {1,6}; {1,9}; {6,9,11} |
| 2,9,11 | {2,9}; {2,11}; {6,9,11} |
| 3,4,7 | {3,4,5}; {3,7,10}; {4,7} |
| 3,4,10 | {3,4,5}; {3,7,10}; {4,10} |
| 3,5,7 | {3,4,5}; {3,7,10}; {5,7} |
| 3,5,10 | {3,4,5}; {3,7,10}; {5,10} |
| 4,5,7 | {3,4,5}; {4,7}; {5,7} |
| 4,5,10 | {3,4,5}; {4,10}; {5,10} |
| 4,7,10 | {4,7}; {4,10}; {3,7,10} |
| 5,7,10 | {5,7}; {5,10}; {3,7,10} |
| 8,12,13 | {8,12}; {8,13}; {12,13} |
| 8,12,14 | {8,12}; {3,8,14}; {12,14} |
| 8,13,14 | {8,13}; {3,8,14}; {13,14} |
| 12,13,14 | {12,13}; {12,14}; {13,14} |

The independently recomputed witness semantic digest is exactly
`2492601fb4dbb6dd642d73e34404f446ff8d0f1cee6edfaec7babbba39424e03`.
The unexpected 113 local types are not an additional defect: the proof of
the four full modes uses the deleted common-point premise, so the diagnostic
mutation is allowed to leave that classification.

## Hostile mutations and frozen-bundle defects

The strict independent validator rejects edge deletion, duplicate edges,
diagnostic changes, status inflation, and forged normalization metadata.
Attacking the frozen `validate_weakened_candidate` routine gives:

| mutation | frozen validator |
|---|---|
| remove one recorded \(K\)-edge | rejects |
| change `claim_label` to `VERIFIED` | rejects |
| alter the recorded Berge count without updating the core | rejects |
| append a duplicate \(K\)-edge | **accepts** |
| change `active_order`, `K_degree`, `size3_point_count`, `root_mode`, `root_normalization`, `restrictions`, and `omitted_premise` while retaining the old semantic digest | **accepts** |
| relabel the valid core so that \(\{0,1,2\}\) is not a selected point, recompute the core digest, and retain metadata claiming that normalized root | **accepts** |

The reason is precise: the frozen diagnostic digest and validator bind only
`variant`, `point_sets`, deduplicated/sorted `K_edges`, and recomputed
diagnostics. They do not bind or validate the other schema fields, root
presence/mode, restrictions, or the absence of duplicate raw \(K\)-edge
records. The archived object itself passes the stricter checks, so this is a
validator/integrity failure rather than a refutation of that core.

There is also source/artifact skew. The archived witness's
`solver_statistics` lacks `cnf_sha256`, while the frozen source at the
reported hash always inserts that field before creating a candidate.
Running the frozen positive branch now reproduces the same core semantic
digest and yields the independently rebuilt formula hash
`8260378538dccf0b3b3355619ceb237d7d6f89e1f3b26d86ea316f7e593df146`,
but the full archived JSON is not the direct output of the frozen source as
written.

## Encoded and unencoded premises

The full common-point rule, meeting-crossing alternatives, exact \(F\)
union, point linearity, point \(K\)-cliques, overlap cap, incidence counts,
and exact \(K\)-degree are encoded.

The following are proof premises or deliberate restrictions outside the
CNF:

- the entire frozen Wave 6--12 active-triangle framework;
- reduction to the \(r=15,q=2^{15}\) profile;
- exclusion of point sizes four and five;
- derivation of the four local root modes and the structural minimum
  co-point counts;
- the aggregate arguments excluding \(m=13,15\) and restricting \(m=11\);
- fixed support for disjoint point sets and exact completion of the
  remaining fixed-point support;
- inactive vertices and point sets;
- a 99-vertex adjacency matrix and the global SRG
  \((99,14,1,2)\) equations.

The CNF also does not force every non-root selected size-three point to have
one of the four derived modes. That omission broadens the encoded search and
therefore does not invalidate branch coverage of valid objects. Likewise,
the human proof's later parity exclusion of 223 and its exclusion of 111
are not encoded; the scan retains those extra branches.

## Post-reconstruction comparison with the human proof

Only after completing the arithmetic, formula, and witness reconstruction
above, I read
`agents/2026-07-22-wave13-n3-45-proof-a.md` at SHA-256
`e721614256f003d7266d0b3d1bb2f884febbdec33893f92ed18bf8961c6958e8`.
Its nine profiles, mixed-order-fourteen reduction, large-point flower
arguments, and four order-fifteen local modes agree with the independent
results. Its direct special-label argument covers the mixed `(2,3,3)`
subcase omitted by the frozen profile program.

The human proof then uses additional non-SAT arguments to remove \(t=3\),
remove mode 111, and derive a final \(H\)-degree parity contradiction. Those
steps are outside this computational audit. The fact that the SAT scan kept
111 and 223 is safe overcoverage, not a missed branch. This report does not
promote the human proof's conditional \(n_3\ge48\) conclusion.

## Final status boundary

```text
restricted arithmetic/local reconstruction: PASS
17-branch semantic coverage:             PASS
17 exact formula-stream rebuilds:        PASS
frozen bundle self-validation:           FAIL
17 negative solver returns:              UNSAT_UNVERIFIED
n3=45 exclusion by this computation:     UNKNOWN
project target:                          UNKNOWN
novelty:                                 UNKNOWN
```
