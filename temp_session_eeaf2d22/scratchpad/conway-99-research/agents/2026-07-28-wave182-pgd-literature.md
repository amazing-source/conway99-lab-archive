# Wave 182 equality-design literature audit

## Verdict

`UNKNOWN` as a literature theorem audit.

No checked primary theorem excluded the conditional 99-by-231 all-nine
incidence design from Wave 182.  Wave 183 subsequently derives an internal
root-orthogonality contradiction to every multiplicity-nine support, so this
report is retained as a correctly scoped null literature boundary rather
than the current proof boundary.

## Partial-geometric-design identification

For the Wave 182 lower equality case,

```text
F F^T=20I+5A+J
```

has spectrum `189^1,35^54,0^44`.  Hence every weight-nine block column `f`
lies in the principal plus graph-3 eigenspaces and satisfies

```text
A f=3f+1.
```

Equivalently, the conditional incidence structure is

```text
PGD(99,231,9,21;14,49)
```

in modern notation, a partial geometric design `(r,k,t,c)=(21,9,14,20)`
in the original Bose notation, and the two-class PBIBD

```text
(v,b,k,r;lambda_1,lambda_2)=(99,231,9,21;6,1).
```

The standard feasibility equations and Neumaier inequalities all hold.
The relevant characterization and feasibility sources are:

- Bose, Bridges, and Shrikhande,
  [*Partial geometric designs*](https://doi.org/10.1016/0012-365X(76)90088-1).
- Bridges and Shrikhande,
  [*Special partially balanced incomplete block designs and associated
  graphs*](https://doi.org/10.1016/0012-365X(74)90068-5).
- Song and Tranel,
  [*Partial geometric designs having circulant concurrence
  matrices*](https://arxiv.org/abs/2106.11047).
- Neumaier,
  [`t 1/2`-designs](https://doi.org/10.1016/0097-3165(80)90067-9).

## Intriguing-set and Delsarte boundary

Each conditional size-nine block is a positive intriguing set with
intersection numbers `(4,1)`.  Its inner distribution in the graph's
two-class association scheme is

```text
(1,4,4),
```

whose Delsarte transform is `(9,90,0)`.  Thus the individual-block
nonnegativity conditions are attained, with equality in the `-4`
eigenspace, rather than violated.

Primary references:

- Bamberg, De Clerck, and Durante,
  [*Intriguing sets of partial quadrangles*](https://doi.org/10.1002/jcd.20269).
- Delsarte,
  [*An algebraic approach to the association schemes of coding
  theory*](https://hdl.handle.net/2078.1/205698).

## Missing coherent-configuration hypothesis

Strongly regular design/coherent-configuration theorems require controlled
block-side intersections, typically two intersection sizes with a strongly
regular relation on blocks.  Wave 182 did not prove that

```text
|X_r intersect X_s|
```

depends only on the orthogonality of `r,s`.  The local `A6` root system does
not by itself establish that global condition, so Higman-type absolute and
Krein bounds could not be invoked.

The exact missing literature bridge was:

> Gluing the 99 local projective `A6` root systems with the Wave 182 point
> concurrence numbers forces global block intersections to depend only on
> root orthogonality.

No checked primary source supplied that theorem.

## Modular ranks

The identity

```text
M^2=35M+294J,  M=F F^T,
```

gives compatible modular behavior: rank 55 over `F_2`, Gram rank 54 over
`F_3`, Gram rank one over `F_5`, and a square-zero Gram over `F_7`.
Known strongly-regular-graph p-rank theory did not convert these values into
nonexistence.  Bruck--Ryser--Chowla does not apply to this rectangular
two-concurrence design.

Primary p-rank reference:

- Brouwer and van Eijl,
  [*On the p-rank of the adjacency matrices of strongly regular
  graphs*](https://doi.org/10.1023/A:1022438616684).

```yaml
role: literature
date_utc: 2026-07-28T23:58:49Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: UNKNOWN
scope: >-
  Primary-source feasibility and nonexistence audit for the conditional
  Wave182 all-nine 99-by-231 incidence design.
inputs:
  - attempts/wave182-a6-root-gluing/derivation.md
    sha256: 8503f7c4734e13dcc13856bee5066e1cd1c34303bba72aadea23f88871f4f05b
  - attempts/wave182-a6-root-gluing/exact-results.json
    sha256: 812529cb1e5e13efe34cd87f3e9916b4a747fd08d82c56eefc0e9ec83802ec21
  - attempts/wave182-a6-root-gluing/run-report.yaml
    sha256: c7c90a9ddc674eee84f74354a92eeec1181c030c3c3d9166be4c59b3784e83e3
method: >-
  Exact spectral reduction and primary-theorem hypothesis audit for partial
  geometric designs, SPBIBDs, intriguing sets, association schemes,
  coherent configurations, and modular rank.
command: primary-source theorem and parameter audit
outputs:
  - agents/2026-07-28-wave182-pgd-literature.md
limitations:
  - Focused rather than exhaustive bibliography.
  - No literature theorem was found that excludes the design.
  - Wave183 later supersedes this null boundary by a direct scoped argument.
  - The endpoint and Conway-99 remain UNKNOWN.
```
