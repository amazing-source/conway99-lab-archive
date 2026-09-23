# External DRAT-to-LRAT calibration

Verdict: `PASS` for the small proof pipeline; target status unchanged.

```yaml
role: verifier
date_utc: 2026-07-22T20:29:00Z
source_commit: 08ebf70d728b0d14a86d63005ced704eda7b3b50
claim_label: VERIFIED
scope: both complete pair_count=3 matching branches only
target_scope: none
limitations: no target branch was proved UNSAT
```

## Pinned tools

The tools were built from clean, shallow source checkouts under Ubuntu 24.04
in WSL2:

| tool | version/commit | role |
|---|---|---|
| CaDiCaL | 3.0.1, `c60730422e758ef1cebe7aeddf2dda31c996bf04` | DRAT producer |
| drat-trim | `2e5e29cb0019d5cfd547d4208dca1b3ec290349f` | DRAT check and LRAT conversion |
| lrat-check | same source commit | independent LRAT replay |

CaDiCaL was configured with `g++ -O3 -DNDEBUG`. The source checkouts and
binaries were kept outside Git; credentials were neither used nor copied.

## Instances and artifacts

Both fiber-matching partitions of two were materialized as unit clauses in
the audited compact CNF encoding.

| branch | artifact | bytes | SHA-256 |
|---|---|---:|---|
| `(2)` | CNF | 52,060 | `e8efa30aaf4f025491b5cf7c56e2730d66a0be8f45220e32442b3ead788c68f5` |
| `(2)` | DRAT | 4,016 | `347c2428d43e5090c2e1d5b9525551f4f88c86ae843186753542aacff9333b9d` |
| `(2)` | LRAT | 18,127 | `1725dbbacbbc89fedca873d7ca33095ba7fad1704be3b8989ebd04388b5a8626` |
| `(1,1)` | CNF | 52,060 | `90e3cd85235e930dcb9f72cbf70036080cc357270e56fe6a6c0bd0770521c4e7` |
| `(1,1)` | DRAT | 697 | `45385a9740df4a1f93f0879e6b98880c4c766e0bf2ffd795df9f17b66f9cd8e2` |
| `(1,1)` | LRAT | 17,631 | `6235c29bbddd8222a37827abfe20d2a6087a06f9b5a2453cfd96c78814334ae0` |

Each CNF has 1,938 variables and 3,744 clauses.

## Reproduction outline

Generate the two branch-unit instances:

```powershell
.venv\Scripts\python code\sat_model.py --pair-count 3 --variant compact `
  --branch 2 --cnf logs\local\m3-branch-2-compact.cnf
.venv\Scripts\python code\sat_model.py --pair-count 3 --variant compact `
  --branch 1+1 --cnf logs\local\m3-branch-1+1-compact.cnf
```

For each instance, run the equivalent Linux commands with the pinned tools:

```bash
cadical --no-binary INSTANCE.cnf PROOF.drat
drat-trim INSTANCE.cnf PROOF.drat -L PROOF.lrat
lrat-check INSTANCE.cnf PROOF.lrat
```

CaDiCaL returned `UNSATISFIABLE`. `drat-trim` returned `s VERIFIED` and
emitted LRAT; the separately compiled `lrat-check` returned `VERIFIED` for
both branches.

An older ignored `m3-direct.drup` artifact was deliberately not reused. The
independent Wave 2 verifier rejected it as malformed because one line lacked a
terminating zero. This fresh pipeline replaces that calibration artifact; it
does not retroactively validate the old file.

## Evidentiary boundary

This proves only that the proof-producing/checking path works on a small
negative control whose complete branch cover has two members. A target
nonexistence claim would require the exact target CNF and a complete accepted
proof for every one of the 11 audited target branches, with retained artifacts
and clean-clone replay.
