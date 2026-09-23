# Wave 31 T20 frame independent audit

## Verdict

```text
PASS_SCOPED_FINITE_EVIDENCE
```

The frozen construction package passes every independent finite check in the
protocol.  This verdict verifies the complete T20 norm-four shell, its full
line-pair geometry, the exact rational box-relaxation witness, the cap-one
restriction, the named radius-two nonhit, and the conditional U-block A4
transfer.

It does **not** find or exclude an unrestricted T20 frame.  It does not verify
an orientation, `Q_A`, `B_A`, `A4_A`, a coupled endpoint, `n3=708`,
Conway-99, or novelty.

## Frozen provenance

The verifier froze the nine submitted files and four upstream files at:

```text
commit: 67a0e4585c9c378dcd658784a3876564557b70e3
tree:   47ef723b915045c0ef83f15b49235b278dbfb6aa
parent: 31bc516a581decb6394bf5e780f07fb05d567274
```

All 13 committed blob hashes equal the worktree hashes in
`input-freeze.sha256`.  The submitted eight-entry artifact manifest and
four-entry upstream input freeze both validate.

The submitted report's embedded `git_commit` is the parent hash because the
report was generated immediately before its own construction commit.  The
verifier uses the final submission commit above as the controlling freeze.
No candidate byte was repaired or reinterpreted.

## Independent exact results

### Displayed T20 and shell

Fresh integer/rational matrix arithmetic gives:

```text
rank:                                  20
determinant:                           729
positive definite:                    yes, all exact LDL pivots positive
T20 canonical hash:                   1890fe1973eed47850c307d0975ae393f2a8ab32a9d0b16b35ebcab7012445d6
21*T20^-1 integral:                    yes
21*T20^-1 canonical hash:             006011e5ea2fa29cc942bcaa3e72e6d300a549fbad6b6991f3edffb20371a024
T20*(21*T20^-1):                      21I_20
```

Two complete exact enumeration trees were run: one in the displayed basis
and one after a nontrivial coordinate permutation.  The changed-basis shell
maps back byte-for-byte as the same sorted mathematical set.

```text
norm-zero vectors:                       1
norm-one, norm-two, norm-three vectors:  0
norm-four vectors:                    5076
antipodal lines:                      2538
canonical line hash:
25af9df21492a5b9022c1888424f4892e0e1cb56d82adee73b49197a536f569e
```

The complete ordered line list equals the submitted list.  Canonical
orientation only names each antipodal line; no target automorphism or orbit
quotient is used.

The coordinate-height distribution is:

| Maximum absolute coordinate | Lines |
|---:|---:|
| 1 | 1196 |
| 2 | 1019 |
| 3 | 278 |
| 4 | 36 |
| 5 | 9 |

All 2,538 canonical lines have distinct residues modulo two, and all 2,538
also have distinct residues modulo three.

### Complete pair geometry

All 3,219,453 unordered pairs were recomputed with integer arithmetic:

| Inner product | Pairs |
|---:|---:|
| -2 | 80,883 |
| -1 | 671,126 |
| 0 | 1,382,670 |
| +1 | 923,008 |
| +2 | 161,766 |

No other pair inner product occurs.  The absolute counts are:

```text
|0|: 1,382,670
|1|: 1,594,134
|2|:   242,649
```

The independently recomputed absolute-two degree distribution is:

| Degree | Lines |
|---:|---:|
| 160 | 108 |
| 178 | 840 |
| 196 | 1242 |
| 214 | 330 |
| 232 | 15 |
| 322 | 3 |

Its degree sum is exactly twice 242,649.  The submitted orientation rule is
therefore correct: a canonical `+2` pair needs opposite signs and a canonical
`-2` pair needs equal signs to avoid forbidden signed inner product `+2`.

### 105-line moment system

The verifier independently formed all 210 upper-triangular outer-product
coordinates.  Since every line has T20 norm four,

```text
trace(T20 * 21*T20^-1) = 420 = 4*105.
```

The moment target therefore forces 105 rows.  A repeated antipodal line would
give signed inner product `+4` or `-4`, so distinct Boolean line variables are
necessary for the endpoint alphabet.

For the 210 moment equations plus odd cardinality:

```text
variables:             2538
equations:              211
coefficient rank GF(2): 210
augmented rank GF(2):   210
dependencies:             1
consistent:              yes
```

The separate coefficient and augmented ranks close the ambiguity in treating
an augmented bit as an ordinary pivot.  Consistency is only a relaxation; it
does not supply a Boolean frame.

### Rational relaxation witness

The verifier parsed every weight from the submitted result as a rational
number and instantiated all 2,538 line weights:

```text
unit weights:                   33
strictly fractional weights:  210
zero weights:                 2295
support:                       243
sum of all weights:            105
verified moment entries:       210
all weights in [0,1]:          yes
certificate hash:
2e7f5d482685db1c98f99fe239021f87e3f7c27f0506d92611e935a0617af161
```

The minimum fractional weight is

```text
4224879822682012573982774/10603961297504408600788109573
```

and the maximum is

```text
10580278550697598610039691783/10603961297504408600788109573.
```

Every one of the 210 reconstructed moments equals the integral target
exactly.  The certificate proves only that the continuous box relaxation is
nonempty.  Its 210 fractional weights make it explicitly non-Boolean.

### Named near-frame and exact radius-two scan

The support and residual hashes reproduce:

```text
support hash:
fd23ed360485379c884d48d3bac892e7e46bec8a3875bc7c6eca4f185617e7fd
residual hash:
e7877387488d16a511f6f51390999e87ef7aa97cbcb24aeb5d9f6d1ce1d2f89b
Frobenius residual score:               121
nonzero upper-triangular entries:        63
maximum absolute residual entry:          2
```

The independent scan uses the collision-free bounded base-257 encoding
proved in `protocol-freeze.md`:

```text
one-exchange removals:                  105
one-exchange additions:                2433
one-exchange choices:                255465
exact repairs:                            0

two-exchange removal pairs:             5460
two-exchange addition pairs:         2958528
exact repairs:                            0
```

The submitted SplitMix64 coefficient hash also reproduces:

```text
09b7734bc7967f15ef7b2587564688af29a311bd763a5ad026454db9109b6080
```

Its complete replay has zero matching fingerprints at radius one and zero at
radius two.  Static inspection confirms that if matches existed, every
matching removal tuple would be checked against all 210 exact entries.
Modulo-`2^64` collisions could add work but could not suppress an exact
repair.

The only negative conclusion is:

```text
no second-moment selection is within two exchanges of
W31-T20-NEAR-105-001.
```

Distance three or greater and every other starting support remain unsearched
by this certificate.

### Cap-one restriction

There are 1,196 lines of coordinate height at most one.  Each chosen line
contributes at most one to a diagonal moment.  Coordinate one (zero-based) of
`21*T20^-1` is 266, but 105 such rows contribute at most 105.  The
all-cap-one domain is excluded.  The remaining 1,342 lines are not excluded.

### Conditional row data and A4 transfer

Using the frozen `trace(B_A)=36` premise, each row's cubic contribution
`60-6c_i` gives:

```text
sum_i c_i = (105*60-36)/6 = 1044.
```

The submitted 13 row profiles and all directed aggregates then reproduce:

```text
+1: 2316   -1: 648   -2: 1044   0: 6912   sum q: 216.
```

For the U block:

```text
B_U=I  =>  Q_U=U^-1
A4_U=M_U W_U M_U
     =X_U U Q_U U X_U^T
     =M_U.
```

Thus all 126 U rows have A4 diagonal four, U trace 504, and zero excess.
The frozen global trace 1,260 and 84 excess units leave T20 trace 756:

```text
756 = 4*(105+84).
```

This is a necessary transfer under the frozen decomposable endpoint premises,
not a construction of `A4_A`.

## Reproduction

The independent commands passed:

```text
python -B verification/wave31-t20-frame/independent_check.py --output verification/wave31-t20-frame/independent-results.json
python -B -m unittest discover -s verification/wave31-t20-frame -p test_*.py -v
```

The independent suite has 11 passing tests, including a changed-basis shell
check, separate GF(2) ranks, negative-coordinate fingerprint linearity,
bounded positional-injectivity control, and a hostile status-promotion
mutation.

As a nondecisive reproducibility check only, the submitted construction suite
also passed 10 tests and regenerated its JSON byte-identically with SHA-256

```text
d2592a71e8600a894aa7d87e6ed1c8230010b919488b10f9854710bb77944152.
```

The independent verdict does not rely on that self-replay.

## Final status wall

```text
complete T20 norm-four shell:                 VERIFIED
complete line-pair geometry:                  VERIFIED
continuous second-moment relaxation:          VERIFIED EXACT WITNESS
cap-one-coordinate line restriction:          VERIFIED EXCLUDED
named radius-two near-frame neighbourhood:     VERIFIED EXCLUDED
unrestricted Boolean second moment:            UNKNOWN
oriented zero-sum alphabet frame:              UNKNOWN
Q_A / B_A / A4_A:                              UNKNOWN
coupled T20 plus U24 endpoint:                  UNKNOWN
rooted or integrally indecomposable forms:      UNKNOWN
n3=708, Conway-99, and novelty:                 UNKNOWN
```
