# Wave51 independent rank-one cut verification protocol

## Frozen claim

The object under review is one fixed rational relaxation:

- 208 nonnegative order-seven class variables and `y=h11/4`;
- all 170 sealed Wave44 equations;
- `2079 <= y <= 4158`;
- all 17 sealed Wave45 cuts;
- the `source_direction_index=0` Wave47 cut for each of 17 sources and
  eight three-root families, giving 136 cuts; and
- one sealed Wave49 integer direction for each of 21 five-root families.

The scoped question is whether this exact 174-cut system has the rational
witness stored by the Wave51 source package.

## Separation correction

The source agent selected the bundle, constructed the witness, replayed it,
and labeled its own output `VERIFIED`/`VERIFIED_SCOPED`. That chronology
violates the repository separation rule, and `VERIFIED_SCOPED` is not an
allowed claim-label value. The source is therefore treated as `CANDIDATE`
until this clean-room verifier completes. Source files are not silently
repaired.

## Independent attacks

The verifier:

1. checks byte hashes for all source artifacts and recursively checks the
   Wave45, Wave47, Wave49, and Wave51 package manifests;
2. rebuilds the ordered 170-row system from the four frozen Wave44 families
   and checks every family hash commitment;
3. checks the self-hash, primitiveness, sense, class coverage, and census of
   all 17 Wave45 cuts;
4. checks all 2,657 Wave47 cut self-hashes, uniqueness, source/family
   coverage, and the exact 136-cut index-zero selection;
5. independently derives the order-six deck from Wave43, checks all Wave49
   coefficient and direction self-hashes, and recomputes all 5,691 exact
   order-six/order-seven quadratic evaluations;
6. compares the reconstructed 174-cut catalog hash with the source package;
7. rebuilds the 209-coordinate rational witness from stored fractions and
   exactly substitutes it into every equation, bound, and cut; and
8. proves active coefficient rank 209 by exact modular Gaussian elimination.

The numerical optimizer and source `probe.py` are not imported or used.

## Scope wall

An exact feasible point refutes a Farkas infeasibility certificate only for
this fixed finite bundle. It does not establish feasibility of all stored
rank-one cuts, the full PSD system, integer counts, the endpoint, or a graph.
Those claims remain `UNKNOWN`.
