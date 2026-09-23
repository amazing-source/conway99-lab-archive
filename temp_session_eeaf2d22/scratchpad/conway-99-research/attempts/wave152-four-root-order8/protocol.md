# Protocol

## Scope

Construct four-root/two-free flag covariance constraints that close at order
eight, test exact endpoint pseudowitnesses, and feed exact negative directions
back as linear cutting planes.

## Separation

- Discovery code and artifacts live only in this directory.
- Discovery does not promote its own negative directions to `VERIFIED`.
- The verifier freezes discovery hashes before inspection and independently
  reconstructs flag semantics, moments, and exact quadratic values.
- A refuted pseudowitness is not an endpoint refutation.
- Numerical feasibility or infeasibility is not a certificate.

## Restrictions

- Root labels are fixed pointwise.
- Only the two free vertices are quotiented by their swap.
- No automorphism of the hypothetical graph is assumed.
- Only locally admissible induced classes of orders 6, 7, and 8 are used.
- Every run refuses to proceed below 15 percent free physical memory.

## Promotion rule

An exact negative integer quadratic value can establish that one stored
rational count vector violates a necessary covariance constraint. Endpoint
infeasibility would require complete separation of every feasible vector and
an independently checked exact dual or equivalent proof certificate.

