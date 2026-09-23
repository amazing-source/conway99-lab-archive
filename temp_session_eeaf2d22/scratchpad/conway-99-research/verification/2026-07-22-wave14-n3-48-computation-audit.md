# Wave 14 independent computation audit: conditional \(n_3=48\)

```yaml
role: verifier
date_utc: 2026-07-23T09:37:49Z
git_commit: fd02baec74a5cc19dd415277f9d2504e2d022a9f
claim_label: VERIFIED
scope: >
  Independent verification of the Wave 14 conditional n3=48 active-local
  computation lane: the twelve sum-q profiles, inherited three-profile
  filter, flower and rooted-local finite reductions, eleven-branch cover,
  all thirteen deterministic CNF streams, the one positive full active-local
  certificate, two positive weakened controls, raw scan status boundary, and
  mutation/provenance resistance. This scope does not include a 99-vertex
  graph, H, global SRG equations, a proof of any solver-negative row, or the
  truth of the inherited Wave 6--13 premises.
inputs:
  agents/2026-07-22-wave14-n3-48-computational.md: 54b532035f0ac3c09aaafd1a825600151d6ae55d3a2fcb87f911cfe37dc8b756
  code/wave14_n3_48_profiles.py: fb7c670d0240401929bac609177c83dd618c6baf5969a2e99e6f0dc7ed48f827
  code/wave14_n3_48_active_sat.py: 84e0dcd6cd11f4742abecfe00e1df1ac96047a8967d94f8f5e735d330b4a2ef2
  code/wave14_n3_48_verify.py: 6b2318acc5784290c2f5a32046cd76535bf00db9123b4de4246b882cd2b7c827
  code/wave14_n3_48_test.py: e29999d7485ef3fefc6a32892d2889fd5c1bf6db69733866ea3803ffed0a28ef
  attempts/wave14-computation/n3-48-profile-census.json: c2acf43d29aa08179869a31327991336ac54559fa5ec4915d9f3ea993de7bb5a
  attempts/wave14-computation/n3-48-active-local-scan.json: 4ce53c2fc8a8c0bc005ac1b73dc657ea3c8b7a7f1e3bae1cd73f24de73c539f2
  attempts/wave14-computation/n3-48-positive-controls.json: db6fb90836dc16440a9e0c73ccff420516af9641e60d6775537f7a695e33ae33
  attempts/wave14-computation/n3-48-r16-q2x16-no-size3-full-candidate.json: b5873ddca8dd92bbcc50fb91b942472f426010264fcfe5599912e178318f4ad5
  attempts/wave14-computation/n3-48-r16-q2x16-root-q3x0-no_common_point_control-candidate.json: a5f049c7a7651db6ae8ba5d08cd4d5509814fdcc6202a5080a549acefb0fc024
  attempts/wave14-computation/n3-48-r16-q2x16-no-size3-k_degree_upper_control-candidate.json: 0cb8644bbd6013dbdb1e00657a3cf6a6e9c3a146ad65a43e7270aee6488c1e37
  attempts/wave14-computation/n3-48-independent-validation.json: 20ac2afa64329074677f698331460a27e987ff74527e99ceeee5e5f01fc6d069
  attempts/wave14-computation/n3-48-run-failures.json: 0a4b82afccf09ed26a5dcd34306243723115ff304bbe6f018286c1de141c57b3
method: >
  A fresh verifier importing no Wave 14 discovery module independently
  enumerated integer partitions, flower words, and rooted local modes;
  rebuilt the PySAT CNFs clause by clause; recomputed every materialized
  DIMACS hash; validated the three raw positive objects from their point and
  K-edge lists; fixed those decisions back into independently rebuilt CNFs;
  and attacked certificate, formula, provenance, status, premise, and
  semantic-hash metadata with hostile mutations.
command: |
  $env:PYTHONDONTWRITEBYTECODE='1'
  .venv\Scripts\python.exe verification\n3-48-computation\independent_audit.py
  .venv\Scripts\python.exe -m py_compile verification\n3-48-computation\independent_audit.py
  .venv\Scripts\python.exe code\wave14_n3_48_test.py -v
outputs:
  verification/n3-48-computation/independent_audit.py: e0199aaa481b632104ab200496bf2b20efed529a93901a0d401220e062f66d51
  verification/n3-48-computation/independent-audit-results.json: b19959c358526b710ed1b7e7beff477ddbc35b975609ab1ccd917ccb0f0a5ae4
limitations: >
  The git_commit is the candidate report's declared frozen starting commit;
  no Git command was run. No Wave 14 proof report or artifact and no Wave 13
  path was inspected. The three-profile filter imports the previously
  verified degree-three obstruction without re-auditing it. Seven UNSAT
  returns lack emitted and checked proof traces and remain non-evidentiary.
  One budget return and two timer returns remain UNKNOWN. The model omits the
  inactive and global structures listed below. The positive full object is
  an active-local relaxation certificate, not H, not a Conway graph, and not
  a counterexample. Conditional n3=48 exclusion, the target, and novelty
  remain UNKNOWN.
```

## Verdict

**PASS within the stated conditional active-local scope.** No critical defect
was found.

The exact finite enumerations, branch normalization, formula streams, positive
certificate, weakened controls, archive provenance, and status boundary all
reproduced. `VERIFIED` above applies only to those scoped computational claims.
It does not apply to any negative solver return or to Conway-99.

## Conditional boundary

This audit takes the following Wave 6--13 facts as inherited premises rather
than re-proving them:

1. \(\sum_Tq(T)=2n_3/3\), \(q(T)\ge2\), and \(d_L(T)=3q(T)\).
2. \(K\) is the simple complement of \(L\) on distinct active labels.
3. Every active label lies in exactly three non-singleton linear point sets,
   and every selected point is a \(K\)-clique.
4. Three points cannot pairwise meet at three distinct labels.
5. A meeting crossing has every row and column \(L\)-degree in
   \(\{0,2\}\).
6. A full \(2\)-by-\(2\) \(L\)-crossing contributes four to the fixed-point
   total \(2\sum_{T\in P}q(T)\).
7. The expansion bound \(2s\le r-s\).
8. The previously verified degree-three obstruction used in the inherited
   profile filter.

The verifier checks the deductions made from these premises. It does not
claim that this lane independently establishes the premises themselves.

## Twelve profiles and three inherited survivors

Independent nondecreasing partitioning of \(32\), followed by
\(3q\le r-1\), produced exactly these rows. The displayed \(K\)-degrees are
\(r-1-3q\).

| \(r\) | \(q\)-multiset | \(K\)-degree multiset | inherited result |
|---:|---|---|---|
| 16 | \(2^{16}\) | \(9^{16}\) | survives |
| 15 | \(2^{14}4\) | \(8^{14}2\) | \(d_K<3\) |
| 15 | \(2^{13}3^2\) | \(8^{13}5^2\) | survives |
| 14 | \(2^{12}4^2\) | \(7^{12}1^2\) | \(d_K<3\) |
| 14 | \(2^{11}3^2 4\) | \(7^{11}4^2 1\) | \(d_K<3\) |
| 14 | \(2^{10}3^4\) | \(7^{10}4^4\) | survives |
| 13 | \(2^{10}4^3\) | \(6^{10}0^3\) | \(d_K<3\) |
| 13 | \(2^9 3^2 4^2\) | \(6^9 3^2 0^2\) | \(d_K<3\) |
| 13 | \(2^8 3^4 4\) | \(6^8 3^4 0\) | \(d_K<3\) |
| 13 | \(2^7 3^6\) | \(6^7 3^6\) | inherited degree-three obstruction |
| 12 | \(2^4 3^8\) | \(5^4 2^8\) | \(d_K<3\) |
| 11 | \(2\,3^{10}\) | \(4\,1^{10}\) | \(d_K<3\) |

The three inherited survivors are therefore
\(r16\text{-}q2x16\), \(r15\text{-}q2x13\text{-}q3x2\), and
\(r14\text{-}q2x10\text{-}q3x4\). The archived profile semantic digest
recomputed as
`07eb5c0430458adb4e17a00d27b3635d14031d87c185adb48368f56bfb75bd13`.

## Flower and size reductions

For a selected root point of size \(s\), the two petals at each root
occurrence have disjoint external parts. A singleton petal endpoint is
\(K\)-adjacent to every root label. For root occurrence \(i\), the independent
degree lower bound used was

\[
(s-1)+\#\{\text{all singleton petals}\}
 +\sum_{\substack{\text{large petals}\\\text{based at }i}}(|Q|-1).
\]

The exhaustive results were:

| profile/root size | total words | capacity-feasible | degree survivors |
|---|---:|---:|---:|
| \(r=16,s=5\) | \(4^{10}=1{,}048{,}576\) | 11 | 0 |
| \(r=16,s=4\) | \(3^8=6{,}561\) | 423 | 16 |
| \(r=15,s=5\) | \(4^{10}=1{,}048{,}576\) | 1 | 0 |
| \(r=15,s=4\) | \(3^8=6{,}561\) | 157 | 0 |
| \(r=14,s=4\) | \(3^8=6{,}561\) | 45 | 0 |

The exact sixteen \(r=16,s=4\) survivors are all concatenations of four
ordered pairs, each independently equal to \((2,3)\) or \((3,2)\):

```text
23232323 23232332 23233223 23233232
23322323 23322332 23323223 23323232
32232323 32232332 32233223 32233232
32322323 32322332 32323223 32323232
```

Every word has four singleton petals and one based size-three petal at each
root, saturating degree nine:

\[
3\text{ roots}+4\text{ singleton endpoints}+2\text{ based endpoints}=9.
\]

For any based size-three petal, its two external labels must consequently be
\(L\)-adjacent to the other three roots. The resulting \(K_{3,2}\)
\(L\)-crossing has row degrees \((2,2,2)\) and column degrees \((3,3)\).
The two-sided \(\{0,2\}\) rule rejects all sixteen. Thus all three profiles
reduce to point sizes two and three.

## Rooted local modes and the safe 11-to-4 reduction

For a selected size-three point \(P=\{i,j,k\}\), let \(t_i\) be the number
of size-three points through \(i\), including \(P\), and let \(z_i\) count
the other size-three petals through \(i\) whose \(L\)-crossing with \(P\)
is empty. The verifier independently exhausted
\(t_i\in\{1,2,3\}\) and \(0\le z_i<t_i\), using:

\[
3+t_i+t_j+t_k\le r-3,
\]

\[
d_U(i)\ge\sum_{j\ne i}(3-t_j+2z_j),\qquad
d_U(i)\le d_K(i)-(3+t_i),
\]

and

\[
4\sum_i(t_i-1-z_i)\le2(q_i+q_j+q_k).
\]

| \(r\) | root \(q\)-type | labeled modes | equal-\(q\) coordinate orbits |
|---:|---|---:|---:|
| 16 | 222 | 32 | 10 |
| 15 | 222 | 8 | 4 |
| 15 | 223 | 0 | 0 |
| 15 | 233 | 0 | 0 |
| 14 | 222 | 1 | 1 |
| 14 | 223 | 0 | 0 |
| 14 | 233 | 0 | 0 |
| 14 | 333 | 0 | 0 |

The raw cover is symmetry-safe: an assignment has no selected triple, or one
selected triple has one of the enumerated numbers of \(q=3\) labels. Only
permutations within equal-\(q\) label classes name a chosen root. No
completed-graph automorphism, transitivity, or connectedness is assumed.

The eleven raw branches consist of 2 branches at \(r=16\), 4 at \(r=15\),
and 5 at \(r=14\). Empty rooted-mode tables eliminate all roots containing a
\(q=3\) label. The \(r=15\) all-size-two branch is impossible because its
total incidence \(3r=45\) is odd. In the \(r=14\) all-size-two branch, the
three \(F\)-neighbours of a \(q=3\) label and two further distinct
length-two neighbours force \(d_K\ge5>4\). The exact surviving cover is:

```text
r16-q2x16       no-size3
r16-q2x16       root-q3x0
r15-q2x13-q3x2  root-q3x0
r14-q2x10-q3x4  root-q3x0
```

## Formula semantics and exact streams

The independent builder used PySAT 1.9.dev7 and reconstructed:

- a selected-point variable for every two- and three-subset;
- a \(K\)-edge and an exact point-owned \(F\)-edge variable for every label
  pair;
- exact incidence three at every label;
- linear pair ownership, \(F\) if and only if a selected point owns the pair,
  and selected-point \(K\)-cliques;
- the common-point rule as “every \(F\)-triangle is its selected triple”;
- singleton-side meeting crossings forced \(L\)-empty, and every \(2\)-by-\(2\)
  crossing forced either \(L\)-empty or \(L\)-complete;
- reified full-\(L\) overlap witnesses and the cap
  \(\#\text{full overlaps}\le\lfloor\sum_{v\in P}q(v)/2\rfloor\);
- exact profile \(K\)-degrees; and
- branch units appended to the deterministic DIMACS stream.

The no-common-point control omits the common-point clauses and requires an
unowned \(F\)-triangle witness. The degree-upper control replaces exact
\(K\)-degrees by upper bounds and forces label zero to be deficient.

Every independently rebuilt tuple below matches both the archive and the
candidate report. Counts are
`variables / base clauses / branch units / materialized clauses`.

| profile | branch | variant | counts | materialized DIMACS SHA-256 |
|---|---|---|---|---|
| r16-q2x16 | no-size3 | full | 469160 / 1639520 / 560 / 1640080 | `4f0a295ce08409877efee09f87f1ccaf289ea5fe3014d115a4ef99e3e2b5ebdb` |
| r16-q2x16 | root-q3x0 | full | 469160 / 1639520 / 1 / 1639521 | `010481d24a8870fd5918b748f67a71bae0159aaabed5df4d911f3379c828769d` |
| r15-q2x13-q3x2 | no-size3 | full | 326446 / 1137931 / 455 / 1138386 | `e9d9a23627adaa7d52e630e9477c26ad549b72a9f8057f3d45022821cd7cac78` |
| r15-q2x13-q3x2 | root-q3x0 | full | 326446 / 1137931 / 1 / 1137932 | `54d2c55fb75c51df00db9900245d0aefce058990f0b214498ffd87bc36d6750f` |
| r15-q2x13-q3x2 | root-q3x1 | full | 326446 / 1137931 / 1 / 1137932 | `8f4e055f9423431ce3f1aaa9478d534881c681aac97b8deaf5fdf268e06ba514` |
| r15-q2x13-q3x2 | root-q3x2 | full | 326446 / 1137931 / 1 / 1137932 | `76d1da14f0a1aae3f063d12161baa4a964535e0cdb21be50067f8dca1a69b656` |
| r14-q2x10-q3x4 | no-size3 | full | 227295 / 780242 / 364 / 780606 | `197aca54f1dc3362e7cc124628ca54842437d5bf06573d168f649866ca0e6042` |
| r14-q2x10-q3x4 | root-q3x0 | full | 227295 / 780242 / 1 / 780243 | `8483315145c89d24be050391fa40899a4d7272d0a4c38d4726b1c05a90bac784` |
| r14-q2x10-q3x4 | root-q3x1 | full | 227295 / 780242 / 1 / 780243 | `1f9ebed0748cb0304980639ef5c2584c264bf48bb4afa2d6a294858159bb06da` |
| r14-q2x10-q3x4 | root-q3x2 | full | 227295 / 780242 / 1 / 780243 | `21b4cacbdf044b18a618eec9f72df71bda29dbbe699867c56d95a93bb986631e` |
| r14-q2x10-q3x4 | root-q3x3 | full | 227295 / 780242 / 1 / 780243 | `95921cb5b0418a38adef1a49f0288e4cf720e9307d4614d8e439f4817f7659ea` |
| r16-q2x16 | root-q3x0 | no-common control | 469720 / 1641761 / 1 / 1641762 | `2c386e58446c3142a6f0d93f8f92f0cd6a085951d82f7214eb9cc9adef2b6d4b` |
| r16-q2x16 | no-size3 | degree-upper control | 468352 / 1637855 / 560 / 1638415 | `4bf32491072b83a53ff254ee8359e606e3b93d1cbb974ba380ed82f2f7af59ef` |

## Positive full active-local object

The raw point and \(K\)-edge lists were validated without trusting solver
diagnostics or importing discovery code. The semantic digest independently
recomputed as:

```text
b533da6c967098ed5ec9afd4d0d4e6166c6082e4bf9de5717f48c7b6835d686a
```

Reconstructed facts:

- 16 active labels, all \(q=2\);
- 24 selected size-two points and no size-three points;
- incidence degree three at every label;
- no repeated pair owner; \(F\) has 24 edges and is cubic and triangle-free;
- 72 \(K\)-edges, degree nine at every label;
- every selected point is a \(K\)-clique;
- 48 meeting crossings checked, with zero violations;
- zero common-point/Berge violations and zero overlap-cap violations; and
- all point and \(K\)-edge decisions extend to a satisfying assignment of the
  independently rebuilt auxiliary CNF.

This validates a positive object only for the explicitly encoded active-local
relaxation. It is not \(H\), not a 99-vertex adjacency matrix, not a Conway
graph, and not a counterexample.

## Two weakened positive controls

Both controls produced the required genuine violation of the omitted premise,
while their other encoded families passed and their raw decisions extended to
the independently rebuilt control formulas.

| control | independently replayed result | semantic SHA-256 |
|---|---|---|
| omit common-point rule | 22 points, 4 triples, exact \(K\)-degree 9, 48 valid meeting crossings, exactly 11 unowned \(F\)-triangle/Berge violations | `00fa2235b5716387a2eb8e57438f078df5361925c83513d767437890285406ff` |
| weaken exact \(K\)-degree to upper bounds | 24 size-two points, 63 \(K\)-edges, degree sequence \(6,9,9,9,9,9,9,8,6,9,5,5,7,9,8,9\), with label zero deficient and all other encoded families valid | `e918fe1cad2812f5a9c708df63d95e531e1a015d406ba4607293a940170294b5` |

## Raw scan status boundary

The archived order and status split reproduced exactly:

| profile | branch | archived status |
|---|---|---|
| r16-q2x16 | no-size3 | `SAT_CANDIDATE` |
| r16-q2x16 | root-q3x0 | `TIMEOUT_UNKNOWN` |
| r15-q2x13-q3x2 | no-size3 | `BUDGET_UNKNOWN` |
| r15-q2x13-q3x2 | root-q3x0 | `TIMEOUT_UNKNOWN` |
| r15-q2x13-q3x2 | root-q3x1 | `UNSAT_UNVERIFIED` |
| r15-q2x13-q3x2 | root-q3x2 | `UNSAT_UNVERIFIED` |
| r14-q2x10-q3x4 | no-size3 | `UNSAT_UNVERIFIED` |
| r14-q2x10-q3x4 | root-q3x0 | `UNSAT_UNVERIFIED` |
| r14-q2x10-q3x4 | root-q3x1 | `UNSAT_UNVERIFIED` |
| r14-q2x10-q3x4 | root-q3x2 | `UNSAT_UNVERIFIED` |
| r14-q2x10-q3x4 | root-q3x3 | `UNSAT_UNVERIFIED` |

Thus the exact histogram is:

```text
1 SAT_CANDIDATE
7 UNSAT_UNVERIFIED
1 BUDGET_UNKNOWN
2 TIMEOUT_UNKNOWN
```

Every negative row records `proof_trace_emitted=false`,
`proof_trace_checked=false`, and
`NON_EVIDENTIARY_NO_CHECKED_PROOF_TRACE`. The verifier did not rerun these
bounded searches to infer nonexistence, because their solver exit status is
not a certificate. No negative result is promoted in this audit.

## Validator, provenance, and mutation resistance

The verifier bound the candidate report, four source files, eight computation
artifacts, all declared candidate paths, all file hashes, semantic cores, and
all branch formula hashes. The discovery-side independent-validation artifact
was hash-checked and semantically self-checked but was not used as the basis
of the fresh reconstruction.

Twenty-nine hostile mutations were rejected:

- claim, target, novelty, and scope inflation;
- encoded/unencoded premise and symmetry-boundary forgery;
- duplicate or deleted points and \(K\)-edges;
- forged diagnostics, branch normalization, formula hash, and semantic hash;
- scan claim/target/novelty inflation;
- negative status promotion even after recomputing the enclosing semantic
  digest;
- forged proof checking and negative evidentiary policy;
- candidate path and semantic-digest redirection;
- missing or duplicate branches; and
- scan formula, premise-list, negative-policy, and semantic-hash forgery.

The independent verifier passed. The supplied discovery regression suite also
passed all seven tests:

```text
Ran 7 tests in 24.929s
OK
```

Environment: Python 3.13.14, python-sat 1.9.dev7, Glucose 4.2,
Windows 11 build 26200.

## Explicitly unencoded/global premises

The CNFs do not encode:

1. inactive point sets or inactive graph vertices;
2. which disjoint active point sets represent adjacent original vertices;
3. fixed support contributed by disjoint active points;
4. equality completion of every fixed-point support sum;
5. the 693-vertex \(H\);
6. a 99-vertex adjacency matrix; or
7. the global SRG \(\lambda/\mu\) equations.

Consequently the correct publication boundary is:

```text
conditional n3=48 exclusion: UNKNOWN
conditional n3>=51:          NOT CLAIMED
srg(99,14,1,2):              UNKNOWN
novelty:                      UNKNOWN
```
