# Wave 42 branch-15 triangle-delta verifier

## Assignment

Independently check the proposed seventh-triangle prism-clause reduction in
refined endpoint branch 15 without relying on the discovery implementation.

## Verdict

`VERIFIED_SCOPED_REDUCTION`.

The clean-room implementation independently replayed the frozen OPB closure,
derived `x2=1`, reconstructed the rooted triangle `[1,15,17]`, and enumerated
the complete clause family. Only after freezing those results did the verifier
parse the discovery catalogues. Both complete normalized clause streams match
exactly.

The verified delta has 64,932 raw clauses and 33,778 clauses after independent
closure simplification. It yields no unit or contradiction. Branch 15 remains
open, endpoint coverage remains 0/33, and Conway-99 remains `UNKNOWN`.

Reproduction commands, exact hashes, limitations, hostile tests, and the
post-freeze comparison are in
`verification/wave42-branch15-triangle-delta/`.
