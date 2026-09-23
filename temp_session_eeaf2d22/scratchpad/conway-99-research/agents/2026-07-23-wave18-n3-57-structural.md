# Wave 18 structural discovery at the conditional `n3=57` frontier

Verdict: **conditional `n3=57` is excluded / DERIVED, pending independent
verification.**  The derivation uses only the frozen audited `H/L`,
indexed-point, crossing, fixed-point, and dense-subset premises.  It does
not use a Wave 17 result, a Wave 14 residual cap, a global `H`-degree rule,
or any point-size upper bound.

There are nine admissible active `q`-profiles.  The dense-subset argument
immediately eliminates every profile through `r=17`.  Exact incidence and
spectral equality reduce `r=18` and `r=19` to four small point-size cases;
endpoint-local crossing arithmetic contradicts each one.

Under the project protocol this discovery lane does not mark its own result
`VERIFIED`.  The Conway-99 existence target and novelty both remain
`UNKNOWN`.

```yaml
role: proof_a
date_utc: 2026-07-23T12:37:05Z
git_commit: 0e5c09fcab45b0af0509a5832f559f355582e7f5
claim_label: DERIVED
scope: conditional exclusion of project n3=57 for a putative srg(99,14,1,2), independent of whether the Wave 17 n3=54 census is accepted
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/2026-07-23-wave16-n3-51-structural-audit.md: 99203a15db2646a759edbb2241eb4bd5e6001733ac862952c9db57446c58ead6
  verification/2026-07-23-wave15-global-lift-audit.md: edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036
method: freeze audited inputs; enumerate all active q-profiles with sum 38 and d_K at least 4; prove delta(G[X]) at least 6 by endpoint-local crossing and fixed-point identities; apply exact incidence and dense-subset bounds; analyze the r=18 and r=19 equality cases by point-size excess, parity, simple cubic point incidence, and exact overlap-deleted crossing counts
command: |
  .venv\Scripts\python.exe -B attempts\wave18-n3-57-structural\exact_check.py --output attempts\wave18-n3-57-structural\exact-checks.json
  .venv\Scripts\python.exe -B -m unittest -v attempts\wave18-n3-57-structural\test_exact_check.py
  .venv\Scripts\python.exe -B attempts\wave18-n3-57-structural\exact_check.py --verify attempts\wave18-n3-57-structural\exact-checks.json
outputs:
  attempts/wave18-n3-57-structural/exact_check.py: 0896a9a5536090262e78efe3a831f3a3b839373f11b00a956d038fe2a1ef2a22
  attempts/wave18-n3-57-structural/test_exact_check.py: 7b9fe196da7c8e1178f88d7e9123b6b693687485016ba3222ffec0ac199d58ba
  attempts/wave18-n3-57-structural/exact-checks.json: 76decce7f0af8e3bf2db483096a10a86321a9d7143e6123ad2081ec17d28604c
  attempts/wave18-n3-57-structural/failed-runs.md: 98bcbe50920ea53bbcc50417f382806640a6fab55d40e6d69231ad07807dc439
  admissible_q_profiles: 9
  focused_tests: "10/10 PASS"
  exact_json_replay: PASS_BYTE_IDENTICAL
  conditional_n3_57: EXCLUDED_DERIVED
  conway_99_target: UNKNOWN
  novelty: UNKNOWN
limitations: conditional on the frozen audited H/L and indexed-point semantics rather than a raw 99-by-99 adjacency derivation; the checker verifies finite arithmetic but is not a semantic proof certificate; no independent Wave 18 verifier has yet audited this derivation; no Wave 17 premise, construction, formal proof object, target existence/nonexistence conclusion, automorphism, catalog completeness, or novelty conclusion is supplied
```

The commit value was read directly from `.git/HEAD` and its referenced file;
no Git command was run.  The shared branch may move independently.

## 1. Frozen premises and independence boundary

At `n3=57`, the audited identities give

```text
sum_T q(T) = 2n3/3 = 38,
q(T) = 0 or q(T) >= 2.
```

Let `r` be the number of active labels, so the zero entries are omitted
from the active profile.  For an active label,

```text
d_K(T) = r-1-3q(T) >= 4.
```

The indexed active point at an original graph vertex `u` is

```text
S_u = {active triangle labels containing u}.
```

The imported properties are:

1. every nonempty `S_u` has size at least two;
2. the points are linear, every active label occurs in three indexed points,
   and three distinct labels cannot occur in three pairwise-meeting points;
3. after deleting both copies of a possible common label, the crossing on
   an actual graph edge has every row and column degree zero or two;
4. the fixed-point identity is

   ```text
   sum_{v adjacent to u} d_H(uv)
      = 2 sum_{T in S_u} q(T);
   ```

5. the labels in `S_u` give exactly `2|S_u|` distinct neighbors of `u`
   in the active original-vertex set

   ```text
   X = {u : S_u is nonempty};
   ```

6. the exact active incidence identity and subset bound are

   ```text
   sum_{u in X}|S_u| = 3r,
   2e(G[X]) <= 3|X|+|X|^2/9.
   ```

In particular, `delta(G[X])>=6` implies `|X|>=27`.

No Wave 17 report, artifact, result, or cap is an input.  This lane is
therefore a direct analysis of the equality `n3=57`, not a consequence of
any claimed `n3>=57` lower bound.

## 2. Exact active `q`-profiles

Since every active entry is at least two, `r<=19`.  Nondecreasing partition
generation followed only by the displayed `d_K>=4` test gives exactly nine
profiles:

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

Thus all `q=4` cases are explicit, and no admissible profile contains an
active entry `q>=5`.

## 3. Minimum induced degree, including every `q=4` pairing

Fix a size-two point `P=S_u={i,j}`.  For an actual edge `uv`, the
endpoint-local crossing rule gives:

| other endpoint | crossing after common-label deletion | edge count |
|---|---|---:|
| inactive | two rows and no columns | `0` |
| active and meeting `P` | one remaining row | `0` |
| active and disjoint from `P` | two rows | `0` or `4` |

The last row holds for every other point size: a nonzero column must use
both rows, while a nonzero row has exactly two entries, so the nonempty
crossing is one `K_(2,2)`.

Consequently every term in the fixed-point sum at `u` is zero or four.  A
size-two point with label values `(a,b)` therefore has

```text
number of positive terms = (a+b)/2
```

when `a+b` is even, and is impossible when `a+b` is odd.  The complete
table through the largest admissible value is:

| pair | fixed sum | positive distinct nonmeeting active neighbors | induced-degree lower bound |
|---|---:|---:|---:|
| `(2,2)` | 8 | 2 | 6 |
| `(2,3)` | 10 | impossible | — |
| `(2,4)` | 12 | 3 | 7 |
| `(3,3)` | 12 | 3 | 7 |
| `(3,4)` | 14 | impossible | — |
| `(4,4)` | 16 | 4 | 8 |

The four meeting neighbors and the positive neighbors are disjoint because
every meeting crossing is zero.  The positive summands are indexed by
distinct actual graph neighbors, and a positive crossing has a nonempty
other endpoint, so those neighbors lie in `X`.

If `|S_u|>=3`, its `2|S_u|` meeting neighbors already give degree at least
six.  Hence in every admissible profile

```text
delta(G[X]) >= 6.                                      (1)
```

This does not impose a point-size cap.  It also does not impose a global
`H`-degree restriction: exhaustive enumeration admits crossing edge counts
`0,4,6` in a `3`-by-`3` crossing.  Only the size-two endpoint statement
`d_H(uv) in {0,4}` is used.

## 4. Profiles through `r=17`

From non-singleton points and the incidence identity,

```text
2|X| <= sum_{u in X}|S_u| = 3r,
|X| <= floor(3r/2).
```

For `r<=17`, this gives `|X|<=25`.  Equation (1) and the audited
dense-subset inequality give `|X|>=27`, a contradiction.  This eliminates
the first six rows of the profile table.

## 5. The two `r=18` equality profiles

Here the incidence sum is `54`, so non-singleton points give `|X|<=27`;
equation (1) gives `|X|>=27`.  Therefore

```text
|X|=27, every active point has size two.
```

At `m=27`, the lower and spectral degree-sum bounds coincide:

```text
6m = 162 = 3m+m^2/9.
```

Thus `G[X]` is exactly 6-regular.

Regard each size-two indexed point as an edge on the `r=18` active labels.
Linearity makes this point graph simple, and the three indexed occurrences
of every label make it cubic.

### 5.1 Profile `2^16 3^2`

A point mixing a `q=2` label and a `q=3` label is impossible by the fixed
sum ten and endpoint-local `{0,4}` rule.  Hence the simple cubic point graph
has no edge between the sixteen even labels and the two odd labels.  Each
odd label would need all three point-graph neighbors inside a simple
two-vertex graph, where its maximum degree is one.  Contradiction.

### 5.2 Profile `2^17 4`

The unique `q=4` label has three incident point-graph edges.  Their other
ends must be `q=2` labels.  Each corresponding `(2,4)` indexed point has
four meeting neighbors and exactly three distinct positive nonmeeting
neighbors, so its degree in `G[X]` is at least seven.  This contradicts
6-regularity.

## 6. The `r=19`, `q=2^19` profile

The incidence sum is `57`.  Together with (1),

```text
27 <= |X| <= floor(57/2)=28.
```

### 6.1 Equality case `|X|=27`

The point-size excess above two is `57-2(27)=3`.  The only size multisets
are

```text
2^26 5,
2^25 3 4,
2^24 3^3.
```

As above, spectral equality makes `G[X]` 6-regular.  The first two
multisets are impossible because a size-five or size-four point has,
respectively, ten or eight distinct meeting neighbors.

It remains to consider `2^24 3^3`.  Fix a size-three point `P`.  Its six
meeting neighbors saturate its induced degree, so it has no disjoint active
neighbor.  An inactive endpoint contributes zero to the fixed-point sum.
After common-label deletion:

```text
P meeting a size-two point:    2-by-1 crossing, edge count 0;
P meeting a size-three point:  2-by-2 crossing, edge count 0 or 4.
```

Only the other two size-three indexed vertices can therefore contribute
positively, for a total at most eight.  But all three labels at `P` have
`q=2`, so its fixed-point sum is

```text
2(2+2+2)=12.
```

Contradiction.

### 6.2 Near-equality case `|X|=28`

Now the excess is one, so the unique point-size multiset is

```text
2^27 3.
```

Let `P` be the unique size-three point.  Its six meeting neighbors are all
size-two points, and every corresponding overlap-deleted crossing is
`2`-by-`1`, hence empty.  Inactive endpoints also contribute zero.  A
positive disjoint crossing from `P` to a size-two active point is
`3`-by-`2`; exhaustive two-sided zero-or-two enumeration gives edge count
exactly four.  The fixed sum twelve therefore forces three distinct
positive disjoint active neighbors in addition to the six meeting
neighbors:

```text
d_{G[X]}(P) >= 9.
```

All other induced degrees are at least six, so the degree sum is at least
`171` and, being even, at least `172`.  The exact spectral upper bound is

```text
2e(G[X]) <= 3(28)+28^2/9 = 1540/9 < 172.
```

Equivalently, the largest even integer permitted by that bound is `170`.
Contradiction.

## 7. Scoped consequence and next residual

All nine admissible profiles are eliminated.  Therefore, under the frozen
audited premises,

```text
n3=57 is impossible.                                   (DERIVED)
```

Because no Wave 17 conclusion was imported, this report alone does not
replace the currently audited lower bound `n3>=54` by `n3>=60`.  Its
standalone residual statement is

```text
n3 is 54, or n3 is at least 60 (with 3 dividing n3).
```

If the separate Wave 17 exclusion of `n3=54` is later accepted, the next
residual is exactly

```text
n3 >= 60,
induced_C6_count = 209286+n3 >= 209346.
```

That prospective combination is recorded as a consequence, not used as a
premise here.

## 8. Reproducibility and retained failure

The checker uses only the Python standard library.  It hashes every frozen
input at startup, enumerates all nine profiles, exhausts the relevant
crossing matrices, enumerates every point-size excess partition at
`m=27,28`, and checks the exact rational spectral bounds.  Ten focused tests
pass, followed by byte-identical JSON replay.

The first execution failed because `point_size_profiles` attempted to
concatenate a generator with a tuple.  Seven tests passed and three errored
with the same `TypeError`; no JSON result was produced.  The failure,
command, stack-trace endpoint, and narrow mechanical repair are retained in
`attempts/wave18-n3-57-structural/failed-runs.md`.  No failed mathematical
lemma was discarded.
