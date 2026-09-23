# Wave 183 root-support/girth verification

Verdict: **VERIFIED_WITH_SCOPE**.

This package independently verifies the Wave 183 deductions conditional on
the Wave 181 equality case and the already verified Wave 182 root identities.
It does not enumerate graphs or search for candidate configurations.

The checked conclusions are:

- every pair of vertices in one root support has at most one common neighbor
  inside that support;
- the unordered two-path injection excludes support multiplicities 9 and 10;
- the cubic multiplicity-8 case forces at least three vertex-disjoint
  triangles on eight vertices and is therefore impossible;
- the only remaining induced support graphs are `5K1`, `3K2`, and `C7`;
- the number of projective roots is between 297 and 415, with
  `7R-2079=2n5+n6`;
- the characteristic-three frame splits as
  `sum_(m=7) r tensor r = sum_(m=5) r tensor r`.

No contradiction is obtained from the split frame.  The Wave 181 equality
case, rank 11, and the original endpoint remain **UNKNOWN**.

Reproduce:

```powershell
python verification/wave183-root-support-girth-verifier/independent_check.py
python -m unittest verification.wave183-root-support-girth-verifier.test_independent_check
```

The proof audit is in `audit.md`; hashes are frozen in
`package-manifest.sha256`.
