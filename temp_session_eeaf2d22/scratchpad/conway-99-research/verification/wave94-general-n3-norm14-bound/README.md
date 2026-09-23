# Wave 94 independent verifier

Verdict: `VERIFIED` in the conditional scope of a hypothetical
`srg(99,14,1,2)`.

The clean-room verifier proves

```text
N14 <= floor((38808+12P)/7)
     = floor((55440-4*n3)/7),
```

where `P` counts induced triangular prisms, `n3+3P=4158`, and `N14` counts
both signs. No prism-free, rank-28, or automorphism hypothesis is used.

See `audit.md` for the proof and boundary. The result does not bound `N16`
or `N18`, improve the general upper bound on `n3`, or resolve Conway-99.
