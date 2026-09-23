# Wave 102: rooted prism-incidence code

Status: `DERIVED`; independent verification required.

Let

```text
O = #{v : f_v is odd},
```

where `f_v` is the number of induced triangular prisms containing `v`.
Retaining the parity defect in Wave 100 gives the candidate refinement

```text
7*N14 <= 55440-5*n3-O/2
N14 <= 2*floor((55440-5*n3-O/2)/14).
```

This is strictly stronger when `P=1`: the compatible row `n3=4155` has
`O=6`, hence

```text
N14 <= 4950
```

instead of the scalar bound `4952`.

Over `F2`, the parity vector factors through the triangle-prism graph:

```text
f mod 2 = B D 1,
```

where `B` is vertex-versus-triangle incidence and `D` is
triangle-versus-prism incidence. Thus it belongs to the even triangle code.
The universal code constraints do not force it nonzero in general:
the locally parameter-compatible motif `C4 box K3` contains four prisms and
every motif vertex lies in two of them.

The package also proves that distinct prisms share at most four vertices.
If a graph had exactly three prisms and `f` were even everywhere, their
union would be the `3 by 3` rook graph, which already contains six prisms.
Therefore `f mod 2` is nonzero for `P=1,2,3`.

No strict upper bound on `n3`, graph nonexistence, or Conway-99 resolution
is claimed.

Reproduce:

```powershell
python -B attempts\wave102-prism-incidence-code\exact_check.py --verify
python -B -m unittest discover `
  -s attempts\wave102-prism-incidence-code -p "test_*.py" -v
```
