# Wave 34 rooted complete-domain encoding comparison audit

Verdict: **the candidate is independently VERIFIED as an exact,
complete-domain, no-symmetry-breaking CNF encoding of the conditional Wave 33
six-block graph criterion; this does not determine satisfiability**

```yaml
role: verifier
date_utc: 2026-07-24T20:53:21Z
git_commit: 79a11c6121c53155ac5a18dea391be7b8bd619b7
git_commit_provenance: >-
  Public candidate commit released to the verifier by the orchestrator. Per
  assignment, the verifier did not invoke Git and does not claim a separate
  checkout-state query.
claim_label: VERIFIED
scope: >-
  Independently compare the byte-frozen Stage-1 criterion with the released
  Wave 34 candidate; bind its signed-Fano coordinates to the exact Wave 33
  labeling; validate manifests, gzip, ordered-D gates, every semantic family,
  every product/cardinality gadget, all variable allocation and clause bytes,
  model decoding, witness-checker route, no-symmetry scope, and
  complete-domain equivalence. This status is encoding-only.
inputs:
  verification/wave34-rooted-encoding/precomparison/artifact-manifest.sha256: 3f1bdcb0ca2d08ee0380cd1435673fddb499db8c3a8273f6676c18f17ad3550c
  verification/wave34-rooted-encoding/candidate-release.md: 023088f9a1e4e21929a9d1c5666f2ce3ac3b757e93491d67a3b37f9a8338fa80
  attempts/wave34-rooted-encoding/publication-manifest.sha256: 7cba8a082545cbfcbf01785e6e15a0198bd1cf2357ed0a2b3f353b564a1433e7
  attempts/wave34-rooted-encoding/artifact-manifest.sha256: e96036e97884f0bbc19c30073dbe295852117e9d4d54892cf5e57b20e6f6ec05
  attempts/wave34-rooted-encoding/correction-ledger.md: 6daaa2c49cda2ca9e254210ebe64e493cf66cc66510ed6a711251e40e507ff0d
  .gitattributes: 3b5a883d038c4a3377a8b237ed0180e4f1d80423e987d13682dde670c92614bd
method: >-
  Use a verifier-owned standard-library implementation that imports and
  executes no candidate generator code. Reconstruct canonical labels,
  primary and auxiliary semantics, all exact equation scopes, every Tseitin
  and threshold clause, and the complete numeric DIMACS stream. Compare each
  line byte-for-byte; independently decompress gzip; use synthetic signature
  models only to test the released decoder/checker mapping.
command: |-
  python -B verification/wave34-rooted-encoding/independent_compare.py --output verification/wave34-rooted-encoding/comparison-results.json
  python -B -m unittest discover -s verification/wave34-rooted-encoding -p test_independent_compare.py -v
dependencies:
  python: 3.13.14
  external_packages: none
  seed: none
  candidate_generator_imported: false
  candidate_generator_executed: false
  large_solver_executed: false
  proof_checker_executed: false
outputs:
  verification/wave34-rooted-encoding/independent_compare.py: 43d118d5bc0583491d6b226828b3f319eae62b9bc27ed0614dcde8ed53489b61
  verification/wave34-rooted-encoding/test_independent_compare.py: e58eccfc7babe7de36a35208993d0da4035f234906ac30d7e04ae7458c3f801a
  verification/wave34-rooted-encoding/comparison-results.json: 05bfd6d0d7e5971c8d8ee15bc5f5b2d88260a2288a00963125ae8b1e2f300015
  verification/wave34-rooted-encoding/correction-ledger.md: 357af11935c1dfd4455f67d7c131e841f1c4e22476aca4bb98e2d7b502daf7e0
  verification/wave34-rooted-encoding/comparison-input-freeze.sha256: 9d104127dd5c72c5708670efb8011b781c52769188dcd45e27a13a193b10c258
  verification/wave34-rooted-encoding/test-results.txt: 3c4ebb7b782b319447a46840951c175d401a6b4307f377c81e2aac79673259f4
limitations:
  - The formula has not been solved.
  - No SAT model, graph witness, UNSAT proof, or proof-checker run exists.
  - The candidate witness checker has no positive target control because no
    target witness is known.
  - The result is conditional and graph-scoped, not an endpoint certificate.
```

## 1. Separation and candidate-byte integrity

Before release, the eleven Stage-1 artifacts were frozen under manifest

```text
3f1bdcb0ca2d08ee0380cd1435673fddb499db8c3a8273f6676c18f17ad3550c.
```

They still validate unchanged.

The released manifests also validate exactly:

```text
publication: 16 entries
SHA-256: 7cba8a082545cbfcbf01785e6e15a0198bd1cf2357ed0a2b3f353b564a1433e7

local: 18 entries
SHA-256: e96036e97884f0bbc19c30073dbe295852117e9d4d54892cf5e57b20e6f6ec05
```

Every publication entry occurs in the local manifest with the same hash.  The
local manifest adds exactly:

```text
attempts/wave34-rooted-encoding/publication-manifest.sha256
attempts/wave34-rooted-encoding/rooted-complete.cnf.
```

The post-freeze candidate correction ledger is outside both manifests; this
packaging qualification is retained as `W34-RC-V-001`, not silently repaired.

## 2. Exact canonical label binding

Stage 1 and the candidate use different Fano coordinates.  An independent
enumeration found the expected 168 point-line design isomorphisms.  The
lexicographically first chosen binding from candidate coordinates to the
frozen Wave 33 coordinates is:

```text
candidate point p -> Wave33 point:
[0,1,3,2,5,6,4]

candidate line l -> Wave33 line:
[0,1,2,3,4,5,6].
```

Thus support vertices map by

```text
P_p -> P_[0,1,3,2,5,6,4][p],
L_l -> R_l.
```

Copy labels retain their copy index.  Because O labels are grouped in blocks
of ten by point, the O permutation is:

```text
candidate O  0.. 9 -> Wave33 O  0.. 9
candidate O 10..19 -> Wave33 O 10..19
candidate O 20..29 -> Wave33 O 30..39
candidate O 30..39 -> Wave33 O 20..29
candidate O 40..49 -> Wave33 O 50..59
candidate O 50..59 -> Wave33 O 60..69
candidate O 60..69 -> Wave33 O 40..49.
```

The complete 70-entry permutation has SHA-256

```text
d2c2d5c2edefa2794401ef6438496c52b6a0c8cd67eaad9d173735c17f437796.
```

Under these permutations, all `14x14` support entries and all `14x70`
support-to-O entries agree exactly.  The independently reconstructed candidate
hashes also match its audit:

```text
A_S: d9fe824cd6ccdadce6a946a1b042f5c282dbe182edcb7d1accfa55f96c7a8cfd
F:   58d2724fc989fb19a0be5dd83f64ed5c15ca32e5812bb83a9619af8e69bf8a74
O-label dictionaries:
     7b1ce2dc9c31c4399b8116a5b44e10f4376738661bb7f24694eba55bed4d140e.
```

The fixed `SS` identity passes all 196 entries.

## 3. Ordered D is an exact representation, not a restriction

The Stage-1 reconstruction used the mathematically independent primary bits:

```text
C(70,2) unordered D bits + 70*15 B bits
= 2,415 + 1,050
= 3,465.
```

The candidate exposes all ordered `D[i,j]` entries:

```text
4,900 ordered D variables + 1,050 B variables = 5,950 primaries.
```

The difference is exactly:

```text
70 explicit diagonal D variables
+ 2,415 mirrored off-diagonal D variables
= 2,485.
```

The raw formula begins with all necessary gates:

```text
70 negative diagonal units;
2 equivalence clauses for each of C(70,2)=2,415 mirrored pairs;
4,830 symmetry clauses;
4,900 gate clauses total.
```

Therefore every candidate ordered D assignment satisfying the gates projects
to one symmetric hollow labeled D, and every unordered labeled D has exactly
one gated ordered extension.  This is a bijection, not symmetry breaking.

All auxiliary counts are otherwise identical to Stage 1:

```text
product auxiliaries:       280,245 in both encodings
cardinality auxiliaries:   946,806 in both encodings.
```

Consequently:

```text
candidate variables - Stage1 variables = 2,485
candidate clauses   - Stage1 clauses   = 4,900

clause histogram differences:
unit +70, binary +4,830, ternary +0.
```

This exactly explains candidate totals:

```text
variables: 1,233,001
clauses:   4,323,943.
```

## 4. Every semantic family reconstructed

The verifier independently generated these exact families:

| family | semantic constraints | allocated variables | clauses |
|---|---:|---:|---:|
| primary D,B | 0 | 5,950 | 0 |
| D hollow | 70 | 0 | 70 |
| D symmetry | 2,415 | 0 | 4,830 |
| D row weight 9 | 70 | 45,150 | 175,210 |
| B row weight 3 | 70 | 3,780 | 13,930 |
| SQ: `FB=2J` | 210 | 5,670 | 20,370 |
| SO: `A_SF+FD=2J-F` | 980 | 20,076 | 71,316 |
| OO diagonal | 70 | 70,980 | 277,270 |
| OO off diagonal | 2,415 | 748,335 | 2,591,757 |
| OQ: `DB=2J-B` | 1,050 | 289,800 | 1,012,200 |
| QQ column weight 14 | 15 | 14,175 | 55,455 |
| QQ pair intersection 2 | 105 | 29,085 | 101,535 |

The off-diagonal family totals include their product and cardinality
auxiliaries.  They reconcile exactly with the Stage-1 separated accounting.

The complete exact-count distribution is:

```text
D row:      (scope 69, target 9)  x70
B row:      (scope 15, target 3)  x70
SQ:         (scope 10, target 2)  x210
SO:         (9,0)x56, (9,1)x84, (10,1)x504, (10,2)x336
OO diagonal:(scope 84, target 12) x70
OO offdiag: (84,0)x21, (84,1)x588, (84,2)x1806
OQ:         (scope 70, target 2)  x1050
QQ diagonal:(scope 70, target 14) x15
QQ offdiag: (scope 70, target 2)  x105.
```

Together with the fixed `SS` block, these are exactly all six blocks of

```text
A^2=12I-A+2J.
```

## 5. Gadget equivalence in both directions

The verifier separately exhausted the three-clause AND gadget on all eight
assignments and confirmed

```text
y <-> (x AND z).
```

For the exact-count gadget it checked the semantic threshold recurrence
through `n=7`, every target, and every primary assignment.  It also generated
the frozen CNF recurrence independently and existentially exhausted every
primary and auxiliary assignment for `n=1..4`, every target.  The accepted
primary assignments are exactly those of weight `k`.

The state and clause formulas agree independently:

```text
states S(n,k) = (k+1)n - k(k+1)/2, 0<k<n;
clauses C(n,k) = 2(k+1)^2+2+(n-k-1)(4(k+1)-1),
```

with `n` units for targets zero or `n`.

Thus product and threshold auxiliaries are uniquely fixed by the primaries.
They neither add nor remove a D,B solution.

## 6. Full formula byte reconstruction

The verifier implementation did not import or execute `generate_cnf.py`.
Instead, it rebuilt every variable and clause from the Stage-1 specification
and the audited candidate label binding, then compared the raw formula one
line at a time.

Result:

```text
variables:                1,233,001
semantic map records:     1,233,001
clauses compared:         4,323,943
bytes compared:          89,546,779
first mismatch:           NONE
extra or missing bytes:   NONE
unreferenced variables:   NONE

unit clauses:                12,154
binary clauses:           1,828,218
ternary clauses:          2,483,571

raw formula SHA-256:
2362d15f3a20df0a0d7745eb619a94061cee9911c8dda36c191fb6d728c1c3d3

verifier semantic-variable-map commitment:
263cdb9ab2e54c0d122f8b0df5fad4eb397576a7b55a758dc94936f542857b40.
```

Because every emitted clause is accounted for, there is no hidden
automorphism, orbit, transitivity, Cayley, circulant, outside-vertex symmetry,
or fixed-design constraint.  Every binary `70x15` B enters the domain before
the equations; the design is forced by the full criterion rather than chosen
in advance.

## 7. Gzip publication round trip

The compressed artifact independently passes:

```text
gzip bytes:       17,402,973
gzip SHA-256:     6b6beb5d49c7fe75b9b475162cc4bd97de2793389df150dfab9765ba497305f0
header:           1f8b08000000000002ff
method:           deflate
flags:            0
mtime:            0
level marker:     9
OS byte:          255

restored bytes:   89,546,779
restored SHA-256: 2362d15f3a20df0a0d7745eb619a94061cee9911c8dda36c191fb6d728c1c3d3
chunkwise equal to raw: YES
CRC/size footer accepted: YES.
```

The three path-specific `-text -diff` rules are present in `.gitattributes`.
The raw line-ending audit confirms that the pinned outputs retain their exact
CRLF or mixed raw bytes.

## 8. Primary model mapping and witness route

The map is exact:

```text
var(D[i,j]) = 1 + 70*i + j,       ids 1..4900;
var(B[i,q]) = 4901 + 15*i + q, ids 4901..5950.
```

Thirteen verifier-created signature models encode every primary id in binary.
The released decoder reproduced all 5,950 ids in the expected D/B cells, every
fixed cell, and every O-label record.  A hostile decoded graph was independently
counted and rejected by the candidate checker with exactly the same six-block
failure census.

The decoder does not evaluate DIMACS and requires only complete primaries, not
all auxiliaries.  Its output is correctly marked `DECODED_UNCHECKED`; this
documentation qualification is `W34-RC-V-003`.  A positive result still
requires the complete graph checker.  No positive model exists here.

## 9. Correction ledger

Three non-formula corrections are frozen:

1. `W34-RC-V-001`: the candidate's post-freeze correction ledger is outside
   both candidate manifests.
2. `W34-RC-V-002`: the frozen preflight bytes predate the published
   generator's added `contiguous` metadata.  All normalized semantic counts
   match, but the recorded command does not reproduce the pinned preflight
   hash with the current generator.
3. `W34-RC-V-003`: decoder prose should say “complete primary assignment,”
   not imply that decoder alone validates a complete DIMACS model.

None changes a formula byte, equation, satisfying primary assignment, or
mathematical status.

## 10. Necessity, sufficiency, and exact scope

Forward direction: a labeled binary D,B satisfying the six blocks obeys all
explicit row/design counts; it has a unique ordered-D gate extension, unique
product values, and unique threshold values, so it satisfies the candidate
CNF.

Reverse direction: every CNF model projects through the hollow/symmetry gates
to one binary symmetric hollow D and arbitrary binary B.  The bidirectional
product and threshold gadgets make every encoded exact count true.  The
reconstructed family inventory is exactly the six blocks, so the assembled

```text
[[A_S,F,0],[F^T,D,B],[0,B^T,0]]
```

satisfies `A^2=12I-A+2J`.

Therefore the candidate is `VERIFIED` as a complete-domain encoding of the
conditional graph criterion.

## 11. Strongest surviving objection and status wall

The strongest surviving objection is outside the encoding theorem: no one has
shown whether this verified formula is satisfiable.  No SAT model, complete
99-vertex witness, UNSAT proof, or checked proof exists.  Formula
verification cannot be promoted into existence or nonexistence.

```text
candidate encoding exact scope:            VERIFIED
manifested formula bytes:                  VERIFIED
gzip round trip:                           VERIFIED
complete-domain/no-symmetry equivalence:   VERIFIED

SAT:                                       UNKNOWN
UNSAT:                                     UNKNOWN
rooted graph extension:                    UNKNOWN
rooted endpoint:                           UNKNOWN
n3=708:                                    UNKNOWN
Conway-99:                                 UNKNOWN
novelty:                                   UNKNOWN
```
