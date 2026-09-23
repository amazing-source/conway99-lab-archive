# Wave 20 structural discovery at the conditional `n3=63` frontier

Verdict: **conditional `n3=63` is excluded / `DERIVED`, pending a fresh
independent audit.**  The argument uses only the authenticated framework
through Wave 18.  It does not import a Wave 19 conclusion, artifact, search
restriction, or verifier result.

The complete `sum q=42`, `d_K>=4` census has **18**, not two, profiles.  A
first exploratory generator incorrectly returned only the two endpoint
profiles.  That false intermediate claim is prominently retained as
`REJECTED`; the repaired checker caught it before this report was written.
Every restored `r=18,19,20` case is handled explicitly below.

The finite arithmetic leaves no residual: `r<=17` violates the active-set
order bound, while all cases at `r=18,19,20,21` are excluded by exact
inside/outside moments, endpoint-local crossing arithmetic, point linearity,
positive-support handshakes, and one exact projector inequality.

This discovery lane cannot promote its own result to `VERIFIED`.  The
Conway-99 existence target and novelty both remain `UNKNOWN`.

```yaml
role: proof_a
date_utc: 2026-07-23T16:12:28Z
git_commit: NO_GIT
claim_label: DERIVED
scope: >
  Conditional exclusion of project n3=63 for a putative
  srg(99,14,1,2), using only authenticated H/L, indexed-point,
  crossing, fixed-point, and exact spectral premises through Wave 18.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  CONJECTURE.md: 7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58
  verification/2026-07-23-wave15-algebraic-audit.md: b0541d05d2c1c359152b86223e2ebbdbd002b2ff42deb699f6a0b21d149a5b45
  verification/2026-07-23-wave16-n3-51-structural-audit.md: 99203a15db2646a759edbb2241eb4bd5e6001733ac862952c9db57446c58ead6
  verification/2026-07-23-wave18-n3-57-structural-audit.md: 8534456ac92fd704ad7b24f5d7d2c262ea31476132018e9d14a8e4779b27ae5d
method: >
  Enumerate all nondecreasing q-partitions of 42 under d_K>=4;
  enumerate all indexed-point size profiles and all induced-degree
  histograms within the exact subset bound; apply the exact first and
  second outside-neighbor moments and integer convex bounds; then close
  every surviving r,m branch by endpoint-local crossing weights,
  point-linearity, handshake parity, or the exact (-4)-projector PSD
  inequality.
command: |
  .venv\Scripts\python.exe -B -m unittest -v attempts\wave20-n3-63-structural\test_exact_check.py
  .venv\Scripts\python.exe -B attempts\wave20-n3-63-structural\exact_check.py --output attempts\wave20-n3-63-structural\exact-results.json
  .venv\Scripts\python.exe -B attempts\wave20-n3-63-structural\exact_check.py --verify attempts\wave20-n3-63-structural\exact-results.json
outputs:
  attempts/wave20-n3-63-structural/exact_check.py: d88213ede4775548dd2670e593de30e04b724de5cb5efcd15f8c295305dafc12
  attempts/wave20-n3-63-structural/test_exact_check.py: 9e1e9876468c4555334e04342be543a60c3b98577fb216b56dcc3d6eee6e3d41
  attempts/wave20-n3-63-structural/exact-results.json: cd55e820f87501a9e1c6644462aaf114f2b2b8c91438c328146efdf6d8c001da
  attempts/wave20-n3-63-structural/failed-runs.md: 685279b28fcc3479ec08bdc365fdb5ef62423924ee3b848064dd5e664176eb92
  complete_q_profiles: 18
  focused_tests: "14/14 PASS"
  exact_json_replay: PASS_BYTE_IDENTICAL
  conditional_n3_63: EXCLUDED_DERIVED_PENDING_INDEPENDENT_AUDIT
  prospective_next_multiple: 66
  prospective_induced_C6_lower_bound: 209352
  conway_99_target: UNKNOWN
  novelty: UNKNOWN
limitations: >
  This is a conditional theorem over previously audited semantic premises,
  not a raw 99-by-99 adjacency certificate or a formal proof object.  The
  checker verifies finite arithmetic and case coverage but cannot verify its
  own imported graph semantics.  The initially false two-profile census
  demonstrates that profile completeness requires a materially independent
  replay.  No Wave19 result, raw solver status, automorphism assumption,
  catalog non-hit, target resolution, or novelty conclusion is supplied.
```

## 0. Independence boundary and the rejected census

This lane froze the following boundary before deriving the final result:

- use only audited facts available through Wave 18;
- do not assume that `n3=60` has been excluded;
- do not inspect or rely on a Wave 19 discovery package or audit;
- do not use a solver exit status as evidence; and
- keep the target and novelty statuses `UNKNOWN`.

A filename-only repository inventory displayed Wave 19 path names, but no
Wave 19 file supplied a premise, formula, case split, or computation here.

The first bounded exploratory partition routine was defective.  At each
recursion level it replaced the permanent maximum part by

```text
min(permanent_maximum, remaining_total/remaining_parts)
```

and then passed that temporary average bound to deeper levels.  It therefore
silently discarded nonconstant profiles and returned only `r=14,q=3^14` and
`r=21,q=2^21`.  That result was announced provisionally and then withdrawn
when the deterministic checker found 18 rows.

```text
initial two-profile claim: REJECTED / FALSE / NO EVIDENCE
repaired complete census:  DERIVED, independently auditable
```

The exact bug, chronology, and repair are retained in `failed-runs.md`.

## 1. Frozen premises

Assume for contradiction that a putative `srg(99,14,1,2)` has project
parameter `n3=63`.

Let `A` be the active graph-triangle labels, `r=|A|`, and write

```text
q(T)=d_L(T)/3.
```

The authenticated framework supplies:

1. the active arithmetic

   ```text
   sum_T q(T)=2n3/3=42,
   q(T)>=2;
   ```

2. if `K=complement(L[A])`, then

   ```text
   d_K(T)=r-1-3q(T)>=4;
   ```

3. for each original graph vertex `u`, the nonempty indexed active point

   ```text
   S_u={T in A:u in T}
   ```

   has size at least two;
4. the points are linear, every active label occurs in exactly three points,
   and a pair of labels can therefore co-occur in at most one point;
5. each label in `S_u` supplies its two other active-triangle vertices as
   distinct neighbors of `u`, so a point of size `s` has `2s` distinct
   meeting neighbors;
6. for an actual graph edge `uv`, after deleting both copies of a possible
   common label, the crossing between `S_u` and `S_v` has every row and
   column degree zero or two;
7. the fixed-point identity is

   ```text
   sum_{v adjacent to u} d_H(uv)
     =2 sum_{T in S_u}q(T);
   ```

8. with

   ```text
   X={u:S_u is nonempty},  m=|X|,
   ```

   exact incidence gives

   ```text
   sum_{u in X}|S_u|=3r;
   ```

9. the target spectrum gives the subset bound

   ```text
   2e(G[X])<=3m+m^2/9.
   ```

At a size-two point, the crossing law gives zero on a meeting edge and
either zero or four on a disjoint edge.  If its labels have values `a,b`,
the fixed sum is `2(a+b)`.  Therefore:

```text
a+b odd:  impossible;
a+b even: number of positive disjoint neighbors=(a+b)/2,
d_{G[X]}(u)>=4+(a+b)/2.
```

In every valid branch this is at least six.  A point of size at least three
already has at least six meeting neighbors.  Hence

```text
delta(G[X])>=6,
m>=27.                                                   (1)
```

The second inequality is the audited exact spectral consequence.

## 2. Complete `sum q=42` profile census

The repaired fixed-length partition generator keeps the permanent
`d_K>=4` maximum unchanged.  It finds exactly:

| `r` | active `q` multiset | `d_K` multiset | `m<=floor(3r/2)` |
|---:|---|---|---:|
| 14 | `3^14` | `4^14` | 21 |
| 15 | `2^3 3^12` | `8^3 5^12` | 22 |
| 16 | `2^6 3^10` | `9^6 6^10` | 24 |
| 17 | `2^13 4^4` | `10^13 4^4` | 25 |
| 17 | `2^12 3^2 4^3` | `10^12 7^2 4^3` | 25 |
| 17 | `2^11 3^4 4^2` | `10^11 7^4 4^2` | 25 |
| 17 | `2^10 3^6 4` | `10^10 7^6 4` | 25 |
| 17 | `2^9 3^8` | `10^9 7^8` | 25 |
| 18 | `2^15 4^3` | `11^15 5^3` | 27 |
| 18 | `2^14 3^2 4^2` | `11^14 8^2 5^2` | 27 |
| 18 | `2^13 3^4 4` | `11^13 8^4 5` | 27 |
| 18 | `2^12 3^6` | `11^12 8^6` | 27 |
| 19 | `2^17 4^2` | `12^17 6^2` | 28 |
| 19 | `2^16 3^2 4` | `12^16 9^2 6` | 28 |
| 19 | `2^15 3^4` | `12^15 9^4` | 28 |
| 20 | `2^19 4` | `13^19 7` | 30 |
| 20 | `2^18 3^2` | `13^18 10^2` | 30 |
| 21 | `2^21` | `14^21` | 31 |

For `r<=17`, incidence gives `m<=25`, contradicting (1).  It remains to
analyze `r=18,19,20,21`.

## 3. Exact point-size and outside-moment reduction

Let

```text
D=A_{G[X]},
d_u=d_{G[X]}(u),
a=sum_u d_u=2e(G[X]).
```

For a point of size `s`, the endpoint-local lower bound is

```text
d_u>=6  if s=2,
d_u>=2s if s>=3.                                      (2)
```

If `c_y` is the number of neighbors in `X` of an outside vertex `y`, then
`A^2=12I-A+2J` gives the exact moments

```text
sum_y c_y       =14m-a,
sum_y c_y^2     =12m-a+2m^2-sum_u d_u^2.              (3)
```

For `N=99-m` nonnegative integer outside degrees of sum `S`, write
`S=bN+t`, `0<=t<N`.  Convexity gives the exact integer minimum

```text
sum_y c_y^2 >=(N-t)b^2+t(b+1)^2.                      (4)
```

The checker enumerates every point-size partition, every degree histogram
allowed by (2), `d_u<=14`, and the exact subset upper bound, and then applies
(3)--(4), the corresponding bounded maximum, and square/sum parity.

The resulting necessary boundary is:

| `r` | `m` | raw size profiles | surviving size profiles | degree-state summary |
|---:|---:|---:|---|---|
| 18 | 27 | 1 | `2^27` | `6^27` |
| 19 | 27 | 3 | `2^24 3^3` | `6^27` |
| 19 | 28 | 1 | `2^27 3` | `6^28` |
| 20 | 27 | 11 | `2^21 3^6` | `6^27` |
| 20 | 28 | 5 | `2^24 3^4` | `6^28` |
| 20 | 29 | 2 | `2^28 4`; `2^27 3^2` | one state; four states |
| 20 | 30 | 1 | `2^30` | 13 states |
| 21 | 27 | 30 | `2^18 3^9` | `6^27` |
| 21 | 28 | 15 | `2^21 3^7` | `6^28` |
| 21 | 29 | 7 | `2^25 3^3 4`; `2^24 3^5` | one state; four states |
| 21 | 30 | 3 | all three | 1, 9, and 13 states |
| 21 | 31 | 1 | `2^30 3` | 34 states |

The four degree histograms for either all-size-three-excess `m=29` profile
are

```text
6^29,
6^28 8,
6^27 7^2,
6^25 7^4.                                             (5)
```

For `r=20,m=29`, the `2^28 4` profile has only `6^28 8`; for
`r=21,m=29`, the `2^25 3^3 4` profile has only `6^28 8`.

This moment census is a relaxation: it does not assume a point arrangement,
support graph, or common-neighbor completion.  Therefore eliminating a row
is sound, while surviving rows still require semantic analysis.

## 4. Generalized `F/R/Z` reduction

Let `N` be the active-label-by-point incidence matrix.  The meeting graph
`F_X` on point vertices has

```text
A_{F_X}=N^T N-diag(|S_u|),
d_{F_X}(u)=2|S_u|,
|E(F_X)|=3r.
```

Let `R` be the simple graph of actual edges `uv` with positive
`d_H(uv)`.  Attach to each `R`-edge its overlap-deleted labeled crossing
matrix `Z_uv`.  Exact `N3` coverage is

```text
sum_{uv in E(R)} Z_uv = 2A_L.                          (6)
```

Equation (6) is entrywise: every `L` label-pair has exactly its two
independent cross graph-edges, and every `K` pair has zero coverage.

For the small point types that survive:

```text
size 2 against a disjoint point: weight 4;
size 2 against a meeting point:  weight 0;
size 3 against size 2:           weight 0 meeting, 4 disjoint;
size 3 against size 3:           weight 0 or 4 meeting,
                                  weight 0,4,6 disjoint.
```

In an all-`q=2` branch, a size-three point has fixed sum 12, so

```text
4a+6b=12
```

has only

```text
(a,b)=(3,0) or (0,2).                                 (7)
```

Call the weight-six subgraph on size-three points `Z_6`.  Every vertex of
`Z_6` has degree two and no weight-four support edge, so its nonempty
components are simple cycles.  This is the only `Z` refinement needed;
the arithmetic below closes before a catalog or solver is required.

## 5. The four `r=18` profiles

Here `m=27`, every point has size two, and every induced degree is six.
A size-two point with labels `i,j` has at least

```text
4+(q(i)+q(j))/2
```

induced neighbors.  Equality at six forces

```text
q(i)=q(j)=2.
```

Thus no point can contain a label with `q>2`.  Every one of the four
`r=18` profiles has such a label, and every active label must occur in
three points.  Contradiction.

## 6. The three `r=19` profiles

At both possible orders, every size-two point has induced degree six and
therefore contains only `q=2` labels.

### `m=27`

The point sizes are `2^24 3^3`.  Every `q>2` label must place all three of
its occurrences in the three size-three points, hence occurs in all three.
Every `r=19` profile has at least two such labels.  Those two labels would
co-occur in all three large points, violating linearity.

### `m=28`

The point sizes are `2^27 3`.  A `q>2` label cannot occur in a size-two
point, while the unique size-three point supplies at most one of its three
required occurrences.  Contradiction.

## 7. The two `r=20` profiles

The profiles are

```text
2^19 4,
2^18 3^2.
```

For the odd labels, a size-two point containing exactly one `q=3` label is
impossible; a size-two point containing both has induced degree at least
seven.

### `m=27`

The moment row is `2^21 3^6`, with every induced degree six.

For `2^19 4`, the `q=4` label occurs in exactly three of the six large
points.  A special large point has fixed sum 16 and hence positive
meeting degree four among the large points; an ordinary large point has
positive meeting degree three.  This would be a simple graph with degree
sequence

```text
4^3 3^3,
```

whose degree sum is 21.  Contradiction.

For `2^18 3^2`, a large point with exactly one odd label has fixed sum 14,
not divisible by the available meeting weight four.  Therefore the two odd
labels would have to occur together in all three of their occurrence points,
violating linearity.

### `m=28`

The moment row is `2^24 3^4`, again with every induced degree six.

In the `q=4` branch, each of the three special large points needs four
positive large-point neighbors, but only three other large points exist.

In the two-`q=3` branch, fixed-sum parity again forces the two occurrence
sets to coincide in three points, violating linearity.

### `m=29`

There are two moment survivors.

For `2^28 4`, the degree histogram is `6^28 8`.  All size-two points have
degree six, so no special label can occur there.  One size-four point cannot
supply three occurrences of a `q=4` label or of either `q=3` label.

For `2^27 3^2`, consider first the unique `q=4` label.  A size-three point
containing it has fixed sum 16.  A single weight-six crossing cannot be
completed to 16 using weight-four crossings, so it needs four weight-four
edges.  At most one can be a meeting edge to the other large point; at
least three are disjoint, forcing induced degree at least nine.  But every
moment state has maximum degree at most eight.  Thus all three `q=4`
occurrences are size-two points.

Those three special size-two points have positive-support degree three, the
other 24 have degree two, and the two ordinary size-three points each have
positive-support degree three.  A weight-six type is impossible with only
two size-three vertices because it needs two distinct weight-six neighbors.
The positive-support degree sum is therefore

```text
3*3+24*2+2*3=63,
```

contradicting the handshake lemma.

In the two-`q=3` profile, the odd labels can co-occur in at most one
size-two point.  To reach three occurrences each using only two large
points, both labels would have to occur in that size-two point and in both
large points, again violating linearity.

### `m=30`

All 30 points have size two.

For `2^19 4`, three points have positive-support degree three and the other
27 have degree two.  The sum is

```text
3*3+27*2=63,
```

impossible.

For `2^18 3^2`, the two odd labels can share at most one point although
each needs three size-two occurrences.  Contradiction.

## 8. The all-`q=2`, `r=21` profile

Now the incidence sum is 63 and `27<=m<=31`.

### `m=27`

The sole moment survivor is `2^18 3^9`, with every induced degree six.
Each size-three point has no disjoint active neighbor.  Meeting a size-two
point contributes zero, while meeting another size-three point contributes
zero or four.  Its fixed sum 12 therefore requires three positive
size-three meeting neighbors.

This would be a 3-regular graph on nine vertices.  Its degree sum 27 is odd.

### `m=28`

The sole survivor is `2^21 3^7`, again with every induced degree six.
The identical argument requires a 3-regular graph on seven vertices, whose
degree sum 21 is odd.

### `m=29`

The moment survivors are

```text
2^25 3^3 4,
2^24 3^5.
```

For `2^25 3^3 4`, the only degree histogram is `6^28 8`.  The unique
size-four point is saturated by its eight meeting neighbors and has fixed
sum 16.  A meeting size-two point contributes zero; a meeting size-three
point contributes at most four.  It therefore needs four distinct
size-three meeting neighbors, but only three exist.

For `2^24 3^5`, use (7).  If `b` of the five size-three vertices are
weight-six type, they induce a simple 2-regular graph, so

```text
b=0 or b>=3.
```

The 24 size-two vertices contribute positive-support degree 48.  The total
positive-support degree is

```text
48+3(5-b)+2b=63-b.
```

It must be even, so `b` is odd; hence `b=3` or `5`.  Every weight-six type
has two disjoint active neighbors and therefore induced degree at least
eight.  But the four exact moment histograms in (5) have at most one vertex
of degree at least eight.  Contradiction.

### `m=30`

There are three point-size profiles.

For `2^29 5`, all positive crossings at the size-five point have weight
four, so its positive-support degree is five.  The degree sum in `R` is

```text
29*2+5=63,
```

impossible.

For `2^28 3 4`, the sole possible weight-six edge is between the large
points.  It cannot occur because the size-three fixed sum would leave
`12-6=6`, which cannot be assembled from weight-four edges.  All support
weights are therefore four, and

```text
28*2+3+4=63,
```

is again impossible.

For `2^27 3^3`, the no-weight-six branch has degree sum

```text
27*2+3*3=63
```

and is impossible.  If weight six occurs, (7) forces all three large points
to form a weight-six triangle.  They are pairwise disjoint points, hence
the corresponding three original vertices induce a triangle and each has
induced degree at least eight.

Use the exact full-graph projector

```text
M=3I-D+J/9 >= 0,                                      (8)
```

the principal restriction of seven times the `(-4)`-eigenspace projector.
Let `z` be the indicator of the three large vertices.  They induce three
edges.  With `a=sum d_u`, their degree lower bounds give

```text
a>=27*6+3*8=186.
```

Exact arithmetic in (8) gives

```text
z^T M z=4,
1^T M 1=190-a<=4,
z^T M 1<=3*(19/3-8)=-5.
```

Positive-semidefinite Cauchy would require

```text
(z^T M 1)^2 <= (z^T M z)(1^T M 1),
```

but the left side is at least 25 and the right side at most 16.
Contradiction.

### `m=31`

The point sizes are `2^30 3`.  The unique size-three point meets only
size-two points, whose overlap-deleted crossing is zero.  Its fixed sum 12
therefore gives three positive disjoint weight-four edges.  The positive
support degree sum is

```text
30*2+3=63,
```

impossible.

This closes the last profile.

## 9. Scoped consequence

All 18 complete `q`-profiles are excluded under the frozen premises:

```text
conditional n3=63: excluded / DERIVED, pending audit. (9)
```

This report does not assume the exclusion of `n3=60`.  If the earlier
conditional lower bound through 63 is separately verified and integrated,
then divisibility by three would make the next possible value

```text
n3>=66,
induced_C6_count=209286+n3>=209352.
```

Those are prospective combined consequences, not standalone outputs of this
lane.

## 10. Reproducibility, failures, and strongest self-objection

The checker uses only the Python standard library and exact integer or
`Fraction` arithmetic.  It authenticates every frozen input, hard-codes the
complete 18-row `q` census, enumerates all point-size and degree-moment
profiles, checks every displayed handshake, and replays the projector
inequality.  Fourteen focused tests pass; the frozen JSON regenerates
byte-identically.

Retained failures include:

1. the false two-profile census caused by the recursive-bound bug;
2. a naive `q` product that timed out before a complete result;
3. a vertex-by-vertex outside-moment dynamic program that timed out; and
4. an unbounded degree-distribution recursion that timed out.

None supplies evidence.

The strongest objection is **case-completeness plus semantic quantifiers**.
The initial false census shows that a plausible-looking partition list is not
enough.  A fresh verifier should:

1. regenerate the 18 `q` profiles by a materially different algorithm;
2. independently reconstruct every moment row rather than trusting the
   submitted JSON;
3. verify that the overlap-deleted crossing law applies to every actual edge
   used here and that a positive crossing endpoint is active;
4. verify that label occurrence degree three and point linearity justify
   every `q=3` and `q=4` occurrence argument; and
5. rederive the projector sign and coefficient in
   `3I-D+J/9>=0`.

If any of those bridges is weaker than stated, the conditional exclusion
does not follow.  The accompanying checker cannot resolve that objection
because it belongs to the discovery lane.

Final status boundary:

```text
initial two-profile census:              REJECTED / FALSE
complete 18-profile census:              DERIVED
exact point/outside-moment reduction:    DERIVED
r=18,19,20 case exclusions:              DERIVED
r=21, m=27..31 exclusions:               DERIVED
conditional n3=63 exclusion:             DERIVED_PENDING_INDEPENDENT_AUDIT
prospective combined n3 lower bound:     66
prospective combined C6 lower bound:     209352
Conway srg(99,14,1,2):                   UNKNOWN
novelty:                                 UNKNOWN
```
