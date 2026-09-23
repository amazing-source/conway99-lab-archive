# Wave 51 globally symmetric triangle triple-count relaxation

```yaml
role: proof_b
date_utc: 2026-07-27T18:57:12Z
git_commit: e4394aa9172fa97a6dafa9158148c2183603a01b
claim_label: CANDIDATE
scope: exact aggregate triple-count relaxation at the prism-free n3=4158 endpoint
inputs:
  attempts/wave51-global-triple-tensor/input-freeze.sha256: frozen source list
method: symmetric normalized tensor t_ijk=v_k p^k_ij with exact integer certificate
command: python -B attempts/wave51-global-triple-tensor/exact_tensor.py --verify attempts/wave51-global-triple-tensor/exact-result.json
outputs:
  attempts/wave51-global-triple-tensor/exact-result.json: 8d42c51b5e6b5137466a4adf95442f4d67cf2708c29ac134f7972b8cfbc16d1e
limitations: aggregate triples only; no association scheme, graph, endpoint resolution, or novelty claim
```

## Result

The exact globally symmetric triple-count relaxation is feasible. Relations
`I,K,D,C,B` have valencies `(1,18,32,144,36)`. Writing

```text
t_ijk = v_k p^k_ij,
```

the relaxation requires full symmetry of `t`, the five transportation
margins, the relation values of `K^2`, `KS=SK=4K`, the signed identity
`S^2+13S-68I=0`, and the local `3K6` row at a `K` pair.

An explicit nonnegative integer tensor satisfies every equation. It is the
point `(a,f,i)=(288,0,288)` in the derived three-parameter linear family. All
five normalized slices are integral local tables, and all 125 global balance
equations

```text
v_k p^k_ij = v_i p^i_kj
```

hold exactly. This is a positive aggregate control, so the linear
triple-count lane supplies no endpoint contradiction.

## Algebraic boundary

The setup also independently recovers

```text
spec(K) = 18^1, 7^54, 0^44, (-3)^132,
S = K^2 - 17I - 4K - J = B-D,
spec(S) = 4^187, (-17)^44,
S^2 + 13S - 68I = 0.
```

Here `4I-S=21E_0`, the previously known scaled projector. No algebraic
novelty is claimed.

The five average tables fail 100 of 625 association-algebra associativity
tests; the first failure is `81 != 153`. Therefore they are not a homogeneous
association-scheme construction. This is not a contradiction for the
aggregate relaxation because actual pair-local tables may vary while having
these averages.

## Boundary and continuation

The certificate gives neither 231 compatible local tables nor an adjacency
matrix. It omits quadruple consistency and all graph-realizability
conditions. Feasibility is not evidence of existence. No completed-graph
automorphism was assumed. The prism-free endpoint, Conway-99, and novelty
remain `UNKNOWN`.

The smallest stronger alternative-space problem is a quadruple-consistency
lift that retains pair-to-pair variation, or equivalently a local
Terwilliger/coherent-configuration refinement around one triangle.
