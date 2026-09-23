# Wave 51 alternative-space scout and exact probe

```yaml
role: verifier
date_utc: 2026-07-27T18:45:00Z
git_commit: e4394aa9172fa97a6dafa9158148c2183603a01b
claim_label: VERIFIED
scope: exact feasibility of one balanced 174-cut rational endpoint relaxation
inputs: verification/wave51-rankone-cut-relaxation/input-freeze.sha256
method: verified cut reconstruction, numerical active-set scouting, exact RREF, exact substitution
command: .\.venv\Scripts\python.exe verification\wave51-rankone-cut-relaxation\probe.py --compute
outputs: verification/wave51-rankone-cut-relaxation/exact-result.json
limitations: rational aggregate witness only; full PSD, integrality, graph, and endpoint remain UNKNOWN
```

The smallest balanced cross-layer bundle was selected: 17 Wave45 cuts, 136
Wave47 first-direction cuts covering every frozen source/family pair, and 21
Wave49 cuts, together with the 170 Wave44 equations and standard bounds.

The result is exact feasibility over `Q`, not a solver status. The rank-209
rational witness satisfies all 170 equations and all 174 cuts; it has support
136, `h11/4=4158`, 66 tight cuts, and maximum denominator length 272 digits.
Therefore this fixed bundle cannot yield a Farkas contradiction.

The recommended continuation is an exact rational cutting-plane/facial-dual
loop. Proof-producing full-domain SAT/PB remains the complete but expensive
global route. Coherent configurations require exhaustive color closure without
hidden transitivity, and covering/interlacing should wait for a forced quotient.

No Wave46--Wave49 artifact was modified. Endpoint `n3=4158`, a strict upper
bound, graph construction, Conway-99, and novelty remain `UNKNOWN` or
`NOT_PROVED`.
