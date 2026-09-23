# Wave 205 proof A: nonedge fourth trace

Status: `DERIVED` and `REFUTED`, pending independent verification.

For every nonedge in the conditional prism-free endpoint, the exact
two-center cross Gram has:

```text
marked corner [[1,2],[2,1]],
marked row/column profile 0^0 1^5 2^2,
ordinary integer row/column sum 6.
```

If `t_xy` counts its entries equal to two, then

```text
t_xy>=6,
average t_xy=7,
tr(P_xP_y)=2t_xy,
h_xy=tr((C C^T)^2).
```

A complete normalized census has 646 matrices at `t=6` and 7,886 at
`t=7`.  Rank-11 nonsquare modules with true-relation distance at least four
exist at `t=6`, refuting a local proof of `t>=7`.  At `t=7`, such modules
exist for every `h=0,1,2`.

Four explicit 28-vertex adjacency certificates are checked without a
solver and embedded exactly in the fixed nonsquare 11-space.  They are
local controls, not 99-vertex graphs.

Reproduce with:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave205-nonedge-fourth-trace-proof-a\exact_check.py --verify attempts\wave205-nonedge-fourth-trace-proof-a\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave205-nonedge-fourth-trace-proof-a\test_exact_check.py
```

The inflection is a sealed obstruction: pair-local fourth-order data cannot
advance without a simultaneous 99-center extension invariant.

