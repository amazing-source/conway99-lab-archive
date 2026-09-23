# Wave 136 independent verification report

## Verdict

`PASS_WITH_SCOPE_CORRECTION`

The Arf/Gauss diagnostic and the proposed additive-\(\mathbf F_4\)
graph-state identities pass independent exact reconstruction.  The sealed
Wave 131 rational formal enumerator is refuted by the Arf magnitude
condition.  The graph-state self-duality, 5,050/2,550/2,500 state counts,
MacWilliams transform, binary-axis coupling, and all nine
support-at-most-three coefficient rows are correct.

One scope correction is required.  The mixed graph-state rows are a new
constraint layer relative to the scalar Wave 134 model, but no formal
algebraic-independence certificate proves that they are independent of
*every possible consequence* of all Wave 134 constraints.  That stronger
claim is `UNKNOWN_NOT_PROVED`.  External literature novelty is also
`UNKNOWN`.

No result constructs an additive code without first supplying the
hypothetical adjacency matrix, constructs or excludes that matrix, or
changes Conway-99 from `UNKNOWN`.

## Clean-room order

The verifier first froze the following derivation in
`independent-freeze.md`, before reading the Wave 136 discovery code or
results:

1. \(A^2=A\) over \(\mathbf F_2\);
2. the previously verified \(\operatorname{rank}_{\mathbf F_2}A=54\);
3. the nondegenerate quadratic form
   \(q(u)=\operatorname{wt}(u)/2\bmod2\) on
   \(R=\operatorname{im}(A)\);
4. the two possible Gauss sums \(\pm2^{27}\);
5. the explicit pair convention
   \(I=00,X=10,Z=01,Y=11\);
6. the complete four-symbol character matrix; and
7. the rule that no enumerator witness is a code or graph.

Only then were the discovery memo and diagnostic inspected.

## Arf/Gauss reconstruction

Let

\[
H=\{x\in\mathbf F_2^{99}:\operatorname{wt}(x)\text{ is even}\}.
\]

Because the length is odd, the dot product on \(H\) is nondegenerate and
alternating.  The imported exact binary rank gives
\(\dim R=54\), while

\[
E=\ker(A)\cap H
\]

has dimension \(44\).  The adjacency identity makes \(R\) nondegenerate,
so

\[
H=R\mathbin{\perp}E.
\]

For even words,

\[
q(x+y)=q(x)+q(y)+x\cdot y.
\]

The elementary finite-field Gauss theorem therefore gives

\[
G_R=\pm2^{27},\qquad G_E=\mp2^{22}.
\]

Independently,

\[
G_H=\sum_{w\ {\rm even}}(-1)^{w/2}\binom{99}{w}
    =\operatorname{Re}(1+i)^{99}
    =-2^{49},
\]

which fixes the opposite sign coupling but not the Arf sign.

The verifier rebuilt all binary Krawtchouk coefficients from their defining
binomial sum.  The sealed Wave 131 witness passes all 100 forward and all
100 inverse ordinary MacWilliams equations.  Its exact sums are

\[
G_R=
\frac{
246964934998081883385269739380937552159104000
}{
452929323301482718880047428141
},
\]

\[
G_E=
-\frac{
7717654218690058855789679355654298504972000
}{
452929323301482718880047428141
}
=-\frac{G_R}{32}.
\]

Thus ordinary MacWilliams fixes the ratio on this even-dual projection,
but the witness has \(|G_R|\ne2^{27}\).  The Wave 131 rational point is
therefore exactly refuted as a candidate for this quadratic code
structure.  It was only a formal rational enumerator, so no code or graph
is refuted.

## Additive \(\mathbf F_4\) graph-state reconstruction

With pair notation \((x,z)\), use the trace-Hermitian/symplectic form

\[
\langle(x,z),(y,t)\rangle=x\cdot t+z\cdot y.
\]

For

\[
S_A=\{(x,Ax):x\in\mathbf F_2^{99}\},
\]

symmetry of \(A\) gives

\[
\langle(x,Ax),(y,Ay)\rangle
=x\cdot Ay+Ax\cdot y=0.
\]

The first component makes the map injective, so \(|S_A|=2^{99}\).
An isotropic additive code of this size in the \(2^{198}\)-element
symplectic ambient space is self-dual.  This proves additive
self-duality; it does not assert \(\mathbf F_4\)-linearity.

In state order \(I,X,Z,Y\), direct character evaluation gives

\[
H_4=
\begin{pmatrix}
1&1&1&1\\
1&1&-1&-1\\
1&-1&1&-1\\
1&-1&-1&1
\end{pmatrix}.
\]

After identifying the \(X\) and \(Z\) variables, the enumerator
\(P(u,v,w)\), ordered as \(I,Y,(X+Z)\), obeys

\[
P(u,v,w)=2^{-99}
P(u+v+2w,\ u+v-2w,\ u-v).
\]

Reordering variables as \((x,y,z)=(u,w,v)\) gives

\[
(x,y,z)\longmapsto
(x+2y+z,\ x-z,\ x-2y+z),
\]

exactly the Wave 134 three-variable transform.  This is transform
equivalence, not object equivalence: the code types and forced
coefficients differ.

For every binary \(x\),

\[
n_Y=|\operatorname{supp}(x)\cap\operatorname{supp}(Ax)|
    =x^TAx=0\pmod2
\]

because \(A\) is alternating.  There are
\(\binom{101}{2}=5050\) raw triples \((n_I,n_Y,n_R)\), of which 2,550
have even \(n_Y\); the remaining 2,500 coefficient rows are forced to
zero.

As a computational control, every simple graph through order four was
enumerated: 75 graphs, 16,932 ordered isotropy checks, 16,932 orthogonal
candidate checks, and 300 exact transform evaluations.  Every graph code
was self-dual and every transform check passed.  The order-three triangle,
whose adjacency matrix is idempotent over \(\mathbf F_2\), independently
confirmed the pure-\(Y\)/image and pure-\(X\)/kernel axes.

## Support-at-most-three rows

For \(T=\operatorname{supp}(x)\), the graph word has support

\[
T\cup\operatorname{Odd}(T).
\]

For a three-set, let \(p\) be the number of vertices of \(T\) having
internal degree two, \(c\) the number of outside vertices adjacent to all
three, and \(n_Y\) the number of vertices of odd internal degree.  Counting
outside vertices by their number of neighbors in \(T\) gives

\[
n_R=33+2p+4c-n_Y.
\]

The local graph on a vertex neighborhood is \(7K_2\).  It independently
gives 27,720 independent triples with \(c=1\) and 8,316 one-edge triples
with \(c=1\); the remaining census follows from the SRG parameters.
The exact reconstructed lower table is:

| input | count | \(n_I\) | \(n_Y\) | \(n_R\) |
|---|---:|---:|---:|---:|
| one vertex | 99 | 84 | 0 | 15 |
| edge | 693 | 73 | 2 | 24 |
| nonedge | 4,158 | 73 | 0 | 26 |
| independent, \(c=0\) | 70,686 | 66 | 0 | 33 |
| independent, \(c=1\) | 27,720 | 62 | 0 | 37 |
| one edge, \(c=0\) | 41,580 | 66 | 2 | 31 |
| one edge, \(c=1\) | 8,316 | 62 | 2 | 35 |
| induced path | 8,316 | 64 | 2 | 33 |
| triangle | 231 | 60 | 0 | 39 |

The three-set rows sum to \(\binom{99}{3}=156,849\), and the one- and
two-set rows close their respective censuses.  The input \(x\) is the
first graph-code component, so distinct input sets cannot collide.  These
are therefore graph-forced coefficient lower bounds.

## Vetoes and scope walls

1. **No fixed Arf sign.**  The derivation forces two branches.  Selecting
   one sign needs a new premise.
2. **No formal-independence inflation.**  The graph-state coefficients are
   not variables in the scalar Wave 134 relaxation and thus form a new
   modeled layer.  A stronger assertion that they are algebraically
   independent of every Wave 134 consequence is not certified here.
3. **No external novelty claim.**  This verifier performed no exhaustive
   priority audit.
4. **No realization claim.**  A rational point would be only a formal
   enumerator.  Exact infeasibility would require a replayable Farkas
   certificate.
5. **No shadow layer promoted.**  The proposed quantum-shadow inequalities
   were not needed for these checks and remain outside this verified base
   package until their convention and normalization are independently
   sealed.

The appropriate next step is the discovery memo's two exact Arf-branch
solves, followed by an exact rational solve of the 5,050-state graph-state
base system.  Until a terminal certificate is independently replayed,
Conway-99 remains `UNKNOWN`.
