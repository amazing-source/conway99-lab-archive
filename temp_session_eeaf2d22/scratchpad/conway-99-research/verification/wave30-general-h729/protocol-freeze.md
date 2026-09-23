# Wave 30 general-h729 independent-verifier protocol freeze

Date frozen (UTC): `2026-07-24T04:24:29Z`

Role: adversarial verifier

## Blindness boundary

The verifier computed the hashes below before opening or otherwise inspecting
the contents of the Wave 30 discovery report or discovery package. Only path
names, byte lengths, hashes, Git object identifiers, and working-tree status
were inspected. The verifier will use a separate implementation and will not
import discovery code.

## Exact claim to test

Under the previously frozen `h=729` endpoint hypotheses, every rootless
integral positive-definite rank-44 `S`-form which decomposes as an integral
orthogonal direct sum must have exactly two blocks:

- one rank-20 determinant-729 block, denoted `A20`;
- one rank-24 even-unimodular block, denoted `U24`;
- row-support split `105/126`;
- block traces `36/24`; and
- `B_U = I`.

Equivalently, 14 of the 15 arithmetically possible block types are excluded.
The surviving type itself is not claimed impossible or graph-realizable.

The verifier will also test all imported determinant, parity, frame, rootless,
rank/signature, partition, trace-residue, AM-GM, complement, and premise
deletion steps. The final block type, rooted or integrally indecomposable
forms, `n3=708`, the Conway 99-graph problem, and novelty remain `UNKNOWN`.

## Discovery artifacts frozen before inspection

Each line is `sha256  bytes  path`.

```text
1bc63f569600bca88e12c977a0bd94ecdd03aa5f3fd8c4f203d4778fbec78efa  15875  agents/2026-07-24-wave30-general-h729.md
29cbbdff1ab167b436db725130d830bfd047beb1c4ba834c51b5a33c3aed690a  784  attempts/wave30-general-h729/artifact-manifest.sha256
ed8edcbb0febde6d6fbd57776b7696402f832421fa11fb1984fcd57c8369eaff  20274  attempts/wave30-general-h729/exact_check.py
93cc1633d0b25d5f3daecd4c49cbc3b2dc3f754576a3cd5c9364c729a79a7698  16112  attempts/wave30-general-h729/exact-results.json
397f74c75a8ae24bedd26fea41c0fb82d03c6611a87627e86aeb29244a586006  2848  attempts/wave30-general-h729/failed-routes.md
a07c703b20237441b221e13c68be885d01db180871b8496af5d7204e2587793b  599  attempts/wave30-general-h729/input-freeze.sha256
77232c06827c4c62e7dc6f5380cc4ebe2a3c6d5496fe8c3592589986089e416f  2590  attempts/wave30-general-h729/run-report.yaml
9075d5fd77253850ba09c4655d9cbab135eb32fdd36638dc4aa9051fa49898a2  9245  attempts/wave30-general-h729/test_exact_check.py
```

## Applicable prior state frozen before inspection

Git state:

```text
branch: codex/first-research-wave
HEAD: ae8fd70baaeb35302f957653e20ad710e5e77281
HEAD tree: 385605545e6784ee290d17afdfd460e4fe526ef3
public branch at freeze: aadc0dafce387233fc16406cc9822f069becd645
merge base: aadc0dafce387233fc16406cc9822f069becd645
```

Recent commits:

```text
ae8fd70baaeb35302f957653e20ad710e5e77281 docs: integrate Wave 29 single-lattice exclusion
ff6902812c46d33bd081e7580d09baa1d60a5494 docs: audit Wave 29 literature
5dbff08f8cb53102118acd281a6d4b353a962cf8 verify: certify Wave 29 S0 endpoint exclusion
2b1337e06453a41120534dcecafdf6fc726fe10d search: add Wave 29 S0 endpoint exclusion
aadc0dafce387233fc16406cc9822f069becd645 fix: normalize Wave 28 publication metadata
```

At freeze time the only visible working-tree entries were untracked Wave 30
discovery/construction paths. The verifier directory did not yet contain any
artifact other than this subsequently written protocol.

Key prior artifacts:

```text
ca6754e22fce3ac108bea4a10188f14cebed9aa2d922894b0640996f23cbaa58  86054  CLAIMS.yaml
7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58  4589  CONJECTURE.md
23fa1a25521b8e78730e11bb88f05f096a8e1137430169be701af4abaa0b6af6  84803  OBLIGATIONS.yaml
5b699e36e16c82c7a132a6a0ba236cca830f6522de31874b1fe6db17c0e87bae  101015  STATUS.yaml
e6ae61331a54d53f2a98712296ebac855f45b46de32ff2ec4d85018f2d8a5045  13485  agents/2026-07-24-wave29-s0-frame-exclusion.md
8cb5b0198ac9e787a8234820e648626dc27f900f53b7511068d5442d06d7a39b  826  attempts/wave29-s0-frame-exclusion/artifact-manifest.sha256
6a31c4ae0b2c994f4c715ba5118e3b25a052e8b3fc99dea88ea794cb7d9d8dce  22409  attempts/wave29-s0-frame-exclusion/exact_check.py
7a85c5321b5e91365c246dff7bae9264cc82494da5c866b1b351511099f6638c  12140  attempts/wave29-s0-frame-exclusion/exact-results.json
bba05cd84c1ac35284c9f8af7d8dd32480f11158ada69195b1bfa61892cad234  3198  attempts/wave29-s0-frame-exclusion/failed-routes.md
5ddbd25498cf9f7048705e190f81e203d3d21efcc72d1750de2235e419fda1c4  714  attempts/wave29-s0-frame-exclusion/input-freeze.sha256
91fba9dad3bb9d906eb69c06ca97be82ff804296dcb010be3f6749e67beba286  3068  attempts/wave29-s0-frame-exclusion/run-report.yaml
26dff5f61d6bc6e3d752f596f5c318baee47358f27552e4a0b7e4c3e8a6a5c4f  8038  attempts/wave29-s0-frame-exclusion/test_exact_check.py
6a62209abbca6403dee7b9ebf83edbdccd5466a278957ab9d63f37bcd3f08cf8  596  verification/wave29-s0-frame-exclusion/artifact-manifest.sha256
dbdcb88bf309cbfa47a42b9fb63dd7cf483e07cac8b92c475094c96be3723b7d  11039  verification/wave29-s0-frame-exclusion/audit.md
6853c92a09f420e390eed25e5e62fed82d7b61bbdb9dcbaa35a3e1cf63ac0567  2580  verification/wave29-s0-frame-exclusion/failure-ledger.md
f072583e33ef483cc72c29989d58ba2ec2accb91da80f128a7a8b73329205ab0  22248  verification/wave29-s0-frame-exclusion/independent_check.py
c0418cec88915089d6cc2e29735ca3e7bc425cfcd2b3ce09a78a707e36e0aa04  14486  verification/wave29-s0-frame-exclusion/independent-results.json
8ab139038fa6792cd9abad0030a0ee17f8cb5cd6eee749a312e2d13a0abd5e30  3068  verification/wave29-s0-frame-exclusion/protocol-freeze.md
d6ddcbdb2c6141ff1731e4913c6436d9b6fd6cc3c5f2bdf6454cb38d85cc9764  3205  verification/wave29-s0-frame-exclusion/run-report.yaml
4761535a50e48d544483096b1de991c81d67f9d4d8062fe081a1c6602109d261  7574  verification/wave29-s0-frame-exclusion/test_independent_check.py
```

The Git commit and tree identifiers freeze all other tracked prerequisites.

## Verification rules

1. Reconstruct the argument from the frozen endpoint data and standard exact
   linear algebra; do not import discovery Python.
2. Treat decomposition as an arbitrary nontrivial integral orthogonal
   decomposition until arithmetic proves a narrower form.
3. Enumerate every determinant/rank partition admitted by the hypotheses.
4. Test each purported exclusion with exact integers and fractions.
5. Include premise-deletion and boundary tests designed to make false
   generalizations pass superficially.
6. A solver exit code, floating-point approximation, or absence of a found
   object is not a certificate.
7. Preserve every objection, including objections later discharged.
8. Do not change central or discovery artifacts and do not perform Git writes.
