# Wave 74 hostile controls

- `d_x` counts neighbors in **each** sign side, not total support degree;
  total support degree is \(2d_x\).
- The outside set has 83 vertices at norm 16 and 81 at norm 18.
- Side-to-outside incidences are recomputed from degree 14, cross edges, and
  twice the same-side edge count.
- Pair capacities distinguish adjacent pairs (\(\lambda=1\)) from
  nonadjacent pairs (\(\mu=2\)).
- The \(h=2\) pigeonhole uses disjoint same-sign edges.  The adjacent-edge
  shape is separately rejected because 71 internal incidences exceed
  capacity 70.
- Histogram enumeration is complete for \(0\le d\le7\), forced by
  \(2d\le14\).
- Surviving histograms are labeled necessary, never constructive.
- No solver status, floating arithmetic, automorphism, or transitivity is
  used.
- Conway status and novelty are explicitly `UNKNOWN`.
