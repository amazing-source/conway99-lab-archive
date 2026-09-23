# Wave56 bootstrap-percolation/closure protocol

Role: `proof_b`.

Baseline commit: `a4a61658356253fb95cf68252c972a4f79df38fe`.

## Frozen scope

Work conditionally with a hypothetical `srg(99,14,1,2)`.  Determine, without
assuming any graph automorphism:

1. the exact closure alternatives for a two-vertex nonedge seed;
2. the relation among induced `N3` copies, induced triangular prisms, induced
   `K3 square K3` copies, percolating nonedges, and nonpercolating nonedges;
3. the forced first three synchronous 2-bootstrap waves from an arbitrary
   nonedge;
4. every labeled relation among the four edge-triangle mates allowed by the
   local `lambda=1`, `mu=2` caps;
5. every exact multiplicity profile for vertices outside the forced
   eight-vertex seed neighborhood that see at least two of those vertices;
6. any exact global count or smaller CSP/inequality that follows.

No equality between different global counts may be asserted unless its
incidence multiplicities are proved.  A finite local profile census is not a
completed graph and cannot exclude the endpoint by itself.

## Source boundary

The primary cited source is Ibrahim, LaFayette, and McCall, *Australasian
Journal of Combinatorics* 93(1) (2025), 60--89:

- Lemma 4.9, printed page 74, classifies a 2-bootstrap closure in a strongly
  regular graph;
- Theorem 4.19, printed page 84, states the Conway-parameter percolation and
  `K3 square K3` consequences.

Every target-specific parameter, multiplicity, local relation, and count will
be rederived in the package.  The source is used for the general closure
lemma and literature attribution, not as a substitute for project arithmetic.

## Exact computational contract

- Enumerate all `2^6=64` labeled graphs on the four tips.
- Check every one of the 28 pairs in the forced eight-vertex graph directly.
- Detect induced triangular prisms by complete six-subset enumeration.
- For each admissible tip graph, enumerate every outside neighborhood mask on
  the eight vertices with at least two neighbors.
- Solve the exact pair-deficit multicover over nonnegative integers and retain
  every labeled solution, with no orbit quotient used as evidence.
- A formal dihedral grouping may be reported only after the full labeled list
  is retained.
- Abort if free physical memory is below 15 percent.

## Status wall

All new mathematical output is `DERIVED` or `UNKNOWN`, pending an independent
verifier.  Discovery must not promote itself to `VERIFIED`.
