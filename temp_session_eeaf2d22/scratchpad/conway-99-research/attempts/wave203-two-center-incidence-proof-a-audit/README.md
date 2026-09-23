# Wave 203 proof-A hostile audit

This package independently audits the sealed Wave203 two-center theorem:

```text
m_(x->y)+m_(y->x)<=5,
3n3+4p3<=5|U|,
epsilon>=5b.
```

It verifies the shared-slot identification, reverse matching,
leaf-normalized relation addition, distinct columns, and the
all-equal-versus-checkerboard Gram obstruction. It confirms that no
`Q>=7060` claim follows without a separate proof that `b>0`.

Run:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave203-two-center-incidence-proof-a-audit\exact_check.py --verify attempts\wave203-two-center-incidence-proof-a-audit\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave203-two-center-incidence-proof-a-audit\test_exact_check.py
```
