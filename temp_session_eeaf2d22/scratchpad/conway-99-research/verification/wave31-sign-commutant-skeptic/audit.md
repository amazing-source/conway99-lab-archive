# Wave 31 sign-commutant skeptical audit

```yaml
role: verifier
date_utc: 2026-07-24T06:58:18Z
git_commit: a8b0c34040f6857b3c5ebcc44f108e03a4159088
claim_label: UNKNOWN
scope: >-
  Secondary skeptical audit of the frozen Wave 31 conditional exclusion of
  nontrivial rootless integral orthogonal decompositions of the rank-44
  target-incidence scaled-dual S-form. The audit may return
  PASS_NO_FATAL_GAP or VETO but does not itself promote the central claim.
inputs: verification/wave31-sign-commutant-skeptic/input-freeze.sha256
method: >-
  Independent exact reconstruction of the lattice-basis transport, row
  support, incidence eigenspace transport, spectral-projector commutator,
  adjacent-edge cancellation, signed double count, projector-block trace,
  lattice-block trace, and all proper block/complement cases, with small
  exact countermodels after named premises are removed.
command: >-
  python -B verification/wave31-sign-commutant-skeptic/skeptic_check.py
  --output verification/wave31-sign-commutant-skeptic/results.json
outputs:
  verification/wave31-sign-commutant-skeptic/skeptic_check.py: 3e99a11b6fc63f034b0ec93c142f02c2f3876bc27513dcce8c80eb67222dc81a
  verification/wave31-sign-commutant-skeptic/results.json: 0dd057b903da3092528f4e0bc2b9283e8ee6fa3222553b24b219dda732d35007
limitations:
  - This is a secondary hostile audit, not the designated publication verifier.
  - No target graph, endpoint frame, or lattice is constructed.
  - The result is conditional on actual target vertex-triangle incidence and a rootless integral orthogonal split.
  - Rooted and integrally indecomposable endpoint forms remain untreated.
  - n3=708, Conway-99 existence or nonexistence, and novelty remain UNKNOWN.
```

## Verdict

```text
PASS_NO_FATAL_GAP
```

No fatal hidden assumption, sign error, omitted summand, or decomposition edge
case was found in the frozen candidate at
`a8b0c34040f6857b3c5ebcc44f108e03a4159088`.

This verdict is deliberately narrower than `VERIFIED`: it is a second
skeptical check and does not edit or promote the discovery claim.  The
conditional conclusion checked here is:

```text
actual target incidence
+ rank-44 integral frame identities
+ min(S)>=4
+ nontrivial integral orthogonal decomposition of S
==> contradiction.
```

## 1. Integral basis change and row support

Let the original form and frame be `T,Y`, with

```text
Y^T Y=21T^(-1),
M=YTY^T.
```

If `P` is unimodular and `S=P^T T P` is block diagonal, the correct
contragredient frame is

```text
X=Y P^(-T).
```

Because `P^(-T)` is integral,

```text
X^T X
 =P^(-1)Y^T YP^(-T)
 =21(P^TTP)^(-1)
 =21S^(-1),

XSX^T=YTY^T=M.
```

Thus the candidate may work in an integral block basis without changing
`M=21E`.  The submitted report does not spell out this transformation, but
the transformation is valid and was also documented upstream.  The exact
checker includes a nontrivial two-dimensional unimodular example and verifies
both identities over the rationals.

For a row `x_i=(x_i1,...,x_im)`, orthogonality gives

```text
4=x_i^T S x_i=sum_j x_ij^T S_j x_ij.
```

Every nonzero block component is a nonzero integral vector of `S` and hence
has norm at least four.  Exactly one component is therefore nonzero.  The
word "even" in the submitted support sentence is harmless but unnecessary;
minimum four alone proves the assertion.

Every positive-rank lattice block has at least one row.  Otherwise its
diagonal block in

```text
X^T X=21S^(-1)
```

would be zero although `21S_j^(-1)` is positive definite.  Hence choosing one
component in a nontrivial decomposition produces a genuinely nonempty proper
triangle subset `I`.  Cross-block frame inner products vanish, so `M` and
`E=M/21` are coordinate-block diagonal across `I` and its complement.

The minimum-four premise is active.  With `S=diag(2,2)`, the integral row
`(1,1)` has norm four while meeting both orthogonal blocks.

## 2. Incidence transport is onto the exact eigenspace

For `u in im(E)=ker(Gamma)`,

```text
||Nu||^2=u^T(3I+Gamma)u=3||u||^2.
```

Thus `N` is injective on the 44-dimensional space `im(E)`.  Also

```text
(7I+A)Nu=N(3I+Gamma)u=3Nu,
```

so `Nu` lies in `ker(A+4I)`.  The target adjacency spectrum gives that
eigenspace dimension 44, proving equality rather than only containment:

```text
N(im(E))=ker(A+4I)=V.
```

The projector

```text
P=(27I-9A+J)/63
```

has eigenvalues `0,0,1` on the `14,3,-4` eigenspaces.  This checks both its
normalization and the use of `J`.

Coordinate-block diagonality is equivalent to `DE=ED` for the associated
diagonal sign matrix.  It makes `D` preserve `im(E)`.  Therefore, for
`K=NDN^T`,

```text
K(Nu)=ND(3I+Gamma)u=3N(Du) in V.
```

The symmetry of `K` is essential: it makes `V^perp` invariant as well, so
`KP=PK`.  A nonsymmetric exact countermodel in `results.json` preserves a
one-dimensional `V` but does not commute with its orthogonal projector.

## 3. Every commutator sign and coefficient

Expanding `KP=PK` gives

```text
-9KA+KJ=-9AK+JK,
9(KA-AK)=KJ-JK.
```

There is no sign reversal.  Since every triangle has three vertices,

```text
N^T 1=3 1,
K1=NDN^T1=3Ns=3d.
```

Symmetry then gives

```text
KJ-JK=3(d1^T-1d^T),
3(KA-AK)=d1^T-1d^T.
```

All factors `9`, `3`, and their cancellation agree with the frozen report.

## 4. The adjacent entry has no omitted summands

For distinct vertices, `Z_xw` can be nonzero only if `x~w`, while `A_wy`
can be nonzero only if `w~y`.  Thus every term in `(ZA)_xy` is indexed by a
common neighbor of adjacent `x,y`.  The same is true for `(AZ)_xy`.
The target has exactly one such neighbor `z`, so the full sums, not a
truncation, are

```text
(ZA)_xy=Z_xz,
(AZ)_xy=Z_zy.
```

Both edges `xz` and `zy` belong to the same unique graph triangle `xyz`;
because their signs come from the one diagonal triangle sign `s_xyz`,

```text
(ZA-AZ)_xy=0.
```

The diagonal part contributes `d_x-d_y`.  The `(x,y)` entry of the exact
commutator is consequently

```text
3(d_x-d_y)=d_x-d_y,
```

and forces equality along every edge.

The shared-triangle-sign premise is active.  On a single triangle, assigning
sign `+1` to `xz` and `-1` to `zy` gives
`(ZA-AZ)_xy=2`.  This symmetric signed adjacency matrix cannot arise from
one sign per graph triangle.

## 5. Connectedness and the signed double count

The use of connectedness is valid and explicit.  Adjacent pairs are joined
directly; every nonadjacent target pair has two common neighbors because
`mu=2`, hence is joined by a path of length two.  Therefore the signed
degree is a single integer `d` on all 99 vertices.

If `b=|I|`, there are `b` plus signs and `231-b` minus signs.  Each signed
triangle contributes to three vertex degrees, so

```text
99d=3(b-(231-b))=3(2b-231),
33d=2b-231.
```

Because `231=7*33` and `2` is a unit modulo 33,

```text
33 divides b.
```

The eight possible sizes are exactly

```text
0,33,66,99,132,165,198,231.
```

Connectedness cannot be dropped silently.  The checker uses the disjoint
union of two triangles: every edge still has one common neighbor and the
local cancellation holds, but plus and minus triangle signs give signed
degrees `+1` and `-1` on the two components.

## 6. Both trace routes close every block edge case

The submitted lattice-block trace is correct.  If the selected lattice block
has rank `r`, then

```text
X_I^T X_I=21S_I^(-1)
```

and

```text
4b=tr(S_I X_I^T X_I)=21r.
```

Thus `r=4k`, `b=21k`.  A nonempty proper rank block has `1<=k<=10`, while
`33|21k` forces `11|k`, a contradiction.  The checker exhausts all ten
proper ranks and all 55 unordered multi-block rank partitions of
`44=4*11`; every nonempty proper union again has `1<=k<=10`.  Choosing the
complement merely sends `(b,d)` to `(231-b,-d)`, so it creates no exception.

There is also a shorter independent check, not needed to repair the
submitted proof.  Since `E` is coordinate-block diagonal, the principal
block `E_I` is itself an orthogonal projector.  Its diagonal entries are
all `4/21`, hence

```text
rank(E_I)=tr(E_I)=4b/21.
```

The left side is an integer, so `21|b`.  Together with `33|b`,

```text
lcm(21,33)=231 divides b.
```

Only `b=0` and `b=231` remain.  This simplification confirms, rather than
exposes a flaw in, the submitted rank trace: indeed `rank(E_I)=r` because
`X_I` has full column rank.  It also makes all multiple-block and complement
choices visibly harmless.

## 7. Scope walls

The countermodels show that the following premises are genuinely active:

- minimum four for one-block row support;
- coordinate block commutation `DE=ED`;
- symmetry of `K`;
- one shared sign per graph triangle;
- connectedness, here supplied by target `mu=2`;
- actual vertex-triangle incidence and the target adjacency spectrum.

The audit does not weaken any public status wall:

```text
rootless decomposable endpoint S-form:  PASS_NO_FATAL_GAP for conditional exclusion
rootless indecomposable endpoint form:  UNKNOWN
rooted endpoint form:                   UNKNOWN
n3=708:                                UNKNOWN
Conway-99 existence/nonexistence:       UNKNOWN
novelty:                               UNKNOWN
```
