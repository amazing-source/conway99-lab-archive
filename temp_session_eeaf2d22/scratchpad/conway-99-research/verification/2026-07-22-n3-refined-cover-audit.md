# Independent audit of the refined `N3` cover

Verdict: `PASS` for the conditional 78-branch cover and its implementation.
Conway-99 remains `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T00:03:07Z
git_commit: a066170e452f31efe1e00610b8159a66b825b01f
claim_label: VERIFIED
scope: profile semantics, symmetry safety, exhaustive coverage, strict certificate checking, and SAT implementation of the refined N3 branches
inputs:
  code/matching_orbits.py: 1ba68393c385ef296458555b7c48533786ea592a50bec589be675f95fd550240
  code/sat_model.py: 45f0da74619b31a1a31cc407f702f8e86a0597ee73d29ec268528cd89980aef8
  code/test_matching_orbits.py: 42753845f010c1ed9453a2359bd45f09550fe36665247d325fd1707032d0e4bc
  code/test_sat_model.py: bca83cd0f00814cdb56dc3e6dbbe5a079a35a8f65bb2862b774cfcd5b5f5cca5
  verification/n3-refined-cover/n3-refined-cover.json: fd9a14193365bf40d3d7bcbe53d56c6f1ffa8a93ca63d5b68506c3354f3b9f8a
  verification/n3-refined-cover/verify.py: cbf0b46a4656b54c0f5b6a65a7f0e549286a5cfb68ca7ee54813b43423d1cb9a
  verification/test_n3_refined_cover.py: ffe253a5084e0d35d4ec9363d76a7b508662b38f4a9e2aa3c08f5325a010034a
method: independent profile derivation, full-wreath filtering, exact parent and oriented orbit enumeration, Burnside and orbit-stabilizer checks, all-branch literal comparison, cross-backend formula audit, and adversarial mutations
command: |
  .venv/Scripts/python verification/n3-refined-cover/verify.py
  .venv/Scripts/python -m unittest discover -s code -p "test_*.py" -v
  .venv/Scripts/python -m unittest discover -s verification -p "test_*.py" -v
outputs:
  certificate_sha256: fd9a14193365bf40d3d7bcbe53d56c6f1ffa8a93ca63d5b68506c3354f3b9f8a
  code_tests: 48_passed
  verification_tests: 19_passed
limitations: conditional on the previously audited N3 normalization; no refined branch has a complete proof or candidate graph
```

## Independent mathematical reconstruction

For `p=(0,2)`, the verifier reconstructed the coordinate-4 target directly as

```text
2 - incidence(4,p) - incidence(5,p) = 2.
```

The normalized unit fixes `(2,4)` as one neighbor. Independently enumerating
the coordinate-4 fiber leaves exactly the eleven endpoints recorded in the
certificate. Reconstruction of the lexicographic residual labels and named
edge-variable order reproduced the literal map

```text
0:2, 1:14, 3:34, 6:44, 7:45, 8:46, 9:47,
10:48, 11:49, 12:50, 13:51.
```

Without importing discovery code, the standalone checker enumerates all
645,120 elements of `C2 wreath S7` and filters two subgroups:

- the parent setwise `N3`-unit stabilizer, of order 768; and
- its orientation-preserving subgroup fixing coordinate zero, of order 384.

Explicit generators reproduce both filtered groups exactly. The checker then
reconstructs the parent 12 matching orbits, all 945 compatible matchings, all
10,395 refined states, and the 78 oriented orbits. Coverage is disjoint and
exhaustive, orbit-stabilizer holds case by case, and the independent Burnside
sum is 29,952.

The verified orbit-size histogram is

```text
{1:3, 8:6, 12:6, 32:3, 48:18, 64:6,
 96:9, 192:12, 384:15}.
```

## Implementation and backend audit

All 78 implementation specifications agree with the public certificate. Each
contains all 66 shared-fiber decisions, with six positive matching edges, and
one refinement edge outside that fiber. Every representative maps to the
recorded parent branch and exact literal list.

Compact/direct and CNF/native construction paths were compared. From their
respective unnormalized bases, every refined case adds precisely 67 clauses,
with seven positive and 60 negative units, and adds no variables or `AtMost`
constraints. Representative native counts are:

```text
variables: 289,338
clauses: 285,919 compact; 857,623 direct
native AtMost: 5,838 compact; 9,324 direct
OPB constraints: 291,757
```

The native OPB rendering of every appended unit agrees with the in-memory
formula. Invalid API and CLI state transitions were rejected before changing
the formula. The internal parent-branch marker set by a refined branch is an
intentional record of its already-applied 12-way ancestor.

## Strict certificate boundary

The standard-library checker rejects duplicate keys, unknown fields,
non-standard `NaN`/`Infinity`, Boolean values masquerading as integers,
malformed matchings, altered literals, noncanonical representatives, incorrect
orbit data, and coverage defects. Seventeen independent certificate mutations
were rejected during the audit; committed regression tests retain the parser
classes most prone to Python type confusion.

The generator reproduced the certificate with byte-identical SHA-256. The
`VERIFIED` label applies only to the exact conditional case split and its
implementation. It does not establish the upstream cited-and-derived `N3`
occurrence, satisfiability, unsatisfiability, or either target resolution.
