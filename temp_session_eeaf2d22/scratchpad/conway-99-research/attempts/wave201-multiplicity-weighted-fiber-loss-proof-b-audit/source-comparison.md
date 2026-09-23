# Sealed source comparison

The Wave201 proof-A package manifest has SHA-256

```text
36d95b7d1bee4739cc5f33c780d22168fe58bf974904031db86d25da77bce695.
```

All 10 manifest entries match. Its exact replay passes and all six tests
pass.

The hostile audit agrees with the source on:

- the value-by-value same-fiber charge;
- all empty, singleton, and multiple-value baseline cases;
- exactly three degree-five baselines at a tight center;
- `delta>=3q-epsilon`;
- the derived row with floor 891;
- the nonnegative budget difference; and
- conditional `Q>=7059`.

No source repair was needed.
