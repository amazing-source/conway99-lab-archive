# Wave141: bivariate graph-code enumerator

Claim label: `DERIVED` for the exact identities and equality-space dimension;
`UNKNOWN` for formal feasibility, realizability, Conway-99, and novelty.

For a hypothetical adjacency matrix \(A\), define

```text
B[i,j] = #{x in F_2^99 : wt(x)=i and wt(Ax)=j}.
```

This retains the input weight that the ordinary image enumerator forgets,
while using only 5,000 output-even states rather than the 29,903 invariant
coordinates of the fully refined four-variable complete enumerator.

## Exact structure

The exact marginals and symmetries are

```text
sum_j B[i,j] = binom(99,i),
sum_i B[i,j] = 2^45 A_j,
B[i,j] = 0 for odd j,
B[i,j] = B[99-i,j].
```

Here \(A_j\) is the weight enumerator of `im(A)`.  The last identity follows
from `A*1=0`.

Writing \(K_t(w)\) for the binary Krawtchouk polynomial, the exact bivariate
MacWilliams equation is

```text
B[i,j] = 2^-99 sum_(a,b) K_i(b) K_j(a) B[a,b].
```

The checker unit-tests the index convention on the adjacency matrix of
`K3`, which is symmetric, even-rowed, and idempotent over `F2`.

Output parity and this transform generate a dihedral group `D8`, not the
`S3` that occurred in the coarser three-class GF(4) enumerator.  Exact
Burnside traces give

```text
10,000 raw bivariate states
 5,000 output-even states
 1,275-dimensional common invariant space
 3,725 independent equality rank
```

Input complementation reduces the working variables to 2,500; the remaining
transform rank is 1,225.

## Exact n3 objective

On the even code `R=im(A)`, let

```text
q(y) = wt(y)/2 mod 2.
```

Its polarization is the binary inner product.  Every adjacency row has
`q(row_i)=14/2=1 mod 2`, and
`row_i dot row_j=A_ij`.  Therefore

```text
q(A 1_S) = |S| + e(G[S]) mod 2.
```

For six-sets, the signed output shell depends only on the parity of the
induced edge count.  Replaying the frozen Wave21 source-to-canonical
alignment and all 62 affine six-vertex count formulas gives

```text
sum_(j even) (-1)^(j/2) B[6,j]
    = 2024484 + (512/3)n3.
```

The same replay yields the direct signed rows

```text
S0 =          1
S1 =        -99
S2 =       3465
S3 =     -56595
S4 =     462924
S5 =   -1821204
S6 =    2024484 + (512/3)n3.
```

This is stronger and safer than assigning individual full compositions to
the 62 induced graph classes: full output weight can depend on embedding
data not present in the induced isomorphism class, whereas its sign does
not.

Nonnegativity of the sixth row alone gives only `n3<=6,553,737` after the
known multiple-of-three condition, much weaker than 4,158.  A useful new
bound must come from the transform, marginals, Arf/Krawtchouk rows, and
nonnegativity together.

## Numerical status

`numeric_scout.py` tested both Arf signs in 2,500 conditional coordinates
`p[i,j]=B[i,j]/binom(99,i)`, with exact low rows, signed rows through degree
five, ordinary image/kernel constraints, all approved shadow inequalities,
and row-generated bivariate transform equations.

The first 50 transform rows solve but leave enormous inactive normalized
residuals.  Adding the 30 most violated rows makes HiGHS return an unknown
floating status for both signs.  The earlier orthonormal-coordinate smoke
also returned a numerical solve error.  These outcomes are
`UNKNOWN_NUMERICAL`: they are neither infeasibility evidence nor feasible
points for the full transform.

## Reproduce

```powershell
python -B attempts\wave141-bivariate-graph-code\exact_check.py --verify

python -B -m unittest discover `
  -s attempts\wave141-bivariate-graph-code -p "test_*.py" -v
```

The exact checker uses only Python's standard library.  Numerical scout
statuses, when present, are telemetry only; an exact rational primal or
Farkas dual is required for an evidentiary optimization claim.
