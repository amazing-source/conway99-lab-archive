# Wave 71 failed routes and surviving boundary

## Bare Brown invariant

Fixing the marked \(\mathbf Z/9\) class does not improve the Milgram parity
condition.  Its quadratic value is \(5/9\), but its normalized Gauss phase is
still \(+1\).  The required 7-primary determinant sign remains available for
each positive even \(q\).

## Treating the discriminant group as a genus

The group
\(\mathbf Z/9\oplus(\mathbf Z/7)^q\) does not specify a positive-definite
genus, and a genus would not specify the 99 marked vectors.  Wave 71 does not
claim genus existence or nonexistence from the group alone.

## Scalar theta series as a complete invariant

The level-7 neighbor makes scalar modular forms usable, but the congruence
modulo 7 is only necessary.  All eight rows survive their mandatory
\(q^1,\ldots,q^6\) zero coefficients.  No row is deleted by that gap alone.

## Floating Hermite and LP bounds

No floating sphere-packing estimate is used as proof.  The exact mod-7
calculation gives a much sharper special conclusion only for \(q=16\):
\(\min(\sqrt7L^*)\le18\).  It does not delete that row.

## Low-norm eigenvectors

For \(q=16\), modular reduction forces an integral \(-4\)-eigenvector of
squared coordinate norm 14, 16, or 18.  Exact support arguments reduce these
to tightly structured signed subgraphs, but none of the surviving structures
is excluded here:

- norm 14: the complement-of-Fano incidence graph on \(7+7\), with a forced
  external \(2\)-\((15,3,2)\) design;
- norm 16: a 4-regular bipartite graph on \(8+8\);
- norm 18: a \(9+9\) signed support with at most two same-sign edges per
  side, and matching restrictions when there are two.

The exact next target is to combine these finite structures with the rooted
transition/hypergraph constraints or with higher-degree theta data.

Conway-99 and novelty remain `UNKNOWN`.
