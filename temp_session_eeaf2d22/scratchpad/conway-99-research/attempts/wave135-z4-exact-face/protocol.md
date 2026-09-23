# Wave135 protocol

## Frozen scope

Use the corrected, sealed Wave134 orbit sets and forced lower bounds. Do not
assume automorphisms, endpoints, rooted motifs, or an `n3` value.

## Exact linear algebra

1. Build all 161 forbidden character rows over the integers.
2. Compute exact rational rank and left-kernel relations.
3. Reproduce the lower rank bound with a nonzero minor modulo
   `p=2147483647`.
4. Add normalization, `A_0=1`, and the torsion-shell equality.
5. Compare exact coefficient and augmented ranks.

## Search

1. Translate by the complete forced-primal lower vector.
2. Eliminate an exact 143-row basis plus the three affine rows.
3. Start with all forced-dual lower rows.
4. Solve the active system with GMP rationals.
5. Replay all allowed rows exactly and add the most negative missing rows.
6. Stop at the wall, memory guard, iteration cap, or a terminal certificate.

Host free memory must remain at least 15%; a worker approaching 3 GiB is to be
stopped externally.

## Promotion

- `DERIVED`: exact rank, dependency, or algebraic consequence replayed
  independently.
- `CANDIDATE`: a machine-readable witness not yet independently replayed.
- `VERIFIED`: independent exact replay succeeds.
- `UNKNOWN`: bounded or failed search without a certificate.

Discovery may not certify itself. A rational enumerator is not a code or graph.
