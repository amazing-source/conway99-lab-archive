# Wave 204 proof A: global slot-holonomy boundary

This package separates two exact statements in the conditional prism-free
rank-11 endpoint.

1. On the **actual triangle-block transition digraph**, every selected flag
   gives an arrow `S -> T` with gain

   ```text
   g(S->T)=z_T-z_S.
   ```

   The gain is a coboundary.  Every genuine closed block cycle therefore has
   zero holonomy by telescoping.

2. Wave 203 does **not** supply a transition on graph centers or a permutation
   of five slots.  Its maps are partial injections for one nonedge at a time.
   The target block of an `x->y` flag need not equal the source block of a
   `y->z` flag.  Hence center-triangle, center-quadrilateral, and center-
   pentagon holonomy is undefined at the frozen interface.

The exact controls in `exact-results.json` use the nonsquare ternary form
`diag(1,...,1,2)` in dimension 11.  They give directed center cycles of
lengths 3, 4, and 5 in which every displayed center is an exact `A6` simplex
and every displayed flag obeys `T=S+X_a+X_b`, yet consecutive block arrows do
not compose and the projected gain defect is nonzero.

These are relaxed local controls, not endpoint objects.  They do not provide
99 stars, 231 global columns, the global frame identity, an SRG incidence
matrix, a cover with Wave 201 totals, a code, or a graph.

Run:

```powershell
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave204-global-slot-holonomy-proof-a\test_exact_check.py
.\.venv\Scripts\python.exe -B attempts\wave204-global-slot-holonomy-proof-a\exact_check.py --verify attempts\wave204-global-slot-holonomy-proof-a\exact-results.json
```

The implication “Wave 203 edgewise data induce center-cycle holonomy” is
refuted at its stated local premises.  Rank 11, the endpoint, `Q>=7060`, a
strict `n3` improvement, and Conway-99 remain `UNKNOWN`.
