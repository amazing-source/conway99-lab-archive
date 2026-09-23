# Wave159 four-root cut-loop protocol

## Frozen scope

Starting from the sealed Wave152 thirteen-cut exact witness and its frozen
four-root evaluation:

1. derive the fresh exact root-mask-3 and root-mask-12 covariance cuts;
2. retain all thirteen prior cuts and add both fresh cuts;
3. run a tight-tolerance HiGHS scout on the pair-root zero face;
4. if and only if numerical feasibility is credible, reconstruct and replay
   an exact rational fifteen-cut witness;
5. reevaluate all four-root blocks only if host memory remains comfortably
   above the 15% floor.

## Immutability

Every top-level regular file in `attempts/wave152-four-root-order8` was hashed
before inspection. The pre-existing `__pycache__` directory was outside that
inventory; its four files all predate Wave159. Wave159 writes only under
`attempts/wave159-four-root-cut-loop`. Python runs set
`PYTHONDONTWRITEBYTECODE=1` so importing frozen scripts cannot create bytecode
beside them. A second inventory over the same frozen paths must match before
the package is sealed.

## Evidence boundary

- Solver status and floating residuals are diagnostic.
- Feasibility is promoted only after exact rational reconstruction and replay.
- Discovery cannot independently certify itself.
- A count pseudowitness is not a graph.
- Endpoint feasibility, a strict upper bound, and Conway-99 remain `UNKNOWN`
  unless separately proved.
- Every retained-cut restriction and every active-cut choice must be recorded.

## Resource boundary

At least 15% of host physical memory must remain free. The first Wave159
sample was 28.49%. Any optional heavy reevaluation is skipped unless
headroom is comfortably above the floor.
