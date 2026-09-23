# Wave 107: exact spectrum of the Wave 105 outside graph

Status: `DERIVED`; independent verification required.

Conditional on a hypothetical `srg(99,14,1,2)` containing the induced
`C4` Cartesian `K3` motif from Wave 105, the 87-vertex outside graph `D`
has characteristic polynomial

```text
(x-3)^42 (x+4)^32 (x^2-9x-46)
(x+3)^2 (x+2)^2 (x+1) x^4 (x-2)^2.
```

This refutes the initially proposed `x^2-9x-38` factor: that factor gives
`tr(D^2)=1082`, whereas the forced degree census gives 1098.

The corrected factorization forces:

```text
549 edges, 167 triangles, 1356 four-cycles,
nullity_Q(D)=4,
rank_Q(D-3I)=45,
rank_Q(D+4I)=55.
```

The Perron eigenvector is explicitly positive, and simplicity of its
eigenvalue forces `D` to be connected. All corrected eigenvalues satisfy
interlacing, so no spectral obstruction was found. The motif extension
and Conway-99 remain `UNKNOWN`.

Reproduce using only the standard Python library:

```powershell
python -B attempts\wave107-c4boxk3-spectrum\exact_check.py --verify
python -B -m unittest discover `
  -s attempts\wave107-c4boxk3-spectrum -p "test_*.py" -v
```
