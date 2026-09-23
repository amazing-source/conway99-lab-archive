# Wave 204 literature and hostile-control lane

Status: `REFUTED_PENDING_INDEPENDENT_VERIFICATION` for one precisely scoped
lemma; `UNKNOWN` for the prism-free rank-11 endpoint and Conway 99.

The exact countermodel refutes:

> The 99-center degree/complement data, local `(7,3)` Hilton--Milner
> families, four-point pair fibers, the Wave201 equality row, and the
> Wave203 five-slot capacity force a bidirectional selected label.

The certificate has:

```text
99 centers on Z/99Z
14-regular circulant skeleton, complement degree 84
1,287 full local flags, 1,200 selected
J=3,561, delta=3
p3=3,123, q=237
selected multiplicities 1^3123, 2^234, 3^3
79 centers with three nonprivate outgoing labels, 20 with zero
epsilon=708, L=delta-3q+epsilon=0
b=0
combined full two-orientation multiplicity <=3<=5
```

Every local repeated label has an explicit pair fiber and distinct
Wave203 third-block slots. All used labels follow one global orientation
of the circulant complement, so reverse occupancy is absent.

This is a rational `0/1` local-incidence skeleton. It is **not** a strongly
regular graph: the circulant has adjacent common-neighbor counts from 6
through 12 rather than `lambda=1`. Its declared block/fiber types are not
derived from its adjacency. It supplies no ternary columns, canonical
relations, rank-11 code, circuit cover, or endpoint object. It therefore
refutes only a theorem using the displayed local interface; it does not
refute a genuine global ternary-column or SRG obstruction.

Run:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave204-literature-hostile-controls\build_countermodel.py --verify attempts\wave204-literature-hostile-controls\countermodel.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave204-literature-hostile-controls\test_countermodel.py
```

The primary-source audit is in `literature-audit.md`. No searched theorem
excludes the frozen endpoint, and no novelty claim is made.
