# Audit of Reimbayev, arXiv:2608.19410v1 (order-seven census in srg(n,k,1,2)) — 2026-09-21

Scope: figure-free audit of the 208 printed frequency formulas, specialised to (n,k)=(99,14), against the
independently derived order-7 affine family of `YesterdaysLemon/conway-99-research` (wave 23:
712×208 orbit-refined 6→7 extension system, rank 207, counts affine in (n3, h11)).

## Method
1. Parsed the TeX source (`The_Subgraphs_of_Order_Seven.tex`, flalign block) into exact sympy expressions
   (`r7_check/parse_r7.py`). All 208 are affine in (n3, z11).
2. Figure-free identity: Σ_i z_i must equal C(n,7) on the srg locus n = k(k−2)/2 + k + 1.
3. Value matching at n3 = 705: each printed formula's (value at z11=1412, slope 4·c_z11) vs the repo family
   records (`attempts/wave23-weighted-extensions/affine-witness.json`) — `r7_check/match705.py`.
4. Full three-coefficient check: the repo system was rebuilt with symbolic n3 (exact QQ arithmetic,
   `r7_check/family_n3.py`), giving every class count as p + q·n3 + r·z (z = h11/4).

## Findings
- As printed, the n3- and z11-coefficients of Σz_i vanish on the srg locus (coefficient k²−2n+2 → 0),
  but the constant term is short: Σz_i − C(n,7) = −nk(k−2)(k−4)(19k⁴−456k³+4484k²−21752k+42008)/168,
  i.e. −94 034 160 at (99,14).
- Exactly four printed formulas match no repo class, and exactly four repo classes are unmatched.
  Resolving them gives simple typos:
  | formula | printed | corrected |
  |---|---|---|
  | z_21 | nk(k−2)(k−3)(k−4) − 2n3 − z11/2 | nk(k−2)(k−4) − 2n3 − z11/2  (drop the factor (k−3)) |
  | z_80, z_84 | ½nk(k−2)(k−4)(2k−7) + 16n3 + 3z11/2 | ½nk(k−2)(k−4)(2k−17) + 16n3 + 3z11/2 |
  | z_176 | (1/84)nk(k−2)(k−4)(k⁴−24k³+236k²−1136k+2264) + 6(5k−34)n3 − 9z11 | same with 1/8 instead of 1/84 |
  (z_80 and z_84 are two distinct classes with identical frequency; the repo also has two classes with the
  same affine count at (99,14): masks 42232 and 44337.)
- With these four corrections: Σz_i = C(n,7) holds identically in k on the srg locus, and all 208 corrected
  formulas coincide with the 208 repo classes in all three coefficients (a, b_n3, c_z11) at (99,14);
  every repo class is hit exactly once (up to the two identical-count pairs).
- Consequence for Conway-99: the corrected order-7 census imposes only z_1,z_2,z_3 ≥ 0 and integrality, i.e.
  0 ≤ n3 ≤ 4158, 2n3 ≤ z11 ≤ 4n3, 4 | z11. Feasible set = all n3 in [0,4158] (no mod-3 condition even).
  Intersected with the repo's rigorous 708 ≤ n3 ≤ 4158 it changes nothing. The order-7 route is closed
  (as the repo's wave 22/23/43/44 had already concluded with its own system).
- Note: Reimbayev's z11 equals the repo's h11 (both give the 353 admissible values 1412..2820 at n3=705).

## Artifacts
`scratchpad/r7_check/`: parse_r7.py, spec99.json, match705.py, corrected.py, family_n3.py, repo_family_affine.json,
feasible_n3_z11.json. arXiv source: `scratchpad/arxiv/r7/`.
