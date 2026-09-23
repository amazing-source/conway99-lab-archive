# Wave 166: rooted spaces for a Wagner lower bound

Status: `DERIVED_STRATEGY`; the sufficient four-failure lemma is
`UNPROVED`.

## Why the target changed

At the prism-free endpoint, Wave 165 gives

```text
C8 <= 3118.
```

The verified cube/Wagner covariance inequality is

```text
37422 + 12*C8 - 4*W8 >= 0.
```

Therefore an absolute lower bound

```text
W8 >= 18710
```

would already contradict the endpoint. This replaces the earlier relative
target on `W8-3*C8` by a concrete counting problem.

## Fixed-four-cycle space: exact but insufficient

For a fixed induced four-cycle with singleton classes `U_i`, every
`x in U_i` satisfies

```text
deg(x,U_(i+2))
  = deg(x,U_(i-1)) + deg(x,U_(i+1)).
```

At `P=0`, each opposite-class graph has 18 edges and maximum degree two.
The four outside vertices of a cube or Wagner extension form one of three
labelled four-cycles: one cube pattern and two crossed Wagner patterns.

An explicit abstract shell with all consecutive matchings equal to the
identity on `Z/9`, and opposite shifts `{0,1}` versus `{2,3}`, satisfies
every displayed degree equation but has no crossed Wagner. Thus these shell
equations alone cannot force `W8>0`; next-shell compatibility is essential.

## Induced-five-cycle space

The target has exactly 33,264 induced `C5`s, and every Wagner graph contains
exactly eight. Hence

```text
sum_(F induced C5) e_W(F) = 8*W8.
```

The exact sufficient aggregate target is

```text
sum_F e_W(F) >= 149680.
```

A uniform local lemma `e_W(F)>=5` would be stronger than necessary, giving
`W8>=20790`.

## Nonedge-root reduction

Every nonedge lies in exactly 40 induced `C5`s with that nonedge marked as
a diagonal. For a marked cycle

```text
u-p-v-y-x-u,
```

two forced second-common-neighbor vertices `r,s`, followed by a
singleton-supported common neighbor `z`, give a canonical Wagner extension
when the support and inducedness checks pass.

Let `f(uv)` be the number of the 40 marked cycles at a nonedge `uv` that
have no such extension. The single remaining sufficient lemma is:

```text
P=0  =>  f(uv) <= 4 for every nonedge uv.        (UNPROVED)
```

If true, at least `4158*36=149688` marked cycles extend, so
`W8>=18711`; together with `C8<=3118`, this contradicts the endpoint
covariance inequality.

## Current obstruction

The pair equations bound the obvious endpoint-support failures by four in
each of the two common-neighbor lanes. They do not yet:

1. force a pure endpoint pair to be nonadjacent;
2. force one of its two common neighbors to have the required singleton
   support; or
3. couple the two lanes strongly enough to reduce eight possible failures
   to four.

The previously verified Wave 150 pair-root pseudowitness also survives both
new scalar inequalities with slack 2,079:

```text
C8=11781/4, W8=35343/2, A=B=2079.
```

Thus pair-root order-eight PSD plus the two scalar bounds cannot be enough.
A proof-producing computational continuation must either couple the full
root-3 and root-12 covariance blocks into one exact dual certificate, add an
integrality argument, or lift marked-`C5` completion second moments to order
eleven.

No Wagner lower bound, endpoint exclusion, graph, literature novelty, or
Conway-99 resolution is claimed.
