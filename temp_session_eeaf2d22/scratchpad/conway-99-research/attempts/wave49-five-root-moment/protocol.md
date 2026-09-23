# Wave 49 exact five-root, one-free-vertex moment protocol

## Frozen finite matrix

Fix a locally admissible labelled graph `sigma` on the pointwise-labelled
root set `[5]={0,1,2,3,4}`.  A flag is an admissible one-vertex extension of
`sigma`; it is indexed by the five-bit neighborhood of the free vertex in the
ordered root set.  No root label is quotiented and the single free vertex has
no nontrivial permutation.

For every root embedding `theta` in a graph `G`, let `c_a(theta)` be the
number of vertices outside the roots whose root-neighborhood bitmask is
`a`.  The raw finite moment is

```text
M_sigma(a,b) = sum_theta c_a(theta)c_b(theta).
```

It is an exact sum of integer outer products and therefore PSD in every
graph.

The product split is exhaustive and unique:

- the same free vertex contributes only to a diagonal entry and has induced
  union order six;
- two distinct ordered free vertices contribute to an ordered matrix entry
  and have induced union order seven.

For every unrooted induced class, coefficients count every ordered root
embedding with labelled root mask exactly `sigma`, together with the relevant
same or ordered-distinct free choice.  There is no automorphism division.

## Canonical root representatives

The 21 canonical locally admissible order-five masks and expected matrix
sizes are:

```text
0:32, 1:32, 3:28, 7:22, 15:16, 19:16, 20:32,
21:26, 23:16, 28:28, 29:21, 31:13, 54:18, 58:24,
59:16, 62:16, 184:16, 185:15, 207:10, 220:21, 221:12.
```

The implementation must also construct tensors for every one of the 683
labelled admissible five-vertex masks.  For every canonical root `sigma` and
every `pi in S5`, relabelling sends

```text
sigma -> pi(sigma)
a     -> pi(a)
```

and must give exact permutation congruence of every order-six and order-seven
class coefficient matrix.  This is a change of root coordinates, not an
automorphism assumption on a target graph.

Thus enforcing the matrix for one canonical representative enforces every
labelled root type in its isomorphism orbit.

## Normalization

At `n=99`, if `N_sigma` is the order-five induced count of the canonical
unrooted class and `Aut(sigma)` is its exact automorphism count, the number of
ordered root embeddings with labelled mask exactly `sigma` is

```text
R_sigma = N_sigma * Aut(sigma).
```

Every root has `99-5=94` possible free vertices.  The probability-normalized
matrix is therefore

```text
M_sigma / (R_sigma * 94^2).
```

All-ones identities must be checked directly on every witness and control.

## Required controls and targets

- independently regenerate all local class streams through order seven;
- match the frozen 21/62/208 class censuses and hashes;
- compare direct and expanded matrices for Petersen and Clebsch in all 21
  families;
- reconstruct order-five and order-six decks of the frozen Wave43,
  Wave44, and fifteen immutable Wave45-v1 witnesses;
- evaluate every one of the 17 witnesses with exact integer matrices and
  exact integer negative directions when found;
- add all 21 normalized matrices to the frozen Wave48 real SDP only as a
  numerical scout.

## Status and safety

- Discovery output is `CANDIDATE`; global status remains `UNKNOWN`.
- Numerical infeasibility is not a proof.  A dual is only a candidate until a
  complete exact rational certificate is independently checked.
- Numerical near-feasibility must preserve the candidate vector and residuals.
- No graph automorphism is assumed.
- No endpoint exclusion, strict upper bound, graph construction, Conway-99,
  novelty, or priority claim may be made.
- Abort before any phase that would leave less than 20% free physical memory.
- Do not import or execute the Wave 47 three-root discovery implementation.
  Its sealed, independently verified coefficients may be consumed only by the
  combined numerical SDP.
