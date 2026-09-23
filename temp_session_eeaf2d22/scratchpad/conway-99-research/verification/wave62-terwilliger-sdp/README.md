# Independent verification of Wave 62

Status: **VERIFIED for the finite, declared one-point relaxation only**.

This package reconstructs the 84 signed-edge labels, all six relations, the
association scheme, its primitive idempotents, the rooted incidence
eigenspaces, the one-parameter endpoint averages, and the implemented
degree-24 Schur family without importing the discovery module.

The discovery numbers reproduce exactly:

```text
intersection tensor SHA-256: 44574bd2abfb7a909c85b2f52aacd72e9e73c84981d9d48da112a481e299b2ff
surviving integer y values:  0,...,42
implemented matrices:        1,949
endpoint scalar blocks:       23,388
positive / zero / negative:   23,316 / 72 / 0
```

The exact smallest positive block is

```text
2097151996002572622721189252991
------------------------------------------------
9499526251094051785686150082270420436779008
```

at multiplier `0`, powers `(P3,P-4)=(0,24)`, endpoint `h=0`, and the
14-dimensional scaffold block.

One minor documentation correction is required. The prose says all six
multipliers and all exponent pairs `a+b<=24`, which contains 1,950 triples.
The implementation explicitly omits the tautological triple
`(E_0,a,b)=(E_0,0,0)`, giving 1,949. Adding the omitted `E_0=J/84` produces
23,400 endpoint inequalities, 23,318 positive values, 82 zeros, and still no
negative value. The null conclusion is unchanged.

No target-graph automorphism is assumed. The scaffold group is used only
because conjugating any universally valid PSD Schur product preserves PSD,
and averaging those conjugates preserves PSD. The verifier checks generators
of `C2 wreath S7` only for preservation of the signed-edge orbitals.

The endpoint `n3=4158`, a strict upper bound, and Conway-99 remain `UNKNOWN`.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave62-terwilliger-sdp\verify_wave62.py `
  --expect verification\wave62-terwilliger-sdp\exact-verifier-result.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave62-terwilliger-sdp -p "test_*.py" -v
```
