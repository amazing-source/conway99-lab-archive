# Wave 24 verifier failure and hostile-control ledger

No mathematical defect was found in the frozen discovery claim.

## Retained harness issue

Before candidate inspection, the first PowerShell command used
`[System.IO.Path]::GetRelativePath` to label the hash freeze.  That method is
not available in the host's loaded .NET surface.  SHA-256 computations
completed, but path labels were blank, so that output was discarded.  The
freeze was immediately repeated using a checked workspace-prefix removal,
producing the complete eight-entry `preinspection-freeze.sha256` before any
candidate content was opened, imported, or executed.

This was a path-labeling failure only; it supplied no mathematical evidence.

## Hostile controls that correctly fail

1. Dropping integrality permits `C=(2/11)I_44`.  It has trace eight,
   `tr(C^2)=16/11`, and
   `det(I+2C)=(15/11)^44>6561`.
2. Dropping positive-form self-adjointness permits an integral matrix with
   eight diagonal ones and a skew block `[[0,-2],[2,0]]`.  It has trace
   eight and determinant `17*6561`, but nonreal eigenvalues.
3. Dropping `h!=1` restores `h=1`.
4. Dropping `h=1 mod 4` restores both `h=3` and `h=7`.
5. Adding one to a diagonal entry of the survivor's `G` breaks evenness.
6. Adding two to `B[0,0]` preserves its parity class but breaks `GB=21Q`.
7. Reusing the old endpoint `Delta=12` would reject a single `q=11`;
   the correct `Delta=15` permits one, while the centered pair minor still
   excludes two.

All seven controls are checked exactly in `test_independent_check.py`.

## Submitted replay

The frozen submitted suite passed all 15 tests.  Fresh submitted JSON
regeneration was byte-identical to `exact-results.json`, with SHA-256

```text
a4241cdeea64a8f6073037d564e72fb7ef545287d45aca4759cec6c31d26a463.
```

Solver exits and test counts are treated as replay evidence only; the
continuum inequality and theorem hypotheses are audited in
`theorem-applicability.md`.
