# Wave151 independent derivation

## One incidence group

The frozen Wave149 diagonal block is

\[
G_{ii}=9I-M+J,
\]

where \(M\) is the perfect matching
\((0,1),(2,3),\ldots,(10,11)\). Its diagonal entries are 10, matched
off-diagonal entries are zero, and every other off-diagonal entry is one.

Suppose a binary \(12\times60\) matrix has two ones in every column. Each
column can be viewed as an edge between its two occupied rows. The Gram entry
at rows \(u,v\) counts columns containing both rows, hence counts copies of
the edge \(\{u,v\}\). The required Gram block therefore forces:

- none of the six matching edges;
- one copy of every other edge of \(K_{12}\).

There are \(\binom{12}{2}-6=60\) such edges. The verifier independently lists
them in lexicographic order and forms their vertex-edge incidence matrix
\(C_0\).

## The second group

Let \(E_0,\ldots,E_{59}\) be that edge list. The sealed permutation \(Q_1\)
defines group one by making column \(c\) the incidence vector of
\(E_{Q_1(c)}\). The verifier checks that \(Q_1\) contains every integer from
0 through 59 exactly once.

Stacking the two incidence matrices gives \(C_{01}\in\{0,1\}^{24\times60}\).
Direct integer checks give:

- all 1,440 entries are binary;
- every row sum is 10;
- each column has two ones in group zero and two in group one;
- `SHA-256(C01) =
  11dd68b64c237e6d45e221e8910b3da69e9492dd01aeb697555d874fdab9eed5`.

## Gram replay

The verifier computes row inner products directly and compares all entries:

| Block | Entries | Canonical SHA-256 |
|---|---:|---|
| \(G_{00}=C_0C_0^\mathsf T\) | 144 | `a3e4e131fb05463e586a880b9915523c286281f3c2e3622843b3a2353745b4f1` |
| \(G_{11}=C_1C_1^\mathsf T\) | 144 | `a3e4e131fb05463e586a880b9915523c286281f3c2e3622843b3a2353745b4f1` |
| \(G_{01}=C_0C_1^\mathsf T\) | 144 | `21330ee4f3ba598ae0535586a34c34d9e7a7a63552bb81eab6656a5ddfda5fc4` |
| \(G_{10}=C_1C_0^\mathsf T\) | 144 | `21330ee4f3ba598ae0535586a34c34d9e7a7a63552bb81eab6656a5ddfda5fc4` |

Thus all 576 entries of the 24-row principal Gram submatrix agree with the
frozen Wave149 target. This is a genuine exact partial factor.

## Retained third-group candidate

The stored \(Q_2\) is also a permutation. Its incidence group \(C_2\) does
not realize the required cross blocks:

\[
\|C_0C_2^\mathsf T-G_{02}\|_F^2=40,\qquad
\|C_1C_2^\mathsf T-G_{12}\|_F^2=40.
\]

The total exact squared residual is 80. The verifier reproduces both residual
matrices and their hashes. A positive residual proves only that this
particular \(Q_2\) fails; it is not evidence that no exact \(Q_2\) exists.

The separate unrestricted score 108 cannot be replayed because no
corresponding pair of permutations is stored.

## Fixed-\(Q_1\) solver audit

For the single stored \(Q_1\), a possible mapping from a domain column to a
third-group edge can be removed whenever it would add to a target Gram entry
that must be zero. Independently applying this rule leaves exactly 1,620
Boolean mappings. The stated model dimensions are consequently consistent:

- 60 domain exact-one constraints;
- 60 image exact-one constraints;
- 288 cross-block capacity constraints.

The stored JSON says `unsat`, but the sealed package contains no proof trace,
LRAT/DRAT-style proof, or other independently replayable unsatisfiability
certificate. The status is therefore classified
`UNVERIFIED_SOLVER_DIAGNOSTIC`. Even a future proof would concern only the
single displayed \(Q_1\).

## Scope

The exact result is only a 24-by-60 factor for two groups. The third
12-row group, full \(36\times60\) matrix \(C\), and compatible
\(60\times60\) residual adjacency matrix \(D\) remain `UNKNOWN`. No graph,
Conway-99 resolution, or improved strict upper bound follows.
