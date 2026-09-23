# Wave 45 verifier: finite rooted flag moments

```yaml
role: verifier
date_utc: 2026-07-27T16:51:41Z
git_commit: 4636864ffc6310acaa71a41fff239a24e28404fc
claim_label: VERIFIED
scope: >
  Exact coefficient, control, stored-witness, and immutable 17-cut checkpoint
  verification; no endpoint promotion.
```

## Verified result

The clean-room implementation was frozen before discovery inspection. It
independently produced:

```text
root type            flags   union orders
vertex                 17       4..7
ordered edge           16       4..6
ordered nonedge        19       4..6

unrooted classes: 9, 21, 62, 208 at orders 4, 5, 6, 7.
```

After translating the discovery upper-triangle encoding, all 484 class
records and all 16,660 nonzero ordered entries match the clean stream. Direct
Petersen and Clebsch outer products also match all six expanded matrices
exactly.

The Wave 43 and Wave 44 stored count witnesses each have six independently
replayed negative integer directions in the `17 x 17` vertex-root matrix.
All 12 exact quadratic numerators match the sealed discovery result.

The pair-root matrices are exact PSD of rank one for both witnesses. They
depend only on counts through order six, already fixed at the endpoint. The
vertex matrix reaches order seven and supplies the genuine new obstruction.

## Immutable checkpoint v1

The verifier checked the sealed manifest and replayed 17 cuts and 15
intermediate witnesses:

- every cut reconstructs from the clean coefficient stream;
- every witness satisfies all 170 original rows;
- every prior cut is satisfied exactly;
- every new cut strictly rejects its source witness;
- every intermediate vertex matrix and negative quadratic matches.

The sixteenth solver call returned `unknown` with reason `timeout`. This is
not an infeasibility certificate.

```text
stored Wave43 witness: REFUTED
stored Wave44 witness: REFUTED
finite checkpoint:     VERIFIED INCOMPLETE
endpoint n3=4158:      UNKNOWN
strict upper bound:    NOT PROVED
Conway-99:             UNKNOWN.
```

The mathematical next step is a proof-producing treatment of the full
positive-semidefinite constraint, or a complete exact family of separating
directions. Continuing to accumulate finite cuts may find stronger
obstructions, but it cannot be promoted merely because one solver run times
out.
