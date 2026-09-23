# Wave 27 A2-free construction verifier failure ledger

No mathematical or certificate defect was found.

## Procedural notes

- The seven intended discovery artifacts were hash-frozen before the report or
  checker was opened. A transient root replay file mentioned by the
  orchestrator was absent from the frozen list and had no effect on the audit.
- The independent checker was written as a fresh standard-library
  reconstruction. It does not import the discovery checker.
- The submitted checker was replayed only after the independent reconstruction
  had passed. Its regenerated JSON was byte-identical to the submitted JSON.

## Scope attacks retained

- The root graph test distinguishes an embedded `A2` root subsystem from an
  orthogonal `A2` direct summand. The former is present; the latter is excluded.
- `B` is not Euclidean-symmetric in the displayed coordinates. The verified
  requirement is the exact identity `B^T G = G B`.
- No projector-frame, Schur-square, cubic-tensor, primitive-embedding, or graph
  premise was inferred from the abstract matrices.
- The verdict does not classify all determinant-nine forms and does not exclude
  `n3=708`.
