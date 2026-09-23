# Wave144 six-set odd-profile clean-room verification

## Verdict

**PASS_NULL_BOUNDARY**, with claim label **VERIFIED** for the relaxation
statement only.

The sealed Wave144 payload supplies an exact integer feasible point at
`n3=4158` for its six-set odd-output marginal relaxation. This is the already
imported upper cap, so the package establishes a null boundary: the new
relaxation does not exclude the endpoint and does not improve the bound.

## Manifest binding

The discovery manifest was frozen before discovery internals were inspected.
Its SHA-256 digest is:

`b5369353ac6959b0662e3f424cf80e48094ac6bcdb79572bf604632c45509436`

The clean-room verifier confirmed that the live manifest still has those exact
bytes and that all ten sealed discovery artifacts match their listed hashes.
The four prerequisite artifacts also match the hashes frozen in the payload.

## Independent checks

- Regenerated exactly 9, 21, and 62 locally admissible unlabeled graph classes
  of orders 4, 5, and 6.
- Independently reconstructed deletion decks and obtained unique/bijective
  source-class alignments.
- Recomputed all 62 exact local output-weight support sets by exhaustive
  integer enumeration of the 64 `z_P` cells.
- Produced and replayed an independent local witness for all 368 attainable
  class/weight cells. The canonical witness collection has SHA-256 digest
  `7bd5bb358bfef588fb6716806402f593cf0dbc234c578c23b677ca1754f39baa`.
- Confirmed the four singleton supports:
  class 1 to 66, class 3 to 56, class 5 to 46, and class 14 to 36.
- Confirmed class 36 has support
  `{24,28,32,36,40,44,48,52,56,60,64,72}`. A second exhaustive traversal
  with reversed high-cell order again excluded weight 68.
- Replayed all 66 selected sparse local `z_P` witnesses. Their key set is
  exactly the 65 aggregate cells together with the four forced cells; overlap
  leaves 66 distinct keys.
- Replayed all 65 positive integer cells of the endpoint aggregate and all 62
  class marginals. Their sum is `C(99,6)=1,120,529,256`.
- Independently reproduced the reciprocity moments:
  `1,120,529,256`, `12,854,346,120`, `55,869,122,232`, and
  `84,712,070,520` for `t=0,1,2,3`.
- Independently reproduced signed `S_6=2,734,116`.
- Host memory remained above the required 20% free threshold; the observed
  free-memory snapshots around the full replay were approximately 44%.

The regression suite passed five tests, including hostile changes to one
local witness, one aggregate count, and the selected-local key set.

## Audit of the earlier verifier

The existing `verification/wave144-sixset-odd-profile` package has an intact
five-entry manifest with SHA-256
`f0f2f6b2250b60da8949449ee0bbc0ba680a7ea982eca6dee3f48428d0546140`
and stores the same verdict. Because it was authored by the discovery agent,
this clean-room review treats it only as an integrity-checked auxiliary
artifact. It was not used to establish this verdict.

## Exact unresolved boundary

No global graph realization is established. The aggregate proves that
class/weight totals can be filled with individually valid local `z_P`
solutions, but it does not place those solutions on the actual six-subsets of
one common 99-vertex set.

In particular, two chosen six-subsets may overlap in five vertices. Their
local certificates must then refer consistently to the same outside vertices,
the same incidences from those vertices into the shared five-set, and the same
adjacencies. Wave144 has no variables or equations that identify those shared
objects across its separately chosen local witnesses. This missing
overlap/gluing consistency is precisely why `PASS_NULL_BOUNDARY` is not a
graph construction, a counterexample, or a better upper bound.
