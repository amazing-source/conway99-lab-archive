# Wave 123: fixed-C4 projector and three-point boundary

Claim labels: `DERIVED`, `REFUTED_AS_A_REALIZATION`,
`REFUTED_AS_A_RELAXATION`, `CANDIDATE`, and `UNKNOWN`.
Independent verification is required.

The concrete forty-record Wave120 signed-support realization cannot be a
family in one graph's `-4` eigenspace.  If `T` contains actual eigenvectors,
the projector

```text
W = T (T^T T)^-1 T^T
```

onto their span must satisfy `W <= E_-4`.  Since every diagonal entry of
`E_-4` is `4/9`, every coordinate leverage must be at most `4/9`.
Exact rational calculation finds 46 violations for the forty records, with
maximum

```text
154998381711798556753484666134716334
-------------------------------------------------- = 0.670912...
231026319585357084224437520694259587
```

The first 26 records also fail, at six coordinates.  This corrects only the
coordinate-support interpretation: Wave120's abstract positive-definite
residual Gram remains a valid pairwise null control.

A different explicit 26-record subset passes the diagonal leverage test
exactly; its maximum is `0.443656... < 4/9`.  It also passes 2,340 exact
rooted product-Johnson three-point PSD blocks, including centered
endpoint-one and degree-two within/cross-block factors.  These blocks use
genuine triple intersections: 28 of 52 pair-overlap triples split into
multiple triple-intersection values.

The same 26-record subset is **not** a common eigenspace family.  For 352
coordinate pairs, neither permitted graph projector entry

```text
E_uv = 1/63  (nonedge),    E_uv = -8/63  (edge)
```

makes the corresponding `2 x 2` principal minor of `E-W` positive
semidefinite.  Thus diagonal leverage and code-only three-point data are
still too weak, while graph-valued projector completion is genuinely
stronger.

A bounded 30-restart heuristic found no different 26-subset passing every
two-by-two row.  That search was not exhaustive and proves no
nonexistence.  Whether any size-26 graph-compatible family exists, both
needed local caps, rank 28, rank 30, Conway-99, and novelty remain
`UNKNOWN`.

## Reproduce

```powershell
python -B attempts\wave123-fixedc4-threepoint\exact_check.py `
  --verify attempts\wave123-fixedc4-threepoint\exact-results.json

python -B -m unittest discover `
  -s attempts\wave123-fixedc4-threepoint -p "test_*.py" -v
```

The exact checker uses only Python's standard library and refuses to start
below 15% free physical memory.
