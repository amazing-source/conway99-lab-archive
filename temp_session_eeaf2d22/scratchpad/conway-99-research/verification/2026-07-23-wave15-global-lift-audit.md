# Wave 15 `n3=48` global-lift adversarial audit

Verdict: **PASS for the scoped `DERIVED` exclusion of `n3=48`.**  The
audited Wave 14 residual forces an induced set `X` of at most 24 original
vertices with minimum internal degree at least six.  An
`srg(99,14,1,2)` cannot contain such a set: its positive restricted
eigenvalue is three and the exact subset bound gives `|X|>=27`.

An independent outside-vertex second-moment proof gives the same
contradiction, and hostile mutations confirm that the sixth neighbor and
the deletion of the shared active label are essential.  No gap was found in
the submitted bridge or arithmetic.

Combining the new equality exclusion with the previously audited
`n3>=48`, the inherited divisibility `3 | n3`, and the exact induced-cycle
identity gives the conditional necessary bounds

```text
n3 >= 51,
induced_C6_count = 209286+n3 >= 209337.
```

This does not decide whether `srg(99,14,1,2)` exists.  The Conway-99 target
and novelty remain `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T10:42:31Z
git_commit: 6b6d721885a6d7c8451c6d6322a35e881b72d94e
claim_label: DERIVED
audit_verdict: PASS
scope: conditional exclusion of n3=48 for a putative srg(99,14,1,2), assuming the independently audited Wave 14 residual
inputs:
  agents/2026-07-22-wave14-n3-48-proof-a.md: f0a7d7b5638415cff7d5ad4ef176542de9aa89a2b46a03347f90a2133f18999c
  verification/2026-07-22-wave14-n3-48-proof-audit.md: 44d1383548b26660dfb5d4b140c831774f6ca81e58ae140e3ceb2f80a9740802
  agents/2026-07-23-wave15-global-lift.md: ac5045268fdf5042cd6b975baa942a1a905870d1eaebfa4d25096fc81e03b843
  attempts/wave15-global-lift/preinspection-freeze.md: 28705cbf7897cc74c2bd5a301d491bdb84830cbffcde36da4eb8a3524aec4685
  attempts/wave15-global-lift/build_subset_moment_certificate.py: 22c87bb40fb860c981b61fca66af49f896548e8083fd069007f8b2b94cfd32ba
  attempts/wave15-global-lift/verify_subset_moment_certificate.py: 0429db33fa0a61864ff8456326379fab47a09e7b8ea7234130d12b018cd041c2
  attempts/wave15-global-lift/test_subset_moment.py: a1c981666166b97d0d84d9f90c4c977e3dff9f3e5cc61b1e57711b9d9ce642f7
  attempts/wave15-global-lift/subset-moment-certificate.json: cb02ab80f92d7d2c8ec5140e3be2916354976442aa2e1869524aa728c73bd386
  agents/2026-07-22-wave6-opposite-edge-graph.md: 4197c40e1b43d72d5a2ad9a6203099ffed2e1dbf4f0b3c07186aaad54cae4fa2
  verification/2026-07-22-wave13-n3-45-audit.md: a7e520790680a3cec1d8fcff42db30105572aefeea8a41cf178aaf703147925a
  verification/2026-07-22-wave14-status-audit.md: b41d501b8fefda44268e7fb9e2fe1012d1a2da0081433da6b0621c448c23014e
  verification/n3-48-global-lift/preinspection-freeze.md: c83bb89600d27eeee7e45040bd2fffcf2b089c25a015b2799bb61d2cc6a88bb3
method: independent preinspection reconstruction, point-to-vertex semantic audit, exact crossing enumeration, two independent SRG subset derivations, all-profile arithmetic replay, and hostile premise mutations
command: |
  .venv\Scripts\python.exe -B attempts\wave15-global-lift\build_subset_moment_certificate.py --countermodel attempts\wave14-proof-a\all2-active-countermodel.json --output verification\n3-48-global-lift\regenerated-certificate.json
  .venv\Scripts\python.exe -B verification\n3-48-global-lift\independent_check.py
  cd verification\n3-48-global-lift
  ..\..\.venv\Scripts\python.exe -B -m unittest -v test_independent_check.py
  cd ..\..
  .venv\Scripts\python.exe -B attempts\wave15-global-lift\verify_subset_moment_certificate.py attempts\wave15-global-lift\subset-moment-certificate.json
  .venv\Scripts\python.exe -B -m unittest -v attempts\wave15-global-lift\test_subset_moment.py
outputs:
  verification/n3-48-global-lift/independent_check.py: ce813ef1399a29eb93bd29768b6e3b40b21a187cd275d938516e3f6174f57c94
  verification/n3-48-global-lift/test_independent_check.py: a217ef8ba4764cf0f4d0573d8f5d2bae6c488dcf176abbb86538a0748ed27213
  verification/n3-48-global-lift/regenerated-certificate.json: cb02ab80f92d7d2c8ec5140e3be2916354976442aa2e1869524aa728c73bd386
  independent_checker: PASS
  independent_hostile_tests: "11/11 PASS"
  submitted_arithmetic_verifier: PASS
  submitted_focused_tests: "5/5 PASS"
  public_lf_bundle_crlf_count: 0
  exact_certificate_regeneration: PASS_BYTE_IDENTICAL
  initial_failed_public_baseline_commit: 522260a
  pre_repair_crlf_certificate_sha256: 42d1da171274d82fa87c9489f1ed3e3334c404ea7f8f1ddce27021893831a4df
  normalized_discovery_report_eof: PASS_ONE_TERMINAL_LF_NO_TRAILING_BLANK
  normalized_discovery_freeze_eof: PASS_ONE_TERMINAL_LF_NO_TRAILING_BLANK
  normalization_semantic_reaudit: PASS_METADATA_ONLY
  conditional_n3_48_exclusion: EXCLUDED_DERIVED
  conditional_n3_lower_bound: 51
  conditional_induced_C6_lower_bound: 209337
  conway_99_target: UNKNOWN
  novelty: UNKNOWN
limitations: conditional on the audited Wave 14 semantic framework rather than a raw 99-by-99 adjacency derivation; the arithmetic scripts accompany rather than replace the human bridge; no unconditional target, construction, formal proof object, or novelty claim is supplied
```

The `git_commit` value was read directly from `.git/HEAD` and its ref file;
no Git command was run.  The shared-workspace branch may have moved since
that observation.

## Public LF repair re-audit

The initial discovery baseline commit `522260a` is preserved as a failed
public-provenance baseline.  In that state, the Windows worktree certificate
used CRLF bytes with SHA-256

```text
42d1da171274d82fa87c9489f1ed3e3334c404ea7f8f1ddce27021893831a4df,
```

while public Git normalization produced different LF bytes.  The repaired
builder now writes `newline="\n"` explicitly.  The pre-repair builder hash
is retained here as

```text
d8bff71e134666d45b8e08f995967f0765b9be41a062d3b7b532abcaa043a0be.
```

The repaired public-LF bundle has the exact hashes:

```text
discovery report:
ac5045268fdf5042cd6b975baa942a1a905870d1eaebfa4d25096fc81e03b843

preinspection freeze, unchanged:
28705cbf7897cc74c2bd5a301d491bdb84830cbffcde36da4eb8a3524aec4685

certificate builder:
22c87bb40fb860c981b61fca66af49f896548e8083fd069007f8b2b94cfd32ba

LF certificate:
cb02ab80f92d7d2c8ec5140e3be2916354976442aa2e1869524aa728c73bd386

submitted verifier, unchanged:
0429db33fa0a61864ff8456326379fab47a09e7b8ea7234130d12b018cd041c2

submitted tests, unchanged:
a1c981666166b97d0d84d9f90c4c977e3dff9f3e5cc61b1e57711b9d9ce642f7
```

Byte inspection gives CRLF count zero for every displayed repaired bundle
file.  Each also has exactly one terminal line-feed sequence and no trailing
blank line.

Fresh execution of the repaired builder against the frozen Wave 14
countermodel produced
`verification/n3-48-global-lift/regenerated-certificate.json`.  It has
length 5,147 bytes, zero CRLF sequences, SHA-256
`cb02ab80f92d7d2c8ec5140e3be2916354976442aa2e1869524aa728c73bd386`,
and is byte-for-byte identical to the submitted repaired certificate.

The first attempted regeneration wrapper targeted a unique operating-system
temporary path, but command policy rejected the wrapper before execution.
It produced no certificate and ran no tests.  The verifier then used the
assigned verifier path above; exact regeneration passed.  After that repair,
the five submitted tests and eleven independent hostile tests all passed.

The repair changes byte-level public provenance only.  It changes no
mathematical premise, proof step, certificate semantics, derived bound,
claim label, target status, or novelty status.

## Metadata-only normalization re-audit

After the discovery lane normalized its report and preinspection-freeze
metadata, this verifier repeated the provenance and execution checks.  The
normalized hashes are exactly:

```text
agents/2026-07-23-wave15-global-lift.md
cae721e807b84b1400ce401f443b3b92a8ec8dc6abdacf2942eb70ec753c78a7

attempts/wave15-global-lift/preinspection-freeze.md
28705cbf7897cc74c2bd5a301d491bdb84830cbffcde36da4eb8a3524aec4685
```

Byte-level inspection finds exactly one terminal line feed and no trailing
blank line in each normalized file.  The mathematical proof, Wave 14
countermodel, Wave 15 certificate, and executable artifact hashes remain:

```text
Wave 14 proof report:
f0a7d7b5638415cff7d5ad4ef176542de9aa89a2b46a03347f90a2133f18999c

Wave 14 active countermodel:
5d06ae777fb0ca4450951708bba3ffc85d1f617be1d19c2be210f43df82b8952

Wave 15 arithmetic certificate:
42d1da171274d82fa87c9489f1ed3e3334c404ea7f8f1ddce27021893831a4df

Wave 15 builder / submitted verifier / submitted tests:
d8bff71e134666d45b8e08f995967f0765b9be41a062d3b7b532abcaa043a0be
0429db33fa0a61864ff8456326379fab47a09e7b8ea7234130d12b018cd041c2
a1c981666166b97d0d84d9f90c4c977e3dff9f3e5cc61b1e57711b9d9ce642f7
```

The submitted five tests and the eleven independent hostile tests were
rerun after normalization; all sixteen pass.  The normalization changes no
mathematical premise, derivation, certificate result, status boundary, or
verdict.  It is recorded here rather than silently replacing the earlier
provenance hash.

## 1. Independence protocol

Before opening the submitted Wave 15 report or any Wave 15 attempt artifact,
I reconstructed the global lift from only the frozen Wave 14 proof and its
independent audit.  That reconstruction was written to
`verification/n3-48-global-lift/preinspection-freeze.md`.  It already
contained:

```text
|X| <= 24,
delta(G[X]) >= 6,
average_degree(G[X]) <= 3+|X|/9,
therefore |X| >= 27,
```

and hence the anticipated contradiction.

Only after that freeze did I inspect
`agents/2026-07-23-wave15-global-lift.md` and its four arithmetic
artifacts.  I did not open the separate Wave 15 algebraic report.  A later
repository-wide text search for the already inherited divisibility fact
returned one isolated matching line from that sibling report; the
mathematical reconstruction and scoped verdict had already been frozen, and
no sibling derivation or result was used here.

The submitted global-lift report matches the independent reconstruction.

## 2. Audit of every local-to-global bridge

### 2.1 Indexed points are original vertices

The audited premise is not an abstract collection of unindexed subsets.
For each original vertex `u`, its nonempty active point is

```text
S_u = {active graph-triangle labels containing u}.
```

Thus every point object is indexed by one original vertex, and distinct
point objects correspond to distinct indices in

```text
X = {u in V(G): S_u is nonempty}.
```

No quotient by equal set values is taken.  Even if one tries to identify
equal values, duplicates cannot occur here: if `S_u=S_v` contained two
active labels, two distinct graph-triangles would contain both `u` and
`v`.  They would put the edge `uv` in two triangles, giving the adjacent
pair two common neighbors and contradicting `lambda=1`.

### 2.2 The active set has at most 24 vertices

Each of the sixteen active labels is a graph-triangle and occurs in its
three vertex-points.  The audited residual permits only point sizes two and
three.  If `x_2,x_3` count the corresponding indexed vertices, then

```text
2x_2+3x_3=16*3=48,
|X|=x_2+x_3<=24.                                        (1)
```

The independent checker enumerates all nine nonnegative solutions:

```text
(x_2,x_3) =
(24,0),(21,2),(18,4),(15,6),(12,8),
(9,10),(6,12),(3,14),(0,16),
```

with `|X|` ranging from 24 down to 16.  The argument needs only the
inequality in (1), not this enumeration.

### 2.3 Active triangles give `2|S_u|` distinct neighbors in `X`

Every label in `S_u` is an actual triangle through `u`.  Its other two
vertices are adjacent to `u` and have nonempty active points, so they lie in
`X`.

The vertices supplied by two different labels are disjoint.  If two such
triangles shared a second vertex `v`, they would both contain the graph edge
`uv`; their two different third vertices would be two common neighbors of
the adjacent pair `u,v`, again contradicting `lambda=1`.  Hence

```text
u has 2|S_u| distinct active-triangle neighbors in X.    (2)
```

### 2.4 `R` supplies distinct actual graph neighbors

The audited Wave 14 residual defines `R` as a **simple** graph on the
indexed active point objects.  An `R`-edge `S_uS_v` records the actual
graph edge `uv` and has `d_H(uv)=4`.  Therefore:

- there are no loops or parallel support incidences;
- different `R`-neighbors are different original vertices in `X`;
- every `R`-neighbor is adjacent in `G[X]`; and
- the exact fixed-point sum gives
  `d_R(S_u)=|S_u|`.

No candidate-only support edge is promoted to an original graph adjacency
in this step; actual adjacency is part of the audited definition of `R`.

### 2.5 A size-two support neighbor cannot be a triangle neighbor

This is the critical overlap check.  Let `P=S_u` have size two and suppose
that an `R`-neighbor `Q=S_v` were also one of the four neighbors supplied
by an active triangle.  Then `P` and `Q` share that active label.  They
cannot share a second label by the preceding `lambda=1` argument.

For the actual graph edge `uv`, delete both labeled copies of the common
active label as required by the inherited meeting-crossing rule.  The
remaining crossing has one row on the `P` side and at most two columns on
the `Q` side, since `|Q|` is two or three.  The two-sided `0/2` rule in
fact forces this crossing to be empty: any nonzero column would have degree
one.  Thus

```text
d_H(uv)=e_L(P,Q)=0,
```

whereas an `R`-edge requires `d_H(uv)=4`.  Contradiction.

The submitted proof uses the slightly weaker observation that a
`1 by 2` crossing has at most two edges, which is already enough to rule
out `d_H=4`.  The independent exhaustive crossing check recovers the
stronger exact value zero for both possible sizes of `Q`.

### 2.6 Minimum induced degree

If `|S_u|=3`, equation (2) already supplies six distinct neighbors.  If
`|S_u|=2`, equation (2) supplies four and `d_R(S_u)=2` supplies two more;
Section 2.5 proves the two groups disjoint.  Therefore

```text
delta(G[X])>=6.                                          (3)
```

Additional edges inside `X` can only increase induced degrees, so omitted
active-active edges do not weaken (3).

## 3. Independent spectral contradiction

For an `srg(99,14,1,2)` with adjacency matrix `A`,

```text
A^2=12I-A+2J.
```

On the subspace perpendicular to the all-ones vector, the restricted
eigenvalues solve

```text
theta^2+theta-12=0,
theta in {3,-4}.
```

Let `m=|X|`, let `e=e(G[X])`, and decompose

```text
1_X=(m/99)1+y,  y perpendicular to 1.
```

The largest restricted eigenvalue is three, so

```text
2e
 <= 14m^2/99+3(m-m^2/99)
 = 3m+m^2/9.                                             (4)
```

From (3), `2e>=6m`.  Combining with (4) gives

```text
6m<=3m+m^2/9,
m>=27.                                                   (5)
```

This contradicts `m<=24`.  The sign and eigenvalue choice are correct:
the upper bound uses the positive restricted eigenvalue `3`, not the least
eigenvalue `-4`.

## 4. Independent outside second-moment contradiction

The second proof was also reconstructed exactly.  For `x in X` put
`d_x=|N(x) intersect X|`; for `z outside X` put
`a_z=|N(z) intersect X|`.  Counting the cut gives

```text
sum_z a_z=14m-sum_x d_x.                                (6)
```

Every adjacent pair in `X` has one common neighbor and every nonadjacent
pair has two.  Counting these common neighbors first by the pair and then
by the common vertex gives

```text
sum_z C(a_z,2)
 = m(m-1)-e-sum_x C(d_x,2).                             (7)
```

Equations (6)-(7), with `2e=sum_x d_x`, imply

```text
sum_z a_z^2
 = 2m^2+12m-sum_x(d_x^2+d_x).                           (8)
```

Write `d_x=6+s_x`, `T=sum s_x`, and `U=sum s_x^2`.
Cauchy over the `99-m` outside vertices requires

```text
Phi
 = (99-m)(2m^2-30m-13T-U)-(8m-T)^2
 = -2m(m-27)(m-55)
   +(29m-1287)T-(99-m)U-T^2
 >=0.                                                    (9)
```

For `0<m<=24`, the constant term is strictly negative,
`29m-1287<=-591`, and `T,U>=0`.  Every term on the final line of (9) is
therefore nonpositive and the constant is strictly negative, so
`Phi<0`.  This is a second complete contradiction.

The independent checker verifies the direct and expanded forms of (9) for
every `m<=24`, not just the nine incidence profiles.  It also confirms that
increasing any internal degree only makes the defect more negative.

## 5. Concrete all-size-two replay

For the Wave 14 all-size-two relaxation, `m=24` and the mandatory induced
subgraph is 6-regular with 72 edges.  A lift with no additional internal
edges would force the 75 outside degrees to satisfy

```text
sum a_z=192,
sum a_z^2=432.
```

But the minimum square sum of 75 nonnegative integers totaling 192 is
attained by 33 twos and 42 threes:

```text
33*2^2+42*3^2=510>432.
```

The deficit is 78.  Formula (9) proves that additional edges inside `X`
cannot repair it.

This refutes a full SRG lift, not the frozen active-layer object itself.
The Wave 14 object remains a valid `CANDIDATE` countermodel to its stated
narrow relaxation.

## 6. Hostile mutations and evidence boundary

The independent checker and eleven focused tests attack the assumptions
most likely to create a false lift:

| mutation or boundary | result | significance |
|---|---|---|
| Retain rather than delete the shared active label | A legal four-edge `2 by 3` crossing appears | The inherited labeled deletion is essential and is present. |
| Permit one support/triangle-neighbor overlap at a size-two point | The guaranteed degree drops from six to five | The exact `d_H=0` versus `d_H=4` argument forbids the overlap. |
| Replace the simple `R` by parallel support incidences | Two incidences need not give two vertices | The audited `R` is simple and comes from a simple original graph. |
| Treat an `R`-edge as nonadjacent in the original graph | The lift to `G[X]` fails | Actual graph adjacency is part of the audited definition of `R`. |
| Weaken minimum degree six to five at `m=24` | Neither proof gives the claimed contradiction | Confirms that the support-derived sixth neighbor is substantive. |
| Mutate the positive restricted eigenvalue from three to four | The `m=24` spectral gap changes sign | The exact SRG matrix equation independently fixes the value three. |
| Raise the subset size to 27 | The spectral gap is exactly zero | Confirms the sharp boundary of the stated inequality. |

The submitted verifier and its five tests also pass.  Its JSON certificate
is an arithmetic accompaniment: it does not itself derive the semantic
point-to-vertex bridge, and it does not validate every prose-valued metadata
field.  That is a noncritical tooling limitation because the bridge is
checked explicitly above and by the independent checker; no solver status
or certificate field is used as a substitute for the proof.

No automorphism, connectivity, catalog completeness, negative search, or
unverified solver result enters the exclusion.

## 7. Consequences and status boundary

The prior audited Wave 13 result gives `n3>=48`.  The present argument
excludes equality.  The inherited identity

```text
4158=3P+n3
```

gives `3 | n3`, so the next possible value is 51.  Reimbayev's exact
six-cycle identity specialized to the Conway parameters is

```text
induced_C6_count=209286+n3.
```

Hence the scoped consequences are:

```text
Wave 15 global-lift argument:             PASS / DERIVED
conditional n3=48 residual:               EXCLUDED / DERIVED
conditional n3 lower bound:               51
conditional induced-C6 lower bound:       209337
Wave 14 active relaxation countermodel:   still CANDIDATE in its own scope
Conway-99 existence/nonexistence:          UNKNOWN
novelty:                                  UNKNOWN
```

The claim remains conditional on the audited Wave 14 framework.  It is a
new necessary bound for any putative Conway graph, not an existence or
nonexistence proof.
