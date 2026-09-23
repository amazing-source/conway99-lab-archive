# Wave 44 rooted order-seven flags

Status: **EXACT FEASIBLE NECESSARY-COUNT SYSTEM; endpoint UNKNOWN**.

Wave 43 found an exact feasible vector for the complete unrooted
seven-vertex deletion deck at `n3=4158`. This package adds the smallest
rooted overlap layers while retaining the same 208 seven-vertex graph
classes.

## Rooted equations

For a distinguished vertex `u`, the other 98 vertices split into 14 neighbors
and 84 nonneighbors. Hence the number of rooted seven-subsets in which `u`
has selected degree `d` is

```text
99 * binom(14,d) * binom(84,6-d),  d=0,...,6.
```

For an ordered adjacent pair `(u,v)`, the other 97 vertices split as

```text
common, u-only, v-only, neither = 1,12,12,72.
```

For an ordered nonedge they split as

```text
common, u-only, v-only, neither = 2,12,12,71.
```

Choosing five vertices from these categories gives 36 edge-rooted and 46
nonedge-rooted signatures. The coefficient of a seven-class in a rooted row
is the exact number of ordered root pairs in that class with that signature.
No automorphism of a putative graph is assumed.

The layered exact coefficient ranks are stable over `F_101`, `F_103`, and
`F_107`:

```text
81  unrooted rows
82  plus vertex-root rows
87  plus edge-root rows
93  plus nonedge-root rows.
```

Thus these rows are strictly stronger than the feasible unrooted system. The
old witness confirms this concretely: it violates all 7 vertex rows, all 36
edge rows, and all 46 nonedge rows.

## Exact positive control

The stronger system is nevertheless feasible. An exact integer discovery
produced:

```text
h11:                 16632
seven classes:         208
positive classes:       91
zero classes:          117
maximum class count: 3222792342
exact rows checked:     170
seven-subset total: 14887031544 = binom(99,7).
```

The witness SHA-256 is
`9be153b2487c3e07e20bffeb7ee6c890e69caa6e8d6b6e2936fbc5d8927bd5b9`.
The exact result SHA-256 is
`c41b194d2d4ae8121883d84ba4f5011f48336a58a0dd4f5cebf9ab560ee3ae19`.

The complete frozen `row-system.json` SHA-256 is
`fb81601a9c97fc6860702403e56da65c2ba8fd69ee6a61007a0da53cade1d722`.
Each family commits to compact canonical JSON of
`{"rows":[...],"rhs":[...]}`; the combined commitment hashes the mapping
from all four family names to those objects:

```text
base:     4788642cf268145dbcfdca456ef5078f1c2c2edb3626698ecf5c327b1efca359
vertex:   042ec8cf9026fadc1408ab5401f240dd8ae528a9d7dffd9068bd31230194c9d7
edge:     255237841b93babdd825fff9c9e2bdd30e8132d9470b9015005a8d660cbac482
nonedge:  9a20e3a28a00f4850d747630348ff4db8f512ba5cb462fd366362165f52d0bec
combined: 863a75a616c138e750178c93234a92289363318f4bd0775c7b0792e44b7c61cb
```

Z3 was used only to discover the vector. The published checker reconstructs
all 170 equations and verifies every residual with ordinary integer
arithmetic. Certificate checking does not invoke Z3 or trust its status. A
second checker replays the frozen coefficient matrix, hashes, witness
residuals, and status wall using only the Python standard library; it does
not import any equation-construction or solver module.

## False solver chronology

Before the exact witness was available, a floating SciPy/HiGHS MILP run
reported the same system infeasible. The exact witness refutes that report.
The failure is retained as a numerical false negative, not mathematical
evidence. The continuous floating LP was also numerically feasible, further
warning against status-based promotion.

## Boundary

The rooted variables are still aggregate counts. They do not say which
seven-subsets overlap at a particular root, do not force one root's complete
flag distribution to be compatible with another's, and do not impose a
positive-semidefinite flag moment matrix.

Therefore:

```text
rooted aggregate order-seven system: EXACT FEASIBLE
n3=4158:                              UNKNOWN
upper bound below 4158:               NOT PROVED
graph construction:                  NONE
Conway-99:                            UNKNOWN.
```

The next meaningful flag-algebra step is a PSD moment matrix whose entries
count pairs of rooted flags glued along a common vertex, edge, or triangle.

## Reproduce

The exact checker does not run a solver:

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave44-rooted-flags\exact_check.py `
  --verify attempts\wave44-rooted-flags\exact-results.json

.\.venv\Scripts\python.exe -B `
  attempts\wave44-rooted-flags\verify_frozen.py

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave44-rooted-flags -p "test_*.py" -v

.\.venv\Scripts\python.exe -B `
  attempts\wave44-rooted-flags\manifest_check.py
```

The discovery-only solve requires a separate Z3 installation and is not
needed to check the certificate.
