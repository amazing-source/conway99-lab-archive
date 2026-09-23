# Wave 80 hostile controls

## Domain quotient

The domain is \(L^*/7L^*\), which has dimension 44.  Replacing it by
\(L^*/L\) would erase the \(r\)-dimensional radical and incorrectly make
the code dimension \(q\).

## Spanning guard

The tight-frame identity does not by itself prove that evaluation is
injective.  The proof uses
\[
3M\subseteq\langle v_i\rangle,\qquad L=M+\mathbf Zv_0,
\]
so the quotient by the marked-vector span is 3-primary and the vectors span
after reduction modulo seven.

## Form scale

The finite form is
\[
\beta(y,z)=7\langle y,z\rangle\pmod7,
\]
not the reduction of \(\langle y,z\rangle\), which need not be integral.
The code dot product is \(2\beta\), because the frame scalar is 63 and
\(63\langle y,z\rangle=9(7\langle y,z\rangle)\).

## Hull direction

The radical preimage is \(L/7L^*\).  Its image is the row space of the
marked Gram matrix, which is \(-S\) modulo seven.  Therefore the Seidel row
space equals the hull; it is not merely a subcode of an unknown hull.

## Orthogonal-type sign

Wave 66's seven-primary Gauss sign is translated into the determinant square
class of \(C/R\).  Multiplication of the form by two does not change the
determinant class because \(q\) is even.  The resulting determinant is the
opposite of the split \(q\)-dimensional class for every surviving row, so
the quotient is consistently minus type.

## Dual-distance exhaustion

For support at most four, all off-diagonal sign patterns are enumerated, not
only graph isomorphism representatives.  For support five:

1. all \(2^{10}\) labelled graphs are opened;
2. only necessary induced \(\lambda=1,\mu=2\) bounds are used;
3. every full-support projective kernel vector is enumerated;
4. every one of its \(2^5\) possible outside incidence patterns is tested.

The conclusion \(d(C^\perp)\ge6\) is a complete finite theorem conditional
on the graph.  A locally admissible singular support-six positive control
with compatible one-vertex outside patterns prevents silently promoting the
same argument to weight six.

## Short-vector reduction

The reduction from lattice vectors to codewords uses Wave 71's proved
\(\{0,\pm1\}\) profiles only at norms 14, 16, and 18.  Injectivity modulo
seven is asserted only for these bounded profiles.  Scalar closure adds six
codewords per projective line, but only two of them need lift to short
lattice vectors.

## MacWilliams status

Strict slack in the first five orthogonal-array moments shows only that the
mandatory lower-count data do not immediately overfill those equations.  It
is not a nonnegative integral weight enumerator and is not evidence of code
existence.

## Status

The non-split quotient represents all three required self-dot values.  No
rank row is deleted.  Conway-99 and novelty remain `UNKNOWN`.
