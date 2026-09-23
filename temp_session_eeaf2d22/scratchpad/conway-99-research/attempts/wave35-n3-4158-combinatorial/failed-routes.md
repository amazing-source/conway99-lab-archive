# Retained failed routes at the prism-free endpoint

The frozen endpoint is

```text
n3=4158, triangular-prism count P=0, q(T)=12 for all 231 triangles.
```

None of the routes below is evidence for existence or nonexistence.

## Local holonomy parity

For a base triangle `T`, the three cross-fibre bijections compose to a
permutation `sigma_T` of twelve points.  A prism partner is exactly a fixed
point, so the endpoint makes every `sigma_T` a derangement.

The sign of `sigma_T` is gauge invariant, but derangements of twelve points
occur with either sign.  Multiplying signs over the 231 base triangles did
not produce a cancellation identity: each edge-transition appears only once
after choosing triangle orientations, and the inverse-transition relation
only squares the product if both orientations are included.  No parity
contradiction was derived.

## One-triangle incidence reduction

The exact reduction in `exact_check.py` leaves sixty blocks, each selecting
one allowed pair from each of the three twelve-point fibres.  A restricted
factor choice has:

```text
183980 individually valid block types;
68774, 90364, 24138, 704 types with 0,1,2,3 internal X-edges;
an exact X0-X1 pairwise edge-bijection realizing the required concurrence.
```

These positive controls refute a contradiction based only on the existence
of an individual block or on one pair of fibres.  They do not construct the
simultaneous sixty-block object.

## Bounded heuristic search

A standard-library swap search used:

```text
seed=4158
restarts=20
swaps_per_restart=300000
objective=sum of squared residuals in the three 12-by-12 cross concurrences
best objective=106
observed wall time approximately 480 seconds
```

Failure to reach zero is not evidence.  The search was incomplete and no
claim uses it.

## Proofless SAT/PB attempts

Using the environment's PySAT installation:

1. A 3,600-variable pairwise `X0-X1` assignment was SAT.  Its model is the
   exact pairwise certificate checked by `exact_check.py`.
2. Holding that one certificate fixed, a 3,600-variable `X2` extension was
   reported UNSAT by CaDiCaL 1.9.5 after approximately 365.5 seconds.  No proof
   certificate was emitted, and only that one `X0-X1` choice was fixed.
   Classification: `UNSAT_UNVERIFIED`, not evidence.
3. A simultaneous model over 183,980 valid block variables was encoded twice
   with MiniCard native cardinalities.  The process exited with code 1 after
   encoding and emitted no solver result.  Classification: failed run, not
   evidence.

No solver output is promoted in the report.

## Boundary

The exact local identities and the pairwise control survive.  Simultaneous
three-fibre compatibility, compatibility between different base triangles,
the `n3=4158` endpoint, and Conway-99 remain `UNKNOWN`.
