# Wave163 draft: compressed coupled conic dual

Status: `DRAFT_UNEXECUTED`.

This package was prepared while an unrelated process left host free memory
below the user-mandated 15 percent floor.  No rank computation, optimizer, or
certificate recovery has been run.  Nothing here is `VERIFIED`, and there is
no run report or manifest yet.

## Objective

Replace the unsuccessful scalar cutting-plane loop by a genuinely
whole-block dual search for the persistent root-mask-3 and root-mask-12
four-root covariance matrices.

Let `B_3(x)` and `B_12(x)` denote the exact affine covariance pencils on the
full endpoint count vector

```text
x = (1, x7[208], x8[916]).
```

The stored directions give small rational subspaces:

```text
U3:  at most 6 columns  -> Y3 in S_+^6
U12: at most 8 columns -> Y12 in S_+^8.
```

Search for multipliers

```text
Z3  = U3  Y3  U3^T,
Z12 = U12 Y12 U12^T,
```

so the unknown symmetric matrices `Y3,Y12` have only
`6*7/2 + 8*9/2 = 57` scalar coordinates.  Off-diagonal entries of `Y`
retain cross-direction matrix information that no nonnegative combination
of the previous rank-one cuts can see.

## Critical scope correction

The exact pseudowitness reconstructions fixed `x7` and imposed the pair-root
zero face.  Those conditions are useful diagnostic slices, but they are not
universal graph identities.  A target-level conic certificate must work
against the full `x7+x8` affine system and may use only independently proved
equalities.

The first exact replay will therefore keep separate:

1. the universal endpoint affine rows (Wave44, deletion, and marked rows);
2. optional conditional rows defining the fixed-`x7`/pair-root-zero slice.

A certificate found only in the second system is conditional and cannot
exclude `n3=4158`.

## Memory-gated continuation

Once free host memory is safely above 18 percent:

1. reconstruct the exact compressed pencil rows;
2. compute their quotient rank modulo the universal affine row space;
3. recover every exact rational quotient kernel;
4. test whether any kernel contains nonzero PSD `Y3,Y12`;
5. separately solve the conic/Farkas problem that also permits nonnegative
   count slacks;
6. replay any candidate identity coefficient-by-coefficient with rational
   arithmetic.

Until those steps and an independent verifier are complete, Conway-99, the
endpoint, and a strict upper bound remain `UNKNOWN`.

