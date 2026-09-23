# Wave 38 retained failed routes and boundary

All statuses are conditional on `n3=4158`, equivalently `P=0`. None changes
the current upper bound.

## Monolithic all-prism OPB

A direct exact schema exists: enumerate an unordered pair of potential
triangles, enumerate its six perfect matchings, and block the nine required
positive edges after evaluating the fixed rooted scaffold.

This is computationally unacceptable as a materialized formula. The
residual-only subfamily has exactly `24,388,892,640` labelled clauses. The
coarse upper bound over all `96,215` potential triangles is
`27,771,690,030`. Deduplicating branch-simplified clauses would itself demand
an infeasible catalog.

The exporter is retained as a guarded streaming specification because it
gives a simple completeness reference for the lazy oracle. It was not run.

## Pairing only the six branch-fixed triangles

Wave 36's `282,774` active clauses per parent are sound but partial. They
forbid only prisms whose one side is among six triangles through coordinate
2 fixed by the parent branch. They cannot certify a graph with no prism
elsewhere and are not used as a completeness claim here.

## Treating endpoint units as the whole endpoint

The 84 negative units are exactly reproduced as the prism clauses having a
fixed root triangle on one side. They are necessary but do not forbid prisms
whose two triangles avoid the root. Treating these units as sufficient would
repeat the prior scope error.

## One-shot candidate checking

Finding prisms in one SAT candidate and adding their cuts does not complete a
case. A new satisfying assignment may contain different prisms. The cuts must
be accumulated and solving repeated until a checked zero-prism witness or a
checked UNSAT proof appears.

## Dropping induced-nonedge literals without the SRG base

The prism clauses mention only nine required positive edges. This compression
is sound because the complete base model enforces the adjacent-pair
common-neighbor parameter `lambda=1`; any extra cross edge would violate that
condition. The clauses must not be transplanted into an arbitrary graph model
that lacks this invariant.

## Solver run deliberately omitted

The host had very little free physical memory and unrelated long-running
searches were active. No memory-heavy target formula generation or solve was
started. Formula shape, exact counts, witness enumeration, cumulative cut
handling, tamper rejection, and a small fixture were tested instead.

## Current boundary

The package is construction infrastructure. It has:

- no target OPB artifact;
- no target solver result;
- no complete cut iteration;
- no graph witness;
- no UNSAT proof; and
- no independent verifier result yet.

Therefore all 33 refined cases, `n3=4158`, Conway-99, and the possibility of
improving the general upper bound remain `UNKNOWN`.
