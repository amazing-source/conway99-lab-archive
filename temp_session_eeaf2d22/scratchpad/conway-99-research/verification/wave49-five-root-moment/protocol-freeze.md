# Wave 49 five-root moment clean-room protocol

Freeze time: 2026-07-27, after reading only
`attempts/wave49-five-root-moment/verifier-protocol.md` and
`input-freeze.sha256`, before opening the Wave 49 discovery implementation,
coefficients, or result.

Role: verifier. This lane writes only under
`verification/wave49-five-root-moment/` and
`agents/2026-07-27-wave49-five-root-moment-verifier.md`. It will not import
or execute `five_root_moment.py` or `combined_sdp_scout.py`, and it will not
stage, commit, or publish.

## Frozen exact scope

Independently reconstruct:

1. every labelled simple graph on 5, 6, and 7 vertices satisfying:
   - adjacent vertex pairs have at most one common neighbor;
   - nonadjacent vertex pairs have at most two common neighbors;
2. complete vertex-permutation orbits and canonical representatives;
3. all 21 canonical order-five rooted families and their admissible
   one-vertex attachment coordinates;
4. every order-six single-free tensor and every order-seven ordered
   same/distinct-free product coefficient, using ordered root embeddings and
   no automorphism divisor;
5. all 683 labelled admissible five-root masks and all 21 times 120 canonical
   root permutations, for 2,520 explicit coordinate-congruence mappings at
   each tensor order;
6. independent Petersen and Clebsch graph controls, direct integer
   outer-product matrices, coefficient-expanded matrices, all-ones
   normalization, and exact PSD-by-construction for all 42 graph/family
   pairs; and
7. all 17 frozen supports, their exact lower decks, all 357
   support/family witness matrices, and every supplied integer negative
   direction.

The number 2,520 counts canonical-root/permutation mapping families, not
target-graph automorphisms. A rooted coordinate relabelling changes tensor
coordinates only and may never divide an embedding total.

## Independent commitments before comparison

Before opening Wave 49 discovery code, `coefficients.json`, or `results.json`,
freeze:

- all upstream input hashes;
- canonical labelled/unlabelled graph catalogues for orders 5, 6, and 7;
- the 21 root masks and attachment-coordinate catalogues;
- complete order-six and order-seven coefficient payloads and hashes;
- all 2,520 order-six and 2,520 order-seven permutation-congruence checks;
- Petersen/Clebsch control matrices and hashes;
- all 17 support hashes, lower-deck hashes, 357 witness matrices, negative
  directions, and exact quadratic values;
- the independent implementation and result hashes.

Only after that freeze may the discovery result be parsed as an untrusted
claim. Discovery solver statuses, floating duals, residuals, and eigenvalue
margins are never exact evidence.

## Canonical graph convention

A labelled graph on `n` vertices is encoded by a bit mask in lexicographic
edge order

```text
(0,1),(0,2),...,(0,n-1),(1,2),...,(n-2,n-1).
```

Canonicalization is the minimum relabelled mask over all `n!` vertex
permutations. Orbit removal must enumerate every labelled mask or otherwise
prove exactly equivalent coverage. Attachment coordinates are the admissible
five-bit neighborhoods of a sixth vertex; coordinate order is increasing
attachment mask.

For an unrooted order-six or order-seven graph, every ordered injection of
the five labelled roots is visited. The remaining one or two vertices
determine attachment coordinates. Same-free products use the same remaining
vertex; distinct-free products use ordered distinct remaining vertices.
Every count is integral and no stabilizer or automorphism division is used.

## Tensor and relabelling checks

For every labelled admissible root mask, reconstruct its attachment
coordinate list and both coefficient tensors. For each canonical root and
each of the 120 permutations:

- explicitly map each attachment bit mask;
- prove the map is a bijection;
- map the root mask and identify its labelled-root tensor;
- check every order-six coefficient;
- check every order-seven same/distinct coefficient;
- check embedding totals before and after relabelling; and
- reject any normalization by a root or ambient automorphism size.

## Controls and witnesses

Petersen and Clebsch adjacency must be reconstructed from their standard
finite combinatorial definitions, not copied from the candidate output. For
each root family, enumerate every ordered root embedding in the control graph
and count admissible attachments directly. Its direct moment matrix is the
integer sum of attachment-count outer products. Independently expand the
order-six/order-seven coefficient tensors against the graph's induced
six/seven-vertex class counts and require entrywise equality.

Each moment matrix must satisfy exact all-ones normalization and be PSD by
its explicit integer Gram decomposition. Numerical eigenvalues are not used.

For each of 17 frozen supports:

- bind the raw support hash;
- reconstruct every one-vertex-deletion lower-deck class exactly;
- for all 21 root families reconstruct the witness matrix;
- bind its canonical hash;
- parse each supplied integer direction;
- recompute its exact integer quadratic value; and
- require strict negativity exactly where claimed.

## Hostile tests

Reject a changed input hash, edge-bit order, common-neighbor cap, omitted
labelled graph, wrong canonical representative, attachment-coordinate
permutation, missing root injection, automorphism division, swapped same and
distinct free vertices, altered tensor coefficient, changed control edge,
incorrect normalization, omitted support/deck card, witness-entry mutation,
direction-coordinate mutation, or quadratic-value mutation.

## Resource and status wall

At least 20 percent of physical memory must remain free. No persistent
background process is started.

Agreement may receive `VERIFIED_SCOPED` only for this finite coefficient,
coordinate-congruence, control, and witness calculation. Endpoint
`n3=4158`, branch closure, a strict upper bound, graph construction, novelty,
and Conway-99 remain `UNKNOWN` or `NOT_PROVED`.
