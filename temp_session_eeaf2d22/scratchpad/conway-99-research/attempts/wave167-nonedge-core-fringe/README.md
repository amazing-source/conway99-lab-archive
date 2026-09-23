# Wave 167: nonedge core, fringe, and global defect

Status: `DERIVED`; the structural counts and defect identity have an
independent verifier, but the endpoint remains `UNKNOWN`.

## Exact correction to Wave 166

Fix a nonedge `uv` with common neighbors `p,q`, and assume the prism-free
endpoint `P=0`. The 40 marked induced five-cycles rooted at `uv` split
exactly into:

```text
36 core marks + 4 fringe marks.
```

All four fringe marks fail the canonical Wagner-completion test. This proves

```text
f(uv) >= 4,
```

not the Wave 166 sufficient target `f(uv)<=4`. Equality would additionally
require every core mark to succeed.

## Completion uniqueness and exact defect

A successful marked five-cycle has at most one Wagner completion: one
completion vertex is already forced as the second common neighbor of a
specified nonadjacent pair. Conversely, every induced Wagner graph supplies
exactly eight successful marked-cycle incidences. Hence, for the total number
`F` of failed marks,

```text
F = 166320 - 8*W8.
```

The four mandatory failures at each of 4,158 nonedges give a baseline

```text
B0 = 4*4158 = 16632.
```

Define the extra defect

```text
E = F-B0 = 149688-8*W8 = 8*(18711-W8).
```

Thus `E` is a nonnegative multiple of eight. At the prism-free endpoint,
the verified cube upper bound and cube/Wagner covariance imply

```text
W8 <= 18709,
```

so any endpoint graph would have

```text
E >= 16.
```

It is therefore sufficient to prove the strictly weaker global stability
statement

```text
E <= 8.
```

The old pointwise equality `f(uv)=4` would force `E=0`, but is more than the
endpoint argument needs.

## Why a larger space is necessary

An explicit abstract 22-edge cross-shell obeys all currently derived root
degrees and root-visible `P=0` exclusions while producing at least four
additional core failures. It is not a full strongly regular graph, so it is
not a counterexample to the desired global result. It proves that local shell
equations alone cannot establish it.

The next attack must couple overlapping nonedge roots, use a full exact
rooted conic certificate, or translate the problem to the incidence geometry
of the graph's unique edge-triangles.

No strict `n3` bound, endpoint exclusion, graph, literature novelty, or
Conway-99 resolution is claimed.
