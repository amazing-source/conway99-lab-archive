# Wave 41 multiedge rank packing: verifier report

```yaml
role: verifier
date_utc: 2026-07-27T05:25:50Z
git_commit: 4f1754a28723a8e0e4ea3025312cd264b1b117d2
claim_label: VERIFIED
verdict: VERIFIED_SCOPED
scope: all-odd edge types 1^6, 1^3+3, 1+5, and 3+3
inputs: verification/wave41-multiedge-rank-packing/input-freeze.sha256
method: independent exact F7 Schur obstruction plus complete matching certificates
command: .\.venv\Scripts\python.exe -B -m unittest discover -s verification\wave41-multiedge-rank-packing -p "test_*.py" -v
outputs: verification/wave41-multiedge-rank-packing/package-manifest.sha256
limitations: seven even-part types remain UNKNOWN; universal verified floor remains 25
```

## Verdict

The following implication is independently **VERIFIED_SCOPED**:

```text
if a hypothetical srg(99,14,1,2) contains an edge of type
1^6, 1^3+3, 1+5, or 3+3, then rank_F7(M)>=26.
```

This does not raise the universal floor. The seven types containing an even
part remain `UNKNOWN`, so the universal verified result stays
`rank_F7(M)>=25`.

## Independent certificate

The verifier froze its protocol and implementation before opening discovery.
For each all-odd type, the 27-block has rank 25 and every possible third-fibre
border column lies in its image. Exact singular Schur elimination reduces
rank 25 to a zero-residual equality.

The residual diagonal yields a complete twelve-by-twelve bipartite matching
condition. Exact matching numbers, with equal-size minimum vertex-cover
certificates, are:

```text
1^6: 0,  1^3+3: 6,  1+5: 10,  3+3: 12.
```

Only `3+3` has a perfect candidate, uniquely. Its full Schur target contains
field entries forbidden in a perfect-matching block, so rank 25 is impossible
there as well.

The verifier also independently checked:

- the complete 39-block construction and all `10,395` labelled internal
  perfect matchings;
- `rank(K39)=1+rank(3I-A_core)`;
- `rank(NMN^T)=rank(M)` over `F_7`;
- the universal three-dimensional compact kernel and its annihilation by all
  60 outside columns;
- discovery's generic rank-28 and triangle-free rank-29 controls;
- deterministic regeneration and 16 hostile tests.

## Discovery discrepancy

The mathematical candidate agrees. One ancillary field is refuted:
`exact-results.json` says “five even-part edge types,” but the correct number
is seven. The discovery README is already consistent with seven. This typo
does not affect the scoped theorem.

Full evidence is in
`verification/wave41-multiedge-rank-packing/audit.md`.
