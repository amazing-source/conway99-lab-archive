# Independent verification of the Wave 39 branch-15 proof shard

Status: `VERIFIED` at the narrow shard scope only.

The frozen branch-15 formula contains the units `x24=1` and `x2=1`.
Source line 571132 is

```text
sum_{i=3569}^{3650} ~xi + ~x2 >= 82.
```

There are exactly 82 literals in the sum before `~x2`. Because `x2=1`,
`~x2` is false, so all 82 remaining literals are forced true. In particular,
`~x3591` is true. Under the extra shard assumption `x187=1`, source line 106,

```text
~x24 + ~x187 + x3591 >= 1,
```

then has no true literal. This independently verifies that refined branch 15
entails `x187=0`.

The verifier also checked the exact source bytes and line numbers, the
append-unit OPB transformation, all published hashes and metadata, and both
retained proof bodies. Fresh strict VeriPB 3.0.2 invocations independently
reported `VERIFIED UNSATISFIABLE` for both raw and elaborated-kernel proofs.
CakePB was not rerun and has no retained conclusion.

This closes only `branch15 AND x187=1`. The complementary `x187=0` shard,
refined branch 15, every complete endpoint case, the endpoint `n3=4158`, and
Conway-99 remain open. Proof coverage remains exactly `0/33`; no improved
upper bound follows.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B verification\wave39-proof-solver\independent_check.py `
  --run-veripb `
  --output verification\wave39-proof-solver\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave39-proof-solver -p "test_*.py" -v
```
