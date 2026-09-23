# Independent audit

The protocol was frozen at SHA-256
`18316e2d36e981a64f369d852c132c905d695a521388763c24f2362b741668a3`
before any Wave 44 discovery file was opened.

## Exact reconstruction

The verifier rebuilt all 1,044 unlabeled seven-vertex graphs from the full
`2^21` labelled universe, filtered the 208 locally admissible classes, and
matched the already verified Wave 43 class stream. It independently rebuilt:

- all 62 deletion rows and 19 affine Hamiltonian rows;
- seven vertex-degree root rows;
- 36 ordered adjacent-pair signatures using category sizes `(1,12,12,72)`;
- 46 ordered nonadjacent-pair signatures using `(2,12,12,71)`.

Every rooted column partitions correctly: seven vertex roots and 42 ordered
pair roots. Right-side totals match the corresponding direct choices from
the SRG category sizes. No graph automorphism or witness-dependent row
selection is used.

The 91-support witness is canonical, duplicate-free, positive integral, has
`y=4158`, and satisfies every row with residual exactly zero. Six hostile
mutations - support, `y`, each rooted family, and a right side - are all
rejected.

## Post-freeze discovery comparison

The frozen protocol required complete normalized streams, not merely matching
dimensions or ranks. After the freeze, the verifier strictly parsed
`attempts/wave44-rooted-flags/row-system.json` at SHA-256
`fb81601a9c97fc6860702403e56da65c2ba8fd69ee6a61007a0da53cade1d722`.
It imported no discovery module.

The published class order equals the independently generated 208-class order.
All four family objects agree in exact row order:

```text
81 base rows       x 209 coefficients
 7 vertex rows     x 209 coefficients
36 edge rows       x 209 coefficients
46 nonedge rows    x 209 coefficients
170 right sides
```

Thus 35,530 coefficients and 170 right sides were compared and matched. The
artifact's per-family and combined canonical hashes recompute correctly and
also equal independently computed commitments. An earlier provisional
verifier digest used `[numeric_rows,rhs]`; discovery uses
`{"rows":numeric_rows,"rhs":rhs}`. This was an encoding difference only. The
retained internal digest is
`319d4586c21faa218c577cfed9eb9565fb3b7bae8697ff773e3e1b482305a2c4`;
the shared canonical combined digest is
`863a75a616c138e750178c93234a92289363318f4bd0775c7b0792e44b7c61cb`.

## Numerical solver audit

HiGHS reports status 2 (`infeasible`) for both the unscaled and row-scaled
free MILP. This cannot be mathematical infeasibility:

- the exact integer residual is zero;
- the binary64 matrix-vector residual is also exactly zero;
- the same HiGHS model with all variable bounds fixed to the witness returns
  status 0 (`optimal`) with and without presolve.

The nonzero right sides range from `4,158` to `108,273,563,244`. The
inconsistent free-search status is numerical/MIP behavior, not an exact
Farkas or branch certificate. It is explicitly rejected as evidence.

## Scope boundary

This proves feasibility only for the specified aggregate rooted relaxation.
It supplies no compatible overlapping-subset realization, graph, endpoint
evidence, strict upper bound, or Conway-99 solution.
