---
role: proof_b
date_utc: 2026-07-23T19:43:07Z
git_commit: 667463c93e9836085ba09428ca21bf57f2fd10c5
claim_label: DERIVED
scope: conditional exclusion of n3=705 for a putative srg(99,14,1,2), using only the audited Wave-20 global-Schur and Wave-21 projection-lattice premises
inputs:
  - path: verification/2026-07-23-wave20-global-schur-audit.md
    sha256: 6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3
  - path: attempts/wave20-global-obstruction/independent-verifier/independent-results.json
    sha256: 575939f9abe19e5578a2efd1155495877c2080944c75cc0db6702c21a9ce2637
  - path: verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md
    sha256: 45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268
  - path: verification/wave21-lattice-extension/independent-results.json
    sha256: 735ff677e7837f14ec2a52cbccd827d30abc5eee68ee5e4f8e2bd6a9e5bd21b1
  - path: verification/wave21-lattice-extension/theorem-sources.md
    sha256: 7f70a36ad124a94d983771274cb7b925a4f2560d835b0f607563045110107f8f
method: independent scaled-dual parity argument, exact trace-square congruence, Cauchy and Maclaurin determinant bound, determinant/index factor exhaustion, and hostile relaxations
command: python -B attempts/wave23-endpoint-crosscheck/exact_check.py --output attempts/wave23-endpoint-crosscheck/exact-results.json
outputs:
  - path: attempts/wave23-endpoint-crosscheck/input-freeze.sha256
    sha256: 48d7f4a9340f20140e0c83cb49235f523ad87f6fb46057e9a387487293edbce0
  - path: attempts/wave23-endpoint-crosscheck/exact_check.py
    sha256: 92c480e4b4c45f528f41f825d522982cd273c952104a7fe134b1b4acc161b2da
  - path: attempts/wave23-endpoint-crosscheck/test_exact_check.py
    sha256: 24ae053c2508e8e30c9118d9a58e90b2cf445b536df0de6066ec43143e850bb6
  - path: attempts/wave23-endpoint-crosscheck/exact-results.json
    sha256: 1b31074d0fe4872c14caf1e25842377e4ddab9860f241d87d2814a350ac100a4
  - path: attempts/wave23-endpoint-crosscheck/failed-runs.md
    sha256: ca5f7078e352a1406c9260ead56f2f5cb9c775e1c9099e0ef5b2746190ecc8bb
  - path: attempts/wave23-endpoint-crosscheck/failed-routes.md
    sha256: 86e14750167d09ec330a801af5f81e5d1f3bc7f8ed4b56866de5d9ff5bb62abe
limitations: pending an independent verifier; relies on the audited prose-to-lattice bridges and the even-unimodular signature theorem; no graph is constructed; target existence and novelty remain unknown
correction_provenance:
  frozen_discovery_commit: b3763368049422b5f10f949a8ac02b14ec0fb54f
  verifier_commit: a6771108ec00bddfcc8ae5b41779760673fef22e
  verifier_audit: verification/wave23-endpoint-crosscheck/2026-07-23T195158Z-audit.md
  verifier_audit_sha256: 56cf0b8c14f9af50a58e60a8a6a273726a79d15782527ff8ea46194e9dea5d8c
---

# Wave 23 endpoint cross-check: a trace-square/index exclusion of n3=705

## Verdict

`DERIVED_PENDING_INDEPENDENT_VERIFIER`.

The audited Wave-20 and Wave-21 premises, when combined with one additional
scaled-dual parity observation and the `k=2` Maclaurin inequality, exclude
the endpoint `n3=705`.  Subject to independent verification, the conditional
count bound becomes

```text
n3 >= 708
induced C6 count >= 209994.
```

This remains a necessary condition for a putative graph.  It neither
constructs nor excludes `srg(99,14,1,2)`, whose status remains `UNKNOWN`.
Novelty has not been assessed.

## Separation and frozen premises

This lane used only the five audited artifacts listed in the front matter.
Their hashes and byte lengths were frozen in
`attempts/wave23-endpoint-crosscheck/input-freeze.sha256` before the
derivation.  No other Wave-23 attempt, report, code, result, or message was
inspected during discovery.  After the discovery was frozen at commit
`b3763368049422b5f10f949a8ac02b14ec0fb54f`, the correction described in
Section 7 inspected only the independent audit committed at
`a6771108ec00bddfcc8ae5b41779760673fef22e`; that audit is correction
provenance, not a premise of the main proof.

The imported audited facts are:

1. `M=21E` is the integral rank-44 projector Gram matrix and
   `A4=M(M o M)M`.
2. On `U=im(M)`, the operator `B=A4/21` is positive definite.
3. For `L=U intersect Z^231`, `B` is an integral endomorphism,
   `B=I mod 2L`, and at `Delta=n3-693`,
   `tr(B)=4Delta`.
4. If `G` is the Gram matrix of an integral basis of `L`, then
   `21L*` is contained in `L`,
   `h=[L:21L*]=21^44/det(G)`, and `h` divides `21^44`.
5. With `Q=X^T(M o M)X`,
   `det(B)=h det(Q)`, where `Q` is even, integral, and positive definite.
6. An even unimodular integral form has signature divisible by eight.

At `n3=705`, `Delta=12`, so

```text
rank(B)=44,  tr(B)=48,  tr(A4)=1008.
```

## 1. The scaled dual is an even lattice of determinant h

In coordinates relative to the chosen integral basis of `L`, the inclusion
`21L*` in `L` says exactly

```text
S = 21 G^{-1} is integral.
```

It is symmetric and positive definite, and

```text
det(S)=21^44/det(G)=h.
```

The useful extra observation is that `S` has even diagonal.  Indeed,

```text
S_ii det(G) = 21 det(G without row i and column i).
```

The determinant `det(G)` is odd.  Modulo two, each 43-by-43 principal
submatrix on the right is alternating: it is symmetric with zero diagonal.
An alternating matrix of odd order is singular, so that principal minor is
even.  Since `det(G)` and 21 are odd, `S_ii` is even.

Thus `S` itself is an even integral positive-definite Gram matrix of rank 44
and determinant `h`.  The elementary odd-determinant congruence for an even
rank-44 Gram matrix gives

```text
h = det(S) = 1 mod 4.
```

Moreover, `h=1` is impossible: it would make `S` even, positive definite,
and unimodular of signature 44, whereas an even unimodular form must have
signature divisible by eight.

This argument uses the same frozen signature theorem already audited for
`Q`; it introduces no lattice-classification assumption.

## 2. The first possible trace square is 60

Because `B=I mod 2L`, its integral coordinate matrix has the form

```text
B=I+2C
```

with `C` integral.  At the endpoint,

```text
48=tr(B)=44+2tr(C),
tr(C)=2.
```

For every integral matrix `C`,

```text
tr(C^2) = tr(C) mod 2.
```

The off-diagonal products in `tr(C^2)` occur in equal pairs, while
`C_ii^2=C_ii mod 2`.  Hence `tr(C^2)` is even, and

```text
tr(B^2)
 = tr(I+4C+4C^2)
 = 44+8+4tr(C^2)
 = 4 mod 8.
```

The 44 eigenvalues of the self-adjoint positive-definite operator `B` are
positive reals.  Cauchy gives

```text
tr(B^2) >= tr(B)^2/44 = 48^2/44 = 576/11.
```

The first integer at least `576/11` that is `4 mod 8` is 60.  Therefore

```text
tr(B^2) >= 60,
tr(A4^2)=21^2 tr(B^2) >= 441*60 = 26460.
```

The trace-square bound is sharp before the lattice factorization is used:
the abstract spectrum `3,3,1,...,1` has trace 48 and trace square 60.

## 3. Maclaurin improves the determinant cap from 45 to 42

Let `lambda_1,...,lambda_44` be the positive eigenvalues of `B`, and let
`e_2` be their second elementary symmetric sum.  Newton's identity and the
trace-square lower bound give exactly

```text
e_2
 = (tr(B)^2-tr(B^2))/2
 <= (48^2-60)/2
 = 1122.
```

Since

```text
C(44,2)=946,
1122/946=51/43,
```

the `k=2` and `k=44` cases of Maclaurin's inequalities give

```text
det(B)^(1/22)
 <= e_2/C(44,2)
 <= 51/43.
```

Consequently

```text
det(B) <= (51/43)^22 < 43.
```

The strict comparison is an exact integer comparison:

```text
51^22 = 36859027642628666340203552228411828601
43^23 = 37134234731477575983465092780473537507
gap   =   275207088848909643261540552061708906 > 0.
```

Because `B` is an integral positive-definite endomorphism,
`det(B)` is a positive integer.  Hence

```text
det(B) <= 42.
```

This is the point at which trace-square information strengthens the earlier
trace-only cap 45.

## 4. No determinant/index factor survives

The audited factorization is

```text
det(B)=h det(Q).
```

The congruence `B=I mod 2L` makes `det(B)` odd.  Since `h` is odd,
`det(Q)` is odd.  The matrix `Q` is even, integral, positive definite, and
rank 44, so its odd determinant is `1 mod 4`.  The value one is impossible
by the even-unimodular signature obstruction at rank 44.  Therefore

```text
det(Q) >= 5.
```

Combining this with `det(B)<=42` gives

```text
h <= floor(42/5)=8.
```

But `h` divides `21^44`, so the only 3,7-smooth possibilities at most eight
are

```text
h in {1,3,7}.
```

The scaled-dual determinant congruence `h=1 mod 4` leaves only `h=1`, and
the scaled-dual signature argument already excludes `h=1`.  No endpoint
factorization remains.

Equivalently, the previously audited endpoint list `{1,9}` is closed from
both sides: the scaled dual excludes one, while the new determinant cap
rules out the `h=9,det(Q)=5,det(B)=45` survivor.

## 5. Translation and modular-rank boundary

The Wave-20 divisibility relation gives `3|n3`.  Once 705 is excluded, the
next arithmetically possible value is 708.  The inherited exact identity
for induced six-cycles is `209286+n3`, giving the conditional lower bound
209994.

The binary-rank facts are consistent:

```text
B mod 2 = I on L/2L,          rank_F2(B)=44,
A4 mod 2 = M,                 rank_F2(A4)=44.
```

No endpoint contradiction from ranks modulo 3, 5, or 7 follows from the
frozen data, and none is claimed.  The active modular input is the
modulo-two identity, used to obtain the trace-square residue and odd
determinant.

## 6. Exact replay and hostile routes

The standard-library checker:

- verifies all five frozen input hashes and selected endpoint fields;
- checks the rank-44 determinant residues;
- derives `tr(B^2)>=60`;
- computes `e_2<=1122` and the exact Maclaurin fraction;
- exhausts the possible 3,7-smooth factor pairs;
- writes deterministic LF-only JSON.

All 25 tests pass.  They include exhaustive rank-two and rank-four
even-matrix residue checks, a scaled-dual sanity example, the sharp abstract
trace-square spectrum, input/rank/scale mutations, exact power comparison,
and four hostile relaxations.  Each hostile relaxation leaves a concrete
formal endpoint survivor:

| Omitted condition | Survivor |
|---|---|
| `tr(B^2)=4 mod 8` | `(h,detQ,detB)=(9,5,45)` |
| signature obstruction excluding `det(Q)=1` | `(9,1,9)` |
| `h` is 3,7-smooth | `(5,5,25)` |
| scaled-dual obstruction to `h=1` | ten `h=1` pairs |

The retained route and run ledgers record why none of these weaker systems
is promoted.

## 7. Correction of an ancillary hostile control

The independent audit
`verification/wave23-endpoint-crosscheck/2026-07-23T195158Z-audit.md`
verified the main proof and identified one nonblocking defect in the frozen
hostile ledger.  The original `(9,3,27)` example does not retain all the
claimed constraints: although it arises if the `det(Q)` residue is dropped,
it also violates the frozen identity `det(B)=1 mod 4`.

The repaired single-relaxation control is

```text
(h,det(Q),det(B))=(9,1,9).
```

It omits only the even-unimodular signature obstruction to `det(Q)=1`.
It retains the mod-four residues of all three determinants, 3,7-smoothness,
`det(B)=h det(Q)`, positivity, and the cap `det(B)<=42`.  The invalid
`(9,3,27)` control remains explicitly documented in both ledgers, with the
frozen discovery and verifier commits, so the correction is auditable.

No line of the endpoint exclusion uses either hostile control.  The proof
and conditional bounds are unchanged.

## Scope wall

Publication-safe claim, pending independent verification:

> Every putative `srg(99,14,1,2)` satisfies `n3>=708`, and hence has at
> least 209994 induced six-cycles.

This does not establish that the graph exists, does not provide an adjacency
matrix, and does not establish nonexistence.  Conway-99 remains `UNKNOWN`.
