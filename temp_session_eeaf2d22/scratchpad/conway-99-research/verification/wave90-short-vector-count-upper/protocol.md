# Wave 90 clean-room verification protocol

Date frozen: 2026-07-28 UTC.

Role: verifier.

The discovery manifest was hashed and every discovery file was inventoried
before inspection.  The verifier will not import or execute discovery code.

## Scope to reconstruct

Under the prism-free endpoint hypothesis `P=0` (equivalently `n3=4158`),
audit the claimed bound

```text
N14 <= 5544,
```

where `N14` counts both signs of every integer `-4` eigenvector of squared
norm 14.  The theorem must not silently assume `r=28`.

## Hostile questions

1. Does a norm-14 eigenvector determine both seven-point sign classes?
2. Does fixing a root and one sign class lose a sign or orientation factor?
3. Is the complementary-Fano seed map injective?
4. Are there exactly 84 selected transitions and at most eight seeds per
   transition?
5. Does prism-freeness really bound each seed by four transitions?
6. Is the final double count `7*N14 <= 99*392` correctly oriented?

Discovery prose and solver exits are not certificates.
