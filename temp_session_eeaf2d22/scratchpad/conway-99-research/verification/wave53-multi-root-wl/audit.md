# Wave 53 multi-root WL independent audit

Verdict: **VERIFIED for the stated finite two-root templates.** There are no
numerical corrections to the discovery claims. No root relation is excluded,
and both the prism-free endpoint and Conway-99 remain `UNKNOWN`.

## Independent reconstruction

The verifier froze `protocol.md` before reading the discovery implementation
or result. `independent_check.py` imports only the Python standard library and
does not import or call discovery code.

For `K`-related roots, the shared graph vertex lies in seven graph triangles:
the two roots and five other triangles. Hence there are five common
`K`-neighbors. For disjoint roots, every root-to-root cross edge lies in a
unique triangle, and every common `K`-neighbor supplies such an edge. The
definitions of relations `B,C,D` therefore give `2,1,0` common
`K`-neighbors.

The two cross edges in the `B` case use distinct root endpoints, because two
edges sharing a root endpoint would give an adjacent pair a second common
neighbor, contradicting `lambda=1`. Let the corresponding common triangles be
`T0,T1`. They already have two cross edges, one internal to each root
triangle. Adjacent-pair uniqueness forbids endpoint-to-third-vertex cross
edges; the only possible third edge is between the third vertices, and it
would form a triangular prism. Under the frozen prism-free scope it is absent,
so the shared Boolean variable `{T0,T1}` is fixed true for relation `B`.
This is graph-level forcing, not a consequence of the cap equations alone.

Each root contributes `3 * 36 = 108` cross-sector candidates and 36 caps.
Only the `B` pair above represents the same unordered actual triangle pair in
both rooted systems. The resulting exact counts are:

| relation | common K | triangle core | candidates | shared | caps | order |
|---|---:|---:|---:|---:|---:|---:|
| K | 5 | 31 | 216 | 0 | 72 | 319 |
| B | 2 | 36 | 215 | 1 | 72 | 323 |
| C | 1 | 37 | 216 | 0 | 72 | 325 |
| D | 0 | 38 | 216 | 0 | 72 | 326 |

Every cap contains six distinct candidate variables and has right side two.
An ordinary candidate has two cap incidences per rooted context; the merged
`B` candidate has four. Candidate IDs are canonical unordered pairs of actual
triangle IDs. The verifier's external aliases form an exact bijection with
the discovery node envelope, ruling out label-based split/merge errors.

## Exact WL results

The verifier uses exact integer signatures, synchronous refinement, and
canonical signature ordering. It recomputed the full ordered-pair partition,
then checked intersection counters for every pair in every stable color
class, not only one representative.

| relation | 2-WL color sequence | stable 2-WL | nonzero intersections | 3-WL sequence | stable 3-WL |
|---|---|---:|---:|---|---:|
| K | 34, 133, 283, 285 | 285 | 11,268 | 73, 107 | 107 |
| B | 44, 140, 578, 584 | 584 | 32,018 | 103, 287, 321 | 321 |
| C | 30, 82, 319, 321 | 321 | 12,562 | 88, 206, 240 | 240 |
| D | 30, 50, 63 | 63 | 1,600 | 61 | 61 |

For each relation, a deterministic nonidentity vertex permutation was applied
and both closures were recomputed. After mapping tuples back, the 2-WL and
3-WL partitions were unchanged. Thus the counts do not depend on insertion
order, hash order, node names, or a hidden automorphism assumption.

Using the independently derived semantic node bijection, the stored discovery
2-WL partition is exactly equivalent to the clean-room partition for all
ordered pairs. Its entire intersection tensor agrees after the induced color
bijection. The discovery's stored 2-WL partition and intersection-tensor
hashes also recompute correctly.

The triangle-core calculation is the explicitly claimed folklore 3-WL
variant, with the same replacement vertex used in all three coordinate
replacement colors. Independent stable color counts and complete class-size
multisets match in all four cases.

### Record-envelope caveat

The discovery JSON stores a `tuple_partition_sha256` for 3-WL but omits the
triple-color vector from which that hash was computed. Therefore that stored
hash is **not reconstructible from the discovery JSON alone**. This is an
envelope limitation, not a numerical correction: the independent records
contain their full triple-color vectors, and independent recomputation matches
the claimed 3-WL counts and discovery class-size multisets.

## Positive controls and scope

The verifier constructed controls independently using offsets 0 and 2 in
each `K6,6` sector pair, rather than the discovery's documented offsets 0 and
1. Every one of the 72 cap equations was evaluated exactly. The selected
unique-variable counts are 72 for `K,C,D` and 71 for `B`; the latter is
because its forced-true variable is shared by both rooted systems.

These controls prove only feasibility of the merged local cap equations. They
are not supplied to WL, do not select an arbitrary completion for the
unresolved `B/C` variables, and do not construct or extend to an
`srg(99,14,1,2)`.

## Adversarial checks

The 12 clean-room tests reject a wrong overlap, a split shared candidate, a
missing `B` force, a missing cap, a deleted control edge, a mutated stored
partition hash, nonsquare WL inputs, and partition splitting. The construction
also rejects arbitrary values on unresolved `B/C` pairs.

The discovery input-freeze and package-manifest references all match current
files. The discovery exact envelope has SHA-256
`d99d89ef56cbd1f603cc8668b340bd7ad20993570899eaf556ee4c9a7f400717`;
all four embedded relation-record hashes validate. Standalone component files
are not shipped in the discovery directory, but all four records are embedded
and individually hashed inside `exact-result.json`.

The final exact run enforced a 15 percent free-physical-memory floor at every
WL round. The host remained above 52 percent free at the observed checkpoints.

## Status boundary

- finite two-root CSP construction and caps: `VERIFIED`
- claimed stable 2-WL counts and intersection parameters: `VERIFIED`
- claimed triangle-core folklore 3-WL counts: `VERIFIED`
- positive local controls: `VERIFIED` for local cap scope only
- excluded root relations: none
- prism-free endpoint: `UNKNOWN`
- Conway-99: `UNKNOWN`

The agent report's `DERIVED` label and `UNKNOWN` endpoint language are
appropriately conservative.
