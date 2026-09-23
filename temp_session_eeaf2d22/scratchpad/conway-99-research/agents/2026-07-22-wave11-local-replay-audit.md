# Wave 11 independent audit of the `n3=39` local replay

Verdict: the first implementation was rejected. After the repairs recorded
below, the conditional rooted-flower replay receives `PASS`. The Conway-99
target result remains `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T05:29:54Z
git_commit: 19d77662fe6885b12eef731cdc04ca08652f4917
claim_label: VERIFIED
scope: independent verification of the conditional n3=39 rooted-local-flower replay
inputs:
  verification/n3-39-equality/audit_local.py: 8db04ec4bb4db4266226581f70e1abc1f74a2e00ddde3277206da634d36c5a9b
  verification/n3-39-equality/verify_local.py: 0113924cc8c36f8cbccad31630e54174de49aeaadcb874c1005f2e8e5622d887
  verification/test_n3_39_local.py: c90029a2a1a452456804efe0a2dd43739dfa7e83cd6baa844eed7842fcd87603
  verification/n3-39-equality/n3-39-local.json: 4cd23939cfb8ec5080b57fb0626e9579b68250a219ea17876a8e1f4066ad2261
method: adversarial source review, explicit local-flower reconstruction, bytewise comparison of two standard-library implementations, scratch certificate regeneration, frozen-digest replay, semantic mutation fixtures, and unit tests
command: |
  python verification/n3-39-equality/audit_local.py `
    --certificate "<scratch>/n3-39-local.json" `
    --git-commit c299b88fbd956c813ff3379ff236b3123a90d242 `
    --dump-dir "<scratch>/streams"
  python verification/n3-39-equality/verify_local.py `
    --certificate "<scratch>/n3-39-local.json" `
    --output "<scratch>/replay.json"
  $env:N3_39_CERTIFICATE = "<scratch>/n3-39-local.json"
  python -m unittest -v verification/test_n3_39_local.py
  Remove-Item Env:N3_39_CERTIFICATE
  python verification/n3-39-equality/verify_local.py `
    --certificate verification/n3-39-equality/n3-39-local.json
outputs:
  initial_verdict: FAIL
  final_conditional_replay_verdict: PASS
  tests: 7_passed
  certificate_records: 8907
  certificate_bytes: 1730729
  combined_stream_sha256: 452850018ad13362694f5bfff2e4beac03288a113a0391c3456a47cd6fbfe9a1
  certificate_file_sha256: 4cd23939cfb8ec5080b57fb0626e9579b68250a219ea17876a8e1f4066ad2261
  certificate_git_commit: c299b88fbd956c813ff3379ff236b3123a90d242
  archive_git_commit: 19d77662fe6885b12eef731cdc04ca08652f4917
  conditional_n3_39_survivors: 0
  conditional_global_n3_lower_bound: 42
  conditional_induced_C6_lower_bound: 209328
  target_result: UNKNOWN
limitations: conditional on the frozen active-triangle reduction and local point-set premises; this is regression evidence for that proof layer, not a standalone certificate for existence or nonexistence of srg(99,14,1,2)
```

## Frozen proof boundary

The replay starts after the human reduction of the `n3=39` case to thirteen
active triangles. It assumes:

```text
active_triangle_count=13
K_is_simple_complement_of_L_on_distinct_active_triangles
K_is_6_regular
each_active_triangle_has_exactly_three_point_sets
active_point_sets_have_size_at_least_two
every_active_point_set_is_a_clique_in_K
point_hypergraph_is_linear
common_point_Berge_triangle_is_forbidden
every_labeled_crossing_degree_is_zero_or_two
```

These assumptions are not conclusions of this replay. They are serialized in
`premises.jsonl`, included in the combined digest, duplicated at the
certificate envelope, and checked against a frozen independent constant.

## Initial adversarial verdict: `FAIL`

The first submitted replay had correct headline counts but was not acceptable
as independent regression evidence.

1. The expected certificate `n3-39-local.json` was absent, so the unit test
   failed before running a test.
2. The premise list lived outside the hashed record streams. Removing the
   complement, common-point, or two-sided crossing premise left every stream
   hash unchanged; rejection depended only on a separate string-list check.
3. Both implementations encoded the same terminal formulas directly:
   size four used `3+2*chosen224`, while size three used the same
   occurrence-count expression for forced `U`-degree.
4. Neither implementation constructed the local point sets, the point-clique
   edge set `F`, singleton-forced `K`-edges, or `U=K-F`.
5. The owner stream merely emitted `rejection: common_point`; it did not
   construct the three point sets and check their three distinct singleton
   intersections.
6. The independent verifier had no nonempty frozen stream-hash table, so a
   coordinated change to both programs and the certificate could pass.
7. Only five certificate mutations were tested. In particular, common-point,
   point-clique, and crossing-premise deletion were not included.

The first scratch generator and replay agreed with each other, but agreement
between two implementations sharing those omissions was insufficient.

## Exact repairs required by the audit

The verifier required the following changes before reconsidering the replay:

- add `premises.jsonl` as the first stream and include it in the combined hash;
- add the missing premise that every active point set is a clique in `K`;
- construct canonical rooted flowers with disjoint external labels;
- construct `F` from point-clique edges;
- enumerate the labeled crossing matrices on both sides, and add a cross-pair
  to mandatory `K` only when a singleton-side crossing is uniquely empty;
- derive the size-four degree lower bound from the constructed edge set;
- form `U` from mandatory `K`-edges after removing `F`;
- construct a hypothetical owner for every forced cross-edge and verify that
  the three pairwise intersections are singletons at three distinct vertices;
- make the independent verifier derive its counts by a structurally different
  integer-coded enumeration and closed crossing-count table;
- freeze every stream byte count, record count, and SHA-256, plus the combined
  digest;
- add premise-deletion and semantic mutation fixtures;
- allow the tests to receive a scratch certificate through
  `N3_39_CERTIFICATE`;
- publish the regenerated certificate and retain target status `UNKNOWN`.

## Intermediate root-three mismatch and repair

The first explicit-flower repair exposed one real disagreement. The primary
implementation counted singleton-forced edges from mixed `233` occurrences,
while the independent implementation retained the older formula that counted
only homogeneous `223` occurrences. Exactly fifty feasible root-three records
differed.

Let `c_i` be the number of size-two petals at occurrence `i` of a size-three
root point. A size-two petal at `i` contributes one forced `U`-edge to each of
the other two root vertices and none to `i`. Consequently

```text
forcedU(v) = sum_{i != v} c_i
           = total number of size-two petals - c_v.
```

Here `c_v=d_U(v)`. The repaired independent formula is therefore

```python
total_size_two_petals = sum(capacities)
forced = [
    total_size_two_petals - capacity
    for capacity in capacities
]
```

It is applied only to flowers within the ten-vertex external budget;
capacity-rejected records retain the zero vector. The discarded formula
differed from the explicit construction on exactly fifty profiles and would
have produced root-three stream digest
`b7a40f4ea3708e7291ece353431b674d011df6d80f972252dad8a5b3d3b634b3`.

After this correction, all nine streams from the primary and independent
implementations are byte-for-byte identical.

## Final stream manifest

Canonical records use sorted-key, compact ASCII JSON followed by one LF byte.

| Stream | Records | Bytes | SHA-256 |
|---|---:|---:|---|
| `premises.jsonl` | 1 | 512 | `1c7925ef36a023738279dcf3c7e5fba5ea29055c609f7ca79a24b27a49020100` |
| `crossing_matrices.jsonl` | 682 | 100338 | `58d91ba3cd113431183d29a51e5b43c7580bc9815767df35269cfb0f49ddb304` |
| `collision_pairs.jsonl` | 1546 | 167922 | `2e12039f9a70a27f093cd5dbf8d4b8931138eb1b9db0d75908574459190ba8fc` |
| `size_bounds.jsonl` | 12 | 1539 | `b4948bf52f4b49253003fa2587c63f8f1f4f9d6883de64d78ef4a82db92ae222` |
| `degree_table.jsonl` | 4 | 364 | `752f167eed12daf3e9d12429c6fbe45dd5b9fab22edeb7f75179b212fbc552b9` |
| `owner_motifs.jsonl` | 36 | 4824 | `701c339f54f9305429e388e129d38b9f9fa5f73491b473cb6295355f3830a3ff` |
| `root4_profiles.jsonl` | 6561 | 1433584 | `417ccd654d8938a8cb9436306078d9a99643fc129a96e377b1599d3be6d71225` |
| `root3_profiles.jsonl` | 64 | 21504 | `a2523cf95f35a59cd9e405553ddfa324b7b640ae8ce53888c77896952fc789df` |
| `parity.jsonl` | 1 | 142 | `3db91a9a63245986dd93ddbf99fdb9514257a93cb11091f79906d9abdae32969` |

The ordered concatenation has:

```text
records: 8907
bytes:   1730729
sha256:  452850018ad13362694f5bfff2e4beac03288a113a0391c3456a47cd6fbfe9a1
```

The committed certificate file has SHA-256
`4cd23939cfb8ec5080b57fb0626e9579b68250a219ea17876a8e1f4066ad2261`.
Its embedded source commit is
`c299b88fbd956c813ff3379ff236b3123a90d242`; commit
`19d77662fe6885b12eef731cdc04ca08652f4917` archives the certificate and
verification record.

## Semantic fixtures

The final replay checks more than record totals.

### Labeled crossings

The accepted crossing-matrix counts for dimensions `1..3` are

```text
        right
left    1  2  3
  1     1  1  1
  2     1  2  4
  3     1  4 16
```

For the full `1-by-2` mask, a one-sided check would accept the row degree two,
while the required two-sided check rejects the two column degrees one. The
fixture is exactly `[true,false]`.

### Distinct external vertices and common-point owners

The collision basis contains:

```text
linearity collisions:    90
common-point collisions: 1456
```

Disabling the common-point rule exposes `1456` collision records and `36`
owner motifs. In both implementations, every owner motif constructs the two
point sets through their common root and the attempted edge owner. Their
pairwise intersections are checked to be singleton sets whose union has size
three.

### Complement bridge and size four

The canonical two-occurrence `224` witness gives minimum root degree seven
when empty `L`-crossings are complemented into `K`; retaining only
point-clique edges gives degree three. The exact mutation fixture is `[7,3]`.

Among the `3^8=6561` ordered size-four petal profiles:

```text
external-capacity rejections: 6552
K-degree rejections:             9
feasible crossing extensions:   33
explicit root-degree histogram:
  capacity rejected: 6552
  lower degree 10:       8
  lower degree 11:       1
```

Changing the nine-vertex outside budget to ten changes the feasible-profile
count from `9` to `45`.

### Size three

The sixty-four raw petal-size words split as:

```text
has a 233 occurrence:          56
all occurrences are 333:       1
has 223 and no 233 occurrence:  7
```

After the external-capacity filter:

```text
external-capacity rejections:   7
type-233 U-degree rejections:  50
root U-degree rejections:       7
feasible crossing extensions: 917
```

The exact forced-`U` fixtures are:

```text
petals              d_U       forced_U
2,2,2,2,2,3       2,2,1       3,3,4
2,2,2,2,3,3       2,2,0       2,2,4
2,2,3,3,3,3       2,0,0       0,2,2
2,2,2,2,2,2       2,2,2       4,4,4
3,3,3,3,3,3       0,0,0       0,0,0
```

The final row is rejected by external capacity; it confirms that no forced
degree is claimed for a flower that cannot fit in the thirteen-vertex domain.

### Degree table and parity

For `t=0,1,2,3` size-three point sets through a vertex, the replay checks

```text
d_F = 3+t
d_U = 3-t = 3,2,1,0.
```

After sizes three and four are eliminated, all point sets would have size two.
Their incidence sum would be even, contradicting the recorded total
`13*3=39`.

## Eight rejected certificate mutations

The independent verifier rejects:

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

The premise-deletion cases are protected twice: the certificate envelope must
equal the frozen premise tuple, and the premise stream must match its frozen
SHA-256 and the combined digest.

## Final status boundary

The first detached clone found that the original outer JSON writer used
platform-default newlines. Git's LF copy and a Windows CRLF regeneration had
different file hashes even though their parsed JSON and internal canonical
stream hashes agreed. The writer now emits LF bytes explicitly, and a seventh
test rejects CRLF output. Five hash seeds reproduce both the file hash and the
combined stream hash recorded above.

The two standard-library implementations now agree exactly, the committed
certificate independently replays, all seven tests pass, the semantic mutation
fixtures pass, and the proof boundary is hash-bound. This verifies the
conditional local replay from the stated thirteen-active-triangle premises to
the contradiction at `n3=39`.

It does not independently establish those upstream premises from an arbitrary
`srg(99,14,1,2)`, does not enumerate all original graphs, and does not produce
a standalone Conway certificate. The conditional consequences recorded by
the certificate are

```text
n3 >= 42
induced_C6_count >= 209328.
```

The research target remains:

```text
UNKNOWN
```
