# Wave 26 A2 cubic verifier: failures and limitations

## Procedurally contaminated auxiliary route

A nested normalization scout used an exclusion glob that did not work as
intended on Windows and saw snippets of the prohibited Wave 26 report before
finishing. Its derivation is excluded from the evidence for the verdict. The
main verifier had already obeyed the inspection wall, and its own checker,
tests, result, and hashes were frozen before candidate inspection.

## Active-premise hostile control

The inequality does not follow from the notation `M=X S X^T` alone. An exact
eight-row antipodal control with `S=A2 direct_sum A2` has:

```text
integral rows: true
full column rank: true
every row norm: 4
M 1=0: true
tr(A2 Q_AA): 0
tight frame X^T X=21 S^-1: false
public off-diagonal M alphabet: false
```

This is a dropped-premise control, not a candidate projector or graph.

## Redundant premise found

`M 1=0` is not required for the floor 18. The tight-frame block already
forces seven rows on each of the three root lines, making all three signed
imbalances odd. `M 1=0` only restricts them to `(t,t,-t)`.

## Terminology defect

The discovery prose sometimes says “231-column realization,” while its
correct displayed matrix is `X in Z^(231 x 44)` and the 231 frame objects are
rows. No algebraic orientation error follows from this wording.

## Tooling-only blocked command

A combined PowerShell command that created and then deleted a temporary
regeneration file was rejected by the execution policy before it ran. No file
was created and no mathematical check failed. Determinism was instead checked
inside the 17-test Python suite, which writes two temporary outputs and
compares their bytes; the ordinary checker generation was also rerun
separately.

## Scope limitations

- No actual 231-row frame, projector matrix, or graph is available.
- The result is conditional on the full projector/tight-frame and Schur-square
  origin.
- Only the stronger origin of the explicit Wave 24 survivor is refuted.
- Other determinant-nine forms and all other index survivors are unclassified.
- This is not an `h=9` exclusion and not an `n3=708` endpoint exclusion.
- Conway-99 existence and novelty remain `UNKNOWN`.
