# Wave 69 independent cyclic-cover audit

Date UTC: 2026-07-27T23:29:37Z

Verdict: **VERIFIED** for the restricted order-11 quotient, order-11
automorphism, vertex-transitive, and Cayley exclusions.  The unrestricted
Conway-99 problem remains **UNKNOWN**.

## Quotient reconstruction

For adjacency matrix `A`, the strongly regular graph equations give

```text
A^2 = 12 I - A + 2 J.
```

A fixed-point-free order-11 action has nine orbits of size 11.  On vectors
constant on each orbit its quotient `Q` is symmetric, nonnegative, integral,
has row sum 14, has even diagonal, and obeys

```text
Q^2 + Q = 12 I + 22 J.
```

The full nonprincipal eigenspaces of `A` have dimensions 54 and 44 for
eigenvalues 3 and -4.  They are rational representations of `C_11`.  Every
nontrivial irreducible rational `C_11` representation has dimension 10.
Because the fixed space has dimension nine, including the principal vector,
the only possible fixed multiplicities are

```text
spec(Q) = {14, 3^4, (-4)^4},   trace(Q)=10.
```

For diagonal entry `d`, the row sum and diagonal matrix equation are

```text
sum(off diagonal entries) = 14-d,
sum(off diagonal squares) = 34-d^2-d.
```

Independent moment enumeration gives exactly seven row multisets:

```text
d=0:
  (0,0,2,2,2,2,3,3)
  (0,1,1,1,2,3,3,3)
  (0,1,1,2,2,2,2,4)
  (1,1,1,1,1,2,3,4)

d=2:
  (0,0,1,1,2,2,3,3)
  (0,1,1,1,1,2,2,4)

d=4:
  (1,1,1,1,1,1,2,2)
```

Their labeled permutation counts are `2716`, `3360`, and `28`.  Evenness and
trace 10 leave exactly three sorted diagonal cases:

```text
(0,0,0,0,0,0,2,4,4)
(0,0,0,0,0,2,2,2,4)
(0,0,0,0,2,2,2,2,2)
```

## Exhaustive certificate

The verifier independently selected full labeled rows.  At depth `i`, every
permutation of every allowable row multiset was considered, symmetry with
rows `0,...,i-1` was enforced, and every now-testable off-diagonal equation

```text
sum_k q_ik q_jk + q_ij = 22
```

was checked.  At depth nine these conditions are exactly all entries of the
quotient matrix equation.

The label-complete tree applies no residual-vertex canonical pruning.  Sorting
the diagonal is only a simultaneous orbit relabeling.  Its results were:

| Sorted diagonal | Nodes | Candidates | Transcript SHA-256 |
|---|---:|---:|---|
| `000000244` | 371839 | 0 | `10091391a121b71ca346ed28aca78db2f3e148e9a3c19b1f3ff11890410c3185` |
| `000002224` | 370939 | 0 | `f4092efa66a9c45115fc58784a3b7245075ba1661a854884132e3532223e319b` |
| `000022222` | 365755 | 0 | `26b9a8eeeff89a19ea8462390c57686941f3a65be91bbeb9e0990d76c800decf` |

Total: **1,108,533 nodes and zero quotients**.

The optional canonical tree independently visited 8,980 nodes and also found
zero quotients.  All branch counts, rejection counts, leaf counts, node
counts, and all six transcript hashes match the sealed discovery output
exactly.  The comparison contains 11 exact comparisons and zero mismatches.

Therefore no semiregular `C_11` quotient exists.  A block-circulant
`Z_11` lift would necessarily have this quotient at frequency zero, so its
candidate set is empty without a voltage SAT nonhit.

## Imported fixed-point theorem and vertex transitivity

Wave 72 separately verified that every exact-order-11 automorphism must be
fixed-point-free.  Combining that theorem with the verified quotient
obstruction excludes every order-11 automorphism.

If the graph were vertex-transitive, orbit-stabilizer would make its finite
automorphism-group order divisible by 99 and hence by 11.  Cauchy's theorem
would supply an element of order 11, a contradiction.  Thus a realization, if
one exists, is not vertex-transitive.

## Independent Cayley obstruction

Sylow's theorem makes the order-11 subgroup of every group of order 99 unique
and normal.  Conjugation by a Sylow-3 subgroup of order nine has image with
order dividing both 9 and `|Aut(C_11)|=10`, so the action is trivial.  Groups
of order nine are abelian.  Hence every group of order 99 is abelian, of type

```text
C_99  or  C_3 x C_3 x C_11.
```

For an inverse-closed Cayley connection set `D`, abelian characters give 54
nonprincipal eigenvalues 3 and 44 eigenvalues -4.  If `X` is the set of the 54
characters with value 3 and `g` is nonidentity, Fourier inversion gives

```text
99*1_D(g) = 18 + 7*S_X(g).
```

Thus `S_X(g)` is `-18/7` outside `D` and `81/7` inside `D`.  But it is a sum
of roots of unity and hence an algebraic integer.  A rational algebraic
integer is an integer, so both cases are impossible.  Cayley realizations are
excluded independently.

## Hostile checks and boundary

- The discovery directory remained 17-for-17 byte-identical after inspection.
- The label-complete tree records zero canonical rejections at every depth.
- A mutated transcript hash is detected by the comparison.
- A Wave 72 artifact relabeled from `VERIFIED` to `DERIVED` is rejected.
- Sorting only the diagonal was checked as simultaneous row/column relabeling.
- Thirteen verifier tests pass.
- Minimum observed free host memory during this audit exceeded 57 percent.

No argument here excludes an asymmetric target or one with automorphism group
order prime to 11.  No construction, unrestricted nonexistence proof, strict
global `n3` upper bound, or literature-priority claim follows.  Conway-99 and
novelty remain `UNKNOWN`.
