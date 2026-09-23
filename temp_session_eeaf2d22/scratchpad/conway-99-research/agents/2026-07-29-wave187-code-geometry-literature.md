# Wave 187 literature report: no available theorem sees the full zero-fusion-frame cap

```yaml
role: literature
date_utc: 2026-07-29T01:34:46Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: CITED
scope: >-
  Exact-hypothesis literature audit for the conditional rank-11 endpoint:
  a projective ternary [231,11] 3-divisible code whose columns are singular
  points of Q(10,3), have dual distance at least four and zero frame, carry
  99 seven-column full-support star relations, and whose dual has at least
  8,778 words of weights four through nine.
inputs:
  - path: verification/wave186-star-translation-cover-verifier/package-manifest.sha256
    sha256: edb833cbed8706f164199d4ecab8ff26757c54dfc46915819e150e17d73fef76
  - path: verification/wave186-star-translation-cover-verifier/README.md
    sha256: 6f269a78d6bf43eccd367d1f9a885cd109ca52278f0928682ebfc372b48fc557
  - path: agents/2026-07-28-wave175-polar-literature.md
    sha256: 79a8fc87f396f081620d30a0a0145c4e21ae592cad8ea3dee1e76ec052c8fe29
  - path: agents/2026-07-28-wave177-divisible-code-literature.md
    sha256: 4c5336105d875c4ca841543399ff3e165a29ce476e487df875751442b4ecc484
  - https://arxiv.org/abs/2012.12977
  - https://arxiv.org/abs/2505.12175
  - https://arxiv.org/abs/2101.11756
  - https://doi.org/10.1016/j.acha.2010.05.002
  - https://arxiv.org/abs/1707.00650
  - https://arxiv.org/abs/1912.10147
  - https://doi.org/10.1016/S0012-365X(02)00683-0
  - https://arxiv.org/abs/2301.09457
  - https://arxiv.org/abs/2011.11101
  - https://arxiv.org/abs/1807.05164
  - https://arxiv.org/abs/1409.0779
  - https://arxiv.org/abs/2504.21797
  - https://doi.org/10.1023/A:1022477715988
method: >-
  Searched current primary mathematical sources in finite-field frame and
  projective-design theory, projective divisible codes, strong blocking
  sets, low-weight code bounds, and representable-matroid circuit theory.
  For every theorem retained below, compared each structural hypothesis
  with the frozen endpoint. No construction or exhaustive search was run.
command: >-
  Primary-source web/PDF inspection plus exact hand substitution of
  q=3, n=231, k=11, d_perp>=4, and the verified Wave 186 circuit counts.
outputs: []
limitations:
  - This is a targeted theorem audit, not an exhaustive proof of absence from the literature.
  - Source noncoverage is not evidence of mathematical nonexistence.
  - The endpoint and Conway 99 remain UNKNOWN.
```

## Verdict

`CITED`: the theorem statements and failures below are source-backed.

`UNKNOWN`: no inspected theorem proves existence or nonexistence of the
frozen endpoint. In particular, no theorem found simultaneously uses the
singular quadric, dual distance four, zero frame, 99 star relations, and
the lower bound on short dual words.

## Frozen target

Assume

```text
n3=4158, P=0, rank_F3(D)=11.
```

The exact object to exclude is:

```text
V: nondegenerate orthogonal 11-space over F_3
Z={z_T}: 231 spanning, singular, projectively distinct vectors
W=row/synthesis code: ternary [231,11], 3-divisible and self-orthogonal
d(W^perp)>=4
sum_T z_T tensor z_T=0
induced polar graph on Z: 32-regular, with 3696 selected orthogonal pairs
```

There are additionally 99 distinguished stars. For each original point
`x`, the seven columns through `x` have Gram matrix `J_7-I_7`, span a
nondegenerate six-space `E_x`, and have exactly the one full-support
relation

```text
sum_(T contains x) z_T=0.
```

Writing

```text
P_x=-sum_(T contains x) z_T tensor z_T,
```

gives rank-six self-adjoint idempotents with

```text
P_x^2=P_x, rank(P_x)=6, and sum_x P_x=0.
```

Wave 186 independently verifies

```text
Q>=3696,
projective circuits of weights 4..9 >=4389,
B_4+B_5+B_6+B_7+B_8+B_9>=8778.
```

These are necessary conditions, not an existence certificate.

## Theorem audit

| Paradigm and exact result | Hypotheses met | Decisive failure or consequence |
|---|---|---|
| Finite-field frames: Corollary 3.9 of [Greaves--Iverson--Jasper--Mixon](https://arxiv.org/abs/2012.12977) says a frame is 0-tight iff its analysis image is totally isotropic; hence a `d x n` 0-tight frame needs `n>=2d`. | Yes: the columns span `V` and their frame operator is zero. | Gives only `231>=22`. It has no cap, quadric, polar-degree, star, or circuit-count conclusion. |
| Finite-field projective 2-designs: Definition 15 and Theorem 16 of [Iverson--King--Mixon](https://arxiv.org/abs/2101.11756) require both `{x_i}` and `{x_i tensor x_i}` to be tight frames (in their Hermitian finite-field model), and then give `n>=d^2`. | Equal singular norm and first-order zero tightness resemble only part of the definition. | No second-tensor tight-frame identity is known; the model is Hermitian over `F_(q^2)`, while the endpoint is orthogonal over `F_3`. The zero-frame identity alone is not a projective 2-design. |
| Current finite-field ETF criterion: [Jorquera--King](https://arxiv.org/abs/2505.12175) characterize when an equiangular system is tight via Welch saturation plus a triple-product condition. | The target is an equal-norm zero-tight frame. | It is not equiangular: squared off-diagonal inner products take both `0` and `1`, with 3,696 orthogonal selected pairs. Thus neither the criterion nor its design consequences starts. |
| Classical tight fusion frames: [Casazza--Fickus--Mixon--Wang--Zhou](https://doi.org/10.1016/j.acha.2010.05.002) characterize equal-rank orthogonal projectors over finite-dimensional Hilbert spaces whose sum is a scalar multiple of the identity. | The 99 operators `P_x` are equal-rank orthogonal projectors algebraically, and their sum is scalar (`0`). | The theorem is over real/complex Hilbert spaces and uses a positive frame constant. Characteristic-three cancellation `sum P_x=0` is outside its hypotheses. |
| Divisible lengths: Theorem 1 of [Kiermaier--Kurz](https://arxiv.org/abs/1707.00650) says a full-length `q^r`-divisible code of length `n` exists iff the leading coefficient of the `S_q(r)`-adic expansion of `n` is nonnegative. | `q=3`, `r=1`, and `W` is full-length and 3-divisible. | Here `S_3(1)=(4,3)` and `231=0*4+77*3`, so the theorem permits the length. It fixes neither dimension 11 nor projectivity, cap, quadric, zero frame, stars, or `B_4+...+B_9`. |
| Projective divisible-code length theory: [Heinlein--Honold--Kiermaier--Kurz--Wassermann](https://arxiv.org/abs/1912.10147) identifies simple divisible point sets with projective divisible codes and surveys length exclusions. | Projectivity and 3-divisibility hold. | The projective length problem is only partially classified in general, and the cited restrictions do not address the fixed dimension or any of the four extra endpoint structures. |
| Divisible primal/dual distance: [Duursma](https://doi.org/10.1016/S0012-365X(02)00683-0) proves `d+c d_perp <= n+c(c+1)` for a `c`-divisible code. | `c=3`, `n=231`, and `d_perp>=4`. | It yields at best `d<=231`; this is vacuous. The theorem bounds minimum distances, not the number of dual words of weights 4 through 9. |
| Minimal codes and strong blocking sets: Theorem 2.15 of [Bishnoi--D'haeseleer--Gijswijt--Potukuchi](https://arxiv.org/abs/2301.09457) states that a nondegenerate code is minimal iff its generator columns form a strong blocking set; [Bartoli--Cossidente--Marino--Pavese](https://arxiv.org/abs/2011.11101) define this by requiring every hyperplane intersection to span that hyperplane. | The target is nondegenerate and projective. | Cap, 3-divisibility, zero frame, and the 99 local relations do not imply the required hyperplane-spanning property. No minimality proof is available, so the strong-blocking bounds cannot be imported. |
| Near-minimum circuit count: [Gurjar--Vishnoi](https://arxiv.org/abs/1807.05164) give an `m^{O(alpha^2)}` bound for circuits of size at most `alpha` times girth in a **regular** matroid. | The target matroid is simple ternary of girth four. | Regularity is not established and does not follow from ternary representability. Even under regularity, the asymptotic hidden-exponent bound would not contradict 4,389 circuits on 231 elements. |
| Matroid growth and excluded minors: [Nelson](https://arxiv.org/abs/1409.0779) gives growth-rate results for minor-closed classes with specified exclusions. | The columns define a simple rank-11 ternary matroid. | A single represented matroid is not a minor-closed class, and no required excluded minor is known. The theorem controls element count, not short-circuit multiplicity. |
| High-girth representable matroids: [Davies et al.](https://arxiv.org/abs/2504.21797) force graphic/cographic minors from sufficiently large girth. | Ternary representability holds. | The endpoint has girth exactly four, the opposite regime. |
| Polar-space cap bounds: [Blokhuis--Moorhouse](https://doi.org/10.1023/A:1022477715988) bound a cap in a finite orthogonal space in the polar sense: no two points share a generator. | All 231 points are singular. | The target has 3,696 orthogonal selected pairs, so it is not a polar cap/partial ovoid. It is only an ordinary projective cap: no three selected points are ambient-collinear. |

## Low-weight dual words: why the standard bounds do not bite

Let `H=W^perp`, so `H` has parameters `[231,220,d_H>=4]_3`.
The radius-one Hamming bound is

```text
3^220 * (1+2*231) <= 3^231,
```

or merely

```text
463 <= 177147.
```

It is extremely slack and contains no coefficient-wise upper bound on
`B_4+...+B_9`.

Assmus--Mattson-type conclusions require an upper bound on the number of
nonzero weights in a specified range. The Wave 186 result instead gives a
lower bound on the number of words across six weights. The full primal and
dual spectra are not known, so the design hypothesis cannot be checked.
Even if it could, the theorem would produce support designs rather than an
upper bound contradicting `8778`.

Likewise, ordinary MacWilliams/Pless identities can be used to build a new
linear program, but the literature theorem itself does not turn the lower
bound `8778` into an exclusion. The previously proposed complete ordinary
weight enumerator was refuted as a forced lift, so it cannot be substituted
as if verified.

## The useful new reframe

The 99 star spaces form a characteristic-three analogue of a **zero-tight
fusion frame**:

```text
99 nondegenerate six-spaces E_x in an orthogonal 11-space,
orthogonal projectors P_x of rank 6,
sum_x P_x=0.
```

This is materially stronger than viewing the 231 columns only as a cap.
It also retains the graph through the trace Gram matrix

```text
G_P=(tr(P_x P_y))=2 B L B^T,
rank_F3(G_P)<=65.
```

Classical fusion-frame simplex and coherence bounds use positivity over
`R` or `C`; they do not survive the zero scalar in characteristic three.
Finite-field frame theory handles rank-one zero-tight frames, but the
inspected sources do not supply the needed rank-six fusion-frame theorem.

The most promising non-brute-force continuation is therefore not another
generic cap or code search. It is to develop a finite-field fusion-frame
or operator-design obstruction that additionally uses:

1. each `P_x` decomposes into the seven singular rank-one operators of a
   full-support simplex;
2. every column occurs in exactly three such decompositions;
3. `G_P` is constrained by the endpoint incidence matrix `B L B^T`; and
4. the same decompositions force at least 4,389 projective circuits of
   sizes at most nine.

No inspected theorem currently combines even items 1--3, let alone the
short-circuit lower bound. That conjunction is the precise `UNKNOWN`
boundary, not a literature exclusion.
