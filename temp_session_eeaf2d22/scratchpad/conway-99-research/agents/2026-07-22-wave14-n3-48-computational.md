# Wave 14 computational lane: conditional \(n_3=48\)

```yaml
role: construction
date_utc: 2026-07-23T09:04:19Z
git_commit: fd02baec74a5cc19dd415277f9d2504e2d022a9f
claim_label: CANDIDATE
scope: >
  Independent reconstruction of the sum-q=32 active profiles at conditional
  n3=48; exact standard-library flower, crossing, and rooted-local reductions;
  an eleven-branch symmetry-safe PySAT cover of the remaining active-local
  relaxation; one complete positive full-model active-local candidate; and
  two positive weakened controls. This is not a completed 99-vertex search.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  CONJECTURE.md: 7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58
  agents/2026-07-22-wave13-n3-45-proof-a.md: e721614256f003d7266d0b3d1bb2f884febbdec33893f92ed18bf8961c6958e8
  verification/2026-07-22-wave13-n3-45-audit.md: a7e520790680a3cec1d8fcff42db30105572aefeea8a41cf178aaf703147925a
  verification/2026-07-22-wave13-n3-45-audit-b.md: cc1de941e2a4e907a3625bfb9d308d40cc95d084faaa7da567c2c7420817e8e0
  verification/2026-07-22-wave13-computation-audit.md: b1914cd618aea228cf0c442c6e6fa94c00faf241ddd8d787ce7ba0ae91f14fa3
method: >
  Independent integer partitioning; exhaustive standard-library flower words;
  symbolic two-sided crossing checks; rooted t/empty-crossing enumeration;
  deterministic CNF construction; safe equal-q label normalization; bounded
  Glucose 4.2 exploration with exact DIMACS-stream hashes; complete positive
  candidate validation; two positive weakened controls; nine hostile
  mutations; and deterministic formula-hash rebuilds.
command: |
  $env:PYTHONDONTWRITEBYTECODE='1'
  .venv\Scripts\python.exe code\wave14_n3_48_profiles.py --output attempts\wave14-computation\n3-48-profile-census.json
  .venv\Scripts\python.exe code\wave14_n3_48_active_sat.py --scan --solver glucose42 --conflict-budget 30000 --time-limit 5 --scan-output attempts\wave14-computation\n3-48-active-local-scan.json --candidate-dir attempts\wave14-computation
  .venv\Scripts\python.exe code\wave14_n3_48_active_sat.py --controls --solver glucose42 --conflict-budget 50000 --time-limit 10 --control-output attempts\wave14-computation\n3-48-positive-controls.json --candidate-dir attempts\wave14-computation
  .venv\Scripts\python.exe code\wave14_n3_48_verify.py --output attempts\wave14-computation\n3-48-independent-validation.json
  .venv\Scripts\python.exe code\wave14_n3_48_test.py -v
outputs:
  code/wave14_n3_48_profiles.py: fb7c670d0240401929bac609177c83dd618c6baf5969a2e99e6f0dc7ed48f827
  code/wave14_n3_48_active_sat.py: 84e0dcd6cd11f4742abecfe00e1df1ac96047a8967d94f8f5e735d330b4a2ef2
  code/wave14_n3_48_verify.py: 6b2318acc5784290c2f5a32046cd76535bf00db9123b4de4246b882cd2b7c827
  code/wave14_n3_48_test.py: e29999d7485ef3fefc6a32892d2889fd5c1bf6db69733866ea3803ffed0a28ef
  attempts/wave14-computation/n3-48-profile-census.json: c2acf43d29aa08179869a31327991336ac54559fa5ec4915d9f3ea993de7bb5a
  attempts/wave14-computation/n3-48-active-local-scan.json: 4ce53c2fc8a8c0bc005ac1b73dc657ea3c8b7a7f1e3bae1cd73f24de73c539f2
  attempts/wave14-computation/n3-48-r16-q2x16-no-size3-full-candidate.json: b5873ddca8dd92bbcc50fb91b942472f426010264fcfe5599912e178318f4ad5
  attempts/wave14-computation/n3-48-positive-controls.json: db6fb90836dc16440a9e0c73ccff420516af9641e60d6775537f7a695e33ae33
  attempts/wave14-computation/n3-48-r16-q2x16-root-q3x0-no_common_point_control-candidate.json: a5f049c7a7651db6ae8ba5d08cd4d5509814fdcc6202a5080a549acefb0fc024
  attempts/wave14-computation/n3-48-r16-q2x16-no-size3-k_degree_upper_control-candidate.json: 0cb8644bbd6013dbdb1e00657a3cf6a6e9c3a146ad65a43e7270aee6488c1e37
  attempts/wave14-computation/n3-48-independent-validation.json: 20ac2afa64329074677f698331460a27e987ff74527e99ceeee5e5f01fc6d069
  attempts/wave14-computation/n3-48-run-failures.json: 0a4b82afccf09ed26a5dcd34306243723115ff304bbe6f018286c1de141c57b3
  raw_active_profiles: 12
  profiles_after_inherited_filters: 3
  raw_symmetry_cover_branches: 11
  branches_after_exact_finite_reductions: 4
  full_active_local_positive_candidates: 1
  positive_weakened_controls: 2
  proofless_unsat_returns: 7
  bounded_unknown_returns: 1
  enforced_timeout_unknown_returns: 2
  target_result: UNKNOWN
  novelty: UNKNOWN
limitations: >
  All mathematics is conditional on the audited Wave 6--13 active-triangle
  framework. This lane cannot verify its own new finite reductions or
  candidate. Seven Glucose returns were UNSAT but no proof trace was emitted
  or checked; they are UNSAT_UNVERIFIED and are not evidence. One conflict
  budget and two wall timers ended UNKNOWN. The model omits disjoint-point
  fixed support, inactive vertices, H itself, a 99-vertex adjacency matrix,
  and the global SRG equations. The positive full candidate is an
  active-local relaxation only. No completed-graph automorphism is encoded.
```

The `git_commit` field is the frozen starting commit read before this lane
began. The shared repository advanced concurrently, but this lane did not use
or inspect any other Wave 14 work and made no Git changes.

## Status boundary

This lane has one positive result and several negative exploratory results of
very different evidentiary strength.

- The archived order-sixteen object is a complete finite certificate for the
  explicitly encoded active-local relaxation. A separate standard-library
  validator reconstructs every semantic invariant from its raw point sets and
  \(K\)-edges.
- The seven solver `UNSAT` returns have no checked proof traces and therefore
  have no nonexistence force.
- The finite partition, flower, crossing, parity, and local-state reductions
  are exact executable derivations, but this discovery lane labels them
  `CANDIDATE` pending an independent verifier.

Consequently this report does **not** exclude \(n_3=48\), does not prove
\(n_3\ge51\), and does not change Conway-99 or novelty from `UNKNOWN`.

## Inherited and omitted premises

The computation starts from the audited conditional Wave 6--13 framework:

1. \(H\) has the graph edges as vertices, is triangle-free, and
   \(|E(H)|=n_3\).
2. \(L\) has the graph-triangles as vertices and induced-\(N_3\) side-pairs
   as edges.
3. For every active triangle \(T\),

   ```text
   q(T)>=2,  d_L(T)=3q(T),  sum_T q(T)=2n3/3.
   ```

4. \(K\) is the simple complement of \(L\) on distinct active labels.
5. Every active label lies in exactly three non-singleton indexed point sets;
   the point family is linear and every point is a clique in \(K\).
6. Three indexed points cannot pairwise meet at three different labels.
7. After deleting a common label, every row and column degree of a meeting
   \(L\)-crossing is zero or two.
8. For a point \(P\), full \(2\)-by-\(2\) meeting crossings contribute four
   each to the fixed-point total \(2\sum_{T\in P}q(T)\).

The CNF encodes exact point incidence, point sizes two and three after the
finite flower reduction, linearity, exact point-pair ownership \(F\), point
\(K\)-cliques, the common-point rule, all meeting crossings, the overlap
upper cap, and the profile-specific \(K\)-degrees.

It deliberately does not encode inactive points, which disjoint points are
actual graph neighbours, their fixed-point support, equality completion of
the support sums, the 693-vertex \(H\), a 99-vertex adjacency matrix, or the
global \((99,14,1,2)\) equations.

## Twelve exact active profiles

At \(n_3=48\),

```text
sum_T q(T)=32,  q(T)>=2,  3q(T)<=r-1.
```

Independent nondecreasing partitioning gives exactly:

| \(r\) | active \(q\)-multiset | \(K\)-degree multiset | inherited filter |
|---:|---|---|---|
| 16 | \(2^{16}\) | \(9^{16}\) | survives |
| 15 | \(2^{14}4\) | \(8^{14}2\) | \(d_K<3\) |
| 15 | \(2^{13}3^2\) | \(8^{13}5^2\) | survives |
| 14 | \(2^{12}4^2\) | \(7^{12}1^2\) | \(d_K<3\) |
| 14 | \(2^{11}3^2 4\) | \(7^{11}4^2 1\) | \(d_K<3\) |
| 14 | \(2^{10}3^4\) | \(7^{10}4^4\) | survives |
| 13 | \(2^{10}4^3\) | \(6^{10}0^3\) | \(d_K<3\) |
| 13 | \(2^9 3^2 4^2\) | \(6^9 3^2 0^2\) | \(d_K<3\) |
| 13 | \(2^8 3^4 4\) | \(6^8 3^4 0\) | \(d_K<3\) |
| 13 | \(2^7 3^6\) | \(6^7 3^6\) | verified degree-three obstruction |
| 12 | \(2^4 3^8\) | \(5^4 2^8\) | \(d_K<3\) |
| 11 | \(2\,3^{10}\) | \(4\,1^{10}\) | \(d_K<3\) |

The \(d_K\ge3\) filter uses the three non-singleton point cliques through
each active label. The last order-thirteen row is removed by the already
verified degree-three obstruction. The remaining profile orders are 16, 15,
and 14.

The census semantic digest is

```text
07eb5c0430458adb4e17a00d27b3635d14031d87c185adb48368f56bfb75bd13.
```

## Exact large-point reduction

Expansion gives \(2s\le r-s\), so the maximum point sizes before local
checking are five, five, and four at orders 16, 15, and 14. The programs
enumerate every ordered word of the two petals at each root occurrence.

| profile/root size | total words | capacity-feasible | \(K\)-degree survivors |
|---|---:|---:|---:|
| \(r=16,s=5\) | \(4^{10}=1,048,576\) | 11 | 0 |
| \(r=16,s=4\) | \(3^8=6,561\) | 423 | 16 |
| \(r=15,s=5\) | \(4^{10}=1,048,576\) | 1 | 0 |
| \(r=15,s=4\) | \(3^8=6,561\) | 157 | 0 |
| \(r=14,s=4\) | \(3^8=6,561\) | 45 | 0 |

The only delicate row is order 16, size four. Every one of its sixteen
surviving words has exactly one singleton petal and one size-three petal at
each root. The known \(K\)-neighbours saturate degree nine:

```text
3 other roots + 4 singleton endpoints + 2 based triple endpoints = 9.
```

For a based size-three petal, its two external labels are therefore
\(L\)-adjacent to all three other roots. The meeting crossing is all of
\(K_{3,2}\), with row degrees \((2,2,2)\) but column degrees \((3,3)\).
The two-sided zero-or-two rule rejects all sixteen words. Thus all three
surviving profiles have point sizes only two or three.

## Rooted size-three local states

For a size-three point \(P=\{i,j,k\}\), let \(t_i\) count size-three points
through root \(i\), and let \(z_i\) count its other size-three petals whose
crossing with \(P\) is empty in \(L\). If

```text
d_F(i)=3+t_i,  U=K-E(F),
```

then literal distinct-endpoint forcing gives

```text
d_U(i) >= sum_{j != i} (3-t_j+2z_j).
```

The six external petal parts use \(3+t_i+t_j+t_k\) labels, and the number of
full-\(L\) overlaps is

```text
f=sum_i(t_i-1-z_i),  4f<=2(q_i+q_j+q_k).
```

Exhausting \(t_i\in\{1,2,3\}\) and \(0\le z_i<t_i\) gives:

| profile | root \(q\)-type | labeled states | equal-\(q\) coordinate orbits |
|---|---|---:|---:|
| \(r=16\) | 222 | 32 | 10 |
| \(r=15\) | 222 | 8 | 4 |
| \(r=15\) | 223 | 0 | 0 |
| \(r=15\) | 233 | 0 | 0 |
| \(r=14\) | 222 | 1 | 1 |
| \(r=14\) | 223 | 0 | 0 |
| \(r=14\) | 233 | 0 | 0 |
| \(r=14\) | 333 | 0 | 0 |

Hence no size-three point in either mixed profile can contain a \(q=3\)
label. Two further exact reductions apply:

- the order-fifteen all-size-two branch has total incidence \(45\), impossible
  for size-two points alone; and
- in the order-fourteen all-size-two branch, a \(q=3\) label has three
  neighbours in the cubic triangle-free point graph \(F\). The other two
  \(F\)-neighbours of any one of them are two new forced \(K\)-neighbours,
  giving \(d_K\ge3+2=5>4\).

The raw eleven-branch cover therefore reduces exactly to:

```text
r16-q2x16:          no-size3, root-q3x0
r15-q2x13-q3x2:     root-q3x0
r14-q2x10-q3x4:     root-q3x0
```

These reductions do not assume connectedness, transitivity, or an
automorphism of a completed graph.

## Exact SAT encoding and symmetry boundary

For each profile the formula has variables for all size-two and size-three
point candidates, all \(K\)-edges, the exact point-clique union \(F\), and
reified full-\(L\) overlaps. Sequential counters encode incidence, overlap
caps, and \(K\)-degrees.

| profile | variables | base clauses |
|---|---:|---:|
| \(r=16,2^{16}\) | 469,160 | 1,639,520 |
| \(r=15,2^{13}3^2\) | 326,446 | 1,137,931 |
| \(r=14,2^{10}3^4\) | 227,295 | 780,242 |

The eleven raw branches are a complete cover of this encoded relaxation:
an assignment either has no selected size-three point, or one selected point
has a definite number of \(q=3\) labels. Active labels are arbitrary names,
so the \(q\)-multiset is sorted. For a positive branch, only permutations
inside equal-\(q\) label classes name one selected root. No permutation is
assumed to extend to the original graph.

The formula does not impose any other symmetry constraint.

## Bounded full scan

The clean archived scan used Python 3.13.14, python-sat 1.9.dev7, Glucose
4.2, a 30,000-conflict budget, and an enforced five-second wall timer per
branch.

| profile | branch | result | conflicts | seconds | materialized CNF SHA-256 |
|---|---|---|---:|---:|---|
| \(r16\) | no-size3 | `SAT_CANDIDATE` | 168 | 0.956 | `4f0a295ce08409877efee09f87f1ccaf289ea5fe3014d115a4ef99e3e2b5ebdb` |
| \(r16\) | root-q3x0 | `TIMEOUT_UNKNOWN` | 16,323 | 5.904 | `010481d24a8870fd5918b748f67a71bae0159aaabed5df4d911f3379c828769d` |
| \(r15\) | no-size3 | `BUDGET_UNKNOWN` | 30,041 | 2.532 | `e9d9a23627adaa7d52e630e9477c26ad549b72a9f8057f3d45022821cd7cac78` |
| \(r15\) | root-q3x0 | `TIMEOUT_UNKNOWN` | 24,462 | 5.631 | `54d2c55fb75c51df00db9900245d0aefce058990f0b214498ffd87bc36d6750f` |
| \(r15\) | root-q3x1 | `UNSAT_UNVERIFIED` | 2,683 | 1.334 | `8f4e055f9423431ce3f1aaa9478d534881c681aac97b8deaf5fdf268e06ba514` |
| \(r15\) | root-q3x2 | `UNSAT_UNVERIFIED` | 2,681 | 1.010 | `76d1da14f0a1aae3f063d12161baa4a964535e0cdb21be50067f8dca1a69b656` |
| \(r14\) | no-size3 | `UNSAT_UNVERIFIED` | 2,655 | 0.476 | `197aca54f1dc3362e7cc124628ca54842437d5bf06573d168f649866ca0e6042` |
| \(r14\) | root-q3x0 | `UNSAT_UNVERIFIED` | 14,380 | 2.545 | `8483315145c89d24be050391fa40899a4d7272d0a4c38d4726b1c05a90bac784` |
| \(r14\) | root-q3x1 | `UNSAT_UNVERIFIED` | 223 | 0.365 | `1f9ebed0748cb0304980639ef5c2584c264bf48bb4afa2d6a294858159bb06da` |
| \(r14\) | root-q3x2 | `UNSAT_UNVERIFIED` | 397 | 0.379 | `21b4cacbdf044b18a618eec9f72df71bda29dbbe699867c56d95a93bb986631e` |
| \(r14\) | root-q3x3 | `UNSAT_UNVERIFIED` | 1,018 | 0.522 | `95921cb5b0418a38adef1a49f0288e4cf720e9307d4614d8e439f4817f7659ea` |

The seven `UNSAT_UNVERIFIED` rows do not become evidence merely because
some also have an independent finite reduction. The reduction and solver
status are kept as separate claims. No proof trace field exists in the scan.

The scan semantic digest is

```text
de119937479d4f5c8fe75cab3affe275938c32bdfe660410d7443a0348b0fc7a.
```

## Positive full active-local certificate

The order-sixteen no-size-three branch produced a complete finite object:

```text
16 active labels, all q=2;
24 size-two point sets, giving incidence degree 3 at every label;
no repeated point-pair owner;
the point graph F is cubic and triangle-free;
72 K-edges, degree 9 at every label;
every selected point is a K-clique;
48 meeting crossings checked, 0 violations;
0 common-point/Berge violations;
0 fixed-overlap-cap violations.
```

Its semantic digest is

```text
b533da6c967098ed5ec9afd4d0d4e6166c6082e4bf9de5717f48c7b6835d686a.
```

The independent standard-library validator reconstructs these values only
from the raw point and \(K\)-edge lists; it does not trust the solver's
diagnostic fields. This object proves only that the listed active-local
premises do not themselves exclude \(n_3=48\). It is not an \(H\), not a
partial 99-vertex adjacency matrix, and not a Conway graph.

## Two positive weakened controls

Two deliberately weakened formulas were required to produce assignments
that genuinely violate the omitted premise.

1. Removing the common-point clauses while requiring an unowned
   \(F\)-triangle produced a root-normalized object with 22 points, four of
   size three, exact 9-regular \(K\), valid meeting crossings, valid overlap
   caps, and exactly 11 common-point/Berge violations. Its semantic digest is

   ```text
   00fa2235b5716387a2eb8e57438f078df5361925c83513d767437890285406ff.
   ```

2. Replacing exact \(K\)-degree nine by upper bounds and requiring label zero
   to be deficient produced an all-size-two object with degree sequence

   ```text
   6,9,9,9,9,9,9,8,6,9,5,5,7,9,8,9.
   ```

   All other encoded premise families pass. Its semantic digest is

   ```text
   e918fe1cad2812f5a9c708df63d95e531e1a015d406ba4607293a940170294b5.
   ```

The controls semantic digest is

```text
fb39d2cf7f9b42375eb2bf77f211739c9da61f7f1c1b74d65b12355fc4f89905.
```

## Independent replay and hostile mutations

`wave14_n3_48_verify.py` does not import either discovery module. It
independently reconstructs:

- all twelve partitions and all three inherited-filter survivors;
- the five flower census pairs
  \((11,0),(423,16),(1,0),(157,0),(45,0)\);
- the eight rooted local-state counts;
- the four post-finite-reduction branches;
- every invariant of the full positive candidate and both controls; and
- semantic hashes and status boundaries.

Nine hostile mutations are rejected: claim inflation, target inflation,
duplicate and deleted \(K\)-edges, duplicate points, forged normalization,
forged diagnostics, altered \(q\)-data, and a forged semantic digest.

The formula regression tests rebuild all eleven full CNF hashes and both
control hashes from source. They also fix every archived point and \(K\)-edge
decision back into the relevant CNF and confirm that each positive core
extends to a satisfying assignment of all \(F\), counter, overlap, and control
auxiliaries. All seven focused tests pass:

```text
Ran 7 tests in 23.592s
OK
```

The independent-validation semantic digest is

```text
965e2457c4b1357ded77b370907e0414e730abd310a94fc02754ef8a4416aefa.
```

## Preserved failures

The first short scan launch was killed by the outer five-second command
limit and produced no retained result. A second attempt used CaDiCaL 1.9.5.
Its PySAT wrapper accepted conflict budgets but raised `NotImplementedError`
from both `interrupt()` and `clear_interrupt()`. That run stopped during its
second branch and carries no mathematical weight.

The source now explicitly records whether a requested wall timer is actually
enforceable. The complete archive uses Glucose 4.2, for which the timer was
enforced. Exact failure metadata is retained in
`attempts/wave14-computation/n3-48-run-failures.json`.

## Recommended verifier handoff

The most useful independent checks are:

1. reconstruct the order-sixteen size-four \(K_{3,2}\) crossing argument,
   paying attention to the two-sided crossing rule;
2. reconstruct the rooted local-state inequalities and the four-branch
   post-finite cover;
3. validate the positive order-sixteen certificate from raw lists without
   importing discovery code; and
4. if any negative SAT row is to be used, regenerate it with proof output and
   check that trace independently.

The positive order-sixteen object shows that further work must use premises
outside the current active-local relaxation, such as disjoint-point fixed
support or a stronger global coupling. The correct final status remains:

```text
conditional n3=48 exclusion: UNKNOWN
conditional n3>=51:          NOT CLAIMED
srg(99,14,1,2):              UNKNOWN
novelty:                      UNKNOWN
```
