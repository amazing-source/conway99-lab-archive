# Wave 16 computational lane: conditional \(n_3=51\)

```yaml
role: construction
date_utc: 2026-07-23T10:40:50Z
git_commit: 861cfeb6195b19b08feceff07be88a6ab5093fd4
claim_label: CANDIDATE
scope: >
  Independent reconstruction of all sum-q=34 active profiles at conditional
  n3=51; a new crossing-degree exclusion of every active point of size at
  least four; an exhaustive rooted size-three local census; a symmetry-safe
  sixteen-to-seven finite branch reduction; seven deterministic active-local
  CNF streams; one complete positive active-local relaxation certificate;
  exact archive replay; and twenty hostile metadata/semantic mutations. This
  is not a completed H search or a 99-vertex graph search.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  CONJECTURE.md: 7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58
  verification/2026-07-22-n3-side-incidence-audit.md: 9b6ff3cc9ec8bec13ffd93a8abe0bf0f35398c99f676d00064d6bf5fe6db6787
  verification/2026-07-22-wave14-n3-48-computation-audit.md: 9a1b3bb8bb0edfdacfac61635b4a2256579fe9a175150589880dadf6a04ae94d
method: >
  Independent nondecreasing integer partitioning; an exact petal-crossing
  K-incidence inequality; exhaustive standard-library local-state
  enumeration; deterministic PySAT sequential-counter CNFs; a complete
  equal-q label-normalized branch cover; bounded Glucose 4.2 exploration
  with enforced wall timers; raw positive certificate export; structural
  replay; fixed-candidate CNF replay; all seven DIMACS-stream hash rebuilds;
  failure preservation; and twenty hostile mutations.
command: |
  $env:PYTHONDONTWRITEBYTECODE='1'
  .venv\Scripts\python.exe code\wave16_n3_51_profiles.py --output attempts\wave16-n3-51-computation\n3-51-profile-census.json
  .venv\Scripts\python.exe code\wave16_n3_51_active_sat.py --scan --solver glucose42 --conflict-budget 30000 --time-limit 5 --candidate-dir attempts\wave16-n3-51-computation --scan-output attempts\wave16-n3-51-computation\n3-51-active-local-scan.json
  .venv\Scripts\python.exe code\wave16_n3_51_verify.py --output attempts\wave16-n3-51-computation\n3-51-discovery-validation.json
  .venv\Scripts\python.exe code\wave16_n3_51_test.py -v
outputs:
  code/wave16_n3_51_profiles.py: 2bd7874a1819a0bcdaa529ae876fdc6e15a84aa21baddf655a060c6c004d4d4c
  code/wave16_n3_51_active_sat.py: 0cdeab26f21626d4bf6f709e872ce6c3c9df8e4ba6ba48229b7b384e057292da
  code/wave16_n3_51_verify.py: ebebb20a3bdf54e53276d86c96c852bbd5dcbbbaf20b1b8448d5da33af85ce8b
  code/wave16_n3_51_test.py: 4d192543a37fcc59a8c8e3f552e2523ea965e1da3fd93a82b932168b07d20c89
  attempts/wave16-n3-51-computation/n3-51-profile-census.json: f16acb933a6d54e3a96e97521cf3e06b6e04bac06dbf72376fb67a462eec0ffe
  attempts/wave16-n3-51-computation/n3-51-active-local-scan.json: f0345ca8b2ab1591b76b128c4412d35386047b3959e5fcef7a4e7fa2dea16286
  attempts/wave16-n3-51-computation/n3-51-r16-q2x14-q3x2-no-size3-active-local-candidate.json: 96680888b27229819cdc7b59a95558134369f42a32a63925c7653130c28414ef
  attempts/wave16-n3-51-computation/n3-51-run-failures.json: 575bc434fa1e891d7b0159a01b6782ac6c10705fe986b457f3d06773918180ae
  attempts/wave16-n3-51-computation/n3-51-discovery-validation.json: d49b8c4c140a9f6f4682f6de49fcc045833ec3c4fccd2ffe04641a807f211752
  raw_active_profiles: 16
  profiles_after_inherited_filters: 4
  raw_symmetry_cover_branches: 16
  branches_after_exact_finite_reductions: 7
  full_active_local_positive_candidates: 1
  proofless_unsat_returns: 1
  enforced_timeout_unknown_returns: 5
  preserved_historical_budget_unknown_returns: 1
  target_result: UNKNOWN
  conditional_n3_51_exclusion: UNKNOWN
  novelty: UNKNOWN
limitations: >
  Every statement is conditional on the previously audited active-triangle
  framework. This construction lane cannot verify its own new large-point
  inequality, finite reductions, formula encoding, or positive candidate.
  The one UNSAT return has no emitted or checked proof trace and has no
  nonexistence force. The five timer returns and preserved earlier budget
  return are UNKNOWN. The CNFs omit inactive vertices, disjoint-point fixed
  support, equality completion of support sums, H, a 99-vertex adjacency
  matrix, and the global SRG equations. The positive object is an
  active-local relaxation only. No automorphism of a completed graph is
  assumed. Conditional n3=51, Conway-99, and novelty remain UNKNOWN.
```

The `git_commit` field is the frozen starting commit read directly from the
shared worktree metadata. The shared repository advanced concurrently. This
lane made no Git changes and did not inspect any sibling Wave 16 work.

## Status boundary

This lane produces two kinds of new output, neither self-verified:

1. The exact arithmetic and finite reductions below are
   `DERIVED_PENDING_AUDIT`.
2. The archived positive assignment is a `CANDIDATE` for the explicitly
   encoded active-local relaxation.

The single solver `UNSAT` return is `UNSAT_UNVERIFIED`; the five final timer
returns are `TIMEOUT_UNKNOWN`; and the preliminary budget return is
`BUDGET_UNKNOWN`. No negative solver status is evidence for nonexistence.

Consequently this report does **not** exclude \(n_3=51\), does not prove
\(n_3\ge54\), and does not change Conway-99 or novelty from `UNKNOWN`.

## Inherited and omitted premises

The lane starts from the audited conditional active-label framework:

1. For every active triangle \(T\),

   ```text
   q(T)>=2,  d_L(T)=3q(T),  sum_T q(T)=2n3/3.
   ```

2. \(K\) is the simple complement of \(L\) on distinct active labels.
3. Every active label lies in exactly three non-singleton indexed point
   sets; the point family is linear and every point is a \(K\)-clique.
4. Three points cannot pairwise meet at three different labels.
5. Every row and column degree of a meeting \(L\)-crossing is zero or two.
6. A full \(2\)-by-\(2\) \(L\)-crossing contributes four to the fixed-point
   total \(2\sum_{T\in P}q(T)\).
7. The expansion bound is \(2|P|\le r-|P|\).
8. The previously verified degree-three obstruction excludes
   \(d_K(T)=3\).

The CNFs deliberately omit inactive point sets and vertices, the identity of
actual graph adjacencies among disjoint points, fixed support contributed by
disjoint points, equality completion of fixed-point support sums, the
693-vertex graph \(H\), a 99-vertex adjacency matrix, and all global
\((99,14,1,2)\) equations.

## Sixteen exact active profiles

At \(n_3=51\),

```text
sum_T q(T)=34,  q(T)>=2,  3q(T)<=r-1,
d_K(T)=r-1-3q(T).
```

Independent nondecreasing partitioning gives exactly sixteen rows:

| \(r\) | active \(q\)-multiset | \(K\)-degree multiset | inherited disposition |
|---:|---|---|---|
| 17 | \(2^{17}\) | \(10^{17}\) | survives |
| 16 | \(2^{15}4\) | \(9^{15}3\) | degree-three obstruction |
| 16 | \(2^{14}3^2\) | \(9^{14}6^2\) | survives |
| 15 | \(2^{13}4^2\) | \(8^{13}2^2\) | \(d_K<3\) |
| 15 | \(2^{12}3^2 4\) | \(8^{12}5^2 2\) | \(d_K<3\) |
| 15 | \(2^{11}3^4\) | \(8^{11}5^4\) | survives |
| 14 | \(2^{11}4^3\) | \(7^{11}1^3\) | \(d_K<3\) |
| 14 | \(2^{10}3^2 4^2\) | \(7^{10}4^2 1^2\) | \(d_K<3\) |
| 14 | \(2^9 3^4 4\) | \(7^9 4^4 1\) | \(d_K<3\) |
| 14 | \(2^8 3^6\) | \(7^8 4^6\) | survives |
| 13 | \(2^9 4^4\) | \(6^9 0^4\) | \(d_K<3\) |
| 13 | \(2^8 3^2 4^3\) | \(6^8 3^2 0^3\) | \(d_K<3\) |
| 13 | \(2^7 3^4 4^2\) | \(6^7 3^4 0^2\) | \(d_K<3\) |
| 13 | \(2^6 3^6 4\) | \(6^6 3^6 0\) | \(d_K<3\) |
| 13 | \(2^5 3^8\) | \(6^5 3^8\) | degree-three obstruction |
| 12 | \(2^2 3^{10}\) | \(5^2 2^{10}\) | \(d_K<3\) |

Every degree sum is even. The four surviving profile orders are 17, 16, 15,
and 14. The profile semantic digest is

```text
17413e627975c24b40c01132ea5276e7e533120f00467ca2217b574bf7d9651b.
```

## New large-point obstruction

This lane found a short general reduction for the four surviving profiles.
Let \(P\) be a selected point of size \(s\ge4\). Each root label has two other
points, so \(P\) has \(2s\) petals. Their nonempty external parts are pairwise
disjoint by linearity and the common-point rule.

Consider a petal with \(t\) external labels. There are \(st\) pairs between
\(P\) and its external part. If \(t=1\), the singleton-side crossing is empty
in \(L\), so all \(s\) pairs are in \(K\). If \(t\ge2\), every external
column has \(L\)-degree at most two, so the crossing has at most \(2t\)
\(L\)-edges. It therefore contributes at least

\[
st-2t=(s-2)t\ge s
\]

distinct \(K\)-incidences from \(P\). All \(2s\) petals together force at
least \(2s^2\) external \(K\)-incidences.

The root clique already consumes \(s(s-1)\) degree-incidences. Since
\(q\ge2\), every root has \(d_K\le r-7\). The maximum remaining external
capacity is therefore

\[
s(r-7)-s(s-1)=s(r-s-6).
\]

The exact worst-case comparisons are:

| profile order | point size | forced external \(K\)-incidence | maximum available |
|---:|---:|---:|---:|
| 17 | 4 | 32 | 28 |
| 17 | 5 | 50 | 30 |
| 16 | 4 | 32 | 24 |
| 16 | 5 | 50 | 25 |
| 15 | 4 | 32 | 20 |
| 15 | 5 | 50 | 20 |
| 14 | 4 | 32 | 16 |

The expansion bound permits no larger sizes. Thus every selected active point
has size two or three. This argument uses no connectedness, transitivity, or
completed-graph automorphism. It is `DERIVED_PENDING_AUDIT`.

## Rooted size-three census

For a selected triple \(P=\{i,j,k\}\), let \(t_i\) count selected triples
through \(i\), including \(P\), and let \(z_i\) count its other triple petals
whose crossing with \(P\) is empty in \(L\). The exhaustive census uses

```text
3+t_i+t_j+t_k <= r-3,
d_U(i) <= d_K(i)-(3+t_i),
d_U(i) >= sum_{j != i}(3-t_j+2z_j),
4*sum_i(t_i-1-z_i) <= 2*(q_i+q_j+q_k).
```

The exact labeled counts and equal-\(q\) coordinate orbit counts are:

| profile | root \(q\)-type | labeled states | equal-\(q\) orbits |
|---|---|---:|---:|
| \(r=17,2^{17}\) | 222 | 75 | 21 |
| \(r=16,2^{14}3^2\) | 222 | 32 | 10 |
|  | 223 | 3 | 2 |
|  | 233 | 1 | 1 |
| \(r=15,2^{11}3^4\) | 222 | 8 | 4 |
|  | 223 | 0 | 0 |
|  | 233 | 0 | 0 |
|  | 333 | 0 | 0 |
| \(r=14,2^8 3^6\) | 222 | 1 | 1 |
|  | 223 | 0 | 0 |
|  | 233 | 0 | 0 |
|  | 333 | 0 | 0 |

The raw sixteen-branch cover consists of a no-triple branch plus one branch
for each possible \(q=3\) multiplicity of a selected triple. The following
exact reductions leave seven branches:

- the no-triple branches at odd orders 17 and 15 fail incidence parity;
- the empty local tables remove every \(q=3\)-containing root at orders 15
  and 14; and
- in the order-14 no-triple branch, a \(q=3\) label has a cubic
  triangle-free point graph, whose first and second neighbourhoods force
  five distinct \(K\)-neighbours above its target degree four.

The surviving cover is:

```text
r17-q2x17:          root-q3x0
r16-q2x14-q3x2:     no-size3, root-q3x0, root-q3x1, root-q3x2
r15-q2x11-q3x4:     root-q3x0
r14-q2x8-q3x6:      root-q3x0
```

Only permutations within equal-\(q\) classes name a selected root. No
permutation is asserted to extend to an automorphism of the original graph.

## Exact active-local encoding

For each surviving profile, the CNF contains:

- one selection variable for every two- and three-subset;
- one \(K\)-edge and one exact point-owned \(F\)-edge variable per pair;
- incidence exactly three at each label and linear pair ownership;
- selected-point \(K\)-cliques;
- the common-point rule as “every \(F\)-triangle is its selected triple”;
- exact singleton-side and \(2\)-by-\(2\) meeting-crossing rules;
- reified full-\(L\) overlap caps at selected triples; and
- exact profile-specific \(K\)-degrees.

Branch units are appended to the deterministic materialized DIMACS stream.
The bounded final scan used Python 3.13.14, python-sat 1.9.dev7, Glucose 4.2,
a 30,000-conflict budget, and an enforced five-second wall timer per branch.

| profile | branch | raw status | variables | base clauses | units | DIMACS SHA-256 |
|---|---|---|---:|---:|---:|---|
| \(r17,2^{17}\) | root-q3x0 | `TIMEOUT_UNKNOWN` | 662,354 | 2,312,884 | 1 | `344f3a6f612f8d9953a7dcd987c12915409cc9b5e2b7fc63400cc11f02737945` |
| \(r16,2^{14}3^2\) | no-size3 | `SAT_CANDIDATE` | 472,338 | 1,645,848 | 560 | `ec45a872696abb49c6f168294f5ff5f7f60ba1ddcb9d52d1d627e5b46a3f20e3` |
| \(r16,2^{14}3^2\) | root-q3x0 | `TIMEOUT_UNKNOWN` | 472,338 | 1,645,848 | 1 | `7ad174733bc95b036d1ab34dc537e04f2e22189c79e8d433fe63226f07d518a5` |
| \(r16,2^{14}3^2\) | root-q3x1 | `TIMEOUT_UNKNOWN` | 472,338 | 1,645,848 | 1 | `f622aa928be453afd46c3cdb13718f381e0c8063b2094f24ad42f6a138669c58` |
| \(r16,2^{14}3^2\) | root-q3x2 | `TIMEOUT_UNKNOWN` | 472,338 | 1,645,848 | 1 | `f0a408306ba86e88a9b2a40d47c7eb2e0e9180acb5cada3dabda7d23b7b65fa0` |
| \(r15,2^{11}3^4\) | root-q3x0 | `TIMEOUT_UNKNOWN` | 337,321 | 1,159,567 | 1 | `9fffa5128566092d63f6195a4fba1e512fc81fdcb8e84888a8c832079193a073` |
| \(r14,2^8 3^6\) | root-q3x0 | `UNSAT_UNVERIFIED` | 239,279 | 804,058 | 1 | `391fe91f002ff3151caafe8a6f9ef760caa838f617f8c4c93635cd7170f6a883` |

The exact final status histogram is:

```text
1 SAT_CANDIDATE
5 TIMEOUT_UNKNOWN
1 UNSAT_UNVERIFIED
```

The failure archive also retains the preliminary 10,000-conflict
`BUDGET_UNKNOWN` probe of the last branch. Its CNF digest agrees with the
final stream. No proof trace was emitted or checked in any negative run.

## Positive active-local certificate

The positive certificate has semantic digest

```text
d858ceae9ec4f6722c5b73a103bdc68a6b2c55f34db20295ec57b59864896c82.
```

Raw reconstruction gives:

- profile \(r=16,\ q=2^{14}3^2,\ d_K=9^{14}6^2\);
- 24 selected size-two points and no selected triples;
- incidence degree three at all sixteen labels;
- a linear 24-edge cubic point graph \(F\) with no triangle;
- 69 \(K\)-edges with exact target degrees;
- all selected-point clique edges present;
- 48 meeting crossings checked with no violation;
- no common-point/Berge-triangle or overlap-cap violation; and
- all point and \(K\)-edge decisions extend to a satisfying assignment of
  the archived CNF.

This is a complete certificate only for the encoded active-local relaxation.
It contains no inactive structure, \(H\), adjacency matrix, or global SRG
completion, and is not a construction or counterexample for Conway-99.

## Replay, provenance, and hostile mutations

The discovery-side validator independently re-enumerates the sixteen
partitions and rooted local-state counts, checks every large-point
degree-sum comparison, validates the positive object from its raw point and
\(K\)-edge lists, fixes those decisions back into the CNF, rebuilds all seven
formula streams and hashes, binds the failure archive to the final scan, and
checks every declared source and candidate hash.

Twenty hostile changes are rejected:

- claim, target, conditional-target, novelty, and scope inflation;
- duplicate or deleted points and \(K\)-edges;
- altered \(q\)-data, forged symmetry text, deleted premises, diagnostics,
  formula digest, and semantic digest;
- scan claim inflation, negative-result promotion, forged proof checking,
  duplicate branches, and candidate-path redirection.

The validator passes. The focused regression suite also passes:

```text
Ran 8 tests in 19.548s
OK
```

This replay remains a discovery-side check, not the independent verifier
required to promote any new reduction or certificate.

## Precise residual handoff

An independent verifier should attack the following in order:

1. Re-derive the \(2s^2>s(r-s-6)\) large-point contradiction directly from
   the inherited crossing and petal-disjointness premises.
2. Independently enumerate the local table
   `75, 32, 3, 1, 8, 0, 0, 0, 1, 0, 0, 0`.
3. Reconstruct the sixteen-to-seven branch reduction without importing the
   discovery modules.
4. Rebuild all seven CNFs independently and compare the materialized hashes.
5. Validate the positive \(r=16\) raw object and fix it into the rebuilt CNF.
6. Keep the proofless order-14 `UNSAT` and all timeout/budget rows
   non-evidentiary.

After those checks, the unresolved conditional frontier is exactly the seven
active-local branches displayed above together with all omitted inactive,
fixed-support, \(H\), and global SRG completion constraints.
