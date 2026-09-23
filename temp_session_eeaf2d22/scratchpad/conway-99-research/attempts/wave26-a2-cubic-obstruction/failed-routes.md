# Wave 26 retained failed and bounded routes

## 1. The obstruction does not reject the index `h=9`

The proof uses the two explicit orthogonal `A2` summands and the corresponding
`Q_AA=A2` blocks in the Wave 24 hostile-control package.  It does not classify
all even rank-44 determinant-nine lattices or all compatible `Q` forms.
Therefore it rejects the omitted Schur origin of that one package, not the
index value.

## 2. The two `A2` summands alone do not contradict global trace 60

Each `A2` summand forces a pure-cubic compression trace of at least 18, for a
combined floor of 36.  A general `Q` could allocate at least 36 of the total
trace 60 to those two summands.  The explicit package instead allocates only
10 to each, which is why it fails.  The general floor is not by itself an
endpoint contradiction.

## 3. No `E8` tensor-lattice minimum is imported

Odd second-moment parity forces the pure cubic on each `E8` block to be
nonzero modulo two.  A tempting continuation is to lower-bound its Euclidean
tensor norm and add five such bounds to the two `A2` floors.  This report does
not import or prove a minimum theorem for `E8 tensor E8 tensor E8`; no bound
from this route is used.

## 4. No failed search is nonexistence evidence

The exact checker enumerates only the six `A2` roots and the finite signed
line imbalances forced by their exact count seven.  It does not search
231-column frames, primitive embeddings, graphs, or all determinant/index
survivors.  Absence of any such object is not asserted.

## 5. Active hostile controls

- Replacing scale 21 by a hypothetical scale 18 gives six occurrences on
  each root line, permits balanced signs, and removes the cubic floor.
- Replacing the explicit `Q_AA=A2` block by `2A2` raises the compression trace
  from 10 to 20 and removes the trace contradiction.
- Replacing `A2` by the diagonal even Gram matrix `2I` introduces norm-four
  component vectors, so the three-root-line classification no longer applies.
- Moving two ordered entries between the `-1` and zero bins is detected by
  the exact moment checks.

These controls show which premises are active.  They are not candidate
Conway objects.
