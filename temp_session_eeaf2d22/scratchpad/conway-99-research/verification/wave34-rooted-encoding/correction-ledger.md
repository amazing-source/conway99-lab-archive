# Wave 34 rooted-encoding verifier correction ledger

The verifier does not rewrite candidate artifacts.  These corrections qualify
packaging or documentation only; none changes a formula byte, semantic
constraint, or mathematical status.

## W34-RC-V-001: post-freeze ledger is outside both candidate manifests

Severity: `PACKAGING`

The 16-entry publication manifest and 18-entry local manifest validate
exactly.  Their difference is exactly the raw CNF plus the publication
manifest.  However, the candidate's later
`attempts/wave34-rooted-encoding/correction-ledger.md` is in neither manifest.
The artifact manifest necessarily omits its own self-hash, but it also omits
this separately hashable ledger.

Correction:

```text
candidate correction-ledger SHA-256:
6daaa2c49cda2ca9e254210ebe64e493cf66cc66510ed6a711251e40e507ff0d
```

Therefore “18-entry complete local manifest” is historically accurate for the
pre-ledger freeze but not literally comprehensive after the ledger was added.
The verifier input and artifact manifests cover this gap.  Formula impact:
`NONE`.

## W34-RC-V-002: frozen preflight bytes are not reproduced by current generator

Severity: `REPRODUCIBILITY`

The frozen `encoding-preflight.json` is 5,676 bytes with SHA-256

```text
155f2e310238112d36f8eddac635f4b25fe40f4a417fb3efd59f1fbe5afb970a.
```

It lacks the per-variable-group `contiguous` metadata present in the published
generator and final `encoding-audit.json`.  Adding only those fields to the
frozen preflight yields the current-generator-shaped 5,877-byte document with
SHA-256

```text
6b8b5c8be9efd30580f9f5293ca02b2afb611f09747d7a54f264b9deb24372ff.
```

After removing emitted-formula fields and the added `contiguous` metadata,
every semantic count in preflight and final audit is identical.  The recorded
preflight command therefore reproduces the counts but not the pinned bytes
with the published generator.  Formula impact: `NONE`.

## W34-RC-V-003: decoder accepts complete primaries, not a complete DIMACS model

Severity: `DOCUMENTATION`

`decode_model.py` requires consistent values for variables `1..5950`.  It does
not require the 1,227,051 auxiliary variables and does not evaluate the CNF.
That is narrower than prose suggesting that it enforces a “complete DIMACS
assignment.”

The code correctly labels its output `DECODED_UNCHECKED`.  A passing complete
99-vertex adjacency under the independent graph checker would be a valid
positive certificate regardless of omitted auxiliary values, because the
verified equivalence gadgets give a unique auxiliary extension.  The safety
boundary is therefore preserved, but future prose should say “complete primary
assignment followed by the mandatory graph checker.”  Formula impact: `NONE`.
