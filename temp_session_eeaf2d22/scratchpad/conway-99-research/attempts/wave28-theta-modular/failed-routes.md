# Wave 28 theta/modular failures and scope walls

## Strongly 21-modular or Fricke-eigenform shortcut

Refuted for every endpoint determinant.  If a rank-44 lattice of exact level
`N` were isometric to its `N`-scaled dual, determinants would force

```text
det(S)=N^22.
```

None of the eight endpoint determinants has this value.  In particular,
`21S^-1` being even integral does not supply a Fricke eigenvalue, a partial
dual isometry, or any strongly-modular extremal bound.

## Treating `G=21S^-1` as the natural Fricke partner in every row

Invalid.  The exact levels are 3, 7, and 21.  At levels 3 and 7 the natural
partner has Gram `N S^-1`, while

```text
G=(21/N)(N S^-1).
```

The gap in `theta_G` is then partly the automatic result of rescaling by
seven or three.  It is not a rootlessness statement about the natural
Fricke partner.

## Root coefficient from determinant or discriminant data

Refuted twice.

- At `h=9`, `E8^5 orthogonal_sum A2^2` and
  `E8^4 orthogonal_sum E6^2` have isometric discriminant forms but root
  counts 1212 and 1104.
- At `h=729`, the exact candidate
  `K12 orthogonal_sum LAMBDA(F)` is rootless, while
  `E6^6 orthogonal_sum E8` has 672 roots.  The two discriminant quadratic
  forms are isometric six-dimensional forms over `F_3`.

Thus even the Weil representation does not select the zero-component
root coefficient.

## Ordinary harmonic theta series for the cubic frame moment

Blocked by antipodal cancellation.  For every odd homogeneous polynomial
`P`, the full zero-coset lattice sum pairs `v` with `-v` and has

```text
P(v)+P(-v)=0.
```

The endpoint cubic tensor uses a selected orientation of 231 norm-four
pairs, so its squared norm 60 is invisible to the ordinary odd harmonic
theta series.

## Norm-four coefficient alone

The frame implies only the scalar necessary bound `r_S(4)>=462`.  Every
one of the 17 orthogonal-ADE bare-lattice controls exceeds it, and the
rootless `h=729` control has `r_S(4)=147636`.  This count does not encode
the pairwise Gram alphabet, tight second moment, orientation, or cubic
moment, so no endpoint conclusion follows.

## Partial-dual cusp attack

Not completed.  The determinant list gives the orders of the 3- and
7-primary discriminant groups but, in mixed rows, not both local quadratic
signs or the leading terms of the partial-dual coset theta series.  No
vanishing order was assigned at the `1/3` or `1/7` cusp.

## Timed exploratory inverse enumeration

An exploratory exact reverse-LDL enumeration attempted the norm-2 balls of
`3 K12^-1` and `LAMBDA(F)^-1` in their displayed inverse coordinate bases.
It exceeded the 60-second cutoff and produced no result.  Nothing in the
report depends on that run.  The safe bound for `21S^-1` uses only its
checked even integrality: every nonzero norm is at least two, and the
additional odd scaling gives minimum at least 14.

## Full endpoint origin

No candidate in this lane supplies `X`, `M`, `Q`, `B`, the 231-row Gram
alphabet, a Schur-square certificate, or a graph.  The hostile controls
demonstrate only that bare lattice/theta premises do not contradict the
eight determinant rows.
