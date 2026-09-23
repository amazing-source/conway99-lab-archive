# Wave 60 disconnected-core incidence-design protocol

Frozen: 2026-07-27

Status policy: this is discovery work.  A constructed matrix is `CANDIDATE`
until an independent verifier replays it.  A solver status alone is not an
UNSAT certificate, and no result in this package changes the endpoint from
`UNKNOWN` without independent verification.

## Conditional scope

Assume the prism-free `n3=4158` endpoint and fix a triangle.  Let its
36-vertex neighbour core `X=X0 union X1 union X2` have three connected
components.  The independently verified Wave 36 component equations then
force every component to contain four vertices from each fibre and every
column of the `36 x 60` incidence matrix `B` to contain:

- two vertices from every fibre;
- two vertices from every connected component.

No automorphism of the target graph, the fixed triangle, its fibres, the
three components, or the sixty columns is assumed.

## Component classification

Enumerate every simple fibre-labelled component with four vertices per fibre
such that:

1. every fibre induces a perfect matching;
2. every pair of fibres is joined by a perfect matching;
3. the resulting 12-vertex graph is connected, cubic, and triangle-free;
4. adjacent pairs have no common component neighbour;
5. same-fibre nonedges have at most one common component neighbour;
6. cross-fibre nonedges have at most two common component neighbours.

The last two bounds are the exact local consequences of the SRG
common-neighbour equations; in particular they exclude `K3,3`.  Normalize
coordinates only, then quotient by all independent permutations inside the
three fixed fibres.  Fibre permutations are not used.

## Column and design enumeration

For every multiset of three classified component types:

1. build the labelled 36-vertex disjoint union `A_X`;
2. form the exact target

   `G = 12I - A_X + 2J - blockdiag(J12,J12,J12) - A_X^2`;

3. enumerate every distinct six-subset `b` with two vertices in each fibre
   and component;
4. require the pointwise mixed cut

   `d(b) = 2*1 - (I+A_X)b >= 0`;

5. discard a column containing a pair whose target entry in `G` is zero;
6. ask for sixty distinct candidate columns satisfying `BB^T=G`.

The selection problem is encoded with one Boolean variable per distinct
column and exact-cardinality constraints for the 630 off-diagonal Gram
entries.  The 36 diagonal equations and the total of sixty columns are
redundant: inside any one component, the target multiplicities of its local
pairs sum to sixty, every candidate contains exactly one such pair, and the
local pair degrees give the diagonal row sums.  The checker proves and tests
this reduction before solving.  A SAT model must be checked directly from the
emitted binary matrix.  An UNSAT label requires either a complete proof
checked by a separate proof checker or an independently replayable exhaustive
enumeration; otherwise it remains only a solver observation.

## Resource and publication rules

- Stop before physical free memory falls below 15 percent.
- Preserve the exact input hashes, commands, candidate matrix, CNF/proof
  artifacts when applicable, tests, and failed routes.
- Discovery does not verify itself.
- Do not edit other waves or repository checkpoint documents.
