# Wave155 clean-room feedback verification protocol

## Frozen discovery inputs

The assigned `attempts/wave155-four-root-feedback` directory did not exist.
The seven exact named artifacts were found under
`attempts/wave152-four-root-order8` and hashed before any inspection:

- `build_exact_cuts.py`
  `ffc57ca81560e90ac3f0f3cf27f84b5ed9af0e8fffb0c6e32079dfcc9bb73b70`
- `exact-cuts.json`
  `055b8253636167b85f68e09b1a470d4fe94e2d8bcfbe5eb02ade0e69ad73603d`
- `iteration2-cuts.json`
  `3652888b035ba2675cb860dcf59414f0b9e7e353e7f943ecfd1e37646718aa25`
- `zero-face-two-cuts-highs.json`
  `11a06307d898b10f0472a0908c5c775b00260672d9054f67c9adb7b30b6da005`
- `zero-face-four-cuts-highs.json`
  `22dc59c5d78660131bd755855029deab757e236ffc633fa75a4751b30bc86372`
- `exact-witness-after-two-cuts.json`
  `b36c592546f5e5b3f9159a82267a3cb7cefaf37e6ee7588b4e2ba0a5c65d07af`
- `exact-witness-after-four-cuts.json`
  `13fcdecd15da2a0c23abb71950fcda58e7f5e91b8caadc99d1e6e352aebeaeb9`

## Separation

No discovery Python file will be imported or executed. The verifier will
independently rebuild rooted flag semantics, primitive covariance
inequalities, exact witness evaluation, and retained linear equalities.

## Evidence boundary

Solver statuses remain diagnostic. Positive feasibility is accepted only
through exact rational witness replay. The scope is feasibility of the finite
relaxation after two and four feedback cuts, not a graph construction,
endpoint theorem, Conway-99 resolution, or strict bound.

## Resource boundary

The verifier must retain at least 15% host free memory. Initial free memory
was 26.70%.
