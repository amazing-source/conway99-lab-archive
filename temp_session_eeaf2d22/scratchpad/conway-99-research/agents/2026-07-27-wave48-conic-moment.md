# Wave 48 proof-agent report: combined conic moments

Role: proof B
Status: exact facial identities `DERIVED`; SDP feasibility `UNKNOWN`

I combined all currently available order-seven count and moment constraints
into one normalized real SDP. Clarabel and SCS both returned points extremely
close to the boundary but disagreed by several orders of magnitude, and each
point retained a small negative probability or eigenvalue. No numerical
status is promoted.

The durable result is exact facial structure. The Wave 44 affine system has
rank 93 and nullity 116. All eleven moment families have universal kernels;
their integer bases were proved exactly against the 170 equations and their
dimensions were closed by ranks modulo three primes. This explains why the
unreduced common-eigenvalue margin was pinned near zero.

After exact facial reduction, Clarabel still returned `optimal_inaccurate`
with negative residual-scale quantities. Bounded margin-zero/log-det runs
timed out and were terminated. There is no exact feasible vector and no exact
infeasibility witness. Endpoint status remains `UNKNOWN`.

The recommended next same-order lane is five pointwise-labelled roots plus
one free vertex. It needs only orders six and seven. There are 21 canonical
root types representing 683 labelled masks; matrices range from 10 to 32,
and the coefficient workload is tractable. Root relabelling can be justified
by explicit permutation congruence of pointwise-labelled matrices, without
assuming an automorphism of the unknown target graph.
