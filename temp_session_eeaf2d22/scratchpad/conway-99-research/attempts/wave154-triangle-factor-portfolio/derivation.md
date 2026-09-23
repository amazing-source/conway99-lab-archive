# Joint exact-cover derivation

Each 12-row incidence group is the vertex-edge incidence matrix of
`K_12-M`, so a column of the complete factor is a triple

```text
(e0,e1,e2).
```

A triple is removed if any of its endpoint pairs meets a zero entry in one of
`G_01,G_02,G_12`. Exactly 69,270 triples survive.

Selecting 60 triples must obey:

1. every edge in group zero is selected exactly once;
2. every edge in groups one and two is selected at most once;
3. each vertex-pair cell receives at most its target Gram entry.

Condition 1 selects exactly 60 columns. Conditions 2 then force every edge in
groups one and two to occur exactly once. Each cross block receives exactly
240 total endpoint-pair incidences, equal to the sum of its target entries;
therefore the cellwise upper bounds are also equalities. This is an exact
encoding, not a relaxation.

The local symmetry group used for portfolio classification is the centralizer
of the two frozen involutions `M` and `P`. It permutes the three four-point
orbits, with an independent Klein-four translation on each, giving

```text
6 * 4^3 = 384
```

elements. It is a symmetry of the abstract finite witness only; it is not
assumed to act on a putative 99-vertex graph.

Conjugating a Q1 edge permutation by all 384 maps produces its explicit
orbit. Direct enumeration proves that the Wave151 Q1 and the new Wave154 Q1
belong to disjoint orbits.
