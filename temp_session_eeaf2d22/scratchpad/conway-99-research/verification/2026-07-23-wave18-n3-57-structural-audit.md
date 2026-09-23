# Wave 18 adversarial audit of the conditional `n3=57` exclusion

Verdict: **PASS / VERIFIED for the scoped conditional claim.** Under the
authenticated, previously audited `H/L` and indexed-point premises, a putative
`srg(99,14,1,2)` cannot have project parameter `n3=57`.

This verdict does **not** establish existence or nonexistence of the Conway-99
target, does not use the separate Wave 17 exclusion of `n3=54`, and is not a
novelty determination. The global target and novelty both remain `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T12:53:06Z
git_commit: NO_GIT
claim_label: VERIFIED
scope: >
  Independent adversarial verification of the conditional exclusion of
  project n3=57 for a putative srg(99,14,1,2), under the authenticated
  Wave 15/16 H/L, indexed-point, crossing, fixed-point, and spectral premises.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  agents/2026-07-23-wave18-n3-57-structural.md: fa1dde1f96aaaf2c9a90c73308afbc967fab892fe79246bf7eafa2831fea38f6
  verification/2026-07-23-wave15-global-lift-audit.md: edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036
  verification/2026-07-23-wave16-n3-51-structural-audit.md: 99203a15db2646a759edbb2241eb4bd5e6001733ac862952c9db57446c58ead6
  attempts/wave18-n3-57-structural/exact_check.py: 0896a9a5536090262e78efe3a831f3a3b839373f11b00a956d038fe2a1ef2a22
  attempts/wave18-n3-57-structural/test_exact_check.py: 7b9fe196da7c8e1178f88d7e9123b6b693687485016ba3222ffec0ac199d58ba
  attempts/wave18-n3-57-structural/exact-checks.json: 76decce7f0af8e3bf2db483096a10a86321a9d7143e6123ad2081ec17d28604c
  attempts/wave18-n3-57-structural/failed-runs.md: 98bcbe50920ea53bbcc50417f382806640a6fab55d40e6d69231ad07807dc439
method: >
  Freeze the expected reconstruction and hostile tests before inspecting the
  submission; rederive all premises and equality cases; enumerate q-profiles,
  point-size profiles, and overlap-deleted crossings with materially
  independent algorithms; track actual original-vertex identities; replay
  exact spectral arithmetic; run 24 hostile mutations; authenticate and replay
  the submitted artifacts only after the independent result is fixed.
command: |
  .venv\Scripts\python.exe -B verification\n3-57-structural\independent_checker.py
  .venv\Scripts\python.exe -B -m unittest -v verification\n3-57-structural\test_independent_checker.py
  .venv\Scripts\python.exe -B attempts\wave18-n3-57-structural\exact_check.py --verify attempts\wave18-n3-57-structural\exact-checks.json
  .venv\Scripts\python.exe -B -m unittest -v attempts\wave18-n3-57-structural\test_exact_check.py
  rg -n -i 'wave ?17|wave ?14|global.*H.*degree|point-size.*cap|automorph' agents\2026-07-23-wave18-n3-57-structural.md
outputs:
  verification/n3-57-structural/preinspection-freeze.md: 2127ca8b3468cfe04d649180f37cc3f4a2a5b283b4988d309ccd3ccc798bf001
  verification/n3-57-structural/independent_checker.py: df3539f0161d98e4f9a83e587480f4ed77e584e0ca9d91af80d466417d71596c
  verification/n3-57-structural/test_independent_checker.py: 13584f2c98fd18f864a89cd064c7b83110afcf821ce24c5d5b8e2fbe9bd101bd
  verification/n3-57-structural/checker-results.json: 1e640f9e3a0d754f60f66638c481f01ce878ef6ccdc140c2ad79aada903aaf1d
  verification/n3-57-structural/mutation-results.json: eb5f4204e625bfa07f1a4f1e3c99940adacde68d73a0ae07bec1429ea7c40f59
  independent_tests: "14/14 PASS"
  submitted_tests: "10/10 PASS"
  submitted_json_replay: PASS
  hostile_mutations: "24/24 DETECTED"
  conditional_n3_57: EXCLUDED_VERIFIED
  conway_99_target: UNKNOWN
  novelty: UNKNOWN
limitations: >
  This is a conditional theorem over authenticated audited framework premises,
  not a raw 99-by-99 adjacency certificate or a machine-checked formal proof.
  The finite checker accompanies the semantic proof and does not replace it.
  No construction, global target conclusion, literature-exhaustiveness claim,
  or novelty certificate is supplied.
```

## 1. Clean-room boundary and status discipline

The reconstruction plan, pass conditions, checker architecture, and mutations
`M01` through `M24` were written before the submitted Wave 18 report or attempt
directory was opened. The boundary file has SHA-256
`2127ca8b3468cfe04d649180f37cc3f4a2a5b283b4988d309ccd3ccc798bf001`.

Only after that freeze was hashed were the submitted report and artifacts
inspected. The discovery report properly labeled its own result `DERIVED`;
this independent verifier is the lane promoting only the scoped conditional
claim to `VERIFIED`.

## 2. Premises and the `d_K>=4` obstruction

At `n3=57`, the audited identities give

```text
sum_T q(T) = 2n3/3 = 38,
q(T) = 0 or q(T) >= 2.
```

Let there be `r` active triangle labels and omit inactive labels. For an
active label `T`,

```text
d_L(T) = 3q(T),
d_K(T) = r-1-3q(T).
```

The active indexed point at an original vertex `u` is

```text
S_u = {active triangle labels containing u}.
```

The authenticated framework supplies:

1. every nonempty `S_u` has size at least two;
2. the indexed points are linear;
3. every active label occurs in exactly three indexed points;
4. three distinct labels cannot occur in three points that meet pairwise in
   those three distinct labels;
5. for an actual graph edge `uv`, after deleting both copies of a possible
   common label, every row and column of the label crossing has degree zero or
   two;
6. the fixed-point identity

   ```text
   sum_{v adjacent to u} d_H(uv) = 2 sum_{T in S_u} q(T);
   ```

7. every label in `S_u` supplies its two other triangle vertices as distinct
   original neighbors in the active set `X`;
8. the active incidence identity

   ```text
   sum_{u in X}|S_u| = 3r;
   ```

9. the exact subset bound

   ```text
   2e(G[X]) <= 3|X|+|X|^2/9.
   ```

The `d_K>=4` premise was reconstructed rather than treated as a numeric
filter. Non-singleton linear points through a label first give `d_K>=3`.
If equality held for a label `x`, with `N_K(x)={a,b,c}`, the three points
through `x` would have to be

```text
{x,a}, {x,b}, {x,c}.
```

The two other indexed points through `a` have nonempty, disjoint external
parts. The overlap-deleted zero-or-two crossing rule confines those parts to
`{b,c}`, so they must be `{a,b}` and `{a,c}`. Then `{x,a}`, `{x,b}`, and
`{a,b}` meet pairwise at the three distinct labels `x,a,b`, violating premise
4. Thus degree three is impossible and

```text
d_K(T) >= 4
```

for every active label. The independent finite replay finds both ordered
external assignments. Mutation `M03` confirms that weakening the bound to
three admits four additional `n3=57` profiles, so this step is substantive.

## 3. Complete `sum q=38` profile census

The independent checker generated profiles in two unrelated ways:

- recursion over multiplicity vectors; and
- bounded `combinations_with_replacement`.

Both impose only `q>=2`, `sum q=38`, and
`r-1-3q>=4`. They agree on the following nine profiles:

| `r` | active `q` multiset | `d_K` multiset | `floor(3r/2)` |
|---:|---|---|---:|
| 14 | `2^4 3^10` | `4^10 7^4` | 21 |
| 15 | `2^7 3^8` | `5^8 8^7` | 22 |
| 16 | `2^10 3^6` | `6^6 9^10` | 24 |
| 17 | `2^15 4^2` | `4^2 10^15` | 25 |
| 17 | `2^14 3^2 4` | `4 7^2 10^14` | 25 |
| 17 | `2^13 3^4` | `7^4 10^13` | 25 |
| 18 | `2^17 4` | `5 11^17` | 27 |
| 18 | `2^16 3^2` | `8^2 11^16` | 27 |
| 19 | `2^19` | `12^19` | 28 |

The canonical profile hash is
`7cf492da86e2fb2ba40ee158e379144a502a746363d2ad81b544ecc99d5416a3`.
In particular, every `q=4` case is present and no surviving entry has
`q>=5`.

## 4. Endpoint crossings and actual-neighbor semantics

The independent crossing enumerator is row-recursive: it selects degree-zero
or degree-two row supports and incrementally rejects any column that cannot
finish with degree zero or two. It is not the submitted bitmask-style
enumerator. For original point sizes two through five it obtains:

| endpoint sizes | disjoint edge counts | meeting edge counts after deleting the common label |
|---|---|---|
| `2 x 2` | `{0,4}` | `{0}` |
| `2 x 3` | `{0,4}` | `{0}` |
| `2 x 4` | `{0,4}` | `{0}` |
| `2 x 5` | `{0,4}` | `{0}` |
| `3 x 3` | `{0,4,6}` | `{0,4}` |
| `3 x 4` | `{0,4,6}` | `{0,4}` |
| `3 x 5` | `{0,4,6}` | `{0,4}` |
| `4 x 4` | `{0,4,6,8}` | `{0,4,6}` |
| `4 x 5` | `{0,4,6,8}` | `{0,4,6}` |
| `5 x 5` | `{0,4,6,8,10}` | `{0,4,6,8}` |

The canonical table hash is
`ea2b1716e3c84771e0075fc93d599f4d27e328bf6cd21f7ebf3ff8ad3d1d969a`.
The legal six-edge `3 x 3` crossing is also a direct countercontrol against
silently importing a global `d_H in {0,4}` rule.

For a size-two point `P=S_u={i,j}`, an inactive other endpoint has no
columns, a meeting active endpoint leaves one row, and a disjoint active
endpoint leaves two rows. Hence an actual edge at `u` has crossing count
zero or four, and every meeting crossing is zero. The fixed sum gives the
complete table needed by all nine profiles:

| label values at `P` | fixed sum | positive disjoint active neighbors | lower bound on `d_{G[X]}(u)` |
|---|---:|---:|---:|
| `(2,2)` | 8 | 2 | 6 |
| `(2,3)` | 10 | impossible | - |
| `(2,4)` | 12 | 3 | 7 |
| `(3,3)` | 12 | 3 | 7 |
| `(3,4)` | 14 | impossible | - |
| `(4,4)` | 16 | 4 | 8 |

The neighbor counts here are counts of actual original vertices, not abstract
support slots. The fixed-point sum is indexed by the 14 distinct vertices
`v in N_G(u)`, so distinct positive summands are distinct graph neighbors.
A positive endpoint is active, and it cannot be one of the four meeting
triangle neighbors because every meeting crossing is zero.

The checker separately stores a displayed neighbor identity and its physical
original-vertex identity. It rejects both merging two required neighbors and
splitting one physical neighbor into two displayed identities. These are
hostile tests `M16` and `M17`, not assumptions inferred from a sum.

Finally, each of the `|S_u|` active triangles supplies two distinct triangle
neighbors: reuse would put an edge in two graph triangles and contradict
`lambda=1`. Thus:

- if `|S_u|>=3`, triangle neighbors alone give degree at least six;
- if `|S_u|=2`, the table gives at least four meeting plus two positive
  nonmeeting neighbors, or declares the point impossible.

Therefore

```text
delta(G[X]) >= 6.                                      (1)
```

No upper bound on point size is used.

## 5. Incidence and exact spectral threshold

Each active label occurs at its three original triangle vertices, while every
active indexed point has size at least two. Consequently, for
`m=|X|`,

```text
2m <= sum_{u in X}|S_u| = 3r,
m <= floor(3r/2).                                      (2)
```

For an `srg(99,14,1,2)` adjacency matrix,

```text
A^2 = 12I-A+2J.
```

On the all-ones orthogonal subspace the restricted eigenvalues solve
`theta^2+theta-12=0`, hence are `3` and `-4`. Applying the upper restricted
eigenvalue to the indicator of `X` yields

```text
2e(G[X]) <= 14m^2/99 + 3(m-m^2/99)
          = 3m+m^2/9.                                 (3)
```

Equation (1) gives `2e(G[X])>=6m`. The exact gap between the right side of
(3) and this lower bound is

```text
m(m-27)/9.
```

Thus `m>=27`. Equality at `m=27` is allowed by the inequality and forces
every vertex of `G[X]` to have degree exactly six. The checker uses integers
and `fractions.Fraction`; no floating-point comparison decides this boundary.

For every profile with `r<=17`, (2) gives `m<=25`, immediately contradicting
`m>=27`. This eliminates the first six profiles.

## 6. Exhaustion of the `r=18` equality profiles

For `r=18`, the incidence sum is 54. Equations (1)-(3) force

```text
m=27,
all 27 points have size two,
G[X] is 6-regular.
```

Treat each size-two indexed point as an edge on the 18 active labels.
Linearity prevents parallel edges, and every label occurs in exactly three
points, so this point graph is simple and cubic.

### `q=2^16 3^2`

A mixed `(2,3)` edge is impossible because its fixed sum 10 is not a multiple
of the only positive local crossing value four. Hence no point-graph edge
joins the 16 `q=2` labels to either `q=3` label. Each of the two `q=3` labels
would then require degree three inside a simple graph on two vertices, whose
maximum degree is one. Contradiction.

### `q=2^17 4`

The unique `q=4` label lies in three size-two points, and every other endpoint
has `q=2`. Each `(2,4)` indexed point has induced degree at least seven by the
size-two table. This contradicts exact 6-regularity.

Both `r=18` profiles are therefore impossible.

## 7. Exhaustion of `r=19`, including `m=27` and `m=28`

The only `r=19` profile is `q=2^19`; the incidence sum is 57 and
`27<=m<=28`.

### `m=27`

The excess over 27 points of size two is three. Independent size-count-vector
enumeration gives exactly

```text
2^26 5,
2^25 3 4,
2^24 3^3.
```

Its canonical hash is
`4958b37b00df7b3d62c55d9e34af940edc77926bb918fe5fe331f6f57191695d`.
Spectral equality again makes `G[X]` 6-regular.

- `2^26 5` is impossible because the size-five point has ten distinct
  meeting triangle neighbors.
- `2^25 3 4` is impossible because the size-four point has eight distinct
  meeting triangle neighbors.
- In `2^24 3^3`, fix a size-three point `P`. Its six meeting neighbors
  saturate degree six, so it has no disjoint active neighbor. Inactive
  endpoints contribute zero; a meeting size-two point leaves a `2 x 1`
  crossing and contributes zero. Only the other two size-three vertices
  could contribute, and a meeting size-three crossing contributes at most
  four. Thus the fixed-point sum is at most eight, but
  `2(2+2+2)=12`. Contradiction.

### `m=28`

The excess is one, so the unique profile is

```text
2^27 3
```

with canonical hash
`d32ab4439fb30af6931d1be1120af2a23674ac8f246e475af5cae2cb0ccf0cb8`.
Let `P` be the unique size-three point. Its six distinct meeting neighbors are
all size-two points; after common-label deletion each crossing is `2 x 1`
and hence empty. An inactive endpoint also contributes zero.

A positive disjoint crossing to a size-two active point is `3 x 2` and has
exactly four edges. The fixed sum 12 therefore forces three distinct positive
disjoint actual neighbors in addition to the six meeting neighbors:

```text
d_{G[X]}(P) >= 9.
```

All other 27 vertices have degree at least six, so the raw degree-sum lower
bound is `9+27*6=171`. A graph degree sum is even, hence it is at least 172.
But (3) gives

```text
2e(G[X]) <= 3(28)+28^2/9 = 1540/9,
```

whose largest permitted even integer is 170. Contradiction.

Every `r=19` point-size branch is exhausted.

## 8. Provenance and forbidden-import audit

The submitted input block names only `AGENTS.md` and the authenticated Wave
15 and Wave 16 audits. Text search finds references to Wave 17, Wave 14, a
global `H`-degree rule, point-size caps, and automorphisms only where the
report explicitly excludes them, records limitations, or states a
prospective consequence conditional on a future independent acceptance of
Wave 17.

Specifically:

- no `n3=54` exclusion is a premise;
- no Wave 14 residual cap or support-graph identity is used;
- the legal six-edge `3 x 3` crossing rules out a global `{0,4}` assumption;
- size-four and size-five points are analyzed directly rather than excluded
  by a cap;
- no automorphism restriction appears in an enumeration;
- the optional statement “if Wave 17 is separately accepted, then `n3>=60`”
  is downstream commentary and is not used in any `n3=57` branch.

The assumption-whitelist mutations `M21` through `M24` reject all four
forbidden imports.

## 9. Independent checker, mutations, and submitted replay

The independent checker imports no submitted code. Its profile generator,
crossing generator, point-size generator, neighbor-identity model, and exact
arithmetic are materially different from the submitted implementation. Its
semantic-core hash is
`a1764f8433fc8e3ecbdbd43a71c7c6e7e1e7e1daaef38f51422f7fe332d5c553`.

All 14 independent unit tests pass. All 24 frozen hostile mutations are
detected:

| Mutation | Detection |
|---|---|
| `M01`: `sum q` 38 to 37 | profile count changes 9 to 6 |
| `M02`: `sum q` 38 to 39 | canonical profile hash changes despite the count remaining 9 |
| `M03`: permit `d_K=3` | four extra profiles appear |
| `M04`: relax incidence cap by one | `r=18` cap becomes 28 and forced equality is lost |
| `M05`: strengthen incidence cap by one | `r=18` cap becomes 26 and falsely bypasses equality analysis |
| `M06`: call a nonpositive dense gap contradictory | exact zero at `m=27` refutes the mutation |
| `M07`: replace `m>=27` by `m>27` | the valid equality boundary is lost |
| `M08`: delete an `r=18` profile | coverage count falls from two to one |
| `M09`: duplicate an `r=18` profile | canonical sequence hash changes |
| `M10`: omit `m=27` | three required point-size profiles disappear |
| `M11`: omit `m=28` | required `2^27 3` profile disappears |
| `M12`: add one crossing edge at size two | a row/column has forbidden degree one or three |
| `M13`: add one crossing edge at size three | a row and column have forbidden degree one |
| `M14`: add one crossing edge at size four | a row and column have forbidden degree one |
| `M15`: add one crossing edge at size five | a row and column have forbidden degree one |
| `M16`: merge two positive neighbors | repeated displayed/physical vertex identity is rejected |
| `M17`: split one physical neighbor | repeated physical identity is rejected |
| `M18`: perturb the `m=27` degree sum | 163 is odd and exceeds the exact upper bound 162 |
| `M19`: change 1540 to 1541 | exact formula authentication detects `1541/9`, although the rounded even cap stays 170 |
| `M20`: use float near an exact boundary | `2^53` and `2^53+1` collide as floats; all real decisions use `Fraction` |
| `M21`: inject Wave 17 exclusion | assumption whitelist rejects it |
| `M22`: inject global `H`-degree `{0,4}` | whitelist and legal six-edge `3 x 3` crossing reject it |
| `M23`: inject Wave 14 cap | assumption whitelist rejects it |
| `M24`: inject automorphism | assumption whitelist rejects it |

The mutation canonical hash is
`fc8ea1473ea2c319bbea5ff807ab2c99dae0eeb9dc65f11160ff548218c32fde`.

After the independent result was fixed, the submitted JSON verifier replayed
successfully and all 10 submitted tests passed. The retained submitted
failure log records an initial generator/tuple `TypeError` and its narrow
repair; it does not hide a failed mathematical lemma.

## 10. Final status and limitations

All nine admissible `q`-profiles and every `r=18` and `r=19` equality or
near-equality branch have a checked contradiction. No substantive gap was
found in the scoped derivation. Therefore:

```text
conditional n3=57 exclusion: VERIFIED
Conway-99 existence/nonexistence target: UNKNOWN
novelty: UNKNOWN
```

The verification remains conditional on the authenticated audited `H/L` and
indexed-point framework. It is not a raw graph certificate, a formal proof
object, a construction, a literature survey, or an unconditional resolution
of the Conway-99 problem.
