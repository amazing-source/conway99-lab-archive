# Wave 39 proof-solver micro-shard

Status: `CANDIDATE_STANDARD_PROOF_PENDING_CAKEPB_AND_INDEPENDENT_REPLAY`.
The complete endpoint remains `UNKNOWN`, and checked endpoint-case coverage
remains `0/33`.

This package turns one previously implicit branch-15 propagation into a small,
byte-bound proof certificate. The published Wave 37 OPB for refined branch 15
contains the units `x24=1` and `x2=1`. Its common-neighbor capacity constraint
forces `x3591=0`. Under the additional primary-edge assumption `x187=1`, a
wedge implication is then false in every literal. Therefore

```text
branch 15 implies x187=0.
```

The residual primary variable `x187` represents the edge between residual
indices `2` and `24`, whose labels are `(0,4)` and `(2,4)`. Thus the exhaustive
polarity split

```text
branch15 AND x187=1
branch15 AND x187=0
```

now has a candidate checked certificate for the first shard. The second shard
is still open. This is not one-half of endpoint probability or model count;
it is one closed member of an explicitly named two-way logical split.

## Standard proof-producing replay

The same shard was exported as an exact OPB by changing the frozen base header
from 574,615 to 574,616 constraints and appending only
`+1 x187 >= 1 ;`. The deterministic compressed formula and metadata are
published here; the 29,827,719-byte raw OPB is regenerated and ignored.

Pinned Exact commit `b921cd1` reported `UNSATISFIABLE` while parsing:

```text
propagations:        830
unit literals:       830
decisions:             0
conflicts:             0
```

It emitted a 72,616-byte VeriPB proof. Pinned VeriPB 3.0.2 then returned
`VERIFIED UNSATISFIABLE` for:

- strict replay of the raw proof;
- elaboration to the 92,655-byte kernel proof; and
- strict replay of the kernel proof.

The CakePB invocation was interrupted before it emitted a result. Its process
was terminated and its empty transcript was discarded. Therefore this lane
does **not** promote the shard to `VERIFIED`; the formal-kernel gate and an
independent verifier remain outstanding.

## Why the proof is sound

Every cited OPB constraint has unit coefficients and is of the form

```text
sum(literals) >= bound.
```

If the number of already true literals plus the number of unassigned literals
equals the bound, every unassigned literal must be true. This is generalized
unit propagation. If that maximum possible left-hand side is below the bound,
the current assumptions are contradictory.

The checker independently:

1. binds the gzip and decompressed SHA-256 digests of the published OPB;
2. binds each cited source line by line number, exact bytes, term count, and
   bound;
3. replays three generalized-unit inferences;
4. checks the final violated constraint; and
5. rejects any claim that a complete endpoint case was closed.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B attempts\wave39-proof-solver\generate_certificate.py `
  --output attempts\wave39-proof-solver\branch-15-x187-positive-certificate.json

.\.venv\Scripts\python.exe -B attempts\wave39-proof-solver\verify_certificate.py `
  attempts\wave39-proof-solver\branch-15-x187-positive-certificate.json `
  --output attempts\wave39-proof-solver\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave39-proof-solver -p "test_*.py" -v

.\.venv\Scripts\python.exe -B attempts\wave39-proof-solver\export_shard_opb.py `
  --raw attempts\wave39-proof-solver\branch-15-x187-positive.opb `
  --gzip attempts\wave39-proof-solver\branch-15-x187-positive.opb.gz `
  --metadata attempts\wave39-proof-solver\branch-15-x187-positive-formula.json
```

## Resource and promotion boundary

No new large solver was launched. At inspection time, host free physical
memory was approximately 2.5 MiB, WSL could not create its VM, and the two
pre-existing Wave 36 scouts were still CPU-active. They were not signaled,
attached to, stopped, or modified.

The package contains two proof views: a tiny project-local generalized-unit
certificate, and a standard Exact/VeriPB raw-plus-kernel proof. Both still
require independent verification, and CakePB has not returned a terminal
result. Even after promotion this closes only the positive `x187` shard inside
branch 15. Branch 15, all 33 endpoint cases, `n3=4158`, and Conway-99 remain
unresolved.
