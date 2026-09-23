# Wave 15 algebraic-lane adversarial audit

Verdict: **PASS after metadata-only repair.**  The first audit found one
noncritical ambiguous JSON key; the discovery lane recorded and repaired it,
and this re-audit confirms that both weighted moments are now unambiguous and
the obsolete key is absent.  The submitted spectral argument independently
verifies the conditional exclusion

```text
n3 != 48
```

inside the already audited Wave 14 framework.  Combining it with the
independently audited Wave 13 bound `n3>=48` and the exact divisibility
`3 | n3` gives the new necessary condition

```text
n3 >= 51.
```

This does not prove that `srg(99,14,1,2)` exists or does not exist.  The
target and novelty remain `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T10:02:27Z
metadata_reaudit_utc: 2026-07-23T10:17:11Z
git_commit: 6b6d721885a6d7c8451c6d6322a35e881b72d94e
claim_label: VERIFIED
audit_verdict: PASS_AFTER_METADATA_REPAIR
scope: >
  Independent adversarial verification of the Wave 15 spectral exclusion
  of the sole audited Wave 14 r=16, q=(2^16) residual under the conditional
  assumption n3=48 for a putative srg(99,14,1,2), plus exact replay of the
  retained triangle-intersection moments and the n3>=51 consequence.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  agents/2026-07-22-wave14-n3-48-proof-a.md: f0a7d7b5638415cff7d5ad4ef176542de9aa89a2b46a03347f90a2133f18999c
  verification/2026-07-22-wave14-n3-48-proof-audit.md: 44d1383548b26660dfb5d4b140c831774f6ca81e58ae140e3ceb2f80a9740802
  verification/2026-07-22-wave13-n3-45-audit.md: a7e520790680a3cec1d8fcff42db30105572aefeea8a41cf178aaf703147925a
  agents/2026-07-23-wave15-algebraic.md: 65f95552ad21b77e34cd7f1682746953cc8cb62c88dec7cbca701fe628c7caca
  attempts/wave15-algebraic/exact_checks.py: 8ff39bf33e2afb917a6ab52294329649d926f55bb24179561f4dd1ed5ced4b87
  attempts/wave15-algebraic/exact-checks.json: a6c9109e4fcfcdd2f5a8f5d4299ac1b4cf4037b8f1e4c468b4ecd75aba762512
  verification/n3-48-algebraic/preinspection-freeze.md: cb1bb60a0d7b2ee7c92daa0a240ca34b1699bfc6e06282ab7c29843b24a3f181
method: >
  Preinspection reconstruction from only the permitted Wave 14 proof and
  audit; exact Rayleigh-quotient derivation; point-to-original-vertex and
  meeting/support overlap audit; independent standard-library arithmetic
  checker; exact reconstruction of the triangle-incidence spectrum,
  polynomial, local moments, and global pair counts; and seven hostile
  semantic/spectral mutations. The metadata re-audit additionally requires
  the two exact weighted-moment keys, rejects either obsolete key, and
  compares an in-memory regeneration with the frozen JSON.
command: |
  python -B attempts/wave15-algebraic/exact_checks.py
  python -B verification/n3-48-algebraic/independent_check.py --artifact attempts/wave15-algebraic/exact-checks.json
  python -B -m unittest -v verification/n3-48-algebraic/test_independent_check.py
outputs:
  verification/n3-48-algebraic/preinspection-freeze.md: cb1bb60a0d7b2ee7c92daa0a240ca34b1699bfc6e06282ab7c29843b24a3f181
  verification/n3-48-algebraic/independent_check.py: fee7edfae4088c8eb3767e543e21ba209912036b5907820f4e544349d3218e0b
  verification/n3-48-algebraic/test_independent_check.py: 0cd44a95284f9004f8d9fe41cca36edf46a49d0c09dfe0afad8a23353ded40c1
  submitted_arithmetic_replay: PASS
  metadata_repair: PASS
  obsolete_moment_keys: ABSENT
  independent_checker: PASS
  independent_tests: "7/7 PASS"
  hostile_mutations: "7/7 REJECTED"
  conditional_n3_48_exclusion: VERIFIED
  conditional_n3_lower_bound: 51
  conway_99: UNKNOWN
  novelty: UNKNOWN
limitations: >
  Conditional on the independently audited Wave 13 and Wave 14 semantic
  framework; this audit did not rederive all active-triangle machinery from
  a raw 99-by-99 adjacency matrix. No Wave 15 global-lift report or verifier
  path was read. The qualitative interlacing nonhit in the submitted report
  has no enumerated matrices and is treated only as a failed-route note, not
  as evidence. No literature search was performed, so novelty is UNKNOWN.
```

The `git_commit` above was read directly from `.git/HEAD` and its referenced
file without running Git.  The shared branch can move independently; it is
only the full hash observed when this audit's inputs and checker outputs were
frozen.

## 1. Independence protocol

Before opening the submitted Wave 15 report or either submitted attempt
artifact, I read only:

```text
agents/2026-07-22-wave14-n3-48-proof-a.md
verification/2026-07-22-wave14-n3-48-proof-audit.md
```

I reconstructed the needed point-to-vertex map, the active-vertex upper
bound, the minimum-degree bridge, and the exact subset inequality.  That
preinspection result was frozen in
`verification/n3-48-algebraic/preinspection-freeze.md`.

The frozen expected proof was:

```text
|X|<=24,
delta(G[X])>=6,
2e(X)<=3|X|+|X|^2/9,
```

which would force `|X|>=27`.  The submitted report follows this exact route.
The later comparison found no semantic change needed in the frozen bridge.

I did not open `agents/2026-07-23-wave15-global-lift.md` or anything under
`verification/n3-48-global-lift/`.  I also did not inspect a Wave 14
computational source or artifact.  No Git operation was used.

## 2. Claim-by-claim verdict

| Claim | Verdict | Independent result |
|---|---|---|
| Target spectrum `14^1,3^54,(-4)^44` | PASS | Recovered from `A^2=12I-A+2J`, dimension, and trace. |
| Subset inequality | PASS | For `m=|X|`, exactly `2e(X)<=3m+m^2/9`. |
| Point-to-original-vertex map | PASS | The Wave 14 family is indexed as `P=S_u`; `X` is the set of those original vertices, not a deduplicated set of block values. |
| `|X|<=24` | PASS | Sixteen active triangles give 48 indexed incidences and every nonempty `S_u` has size at least two. |
| Meeting-neighbor count | PASS | A point of size `s` supplies `2s` distinct neighbors in `X`; repetition would put one edge in two graph triangles, violating `lambda=1`. |
| Support degree | PASS | Residual `d_H in {0,4}` and fixed sum `4|S_u|` give `d_R(S_u)=|S_u|`; `R` consists of actual graph adjacencies between active point objects. |
| Size-two meeting/support exclusion | PASS | After deleting the common label, the size-two endpoint has one crossing row, hence crossing size at most two; it cannot be an `R`-edge of `H`-degree four. |
| `delta(G[X])>=6` | PASS | Size at least three gives six meeting neighbors; size two gives four meeting plus two distinct, nonmeeting support neighbors. |
| Conditional `n3=48` exclusion | PASS / VERIFIED | Spectral lower order 27 contradicts active upper order 24. |
| Consequence `n3>=51` | PASS / VERIFIED | Uses the prior audited `n3>=48` and the general integer identity `sum_T q(T)=2n3/3`, hence `3 | n3`. |
| Triangle-graph spectrum and polynomial | PASS | Reconstructed `18^1,7^54,0^44,(-3)^132` and `Q^3-4Q^2-21Q=18J`. |
| Fixed-triangle moments | PASS | Reconstructed weighted moments 216 and 288, hence `a_2+3a_3=36`. |
| Weighted-moment metadata repair | PASS | Current payload has exactly `weighted_sum_i_a_i=216` and `weighted_sum_i_squared_a_i=288`; both obsolete keys are absent. |
| Global cross-edge pair counts | PASS | Reconstructed `(2326,20742,48,1370)`. |
| Triangle-moment obstruction | CORRECTLY ABSENT | All local and global counts are nonnegative and consistent; this lane supplies no contradiction. |
| Qualitative small-subgraph interlacing nonhit | NOT USED | No exact small matrices or spectra are supplied; it has no evidentiary role. |

## 3. Exact subset-spectral inequality

For a target adjacency matrix `A`,

```text
A^2=(k-mu)I+(lambda-mu)A+mu J
   =12I-A+2J.
```

On the all-ones complement this becomes

```text
A^2+A-12I=0,
```

whose roots are `3` and `-4`.  If their multiplicities are `f,g`, then

```text
f+g=98,
14+3f-4g=0,
```

so `(f,g)=(54,44)`.

For the indicator `x` of an arbitrary `m`-vertex set, write

```text
x=(m/99)1+y,  y perpendicular to 1.
```

The largest restricted eigenvalue is three, so

```text
2e(X)
 =14m^2/99+y^T A y
<=14m^2/99+3(m-m^2/99)
 =3m+m^2/9.                                            (1)
```

This is an exact rational bound.  The unused lower companion bound also
checks:

```text
2e(X)>=-4m+2m^2/11.                                    (2)
```

If the induced average degree is at least six, then `2e(X)>=6m`.  Combining
with (1), for nonempty `X`,

```text
6m<=3m+m^2/9
```

forces `m>=27`.  At the weakest active case `m=24`, the exact edge bounds are

```text
e(X)>=72,
e(X)<=68.
```

## 4. Point objects really are original vertices

The Wave 14 point family is explicitly **indexed**:

```text
P=S_u={active graph-triangles containing original vertex u}.
```

Define

```text
X={u:S_u is nonempty}.
```

Each of the sixteen active graph triangles has three original vertices, so
the indexed incidence sum is

```text
sum_(u in X)|S_u|=16*3=48.
```

Every nonempty point has size at least two.  Therefore

```text
2|X|<=48,
|X|<=24.                                                (3)
```

This count does not silently identify equal set values.  Even if one tried
to forget the indexing, two distinct vertices with the same point of size
at least two would violate the audited linearity of the indexed family.

## 5. The delicate minimum-degree bridge

Fix `u in X` and let `s=|S_u|`.  Every active graph triangle through `u`
contains two other original vertices.  They belong to `X`, are adjacent to
`u`, and are distinct across the `s` triangles: a repeated vertex would put
the edge joining it to `u` in two graph triangles, contradicting
`lambda=1`.  Thus meeting edges give

```text
d_(G[X])(u)>=2s.                                        (4)
```

For `s>=3`, this is already at least six.

Now take `s=2`.  Wave 14 defines a simple graph `R` on the indexed points,
where an `R`-edge is an actual original-graph edge of `H`-degree four.  Since
every nonzero residual `H`-degree equals four and the fixed sum at `S_u` is
`4s`,

```text
d_R(S_u)=s=2.                                           (5)
```

Both endpoints of an `R`-edge are active: an empty endpoint has empty
crossing and therefore `H`-degree zero.

It remains to show that the two neighbors in (5) are not among the four
meeting neighbors in (4).  If `uv` is a meeting edge, `S_u,S_v` share their
active triangle.  Delete that common label on both sides, as the inherited
crossing identity requires.  The `S_u` side then has one label, and its sole
row has degree zero or two.  Hence

```text
d_H(uv)=e_L(S_u,S_v)<=2.
```

It cannot equal four, so `uv` is not an `R`-edge.  Since `R` is simple, its
degree two supplies two distinct additional original neighbors.  Therefore

```text
d_(G[X])(u)>=4+2=6.                                     (6)
```

Equations (4)--(6) establish `delta(G[X])>=6` with no assumption about a
nonedge and no global disjointness assumption stronger than the size-two
case actually needed.

Combining (3), (6), and Section 3 gives the contradiction

```text
27<=|X|<=24.
```

The conditional `n3=48` residual is therefore impossible.

## 6. Divisibility and the strengthened lower bound

The prior independent Wave 13 audit verifies

```text
n3>=48.
```

The inherited general active-triangle identity is

```text
sum_T q(T)=2n3/3.
```

Its left side is an integer.  Hence `3` divides `2n3`, and coprimality gives
`3 | n3`.  Excluding 48 therefore moves the next possible value to 51:

```text
n3>=51.
```

This is a necessary condition on a putative Conway graph, not an existence
or nonexistence result.

## 7. Independent triangle-moment reconstruction

Let `C` be the `99`-by-`231` vertex/graph-triangle incidence matrix.  Every
vertex lies in seven graph triangles and every edge lies in its unique
triangle, so

```text
CC^T=7I+A,
C^TC=3I+Q.
```

The nonzero eigenvalues of `C^TC` are `21^1,10^54,3^44`; its nullity is 132.
Consequently

```text
spec(Q)=18^1,7^54,0^44,(-3)^132.
```

The polynomial `p(x)=x(x-7)(x+3)` kills all restricted eigenspaces, while
`p(18)=18*231`, proving

```text
Q^3-4Q^2-21Q=18J.                                      (7)
```

For a fixed graph triangle `T`, there are 18 meeting triangles, and each
meeting pair has exactly five common `Q`-neighbors.  A disjoint triangle
joined to `T` by `i` cross edges has exactly `i` common `Q`-neighbors; the
cross edges are a matching, so `0<=i<=3`.  The row sum of `Q^2` and the
diagonal of `Q^4` give

```text
sum_i i a_i(T)=216,
sum_i i^2 a_i(T)=288,
a_2(T)+3a_3(T)=36.                                     (8)
```

For the all-`q=2` profile, `a_2=d_L=3q`, so an active triangle has

```text
(a_0,a_1,a_2,a_3)=(22,174,6,10),
```

and an inactive triangle has

```text
(a_0,a_1,a_2,a_3)=(20,180,0,12).
```

Summing over 16 active and 215 inactive triangles and dividing by two gives
the unordered disjoint-triangle pair counts by number of cross edges:

```text
(N_0,N_1,N_2,N_3)=(2326,20742,48,1370).
```

They total `24486`, have the required first moment, and are all nonnegative.
The report is correct that these moments do not themselves obstruct
`n3=48`.

## 8. Independent checker and hostile mutations

`verification/n3-48-algebraic/independent_check.py` imports no submitted
module.  It independently:

- derives both restricted eigenvalues and their multiplicities;
- verifies both exact subset bounds;
- enumerates all nine nonnegative solutions of
  `2x_2+3x_3=48`;
- verifies that every one of their orders 16 through 24 contradicts the
  spectral upper bound;
- reconstructs (7), (8), both local distributions, and all four global pair
  counts; and
- verifies the submitted JSON's semantic digest and critical exact fields.

All seven focused tests pass.  The checker also rejects seven hostile
weakenings:

```text
allow an active singleton                         REJECTED
make support edges non-adjacencies                REJECTED
allow repeated support neighbors                  REJECTED
do not delete the common active label             REJECTED
allow repeated meeting vertices                   REJECTED
allow a meeting crossing of size four             REJECTED
replace the restricted maximum 3 by 4             REJECTED
```

The submitted exact checker reruns successfully, its frozen JSON hash
matches the report, and its semantic digest independently recomputes as

```text
40f5d81a71cc500c57e5f5858d11acde0afaf67d81233e68bf0794649e1a9ae8.
```

## 9. Recorded ambiguity, transparent repair, and status boundary

The first audit recorded that the original submitted JSON field

```text
fixed_triangle_moments.sum_i_a_i = 216
```

had an ambiguous name.  Its value was the **weighted** moment
`sum_i i*a_i`, not the unweighted count `sum_i a_i`.  The submitted report,
code comment, and arithmetic had always stated and used the weighted identity
correctly, so this was a noncritical metadata-label defect rather than a
mathematical error.

The discovery lane preserved that history in its report and renamed the two
script variables and JSON fields to

```text
weighted_sum_i_a_i = 216
weighted_sum_i_squared_a_i = 288
```

Their semantics are now explicit:

```text
weighted_sum_i_a_i         = sum_i i*a_i,
weighted_sum_i_squared_a_i = sum_i i^2*a_i.
```

The obsolete keys `sum_i_a_i` and `sum_i_squared_a_i` are absent from the
current generated payload and frozen JSON.  The submitted script regenerates
that JSON exactly in memory, and the new semantic digest recomputes as

```text
40f5d81a71cc500c57e5f5858d11acde0afaf67d81233e68bf0794649e1a9ae8.
```

For transparent provenance, the first-audited hashes were

```text
report:          5c5468e7bc25110d11f9c88996e75cfa011de5b3269f52a405a0615e150686a7
script:          ffd34b7ce806f9042f1ee33b2a6f4514f22e9a33a782bf7e38c7ccd115293701
JSON:            2b7e737ed496b997e106600867410ffbadf5ff5ac56a3afdc46ddedb26d56a45
semantic digest: 48841fbd08ba74f4bbe1dcdc2347e0fcdd2a80d72ad76ba97fa7f2b742d63cec
```

and the repaired hashes are

```text
report:          65f95552ad21b77e34cd7f1682746953cc8cb62c88dec7cbca701fe628c7caca
script:          8ff39bf33e2afb917a6ab52294329649d926f55bb24179561f4dd1ed5ced4b87
JSON:            a6c9109e4fcfcdd2f5a8f5d4299ac1b4cf4037b8f1e4c468b4ecd75aba762512
semantic digest: 40f5d81a71cc500c57e5f5858d11acde0afaf67d81233e68bf0794649e1a9ae8
```

The repair changes names, hashes, and the discovery report's repair log only.
Independent replay returns the same spectrum, all nine active-point rows,
the same `m<=24` versus `m>=27` contradiction, the same triangle moments
216 and 288, the same four pair counts, and the same status boundary.  The
proof is unchanged.

The qualitative statement that principal interlacing was too weak is not
accompanied by the small matrices or spectra to which it refers.  Because it
is explicitly retained only as a failed-route note and is unused, this audit
assigns it no evidentiary status.

Final boundary:

```text
Wave 15 subset-spectral inequality:       PASS / VERIFIED
point-to-original-vertex bridge:          PASS / VERIFIED
active order |X|<=24:                     PASS / VERIFIED
active minimum degree delta>=6:           PASS / VERIFIED
conditional n3=48 exclusion:              PASS / VERIFIED
necessary conditional bound n3>=51:       PASS / VERIFIED
triangle-intersection moment lane:        PASS / consistent, no obstruction
weighted-moment metadata repair:          PASS / obsolete keys absent
Conway srg(99,14,1,2):                    UNKNOWN
novelty:                                  UNKNOWN
```
