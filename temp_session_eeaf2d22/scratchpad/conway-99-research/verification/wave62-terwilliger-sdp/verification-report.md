# Wave 62 independent verification report

## Verdict

The scoped finite claims are **VERIFIED**, with one non-mathematical
documentation correction.

The verifier rebuilt the label space and algebra from definitions. It did
not import or call `attempts/wave62-terwilliger-sdp/exact_check.py`.

## Independent reconstruction

The 84 labels are signed two-subsets of seven supports. Pair classification
produces the diagonal plus five off-diagonal relations with valencies

```text
1, 2, 1, 20, 20, 40.
```

Direct triple counting proves a homogeneous commutative association scheme.
The independently serialized intersection tensor has SHA-256

```text
44574bd2abfb7a909c85b2f52aacd72e9e73c84981d9d48da112a481e299b2ff.
```

Character multiplication, row orthogonality, idempotence, mutual
orthogonality, and completeness all hold exactly for multiplicities

```text
1, 6, 7, 14, 21, 35.
```

The independent 14-by-84 root-incidence matrix has row degree 12 and column
degree 2. Its root-side Gram eigenvalues are `24^1,10^6,12^7`. The SRG block
identity fixes residual adjacency eigenvalues `12,-2,0` on their images. On
the 70-dimensional incidence kernel the polynomial is
`t^2+t-12=(t-3)(t+4)`; dimension and trace give multiplicities 40 and 30.
Thus the residual spectrum used by discovery is independently recovered.

After the prism-forbidden first orbital is set to zero, imposing the forced
average blocks `12,-2,0` uniquely gives densities

```text
0, h, 1/10, (1-h)/10, 1/5+h/40,
```

where `h=y/42`. The unordered edge counts are therefore

```text
0, y, 84, 84-2y, 336+y,   0<=y<=42.
```

Projector entries and all six averaged blocks were recomputed from the
primitive idempotents. Every integer `y=0,...,42` survives. Because every
block is affine in `y`, exact nonnegativity at `y=0,42` also proves
feasibility for the whole real interval.

## Degree-24 Schur audit

For each implemented triple, the verifier recomputed the group average of

```text
E_s o P3^(o a) o P-4^(o b)
```

from the edge and nonedge entry values. No graph symmetry was used. The
exact census matches discovery:

```text
implemented matrices:       1,949
endpoint block inequalities: 23,388
positive:                    23,316
zero:                        72
negative:                    0
```

The reported smallest positive rational and its location also match exactly.

## Correction

The protocol and derivation describe all six multipliers and all
`a,b>=0`, `a+b<=24`. Literally that family contains 1,950 matrices. The code
skips only `(s,a,b)=(0,0,0)`, the unpowered principal idempotent `E_0=J/84`.
The published count 1,949 is correct for the implementation, but the prose
should disclose this omission. Including it adds 12 nonnegative endpoint
blocks and does not alter the null result.

## Hostile checks

The verifier rejects a changed orbital, a changed character entry, a
perturbed endpoint density, a changed manifest digest, and a changed frozen
result. It also checks discovery-manifest coverage: ten listed files, no hash
mismatch, no unlisted file, and no missing listed file.

## Boundary

This proves only that the declared one-point averaged relaxation and bounded
Schur family do not exclude the endpoint. It does not construct a residual
graph or a 99-vertex SRG. It does not prove existence, nonexistence, novelty,
or a strict upper bound. Endpoint `n3=4158` and Conway-99 remain `UNKNOWN`.
