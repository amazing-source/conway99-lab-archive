# Wave 110 derivation: safe row-lex symmetry

Claim labels: `DERIVED` for the conditional encoding and symmetry proof;
`UNKNOWN` for the four bounded searches.

## 1. Frozen conditional domain

Wave 105 fixes the 12-vertex induced motif `H=C4 box K3`, the 87 by 12
outside-incidence matrix `P`, and the unknown outside adjacency matrix `D`.
Wave 110 retains all three block equations

```text
H^2 + P^T P = 12I-H+2J,
D P + P H   = 2J-P,
D^2 + P P^T = 12I-D+2J.
```

It uses the same 3,741 outside-edge variables, all 1,044 distinct linear
incidence rows, all 87 degree rows, and all 3,741 nonlinear outside-pair
common-neighbor rows. Each of the 317,985 conjunction variables is encoded
in both directions.

## 2. The available relabeling group

Two outside vertices may be relabeled without changing `P` exactly when
their motif-neighborhood patterns are identical. The 87 fixed rows form 37
classes with multiplicity histogram

```text
size 1: 12 classes
size 2: 12 classes
size 3:  1 class
size 4: 12 classes.
```

The product of the symmetric groups on these classes acts on every labeled
extension satisfying the frozen equations. This statement does not say that
a target graph has a nontrivial automorphism. It says only that labels
assigned to rows with identical fixed boundary data are interchangeable in
the SAT encoding.

## 3. Why all row orders are simultaneously safe

For vertex index `i`, set `w_i=2^(86-i)`. On a labeled outside graph define

```text
Phi(D) = sum D_ij w_i w_j,
```

where the sum includes only pairs `i,j` belonging to different fixed-pattern
classes. Edges internal to one class are deliberately omitted.

Take a labeling minimizing `Phi` in its finite orbit under the relabeling
group. Let `i<j` lie in the same class `C`. Swapping their labels preserves
`P`, all graph equations, and the invariant `e(X0)`. Its change in potential
is

```text
(w_i-w_j) sum_{k not in C} w_k (D_jk-D_ik).
```

Because the powers of two are superincreasing in column order, the sign of
the inner sum is determined by the first column outside `C` where the two
rows differ. If the external row of `i` were lexicographically greater than
the external row of `j`, the swap would strictly lower `Phi`, contradicting
minimality. Therefore every class is lexicographically nondecreasing in the
same minimizing labeling.

This one shared potential proves simultaneous satisfiability of all row
orders. It is stronger than arguing class by class, where later column
permutations could otherwise disturb an earlier row order.

## 4. CNF equivalence

For consecutive class rows `a,b`, the encoding compares all columns outside
their class and asserts `a <=lex b`. A prefix variable records equivalently
that all preceding positions are equal. At a position whose prefix is equal,
the clause forbids `(a,b)=(1,0)`. The next prefix variable is constrained in
both directions to equal

```text
current_prefix AND (a_bit == b_bit).
```

Exhaustive truth-table tests over every pair of Boolean vectors of lengths
zero through four check that an auxiliary assignment exists exactly when
the lex relation holds.

There are 50 consecutive comparisons over 4,176 bit positions. They add
4,126 prefix variables and 24,756 CNF clauses. Together with the exact
common-neighbor encoding, each branch submits

```text
325,852 variables,
978,711 ordinary CNF clauses,
4,873 exact-cardinality rows,
9,746 native at-most constraints.
```

## 5. Complete invariant branch split

The three empty-pattern vertices form `X0`. Wave 110 does not fix a labeled
representative of their induced graph, because doing so and then ordering all
three labels would require a separate stabilizer argument. Instead, it
branches only on the invariant number of induced edges

```text
e(X0) in {0,1,2,3},
```

using one exact-cardinality row over the three edge variables. Relabeling
preserves this count, so the potential-minimizing representative remains in
the same branch. The four branches partition the complete motif-extension
domain.

## 6. Bounded result

All four 45-second MiniCard runs returned `UNKNOWN_TIMEOUT`. Free physical
memory was above 50% before and after every run. Wave 105 also timed out in
all four branches at the same limit, so this symmetry breaker did not change
the solve status at this budget.

No graph was returned to verify, and no proof-producing UNSAT result exists.
The motif's extendibility, the existence of the target graph, and Conway-99
all remain `UNKNOWN`.
