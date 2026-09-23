# Wave 175: finite-polar boundary after dual distance four

Status: `VERIFIED_WITH_SCOPE`.

Wave 174 turns the 231 centered ternary columns into singular projective
points with no three collinear and 32 orthogonal companions each.  At the
smallest rank `k=11`, they lie on `Q(10,3)`.

The exact polar spectrum and the mod-three refined second moment both
survive.  The singular quadratic Veronese embedding nevertheless gives
necessary rank bounds that are new to this repository:

```text
rank_F3(J-I-R)<=65,
rank_F3(I+R)<=66.
```

This lane also quarantines an inapplicable polar-cap bound: its definition
forbids all orthogonal pairs, whereas the endpoint configuration has 3,696.
No graph or code search is used, and no endpoint exclusion is claimed.

An independent verifier reconstructed every parameter, moment, spectral
energy, divisibility condition, and rank cap. It also checked the cap
definition in the primary Blokhuis--Moorhouse paper. External novelty remains
`UNKNOWN`.
