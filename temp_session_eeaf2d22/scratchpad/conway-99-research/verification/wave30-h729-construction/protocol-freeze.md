# Wave 30 h729 construction: preinspection protocol freeze

## Role and scope

- Role: blind independent computational verifier.
- Frozen repository commit at hashing time:
  `ae8fd70baaeb35302f957653e20ad710e5e77281`.
- The construction report and every file under
  `attempts/wave30-h729-construction/` were hashed before their contents or
  checker internals were inspected.
- A conservative dependency superset was also frozen before inspection:
  the central statement/status ledgers, the Wave 28 glue/theta packages, the
  Wave 29 endpoint package, and the Wave 30 general-h729 package.
- Verification is restricted to the submitted bare lattice objects `S` and
  `G`. It does not certify any `Q`, `B`, `X`, `M`, `W`, frame, Schur-complement,
  or graph object. The `n3=708` endpoint and Conway's 99-graph problem remain
  `UNKNOWN`.
- Discovery code and prose are untrusted inputs. The verifier will parse the
  raw machine-readable matrices/certificates and use a separately written
  implementation.

## Required independent checks

1. Parse all submitted matrices and certificates without importing discovery
   code.
2. Check dimensions, symmetry, integrality, even diagonal, exact positive
   definiteness, and determinants.
3. Reconstruct all five claimed 2-neighbor transitions and prove the exact
   primitive/full-rank index relations.
4. Exhaustively reproduce norm-2 counts `240 -> 112 -> 48 -> 20 -> 6 -> 0`.
5. Prove the final rank-20 lattice has minimum `4` and exactly `5076` norm-4
   vectors.
6. Check that `3*T20^-1` and `21*T20^-1` are even integral.
7. Independently check the Leech Gram matrix invariants, minimum, and
   rootlessness.
8. Check the direct sum has rank `44`, determinant `729`, minimum `4`, and no
   roots.
9. Compute `G = 21*S^-1`, check it is even integral, and verify `S*G=21I`.
10. Attack basis dependence, LLL/canonicalization assumptions, enumeration
    coverage, and deleted-premise variants.

## SHA-256 freeze

Each line is `sha256  byte_count  repository-relative-path`.

```text
3c1354a04f33602c6e339875c8de4f77d1874bd6e8f83dbcb712b91717d6c1ff  19163  agents/2026-07-24-wave28-glue-discriminant.md
8783be7e730306637ed863b4d9fbe8f4193ad756e7ec86d697c7407688a5423a  16356  agents/2026-07-24-wave28-theta-modular.md
e6ae61331a54d53f2a98712296ebac855f45b46de32ff2ec4d85018f2d8a5045  13485  agents/2026-07-24-wave29-s0-frame-exclusion.md
1bc63f569600bca88e12c977a0bd94ecdd03aa5f3fd8c4f203d4778fbec78efa  15875  agents/2026-07-24-wave30-general-h729.md
479ed105825ea2b2a0802c34fcc332b8dc1420b27966bec41053702f3212451f  10947  agents/2026-07-24-wave30-h729-construction.md
5ac509e960c3b2e5e8b949aa88958f9bce6ae7b5b34a7baad140d20d3487bcbb  819  attempts/wave28-glue-discriminant/artifact-manifest.sha256
9b58940cf9f3d732593e03bde69974b56145950f28e5012ccc0735082dd2cf51  12875  attempts/wave28-glue-discriminant/exact_check.py
13a3bb8f83c56ff899991362736089b772114cff840a2cb20d68845e231b3cf1  20212  attempts/wave28-glue-discriminant/exact-results.json
a976651e93ab1b4c9e87735fc5a51d22baa79da2259d99e08dfe4334227dd2d0  2928  attempts/wave28-glue-discriminant/failed-routes.md
505cf42659e61d9340c6191b9a484c7eb064b02a3ecb1be1f8597a245095b7d2  693  attempts/wave28-glue-discriminant/input-freeze.sha256
bb12cb91b9db78231a447c2e3f6adee7d3b4fe3e6e21f96beaa7c3057f0a2a67  3759  attempts/wave28-glue-discriminant/run-report.yaml
d2617492eaa41905b72e850e1027db10e32aa04bc92d78e1751271151711676a  6874  attempts/wave28-glue-discriminant/test_exact_check.py
1a7a68019241b5f83b4f9154a1361d1ebcf8da72d287175a13e8400b83b07692  908  attempts/wave28-theta-modular/artifact-manifest.sha256
8185f7c483dc5dfa7ca31dd60058ee48ef6cdf8b29074c4f02f9dfcccdb095e1  31526  attempts/wave28-theta-modular/exact_check.py
9d7b1ffcc0cef2441aa6dd381228abaa1018f721594e930cdd7227c0647470d6  15963  attempts/wave28-theta-modular/exact-results.json
75e6bdbc7840f02c7a50497cf028144d76dd2e2a4f2b24d24fa83625477c49b9  3139  attempts/wave28-theta-modular/failed-routes.md
42dda26e43b0512c9d929cae9877fbee9befb647450604d735d3ad5205cadcc8  113  attempts/wave28-theta-modular/input-freeze.sha256
b8df638151623436079fca5dadc86fc6a255375cd02c23841c483550b93d5565  2849  attempts/wave28-theta-modular/run-report.yaml
cad0b503878708bbaf49041b0325e54abe7a5180e05e3387c6e98e5f51bb555a  264  attempts/wave28-theta-modular/source-freeze.sha256
16dff2aa4c122e818c0898f604e12b2a67967591f528d048ccfe312f7bc4e1bc  6573  attempts/wave28-theta-modular/test_exact_check.py
8cb5b0198ac9e787a8234820e648626dc27f900f53b7511068d5442d06d7a39b  826  attempts/wave29-s0-frame-exclusion/artifact-manifest.sha256
6a31c4ae0b2c994f4c715ba5118e3b25a052e8b3fc99dea88ea794cb7d9d8dce  22409  attempts/wave29-s0-frame-exclusion/exact_check.py
7a85c5321b5e91365c246dff7bae9264cc82494da5c866b1b351511099f6638c  12140  attempts/wave29-s0-frame-exclusion/exact-results.json
bba05cd84c1ac35284c9f8af7d8dd32480f11158ada69195b1bfa61892cad234  3198  attempts/wave29-s0-frame-exclusion/failed-routes.md
5ddbd25498cf9f7048705e190f81e203d3d21efcc72d1750de2235e419fda1c4  714  attempts/wave29-s0-frame-exclusion/input-freeze.sha256
91fba9dad3bb9d906eb69c06ca97be82ff804296dcb010be3f6749e67beba286  3068  attempts/wave29-s0-frame-exclusion/run-report.yaml
26dff5f61d6bc6e3d752f596f5c318baee47358f27552e4a0b7e4c3e8a6a5c4f  8038  attempts/wave29-s0-frame-exclusion/test_exact_check.py
29cbbdff1ab167b436db725130d830bfd047beb1c4ba834c51b5a33c3aed690a  784  attempts/wave30-general-h729/artifact-manifest.sha256
ed8edcbb0febde6d6fbd57776b7696402f832421fa11fb1984fcd57c8369eaff  20274  attempts/wave30-general-h729/exact_check.py
93cc1633d0b25d5f3daecd4c49cbc3b2dc3f754576a3cd5c9364c729a79a7698  16112  attempts/wave30-general-h729/exact-results.json
397f74c75a8ae24bedd26fea41c0fb82d03c6611a87627e86aeb29244a586006  2848  attempts/wave30-general-h729/failed-routes.md
a07c703b20237441b221e13c68be885d01db180871b8496af5d7204e2587793b  599  attempts/wave30-general-h729/input-freeze.sha256
77232c06827c4c62e7dc6f5380cc4ebe2a3c6d5496fe8c3592589986089e416f  2590  attempts/wave30-general-h729/run-report.yaml
9075d5fd77253850ba09c4655d9cbab135eb32fdd36638dc4aa9051fa49898a2  9245  attempts/wave30-general-h729/test_exact_check.py
d70d00c8a278bcd8710cf7c8d53c679e05509db2b08bc7ad2f11af4bbe6e564a  819  attempts/wave30-h729-construction/artifact-manifest.sha256
6415f40948f5033fff47c1f090776f417ac0a8cd0adf589cb5d4aa66cbb7d852  21506  attempts/wave30-h729-construction/exact_check.py
0d3723ba4c185dc7865858d16bfc6ada99fd87b4e21da616ef1b1d1ad6b67e11  168059  attempts/wave30-h729-construction/exact-results.json
51d6a9681b5fdddc6dffe70baf1f80f03a2b652440ebd5506cfce0dced440115  3703  attempts/wave30-h729-construction/failed-routes.md
895ce37d214acf92aa5c4f2bd1eaaadaa8ef625045e31479b25eb4f42caf17fe  363  attempts/wave30-h729-construction/input-freeze.sha256
bfe878cc209ec0699310bb81fd25f720babc73a9ccb326aa660c323629e53dcd  3130  attempts/wave30-h729-construction/run-report.yaml
0bd86cadac900ddcfb34d6c76bfa827fe94cc001ef75d1c9c9e6b008d7373cd5  7722  attempts/wave30-h729-construction/test_exact_check.py
ca6754e22fce3ac108bea4a10188f14cebed9aa2d922894b0640996f23cbaa58  86054  CLAIMS.yaml
7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58  4589  CONJECTURE.md
23fa1a25521b8e78730e11bb88f05f096a8e1137430169be701af4abaa0b6af6  84803  OBLIGATIONS.yaml
5b699e36e16c82c7a132a6a0ba236cca830f6522de31874b1fe6db17c0e87bae  101015  STATUS.yaml
f1da76840c7db2ef0974415f737a211af04a8c77af0bb6ac8e9997d8c662d56f  73404  STRUCTURE.md
d25e446673fcb80cb21afc87cd1f271c4c5e4d6d36f6ec6a564e7d6fbb2296a7  497  verification/wave28-glue-discriminant/artifact-manifest.sha256
5c1dc7978d571a9471837b45a36663c7c457b6434800776501e4967146956b86  17670  verification/wave28-glue-discriminant/audit.md
787884dc0278c1280f236e71783cc883c314e898bcf7ac3c2a3a4aacb361aa4c  18077  verification/wave28-glue-discriminant/independent_check.py
0d15724c772300072c565030e88080c05333af8f75241b633d5801e5c4ac83fe  29056  verification/wave28-glue-discriminant/independent-results.json
801bc632810035ac95724866fcaf63fe476a002b617ccc4bb5844b2f7300c4cc  10942  verification/wave28-glue-discriminant/test_independent_check.py
50a5e3d4b5bb066b4b281c80d6d2caa0906afc21b9de99e12731177f661c6fed  867  verification/wave28-theta-modular/artifact-manifest.sha256
adc90e404735ca147bc0a5418974d8af0bde71c4ddc2dc62a8c07dee670dbfeb  14569  verification/wave28-theta-modular/audit.md
0bbf9d7b21ca3f7e5226df1683350772b407773d133350fb20fe5eae232e15f2  16229  verification/wave28-theta-modular/catalogue-data.json
513efd1a915bc14adc3003c41e6758839375d9a36a0055f08faa56417c942b18  62149  verification/wave28-theta-modular/independent_check.py
24298ae282c7baa252a39ffe96fc37b7c696cb51f14b9ddea2318a59b4335b7f  28901  verification/wave28-theta-modular/independent-results.json
16af82dcc5db7d5664f0a68ba855e4e60bd79c7b401a4575568e6fd8c6fac640  2581  verification/wave28-theta-modular/run-report.yaml
9229bacd7dcd52ccb6c2da4162507f11b48c93c028f31840884cbdca50a619ed  1661  verification/wave28-theta-modular/source-manifest.json
b1cf879f8eb4452c1ac2f168ef6030022f54e1500a6b242acb2bbc7cbfb8ca83  10753  verification/wave28-theta-modular/test_independent_check.py
47ab1b9d7cf1c49aa53a905863d64243ab087bbe331c1ec6e845dc06afc446fd  2074  verification/wave28-theta-modular/theorem-source-manifest.json
6a62209abbca6403dee7b9ebf83edbdccd5466a278957ab9d63f37bcd3f08cf8  596  verification/wave29-s0-frame-exclusion/artifact-manifest.sha256
dbdcb88bf309cbfa47a42b9fb63dd7cf483e07cac8b92c475094c96be3723b7d  11039  verification/wave29-s0-frame-exclusion/audit.md
6853c92a09f420e390eed25e5e62fed82d7b61bbdb9dcbaa35a3e1cf63ac0567  2580  verification/wave29-s0-frame-exclusion/failure-ledger.md
f072583e33ef483cc72c29989d58ba2ec2accb91da80f128a7a8b73329205ab0  22248  verification/wave29-s0-frame-exclusion/independent_check.py
c0418cec88915089d6cc2e29735ca3e7bc425cfcd2b3ce09a78a707e36e0aa04  14486  verification/wave29-s0-frame-exclusion/independent-results.json
8ab139038fa6792cd9abad0030a0ee17f8cb5cd6eee749a312e2d13a0abd5e30  3068  verification/wave29-s0-frame-exclusion/protocol-freeze.md
d6ddcbdb2c6141ff1731e4913c6436d9b6fd6cc3c5f2bdf6454cb38d85cc9764  3205  verification/wave29-s0-frame-exclusion/run-report.yaml
4761535a50e48d544483096b1de991c81d67f9d4d8062fe081a1c6602109d261  7574  verification/wave29-s0-frame-exclusion/test_independent_check.py
```

The construction-package hashes that control this audit are therefore:

- report: `479ed105825ea2b2a0802c34fcc332b8dc1420b27966bec41053702f3212451f`;
- submitted machine-readable result:
  `0d3723ba4c185dc7865858d16bfc6ada99fd87b4e21da616ef1b1d1ad6b67e11`;
- submitted checker:
  `6415f40948f5033fff47c1f090776f417ac0a8cd0adf589cb5d4aa66cbb7d852`;
- submitted hostile tests:
  `0bd86cadac900ddcfb34d6c76bfa827fe94cc001ef75d1c9c9e6b008d7373cd5`;
- submitted failure ledger:
  `51d6a9681b5fdddc6dffe70baf1f80f03a2b652440ebd5506cfce0dced440115`;
- submitted run report:
  `bfe878cc209ec0699310bb81fd25f720babc73a9ccb326aa660c323629e53dcd`.

## Resolution of the precommitted input manifest

The construction package's `input-freeze.sha256` was itself frozen above,
before inspection, at
`895ce37d214acf92aa5c4f2bd1eaaadaa8ef625045e31479b25eb4f42caf17fe`.
After the independent implementation had completed its first successful
reconstruction, that already committed manifest was opened. It names the
following three direct dependencies. Their current bytes reproduce the
precommitted hashes:

```text
6a15446551b78822706a8e005bef49a411b904cf05f9459b6b3350239839ee1e  2617  agents/2026-07-24-wave28-orchestrator-brief.md
2c8021769d47faebbcd544b364649a2cb93c066a369f76f725cffab1588982db  51794  verification/wave28-simultaneous-neighbor/independent_check.py
513efd1a915bc14adc3003c41e6758839375d9a36a0055f08faa56417c942b18  62149  verification/wave28-theta-modular/independent_check.py
```

Thus the two direct dependencies omitted from the initial conservative
path-based superset were still cryptographically committed before inspection,
via the frozen manifest; no dependency bytes were selected after seeing their
contents.
