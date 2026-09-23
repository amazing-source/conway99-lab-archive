# Wave 39 cross-base failed routes and exact boundary

## Universal local rank twelve is false

It was tempting to strengthen the Wave 38 bridge to

```text
rank_F3(P_T-I)>=12
```

for every simple tripartite four-regular quotient with two-regular
bipartite blocks.  The exact package contains rank-ten and rank-eleven
controls.  The rank-eleven control has nonsquare discriminant, so adding
the global rank-twelve determinant class does not rescue the claim.

These are quotient controls, not endpoint graphs.

## Five-space pigeonhole is not itself contradictory

At the surviving boundary, every vertex forces 84 norm-one projections
into a nonsquare five-space with only 72 norm-one vectors.  This yields at
least twelve support-four/six dependencies.

The exact positive control realizes the projection profile, all 84 distinct
isotropic rows, exactly twelve repeated projections, and all resulting
short dependencies in an eleven-dimensional nonsquare space.  Therefore
the determinant and projection equations alone do not exclude the
boundary.  A proof must use the full relation alphabet, the remaining 140
triangles, the square-zero frame, or compatibility across multiple stars.

## Projective counting would be weaker

The nonsquare five-space has only 36 projective norm-one points, but the
actual projected vectors are oriented.  Counting its 72 oriented norm-one
vectors is both valid and sharper: it forces exact equality `q_U=q_V`, not
merely proportionality.

## Nonadjacent-triangle projections remain unclosed

For a triangle `U` nonadjacent to `x`, let `t` be the number of star
triangles having two cross edges with `U`.  Direct counting gives

```text
t in {0,1,2,3},
number of nonzero d_i = 6-t,
(q_U,q_U)=-t mod 3.
```

The first moment over the 140 such triangles is compatible with many
distributions and did not force an additional anisotropic-vector overflow.
No second-moment classification was proved in this lane, so it is retained
as a continuation rather than a claim.

## Exact remaining target

The smallest exposed target is to classify relations

```text
z_U-z_V+sum_i(d_Ui-d_Vi)z_Ti=0
```

of support four and six under the full triangle-incidence geometry, then
count their required multiplicity across all 99 vertex stars.  The current
package proves they are unavoidable at `r3=12`; it does not prove their
global incompatibility.

```text
endpoint exclusion:       NOT OBTAINED
P>=1 / n3<=4155:          NOT PROVED
strongest general bound:  n3<=4158
target status:            UNKNOWN
```
