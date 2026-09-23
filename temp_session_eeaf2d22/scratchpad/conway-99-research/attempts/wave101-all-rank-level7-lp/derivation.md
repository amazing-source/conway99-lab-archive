# Exact derivation

## Frozen setting

Condition on the independently verified Wave 66/71 transfer from a
hypothetical `srg(99,14,1,2)`. For each surviving even `q` in
`2,4,...,14`, there are rank-44 positive-definite even level-7 lattices
`L,K` with

```text
det(L)=7^q,  K=sqrt(7)L*,  min(K)>=14.
```

Use

```text
Theta_K = sum_n x_n q^n,  Theta_L = sum_n y_n q^n,
```

where the exponent is half the squared norm. Hence

```text
x0=y0=1,  x1=...=x6=0,
```

and every nonconstant `x_n,y_n` is a nonnegative even integer for an actual
lattice.

## Full modular space and Poisson factor

The frozen Wave 86 basis has exact rank 15 through the Sturm bound 14 and
therefore spans all of `M_22(Gamma0(7))`. Its exact rational Fricke matrix
`F` satisfies `F^2=I`. The corrected normalized Eisenstein transformations
are

```text
A_k|W_7 = -i 7^((k-1)/2) B_k,
B_k|W_7 = -i 7^((1-k)/2) A_k.
```

Poisson summation in rank 44 gives, for each row,

```text
y = -7^(11-q/2) F x.
```

The powers for `q=2,4,...,14` are respectively `10,9,...,4`. The minus sign
comes from `i^(-22)=-1`.

## Seven-variable exact LP

The equation `y0=1` has a nonzero `x14` coefficient, so eliminate `x14`.
Write `z=(x7,...,x13)`. Then every relevant coefficient is an affine
rational form

```text
x14 = c14 + a14.z,
y_n = c_n + a_n.z,  1<=n<=14.
```

The feasible scalar cone is cut out by

```text
x7,...,x13,x14,y1,...,y14 >= 0.
```

For every reported objective `O=c+a.z`, the script solves two exact
seven-by-seven rational systems:

1. A dual identity

   ```text
   O-B = sum_g lambda_g g,  lambda_g>=0,
   ```

   where each `g` is one of the nonnegative coordinate forms.

2. A primal point at which all seven supported forms vanish.

Exact equality of the primal and dual values proves that `B` is the
continuous LP optimum. Since an actual theta coefficient counts `v` and
`-v`, every reported integer-weight objective is even; the theorem-level
integer bound is the least even integer at least `B`.

## Main and prefix bounds

| q | total through norm 28 | first positive prefix | parity-rounded prefix bound |
|---:|---:|---:|---:|
| 2 | 182 | through norm 26 | 166 |
| 4 | 1,584 | through norm 24 | 142 |
| 6 | 11,400 | through norm 24 | 1,328 |
| 8 | 80,110 | through norm 24 | 9,626 |
| 10 | 561,084 | through norm 22 | 932 |
| 12 | 189,901,474 | through norm 22 | 9,748 |
| 14 | 1,831,606,638 | through norm 20 | 6,842 |

`exact-results.json` records all intermediate prefix optima, the triangular
objective

```text
8x7+7x8+6x9+5x10+4x11+3x12+2x13+x14,
```

every exact multiplier, and a matching exact primal optimizer.

## Congruence check

For each reported objective, the Wave 71 level-one mod-7 affine family was
replayed after imposing `x0=1` and `x1=...=x6=0`. Every objective has a
nonzero direction residue, so none has a fixed residue modulo seven.
Consequently this package uses parity rounding only. It does not claim that
the displayed rational LP optimizers jointly satisfy every integral or
mod-7 theta constraint; a combined exact integer program is a separate
problem.

## Rigorous upper-bound comparison

Let `S_m={v in K: 0<(v,v)<=m}`. Since `min(K)>=14`, a nonzero vector of norm
at most 28 cannot lie in `2K`.

For `m<=26`, if two vectors in one nonzero coset of `K/2K` are not
antipodal, then

```text
u=(v-w)/2, t=(v+w)/2
```

are two nonzero vectors of `K`, while

```text
(u,u)+(t,t)=((v,v)+(w,w))/2 <= 26.
```

This contradicts `(u,u),(t,t)>=14`. Thus each nonzero mod-2 coset contains
at most one antipodal pair and

```text
|S_26| <= 2(2^44-1) = 35,184,372,088,830.
```

At the norm-28 boundary, any two non-antipodal representatives in the same
coset force equality throughout and are orthogonal norm-28 vectors. There
are at most 44 such directions per coset, so

```text
|S_28| <= 88(2^44-1) = 1,548,112,371,908,520.
```

Every Wave 101 lower bound is well below its corresponding rigorous upper
bound. There is no contradiction and no row exclusion.

## Exact null boundary

The script also gives integral, even, nonnegative first-15-coefficient
controls attaining a zero prefix:

| q | scalar LP still permits |
|---:|---:|
| 2 | `x7=...=x12=0` |
| 4,6,8 | `x7=...=x11=0` |
| 10,12 | `x7=...=x10=0` |
| 14 | `x7=x8=x9=0` |

These are formal scalar coefficient controls, not lattices or graphs. They
show why the new positive bounds land beyond the graph dictionary:
Wave 71 proves the signed-unit eigenvector interpretation only for
`x7,x8,x9`, corresponding to norms `14,16,18`.
