# Wave 30 failed routes and hostile controls

## Routes that do not generalize

1. **`h=729` alone does not split the lattice.**  The Wave 29 proof used
   `K12 orthogonal_sum LAMBDA(F)`.  A determinant and a discriminant form do
   not supply an integral orthogonal decomposition.  The Wave 30 theorem is
   explicitly conditional on such a decomposition and on minimum at least
   four.

2. **An orthogonal rational decomposition is insufficient.**  The support
   argument writes every integral row in integral block coordinates.  A
   rational subspace split can have rows with nonintegral projections and
   does not make `X`, `M`, `W`, `Q`, or `B` split over the lattice.

3. **Dropping minimum four permits mixed rows.**  Two nonzero orthogonal
   components of norm two give a mixed vector of norm four.  Thus the
   shell-support split fails even though the ambient sum is orthogonal.

4. **The exceptional-block logarithmic cap alone leaves six types.**  It
   misses the complement cap for `(rank(A),a)=(20,2)` and the equality
   structure for four more types.

5. **Equality is not merely a numerical coincidence.**  When
   `det(B_R)=3^tr(C_R)`, every inequality in the Wave 24 chain is equality.
   This forces the nonzero eigenvalues of `C_R` to be one and its
   characteristic pseudodeterminant to have absolute value one.  Real
   diagonalizability then gives `C_R^2=C_R`.  Treating equality only as a
   floating-point spectrum would lose the integral image/kernel split.

6. **No contradiction was found in the last rank-20 plus rank-24 type.**
   The complement has `B_U=I`.  The exceptional block has a scalar spectral
   control

   ```text
   spec(C_A) = {2^1,1^6,0^13},
   spec(B_A) = {5^1,3^6,1^13},
   ```

   with the required traces and determinant.  This is not a lattice or frame
   construction, but it proves that the present scalar spectral inequalities
   cannot exclude the last type.

## Countercontrols retained

- Without the multiple-of-six trace residue, the Wave 29 type admits the
  arithmetic trace pair `(28,32)` and its exceptional logarithmic cap is
  `3^8=6561`, above `3645`.
- Before the equality-split veto, five decomposition types pass both block
  logarithmic caps.
- In the last type, the `126` complement rows are forced only to have
  `c_i` in `{9,10,11}` with `sum c_i=1256`.  There are 62 nonnegative
  aggregate multiplicity profiles.  Their existence as count profiles is
  not evidence for a symmetric row-pattern matrix.

## Remaining exact boundary

The current derivation leaves only

```text
S = A_20 orthogonal_sum U_24,
det(A_20)=729,
det(U_24)=1,
min(A_20),min(U_24)>=4,
B_U=I_24.
```

No classification of `U_24`, automorphism assumption, restricted search, or
failed-search inference is used.  General indecomposable and rooted
determinant-729 lattices also remain untreated.
