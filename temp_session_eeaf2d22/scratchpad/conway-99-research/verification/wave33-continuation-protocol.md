# Wave 33 continuation protocol freeze

Date frozen: 2026-07-24T09:50:57Z

Public base commit:
`b2595baa40d50e9c259051751fe27090bee6a449`

Project status at freeze:

```text
Conway-99 existence/nonexistence:                 UNKNOWN
n3=708:                                           UNKNOWN
rooted endpoint:                                  UNKNOWN
rootless decomposable actual-incidence endpoint:  VERIFIED impossible
rootless indecomposable actual-incidence endpoint: UNKNOWN
strongest conditional bound:                      n3>=708
```

## Frozen inputs

| input | SHA-256 |
|---|---|
| `AGENTS.md` | `4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3` |
| `CONJECTURE.md` | `7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58` |
| `verification/wave32-rooted-vector/audit.md` | `36d83232d82e30205e0aefa30aedff0a517de1edb0adbaa54575ea68d04ce1a5` |
| `verification/wave32-rooted-vector/independent-results.json` | `4ed239e997e4485abdab4e26a2e28e2a981b6fff069c4d926ccff3d2241dbe6f` |
| `verification/wave32-indecomposable/audit.md` | `15285e618b3a38c91c5d2e373dcb859720a2062d9ca108cd79cae12506a53f44` |
| `verification/wave32-indecomposable/independent-results.json` | `4b90ef54358a14abc92c925c8e0f94ed9510b4f80857fde5aa4e2abf4ba89e2a` |
| `verification/2026-07-24-wave32-clean-clone.md` | `125f33304867ddd0b0031e9e35e582c47ef9cf400e0fe8fda18251b2a5d35f0c` |

## Target R: rooted continuation

Assume the exact frozen target graph and the full actual
vertex-triangle-incidence endpoint package at `n3=708`. Assume a norm-two
endpoint root. Wave 32 then permits, up to relabeling, only the signed
seven-plus-seven support whose induced graph is the bipartite complement of
the Fano incidence graph and whose triangle image has census

```text
(+1)^21,0^189,(-1)^21.
```

The Wave 33 rooted target is exhaustive within these premises:

1. extend this labeled representative to a complete simple graph satisfying
   `A^2=12I-A+2J`, together with every frozen projector, lattice, tensor, and
   Schur condition; or
2. exclude every such extension by a complete checkable argument or
   certificate.

Relabeling the already-forced support is allowed. No further graph
automorphism, orbit, transitivity, Cayley, circulant, or outside-vertex
symmetry may be assumed.

Necessary consequences that do not complete either item remain scoped
reductions. A partial graph, relaxation, timeout, heuristic nonhit, or
uncertified solver status is not an exclusion.

## Target I: rootless indecomposable continuation

Assume the exact frozen target, actual incidence, and a rootless endpoint.
Wave 31 excludes integral orthogonal decomposition, and Wave 32 proves that
the surviving endpoint is integrally indecomposable and requires

```text
tr(A_-1 A_-2^2)=0.
```

The Wave 33 rootless target is:

1. derive from actual incidence and the frozen projector/Schur package that
   `tr(A_-1 A_-2^2)>0`, thereby excluding the rootless branch; or
2. produce another complete obstruction or a complete valid endpoint
   construction.

Pair counts, low-order moments, finite-field analogues, or matrix-only
controls may delimit a proof route but cannot substitute for actual
incidence. Any hostile object must state exactly which premises it drops.

## Discovery separation

The initial rooted proof, rootless proof, and construction agents work from
the public Wave 32 checkpoint and do not inspect one another's new Wave 33
artifacts before saving their first reports. Discovery agents may label
results only `DERIVED`, `CANDIDATE`, finite evidence, or `UNKNOWN`.

Only the orchestrator may integrate or publish. Every substantive candidate
must receive a clean-room adversarial verifier that does not import or
execute discovery code. Repairs retain the failed bytes and receive a fresh
verification pass.

## Promotion wall

No Wave 33 artifact changes any global status unless all applicable
statement, exactness, independent-verification, clean-clone, and current
literature gates pass. In particular, a new necessary reduction does not
exclude `n3=708` and does not resolve Conway-99.
