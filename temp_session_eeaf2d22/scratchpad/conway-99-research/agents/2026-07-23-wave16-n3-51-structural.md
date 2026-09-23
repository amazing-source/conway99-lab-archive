# Wave 16 structural exclusion at the conditional `n3=51` frontier

Verdict: **the conditional case `n3=51` is excluded.**  The exclusion is
`DERIVED_PENDING_INDEPENDENT_AUDIT`, not `VERIFIED`.

Exact profile enumeration leaves four active `q`-profiles.  They have
`14 <= r <= 17`, use only `q=2,3`, and therefore have at most 25 active
original vertices.  Every such vertex nevertheless has at least six
neighbors inside the active set.  This contradicts the independently
audited SRG dense-subset bound, which requires at least 27 vertices.

The new step does **not** assume the Wave 14 identities
`d_H in {0,4}` or `d_R(P)=|P|`.  In fact the latter identity does not
generalize: a size-two point on two `q=3` labels has three, not two,
positive support neighbors.  Only the exact two-sided crossing at an
endpoint of size two is classified.

```yaml
role: proof_a
date_utc: 2026-07-23T10:26:35Z
git_commit: 861cfeb6195b19b08feceff07be88a6ab5093fd4
claim_label: DERIVED
audit_status: DERIVED_PENDING_INDEPENDENT_AUDIT
scope: conditional exclusion of n3=51 for a putative srg(99,14,1,2)
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  CONJECTURE.md: 7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58
  verification/2026-07-22-n3-count-bound-audit.md: 773321e8b9934d658f810c6c2eef0e00a339414d98be330ca273d3f9b8bd7753
  verification/2026-07-22-n3-side-incidence-audit.md: 9b6ff3cc9ec8bec13ffd93a8abe0bf0f35398c99f676d00064d6bf5fe6db6787
  verification/2026-07-22-wave12-n3-42-premise-audit.md: abc6be22f73735e2e46c3c59cbb3b15665b9b639db4b263b59a3c50515ba13a2
  verification/2026-07-22-wave12-integration-audit.md: 90021fc6f29cfc4ac0d3df07769ce43b4f270a99a13784ff7491711d15352e70
  verification/2026-07-22-wave13-n3-45-audit.md: a7e520790680a3cec1d8fcff42db30105572aefeea8a41cf178aaf703147925a
  verification/2026-07-23-wave15-global-lift-audit.md: edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036
historical_provenance:
  discovery_wave15_audit_path: verification/2026-07-23-wave15-global-lift-audit.md
  discovery_wave15_audit_transient_sha256: d5e931284407a2071eaf1e6523aac045c96df0b212c946cd4e9b074b9cf41191
  discovery_wave15_audit_transient_bytes_publicly_recoverable: false
  failed_discovery_baseline_commit: 09c20e6c8774ff8676de789b631fd7b0973cf1f5
  public_replay_input_reaudited: true
method: exact q-profile enumeration, audited point-degree filter, complete size-two crossing classification, fixed-point support count, and the audited SRG spectral subset bound
command: |
  .venv\Scripts\python.exe -B attempts\wave16-n3-51-structural\exact_check.py --verify attempts\wave16-n3-51-structural\exact-checks.json
  .venv\Scripts\python.exe -B attempts\wave16-n3-51-structural\test_exact_check.py
outputs:
  attempts/wave16-n3-51-structural/exact_check.py: 5aef211ea7d457543fc3f494eea125bbd0fd6fae2533fd566b475ff3f971c5cf
  attempts/wave16-n3-51-structural/test_exact_check.py: 4fbb3199e49a4d393eb6a434445b84a999eada8adbc801eff1557a36ea707a17
  attempts/wave16-n3-51-structural/exact-checks.json: 7419a54effd68d6853e787616a82dc618163d472d8969772cd2e6220b336ab24
  exact_checker: PASS
  focused_tests: "8/8 PASS"
  conditional_n3_51: EXCLUDED_DERIVED_PENDING_INDEPENDENT_AUDIT
  prospective_conditional_n3_lower_bound: 54
  prospective_conditional_induced_C6_lower_bound: 209340
  conway_99_target: UNKNOWN
  novelty: UNKNOWN
limitations: conditional on the explicitly audited H/L/point/crossing framework and dense-subset lemma; the discovery lane cannot verify its own local-to-global bridge; the finite checker accompanies rather than replaces the human proof; no construction, unconditional Conway-99 result, formal proof object, or novelty conclusion is claimed
```

The commit value was read directly from `.git/HEAD` and its ref file before
this report was written; no Git command was run.  The shared branch may have
moved since that observation.  This lane made no Git changes and did not
inspect any sibling Wave 16 work.

### Public-input provenance repair

The discovery lane originally read a transient, uncommitted Wave 15 audit
whose SHA-256 was
`d5e931284407a2071eaf1e6523aac045c96df0b212c946cd4e9b074b9cf41191`.
Those exact bytes were replaced during Wave 15's public-provenance repair and
are no longer available as a standalone artifact. Baseline commit `09c20e6`
preserves this report with that historical hash in the `inputs` map.

For reproducible public replay, the current `inputs` map instead pins the
final published Wave 15 audit at
`edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036`.
The fresh independent Wave 16 re-audit records both hashes, also preserves the
first verifier's intermediate uncommitted hash, and reconstructs the subset
lemma and the full Wave 16 argument from the final public input. This repair
changes report metadata and its file hash only; it changes no premise used in
the proof, derivation, checker output, bound, or status label.

## 1. Imported audited premises

Assume that `G` is an `srg(99,14,1,2)` and that `n3=51`.  Only the following
previously audited facts are imported.

1. `H` has the graph edges of `G` as vertices and its edges correspond
   bijectively to induced `N3` copies.
2. `L` is the graph on graph-triangles whose edges are the two side
   triangles of an induced `N3`.  If

   ```text
   q(T)=d_L(T)/3,
   ```

   then `q(T)=0` or `q(T)>=2`, and

   ```text
   sum_T q(T)=2n3/3.
   ```

3. Let `A` be the active triangles, `r=|A|`, and
   `K=complement(L[A])`.  For each original vertex `u`,

   ```text
   S_u={T in A : u in T}.
   ```

   The nonempty indexed point sets `S_u` have size at least two, are cliques
   in `K`, and form a linear family.  Each active label lies in exactly three
   point sets.  Three point sets cannot pairwise meet at three distinct
   labels.
4. For an actual graph edge `uv`, delete the two copies of the possible
   common label from the labeled `L`-crossing between `S_u` and `S_v`.
   Every remaining row and column has degree zero or two, and

   ```text
   d_H(uv)=e_L(S_u,S_v),
   sum_{v:uv in E(G)} d_H(uv)=2 sum_{T in S_u}q(T).       (1)
   ```

5. If `X` is an induced vertex set in `G` with minimum internal degree at
   least six, then

   ```text
   |X|>=27.                                               (2)
   ```

Premise 5 was independently audited in Wave 15 by both a spectral proof and
an outside-vertex second-moment proof.  No Wave 14 residual classification,
point-size upper bound, support graph, candidate, solver result, or
automorphism is imported here.

## 2. Exact active `q`-profiles

At `n3=51`,

```text
sum_T q(T)=34,  q(T)>=2,  3q(T)<=r-1.                   (3)
```

The final inequality is `d_L(T)<=r-1`.  Since `q>=2`, also `r<=17`.
Nondecreasing integer partitioning gives exactly sixteen raw profiles:

| `r` | `q` multiset | `K`-degree multiset |
|---:|---|---|
| 12 | `2^2 3^10` | `5^2 2^10` |
| 13 | `2^9 4^4` | `6^9 0^4` |
| 13 | `2^8 3^2 4^3` | `6^8 3^2 0^3` |
| 13 | `2^7 3^4 4^2` | `6^7 3^4 0^2` |
| 13 | `2^6 3^6 4` | `6^6 3^6 0` |
| 13 | `2^5 3^8` | `6^5 3^8` |
| 14 | `2^11 4^3` | `7^11 1^3` |
| 14 | `2^10 3^2 4^2` | `7^10 4^2 1^2` |
| 14 | `2^9 3^4 4` | `7^9 4^4 1` |
| 14 | `2^8 3^6` | `7^8 4^6` |
| 15 | `2^13 4^2` | `8^13 2^2` |
| 15 | `2^12 3^2 4` | `8^12 5^2 2` |
| 15 | `2^11 3^4` | `8^11 5^4` |
| 16 | `2^15 4` | `9^15 3` |
| 16 | `2^14 3^2` | `9^14 6^2` |
| 17 | `2^17` | `10^17` |

Here an active label of value `q` has

```text
d_K=r-1-3q.                                              (4)
```

The three non-singleton point sets through an active label supply three
distinct `K`-neighbors, so `d_K>=3`.  The general repeated-degree-three
lemma audited in Wave 13 excludes equality.  For completeness, if
`N_K(x)={a,b,c}`, the three points through `x` must be

```text
{x,a}, {x,b}, {x,c}.
```

The other two points through `a` have disjoint nonempty external parts.  A
singleton-side labeled crossing with `{x,a}` is empty, so those external
labels must be `K`-neighbors of `x`; only `b,c` are available.  This forces
the point `{a,b}` (and similarly the remaining pairs), while
`{x,a},{x,b},{a,b}` meet pairwise at the three distinct labels `x,a,b`,
contrary to the audited point-family rule.

Thus every active label has `d_K>=4`.  Four profiles survive:

| `r` | `q` multiset | `K`-degree multiset |
|---:|---|---|
| 14 | `2^8 3^6` | `7^8 4^6` |
| 15 | `2^11 3^4` | `8^11 5^4` |
| 16 | `2^14 3^2` | `9^14 6^2` |
| 17 | `2^17` | `10^17` |

In particular every surviving active label has `q` equal to two or three.
The finite checker reconstructs all sixteen raw rows and the exact four-row
filter from (3)-(4).

## 3. The active set has at most 25 original vertices

Let

```text
X={u in V(G): S_u is nonempty}.
```

The points are indexed by original vertices; they are not quotient objects.
Every active graph-triangle has three original vertices and hence occurs in
exactly three indexed points.  Therefore

```text
sum_{u in X}|S_u|=3r.                                   (5)
```

Every summand is at least two, giving

```text
|X|<=floor(3r/2).
```

For the four surviving profiles the respective upper bounds are

```text
r:       14  15  16  17
|X| <=:  21  22  24  25.                               (6)
```

This uses no assertion that point sizes are only two or three.  Points of
any size at least three will already have enough triangle neighbors for the
next step.

## 4. Exact size-two crossing lemma

Fix a size-two active point

```text
P=S_u={i,j}.
```

For any graph neighbor `v` of `u`, write `Q=S_v`.

- If `Q` is empty, the crossing is empty.
- If `P` and `Q` share an active label, linearity says they share only one.
  Delete the common labeled copies.  The `P` side then has one row.  A
  nonzero row would have two entries, but the corresponding columns would
  each have degree one.  The two-sided zero-or-two rule therefore makes the
  crossing empty.
- If `P` and `Q` are disjoint, the crossing has two rows.  If it is nonempty,
  a nonzero column must meet both rows.  A nonzero row has exactly two
  entries, so exactly two columns are selected and the crossing is a
  `K_(2,2)` with four edges.

Consequently every actual edge incident with `u` satisfies the
endpoint-specific conclusion

```text
d_H(uv) in {0,4}.                                        (7)
```

This is **not** a claim that all vertices of `H` have degree zero or four.
The checker exhausts all admissible one-row crossings of widths zero through
sixteen and all two-row crossings of widths two through seventeen.

Apply the fixed-point identity (1).  In the four surviving profiles,
`q(i),q(j)` lie in `{2,3}`:

| point label types | fixed sum `2(q(i)+q(j))` | conclusion |
|---|---:|---|
| `2,2` | 8 | exactly two positive support neighbors |
| `2,3` | 10 | impossible modulo four |
| `3,3` | 12 | exactly three positive support neighbors |

Thus a size-two point is never mixed.  It has at least two distinct graph
neighbors in `X` with positive `H`-degree.  These are not among its four
active-triangle neighbors: a triangle neighbor shares an active label with
`P`, and the overlap case above has `H`-degree zero.

## 5. Every active vertex has at least six active neighbors

For each label in `S_u`, the two other vertices of that graph-triangle are
neighbors of `u` in `X`.  Different triangles through `u` supply disjoint
pairs: otherwise one edge through `u` would lie in two graph-triangles,
contrary to `lambda=1`.  Hence the active triangles supply exactly

```text
2|S_u|
```

distinct neighbors in `X`.

- If `|S_u|>=3`, this is already at least six.
- If `|S_u|=2` on two `q=2` labels, four triangle neighbors plus the two
  disjoint positive-support neighbors give induced degree at least six.
- If `|S_u|=2` on two `q=3` labels, the corresponding lower bound is seven.
- A mixed size-two point was excluded in Section 4.

Therefore

```text
delta(G[X])>=6.                                          (8)
```

No support graph `R` was introduced, and no multiplicity was treated as a
new vertex: every positive term in (1) belongs to a distinct actual edge
`uv` of the simple graph `G`.

## 6. Dense-subset contradiction

For clarity, the audited dense-subset lemma follows from the exact SRG
matrix equation

```text
A^2=12I-A+2J.
```

The largest restricted eigenvalue is three.  If `m=|X|` and `e=e(G[X])`,
the characteristic-vector bound gives

```text
2e <= 3m+m^2/9.                                          (9)
```

Minimum degree six gives `2e>=6m`, so every nonempty such set satisfies

```text
m>=27.                                                   (10)
```

But (6) gives `m<=25`.  This contradiction excludes every one of the four
surviving profiles and therefore excludes the conditional case `n3=51`.

Subject to independent verification, combining this exclusion with the
audited Wave 15 lower bound `n3>=51`, the inherited divisibility
`3 | n3`, and the exact cycle identity gives

```text
n3>=54,
induced_C6_count=209286+n3>=209340.
```

These prospective bounds remain `DERIVED_PENDING_INDEPENDENT_AUDIT`.
The existence of `srg(99,14,1,2)` and the novelty of the conditional
strengthening remain `UNKNOWN`.

## 7. Failed generalizations and hostile mutations

1. **`d_R(P)=|P|` does not generalize.**  A size-two `q=3,3` point has
   fixed sum twelve and hence three positive four-edge support neighbors.
   Its support degree is three while its point size is two.  The proof uses
   only the lower bound needed for induced degree.
2. **Global `H`-degree `{0,4}` was not established or used.**  Equation (7)
   is endpoint-specific to a size-two point.  Larger endpoints may still
   support crossing sizes six or more.
3. **Mixed `q`-profiles are not themselves contradictory.**  Three of the
   four survivors contain both `q=2` and `q=3`.  Only a size-two point
   containing one of each is impossible; a larger mixed point is allowed and
   already has six triangle neighbors.
4. **The two-sided crossing rule is essential.**  Checking row degrees only
   admits a two-edge `2`-by-`3` crossing.  The exact artifact records
   row-only edge counts `{0,2,4}` versus two-sided counts `{0,4}`.
5. **The repeated-degree-three lemma is essential.**  If `d_K=3` were
   permitted, the additional profiles `r=13, q=2^5 3^8` and
   `r=16, q=2^15 4` would survive the numerical filter.
6. **The no-singleton premise is essential.**  Without it, (5) would not
   imply the upper bound in (6), and singleton vertices would not receive
   six triangle neighbors.

These are counterexamples to weakened proof steps, not counterexamples to
Conway-99.  No non-hit or solver status is used as nonexistence evidence.

## 8. Reproducibility and status boundary

The standard-library checker verifies the sixteen raw profiles, the four
survivors, every relevant one- and two-row crossing width, all size-two
fixed sums, the four active-set bounds, and the hostile mutations.  Its
eight focused tests pass.

The program does not derive the audited `H/L` framework from a raw
99-by-99 adjacency matrix, and it is not an independent verifier.  The
scoped status is:

```text
conditional n3=51 exclusion:          DERIVED_PENDING_INDEPENDENT_AUDIT
prospective conditional n3 bound:     n3>=54
prospective induced C6 bound:          >=209340
srg(99,14,1,2) target:                 UNKNOWN
novelty:                               UNKNOWN
```
