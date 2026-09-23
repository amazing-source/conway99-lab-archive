# Boundary observations and failed sharpenings

## Nine is the endpoint constant, not automatically the general constant

The exact boundary-matching argument gives size ten precisely when the
relevant opposite edge apexes are adjacent. That adjacency creates an
induced triangular prism. Therefore nine is valid in the prism-free branch,
but not from the bare SRG parameters alone.

## The cube upper bound does not close the endpoint

Combining the stronger relation

```text
12*C8 <= 41580-n3
```

with the verified inequality

```text
41580 - n3 + 12*C8 - 4*W8 >= 0
```

gives

```text
W8 <= (41580-n3)/2.
```

This is still an upper bound on `W8`; endpoint exclusion requires a lower
bound of the opposite kind. The useful unresolved quantity remains
`W8-3*C8`.

## A rooted Wagner comparison is the natural continuation

The successful change of space is from global eight-vertex counts to
extension multiplicities over a fixed four-cycle. A corresponding rooted
classification of Wagner extensions could yield a direct inequality
between `W8` and `C8`. No such classification is proved here.
