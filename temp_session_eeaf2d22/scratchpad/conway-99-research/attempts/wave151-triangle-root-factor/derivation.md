# Derivation

## Edge-permutation reduction

For one 12-row group, Wave149 gives

```text
C_i C_i^T = 9I-M+J,
```

where `M` is a perfect matching. The diagonal entries are 10. A matched pair
of rows has inner product zero, and every other pair has inner product one.

Since every column contains exactly two ones in the group, each column is an
edge. The Gram entries imply that every nonmatching edge occurs exactly once
and no matching edge occurs. Thus each group is the vertex-edge incidence
matrix of `K_12-M`, whose edge set has size 60.

After fixing group zero in lexicographic edge order, any further group is
specified by a permutation `Q` of those 60 edges.

## Two-group exact cover

For domain edge `e` and image edge `f`, selecting `Q(e)=f` contributes one to
each of the four vertex-pair cells in `e x f`. The target matrix `G_01`
therefore gives a finite capacitated exact-cover problem:

```text
each domain edge is selected once,
each image edge is selected once,
every vertex-pair cell receives exactly G_01[u,v] contributions.
```

The stored `Q1` satisfies all equations exactly and yields the certified
24-by-60 partial factor.

## Third group

With `Q1` fixed, the third permutation `Q2` must satisfy both

```text
C_0 C_2^T = G_02,
C_1 C_2^T = G_12.
```

Mappings that touch a zero target entry can be removed in advance, leaving
1,620 Boolean variables. Exact-one permutation constraints and all 288
vertex-pair capacities form the bounded Z3 model in
`fixed_q1_q2_scout.py`.

The particular `Q1` is reported UNSAT by that model, without an exported
checkable proof. This does not decide whether another `Q1` can extend.

## Conditional residual block

Only after a complete `C=(C_0;C_1;C_2)` exists can one search for the
60-by-60 adjacency matrix `D`. It must be symmetric, binary, zero-diagonal,
and 8-regular, and satisfy

```text
C_i D = 2J-C_i-M_iC_i-F_ijC_j-F_ikC_k,

D^2 = 12I-D+2J-sum_i C_i^T C_i.
```

The second equation fixes every common-neighbor count inside `B`; it is not
replaced by a weaker spectral or degree condition.
