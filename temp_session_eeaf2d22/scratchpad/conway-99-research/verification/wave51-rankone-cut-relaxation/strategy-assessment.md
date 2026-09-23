# Wave 51 alternative exact-certificate strategy assessment

## Verdict

The best next exact lane is a rational cutting-plane/facial-dual loop, not an
immediate full-graph SAT run or a covering ansatz.

The Wave51 probe shows why: a balanced 174-cut rank-one relaxation is exactly
feasible over the rationals. Therefore those already available directions
cannot be rearranged into a Farkas contradiction. The useful next falsifiable
step is to add rational directions chosen by separation against the current
exact witness, re-solve exactly, and demand either an exact rational witness or
an exact Farkas dual at every finite stage.

## Ranked routes

### 1. Facial-reduced SDP dual / exact rational cutting plane

Priority: **highest**.

Wave48 has exact facial reductions, so its structural kernels no longer need
to be guessed numerically. Wave51 demonstrates an exact finite workflow:
integer rank-one inequalities, rational active-set reconstruction, exact
substitution, and a certificate-sized output. The current 174-cut bundle is
feasible, but it exposes 66 tight directions and a sparse active system that
can seed exact separation.

Next bounded target:

1. start from the Wave51 rational witness;
2. evaluate every verified Wave45/Wave47/Wave49 matrix exactly;
3. add one primitive integer negative direction for the most violated matrix;
4. solve the enlarged rational LP;
5. stop only at an exact rational feasible witness or exact Farkas
   contradiction.

If the full spectrahedral system is weakly infeasible, an ordinary linear SDP
dual may fail to certify it; facial reduction and stronger algebraic
certificates are then relevant. This distinction is documented in
[Klep--Schweighofer](https://arxiv.org/abs/1108.5930) and
[Naldi--Sinn](https://arxiv.org/abs/1810.11792). Recent rational-certificate
work also illustrates that numerical low-rank structure can sometimes be
rounded into exact SDP nonexistence certificates
([Anglès Munné--Huber](https://arxiv.org/abs/2603.19901)).

### 2. Proof-producing SAT / pseudo-Boolean ILP

Priority: **global but expensive**.

A full 99-vertex encoding is finite and can in principle settle the existence
question. It begins with 4,851 edge variables before common-neighbor,
cardinality, prism, and symmetry-breaking auxiliaries. Existing project runs
show that restricted shards are tractable, but no complete-domain proof exists.

This route is publication-grade only when the exact unrestricted mapping and
raw proof are independently replayed. VeriPB explicitly supports checking
satisfiability, unsatisfiability, optimization bounds, and complete enumeration
certificates ([official VeriPB documentation](https://gitlab.com/MIAOresearch/software/VeriPB/-/blob/HEAD/README.md));
for CNF, CaDiCaL can emit a proof trace
([official CaDiCaL repository](https://github.com/arminbiere/cadical)).

Best use now: encode a genuinely complete local-overlap shard discovered by
the rational cutting plane, rather than restart the unrestricted adjacency
CNF without a decomposition certificate.

### 3. Coherent configurations / intersection-number ILP

Priority: **promising only without hidden homogeneity**.

The attraction is clear: replace vertex-labelled adjacency variables by
intersection numbers among a finite collection of rooted colors, then solve an
integer feasibility problem with a checkable certificate. Coherent
configurations generalize association schemes and encode adjacency algebras
([background](https://arxiv.org/abs/1910.01065)).

The current obstacle is logical, not computational: the endpoint does not
force vertex transitivity or a preselected coherent configuration. A fixed
fiber/color ansatz would be conditional. A safe version must take the full
coherent closure of explicitly forced rooted relations or exhaust every
resulting color refinement.

Small next target: run exact two-dimensional Weisfeiler--Leman refinement on
one forced local incidence structure and record whether it closes to a bounded
intersection-number system without assuming automorphisms.

### 4. Graph coverings and interlacing

Priority: **lowest for nonexistence**.

The SRG parameters already force adjacency spectrum
`14^1, 3^54, (-4)^44`; ordinary interlacing is therefore largely spent.
Cover/lift methods are strongest when a quotient or voltage structure is
forced. None is currently forced at the endpoint, and selecting one would
again be conditional. The main covering/interlacing literature is
construction-oriented—for example, Ramanujan coverings establish covers with
controlled new eigenvalues ([Hall--Puder--Sawin](https://arxiv.org/abs/1506.02335))—rather
than a direct nonexistence mechanism for this parameter set.

Revisit only if the coherent-closure lane forces a small quotient.

## Status wall

The Wave51 witness proves only exact feasibility of one real rational finite
relaxation. It is not integral and does not realize a graph. Full PSD
feasibility, full integer feasibility, endpoint `n3=4158`, a strict upper
bound, Conway-99, and novelty remain `UNKNOWN` or `NOT_PROVED`.
