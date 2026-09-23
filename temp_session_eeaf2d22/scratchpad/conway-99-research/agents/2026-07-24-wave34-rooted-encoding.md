# Wave 34 rooted complete-domain encoding/construction report

Status: **CANDIDATE exact encoding; graph extension UNKNOWN**

```yaml
role: construction
date_utc: 2026-07-24T20:07:37Z
git_commit: 0fa5b8161baf8b2a5404a67051b7d61cbc906da3
claim_label: CANDIDATE
scope: >-
  Complete unrestricted labeled Boolean encoding of the frozen Wave 33 rooted
  six-block graph-extension criterion on cells |S|,|O|,|Q|=14,70,15. No
  automorphism, orbit, transitivity, Cayley/circulant condition, outside-vertex
  symmetry, or fixed O-Q design is assumed.
inputs:
  - AGENTS.md sha256=4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  - CONJECTURE.md sha256=7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58
  - STATUS.yaml sha256=feda17934162602804015e17130c029ffdba7bf0307cdf234f4a7d8979298864
  - verification/wave34-continuation-protocol.md sha256=60e6c3aba152e924a51bd2503e82de3d05bb39fada258da4a2796e344ae23cd4
  - verification/2026-07-24-wave33-clean-clone.md sha256=d83e18052114affaed873ddaa7bdc6a26c63afc6432345e1027aeef5bd66d052
  - verification/wave33-rooted-extension/comparison-results.json sha256=2e36ecade28bca12d35a963a8c6b52777ac7d766a3c4b3267774000fe2e929fd
  - verification/wave33-rooted-extension/comparison-audit.md sha256=fc7abcd53154d4551a5d3d97d38024840b4228195e143559c9e8b46c15644b8a
  - verification/wave33-rooted-construction-chronology/chronology-results.json sha256=b2f0b872221a3fd9f41d6a88637be21034b70e8c8129fe57617115548b425957
  - verification/wave33-rooted-construction-chronology/audit.md sha256=1346992e11db72c4c94018293d3827214e2ee79e074490b8f905028e20fa30f1
method: >-
  Standard-library deterministic DIMACS generation. Represent every ordered
  D entry and every B entry as a primary Boolean; impose D symmetry and
  hollowness explicitly; Tseitin-linearize every product; encode every exact
  integer sum by an equivalence threshold counter; independently stream-audit
  DIMACS syntax and the explicit D gates; provide SAT decoding and an
  independent full-graph checker.
command: >-
  python -B attempts/wave34-rooted-encoding/generate_cnf.py --output
  attempts/wave34-rooted-encoding/rooted-complete.cnf --audit
  attempts/wave34-rooted-encoding/encoding-audit.json --primary-map
  attempts/wave34-rooted-encoding/primary-map.json --spec
  attempts/wave34-rooted-encoding/criterion-spec.json
outputs:
  - attempts/wave34-rooted-encoding/rooted-complete.cnf sha256=2362d15f3a20df0a0d7745eb619a94061cee9911c8dda36c191fb6d728c1c3d3
  - attempts/wave34-rooted-encoding/rooted-complete.cnf.gz sha256=6b6beb5d49c7fe75b9b475162cc4bd97de2793389df150dfab9765ba497305f0
  - attempts/wave34-rooted-encoding/encoding-audit.json sha256=00be08c4da5bccabc54004cd1b70705a6112847f10658fd2fb0976416cbaa826
  - attempts/wave34-rooted-encoding/dimacs-audit.json sha256=da267da5708f50a0eb46f2c511318e99797ef8a6a9c5f4537db91fef5d5ff1ab
limitations: >-
  No SAT witness, UNSAT proof, independently checked complete semantic
  reconstruction, endpoint realization, n3=708 result, Conway-99 resolution,
  or novelty result is supplied.
```

## 1. Exact claim and domain

This run supplies a deterministic **candidate encoding** of the complete
unrestricted labeled Wave 33 criterion. It does not claim that the formula is
SAT or UNSAT.

The vertex order is

```text
S = 0..13, O = 14..83, Q = 84..98.
```

The fixed support coordinates are `P0,...,P6,L0,...,L6`, with Fano lines

```text
013, 026, 045, 124, 156, 235, 346.
```

`A_S` joins `Pp` to `Ll` exactly when point `p` is not on line `l`. The 70
O labels are in lexicographic `(point,line,copy)` order: a nonincident
point-line pair occurs once and an incident pair occurs twice. The fixed
support-to-O matrix `F` is the endpoint incidence of these labels. Thus

```text
A_S row weight = 4,
F row weight   = 10,
F column weight = 2.
```

The unknown blocks are:

```text
D: symmetric hollow binary 70 x 70 O-O adjacency;
B: arbitrary binary 70 x 15 O-Q incidence.
```

The full graph candidate is

```text
    [ A_S   F    0 ]
A = [ F^T   D    B ].
    [  0   B^T   0 ]
```

There are `C(70,2)+70*15 = 2415+1050 = 3465` independent semantic
Boolean choices before equations. The CNF deliberately exposes all 4,900
ordered `D[i,j]` entries plus all 1,050 `B[i,q]` entries, then imposes 70
hollow units and 2,415 explicit symmetry equivalences. This representation
does not remove any labeled matrix.

No `B` design is selected in advance. The formula ranges over every labeled
binary `70 x 15` matrix and forces the design equations inside the formula.
No symmetry-breaking clause appears.

## 2. Imported premises and the six encoded blocks

The only imported substantive result is the frozen Wave 33 scoped result:
conditional on the fixed signed-Fano support and incidence, the following six
integer block equations are necessary and sufficient for the 99-vertex graph
identity.

```text
SS: A_S^2 + F F^T             = 12 I - A_S + 2 J
SQ: F B                       = 2 J
SO: A_S F + F D               = 2 J - F
OO: F^T F + D^2 + B B^T       = 12 I - D + 2 J
OQ: D B                       = 2 J - B
QQ: B^T B                     = 12 I + 2 J
```

The generator checks all 196 fixed `SS` entries before allocating a clause.
It then encodes:

```text
SQ: 210 entries;
SO: 980 entries;
OO: 70 diagonal and 2,415 unique off-diagonal entries;
OQ: 1,050 entries;
QQ: 15 diagonal and 105 unique off-diagonal entries.
```

The quotient constraints `D 1=9 1` and `B 1=3 1` are also encoded explicitly,
although the full block package has redundancy. `B^T 1=14 1` is the `QQ`
diagonal. The off-diagonal `QQ` equations force every two Q columns to meet
in exactly two rows. Binary B rows of weight three therefore form the full
labeled `2-(15,3,2)` design condition; simplicity also follows from the `OO`
common-neighbour bound.

Fixed zeros in the S-Q and Q-Q cells are imposed structurally by having no
variables for those cells. Terms containing the explicitly false `D[i,i]`
are the only products omitted from scalar sums.

## 3. Numbered derivation lemmas

### Lemma R-C.1 — fixed signed-Fano block

For the displayed coordinates,

```text
A_S^2 + F F^T = 12 I_14 - A_S + 2 J_14
```

entrywise. The generator checked all 196 entries. It also obtained:

```text
support edges: 28
F^T F off-diagonal overlap histogram:
  0 -> 1,806 pairs
  1 ->   588 pairs
  2 ->    21 pairs
```

The 21 overlap-two pairs are exactly the two copies of each incident
point-line label.

### Lemma R-C.2 — product gadget

For fresh `y`, the three clauses

```text
(-y or x), (-y or z), (-x or -z or y)
```

are satisfiable exactly when `y = x z` on Boolean inputs. The unit suite
checks all eight assignments. Every entry of `D^2`, `D B`, `B B^T`, and
`B^T B` is linearized only through this equivalence gadget.

### Lemma R-C.3 — exact-cardinality gadget

For literals `x_1,...,x_n`, the generator introduces threshold states
`t(i,j)` with the equivalence

```text
t(i,j) <-> t(i-1,j) or (t(i-1,j-1) and x_i).
```

It asserts `t(n,k)` and `not t(n,k+1)` for an exact target `k`, with direct
units for targets zero and `n`. Exhaustive extension tests passed for every
assignment with `1<=n<=4` and every `0<=k<=n`. Because every recurrence is an
equivalence, the auxiliary variables neither remove nor add primary
solutions.

### Lemma R-C.4 — candidate formula equivalence

Substituting the Lemma R-C.2 products into the Lemma R-C.3 exact sums gives
the six integer blocks entrywise, together with binary, symmetry, hollow,
row, column, and design constraints. Conversely, any binary `D,B` satisfying
the six blocks determines all product and threshold auxiliaries and extends
to a CNF assignment.

This lemma is marked **CANDIDATE**, not `VERIFIED`: the discovery tests check
every family/count and the primitive gadgets, while the independent DIMACS
auditor reconstructs the explicit D gates, but a second author has not yet
regenerated the complete semantic clause stream independently.

### Lemma R-C.5 — SAT certificate route

Given a complete DIMACS model, `decode_model.py` reads the first 5,950 primary
variables, reconstructs the fixed cells and all `D,B` cells, and emits a full
99-row binary adjacency JSON. The separate `check_witness.py` does not import
the generator or decoder. It checks:

```text
99 x 99 binary shape;
symmetry and zero diagonal;
every fixed labeled S-S, S-O, S-Q, and Q-Q cell;
D row weight 9, B row weight 3, B column weight 14;
all 9,801 integer entries of A^2 = 12 I - A + 2 J.
```

A model is not a positive result until that full checker passes. No model was
obtained in this run.

## 4. Mandatory pre-search count audit

The count audit was saved before any formula emission or solver attempt as
`encoding-preflight.json`, SHA-256
`155f2e310238112d36f8eddac635f4b25fe40f4a417fb3efd59f1fbe5afb970a`.

| family | semantic constraints | auxiliary variables | clauses |
|---|---:|---:|---:|
| explicit primary D,B | — | 5,950 primary | 0 |
| D hollow | 70 | 0 | 70 |
| D symmetry | 2,415 | 0 | 4,830 |
| D row weight 9 | 70 | 45,150 | 175,210 |
| B row weight 3 | 70 | 3,780 | 13,930 |
| SQ / `FB=2J` | 210 | 5,670 | 20,370 |
| SO / `A_SF+FD=2J-F` | 980 | 20,076 | 71,316 |
| OO diagonal | 70 | 70,980 | 277,270 |
| OO off diagonal | 2,415 | 748,335 | 2,591,757 |
| OQ / `DB=2J-B` | 1,050 | 289,800 | 1,012,200 |
| QQ column weight 14 | 15 | 14,175 | 55,455 |
| QQ pair intersection 2 | 105 | 29,085 | 101,535 |
| **total** | — | **1,233,001 all variables** | **4,323,943** |

Auxiliary totals split as:

```text
product auxiliaries:       280,245
cardinality auxiliaries:   946,806
primary variables:           5,950
total:                    1,233,001
```

The completed raw DIMACS is 89,546,779 bytes and has SHA-256
`2362d15f3a20df0a0d7745eb619a94061cee9911c8dda36c191fb6d728c1c3d3`.

## 5. Independent audits and tests

The final standard-library suite passed 10 tests in 43.387 seconds:

```powershell
python -B -m unittest discover `
  -s attempts/wave34-rooted-encoding `
  -p "test_*.py" -v
```

It covers the complete fixed block, O-label multiplicities, product truth
table, exhaustive small cardinality extensions, primary ranges, all semantic
family counts, count/emission determinism, audit JSON round-trip, a partial
model parser control, and an invalid fixed-skeleton graph that the independent
witness checker rejects.

The separate streaming command

```powershell
python -B attempts/wave34-rooted-encoding/audit_dimacs.py `
  --cnf attempts/wave34-rooted-encoding/rooted-complete.cnf `
  --output attempts/wave34-rooted-encoding/dimacs-audit.json
```

passed:

```text
declared/observed variables: 1,233,001
declared/observed clauses:   4,323,943
clause lengths: 1 -> 12,154; 2 -> 1,828,218; 3 -> 2,483,571
all declared variables occur: yes
all primary variables occur: yes
first 4,900 explicit hollow/symmetry clauses independently matched: yes
malformed clauses: 0
tautological clauses: 0
repeated literals: 0
```

This audit is not a solver result or a complete independent semantic
regeneration.

## 6. Solver and certificate path

No large search was run. Before any such run, the environment check found none
of the following commands on `PATH`:

```text
cadical, kissat, cryptominisat5, drat-trim, lrat-check, veripb.
```

Therefore there is no solver/version/proof-format combination to authenticate
in this run. Executing an uninspected non-proof-producing wrapper would add
only a possible timeout or nonhit, which has no evidentiary value.

The frozen negative-certificate route is:

1. run a source-inspected proof-producing solver on the exact SHA-pinned CNF;
2. retain a complete LRAT proof, or another fully specified independently
   checkable proof;
3. record solver and checker source/version/binary hashes;
4. check the proof against the exact CNF bytes;
5. independently reconstruct the criterion-to-CNF mapping; and
6. only then consider a complete-domain UNSAT conclusion.

A solver exit code, timeout, heuristic nonhit, or proof against a formula with
extra symmetry/design assumptions remains unacceptable.

## 7. Publication packaging

The raw CNF is below GitHub's 100 MB hard limit but above its 50 MB warning and
too close to the hard limit for a robust ordinary-Git artifact. It is retained
locally; it was not deleted or weakened.

`package_cnf.py` creates a deterministic gzip with deflate level 9, zero
timestamp, empty embedded filename, and normalized OS byte. Two consecutive
runs were byte-identical:

```text
compressed bytes:   17,402,973
compressed SHA-256: 6b6beb5d49c7fe75b9b475162cc4bd97de2793389df150dfab9765ba497305f0
decompressed bytes: 89,546,779
decompressed SHA:   2362d15f3a20df0a0d7745eb619a94061cee9911c8dda36c191fb6d728c1c3d3
round trip exact:   yes
```

The ordinary-Git publication choice is:

- include the deterministic generator, small exact checkers, specification,
  mapping, audits, and `rooted-complete.cnf.gz`;
- exclude the raw `rooted-complete.cnf` from ordinary Git while retaining it
  locally; and
- reproduce the exact raw bytes either by generator or decompression.

The orchestrator controls staging and may instead choose LFS, but must not
stage the 89.5 MB raw file accidentally.

## 8. Commands, versions, seeds, and runtime

Dependency: CPython 3.13.14, standard library only. Seed: none; every artifact
is deterministic.

```powershell
# Preflight before formula/search, about 8.6 s
python -B attempts/wave34-rooted-encoding/generate_cnf.py `
  --audit-only `
  --audit attempts/wave34-rooted-encoding/encoding-preflight.json `
  --primary-map attempts/wave34-rooted-encoding/primary-map.json

# Final formula/spec/audit emission, about 20.9 s
python -B attempts/wave34-rooted-encoding/generate_cnf.py `
  --output attempts/wave34-rooted-encoding/rooted-complete.cnf `
  --audit attempts/wave34-rooted-encoding/encoding-audit.json `
  --primary-map attempts/wave34-rooted-encoding/primary-map.json `
  --spec attempts/wave34-rooted-encoding/criterion-spec.json

# Independent DIMACS audit, about 11.5 s
python -B attempts/wave34-rooted-encoding/audit_dimacs.py `
  --cnf attempts/wave34-rooted-encoding/rooted-complete.cnf `
  --output attempts/wave34-rooted-encoding/dimacs-audit.json

# Deterministic compressed package and round-trip audit, about 34.0 s
python -B attempts/wave34-rooted-encoding/package_cnf.py `
  --source attempts/wave34-rooted-encoding/rooted-complete.cnf `
  --output attempts/wave34-rooted-encoding/rooted-complete.cnf.gz `
  --audit attempts/wave34-rooted-encoding/compression-audit.json
```

The full structured command ledger is
`attempts/wave34-rooted-encoding/run-manifest.json`.

## 9. Machine-readable outputs and SHA-256

| artifact | SHA-256 |
|---|---|
| `rooted-complete.cnf` | `2362d15f3a20df0a0d7745eb619a94061cee9911c8dda36c191fb6d728c1c3d3` |
| `rooted-complete.cnf.gz` | `6b6beb5d49c7fe75b9b475162cc4bd97de2793389df150dfab9765ba497305f0` |
| `criterion-spec.json` | `3429a093c682877a3a14848620860f8ffb5e4cc0b0ca70f0fc5a2f85697d1d82` |
| `primary-map.json` | `d20ae9196012b2bbf512938abd5641b4281c10e05495b19342a3b46e4d9a264c` |
| `encoding-preflight.json` | `155f2e310238112d36f8eddac635f4b25fe40f4a417fb3efd59f1fbe5afb970a` |
| `encoding-audit.json` | `00be08c4da5bccabc54004cd1b70705a6112847f10658fd2fb0976416cbaa826` |
| `dimacs-audit.json` | `da267da5708f50a0eb46f2c511318e99797ef8a6a9c5f4537db91fef5d5ff1ab` |
| `compression-audit.json` | `df6bcc6077480ff5348357a51b471862ad82c2d1088a561d1dabd1c96664746c` |
| `generate_cnf.py` | `e976ed971cc1dac0ce439257b9269b7be2298b535025697f860be62a1a467c96` |
| `decode_model.py` | `c783572b6922e0297fa731bd767c6823c7f188390f7f285e93c028e9403ab5bd` |
| `check_witness.py` | `127d5965a50f21c441799bc1c48211a6e4cfa206517e660707c772bb60ec2035` |
| `audit_dimacs.py` | `9ecfb7b06a0d5b078fcd998c926b2e7f4af0ae717855d68dbd047be6c796371a` |
| `package_cnf.py` | `b6a771016c433efbf0b2a2bc236b29651e5b750c2b8cd1a7ae3a1deeb2d13994` |
| `test_encoding.py` | `e004c0d5e913e9aa6a2fc6f889b559c893f8be66911bc8a522726624375f7e6b` |
| `test-results.txt` | `98b747fc36cd3e9552af131445d6f596ebc0b7c82cfcca5672bcbdff80e7b99a` |

## 10. Failed routes retained

1. The first unit run passed seven tests and failed one assertion because the
   test expected the `F^T F` overlap histogram with keys zero and two reversed.
   The generated fixed matrices and the 196-entry block check were correct.
   Only the test expectation changed; the encoding did not. Subsequent runs
   passed all ten tests.
2. A proof-producing large search was not started because no solver/proof
   checker was on `PATH`. This is an environment/certificate blocker, not
   evidence about satisfiability.
3. No selected-design search was attempted. Such a search would be restricted
   and could not support complete-domain UNSAT.

## 11. Strongest self-objection

The strongest objection is not formula size; it is independent semantic
mapping. The CNF is deterministically generated, gadget-tested, count-audited,
and independently syntax/gate-audited, but a second implementation has not
yet reconstructed every nonlinear family clause-for-clause.

There is also a labeling audit obligation. The allowed frozen Wave 33 inputs
describe the signed-Fano support and confirm its fixed labeling, but do not
publish the raw prior `A_S,F` bytes or their hash values in the files available
to this track. This run therefore freezes the explicit canonical coordinates
above. They are bijectively label-equivalent to any signed-Fano
coordinatization, so complete-domain SAT/UNSAT is invariant, but a verifier
must supply and check the explicit permutation before claiming byte identity
with the Wave 33 candidate package.

Finally, the witness checker has a hostile negative control but cannot have a
positive target control unless a graph witness is found. A SAT result must
still pass it; an UNSAT result requires a complete independently checked proof.

## 12. Limitations and strongest justified conclusion

Complete versus restricted coverage:

```text
formula semantic domain: complete labeled D,B domain, CANDIDATE mapping
automorphism restriction: none
fixed O-Q design: none
SAT witness: none
UNSAT certificate: none
rooted graph extension: UNKNOWN
full rooted endpoint: UNKNOWN
n3=708: UNKNOWN
Conway-99: UNKNOWN
novelty: UNKNOWN
```

The strongest justified conclusion is:

> A complete-domain, no-symmetry-breaking CNF candidate for the exact rooted
> six-block criterion has been emitted with reproducible counts, hashes,
> publication-safe compression, decoder, and independent full-graph checker.
> It has not been solved or independently promoted. The rooted binary
> criterion and Conway-99 remain `UNKNOWN`.
