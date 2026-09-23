# Wave 165: a general induced-cube/prism inequality

Status: `DERIVED`; repository-level independent verification and package
sealing are still required.

## Result

Let `C8` denote the number of induced subgraphs isomorphic to the
three-dimensional cube `Q3`, let `P` denote the number of induced triangular
prisms, and let `n3` have its established Conway-99 meaning. Every
hypothetical `srg(99,14,1,2)` satisfies

```text
12*C8 <= 37422 + 3*P = 41580 - n3.              (1)
```

Consequently,

```text
C8 <= 3465                                           generally,
C8 <= 3118                                           if P=0,
C8 <= 3118                                           at n3=4158.
```

The proof is purely combinatorial. It moves the eight-vertex cube count into
the space of rooted extensions of induced four-cycles, then counts the
exceptional extensions through induced triangular prisms.

## Local lemmas

Fix an induced four-cycle

```text
a0 -- a1 -- a2 -- a3 -- a0.
```

For each `i` modulo four, let `S_i` be the outside vertices adjacent to
`a_i` and to no other vertex of the fixed cycle. The strongly regular
parameters imply

```text
|S_i| = 10.
```

Every vertex of `S_i` has at most one neighbor in `S_(i+1)`. Indeed, if
`x in S_i` had two such neighbors `y,y'`, then the nonadjacent pair
`x,a_(i+1)` would have the three common neighbors `a_i,y,y'`,
contradicting `mu=2`.

Let `t_i` be the unique outside triangle apex on the cycle edge
`a_i a_(i+1)`. Exact common-neighbor accounting sharpens the partial
matching to

```text
|E(S_i,S_(i+1))| = 10  if t_(i-1) is adjacent to t_(i+1),
                       9  otherwise.
```

The exceptional apex edge produces an induced triangular prism. There are
two opposite apex-pair tests for a fixed square. If fewer than both tests
produce prisms, the square extends to at most nine cubes; if both do, it
extends to at most ten.

## Double count

Let `d(F)` be one when both apex-pair tests are present at the square `F`,
and zero otherwise. Every induced prism gives exactly three marked
square--apex-pair incidences, so

```text
2*sum_F d(F) <= 3*P.
```

The target has exactly 2,079 induced four-cycles and every `Q3` has exactly
six square faces. Therefore

```text
6*C8 <= 9*2079 + sum_F d(F),
12*C8 <= 18*2079 + 3*P = 37422 + 3*P.
```

The independently verified identity `n3+3P=4158` gives (1).

## Relation to the verified cube/Wagner covariance inequality

Wave 158 independently verified

```text
41580 - n3 + 12*C8 - 4*W8 >= 0.
```

Writing `N9=41580-n3`, the new result is `12*C8<=N9`. Combining the two
inequalities gives the additional derived upper bound

```text
W8 <= (41580-n3)/2.
```

These are genuine general motif bounds, but they do not by themselves
improve `n3 <= 4158`: a companion lower bound on the Wagner count, or more
directly on `W8-3*C8`, is still missing.

## Evidence boundary

- One clean-room hostile reader reconstructed `C8<=3465`.
- A second clean-room audit accepted the endpoint refinement
  `C8<=3118`.
- A hostile multiplicity audit accepted the marked-square/prism
  correspondence and equation (1).
- No computational checker was run because host free RAM was below the
  user-mandated 15% reserve.
- This directory is not yet a sealed `VERIFIED` package.
- Literature novelty is `UNKNOWN`.
- Conway-99 remains `UNKNOWN`.
