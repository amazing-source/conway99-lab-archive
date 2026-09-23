# Wave 17 structural audit of the conditional `n3=54` residual

Verdict: **PASS WITH RECORDED CLARIFICATIONS / VERIFIED for the scoped
structural residual.**  The audit verifies the six-profile reduction, the
sharp `r=18` equality structure, exclusion of the `F=3K3,3` branch by a
human parity proof, and the stated binary, surface, and moment restrictions.

It does **not** exclude `n3=54`.  Two point-graph component profiles remain:

```text
connected cubic girth-at-least-five F of order 18;
K3,3 plus a connected cubic girth-at-least-five F of order 12.
```

The existence of a putative `srg(99,14,1,2)`, the conditional `n3=54` case,
and novelty all remain `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T12:20:44Z
git_commit: 1eb7c18
claim_label: VERIFIED
audit_verdict: PASS_WITH_RECORDED_CLARIFICATIONS
scope: independent adversarial verification of the frozen Wave 17 conditional n3=54 structural residual, not an exclusion of n3=54 or Conway-99
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  agents/2026-07-23-wave16-n3-51-structural.md: 95d04a774397332417c9613718fe6699a5392ef5222fef1cfa00b12e2860af3f
  verification/2026-07-23-wave16-n3-51-structural-audit.md: 99203a15db2646a759edbb2241eb4bd5e6001733ac862952c9db57446c58ead6
  verification/2026-07-23-wave15-global-lift-audit.md: edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036
  verification/2026-07-23-wave15-algebraic-audit.md: b0541d05d2c1c359152b86223e2ebbdbd002b2ff42deb699f6a0b21d149a5b45
  attempts/wave16-n3-51-structural/exact_check.py: 5aef211ea7d457543fc3f494eea125bbd0fd6fae2533fd566b475ff3f971c5cf
  agents/2026-07-23-wave17-n3-54-structural.md: ffae576057617b6d8e32f7df4a1cd9627c63bdfe40fb58f394fd2640d1d82d18
  attempts/wave17-n3-54-structural/exact_check.py: 8f4f8c27e486cd67b29028911ec101fdcb6e812e6ac12b5572a896d3fa84155a
  attempts/wave17-n3-54-structural/test_exact_check.py: 3ee410014dc80cedb78a63869d738168668f1e8bfb54e7e2e24c64d0f5ec3034
  attempts/wave17-n3-54-structural/restricted_k33_sat.py: 405f5ac2714bf4fd74856cb6b153de9d4602989456c82132efcf8640f654613a
  attempts/wave17-n3-54-structural/unrestricted_active_sat.py: 54cb7878f7ea50dc119f6420a0d9d1d784e5a41a6238dea35f0c7f37eae6ab15
method: preinspection freeze, independent combinations-based profile census, exhaustive small crossing enumeration, equality-case Rayleigh reconstruction, explicit original-neighbor indexing, graph closure countercontrols, direct incidence-product scope tests, independent F2 parity witness, binary Gaussian elimination, local surface-link reconstruction, exact triangle moments, provenance checks, and hostile mutations
command: |
  .venv\Scripts\python.exe -B verification\n3-54-structural\independent_check.py
  cd verification\n3-54-structural
  ..\..\.venv\Scripts\python.exe -B -m unittest -v test_independent_check.py
  cd ..\..
  .venv\Scripts\python.exe -B attempts\wave17-n3-54-structural\exact_check.py
  .venv\Scripts\python.exe -B -m unittest -v attempts\wave17-n3-54-structural\test_exact_check.py
  .venv\Scripts\python.exe -B attempts\wave17-n3-54-structural\restricted_k33_sat.py
  .venv\Scripts\python.exe -B attempts\wave17-n3-54-structural\restricted_k33_sat.py --omit-matching
outputs:
  verification/n3-54-structural/preinspection-freeze.md: 5d9387bb8af4f218bccfbd52b1a3d550d2505a9a0727d197ee8e52d7f1407481
  verification/n3-54-structural/independent_check.py: 4a3df41d392d608c01333fb10ebf259251223e1e27c3c970c398f1ddb482d803
  verification/n3-54-structural/test_independent_check.py: 337eaffc5fd199d2805a4695b5eceec13a8224882c772f5049c043ba03cc88bb
  independent_semantic_sha256: a53ff59d0e7f814932a1b846f4c7ec755f54f1a28b4d130087a23e371396a5f3
  independent_hostile_tests: "21/21 PASS"
  submitted_focused_tests: "7/7 PASS"
  raw_profiles: 23
  profiles_after_d_K_at_least_4: 6
  excluded_by_dense_subset_bound: 5
  equality_profile: "r=18, q=2^18, |X|=27"
  three_K3,3_branch: EXCLUDED_VERIFIED_BY_PARITY
  remaining_F_component_profiles: 2
  restricted_F_equals_3K3,3_sat: UNSAT_UNVERIFIED_NON_EVIDENTIARY
  restricted_matching_omitted_control: UNSAT_UNVERIFIED_NON_EVIDENTIARY
  conditional_n3_54_exclusion: UNKNOWN
  conway_99_target: UNKNOWN
  novelty: UNKNOWN
limitations: conditional on the hash-bound audited H/L/indexed-point/crossing and SRG spectral premises rather than a raw 99-by-99 adjacency derivation; no full equality-case lift, outside-vertex realization, formal proof object, target resolution, or novelty conclusion is supplied; the unrestricted SAT timeout was not replayed and its listed command does not itself encode the historical 60-second boundary
```

The short commit identifier `1eb7c18` was supplied by the orchestrator as
the frozen Wave 17 checkpoint.  No Git command was used.  The submitted
report is independently content-bound by its full SHA-256 above.

## 0. Freeze, independence, and provenance

The attack plan was written to
`verification/n3-54-structural/preinspection-freeze.md` before opening the
submitted report or any file under
`attempts/wave17-n3-54-structural/`.  Its SHA-256 remains

```text
5d9387bb8af4f218bccfbd52b1a3d550d2505a9a0727d197ee8e52d7f1407481.
```

The submitted report matched the expected frozen hash
`ffae576057617b6d8e32f7df4a1cd9627c63bdfe40fb58f394fd2640d1d82d18`.
Every declared input and output path existed, and all eleven checked
submission/premise hashes matched.  The independent checker imports no
discovery module and uses a combinations-based profile generator rather
than the submitted recursive partitioner.

## 1. Profiles, distinct neighbors, and the equality boundary

At `n3=54`, the exact arithmetic is

```text
sum q(T)=36,
q(T)>=2,
3q(T)<=r-1,
d_K(T)=r-1-3q(T).
```

Independent nondecreasing enumeration gives 23 raw profiles.  Filtering by
the previously audited strict condition `d_K>=4` leaves exactly:

| `r` | `q` multiset | `d_K` multiset | `|X|` upper bound |
|---:|---|---|---:|
| 14 | `2^6 3^8` | `7^6 4^8` | 21 |
| 15 | `2^9 3^6` | `8^9 5^6` | 22 |
| 16 | `2^12 3^4` | `9^12 6^4` | 24 |
| 17 | `2^16 4` | `10^16 4` | 25 |
| 17 | `2^15 3^2` | `10^15 7^2` | 25 |
| 18 | `2^18` | `11^18` | 27 |

The `q=4` row is real and essential.  A hostile mutation deleting all
`q=4` profiles changes the residual count from six to five.

For an indexed size-two point `S_u={i,j}`, the independently enumerated
overlap-deleted crossing has:

```text
meeting case:              {0} edges;
disjoint case:             {0,4} edges.
```

The fixed sum `2(q(i)+q(j))` therefore gives:

| type | support-neighbor count |
|---|---:|
| `22` | 2 |
| `24` | 3 |
| `33` | 3 |
| `44` | 4 |
| `23`, `34` | impossible modulo four |

These are distinct original graph-neighbor indices because the fixed-point
sum ranges over the fourteen distinct vertices in `N_G(u)`.  A positive
term has an active, disjoint other endpoint and hence cannot duplicate any
of the four active-triangle neighbors.  For a point of size at least three,
the active triangles themselves supply `2|S_u|>=6` distinct neighbors; no
point-size-at-most-three assumption is used.

The independent crossing checker also retains the legal six-edge
`3`-by-`3` crossing.  Thus no global assertion
`d_H in {0,4}` has entered the proof.  The `24` type has three support
neighbors for a point of size two, explicitly refuting any hidden use of
the Wave 14 identity `d_R(P)=|P|`.

The first five rows have `|X|<=25` and contradict the audited subset lower
bound `|X|>=27`.  In the last row all inequalities are equalities:

```text
r=18,
|X|=27,
all 27 indexed points have size two,
q=2 on all 18 labels,
2e(G[X])=162.
```

Minimum degree six and average degree six make `G[X]` exactly 6-regular.
Writing `x=1_X=(3/11)1+y`, equality in
`y^T A y <=3||y||^2` puts `y` in the eigenvalue-three eigenspace and gives

```text
A x=3x+3*1.
```

The cut is therefore equitable with quotient matrix

```text
[[6,8],
 [3,11]].
```

Both sides count 216 cut edges.  Interlacing also gives every nonprincipal
eigenvalue of `G[X]` at most three, so a second 6-regular component is
impossible.

## 2. The exact `F/R` representation and matrix scope

The 27 size-two indexed points are the edges of a simple cubic graph `F` on
18 active labels.  Simplicity follows from indexed-point linearity; cubicity
from the three points through every label; and triangle-freeness from the
audited prohibition on three points meeting pairwise at three different
labels.

Each `F`-edge has four distinct line-graph neighbors and exactly two
positive disjoint support neighbors.  Equality in the 6-regular active
subgraph leaves no additional active-active edge.  Consequently

```text
G[X]=line(F) union R
```

as an edge-disjoint union, where `R` is a simple 2-factor on the 27 edges
of `F`.  A concrete hostile example independently verifies that line
neighbors have degree four, disjoint support-cycle neighbors have degree
two, and the two sets do not collide.

For the 18-by-27 vertex-edge incidence matrix `N`, direct integer
reconstruction verifies the full scope of

```text
N A_R N^T=2A_L.
```

It includes:

- zero diagonal entries, because an `R`-edge joins disjoint `F`-edges;
- zero entries on every `K`-pair, including every `F`-edge; and
- exact value two on an `L`-pair, from its two `N3` cross graph-edges.

The separate identity

```text
A_X=N^T N-2I+A_R
```

then follows entrywise.

The independent-cross-edge matching rule is strictly stronger than the
matrix identity.  A hostile construction gives product entry two while
reusing the same `F`-edge in both covers.  The submission correctly states
matching as a separate inherited `N3` property, and the parity exclusion
below does not depend on it.  An adjacent-`F`-edge mutation in `R` creates
diagonal entry two in `N A_R N^T`, so it cannot be hidden inside the full
identity.

## 3. Codegree closure and the `3K3,3` parity contradiction

If nonadjacent labels `a,b` in `F` have exactly two common `F`-neighbors,
the corresponding two meeting edges are independent cross-edges between
the disjoint active graph-triangles `a,b`.  There can be no support
rectangle across their stars because `ab` lies in `K`.  Equality in
`G[X]=line(F) union R` therefore leaves exactly those two cross-edges,
making `a,b` the side pair of an induced `N3`, hence an `L`-edge: a
contradiction.

One wording clarification is material enough to record explicitly:
`ab in K` here follows from the audited **zero meeting-crossing** for the
size-two points `{a,c}` and `{b,c}` after deleting their common label `c`.
Membership of each individual point in a `K`-clique gives `ac,bc in K`,
but by itself does not give `ab in K`.  The submitted phrase “point-clique
rule” is shorthand for the meeting-point consequence.  The needed premise
is imported and independently checked, so this is a terminology correction,
not a missing hypothesis or repaired conclusion.

For a cubic triangle-free graph, a 4-cycle gives opposite vertices with at
least two common neighbors.  The no-codegree-two result forces a third.
Applying the same result to their three common neighbors makes their unique
remaining neighbor common, closing the entire component to `K3,3`.
The cube graph is an explicit hostile countercontrol: it is cubic and
triangle-free but has a nonadjacent codegree-two pair.  `K3,3` closes as
claimed, while the Petersen graph provides a girth-five control.

Since every non-`K3,3` component has girth at least five and hence order at
least ten, the component-order partitions of 18 are exactly

```text
(18), (6,12), (6,6,6).
```

For `F=3K3,3`, no `R`-edge stays within one component.  Degree counting
forces exactly nine `R`-edges between each pair of components.  Over
`F_2`, the `A,B` block of the exact-coverage identity is

```text
N_A M_AB N_B^T=0.
```

Choose the indicator of one bipartition class on each `K3,3`.  Multiplying
on both sides shows directly that the parity of all entries of `M_AB` must
be zero, since every `K3,3` edge meets each chosen class once.  But the
entry sum is the forced odd number `x_AB=9`.  This contradiction is
complete and uses neither SAT status nor the matching refinement.

The independent checker represents all 81 entries of `M_AB` as binary
variables and reconstructs the all-entry parity functional as an explicit
linear combination of the 36 block equations.  This materially differs
from the submission's Eulerian-subgraph presentation and reaches the same
contradiction.

## 4. Binary rank, surface, and outside moments

Over `F_2`, let `P` be the vertex-edge incidence matrix of the 2-factor
`R`.  Because every diagonal degree is two,

```text
P P^T=A_R.
```

The exact-coverage identity gives `(NP)(NP)^T=0`.  Thus the row space of
`NP` is self-orthogonal in a 27-dimensional nondegenerate space and has
dimension at most 13.  Independent binary elimination reproduces

```text
rank(N)=18-c_F,
rank(P)=27-c_R,
c_F+c_R>=5.
```

The alternative image/kernel argument gives

```text
nullity(A_R)>=9-2c_F.
```

Exact elimination on every cycle length 3 through 27 confirms that an odd
cycle contributes nullity one and an even cycle contributes two.  Therefore:

```text
c_F=1: c_R>=4 and o_R+2e_R>=7;
c_F=2: c_R>=3 and o_R+2e_R>=5.
```

For each active label, the audited side graph is simple, triangle-free, and
2-regular with six edges.  The only possible cycle partition is `(6)`, so
it is a single hexagonal face.  At a support edge between points
`{a,b}` and `{c,d}`, the four face-corner pairings are

```text
ac-ad, ad-bd, bd-bc, bc-ac.
```

The independent link checker obtains one 4-cycle; deleting one corner
breaks the manifold link.  Every auxiliary edge has its two distinct side
faces, so these cells form a closed, possibly disconnected surface with

```text
V=27, E=54, F=18, chi=-9.
```

The sum of Euler characteristics of orientable closed components is even.
Hence at least one component is nonorientable.  This is a structural
restriction, not a contradiction.

The statement that the 27 support edges are all nonisolated vertices of
`H` also survives audit.  For `u` outside `X`, `S_u` is empty, so its
fixed-point sum is zero; nonnegativity forces every incident `H`-degree to
vanish.  Inside `X`, meeting edges have degree zero and the 27 `R`-edges
have degree four.  Their handshake sum is exactly `2*54`, accounting for
all `N3` edges.

Finally, the SRG block equations for the equitable cut reproduce exactly.
For `c` triangular components of `R`, unique-triangle and cut-edge counting
gives:

| vertices in `X` | triangle count |
|---:|---:|
| 0 | `105-c` |
| 1 | `81+3c` |
| 2 | `27-3c` |
| 3 | `18+c` |

For every `0<=c<=9`, the 213 inactive triangles have meeting moments

```text
sum m_T=270,
sum m_T^2=756.
```

Adding the eighteen active terms gives `918`.  The constancy in `c`
confirms that these moments do not exclude either residual profile.

## 5. Hostile tests and computation boundary

The 21 independent tests cover:

- every frozen input hash and all conservative status labels;
- the 23-to-6 census and deletion of the `q=4` survivor;
- endpoint-local crossings and a legal six-edge global countercontrol;
- all `q=2,3,4` size-two types and point sizes above three;
- Rayleigh equality and equitable-cut arithmetic;
- cubic, triangle-free, codegree, and component-closure controls;
- distinct line/support neighbor indexing;
- diagonal, adjacent, independent, and matching scopes of the matrix
  identity;
- the independent `3K3,3` parity witness;
- graph-incidence ranks and all cycle nullities;
- surface-link mutation; and
- all outside-triangle and active-intersection moments.

All 21 pass.  The seven submitted focused tests also pass.

Both restricted SAT scouts replay:

```text
matching enforced:  4779 variables, 11232 clauses, UNSAT
matching omitted:   3483 variables,  7992 clauses, UNSAT
```

Neither run emitted a checked proof certificate.  Their statuses remain
`UNSAT_UNVERIFIED` and carry no evidentiary weight.  The human parity proof
is the only accepted exclusion of `3K3,3`.

The reported unrestricted scout was not rerun.  Its command is unbounded,
and the submission records a manual stop after 60 seconds.  The listed
command does not by itself reproduce or enforce that historical wall-clock
boundary, and no timeout transcript or result artifact is supplied.  This
is a nonblocking reproducibility objection because the timeout is explicitly
retained only as a failed, non-evidentiary approach.  It supplies no premise
to the verified structural residual.

## 6. Final status boundary

```text
23 raw profiles and six d_K>=4 survivors:       VERIFIED
five r<=17 profiles excluded spectrally:         VERIFIED
r=18 equality and equitable-cut reduction:       VERIFIED
F simple/cubic/triangle-free and GX=line(F)+R:    VERIFIED
full N A_R N^T=2A_L identity:                    VERIFIED
no-codegree-two/component classification:        VERIFIED
F=3K3,3 branch exclusion by human parity:         VERIFIED
binary rank/nullity restrictions:                 VERIFIED
closed hexagonal surface; nonorientable component: VERIFIED
outside and triangle moment identities:           VERIFIED
remaining F component profiles:                   2
conditional n3=54 exclusion:                      UNKNOWN
stronger conditional n3 lower bound:              NOT CLAIMED
raw SAT UNSAT/timeout statuses:                    NON_EVIDENTIARY
global H-degree {0,4}:                             NOT ASSUMED
Wave 14 point-size/support identity:               NOT ASSUMED
Conway srg(99,14,1,2):                             UNKNOWN
novelty:                                           UNKNOWN
```
