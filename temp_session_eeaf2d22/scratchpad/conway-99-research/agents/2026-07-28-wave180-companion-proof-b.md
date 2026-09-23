# Wave 180 proof-B audit

## Verdict

`DERIVED`: no gap found in the conic-companion classification or the
`2772/5544` counting refinement.  Independent verifier promotion remains
required.

The audit made one necessary wording correction:

> A circuit cross-realizing three nonedges need not itself be the weight-four
> conic circuit.  It can be either member of the unique weight-four /
> weight-five companion pair.

For a triple-serving circuit, the three pairs share a center `x`; their
leaves form a triangle `T` anticomplete to `x`, and `z_T in E_x`.  If `t`
counts the `x`-star blocks having two cross edges to `T`, then

```text
(m_0,m_1,m_2)=(1+t,6-2t,t).
```

Projector singularity leaves `t=0` or `t=3`.  At `t=0`, the pairing profile
of `z_T` equals that of one star column.  Nondegeneracy forces equality of
the columns, contradicting dual distance at least four.  At `t=3`, if `A`
is the three-block marked set and `B` its four-block complement, the signs
are

```text
z_T+2*sum_(S in A) z_S=0,
z_T+  sum_(S in B) z_S=0.
```

The two supports are circuits of weights four and five and have the same
three-label exact-transversal set.  An inclusion-minimal nonedge cover of
size `N`, with `a` triple-serving members, obeys

```text
4158<=2N+a.
```

Every one of the `a` members has a distinct companion outside the cover, so
the total nonedge-realizing count `Q` obeys `Q>=N+a>=2079`.  Adding the 693
globally isolated edge circuits gives 2,772 projective classes and 5,544
nonzero ternary dual words.

```yaml
role: proof_b
date_utc: 2026-07-28T23:11:00Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Wave180 multiplicity-three cross-circuit classification and global
  companion-cover count.
inputs:
  - attempts/wave177-relation-averaging-conic/derivation.md sha256=324029228654f8f7460404d9ec018b7bf5d191c79603d0df43805fef99d9e3ff
  - attempts/wave178-edge-circuit-injection/derivation.md sha256=bb6aa28ad689084734741d939ad6442910aaa0d027ee5f150e2588fcc57b82b5
method: >-
  Independent centered-Gram and star-projector scrutiny followed by
  minimal-cover counting.
command: read-only analytic derivation; no construction search
outputs:
  - agents/2026-07-28-wave180-companion-proof-b.md
limitations:
  - The theorem is conditional on the rank-11 endpoint.
  - Independent verifier promotion remains required.
  - The endpoint and Conway-99 remain UNKNOWN.
```
