# Wave203 two-center incidence verifier

This package independently verifies the analytic two-center theorem

```text
m_(x->y)+m_(y->x)<=5
```

for canonical exact-three flags in the frozen prism-free rank-11
endpoint framework.  It checks the two five-slot systems, partial
third-block injection, `j(S,T)=2` reverse matching, global ternary
coefficient normalization, four-column distinctness, and the Wave181
Gram rejection of the resulting all-equal word.

The exact consequences are

```text
3n3+4p3<=5|U|,
epsilon>=5b.
```

No checked row forces `b>0`, so the conditional bound remains

```text
Q>=7059.
```

Run:

```powershell
.\.venv\Scripts\python.exe -B verification\wave203-two-center-incidence-verifier\independent_check.py --verify verification\wave203-two-center-incidence-verifier\independent-math-result.json
.\.venv\Scripts\python.exe -B -m unittest -v verification\wave203-two-center-incidence-verifier\test_independent_check.py
.\.venv\Scripts\python.exe -B verification\wave203-two-center-incidence-verifier\source_comparison_check.py --verify verification\wave203-two-center-incidence-verifier\source-comparison-results.json
.\.venv\Scripts\python.exe -B -m unittest -v verification\wave203-two-center-incidence-verifier\test_source_comparison_check.py
```

No graph, code, cover, flag-family, SAT, LP, configuration,
enumeration, isomorphism, or brute-force search is used.
