# Independent audit: Wave 32 rooted-vector reduction

## Verdict

`VERIFIED` for the corrected v2 frozen bytes and the scoped necessary
reduction. A nonblocking defect in the superseded prepublication v1 bytes is
retained below as chronology. Under the full actual-incidence and frozen
endpoint hypotheses, every norm-two root has triangle-coordinate pattern

```text
(+1)^21, 0^189, (-1)^21,
```

and its transported vertex support is the bipartite complement of the Fano
incidence graph on two seven-sets.

This is not a root exclusion. Partial-control extendibility, endpoint
existence, `n3=708`, Conway-99 existence/nonexistence, and novelty remain
`UNKNOWN`.

The verifier read the discovery files but did not execute or import discovery
code. `independent_check.py` is a clean-room standard-library implementation.
All corrected v2 hashes in `input-freeze.sha256` were checked before every
run, and the eight-entry v2 discovery manifest replayed independently.

## Discovery-byte chronology

| Artifact | Superseded v1 SHA-256 | Corrected v2 SHA-256 |
|---|---|---|
| `agents/2026-07-24-wave32-rooted-proof.md` | `ded47e87b82ec9a6c897b90b23e9dcac5c957678ecb0e01dcc92d16b4d4cc927` | `04990231e3b42cded363e39ffea771556e52ec66fe03a97164ae99f40ddbefe0` |
| `exact_check.py` | `41e077321fa691a3916da50e992a09d43d4f2d252cae39030bc2d7663bd60e97` | `c753cbda03f8db54f9ad618040c87084cdafa3ce151a5810f72428815a511642` |
| `test_exact_check.py` | `38b7023a66c4b3305cfb080d27cbf39dd5330dab79eaa85eb7c0fcbd3104dd76` | `7f0528ab5485d78c33f24d05d9cd773ed5a5951c44052e4a3489075d33d7c7cc` |
| `exact-results.json` | `6ff9844994c2605266feaad96b4a4ebaf193b5be437bd9e4b21dbf7b98860d99` | `9fa31703b5c4721476b1b88f217d7455615c0d92c0d6db7f150abadfc069c2a0` |
| `input-freeze.sha256` | `778473a5e3c872bf2c8d539b165d58d2d1329dd1224b515f6012fd628499b289` | unchanged |
| `failed-routes.md` | `5a45f61c3033bdd19b6f9f651931efa0a1852fc96e97fc2a9e0525d90724a706` | `444b36cb1bd3d1f604687b2a7d3d3c855fa1590689d0cc1ff18f9da288f17c19` |
| `correction-ledger.md` | absent | `dd95a3d5af1156bfbdac89f2eac0decd15426b2a2261ff334a115f72ab69a2ce` |
| `run-report.yaml` | `19d7aa1e6da04d6de618e14901121fd9543b081688ccc5f7aae85cf95634abcf` | `6ca9ddcbc94b23cc64c0bf0ebb2a4a7ecab413a8db579680dc785ebceee3c137` |
| discovery manifest | `a2dd5896871dda4d0dc54b56d9cb081993079ad03241113e1a36bb0ab972d291` | `ba6c7099e06e24fe2feee4d19021dac9ddf49cbfe99acdd54f905a6c40728b8e` |

V1 misstated one residual degree as 8. V2 computes and tests
`10^42,12^28,14^15` and derives the hostile `q=3` metadata from the supplied
eigenvalue. No discovery code was imported or executed by this verifier.

## Obligation table

| Obligation | Status |
|---|---|
| Frozen input bytes | `PASS` |
| Corrected v2 discovery manifest replay | `PASS` |
| Primitivity implies `X^T` onto and `y in M Z^231` | `PASS` |
| `NM` transport and constant residue modulo 3 | `PASS` |
| Exclusion of nonzero residue classes | `PASS` |
| Integer `-4` amplitude bound and seven-plus-seven support | `PASS` |
| Saturation to the `2-(7,4,2)` Fano-complement design | `PASS` |
| Outside census and `21/189/21` triangle pattern | `PASS` |
| Matrix-only 32-to-16 extreme-fiber lemma | `PASS` |
| Tensor, Schur, congruence, and `A4` constraints | `PASS` |
| Root-reflection identities and scope | `PASS` |
| Superseded v1 text `{8,12,14}` for remaining degrees | `FAIL`; nonblocking, historical, and repaired in v2 |
| Corrected v2 residual-degree distribution | `PASS`: `10^42,12^28,14^15` |
| Corrected v2 hostile `q=3` metadata | `PASS` |
| Partial-control extendibility | `UNKNOWN` |
| Root exclusion / rooted endpoint | `UNKNOWN` |
| `n3=708` / Conway-99 / novelty | `UNKNOWN` |

## Independent reconstruction

### Integral-image and modulo-three bridge

Because the columns of `X` are a basis of a primitive sublattice, all Smith
invariants are one. The same maximal minors govern `X^T`, so
`X^T: Z^231 -> Z^44` is onto. Choosing integral `c` with `X^T c=r` gives

```text
y=XSr=XSX^T c=Mc.
```

Using `M=21E`, `NE=P_-4 N`,
`P_-4=(27I-9A+J)/63`, and the fact that every column of `N` sums to three,

```text
NM=(9I-3A)N+J_(99x231).
```

Thus `z=Ny=NMc` is constant modulo three. Independently,

```text
Az=-4z,  sum z=0,  ||z||^2=126,  N^Tz=3y.
```

Write `z=3k+epsilon*1`, with `epsilon` in `{-1,0,1}`. The sum and norm give

```text
sum k=-33 epsilon,
||k||^2=14+11 epsilon^2.
```

For nonzero `epsilon`, `||k||^2=25` but
`||k||^2 >= sum|k_v| >= |sum k_v|=33`, a contradiction. Therefore

```text
z=3k,  Ak=-4k,  sum k=0,  ||k||^2=14.
```

### Amplitude and support design

At a coordinate `a=k_v`, the neighbor sum is `-4a` and the nonneighbor sum
is `3a`. Since these sets partition the other 98 vertices,

```text
14-a^2 >= 4|a|+3|a|=7|a|.
```

Hence `a` is `0,+1,-1`; norm and sum force seven of each sign.

Let `t_P,t_R` be the same-sign edge counts and `c` the cross-edge count.
The eigenvector equations give

```text
c=28+2t_P=28+2t_R,
```

so `t_P=t_R=t`. Counting pairs of positive vertices through negative common
neighbors yields at least `42+7t`; the strongly regular bounds give at most
`t+2(21-t)=42-t`. Thus `t=0`. The cross graph is 4-regular, and equality
forces every same-side pair to have two common neighbors. Its incidence
matrix satisfies

```text
C1=C^T1=4*1,  CC^T=2I+2J.
```

The complement is the unique `2-(7,3,1)` design, hence the Fano plane.

### Outside and triangle census

Every outside zero vertex has equally many positive and negative support
neighbors, at most one of each. The 140 support-outside incidences therefore
give 70 vertices of type `(1,1)` and 15 of type `(0,0)`. Strongly regular
`lambda=1, mu=2` split the 70 into 28 support-edge completions and 42
support-nonedge completions.

Since `N^T k=y`, a triangle coordinate is its signed support sum. Each support
vertex lies in four two-support triangles and three one-support triangles.
Consequently there are 21 values `+1`, 21 values `-1`, and 189 zeros.

### Matrix-only extreme fibers

For `y_i=2 epsilon_i`, set `u_i=epsilon_i x_i-r`. These are roots orthogonal
to `r`. In an equal-sign fiber, their off-diagonal Gram entries are in
`{-2,-1}`. Exhaustive exact principal-minor testing gives PSD counts

```text
size 1,2,3,4:  1,2,1,0.
```

Thus each sign fiber has size at most three, reducing the 32 frozen Wave-28
patterns to 16. The unique triple has affine-`A2` Gram matrix and sums to
zero; its opposite-sign transformed products vanish, forcing original
cross-frame products `-2`.

### Tensor, `A4`, and reflection checks

For the trace-free symmetric cubic on 44 dimensions, decompose along
`e=a/sqrt(2)` and its 43-dimensional complement. If
`w=T(e,e,.)` and `A=T(e,.,.)|e-perp`, the minimum norm of the complementary
trace lift is `||w||^2/15`. Therefore

```text
60 >= (46/15)||w||^2+3||A||^2,
23g2 <= 1800,
23H2 <= 1800.
```

With `D=(W-M)/2` integral and even diagonal six,
`H2=y^TWy` is `2 mod 4`, so `H2` is one of `2,6,...,78`. Rebuilding the
incidence constants gives

```text
||Np||^2=294,  sum Np=126,
(Np)^T A(Np)=1512+8f,
g2=1134-8f,
```

and hence `g2 in {6,14,...,78}` with `f in {141,140,...,132}`. Also
`y^T(MWM)y=441 y^TWy`. These sets are nonempty and provide no contradiction.

The exact coordinate reflection is `I-yy^T/21`; it sends
`X` to `X-yr^T`, commutes with `E`, and preserves `M`. Incidence transports
it to `I-zz^T/63=I-kk^T/7`. Its fractional off-diagonal entries show that it
is not a coordinate permutation or graph automorphism.

## Correction and boundary

The clean-room partial control has degree histogram
`14^14,4^42,2^28,0^15` and 210 edges. Therefore the three outside classes
need 10, 12, and 14 further neighbors. V1 stated 8, 12, and 14; corrected v2
now computes the exact distribution `10^42,12^28,14^15`. The verifier did not
alter or execute either discovery version.

This partial object checks only support-incident degrees, common-neighbor
counts, triangles, and the signed `-4` vector. It is not an extension
certificate and cannot be used as evidence for or against a completed graph.

## Replay

From this directory:

```text
python -B -m unittest -v test_independent_check.py
python -B independent_check.py --output independent-results.json
```

The replay passes 19 tests, including corrected-v2 frozen-byte and manifest
checks. Adversarial mutations and the v1-to-v2 correction chronology are
listed in `failed-objections.md`; exact machine-readable outcomes are in
`independent-results.json`.
