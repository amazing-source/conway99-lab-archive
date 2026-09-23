# Verifier failed-route ledger

- The numerical HiGHS infeasibility result for extending the one fixed block
  witness was not promoted.  It has no exact infeasibility certificate and
  concerns only one block witness.
- The 180-second MiniCard nonhit was not rerun as evidence and remains
  `UNKNOWN`.
- The explicit 140-block witness was not interpreted as a graph: it has
  neither transition choices nor the complete residual-codegree rows.
- The rational invariant point was used only to verify feasibility of the
  declared linear relaxation.  Its scaffold symmetry was not imposed on any
  target graph.
- The residual-codegree closure was not overstated as a full prism-free
  endpoint encoding.  It completes the `srg(99,14,1,2)` equations but does not
  separately forbid prisms away from the selected root.
