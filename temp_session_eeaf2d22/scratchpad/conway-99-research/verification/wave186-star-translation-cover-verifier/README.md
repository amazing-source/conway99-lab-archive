# Wave 186 independent verifier

This package independently audits
`attempts/wave186-star-translation-cover`.  It does not import or execute
the discovery checker.

The verifier reconstructs:

- the two multiplicity-two star translates;
- the multiplicity-three companion and private-leaf translate;
- the private-label incidence bound;
- the capacity-three outside assignment;
- the distinct triple-companion lower bound; and
- the exact coefficient combination giving the `8/9` cover bound.

The verdict is `VERIFIED_WITH_SCOPE`:

```text
Q >= 3696,
projective short circuits >= 4389,
B_4+B_5+B_6+B_7+B_8+B_9 >= 8778.
```

The Wave 181 equality face `Q=2079` is thereby excluded.  The conditional
rank-11 endpoint and Conway 99 remain `UNKNOWN`.

Reproduce with:

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave186-star-translation-cover-verifier\independent_check.py `
  --verify `
  verification\wave186-star-translation-cover-verifier\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest -v `
  verification\wave186-star-translation-cover-verifier\test_independent_check.py
```
