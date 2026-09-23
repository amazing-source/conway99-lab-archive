# Wave157: general cube/Wagner cut

This bounded lane derives the symbolic form hidden by the endpoint-only
primitive cut:

```text
41580 - n3 + 12*C8 - 4*W8 >= 0.
```

`C8` is the induced cube count and `W8` the induced Wagner/Möbius-ladder
count. At `n3=4158`, the formula reduces to the stored endpoint cut

```text
18711 + 6*C8 - 2*W8 >= 0.
```

The derivation starts from the SRG parameters, pointwise-labelled root mask
12, flag masks `21812` and `22708`, and the statically parsed independent
Wave43 formula `N_9=41580-n3`. It does not import or execute discovery code.

The result does not prove a strict upper bound: the endpoint with
`C8=W8=0` satisfies the inequality with slack `37422`. A separate relation
forcing Wagner counts far above cube counts would be needed.

## Files

- `derivation.md`: human-checkable mathematical derivation.
- `derive_symbolic_cut.py`: standard-library exact enumerator.
- `exact-results.json`: machine-readable derived certificate.
- `test_derive_symbolic_cut.py`: exact regression checks.
- `protocol.md` and `input-freeze.sha256`: frozen scope and inputs.
- `run-report.yaml` and `package-manifest.sha256`: reproducibility metadata.

## Reproduce

```powershell
python attempts\wave157-general-cube-wagner\derive_symbolic_cut.py
python -m unittest attempts\wave157-general-cube-wagner\test_derive_symbolic_cut.py -v
```

Status is `DERIVED`; independent verification remains a separate role.
