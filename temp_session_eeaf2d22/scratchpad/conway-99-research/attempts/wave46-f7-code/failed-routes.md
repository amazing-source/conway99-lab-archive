# Retained null routes

## Ordinary weight-enumerator and MacWilliams route

The constraints

```text
length 231,
28 <= dimension <= 44,
self-orthogonal,
contained in 1^perp,
dual distance at least 3,
A69 >= 1386,
A1=A2=A4=0
```

do not contradict one another. Explicit actual codes satisfying a stronger
`A69>=668653683264` are archived for every dimension `28,...,44`.

This closes the ordinary-enumerator relaxation as a source of contradiction
unless more endpoint-specific information is added. It does not show that
an endpoint projector code exists.

## Complete weight-enumerator moments through degree two

The six forced endpoint scalar compositions, each with coefficient at least
231, have strict slack in every strength-two orthogonal-array moment at
dimension 28. Higher dimensions only increase the available slack.

The route stops because the compositions of the remaining
`7^r7-1-1386` nonzero words are unknown. A low-degree moment pass is neither
a complete enumerator nor an existence certificate.

## Weight divisibility from sum and squared norm

Exact residue dynamic programming for

```text
sum x_i=0,  sum x_i^2=0 mod 7
```

forbids weights exactly `1,2,4`. It permits every other weight through 231.
There is no useful high-weight divisibility restriction from these two
identities alone.

## Schur-cube rank

The exact entrywise identity

```text
M^(o3)=M+4I,  (M+4I)^(-1)=3M+2I
```

makes the third Schur power full and yields `r7>=11`. The previously
verified endpoint floor is `r7>=28`, so this route supplies structure but no
new bound.

## Quarantined `A+3I` object

The phrase `M=A+3I` in the initial assignment was inconsistent with the
project's object. For the 99 by 99 adjacency matrix, `A+3I` is invertible
over `F7` and has the full row code `F7^99`. It is not the 231 by 231
triangle projector `M=21E_0`.

The computation is retained as a prompt-error control and has
`used_in_live_conclusion=false`. It must not be recycled into the endpoint
argument.

## Most precise continuation

The next coding-theory target must retain the distinguished generator
geometry rather than only the row span. Promising exact data would be:

- complete symbol compositions of products or sums of two distinguished
  projector rows, stratified by their endpoint relation;
- character sums of the unknown complete enumerator beyond strength two;
- a proved stronger lower bound on `d(C^perp)` or exact small dual
  composition counts;
- identities in the Schur algebra generated jointly by the distinguished
  rows, not just the dimension of `C^(o3)`.

No absence-of-object inference is made from these null routes.
