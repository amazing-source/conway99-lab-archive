# Wave 33 rooted-extension static comparison audit

Verdict: **the candidate's core rooted structural-reduction claims are
independently VERIFIED in their graph-only scope; no material discrepancy was
found**

The frozen precomparison reconstruction and the released candidate agree,
after the explicit notation map

```text
candidate A_S = clean-room F   (support adjacency),
candidate F   = clean-room D   (support-to-O incidence),
candidate D   = clean-room H   (induced O adjacency),
candidate B   = clean-room B   (O-Q incidence).
```

They agree on:

```text
|S|,|O|,|Q| = 14,70,15;
quotient = [[4,10,0],[2,9,3],[0,14,0]];
Q independent;
simple 2-(15,3,2) O-Q design;
all six blocks of A^2=12I-A+2J;
necessity and sufficiency for the SRG graph extension;
no automorphism restriction;
spec(H) = 9^1,(-1)^14,(-1+sqrt(2))^6,(-1-sqrt(2))^6,3^27,(-4)^16.
```

No binary criterion solution or exclusion is supplied.  Rooted graph
extension/exclusion, the full projector/lattice/tensor/Schur endpoint,
`n3=708`, Conway-99, and novelty all remain `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-24T10:28:37Z
git_commit: b2595baa40d50e9c259051751fe27090bee6a449
claim_label: VERIFIED
audit_verdict: STATIC_CLEAN_ROOM_COMPARISON_PASS
scope: >-
  Static comparison of the frozen Wave 33 rooted-extension candidate against
  the byte-frozen precomparison clean-room reconstruction. Verify manifest
  integrity, exact quotient/design/block/spectral claims, graph-vs-endpoint
  scope, 56 triangles, 294 four-cycles, determinant 2^32*3^29, and the hostile
  two-PG(3,2) design. Do not import or execute candidate code.
```

## 1. Byte separation and release corrections

Before candidate inspection, the verifier's eight precomparison artifacts were
frozen by a manifest whose SHA-256 is

```text
a0cd7d284a23aba5576f2da2a1282c9acb209953c3da5d01e706d793f61d3ea7.
```

Those eight bytesets still validate unchanged.  The released candidate
inventory has SHA-256

```text
f10119fecdbd226ca5a89180e2c8663b88c8f7d929ed8a619015070e0f637566
```

and all nine entries validate.  The two non-byte release corrections are
recorded explicitly:

1. The superseded `17f9...` manifest note is replaced by the validated
   candidate inner-manifest hash
   `153860d39fe7274a2f55ee952bcad1135cf4134ccc36d9aec07f6da379c5ca04`.
2. The release inventory has nine paths: one report plus eight files under
   `attempts/`, counting the inner manifest.  The inner manifest itself has
   eight entries because it omits its own impossible self-hash: one report
   plus the other seven `attempts/` files.

The comparison artifacts are separate files.  No precomparison file or
candidate file was rewritten.

## 2. Static-only candidate inspection

Candidate Python was treated as inert UTF-8 text.  The verifier parsed
`exact_check.py` and `test_exact_check.py` into Python syntax trees, but did not
import, execute, or call either file.  The source parses, contains no direct
`eval`, `exec`, `compile`, or `__import__` call, and the test source contains
15 statically visible `test_*` methods.

The candidate's statement that its own suite ran 15 tests remains a discovery
run-report statement; this comparison does not reuse that execution as
evidence.  Instead, the verifier's separate static comparison suite passes
15 tests.

## 3. Quotient, design, and exact criterion

The candidate's common-neighbour counts match the precomparison derivation:

```text
o in O: 26 = 8 + 2 deg_O(o), so deg_O(o)=9 and deg_Q(o)=3;
q in Q: 28 = 2 deg_O(q), so deg_O(q)=14 and deg_Q(q)=0.
```

Thus `Q` is independent and the displayed quotient follows.  The `70 x 15`
O-Q incidence has row weight 3, column weight 14, and

```text
B^T B=12I+2J.
```

Repeated rows would make two O vertices share at least three Q neighbours, so
the resulting `2-(15,3,2)` design is simple.

After applying the notation map above, every candidate block equation is
exactly the corresponding independently frozen block.  The candidate also
keeps every required binary, symmetry, and zero-diagonal gate.  Conversely,
the six blocks reassemble the full 99-by-99 identity; its diagonal gives
degree 14 and its off-diagonal entries give `lambda=1`, `mu=2`.  Hence the
criterion is necessary and sufficient for an `srg(99,14,1,2)` **graph**
extension.  It is not an endpoint certificate.

## 4. Spectrum, determinant, and cycles

The verifier independently reevaluated the exact quadratic-integer spectrum.
Its first five moments are

```text
tr(H^0)=70,
tr(H)=0,
tr(H^2)=630,
tr(H^3)=336,
tr(H^4)=13062.
```

Therefore

```text
|E(H)|=315,
triangles(H)=336/6=56.
```

For a simple 9-regular graph on 70 vertices,

```text
tr(H^4)=2|E(H)|+4*70*binom(9,2)+8 C4(H),
```

which gives `C4(H)=294`.  Multiplying the exact eigenvalues gives

```text
det(H)
 =9*(-1)^14*((-1+sqrt(2))*(-1-sqrt(2)))^6*3^27*(-4)^16
 =2^32*3^29.
```

The combinatorial edge partition also closes independently:

```text
unique common neighbour in S:  42;
unique common neighbour in Q: 105;
unique common neighbour in O: 168;
total H edges:                315.
```

The last class contributes `168/3=56` all-O triangles.  Together with the
other cell types, the full target triangle count is

```text
28+42+105+56=231=693/3.
```

## 5. Hostile `PG(3,2)` control

From the 15 nonzero vectors of `F_2^4`, the comparison checker regenerated all
35 lines of `PG(3,2)`.  Applying the released point permutation produces a
disjoint second line system.  Their union has exactly:

```text
70 distinct triples;
row weight 3;
column weight 14;
every point pair in 2 triples;
SHA-256 ddc3d4d8262a88e1de3078ae3fe3ef37087d2f3fed1ab251efe4c924292f81fb.
```

The verifier separately regenerated the fixed support labeling and obtained
the candidate's exact support-adjacency, support-incidence, and O-label
hashes.  Against that labeling, it reproduced the complete `FB` histogram

```text
0:17, 1:55, 2:75, 3:48, 4:9, 5:2, 6:3, 7:1,
```

so exactly 135 of 210 entries differ from two.  This validates the intended
hostile conclusion: the abstract simple `2-(15,3,2)` condition is consistent,
but this row ordering fails fixed-label coupling and is not an extension.

## 6. Final status wall

```text
candidate structural reduction:          VERIFIED
manifest/results consistency:            VERIFIED
material discrepancy:                    NONE FOUND
binary criterion solution:               UNKNOWN
rooted graph extension or exclusion:      UNKNOWN
full rooted endpoint:                     UNKNOWN
n3=708:                                   UNKNOWN
Conway-99 existence/nonexistence:         UNKNOWN
novelty:                                  UNKNOWN
```

The strongest surviving objection is exactly the one retained by both
packages: no binary pair solving the finite criterion has been found or
excluded.  The comparison verifies an exact reduction and its conditional
consequences, not a resolution of that finite problem.
