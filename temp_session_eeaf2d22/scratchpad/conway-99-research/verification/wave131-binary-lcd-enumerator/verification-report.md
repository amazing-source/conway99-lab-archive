# Wave 131 verification report

Claim label: `VERIFIED`, scoped to conditional finite distributions and
rational ordinary-enumerator feasibility.

## Preinspection

The discovery manifest was frozen at

```text
c305de05df2001d869db3dbfc14f7a2a8c7f305ce43471c56c66dc775e89d576.
```

All 13 sealed entries matched.  The discovery replay and its five tests
passed before the independent implementation was run.

## Binary LCD and symplectic facts

Reducing

```text
A^2=12I-A+2J
```

modulo two gives `A^2=A`.  Symmetry gives
`ker(A)=im(A)^perp`, while idempotence decomposes every vector as

```text
x=Ax+(I+A)x.
```

The two summands lie in `im(A)` and `ker(A)`, and their intersection is
zero.  Thus the `[99,54]` image and `[99,45]` kernel form a dual LCD pair.

Every adjacency row has even weight 14, so the image code is even.  Its
restricted dot product is therefore alternating and, by LCD, nondegenerate.
It is a 54-dimensional binary symplectic space.  Since
`A one=14 one=0`, the all-one word lies in the kernel and gives
`B_w=B_(99-w)`.

If either subset map agrees on `S,T` with `|S|,|T|<=3`, their symmetric
difference has weight at most six and lies in the opposite code.  The
imported minimum-eight bounds force `S=T`.

## Complete subset census

The independent census gives:

```text
vertices:                         99
edges/nonedges:                  693 / 4,158
triangles:                       231
induced paths:                 8,316
one-edge triples, c=0/c=1:   41,580 / 8,316
independent triples, c=0/c=1:70,686 / 27,720
```

For a three-set with `e` induced edges and `c` common neighbors,

```text
wt(A1_S)=30+2e+4c.
```

Toggling the three subset coordinates gives the dual weights.  Aggregation
reproduces exactly:

```text
image:
14:99, 24:4158, 26:693, 30:70686,
32:41580, 34:36036, 36:8547.

dual:
15:99, 24:693, 26:4158, 31:41580,
33:79002, 35:8316, 37:27720, 39:231.
```

Complementing by the all-one word gives the eight high-weight dual bounds.

## Rational MacWilliams witness

The verifier parsed all coefficients independently and checked:

```text
sum A_i=2^54,          sum B_j=2^45,
A_0=B_0=B_99=1,
d_A=14,               d_B=15,
A_i=0 for odd i,
B_j=B_(99-j),
all coefficients nonnegative,
all 23 forced lower bounds.
```

For every `j=0,...,99`, it evaluated

```text
B_j=2^-54 sum_i A_i K_j(i)
```

with exact binary Krawtchouk values, then evaluated all 100 inverse rows.
All 200 identities hold exactly.

The witness has 34 fractional image coefficients and 32 fractional dual
coefficients.  It is therefore not an integral formal enumerator.

## Integral and realization boundary

The sealed integral scout ended `UNKNOWN_HARD_TIMEOUT` and contains neither
an integral solution nor an infeasibility certificate.  This supplies no
evidence either way.

Even an integral ordinary enumerator would not construct a code.  A code
would not automatically be LCD or contain the two labelled 99-row systems,
and would not construct the target graph.  The no-code/no-graph boundary is
therefore preserved.
