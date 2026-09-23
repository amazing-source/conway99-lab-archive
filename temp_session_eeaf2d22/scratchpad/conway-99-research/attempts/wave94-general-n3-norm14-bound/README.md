# Wave 94: general prism-sensitive `N14` upper bound

Status: `DERIVED`; independent verification required.

For every hypothetical target graph, exact rooted prism counting gives

```text
N14 <= floor((38808+12P)/7)
     = floor((55440-4*n3)/7).
```

The theorem counts both signs and assumes neither prism-freeness nor
rank 28. It bounds only the norm-14 shell.

Run:

```powershell
python -B attempts/wave94-general-n3-norm14-bound/exact_check.py
python -B attempts/wave94-general-n3-norm14-bound/exact_check.py `
  --verify attempts/wave94-general-n3-norm14-bound/exact-results.json
python -B -m unittest discover `
  -s attempts/wave94-general-n3-norm14-bound `
  -p "test_*.py" -v
```

