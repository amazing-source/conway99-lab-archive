# Wave 24 retained incomplete and non-excluding routes

None of the items below is evidence that the target exists or does not exist.
They are retained to keep the exact boundary of the `n3=708` attack visible.

## 1. The modular ranks remain graph-dependent

The verified Smith formula gives

```text
h=3^(44-rank_F3(M)) 7^(44-rank_F7(M)).
```

The new determinant bound narrows the possible index to

```text
{9,21,49,81,189,441,729,1029},
```

and the checker records the corresponding pairs of modular ranks.  The
previous identities `NM=J mod 3` and `S_Seidel^2=0 mod 7` do not decide those
ranks.  No saturation of the triangle-incidence columns and no integral
splitting of the rational `+7` and `-7` spaces is assumed.

## 2. Moment and characteristic-polynomial data do not exclude 708

The nonzero characteristic-polynomial coefficient of `C=(B-I)/2` improves
the universal floor to

```text
tr(C^2)>=8,  tr(B^2)>=108,
```

and the logarithmic pseudodeterminant argument improves the determinant cap
to `det(B)<=6561`.  This is a restriction, not a contradiction.

An exact rank-44 coordinate-lattice relaxation survives with

```text
h=9, det(Q)=9, det(B)=81, tr(B)=60.
```

It is checked in `exact_check.py`.  This object is not asserted to have a
primitive embedding in `Z^231`, to arise from 231 norm-four projector
vectors, or to satisfy `W=M o M`.

## 3. Local diagonal and harmonic constraints still have scalar survivors

At `n3=708`,

```text
sum_T(q(T)-2)=10,
tr(A4)=1260.
```

The harmonic-cubic kernel excludes `q=12`, and a centered two-by-two minor
allows at most one `q=11`.  The local diagonal budget gives additional
multiplicity caps for large `q`, but the scalar profile

```text
221 entries q=2, 10 entries q=3
```

satisfies every displayed `q` budget.  No matrix realizing that profile is
claimed.

## 4. Even-lattice existence cannot be inferred from determinant residues

The conditions

```text
h=1 mod 4, det(Q)=1 mod 4,
```

and the rank-44 even-unimodular obstruction are necessary.  They are not a
classification of level-21 even lattices or their discriminant forms.
Consequently, absence from an unperformed lattice catalog search is not used
as evidence.

## 5. The next obstruction must retain the projector origin

The exact survivor shows that any continuation must use information discarded
by the coordinate-lattice relaxation, such as:

- a primitive embedding in the standard `231`-dimensional lattice;
- generation of the scaled dual by the 231 norm-four columns with Gram
  entries in `{4,1,0,-1,-2}`;
- the tight-frame identity and the exact row distributions at `n3=708`; or
- the fact that `Q` is induced by the specific Schur square `W=M o M`.

A failed search inside any one of these restricted models will not establish
nonexistence without a complete, independently checked certificate.
