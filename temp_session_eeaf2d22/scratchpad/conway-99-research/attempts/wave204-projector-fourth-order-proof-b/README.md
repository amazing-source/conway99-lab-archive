# Wave 204 proof B: fourth-order projector detector

At the conditional prism-free centered-rank-11 endpoint, an adjacent pair
of vertex-star projectors reduces to one exact `6 by 6` matrix.  If `N` is
the biadjacency matrix of the outer `2`-regular bipartite graph, then

```text
A_xy=P_x P_y P_x restricted to E_x=N N^T.
```

The four Wave176 cycle types have alternating fourth traces

```text
type                         6  4+2  3+3  2+2+2
tr(P_x P_y P_x P_y) in F_3  0   1    0     0
```

Thus the fourth trace, equivalently the exterior-square trace, detects
exactly the adjacent `4+2` type.  This is a conditional local theorem, not
an endpoint exclusion.

The package also contains two deliberately non-graph abstract controls with
99 projectors and 231 labelled columns.  They have the same pairwise
projector trace Gram but different fourth-trace matrices.  Every satisfied
and failed endpoint premise is listed in `exact-results.json` and
`failed-routes.md`.

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave204-projector-fourth-order-proof-b\exact_check.py --verify attempts\wave204-projector-fourth-order-proof-b\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave204-projector-fourth-order-proof-b\test_exact_check.py
```

Status: `DERIVED_PENDING_INDEPENDENT_VERIFICATION`.
