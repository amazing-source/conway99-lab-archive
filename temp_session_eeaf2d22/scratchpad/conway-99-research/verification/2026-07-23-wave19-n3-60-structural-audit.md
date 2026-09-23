# Wave 19 `n3=60` structural adversarial audit

Verdict: **PASS / DERIVED for the submitted coarse necessary reduction, with
one material completeness objection to Residual B.**  Independent
reconstruction reproduces all thirteen `sum(q)=40` profiles, the
endpoint-local crossing rule, every exclusion through `r=19`, the five
`r=20,m=28` exclusions, the two `r=20,m=29` exclusions, the `m=27`
arithmetic/cubic residual, and the `m=30` moment/topology/histogram residual.

The objection is exact but non-fatal to that conclusion.  At `m=30`, if `N`
is the `20`-by-`30` active-label/point incidence matrix, `A_R` is the
positive-crossing two-factor, and `A_L` is the active label graph, the
audited framework also forces

```text
N A_R N^T = 2 A_L.                                      (R)
```

The submitted JSON neither states (R) nor instantiates `F,R,L` on one common
labeled system.  Thus it is not a complete machine-readable residual
certificate.  This does **not** falsify any submitted exclusion: the report
explicitly describes its residual fields as necessary conditions rather than
feasibility certificates.  Equation (R) narrows but does not close `m=30`.
Residual A and Residual B both remain open, so the exact status boundary is

```text
conditional n3=60:  UNKNOWN_FINITE_RESIDUAL
Conway-99 target:   UNKNOWN
novelty:            UNKNOWN
```

```yaml
role: verifier
date_utc: 2026-07-23T13:56:27Z
git_commit: 13b2a90604e78a400eb05be5e7bf261f29d46f77
claim_label: DERIVED
audit_verdict: PASS_WITH_MATERIAL_COMPLETENESS_OBJECTION
scope: >-
  Independent adversarial audit of the Wave 19 conditional n3=60 structural
  reduction, including all q profiles and exclusions, Residual A at m=27,
  Residual B at m=30, and omitted compatibility conditions.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/2026-07-23-wave15-global-lift-audit.md: edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036
  verification/2026-07-23-wave15-algebraic-audit.md: b0541d05d2c1c359152b86223e2ebbdbd002b2ff42deb699f6a0b21d149a5b45
  verification/2026-07-23-wave16-n3-51-structural-audit.md: 99203a15db2646a759edbb2241eb4bd5e6001733ac862952c9db57446c58ead6
  agents/2026-07-23-wave19-n3-60-structural.md: b2f90af07f34a6525ea35cdf4d392d95aea10fc319633cd17037d00145690744
  attempts/wave19-n3-60-structural/exact_check.py: c7564eef0f1c62165c91a36071ab34b494ead891877011e755407ad48adee460
  attempts/wave19-n3-60-structural/test_exact_check.py: 1b1d2628d6c2d837dec24ec679d579676b5a0e66962e0266cee2642040bf6165
  attempts/wave19-n3-60-structural/exact-checks.json: fc884ea131b1b6c926d9e71ddb1f7925e15c39498f1d7b72819a6473b39ab8dd
  attempts/wave19-n3-60-structural/residual-certificates.json: 3396b3b67b944b86bfd0d51e8beca25dfc9350815269c62cda4fa7c22a7a5c8b
  attempts/wave19-n3-60-structural/failed-attempts.md: 62d43cdb66c599c8c1e1618ca54267c1bf08ba20ad175e04883349cf6f876a0e
method: >-
  Froze independent pass/fail conditions before opening Wave 19; authenticated
  only Wave 15/16 premises; used multiplicity rather than partition generation,
  row-support rather than bit-mask crossing enumeration, complement rather
  than permutation classification of cubic graphs, degree-by-degree dynamic
  programming for outside histograms, direct common-neighbor moment counting,
  a labeled hostile F/R countercontrol, and independent GF(2) rank/nullity
  derivations. No Wave 17/18 input was opened or imported.
command: |
  Push-Location verification\n3-48-global-lift
  ..\..\.venv\Scripts\python.exe -B independent_check.py
  ..\..\.venv\Scripts\python.exe -B -m unittest -v test_independent_check.py
  Pop-Location
  Push-Location verification\n3-51-structural
  ..\..\.venv\Scripts\python.exe -B independent_check.py
  ..\..\.venv\Scripts\python.exe -B -m unittest -v test_independent_check.py
  Pop-Location
  .venv\Scripts\python.exe -B verification\n3-60-structural\global\independent_global_check.py --verify verification\n3-60-structural\global\global-reduction-certificate.json
  .venv\Scripts\python.exe -B -m unittest -v verification\n3-60-structural\global\test_independent_global_check.py
  .venv\Scripts\python.exe -B attempts\wave19-n3-60-structural\exact_check.py --verify attempts\wave19-n3-60-structural\exact-checks.json --verify-residual attempts\wave19-n3-60-structural\residual-certificates.json
  .venv\Scripts\python.exe -B -m unittest -v attempts\wave19-n3-60-structural\test_exact_check.py
  .venv\Scripts\python.exe -B verification\n3-60-structural\independent_residual_check.py --output verification\n3-60-structural\independent-results.json
  .venv\Scripts\python.exe -B -m unittest -v verification\n3-60-structural\test_independent_residual_check.py
  .venv\Scripts\python.exe -B verification\n3-60-structural\independent_residual_check.py --verify verification\n3-60-structural\independent-results.json
  .venv\Scripts\python.exe -B verification\n3-60-structural\rectangle_identity_probe.py --output verification\n3-60-structural\rectangle-identity-results.json
  .venv\Scripts\python.exe -B -m unittest -v verification\n3-60-structural\test_rectangle_identity_probe.py
  .venv\Scripts\python.exe -B verification\n3-60-structural\rectangle_identity_probe.py --verify verification\n3-60-structural\rectangle-identity-results.json
  .venv\Scripts\python.exe -B verification\n3-60-structural\rectangle-followup\check.py --verify verification\n3-60-structural\rectangle-followup\results.json
outputs:
  verification/n3-60-structural/preinspection-freeze.md: 983f90c1d150c6e14e5e2bc7a010e1a3809848ddb1e4b825e5fdfac70398d6af
  verification/n3-60-structural/global/independent_global_check.py: d65e61ee7ff21707a665f5ba426e8cf0aa8dbdfb5c95e1e11d9befc85c5e6db6
  verification/n3-60-structural/global/global-reduction-certificate.json: 2bc0a9bdf21f6b2a087f5df5e5170bc96f455224c06ec9699a80af4a9d84854b
  verification/n3-60-structural/independent_residual_check.py: d2c19eb105adc41730fc45bee63f5682bc973b0d3b0c156bb82505a6bec6a330
  verification/n3-60-structural/independent-results.json: f18512a7ade40a1509759b32b6897f769ef55a85fd1ce6f2a5ce12bee7383c41
  verification/n3-60-structural/test_independent_residual_check.py: 13530f4c01859c2f9d941c357287eb470c339b1fd6969b9531f0142c68fbf410
  verification/n3-60-structural/rectangle_identity_probe.py: 273134d5b58f484dd50b1e9da73615ed2b6a0378ec57ae4bc4e922a75a1f3934
  verification/n3-60-structural/rectangle-identity-results.json: 8192b17eddc82188f2db046dd6f641b83400fece93a9fa70f1ec314b668305d9
  verification/n3-60-structural/test_rectangle_identity_probe.py: cbd7ec2d10544dad74d5d439ccd967de9faf484affc148520c4c3799b56c396a
  verification/n3-60-structural/rectangle-followup/check.py: 679f3fdc03a8ae092913731cde4fe77c7aefd1b0cb3cb636ecb72ffede54186a
  verification/n3-60-structural/rectangle-followup/results.json: 310603bee42385b49e0df434370f03195a04b0d3b6e8d7fe8a8bba427e8802d2
  verification/n3-60-structural/rectangle-followup/run-report.yaml: 11df4b25429aa5a530a56ce91c8ef13e6d65fc52bcc1ea28e48e56e04179126f
  verification/n3-60-structural/failed-runs.md: 42897915b3b9ea39de4716e26517c3b011a7b19d8a38e368b2b8a35219286d4a
results:
  preinspection_freeze_order: PASS
  authenticated_wave15_independent_tests: "11/11 PASS"
  authenticated_wave16_independent_tests: "24/24 PASS"
  independent_global_tests: "16/16 PASS"
  independent_residual_tests: "16/16 PASS"
  independent_rectangle_tests: "8/8 PASS"
  submitted_wave19_tests: "11/11 PASS"
  deterministic_replays: PASS_BYTE_IDENTICAL
  admissible_q_profiles: 13
  exclusions_through_r19: 12
  r20_m28_profiles_excluded: 5
  r20_m29_profiles_excluded: 2
  m27_residual: UNKNOWN
  m30_residual: UNKNOWN_WITH_OMITTED_STRONGER_IDENTITY
  conditional_n3_60: UNKNOWN_FINITE_RESIDUAL
limitations: >-
  Conditional on the audited Wave 15/16 H/L, indexed-point, fixed-point,
  no-singleton, no-Berge, and target spectral framework rather than a fresh
  99-by-99 adjacency derivation. The finite residual summaries are necessary
  conditions, not constructions, nonexistence certificates, or SRG extension
  certificates. The rectangle identity and GF(2) consequences do not close
  m=30. No exhaustive F/R search, automorphism restriction, SAT/ILP result,
  or novelty determination is used. This verifier does not promote its own
  derived findings to VERIFIED.
```

The target full hash was resolved from the repository reflog by direct file
reading; no Git command was run.  The shared branch had already advanced, so
the input hashes above—not the later branch tip—pin the bytes audited here.

## 1. Ordering and authenticated premise boundary

`verification/n3-60-structural/preinspection-freeze.md` was created and
hashed before any Wave 19 candidate or attempt file was opened.  It fixed the
independent derivations, pass/fail conditions, hostile mutations, and the
`UNKNOWN_FINITE_RESIDUAL` publication boundary.  Its unchanged SHA-256 is

```text
983f90c1d150c6e14e5e2bc7a010e1a3809848ddb1e4b825e5fdfac70398d6af.
```

No Wave 17 or Wave 18 file, source, certificate, or result was used.  The
authenticated inputs were limited to the current Wave 15 global/algebraic
audits and the Wave 16 structural audit.  Their existing independent suites
replayed `11/11` and `24/24`.

The imported framework facts are:

1. `d_L(T)=3q(T)`, active `q(T)>=2`, and `sum_T q(T)=40`;
2. `d_K(T)=r-1-3q(T)>=4`;
3. indexed original-vertex points `S_u`, no singleton, linearity, three point
   occurrences per active label, and no Berge triangle;
4. for an actual edge `uv`, after deleting a possible common label from both
   endpoints, `d_H(uv)` is the two-sided `L`-crossing size and every remaining
   row and column has degree zero or two;
5. `sum_{v~u}d_H(uv)=2 sum_{T in S_u}q(T)`;
6. `sum_{u in X}|S_u|=3r`, exactly `2|S_u|` distinct meeting neighbors, and
   `2e(G[X])<=3|X|+|X|^2/9`.

## 2. Profiles and endpoint semantics

Multiplicity-equation enumeration, independent of the submitted partition
generator, gives exactly:

| `r` | active `q` multiset |
|---:|---|
| 14 | `2^2 3^12` |
| 15 | `2^5 3^10` |
| 16 | `2^8 3^8` |
| 17 | `2^14 4^3` |
| 17 | `2^13 3^2 4^2` |
| 17 | `2^12 3^4 4` |
| 17 | `2^11 3^6` |
| 18 | `2^16 4^2` |
| 18 | `2^15 3^2 4` |
| 18 | `2^14 3^4` |
| 19 | `2^18 4` |
| 19 | `2^17 3^2` |
| 20 | `2^20` |

For a size-two point, common-label deletion leaves either one row (meeting
case) or two rows (disjoint case).  The column rule kills every one-row
crossing.  With two rows, a nonzero column uses both rows and each active row
must use exactly two columns, so the crossing is empty or a complete
`2`-by-`2` rectangle.  Hence an actual edge at that endpoint has
`d_H in {0,4}`.  This is endpoint-local: the independent `3`-by-`3` hostile
control retains the valid value six.

The resulting size-two table is exact:

| endpoint `q` pair | fixed sum | positive disjoint neighbors | induced-degree lower bound |
|---|---:|---:|---:|
| `(2,2)` | 8 | 2 | 6 |
| `(2,3)` | 10 | impossible | — |
| `(2,4)` | 12 | 3 | 7 |
| `(3,3)` | 12 | 3 | 7 |
| `(3,4)` | 14 | impossible | — |
| `(4,4)` | 16 | 4 | 8 |

Points of size at least three already have six meeting neighbors.  Thus
`delta(G[X])>=6`, and the exact subset bound forces `|X|>=27`.

## 3. Complete exclusion coverage

| scope | independent reason | result |
|---|---|---|
| `r<=17` | `|X|<=floor(3r/2)<=25<27` | excluded |
| `r=18,m=27` | equality makes `G[X]` 6-regular and the point graph simple cubic triangle-free; the three profiles fail by a `q=4` high-degree point, a two-vertex odd component, or an odd `K4` | excluded |
| `r=19,m=27` | equality gives 6-regularity; the three point profiles contain a high-degree point or leave a size-three fixed sum at least 12 with crossing capacity at most 8 | excluded |
| `r=19,m=28` | the unique size-three point either has a non-multiple-of-four fixed sum or degree at least nine; parity gives degree sum at least 172 while the spectral maximum is 170 | excluded |
| `r=20,m=28` | all five point profiles exceed the total excess two, fail a size-three crossing ledger, or force at least five positive meeting edges on four size-three points and hence overlapping point triangles, contradicting three occurrences per label | excluded |
| `r=20,m=29`, `2^28 4` | forced excess vector `(6,0^28)` gives outside sum 226 and square sum 698, below integer minimum 742 | excluded |
| `r=20,m=29`, `2^27 3^2` | only `T=4,6`; respective square upper bounds `752,724` are below integer minima `756,742` | excluded |

The `m=28` four-size-three step was checked with the full endpoint ledger:
after six-edge crossings are excluded, the four points need twelve positive
crossing incidences; at most two can be nonmeeting because total degree excess
is at most two.  Thus at least ten incidences, or five edges, lie in the
positive-meeting graph.  Every five- or six-edge graph on four vertices has
two triangles sharing an edge.  No-Berge makes each triangle share one label;
linearity makes the two labels equal, putting one label in four points.

## 4. Residual A: `r=20,m=27`

Spectral equality makes `G[X]` 6-regular.  Of eleven point-size profiles,
meeting degrees eliminate every one except

```text
2^21 3^6.
```

For outside degrees `a_z=|N(z) intersect X|`, direct cut and common-neighbor
pair counts independently give

```text
sum a_z=216,  sum a_z^2=648,  number of z=72.
```

The integer minimum is `72*3^2=648`, so the outside histogram is exactly
`3^72`.

Each size-three point has its six meeting neighbors and needs three positive
four-edge crossings to other size-three meeting points.  The resulting graph
`J` is simple cubic on six vertices.  The complement of `J` is 2-regular, so
it is either `C6` or `C3+C3`; therefore `J` is respectively the triangular
prism or `K3,3`.  Independent labeled enumeration gives 60 prism labelings
and 10 `K3,3` labelings.  Explicit linear no-Berge six-point realizations
confirm that neither type is locally excluded.

Each size-two point has exactly two positive disjoint size-two neighbors, so
these edges form a 21-vertex simple 2-factor.  The independent generating
function gives 60 abstract cycle-length multisets.

These are necessary summaries, not compatible objects.  The submitted
certificate does not assign intersection labels to `J`, place the 2-factor
on the 21 labeled size-two points, enforce disjoint endpoints, join both
layers to one 20-label/27-point incidence system, or construct outside
vertices.  A hostile prism whose triangle edges receive three distinct
intersection labels is cubic but violates no-Berge; an abstract 3-cycle of
pairwise meeting size-two points is a valid cycle type but cannot be a
positive disjoint 2-factor.  The candidate explicitly disclaims feasibility,
so these omissions do not invalidate its `UNKNOWN` status.

## 5. Residual B: `r=20,m=30`

All points have size two.  The point graph `F` on 20 labels is simple cubic
and triangle-free, and its line graph is the 4-regular meeting graph on the
30 indexed points.  The fixed sum eight gives two positive disjoint
neighbors per point; these form a simple spanning 2-factor `R`, disjoint from
the line graph.  Every further induced edge has disjoint endpoints and zero
crossing; their graph is `Z`.

Writing `T=2e(Z)` and `U=sum_x d_Z(x)^2`, the spectral bound gives `T<=10`.
For `T=8,10`, even `U=T` yields:

| `T` | outside sum | square upper bound | integer minimum |
|---:|---:|---:|---:|
| 8 | 232 | 788 | 796 |
| 10 | 230 | 760 | 782 |

Thus `e(Z)<=3`.  Independent generation of all simple graphs with at most
three edges gives exactly the nine advertised topologies.  A separate
degree-by-degree histogram dynamic program reproduces every count:

| `Z` | `(T,U)` | outside histogram count |
|---|---:|---:|
| empty | `(0,0)` | 1297 |
| `K2` | `(2,2)` | 354 |
| `2K2` | `(4,4)` | 69 |
| `P3` | `(4,6)` | 52 |
| `3K2` | `(6,6)` | 6 |
| `P3+K2` | `(6,8)` | 3 |
| `P4` | `(6,10)` | 2 |
| `K1,3` | `(6,12)` | 1 |
| `K3` | `(6,12)` | 1 |

The `K1,3`/`K3` collision is deliberately retained: the first two moments
do not determine topology.

### 5.1 Material omitted rectangle identity

Wave 15 independently audits that an `L`-edge is a pair of disjoint graph
triangles joined by exactly two original cross edges (`a_2=d_L=3q`).  Let
`N` be label/point incidence.

- An `R` edge has a nonzero size-two crossing, hence its two point-edges
  contribute the full four-entry `L` rectangle to `N A_R N^T`.
- Conversely, an `L` edge `TU` has exactly two original cross edges between
  triangles `T,U`.  At `m=30` each associated endpoint point has size two;
  the crossing contains `TU`, so the two-sided rule makes it positive and
  each original edge belongs to `R`.
- Therefore every `L` entry occurs exactly twice and every non-`L` entry
  occurs zero times, proving (R).
- A `Z` edge has zero crossing, so it is absent from `A_R` and from (R).

The focused hostile control takes connected cubic triangle-free
`F=G(10,2)` and a deterministically found disjoint-edge 30-cycle `R`.  It
satisfies every coarse `F/R` field in the submitted JSON, with `Z` empty,
but its off-diagonal rectangle multiplicities are

```text
0^104 1^57 2^24 3^5,
```

including multiplicity one at label pair `(0,3)`.  It fails (R).  This is a
positive countercontrol to certificate completeness, not a graph
counterexample and not nonexistence evidence.

### 5.2 Independently checked `GF(2)` consequence

Let `c=c(F)`.  Over `GF(2)`, (R) gives `N A_R N^T=0`.  The cut space
`W=im(N^T)` has dimension `20-c`, while `ker N` has dimension `10+c`.
Equivalently, projecting the totally isotropic space `W` through the radical
of the alternating form `A_R` gives the exact necessary bound

```text
nullity(A_R) >= 10-2c.
```

A simple cubic triangle-free component has even order at least six, so
`c<=3`.  For a cycle, the recurrence `x_(i+2)=x_i` gives `GF(2)` adjacency
nullity one for odd length and two for even length.  Independent dense-row
and bitset elimination agree on all 331 cycle partitions:

| components of `F` | required nullity | surviving abstract `R` cycle types |
|---:|---:|---:|
| 1 | at least 8 | 147 |
| 2 | at least 6 | 263 |
| 3 | at least 4 | 323 |

Universally excluded are

```text
(3,27),(5,25),(7,23),(9,21),
(11,19),(13,17),(15,15),(30).
```

If any component of `F` is nonbipartite, the all-one edge vector lies in
`ker A_R` but not in the cut space, strengthening the bound to
`nullity(A_R)>=12-2c`; a connected nonbipartite `F` leaves 55 abstract cycle
types.  These are exact necessary refinements only.  They do not enumerate
placements of `R`, construct `L`, incorporate `Z` or outside vertices, or
close Residual B.

## 6. Hostile tests and evidence boundary

The independent suites exercised:

- endpoint swap, duplicated/omitted endpoints, inconsistent labels, retained
  common labels, row-only crossings, and crossing-label flips;
- loops, parallel edges, disconnected cubic controls, and a
  degree-preserving 2-switch distinguishing `K3,3` from the prism;
- an imposed connected-complement restriction, which incorrectly deletes
  `K3,3`;
- one-unit `q` transfers, including a genuine transfer between the two
  `r=19` profiles that must be retained;
- outside histograms with wrong first or second moments and the genuine
  `K1,3`/`K3` moment collision;
- every `Z` topology through three edges and four-edge counterpressure;
- locally cubic but no-Berge-incompatible intersections, overlapping
  abstract `R` cycles, and the labeled rectangle-identity countercontrol.

Verifier-internal command and test failures are retained in
`verification/n3-60-structural/failed-runs.md`; the global lane retains its
own two failures separately.  A superseded auxiliary rectangle suite timed
out and is explicitly not evidence.  No solver exit code, restricted search,
or failure to construct is used.

## 7. Final boundary and blocking objection

```text
profiles through r=19:             EXCLUDED / DERIVED
r=20,m=28:                         EXCLUDED / DERIVED
r=20,m=29:                         EXCLUDED / DERIVED
r=20,m=27:                         UNKNOWN
r=20,m=30 coarse moments:          REPRODUCED / DERIVED
r=20,m=30 exact compatibility:     STRONGER FINITE RESIDUAL / UNKNOWN
conditional n3=60:                 UNKNOWN_FINITE_RESIDUAL
Conway-99 target:                  UNKNOWN
novelty:                           UNKNOWN
```

There is **no blocking objection to the submitted coarse necessary reduction
or to its `UNKNOWN_FINITE_RESIDUAL` conclusion**.  There is a **material
blocking objection to calling `residual-certificates.json` a complete
machine-readable residual certificate**: it omits (R), accepts incompatible
coarse `F/R` data, and does not join its local objects.  Publication is sound
only if the artifact remains described as a catalog of necessary
moment/topology summaries, exactly as its limitations ultimately state.
