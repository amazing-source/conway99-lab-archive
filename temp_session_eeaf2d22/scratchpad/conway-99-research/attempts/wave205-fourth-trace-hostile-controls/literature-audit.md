# Primary-source fourth-moment and association-scheme audit

## Scope and evidence boundary

The audit asked whether a published theorem forces the nonedge values or the
full matrix

```text
h_xy=tr(P_x P_y P_x P_y)
```

from the frozen rank-11 endpoint data. Searches covered finite-field frames
and fusion frames, real/complex Grassmannian projector designs, trace
identities, and finite orthogonal/polar association schemes.

No directly applicable fourth-moment globalization theorem was located. This
is a bounded literature non-discovery, not evidence that no such theorem
exists.

## 1. Finite-field frames

Greaves, Iverson, Jasper, and Mixon develop rank-one frame theory over
arbitrary and finite fields in
[Frames over finite fields: Basic theory and equiangular lines in unitary geometry](https://arxiv.org/abs/2012.12977).
Their Proposition 3.5 assumes that the vectors form a frame, hence span the
ambient space, and proves that a frame is `c`-tight exactly when its Gramian
`G` satisfies

```text
G^2=cG.
```

For `c=0` this justifies the square-zero centered Gram identity in the frozen
endpoint and in the control, provided spanning is separately checked. The
paper explicitly warns in Remark 3.7 that the spanning hypothesis cannot be
removed.

Hypothesis gap: this is a vector-frame theorem. It does not say that the 99
rank-six star projectors form a finite-field `p=2` fusion design, and it does
not determine `tr(P_xP_yP_xP_y)`.

The companion orthogonal-geometry paper,
[Frames over finite fields: Equiangular lines in orthogonal geometry](https://arxiv.org/abs/2012.13642),
relates rank-one equiangular tight frames to modular strongly regular graphs.
Its objects are line representatives and their Gram/signature matrices, not
the rank-six projector fourth moments in Wave 205.

Result: `G^2=0` transfers; a fourth-moment or fusion-frame identity does not.

## 2. Tight fusion frames and Grassmannian cubatures

Bachoc and Ehler work on the real compact Grassmannian in
[Tight p-fusion frames](https://arxiv.org/abs/1201.1798). Their setup uses:

- real subspaces of `R^d`;
- Euclidean orthogonal projectors;
- positive real weights;
- the normalized `O(d)`-invariant Haar measure; and
- real positivity in the fusion-frame potential.

Theorem 5.3 characterizes tight `p`-fusion frames by exact integration on a
specified polynomial subspace. Definition 5.5 and Theorem 5.7 characterize a
strength-`2p` cubature by exact integration of all Grassmannian polynomials of
degree at most `2p`, equivalently by equality in a positive lower bound for
the `p`-fusion-frame potential. Remark 5.8 explicitly says that for `p>=2` a
strength-`2p` cubature is stronger than a tight `p`-fusion frame.

Hypothesis gap: `F_3` has no ordered positivity or normalized compact Haar
integral of this kind. More importantly, neither the centered zero-frame
identity nor `sum_x P_x=0` establishes any `p=2` cubature/design condition for
the 99 star spaces. Importing the theorem would require first proving exactly
the missing fourth-moment hypothesis.

Result: no transfer.

## 3. Projector designs and association schemes

Roy's
[Bounds for codes and designs in complex subspaces](https://arxiv.org/abs/0806.2317)
works on the complex Grassmannian `G(m,n)` with `U(n)`, analytic integration,
and positive trace inner product. Section 2 emphasizes that
`tr(P_aP_b)` alone does not determine the orbit of a pair of subspaces;
the complete principal-angle multiset does.

Theorem 10.5 obtains an association scheme only when a set is simultaneously
a `(2t-2)`-design, an `A`-code with exactly `t` inner-product values, and
satisfies specified annihilator-polynomial hypotheses. Corollary 10.2 likewise
requires a `2t`-design and an exact count of principal-angle classes.

Hypothesis gap: the 99 modular star spaces have not been proved to be a
complex or real Grassmannian design, a finite-field analog of that design, or
a full orbit with the required principal-angle relations. The pair trace
matrix and `sum P_x=0` do not supply these premises.

Result: no association-scheme closure follows.

## 4. Finite orthogonal and polar association schemes

Adriaensen and De Boeck prove in Theorem 4.18 of
[Association schemes and orthogonality graphs on anisotropic points of polar spaces](https://arxiv.org/abs/2402.05055)
that, for a nondegenerate elliptic or hyperbolic quadric in `PG(n,q)` with
`q` odd, explicitly defined relations on the full set of anisotropic points
form an association scheme. The relations depend on the type of the line
spanned by two points and on their quadratic types. For `q=3`, restriction to
one quadratic type yields a two-class scheme.

Hypothesis gap: the Wave 205 vertices are 99 six-dimensional nondegenerate
subspaces/projectors, not the full anisotropic point set of a quadric. No
transitivity, full-orbit hypothesis, or matching pair-orbital classification
has been proved. The theorem cannot be restricted to an arbitrary 99-subset
while retaining its intersection numbers.

Result: no transfer.

## 5. Trace identities

Grinberg's
[The trace Cayley-Hamilton theorem](https://arxiv.org/abs/2510.20689)
proves over a commutative ring that the characteristic coefficients of one
matrix satisfy

```text
k c_k + sum_{i=1}^k tr(A^i)c_{k-i}=0.
```

Hypothesis gap: this is an identity for powers of one matrix. It does not
express the mixed cyclic word `tr(ABAB)` in terms of `tr(AB)`. In
characteristic 3, the coefficient `k` also vanishes at `k=3`, so characteristic
zero Newton-identity divisions cannot be imported without a separate
argument.

The local exact projectors in this package directly demonstrate the relevant
independence:

```text
tr(PQ1)=tr(PQ2)=2,
tr(PQ1PQ1)=1,
tr(PQ2PQ2)=2.
```

Result: no trace-identity collapse of `h` to `g`.

## 6. Exact rank bounds

The applicable unconditional coordinate count is internal linear algebra:

```text
dim(self-adjoint End(F_3^11))=66
dim(trace-zero self-adjoint End(F_3^11))=65
dim Sym^2(F_3^65)=2145.
```

After quadratic lifting, `h(A,B)=tr(ABAB)` is a bilinear contraction on this
2145-dimensional space. Therefore `rank(H)<=99`, which is vacuous for a
`99 by 99` matrix.

The common shortcut `rank(H)<=55` from `dim(wedge^2 V)=55` is invalid:
`wedge^2(P_x)` is an endomorphism of the 55-space, so its unreduced operator
coordinate space has dimension 3025.

Result: no incompatible rank bound.

## 7. Current target status

The peer-reviewed 2025 paper
[On the automorphism group of a putative Conway 99-graph](https://doi.org/10.5802/alco.418)
states in its abstract and introduction that existence remains open.

The latest primary source located in this audit,
[Approaching the Conway-99 problem using SAT solvers](https://arxiv.org/abs/2604.23037),
was submitted 2026-04-24. It reports experimental SAT encodings and an
inability to search the problem in reasonable time, not a construction or a
nonexistence certificate.

Evidence cutoff: the search establishes an open status through the located
2026-04-24 source. It is not a proof that no later announcement exists.
Accordingly, this repository's status remains `UNKNOWN`.

## 8. Audit verdict

Every attractive published route located here has a missing hypothesis:

- finite-field frame theory reaches `D^2=0`, not projector fourth moments;
- real fusion-frame fourth moments require positivity and a proved
  `p=2` design/cubature condition;
- Grassmannian association schemes require design and angle-class premises;
- polar schemes use full geometric orbits of anisotropic points; and
- trace identities do not collapse the mixed word `ABAB`.

The newly named graph-specific bottleneck is not merely "find a fourth
moment." It is to prove that the actual 99 star spaces satisfy an endpoint
relation/design/module law strong enough to control the nonedge contraction
of the fourth-order trace tensor.
