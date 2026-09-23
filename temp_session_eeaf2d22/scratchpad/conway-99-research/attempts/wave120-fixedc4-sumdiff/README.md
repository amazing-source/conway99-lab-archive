# Wave 120: fixed-C4 sums and differences

Claim labels: `DERIVED`, `REFUTED_AS_A_RELAXATION`, and `UNKNOWN`.
Independent verification is required.

For two same-oriented short vectors through one induced four-cycle, their
sum has cycle coordinates `(2,-2,2,-2)`.  The common projector gives the
exact real affine minimum `112/5`.  Integrality and only the four anchor
equations sharpen every actual integer eigenvector in that affine slice to
squared norm at least

```text
32.
```

More generally, the sum of `r` same-oriented extensions has squared norm
at least `4r^2+8r`.  This gives explicit pairwise inner-product intervals
for all pairs of norms 16, 18, and 20 and a family-wide moment inequality.
It is a genuine strengthening of the earlier minimum-distance relaxation.

It still does not prove either required local cap.  A machine-readable
size-40 formal norm-16 witness satisfies:

- the fixed-C4 type counts and all four anchor eigen-equations;
- every derived sum/difference norm and low-norm magnitude-profile rule;
- every positive subset-sum anchor-mass inequality;
- a positive-definite rank-40 residual Gram after subtracting the common
  interpolant;
- binary constant weight 16 and minimum support distance 14.

Thus pairwise PSD/Gram or binary minimum-distance Delsarte data alone admit
40 extensions, well above the needed caps 25 and 24.  The witness is not a
common integer eigenspace family: it does not encode the 95 outside
eigen-equations, one common graph adjacency matrix, or the full target
parity code.  Those simultaneous higher-order conditions are exactly what
remain.

No rank row is excluded.  Conway-99 and literature novelty remain
`UNKNOWN`.
