# Wave 11 computational lane: the \(n_3=39\) equality case

```yaml
role: construction
date_utc: 2026-07-23T05:35:59Z
git_commit: 19d77662fe6885b12eef731cdc04ca08652f4917
claim_label: DERIVED
scope: >
  Independent computational checks of the already reduced n3=39 equality
  case. This report does not claim the full conjecture, does not certify the
  preceding mathematical reductions, and does not promote its own findings
  to VERIFIED.
inputs:
  verification/n3-39-equality/verify.py: 195f0c87ddca000839ea41edf5569fd4791b1068f2edaaff72c05e0b327c17c5
  verification/test_n3_39_equality.py: bcbe59dc51aa261481010148c936da9e48c08efdd63d28e5d02c31d8692b8b67
  verification/n3-39-equality/audit_local.py: 8db04ec4bb4db4266226581f70e1abc1f74a2e00ddde3277206da634d36c5a9b
  verification/n3-39-equality/verify_local.py: 0113924cc8c36f8cbccad31630e54174de49aeaadcb874c1005f2e8e5622d887
  verification/test_n3_39_local.py: c90029a2a1a452456804efe0a2dd43739dfa7e83cd6baa844eed7842fcd87603
  verification/n3-39-equality/n3-39-local.json: 4cd23939cfb8ec5080b57fb0626e9579b68250a219ea17876a8e1f4066ad2261
method: >
  Replayed the finite local proof with two structurally separate
  implementations, audited every emitted JSONL stream, tested deterministic
  regeneration under five hash seeds, mutation-tested the verifier, and
  reconciled the result with an independent colour-preserving nauty census.
command: |
  python verification/n3-39-equality/verify.py
  python verification/n3-39-equality/verify_local.py --certificate verification/n3-39-equality/n3-39-local.json
  python -m unittest -v verification.test_n3_39_equality verification.test_n3_39_local
outputs:
  verification/n3-39-equality/n3-39-local.json: 4cd23939cfb8ec5080b57fb0626e9579b68250a219ea17876a8e1f4066ad2261
limitations: >
  The committed local certificate is independently checkable, but its theorem
  is conditional on the formalized premises and the preceding human
  reductions. The 8,040-type nauty census was independently reproduced and
  digest-recorded, but its generator sources and catalogs were scratch
  artifacts and are not presently archived in this repository. The blind CNF
  branch retained neither a public model nor a proof trace and is therefore
  non-evidentiary. The target conjecture remains UNKNOWN.
```

## Result and evidence boundary

This lane found no admissible object in the reduced \(n_3=39\) equality
case. Three computational routes were deliberately kept at different
evidentiary levels:

| Lane | Result | Public evidentiary status |
|---|---:|---|
| Local finite replay | 8,907 records, nine hashed streams, no surviving local profile | Committed deterministic certificate; independently replayable |
| Colour-preserving nauty census | 8,040 isomorphism types, no compatible mandatory \(K\) | Independently reproduced cross-check; source catalogs are not committed |
| Blind CNF branch | Listed local branches returned UNSAT | Discovery chronology only; no model, DIMACS, or proof trace is archived |

The computational scope is only the frozen equality case. Conditional on the
preceding reductions and on verifier acceptance, excluding this case gives

\[
n_3\geq 42,\qquad
\#C_6^{\mathrm{ind}}\geq 209{,}328,
\]

with branch bounds

```text
[42, 42, 42, 48, 48, 42, 42, 48, 42, 48, 42, 48]
```

This does **not** resolve the target conjecture. Its status remains
`UNKNOWN`.

## Frozen equality profiles

At \(n_3=39\), the active profiles supplied to this lane are:

| rank | point-size profile \(q\) | required \(K\)-degrees | singleton lower bound | outcome before the final equality case |
|---:|---|---|---:|---|
| 13 | \(2^{13}\) | \(6^{13}\) | 0 | surviving equality profile |
| 12 | \(2^{10}3^2\) | \(5^{10}2^2\) | 2 | excluded |
| 11 | \(2^7 3^4\) | \(4^7 1^4\) | 8 | excluded |
| 10 | \(2^4 3^6\) | \(3^4 0^6\) | 18 | excluded |

Thus the finite computation concerns 13 active triples and a 6-regular
complement graph \(K\). No automorphism of a completed object is assumed in
either public checker.

## Committed 8,907-record local replay

The certificate records the proof's local obligations, not a catalog of
global objects. The primary generator constructs explicit canonical flower
data, including \(F\), the mandatory edges of \(K\), the residual graph
\(U\), and owner data. The independent implementation uses a distinct
integer-coded representation and a closed crossing-count calculation. The
two implementations emitted byte-for-byte identical streams.

The committed certificate embeds source commit
`c299b88fbd956c813ff3379ff236b3123a90d242`. Its file SHA-256 at the report
commit is
`4cd23939cfb8ec5080b57fb0626e9579b68250a219ea17876a8e1f4066ad2261`.

### Stream manifest

| stream | records | bytes | SHA-256 |
|---|---:|---:|---|
| `premises` | 1 | 512 | `1c7925ef36a023738279dcf3c7e5fba5ea29055c609f7ca79a24b27a49020100` |
| `crossing_matrices` | 682 | 100,338 | `58d91ba3cd113431183d29a51e5b43c7580bc9815767df35269cfb0f49ddb304` |
| `collisions` | 1,546 | 167,922 | `2e12039f9a70a27f093cd5dbf8d4b8931138eb1b9db0d75908574459190ba8fc` |
| `size_bounds` | 12 | 1,539 | `b4948bf52f4b49253003fa2587c63f8f1f4f9d6883de64d78ef4a82db92ae222` |
| `degree_table` | 4 | 364 | `752f167eed12daf3e9d12429c6fbe45dd5b9fab22edeb7f75179b212fbc552b9` |
| `owner_motifs` | 36 | 4,824 | `701c339f54f9305429e388e129d38b9f9fa5f73491b473cb6295355f3830a3ff` |
| `root4_profiles` | 6,561 | 1,433,584 | `417ccd654d8938a8cb9436306078d9a99643fc129a96e377b1599d3be6d71225` |
| `root3_profiles` | 64 | 21,504 | `a2523cf95f35a59cd9e405553ddfa324b7b640ae8ce53888c77896952fc789df` |
| `parity` | 1 | 142 | `3db91a9a63245986dd93ddbf99fdb9514257a93cb11091f79906d9abdae32969` |
| **combined** | **8,907** | **1,730,729** | **`452850018ad13362694f5bfff2e4beac03288a113a0391c3456a47cd6fbfe9a1`** |

### Replayed local counts

The size-4 root replay checks all \(3^8=6{,}561\) assignments:

- 6,552 fail capacity;
- 9 pass capacity;
- the nine explicit roots have degree histogram \(10:8,\ 11:1\);
- they contribute 33 checked crossing extensions.

The size-3 replay checks all 64 root profiles. The raw type split is:

```text
has 233:           56
all 333:            1
has 223, no 233:    7
```

Six of the 56 `233` profiles fail capacity, as does the single all-`333`
profile. With rejection priority applied, the same records classify as

```text
capacity:  7
type 233: 50
root U:    7
```

The corresponding crossing-extension checks reconcile as:

```text
type 233:       1,468 = 700 + 768
all 333:          512
root 223/333:     217
all raw roots:  2,197 = 13^3
```

The certificate records 917 feasible size-3 extensions and 33 feasible
size-4 extensions. Collision witnesses split into 90 linearity cases and
1,456 common-point cases.

### Determinism and verifier attacks

The complete generation/check cycle was rerun with
`PYTHONHASHSEED=0,1,42,314159,777`. For every seed:

- the compact check passed;
- the primary and independent local generators agreed;
- all 17 focused tests passed;
- the combined stream digest remained
  `452850018ad13362694f5bfff2e4beac03288a113a0391c3456a47cd6fbfe9a1`.

The verifier also rejected all eight targeted certificate corruptions:

```text
drop_stream
alter_combined_digest
drop_complement_bridge
drop_common_point_premise
drop_point_clique_premise
drop_crossing_degree_premise
restore_false_survivor
inflate_target_status
```

## Independent 8,040-type nauty census

This cross-check used nauty 2.9.1 and colour-preserving canonical generation
of bipartite incidence graphs. The left class has 13 vertices of degree 3;
right-class degrees are point sizes 2 through 5; girth at least 8 excludes
incidence \(4\)- and \(6\)-cycles.

Two generation routes were compared:

1. exact resource-profile catalogs; and
2. unprofiled catalogs generated separately for right-class orders 13
   through 19.

After canonical sorting and deduplication, their unions agreed at every
right-class order. The order counts were:

| right-class order | types |
|---:|---:|
| 13 | 0 |
| 14 | 0 |
| 15 | 2 |
| 16 | 159 |
| 17 | 3,665 |
| 18 | 3,935 |
| 19 | 279 |
| **total** | **8,040** |

The nonempty resource profiles
\((x_2,x_3,x_4,x_5)\) were:

| profile | types |
|---|---:|
| \((6,9,0,0)\) | 2 |
| \((9,7,0,0)\) | 141 |
| \((10,5,1,0)\) | 13 |
| \((11,3,2,0)\) | 5 |
| \((12,5,0,0)\) | 3,173 |
| \((13,3,1,0)\) | 451 |
| \((14,1,2,0)\) | 41 |
| \((15,3,0,0)\) | 3,725 |
| \((16,1,1,0)\) | 210 |
| \((18,1,0,0)\) | 279 |

All \(x_5>0\) catalogs were empty. This agrees with the separate analytic
exclusion of point size at least 5.

### Census digests

These hashes identify the independently reproduced run. The names in this
table are audit artifact labels, not claims that the files are currently
present in the public repository.

| artifact | SHA-256 |
|---|---|
| primary census program, `audit_n3_39.py` | `d999a986de0c86e430ab4b4ab12c0350674d4983df200284fd144759df80affb` |
| independent verifier, `verify_n3_39_independent.py` | `075627244dfde7ba4819f2507677edefac4667b8a69ab48c9a35f7fc87eac180` |
| generation wrapper, `generate_n3_39_catalogs.sh` | `4cdd426036a26978232790fee95af26aaf2d4fbe73e0b63d13d953de4492d3d7` |
| modified nauty source, `genbg_profile.c` | `6717709745dc2401588fadf1c4816acd19688d39b9c90596e997d2c36443cdfb` |
| primary audit certificate, `n3-39-audit.json` | `a3ede096784776cf38355056b2a6d3289f0121dcf0b232612873bb605fed1b16` |
| independent verification output | `b66c5c637be409e3d44eb451b4f59b90f8eaf8de82535285aac054a569b355e7` |
| ordered record signature | `923d0aa9c5801d6f9837854f847d2e25bf397aa206e347b0505e3c021cfed7ac` |

The primary and independent consumers both replayed all 8,040 records and
found zero compatible mandatory-\(K\) survivors. For each incidence type,
the mandatory \(K\) contains:

- every clique edge forced by a point; and
- every cross-pair forced when one co-point has size 2, because that
  singleton crossing must be \(L\)-empty.

Every such edge must lie in the required 6-regular \(K\). Yet the minimum
mandatory edge count was 46, while \(K\) has only 39 edges, and the minimum
mandatory maximum degree was 9, while \(K\) has degree 6.

The exact mandatory-edge histogram was:

```text
46:1 47:1 50:4 51:1 52:7 53:13 54:21 55:14 56:53 57:32
58:111 59:81 60:212 61:251 62:481 63:551 64:720 65:865
66:872 67:973 68:812 69:723 70:476 71:357 72:201 73:119
74:54 75:21 76:6 77:3 78:4
```

The mandatory maximum-degree histogram was:

```text
9:1 10:174 11:2705 12:5160
```

### Occurrence reconciliation

Across the 8,040 incidence types, the six rooted local-type totals were:

| local type | occurrences |
|---|---:|
| `222` | 29,115 |
| `223` | 55,479 |
| `224` | 2,797 |
| `233` | 16,308 |
| `234` | 267 |
| `333` | 554 |
| **total** | **104,520 = 8,040 × 13** |

There were 766 size-4 points: 499 had four `224` roots and 267 had three
`224` roots plus one `234` root. Thus

```text
4 × 499 + 3 × 267 = 2,797 occurrences of 224
267 occurrences of 234
```

At graph level, 720 types had a size-4 point. Of the remaining types, 6,024
had a `233` root. The final 1,296 types had neither feature. Their 3,368
size-3 roots had compositions

| `(#223, #333)` | roots |
|---|---:|
| `(1, 2)` | 15 |
| `(2, 1)` | 240 |
| `(3, 0)` | 3,113 |
| `(0, 3)` | 0 |

With the proof's priority order, the graph-level reconciliation is:

```text
size 4:                    720
no size 4, has 233:      6,024
has an all-223 root:     1,225
remaining mixed root:       71
total:                    8,040
```

The raw graph counts are 75 with a mixed root and 1,225 with an all-`223`
root; four graphs have both. Giving the all-`223` class priority explains
the displayed \(1{,}225+71\) split and prevents an apparent four-record
discrepancy. The resulting \(720+6{,}024+71+1{,}225\) partition mirrors the
local proof's obstruction classes.

### Reproduction boundary for the census

The census recipe is precise:

1. use nauty 2.9.1 with the hashed colour-preserving `genbg_profile.c`;
2. enumerate all nonnegative profiles satisfying
   \[
   2x_2+3x_3+4x_4+5x_5=39,\qquad
   x_2+3x_3+6x_4+10x_5\leq39;
   \]
3. generate girth-at-least-8 exact-profile catalogs and, independently,
   unprofiled catalogs for right-class orders 13 through 19;
4. independently recheck degrees, bipartition colours, girth, canonical
   deduplication, and equality of the two catalog unions;
5. replay all records through both mandatory-\(K\) consumers and compare the
   ordered-record signature and output digests above.

The run used nauty's `-Z1` pruning, but every emitted graph was revalidated
directly. No symmetry or automorphism of the completed graph was assumed.

The public repository does not yet archive the modified generator, wrappers,
catalogs, or audit JSON. Consequently the hashes make a later archival replay
auditable, but the current repository alone is insufficient for a clean
one-command regeneration. This is why the census is a strong independent
`DERIVED` cross-check rather than the publication certificate.

## Defects found and repaired

The audit was useful precisely because the first implementation was not
treated as authoritative. The following defects were found and repaired
before the final hashes above were frozen:

1. **Raw and priority counts were conflated.** The compact checker exposed
   `7/50/7` as though it were the raw size-3 split. It now reports the raw
   `56/1/7` split separately and makes the six-profile capacity overlap
   explicit.
2. **Aggregate tests were too weak.** Mutating an endpoint coefficient from
   2 to 3, or a lower bound from 4 to 5, could leave snapshots unchanged.
   Tests now inspect exact edge-set witnesses, literal endpoint unions, and
   premise gates.
3. **A consequence was mislabeled.** `global_p6` was renamed
   `global_induced_C6`.
4. **The local certificate was initially absent.** That caused a
   `FileNotFound` failure. The deterministic certificate is now committed,
   and an environment override permits isolated scratch regeneration.
5. **Premises were outside the authenticated streams.** They now live in
   the hashed `premises` JSONL stream.
6. **The active-point clique premise was implicit.** The checker now states
   and tests that every active point induces its required clique in \(K\).
7. **The two replays shared too much structure.** The primary replay now
   constructs explicit \(F,K,U\), and owner objects; the independent replay
   uses a distinct integer encoding and closed crossing formula. Owner
   intersections are explicitly checked.
8. **The expected-hash table was empty.** All nine stream constants and the
   combined digest are now frozen and enforced.
9. **Mutation coverage was incomplete.** Five mutations were expanded to the
   eight attacks listed above.
10. **One root-3 formula was wrong.** The independent replay used
    \(2(\#223-\text{own223})\), which fails for mixed `233` roots. It now uses
    “all size-2 petals minus size-2 petals at the root.” Exactly 50 feasible
    records had exposed the mismatch; the final root-3 digest is the one
    recorded in the manifest.
11. **Premise and edge distinctness were under-asserted.** Every witness now
    carries the linearity premise; `two224` also carries the common-point
    premise; singleton crossing tables and edge distinctness are checked in
    production and in deletion tests.
12. **The complement bridge was only implicit.** A diagnostic countermodel
    showed that omitting \(K=\overline L\) is fatal. The bridge is now an
    executable premise and deleting it makes verification fail.
13. **The outer JSON used platform-default newlines.** A detached clone found
    different LF and CRLF whole-file hashes despite identical parsed JSON and
    canonical record streams. Both writers now emit LF bytes explicitly, and
    the local suite contains a newline regression test.

An additional strengthening, rather than a soundness repair, replaced a
coarse size-4 root lower bound of 7 with explicit constructions showing
degrees 10 or 11 for all nine capacity-feasible roots.

## Blind CNF branch: chronology only

A separately written blind CNF search considered only the mandatory
incidence, girth, 6-regular-\(K\), point-clique, and singleton-crossing
conditions. Before the local proof and nauty reconciliation were used, the
branches corresponding to local types `222`, `223`, `233`, and `333`, and
the size-4 types `224` and `234`, returned `UNSAT`. Point size 5 was
eliminated analytically rather than by that CNF run.

No public script, DIMACS instance, solver version manifest, DRAT/LRAT trace,
or independently checked proof artifact survives from this branch. Solver
exit status and model confidence are not certificates. No variable or clause
counts are asserted here. These runs therefore contribute no evidence to the
reported exclusion and are retained only to document discovery chronology.

## Public verification commands

From the repository root:

```powershell
python verification/n3-39-equality/verify.py
python verification/n3-39-equality/verify_local.py --certificate verification/n3-39-equality/n3-39-local.json
python -m unittest -v verification.test_n3_39_equality verification.test_n3_39_local
```

For a deterministic regeneration without overwriting the committed
certificate, use a disposable directory:

```powershell
$scratchRoot = Join-Path ([System.IO.Path]::GetTempPath()) "n3-39-local-replay"
New-Item -ItemType Directory -Force -Path $scratchRoot | Out-Null

foreach ($seed in 0, 1, 42, 314159, 777) {
    $env:PYTHONHASHSEED = "$seed"
    $runRoot = Join-Path $scratchRoot "seed-$seed"
    New-Item -ItemType Directory -Force -Path $runRoot | Out-Null
    $certificate = Join-Path $runRoot "n3-39-local.json"
    $streams = Join-Path $runRoot "streams"

    python verification/n3-39-equality/audit_local.py `
        --certificate $certificate `
        --dump-dir $streams `
        --git-commit c299b88fbd956c813ff3379ff236b3123a90d242

    $env:N3_39_CERTIFICATE = $certificate
    python verification/n3-39-equality/verify_local.py --certificate $certificate
    python -m unittest -v verification.test_n3_39_equality verification.test_n3_39_local
    Get-FileHash -Algorithm SHA256 $certificate
}

Remove-Item Env:N3_39_CERTIFICATE -ErrorAction SilentlyContinue
Remove-Item Env:PYTHONHASHSEED -ErrorAction SilentlyContinue
```

The combined stream digest should be identical for all five seeds. Any
deviation from the manifest above is a failed replay, not a new mathematical
result.
