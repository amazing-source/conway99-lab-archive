# Wave 34 rooted complete-domain encoding candidate release

Released: 2026-07-24T20:20:34Z

Discovery base:
`0fa5b8161baf8b2a5404a67051b7d61cbc906da3`

Orchestrator checkpoint before release:
`52c94e915927f791d30f680d12181a08567248fb`

## Quarantined claim

```text
label: CANDIDATE
scope: complete unrestricted labeled CNF encoding of the verified Wave 33
       rooted six-block graph criterion
formula status: NOT SOLVED
SAT witness: NONE
UNSAT proof: NONE
rooted graph extension: UNKNOWN
rooted endpoint: UNKNOWN
n3=708: UNKNOWN
Conway-99: UNKNOWN
novelty: UNKNOWN
```

A complete-domain encoding is infrastructure, not a graph and not an
exclusion. The independent verifier must reconstruct the semantic mapping
before this candidate can be promoted even in its encoding-only scope.

## Frozen publication package

The publication manifest contains 16 entries and has SHA-256

```text
7cba8a082545cbfcbf01785e6e15a0198bd1cf2357ed0a2b3f353b564a1433e7.
```

The complete local manifest contains 18 entries, including the raw CNF and
the publication manifest, and has SHA-256

```text
e96036e97884f0bbc19c30073dbe295852117e9d4d54892cf5e57b20e6f6ec05.
```

Both manifests were independently re-read by the orchestrator and every
listed path matched.

Three checksum-pinned audit outputs contain raw CRLF bytes. The
pre-publication Git audit added path-specific `-text -diff` attributes so
ordinary Git preserves those exact bytes instead of normalizing them. This
packaging-only correction is recorded in
`attempts/wave34-rooted-encoding/correction-ledger.md`; no formula or claim
changed.

Key byte freezes:

| artifact | bytes | SHA-256 |
|---|---:|---|
| `agents/2026-07-24-wave34-rooted-encoding.md` | 20,255 | `120f9709aea2f7010866c2b7d7e2b74cb954bba92c903923c8c81db4a7dcea8c` |
| raw `rooted-complete.cnf` | 89,546,779 | `2362d15f3a20df0a0d7745eb619a94061cee9911c8dda36c191fb6d728c1c3d3` |
| published `rooted-complete.cnf.gz` | 17,402,973 | `6b6beb5d49c7fe75b9b475162cc4bd97de2793389df150dfab9765ba497305f0` |
| `criterion-spec.json` | 10,061 | `3429a093c682877a3a14848620860f8ffb5e4cc0b0ca70f0fc5a2f85697d1d82` |
| `primary-map.json` | 5,844 | `d20ae9196012b2bbf512938abd5641b4281c10e05495b19342a3b46e4d9a264c` |
| `encoding-audit.json` | 6,015 | `00be08c4da5bccabc54004cd1b70705a6112847f10658fd2fb0976416cbaa826` |
| `dimacs-audit.json` | 1,474 | `da267da5708f50a0eb46f2c511318e99797ef8a6a9c5f4537db91fef5d5ff1ab` |

The raw CNF remains local and is excluded by the repository's `*.cnf`
ignore rule. Ordinary Git receives the deterministic gzip, generator,
specifications, audits, decoders, checker, and tests. The gzip has an exact
recorded round trip to the raw bytes.

## Orchestrator replay before release

Environment:

```text
Python 3.13.14
standard library only
seed: none
```

Commands:

```powershell
python -B -m unittest discover `
  -s attempts/wave34-rooted-encoding `
  -p 'test_*.py' -v

python -B attempts/wave34-rooted-encoding/audit_dimacs.py `
  --cnf attempts/wave34-rooted-encoding/rooted-complete.cnf `
  --output attempts/wave34-rooted-encoding/dimacs-audit.json
```

Observed:

```text
tests: 10/10 PASS
declared/observed variables: 1,233,001
declared/observed clauses: 4,323,943
syntax, ranges, occurrence, and explicit D-gate prefix: PASS
tautological clauses: 0
repeated literals: 0
```

This replay exercises candidate-owned semantics and a separate
candidate-authored DIMACS auditor. It does not confer `VERIFIED`.

## Comparison wall

The verifier's Stage-1 independent specification must be byte-frozen before
candidate inspection. Stage 2 must:

1. validate both manifests and the gzip-to-raw hash;
2. bind the canonical support coordinates to the exact Wave 33 label order;
3. independently reconstruct every semantic family, target, and count;
4. audit product and exact-cardinality gadgets in both directions;
5. compare independently generated small fixtures or the full clause stream;
6. validate model decoding into the complete 99-vertex witness checker;
7. confirm that no symmetry breaking or fixed design entered the formula;
8. retain the absence of a proof-producing solver and proof checker; and
9. leave satisfiability and every global mathematical status `UNKNOWN`.
