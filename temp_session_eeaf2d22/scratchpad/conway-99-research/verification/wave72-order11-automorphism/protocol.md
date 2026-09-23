# Wave 72 clean-room verification protocol

## Frozen theorem

Assume `G` is a finite simple undirected strongly regular graph with

```text
(v,k,lambda,mu) = (99,14,1,2).
```

For an automorphism `g` of permutation order **exactly** 11, verify that its
fixed-vertex set is empty.

## Independence

The discovery directory was inventoried by path, byte size, and SHA-256 before
its contents were inspected.  The verifier first reconstructed the orbit and
fixed-graph argument without importing or executing discovery code.  Discovery
artifacts were compared only afterward.

## Conditional scope

This package does not verify Wave 69.  It verifies only the implication:

```text
separate complete exclusion of every semiregular C11 action
+ verified Wave 72 fixed-point theorem
=> no order-11 automorphism
=> no vertex-transitive realization.
```

The final implication uses orbit-stabilizer and Cauchy's theorem.

## Status boundary

- The fixed-point theorem may be promoted only by this independent audit.
- The identity permutation is not covered: it has order 1, even though its
  order divides 11.
- No asymmetric realization is excluded.
- Conway-99 remains `UNKNOWN`.

