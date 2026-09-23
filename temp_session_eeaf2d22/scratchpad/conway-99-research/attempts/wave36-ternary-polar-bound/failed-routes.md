# Wave 36 ternary polar-bound limitations and failed routes

The finite orthogonal-graph argument sharpens the conditional endpoint
constraint

```text
rank_F3(M) >= 12.
```

It does not exclude the endpoint.

## Surviving cases

The spectral-mixing bound rejects both determinant classes in dimensions at
most eleven.  At dimension twelve it rejects the nonsquare determinant class
but leaves the square class:

```text
mixing upper bound = 4149/13 > 162.
```

All dimensions 13 through 44 also survive this particular density test.

## Signed inner-product refinement

Orienting the 231 projective points records 36 inner products equal to one,
32 equal to minus one, and 162 equal to zero around each point.  The resulting
integer signed matrix is

```text
L=3I-M,
spec(L)=3^187,(-18)^44.
```

Embedding `L` as a principal block of the signed finite orthogonal scheme
recovers valid interlacing and cross-Gram inequalities, but none improves the
rank-twelve floor.  This is retained as a possible higher-order route, not as
evidence against the surviving endpoint.

## Scope

The ambient polar graph is a counting device.  A surviving polar-graph case
is not an endpoint matrix, and an endpoint matrix is not a Conway graph until
all graph-incidence constraints are also realized.
