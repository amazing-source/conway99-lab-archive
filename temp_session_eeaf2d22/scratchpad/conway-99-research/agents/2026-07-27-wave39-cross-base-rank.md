# Wave 39 proof B: cross-base ternary projection

```yaml
role: proof_b
date_utc: 2026-07-27T02:17:28Z
git_commit: 019b78ac9a5170107d105ad4d8fcd27f55dde642
claim_label: DERIVED_INCONCLUSIVE
scope: >
  Conditional prism-free n3=4158 endpoint and its surviving
  rank_F3(M)=12 square-determinant boundary: cross-vertex-star projection,
  forced short dependencies, and exact low-rank quotient controls.
inputs:
  attempts/wave39-cross-base-rank/input-freeze.sha256: 931273ef657b540468da95a59e79565ae157123358fd8dbe334dea68f2f1aaa9
method: >
  Exact finite-field orthogonal decomposition, determinant classes,
  star projection, quadratic-space enumeration, pigeonhole counting,
  explicit short-relation reconstruction, and exact quotient controls.
command: |
  .\.venv\Scripts\python.exe -B attempts\wave39-cross-base-rank\exact_check.py --output attempts\wave39-cross-base-rank\exact-results.json
  .\.venv\Scripts\python.exe -B attempts\wave39-cross-base-rank\exact_check.py --verify attempts\wave39-cross-base-rank\exact-results.json
  .\.venv\Scripts\python.exe -B -m unittest -v attempts\wave39-cross-base-rank\test_exact_check.py
outputs:
  attempts/wave39-cross-base-rank/exact-results.json: 3955106a57f3910813f1ac680bc9bab6cb28024b883af4b08d157541e973a11b
  attempts/wave39-cross-base-rank/exact_check.py: 93f0730911a66d1c6ed11e262626408b96e98a66c39ff435085361b045b0bc0a
  attempts/wave39-cross-base-rank/test_exact_check.py: a69c7b42e641110f2e39c0f842bd0b8e1b2e97093a49e5ecfa0cd40a6a6a95c5
  attempts/wave39-cross-base-rank/README.md: 419e79b6d196b65bb0a50f7960643b275d25631631f6f8fe345ab570c0c79c48
  attempts/wave39-cross-base-rank/failed-routes.md: 733e3fa85fcffd224cf623bff7d71e5c64e0ed8e5a387511a3c139958598df50
limitations:
  - Discovery does not verify itself; independent reconstruction is required.
  - The forced short dependencies are necessary conditions, not a contradiction.
  - The low-rank quotients and projection control are not endpoint graphs.
  - No endpoint exclusion, improved upper bound, or novelty claim is made.
```

## Result

At the surviving ternary boundary the centered factor space is a nonsquare
eleven-space.  The seven triangles through any original vertex span a
nondegenerate square six-space, leaving a nonsquare five-dimensional
orthogonal complement.

Exactly 84 triangles are adjacent to the fixed vertex without containing
it.  Their centered star-inner profiles have five entries `1` and two
entries `2`, so every orthogonal projection into the five-space has norm
one.  That space contains only 72 oriented norm-one vectors.  Therefore
every original vertex forces at least twelve equal-projection pairs, each
giving a factor-row dependency supported on four or six triangles.

This is a new exact necessary restriction in the repository.  It does not
exclude the endpoint.  An explicit finite quadratic-space control realizes
the projection profile and exactly twelve such collisions.

The hoped-for universal local claim `rank_F3(P_T-I)>=12` is also refuted
more sharply: the package contains rank-ten and determinant-compatible
nonsquare rank-eleven quotient controls.

```text
forced collision pairs per vertex: >=12
forced dependency support:          4 or 6
rank-twelve endpoint exclusion:     NOT OBTAINED
general upper bound:                n3<=4158
n3=4158 / Conway-99:                UNKNOWN
```

The next exact target is to classify these support-four/six dependencies
under the full triangle-incidence relations and test whether their required
multiplicity across all 99 vertex stars is globally impossible.
