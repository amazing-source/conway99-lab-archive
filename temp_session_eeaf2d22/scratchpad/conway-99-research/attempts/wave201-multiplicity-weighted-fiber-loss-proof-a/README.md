# Wave 201: multiplicity-weighted fiber loss

This analytic package proves the local/global row

```text
delta>=sum_nonprivate(m-2)=3q-epsilon
```

by charging repeated leaves inside each four-element pair fiber and
subtracting exactly the three Hilton--Milner baseline repetitions at a
13-flag center. It forces certificate budget `B>=891` and the conditional
bound `Q>=7059`.

Run:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave201-multiplicity-weighted-fiber-loss-proof-a\exact_check.py --verify attempts\wave201-multiplicity-weighted-fiber-loss-proof-a\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave201-multiplicity-weighted-fiber-loss-proof-a\test_exact_check.py
```

No search is performed.
