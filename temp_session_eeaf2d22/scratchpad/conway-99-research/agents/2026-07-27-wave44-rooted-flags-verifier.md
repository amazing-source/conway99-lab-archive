# Wave 44 rooted aggregate verifier

Role: verifier  
Claim label: `VERIFIED_SCOPED_FEASIBILITY`  
Frozen commit: `e28f90464d00b98d37672b0b2b23dba15399a6f2`

Before opening discovery, the verifier derived and froze the 170-row system:
81 public unrooted rows, seven vertex-root rows, 36 ordered adjacent-root
rows, and 46 ordered nonadjacent-root rows, on 208 class counts plus
`y=h11/4`.

The clean-room implementation imports no Wave 44 helper. It independently
reconstructed the 208 canonical classes, all signatures and rows, and the
91-support witness. At `n3=y=4158`, every one of the 170 exact integer
residuals is zero. Modular ranks progress `81 -> 82 -> 87 -> 93` over three
primes, confirming that the rooted rows are strictly stronger than the
unrooted aggregate system while remaining feasible.

After the protocol freeze, strict parsing of the frozen discovery
`row-system.json` confirmed the identical ordered 208-class stream, all
35,530 coefficients, all 170 right sides, and all five canonical family or
combined hashes. No Wave 44 discovery module was imported. The combined
row/RHS commitment is
`863a75a616c138e750178c93234a92289363318f4bd0775c7b0792e44b7c61cb`.

HiGHS reports the free MILP as infeasible, but this is a verified false
negative: the exact witness has integer and binary64 residual zero, and the
same HiGHS model is optimal when bounds are fixed to that witness. Solver
status has no certificate authority.

Publication recommendation: publish only exact feasibility of this aggregate
rooted relaxation. It is not a graph, does not enforce consistency between
overlapping subsets, and is not endpoint evidence. Endpoint exclusion, a
strict upper bound, Conway-99, novelty, and priority remain `UNKNOWN`.
