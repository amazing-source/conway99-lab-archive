# Wave 5 joint `N3` stabilizer cover

```yaml
role: proof_a
date_utc: 2026-07-22T23:16:16Z
git_commit: b075fdd33c0023cbbbebc63469a87f5430c2da34
claim_label: DERIVED
scope: complete 12-branch matching cover conditional on the verified canonical N3 unit and the rooted residual formulation
inputs:
  code/root_model.py: 2a1f074f29f2e00e38437bf81418771d57ab41335605b9f3b9f2cae061a1624e
  code/matching_orbits.py: c216d8a0b15fb9a7da501be07f2b631917e383033c142fa5cc9f3979c498ca1f
  code/sat_model.py: 787fdd808b4a9bfc263cbe820a999612a9ee845f6600b8ddd1bac81a151d5ca5
method: exact stabilizer derivation, exhaustive matching-orbit traversal, and deterministic SAT-literal reconstruction
command: |
  .venv/Scripts/python code/matching_orbits.py --n3-joint
  .venv/Scripts/python -m unittest discover -s code -p "test_*.py" -v
outputs:
  verification/n3-joint-cover/n3-joint-cover.json: 58c4994ff0eef9c5e1702840f791d1400c3da71b445e3c217e3704c5e70de172
  verification/n3-joint-cover/verify.py: c3fc65f7d42afa3d84c8a8ea76fb912ca7bb2eb71a222fbb9414158636fc4598
limitations: universal N3 occurrence remains DERIVED; this cover solves no branch and does not change the target status from UNKNOWN
```

## Stabilizer and invariant fiber

The canonical `N3` normalization fixes the unordered residual edge

```text
{ label(0,2), label(2,4) }.
```

Inside the rooted scaffold group `C2 wreath S7`, its exact setwise stabilizer
fixes the unique shared coordinate `2` and its mate `3`. It may exchange the
two witness pairs by `(0 4)(1 5)`, while the four unused coordinate pairs have
their full wreath-product action. Therefore

```text
H = <(0 4)(1 5)> x (C2 wreath S4),   |H| = 2 * 384 = 768.
```

The endpoint fiber `S_2` is invariant under `H`. Its 12 residual vertices are
indexed by the endpoints

```text
0, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13.
```

The normalized edge forces endpoint edge `(0,4)` in the fiber matching. Ten
endpoints remain, so the conditional state space has exactly

```text
9!! = 945
```

perfect matchings.

## Exact orbit cover

Exhaustive traversal under the eight explicit generators gives 12 disjoint
orbits. Their sizes sum to 945, and every orbit size times its stabilizer size
is 768.

| branch | orbit | stabilizer | positive SAT literals |
|---:|---:|---:|---|
| 1 | 1 | 768 | `24,943,1834,1947,2056,2161` |
| 2 | 12 | 64 | `24,943,1834,1947,2057,2110` |
| 3 | 32 | 24 | `24,943,1834,1948,2004,2110` |
| 4 | 12 | 64 | `24,943,1835,1892,2057,2110` |
| 5 | 48 | 16 | `24,943,1835,1893,2004,2110` |
| 6 | 8 | 96 | `24,944,1777,1947,2056,2161` |
| 7 | 48 | 16 | `24,944,1777,1947,2057,2110` |
| 8 | 64 | 12 | `24,944,1777,1948,2004,2110` |
| 9 | 48 | 16 | `24,944,1778,1892,2056,2161` |
| 10 | 96 | 8 | `24,944,1778,1892,2057,2110` |
| 11 | 192 | 4 | `24,944,1778,1893,2003,2161` |
| 12 | 384 | 2 | `24,944,1778,1893,2004,2110` |

The complete endpoint representatives are stored in the small public JSON
certificate. Each branch fixes every one of the 66 possible edges inside
`S_2`: six are present and 60 absent. The existing `N3` clause is `+24`, so a
branch adds 65 nonduplicate unit clauses without adding variables or
cardinality constraints.

## Why the legacy fiber does not give 12 branches

The witness-pair exchange `(0 4)(1 5)` belongs to `H` and sends `S_0` to
`S_4`. Thus `H` does not act on the legacy fiber `S_0`. Restricting to the
subgroup that fixes endpoint zero gives a group of order 384 and 78 orbits on
the 10,395 legacy-fiber matchings. The number 78 is an audit checksum, not the
new branch count.

Applying an element of `H` globally changes labels of a putative solution. It
does not assert that the completed graph admits that element as an
automorphism. This is the same symmetry-safe relabeling principle used by the
root and `N3` normalizations.

## Search interface

One of the 12 jointly complete branches is selected by combining both flags:

```powershell
.venv\Scripts\python code\sat_model.py --pair-count 7 `
  --cardinality native --n3 --n3-branch 1 `
  --opb logs\local\conway99-n3-branch-01.opb
```

The CLI rejects branch numbers outside `1..12`, a missing `--n3`, non-target
scaffolds, legacy `--branch` combinations, and attempts to choose a different
fiber coordinate. All 12 branches together are complete conditional on the
upstream `N3` normalization; no individual branch is claimed complete for the
unrestricted target by itself.
