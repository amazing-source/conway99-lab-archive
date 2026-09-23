# Wave158 independent verification report

## Verdict

```text
VERIFIED_WITH_SCOPE:
exact general cube/Wagner covariance inequality for every hypothetical
srg(99,14,1,2)
```

The exact verified inequality is

```text
41580 - n3 + 12*C8 - 4*W8 >= 0,
```

where `C8` and `W8` are induced cube and Wagner/Möbius-ladder counts.

This verdict does not certify novelty, `n3<4158`, endpoint existence or
exclusion, a graph, or Conway-99.

## Separation and frozen inputs

The Wave157 manifest was frozen at
`c4082726ff1c4237824982550da6346204c58a91dc932b1f3a2d382b8801e405`
before inspecting the mathematical payload. All eight manifest entries and
both frozen source inputs verify.

The verifier did not import or execute
`attempts/wave157-general-cube-wagner/derive_symbolic_cut.py`. The six-set
formula source was parsed as static Python AST only.

## Root and flags

Mask 12 was decoded independently as the pointwise-labelled root with edges
`03` and `12`. Masks 21812 and 22708 decode to the claimed signed flags.
Swapping free vertices 4 and 5 gives labelled orbits
`{21812,26796}` and `{22708,25900}`. Both flags canonically forget to the
same six-vertex graph, mask 1884 (`N9`).

## Exhaustive covariance reconstruction

For union orders 6, 7, and 8, the verifier:

1. fixed roots 0–3;
2. tried every ordered pair of free pairs covering all non-root vertices;
3. tried both signs and both free-vertex orientations;
4. merged all induced edge and nonedge constraints;
5. completed every edge unseen by either flag;
6. enforced common-neighbor caps `lambda<=1` and `mu<=2`;
7. canonically minimized under every vertex permutation.

The complete class census is:

| Order | Canonical masks |
|---:|---|
| 6 | 1884 |
| 7 | none |
| 8 | 2022000, 5683824 |

Coefficients were then recomputed directly on each canonical graph by
enumerating every ordered root embedding and every ordered covering pair:

| Class | Roots | Positive products | Negative products | Zero | Coefficient |
|---|---:|---:|---:|---:|---:|
| `N9` | 8 | 8 | 0 | 0 | 8 |
| cube | 48 | 96 | 0 | 192 | 96 |
| Wagner | 16 | 0 | 32 | 64 | -32 |

The first moment on `N9` is zero: four roots have sign +1 and four sign -1.

## Named isomorphisms

The three-bit Hamming cube has labelled mask 216081675. The explicit vertex
map

```text
[0,5,6,3,7,2,1,4]
```

sends it to canonical mask 2022000.

The 8-cycle with opposite chords `i--i+4` has labelled mask 174400713. The
explicit map

```text
[0,5,4,1,7,2,3,6]
```

sends it to canonical mask 5683824. Thus the two coefficient classes have
the claimed cube and Wagner/Möbius-ladder names.

## Root count and six-set formula

There are `99*14=1386` ordered first edges. For one such edge, the common
nonneighbor set has 72 vertices. Twelve have internal degree 11 and the
remaining sixty have internal degree 10, giving

```text
12*11 + 60*10 = 732
```

ordered second edges. Hence the root-embedding count is

```text
R = 1386*732 = 1014552.
```

The frozen independent formula source has mask 1884 at one-based index 9.
Its AST is exactly `A(Q(b, 4), -1)`, with

```text
b = n*k*(k-2)*(k-4) = 166320.
```

Therefore `N9=41580-n3`.

## Scaling and endpoint

The raw covariance inequality is

```text
1014552 * (8*N9 + 96*C8 - 32*W8) >= 0.
```

The coefficient gcd is `8R=8116416`, yielding

```text
N9 + 12*C8 - 4*W8 >= 0.
```

At `n3=4158`, `N9=37422`. The endpoint coefficients have an extra gcd 2:

```text
18711 + 6*C8 - 2*W8 >= 0.
```

The total divisor is `16R=16232832`, and the recovered constant, divisor,
and order-eight coefficients match the previously stored endpoint cut.

## Strict-bound analysis

This theorem alone does not improve the upper bound: at `n3=4158`, setting
`C8=W8=0` leaves positive left side 37422. An independent comparison

```text
4*W8 - 12*C8 >= 37424
```

would imply `n3<=4156`, and conditionally `n3<=4155` using the known
divisibility by three. No such comparison is proved here.

## Hostile checks and resources

Ten tests pass. Mutations to the root mask, plus-flag mask, cube coefficient,
Wagner mask, root count, six-set formula, endpoint gcd, and strict-bound
status all fail closed; manifest and named-isomorphism controls also pass.

The first preflight saw only 14.35% free RAM, so computation was deferred.
Work resumed at 15.58%. The final verification run took 26.98 seconds and
stayed between 28.56% and 28.86% free RAM.
