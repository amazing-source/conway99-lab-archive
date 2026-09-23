# Wave152 independent derivation

## Flag semantics

Fix one of the nine locally admissible unlabeled graphs on four vertices and
place its chosen canonical adjacency matrix on pointwise-fixed labels
\(0,1,2,3\). A flag adds vertices \(4,5\). The roots cannot be permuted;
only the swap \(4\leftrightarrow5\) is quotiented out, so the free pair is
unordered.

A labeled graph is retained when every adjacent pair has at most
\(\lambda=1\) common neighbors and every nonadjacent pair has at most
\(\mu=2\) common neighbors. These are necessary induced-subgraph conditions
for a hypothetical \(\operatorname{srg}(99,14,1,2)\).

Enumerating the nine extension bits—eight root-to-free incidences and the
free-pair edge—and quotienting only by the free swap gives:

| Root mask | Flag count |
|---:|---:|
| 0 | 224 |
| 1 | 201 |
| 3 | 155 |
| 7 | 99 |
| 11 | 69 |
| 12 | 178 |
| 13 | 125 |
| 15 | 60 |
| 30 | 70 |

The complete flag lists are stored in `independent-results.json`, together
with a SHA-256 for each list.

## Independent reconstruction of \(x_6\)

The verifier reads only the Wave150 stored \(x_7,x_8\) supports. It does not
call the discovery code or its model loader. Lower counts are reconstructed
by the exact deletion identity

\[
(99-r+1)x_{r-1}(H)
=\sum_G d_H(G)x_r(G),
\]

where \(d_H(G)\) is the number of single-vertex deletions of \(G\) whose
unlabeled canonical class is \(H\). Applying this for
\(7\to6\to5\to4\) yields support sizes

\[
|x_4|=9,\quad |x_5|=21,\quad |x_6|=61.
\]

All resulting values are integers and have the correct totals
\(\binom{99}{r}\). The exact reconstructed \(x_6\) record has canonical
SHA-256
`f6c8adc240488d97b77bd92d136d0d79ecff0ddb7f6db693352563829d53b40a`.

## First and second moments

For a fixed pointwise root embedding, let \(F\) range over unordered pairs
from the other 95 vertices. Let \(s_i\) count pairs producing flag \(i\), and
let \(M_{ij}\) count ordered pairs \((F_1,F_2)\) producing flags \(i,j\).
The union of the roots and two free pairs has:

- order 6 when \(F_1=F_2\);
- order 7 when the pairs share exactly one vertex;
- order 8 when the pairs are disjoint.

Thus the stored \(x_6,x_7,x_8\) counts determine every entry of \(s\) and
\(M\). Independent enumeration gives:

| Union order | Nonzero classes | Matched root embeddings | Emitted products |
|---:|---:|---:|---:|
| 6 | 61 | 5,028 | 5,028 |
| 7 | 204 | 38,576 | 231,456 |
| 8 | 874 | 333,278 | 1,999,668 |

If \(R\) is the number of pointwise root embeddings, the totals check
exactly:

\[
\sum_i s_i=R\binom{95}{2},\qquad
\sum_{i,j}M_{ij}=R\binom{95}{2}^2.
\]

## Integer scaling

Wave150 \(x_8\) coordinates have denominators dividing four. The verifier
therefore accumulates

\[
s^{(4)}=4s,\qquad M^{(4)}=4M.
\]

The exact integer matrix checked is

\[
B=R M^{(4)}-\frac{s^{(4)}(s^{(4)})^\mathsf T}{4}
 =4(RM-ss^\mathsf T).
\]

All products in the division by four are checked for divisibility, and every
block is checked for symmetry. Multiplying by the positive scalar four does
not change positive semidefiniteness.

## Exact negative certificates

A real symmetric positive-semidefinite matrix must satisfy
\(v^\mathsf T Bv\ge0\) for every real vector \(v\). The verifier reconstructs
the full matrices and evaluates the sealed sparse integer vectors exactly.

| Root mask | Dimension | Support | Exact \(v^\mathsf T Bv\) |
|---:|---:|---:|---:|
| 3 | 155 | 24 | \(-2293145527521819747490560\) |
| 12 | 178 | 88 | \(-8605517548253993047296\) |

Both values are strictly negative. Each certificate therefore proves that
its corresponding matrix \(4(RM-ss^\mathsf T)\) is not positive
semidefinite. The flag at every support index is checked against the
independently rebuilt universe. Changing the first vector coordinate changes
the exact quadratic value, and changing a flag-mask association is rejected.

The blocks for root masks 15 and 30 are independently found to be identically
zero, hence exactly PSD. The remaining five blocks have no exact sign
certificate here and remain `UNKNOWN`; a small numerical eigenvalue is not
used as proof.

## Scope

These two exact negative directions refute the single Wave150
`x6/x7/x8` count pseudowitness. They do not show that every count vector at
\(n_3=4158\) violates a four-root block. Consequently endpoint feasibility,
Conway-99, and every strict upper bound remain `UNKNOWN`.
