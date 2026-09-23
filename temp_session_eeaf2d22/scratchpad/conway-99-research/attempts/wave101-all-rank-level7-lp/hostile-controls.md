# Hostile controls

- Frozen-manifest SHA-256 values are checked before any calculation.
- The modular product basis must have dimension exactly 15.
- The rational Fricke matrix must square exactly to the identity.
- Replacing `-7^(11-q/2)` by a wrong sign or power breaks `y0=1` or the
  canonical result.
- Every dual multiplier is checked as an exact nonnegative `Fraction`.
- Every claimed optimum has a matching exact feasible primal point.
- All 22 coordinate forms `x7,...,x14,y1,...,y14` are checked nonnegative.
- Every parity-rounded bound is compared with the exact rational bound.
- The full Wave 71 affine mod-7 directions are checked for each objective;
  no fixed residue is silently assumed.
- Exact zero-prefix controls are retained to prevent reporting a positive
  short-shell bound where none exists.
- Rigorous mod-2 lattice upper bounds are compared explicitly; no
  contradiction is reported.
- The computation refuses to start below 15 percent free physical memory.
- Unit tests replay discovery arithmetic only and are not called an
  independent verification.
