# Wave 6 branch propagation and bounded scouts

Target result: `UNKNOWN`. No candidate or refutation was found.

```yaml
role: construction
date_utc: 2026-07-22T23:58:01Z
git_commit: 5ff65b9ca8aa3fbb7ce949244757adbbc7654b2f
claim_label: DERIVED
scope: unit-propagation closure and non-evidentiary bounded solver scouting for the 12 verified N3 joint branches
inputs:
  code/root_model.py: 2a1f074f29f2e00e38437bf81418771d57ab41335605b9f3b9f2cae061a1624e
  code/matching_orbits.py: c216d8a0b15fb9a7da501be07f2b631917e383033c142fa5cc9f3979c498ca1f
  code/sat_model.py: 787fdd808b4a9bfc263cbe820a999612a9ee845f6600b8ddd1bac81a151d5ca5
method: three-backend unit-propagation comparison, fresh-process MiniCard conflict budgets, deterministic-budget Exact traces, and strict VeriPB/CakePB checking
command: |
  New-Item -ItemType Directory -Force logs/local/wave6-propagation | Out-Null
  1..12 | ForEach-Object {
    $tag = '{0:D2}' -f $_
    $opb = "logs/local/wave6-propagation/branch-$tag.opb"
    $proof = "logs/local/wave6-propagation/branch-$tag.pbp"
    .venv/Scripts/python code/sat_model.py --pair-count 7 --cardinality native --n3 --n3-branch $_ --opb $opb
    .venv/Scripts/python code/sat_model.py --pair-count 7 --cardinality native --n3 --n3-branch $_ --solve --solver minicard --conflict-budget 100000
    Exact --verbosity=1 --timeout-det=2 --proof-assumptions=0 "--proof-log=$proof" $opb
  }
outputs:
  primary_status: UNKNOWN_12_OF_12
  raw_veripb: VERIFIED_NO_CONCLUSION_12_OF_12
  elaboration: PASS_12_OF_12
  kernel_veripb: VERIFIED_NO_CONCLUSION_12_OF_12
  cakepb: VERIFIED_NO_CONCLUSION_12_OF_12
limitations: propagation is not exhaustive search; every bounded solver run ended UNKNOWN and every checked proof trace ended NO CONCLUSION
```

## Frozen environment

The primary measurements were taken from the clean public Wave 5 source
commit shown above, before the Wave 6 refined-cover implementation was added.
The environment used Python 3.13.14 and `python-sat==1.9.dev7`.

| component | SHA-256 |
|---|---|
| Python executable | `b70275ad94210fce7548761143be5e177769721045e287bb6c80aac3f928c65b` |
| PySAT native extension | `1019bacdbb9400cc54fa89aa39294fefe1c63d5a67fdab35f473364529ec72dd` |
| Exact | `842ac70b4e938d24f537a56513ff64ea845206c714ce34da467ce146c5c5c928` |
| VeriPB | `635b6f2fbd7a7fb98bf7a1f7af038355a1e58438cfdc1ee4e2649979017ace36` |
| CakePB | `5920919642b1c498c2654a849fcd894ea18e7736ebf32919a9a8915861033e46` |

The twelve canonical OPBs are the byte-identical Wave 5 formulas recorded in
`verification/2026-07-22-wave5-clean-clone.md`. Each has 289,338 variables,
291,756 constraints, 14,241,485 bytes, six positive matching units, and 60
negative matching units.

## Exact propagation profile

Starting with only the six positive matching edges, every tested encoding
forces all 60 negative decisions in the shared fiber. The selected six edges
also force 492 wedge nonedges. Each selected free mate-pair edge saturates two
coordinate-incidence equations and supplies a further block of 22 forced
residual nonedges. Thus the observed complete root fixpoint is

```text
558 + 22 * (selected free mate-pair edges).
```

Compact/native MiniCard, direct/native MiniCard, compact/CNF CaDiCaL195, and
Exact root propagation agree exactly.

| branch | mate pairs | root units | extra residual nonedges |
|---:|---:|---:|---:|
| 1 | 4 | 646 | 88 |
| 2 | 2 | 602 | 44 |
| 3 | 1 | 580 | 22 |
| 4 | 0 | 558 | 0 |
| 5 | 0 | 558 | 0 |
| 6 | 3 | 624 | 66 |
| 7 | 1 | 580 | 22 |
| 8 | 0 | 558 | 0 |
| 9 | 2 | 602 | 44 |
| 10 | 0 | 558 | 0 |
| 11 | 1 | 580 | 22 |
| 12 | 0 | 558 | 0 |

For a mate edge `p={g,a} ~ q={g,mate(a)}`, the nonedge between `p` and root
neighbor `mate(a)` already has common neighbors `a,q`. The `mu=2` axiom forces
`p` nonadjacent to the other eleven members of the mate fiber; the symmetric
statement for `q` gives the block of 22. This is a useful explicit propagation
lemma, but it is already encoded by the rooted incidence equations and is not
an additional global constraint.

## Bounded MiniCard scouts

Each branch ran in a fresh Python process with a nominal 100,000-conflict
budget. Every run returned `UNKNOWN`.

| branch | conflicts | decisions | propagations |
|---:|---:|---:|---:|
| 1 | 100002 | 465977 | 113291058 |
| 2 | 100000 | 781879 | 113161195 |
| 3 | 100001 | 540386 | 118427250 |
| 4 | 100002 | 552136 | 96274578 |
| 5 | 100000 | 667599 | 117504338 |
| 6 | 100000 | 633682 | 202109225 |
| 7 | 100001 | 631426 | 100223125 |
| 8 | 100002 | 656614 | 104551448 |
| 9 | 100003 | 569907 | 115592859 |
| 10 | 100001 | 550811 | 101618132 |
| 11 | 100002 | 500198 | 106323402 |
| 12 | 100002 | 666726 | 111803023 |

Branch 1 repeated with identical counters. The conflict-budget profiles do not
agree with Exact on a stable branch ordering, so they are not evidence of
relative mathematical hardness.

## Checked deterministic partial traces

Exact ran each branch with deterministic timeout `--timeout-det=2`. Every run
returned `UNKNOWN`.

| branch | conflicts | decisions | propagations | root units |
|---:|---:|---:|---:|---:|
| 1 | 2809 | 111104 | 4624069 | 646 |
| 2 | 3509 | 189515 | 3519607 | 602 |
| 3 | 3141 | 212519 | 3892004 | 580 |
| 4 | 3173 | 183674 | 4142667 | 558 |
| 5 | 3554 | 191901 | 3904842 | 558 |
| 6 | 3424 | 174226 | 4106975 | 624 |
| 7 | 3200 | 173116 | 3991440 | 580 |
| 8 | 3491 | 211206 | 3840536 | 558 |
| 9 | 3304 | 185961 | 3774351 | 602 |
| 10 | 3269 | 178610 | 4117841 | 558 |
| 11 | 3423 | 189594 | 3483830 | 580 |
| 12 | 2891 | 212095 | 4375841 | 558 |

For all twelve raw traces, strict VeriPB replay passed, elaboration succeeded,
the strict kernel replay passed, and CakePB reported `VERIFIED NO CONCLUSION`.
Branch 1 repeated byte identically: 19,727,290 bytes with SHA-256
`2c5f7498a7d09c99571b45966220dc393edf3a2275795d681b6acfd6ae3b4237`.

An accepted partial trace proves only that its recorded deductions are valid.
Because it has no conclusion, it does not eliminate a branch. The bulky raw
traces remain ignored scratch artifacts rather than public evidence.

## Optional refined scouting

After independent development of the 78-way refinement, a shared incremental
MiniCard instance used 100 conflicts per case. All 78 cases returned `UNKNOWN`;
learned clauses were reused, so neither the per-case counters nor their order
are independent. Fresh-solver attempts exceeded the allotted wall envelope
and were discarded. The exact 78-orbit cover itself was subsequently audited
separately; see `verification/2026-07-22-n3-refined-cover-audit.md`.

Nothing in this report is a satisfiability or unsatisfiability result. It is a
reproducible engineering profile for choosing the next proof-producing run.
