# Wave 51 globally symmetric triangle triple-count relaxation

Status: exact positive aggregate control `CANDIDATE`; no graph, endpoint
construction, endpoint exclusion, or contradiction. The prism-free endpoint
and Conway-99 remain `UNKNOWN`.

## Frozen endpoint relations

The 231 graph triangles are partitioned relative to a fixed triangle by five
relations, in this order:

```text
I  equal;
K  share one graph vertex;
D  disjoint with zero cross edges;
C  disjoint with one cross edge;
B  disjoint with two cross edges.
```

Their valencies at the prism-free endpoint are

```text
(1,18,32,144,36).
```

The setup uses only the exact identities

```text
K^2 relation values:        (18,5,0,1,2);
K(B-D) = 4K;
(B-D)^2 = 68I + 13D - 13B;
local K-neighbor graph:     3K6.
```

Here `K` is the triangle-intersection graph. Its spectrum is
`18^1,7^54,0^44,(-3)^132`. The signed matrix

```text
S = K^2 - 17I - 4K - J = B-D
```

has spectrum `4^187,(-17)^44` and satisfies
`S^2+13S-68I=0`. The matrix `4I-S` is exactly the previously known scaled
projector `21E_0`; no novelty is claimed for this algebra.

## Minimal global relaxation

Let `p^k_ij` be the average number of third triangles in relations `i` and
`j` to an ordered pair in relation `k`. Introduce the normalized triple
tensor

```text
t_ijk = v_k p^k_ij.
```

Counting the same ordered triples after permuting their three vertices forces
`t` to be symmetric in all indices. The exact feasibility system asks for a
nonnegative symmetric tensor with:

```text
sum_j t_ijk = v_i v_k;
t_11k = v_k (18,5,0,1,2)_k;
t_14k - t_12k = 4 v_k for k=K, and zero otherwise;
t_44k + t_22k - 2t_24k = v_k (68,0,13,0,-13)_k;
the local 3K6 row for k=K.
```

There are only 35 symmetric variables before forced identity entries and
zeros. No floating-point optimizer is needed: `exact_tensor.py` contains an
explicit nonnegative integer tensor. Each of its five normalized slices is
itself an integral local table, so every slice lies in the corresponding
local-table polytope. The balance equations hold exactly.

## Result

The globally symmetric triple-count relaxation is feasible. Therefore these
linear local and aggregate equations do **not** exclude the prism-free
endpoint.

The certificate is especially easy to reproduce from the three-parameter
linear family at

```text
(a,f,i) = (288,0,288).
```

The complete tensor and all five `5x5` tables are in `exact-result.json`.

## Important non-realizability diagnostic

If the five average tables were incorrectly treated as constant intersection
numbers of an association scheme, their multiplication constants would have
to be associative. They are not: 100 of 625 ordered associativity checks
fail; the first gives

```text
81 != 153.
```

This does not contradict the aggregate relaxation. In a general graph the
local tables may vary from pair to pair, and their averages need not form a
closed adjacency algebra. It does prove that the displayed averages are not
themselves a homogeneous association-scheme construction.

## Reproduce

```powershell
python -B attempts\wave51-global-triple-tensor\exact_tensor.py `
  --output attempts\wave51-global-triple-tensor\exact-result.json

python -B attempts\wave51-global-triple-tensor\exact_tensor.py `
  --verify attempts\wave51-global-triple-tensor\exact-result.json

python -B -m unittest discover `
  -s attempts\wave51-global-triple-tensor -p "test_*.py" -v
```

The checker uses only standard-library integer arithmetic and enforces a 20%
free-physical-memory floor.

## Promotion boundary

- This is discovery-agent work and requires independent replay.
- The certificate controls only averaged triples, not quadruples.
- It does not assign compatible local tables to 231 actual triangle vertices.
- It supplies no adjacency matrix, hypergraph, block design, or SRG.
- Its failure of association-scheme associativity is retained explicitly.
- Feasibility of this relaxation is not evidence that the endpoint exists.
- No automorphism of a completed graph is assumed.
- The prism-free endpoint and Conway-99 remain `UNKNOWN`.
