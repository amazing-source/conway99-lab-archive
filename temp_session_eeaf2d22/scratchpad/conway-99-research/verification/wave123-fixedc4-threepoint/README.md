# Wave 123 independent verification

Verdict: `VERIFIED_SCOPED`.

A clean-room standard-library verifier confirms:

- the displayed 40-record family violates the `4/9` leverage bound at 46
  coordinates;
- its first 26 records violate it at six coordinates;
- the explicit alternate 26-record subset passes every diagonal row;
- that subset satisfies 2,340 rooted product-Johnson feature-Gram PSD
  blocks;
- exactly 352 of its 4,851 coordinate pairs admit neither graph-valued
  projector entry in the two-by-two PSD test.

The 30-restart search was not replayed because no exhaustive search
certificate was retained.  Its scope is correctly `NONEXHAUSTIVE`; it proves
no cap or nonexistence statement.

No rank is excluded.  Existence of some other graph-compatible 26-word
family, both local caps, Conway-99, and novelty remain `UNKNOWN`.

Reproduce:

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave123-fixedc4-threepoint\independent_verify.py `
  --verify `
  verification\wave123-fixedc4-threepoint\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave123-fixedc4-threepoint -p "test_*.py" -v
```
