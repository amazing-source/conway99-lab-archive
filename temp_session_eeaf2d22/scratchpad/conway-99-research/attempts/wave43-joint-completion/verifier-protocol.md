# Independent verifier protocol for Wave 43 joint completion

Freeze this protocol, a fresh implementation, and its tests before reading
any future candidate certificate or UNSAT proof.

## Scope wall

All conclusions remain conditional on `n3=4158`, `rank_F3(M)=12`, every edge
having local type `2+2+2`, and occurrence of the canonical rank-33
mask-`51739` core. No automorphism may be assumed.

Verification of a `B` does not verify a compatible outside graph `H`.
Verification of this one canonical core does not exclude other rank-33 cores,
the endpoint, or Conway-99.

## Independent reduction check

The verifier must not import `solve_joint.py`. Using only the frozen Wave 41
source, it must independently:

1. check the source SHA-256 and selected mask/core-edge SHA-256;
2. reconstruct the cubic 36-vertex core and forced Gram matrix;
3. reconstruct the three lexicographic inventories of sixty allowed
   within-fibre pairs;
4. re-enumerate the filter census
   `216000 -> 118718 -> 49736 -> 45032`;
5. compare the retained-candidate digest;
6. project candidates to pair-combination sets and reproduce counts
   `2881 / 2881 / 2694` and their three digests;
7. derive the compact matching equivalence rather than trusting its prose;
8. independently generate the seed-zero sequential-counter CNF and compare
   its exact variable/constraint census.

## Positive-certificate path

For any alleged `SAT` certificate, ignore solver internals and check directly:

1. exactly sixty distinct triples and blocks are present;
2. each coordinate is a permutation of `0..59`;
3. each block is exactly the union of its three indexed fibre pairs;
4. every block has positive Gram support, exactly two vertices in the
   12-component, and satisfies every local lambda/mu feasibility bound;
5. direct multiplication of the 36-by-60 incidence matrix gives the entire
   forced `BB^T`, including all same-fibre and cross-fibre entries;
6. the three serialized pairwise matchings equal the projections of the
   sixty triples.

Only then may the scoped object be labelled `VERIFIED B`. It remains separate
from construction of `H`.

## Negative-certificate path

Never accept `UNSAT` from a solver status, conflict budget, wall-clock run,
model count, or human inspection. Require all of:

1. canonical DIMACS bytes and SHA-256;
2. a proof-producing solver command and exact solver version;
3. a retained DRAT/LRAT/FRAT proof trace;
4. an independently built proof checker;
5. successful clean-room replay against the frozen DIMACS;
6. a hostile test showing a mutated proof or formula is rejected;
7. a separate proof that the DIMACS is equivalent to the mathematical compact
   matching formulation.

Only this chain can exclude the canonical `B` instance.

