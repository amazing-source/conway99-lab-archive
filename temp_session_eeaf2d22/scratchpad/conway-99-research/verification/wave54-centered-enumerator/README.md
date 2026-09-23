# Independent verification of the Wave54 centered formal enumerator

Status: `VERIFIED` for exact feasibility of the frozen ordinary-enumerator
conditions only.

The verifier froze its protocol before reading Wave54 discovery code, then
computed every ternary Krawtchouk coefficient from the direct binomial sum

```text
K_j(i)=sum_t (-1)^t 2^(j-t) C(i,t) C(231-i,j-t).
```

This is materially separate from discovery's three-term recurrence.  The
candidate

```text
{0:1, 18:2, 144:53316, 153:19798, 159:98496, 162:5072, 198:462}
```

has total size `3^11`.  Its full 232-entry MacWilliams transform consists of
nonnegative integers, has `B_1=B_2=0`, satisfies `B_i>=A_i`, satisfies every
listed dual lower bound, and sums to `3^220`.  All 232 independently computed
coefficients equal discovery's values.

This verifies a formal ordinary weight enumerator, not a ternary code or a
complete enumerator.  No centered point configuration, endpoint matrix,
`srg(99,14,1,2)`, or stricter `n3` upper bound is constructed or proved.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave54-centered-enumerator\independent_check.py `
  --verify verification\wave54-centered-enumerator\independent-results.json

.\.venv\Scripts\python.exe -B `
  verification\wave54-centered-enumerator\audit_discovery.py `
  --verify verification\wave54-centered-enumerator\discovery-audit.json

.\.venv\Scripts\python.exe -B -m unittest -v `
  verification\wave54-centered-enumerator\test_independent_check.py
```

The checker aborts when free physical memory is below 15 percent.  The tests
include a separate small-parameter generating-polynomial reconstruction and
hostile mutations of every frozen condition, transform equality, discovery
coefficient vectors, and manifest hashes.
