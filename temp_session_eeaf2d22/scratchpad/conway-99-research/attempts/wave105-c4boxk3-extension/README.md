# Wave 105: `C4 box K3` full-extension boundary

Status: sealed discovery candidate; independent verification required.

This package tests the first parity-cancelling prism motif exposed by
Wave 102. Exact block counting forces the 87 outside vertices into

```text
|X0|=3, |X1|=48, |X2|=36
```

according to whether they have zero, one, or two motif neighbors. The
outside graph has 549 edges. An archived outside graph passes the entire
degree and linear block equation. It is only a linear-layer witness: it
does not satisfy or test every outside pair codegree.

Aggregate common-neighbor moments leave
`18,11,5,1` degree rows according to `e(X0)=0,1,2,3`; exact graphicality
removes one row.

The full solver lane has 3,741 outside-edge variables and 317,985 explicit
common-neighbor conjunction variables. It covers the full motif-extension
domain, split only by the four isomorphism types of the three-vertex
`X0` graph.

Bounded solver runs remain `UNKNOWN` unless a SAT adjacency is directly
checked or an UNSAT proof is independently replayed.

Reproduce the exact finite boundary:

```powershell
python -B attempts\wave105-c4boxk3-extension\motif_search.py --summary
.\.venv\Scripts\python.exe -B `
  attempts\wave105-c4boxk3-extension\motif_search.py `
  --linear-witness --branch-eX0 0
python -B -m unittest discover `
  -s attempts\wave105-c4boxk3-extension -p "test_*.py" -v
```

Run one bounded complete-domain branch:

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave105-c4boxk3-extension\motif_search.py `
  --solve-seconds 45 --branch-eX0 0
```
