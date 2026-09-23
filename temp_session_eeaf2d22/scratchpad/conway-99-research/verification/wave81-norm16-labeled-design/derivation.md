# Clean-room derivation for Wave 81

The base verification is conditional on the frozen Wave 78 norm-16 signed
support branch. No lattice or modular-form theorem is reverified here.

## 1. Support census

Let `B` be the `8 x 8` bipartite adjacency matrix between the two sign
sides `P` and `N`. Every row and column has weight four, and every pair of
rows or columns has codegree at most two.

For any such matrix, independently relabel the columns so that one chosen
row becomes `00001111`, then sort the rows. The chosen row is the least
weight-four mask, so the verifier's anchored combination search contains
the resulting matrix. It finds exactly 1,800 anchored row-sorted matrices.

To quotient labels, the verifier generates all `8!` column relabellings of
each new representative and sorts its rows. This is the complete
`S8 x S8` orbit: sorting removes row labels and exhaustive column
permutation removes column labels. Exactly five orbits result. This uses no
automorphism of the hypothetical 99-vertex graph.

## 2. Reconstructing the Wave 78 histogram

For a pair of support vertices on one sign side with support codegree `c`,
exactly `2-c` outside vertices of type `X2` contain that pair. Summing over
all pairs gives

```text
sum (2-c) = 2*C(8,2) - 8*C(4,2) = 8.
```

Thus `n2=8`. The 16 support vertices each have `14-4=10` outside
neighbors, while an `Xd` vertex contributes `2d` support incidences:

```text
n0+n1+n2 = 83,
n1+2*n2 = 80.
```

Therefore `(n0,n1,n2)=(11,64,8)`.

## 3. Deficiency-pair couplings

For each sign side, expanding every pair with multiplicity `2-codegree`
produces eight pair occurrences, with every support vertex incident to
exactly two occurrences. Each `X2` vertex pairs one occurrence on `P` with
one on `N`.

The verifier independently enumerates the coupling multisets. Repeated
pair occurrences are indistinguishable, so assignments to equal `P` pairs
are ordered by `N`-pair type. This removes only permutations of the eight
outside labels. The recursion enforces:

- each selected `2 x 2` support rectangle is a matching;
- two selected `X2` supports overlap in at most two support vertices;
- every cross cell is used at most `2-B[i,j]` times.

The five counts are

```text
90, 326, 681, 2068, 1820,
```

for a total of 4,985.

For each selected `X2` rectangle, the exact common-neighbor requirements
give six row units and six column units to be supplied by `X1` singleton
cells. A separate bounded-contingency dynamic program tests those
marginals, with the selected rectangle forbidden. All 4,985 couplings
pass. Deleting every capacity in a positively demanded row makes the
control instance fail, so the test is not vacuous. These flows are
per-`X2` and are not simultaneous outside graphs.

## 4. Local type and edge equations

For an outside vertex `x in Xd`, let `a,b,c` be its numbers of neighbors
in `X2,X1,X0`. Summing its common-neighbor counts with all 16 support
vertices gives

```text
b+2a = 16-5d,
c = a+3d-2.
```

Writing `t=e(X2)`, summing these degrees over the three types gives

```text
e00=5+t,       e01=112-4t,    e02=32+2t,
e11=304+4t,    e12=48-4t,     e22=t.
```

## 5. Six outside pair moments

For a pair of vertices in the same type, the total number of common
neighbors is twice the number of nonedges plus once the number of edges.
For a pair in two different types, the same rule applies to the complete
cross product. Subtracting common neighbors lying in the 16-vertex support
gives the six outside-vertex sums:

```text
sum C(c,2) = 105-t,
sum c*b    = 1296+4t,
sum c*a    = 144-2t,
sum C(b,2) = 3280-4t,
sum C(a,2) = 40-t,
sum a*b    = 720+4t.
```

The support subtractions are respectively `0,0,0,448,16,256`. The
verifier exhausts every bounded histogram allowed by the local equations,
checks all six sums, and applies Havel-Hakimi to the `X2` induced degree
sequence. It reproduces every discovery row exactly:

```text
t=0: 43,
t=1: 7,
t=2,...,12: 0.
```

Hence Wave 81's advertised relaxed degree-histogram conclusion is
`VERIFIED`.

## 6. Verifier-derived graphical strengthening

Claim label: `DERIVED`; separate verification required.

The same histogram triple fixes all six type-subgraph degree sequences:
the three induced graphs and the three bipartite graphs between types.
The verifier applies Havel-Hakimi to the induced sequences and Gale-Ryser
to the bipartite sequences. Three `t=0` rows fail only the `X0` induced
test:

```text
[4,3,1,1,1,0,0,0,0,0,0],
[4,2,2,2,0,0,0,0,0,0,0],
[3,3,3,1,0,0,0,0,0,0,0].
```

For example, the first violates Erdos-Gallai at `k=2` (`7>5`), the second
at `k=1` (`4>3`), and the third at `k=3` (`9>7`). All other 47 rows pass
each individual type-subgraph graphicality test. Thus the strictly
stronger degree-level census is `40+7`. This still does not enforce the
outside common-neighbor equations vertex by vertex.

## 7. Jacobi residual polynomials

The full SRG eigenvalue multiplicities follow from

```text
1+f+g=99,
14+3f-4g=0,
```

so `f=54` for eigenvalue `3` and `g=44` for eigenvalue `-4`.
Jacobi's principal-minor identity gives

```text
chi_D(x)
 = (x-3)^38 (x+4)^28 (x^2-9x-38)
   * det((x+1)I+H)/(x+5).
```

The verifier computes `det((x+1)I+H)/(x+5)` independently by exact Newton
identities for `-(I+H)` and exact synthetic division. Every coefficient
matches the discovery JSON.

For the five support orbits, the first four traces are

```text
[0,1002,906,32422],
[0,1002,906,32406],
[0,1002,906,32398],
[0,1002,906,32390],
[0,1002,906,32390].
```

Since the outside degree multiset is `11 x 14, 64 x 12, 8 x 10`,

```text
trace(D^4) = 23342 + 8*C4(D).
```

The four-cycle counts are therefore `1135,1133,1132,1131,1131`.
All are nonnegative integers, and no support orbit is eliminated.

Swapping the restricted eigenvalue multiplicities changes the first trace
from zero to `-70`. The transient swapped-exponent formula is therefore
rejected everywhere in the sealed verifier output.

## Boundary

The five support orbits and all 4,985 coupling rows remain necessary
incidence candidates. No 83-vertex outside graph is constructed, and no
global SRG compatibility certificate is claimed. Conway-99 and novelty
remain `UNKNOWN`.
