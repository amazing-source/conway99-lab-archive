# Wave 96 retained null routes

## Fixed-C4 type partition

The exact `51,20,20,4` outside partition leaves
`6,148,477,125,000` norm-16 type selections before graph compatibility.
It is a domain reduction, not an extension cap.

## Projector and spherical distance

After fixing the alternating four coordinates, the norm-16 residual sphere
has dimension 40 and squared radius `52/5`.  An 80-point cross-polytope has
minimum squared distance `104/5>14`.  Therefore dimension, projected norm,
and the lattice minimum alone cannot imply at most 25 extensions.

This positive control is not an integral lattice or graph configuration.

## Generic shell bounds

The existing exact degree-four harmonic/spherical control is approximately
`2.46e8` short vectors, far above the needed weighted scale.  Ordinary
orthogonal-array moments likewise have enormous slack.  Neither captures
fixed coordinate incidences.

## Harmonic and Jacobi theta

The degree-eight C4 polynomial and the aggregate four-variable marked theta
series retain the missing coordinate data.  Their nonconstant harmonic
coefficients are signed, and the required rational-characteristic Jacobi
transformation/coset representation has not been frozen.  No LP certificate
is claimed.

## Live targets

- rank 28 endpoint: at most 25 antipodal norm-16/norm-18 extensions per C4;
- rank 30 endpoint: at most 24 antipodal extensions through norm 20 per C4;
- preferably, a direct aggregate Jacobi or flag-SDP incidence upper bound.
