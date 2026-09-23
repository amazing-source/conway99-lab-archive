# Wave130 cutoff-28 independent verification

## Verdict

`VERIFIED_SCOPED_FINITE`

The exact claim promoted is:

> The rank-28, discriminant-16, level-7 index-10/index-70 Jacobi
> necessary-condition relaxation has a rational feasible point through
> Fourier cutoff 28.

## Seal and separation

The verifier first checked the frozen discovery manifest:

```text
MANIFEST.sha256:
  8b1da27e3acaa059934704a85aaa380e101e1db330925ced6e048330d318e3ae
entries replayed:
  34
candidate:
  result-cutoff28-warm.json
candidate SHA-256:
  05ad8cf461cc7c79f85300d45492f1f30e3c1030a3c1943a9da3984d5add39a3
```

The verifier is a separate standard-library implementation.  It does not
import `jacobi_lp.py`, `exact_cdd_lp.py`, the discovery verification routine,
or any discovery module.  It does not deserialize a cached column file and
does not solve the LP.

## Independent reconstruction

From the formulas alone it rebuilt:

- `phi_{-2,1}` with q-zero coefficients `(1,-2,1)`;
- `phi_{0,1}` with q-zero coefficients `(1,10,1)`;
- all eleven modular blocks of dimensions
  `(15,17,17,19,21,21,23,25,25,27,29)`;
- the exact level-7 Fricke involutions and eigenbases;
- all 239 L/K Fourier columns through cutoff 28; and
- every unreduced constant, holomorphy, positivity, graph-gap, graph-support,
  and second-moment row.

The reconstructed-column digest is
`3b2b4b2bff82f42e84db73c0ac9cce5bad30104030f3e9f45642e28da99df65a`.

## Exact replay

Substitution of the sealed rational coordinates gave:

```text
454 equalities:     all exact
1686 inequalities: all nonnegative
506 tight labels:  exact ordered agreement with the candidate
failed rows:        none
solution digest:    3115657abca466038086de7d4c98eb262156d8655e73a66e3a5cf9266ac209e8
```

## Status wall

This verifies only a finite necessary-condition null result.  It neither
constructs nor excludes a graph or lattice, proves neither rank-28
realizability nor rank-28 exclusion, and leaves Conway-99 and any novelty
claim `UNKNOWN`.
