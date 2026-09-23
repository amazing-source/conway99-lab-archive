# Wave 80 verifier audit: characteristic-seven evaluation code

Date: 2026-07-27

Verdict: `VERIFIED` within the exact conditional scope below.

No mathematical correction to the sealed Wave 80 discovery was required.
This is not a graph construction, an endpoint exclusion, or a resolution of
Conway-99.

## Scope and evidence boundary

Assume:

1. a hypothetical `srg(99,14,1,2)`;
2. the independently verified Wave 66 rank-44 marked lattice conclusions;
3. the independently verified Wave 71 level-seven neighbor and short-vector
   dictionary.

Under those assumptions, independently verify the evaluation code

\[
C=\{(\langle y,v_i\rangle\bmod 7)_{i=0}^{98}:y\in L^*/7L^*\}
\subseteq\mathbb F_7^{99},
\]

its hull and finite orthogonal geometry, its dual distance through support
five, and the images of the Wave 71 norm-14, norm-16, and norm-18 vectors.

The discovery inventory was frozen before derivation inspection. The sealed
discovery manifest has SHA-256

```text
51d3e709308851ba9c9c63a8897dec4c761ce11e5126633e0cdf67f6e470cba7
```

and all ten paths listed in it replay with zero mismatches. Runtime
`__pycache__` files are not part of that seal, but their preinspection bytes
are retained in `discovery-inventory-preinspection.tsv`.

## Evaluation is injective

Let \(N\) be the integer span of the 99 marked vectors \(v_i=3u_i\).
The imported lattice construction gives

\[
3M\subseteq N,\qquad v_0\in N,\qquad L=M+\mathbb Z v_0.
\]

Therefore \(3L\subseteq N\), so \(L/N\) is killed by three. Since
\(7\ell-\ell=6\ell\in N\), every class modulo \(N\) is represented by a
seven-fold multiple:

\[
N+7L=L.
\]

Thus the \(v_i\) span \(L/7L\). If every coordinate of \(\Phi(y)\) is zero,
then \(\langle y,N\rangle\subseteq7\mathbb Z\). Pairing with
\(L=N+7L\) shows \(\langle y,L\rangle\subseteq7\mathbb Z\), hence
\(y/7\in L^*\) and \(y\in7L^*\). Consequently

\[
\Phi\text{ is injective},\qquad C\text{ is a }[99,44]_7\text{ code}.
\]

The exact relation \(\sum_i v_i=0\) also gives \(C\subseteq\mathbf1^\perp\).

## Dot form, radical, and hull

On \(L^*/7L^*\), put

\[
\beta(\bar y,\bar z)=7\langle y,z\rangle\bmod7.
\]

The inclusion \(7L^*\subseteq L\) makes this form integral and well defined.
Its radical is exactly \(L/7L^*\): vanishing against every \(z\in L^*\)
is equivalent to \(\langle y,L^*\rangle\subseteq\mathbb Z\), hence
\(y\in(L^*)^*=L\).

The frame identity gives, independently,

\[
\Phi(y)\cdot\Phi(z)
=63\langle y,z\rangle
=9\beta(\bar y,\bar z)
=2\beta(\bar y,\bar z)\pmod7.
\]

Since \([L^*:7L^*]=7^{44}\) and \([L^*:L]=7^q\), the radical has
dimension \(44-q=r\).

The marked Gram entries are \(28,-8,1\) on the diagonal, edges, and
nonedges. Modulo seven these are \(0,6,1\), exactly the entries of \(-S\)
for \(S=2A-J+I\). The marked vectors span the radical preimage, so their
evaluation rows span its image. Therefore

\[
\boxed{C\cap C^\perp=\operatorname{row}_{\mathbb F_7}(S)}
\]

and the hull dimension is exactly \(r\), not merely at least \(r\).

## Orthogonal-space types

Write \(R=\operatorname{row}_{\mathbb F_7}(S)\). The exact SRG spectrum gives
\(S^2=49(I+J)\), hence \(S^2=0\) over \(\mathbb F_7\). Thus \(R\) is totally
isotropic. The nondegenerate quotient

\[
W=R^\perp/R
\]

has dimension \(99-2r=11+2q\). The all-one vector lies in \(R^\perp\),
has norm \(99=1\pmod7\), is not in \(R\), and is orthogonal to \(C\).
Removing that norm-one line gives a nondegenerate space \(W_0\) of dimension
\(10+2q\).

The quotient \(C/R\) is \(L^*/L\) with the code form \(2\beta\). Wave 66's
verified Milgram calculation fixes its determinant Legendre sign as

\[
\delta=(-1)^{q/2+1}.
\]

Scaling by two does not alter the square class (indeed \(2=3^2\) in
\(\mathbb F_7\)). An even \(2m\)-space is split exactly when its determinant
class is \((-1)^m\). The imported sign is the opposite class for all eight
surviving even values of \(q\), so

\[
C/R\cong O^-(q,7),\qquad\text{Witt index }q/2-1.
\]

Extending the even-dimensional \(R\) to \(r\) hyperbolic planes inside the
standard \(99\)-space shows that \(W\), and then \(W_0\), has square
determinant. Since \(-1\) is nonsquare in \(\mathbb F_7\) and
\(\dim(W_0)/2=5+q\) is odd, \(W_0\) is minus type. Determinant multiplication
then makes the complement of \(C/R\) inside \(W_0\) split:

\[
W_0\cong O^-(10+2q,7),\qquad
(C/R)^\perp_{W_0}\cong O^+(10+q,7).
\]

At the endpoint \(r=28,q=16\), this is exactly

```text
C                 [99,44]_7 with hull dimension 28
C/R               O^-(16,7), Witt index 7
W0                O^-(42,7), Witt index 20
(C/R)^perp in W0  O^+(26,7), Witt index 13
```

## Complete support-five dual exclusion

Because \(R\subseteq C\), one has \(C^\perp\subseteq R^\perp\). Symmetry of
\(S\) identifies \(R^\perp=\ker S\).

For a nonzero kernel word with support \(I\), its nonzero coordinates must
give a full-support kernel vector of the principal block \(S[I,I]\). A
weight-one word is impossible because every off-diagonal Seidel entry is
nonzero. Independent enumeration gives the following nonzero determinant
residues for every labelled block:

```text
|I|=2: {6}
|I|=3: {2,5}
|I|=4: {4,5}
```

At size five, the verifier independently enumerates all \(2^{10}=1024\)
labelled induced graphs. Exactly 683 obey the necessary internal
\(\lambda=1,\mu=2\) common-neighbor caps. Among them, 132 labelled graphs
have a full-support projective kernel relation; they form three isomorphism
types with orbit sizes 60, 60, and 12.

For an outside vertex with incidence vector \(p\in\{0,1\}^5\), the missing
coordinate equation is

\[
2\sum_{i\in I}p_i x_i=\sum_{i\in I}x_i\pmod7.
\]

Every projective relation was tested against all 32 patterns. None admits a
compatible pattern. Since a five-set has 94 outside vertices, no support-five
kernel word exists. Therefore

\[
\boxed{d(R^\perp)\ge6,\qquad d(C^\perp)\ge6.}
\]

For a linear code, dual distance at least six is equivalent to every
projection onto at most five coordinates being uniformly surjective.
Accordingly, \(C\) is an orthogonal array of strength five.

The verifier separately searched for, and found, a locally admissible
support-six principal relation with compatible outside patterns. This
positive control proves that the same local argument does not silently
exclude weight six.

## Wave 71 short-vector images

Wave 71 gives, through norm 18, integer vectors

\[
t\in\{0,\pm1\}^{99},\qquad \sum_i t_i=0,\qquad At=-4t,
\]

with equally many \(+1\) and \(-1\) entries and squared coordinate norm
14, 16, or 18. For \(z=\sqrt7\,y\in K\),

\[
\Phi(y)_i=\langle y,3u_i\rangle=3t_i\pmod7.
\]

Direct symbol counting and the frame identity agree:

| norm | code weight | symbols \(3,4\) | self-dot mod 7 | class in \(C/R\) |
|---:|---:|---:|---:|---|
| 14 | 14 | \(7,7\) | 0 | zero or nonzero isotropic |
| 16 | 16 | \(8,8\) | 4 | anisotropic |
| 18 | 18 | \(9,9\) | 1 | anisotropic |

The bounded alphabet makes reduction injective on these profiles. Only
scalars \(+1\) and \(-1\) preserve \(\{0,3,4\}\), so the Wave 71 count
congruence yields a projective-line count \(P\equiv1\pmod7\) and a
scalar-closed codeword count \(6P\equiv6\pmod{42}\).

Minus-type \(16\)-space represents zero and all nonzero field values, so the
orthogonal type excludes none of the three norm alternatives.

## Replay and status

The independent suite passes 10/10 tests. The sealed discovery suite passes
8/8 tests. Ten selected mathematical fields in `comparison.json` agree
exactly, including the endpoint types, support-five counts, hull identity,
short weights, and self-dots.

The low-degree orthogonal-array moments retain strict positive slack after
including the 594 forced weight-98 Seidel scalar multiples and one forced
short projective line. This is only a null control: it is not a complete
nonnegative integral MacWilliams enumerator.

Final status:

```text
Wave 80 conditional theorem: VERIFIED
rank-28 endpoint excluded:    no
code constructed:             no
graph or lattice constructed: no
Conway-99:                    UNKNOWN
literature novelty:           UNKNOWN
```
