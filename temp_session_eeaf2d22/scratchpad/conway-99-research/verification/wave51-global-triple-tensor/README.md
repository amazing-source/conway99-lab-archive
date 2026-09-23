# Wave 51 independent global-triple-tensor verification

Status: the exact tensor arithmetic and its interpretation as a positive
aggregate control are `VERIFIED`. The displayed average tables are `REFUTED`
as association-scheme intersection numbers. The prism-free endpoint,
Conway-99, and novelty remain `UNKNOWN`.

This package is a clean-room verifier. It imports no discovery code. The
discovery package and agent report were hashed into
`preinspection-freeze.sha256` before their contents were inspected.

## Independently derived structure

For a hypothetical `srg(99,14,1,2)`, every edge lies in one triangle.
There are

```text
99*14/2 = 693 edges,
693/3 = 231 triangles,
14/2 = 7 triangles through each graph vertex.
```

Let `N` be vertex-triangle incidence and let `K` join triangles that share a
graph vertex. Then

```text
NN^T = 7I+A,
N^TN = 3I+K.
```

The restricted eigenvalues of the SRG adjacency matrix `A` are `3` and `-4`
with multiplicities `54` and `44`. Equality of the nonzero spectra of
`NN^T` and `N^TN` therefore gives

```text
spec(K) = 18^1, 7^54, 0^44, (-3)^132.
```

The 18 triangles meeting a fixed triangle split according to the shared
vertex. Each of its three vertices contributes six other triangles. Two
triangles from different parts cannot meet again without giving an edge two
distinct common neighbors. Thus the local graph is exactly `3K6`.

## Disjoint-pair count

Cross edges between two disjoint graph triangles form a matching. If one
vertex had two cross neighbors, the edge joining those neighbors inside the
other triangle would lie in two triangles, contradicting `lambda=1`.
Consequently `q<=3`, and `q=3` is exactly a perfect matching between two
triangles: an induced triangular prism.

For a fixed triangle, write `x_q` for the number of disjoint triangles with
`q` cross edges. There are `231-1-18=212` disjoint triangles. Double
counting cross-edge incidences gives

```text
sum x_q = 212,
sum q*x_q = 36*6 = 216.
```

The second count uses the 36 edges from the fixed triangle to outside
vertices and the six disjoint triangles through each outside endpoint.
For each of the three edges of the fixed triangle, each of 12 outside
neighbors has a unique second completion by `mu=2`. This gives

```text
sum binomial(q,2)*x_q = 3*12 = 36.
```

At a prism-free endpoint `x_3=0`; solving yields
`(x_0,x_1,x_2)=(32,144,36)`.

## Signed algebra

The relation values of `K^2` are `(18,5,0,1,2)` on `I,K,D,C,B`.
Since `J=I+K+D+C+B`,

```text
S = K^2-17I-4K-J = B-D.
```

Evaluating this polynomial on the four eigenspaces of `K` gives

```text
spec(S) = 4^187, (-17)^44,
KS=SK=4K,
S^2+13S-68I=0.
```

Furthermore `4I-S` is zero away from the zero eigenspace of `K` and is 21
there, so `4I-S=21E_0`.

## Exact tensor replay

The verifier reconstructs the full symmetric tensor from the 21 displayed
nonzero canonical entries, derives each table as
`p^k_ij=t_ijk/v_k`, and checks:

- nonnegative integral tensor entries and five integral local slices;
- all five row-margin and five column-margin vectors;
- 25 identity entries and 125 global balance equations;
- all `K^2`, `KS`, `SK`, and `S^2` relation values;
- the local `3K6` row and all necessary orientation divisibilities;
- the displayed family point `(a,f,i)=(288,0,288)`.

All checks pass. The five average tables fail exactly 100 of 625 ordered
association-algebra associativity checks. The first failure, at
`(i,j,m,k)=(1,1,2,2)`, is `81 != 153`.

Eleven unit tests pass: one baseline and ten hostile mutations covering
negative, duplicate, noncanonical, and arithmetically corrupted tensors;
table, spectrum, and associativity-report corruption; and status inflation
for the endpoint, Conway-99, and novelty.

## Reproduce

```powershell
python -B verification\wave51-global-triple-tensor\independent_check.py `
  --input attempts\wave51-global-triple-tensor\exact-result.json `
  --output verification\wave51-global-triple-tensor\independent-result.json

python -B -m unittest discover `
  -s verification\wave51-global-triple-tensor -p "test_*.py" -v
```

The checker uses standard-library integer arithmetic and refuses to start
below 20% free physical memory on Windows.

## Logical boundary

The certificate proves feasibility only for an averaged ordered-triple
relaxation. It does not assign the five local tables to 231 actual triangle
vertices, impose quadruple consistency, or supply an adjacency matrix. The
associativity failure rules out only the displayed averages as a homogeneous
association scheme. It is not a graph contradiction. No completed-graph
automorphism is assumed, and feasibility is not evidence that the endpoint
exists.
