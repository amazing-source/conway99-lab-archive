# Wave 30 h729 construction verifier failure ledger

No mathematical check failed in the final replay. The following failed or
nondecisive events are retained.

## V30-C-F001: overly literal scope-list gate

- Event: the first verifier run stopped before arithmetic because it required
  every string `Q`, `B`, `X`, `M`, `W`, `frame`, `Schur`, and `graph` to occur
  literally in the JSON `not_constructed` list.
- Cause: the submitted list spells out `Q`, `B`, `X`, `M`, frames, and graph,
  while the frozen report and run report separately disclaim `W` and the
  Schur identity.
- Disposition: verifier defect, repaired transparently. The replacement gate
  checks the exact submitted nonconstruction sentences, rejects embedded
  downstream-certificate keys, and retains the complete status wall in the
  verifier output.
- Mathematical effect: none; no matrix arithmetic had run.

## V30-C-F002: literal `UNKNOWN` token gate

- Event: the second verifier run stopped before arithmetic because it required
  the literal token `UNKNOWN` in two restriction strings.
- Cause: the JSON says that the construction “neither realizes nor excludes
  n3=708” and “does not resolve Conway-99,” and says that no frame subset is
  supplied. Those are explicit nonresolution statements without the literal
  token.
- Disposition: verifier defect, repaired to require those exact substantive
  disclaimers. The independent result records both statuses as `UNKNOWN`.
- Mathematical effect: none; no matrix arithmetic had run.

## V30-C-F003: vector-set digest encoding mismatch

- Event: the first successful verifier result used a newline-delimited
  coordinate-set digest, so its shell digests differed from the submitted
  canonical-JSON digests despite identical exact counts.
- Disposition: both encodings were applied to the independently enumerated,
  lexicographically sorted coordinate sets. Canonical JSON reproduced every
  submitted root-shell digest and the decisive norm-four digest
  `7b83bccafcd31ee04e0c028f10f51363d3c3b0a22f5f87dc9bbbd14875ca6010`.
  The final verifier emits the comparable canonical digest.
- Mathematical effect: none; this was a serialization difference, not a
  coordinate-set discrepancy.

## Retained discovery nonresults

- The discovery lane's 30-second restricted Z3 frame scout returned
  `unknown`. It is not a witness or a nonexistence result and is not used here.
- The discovery lane stopped a generic Leech norm-four enumeration after four
  minutes. This verifier does not convert that timeout into evidence. Leech
  minimum four is established instead by a complete norm-two enumeration,
  exact even positive definiteness, and an explicit norm-four basis vector.
- The five displayed 2-neighbors are a verified construction route, not a
  complete neighbor-graph search or an isometry classification.

## V30-C-F004: orchestrator publication-byte normalization

The final read-only package audit found extra terminal blank lines in
`audit.md`, this ledger, `run-report.yaml`, and
`test_independent_check.py`. Before the verifier package was committed, the
orchestrator normalized each file to one terminal LF and refreshed every
dependent run-report and manifest hash.

The pre-normalization hashes remain recorded here:

```text
eb0f6031628a981326395e06b2f08b6efdb0f11a73793e397ca7b00523b4cb5d  test_independent_check.py
b5511b585e8a3bb401f224e0e0a09f76378fdc9c21b929b428972d5e4f4d8b01  audit.md
16d56a61650b14127b1e4a5051b9f38831b3d0ee93f9e6adeb5d48c71f9b09f5  failure-ledger.md
31c676899531e21dfcf958ba84c8f90cd65fef446c916ee7344d03061bede359  run-report.yaml
098a129d56348b1cbafabe0478621f2a9db19216b2e5611beb1a05dc5bec2ffd  artifact-manifest.sha256
```

No discovery byte, matrix, shell, mathematical conclusion, or status
boundary changed.

## Hostile final replay

All 24 hostile tests pass. They independently compare the exact ellipsoid
enumerator with a Cartesian exhaustive search in dimension three and reject:

- nonsymmetry, oddness, and indefiniteness;
- mutated or transposed neighbor bases;
- a nonunimodular alleged LLL transform;
- deleted or wrong supports and parity pivots;
- a false submitted inverse or following Gram matrix;
- cross-block coupling in `S`;
- a false scaled dual;
- missing nonconstruction disclaimers; and
- global status inflation.
