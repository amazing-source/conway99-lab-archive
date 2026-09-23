# Wave 140: Arf sign versus adjacency-lattice data

The target Arf sign is still `UNKNOWN`.

This package derives the precise missing invariant:

```text
epsilon_R=(2/det(U)),
```

where `U` is the even unimodular two-adic `3`-eigenlattice of the
adjacency operator. It then constructs exact opposite-sign controls which
share the target binary rank/idempotent data, spectrum, two-primary Smith
factors, and adjacency-lattice discriminant-group structure.

Thus those coarse invariants do not determine the sign. A full
two-primary discriminant quadratic form would distinguish the controls,
but no such target form has been verified. The controls are not integral
adjacency matrices, so a finer argument using all entrywise SRG conditions
remains possible.

Reproduce with:

```powershell
python -B attempts\wave140-arf-sign-lattice\exact_check.py
python -B -m unittest discover `
  -s attempts\wave140-arf-sign-lattice -p "test_*.py" -v
```

No code, graph, or Conway-99 resolution is claimed.
