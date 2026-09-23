# Exact labelled norm-16 incidence reduction

Claim label: `DERIVED`, conditional on the frozen Wave 81 protocol.

Write `B` for the `8 x 8` bipartite adjacency matrix from `P` to `N`.
Every row and column has sum four. Two vertices on the same sign side are
nonadjacent in the hypothetical strongly regular graph, so their full
common-neighbor allowance is `mu=2`. Hence every pair of rows and every
pair of columns of `B` has codegree at most two.

## 1. Complete support census

The exact enumerator fixes one row as `00001111`, sorts the remaining rows,
and exhausts all distinct weight-four rows subject to:

- column sums equal four;
- row-pair codegrees are at most two;
- column-pair codegrees are at most two.

This gives 1,800 anchored row-sorted matrices. Canonical minimization under
independent relabelling of `P` and `N` gives exactly five support orbits.
The coverage argument is in `protocol.md`; no automorphism is imposed.

## 2. The eight degree-two vertices are deficiency pairs

For a pair `{i,j}` in `P`, let

```text
c_ij = number of their common neighbors in N.
```

Every common neighbor not in `N` lies outside. Since an outside vertex has
at most two neighbors in `P`, only an `X2` vertex can contain this pair.
The exact multiplicity of `{i,j}` among the eight `P`-pairs of `X2` is

```text
m_ij = 2-c_ij.
```

Summing over pairs gives

```text
sum m_ij = 2*C(8,2)-8*C(4,2) = 56-48 = 8.
```

For a fixed vertex `i`,

```text
sum_{j != i} c_ij = 4*(4-1)=12,
```

so `sum_{j != i}m_ij=14-12=2`. Thus the deficiency pairs form a 2-regular
multigraph on each sign side. The same proof applies to the columns.

Each of the eight `X2` vertices therefore pairs one occurrence of a
`P`-deficiency pair with one occurrence of an `N`-deficiency pair.

## 3. Exact cross-pair decomposition

For `p_i in P` and `n_j in N`, the full number of common neighbors is one
when `B_ij=1` and two when `B_ij=0`. There are no common neighbors inside
the bipartite support. Consequently

```text
2J-B = sum_{x in X1} e_{i(x)} e_{j(x)}^T
       + sum_{x in X2} 1_{U_x} 1_{V_x}^T.                 (1)
```

Here `U_x` and `V_x` are the two deficiency pairs assigned to `x`.
Equation (1) gives exact cell capacities. In addition, the `2 x 2`
submatrix `B[U_x,V_x]` must be a matching: if a selected support vertex
had two neighbors on the opposite pair, it and `x` would be adjacent but
already have two common neighbors, contradicting `lambda=1`.

Two distinct `X2` vertices can share at most two support neighbors in total.
If they shared three, even a nonadjacent pair would exceed `mu=2`.

The complete multiset-coupling enumeration gives:

```text
support orbits                                  5
basic deficiency-pair coupling multisets    4,985
support orbits retaining a coupling             5
```

Thus the labelled deficiency constraints do not by themselves exclude a
support orbit.

## 4. Support-vs-outside local equations

For an outside vertex `x`, an `X2` support rectangle determines exact
common-neighbor demands on its outside neighbors. If `i in P`, define

```text
q_i(x) =
  1-|B_i intersect V_x|,  if i in U_x,
  2-|B_i intersect V_x|,  otherwise.
```

The eight row demands sum to six; the symmetric column demands also sum to
six. Taking `X2` independent, these demands must be realized by six `X1`
singleton cells. A cell inside `U_x times V_x` is forbidden because it
would share two support neighbors with `x`.

The checker solves each bounded `8 x 8` contingency problem by exact
integral max flow. All 4,985 couplings pass this necessary local test. This
is a positive finite result, not an outside-graph construction.

## 5. Outside type-degree closure

For any outside vertex `x in X_d`, put

```text
a_x = number of neighbors of x in X2,
b_x = number of neighbors of x in X1,
c_x = number of neighbors of x in X0.
```

Counting common neighbors of `x` with all 16 support vertices gives

```text
b_x+2a_x = 16-5d.
```

Since the outside degree is `14-2d`,

```text
c_x = a_x+3d-2.                                           (2)
```

Thus:

```text
X0: b=16-2a, c=a-2,  2<=a<=8;
X1: b=11-2a, c=a+1,  0<=a<=5;
X2: b= 6-2a, c=a+4,  0<=a<=3.
```

Let `t=e(X2)`. Summing (2) gives the six type-edge counts

```text
e00=5+t,       e01=112-4t,    e02=32+2t,
e11=304+4t,    e12=48-4t,     e22=t.                       (3)
```

Now sum the SRG common-neighbor equations over all six unordered pairs of
outside types. Support contributes zero to every pair involving `X0`,
`16*C(8,2)=448` to `X1-X1`, `16*C(2,2)=16` to `X2-X2`, and
`16*8*2=256` to `X1-X2`. Counting the remaining common neighbors through
outside vertices yields:

```text
sum C(c,2) = 105-t,       sum cb = 1296+4t,
sum ca     = 144-2t,      sum C(b,2) = 3280-4t,
sum C(a,2) = 40-t,        sum ab = 720+4t.                  (4)
```

The checker completely enumerates the bounded degree histograms in (2),
imposes all six equations (4), and applies Havel-Hakimi to the `X2` degree
sequence. The exact result is

```text
t=0: 43 histogram triples;
t=1:  7 histogram triples;
t=2,...,12: none.
```

Therefore the eight `X2` vertices induce either an independent set or a
single edge.

## 6. Exact outside spectrum from the support orbit

Let `H` be the `16 x 16` adjacency matrix of the bipartite support and `D`
the `83 x 83` outside adjacency matrix. Jacobi's principal-minor identity
and the SRG resolvent give

```text
chi_D(x)
 = (x-3)^38 (x+4)^28 (x^2-9x-38)
   * det((x+1)I+H)/(x+5).                                  (5)
```

The exponents use the full-graph multiplicities
`mult_A(3)=54` and `mult_A(-4)=44`. Swapping them would fail even
`trace(D)=0`.

The checker computes the final degree-15 factor by exact Newton identities.
All five support orbits pass the trace checks

```text
trace(D)=0, trace(D^2)=1002, trace(D^3)=906.
```

Thus every lane has 501 outside edges and 151 outside triangles. The exact
fourth traces and four-cycle counts are:

| support orbit | `trace(D^4)` | outside 4-cycles |
|---:|---:|---:|
| 1 | 32422 | 1135 |
| 2 | 32406 | 1133 |
| 3 | 32398 | 1132 |
| 4 | 32390 | 1131 |
| 5 | 32390 | 1131 |

The exact characteristic factors and determinants are stored in
`exact-results.json`. No support orbit is eliminated spectrally.

## 7. Boundary

The norm-16 branch remains live. Its exact new boundary is:

- five support isomorphism orbits;
- 4,985 labelled deficiency coupling multisets across one representative
  of each orbit;
- all 4,985 pass the independent-`X2` local marginal test;
- `X2` induces zero or one edge;
- each support orbit fixes the full outside characteristic polynomial.

No 83-vertex outside graph is constructed, and no full SRG compatibility
certificate is claimed. Conway-99 and novelty remain `UNKNOWN`.
