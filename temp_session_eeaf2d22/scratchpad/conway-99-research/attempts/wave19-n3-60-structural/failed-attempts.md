# Retained non-closing attempts and evidence boundary

No computational command failed in this lane.  JSON generation, eleven
focused tests, and both byte-for-byte replay checks passed on their first
execution.

Two mathematical closure attempts did not produce contradictions and are
retained to prevent status inflation:

1. At `r=20,m=27`, the spectral and outside-neighbor inequalities are both
   equalities.  They force point sizes `2^21 3^6`, a 6-regular induced
   graph, and outside degree multiset `3^72`, but do not contradict them.
   The positive-meeting graph on the six size-three points is cubic.  Exact
   enumeration leaves both cubic isomorphism types, `K3,3` and the
   triangular prism.  Their explicit adjacency matrices are preserved in
   `residual-certificates.json`; neither matrix is a full target
   construction or proof of feasibility.

2. At `r=20,m=30`, the spectral degree-sum bound alone permits up to five
   additional induced edges beyond the mandatory 6-regular graph.
   Exact outside-neighbor integer moments improve this to at most three,
   but do not eliminate zero through three edges.  All nine simple graph
   topologies with at most three edges and their exact surviving outside
   degree-multiset counts are preserved in `residual-certificates.json`.

No SAT, ILP, catalog, automorphism-restricted search, or external solver was
run.  The two residual certificates are finite reductions only.  They are
not existence certificates, nonexistence certificates, or evidence about
novelty.
