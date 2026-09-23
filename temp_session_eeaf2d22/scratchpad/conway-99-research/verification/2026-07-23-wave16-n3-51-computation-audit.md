# Independent audit: Wave 16 conditional `n3 = 51` computation

```yaml
role: verifier
date_utc: 2026-07-23T11:18:02Z
git_commit: NOT_QUERIED_VERIFIER_FORBIDDEN_FROM_GIT
claim_label: VERIFIED
scope: >
  The conditional active-label profile census, the sixteen-to-seven finite
  branch reduction, the seven exact active-local CNF streams, and the one raw
  positive active-local relaxation candidate. This verdict does not cover an
  n3=51 exclusion, a completed H, a 99-vertex SRG, Conway-99, or novelty.
inputs:
  agents/2026-07-23-wave16-n3-51-computational.md: b3acf2d1efd7940811320e69307810716f2ec7c34c175f3816b104668c7bb0cc
  code/wave16_n3_51_profiles.py: 2bd7874a1819a0bcdaa529ae876fdc6e15a84aa21baddf655a060c6c004d4d4c
  code/wave16_n3_51_active_sat.py: 0cdeab26f21626d4bf6f709e872ce6c3c9df8e4ba6ba48229b7b384e057292da
  code/wave16_n3_51_verify.py: ebebb20a3bdf54e53276d86c96c852bbd5dcbbbaf20b1b8448d5da33af85ce8b
  code/wave16_n3_51_test.py: 4d192543a37fcc59a8c8e3f552e2523ea965e1da3fd93a82b932168b07d20c89
  attempts/wave16-n3-51-computation/n3-51-profile-census.json: f16acb933a6d54e3a96e97521cf3e06b6e04bac06dbf72376fb67a462eec0ffe
  attempts/wave16-n3-51-computation/n3-51-active-local-scan.json: f0345ca8b2ab1591b76b128c4412d35386047b3959e5fcef7a4e7fa2dea16286
  attempts/wave16-n3-51-computation/n3-51-r16-q2x14-q3x2-no-size3-active-local-candidate.json: 96680888b27229819cdc7b59a95558134369f42a32a63925c7653130c28414ef
  attempts/wave16-n3-51-computation/n3-51-run-failures.json: 575bc434fa1e891d7b0159a01b6782ac6c10705fe986b457f3d06773918180ae
  attempts/wave16-n3-51-computation/n3-51-discovery-validation.json: d49b8c4c140a9f6f4682f6de49fcc045833ec3c4fccd2ffe04641a807f211752
method: >
  Pre-inspection freeze; independent fixed-length integer partitioning;
  independent local-state and orbit enumeration; direct proof audit of every
  finite reduction; independent constraint assembly without importing any
  Wave 16 discovery module; exact materialized-DIMACS hashing; raw candidate
  reconstruction; fixed-primary SAT extension; a fresh bounded replay of the
  archived r14 branch; exact provenance and replay checks; and 38 independent
  hostile mutations.
command: |
  $env:PYTHONDONTWRITEBYTECODE='1'
  .venv\Scripts\python.exe -B verification\n3-51-computation\independent_check.py --output verification\n3-51-computation\independent-audit.json
  .venv\Scripts\python.exe -B verification\n3-51-computation\test_independent_check.py -v
  .venv\Scripts\python.exe -B code\wave16_n3_51_profiles.py --output verification\n3-51-computation\regenerated-profile-census.json
  .venv\Scripts\python.exe -B code\wave16_n3_51_verify.py --output verification\n3-51-computation\submitted-validation-replay.json
  .venv\Scripts\python.exe -B code\wave16_n3_51_test.py -v
outputs:
  verification/n3-51-computation/preinspection-freeze.md: d5e894a319a11e4334ba9950fa3c7676d3eee7f0aed6dc61d74cfd71d0e40d8b
  verification/n3-51-computation/independent_check.py: 708190fa6754af97b52ad2a0d2a606cd2e851628eb11ac5b3aae69459b70fb8b
  verification/n3-51-computation/test_independent_check.py: 7f914516583a15fb3675e1f2a11d7df653e10164d8735388f30e609192732011
  verification/n3-51-computation/independent-audit.json: fbb0b17393eacabed38b37644ecc66fca962b00ca8db8b8bb6b35499794084a0
  verification/n3-51-computation/regenerated-profile-census.json: f16acb933a6d54e3a96e97521cf3e06b6e04bac06dbf72376fb67a462eec0ffe
  verification/n3-51-computation/submitted-validation-replay.json: d49b8c4c140a9f6f4682f6de49fcc045833ec3c4fccd2ffe04641a807f211752
limitations: >
  All conclusions are conditional on the inherited active-triangle framework.
  The CNFs omit inactive vertices and point sets, disjoint-point fixed support,
  support-sum equality completion, H, a 99-vertex adjacency matrix, and global
  SRG equations. The archived and replayed raw r14 UNSAT return has no proof
  trace and remains UNSAT_UNVERIFIED. Five timer outcomes remain
  TIMEOUT_UNKNOWN, and the historical preliminary conflict-budget outcome
  remains BUDGET_UNKNOWN. The intermediate source bytes for that historical
  probe are unavailable. The declared starting commit is internally
  consistent but was not authenticated because this verifier was forbidden
  from using Git. Conditional n3=51, Conway-99, and novelty remain UNKNOWN.
```

## Verdict

`PASS_FOR_CONDITIONAL_ACTIVE_LOCAL_ARCHIVE_ONLY`.

The exact limited claims promoted here are:

1. the arithmetic census contains 16 raw profiles and four profiles after the
   inherited minimum-degree and degree-three filters;
2. the stated large-point and rooted-local reductions give a complete
   seven-branch cover of the encoded active-local relaxation;
3. all seven archived DIMACS digests are exact outputs of the stated encoding;
4. the raw `r16-q2x14-q3x2/no-size3` object satisfies every encoded
   high-level constraint and extends the independently rebuilt CNF.

This audit does **not** exclude `n3=51`. It does not imply `n3 >= 54`, and it
does not alter the target or novelty status from `UNKNOWN`.

## Blind freeze and independence

The acceptance contract was written at
`2026-07-23T11:02:53Z`, before reading the discovery report or source. The
independent checker imports the standard library and PySAT, but no
`wave16_n3_51_*` module. It separately constructs the variables, cardinality
constraints, point-family clauses, crossing clauses, overlap witnesses,
degree clauses, branch units, and materialized byte stream.

The verifier used the same declared PySAT sequential-counter primitive to
make exact stream comparison meaningful, while independently assembling the
constraints and independently checking their high-level semantics.

## Arithmetic and finite cover

Fixed-length nondecreasing partitioning of

```text
sum q = 34, q >= 2, 3q <= r-1
```

reproduced all 16 archived profiles byte-for-byte. Recomputing
`d_K = r-1-3q`, handshake parity, `d_K >= 3`, and the inherited
degree-three obstruction leaves exactly:

```text
r17-q2x17
r16-q2x14-q3x2
r15-q2x11-q3x4
r14-q2x8-q3x6
```

For a selected point of size `s >= 4`, the verifier checked that its `2s`
petals have pairwise disjoint external parts and each forces at least `s`
distinct external K-incidences. Hence the forced count is `2s^2`, while the
maximum available count is

```text
s(r-7) - s(s-1) = s(r-s-6).
```

Every expansion-permitted size in the four profiles gives a strict
contradiction. Only sizes two and three remain.

The rooted size-three state table was independently re-enumerated:

| order/root type | labeled states | equal-q orbits |
|---|---:|---:|
| 17/222 | 75 | 21 |
| 16/222 | 32 | 10 |
| 16/223 | 3 | 2 |
| 16/233 | 1 | 1 |
| 15/222 | 8 | 4 |
| 15/223, 233, 333 | 0, 0, 0 | 0, 0, 0 |
| 14/222 | 1 | 1 |
| 14/223, 233, 333 | 0, 0, 0 | 0, 0, 0 |

The verifier also checked:

- odd-order no-triple branches fail incidence parity;
- empty rooted tables remove the claimed root types;
- in the order-14 no-triple branch, the cubic triangle-free point graph gives
  a `q=3` root its three point neighbours plus two distinct distance-two
  K-neighbours, contradicting its K-degree target four;
- choosing a canonical root uses only coordinate relabeling within equal-q
  classes, not a graph automorphism.

These checks reproduce the archived 16 raw branches and exactly seven
survivors.

## Exact formula reconstruction

The independent assembly reproduced every count and materialized DIMACS
SHA-256:

| profile/branch | variables | base clauses | units | DIMACS SHA-256 |
|---|---:|---:|---:|---|
| `r17-q2x17/root-q3x0` | 662354 | 2312884 | 1 | `344f3a6f612f8d9953a7dcd987c12915409cc9b5e2b7fc63400cc11f02737945` |
| `r16-q2x14-q3x2/no-size3` | 472338 | 1645848 | 560 | `ec45a872696abb49c6f168294f5ff5f7f60ba1ddcb9d52d1d627e5b46a3f20e3` |
| `r16-q2x14-q3x2/root-q3x0` | 472338 | 1645848 | 1 | `7ad174733bc95b036d1ab34dc537e04f2e22189c79e8d433fe63226f07d518a5` |
| `r16-q2x14-q3x2/root-q3x1` | 472338 | 1645848 | 1 | `f622aa928be453afd46c3cdb13718f381e0c8063b2094f24ad42f6a138669c58` |
| `r16-q2x14-q3x2/root-q3x2` | 472338 | 1645848 | 1 | `f0a408306ba86e88a9b2a40d47c7eb2e0e9180acb5cada3dabda7d23b7b65fa0` |
| `r15-q2x11-q3x4/root-q3x0` | 337321 | 1159567 | 1 | `9fffa5128566092d63f6195a4fba1e512fc81fdcb8e84888a8c832079193a073` |
| `r14-q2x8-q3x6/root-q3x0` | 239279 | 804058 | 1 | `391fe91f002ff3151caafe8a6f9ef760caa838f617f8c4c93635cd7170f6a883` |

Clause-level review confirmed that the encoding implements:

- exactly three selected points through each active label;
- linear pair ownership and exact `F` ownership;
- selected-point K-cliques and the common-point/Berge-triangle rule;
- the exact singleton-side and `2 x 2` two-sided crossing laws;
- reified full-L overlap caps at selected triples;
- exact profile-specific K-degrees.

The branch units are part of each hashed stream and are the same units passed
as solver assumptions.

## Positive candidate

Raw reconstruction of the archived positive object gives:

```text
profile: r16-q2x14-q3x2
branch: no-size3
selected points: 24, all size two
incidence degrees: 3^16
K edges: 69
K degrees: 9^14, 6^2
meeting crossings checked: 48
linearity/common-point/crossing/overlap-cap violations: 0
semantic SHA-256: d858ceae9ec4f6722c5b73a103bdc68a6b2c55f34db20295ec57b59864896c82
```

Fixing every point and K-edge primary variable from those raw lists makes the
independently rebuilt CNF satisfiable. This verifies a positive assignment
for the encoded active-local relaxation only; it is not a completed graph.

## Solver statuses and failure preservation

The final archive has exactly:

```text
1 SAT_CANDIDATE
5 TIMEOUT_UNKNOWN
1 UNSAT_UNVERIFIED
```

All negative rows say that no proof trace was emitted or checked. Each timeout
row records an enforced fired timer. A fresh 30,000-conflict replay of the
order-14 branch again returned raw UNSAT, but without a proof certificate that
observation remains `UNSAT_UNVERIFIED` and has no nonexistence force.

The historical 10,000-conflict probe is separately retained as
`BUDGET_UNKNOWN`. Its formula digest agrees with the final stream, but its
intermediate builder hash differs from the final source and those intermediate
bytes are unavailable. The archive is internally linked; the historical run
itself cannot be independently authenticated.

## Replays, mutations, and provenance

- The submitted profile generator reproduced the 39,636-byte profile artifact
  exactly: SHA-256 `f16acb933a6d54e3a96e97521cf3e06b6e04bac06dbf72376fb67a462eec0ffe`.
- The submitted validator reproduced its artifact exactly: SHA-256
  `d49b8c4c140a9f6f4682f6de49fcc045833ec3c4fccd2ffe04641a807f211752`.
- The independent audit was run twice and was byte-identical both times:
  SHA-256 `fbb0b17393eacabed38b37644ecc66fca962b00ca8db8b8bb6b35499794084a0`.
- Submitted regression suite: 8/8 tests passed.
- Independent regression suite: 4/4 tests passed.
- Submitted hostile mutations: 20/20 rejected.
- Independent hostile mutations: 38/38 rejected, including self-consistent
  formula-hash forgery and `TIMEOUT_UNKNOWN`/`BUDGET_UNKNOWN` conflation.
- All 13 path hashes declared by the discovery report match current exact
  bytes.

No Git command or Git API was used by this verifier. Therefore the frozen
commit string is cross-artifact-consistent but not authenticated here.

## Recorded execution corrections

The first timestamp command used `Get-Date -AsUTC`, which this Windows
PowerShell version does not support. It was replaced by
`(Get-Date).ToUniversalTime()` before inspection, and the actual freeze time
is recorded. An initial inventory also checked the guessed path
`code/test_wave16_n3_51.py`; the discovery report identifies the actual file
as `code/wave16_n3_51_test.py`, which was then hashed and executed. Neither
correction changed a research artifact or status.
