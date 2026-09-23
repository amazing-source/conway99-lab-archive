# Wave 60 clean verification

This package independently verifies the exact finite content of
`attempts/wave60-c3-incidence-design`.

The verified scope is:

- `216 -> 50 -> 18` component classification;
- `1,140 -> 275` safe simultaneous-fibre coordinate reduction;
- the complete target `F2` rank histogram and its zero eliminations;
- all-triple candidate-support counts;
- direct aligned type-4 enumeration of 20,928 columns and 21 patterns; and
- the local-pair marginal reduction forcing 60 columns and row sum 10.

The bounded SAT and local-search outputs remain `UNKNOWN`.  No incidence
design, exclusion, endpoint contradiction, or Conway-99 resolution is
claimed.

Run:

```powershell
.\.venv\Scripts\python.exe -B verification\wave60-c3-incidence-design\test_independent_verify.py
.\.venv\Scripts\python.exe -B verification\wave60-c3-incidence-design\independent_verify.py
```

See `audit.md` for the verdict and `protocol.md` for separation and promotion
rules.
