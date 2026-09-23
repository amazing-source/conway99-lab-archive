# Wave 47 three-labelled-root moment candidate

## Candidate result

This discovery package builds the next finite Gram-moment layer that still
closes in the existing order-seven variables.  A flag has:

- three pointwise-labelled root vertices;
- two unordered free vertices; and
- total order five.

The product of two such flags has order five, six, or seven.  Consequently
every matrix entry is an exact integer linear combination of the frozen
order-five, order-six, and order-seven induced-subgraph counts.

All eight labelled root patterns are retained.  No automorphism of a
hypothetical target graph is assumed.  The exact family census is:

| Root pattern | Isomorphism type | Flags | Ordered roots at `n=99` |
|---|---|---:|---:|
| `000` | independent triple | 64 | 590,436 |
| `001`, `010`, `100` | one edge | 56 each | 99,792 each |
| `011`, `101`, `110` | induced path `P3` | 42 each | 16,632 each |
| `111` | triangle | 20 | 1,386 |

Every root has `C(96,2)=4560` free pairs.

## Exact discovery finding

The two frozen Wave 43/44 witnesses and all fifteen immutable Wave45-v1
integer witnesses are exactly indefinite in every one of the eight
three-root families.  Across the 17 witnesses the run found 2,664 exact
integer negative directions and 2,657 distinct primitive PSD inequalities.
Every inequality has the form

```text
constant + sum_H coefficient[H] * x_H >= 0
```

for the 208 order-seven variables, and its recorded source witness makes the
left side strictly negative.

This is a candidate strengthening of the aggregate relaxation.  It rejects
17 particular count vectors; it does not exclude all solutions of the count
system and does not prove the endpoint impossible.

## Controls

For both the Petersen and Clebsch graphs, all eight coefficient expansions
equal a direct sum of integer outer products exactly.  Thus every control
matrix is positive semidefinite by construction.  The coefficient enumerator
also checks symmetry, exact embedding totals for every unrooted class, the
full ordered-root partition, and the all-ones normalization at `n=99`.

## Compact handoff

`compact-handoff.json` is the verifier-facing artifact.  It is 230,767 bytes
and contains:

- all frozen input hashes;
- the exact family and class-stream censuses;
- control-matrix hashes;
- source support hashes for all 17 witnesses;
- one deterministic representative exact cut per witness;
- hashes and byte sizes for the complete reconstruction; and
- an explicit `UNKNOWN` endpoint status wall.

Its canonical payload SHA-256 is
`e6d1991c20c8c30c4e393a081cf3fa3c4264b6ee5dacae279d5b6ab726766867`.

The full reconstruction artifacts are intentionally outside the compact
manifest:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `coefficients.json` | 4,868,254 | `07b55f06ff8f7d5f2de53d92a3222366e122a7306028752ecd31c10962a824b3` |
| `results.json` | 3,159,944 | `a58d04b56ed66094536ffc158b32085e3e940e5c3e42a3983a471e95e99daf37` |
| `cuts.json` | 42,757,624 | `d2ea38ed74a1b9098c9cc8eae52f8d65723c2631335b0acedba647dc16aa313e` |

## Deterministic reconstruction

From the repository root:

```powershell
.\.venv\Scripts\python.exe attempts\wave47-three-root-moment\three_root_moment.py
.\.venv\Scripts\python.exe attempts\wave47-three-root-moment\compact_handoff.py
.\.venv\Scripts\python.exe -m unittest attempts\wave47-three-root-moment\test_three_root_moment.py -v
```

The first command enforces a 20% free-physical-memory guard before launch and
at every family/target continuation boundary, leaving a safety margin above
the user's 15% floor.  The observed full run stayed between 53.05% and 54.53%
free at its recorded checkpoints.

## Scope wall

- coefficient enumeration: exact discovery-side construction;
- 17 source witnesses: exactly separated by retained integer directions;
- Petersen/Clebsch controls: exact direct-versus-expansion equality;
- independent verification: pending;
- full PSD-constrained count-system feasibility: not tested;
- endpoint `n3=4158`: `UNKNOWN`;
- strict upper bound below `4158`: `NOT_PROVED`;
- graph construction: none;
- external mathematical novelty: `UNKNOWN`.
