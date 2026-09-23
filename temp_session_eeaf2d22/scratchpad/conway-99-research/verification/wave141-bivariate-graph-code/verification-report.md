# Independent verification of Wave 141

Verdict: `PASS`.

The final discovery manifest has SHA-256
`75933cca692f2678bdd74190290b91eb13f6492fce52bc88e896ef7485fe06f8`.
All nine listed payloads reproduce their sealed hashes.  The two Wave21
prerequisites also reproduce the hashes pinned by Wave141.  The discovery
checker passes four tests; the clean-room verifier passes eleven hostile
tests without importing or executing either supplied checker.

The verified claims are conditional consequences of the frozen Wave21
six-vertex census and the hypothetical adjacency identities.  They do not
construct a formal enumerator, code, graph, or Conway-99 resolution.

## Bivariate transform

For

```text
B[i,j]=#{x in F_2^n : wt(x)=i and wt(Ax)=j},
```

the exact marginals are

```text
sum_j B[i,j]=binom(n,i),
sum_i B[i,j]=2^(n-rank(A)) A_j,
```

because every input has one input weight and every image word has exactly
`|ker(A)|` preimages.  Even rows imply `A1=0`, so

```text
B[i,j]=0 for odd j,
B[i,j]=B[n-i,j].
```

Let

```text
S={(x,Ax):x in F_2^n}.
```

Symmetry of `A` makes `S` isotropic for

```text
<(x,y),(u,v)>=x dot v+y dot u.
```

Since `dim(S)=n`, it is symplectically self-dual.  Character orthogonality
therefore gives, with the standard binary Krawtchouk convention,

```text
B[i,j]=2^-n sum_(a,b) K_i(b) K_j(a) B[a,b].
```

The order of the two Krawtchouk factors matters: the symplectic pairing swaps
the two coordinate blocks.  The verifier enumerated every vector for two
independent controls, the adjacency matrices of `K3` and `K5`.  Both are
symmetric, even-rowed, idempotent over `F_2`, and kill `1`; every transform
coefficient, marginal, parity condition, and complement condition passes.

## Dihedral equality space

Output parity and the transform generate the expected `D8` representation.
After a change of basis it is the usual action of the eight square symmetries
on a `100` by `100` grid.  Because the side length is even, the exact
Burnside traces are

```text
identity                         10000
quarter, half, three-quarter turns  0
two axis reflections                0
two diagonal reflections          100 each
```

Their average is

```text
(10000+100+100)/8=1275.
```

Thus:

```text
output-even dimension                         5000
common invariant dimension                    1275
combined equality rank                        3725
input-complement-reduced dimension            2500
additional rank after complement reduction    1225
```

As a hostile convention check, direct exact rational row reduction gives
ranks `(5,1)` for the analogous `K3` even-output/complement systems and
`(12,3)` for `K5`, exactly matching the same Burnside calculation.

## Independent Wave21 graph/deck replay

The verifier statically extracted only the two frozen deck dictionaries with
`ast.literal_eval`; no supplied Python was executed.  It independently:

1. enumerated all labeled masks satisfying the local `lambda=1, mu=2`
   common-neighbor restrictions;
2. canonicalized under every vertex permutation;
3. obtained exactly `9`, `21`, and `62` classes on four, five, and six
   vertices;
4. rebuilt every vertex-deletion deck;
5. checked the frozen source-to-canonical mappings bijectively;
6. reproduced all four-to-five and corrected five-to-six deck columns.

The known correction is again exactly `+n_23` in source row seven.

The source class `N3` maps to canonical mask `5941`.  It has eight edges:
two disjoint triangles joined by two independent cross edges.  Hence its
six-shell sign is

```text
(-1)^(6+8)=+1.
```

The signed affine constant contains a substantial cancellation:

```text
 561276870
-559252386
----------
   2024484
```

The signed slope is `512/3`.  The direct `N3=n3` class contributes `+1`
to that slope; the full `512/3` is the sum over all 62 affine class formulas,
not solely the direct `N3` term.

Deleting vertices from the six-class census and dividing by the exact
extension multiplicities independently reconstructs every lower-order
count.  It yields

```text
S0 =          1
S1 =        -99
S2 =       3465
S3 =     -56595
S4 =     462924
S5 =   -1821204
S6 =    2024484 + (512/3)n3.
```

This uses

```text
q(A1_S)=|S|+e(G[S]) mod 2,
```

so it verifies the signed output shell, not every individual output weight.

## Low rows and exactness boundary

Rows zero through three were independently derived.  In particular,

```text
B[2,24]=4158, B[2,26]=693,
```

from nonedges and edges.  A separate triple count gives

```text
B[3,30]=70686
B[3,32]=41580
B[3,34]=36036
B[3,36]=8547.
```

The triple derivation distinguishes triangles, induced paths, one-edge
triples with or without a common neighbor, and independent triples with or
without a common neighbor.  It uses only the SRG parameters and the fact that
each vertex neighborhood is `7K2`.

For larger input sets, the full output weight generally depends on embedding
and higher common-neighbor data not captured by the induced isomorphism
class.  Wave141 correctly limits its general six-class claim to the signed
mod-four shell.

One additional exact check is useful: an `N3` six-set has internal degrees
`3^4,2^2` and outside neighbor profile

```text
0^33, 1^52, 2^8.
```

Therefore `wt(A1_S)=56`, and every `N3` contributes to `B[6,56]`.  This gives
only `B[6,56]>=n3`; it does not identify that cell with `n3`.

## Bounds and numerical status

Nonnegativity of the sixth row alone gives

```text
n3 <= 838878579/128 = 6553738.898...
```

or `n3<=6553737` after the verified multiple-of-three condition.  This is far
weaker than the existing `n3<=4158`.

The floating scout supplies no evidence.  Its partial-row points violate
inactive transform equations by large amounts, and the subsequent statuses
are floating `UNKNOWN`.  No exact rational primal or Farkas dual is present.
The verifier therefore accepts neither feasibility nor infeasibility from
that scout.

Formal rational feasibility, formal integral feasibility, graph
realizability, the target sign, novelty, and Conway-99 all remain `UNKNOWN`.

## Reproduction

```powershell
python -B attempts\wave141-bivariate-graph-code\exact_check.py --verify
python -B -m unittest discover `
  -s attempts\wave141-bivariate-graph-code -p "test_*.py" -v
python -B verification\wave141-bivariate-graph-code\independent_verify.py
python -B -m unittest discover `
  -s verification\wave141-bivariate-graph-code -p "test_*.py" -v
```
