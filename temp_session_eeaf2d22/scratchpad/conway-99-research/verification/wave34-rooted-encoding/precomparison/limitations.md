# Stage 1 limitations and status wall

- This is a precomparison clean-room reconstruction.  No Wave 34 candidate,
  discovery code, attempt output, sibling message, or sibling artifact was
  inspected.
- The specification and executable translation are authored by this verifier;
  their passing self-tests cannot promote them to `VERIFIED`.
- No DIMACS or full JSONL map was emitted in Stage 1.  The deterministic
  4,319,043-clause stream was counted and hashed in memory only.
- No SAT solver or proof checker was invoked, and no large search was
  attempted.
- The exact variable and clause counts are for this prefix-threshold CNF
  translation.  A candidate may use another equisatisfiable encoding and have
  different auxiliary counts.
- Small exact-count encodings were checked exhaustively, but the full formula
  was not exhaustively tested or solved.
- No satisfying `D,B` pair and no complete exclusion certificate is supplied.
- The criterion is complete only for the conditional 99-vertex graph
  extension.  It does not discharge projector, lattice, tensor, Schur,
  endpoint, `n3=708`, Conway-99, or novelty obligations.
- The labeled domain has no automorphism, orbit, transitivity, Cayley,
  circulant, outside-vertex symmetry, or fixed-design restriction.

```text
clean-room encoding specification: DERIVED
candidate comparison:             NOT STARTED
binary criterion solution:        UNKNOWN
rooted graph extension/exclusion:  UNKNOWN
rooted endpoint:                   UNKNOWN
n3=708:                            UNKNOWN
Conway-99:                         UNKNOWN
novelty:                           UNKNOWN
```
