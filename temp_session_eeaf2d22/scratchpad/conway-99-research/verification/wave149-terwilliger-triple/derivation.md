# Independent derivation

## Scope and status

This is a clean-room verification of one local projection for a hypothetical
strongly regular graph with parameters
\(\operatorname{srg}(99,14,1,2)\). It verifies the triangle-root partition,
the matching-composition formula for rooted triangular prisms, and the exact
positive-semidefinite character certificate for one explicit prism-free
matching witness. It does **not** construct a graph or an incidence matrix.

## Triangle-root partition

Fix a triangle \(T=\{t_0,t_1,t_2\}\). An outside vertex cannot meet two
vertices of \(T\): if it met \(t_i,t_j\), then the adjacent pair
\(t_i,t_j\) would have both the third root vertex and the outside vertex as
common neighbors, contradicting \(\lambda=1\).

Let \(A_i\) contain vertices adjacent to \(t_i\) and to no other root, and let
\(B\) contain vertices adjacent to none of \(T\). Each root has its two
triangle neighbors plus 12 other neighbors, so

\[
|A_0|=|A_1|=|A_2|=12,\qquad |B|=99-3-36=60.
\]

For \(x\in A_i\):

- the adjacent pair \(x,t_i\) has one common neighbor, so \(x\) has one
  neighbor inside \(A_i\);
- for \(j\ne i\), the nonadjacent pair \(x,t_j\) already has \(t_i\) as one
  common neighbor and therefore has exactly one additional common neighbor in
  \(A_j\);
- its remaining \(14-1-1-1-1=10\) neighbors lie in \(B\).

Thus each \(A_i\) induces a perfect matching \(M_i\), and each bipartite graph
between \(A_i,A_j\) is a perfect matching \(F_{ij}\).

For \(b\in B\), each nonadjacent pair \(b,t_i\) has exactly two common
neighbors, both in \(A_i\). Hence \(b\) has six neighbors in the three
fibres and eight inside \(B\). The incidence count is consistent:
\(12\cdot10=60\cdot2=120\) for each fibre.

## Prism trace

A transversal triangle selects
\(x_0\in A_0,x_1\in A_1,x_2\in A_2\) with all three cross-matching edges.
Together with the root triangle and the three root-to-fibre edges, this is a
triangular prism. Starting from \(x_0\), the cross matchings return to \(x_0\)
exactly when it is a fixed point of the matching composition. With permutation
matrices in the chosen row convention, the count is

\[
\operatorname{tr}(F_{01}F_{12}F_{20}).
\]

Take \(M_i=M\), where \(M=(0\,1)(2\,3)\cdots(10\,11)\), take
\(F_{01}=F_{02}=I\), and take
\(F_{12}=P:x\mapsto x+6\pmod {12}\). Then \(P\) is a fixed-point-free
involution commuting with \(M\), and the matching composition is \(P\).
Consequently the rooted-prism count is zero.

## Forced Gram projection

If \(C_i\) were the \(12\times60\) binary incidence matrix from \(A_i\) to
\(B\), the strongly regular common-neighbor equations force

\[
C_iC_i^\mathsf{T}=9I-M_i+J
\]

and, for distinct \(i,j,k\),

\[
C_iC_j^\mathsf{T}
=2J-F_{ij}-M_iF_{ij}-F_{ij}M_j-F_{ik}F_{kj}.
\]

For the witness above, the diagonal block is \(9I-M+J\), the 01 and 02
blocks are \(2J-I-2M-P\), and the 12 block is
\(2J-I-P-2MP\). Direct integer construction gives a symmetric \(36\times36\)
matrix with:

- diagonal 10;
- row sums 60;
- off-diagonal entries in \(\{0,1,2\}\);
- canonical matrix SHA-256
  `1cfd0442e69b621c4a82fbeddeec9e7afbfcd04cd8eb458e29170cfd345c7ffc`.

## Exact positive-semidefinite certificate

The commuting involutions \(M,P\) generate three regular orbits of the Klein
four-group on the 12 coordinates. Every joint character
\((m,p)\in\{\pm1\}^2\) therefore has multiplicity three. On the
\((m,p)=(1,1)\) space, the all-ones matrix \(J\) has eigenvalue 12 on the
all-ones line and zero on the other two lines.

For a joint eigenvector with eigenvalues \(m,p,j\), the full Gram matrix
reduces to

\[
\begin{pmatrix}
d&a&a\\
a&d&b\\
a&b&d
\end{pmatrix},
\quad
d=9-m+j,\quad
a=2j-1-2m-p,\quad
b=2j-1-p-2mp.
\]

The five character cases give the exact full spectrum

\[
0^4,\quad 6^9,\quad 10^9,\quad 12^{13},\quad 60^1.
\]

Every eigenvalue is nonnegative, so the matrix is positive semidefinite. Its
rank is \(9+9+13+1=32\), independently reproduced by exact rational row
reduction. In particular, rank at most 60 does not obstruct a hypothetical
\(36\times60\) factor.

## Evidence boundary

Positive semidefiniteness and rank are only necessary conditions for a real
Gram factor. They do not supply the required binary \(36\times60\) incidence
matrix with column sums two, and they say nothing about a compatible
8-regular graph on \(B\) or compatibility across other root triangles.
Therefore this witness refutes only the proposed *first projection* as a
route to forcing a prism. The graph-realization question, the Conway-99
target, and every strict bound remain `UNKNOWN`.
