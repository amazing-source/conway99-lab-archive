# Wave 17 \(n_3=54\) census: preinspection verification freeze

```yaml
role: verifier
date_utc: 2026-07-23T12:24:08Z
git_commit: WORKTREE_PREINSPECTION
claim_label: UNKNOWN
scope: Independent audit of the claimed exhaustive 457-case cubic-support census at the n3=54 boundary
inputs:
  - official House of Graphs cub18-gir5 graph6 catalog (URL and bytes to be independently fetched)
  - official House of Graphs cub12-gir5 graph6 catalog (URL and bytes to be independently fetched)
  - frozen structural reduction and discovery census, to be read only after this freeze
method: Precommitted checks below, implemented independently of the discovery code
command: To be recorded after implementation
outputs:
  - verification/n3-54-census/*
  - verification/2026-07-23-wave17-n3-54-census-audit.md
limitations:
  - This freeze does not assume the target graph exists or does not exist.
  - A SAT/SMT solver exit code, including UNSAT, will not be accepted as a certificate.
  - The status and novelty of the original SRG(99,14,1,2) problem remain UNKNOWN.
```

This file is being written before any discovery-census artifact is opened.  Its
SHA-256 will serve as the immutable statement of the intended checks.

## Frozen independent checks

1. Fetch both catalogs from their official House of Graphs URLs.  Record HTTP
   metadata, compressed and decompressed SHA-256 hashes, byte sizes, and tool
   versions.  Refuse silent redirects to a non-HTTPS or non-House-of-Graphs
   host.  Compare the independently observed hashes with every hash asserted
   by the discovery report.
2. Decode graph6 with a verifier-local parser rather than importing the
   discovery parser.  Reject malformed headers, truncation, noncanonical
   padding bits, loops, duplicate records, and unexpected graph orders.
   Validate every decoded graph as simple, cubic, connected, and of girth at
   least five.  Confirm exactly 455 order-18 records and two order-12 records.
3. Build the claimed 457 residual \(F\) cases independently: the 455 connected
   order-18 graphs, plus each of the two order-12 graphs disjointly unioned with
   a freshly constructed \(K_{3,3}\).  Validate orders, degrees, components,
   and girth, and check that these three component patterns exactly cover the
   structural reduction after the separately claimed \(3K_{3,3}\) exclusion.
4. Represent \(F\) by integer bitsets and represent support variables by
   unordered pairs of edge indices.  Re-derive all compatibility equations
   directly from the frozen structural identities, without importing discovery
   code or serialized kernels.
5. Reconstruct every compatible support and the GF(2) obstruction using an
   independently implemented packed-bit row reducer.  Check every emitted
   kernel basis vector against the original equations, enumerate each
   nontrivial kernel exhaustively, and validate every surviving support
   combinatorially over the integers (degree, simplicity, compatibility,
   component/cycle parity, and any claimed spectral or common-neighbor filter).
6. Independently prove and computationally check the mixed
   \(K_{3,3}+\)order-12 degree-count obstruction.  The proof must state the
   counted sets and multiplicities; the executable check must cover both
   order-12 catalog records and must not depend on an assumed automorphism.
7. Verify every discovery input/output/certificate hash quoted in the frozen
   report.  Recompute any concise result manifest from primary inputs.  Raw
   solver logs may be archived but cannot support an exclusion.
8. Add hostile tests for graph6 parsing and catalog tampering, support
   compatibility, malformed candidates, packed GF(2) row reduction and kernel
   enumeration, and the mixed counting obstruction.  Include at least one
   brute-force comparison against a tiny independently enumerable system.
9. Status policy: promote a conditional census claim to `VERIFIED` only if all
   exact checks pass and the structural bridge it consumes is explicitly
   delimited.  Otherwise label it `REFUTED`, `CANDIDATE`, or `UNKNOWN` and name
   the first unmet obligation.  Even a successful audit will not promote the
   original target or any novelty claim.
