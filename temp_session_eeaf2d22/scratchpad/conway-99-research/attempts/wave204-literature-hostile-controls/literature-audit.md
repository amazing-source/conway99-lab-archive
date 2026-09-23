# Wave 204 exact-hypothesis primary-source audit

## Verdict

`CITED` for the theorem statements and hypothesis comparisons below.

`UNKNOWN` for the exact prism-free rank-11 endpoint and for Conway 99.
The search was focused rather than exhaustive. A source nonhit is not a
novelty, priority, or openness proof.

The 2025 peer-reviewed status paper by Cesarz and Woldar calls existence of
`srg(99,14,1,2)` an open problem. The April 2026 SAT paper reports bounded
experimental inability, not a model or nonexistence certificate. No
searched source through 2026-07-29 supplies a later resolution.

Primary status sources:

- Cesarz--Woldar, [On the automorphism group of a putative Conway
  99-graph](https://doi.org/10.5802/alco.418).
- Keramatipour, [Approaching the Conway-99 problem using SAT
  solvers](https://arxiv.org/abs/2604.23037).

## Theorem/hypothesis audit

| Paradigm and exact result | Hypothesis match | Decisive failure or consequence |
|---|---|---|
| Cellular sheaves and cohomological CSP: a cellular sheaf is a family of stalks and restriction maps on a cell complex; the CSP construction uses a specified presheaf of local partial solutions, and Cech cohomology can detect failure of a global section. Sources: [Curry](https://arxiv.org/abs/1303.3255), [O Conghaile](https://arxiv.org/abs/2206.15253). | The endpoint has local flag sets, and global existence can conceptually be phrased as a section problem. | Wave203 does not provide restriction maps on every overlap. Its third-block map is defined only when a flag exists and is only a partial injection. No functorial transition composition, coefficient group, or completeness theorem is available. Cohomology becomes applicable only after those maps are derived from the ternary columns. |
| Gain graphs: Zaslavsky labels oriented edges by a group, reversal inverts the gain, and a cycle is balanced exactly when its ordered gain product is the identity; balanced cycles obey the theta property. Source: [Biased graphs I](https://doi.org/10.1016/0095-8956(89)90063-4). | Directional nonedge labels suggest oriented edges. | No group-valued gain is derived. The Wave204 exact control has a global orientation and `b=0`, so orientation alone has no holonomy obstruction. Any nontrivial gain rule is an additional theorem, not terminology. |
| Frame/lifted-graphic representation recovery: for a 3-connected matroid with a biased-graph representation, Funk--Slilaty identify matrix representations with canonical gain-graph representations up to switching/scaling, aside from a stated degenerate case. Source: [Matrix representations of frame and lifted-graphic matroids correspond to gain functions](https://doi.org/10.1016/j.jctb.2022.02.007). | The endpoint columns define a simple ternary matroid. | No biased-graph/frame-matroid representation of that matroid, and no required 3-connectivity statement for such a representation, is known. The theorem cannot manufacture gains from an arbitrary ternary column matroid. |
| Symmetric strong circuit elimination: for a connected matroid, SSCE is equivalent to having no pair of skew circuits. Source: Cho--Oxley--Wang, [The symmetric strong circuit elimination property](https://arxiv.org/abs/2508.00132), Theorem 1.1 in the March 2026 revision. | Ordinary circuit elimination always holds for the represented ternary matroid. | The no-skew-circuits hypothesis is not proved. Ordinary elimination neither preserves two desired exterior elements nor bounds the resulting circuit weight or nonedge coverage. Thus no signed short-circuit amplification follows. |
| Orthogonal matroids over tracts: Jin--Kim give circuit/Wick cryptomorphisms and prove regularity equivalences for orthogonal matroids represented over specified fields. Source: [Orthogonal matroids over tracts](https://doi.org/10.1017/fms.2025.10085). | The endpoint lives in an orthogonal 11-space. | An ordinary vector matroid represented by singular points is not thereby an orthogonal matroid with a Wick function. The needed orthogonal-matroid structure has not been constructed. |
| Finite-field zero-tight frames: Greaves--Iverson--Jasper--Mixon characterize a zero-tight frame by total isotropy of the analysis image; Corollary 3.9 yields `n>=2d`. Source: [Frames over finite fields](https://arxiv.org/abs/2012.12977). | The 231 columns span dimension 11 and have zero frame operator. | It gives only `231>=22`. It does not see projectivity, the quadric, 99 star decompositions, or short circuits. |
| Classical tight fusion frames: equal-rank orthogonal projectors in a real/complex Hilbert space sum to a positive scalar multiple of the identity, enabling simplex/coherence bounds. Source: [Casazza--Fickus--Mixon--Wang--Zhou](https://doi.org/10.1016/j.acha.2010.05.002). | The 99 rank-six operators are self-adjoint idempotents of equal rank. | Their sum is zero in characteristic three. Positivity and the positive frame constant are absent, so the Hilbert-space bound is outside its hypotheses. No primary finite-field rank-six replacement was found. |
| Partial geometric designs: the concurrence matrix of a PGD has at most three distinct eigenvalues, all nonnegative integers. Source: Song--Tranel, [Partial geometric designs having circulant concurrence matrices](https://arxiv.org/abs/2106.11047). | The older Wave182 all-nine equality face had a feasible two-concurrence PGD/PBIBD parameter set and the required nonnegative spectrum. | The theorem supplies feasibility structure, not exclusion. More importantly, the current Wave203 `b=0` face does not prove that block-side intersections depend only on one association relation, so coherent-configuration module bounds do not start. |
| Polar caps/partial ovoids: Blokhuis--Moorhouse derive p-rank bounds for caps and ovoids in finite orthogonal spaces. Source: [Some p-ranks related to orthogonal spaces](https://www.ericmoorhouse.org/pub/orthog.pdf), with the authors' [published erratum notice](https://ericmoorhouse.org/pub/orthog.html). | All 231 endpoint columns are singular projective points. | The selected set has 3,696 orthogonal pairs, so it is not a partial ovoid/polar cap under the required no-shared-generator condition. Ordinary projective cap language is insufficient for those bounds. |
| Hilton--Milner: if `k<=n/2`, a pairwise-intersecting family of `k`-subsets of `[n]` with empty total intersection has size at most `C(n-1,k-1)-C(n-1-k,k-1)+1`. Source: Bulavka--Woodroofe, [A short proof of the Hilton--Milner theorem](https://doi.org/10.4153/S000843952510132X), Theorem 1. | With `(n,k)=(7,3)`, the hypotheses hold and the bound is 13. | The local systems can attain equality: the Wave204 certificate places the exact 13-member `H` family at all 99 centers. The theorem has no cross-center conclusion. The [degree version](https://arxiv.org/abs/1703.03896) assumes `n` sufficiently large relative to `k` and supplies no applicable `n=7` refinement. |
| Terwilliger SDP: Schrijver block-diagonalizes the complex `C*` Terwilliger algebra of the binary Hamming cube and obtains PSD constraints on triple-distribution variables. Source: [New code upper bounds from the Terwilliger algebra and semidefinite programming](https://ir.cwi.nl/pub/14098/14098B.pdf). | Higher-order orbit moments are the right kind of missing information. | The theorem is for binary Hamming codes with that explicit `C*` algebra. The endpoint is a characteristic-three polar/incidence configuration with 99 distinguished decompositions; no matching orbit algebra or exact PSD certificate has been constructed. |
| General `k`-point bounds: de Laat--Machado--de Oliveira Filho--Vallentin build 4-, 5-, and 6-point SDP bounds for real equiangular lines as levels of a packing hierarchy. Source: [k-point semidefinite programming bounds for equiangular lines](https://doi.org/10.1007/s10107-021-01638-x). | The unrestricted graph has a real equiangular-line representation, so this paradigm can in principle retain higher-order data. | The frozen rank-11 endpoint columns are over `F_3`, singular, and have both zero and nonzero inner products; they are not the real equiangular code in the theorem. A new exact translation would be required. |
| Multivariate Q-polynomial bounds: Shi--Wang--Sole assume a weakly metric multivariate Q-polynomial association scheme and derive Delsarte/Rao-type bounds. Source: [Codes and designs in multivariate Q-polynomial association schemes](https://arxiv.org/abs/2605.17122). | The endpoint has several natural relations. | Those relations have not been proved to form the required multivariate Q-polynomial scheme. The source does not turn partial local incidence data into one. |

## Literature boundary

No retained theorem simultaneously uses:

1. the 231 singular projective ternary columns in dimension 11;
2. the zero frame operator;
3. all 99 seven-column star decompositions;
4. the canonical quadrilateral relation;
5. the exact-three local Hilton--Milner fibers; and
6. global overlap transitions.

The precise missing bridge is therefore not another name for the local
data. It is a derived transition law or higher-order module identity that
survives the exact `b=0` hostile skeleton and necessarily uses the ternary
columns or actual SRG common-neighbor geometry.
