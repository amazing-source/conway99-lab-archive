# Wave 123 verification report

Claim label: `VERIFIED`, scoped to exact necessary-condition checks for the
displayed coordinate families.

## Preinspection

The discovery manifest was frozen at

```text
39d680e78bf547c4fb5564048c6b7b1561382fd7d289f54a8a86154cff1a08a7.
```

All ten sealed entries matched.  The Wave120 source witness also matched its
frozen hash.  The discovery replay and all five discovery tests passed.

## Projector necessity

For a hypothetical `srg(99,14,1,2)`, the orthogonal projector onto the
`-4` eigenspace is

```text
E=(27I-9A+J)/63.
```

It has diagonal `4/9`, edge entries `-8/63`, and nonedge entries `1/63`.
If the columns of `T` are actual `-4` eigenvectors, their span projector

```text
W=T(T^T T)^(-1)T^T
```

has image contained in `image(E)`, so `E-W` is PSD.

The verifier rebuilt each Gram inverse over exact rationals, checked
`W T=T`, symmetry, and `trace(W)=rank(T)`.  The 40-record projector has 46
diagonal entries above `4/9`; the first-26 projector has six.  These two
displayed coordinate realizations are impossible in one target eigenspace.

The alternate 26-record projector has maximum

```text
1217462828759965373070564
----------------------------------------------- < 4/9,
2744155911807689338327015
```

at coordinate 72 and passes all diagonal rows.

## Graph-valued two-by-two completion

For each pair `u<v`, the verifier tried both allowed values

```text
E_uv=1/63 and E_uv=-8/63
```

in the exact determinant condition

```text
(E_uv-W_uv)^2
 <= (4/9-W_uu)(4/9-W_vv).
```

The 4,851 pairs partition exactly as:

```text
invalid:         352
forced edge:     135
forced nonedge: 1501
ambiguous:      2863.
```

Thus the explicit subset cannot be a common eigenspace family.

## Rooted three-point feature blocks

For every one of the 26 roots and each of six product-Johnson blocks, the
verifier reconstructed:

- selected- and unselected-cell centered endpoint features;
- degree-two within-block pair-incidence features in root-overlap classes
  zero, one, and two; and
- cross-block tensor-product incidence features for all four
  inside/outside cell choices.

This gives

```text
312 + 468 + 1560 = 2340
```

matrices.  Each is explicitly `F F^T`, and 1,581,840 entries were checked
against the claimed combinatorial formulas.

Among all 2,600 triples, 52 pair-overlap tuples occur and 28 split into
multiple three-way intersection values.  The displayed triples `(0,3,6)`
and `(0,6,39)` have the same pair-overlap tuple `(1,1,4)` but triple
intersections zero and one.  The minimum among all four tested signed
three-vector sums is exactly 22.

## Search boundary

No exhaustive search certificate accompanies the 30-restart heuristic.
The verifier confirms only its proper interpretation: failure to find a
different subset proves nothing about all 26-subsets.

The exact results refute the two displayed leverage-failing families and
the explicit alternate subset's graph-valued completion.  They do not prove
either local cap, exclude ranks 28 or 30, or resolve Conway-99.
