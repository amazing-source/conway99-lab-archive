# Wave 65 protocol

## Frozen target

Condition on a prism-free hypothetical `srg(99,14,1,2)` at the endpoint
`n3=4158`. Fix one vertex. The 84 residual vertices are labelled by the edges
of `H=K14-7K2`. Write the residual adjacency as `B=T+D`, where `T` contains
the 84 selected intersecting-label edges and `D` contains the 420
disjoint-label edges.

The package independently reconstructs the rooted scaffold and checks

```text
B^2+B = 10I+2J-Q,
spectrum(B) = 12^1, 3^40, 0^7, (-2)^6, (-4)^30.
```

Here `Q` is the line graph of `H`.

## Separation and status

- The discovery package may emit only `DERIVED`, `CANDIDATE`, `REFUTED`, or
  `UNKNOWN`; it cannot verify itself.
- Scaffold group averaging is allowed only for universally valid PSD matrices.
- The explicit positive control is intentionally unlabelled and local. It is
  not a residual-graph candidate, and its failure of the target moments is
  recorded rather than repaired.
- Floating eigenvalues, solver exits, and search nonhits are not evidence.

## Exact routes

1. Reconstruct the 84 labels, endpoint incidence, line graph, orbital
   valencies, and block-equation right-hand side.
2. Factor `D+5I=ZZ^T` and transfer to the 140-vertex block-intersection graph
   `R=Z^T Z-3I`.
3. Check trace moments through degree four for the Gram factorization and
   through degree six for `B` and `T`.
4. Check finite-field ranks by exact modular elimination.
5. Check scaffold-averaged PSD blocks for every integer `y=0,...,42`.
6. Retain exact positive controls and identify the first missing coupled
   invariant if no contradiction appears.
