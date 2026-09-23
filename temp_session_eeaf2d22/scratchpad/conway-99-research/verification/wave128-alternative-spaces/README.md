# Wave 128 independent verification

Verdict: `VERIFIED_SCOPED`.

The sealed discovery package was preinspected before execution.  A clean-room
standard-library checker then rebuilt the `C4 Cartesian K3` incidence
multiset, the primitive matrix `Q=[one P]`, its Gram matrix, and the induced
action of `B=D+4I`.  It used a separate integer Smith-normal-form reduction
and independently enumerated the finite quadratic modules.

The verifier confirms, conditional on the frozen motif and the verified
Wave 109 projector:

```text
A_U,(7') = Z/256 + Z/4 + (Z/9)^2 + (Z/3)^2 + (Z/5)^2
A_K,(7') = (Z/8)^4 + Z/9 + (Z/3)^2

A_U,7 = A_K,7 = (Z/7)^k, both of type O^-(k,7),
k=16,18,...,30.
```

It also confirms `min(U),min(K)>=4`.  No imported row is excluded.
No lattice, outside graph, motif extension, or Conway graph is constructed.
Those claims and literature novelty remain `UNKNOWN`.

Reproduce:

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave128-alternative-spaces\independent_verify.py `
  --verify verification\wave128-alternative-spaces\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave128-alternative-spaces -p "test_*.py" -v
```
