# Wave 34 rooted encoding: Stage 1 clean-room freeze

```yaml
role: verifier
date_utc: 2026-07-24T20:26:52Z
git_commit: 0fa5b8161baf8b2a5404a67051b7d61cbc906da3
git_commit_provenance: >-
  Public base commit frozen by the Wave 34 protocol. Per assignment, the
  verifier did not invoke Git and does not claim to have queried checkout
  state.
claim_label: DERIVED
scope: >-
  Before candidate release, independently specify a complete unrestricted
  labeled Boolean/CNF encoding of the conditional Wave 33 six-block
  srg(99,14,1,2) graph-extension criterion. Freeze primary semantics,
  binary/symmetry/hollow gates, degree/design/coupling/common-neighbor
  equations, deterministic counts, tests, and an independent DIMACS/model-map
  audit plan. Do not solve the criterion.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave34-continuation-protocol.md: 60e6c3aba152e924a51bd2503e82de3d05bb39fada258da4a2796e344ae23cd4
  agents/2026-07-24-wave33-rooted-extension.md: c324dc48f5c7b9524b8b2ac02fae3acb8b9ec342d0a61081ee86ae4771434c0c
  verification/wave33-rooted-extension/comparison-audit.md: fc7abcd53154d4551a5d3d97d38024840b4228195e143559c9e8b46c15644b8a
  verification/wave33-rooted-extension/comparison-results.json: 2e36ecade28bca12d35a963a8c6b52777ac7d766a3c4b3267774000fe2e929fd
  verification/wave33-rooted-extension/independent-results.json: 66cef570dbbb4a86e2a35f780edcfc1873d0ac2c5266f1c2065c902a8f91e778
  verification/wave33-rooted-extension/input-freeze.sha256: 50f3581217cd995fbc704e92cd42a10d7bc4bea9efd14d9c2fc36840c377fb2e
  verification/wave33-rooted-extension/artifact-manifest.sha256: a0cd7d284a23aba5576f2da2a1282c9acb209953c3da5d01e706d793f61d3ea7
method: >-
  Reconstruct the fixed signed-Fano support from seven lines; name every O
  vertex by its support pair and copy; expand all six blocks entrywise; add
  explicit redundant degree/design gates; Tseitin-encode every nonlinear
  product; encode every exact cardinality by a fully equivalent prefix
  threshold recurrence; independently derive family distributions and
  variable/clause counts; test gates and small counters exhaustively.
command: |-
  python -B -m unittest discover -s verification/wave34-rooted-encoding/precomparison -p test_*.py -v
  python -B verification/wave34-rooted-encoding/precomparison/cleanroom_encoding.py --summary
dependencies:
  python: 3.13.14
  external_packages: none
  solver: not invoked
  seed: none
outputs:
  verification/wave34-rooted-encoding/precomparison/cleanroom_encoding.py: b980832fba54b72cba9eae89e1a0dbc2a9570686b0c376ac2adda96fd19880b1
  verification/wave34-rooted-encoding/precomparison/test_cleanroom_encoding.py: 5da6e32245fcf7833a60774994783910196e10fbe89673ec81622605b2503f24
  verification/wave34-rooted-encoding/precomparison/criterion-spec.json: d0d7f056db66425d932708037b8fea57476c14e6811840681a2be82bc4a732b1
  verification/wave34-rooted-encoding/precomparison/count-expectations.json: 60086cbd410a1cbc1eeecb1eeb70aa3faf82dc6b66e413f52d441898af85e66d
  verification/wave34-rooted-encoding/precomparison/count-formulas.md: c9fea494e9669fefe7386937ba32c41fdb57e32a3679a4d3d1abead0bf444cd7
  verification/wave34-rooted-encoding/precomparison/mapping-check-plan.md: 2325e7516594398a5c91d614cb0aadf3ff246476cc8d5692b76005ee10553ed9
  verification/wave34-rooted-encoding/precomparison/limitations.md: fbfa0c3538a6d5e8a94ec86091dcb2782e47301baae9b6b2a7f26547b6700c26
  verification/wave34-rooted-encoding/precomparison/input-freeze.sha256: fbba7461e1f94f1edbfd0bdfd3f011b61879781d6215f5b9a95080183b666593
  verification/wave34-rooted-encoding/precomparison/test-results.txt: 0a5b475393b2e5fc5cdc1a6a265c41f299e0835126bfc5af71dbd1ef147313c2
limitations:
  - This verifier cannot verify its own Stage 1 derivation.
  - Candidate comparison has not started.
  - No DIMACS/map file, SAT model, UNSAT proof, or 99-vertex certificate exists.
  - No solver or large search was run.
  - Counts are translation-specific; semantic equivalence is the Stage 2 gate.
  - The criterion is graph-complete only and does not settle the full endpoint.
```

## 1. Separation and exact domain

Stage 1 did not inspect any Wave 34 discovery report, attempt directory,
candidate source/output, sibling message, or sibling artifact.  Every new byte
is under this `precomparison` directory.

The only primary variables are:

```text
d_{i,j}, 0 <= i < j < 70:  C(70,2) = 2,415 bits;
b_{i,q}, 0 <= i < 70, 0 <= q < 15: 70*15 = 1,050 bits.
```

Thus the raw labeled domain has exactly `3,465` primary bits.  Each `d_{i,j}`
represents both orientations, and every `D_{i,i}` is the fixed zero constant.
There is no automorphism, orbit, transitivity, Cayley, circulant,
outside-vertex symmetry, or fixed-design restriction.

## 2. Fixed labeled support

The seven zero-based Fano lines are

```text
012, 034, 056, 135, 146, 236, 245.
```

Support vertices are `P_0,...,P_6,R_0,...,R_6`; `P_p--R_l` is an edge iff
point `p` is not on line `l`.  An O label `(p,l,c)` occurs once for a support
edge and twice for a support nonedge, in lexicographic order.  This produces
28 unique edge completions and 42 nonedge-copy completions.

The reconstruction checks that `U` is binary, symmetric, hollow and
4-regular; `F` is binary with row weight 10 and column weight 2; and the fixed
`SS` identity holds.  Canonical JSON hashes are:

```text
U:        8e9df095563e6d7a8166a99d60f51c15c4db6b722080fd233146a2aa6626431d
F:        8a4e68fd7bfa97917c74bde2a3ae34d9786ca1f7597b0bb0b3c77c110cfe0756
O labels: 391ca52fb781969d988c8f75eca24da6c131e480f0e6e5a673b83b04ec39bdb1
```

## 3. Complete equation inventory

With

```text
A = [[U,F,0],[F^T,D,B],[0,B^T,0]],
```

the encoding includes:

```text
SS: U^2 + F F^T             = 12I - U + 2J          fixed preflight
SO: U F + F D               = 2J - F                980 entries
SQ: F B                     = 2J                    210 entries
OO: F^T F + D^2 + B B^T     = 12I - D + 2J          70 diag + 2,415 offdiag
OQ: D B                     = 2J - B                1,050 entries
QQ: B^T B                   = 12I + 2J              15 diag + 105 offdiag.
```

The exact-count layer also states explicitly:

```text
sum_j D_ij=9, sum_q B_iq=3, sum_i B_iq=14,
sum_i B_iq B_ir=2 for q!=r.
```

The first three are required degree/row/column gates.  Some are redundant
with the six blocks, which preserves rather than shrinks the criterion.
Distinct B rows need no separate restriction: equal weight-three rows would
already contribute three common Q neighbors to an `OO` off-diagonal equation
whose right side is at most two.

## 4. Nonlinear and cardinality translation

Every conjunction gets a named Tseitin bit and all three clauses for
`z <-> x AND y`.  There are:

```text
164,220 OO D-products
 36,225 OO B-products
 72,450 OQ DB-products
  7,350 QQ B-products
280,245 total product auxiliaries.
```

Each exact count uses equivalence states `T(i,j)` meaning "at least `j` of the
first `i` literals."  Both directions of

```text
T(i,j) <-> T(i-1,j) OR (T(i-1,j-1) AND x_i)
```

are encoded, with terminal units `T(n,k)` and `not T(n,k+1)`.  Hence a decoded
primary assignment uniquely determines all auxiliaries; auxiliaries cannot
silently relax an equation.

## 5. Independent expectations

The full deterministic translation has:

```text
primary variables:        3,465
product auxiliaries:    280,245
cardinality auxiliaries:946,806
total variables:      1,230,516

product clauses:        840,735
cardinality clauses:  3,478,308
total clauses:        4,319,043
```

Its in-memory numeric DIMACS body commitment is

```text
5a98d5d6c505cb89d365bbae4f382c9593f53bdcc64b57ed975122461202a61d.
```

No DIMACS file was emitted.  The body hash is a deterministic Stage 1
expectation, not a solver certificate.

The strongest distribution checks are:

```text
OO offdiag (scope,target,count):
  (84,0,21), (84,1,588), (84,2,1806)

SO (scope,target,count):
  (9,0,56), (9,1,84), (10,1,504), (10,2,336).
```

## 6. Replay, failed routes, and objection

Nine standard-library tests pass in 12.983 seconds.  They freeze all inputs,
reconstruct fixed data, exhaust all truth assignments to the AND gate,
existentially exhaust small exact counters, check the unrestricted primary
layout and all equation-family distributions, match the machine-readable
count snapshot to a fresh build, and reject an all-zero decoded pair in every
variable block while retaining the fixed `SS` pass.

Rejected Stage 1 routes:

- a full ordered `70x70` D variable matrix was unnecessary and would create
  extra symmetry/hollow mapping obligations;
- subset-clause cardinality was exact but impractically explosive;
- a separate B-row-distinct encoding was redundant and risked obscuring the
  actual common-neighbor implication;
- a solver run would violate the Stage 1 boundary and produce no admissible
  conclusion without a frozen proof/checker plan.

The strongest self-objection is that the same verifier authored the
translation and tests, and the 4.3-million-clause stream was counted rather
than emitted and reparsed.  Stage 2 must therefore compare semantics rather
than demand matching auxiliary counts, and independently attack the
candidate's DIMACS/map/model or proof bytes according to
`mapping-check-plan.md`.

## 7. Status wall

```text
Stage 1 clean-room specification: DERIVED and byte-frozen
candidate comparison:             NOT STARTED
binary criterion solution:        UNKNOWN
rooted graph extension/exclusion:  UNKNOWN
rooted endpoint:                   UNKNOWN
n3=708:                            UNKNOWN
Conway-99:                         UNKNOWN
novelty:                           UNKNOWN
```
