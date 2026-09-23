# Wave 101 independent all-rank level-seven LP audit

Date UTC: 2026-07-28.

Verdict: **VERIFIED_WITH_SHARPENING**.

Conditional scope: the seven scalar theta cones attached by the verified
Wave 66/71 transfer to a hypothetical `srg(99,14,1,2)`, for
`q=2,4,...,14`. The audit does not construct a lattice or graph and does not
exclude any row.

## Frozen discovery artifact

The discovery manifest has SHA-256

```text
54d620a8644d7efe5d2e418869b035331127862c2125ef3da325272417307619
```

All eleven listed discovery entries match. The verifier neither imports nor
executes discovery code before sealing its independent result.

Process note: a broad repository grep returned a few Wave 101 prose-line
matches during the same batched read as the manifest hash. The exact
modular-form arithmetic, LP optimizers, dual multipliers, mod-seven systems,
and upper-bound analysis were nevertheless independently reconstructed, and
the full independent JSON was hash-frozen before substantive discovery
comparison.

## Complete modular space

For `Gamma0(7)`:

```text
index = 8, cusps = 2, e2 = 0, e3 = 2, genus = 0,
dim S_22 = 13, dim M_22 = 15, Sturm bound = 14.
```

The verifier generated the twisted Eisenstein series
`E_k(chi,1)` and `E_k(1,chi)` from generalized Bernoulli numbers and twisted
divisor sums. A selected 15-product basis has exact rank 15 through the
Sturm bound. Using the corrected q-normalized transformations

```text
E_k(chi,1)|W_7 = -i 7^((k-1)/2) E_k(1,chi),
E_k(1,chi)|W_7 = -i 7^((1-k)/2) E_k(chi,1),
```

the independently reconstructed rational Fricke matrix squares exactly to
the identity.

## Poisson factors

Write `x_n=[q^n]Theta_K` and `y_n=[q^n]Theta_L`, with
`Theta=sum_v q^((v,v)/2)`. Since

```text
det(K)=7^(44-q), rank(K)=44, weight=22, i^(-22)=-1,
```

Poisson summation gives

```text
Theta_L = -7^(11-q/2) (Theta_K|_22 W_7).
```

The exact factors for `q=2,4,...,14` are

```text
-7^10, -7^9, -7^8, -7^7, -7^6, -7^5, -7^4.
```

Thus both the sign and every power agree with discovery.

## Exact LP certificates

The conditions

```text
x0=y0=1, x1=...=x6=0,
x7,...,x14,y1,...,y14 >= 0
```

leave seven affine variables after eliminating `x14` with `y0=1`. For every
submitted objective, the verifier solved:

```text
objective - bound = sum_g lambda_g g, lambda_g >= 0,
```

and an exact seven-form active system yielding a feasible primal point with
the same value. Exact strong duality therefore proves each continuous LP
optimum.

The main total bounds independently obtained are:

| q | r | rational lower bound on `x7+...+x14` | even lower bound |
|---:|---:|---:|---:|
| 2 | 42 | `717848/3971` | 182 |
| 4 | 40 | `6286208/3971` | 1,584 |
| 6 | 38 | `45264728/3971` | 11,400 |
| 8 | 36 | `28919488/361` | 80,110 |
| 10 | 34 | `2228061848/3971` | 561,084 |
| 12 | 32 | `15580466396938/82045` | 189,901,474 |
| 14 | 30 | `6793429016900/3709` | 1,831,606,638 |

The first positive prefix in each row also matches:

| q | prefix | rational optimum | even lower bound |
|---:|---:|---:|---:|
| 2 | through norm 26 | `329/2` | 166 |
| 4 | through norm 24 | `704/5` | 142 |
| 6 | through norm 24 | `6632/5` | 1,328 |
| 8 | through norm 24 | `48128/5` | 9,626 |
| 10 | through norm 22 | `27008/29` | 932 |
| 12 | through norm 22 | `282641/29` | 9,748 |
| 14 | through norm 20 | `389888/57` | 6,842 |

For the triangular objective

```text
8x7+7x8+6x9+5x10+4x11+3x12+2x13+x14,
```

the independently verified rational optima are respectively

```text
4396992/3971,
40783020/3971,
295485216/3971,
188945508/361,
14558808192/3971,
33591770046447/164090,
7868750058702/3709.
```

Every objective has integer weights and every nonconstant lattice theta
coefficient is even by `v <-> -v`, so rounding to the least even integer is
valid.

## Mod-seven scope

For every `q` row, the verifier regenerated the level-one weight
`154-3q` family modulo seven from `E4` and `E6`, imposed coefficients
`q^0,...,q^6=(1,0,...,0)`, and propagated every affine direction through
`q^14`.

The direction space projects with full rank three onto `(x7,x8,x9)`.
Moreover, every tested prefix and triangular objective varies along at least
one affine direction. No fixed residue modulo seven is available for these
objectives. Discovery correctly uses antipodal parity only and does not
silently round modulo fourteen.

## Crucial null

Every row retains a formal scalar control with

```text
x7=x8=x9=0.
```

The verifier independently found nonnegative rational witnesses and then
substituted every submitted integral witness into its own affine Fricke
system. All submitted `x7,...,x14,y1,...,y14` values satisfy the equations
exactly and are nonnegative even integers.

Therefore scalar positivity through the Sturm bound does not force a vector
of norm 14, 16, or 18. This is a genuine null boundary, not evidence that
the corresponding lattices exist.

## Mod-two upper comparison and sharpening

Let `S_m` contain the nonzero vectors of `K` of norm at most `m`. If
non-antipodal `v,w` lie in one class modulo `2K`, then

```text
u=(v-w)/2, t=(v+w)/2,
||u||^2+||t||^2=(||v||^2+||w||^2)/2.
```

Since `min(K)>=14`, this proves the submitted valid bounds

```text
|S_26| <= 2(2^44-1) = 35,184,372,088,830,
|S_28| <= 88(2^44-1) = 1,548,112,371,908,520.
```

At norm 28, equality for two non-antipodal same-coset representatives forces
them to be orthogonal, hence at most 44 antipodal pairs per coset.

Discovery bounded the triangular objective by eight times the second
quantity. That is valid but nonsharp. If a coset contains a vector below
norm 28, it contains only that antipodal pair in the range and contributes
at most 16 to the triangular objective. Otherwise it contains only norm-28
directions and contributes at most `2*44=88`. Thus the sharper bound is

```text
triangular objective <= 88(2^44-1)
                      = 1,548,112,371,908,520.
```

Even the largest verified triangular lower bound, 2,121,528,730 in the
`q=14` row, is far smaller. No lower/upper collision occurs.

## Dictionary and status boundary

The verified graph dictionary is used only as

```text
x7=N14, x8=N16, x9=N18.
```

No signed-unit, support, or integer-eigenvector interpretation is assigned
to `x10,...,x14`. The new mass begins beyond the graph-specific dictionary,
so it does not combine directly with the Wave 100 norm-14 upper bound.

Final status:

```text
all seven scalar LP packages: VERIFIED_WITH_SHARPENING
any q row excluded:           no
lattice realized:             no
graph constructed:            no
Conway-99:                    UNKNOWN
literature novelty:           UNKNOWN
```

