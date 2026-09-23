# Wave191 exact-three residual verifier

This package independently verifies the frozen conditional Wave191 theorem:

```text
Q>=6237,
```

where `Q` counts projective short circuits cross-realizing graph nonedges in
the prism-free rank-11 endpoint model.

The verifier independently reconstructs:

1. impossibility of an exact-three private-leaf raw extraction;
2. orbit-closed assignment capacity of genuinely new residual circuits;
3. the joint use of exact-one raw slots by type-three and type-two
   assignments; and
4. the exact certificate

```text
12Q>=9I+6(p2-n2)+p2+3(p3-n3)>=18C.
```

The independent mathematical result was frozen before the Wave191 source
manifest or discovery files were opened.  The local exact-three raw branch
is `REFUTED`; the resulting conditional circuit theorem is
`VERIFIED_WITH_SCOPE`.

The package also records, without using it in the `Q>=6237` proof, a
Wave192 lever: a residual forced after an exact-two type-three raw cannot
itself be exact-two.

No graph, code, cover, endpoint, or Conway-99 solution is claimed.

## Replay

```powershell
.\.venv\Scripts\python.exe -B verification\wave191-exact-three-residual-verifier\independent_check.py --verify-math verification\wave191-exact-three-residual-verifier\independent-math-result.json
.\.venv\Scripts\python.exe -B verification\wave191-exact-three-residual-verifier\independent_check.py --verify verification\wave191-exact-three-residual-verifier\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest -v verification\wave191-exact-three-residual-verifier\test_independent_check.py
```
