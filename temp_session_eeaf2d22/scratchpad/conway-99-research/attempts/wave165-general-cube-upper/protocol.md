# Wave 165 protocol

## Question

Can the fixed-four-cycle partition in a hypothetical
`srg(99,14,1,2)` give a global relation among the induced cube count `C8`,
the induced triangular-prism count `P`, and `n3`?

## Discovery method

1. Import only the strongly regular graph parameters and the independently
   verified count of 2,079 induced four-cycles.
2. Derive the fixed-cycle outside partition without assuming any
   automorphism.
3. Prove a local degree cap between consecutive singleton classes.
4. Determine the exact size, nine or ten, of each boundary partial
   matching.
5. Identify the size-ten exception with an induced triangular prism.
6. Inject cube extensions through all four boundary matchings.
7. Double count marked square--prism and cube--face incidences.

## Separation

- Discovery may label the theorem only `DERIVED`.
- A verifier must reconstruct all seven proof stages independently and
  explicitly audit labelled/unlabelled multiplicities.
- The verifier must not infer graph nonexistence or a strict `n3` bound from
  the cube bound alone.
- Literature novelty must remain `UNKNOWN` until a separate source review.

## Computational policy

The proof itself needs no computation. Any later exact checker must wait
until host free RAM is at least 18%, and it must stop before free RAM falls
below the user's 15% reserve.
