# Independent verification protocol

## Frozen premises

Work conditionally under the Wave 181 equality face and verified Waves
178--179 and 182--183:

1. nonedge star-root intersections are singletons;
2. global-root supports are `5K1`, `3K2`, or `C7`;
3. adjacent-star common roots exclude their shared triangle and yield
   balanced outer-star relations;
4. a balanced edge circuit serves exactly one graph edge and cannot be a
   nonedge-realizing circuit;
5. the equality face supplies 2,079 distinct canonical projective
   weight-four conics.

## Verification method

- Re-prove the support-intersection bound from pairwise nonedge uniqueness
  and triangle-freeness.
- Audit all four columns and coefficients of an edge-root relation before
  invoking dual distance four.
- Recover the root from the projective relation to establish same-edge
  injectivity.
- Apply the verified edge-isolation theorem only after checking its balance
  hypotheses.
- Derive `E=3*n6+7*n7`, the modulo-five obstruction below 12, and the
  ternary projective-to-word factor independently.
- Use no graph, code, SAT, configuration, or isomorphism search.

## Promotion boundary

Promote the conditional lower bound only.  The arithmetic witness for
`E=12` is not a geometric realization, and the lower bound is not an
endpoint contradiction.
