# Wave 27 orchestrator addendum: the `A20` compression floor

```yaml
role: orchestrator
date_utc: 2026-07-24T00:48:00Z
git_commit: 9cc3f1e063ef63954102908c1b852dce7948a84f
claim_label: DERIVED
scope: >-
  Exact exclusion of an orthogonal A20 summand from the n3=708
  projector/Schur endpoint package, and the resulting conditional exclusion
  of every full orthogonal ADE root-lattice form after importing the
  separately verified A2 theorem and the pending-independent-verification
  A6/E6 tensor theorem.
inputs:
  agents/2026-07-23-wave27-general-root-tensor.md: 456a4ad6f27c1c9c09f84b2ff41796473f519b5aaabda36b71022a51bbbe7f38
  attempts/wave27-general-root-tensor/exact-results.json: 98aba5a30b2f3a83b9f6ce6fd6a20458505b668249d97b0810907de50cae678d
  verification/wave26-a2-frame-obstruction/2026-07-23T225015Z-audit.md: 5ec6b1924fb9ca2ab9295808178684751b6a90e43315d00cbf232ba8d9fe84a3
method: >-
  Factor the A_n Cartan matrix as the sum of n+1 explicit integral
  rank-one forms. Evaluate the trace pairing against an arbitrary even
  positive-definite integral principal Q block, then combine its exact
  2(n+1) floor with the positive-integral-determinant AM-GM floor on the
  orthogonal complement.
command: |-
  cd attempts/wave27-a20-trace-addendum
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output exact-results.json
outputs:
  attempts/wave27-a20-trace-addendum/exact_check.py: 7762acf33bf519e3a91f442d4dcae6da34e770d98491b02d995a14550840de7c
  attempts/wave27-a20-trace-addendum/test_exact_check.py: b5d55c15f01c4f7a5856ebce36646140f90994328b62852b8dfb1d121bed4f82
  attempts/wave27-a20-trace-addendum/exact-results.json: dc5716cbf2537cd214906f1bf2eae96d4886e4bd88008cd7508c6a64d78f089c
  attempts/wave27-a20-trace-addendum/input-freeze.sha256: c0a85ebaf10f53b9ab456147b77d021d0e2d4892123c8939c1a15413c09f9679
  attempts/wave27-a20-trace-addendum/failed-routes.md: 178c8578eebe32d10e6d8c5c8862ba05e5c0a2b661c62813310371db6c9b17b5
limitations:
  - The A20 result requires an orthogonal integral summand of S.
  - The full-ADE corollary assumes that all of S is an orthogonal sum of
    irreducible ADE root lattices.
  - The imported A6/E6 tensor theorem is still undergoing its fresh verifier.
  - General even scaled-dual lattices need not be full root lattices.
  - No primitive embedding, projector, Schur certificate, graph, endpoint
    exclusion, target resolution, formal-kernel proof, or novelty result follows.
```

## Result

Let the scaled-dual form have an orthogonal integral summand

```text
S=A20 orthogonal_sum C.
```

For the positive-definite even integral principal block `Q_AA`, the exact
identity below gives

```text
tr(A20 Q_AA) >= 42.                              (1)
```

The rank-24 complementary compression has positive integral determinant, so
AM-GM gives trace at least 24. Therefore the global Schur trace would satisfy

```text
tr(SQ) >= 42+24=66,
```

contradicting the endpoint identity `tr(SQ)=60`. Hence:

```text
orthogonal A20 summand at n3=708: REFUTED.        (2)
```

Combined with the independently verified `A2` frame obstruction and, once
its fresh verifier passes, the Wave 27 `A6` and `E6` tensor obstructions,
this removes every component type allowed by `21R^-1` integrality except
`E8`. Rank 44 is not divisible by eight, so conditionally:

```text
S is a full orthogonal ADE root lattice: REFUTED. (3)
```

Statement (3) does not classify or exclude general even lattices.

## Exact identity

Let `A_n` be the path Cartan matrix and let `e_1,...,e_n` be the standard
integer basis. Define the `n+1` nonzero vectors

```text
v_0=e_1,
v_i=e_i-e_(i+1) for 1<=i<n,
v_n=e_n.
```

Direct coefficient comparison gives

```text
A_n=sum_(i=0)^n v_i v_i^T.
```

For every symmetric matrix `Q`,

```text
tr(A_n Q)
 =sum_i v_i^T Q v_i
 =Q(e_1)+Q(e_n)+sum_(i=1)^(n-1) Q(e_i-e_(i+1)). (4)
```

If `Q` is even, integral, and positive definite, every displayed value is a
positive even integer and is therefore at least two. Thus

```text
tr(A_n Q)>=2(n+1).                               (5)
```

At `n=20`, this is the floor 42 used in (1).

## Complement and threshold checks

For an orthogonal rank-`n` summand of the rank-44 endpoint form, the
complementary compression has rank `44-n` and determinant

```text
det(S_CC) det(Q_CC),
```

a positive integer. Its trace is at least `44-n`. Equations (5) and this
floor give the general aggregate bound

```text
tr(SQ)>=2(n+1)+(44-n)=n+46.
```

This exceeds 60 exactly when `n>=15`; `A14` is the sharp noncontradictory
boundary for this particular argument. Evenness is essential: for a merely
integral positive-definite form, the vector norms need only be at least one.

## Status wall

```text
orthogonal A20 summand:                    DERIVED IMPOSSIBLE
full orthogonal ADE form:                  CONDITIONAL DERIVED IMPOSSIBLE
general h/index rows:                      UNKNOWN
n3=708:                                    UNKNOWN
Conway-99 existence and novelty:           UNKNOWN
```
