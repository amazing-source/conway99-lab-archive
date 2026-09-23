# Wave 49 failed and bounded routes

## Frozen aggregate witnesses

The Wave43 unrooted witness, Wave44 rooted witness, and all fifteen immutable
Wave45 witnesses fail the five-root PSD layer. Every one of their 21 matrices
is exactly indefinite (357 of 357 total). These failures do not imply that the
full endpoint count region is empty.

## Floating common-margin scout

Clarabel returned `optimal_inaccurate` with common margin about `-6.95e-6`,
but the worst full Wave49 eigenvalue was only about `-5.63e-9`. This scale
mismatch and solver status make the outcome a boundary diagnostic, not robust
infeasibility. A planned SCS cross-check was stopped before publication and no
SCS output is part of the sealed package.

## Exact dual route

The floating dual matrices were retained, but no complete rational dual
certificate was reconstructed or independently checked. Consequently neither
endpoint exclusion nor a strict upper bound is proved.

## Symmetry shortcut

No target-graph automorphism restriction was used. Canonical roots are valid
only because all 120 coordinate relabellings were checked coefficientwise for
each of the 21 representatives.
