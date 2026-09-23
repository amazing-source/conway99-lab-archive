# Wave 169 clean-room audit

## Verdict

The arithmetic and local-relaxation null result are
`VERIFIED_WITH_SCOPE`. No failure-hypergraph or global certificate is
verified.

## 1. Completion and thresholds

For a pure marked five-cycle, `mu=2` forces each side's second candidate.
One side already determines at most one possible completion vertex, so a mark
has zero or one completion. Its five cycle vertices plus the three forced
outside vertices form an order-eight success event.

Every Wagner contributes exactly eight successful marks. Therefore

```text
F=166320-8*W8.
```

Exact arithmetic gives

```text
W8>=18710
iff 8*W8>=149680
iff F<=16640.
```

Because `F` is divisible by eight,

```text
F<=16640 iff F<16648.
```

The mandatory baseline is `4*4158=16632`, so for
`E=F-16632`,

```text
F<=16640 iff E<=8.
```

Thus the target permits only `E=0` or `E=8`.

Verdict: `VERIFIED`.

## 2. Mandatory and conditional failures

The exact local model has 18 core cross edges represented in both lanes,
giving 36 core marks, and four fringe edges represented in one lane each.
All four fringe marks necessarily fail through an impure forced support.

Extra core failures inherited from a fringe incidence are conditional. If
two same-side fringe apexes share their ordinary endpoint, that endpoint has
no core edge; if the endpoints are distinct, inherited core failures can
occur. Therefore the local theorem is

```text
f(uv)>=4,
```

not a universal count of extra core failures.

Verdict: `VERIFIED`.

## 3. Integral mismatch energy

For integral one-hot labels,

```text
(1/2)*||e_i-e_j||^2
 = 1-<e_i,e_j>,
```

which is zero for agreement and one for mismatch. This exactly counts
candidate mismatches after all invalid states and induced-pattern checks are
encoded without accidental label collisions.

It is only bookkeeping. Arbitrary unit vectors yield fractional energy, a
PSD relaxation need not be integral, and marginal label counts do not enforce
left/right pairing, purity, support, or cross-lane coupling.

Verdict: `VERIFIED_WITH_SCOPE`.

## 4. Five-failure local null model

A root neighborhood in the target must be `7K2`. The audited abstract gadget
uses two root-triangle edges and five further disjoint neighbor pairs. For
five selected core marks it assigns:

```text
CN(p,rho_i)   = {u,alpha_i},
CN(p,sigma_i) = {v,beta_i},
alpha_i != beta_i.
```

The forced left and right candidates disagree for all five marks. Fresh
outside witnesses can locally saturate the required nonedge common-neighbor
counts without forcing a prism inside the displayed gadget. The middle
vertex has degree exactly 14.

A compatible 22-edge cross-shell has four fringe and 18 core edges with all
required cross degrees. Five sufficiently separated optional core marks
support the mismatch slots.

This construction checks the explicitly encoded root degrees, neighborhood
matching, pairwise common-neighbor allotments, and root-visible prism
exclusions. It does not check:

- degree completion for every fresh vertex within 99 vertices;
- all cross-gadget `lambda/mu` equations;
- every remaining unique triangle apex;
- global prism-freeness;
- forced witness identifications;
- the full spectrum; or
- incidence-code and minor constraints.

It is therefore a relaxation countermodel, not an SRG candidate.

Verdict: `VERIFIED_WITH_SCOPE`.

## 5. Consequence

Any incompatibility graph whose edges are consequences only of the audited
pairwise/root-local clauses admits five mutually compatible failure vertices.
It cannot have independence number at most four, so a Hoffman or clique-cover
certificate in that graph cannot prove the pointwise target.

The next obstruction must use higher-order or global extension compatibility.
A failure hypergraph, lifted exact moment matrix, or complete coupled
root-3/root-12 dual remains a valid direction. Since endpoint exclusion needs
only `E<=8`, a global averaged certificate may be weaker than pointwise
four-failure equality.

No endpoint exclusion or strict `n3` improvement is promoted.
