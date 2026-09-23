# Wave 32 orchestrator correction and scope ledger

## Publication wall

Wave 32 verifies two necessary endpoint reductions and a bounded source
audit. It does not construct or exclude `srg(99,14,1,2)`, exclude
`n3=708`, improve the conditional lower bound `n3>=708`, classify either
surviving endpoint branch, or establish novelty.

The exhaustive actual-incidence endpoint split remains:

```text
rooted endpoint:                              UNKNOWN
rootless integrally decomposable endpoint:   VERIFIED IMPOSSIBLE
rootless integrally indecomposable endpoint: UNKNOWN
```

The middle line always means an **actual-incidence** endpoint. It is not a
matrix-only theorem.

## Rooted discovery v1 correction

The first frozen rooted discovery checker and JSON stated that the
hostile partial control's outside vertices needed remaining degrees
`8,12,14`. The independent verifier reconstructed current outside degrees

```text
4^42,2^28,0^15
```

and therefore the correct residual degrees

```text
10^42,12^28,14^15.
```

The original hashes, false value, and repair are preserved in
`attempts/wave32-rooted-vector/correction-ledger.md`. The corrected
discovery suite computes and asserts both distributions. Its hostile
eigenvalue-three metadata was also made parameter-dependent rather than
reusing eigenvalue-four prose.

The v1 discovery suite emitted several proof bridges as strings or solved
constants. Those tests were not used to promote the claim. The designated
verifier wrote a clean-room implementation, did not import or execute the
discovery checker, and independently computed the primitive-image,
modulo-three, amplitude, Fano-design, outside-census, tensor, and reflection
steps. Its corrected-byte replay preserves the v1 objection and separately
passes the v2 discovery manifest.

## Odd-prime code inference rejected before freeze

An early indecomposable proof draft incorrectly inferred

```text
X^T X=21S^-1=0 modulo 3 and modulo 7
```

merely from integrality. The orchestrator rejected that inference before
the discovery result was frozen. The public failure ledger retains it and
the corrected statements:

```text
rank_Fp(G)=v_p(h),
rank_Fp(M)=44-v_p(h).
```

The independent verifier checks all eight determinant rows, the code-hull
dimensions, and explicit controls refuting universal self-orthogonality.

## Independent-result status-label correction

The first assembled indecomposable verifier JSON retained the discovery
label `DERIVED_VERIFICATION_PENDING` even though its audit and run report
already said `VERIFIED`. The orchestrator caught the mismatch before
publication. The final verifier output uses a scoped verification label and
keeps motif forcing, endpoint existence, `n3=708`, Conway-99, and novelty
`UNKNOWN`.

## Literature-package corrections

The first 14-record literature package passed its mathematical
applicability audit but needed three ancillary corrections:

1. the published author order for *Reflective Integral Lattices* is Rudolf
   Scharlau, then Britta Blaschke;
2. the Hemkemeier--Vallentin algorithm assumes a complete generating system
   through a suitable norm bound, not merely an unspecified supplied
   lattice; and
3. Ali Keramatipour's already-public SAT report was omitted from the
   Wave 32 metadata set.

The corrected package records `14 original + 1 post-audit = 15` sources,
preserves the original 68-query/17-batch chronology, and describes the SAT
work only as computationally infeasible at its tested scale. The v1 hashes
and objections are retained in
`verification/wave32-literature-audit/correction-ledger.md`; the independent
v2 replay checks every correction. Bounded non-discovery remains neither a
novelty certificate nor a theorem of global openness.

## Bibliography freeze boundary

The independent literature verifier freezes the pre-Wave-32
`SOURCES.bib` bytes as a supporting input. Seven sources first located in
this wave are fully recorded, with identifiers and applicability limits, in
`verification/wave32-literature-audit/source-metadata.json`, but are not yet
duplicated into `SOURCES.bib`. Editing the bibliography here would invalidate
the 17-test corrected-byte replay and require a fresh independent freeze.
Accordingly, the Wave 32 claim and obligation use the verified metadata file
as their complete source record and do not represent `SOURCES.bib` as a
complete Wave 32 bibliography.

## Orchestrator harness correction

The first manual validation of the indecomposable verifier manifest
incorrectly treated repo-root-relative manifest paths as package-relative,
producing doubled paths such as
`verification/wave32-indecomposable/verification/wave32-indecomposable/...`.
The next invocation used the manifest's actual repo-root convention and
passed every entry. This was a validator invocation error, not an artifact
failure.

## Unchanged global status

```text
rooted Fano-support reduction:                    VERIFIED SCOPED
rootless connectivity and forbidden-motif rules: VERIFIED SCOPED
rooted endpoint exclusion:                       NOT OBTAINED
actual incidence forces the rootless motif:      UNKNOWN
rooted endpoint:                                 UNKNOWN
rootless integrally indecomposable endpoint:     UNKNOWN
n3=708 / Conway-99 / novelty:                    UNKNOWN
```
