# Wave 15 algebraic lane: a spectral obstruction at conditional `n3=48`

Verdict: **the audited Wave 14 `n3=48` residual is contradictory.**  In its
sole surviving profile, the original vertices lying on active triangles form
an induced subgraph on at most 24 vertices with minimum degree at least six.
The exact spectrum

```text
14^1, 3^54, (-4)^44
```

forces every vertex set whose induced average degree is at least six to have
at least 27 vertices.  This is a complete exact derivation of the conditional
exclusion, but this proof lane cannot verify itself.  Accordingly the new
claim is `DERIVED_PENDING_INDEPENDENT_AUDIT`, not `VERIFIED`.

This raises the project lower bound from `n3>=48` to `n3>=51` if the new
derivation passes independent audit, because project `n3` is divisible by
three.  It does not settle existence of the Conway graph.  Target status and
novelty remain `UNKNOWN`.

```yaml
role: proof_b
date_utc: 2026-07-23T09:50:22Z
metadata_repair_utc: 2026-07-23T10:14:03Z
git_commit: 37b11f4aa83ffbc55e17bd4ca0a16c05fdad18f3
claim_label: DERIVED
scope: >
  Exact spectral exclusion of the sole audited Wave 14 residual
  r=16, q=(2^16) under the conditional assumption project n3=48
  for a putative srg(99,14,1,2).
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  CONJECTURE.md: 7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58
  STRUCTURE.md: 743cf650eea73c132feb78bad56bbed18410f7400f2598b64222f99a87e9f732
  agents/2026-07-22-wave14-n3-48-proof-a.md: f0a7d7b5638415cff7d5ad4ef176542de9aa89a2b46a03347f90a2133f18999c
  verification/2026-07-22-wave14-n3-48-proof-audit.md: 44d1383548b26660dfb5d4b140c831774f6ca81e58ae140e3ceb2f80a9740802
  agents/2026-07-22-wave14-n3-48-computational.md: 54b532035f0ac3c09aaafd1a825600151d6ae55d3a2fcb87f911cfe37dc8b756
method: >
  Re-derive the exact SRG subset edge bound from the 3-eigenspace;
  combine it with the audited active-point incidence, support-degree,
  and two-sided crossing identities; independently check all rational
  arithmetic and retain a triangle-intersection moment lane that does
  not itself obstruct n3=48.
command: |
  $env:PYTHONDONTWRITEBYTECODE='1'
  python -B attempts\wave15-algebraic\exact_checks.py --output attempts\wave15-algebraic\exact-checks.json
outputs:
  attempts/wave15-algebraic/exact_checks.py: 8ff39bf33e2afb917a6ab52294329649d926f55bb24179561f4dd1ed5ced4b87
  attempts/wave15-algebraic/exact-checks.json: a6c9109e4fcfcdd2f5a8f5d4299ac1b4cf4037b8f1e4c468b4ecd75aba762512
  semantic_sha256: 40f5d81a71cc500c57e5f5858d11acde0afaf67d81233e68bf0794649e1a9ae8
  surviving_wave14_profile: "r=16, q=(2^16), K 9-regular"
  active_vertex_upper_bound: 24
  forced_induced_minimum_degree: 6
  spectral_minimum_order_at_average_degree_six: 27
  conditional_project_n3_48_exclusion: DERIVED_PENDING_INDEPENDENT_AUDIT
  conditional_project_n3_lower_bound: 51_PENDING_INDEPENDENT_AUDIT
  conway_99: UNKNOWN
  novelty: UNKNOWN
limitations: >
  The reduction to the r=16 all-q=2 residual and its support/crossing
  identities are imported from the independently audited Wave 14 proof.
  This lane did not rederive the full Wave 6--14 semantic framework from a
  99-by-99 adjacency matrix and cannot promote its own new argument to
  VERIFIED. The Wave 14 computational report was opened during initial
  orientation but supplies no premise and no computation result used here;
  no Wave 14 computation source or artifact and no Wave 15 sibling path was
  inspected. No Git command or floating-point computation is used.
```

The commit was read directly from `.git/HEAD` and its referenced file; no Git
operation was run.  The shared branch may move independently after this
report.  The notation `n3` throughout means the project's induced-`N3` count.
It never denotes a catalogue index; in particular no `n_45` or `n_48`
catalogue label is used.

## 1. Exact imported boundary

Assume for contradiction that a putative
`srg(99,14,1,2)` has project `n3=48`.

Only the following conclusions of the Wave 14 proof and its independent
audit are imported.

1. The two mixed active profiles are impossible.  The sole residual has 16
   active graph-triangles and

   ```text
   q(T)=2 for every active triangle T.
   ```

2. For each original graph vertex `u`, let `P=S_u` be the set of active
   triangles containing `u`.  The nonempty sets `P` form the active point
   family `mathcal P`; every such point has size at least two.  Every active
   triangle contains three original vertices, so

   ```text
   sum_(P in mathcal P) |P| = 16*3 = 48.                (1)
   ```

3. If `uv` is an actual graph edge, delete the common active label, if one
   exists, from both `S_u,S_v`.  The remaining labeled bipartite
   `L`-crossing has every row and column degree zero or two, and

   ```text
   d_H(uv)=e_L(S_u,S_v).                                (2)
   ```

   Here (2) uses the convention that a common label has first been deleted
   from both sides.

4. In this residual every actual graph edge has

   ```text
   d_H(uv) in {0,4}.                                    (3)
   ```

   The fixed-point identity is

   ```text
   sum_(v:uv in E(G)) d_H(uv)
       = 2 sum_(T in S_u) q(T)
       = 4|S_u|.                                        (4)
   ```

Define `R` on the active point objects by joining `S_u,S_v` when `uv` is an
actual graph edge with `d_H(uv)=4`.  Equations (3)--(4) give

```text
d_R(P)=|P|.                                             (5)
```

An endpoint of a positive crossing is necessarily active, so every edge
counted in (5) has both endpoints in `mathcal P`.

The cited Wave 14 audit checks the needed quantifiers: `K` and `L` are simple
complements on distinct active labels, the crossing is labeled and
two-sided, and (2) is applied only to actual graph edges.  No premise from
the Wave 14 computational lane is used.

## 2. Exact spectral subset bound

Let `A` be the adjacency matrix of a putative target graph.  The frozen
certificate identity is

```text
A^2 = 12I - A + 2J.
```

On the all-ones direction, `A` has eigenvalue 14.  On its orthogonal
complement,

```text
A^2+A-12I=0,
```

so the restricted eigenvalues are exactly 3 and -4.  The trace and dimension
equations give multiplicities 54 and 44:

```text
54+44=98,
14+54*3+44*(-4)=0.
```

Now let `X` be any set of `m` original vertices, let `x` be its zero-one
indicator, and write

```text
x = (m/99) 1 + y,    y perpendicular to 1.
```

Because the largest eigenvalue of `A` on `1`-perpendicular is 3,

```text
2e(X) = x^T A x
      = 14m^2/99 + y^T A y
     <= 14m^2/99 + 3||y||^2
      = 3m + 11m^2/99.                                 (6)
```

This is exact rational arithmetic.  No asymptotic estimate or floating-point
eigenvalue is involved.

If the induced average degree on `X` is at least six, then
`2e(X)>=6m`.  Combining with (6), and using `m>0`, gives

```text
6m <= 3m + 11m^2/99,
3 <= 11m/99,
m >= 27.                                                (7)
```

Thus:

> **Spectral subset lemma.** Every nonempty vertex set inducing average
> degree at least six in an `srg(99,14,1,2)` has at least 27 vertices.

## 3. The active original vertices have minimum degree six

Let

```text
X = {u : S_u is nonempty},    m=|X|.
```

By the no-singleton premise and (1),

```text
2m <= sum_(P in mathcal P)|P|=48,
m<=24.                                                   (8)
```

It remains to prove that every vertex of `G[X]` has degree at least six.
Fix `u in X` and put `s=|S_u|`.

Each active triangle through `u` supplies two neighbors of `u` in `X`.
These `2s` neighbors are all distinct: if an edge `uv` belonged to two of
the triangles, that edge would lie in two graph-triangles, contrary to
`lambda=1`.  Therefore the active triangle edges alone give

```text
d_(G[X])(u) >= 2s.                                      (9)
```

If `s>=3`, (9) already gives degree at least six.

Suppose instead that `s=2`.  Equation (5) supplies exactly two incident
`R`-edges.  Neither can be one of the four active triangle edges at `u`.
Indeed, if `uv` is such a triangle edge, `S_u` and `S_v` share its unique
active graph-triangle.  Delete that common label as required in (2).  The
`S_u` side now contains one label.  The two-sided zero-or-two law makes its
sole row have degree at most two, hence

```text
d_H(uv)=e_L(S_u,S_v)<=2.
```

But an `R`-edge has `d_H(uv)=4`.  This contradiction shows that both
`R`-neighbors of `u` are additional to its four active-triangle neighbors.
Consequently

```text
d_(G[X])(u) >= 4+2=6.                                   (10)
```

Equations (9)--(10) prove

```text
delta(G[X])>=6,
e(X)>=3m.                                                (11)
```

The spectral subset lemma (7) now gives `m>=27`, while incidence (8) gives
`m<=24`.  This is the contradiction.

Therefore the sole audited Wave 14 residual cannot occur.  Together with
the audited Wave 14 exclusions of the mixed profiles, this gives the scoped
conclusion

```text
project n3=48: excluded / DERIVED_PENDING_INDEPENDENT_AUDIT.
```

## 4. Dependency and overlap audit

The short proof uses the Wave 14 residual at exactly four places.

| Needed fact | Use |
|---|---|
| 16 active triangles, every active `q=2` | total incidence 48 and right side of (4) |
| no active singleton point | `m<=24` |
| residual `d_H in {0,4}` and fixed-point identity | `d_R(P)=|P|` |
| actual-edge, delete-overlap, two-sided crossing law | a size-two point's `R`-edges cannot be triangle edges |

No assertion is made about an arbitrary graph nonedge.  No automorphism,
transitivity, connectedness, active-completion search, or negative solver
return is used.

The possible overlap between `R` and the active triangle edges is handled
vertex by vertex:

- at a point of size at least three, the triangle edges alone give degree
  at least six, so no disjointness claim is needed;
- at a point of size two, the crossing law proves complete disjointness of
  its two incident `R`-edges from its four triangle edges.

Thus there is no global double-counting assumption hidden in (11).

The all-size-two Wave 14 active-local countermodel does not refute the new
lemma.  It deliberately omitted the global SRG spectrum.  In that subcase
`m=24` and the preceding proof forces at least 72 induced edges, whereas
(6) permits at most exactly 68.

## 5. Independent exact arithmetic replay

`attempts/wave15-algebraic/exact_checks.py` uses only the Python standard
library and exact `Fraction` arithmetic.  It checks:

1. the target restricted eigenvalues and multiplicities;
2. the subset edge bound;
3. every arithmetically possible pair

   ```text
   2*x2+3*x3=48,  x2,x3>=0,
   ```

   although the human proof needs only `m<=24`; and
4. the independent triangle-intersection moment lane in the next section.

For `x3=0,2,...,16`, it obtains `m=24,23,...,16`.  In every row the exact
forced lower bound `3m` exceeds the spectral upper bound.  At the weakest
row `m=24`, the gap is already four edges:

```text
forced e(X)>=72,
spectral e(X)<=68.
```

The retained semantic digest is

```text
40f5d81a71cc500c57e5f5858d11acde0afaf67d81233e68bf0794649e1a9ae8.
```

The script is an arithmetic replay, not a formal proof checker for the
imported semantic bridge.

### Audit-driven metadata repair

At `2026-07-23T10:14:03Z`, an independent audit noted that the JSON key
`sum_i_a_i` was ambiguous: its value 216 means the weighted sum
`sum_i i*a_i`, not the unweighted sum `sum_i a_i`.  The checker variable,
assertions, and JSON fields were renamed to

```text
weighted_sum_i_a_i
weighted_sum_i_squared_a_i
```

and the exact output was regenerated.  The former script, JSON, and semantic
hashes

```text
ffd34b7ce806f9042f1ee33b2a6f4514f22e9a33a782bf7e38c7ccd115293701
2b7e737ed496b997e106600867410ffbadf5ff5ac56a3afdc46ddedb26d56a45
48841fbd08ba74f4bbe1dcdc2347e0fcdd2a80d72ad76ba97fa7f2b742d63cec
```

were replaced by the hashes recorded in the run schema above.  This repair
changes metadata names and hashes only; every integer value, equation,
mathematical conclusion, and status boundary is unchanged.

## 6. Retained algebraic lane that does not obstruct `n3=48`

For completeness, an association-scheme-style triangle calculation was
reconstructed before the vertex-subset obstruction was found.  It gives
useful exact identities but no contradiction by itself.

Let `C` be the `99 x 231` vertex-by-graph-triangle incidence matrix and let
`Q` be the graph on the 231 graph-triangles, adjacent when they meet in an
original vertex.  Every vertex lies in seven graph-triangles and every graph
edge lies in its unique graph-triangle, so

```text
CC^T=7I+A,
C^TC=3I+Q.
```

The nonzero eigenvalues of `C^TC` are those of `CC^T`.  Hence

```text
spec(Q)=18^1, 7^54, 0^44, (-3)^132.                     (12)
```

It follows exactly that

```text
Q^3-4Q^2-21Q=18J.                                       (13)
```

For a fixed triangle `T`, let `a_i(T)` count disjoint triangles joined to
`T` by exactly `i` graph edges.  The cross edges form a matching, so
`0<=i<=3`.  A disjoint triangle is a common `Q`-neighbor precisely when it
contains the unique graph-triangle on one such cross edge.  Two meeting
graph-triangles have exactly five common `Q`-neighbors, namely the other
five graph-triangles through their common original vertex.

The row sum of `Q^2` and the diagonal of `Q^4`, computed from (13), give

```text
sum_i i a_i(T)=216,
sum_i i^2 a_i(T)=288,
a_2(T)+3a_3(T)=36.                                      (14)
```

At the audited all-`q=2` `n3=48` profile, (14) gives

```text
active triangle:   (a_2,a_3)=(6,10),
inactive triangle: (a_2,a_3)=(0,12).
```

The resulting global numbers of unordered disjoint triangle pairs with
zero, one, two, and three cross edges are respectively

```text
(2326, 20742, 48, 1370).                                (15)
```

All values in (15) are nonnegative integers and satisfy the first two
spectral moments.  Thus these triangle-level moments do **not** exclude the
frontier.  Principal interlacing of `Q` is also too weak at this order: its
allowed eigenvalue interval already contains the spectra of the relevant
small intersection graphs.  These failed equations are retained to prevent
repeating a purely triangle-moment search without additional constraints.

## 7. Failure log and strongest self-objection

### Retained failed routes

1. **No obstruction from the first two triangle-intersection moments.**
   Equation (15) is an exact nonnegative solution at project `n3=48`.
2. **No useful contradiction from triangle-graph interlacing alone.**
   The four eigenvalues in (12) give bounds too broad for the 16 active
   triangle labels.
3. **The active-local countermodel remains valid in its stated scope.**
   The new contradiction uses the global target spectrum, which that
   relaxation did not encode.  No archived countermodel file was inspected
   in this lane.

### Strongest self-objection

The only vulnerable bridge is the import from the audited Wave 14 residual:
in particular, (3)--(5) and the exact qualification of (2) for actual graph
edges.  If `R` included nonedges, if a positive crossing could end at an
inactive point, or if the common active label were not deleted on both
sides, the minimum-degree conclusion would not follow.  The Wave 14 proof
and audit explicitly state the needed versions, and Section 3 uses no
stronger formulation.  An independent verifier should nevertheless
reconstruct those four imported facts before promoting the new result.

## 8. Status boundary

```text
Wave 14 mixed-profile exclusions:          imported audited DERIVED
Wave 14 sole residual:                     r=16, q=(2^16)
active original-vertex count:              at most 24
forced active induced minimum degree:      at least 6
spectral order required at average deg 6:  at least 27
conditional project n3=48 exclusion:       DERIVED_PENDING_INDEPENDENT_AUDIT
conditional project n3>=51:                DERIVED_PENDING_INDEPENDENT_AUDIT
Conway srg(99,14,1,2):                     UNKNOWN
novelty:                                   UNKNOWN
```

No target resolution or novelty claim is made.
