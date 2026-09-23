# Wave 41 proof-producing search audit

Status: `CANDIDATE/UNKNOWN`. No complete endpoint case is closed, no graph is
found, and the checked endpoint coverage remains `0/33`.

This package audits the two strongest exact computational routes:

1. the complete rooted `srg(99,14,1,2)` target formula; and
2. the 33-case cover conditional on the prism-free endpoint `n3=4158`.

The conclusion is deliberately conservative. The practical endpoint route is
still exact lazy solve--cut--check with a proof-producing terminal solve. A
static complete endpoint formula is finite but contains more than 24 billion
residual-only prism clauses before simplification and is not viable on this
host.

## New checkable reduction

`propagation_scout.py` streams the frozen Wave 37 branch-15 OPB and applies
only generalized unit propagation to constraints of the form

```text
sum(unit-weight literals) >= bound.
```

The resulting candidate certificate binds the published compressed and raw
formula hashes, every derivation source line, and the complete assignment
order. It reproduces Exact's old parser statistic exactly:

```text
forced variables:            830
forced graph-edge variables: 174 / 3,486
  present:                      7
  absent:                     167
unfixed graph-edge variables: 3,312
contradiction:                none
```

Of the 174 primary assignments, 145 come directly from one-literal rows and
29 are propagation consequences of longer constraints. The previously
verified `x187=0` implication is included. This broader closure is a discovery
certificate pending an independent agent's replay; it does not supersede that
verification.

After closure, 574,351 constraints remain open. Exactly 2,975 have one unit of
residual slack. These are the constraints most likely to propagate after one
branch decision.

## Bounded failed-literal scout

Both polarities of the 32 primary variables with the highest incidence in
one-slack constraints were tested by streaming the exact OPB to a fixed point.
The 64 probes produced:

```text
failed polarities:             0
doubly failed variables:       0
new candidate implications:    0
endpoint cases closed:         0
```

Several positive-edge assumptions caused substantial cascades: the largest
two forced 112 additional variables, and another forced 111. Every probe
nevertheless reached a noncontradictory propagation fixed point. Such a fixed
point is neither a SAT witness nor evidence of existence.

## Current solver boundary

The Python environment contains PySAT 1.9.dev7 with CaDiCaL, Glucose,
Gluecard, Kissat, Lingeling, Maple, MergeSat, MiniCard, and MiniSat backends.
These embedded backends are useful for discovery, but no accepted target-scale
proof-logging path is configured through them.

Pinned Exact, VeriPB, and CakePB identities remain frozen by
`verification/2026-07-22-veripb-calibration.md`. During this audit, WSL listed
Ubuntu but resource pressure prevented a fresh shell/tool invocation from
finishing within two bounded probes. The binaries are therefore
`PINNED_PREVIOUSLY_USED_NOT_RECHECKED_CURRENTLY`, not claimed absent.

Two older embedded endpoint scouts were observed CPU-active over a two-second
sample, with no requested output files. They were not signaled or modified.
Their elapsed CPU use and missing output have no mathematical value.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave41-proof-producing-search\propagation_scout.py `
  --output attempts\wave41-proof-producing-search\branch-15-propagation-certificate.json

.\.venv\Scripts\python.exe -B `
  attempts\wave41-proof-producing-search\residual_profile.py `
  --closure attempts\wave41-proof-producing-search\branch-15-propagation-certificate.json `
  --top 32 `
  --output attempts\wave41-proof-producing-search\branch-15-residual-profile.json

.\.venv\Scripts\python.exe -B `
  attempts\wave41-proof-producing-search\failed_literal_scout.py `
  --closure attempts\wave41-proof-producing-search\branch-15-propagation-certificate.json `
  --variables 13,175,188,178,1727,15,16,17,18,19,20,21,22,23,35,36,37,38,39,40,41,42,43,94,106,189,190,191,192,193,194,195 `
  --output attempts\wave41-proof-producing-search\branch-15-failed-literal-scout.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave41-proof-producing-search -p "test_*.py" -v
```

## Promotion boundary

- A propagation fixed point is `NO_CONCLUSION`.
- A failed polarity is only a candidate implication until independently
  replayed.
- One checked UNSAT case closes only one of 33 endpoint representatives.
- All 33 checked UNSAT cases would exclude `n3=4158` and imply `n3<=4155`.
- A SAT assignment counts only after independent complete-SRG and global
  prism-free checks.
- No timeout, missing output, solver status, or model confidence is a
  certificate.
