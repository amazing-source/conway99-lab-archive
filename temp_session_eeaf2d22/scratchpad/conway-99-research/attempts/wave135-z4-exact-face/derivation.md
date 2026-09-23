# Exact affine-face derivation

## 1. Character matrix

Let `S` be the 1,119 symmetry orbits of primal compositions retained by the
corrected Wave134 model, and let `F` be its 161 forbidden dual orbits. For
`s in S` and `t in F`, let

```text
M[t,s] = Krawtchouk character coefficient from s to t.
```

Every entry is an integer. A formal primal enumerator `x` must satisfy

```text
M x = 0.
```

FLINT rational RREF gives `rank_Q(M)=143`. Independently, a greedy elimination
modulo `p=2147483647` finds a nonzero 143 by 143 minor, proving
`rank_Q(M)>=143`. The 18 explicit independent vectors in the left kernel of
`M` prove `rank_Q(M)<=161-18=143`.

## 2. Meaning of the 18 dependencies

Order the forbidden rows by the Wave134 `(a,b,c)` target composition. The low
odd-weight shells have a common 44-dimensional restriction:

```text
b=2:  c=0,...,48, with c=44,...,48 dependent;
b=4:  c=0,...,47, with c=44,...,47 dependent;
b=6:  c=0,...,46, with c=44,...,46 dependent.
```

This contributes `5+4+3=12` dependencies. They arise because the character
polynomials are being evaluated only on the restricted primal shell, so the
nominally distinct target rows exceed the dimension of the restricted
polynomial-function space.

At the opposite end, the rows collapse to one dimension:

```text
b=92: c=1,2,3 are 7,21,35 times the c=0 row;
b=94: c=1,2 are 5,10 times the c=0 row;
b=96: c=1 is 3 times the c=0 row.
```

These contribute the remaining `3+2+1=6` dependencies. The full primitive
integer coefficients are retained in `face-rank.json`, not inferred from
floating point.

## 3. Affine equations

Besides `M x=0`, a formal enumerator has

```text
sum_s x_s = 2^108,
x_(99,0,0) = 1.
```

These two rows independently raise the rank from 143 to 145. The order of the
torsion subgroup gives the further shell identity

```text
sum_(s=(a,0,c)) x_s = 2^54.
```

It is independent of the first 145 rows. Hence the final coefficient rank is
146 and the affine dimension is 973. The augmented matrix also has rank 146,
so no equality-only contradiction exists.

## 4. Lower-bound translation

Let `l` be the exact Wave134 forced-primal table and write

```text
x = l + z.
```

The primal inequalities become `z_s>=0`. The equalities become

```text
M z = -M l,
sum z = 2^108 - sum l,
z_(99,0,0) = 1 - l_(99,0,0) = 0,
sum_(b=0) z = 2^54 - sum_(b=0) l.
```

Every allowed dual inequality with character row `r_t` and forced lower bound
`d_t` becomes

```text
r_t z >= 2^108 d_t - r_t l.
```

All transformations are exact over the rationals.

## 5. Certification boundary

A feasible rational vector is a certificate only after reconstruction
`x=l+z` and exact replay of:

- all 1,119 primal lower bounds;
- normalization and `A_0=1`;
- the torsion-shell identity;
- all 161 forbidden dual equalities, including the 18 omitted dependent rows;
- all 1,114 allowed dual lower/nonnegativity inequalities.

Even such a rational enumerator would be only a necessary-condition witness.
It would not construct an integral enumerator, a `Z4` code, or the target
strongly regular graph.
