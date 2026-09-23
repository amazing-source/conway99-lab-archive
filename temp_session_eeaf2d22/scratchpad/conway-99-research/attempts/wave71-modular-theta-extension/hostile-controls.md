# Wave 71 hostile controls

## Conditional import guard

Wave 71 never treats the Wave 66 candidate as independently verified.  Every
claim is conditional on its lattice, discriminant, frame, and dual-minimum
statements.

## Exact level guard

The index-three neighbor has nonzero elementary 7-primary discriminant, and
so does its scaled dual.  This proves exact level seven for every surviving
row.  The modular theorem is not applied to the original mixed level-63
lattice.

## Theta convention guard

The checker uses
\(\Theta_K=\sum_xq^{\langle x,x\rangle/2}\).  Thus
\(\min K\ge14\) is exactly the vanishing of coefficients \(q^1\) through
\(q^6\), while norms 14, 16, and 18 are coefficients \(q^7,q^8,q^9\).

## Skoruppa-weight guard

The imported weight is not rank/2.  For Smith factors
\(1^{44-s},7^s\), the elementary-divisor sum is
\(e(K)=44+6s\), so the level-one weight is \(22+3s\).  The checker asserts
the eight exact weights before row reduction.

## Coefficient-range guard

All modular computations use exact integer divisor sums reduced modulo
seven.  Coefficients are generated through \(q^{14}\); the strongest
\(q=16\) relation uses only \(q^0,\ldots,q^9\).  No coefficient outside the
generated range is read.

## Basis guard

For each exact level-one weight, every solution of \(4a+6b=w\) is included
as \(E_4^aE_6^b\).  Gaussian elimination is performed over
\(\mathbf F_7\), with inconsistency witnessed by a zero coefficient row
whose augmented entry is nonzero.

## Parity guard

The mod-14 congruence uses only the fixed-point-free involution
\(x\mapsto-x\) on nonzero vectors of a positive-definite lattice.  It does
not assume a graph automorphism.

## Profile-completeness guard

The low-norm enumerator chooses all counts at magnitudes two, three, and
four, then solves exactly for the remaining \(\pm1\) counts from total norm
and coordinate sum.  The regression suite fixes the raw profile counts
\(3,8,8\).  Mathematical eliminations are recorded separately from this
enumeration.

## Status guard

A forced short vector is not called a contradiction.  The norm-14,
norm-16, and norm-18 structural alternatives remain live, and both Conway
status and novelty remain `UNKNOWN`.
