# Wave 19 structural discovery at the conditional `n3=60` frontier

Verdict: **UNKNOWN / finite residual.**  The frozen audited premises reduce
a putative `n3=60` configuration to two explicit `r=20` regimes, but do not
exclude either regime:

```text
(A) |X|=27, point sizes 2^21 3^6;
(B) |X|=30, point sizes 2^30.
```

Of the thirteen admissible `q`-profiles, all twelve with `r<=19` are
contradicted.  For `r=20`, the intermediate sizes `|X|=28,29` are also
contradicted.  Exact
machine-readable residual certificates give the two cubic cases at
`|X|=27` and every surviving moment/topology case at `|X|=30`.

This lane is independent of Wave 17 catalogs and the Wave 18 `n3=57`
claim.  It uses no global `H`-degree rule, point-size cap, Wave 14 residual
identity, automorphism, SAT result, or ILP result.  The Conway-99 target and
novelty remain `UNKNOWN`.

```yaml
role: proof_a
date_utc: 2026-07-23T13:09:06Z
git_commit: ba13ceec2a6672d1c8ab6fed9c5c9760da3bbcaf
claim_label: UNKNOWN
scope: independent conditional n3=60 structural reduction for a putative srg(99,14,1,2), ending in exact finite residuals at r=20 and |X| in {27,30}
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/2026-07-23-wave16-n3-51-structural-audit.md: 99203a15db2646a759edbb2241eb4bd5e6001733ac862952c9db57446c58ead6
  verification/2026-07-23-wave15-global-lift-audit.md: edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036
method: freeze audited premises; enumerate sum-40 q-profiles under d_K at least 4; replay endpoint-local crossings and the dense-subset bound; analyze incidence and spectral equality; use exact point-size excess partitions, no-Berge parity cases, degree sums, outside-neighbor first and second moments, six-vertex cubic graph enumeration, and all simple extra-edge topologies through three edges
command: |
  .venv\Scripts\python.exe -B attempts\wave19-n3-60-structural\exact_check.py --output attempts\wave19-n3-60-structural\exact-checks.json --residual-output attempts\wave19-n3-60-structural\residual-certificates.json
  .venv\Scripts\python.exe -B -m unittest -v attempts\wave19-n3-60-structural\test_exact_check.py
  .venv\Scripts\python.exe -B attempts\wave19-n3-60-structural\exact_check.py --verify attempts\wave19-n3-60-structural\exact-checks.json --verify-residual attempts\wave19-n3-60-structural\residual-certificates.json
outputs:
  attempts/wave19-n3-60-structural/exact_check.py: c7564eef0f1c62165c91a36071ab34b494ead891877011e755407ad48adee460
  attempts/wave19-n3-60-structural/test_exact_check.py: 1b1d2628d6c2d837dec24ec679d579676b5a0e66962e0266cee2642040bf6165
  attempts/wave19-n3-60-structural/exact-checks.json: fc884ea131b1b6c926d9e71ddb1f7925e15c39498f1d7b72819a6473b39ab8dd
  attempts/wave19-n3-60-structural/residual-certificates.json: 3396b3b67b944b86bfd0d51e8beca25dfc9350815269c62cda4fa7c22a7a5c8b
  attempts/wave19-n3-60-structural/failed-attempts.md: 62d43cdb66c599c8c1e1618ca54267c1bf08ba20ad175e04883349cf6f876a0e
  admissible_q_profiles: 13
  focused_tests: "11/11 PASS"
  exact_json_replay: PASS_BYTE_IDENTICAL
  residual_json_replay: PASS_BYTE_IDENTICAL
  conditional_n3_60: UNKNOWN_FINITE_RESIDUAL
  conway_99_target: UNKNOWN
  novelty: UNKNOWN
limitations: conditional on the frozen audited H/L and indexed-point framework rather than a raw 99-by-99 adjacency derivation; the standard-library artifacts verify finite arithmetic and small graph classifications but are not semantic proof certificates; the two residual descriptions are necessary conditions, not constructions or feasibility certificates; no independent Wave 19 verification, formal proof object, target decision, or novelty conclusion is supplied
```

The commit value was read directly from `.git/HEAD` and its referenced
file; no Git command was run.  The shared branch may move independently.

## 1. Frozen premises and status boundary

At `n3=60`, the audited identities give

```text
sum_T q(T) = 2n3/3 = 40,
q(T) = 0 or q(T) >= 2.
```

Let `r` count the active labels, so zero entries are omitted from an active
profile.  For every active label,

```text
d_K(T)=r-1-3q(T) >= 4.
```

For the active indexed point

```text
S_u={active triangle labels containing original vertex u},
X={u:S_u is nonempty},
```

the imported facts are:

1. every nonempty point has size at least two;
2. the point family is linear, every active label occurs in exactly three
   indexed points, and the dual incidence system has no Berge triangle;
3. an actual graph edge obeys the two-sided zero-or-two crossing rule after
   deleting both copies of a possible common active label;
4. the fixed-point identity is

   ```text
   sum_{v adjacent to u} d_H(uv)
      = 2 sum_{T in S_u} q(T);
   ```

5. a point `S_u` gives exactly `2|S_u|` distinct meeting neighbors of `u`
   in `X`;
6. active incidence and the exact subset inequality give

   ```text
   sum_{u in X}|S_u|=3r,
   2e(G[X]) <= 3|X|+|X|^2/9.
   ```

No Wave 17 or Wave 18 statement, file, result, or artifact is an input.
In particular, this report does not assume that `n3>=60`; it studies the
conditional equality directly.

## 2. Thirteen exact `q`-profiles

Since every active entry is at least two, `r<=20`.  Exact nondecreasing
partition generation and only the displayed `d_K>=4` test leave:

| `r` | active `q` multiset | `d_K` multiset | point cap |
|---:|---|---|---:|
| 14 | `2^2 3^12` | `4^12 7^2` | 21 |
| 15 | `2^5 3^10` | `5^10 8^5` | 22 |
| 16 | `2^8 3^8` | `6^8 9^8` | 24 |
| 17 | `2^14 4^3` | `4^3 10^14` | 25 |
| 17 | `2^13 3^2 4^2` | `4^2 7^2 10^13` | 25 |
| 17 | `2^12 3^4 4` | `4 7^4 10^12` | 25 |
| 17 | `2^11 3^6` | `7^6 10^11` | 25 |
| 18 | `2^16 4^2` | `5^2 11^16` | 27 |
| 18 | `2^15 3^2 4` | `5 8^2 11^15` | 27 |
| 18 | `2^14 3^4` | `8^4 11^14` | 27 |
| 19 | `2^18 4` | `6 12^18` | 28 |
| 19 | `2^17 3^2` | `9^2 12^17` | 28 |
| 20 | `2^20` | `13^20` | 30 |

All active `q=4` cases are explicit; no surviving profile has `q>=5`.

## 3. Universal minimum degree and crossing scope

At a size-two point with label values `(a,b)`, every incident actual edge
has endpoint-local `H`-degree zero or four.  Meeting and inactive endpoints
contribute zero; every positive endpoint is active, disjoint, and a
distinct original graph neighbor.  Thus:

| pair | fixed sum | positive disjoint neighbors | induced-degree lower bound |
|---|---:|---:|---:|
| `(2,2)` | 8 | 2 | 6 |
| `(2,3)` | 10 | impossible | — |
| `(2,4)` | 12 | 3 | 7 |
| `(3,3)` | 12 | 3 | 7 |
| `(3,4)` | 14 | impossible | — |
| `(4,4)` | 16 | 4 | 8 |

Points of size at least three already have at least six distinct meeting
neighbors.  Consequently every admissible profile satisfies

```text
delta(G[X])>=6,
|X|>=27.                                                (1)
```

This is not a global `H`-degree assertion.  Exact two-sided crossing
enumeration gives possible edge counts `0,4,6` for a disjoint `3`-by-`3`
crossing.  The `{0,4}` conclusion is used only where one endpoint has size
two or where overlap deletion leaves at most two rows.

## 4. Elimination through `r=17`

Non-singleton incidence gives

```text
|X| <= floor(3r/2).
```

For every profile through `r=17`, this is at most 25, contradicting (1).

## 5. Elimination of the three `r=18` profiles

Incidence `3r=54` and (1) force `|X|=27` and point sizes `2^27`.  The lower
and spectral degree-sum bounds are both 162, so `G[X]` is 6-regular.

Treat the size-two points as edges of a graph `F` on the eighteen active
labels.  Linearity makes `F` simple, and the three point occurrences of
each label make it cubic.  The no-Berge-triangle premise makes `F`
triangle-free.

- In `2^16 4^2`, every point through a `q=4` label has type `(2,4)` or
  `(4,4)`, hence induced degree at least seven.
- In `2^15 3^2 4`, no size-two point can mix even and odd `q`.  The two
  odd labels would have to form their own cubic component, impossible in a
  simple graph on two vertices.
- In `2^14 3^4`, the four odd labels similarly induce a cubic component.
  It must be `K4`, contradicting triangle-freeness.

## 6. Elimination of the two `r=19` profiles

The incidence sum is 57, so `|X|` is 27 or 28.

At `|X|=27`, spectral equality makes `G[X]` 6-regular.  The point-size
multisets are

```text
2^26 5,
2^25 3 4,
2^24 3^3.
```

The first two have a point with at least eight meeting neighbors.  In the
last, a size-three point has no disjoint active neighbor.  Meeting a
size-two point leaves a `2`-by-`1` crossing and contributes zero; only the
other two size-three points can contribute, at most four each.  The fixed
sum is at least twelve, contradicting the maximum eight.

At `|X|=28`, the point sizes are `2^27 3`.  The unique size-three point has
six size-two meeting neighbors, all with zero overlap-deleted crossing.  A
positive disjoint `3`-by-`2` crossing contributes four.  If the fixed sum
is not divisible by four there is an immediate contradiction; otherwise
it forces at least three additional induced neighbors and degree at least
nine.  The degree sum is then at least 172, while the exact spectral bound
permits at most the even integer 170.

## 7. The sole `r=20`, `q=2^20` profile

Here

```text
sum_{u in X}|S_u|=60,
27<=|X|<=30.
```

For later use, write

```text
d_{G[X]}(x)=6+s_x,
T=sum_x s_x,
U=sum_x s_x^2.
```

For `z` outside `X`, put `a_z=|N(z) intersect X|`.  The exact audited
outside-neighbor counts replay as

```text
sum_z a_z = 8m-T,
sum_z a_z^2 = 2m^2-30m-13T-U,             m=|X|.        (2)
```

For fixed integer count and sum, the minimum square sum is attained by the
two nearest integers.  The checker uses exact integer division, not a
floating-point Cauchy approximation.

### 7.1 Residual A: `|X|=27`

The point-size excess over two is six.  There are eleven integer
partitions.  Spectral equality makes `G[X]` 6-regular, so every point of
size at least four is impossible.  The unique surviving multiset is

```text
2^21 3^6.                                               (A)
```

Equation (2) gives

```text
72 outside vertices,
sum a_z=216,
sum a_z^2=648.
```

The integer minimum is exactly `72*3^2=648`, so every outside vertex has
exactly three neighbors in `X`.  This confirms rather than contradicts the
spectral equality case.

Fix a size-three point `P`.  Its six meeting neighbors saturate its induced
degree.  Size-two meeting endpoints contribute zero to its fixed sum.
Therefore `P` needs exactly three positive crossings to other size-three
meeting points, each of size four.  The positive-meeting graph `J` on the
six size-three points is simple cubic.

Exact enumeration of every simple cubic graph on six labeled vertices,
followed by permutation canonicalization, gives two isomorphism types:

```text
J = K3,3:
0 0 0 1 1 1
0 0 0 1 1 1
0 0 0 1 1 1
1 1 1 0 0 0
1 1 1 0 0 0
1 1 1 0 0 0

J = triangular prism:
0 1 1 1 0 0
1 0 1 0 1 0
1 1 0 0 0 1
1 0 0 0 1 1
0 1 0 1 0 1
0 0 1 1 1 0
```

The first has no triangle; the second has exactly the two triangles
`012` and `345`.  The no-Berge premise does not by itself exclude either:
a triangle of meeting points may use one common active label.

Every size-two point has exactly two positive disjoint size-two neighbors;
a positive edge to a size-three point would give that size-three point an
impossible seventh induced neighbor.  Hence these positive edges form a
simple spanning 2-factor on the 21 size-two points, with 21 edges.  The
checker lists all 60 possible cycle-length multisets.

The induced graph has exactly 81 edges: 60 meeting edges from the twenty
active triangles and 21 positive disjoint size-two edges.  These
conditions, the two displayed `J` matrices, and the outside multiset
`3^72` are necessary conditions.  They are not a full construction or a
feasibility certificate.

### 7.2 Elimination of `|X|=28`

The spectral bound permits total degree excess at most two.  The five
point-size multisets are

```text
2^27 6,
2^26 3 5,
2^26 4^2,
2^25 3^2 4,
2^24 3^4.
```

The first three have meeting-degree excess greater than two.  In
`2^25 3^2 4`, the size-four point consumes the entire excess allowance.
Each size-three point has degree exactly six and can receive positive
meeting contributions only from the other size-three point and the
size-four point, at most four from each.  This is less than its fixed sum
twelve.

For `2^24 3^4`, let `Y` be the four size-three points and let `s(P)` count
the disjoint active neighbors of `P in Y`.  Then

```text
sum_{P in Y}s(P) <= 2.
```

A positive disjoint `3`-by-`3` crossing of size six would force a second
such crossing at the same point, and symmetry would give at least four
disjoint incidences in `Y`; hence no size-six crossing occurs.  All
positive terms have size four.  Each point of `Y` needs three, so the
positive-meeting graph on `Y` has at least five of its six possible edges.

Every graph with five or six edges on four vertices has two triangles
sharing an edge.  Three pairwise-meeting linear points must share one
common label: otherwise their three pairwise intersection labels form a
forbidden Berge triangle.  Applying this to the two triangles forces their
shared-edge label into all four points, contradicting the exact
three-point occurrence of an active label.  Thus `|X|=28` is impossible.

### 7.3 Elimination of `|X|=29`

The point-size choices are

```text
2^28 4,
2^27 3^2.
```

The spectral upper degree sum is 180, so `T<=6`.

For `2^28 4`, the size-four point has eight meeting neighbors, all size
two.  Every overlap-deleted `3`-by-`1` crossing is zero.  Its fixed sum
sixteen requires four positive disjoint `4`-by-`2` crossings, giving
degree at least twelve.  Therefore `T=6`, `U=36`, and all other vertices
have degree six.  Equation (2) would require 70 nonnegative integers with

```text
sum a_z=226,
sum a_z^2=698.
```

The integer minimum square sum at total 226 is 742, a contradiction.

For `2^27 3^2`, each size-three point has degree excess at least two.  The
minimum two occurs only when the two size-three points meet with a positive
four-edge crossing; otherwise it is at least three.  Degree-sum parity
leaves `T=4` or `T=6`.

| `T` | minimum `U` | outside sum | maximum square sum from (2) | integer minimum |
|---:|---:|---:|---:|---:|
| 4 | 8 | 228 | 752 | 756 |
| 6 | 10 | 226 | 724 | 742 |

Both cases contradict the integer minimum.

### 7.4 Residual B: `|X|=30`

All thirty points have size two.  Let `F` be the graph whose vertices are
the twenty active labels and whose edges are the indexed points.  Then `F`
is simple, cubic, and triangle-free.  Its line graph `L(F)` is the
4-regular meeting graph on `X`.

Each indexed point has fixed sum eight and hence exactly two positive
disjoint neighbors.  Those edges form a simple spanning 2-factor `R` on
the thirty points, disjoint from `L(F)`.  Thus

```text
L(F) union R
```

is a mandatory 6-regular spanning subgraph of `G[X]`.  It has 90 edges.
The 331 possible cycle-length multisets for `R` are counted exactly.

Let `Z` contain every remaining induced edge.  Its endpoints are disjoint
points and its crossing is zero.  Then

```text
s_x=d_Z(x),
T=2e(Z),
U=sum_x d_Z(x)^2.
```

The spectral degree-sum bound first gives `T<=10`.  For `T=8,10`, even the
smallest possible `U=T` violates the exact integer outside moment:

| `T` | outside sum | maximum square sum | integer minimum |
|---:|---:|---:|---:|
| 8 | 232 | 788 | 796 |
| 10 | 230 | 760 | 782 |

Therefore

```text
e(Z)<=3.                                                (B)
```

All simple graph types through three edges survive these moment checks:

| `Z` type | `T` | `U` | outside sum | outside square sum | degree-multiset count |
|---|---:|---:|---:|---:|---:|
| empty | 0 | 0 | 240 | 900 | 1297 |
| `K2` | 2 | 2 | 238 | 872 | 354 |
| `2K2` | 4 | 4 | 236 | 844 | 69 |
| `P3` | 4 | 6 | 236 | 842 | 52 |
| `3K2` | 6 | 6 | 234 | 816 | 6 |
| `P3 + K2` | 6 | 8 | 234 | 814 | 3 |
| `P4` | 6 | 10 | 234 | 812 | 2 |
| `K1,3` | 6 | 12 | 234 | 810 | 1 |
| `K3` | 6 | 12 | 234 | 810 | 1 |

Here “degree-multiset count” counts exact histograms of the 69 outside
degrees `a_z` satisfying both moments and `0<=a_z<=14`; it does not count
assignments or prove that a histogram extends to an SRG.  The certificate
lists every histogram when a row has at most ten.

## 8. Exact residual and conclusion

The complete outcome under the frozen premises is:

```text
r<=19:             EXCLUDED / DERIVED
r=20, |X|=28,29:  EXCLUDED / DERIVED
r=20, |X|=27:     FINITE RESIDUAL / UNKNOWN
r=20, |X|=30:     FINITE RESIDUAL / UNKNOWN
n3=60:            UNKNOWN
Conway-99 target: UNKNOWN
novelty:          UNKNOWN
```

Because `n3=60` is not excluded, this lane derives no stronger `n3` or
induced-six-cycle lower bound.  Combining prior waves would not change this
Wave 19 status; no such combination is used here.

## 9. Reproducibility and retained non-closures

The checker uses only the Python standard library.  It hashes every frozen
input on startup, generates all thirteen profiles, exhausts every relevant
small crossing matrix, enumerates all point-size partitions, independently
classifies the six-vertex cubic graphs, verifies every outside moment, and
enumerates the residual degree histograms.  Eleven focused tests pass.
Both JSON artifacts reproduce byte-for-byte.

No computational command failed.  The two proof routes that stop without a
contradiction—the `|X|=27` equality case and the `|X|=30` moment
reduction—are recorded in
`attempts/wave19-n3-60-structural/failed-attempts.md`.  No solver exit code,
model confidence, or absence of a found object is treated as a
certificate.
