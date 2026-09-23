# Wave 31 T20 construction failure ledger

This ledger preserves every bounded or failed route used in this lane.  None
of the timeouts or heuristic nonhits is evidence that a T20 endpoint frame
does not exist.

## Frozen search domain

The exact shell contains `5076` norm-four vectors, represented by `2538`
canonical antipodal lines.  The canonical sign is only a naming convention:
the first nonzero coordinate is positive.  No automorphism of T20, the
endpoint, or a target graph is assumed.

The first Boolean gate is

```text
z_l in {0,1},
sum_l z_l = 105,
sum_l z_l v_l v_l^T = 21 T20^(-1).
```

This has `2538` Boolean variables and `210` upper-triangular moment
equations; the cardinality equation is rationally dependent on the moment
system but is retained explicitly in solver models.

The oriented gate additionally chooses one sign for each selected line and
requires

```text
sum_l z_l epsilon_l v_l = 0,
epsilon_l epsilon_m <v_l,v_m> in {0,1,-1,-2}.
```

All distinct canonical lines have inner product `0,+/-1,+/-2`.  Thus the
alphabet adds exactly two forbidden signed pairs for each of the `242649`
absolute-two edges, or `485298` Boolean clauses.  There are no omitted
absolute-three or absolute-four conflicts.

## Optional solver installation and replay

The exact checker has no dependency on these packages.  The bounded scouts
can be replayed in disposable directories:

```powershell
$highs = Join-Path $env:LOCALAPPDATA 'Temp\wave31-highspy'
$ortools = Join-Path $env:LOCALAPPDATA 'Temp\wave31-ortools'
$scip = Join-Path $env:LOCALAPPDATA 'Temp\wave31-scip'

python -m pip install --target $highs highspy==1.15.1
python -m pip install --target $ortools ortools==9.15.6755
python -m pip install --target $scip pyscipopt==6.2.1

$env:PYTHONPATH = $highs
python -B attempts\wave31-t20-frame\solver_scout.py `
  --engine highs --seconds 45 --workers 1 --seed 0 --verbose
python -B attempts\wave31-t20-frame\solver_scout.py `
  --engine lp --seconds 10 --workers 1 --seed 0

$env:PYTHONPATH = $ortools
python -B attempts\wave31-t20-frame\solver_scout.py `
  --engine cpsat --seconds 40 --workers 8 --seed 0 --verbose
python -B attempts\wave31-t20-frame\solver_scout.py `
  --engine cpsat-xor --seconds 40 --workers 8 --seed 1
python -B attempts\wave31-t20-frame\solver_scout.py `
  --engine cpsat-oriented --seconds 30 --workers 8 --seed 3

$env:PYTHONPATH = $scip
python -B attempts\wave31-t20-frame\solver_scout.py `
  --engine scip --seconds 40 --workers 8 --seed 0 --verbose
```

Wall-clock solver traces are machine- and version-sensitive.  Their statuses
are therefore retained as discovery telemetry, not deterministic
certificates.  The exact rational and radius-two certificates in
`exact-results.json` replay without these packages.

## W31-T20-F001: HiGHS Boolean timeout

HiGHS `1.15.1`, one thread, random seed zero, and a `45` second limit received
the full `211`-row, `2538`-binary second-moment model.  It returned
`Time limit reached` with:

```text
incumbents:      0
processed nodes: 101
LP iterations:   91217
```

No feasible selection and no infeasibility certificate was returned.

## W31-T20-F002: CP-SAT Boolean timeout

OR-Tools CP-SAT `9.15.6755`, eight workers, seed zero, and a `40` second
limit received the same Boolean moment model.  It returned `UNKNOWN` with no
solution:

```text
conflicts:                 6465
branches:                  105746
integer propagations:      38160432
deterministic time:        209.812
```

This is not a complete search.

## W31-T20-F003: explicit GF(2) XOR timeout

The exact mod-two relaxation has rank `210` in the `211` equations consisting
of the moment equations and odd row count.  It is consistent.  Adding all
`210` moment XORs and the count XOR explicitly to CP-SAT, with eight workers,
seed one, and a `40` second limit, still returned `UNKNOWN` with no solution:

```text
conflicts:                 1884
branches:                  111567
propagations:              438406
integer propagations:      13161471
deterministic time:        198.638
```

Consistency of this relaxation is not a frame, and the timeout is not an
obstruction.

## W31-T20-F004: SCIP Boolean timeout

PySCIPOpt `6.2.1` with SCIP `10.0.2`, up to eight threads, seed shift zero,
and a `40` second limit received the full second-moment model.  It returned
`timelimit` with:

```text
solutions: 0
nodes:     73
```

No solver-negative inference is made.

## W31-T20-F005: full sign/alphabet scout timed out

The full oriented CP-SAT model used `5076` signed Boolean variables,
`2538` at-most-one sign constraints, all `210` moment equations, all `20`
zero-sum coordinate equations, the row count, and all `485298` signed
absolute-two clauses.

The first `28` second run spent its budget in presolve and returned `UNKNOWN`
before search.  A second run disabled presolve, used eight workers, seed
three, and a `30` second limit.  It returned `UNKNOWN` with no row set:

```text
conflicts:             103
branches:              20897
propagations:          2757638
integer propagations:  2778533
LP iterations:         69214
deterministic time:    214.515
```

This does not test the later `Q_A`, `B_A`, or `A4_A` gates.

## W31-T20-F006: heuristic near-frame is not a candidate

Random-objective continuous LP vertices followed by deterministic
single-exchange descent produced the retained `105`-line set
`W31-T20-NEAR-105-001`.  Exact arithmetic gives:

```text
Frobenius moment-residual score: 121
nonzero upper-triangular entries: 63
maximum absolute residual entry: 2
```

It is explicitly `NOT_A_FRAME`.  The exact checker then exhausts all one- and
two-exchange repairs:

```text
one-exchange choices:  105 * 2433
removal pairs:         5460
addition pairs:        2958528
exact repairs:         0
```

This proves only that exact, named radius-two neighbourhood is empty.
Selections three or more exchanges away, all other initial supports, and the
unrestricted problem remain `UNKNOWN`.

## W31-T20-F007: slow exploratory pair loop

An initial unoptimized all-pairs inner-product loop exceeded a `60` second
wrapper and was discarded.  A matrix-vector-preprocessed standard-library
implementation subsequently completed the same full calculation and is the
only version used in `exact_check.py`.

## W31-T20-F008: modular fingerprint normalization

A NumPy discovery prototype emitted an expected unsigned-overflow warning
while computing fingerprints modulo `2^64`.  It found zero radius-two
fingerprint candidates.  The published checker replaces that prototype with
explicit Python-integer masking after every fingerprint, scans all
`2958528` addition pairs, and verifies every fingerprint collision
entrywise.  Exact equality necessarily implies fingerprint equality, so a
collision may add work but cannot conceal an exact repair.

## Positive control: exact rational relaxation

HiGHS reported a continuous box-relaxation vertex with `33` unit coordinates
and `210` fractional coordinates.  Solver floats are not used as evidence.
Instead, `exact_check.py` reconstructs the `210` weights by fraction-free
Bareiss elimination and verifies with `Fraction` that

```text
0 < lambda_l < 1 on all 210 fractional coordinates,
sum_l lambda_l = 105,
sum_l lambda_l v_l v_l^T = 21 T20^(-1).
```

This is an exact positive certificate that the continuous relaxation is
nonempty.  It makes any continuous Farkas obstruction impossible for this
line formulation, but it says nothing about Boolean selection or orientation.

## Status wall

```text
complete T20 norm-four shell:                 EXACT
continuous second-moment relaxation:          EXACT WITNESS
cap-one-coordinate line restriction:          EXCLUDED
named radius-two near-frame neighbourhood:     EXCLUDED
unrestricted Boolean second moment:            UNKNOWN
oriented zero-sum alphabet frame:              UNKNOWN
Q_A / B_A / A4_A:                              UNKNOWN
coupled T20 plus U24 projector/Schur package:   UNKNOWN
n3=708, Conway-99, and novelty:                 UNKNOWN
```
