# Portfolio nulls

- **Wave151 Q1 branch:** Z3 `unsat` in 40.46 seconds; no exported proof.
- **New disjoint Q1 branch:** Z3 `unsat` in 57.59 seconds; no exported proof.
  Gluecard4 was interrupted after 180.03 seconds with status unknown.
- **Unfixed joint native-cardinality model:** Gluecard4 interrupted after
  67.66 seconds, no candidate.
- **Unfixed joint MILP:** HiGHS reached 300.68 seconds with no incumbent.
- **Proof-producing CNF attempt:** sequential-counter CNF plus CaDiCaL195 did
  not finish within 180 seconds and exported no proof.

All statuses are `UNKNOWN` for their intended negative use. The two fixed-Q1
branches do not exhaust the Q1 universe, and no bare solver status is a
certificate.
