# Wave 49: exact five-root moment layer

Status: **CANDIDATE**. The endpoint `n3=4158` remains **UNKNOWN**. No strict
upper bound, graph, or exact infeasibility certificate is claimed.

## Exact construction

For a pointwise-labelled admissible root `sigma` on five vertices, the flag
coordinate is the five-bit neighborhood of one free vertex. For each labelled
root embedding `theta`, let `c(theta)` be the integer vector of attachment
counts. The matrix

```text
M_sigma = sum_theta c(theta)c(theta)^T
```

is PSD in every graph. Its diagonal same-free terms have union order six; its
ordered distinct-free terms have union order seven. Coefficients count labelled
root embeddings directly, with no automorphism division.

The run independently regenerated the `21/62/208` canonical admissible class
streams through order seven, constructed sparse tensors for all 683 labelled
admissible five-root masks, and reduced them to the 21 canonical families with
the requested dimensions. All `21*120=2520` root-permutation mappings passed
exact coefficientwise congruence. This is a coordinate-relabel theorem:
`M_{pi(sigma)}=P_pi M_sigma P_pi^T`; it assumes no target-graph automorphism.

Petersen and Clebsch direct outer-product controls agreed with the coefficient
expansions for all 42 graph/family pairs. On the 17 immutable Wave43/44/45
aggregate witnesses, all 357 matrices were exactly indefinite. Each result
includes an integer negative direction and exact negative quadratic numerator.
This refutes those 17 aggregate points only.

## Numerical scout

The 21 normalized matrices were appended to the sealed Wave48 real SDP. The
stable Clarabel run returned `optimal_inaccurate`, common margin
`-6.948173993109943e-06`, worst Wave49 full eigenvalue
`-5.630551168455903e-09`, and scaled count-equation residual
`3.1086244689504383e-15`. The candidate, all 208 probabilities, exact
integer-vector PSD cuts, residuals, and floating dual matrices are retained in
`combined-sdp-result.json`.

This is a near-boundary numerical diagnostic, not infeasibility evidence. No
exact rational dual certificate was extracted.

## Files and reproduction

- `coefficients.json`: complete exact 21-family order-6/order-7 coefficient
  package.
- `results.json`: exact relabelling, controls, witness matrices, inertias, and
  negative directions.
- `combined-sdp-result.json`: floating numerical scout only.
- `compact-handoff.json`: verifier-facing summary and artifact hashes.
- `protocol.md` and `verifier-protocol.md`: frozen conventions and clean-room
  verification boundary.

From the repository root:

```powershell
.\.venv\Scripts\python.exe attempts\wave49-five-root-moment\five_root_moment.py --verify
.\.venv\Scripts\python.exe -m unittest attempts\wave49-five-root-moment\test_wave49_package.py
```

The exact replay takes roughly two minutes on the construction host and aborts
before any phase that would leave less than 20% free physical memory. The
recorded minimum during discovery was 61.82%.
