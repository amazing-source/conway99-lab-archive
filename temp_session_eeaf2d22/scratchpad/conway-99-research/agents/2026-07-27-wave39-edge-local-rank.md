# Wave 39 edge-local rank discovery report

```yaml
role: proof_a
date_utc: 2026-07-27
git_commit: 019b78ac9a5170107d105ad4d8fcd27f55dde642
claim_label: CANDIDATE
scope: universal edge-local characteristic-seven rank consequence, with conditional prism-free endpoint refinement
method: exact construction of all eleven forced 27-vertex normal forms and finite-field Gaussian elimination
limitations: discovery cannot verify itself; no endpoint exclusion, graph, upper-bound improvement, or novelty claim
```

## Candidate theorem

Every hypothetical `srg(99,14,1,2)` satisfies

```text
rank_F7(M) >= 19
```

for the integral triangle projector `M=21E_0`.

Choose an edge `xy` and its unique triangle mate `z`. The twelve remaining
neighbors of each endpoint form perfect matchings `X` and `Y`, and the
`mu=2` rule gives one perfect matching between `X` and `Y`. Therefore the
induced graph on

```text
L={x,y,z} union X union Y
```

has 27 vertices and eleven normal forms, indexed by the positive partitions
of six.

The verified transport identity

```text
N M N^T=27I-9A+J
```

has the same rank as `M` modulo seven. This follows because
`N^T N M=3M`, so `N` is injective on `im(M)` in characteristic seven, and
symmetry handles the right multiplication. The transported matrix is
congruent to the Seidel matrix `J-I-2A`. Its principal block on `L` is
therefore a lower bound for the rank of `M`. For a partition `pi`, exact
elimination gives

```text
rank_F7((27I-9A+J)[L,L])
  =25-2*#{even parts of pi}.
```

No more than three positive even parts sum to six, proving the candidate
floor 19 once the finite normal-form calculation is independently checked.

## Endpoint consequences

Prism-freeness removes every part of size one. The surviving ranks are:

```text
2+2+2 -> 19
2+4   -> 21
3+3   -> 25
6     -> 23.
```

With the previously verified rank ranges and parity, 429 arithmetic
`(r3,r7)` pairs remain rather than 528. At `r3=12`, the rank `r7` is even
and at least 20.

This is a stronger necessary condition, not the requested endpoint
exclusion. The boundary `r7<=20` would force every graph edge to have type
`2+2+2`, which is the next coupling target.
