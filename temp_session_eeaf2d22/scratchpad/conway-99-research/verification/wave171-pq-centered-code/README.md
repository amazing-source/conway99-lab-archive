# Wave 171 independent verification

Verdict: `VERIFIED_WITH_SCOPE`.

The verifier independently checked the unrestricted finite-field theorem for
the triangle-block graph:

```text
X=K-K^2 over F_3,
X^2=0,
B*X=0,
(n0,n1,n2)=(33,36-3*p_L,162+3*p_L).
```

It also checked that the 99 point-star `K7`s are intrinsic in `K` and that,
with `M0=21E0` and `C=2M0-21I`,

```text
X+C=2J,
X=2(C+J),
rank_F3(X)=rank_F3(C)-1.
```

The last identities hold without assuming the prism-free endpoint.  At the
conditional endpoint branch `r3=12`, `row(X)` is exactly the earlier centered
`[231,11]_3` code up to multiplication by two.  This is a verified
reformulation, not a new code obstruction.

No construction, nonexistence proof, strict `n3` bound, or target resolution
is certified.
