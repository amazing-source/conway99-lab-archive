# Wave 16 structural audit of the conditional `n3=51` exclusion

Verdict: **PASS / VERIFIED for the scoped conditional claim.**  Under the
previously audited `H/L` and indexed-point framework, a putative
`srg(99,14,1,2)` cannot have project `n3=51`.

Independent enumeration gives sixteen raw `q`-profiles and exactly four
after the sound `d_K>=4` filter.  Their active original-vertex set `X` has
at most 25 vertices.  A complete endpoint-local crossing analysis proves
that every vertex of `G[X]` has at least six neighbors in `X`, without a
global `H`-degree restriction, a support graph, or a point-size-at-most-three
assumption.  The exact SRG spectral bound requires every such set to have at
least 27 vertices, a contradiction.

Combining the exclusion with the independently audited conditional bound
`n3>=51`, the exact divisibility `3|n3`, and the exact induced-cycle identity
gives the new conditional necessary bounds

```text
n3 >= 54,
induced_C6_count = 209286+n3 >= 209340.
```

This does not decide whether `srg(99,14,1,2)` exists.  The Conway-99 target
and novelty remain `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T11:20:07Z
git_commit: cea6065a0dc80f05e2ae379197f05d60c0f6e922
claim_label: VERIFIED
audit_verdict: PASS
scope: fresh post-freeze re-audit of the conditional exclusion n3=51 for a putative srg(99,14,1,2), and the resulting conditional n3/C6 lower bounds
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  CONJECTURE.md: 7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58
  agents/2026-07-23-wave16-n3-51-structural.md: 95d04a774397332417c9613718fe6699a5392ef5222fef1cfa00b12e2860af3f
  attempts/wave16-n3-51-structural/exact_check.py: 5aef211ea7d457543fc3f494eea125bbd0fd6fae2533fd566b475ff3f971c5cf
  attempts/wave16-n3-51-structural/test_exact_check.py: 4fbb3199e49a4d393eb6a434445b84a999eada8adbc801eff1557a36ea707a17
  attempts/wave16-n3-51-structural/exact-checks.json: 7419a54effd68d6853e787616a82dc618163d472d8969772cd2e6220b336ab24
  verification/2026-07-22-n3-count-bound-audit.md: 773321e8b9934d658f810c6c2eef0e00a339414d98be330ca273d3f9b8bd7753
  verification/2026-07-22-n3-side-incidence-audit.md: 9b6ff3cc9ec8bec13ffd93a8abe0bf0f35398c99f676d00064d6bf5fe6db6787
  verification/2026-07-22-wave12-n3-42-premise-audit.md: abc6be22f73735e2e46c3c59cbb3b15665b9b639db4b263b59a3c50515ba13a2
  verification/2026-07-22-wave12-integration-audit.md: 90021fc6f29cfc4ac0d3df07769ce43b4f270a99a13784ff7491711d15352e70
  verification/2026-07-22-wave13-n3-45-audit.md: a7e520790680a3cec1d8fcff42db30105572aefeea8a41cf178aaf703147925a
  verification/2026-07-22-wave14-n3-48-proof-audit.md: 44d1383548b26660dfb5d4b140c831774f6ca81e58ae140e3ceb2f80a9740802
  wave15_global_lift_audit_as_declared_and_initially_read_historical: d5e931284407a2071eaf1e6523aac045c96df0b212c946cd4e9b074b9cf41191
  wave15_global_lift_audit_pinned_by_first_wave16_audit_historical_uncommitted: decaa1c2657071013159474d896e8a7c71212a4e4e2a37c2530e5cf18fe2c1d2
  wave16_discovery_report_pre_repair_historical: 62c4dad2faa03a5f16e39e7b8efd6cc2bc1a7a93e445be3c2c87f50b4616d97d
  wave16_discovery_failed_baseline_commit: 09c20e6c8774ff8676de789b631fd7b0973cf1f5
  wave16_discovery_provenance_repair_commit: 7530caebc2705dd3b5a6682cf89c51b55810db7a
  verification/2026-07-23-wave15-global-lift-audit.md: edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036
method: fresh post-freeze provenance check, independent premise replay, exact profile generation, independent reconstruction of the degree-three obstruction, exhaustive overlap-deleted crossing enumeration, original-vertex indexing and distinctness audit, explicit no-point-size-cap and endpoint-local H-degree scope audits, exact Rayleigh quotient replay, exact divisibility/C6 consequence replay, submitted-artifact comparison, and twenty-four hostile/provenance/consequence tests
command: |
  .venv\Scripts\python.exe -B verification\n3-51-structural\independent_check.py
  cd verification\n3-51-structural
  ..\..\.venv\Scripts\python.exe -B -m unittest -v test_independent_check.py
  cd ..\..
  .venv\Scripts\python.exe -B attempts\wave16-n3-51-structural\exact_check.py --verify attempts\wave16-n3-51-structural\exact-checks.json
  .venv\Scripts\python.exe -B -m unittest -v attempts\wave16-n3-51-structural\test_exact_check.py
outputs:
  verification/n3-51-structural/preinspection-freeze.md: debd11429f8eccc1b5de0e7ecb68b508741a0e5cc21666cce99cb4831a2bd28f
  verification/n3-51-structural/independent_check.py: a28e4ed757d7d12820ba129644830206b789bce987b7716da23933d70d372b25
  verification/n3-51-structural/test_independent_check.py: dcc767dd0300fb14ed0b69133bb36444d0f0ccd47044ef3fd5397d7c964fb60a
  independent_semantic_sha256: 2820828021ae7d0d622533f5ce87ddc8a0a150a9784cf984fe0450301f46e3c6
  final_wave15_public_hash_check: PASS
  historical_intermediate_hash_retained: PASS
  raw_profiles: 16
  profiles_after_d_K_at_least_4: 4
  independent_hostile_provenance_and_consequence_tests: "24/24 PASS"
  submitted_exact_checker: PASS
  submitted_focused_tests: "8/8 PASS"
  conditional_n3_51: EXCLUDED_VERIFIED
  conditional_n3_lower_bound: 54
  conditional_induced_C6_lower_bound: 209340
  conway_99_target: UNKNOWN
  novelty: UNKNOWN
limitations: conditional on the previously audited H/L, no-singleton, indexed-point, fixed-point, and target spectral premises rather than a raw 99-by-99 adjacency derivation; the finite checkers accompany rather than replace the human semantic bridge; no Wave 16 computational report, source, result, or artifact was read; no formal proof object, target existence/nonexistence result, construction, automorphism assumption, or novelty conclusion is supplied; the two earlier Wave 15 hashes are historical provenance only and are not accepted as current inputs
```

The `git_commit` value was read directly from `.git/HEAD` and its referenced
file at `2026-07-23T11:18:45Z`; no Git command was run.  The shared branch
may move independently.  The first audit's recorded commit
`522260aa71d484c86477599de65f9e08ded437bb` remains visible in repository
history and is not being rewritten by this post-freeze re-audit.

## 0. Post-freeze provenance re-audit

The first Wave 16 audit happened while the Wave 15 audit file was still
changing in the shared workspace.  Its complete provenance sequence is
retained:

```text
hash declared by the submitted Wave 16 report:
d5e931284407a2071eaf1e6523aac045c96df0b212c946cd4e9b074b9cf41191

intermediate uncommitted hash pinned by the first Wave 16 audit:
decaa1c2657071013159474d896e8a7c71212a4e4e2a37c2530e5cf18fe2c1d2

final publicly frozen Wave 15 audit hash used by this re-audit:
edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036
```

The updated independent checker hashes the final Wave 15 file on every run
and fails unless it matches the last value exactly.  It also retains the
first two values as explicitly historical constants.  Two new provenance
tests confirm both properties.  The original preinspection freeze remains
byte-unchanged at
`debd11429f8eccc1b5de0e7ecb68b508741a0e5cc21666cce99cb4831a2bd28f`;
the post-freeze check supplements rather than retroactively rewrites it.

The intermediate Wave 15 bytes are no longer present as a standalone file,
so this re-audit does not claim a bytewise or full semantic comparison with
that historical state.  Fresh comparison of the final frozen Wave 15 proof
against the subset lemma transcribed in the first Wave 16 audit found no
change to the imported statement:

```text
2e(G[X]) <= 3|X|+|X|^2/9,
delta(G[X])>=6 implies |X|>=27.
```

The changes between those Wave 15 audit states concern public provenance and
metadata history, not the matrix identity, eigenvalue calculation, subset
inequality, or status boundary.  The Wave 16 proof was nevertheless replayed
from the final frozen input rather than accepted by semantic-diff assertion.

After this verifier replay, the discovery report received the corresponding
transparent provenance-note repair.  Its pre-repair bytes are preserved by
failed-baseline commit
`09c20e6c8774ff8676de789b631fd7b0973cf1f5`; their SHA-256 was
`62c4dad2faa03a5f16e39e7b8efd6cc2bc1a7a93e445be3c2c87f50b4616d97d`.
The repaired report has SHA-256
`95d04a774397332417c9613718fe6699a5392ef5222fef1cfa00b12e2860af3f`,
pins `edda3785...` as its current Wave 15 input, and retains `d5e931...` as
historical.  The repair is committed at
`7530caebc2705dd3b5a6682cf89c51b55810db7a`.  Inspection confirms that this
repair changes provenance
metadata and explanatory text only; its derivation, evidence outputs, claim
label, bounds, target status, and novelty status are unchanged.

## 1. Independence and source boundary

The accepted premises were frozen in
`verification/n3-51-structural/preinspection-freeze.md` before any submitted
file under `attempts/wave16-n3-51-structural/` was opened.  The human Wave 16
report had necessarily already been read because it is the object assigned
for audit; the freeze explicitly records that ordering.  The independent
checker imports no discovery module.

No Wave 16 computational report, source, result, or artifact was opened.
An initial repository filename inventory exposed the existence of a
computational-lane path, but none of its contents was read and no premise or
status from it is used here.

The submitted Wave 16 report declared the Wave 15 audit at
`d5e931284407a2071eaf1e6523aac045c96df0b212c946cd4e9b074b9cf41191`.
The first Wave 16 verifier run later pinned the then-current intermediate,
uncommitted hash
`decaa1c2657071013159474d896e8a7c71212a4e4e2a37c2530e5cf18fe2c1d2`.
This re-audit instead reads and executable-checks the final public hash
`edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036`.
All three observations are retained above; the intermediate input is
historical provenance, not silently presented as the public artifact.

The imported facts are limited to:

1. `d_L(T)=3q(T)`, `q(T)=0` or `q(T)>=2`, and
   `sum_T q(T)=2n3/3`;
2. the simple active complement `K`, the indexed original-vertex points
   `S_u`, no active singleton, linearity, three points through every active
   label, and the prohibition on three distinct pairwise meeting labels;
3. for an actual graph edge, the two-sided zero-or-two labeled crossing rule
   after deleting both copies of a possible common label, together with
   the support and fixed-point identities; and
4. the exact target matrix equation and resulting subset spectral bound.

No Wave 14 residual classification, point-size upper bound, support graph,
active-layer candidate, automorphism, or solver result is imported.

## 2. Exact profile enumeration and the `d_K>=4` filter

At `n3=51`,

```text
sum_T q(T)=34,   q(T)>=2,   3q(T)<=r-1,
d_K(T)=r-1-3q(T).
```

Independent nondecreasing partition generation reproduces exactly sixteen
rows, distributed by active-label count as

```text
r:                 12  13  14  15  16  17
number of profiles: 1   5   4   3   2   1.
```

Filtering only by `d_K>=3` leaves six rows.  The equality case is genuinely
impossible and not merely inherited as a numerical heuristic.  If
`d_K(x)=3` and `N_K(x)={a,b,c}`, the three non-singleton linear points
through `x` must be

```text
{x,a}, {x,b}, {x,c}.
```

Consider the two other indexed points through label `a`.  Their original
vertex indices are the other two vertices of graph-triangle `a`, so each
forms an actual graph edge with the vertex indexing `{x,a}`.  Delete the
common label `a`.  The `{x,a}` side is the singleton row `{x}`; the
two-sided zero-or-two rule forces the crossing to be empty.  Every external
label of either other point is therefore a `K`-neighbor of `x`.  Linearity
makes the two external parts nonempty and disjoint, while only `b,c` are
available.  Hence they are `{a,b}` and `{a,c}`.

Now `{x,a}`, `{x,b}`, and `{a,b}` meet pairwise at the three distinct labels
`x,a,b`, contrary to the audited common-point rule.  The independent finite
replay finds the two ordered external assignments and the forbidden triple
in both.  Therefore every active label has `d_K>=4`.

Exactly four profiles survive:

| `r` | `q` multiset | `d_K` multiset | `floor(3r/2)` |
|---:|---|---|---:|
| 14 | `2^8 3^6` | `7^8 4^6` | 21 |
| 15 | `2^11 3^4` | `8^11 5^4` | 22 |
| 16 | `2^14 3^2` | `9^14 6^2` | 24 |
| 17 | `2^17` | `10^17` | 25 |

The two extra rows admitted by the hostile `d_K>=3` weakening are exactly
`r=13, q=2^5 3^8` and `r=16, q=2^15 4`.  Thus the repeated-degree-three
argument is essential and has the right quantifiers.

## 3. `X` consists of indexed original vertices

Define

```text
X={u in V(G):S_u is nonempty}.
```

This is a set of original vertex indices, not a quotient of abstract point
values.  Every active graph-triangle occurs in the three points indexed by
its three original vertices, so

```text
sum_{u in X}|S_u|=3r.
```

Every summand is at least two.  Therefore

```text
|X|<=floor(3r/2)<=25.
```

Even if one attempted to quotient equal point values, two distinct indexed
points of size at least two cannot be equal: they would share two active
triangle labels, contrary to linearity.  The proof does not require this
extra observation because it retains the original indices throughout.

## 4. Complete size-two endpoint classification

Fix an indexed size-two point

```text
P=S_u={i,j}
```

and an actual graph neighbor `v` of `u`; put `Q=S_v`.  Linearity permits
`|P intersect Q|` to be zero or one.

| Case | Crossing after deletion | Exact edge counts |
|---|---|---|
| `Q` empty | two rows, zero columns | `{0}` |
| `P,Q` meet | one row, any remaining width | `{0}` |
| `P,Q` disjoint and `|Q|>=2` | two rows | `{0,4}` |

In the meeting case, every column has at most one incident entry, so the
column-side zero-or-two rule makes every column zero.  In the disjoint case,
any nonzero column meets both rows.  A nonzero row has exactly two entries,
so exactly two columns are selected and all four entries of their
`K_(2,2)` are present.  The independent checker exhausts every relevant
width through the maximum active-label count 17.

Consequently, for every actual edge incident with this fixed size-two
endpoint,

```text
d_H(uv) in {0,4}.
```

This is endpoint-local.  The independent hostile checker finds a legal
six-edge two-sided `3`-by-`3` crossing, so it explicitly does **not** assume
that all vertices of `H` have degree zero or four.

The fixed-point identity now gives:

| labels in `P` | fixed sum | positive original neighbors |
|---|---:|---:|
| `(2,2)` | 8 | exactly 2 |
| `(2,3)` | 10 | impossible |
| `(3,3)` | 12 | exactly 3 |

The word “neighbors” here has its literal original-graph meaning.  The sum
runs over the fourteen distinct indices `v in N_G(u)`, so two or three
positive terms are automatically two or three distinct vertices; no support
multiplicity is reified as a vertex.

Every positive term has `Q` nonempty, hence `v in X`.  It also has
`P intersect Q` empty, because every meeting crossing is zero.  Therefore a
positive neighbor is not one of the active-triangle neighbors of `u`: such
a neighbor shares the active graph-triangle label containing the edge.
This proves simultaneously the activity, nonmeeting, distinctness, actual
adjacency, and nonoverlap properties required by the local-to-global step.

The argument defines no support graph `R`.  Indeed the `(3,3)` row has three
positive neighbors for a point of size two, so the Wave 14 identity
`d_R(P)=|P|` would be false here and is not used.

## 5. Minimum degree without a point-size cap

Each active triangle in `S_u` supplies its two other original vertices as
neighbors of `u` in `X`.  Two different triangles through `u` cannot reuse
one of these vertices: that would put the same graph edge in two triangles
and give an adjacent pair two common neighbors, contradicting `lambda=1`.
Thus the active triangles supply exactly

```text
2|S_u|
```

distinct neighbors in `X`.

- If `|S_u|>=3`, these triangle neighbors alone give at least six.
- If `|S_u|=2` has labels `(2,2)`, its four triangle neighbors and two
  distinct positive nonmeeting neighbors give at least six.
- If `|S_u|=2` has labels `(3,3)`, the corresponding total is at least
  seven.
- The mixed `(2,3)` size-two point is arithmetically impossible.

No point-size-at-most-three statement occurs here.  Feasible sizes four
through seven are handled directly by their eight through fourteen distinct
triangle neighbors.  A point of size at least eight is itself impossible in
a 14-regular graph for the same distinct-neighbor reason.  Therefore every
existing vertex of `X` satisfies

```text
delta(G[X])>=6.
```

## 6. Independent exact spectral replay

For the target adjacency matrix,

```text
A^2=12I-A+2J.
```

On the all-ones orthogonal subspace the eigenvalues solve
`theta^2+theta-12=0`, so the largest restricted eigenvalue is exactly three.
For the indicator `x` of an `m`-vertex set, write

```text
x=(m/99)1+y,  y perpendicular to 1.
```

Then, with exact rational arithmetic,

```text
2e(G[X])
 = x^T A x
 <= 14m^2/99+3(m-m^2/99)
 = 3m+11m^2/99
 = 3m+m^2/9.
```

Minimum degree six gives `2e(G[X])>=6m`; since `m>0`,

```text
6m<=3m+m^2/9
```

forces `m>=27`.  The threshold is sharp for this inequality:

```text
m=25: lower 150, upper 1300/9 < 150;
m=27: lower 162, upper 162.
```

This contradicts the independent active-set upper bound `m<=25`.

## 7. Hostile/provenance/consequence tests and submitted-artifact comparison

The twenty-four independent tests comprise twenty pre-existing structural
and hostile tests, two public-provenance tests, and two exact consequence
tests.  The mathematical mutations include:

| Mutation | Outcome |
|---|---|
| Retain a common label instead of deleting both copies | A false four-edge crossing becomes possible. |
| Enforce row degrees but not column degrees | Two-edge crossings appear; mixed fixed sum ten is no longer excluded. |
| Permit `d_K=3` | Exactly two extra profiles survive. |
| Reuse one original triangle neighbor across labels | Rejected as a `lambda=1` violation. |
| Reuse one positive support index | Rejected; the fixed sum is indexed by distinct graph neighbors. |
| Allow a positive meeting or empty-endpoint crossing | Rejected by exhaustive crossing enumeration. |
| Assume global `H`-degree `{0,4}` | Countercontrolled by a legal six-edge `3`-by-`3` crossing. |
| Assume `d_R(P)=|P|` | Countercontrolled by the `(3,3)` size-two row: support count three, point size two. |
| Truncate point sizes at three | Sizes four through seven are checked explicitly; larger sizes exceed degree 14. |
| Allow singleton active points | The active-set cap can rise to 51, destroying the contradiction. |
| Replace restricted eigenvalue three by four | The first allowed order drops to 20 and `m=25` is no longer excluded. |
| Weaken minimum degree six to five | The spectral contradiction at `m=25` disappears. |

The submitted structural checker and its frozen JSON reproduce the same
sixteen profiles, four survivors, crossing alternatives, fixed sums,
active-set caps, and spectral threshold.  All eight submitted focused tests
pass.  Its program correctly describes itself as an arithmetic
accompaniment rather than a verifier of the human semantic bridge.

The two added provenance tests require the final Wave 15 public hash
`edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036`
and require the intermediate uncommitted hash to remain recorded but
different from the accepted input.  Thus a future silent replacement of
either provenance role fails executable verification.

The two consequence tests replay `3*34=2*51`, coprime cancellation to
`3|n3`, the next multiple `54` after excluding `51`, and
`209286+54=209340`.  A mutated incidence identity at `n3=52` and a
nonpositive divisor are rejected.

One byte-hygiene validation wrapper initially failed at PowerShell parse
time with `An empty pipe element is not allowed` because a `foreach` block
was piped directly to `Format-List`.  It ran no checker, changed no file, and
produced no mathematical evidence.  The corrected wrapper first collected
the rows and then formatted them; all four verifier artifacts had zero CRLF,
zero bare carriage returns, zero trailing-whitespace lines, exactly one
terminal line feed, and no trailing blank line.

## 8. Consequences and status boundary

The exact identity

```text
3 sum_T q(T)=2n3
```

and integrality of the left sum imply `3|n3`.  The independently audited
Wave 15 result gives the prior conditional necessary bound `n3>=51`; the
present audit verifies exclusion of equality.  Hence the next possible value
is 54.  Substitution into the exact cycle identity gives

```text
n3>=54,
induced_C6_count=209286+n3>=209340.
```

Final boundary:

```text
Wave 16 structural argument:             PASS / VERIFIED
conditional n3=51:                       EXCLUDED / VERIFIED
conditional n3 lower bound:              54
conditional induced-C6 lower bound:      209340
global H-degree restriction:             NOT ASSUMED
support graph R or d_R identity:          NOT USED
point-size-at-most-three restriction:     NOT USED
Wave 16 computational lane:              NOT INSPECTED
Conway srg(99,14,1,2):                   UNKNOWN
novelty:                                  UNKNOWN
```
