# Retained failed runs and non-evidence

## Frozen direct 44-dimensional enumeration timeout

The candidate freeze records an exploratory direct reverse-LDL enumeration
that exceeded 124 seconds and was stopped. It emitted no complete census or
certificate. This verifier did not replay or use it. The accepted root result
comes from complete exact enumeration in the six orthogonal blocks, followed
by an exact norm/parity dynamic program.

Status: `TIMEOUT_NON_EVIDENTIARY`.

## Superseded intake hashes

The candidate freeze changed twice while verification was in progress:

```text
2ed4ad75b65bc071a39a61ec639929df57231b80e26e3ba2280e23978c7a360e
  initial-support-only freeze

2dac23f1f859ef25eaef487c482b744f726c202c6b9d6bcb9d745bc57627c74e
  preferred-support freeze before the rank-one glue targets

7b8fce3763e2f6d4db2e0f7841e680d01486195d3ea4b6b04c5f59ace768d90a
  final intake used by this audit
```

The checker failed closed when the second hash drifted to the final hash.
Earlier computations were not relabeled against the changed input. The final
result and tests bind only the last hash.

Status: `INPUT_DRIFT_HANDLED_FAIL_CLOSED`.

## Incorrect first hostile mutation

The first test draft assumed that replacing preferred support coordinate 41
with 42 would break at least one simultaneous-neighbor scalar invariant.
Independent reconstruction instead gives

```text
v^T S v = 16,
a^T Q a = 16,
a^T G a = 336
```

for that mutation as well. The failed assertion was a test-design defect, not
a candidate defect. The final suite retains this equality as a positive
control and uses the independently checked replacement `41 -> 2` as the
negative control, where the three values are `14,14,294`.

Status: `HOSTILE_TEST_ASSUMPTION_REFUTED_AND_RETAINED`.
