# Independent verification report: Wave 105

Verdict: `VERIFIED_WITH_CLARIFICATIONS`.

## Frozen claim

Conditional on a hypothetical `srg(99,14,1,2)` containing the induced
12-vertex `C4 box K3`, Wave 105 derives the complete 87-vertex extension
equations, exhibits one feasible linear-layer graph, and records four bounded
full-encoding runs as `UNKNOWN`.

The discovery manifest was frozen before inspection:

```text
b0fd40eda5a3677d4a835788cea20dfcb9bb3c5764719fc04536893f1b5da4a1
```

All 11 discovery files still match that manifest.

## Motif and forced incidence multiset

Independent construction gives a 12-vertex, 24-edge, 4-regular Cartesian
product `C4 box K3`. For each motif pair, subtracting its internal common
neighbors from the target SRG codegree gives the residual-capacity histogram

```text
capacity 0: 42 pairs
capacity 1: 12 pairs
capacity 2: 12 pairs
```

The support of the positive capacities is triangle-free. Therefore an outside
vertex cannot meet three motif vertices: each pair in such a triple would need
positive residual capacity. Every incidence row has weight at most two.

The 36 residual pair incidences consequently force 36 weight-two rows.
Every motif column needs 10 outside neighbors, and the pair rows use six
incidences in each column, forcing four singleton rows per column. With 87
outside vertices, three empty rows remain. Thus

```text
|X0|=3, |X1|=48, |X2|=36,
boundary incidences=120, pair incidences=36.
```

This triangle-free argument is the main clarification: the discovery
write-up constructed and Gram-checked the stated factor but did not spell out
why a factor using weight-three rows was impossible. The verifier records the
missing justification rather than silently treating one Gram factor as a
uniqueness proof.

## Block equations and aggregate census

For

```text
A = [H  P^T]
    [P   D ],
```

independent block multiplication reproduces

```text
H^2+P^T P = 12I-H+2J,
DP+PH       = 2J-P,
D^2+PP^T    = 12I-D+2J.
```

For a type-`i` outside vertex with `c` neighbors in `X2`, its three outside
type-degrees are

```text
(c+4i-10, 24-5i-2c, c).
```

Writing `t=e(X0)` gives, independently,

```text
e00=t,       e01=12-4t,   e02=30+2t,
e11=156+4t, e12=300-4t,  e22=51+t.
```

Each row sums to 549 outside edges. Direct integer enumeration of the six
neighbor-pair moments gives `18,11,5,1` rows for `t=0,1,2,3`. Applying
Erdos-Gallai to the three induced type sequences and Gale-Ryser to the three
bipartite type sequences leaves `18,11,4,1`. The one rejected row is in
`t=2`; only its `X0-X1` bipartite sequence fails.

These are six separate necessary graphicality filters. They do not construct
the six type graphs simultaneously.

## Linear witness

The archived adjacency lists reconstruct a symmetric binary 87-vertex graph
with

```text
549 edges,
3 vertices of outside degree 14,
48 vertices of outside degree 13,
36 vertices of outside degree 12.
```

All 1,044 entries of `DP=2J-P-PH` pass, as do all degree rows. The 1,044
linear incidence rows are distinct; adding 87 degree rows and the three fixed
`X0` edges/nonedges gives the archived 1,134 constraint rows. The independently
recomputed upper-triangle hash is

```text
feb948f5d0095b4baaba139fddda02b6ededcb7898e0d1ead3d2c251c6786fde
```

The verifier additionally evaluated every nonlinear outside-pair equation.
The witness fails 2,525 of the 3,741 rows. The first failure is pair `(0,3)`,
where the left side is 3 and the required value is 2. This strengthens the
status boundary: the graph is a valid linear-layer witness and definitely not
a full extension.

## SAT encoding audit

For every unordered outside pair `i,j`, the discovery source creates one edge
variable and, for every third outside vertex `k`, one conjunction variable
`y_ijk`. Its three clauses truth-table exactly to
`y_ijk <=> (D_ik and D_kj)`. The exact-cardinality wrapper combines
at-most constraints on positive and negated literals, giving equality.
Therefore

```text
D_ij + sum_k y_ijk = 2-(PP^T)_ij
```

is precisely the off-diagonal lower-right block equation. Degree rows supply
the diagonal equations. The linear incidence rows supply the off-diagonal
motif/outside block, while fixed `P` already satisfies the motif block.

The source loops over all 3,741 outside pairs and all 85 nonendpoint centers,
so the symbolic counts reproduce:

```text
3,741 edge variables
317,985 conjunction variables
321,726 variables total.
```

The three `X0` rows have identical empty motif neighborhoods. Exhausting all
eight labelled graphs on these three rows shows that edge count
`t=0,1,2,3` determines the isomorphism type, with labelled multiplicities
`1,3,3,1`. Hence the four fixed representatives are a complete encoding
symmetry split. No automorphism of the unknown 99-vertex target is assumed.

The SAT-return path directly replays the full SRG matrix equation. The
uncertified UNSAT and timeout paths remain fail-closed.

## Raw bounded runs and status

The four raw local logs were available. Byte-identical copies are retained in
this verifier package. Their hashes match the discovery bounded census:

```text
t=0 d96fdc9ced604e9e0c154154d2286bcac53f160ce0fad29f05d26d4727f7832a
t=1 9f010e850bf2e4ffdc04b8b2565213f3aa6a211835dc7ae0a7ccdabd21293191
t=2 969178b35afc137b080b1d646949de07fb71691de6208243f44a05ef9b7fefbd
t=3 c784c686304009402c5b914a28c6dde350431798ca69cb68116c988ab4a0e6ac
```

Every run has `timed_out=true`, `result=UNKNOWN_TIMEOUT`, and
`claim_label=UNKNOWN`. These logs establish chronology and encoding counts;
they are not mathematical certificates.

## Final boundary

- Linear-layer feasibility: `VERIFIED`.
- Exact motif-conditional reduction and encoding completeness: `VERIFIED`.
- Full extension of the motif: `UNKNOWN`.
- Exclusion of the motif: false.
- Occurrence of the motif in every hypothetical target: not claimed.
- Construction or nonexistence of `srg(99,14,1,2)`: `UNKNOWN`.
- Literature novelty: `UNKNOWN`.

No global graph result or Conway-99 resolution follows.
