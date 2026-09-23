# Wave 38 higher-order failed routes and exact boundary

The target throughout is the conditional prism-free endpoint
`n3=4158`.  Nothing in this file is evidence that the endpoint exists or
does not exist.

## Local ternary rank shortcut fails

Over `F_3`, the endpoint reflection factors as `C=V H V^T`.  The seven
factor rows indexed by the graph triangles through any original vertex have
a common sum `w`, independent of the vertex.  Centering by

```text
z_T=v_T-w
```

gives isotropic rows with Gram matrix `D=C+J` and

```text
rank_F3(D)=r3-1.
```

For a fixed graph triangle, contract the six other triangles through each of
its three vertices.  Their extra cross edges form a simple tripartite
four-regular graph `P` with parts `6+6+6`, each bipartite block two-regular.
The exact local Gram block has the same rank as

```text
P-I over F_3.
```

It was tempting to hope that every locally admissible `P` had rank at least
12, which would exclude the surviving `r3=12` case.  That statement is
false.  The frozen 36-vertex core in `exact-results.json` is:

- connected and cubic;
- triangle-free;
- split into three twelve-point fibres;
- a perfect matching within and between every pair of fibres;
- free of doubled quotient edges, hence free of the local triangular
  prisms in question;
- within the exact target common-neighbor caps;
- compatible with a nonnegative forced `B B^T` of rational rank 34; and
- equipped with 152,399 individual columns surviving the mixed cut.

Nevertheless its quotient satisfies

```text
rank_F3(P-I)=10.
```

This is a local positive control only.  It does not supply sixty simultaneous
columns, a compatible `H`, a 99-vertex graph, or an endpoint construction.
It does prove that the one-triangle core axioms and individual-column cut
alone cannot establish the desired local rank-12 lemma.

## Signed four-cycles do not by themselves contradict the endpoint

The reflection spectrum forces

```text
balanced support C4 - unbalanced support C4 = 200277.
```

The subtraction removes all non-simple closed four-walks exactly.  The
result is a strong fourth-order necessary count, but both unknown counts can
remain nonnegative.  No justified bound on chorded versus induced support
four-cycles converts the imbalance into a contradiction.

## Smallest missing lemma exposed by this lane

A rank improvement would follow from:

> Every full simultaneous endpoint completion `(B,H)` forces at least one
> base triangle `T` whose contracted local quotient satisfies
> `rank_F3(P_T-I)>=12`.

The frozen control shows that this lemma must use simultaneous 60-block
compatibility, the `H` equations, or compatibility among different base
triangles.  It cannot follow from the one-triangle cubic core, pairwise
common-neighbor caps, nonnegative `B B^T`, or the individual-column mixed
cut alone.

## Status

```text
signed fourth-order imbalance: DERIVED
ternary vertex-clique centering: DERIVED
fixed-triangle rank bridge:      DERIVED
rank-twelve ternary exclusion:   NOT OBTAINED
P>=1 / n3<=4155:                 NOT PROVED
n3=4158 and Conway-99:           UNKNOWN
```
