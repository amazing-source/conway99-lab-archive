# Wave 34 rootless global overlap: retained Stage 1 failed routes

These are clean-room failures. No Wave 34 discovery artifact was inspected,
and no failure-to-find statement is used as nonexistence evidence.

## 1. The holonomy permutation does not locally force the motif

The only forbidden moved-point count is `q=1`. For every

```text
q in {0,2,3,...,12},
```

the checker supplies a twelve-point permutation with exactly `q` moved
points and three pairwise edge-disjoint perfect matchings. Their restrictions
have no double edge, so the rootless local motif count is zero.

Dropped obligations:

- all `Z`-fibre incidences;
- all graph degrees and `lambda/mu` equations away from the base triangle;
- global consistency between the local systems of different centres;
- the rank-44 integral endpoint lift.

Conclusion: `q!=1` is exact, but no stronger local exclusion follows from the
permutation and three matchings alone.

## 2. The projector cap one does not force the unique closure

The exact Schur-complement calculation reduces an `R2` pair's common-`R3`
codegree from the four Wave 33 board selections to at most one. The fibre
normal form identifies its only possible fixed label. It does not force the
last `Z`-to-fibre edge needed to realize that triangle.

A local matching package attains the compatible-index cap one. Adding the
last edge would create the forbidden motif; omitting it leaves a local
rootless control. Neither choice is a graph extension certificate.

## 3. Local PSD is automatic for the three-matching normal form

For the fixed-point set `F`,

```text
3I-L_F=sum_delta (I-A_delta)[F].
```

This is a sum of three matching Laplacians and is positive semidefinite for
every choice of the matchings. Rootlessness merely deletes double edges;
it does not make this principal Gram indefinite.

Conclusion: this local projector principal minor cannot exclude the branch.

## 4. The global `R0` overlap lower bound has ample capacity

Actual incidence forces at least 6860 `R0`-centred `R3` wedges, while the
projector cap allows

```text
2546*5=12730.
```

The forced lower bound yields many occupied `R0` pairs and at least 3041
four-cycles in the `R3` graph, but neither number exceeds its current exact
capacity. No contradiction follows.

## 5. The cap-five equality case is rigid but not contradictory

An `R0` pair with five common `R3` neighbours has the singular Gram relation

```text
2x+2y+z1+z2+z3+z4+z5=0.
```

The seven triangles are pairwise disjoint within each side of the resulting
`K_{2,5}` overlap, and the labelled incidence transport makes the relation
pointwise consistent on their 21 vertices. Stage 1 found no exact reason that
such a sparse projector dependency is impossible globally.

It is not asserted that the equality case extends to a target.

## 6. Endpoint scalar sharpness is not global realizability

The profile

```text
226 centres with b=10,
  5 centres with b=8
```

has degree sum 2300 and attains the scalar lower bound 6860. It does not
specify a graph `H`, the other relations, compatible fibre systems, or a
target graph. It is retained only to show that the affine summation cannot
be sharpened without another premise.

## 7. No status promotion

The package contains no complete graph, no complete endpoint frame, and no
complete-domain exclusion certificate. Therefore:

```text
actual motif forcing:              UNKNOWN
rootless indecomposable endpoint:  UNKNOWN
n3=708:                            UNKNOWN
Conway-99:                         UNKNOWN
novelty:                           UNKNOWN
```
