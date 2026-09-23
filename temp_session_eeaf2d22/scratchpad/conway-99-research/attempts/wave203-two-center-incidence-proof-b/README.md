# Wave 203 proof B: two-center incidence

For one nonedge `{x,y}`, exact-three flags in the two directions share
five third-block slots. The flag-to-third-block map is injective, and a
matched reverse flag would force a forbidden all-equal relation on the
canonical four-column quadrilateral. Therefore

```text
m_(x->y)+m_(y->x)<=5.
```

Every both-oriented selected label consequently contributes at least
five units to the Wave198 multiplicity deficit `epsilon`.

Run:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave203-two-center-incidence-proof-b\exact_check.py --verify attempts\wave203-two-center-incidence-proof-b\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave203-two-center-incidence-proof-b\test_exact_check.py
```

No Wave202 proof-A note was opened and no search is performed.
