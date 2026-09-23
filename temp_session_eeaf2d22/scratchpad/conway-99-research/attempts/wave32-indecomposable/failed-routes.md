# Wave 32 indecomposable branch: failed routes and exact boundary

## Diagonal commutants do not extend automatically

Wave 31 starts from a coordinate block of the projector and builds a
nonconstant diagonal sign commuting with `E`. An integrally indecomposable
lattice supplies no such block and no nonconstant diagonal commutant. A
rational invariant subspace, a discriminant subgroup, or an invariant
sublattice of the Schur endomorphism `B` is not a coordinate block and cannot
be substituted into that proof.

## Connectivity is a reduction, not an exclusion

Primitivity makes the 231 frame rows generate the endpoint lattice. Under
minimum four, integral orthogonal decomposability is therefore equivalent to
disconnection of the nonorthogonality graph of those rows. The Wave 31
`21|b` and `33|b` argument makes the actual projector support connected.
Consequently a surviving rootless endpoint is forced to be indecomposable.
Connectivity does not itself contradict a positive-definite lattice.

## The forbidden three-row motif is not yet forced

If three rows have pairwise inner products `-2,-2,-1`, their sum has norm
two. In the actual triangle classes, this says that an `r=2` pair cannot have
a common triangle that is `r=3` from both endpoints. Equivalently,

```text
tr(A_minus1 A_minus2^2)=0
```

is necessary for rootlessness.

At `n3=708`, the exact unordered pair counts are

```text
M=+1:  2546
M= 0: 22161
M=-1:   708
M=-2:  1150.
```

These one- and two-point counts do not determine the mixed triple trace.
No valid inequality forcing it positive was found. Treating the large
`M=-2` edge count as proof of a mixed triangle would be an invalid
failure-to-embed inference.

## Modulo two is consistent

The endpoint reduction gives a nondegenerate quadratic space over `F2`,
with all 231 row residues singular, and a symmetric rank-44 idempotent
projector with zero diagonal that kills the all-ones vector. The checker
constructs an exact 231-row, rank-44 finite-field model with all these
features. It is not a positive-definite lattice or target matrix, but it
proves that these mod-two statements alone do not contradict one another.

## Corrected modulo-three and modulo-seven inference

The first proof draft incorrectly inferred

```text
X^T X=21S^-1=0 mod p
```

from the integrality of `21S^-1`. That is false: an integral matrix written
as `21S^-1` need not be entrywise divisible by either prime.

The correct inherited statement is that primitivity gives
`rank_Fp(X)=44`, while, for `u=v_3(h)` and `v=v_7(h)`,

```text
rank_F3(X^T X)=rank_F3(G)=u,
rank_F7(X^T X)=rank_F7(G)=v,
rank_F3(M)=44-u,
rank_F7(M)=44-v.
```

The column codes therefore have restricted dot-product radicals of
dimensions `44-u` and `44-v`; they are self-orthogonal only in determinant
rows where the corresponding exponent is zero. The false universal-code
claim was removed before results were frozen. No checker result depended on
it, and the mod-two hostile control and forbidden motif are unchanged.

## Incomplete bare-lattice hostile-control search

An exploratory simultaneous two-neighbor search began from the verified
rootless bare lattice `T20 orthogonal_sum LAMBDA24`. Exact residue-coset
search found binary classes of minimum eight in both factors, which is
promising for a rootless gluing neighbor. The proof of integral
indecomposability and a complete reproducible certificate were not finished
before freeze. None of this exploratory output is evidence and no candidate
is claimed.

## Exact boundary

```text
actual projector support graph connected:               inherited Wave 31
surviving rootless endpoint necessarily indecomposable: DERIVED
{-2,-2,-1} row motif forbidden by rootlessness:          DERIVED
actual incidence forces that motif:                      UNKNOWN
rootless indecomposable endpoint:                        UNKNOWN
n3=708:                                                  UNKNOWN
Conway-99 and novelty:                                   UNKNOWN
```

## Retained harness correction

The first hostile test expected the determinant of the canonical forbidden
three-row Gram to be `28`. The checker computed the exact determinant `20`
and failed. Direct expansion confirms `20`; it is still positive, and the
sum vector still has norm two. The test and report were corrected before
freezing results. No theorem or status changed.

The first manifest command was launched from the attempt directory while
still prefixing the manifest path by that directory. PowerShell reported the
missing doubled path, but continued to later tests. That invocation is not a
manifest check. The corrected repository-root invocation below is the
operative gate.

A later replay invoked `python -m unittest test_exact_check.py` from the
repository root, where that module is not importable by its bare name. It
failed before loading a test. The corrected attempt-directory replay is the
operative ten-test result.
