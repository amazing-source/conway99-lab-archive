# Wave 33 rooted construction correction ledger

## Pre-search scope correction

The initial `protocol-freeze.md` calls the three outside-block equations the
"complete finite labeled domain." Precisely:

- they are complete for extending the already-forced labeled support to a
  full simple `srg(99,14,1,2)`;
- they are a finite relaxation of the full frozen rooted `n3=708` endpoint,
  because the latter also retains the projector, lattice, tensor, and Schur
  conditions in `verification/wave33-continuation-protocol.md`.

A complete graph witness would still be a positive Conway-99 certificate.
A complete proof that the graph-extension domain is empty would exclude the
rooted branch. Any proper relaxation of the graph equations proves neither.

This correction was recorded before construction search. The initial bytes
remain unchanged, and the orchestrator protocol is frozen separately in
`input-addendum.sha256`.
