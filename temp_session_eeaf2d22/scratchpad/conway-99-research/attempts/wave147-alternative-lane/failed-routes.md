# Wave 147 boundary and retained non-results

## No numerical solve

No SDP solver was run.  The purpose of this lane was to construct the exact
smallest order-eight two-root model and identify the `n3` coefficient before
spending resources on a singular numerical relaxation.

## Ordinary deletion is not the full SRG lift

The 208 equations

```text
92*x_H7 = sum_K d(H7,K8)*x_K8
```

are exact, but they use only the graph order `99`.  A competitive relaxation
must also encode the marked-vertex degree and marked-pair common-neighbor
extension equations at order eight.  Omitting those rows enlarges the
feasible region and cannot justify a nonexistence claim.

## A coefficient is not an isolated formula

The selected PSD entries contain `4*n3` and no prism term, but counts of
other induced classes also occur.  Positivity of one entry, or of a small
principal minor, does not by itself yield a strict upper bound.

## Rationalization wall

Even a future floating optimum below 4158 would remain `UNKNOWN` until the
dual is converted to exact rational PSD blocks and replayed against the
integer coefficient stream.  Singular numerical faces are expected from
the earlier flag-moment work.

## Status

```text
complete coefficient layer:       DERIVED
ordinary deletion lift:           DERIVED
strong SRG extension lift:        NOT_YET_BUILT
numerical SDP:                     NOT_RUN
rational upper-bound certificate: NOT_OBTAINED
strict n3 upper bound:             UNKNOWN
Conway-99:                         UNKNOWN
```

