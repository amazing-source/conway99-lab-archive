# Wave 51 exact rank-one cut-relaxation protocol

## Smallest balanced falsifiable subproblem

Let `x_H` be the 208 nonnegative real order-seven induced-class counts and let
`y=h11/4`. Impose:

1. all 170 frozen Wave44 integer equalities;
2. `x_H >= 0` and `2079 <= y <= 4158`;
3. all 17 frozen Wave45 rank-one PSD cuts;
4. exactly the `source_direction_index=0` Wave47 cut for each of the 17 frozen
   sources and each of the eight three-root families (136 cuts); and
5. exactly one sealed Wave49 candidate-direction cut for each of the 21
   five-root families.

This gives 174 exact linear PSD consequences. The Wave47 selection is the
smallest uniform layer that touches every frozen source/family pair. The
Wave49 selection is one direction per family. The question is:

```text
Does this fixed 174-cut real rational relaxation have a feasible point?
```

It is falsifiable in either direction. An exact Farkas combination would
certify infeasibility. An exact rational feasible point certifies that this
finite cut bundle cannot itself be the desired contradiction.

## Method

- Hash-check every sealed input before use.
- Reconstruct each Wave49 inequality from its integer direction and the
  independently verified Wave49 order-six/order-seven coefficient tensors.
- Use floating HiGHS only to select a candidate basic active set.
- Turn the selected zero coordinates, bound, and tight cuts into exact integer
  equalities.
- Solve that active system by exact sparse rational RREF.
- Accept a witness only after independently substituting its exact fractions
  into all 170 equations, all 174 cuts, nonnegativity, and both `y` bounds.
- Store the exact sparse rational witness and all catalog hashes.

Floating status is not evidence. The exact substitution is the certificate.

## Scope wall

A feasible rational aggregate vector is not an integer count vector, not a
graph, and not evidence for endpoint feasibility. It only refutes this fixed
finite cut bundle as an infeasibility certificate. It does not test the full
Wave45/Wave47/Wave49 PSD cones.

Endpoint `n3=4158`, a strict upper bound, graph construction, Conway-99, and
novelty remain `UNKNOWN` or `NOT_PROVED`.

The probe must abort below 15% free physical memory and must not modify any
Wave46--Wave49 artifact.
