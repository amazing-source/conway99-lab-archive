# Independent verifier protocol for Wave 49

The verifier should use the sealed compact handoff and package manifest, but
must not import or call `five_root_moment.py` or `combined_sdp_scout.py`.

## Exact reconstruction

1. Rehash every frozen input and reconstruction artifact.
2. Independently enumerate every labelled simple graph at orders five, six,
   and seven satisfying adjacent common-neighbor cap one and nonadjacent cap
   two; remove complete vertex-permutation orbits.
3. Reconstruct the 21 canonical order-five masks and the stated attachment
   dimensions.
4. For every order-six and order-seven unrooted class, enumerate ordered
   five-root embeddings and same/distinct free-vertex products directly.
5. Compare all canonical-family coefficient entries and canonical payload
   hashes.

## Root-relabel theorem

Construct tensors for all 683 labelled admissible root masks.  For each of
the 21 canonical roots and all 120 root permutations, check:

- the attachment map is a bijection;
- every order-six tensor is permutation-congruent;
- every order-seven tensor is permutation-congruent; and
- no automorphism divisor occurs in the embedding totals.

The verifier must describe this as coordinate relabelling, not a target-graph
automorphism.

## Controls and witnesses

- Rebuild Petersen and Clebsch independently.
- Compare direct integer outer-product matrices with coefficient expansions
  for all 42 graph/family pairs.
- Check all-ones normalization and exact PSD-by-construction.
- Rehash all 17 supports, reconstruct their lower decks exactly, compare every
  witness matrix hash, and replay every supplied integer negative direction.

## Numerical scout boundary

The Wave48+Wave49 SDP may be replayed numerically, but solver status, floating
duals, residuals, and small eigenvalue margins remain diagnostics.  Do not
promote infeasibility without a complete exact rational dual certificate.

Permitted verification labels are `VERIFIED_SCOPED`, `REFUTED`, or `UNKNOWN`.
Endpoint `n3=4158`, a strict upper bound, graph construction, and Conway-99
must remain `UNKNOWN` or `NOT_PROVED`.
