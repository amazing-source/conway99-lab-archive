# Wave 28 theta/modular independent audit

```yaml
role: verifier
date_utc: 2026-07-24T03:03:00Z
git_commit: d76d030f6d74e2e1b7ca2b2f0f97536241b3a10b
claim_label: VERIFIED
scope: >-
  Clean-room verification of the exact level, scalar character, Poisson/Weil
  transformation, Sturm-bound, modularity-veto, ADE-control, and h=729
  rootless bare-lattice claims in the Wave 28 theta/modular lane. This is not
  verification of a primitive embedding, endpoint frame, Schur certificate,
  n3=708, or Conway-99.
inputs:
  agents/2026-07-24-wave28-orchestrator-brief.md: 6a15446551b78822706a8e005bef49a411b904cf05f9459b6b3350239839ee1e
  agents/2026-07-24-wave28-theta-modular.md: 8783be7e730306637ed863b4d9fbe8f4193ad756e7ec86d697c7407688a5423a
  catalogue-data.json: 0bbf9d7b21ca3f7e5226df1683350772b407773d133350fb20fe5eae232e15f2
  source-manifest.json: 9229bacd7dcd52ccb6c2da4162507f11b48c93c028f31840884cbdca50a619ed
  theorem-source-manifest.json: 47ab1b9d7cf1c49aa53a905863d64243ab087bbe331c1ec6e845dc06afc446fd
method: >-
  Independent Smith-form reasoning, theorem-hypothesis audit, exact integer
  and rational matrix arithmetic, exact finite-field quadratic forms with an
  explicit isometry, a fresh ADE census, and a complete fraction-free
  closed-ellipsoid enumeration. The discovery checker and discovery JSON were
  neither imported nor executed.
command: |-
  cd verification/wave28-theta-modular
  python -B independent_check.py --output independent-results.json
  python -B -m unittest -v test_independent_check.py
outputs:
  independent-results.json: 24298ae282c7baa252a39ffe96fc37b7c696cb51f14b9ddea2318a59b4335b7f
limitations:
  - The hostile control supplies only S and G=21S^-1.
  - It supplies no primitive embedding, X, M, Q, B, Schur-square origin, or graph.
  - The original Sturm chapter is subscription content; its DOI and metadata were checked, while the displayed bound was independently recomputed from the standard formula.
  - Offline replay checks the attributed embedded numeric matrices. Replaying the live HTML fetch, raw hash, and parser requires network access.
  - n3=708, Conway-99 existence, and novelty remain UNKNOWN.
```

## Verdict

No mathematical, source-transcription, or scope-wall defect was found in the
frozen theta/modular report.

The following claims pass independently:

- all eight exact levels and scalar characters;
- the displayed componentwise Poisson/Weil laws under the report's sign
  convention;
- scalar Sturm bounds `7`, `14`, and `58` at levels `3`, `7`, and `21`;
- the determinant veto against exact-level modularity and strongly
  `21`-modular shortcuts;
- all five ADE component coefficients, their scaled-dual minima, and the
  complete 17-form rank-44 ADE census;
- the exact rootless `h=729` bare control
  `K12 orthogonal_sum LAMBDA(F)`;
- the rooted comparator `E6^6 orthogonal_sum E8`; and
- isometry of the two finite discriminant quadratic modules, not merely
  equality of their orders.

The discovery report's lower bound
`min(21 S0^-1) >= 14` is correct but conservative. The independently checked
exact value is

```text
min(21 S0^-1)=28.
```

This is a strengthening, not a repair to a false claim.

## 1. Source and transcription audit

The catalogue pages were fetched independently on 2026-07-24. Their exact
response bodies had:

| object | URL | bytes | raw SHA-256 |
|---|---|---:|---|
| `K12` | `https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/K12.html` | 8,962 | `163e03dfa9a4ab07675daa6e97a371bcfdb38f6195c311c63c699872b3e486c9` |
| `LAMBDA(F)` | `https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/KV32F.html` | 18,876 | `bb1db4504d7010dc093b24a8bcb00b042ea3879a220d669e8190d02abb6468ac` |

The live replay parses the Gram sections as untrusted text, checks the raw
hashes, and discards the HTML. No copied HTML is retained. The attributed
numeric matrices are frozen in `catalogue-data.json`; the source manifest
binds that file, each parsed Gram matrix, and the K12 similarity matrix by
SHA-256.

The verifier did not trust catalogue claims about determinant, minimum, or
kissing number. It recomputed:

| object | rank | determinant | even | positive definite | roots | norm-four vectors |
|---|---:|---:|---|---|---:|---:|
| `K12` | 12 | 729 | yes | exact positive LDL pivots | 0 | 756 |
| `LAMBDA(F)` | 32 | 1 | yes | exact positive LDL pivots | 0 | 146,880 |

The primary/source audit used Scheithauer for the Weil representation and
character convention, Sturm's original DOI for the Sturm theorem, and
Scharlau--Schulze-Pillot for modular and strongly modular definitions. Exact
URLs, access time, byte counts, and raw hashes are in
`theorem-source-manifest.json`. None of those raw documents is redistributed.

## 2. Smith groups and exact levels

Let `d_1 | ... | d_44` be the Smith invariants of `S`. From

```text
S G = 21 I
```

with integral `G`, every `d_i` divides squarefree `21`. If
`det(S)=3^a 7^b`, the cokernel is therefore

```text
A_S = (Z/3Z)^a orthogonal_sum (Z/7Z)^b
```

as an abelian group; the two primary parts are orthogonal because their
orders are coprime. Its exponent is

```text
e = 3^(a>0) 7^(b>0).
```

The exponent is the least positive integer making `e S^-1` integral. Since

```text
21 S^-1 = (21/e)(e S^-1)
```

is even and `21/e` is odd, `e S^-1` has even diagonal. Thus the theta level is
exactly `e`, not merely a divisor of `21`.

The complementary Smith invariants of `G=21S^-1` are the reversed values
`21/d_i`. Both primes occur in every endpoint row, so `G` always has exact
level `21`.

The independent table is:

| `h` | `(a,b)` | level of `S` | level of `G` | scalar character | Sturm exponent |
|---:|---:|---:|---:|---|---:|
| 9 | (2,0) | 3 | 21 | trivial | 7 |
| 21 | (1,1) | 21 | 21 | `chi_21` | 58 |
| 49 | (0,2) | 7 | 21 | trivial | 14 |
| 81 | (4,0) | 3 | 21 | trivial | 7 |
| 189 | (3,1) | 21 | 21 | `chi_21` | 58 |
| 441 | (2,2) | 21 | 21 | trivial | 58 |
| 729 | (6,0) | 3 | 21 | trivial | 7 |
| 1029 | (1,3) | 21 | 21 | `chi_21` | 58 |

## 3. Character and transformation conventions

The report uses

```text
q = exp(2 pi i tau)
theta_gamma(tau) = sum_(x in L+gamma) q^((x,x)/2).
```

For the finite bilinear pairing on `A_L=L*/L`, direct Poisson summation gives

```text
theta_gamma(tau+1)
  = exp(pi i (gamma,gamma)) theta_gamma(tau),

theta_gamma(-1/tau)
  = (-i tau)^22 / sqrt(det(S))
    * sum_delta exp(-2 pi i (gamma,delta)) theta_delta(tau).
```

The negative Fourier-kernel sign fixes which of the two dual Weil
representation conventions is in use. Under that convention, the report's
formula is consistent.

Scheithauer writes the odd-discriminant character as `(d/h)` after the
2-primary oddity term disappears. Every endpoint determinant satisfies
`h=1 mod 4`, so Kronecker quadratic reciprocity gives

```text
(d/h) = (h/d).
```

Consequently the five square determinants have trivial character and the
three `21` times square determinants have `chi_21(d)=(21/d)`, exactly as
reported.

Putting `z=21 tau` in ordinary Poisson summation gives

```text
theta_S(-1/(21 tau))
 = (21 tau/i)^22 / sqrt(h) * theta_(21S^-1)(tau).
```

This is a two-lattice exchange. It is not a Fricke eigenvalue for
`theta_S`.

## 4. Sturm bounds and their scope

The exact index formula is

```text
[SL_2(Z):Gamma_0(N)] = N product_(p|N) (1+1/p).
```

It gives indices `4`, `8`, and `32` at levels `3`, `7`, and `21`. At weight
22, flooring

```text
(22/12) [SL_2(Z):Gamma_0(N)]
```

gives `7`, `14`, and `58`. With the report's `q` convention these correspond
to checking norms through `14`, `28`, and `116`.

These bounds say that two forms already known to lie in the same
weight/level/character space are equal once the indicated initial
coefficients agree. They do not:

- force a particular root coefficient;
- classify all positive-definite lattices;
- determine mixed-level partial-dual cusp data; or
- encode the marked 231-vector frame.

No stronger conclusion was used.

## 5. Modularity veto

If a rank-44 lattice were isometric to its `N`-scaled dual, determinant
comparison would give

```text
h = det(N S^-1) = N^44/h,
h = N^22.
```

For exact levels `N=3,7,21`, none of the eight endpoint determinants is
`N^22`. Hence exact-level modularity is impossible in every row.

Strong `21`-modularity includes the full `21`-scaled-dual isometry, which
would instead require `h=21^22`; again every endpoint determinant fails.
Thus no strongly modular theta ring, partial-dual isometry, shadow bound, or
Fricke eigenform may be imported.

## 6. ADE controls

A fresh recursion found exactly 17 rank-44 orthogonal ADE forms using only
`A2`, `A6`, `A20`, `E6`, and `E8`. For each component, the verifier checked
the Cartan determinant, complete primal shell through norm four, exact
integrality/evenness of `21R^-1`, and the complete scaled-dual ball through
its first nonzero norm:

| component | `r(2)` | `r(4)` | `min(21R^-1)` |
|---|---:|---:|---:|
| `A2` | 6 | 0 | 14 |
| `A6` | 42 | 210 | 18 |
| `A20` | 420 | 35,910 | 20 |
| `E6` | 72 | 270 | 28 |
| `E8` | 240 | 2,160 | 42 |

All 17 decompositions and their product-theta coefficients are serialized in
`independent-results.json`. The eight representatives displayed in the
discovery report agree exactly. They are scalar-theta controls only; the
already public Wave 26--27 arguments exclude them as full endpoint origins.

## 7. Complete source-lattice enumeration

The enumeration is independent of the discovery implementation.

1. A floating heuristic chooses elementary integral row operations.
2. The resulting transform is accepted only after its determinant is checked
   to be `+1` or `-1` and `U S U^T` is reconstructed exactly.
3. An exact rational LDL factorization is converted into the identity

   ```text
   D * x^T (U S U^T) x = sum_i w_i ell_i(x)^2
   ```

   with positive integer `D`, positive integer `w_i`, and integral linear
   forms `ell_i`.
4. The checker reconstructs the entire scaled Gram matrix from those forms
   before enumeration.
5. At each recursion node, integer square roots and exact floor/ceiling
   divisions enumerate every integer satisfying the remaining closed
   inequality. Floating point never accepts or prunes a vector.

For K12, `D=56`; for `LAMBDA(F)`, `D=960`.

| object | recursion nodes | nonzero norm `<=4` vectors | shell counts |
|---|---:|---:|---|
| `K12` | 3,663 | 756 | `{4: 756}` |
| `LAMBDA(F)` | 15,053,011 | 146,880 | `{4: 146880}` |

The absence of a norm-two key is certified by complete coverage, not by a
failed search. The norm-four count for `LAMBDA(F)` is therefore an
independent bounded enumeration, not a value copied from the catalogue or
reconstructed only from modular forms.

## 8. The hostile control and its scaled dual

Set

```text
S0 = K12 orthogonal_sum LAMBDA(F).
```

The checked block data give

```text
rank(S0)=44,
det(S0)=729,
min(S0)=4,
r_S0(2)=0,
r_S0(4)=756+146880=147636.
```

For K12, the independently parsed similarity matrix satisfies the catalogue
identity exactly and yields an explicit determinant-one integral congruence

```text
3 K12^-1 isometric to K12.
```

Thus `min(3K12^-1)=4`. Since `LAMBDA(F)` is integral unimodular, its inverse
Gram is integrally congruent to itself and also has minimum four. Therefore

```text
21S0^-1
 = 7(3K12^-1) orthogonal_sum 21LAMBDA(F)^-1

min(21S0^-1) = min(7*4,21*4) = 28.
```

This verifies a rootless bare `S/G` control. It does not construct the
endpoint's marked norm-four subset, pairwise Gram alphabet, or cubic moment.

## 9. Discriminant quadratic form, not just determinant

For a 3-elementary Gram matrix `A`, the verifier constructs a basis of

```text
F_3^n / image(A mod 3)
```

and computes the scaled discriminant bilinear form `3A^-1 mod 3`. For K12
this gives

```text
A_K =
[[1,0,0,1,1,1],
 [0,1,0,1,1,1],
 [0,0,1,1,1,1],
 [1,1,1,1,0,0],
 [1,1,1,0,1,0],
 [1,1,1,0,0,1]].
```

For E6 the corresponding matrix is `[1]`. The checker emits the explicit
invertible matrix

```text
P =
[[1,0,0,2,2,2],
 [0,1,0,2,2,2],
 [0,0,1,2,2,2],
 [0,0,0,1,0,0],
 [0,0,0,0,1,0],
 [0,0,0,0,0,1]]
```

and verifies, entry by entry,

```text
P^T A_K P = I_6 mod 3.
```

Because the exponent is odd, `q(x)=B(x,x)/2`; hence this bilinear isometry is
an isometry of finite quadratic modules. It is stronger than comparing
dimension, group order, or determinant square class. Relabeling the group
algebra basis by this isometry conjugates the Weil representations.

The rooted comparator

```text
S1 = E6^6 orthogonal_sum E8
```

has the same rank, determinant, exact level, scalar character, finite
quadratic module, and Weil representation, but

```text
r_S1(2)=672,
r_S0(2)=0.
```

Both `21`-scaled duals have minimum 28. Therefore these bare lattice and
Weil data do not determine the zero-component root coefficient.

## 10. Failed-profile chronology

Failures were retained rather than hidden:

- PID 15524 began a full refresh/replay using the initial exact-rational LLL
  implementation. The calling wrapper timed out; the duplicated orphan was
  positively identified and stopped.
- PID 38220 profiled the same exact-rational preprocessing. It consumed about
  236 CPU seconds without reaching a reusable result and was stopped.
- PID 37072 used a faster basis-selection heuristic but retained rational
  arithmetic at every recursion node. Its wrapper timed out after 604
  seconds; because the profile had no persisted result target, the orphan was
  stopped.
- PID 31420 was a 34-second fraction-free smoke profile launched before
  progress telemetry and persisted output were installed. Its wrapper timed
  out and it was stopped.

None of these runs produced a mathematical result used here. They motivated
the fraction-free identity above. The successful persisted run was PID 19292,
started at `2026-07-23T19:54:04-07:00`; its complete progress stream is
retained separately from deterministic mathematical output.

## 11. Scope wall

The verified result is exactly:

```text
bare endpoint lattice/theta premises do not force a root,
and the full discriminant quadratic module plus rootless 21-scaled dual
still does not determine the root coefficient.
```

It is not:

```text
a primitive Z^231 embedding,
a 231-row projector frame,
a Q or B extension,
a Schur-square certificate,
an n3=708 realization or exclusion,
or a Conway-99 result.
```

Accordingly:

```text
theta/modular lane claims: VERIFIED
rootless h=729 bare S/G control: VERIFIED
root forced by these bare data: REFUTED
full endpoint compatibility: NOT CONSTRUCTED
n3=708: UNKNOWN
Conway-99: UNKNOWN
novelty: UNKNOWN
```
