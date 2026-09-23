# Wave 53 multi-root WL verification

This directory independently verifies the finite claims in
`attempts/wave53-multi-root-wl` without importing the discovery
implementation.

## Verdict

All four claimed finite templates and numerical WL results reproduce:

```text
relation   expanded order / stable 2-WL / triangle-core folklore 3-WL
K          319 / 285 / 107
B          323 / 584 / 321
C          325 / 321 / 240
D          326 /  63 /  61
```

The common-`K` counts `5,2,1,0`, all 72 exact-two caps, the unique merged and
forced-true `B` candidate, candidate identity rules, and independent positive
local controls also pass. There are no numerical corrections.

This verifies only the finite two-root relaxation. It excludes no relation;
the prism-free endpoint and Conway-99 remain `UNKNOWN`.

The principal envelope caveat is that discovery `exact-result.json` omits the
3-WL triple-color vector, so its stored 3-WL tuple hash cannot be reconstructed
from that JSON alone. Independent counts and full class-size multisets match,
and the independent component records do retain their full vectors.

## Files

- `protocol.md`: protocol frozen before discovery inspection.
- `independent_check.py`: standard-library clean-room constructor and verifier.
- `test_independent_check.py`: hostile mutation/unit suite.
- `independent-result.json`: compact aggregate and discovery comparison.
- `records/{K,B,C,D}.json`: complete exact partitions, tensors, caps, and
  controls.
- `audit.md`: derivation, adversarial audit, and status boundary.
- `run-report.yaml`: AGENTS.md run-report envelope.
- `execution.log`: final exact checker output.
- `package-manifest.sha256`: verification package hashes.

## Reproduce

```powershell
python -B verification\wave53-multi-root-wl\independent_check.py `
  --discovery attempts\wave53-multi-root-wl\exact-result.json `
  --output-dir verification\wave53-multi-root-wl

python -B -m unittest discover `
  -s verification\wave53-multi-root-wl -p "test_*.py" -v
```

The checker enforces at least 15 percent free physical memory. An
envelope-only deterministic reseal from existing exact records is available:

```powershell
python -B verification\wave53-multi-root-wl\independent_check.py `
  --discovery attempts\wave53-multi-root-wl\exact-result.json `
  --output-dir verification\wave53-multi-root-wl `
  --assemble-existing
```
