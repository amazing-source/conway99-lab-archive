# Independent verification of Wave132

Verdict: **VERIFIED** for the conditional pair identities, high-weight cut,
and rational low-degree split-enumerator feasibility.

This verifier binds sealed discovery manifest
`0b99e87b0f39b1c203709d34ffba3f7b5c94f0078c53fe4020dfc3cd03ec510c`
and imports no Wave132 discovery or checking implementation. It uses only
standard-library exact integer and `Fraction` arithmetic.

The replay independently confirms:

- all 200 forward and inverse binary Krawtchouk/MacWilliams rows;
- nonnegativity, sizes `2^54` and `2^45`, minima 14 and 15, forced lower
  bounds, even image support, and dual complement symmetry;
- all row sums, first moments, parity counts, and intersection ranges in all
  four distinguished split families;
- the distinguished pair tables and their forced lower rows;
- the image-weight bound `w<=92`, including `A94=A96=A98=0`;
- the exact positive Wave131 `A98`, while that older point still passes all
  200 ordinary MacWilliams rows; and
- the independent state counts 171,700 raw compositions, 42,925 even-even
  states, and 7,803 `GL(2,2)` orbits.

The bounded integral timeout remains non-evidentiary. Integral feasibility,
full genus-two feasibility, code realization, graph realization, and
Conway-99 remain **UNKNOWN**.

Reproduce:

```powershell
.\.venv\Scripts\python.exe -B `
  verification/wave132-distinguished-biweight/verify_wave132.py `
  --repository . `
  --package attempts/wave132-distinguished-biweight `
  --expected-manifest 0b99e87b0f39b1c203709d34ffba3f7b5c94f0078c53fe4020dfc3cd03ec510c `
  --write verification/wave132-distinguished-biweight/verification.json
```
