# Wave 69: cyclic-cover and Cayley shift

Status: `DERIVED` discovery claims; independent verification pending.

This package explores two explicitly restricted reformulations of
`srg(99,14,1,2)`:

1. a specified semiregular automorphism of order 11, giving nine vertex
   orbits and a `9 x 9` integer quotient;
2. a Cayley realization on a group of order 99.

The exact quotient equations have seven possible row shapes and three possible
sorted diagonals. A deterministic standard-library enumeration finds no
quotient candidate. The primary `unpruned` mode enumerates all labeled row
choices after sorting only the diagonal; a separate canonical mode gives the
same zero count.

An exact fixed-point argument further shows that every nonidentity order-11
automorphism would have to be fixed-point-free. The quotient obstruction
therefore excludes all order-11 automorphisms, not only a pre-assumed
semiregular one. It follows that a target, if it exists, cannot be
vertex-transitive.

Independently, every group of order 99 is abelian, and Fourier inversion for a
putative Cayley graph forces a sum of roots of unity to be `-18/7` or `81/7`.
That is impossible because a rational algebraic integer must be integral.

These results exclude order-11 symmetry, vertex-transitive targets, and Cayley
targets. They do not assume that an arbitrary target has symmetry, and they do
not resolve the unrestricted Conway-99 problem.

## Reproduce

Quick canonical cross-check:

```powershell
.\.venv\Scripts\python.exe attempts\wave69-cyclic-cover-shift\exact_search.py --mode canonical
```

Complete unpruned plus canonical result:

```powershell
.\.venv\Scripts\python.exe attempts\wave69-cyclic-cover-shift\exact_search.py --mode both --output attempts\wave69-cyclic-cover-shift\exact-results.json
```

Unit tests:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s attempts\wave69-cyclic-cover-shift -p "test_*.py" -v
```

## Files

- `protocol.md`: frozen scope and claim labels.
- `derivation.md`: exact quotient, representation, enumeration, lift, and
  Fourier derivations.
- `exact_search.py`: deterministic standard-library search.
- `exact-results.json`: sealed exact output.
- `test_exact_search.py`: discovery tests.
- `exact_check.py`: fail-closed artifact checker.
- `full-check-results.json`: byte-stable replay of both search trees.
- `failed-routes.md`: inconclusive routes and scope boundaries.
- `run-report.yaml`: protocol run record.
- `input-freeze.sha256`: frozen input hashes.
- `package-manifest.sha256`: package hashes.
