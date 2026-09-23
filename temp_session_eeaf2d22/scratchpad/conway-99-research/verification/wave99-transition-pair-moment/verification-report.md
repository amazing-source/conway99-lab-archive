# Wave 99 verification report

Verdict: **VERIFIED SCOPED**.

## What was independently reproduced

- The rooted seed domain has `C(7,4) 2^4 = 560` seeds.
- There are 84 selected transitions, and each lies in exactly eight seeds,
  so `sum_Q j_Q = 672`.
- Fixing a transition `(s;a,b)`, center `s` contributes no second
  transition. At centers `a` and `b`, an identical-triple transition has
  weight eight; any non-identical alternative has weight at most two.
- The two identical-triple alternatives cannot coexist: the three residual
  labels `{s,a}`, `{s,b}`, and `{a,b}` would form a triangle. The fixed
  adjacent pair would then have the base point `s` and the third residual
  label as two common neighbors, contradicting `lambda=1`.
- Thus centers `a,b` contribute at most ten. The eight possible fourth-point
  centers contribute at most one each. All possible centers are thereby
  partitioned, giving the per-transition cap `18`.
- Summing the cap over all 84 fixed transitions gives the ordered moment
  `sum_Q j_Q(j_Q-1) <= 1512`, hence
  `sum_Q C(j_Q,2) <= 756`. This correctly retains multiplicity eight for
  two transitions on the same base triple and multiplicity one when their
  union has four points.
- For `0 <= j <= 4`, the exact pointwise certificate
  `1[j=0] <= 1-j/2+C(j,2)/6` has right sides
  `1, 1/2, 1/6, 0, 0`. Therefore at most
  `560-672/2+756/6 = 350` seeds are transition-free.
- `N14` counts oriented vectors, including both signs. Each oriented vector
  has seven positive roots, so
  `7*N14 <= 99*350`, with no further factor of two, and `N14 <= 4950`.
- The Wave 86 rearrangement has coefficients
  `1-180/217 = 407/2387` and
  `1-2344/2387 = 43/2387`. Multiplication by 2387 and insertion of
  `N14<=4950` gives
  `407*N16+43*N18 >= 2165002`.

The formal distribution `n0=350,n3=168,n4=42` saturates only the two
recorded seed moments. It is not asserted to be realizable by a graph.

## Hostile checks

The verifier enumerated all 6,040 prism-free local perfect matchings at the
relevant centers. Without the `lambda=1` triangle guard the two original
centers could contribute 16, demonstrating that the guard is essential;
with it their cap is 10. It also tested the incorrect division by 14 in the
root/sign conversion and rejected it.

The discovery package's nine manifest entries were rehashed, and its
manifest remained equal to the frozen hash
`e3a30e37bbf08dcd60e4fff7df6f8f4e51780987ba3446e96ff136954e94a9e6`.
All 17 verifier tests and all eight discovery tests passed.

## Scope boundary

`N14<=4950` assumes only the prism-free endpoint `P=0`, equivalently
`n3=4158`; it does not assume rank 28. The weighted shell inequality uses
the intersection of that branch with the additional rank-28 / `q=16`
hypothesis. No upper bound on `N16` or `N18`, no exclusion of that row, no
strict `n3<4158` bound, and no resolution of Conway-99 follows.

Novelty remains `UNKNOWN`; this audit verifies the internal mathematics,
not priority against the literature.
