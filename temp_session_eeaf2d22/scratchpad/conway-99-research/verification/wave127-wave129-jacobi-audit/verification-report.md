# Wave 127/129 verification report

Claim label: `VERIFIED`, restricted to six finite relaxation-feasibility
claims.

## Seal preinspection

Before discovery inspection, the verifier froze:

```text
Wave127 manifest:
f4a1039928dcbd21e8de81f199265c80631182ec53f51d8c7e657259ee2f5fe4

Wave129 manifest:
93e1f208faec2187ed3339e131af670d181a63a9518e6fd39ef0939540d79e5b
```

All 55 Wave 127 entries and all 16 Wave 129 entries matched.

## Module reconstruction

For `Gamma_0(7)`, the index is eight, there are two cusps, no order-two
elliptic points, two order-three elliptic points, and genus zero.  The
even-weight dimension formula is therefore

```text
dim M_w(Gamma_0(7)) = 1 + 2 floor(w/3).
```

At weights `22,24,...,42`, this gives

```text
15,17,17,19,21,21,23,25,25,27,29,
```

with sum 239.  The verifier independently built the character-seven odd
Eisenstein series and checked that their even-weight products have these
exact ranks through the level-seven Sturm bounds.

Using the standard double-zero division by `A=phi_-2,1` and evaluation at
`z=0` with `B=phi_0,1`, this supports the direct decomposition

```text
J^weak_(22,10)(Gamma_0(7))
 = direct sum_(c=0)^10 M_(22+2c)(Gamma_0(7)) A^c B^(10-c).
```

The cache normalizations `A=q^0(y^-1-2+y)` and
`B=q^0(y^-1+10+y)` also match exactly.

## Fricke factor

Starting from the frozen discriminant-16 relation and substituting the
full-level transformations of `A` and `B`, the exponential factors cancel.
For the `c` block of weight `w=22+2c`, the remaining power of seven is

```text
-14 - 2c + w/2 = -14 - 2c + 11 + c = -3-c.
```

Hence

```text
h_c = -7^(-3-c) (f_c | W_7).
```

All 616 raw product maps square to the identity.  In the sealed
Fricke-eigen basis, all 3,234 exact `q^0` comparisons satisfy

```text
c_K(0,7r) = -7^(-3-c) epsilon c_L(0,r),
epsilon in {+1,-1}.
```

The seven caches form one coherent expansion: every lower cache is the
exact truncation of the next, across 706,322 checked coefficients.

## Independent constraint replay

The verifier did not call `jacobi_lp.py` or `verify_candidate.py`.  From each
sealed Fourier cache it independently rebuilt:

1. both constant equations;
2. every L- and K-side holomorphy zero;
3. every K minimum-gap and graph-support zero;
4. every retained coefficient nonnegativity row; and
5. every L- and K-side tight-frame second-moment row.

Each rational candidate was substituted into every unreduced row:

```text
cutoff 10: 282 equalities,  320 inequalities, 263 tight
cutoff 12: 304 equalities,  436 inequalities, 300 tight
cutoff 14: 326 equalities,  562 inequalities, 332 tight
cutoff 16: 346 equalities,  700 inequalities, 344 tight
cutoff 18: 366 equalities,  846 inequalities, 381 tight
cutoff 20: 386 equalities, 1000 inequalities, 396 tight
```

Every exact equality holds and every exact inequality is nonnegative.

## Cutoff 28 and boundary

The cutoff-28 artifact contains no rational solution.  Its exact reduction
has 139 independent equalities, 510 deduplicated inequalities, and a
100-dimensional affine space.  The floating solve and failed recovery are
diagnostics only; no exact Farkas certificate was produced.  Its status is
therefore `UNKNOWN`.

No graph or lattice is constructed.  Rank 28 is neither realized nor
excluded.  Conway-99 and novelty remain `UNKNOWN`.
