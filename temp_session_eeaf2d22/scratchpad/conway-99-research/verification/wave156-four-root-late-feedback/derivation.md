# Exact derivation

For a fixed ordered four-vertex root type, let `R` be its number of embeddings
and let `c(theta)` be the vector counting order-six flags extending a root
embedding `theta`.  Every real vector `v` gives the covariance inequality

```text
R * sum_theta (v.c(theta))^2 - (sum_theta v.c(theta))^2 >= 0.
```

Products of two unordered free pairs have union order six, seven, or eight.
Enumerating pointwise-labeled roots and quotienting only the swap of the two
free vertices therefore expands the inequality into

```text
constant + sum_H a7(H)*x7(H) + sum_H a8(H)*x8(H) >= 0.
```

The verifier independently enumerates all locally admissible graph classes
and flags.  It derives `x6` and `x5` from `x7` by vertex-deletion identities,
derives the root counts from `x4`, computes every quadratic coefficient, and
divides by the exact coefficient gcd.  No discovery generator is imported or
executed.

## Principal minors

For indices `i,j`, the diagonal centered entries are obtained from the unit
directions `e_i,e_j`.  The off-diagonal entry follows by exact polarization:

```text
B_ij = (q(e_i+e_j) - q(e_i) - q(e_j))/2.
```

This independently reproduces:

- mask 13, indices 5 and 49, flags 181 and 6181;
- mask 12, indices 59 and 71, flags 5428 and 6324;
- mask 12, indices 160 and 166, flags 21812 and 22708.

All three stored two-by-two determinants are strictly negative.

The equal diagonal entries in each mask-12 pair make `(1,-1)` especially
simple.  Re-enumeration followed by primitive gcd reduction gives the two
sparse inequalities stated in the README.

## Witness equalities

For each rational witness, the verifier reconstructs the complete retained
linear system:

1. total `x8` count;
2. all order-seven to order-eight deletion equations;
3. all marked-vertex and marked-pair equations;
4. all ordered-edge and ordered-nonedge zero-covariance equations;
5. every active scalar covariance cut.

Every row is replayed with exact rational arithmetic.  The stored modular row
selection is independently reduced modulo 1,000,003 and has rank 886 on 886
supported `x8` variables.  Solver output is not part of this proof.
