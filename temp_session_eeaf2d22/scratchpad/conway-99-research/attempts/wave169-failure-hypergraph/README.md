# Wave 169: from a failure graph to a failure hypergraph

Status: `DERIVED_STRATEGY`; the local null result has an independent hostile
audit.

## Order-eight completion target

For a marked induced five-cycle, all three possible outside vertices of a
Wagner completion are forced by `mu=2`. A mark therefore has zero or one
completion, and its success is an induced order-eight event. No
two-completion order-eleven moment is needed for the first-moment count.

The exact global targets are equivalent:

```text
W8 >= 18710
F  <= 16640
F  <  16648
E  <= 8.
```

The strict form uses `F` divisible by eight.

## Pairwise incompatibility is insufficient

A tempting route is to put the 40 marks at a fixed nonedge into a graph and
join two marks when the current `lambda=1`, `mu=2`, degree-14, neighborhood
matching, or root-visible `P=0` clauses prevent them from failing together.
If this graph had independence number at most four, a Hoffman or clique-cover
certificate would prove the old pointwise target.

It does not. An explicit abstract local gadget permits five selected pure
marks to fail simultaneously by assigning distinct left and right forced
completion witnesses. The middle vertex has exactly 14 neighbors arranged
as the required seven disjoint edges, and all explicitly encoded pair counts
and root-visible prism exclusions survive.

This gadget is not a full SRG completion. It proves the narrower negative
result:

```text
current pairwise/root-local clauses
do not imply
at most four failed marks.
```

## Retained strategy

The first possible obstruction is at least five-way or global. Two precise
continuations remain:

1. a failure hypergraph whose forbidden hyperedges are five-mark sets that
   cannot extend through the remaining vertices; or
2. a lifted exact sum-of-squares/flag certificate containing the forced
   left/right candidate correlations, plus the full root-3 and root-12
   covariance blocks.

The certificate objective can be written

```text
8*W8-149680 >= 0
```

or, using divisibility, as any exact strict lower bound

```text
8*W8 > 149672.
```

Sampled scalar cuts and marginal left/right counts are insufficient; the
certificate must see their joint matching or global extension.

No endpoint exclusion, strict `n3` bound, graph, novelty, or Conway-99
resolution is claimed.
