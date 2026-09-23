# Wave 11 `n3=39` equality-exclusion audit

Verdict: `PUBLISH` only for the conditional exclusion of `n3=39` and the
resulting necessary bound `n3>=42`. Target result: `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T05:29:58Z
git_commit: 19d77662fe6885b12eef731cdc04ca08652f4917
claim_label: VERIFIED
scope: conditional exclusion of n3=39 for a putative srg(99,14,1,2)
inputs:
  agents/2026-07-22-wave6-opposite-edge-graph.md: 4197c40e1b43d72d5a2ad9a6203099ffed2e1dbf4f0b3c07186aaad54cae4fa2
  agents/2026-07-22-wave7-triangle-side-incidence.md: 7b4693420eae7e6f13ce0d66c786424c18863a1b1c350da83097f8e982ebe324
  agents/2026-07-22-wave8-n3-equality.md: 010fe1e2a9752ac18067b44c9e6cf1114e2d1651364c49a574adbe22fe5461f3
  agents/2026-07-22-wave9-n3-33-equality.md: b2fe46cce67440d1a730d6f56b48a512952624d79afa9835ffc772c050c94555
  agents/2026-07-22-wave10-n3-36-equality.md: 9a1e2ad7cac5e26f9fe4117c8ced2390ca15a4dfda7b1e67faa02b8e90ba507e
  verification/n3-39-equality/verify.py: 195f0c87ddca000839ea41edf5569fd4791b1068f2edaaff72c05e0b327c17c5
  verification/test_n3_39_equality.py: bcbe59dc51aa261481010148c936da9e48c08efdd63d28e5d02c31d8692b8b67
  verification/n3-39-equality/audit_local.py: 8db04ec4bb4db4266226581f70e1abc1f74a2e00ddde3277206da634d36c5a9b
  verification/n3-39-equality/verify_local.py: 0113924cc8c36f8cbccad31630e54174de49aeaadcb874c1005f2e8e5622d887
  verification/n3-39-equality/n3-39-local.json: 4cd23939cfb8ec5080b57fb0626e9579b68250a219ea17876a8e1f4066ad2261
  verification/test_n3_39_local.py: c90029a2a1a452456804efe0a2dd43739dfa7e83cd6baa844eed7842fcd87603
method: independent proof reconstruction, explicit diagnostic countermodel, adversarial proof-to-code audit, repaired semantic witnesses, two-implementation local replay, digest validation, and mutation tests
command: |
  python verification/n3-39-equality/verify.py
  python verification/n3-39-equality/verify_local.py --certificate verification/n3-39-equality/n3-39-local.json
  python -m unittest verification/test_n3_39_equality.py verification/test_n3_39_local.py
outputs:
  verdict: PUBLISH
  current_audit_commit: 19d77662fe6885b12eef731cdc04ca08652f4917
  certificate_source_commit: c299b88fbd956c813ff3379ff236b3123a90d242
  conditional_global_n3_lower_bound: 42
  conditional_induced_C6_lower_bound: 209328
  compact_checker_verdict_initial: FAIL
  compact_checker_verdict_final: PASS
  focused_tests: 17_passed
  certificate_records: 8907
  certificate_bytes: 1730729
  certificate_combined_sha256: 452850018ad13362694f5bfff2e4beac03288a113a0391c3456a47cd6fbfe9a1
  conditional_n3_39_survivors: 0
  target_result: UNKNOWN
limitations: all conclusions are conditional on the committed Wave 6-10 reductions and the explicit active-triangle premises below; the checkers accompany rather than replace the human proof; no construction or nonexistence proof for srg(99,14,1,2), and no novelty claim, is made
```

## Publication boundary

`PUBLISH` in this report has a deliberately narrow meaning. It applies to the
following implication:

> If a putative `srg(99,14,1,2)` reaches the committed `n3=39`
> active-triangle reduction and satisfies the explicit premises recorded
> below, then that equality case is impossible.

Together with the earlier conditional bound `n3>=39`, the divisibility
`3 | n3`, and the cited identity

```text
induced_C6_count = 209286 + n3,
```

this gives

```text
n3 >= 42,
induced_C6_count >= 209328.
```

It does not establish that `srg(99,14,1,2)` exists or does not exist. The
Conway-99 target therefore remains `UNKNOWN`. The local replay certificate
also keeps both its `claim_label` and `target_result` at `UNKNOWN`; its zero
survivors refer only to the stated conditional `n3=39` domain.

## Explicit premise boundary

The final proof, compact checker, and replay certificate use the same
premises. Let `A` be the thirteen active graph-triangles, let `L=L[A]`, and
let

```text
K = complement(L[A]).
```

For distinct active triangles `x,y`,

```text
xy in E(K) if and only if xy not in E(L).
```

The complete premise list is:

1. there are exactly thirteen active graph-triangles;
2. `K` is the simple complement of `L[A]` and is 6-regular;
3. each active triangle belongs to exactly three distinct active point sets;
4. every active point set has size at least two;
5. **every active point set is a clique in `K`;**
6. the point hypergraph is linear, so two distinct point sets meet in at most
   one active triangle;
7. three distinct point sets cannot pairwise meet at three distinct active
   triangles, the common-point or Berge-triangle obstruction;
8. after deleting the common labeled copy from two point sets through one
   active triangle, their simple bipartite `L`-crossing has every row and
   column degree in `{0,2}`.

Linearity and the common-point rule make the external sides used below
pairwise disjoint active triangles. If either crossing side has order one,
simplicity and the degree set `{0,2}` make the crossing empty. The complement
premise then converts every missing crossing `L`-edge into a `K`-edge. Point
cliques supply the edges to the common base triangle.

These statements are premises of the local equality argument, not conclusions
of the compact programs. Their derivation from the putative SRG is contained
in the preceding waves and remains part of the conditional dependency.

## Original objection and diagnostic countermodel

The verifier did not accept the first abbreviated statement. It repeatedly
used

```text
empty L-crossing => K-adjacency
```

without explicitly stating that `K` is the complement of `L` on the active
triangles. This was not merely stylistic: without that bridge, the listed
combinatorial conditions admit a concrete countermodel to the proof step.

Take active labels

```text
A, B, C, 0, 1, ..., 9.
```

Use the size-three point set `{A,B,C}` and size-two point sets indexed by

```text
01,12,23,34,45,56,67,78,89,90,04,27,
A1,A5,B3,B8,C6,C9.
```

Let `F` consist of those pair edges together with `AB,AC,BC`, and put

```text
U = {
  02,13,24,35,46,57,68,79,80,91,05,16,
  A3,A8,B2,B9,C4,C7
}.
```

Then `K=F union U` is a simple 6-regular graph. Every listed point set is a
clique in `K`; every active label has point incidence three; the point family
is linear; and it satisfies the common-point rule. The pair graph is
triangle-free, and no outside label is attached to two of `A,B,C`.

If `L` is allowed to be independently empty, every local `L`-crossing has
degree zero. Nevertheless, at the type-`223` occurrence

```text
{A,B,C}, {A,1}, {A,5},
```

the claimed edge `1B` is absent from `K`. Thus the crossing-to-`K` inference
does not follow from the abbreviated hypotheses.

This object is not a countermodel to the repaired proof. If one imposes
`L=complement(K)`, the crossing between `{A,1}` and `{A,B,C}` contains both
`1B` and `1C`; its two columns have degree one, contrary to the crossing
premise. The repaired statement now places the complement equivalence before
every crossing use, and the checkers make its presence executable.

## Reconstruction of the conditional proof

### Active profile

At `n3=39`, the handshake identity gives `sum q=26`. Enumerating
`q>=2` under `3q(T)<=r-1` leaves

```text
r=13: (2^13),
r=12: (2^10,3^2),
r=11: (2^7,3^4),
r=10: (2^4,3^6).
```

The corresponding `K`-degrees are

```text
6;
5 and 2;
4 and 1;
3 and 0.
```

Three non-singleton point cliques through a triangle need three distinct
incident `K`-edges. The mixed profiles force respectively `2`, `8`, and `18`
singleton occurrences, contradicting the established singleton exclusion.
Thus only thirteen `q=2` triangles remain and `K` is 6-regular.

### Expansion and the point-size bound

Let `P` be a point set of size `s`. At every `i in P`, select one external
triangle from each of the two other point sets through `i`. Linearity puts
each selection outside `P`, separates the two choices at a fixed `i`, and
ensures that point sets based at different members of `P` are distinct. If
two selections based at different `i,j` agreed at `x`, those point sets and
`P` would pairwise meet at the three distinct active triangles `i,j,x`,
contrary to the common-point rule.

Hence all `2s` selections are distinct and lie among the `13-s` triangles
outside `P`:

```text
13-s >= 2s.
```

Therefore every active point set has size at most four.

### Eliminating size four

Suppose `|P|=4`. Its eight other point sets have pairwise-disjoint external
parts inside the nine triangles outside `P`. A second size-four point would
already need

```text
3 + 7 > 9
```

external places. Two size-three points would need

```text
2 + 2 + 6 > 9.
```

Thus no other point has size four, at most one has size three, and at least
three of the four occurrences of `P` are type `224`.

Choose two such occurrences. Their four size-two endpoints are distinct.
Each endpoint is adjacent in `K` to its base member of `P` through its
point-clique edge and to the other three members through the empty singleton
crossing and `K=complement(L)`. Every member of `P` therefore has its three
neighbors inside the `K4` plus all four endpoints, giving `K`-degree at least
seven. This contradicts 6-regularity, so no point has size four.

### The `F/U` accounting and type `233`

All point sets now have size two or three. Let `F` be the union of their
point-clique edges and let

```text
U = E(K) minus E(F).
```

If `t_i` is the number of size-three points through active triangle `i`,
linearity makes their incident clique edges disjoint, so

```text
d_F(i) = 3+t_i,
d_U(i) = 3-t_i.
```

At a type-`233` occurrence write

```text
A={i,a}, P={i,j,k}, Q={i,l,m}.
```

The two singleton crossings force the four distinct `K`-edges

```text
aj, ak, al, am.
```

None can lie in `F`. For example, a point set owning `aj`, together with
`A` and `P`, would have the three pairwise intersections `a,i,j`; the other
three edges give the same common-point obstruction. Hence all four are
`U`-edges incident with `a`, whereas `d_U(a)<=3`. Type `233` is impossible.

### Eliminating size three

Let `P={i,j,k}` have size three. If all three occurrences of `P` were type
`333`, the six other size-three points would have twelve pairwise-distinct
external triangles outside `P`, but only ten are available. Thus `P` has a
type-`223` occurrence because type `233` has already been excluded.

Write that occurrence as

```text
P={i,j,k}, A={i,a}, B={i,b}.
```

Empty singleton crossings and the common-point owner veto give

```text
aj, ak, bj, bk, ab in U.
```

In particular, `j` and `k` each have distinct `U`-neighbors `a,b`. Since
each already lies in the size-three point `P`,

```text
2 <= d_U(j)=3-t_j and t_j>=1,
```

so `t_j=1`; similarly `t_k=1`. Their two other point sets are therefore
size-two points. Call their endpoints `c,d` at `j` and `e,f` at `k`.
Expansion makes

```text
a,b,c,d,e,f
```

distinct and outside `P`. The singleton crossings with `P`, followed by the
same common-point owner veto, force

```text
ic, id, ie, if in U.
```

But the type-`223` occurrence at `i` has `t_i=1` and hence `d_U(i)=2`, a
contradiction. No size-three point exists.

Equivalently, the final semantic checker forms exact endpoint unions for all
seven no-`233`, non-all-`333` flowers. With one, two, or three type-`223`
occurrences, the exact capacity/forced-cardinality vectors are

```text
(2,0,0) / (0,2,2),
(2,2,0) / (2,2,4),
(2,2,2) / (4,4,4).
```

Every profile has a root whose forced `U`-edge set exceeds its capacity.

### Parity

Only size-two point sets remain. Double-counting point-triangle incidences
gives

```text
13 * 3 = 39.
```

That cannot be a sum of even point-set sizes. This final contradiction
excludes `n3=39`.

## First compact-checker failure

The first compact program was not accepted as a faithful semantic regression
of the repaired proof. The audited working-tree hashes were

```text
verification/n3-39-equality/verify.py
1db712f7705ac72a6dd8328780e12a3d9f0834d0a6ef1bffedcd8fc7f55364f8

verification/test_n3_39_equality.py
0ad9d423c6c0009fb5b2e279a721a9713c8e1873e970f70047d84751d8a178a8
```

It classified size-three flowers by applying external capacity before
detecting type `233`, and reported

```text
capacity rejections: 7,
type-233 rejections: 50,
root-U rejections: 7.
```

Those are valid mutually exclusive *rejection-priority* counts, but they were
presented as though they were the proof's raw semantic split. The raw split
is instead

```text
has type 233: 56,
all 333: 1,
has 223 and no 233: 7.
```

Six flowers with five size-three petals are both over capacity and type
`233`; the seventh over-capacity flower is the unique all-`333` flower.
Conflating these categories obscured the exact type-`233` and all-`333`
branches.

The original tests also guarded aggregate histograms rather than semantic
witnesses. Changing the propagation coefficient from the justified value two
to an unsupported value three left the `7/50/7` histogram unchanged. Raising
the claimed four-edge type-`233` lower bound to an unsupported five likewise
left every test green. The common-point helper was tested in isolation but
was not on the production witness path, and the complement bridge existed
only in prose. Finally, the output key called the induced-hexagon bound
`global_p6_lower_bound`.

The initial checker therefore received `FAIL` for proof-to-code fidelity.
This did not refute the repaired human argument: it rejected status inflation
by a regression program whose labels and mutation guards were too weak.

## Repaired compact checker

The final compact checker separates raw semantic tags from overlapping
capacity information. Its exact size-three census is

```text
raw classes:
  type 233:                 56
  all 333:                   1
  223/333 with no 233:       7

overlap:
  capacity-feasible 233:    50
  over-capacity 233:         6
  over-capacity all-333:     1
  over-capacity 223/333:     0

profiles by number of 223 occurrences:
  one: 3
  two: 3
  three: 1
```

The crossing-extension totals provide an independent arithmetic checksum:

```text
type-233 raw:              1468 = 700 + 768
all-333 raw:                512
223/333 root profiles:      217
all raw extensions:        2197 = 13^3.
```

More importantly, the checker now constructs exact witnesses on its
production path:

- the type-`233` witness has precisely the four edges
  `{(1,3),(2,3),(3,4),(3,5)}` as forced `K`-edges, forbidden `F`-owners, and
  hence forced `U`-edges;
- the two-`224` witness separates four point-clique endpoint edges from
  twelve complement-inferred edges and gives root degrees `(7,7,7,7)`;
- the propagation witness forms literal endpoint unions and exact forced
  `U`-edge sets, then independently obtains the identical sets from
  common-point owner vetoes;
- the feasible size-four profiles have type-`224` histogram `{3:8,4:1}`;
- the all-size-two state ends in the explicit odd-incidence check;
- the output key is now `global_induced_C6_lower_bound`.

The complement, point-clique, linearity, common-point, and crossing-degree
premises are executable requirements. Removing any required bridge from a
local witness raises an error. Tests compare literal forced-edge sets and
distinct endpoint unions rather than only their eventual rejection counts.
The compact checker now receives `PASS` as a conditional regression companion.

## Independent replay certificate

The slower primary generator and independent replayer use separate
implementations. The committed certificate is

```text
verification/n3-39-equality/n3-39-local.json
file sha256:
4cd23939cfb8ec5080b57fb0626e9579b68250a219ea17876a8e1f4066ad2261

certificate git commit:
c299b88fbd956c813ff3379ff236b3123a90d242

combined stream:
records = 8907
bytes   = 1730729
sha256  = 452850018ad13362694f5bfff2e4beac03288a113a0391c3456a47cd6fbfe9a1
```

Its stream manifest contains:

```text
premises:                 1
crossing matrices:      682
external collisions:   1546
size bounds:             12
degree table:             4
owner motifs:            36
root-four profiles:    6561
root-three profiles:     64
parity records:           1
```

The collision stream divides into `90` linearity collisions and `1456`
common-point collisions. The replay independently confirms the raw
`56/1/7` size-three split while retaining `7/50/7` only as the explicitly
named capacity-first rejection histogram. It also distinguishes the
one-sided singleton-mask test from the invalid one-sided-only mutation,
checks the `224` degree with and without complement inference, and confirms
the exact root-three endpoint fixtures.

Eight certificate mutations are rejected:

```text
drop_stream,
alter_combined_digest,
drop_complement_bridge,
drop_common_point_premise,
drop_point_clique_premise,
drop_crossing_degree_premise,
restore_false_survivor,
inflate_target_status.
```

The current compact and replay suites pass all seventeen focused tests.
Regenerating the certificate in memory from its recorded commit reproduces
the same manifest and combined digest. The replay reports zero survivors only
inside the conditional local domain and prints `target_result UNKNOWN`.

The first detached clone found that the initial writer used platform-default
newlines: Git's LF-normalized certificate and a Windows CRLF regeneration had
different whole-file hashes even though their parsed JSON and canonical stream
digests agreed. That packaging check received `FAIL` for byte portability.
Commit `c299b88fbd956c813ff3379ff236b3123a90d242` now emits canonical LF bytes
for both certificate and replay output and adds a seventh local test. Five hash
seeds reproduce the exact outer file hash shown above as well as the internal
stream hash. The focused total is therefore seventeen tests.

## Limitations and final status

The verifier independently reconstructed every distinctness, degree, owner,
capacity, and parity step used after the active reduction. No restricted
automorphism, connectedness assumption, solver exit code, or absence-of-hit
argument is used. The diagnostic countermodel preserves the original missing
bridge and records why the repair was necessary. The first checker failure is
also retained rather than overwritten by the final passing implementation.

The finite programs are regression and replay companions. They do not derive
the thirteen-triangle reduction, the singleton exclusion, the common-point
rule, the fixed-triangle identities, `3 | n3`, or the induced-hexagon formula
from a raw 99-vertex graph. Those dependencies remain the committed Wave 6-10
premises and cited upstream results. The certificate is a local replay
manifest, not a formal proof object for Conway-99.

No checked literature conclusion establishes novelty for this equality
exclusion, and this report makes no novelty claim. Qualified external review
is still appropriate. The final status is therefore:

```text
conditional n3=39 exclusion: PUBLISH
conditional n3 lower bound:  42
conditional induced C6 bound: 209328
srg(99,14,1,2) target:       UNKNOWN
```
