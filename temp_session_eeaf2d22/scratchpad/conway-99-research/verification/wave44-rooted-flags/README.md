# Wave 44 rooted aggregate verifier

Status: `VERIFIED_SCOPED_FEASIBILITY`. The endpoint and Conway-99 remain
`UNKNOWN`.

Before opening discovery, the verifier independently derived and froze the
entire system:

```text
62 deletion rows
19 Hamiltonian rows with h11 = 4y
 7 vertex-root rows
36 ordered adjacent-root rows
46 ordered nonadjacent-root rows
--------------------------------
170 rows, 208 class variables + y = 209 variables
```

The clean-room implementation imports no Wave 44 code. It rebuilds the full
unlabeled seven-vertex catalogue, binds the 208-class stream to the verified
Wave 43 interface, independently constructs every rooted signature, and
checks the 91-support witness using exact integers.

Exact result:

```text
y = 4158, h11 = 16632
support = 91, zero classes = 117
seven-subset total = 14,887,031,544
all 170 residuals = 0
modular rank progression = 81 -> 82 -> 87 -> 93
```

After the pre-discovery protocol freeze, the verifier strictly parsed the
published `row-system.json` without importing any Wave 44 discovery code. The
ordered 208-class stream, all 35,530 coefficients, and all 170 right sides are
identical to the independent reconstruction. The canonical family and combined
hashes also match:

```text
base:     4788642cf268145dbcfdca456ef5078f1c2c2edb3626698ecf5c327b1efca359
vertex:   042ec8cf9026fadc1408ab5401f240dd8ae528a9d7dffd9068bd31230194c9d7
edge:     255237841b93babdd825fff9c9e2bdd30e8132d9470b9015005a8d660cbac482
nonedge:  9a20e3a28a00f4850d747630348ff4db8f512ba5cb462fd366362165f52d0bec
combined: 863a75a616c138e750178c93234a92289363318f4bd0775c7b0792e44b7c61cb
```

SciPy/HiGHS independently reports the free MILP as infeasible. That status is
false: the retained nonnegative integer witness has both exact-integer and
binary64 residual zero, and the same HiGHS model becomes optimal when its
bounds are fixed to that witness. Solver status is therefore diagnostic only,
not proof authority.

Reproduce:

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave44-rooted-flags\independent_check.py `
  --verify verification\wave44-rooted-flags\independent-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave44-rooted-flags -p "test_*.py" -v
```

Aggregate rooted counts do not enforce compatibility between overlapping
seven-subsets. The witness is not a graph and is not evidence that one exists.
