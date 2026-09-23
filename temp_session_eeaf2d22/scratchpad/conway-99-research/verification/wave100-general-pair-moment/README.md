# Wave 100 independent verification

Status: `VERIFIED SCOPED`.

For every hypothetical `srg(99,14,1,2)`, with `N14` counting both signs,
the verifier proves

```text
7*N14 <= 34650+15P = 55440-5*n3
N14 <= 2*floor((55440-5*n3)/14).
```

No prism-free or rank-28 assumption is used. This is a general upper bound
on the norm-14 shell as a function of `n3`; it is not an upper bound on
`n3` itself.

The clean-room result was sealed before the Wave 100 derivation or code was
opened. Unlike the discovery arithmetic checker, the independent verifier
also enumerates all 10,395 general local perfect matchings and confirms that
mate-forbidden transitions lie in no seeds while the co-incidence cap 18
continues to apply to every seed-eligible transition.

Reproduce:

```powershell
python -B verification\wave100-general-pair-moment\independent_verify.py `
  --verify
python -B verification\wave100-general-pair-moment\compare_discovery.py `
  --verify
python -B -m unittest discover `
  -s verification\wave100-general-pair-moment -p "test_*.py" -v
```
