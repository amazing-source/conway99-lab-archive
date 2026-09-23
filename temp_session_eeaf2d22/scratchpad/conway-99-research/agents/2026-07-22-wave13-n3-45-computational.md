# Wave 13 computational lane: the conditional \(n_3=45\) frontier

```yaml
role: construction
date_utc: 2026-07-23T08:03:24Z
git_commit: c471801a7adf6852a208b5d5553bcc76a3372d6a
claim_label: CANDIDATE
scope: >
  Exact active-q and K-degree profiles at conditional n3=45; finite local
  point-flower and crossing reductions; an exhaustive 17-branch SAT scout of
  the surviving active-local order-fifteen model; and a machine-readable
  weakened survivor obtained by deleting the common-point premise. This is
  not a completed 99-vertex search.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/2026-07-22-wave12-integration-audit.md: 90021fc6f29cfc4ac0d3df07769ce43b4f270a99a13784ff7491711d15352e70
  verification/n3-42-equality/verify_reduction.py: 8aeec3c8f6f53eb14a8a5da49651c0c2b58cf2e118ecd51157c87af13ee6bf72
  code/wave13_n3_45_profiles.py: 7685a370166c0caa41460d5cbfab3b3a51d28da52441db63f5befeb396e4cf7c
  code/wave13_n3_45_active_sat.py: ad4b0c41e7aeebb3f9b9c5d1253c317e59b96d69f3d782f2ea83de655bf052e7
  code/wave13_n3_45_test.py: 0d2d4d868618ce714599c014ab0f8ac247c2f240a521848433fe94298bfbd3d3
method: >
  Independent integer partitioning, standard-library flower and small-graph
  enumeration, exact CNF encoding with justified active-label normalization,
  bounded CaDiCaL 1.9.5 discovery runs, exact CNF-stream hashing, positive
  weakened-model validation, and hostile artifact mutation.
command: |
  python code/wave13_n3_45_profiles.py --output attempts/wave13-computation/n3-45-local-census.json
  python code/wave13_n3_45_active_sat.py --scan --solver cadical195 --conflict-budget 400000 --scan-output attempts/wave13-computation/n3-45-active-local-sat-scan.json
  python code/wave13_n3_45_active_sat.py --size3 5 --root-mode 111 --variant no_common_point --solver cadical195 --conflict-budget 300000 --candidate attempts/wave13-computation/n3-45-no-common-point-m5-111.json
  python code/wave13_n3_45_active_sat.py --validate attempts/wave13-computation/n3-45-no-common-point-m5-111.json
  python code/wave13_n3_45_test.py -v
outputs:
  attempts/wave13-computation/n3-45-local-census.json: f0fcbd3457e5b39f56e68492d2a29ae2f45a5deeff99cc30803178d3f3ee2019
  attempts/wave13-computation/n3-45-active-local-sat-scan.json: d526bc59b4000a59ff8cc607be89744072a8845763883c8f60af65075bfdd933
  attempts/wave13-computation/n3-45-no-common-point-m5-111.json: e32486506a5da0607c0deddaced42ff77f059b39abc3ba29923cd5d056762bb0
  raw_active_profiles: 9
  profiles_after_no_singleton_filter: 3
  profiles_after_degree_three_obstruction: 2
  mixed_order14_profile_survivors: 0
  order15_local_root_modes: [111, 122, 222, 223]
  order15_integer_incidence_signatures: 59
  full_active_local_sat_branches: 17
  full_active_local_solver_survivors: 0
  weakened_no_common_point_survivors_archived: 1
  target_result: UNKNOWN
limitations: >
  All mathematics is conditional on the frozen Wave 6--12 active-triangle
  premises. The mixed-profile reduction and the SAT encoding were produced
  by this construction lane and have not been independently verified.
  CaDiCaL returned UNSAT on all seventeen full active-local branches, but no
  DRAT/FRAT proof was emitted or checked, so those returns are not evidence
  of nonexistence and do not justify excluding n3=45 or claiming n3>=48.
  The SAT model omits disjoint-point fixed support, inactive vertices, and a
  99-vertex adjacency matrix. No completed-graph automorphism is assumed.
```

## Status boundary

There are two qualitatively different outputs.

1. The standard-library program gives a finite arithmetic/local reduction.
   Its new mixed-profile and order-fifteen conclusions remain `CANDIDATE`
   until a verifier reconstructs them independently.
2. The SAT scout found no survivor in a complete cover of the encoded
   active-local branches. Those seventeen answers are deliberately recorded
   as `UNSAT_UNVERIFIED`, not as a theorem or certificate.

Accordingly this lane does **not** exclude \(n_3=45\), does not establish
\(n_3\ge 48\), and does not change the project target from `UNKNOWN`.

## Nine exact active profiles

At \(n_3=45\), the frozen identities give

```text
sum_T q(T)=30,  q(T)>=2,  3q(T)<=r-1.
```

Exact partitioning produces all nine rows below.

| \(r\) | \(q\)-profile | \(K\)-degree profile | first filter |
|---:|---|---|---|
| 15 | \(2^{15}\) | \(8^{15}\) | survives |
| 14 | \(2^{12}3^2\) | \(7^{12}4^2\) | survives |
| 14 | \(2^{13}4\) | \(7^{13}1\) | singleton deficit |
| 13 | \(2^9 3^4\) | \(6^9 3^4\) | degree-three obstruction |
| 13 | \(2^{11}4^2\) | \(6^{11}0^2\) | singleton deficit |
| 13 | \(2^{10}3^2 4\) | \(6^{10}3^2 0\) | singleton deficit |
| 12 | \(2^6 3^6\) | \(5^6 2^6\) | singleton deficit |
| 11 | \(2^3 3^8\) | \(4^3 1^8\) | singleton deficit |
| 10 | \(3^{10}\) | \(0^{10}\) | singleton deficit |

Three non-singleton point cliques through a label require three distinct
incident \(K\)-edges. This removes the six degree-deficient rows. The frozen
degree-three lemma removes the \(r=13\) row: at a degree-three label, its three
size-two point sets force three further point sets that form a forbidden
Berge triangle. The two frontiers displayed as “survives” are the only ones
examined below.

## Finite reduction of the mixed order-fourteen profile

The expansion inequality \(2s\le 14-s\) bounds point size by four. For a
size-four point there are eight pairwise-disjoint external petal parts in ten
available labels. The exact \(3^8=6561\) petal-word census has 45
capacity-feasible words. Every one forces a root \(K\)-degree above seven, so
no size-four point survives.

All points now have size two or three. Let \(t_i\) be the number of
size-three points through label \(i\), let \(F\) be the union of point-clique
edges, and let \(U=K-E(F)\). For a \(q=2\) label,

```text
d_F(i)=3+t_i,  d_U(i)=4-t_i.
```

For a \(q=3\) label the corresponding \(U\)-capacity is \(1-t_i\). The exact
rooted crossing enumeration uses:

- every singleton-side crossing is empty in \(L\);
- a 2-by-2 meeting crossing is empty or full in \(L\);
- forced \(K\)-crossing edges cannot lie in \(F\), by the common-point rule;
  and
- full 2-by-2 \(L\)-crossings contribute four to the fixed-point sum.

It finds no size-three point containing a \(q=3\) label. A size-three point
on three \(q=2\) labels has only the mode

```text
(t_i,t_j,t_k)=(2,2,2),
```

with all three other size-three co-points contributing four. Hence every
label used by a size-three point has \(t=2\).

If such points exist, form their intersection graph \(R\). It is simple,
cubic, and triangle-free. Write \(e=|E(R)|\). Each edge label \(i\) has a
third point \(\{i,a_i\}\). Its four forced \(U\)-neighbors show that \(a_i\)
is a \(q=2,t=0\) label and that

```text
N_U(a_i)=N_{L(R)}(i).
```

Only twelve labels have \(q=2\). The \(e\) distinct third points consume
incidences among \(3(12-e)\) available \(q=2,t=0\) incidences, so
\(e\le 9\). A nonempty cubic triangle-free \(R\) can therefore have order
four or six. The exact small census has no order-four type and ten labeled
order-six copies, all \(K_{3,3}\). The line graph of \(K_{3,3}\) has no open
twins, so \(i\mapsto a_i\) is injective. It would inject nine edge labels
into only \(12-9=3\) available \(q=2,t=0\) labels, a contradiction.

If all points instead have size two, their point graph is cubic and
triangle-free. At either \(q=3\) label, the three point-mates and at least two
distinct distance-two labels are forced \(K\)-neighbors. The executable
lower bound is

```text
six length-two paths / at most three paths per endpoint
    => at least two distance-two endpoints
    => d_K >= 3+2 = 5 > 4.
```

Thus the mixed order-fourteen profile has no survivor in this construction
lane's finite reduction. This is a promising derived contradiction, but it
is not promoted here.

## Exact order-fifteen local frontier

The all-\(q=2\) profile has \(K\) 8-regular and fixed-point total \(4|P|\)
for every point \(P\). Expansion initially allows point size at most five.

The flower census gives:

| root size | total words | capacity-feasible | \(K\)-degree survivors |
|---:|---:|---:|---:|
| 5 | \(4^{10}=1,048,576\) | 1 | 0 |
| 4 | \(3^8=6,561\) | 157 | 0 |

For size five the sole capacity word has ten singleton petals and forces
root degree fourteen. For size four, singleton endpoints are adjacent to
every root label, while every larger petal contributes its external labels
at its own occurrence; all 157 capacity-feasible words exceed degree eight
somewhere. Hence every point has size two or three.

Put

```text
t_i = number of size-three points through i,
d_F(i)=3+t_i,
d_U(i)=5-t_i.
```

For a size-three root \(P=\{i,j,k\}\), let \(z_i\) count its other
size-three petals whose 2-by-2 crossing with \(P\) is empty in \(L\). Exact
\(U\)-capacity and fixed-point enumeration leaves only:

| sorted \(t\)-mode | sorted \((t,z)\)-mode | forced overlap contribution | remaining support |
|---|---|---:|---:|
| 111 | \(1{:}0,1{:}0,1{:}0\) | 0 | 12 |
| 122 | \(1{:}0,2{:}0,2{:}0\) | 8 | 4 |
| 222 | \(2{:}0,2{:}0,2{:}0\) | 12 | 0 |
| 223 | \(2{:}0,2{:}0,3{:}1\) | 12 | 0 |

Let \(m\) be the number of size-three points. Since

```text
2 x_2 + 3m = 45,
```

\(m\) is odd. Summing the four local types by label degree gives 59 exact
integer signatures:

| \(m\) | signature count |
|---:|---:|
| 1 | 2 |
| 3 | 7 |
| 5 | 16 |
| 7 | 21 |
| 9 | 12 |
| 11 | 1 |
| 13, 15 | 0 |

These signatures are arithmetic possibilities, not asserted hypergraphs.

## The 17-branch active-local SAT scout

For each possible \(m\), the CNF has variables for all 560 candidate point
sets of sizes two and three, all 105 \(K\)-edges, all 105 \(F\)-edges, and,
when needed, reified full-\(L\) overlaps. It enforces:

1. exactly three selected points through every active label;
2. exactly \(m\) selected size-three points;
3. point-hypergraph linearity and \(F\) as the exact union of point-clique
   edges;
4. every selected point is a clique in \(K\);
5. every primal \(F\)-triangle is owned by its selected size-three point,
   which is the common-point/Berge-triangle rule under linearity;
6. the exact zero-or-two meeting-crossing rule;
7. at most three full-\(L\) overlaps at a size-three point; and
8. exact \(K\)-degree eight.

Odd incidence guarantees at least one size-three point. The full
\(S_{15}\) action on active labels names it \(\{0,1,2\}\). Its setwise
stabilizer gives one representative for each of modes 111, 122, 222, and
223. This is label normalization of the active auxiliary object; it does not
assume any automorphism of a completed graph. Minimum co-point counts and the
sole \(m=11\) signature reduce the cover to seventeen branches:

| \(m\) | rooted modes | branches | conflict range | summed solver time |
|---:|---|---:|---:|---:|
| 1 | 111 | 1 | 126 | 0.000 s |
| 3 | 111, 122 | 2 | 311--249,042 | 11.563 s |
| 5 | 111, 122, 222, 223 | 4 | 15--61,121 | 9.813 s |
| 7 | 111, 122, 222, 223 | 4 | 178--44,228 | 12.516 s |
| 9 | 111, 122, 222, 223 | 4 | 178--46,327 | 14.469 s |
| 11 | 222, 223 | 2 | 178--17,179 | 3.344 s |

All branches terminated below the 400,000-conflict bound with solver return
UNSAT. The exact formulas range from 13,209 variables and 32,224 clauses to
333,743 variables and 1,152,802 clauses. The archive records seventeen
distinct SHA-256 hashes of deterministic DIMACS clause streams; its stable
semantic digest is

```text
6325eb4958a850289baede0ba8663317e3a1189bd508c09749a6960e0cefbe49.
```

The complete wall run took 97.7 seconds on Python 3.13.14 under
Windows 11 build 26200. The summed internal CaDiCaL time was 51.703 seconds.

These numbers make the lane reproducible, not evidentiary. No proof trace was
emitted, the formulas have not been independently reconstructed, and a
solver exit status is not a certificate. The only correct record is

```text
17/17 solver returns: UNSAT_UNVERIFIED
n3=45 exclusion:       NOT CLAIMED
target:                 UNKNOWN
```

## Positive weakened survivor and failed detours

Deleting the common-point clauses in branch \(m=5\), root mode 111, produces
a positive model. The archived object has:

```text
15 active labels;
15 size-two points and 5 size-three points;
point-incidence degree exactly 3;
a linear point hypergraph;
an 8-regular K;
all selected points K-cliques;
zero meeting-crossing violations;
zero size-three fixed-point-cap violations;
18 forbidden common-point/Berge triangles.
```

The validator recomputes all of these values and binds semantic SHA-256

```text
2492601fb4dbb6dd642d73e34404f446ff8d0f1cee6edfaec7babbba39424e03.
```

Removing one recorded \(K\)-edge is rejected by the mutation test. This
positive failure model shows that the scout can produce assignments and that
the common-point premise performs real work; it is not a partial Conway
graph.

Two further restricted tests removed the global overlap cap while retaining
the four root modes already derived using the full local premises. They
returned `UNSAT_UNVERIFIED` at:

```text
m=5, root 111:  51,604 conflicts, CNF SHA-256
  3de5838d2a1cd1e2b668cef7305a5aebd45a35c9463f4345873254a46813da2f
m=9, root 111:  49,504 conflicts, CNF SHA-256
  f5894ef665f3672d1cbb4c3e63504f3e196c16ad0e02cf6b6a79cc47a75f83e2
```

Those are not a complete weakened branch cover and carry no mathematical
weight. A selective test replacing exact 8-regularity by degree at most eight
also returned `UNSAT_UNVERIFIED`; it was not extended to a cover. These
detours are retained to prevent their accidental reinterpretation as proofs.

## Recommended verifier handoff

The next rigorous step is not another broad solver run. It is one of:

- independently reconstruct the four rooted modes and the seventeen-branch
  cover, looking first for a missing mode or an unjustified normalization;
- independently encode the same active-local problem and compare all
  seventeen formula hashes or semantic clause families; or
- emit proof-producing CNFs and check DRAT/FRAT traces with a separate
  checker, while retaining the positive no-common-point mutation.

Until one of those succeeds, the SAT result stays `CANDIDATE` and the target
stays `UNKNOWN`.
