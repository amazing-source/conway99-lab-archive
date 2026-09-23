# Wave 37 finite-polar adversarial audit

Verdict: **PASS for the scoped conditional restrictions**.

The ternary code consequences, signed degenerate-triple counts, and both
characteristic-seven rank-eleven association schemes were independently
reconstructed. They add exact necessary structure but do not exclude the
endpoint or improve `n3<=4158`.

## Ternary code consequences

From a symmetric factorization over `F_3`,

```text
C=V H V^T,
```

with `V` full column rank and `H` nondegenerate, the endpoint identities
`C^2=0` and `C1=0` give

```text
V^T V=0,   V^T 1=0.
```

The first follows by multiplying
`V H (V^T V) H V^T=0` by a left inverse of `V` and its transpose. The second
uses injectivity of `VH`.

Together with the previously verified nonzero, pairwise nonproportional
factor rows, this yields a projective self-orthogonal ternary `[231,r3]` code
whose dual distance is at least three. For every codeword, self-orthogonality
and orthogonality to `1` imply that the counts of symbols one and two are each
divisible by three.

The 231 distinguished row words and their negatives are distinct, have
weight 69, and have compositions `(36,33)` and `(33,36)`. Hence
`A_69>=462`. At `r3=12`, the independently checked Schur-square ceilings are

```text
rank_F3(I+B) <= 78,
rank_F3(J-I-B) <= 79.
```

The submitted real MacWilliams distribution was also regenerated. It has
nonnegative transforms and `B_j>=A_j`, but every transform from order 3
through 231 is nonintegral. It is not a formal weight enumerator and not a
code.

## Refuted collinearity inference and corrected count

The verifier retained the discovery package's veto. A singular Gram matrix
does not imply linear dependence in a nondegenerate ambient space. An explicit
counterexample over `F_3` uses ambient diagonal form

```text
diag(1,1,1,1,2)
```

and the three vectors

```text
(0,0,0,0,1)
(0,1,1,1,1)
(1,0,1,2,1).
```

Their vector rank is three while their Gram matrix is the all-two `3 x 3`
matrix, of rank one.

The corrected exact argument passes:

```text
support edges                         = 7,854
balanced triangles - unbalanced       = 34,034
maximum selected collinear triples    = 2,618
minimum independent balanced triples  = 31,416
```

A rank-one three-space has a two-dimensional radical. Its norm-two
projective points form the nine-point affine plane over `F_3`, with 12
collinear triples and 72 independent triples. Therefore at least

```text
ceil(31,416/72)=437
```

distinct rank-one degenerate three-spaces are required.

## Characteristic seven

Entrywise on the endpoint alphabet,

```text
C^(o3)=4(I+C) mod 7.
```

Since `C^2=0`, `I+C` is invertible. The Gram matrix of the 231 pure cubes is
therefore nonsingular, so the factor rows are nonzero and projectively
distinct.

The verifier rebuilt the complete five-relation projective pair algebra by
finite-field dynamic programming. At rank eleven:

| determinant | vertices | orthogonality degree | largest nonprincipal eigenvalue |
|:---|---:|---:|:---|
| square | 141,229,221 | 20,178,004 | `2401(1+sqrt(2))` |
| nonsquare | 141,246,028 | 20,175,603 | `4802` |

Both orthogonality graphs have three nonorthogonal pair types with differing
common-neighbor counts, so neither is strongly regular. Both spectral values
are already greater than the required selected degree 162; neither class is
excluded.

The independent suite passed six tests in 0.278 seconds.

Final scoped status:

```text
conditional ternary/code restrictions: VERIFIED
signed degenerate-space floor 437:      VERIFIED
rank-11 F7 determinant classes:         BOTH SURVIVE
new modular rank floor:                 NONE
n3=4158 endpoint:                       UNKNOWN
upper bound on n3:                      4158
Conway-99:                              UNKNOWN
```
