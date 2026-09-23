# Failed or corrected verifier routes

## Absolute float cutoff

An initial comparison counted every `float64` eigenvalue below `-1e-5`.
This is not stable for large, singular raw integer matrices: roundoff near
the nullspace can create tiny signed values.  The exact matrix hashes had
already matched, so this was a diagnostic convention mismatch rather than a
coefficient failure.

## Denominator-relative float cutoff

A second attempt interpreted the sealed reporting cutoff as `-1e-8` times
the probability-normalization denominator.  This reproduced some families
but excluded genuine reported directions in `root_000`.

The sealed counts across all 136 exact matrices are reproduced by the
scale-relative convention `eigenvalue < -1e-8 * spectral_radius`.  The final
verifier records both this reported count and an independent backward-error
robust count.  Neither is used as an exact certificate; all mathematical
promotion relies on direct integer quadratic values.
