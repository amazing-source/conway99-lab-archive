role: literature
date_utc: 2026-07-24T06:38:04Z
git_commit: 5652578111999645a9d5427d0716053de79e0902
claim_label: UNKNOWN
scope: >-
  Wave 31 exact statement freeze and bounded literature audit for the
  unrestricted surviving rank-20 determinant-729 plus rank-24 rootless
  even-unimodular endpoint realization, including every frame, projector,
  Schur-square, Q/B, cubic-tensor, block, and row identity. The independently
  verified actual-graph q-gap is kept separate from the matrix-only package.
  A later sign-involution obstruction is recorded as a post-freeze candidate.
inputs:
  verification/wave31-literature-audit/protocol-freeze.md: 97660bf039223f55d51f498f5743e2ca1779743bbc058f9c5b7e511957e06621
  verification/wave31-literature-audit/protocol-addendum-sign-involution.md: a9c0ea30cb4431b0218ec547cbc153851cd554fa90e76f8496416f988051425b
  verification/wave30-general-h729/reverification-audit.md: 523a84e2a490f3626a791fb16f43b77b7631b3f26f2de8dcecc83f5e03f4d2cc
  verification/2026-07-22-n3-side-incidence-audit.md: 9b6ff3cc9ec8bec13ffd93a8abe0bf0f35398c99f676d00064d6bf5fe6db6787
  agents/2026-07-22-wave8-status-search.md: 31511fd902d2887823174374c8a058c22452bb81950f49a25834e69efcc460ed
method: >-
  Freeze the exact unrestricted statement before searching; audit exact
  numeric fingerprints and alternate frame, lattice-design, eutactic-star,
  integrability, harmonic-cubic, Schur-square, Leech-lattice, and
  Conway-99 terminology; inspect primary or authoritative source metadata;
  preserve graph/projector scope separation; retain every query, limit,
  source boundary, access failure, and artifact hash.
command: >-
  No single computational literature-search command. See
  verification/wave31-literature-audit/query-ledger.json for all 80 exact
  query strings and access events, and run-report.yaml for validation
  commands.
outputs:
  verification/wave31-literature-audit/protocol-freeze.md: 97660bf039223f55d51f498f5743e2ca1779743bbc058f9c5b7e511957e06621
  verification/wave31-literature-audit/protocol-addendum-sign-involution.md: a9c0ea30cb4431b0218ec547cbc153851cd554fa90e76f8496416f988051425b
  verification/wave31-literature-audit/query-ledger.json: 51e3104691e9d52deab3073ed97f88b8cd2ec490f3980dcc24fa07665fd9dbdd
  verification/wave31-literature-audit/source-metadata.json: dfe2fb7c1dff6c6cc7095fccdfc1c3fdf92674352b633158e4810acfc495930b
  verification/wave31-literature-audit/audit.md: ee5384512debc4e31e0ed28f2a73a00bcca11016749f6cbf9e6f5181934cc5f6
  verification/wave31-literature-audit/run-report.yaml: 4c6784e92842254b23b6290061f393c8a3478f2898804e1c6f80ed5b579cdb68
  verification/wave31-literature-audit/artifact-manifest.sha256: ccbc52b0089484b153251fe4c37759d49618c59a78e449c61dde122e64465d25
limitations:
  - No exact realization, obstruction, graph lift, or global result was proved.
  - A bounded source no-hit cannot establish novelty, priority, nonexistence, or openness.
  - The graph-local q-gap is not a theorem of the narrower projector package.
  - No raw source payload was retained.

# Wave 31 statement/literature handoff

## Outcome

```text
exact statement:                              FROZEN
upstream conditional 20+24 reduction:         VERIFIED
surviving matrix/Schur realization:           UNKNOWN
exact prior result:                           NOT FOUND IN SEARCHED SOURCES
actual-graph q!=1 theorem:                    VERIFIED / CITED
actual-graph forced U profile q=3^4,2^122:    DERIVED NECESSARY
sign-involution constancy lemma:              UNKNOWN
sign-involution obstruction:                  UNKNOWN
graph lift, n3=708, Conway-99, novelty:        UNKNOWN
```

The permitted literature sentence is:

> No exact prior result was found in the sources searched as of 2026-07-24.

Nothing stronger is justified.

## Exact surviving target

The question quantifies over every integral marking of every

```text
S=A orthogonal_sum U,
rank(A),det(A),min(A)=20,729,>=4,
rank(U),det(U),min(U)=24,1,>=4.
```

It does not assume `A=T20`, a displayed Leech Gram matrix, an automorphism,
an orbit structure, or the hostile scalar spectrum of `C_A`.

The required frame is an integral full-rank `X in Z^(231 x 44)` with

```text
G=X^T X=21S^(-1),
M=XSX^T,
M^2=21M,
M1=0,
diag(M)=4,
M_ij in {0,1,-1,-2}.
```

Rootlessness forces

```text
X=X_A orthogonal_row_sum X_U,
dimensions 105x20 and 126x24,
X_A^T X_A=21A^(-1),
X_U^T X_U=21U^(-1).
```

Defining, rather than freely choosing,

```text
W=M o M,
Q=X^T W X,
B=SQ=I+2C,
```

the exact block target has

```text
det(Q_A),det(Q_U)=5,1,
det(B_A),det(B_U)=3645,1,
tr(B_A),tr(B_U)=36,24,
B_U=I_24,
Q_U=U^(-1),
tr(C_A)=8,
tr(C_A^2)>=10.
```

The tensor form is likewise active:

```text
Phi_A^*Phi_A=A^(1/2)Q_AA^(1/2),
Phi_U^*Phi_U=I_24,
```

with integral harmonic cubic tensor `P` and the exact contraction recovering
`Q`. The full index formula is in `protocol-freeze.md`.

The forced directed alphabets are

| block | `+1` | `-1` | `-2` | `0` |
|---|---:|---:|---:|---:|
| `A` | 2316 | 648 | 1044 | 6912 |
| `U` | 2776 | 768 | 1256 | 10950 |

The `-1` pairs split `324+384=708`. Projector/tensor arithmetic alone leaves
62 `U` profiles:

```text
c in {9,10,11},
n9=n11+4,
n10=122-2n11,
0<=n11<=61.
```

## Exact graph/projector boundary

The theorem `q=0 or q>=2` is an independently verified theorem about an
actual putative graph. Its proof uses graph-local perfect matchings and a
triangle-free 2-regular auxiliary graph. Lou-Murin (2014) contains the
equivalent prior-art exclusion `gamma!=11`, where `q=12-gamma`.

It is **not** implied by `X,M,W,Q,B`. Therefore:

```text
matrix-only search: c=11 / q=1 remains legal;
actual-graph search: c=11 / q=1 is forbidden.
```

At the actual-graph layer only, `U` is forced to

```text
4 rows q=3,
122 rows q=2.
```

The `A` block then has `sum q=216`, values in `{0,2,...,11}`, and at most one
row with `q=11`.

## Post-freeze sign-involution candidate

After the original protocol was frozen, the orchestrator supplied a new
possible obstruction. It is recorded separately rather than being silently
inserted into the earlier freeze.

For an actual graph, with `N` the `99 x 231` vertex/triangle incidence matrix
and `P_-4` the graph `-4` projector,

```text
E=M/21=(1/3)N^T P_-4 N.
```

A coordinate block `I` of `E`, of size `m` and rank `r`, yields

```text
D=diag(+1 on I,-1 off I),
DE=ED,
m=21r/4,
K=NDN^T,
[K,P_-4]=0.
```

Writing `delta=diag(D)` and
`s_v=(N delta)_v`, the diagonal of `K` is `s`; each graph edge receives the
sign of its unique triangle; and the signed off-diagonal adjacency has
net-degree `2s_v`.

The exact missing lemma is that this support pattern and
`[K,P_-4]=0` force `s_v` to be constant. If so,

```text
99s=3(2m-231),
33|m.
```

Together with `m=21r/4`, this gives `44|r` and excludes every proper
coordinate block. The constancy implication is **not proved** and remains
`UNKNOWN`; therefore the endpoint is not excluded by this lane.

## Prior-art audit

The 80-query search found four meaningful endpoint comparison classes:

1. Niemeier's rank-24 classification identifies `U` up to isometry as the
   Leech lattice. It does not supply a marking or the 126-row frame.
2. Conway-Sloane's s-integrability/eutactic-star paper is the closest
   alternate vocabulary. No exact scale-21, 126-vector, norm-four,
   cubic-isometric star was located.
3. Bertucci-Bonifacio's June 2026 lattice-bootstrap preprint uses spectral
   identities and triple products and has the Leech lattice saturate a
   dimension-24 bound. It does not state the selected endpoint subset or
   `Phi/Q/B` identities.
4. Greaves-Iverson-Jasper-Mixon give related Conway/frame prior art over a
   finite field: 100 vectors in `F_5^45`, not the real integral `231 x 44`
   object here.

Lou-Murin is exact prior art only for the graph-local fixed-triangle profile
and `q`-gap. Reimbayev, Cesarz-Woldar, and Keramatipour supply current nearby
graph work without a construction, nonexistence certificate, or endpoint
realization.

The 24 post-freeze queries found general signed-graph and
primitive-idempotent context in Stanić, Kharaghani-Pender-Suda, and the
Brouwer-Van Maldeghem monograph. No inspected record states the exact
triangle-sign constancy lemma, the divisibility `33|m`, or the coordinate
block obstruction. Its novelty remains `UNKNOWN`.

No inspected source matched the exact identifying conjunction:

```text
231x44 scale-21 integral frame;
105+126 and 20+24 splits;
determinants 729/1 and Schur-defined 5/1;
traces 36/24 and B_U=I;
Leech-side cubic isometry;
324+384 pair split;
actual-graph q profile 3^4,2^122.
```

## Recommended orchestrator boundary

The next construction/proof work should target the unrestricted
matrix/Schur realization first, without assuming `T20`, a Leech marking, a
row automorphism, or `q!=1`. A separate graph-lift lane may add the verified
q-gap and forced `U` profile. Any finite candidate or no-hit remains
`CANDIDATE` or `UNKNOWN` until an independent verifier checks exact
certificates.
