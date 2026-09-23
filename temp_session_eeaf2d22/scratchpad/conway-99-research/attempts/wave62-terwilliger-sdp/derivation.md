# Exact signed-edge/Terwilliger derivation

## 1. The rooted label space

The 14 neighbors of a fixed graph vertex are seven mate pairs. A residual
vertex is adjacent to two nonmate root neighbors, so it is a signed edge of
`K7`: its two group indices give the support and its two choices inside the
mate pairs give the signs. There are

```text
4 * binom(7,2) = 84
```

labels.

Two distinct labels fall into five orbits under the rooted scaffold group
`C2 wreath S7`. Their valencies are

```text
2, 1, 20, 20, 40.
```

The first orbit is the 84 pairs obtained by flipping exactly one sign on a
fixed support. Such an edge would close a triangular prism with one fixed
root triangle, so it is absent at `n3=4158`.

Exact multiplication of the six orbital matrices gives a commutative
association scheme. In the relation order frozen in `protocol.md`, its
common eigenvalue rows and multiplicities are

```text
m=1:   1,  2,  1, 20,  20,  40
m=6:   1,  2,  1,  6,   6, -16
m=7:   1,  0, -1, 10, -10,   0
m=14:  1,  2,  1, -4,  -4,   4
m=21:  1, -2,  1,  0,   0,   0
m=35:  1,  0, -1, -2,   2,   0.
```

This describes the scaffold, not the automorphism group of a completion.

## 2. The one-parameter endpoint average

Let `y` be the number of selected same-support/Hamming-two edges. The exact
Wave 3 identities give the five selected off-diagonal orbit counts

```text
0, y, 84, 84-2y, 336+y.
```

Consequently `0<=y<=42`. Averaging `B` over every scaffold relabeling gives
an orbital matrix whose eigenvalues on the six spaces above are

```text
12, -2, 0, y/28, y/42, -y/35.
```

The first three values show spectrally that the 6-space and 7-space are
actual `B` eigenspaces. Equivalently, the averaged variance

```text
average(B^2) - average(B)^2
```

vanishes there. This recovers the already known linear relation
`2y+e4=84`; it does not improve the endpoint.

## 3. Exact projector blocks

On the remaining 70-dimensional subspace, `B` has only eigenvalues `3,-4`.
The projector onto eigenvalue three is

```text
P3=(B+4I-16E_1-2E_6-4E_7)/7.
```

Its diagonal is `10/21`. Its off-diagonal entries, listed as
`nonedge/edge`, are

```text
orbit 1: -1/21,  2/21
orbit 2:      0,   1/7
orbit 3:  -2/35,  3/35
orbit 4: -1/105,  2/15
orbit 5: -2/105, 13/105.
```

The averaged `P3` weights on the `14,21,35` scaffold spaces are

```text
4/7 + y/196,
4/7 + y/294,
4/7 - y/245.
```

Their multiplicity-weighted sum is exactly 40. For every real
`0<=y<=42`, all three weights and their complements lie in `[0,1]`.
Therefore the complete one-point invariant linear projector SDP is feasible
throughout the whole endpoint parameter interval.

## 4. Schur-positive extension

Hadamard products of PSD matrices are PSD. The package tests

```text
E_s o P3^(o a) o Pminus4^(o b)
```

for all six primitive scaffold idempotents and `a+b<=24`. After scaffold
averaging each matrix has six scalar blocks, and each block is affine in
`h=y/42`. Exact endpoint evaluation therefore covers every rational
`h in [0,1]`.

The finite census contains

```text
1,949 averaged matrices,
23,388 endpoint block inequalities,
23,316 positive eigenvalues,
72 zero eigenvalues,
0 negative eigenvalues.
```

This is a rigorous null result for the declared family. It is not evidence
that the endpoint graph exists.

## 5. Mathematical boundary

The one-point average forgets which particular orbit-2 matching edges and
orbit-4 cycle edges occur together. That is precisely the compatibility
information in which a contradiction could hide. A genuinely stronger
continuation should use:

1. two-root stabilizer blocks, conditioned on the relation and adjacency of
   the two roots; or
2. triangle-root flags that retain the three simultaneous residual-edge
   choices and the zero-prism clauses.

Either route needs new joint variables. Replacing those variables by
products of averaged counts would be unsound.
