# Wave 15 global-lift obstruction at the conditional `n3=48` frontier

Verdict: **the audited Wave 14 `n3=48` residual is impossible.**  This lane
derives a complete contradiction from the full
`srg(99,14,1,2)` common-neighbor equations.  The new result is
`DERIVED`, not `VERIFIED`: under the repository protocol it requires an
independent verifier before promotion.

The key global fact is that an `srg(99,14,1,2)` has no induced vertex set
of size at most 24 and minimum internal degree at least six.  At the Wave 14
frontier, the vertices with nonempty active point form just such a set:
there are at most 24 of them, every size-three point already has six
active-triangle neighbors, and every size-two point has four
active-triangle neighbors plus two necessarily nonmeeting support
neighbors.

The explicit Wave 14 all-size-two object remains a valid countermodel to its
stated active/local/support relaxation.  What is now refuted is every lift
of that object, and in fact every lift of every size-two/size-three residual,
to a full Conway graph.

```yaml
role: proof_b
date_utc: 2026-07-23T09:48:34Z
git_commit: 37b11f4aa83ffbc55e17bd4ca0a16c05fdad18f3
claim_label: DERIVED
scope: conditional exclusion of n3=48 for a putative srg(99,14,1,2), assuming the audited Wave14 residual reduction
inputs:
  agents/2026-07-22-wave14-n3-48-proof-a.md: f0a7d7b5638415cff7d5ad4ef176542de9aa89a2b46a03347f90a2133f18999c
  verification/2026-07-22-wave14-n3-48-proof-audit.md: 44d1383548b26660dfb5d4b140c831774f6ca81e58ae140e3ceb2f80a9740802
  attempts/wave14-proof-a/all2-active-countermodel.json: 5d06ae777fb0ca4450951708bba3ffc85d1f617be1d19c2be210f43df82b8952
  attempts/wave15-global-lift/preinspection-freeze.md: 28705cbf7897cc74c2bd5a301d491bdb84830cbffcde36da4eb8a3524aec4685
method: exact active-set minimum-degree lift, SRG spectral bound, and an independent common-neighbor second-moment derivation
command: |
  python -B attempts/wave15-global-lift/build_subset_moment_certificate.py --countermodel attempts/wave14-proof-a/all2-active-countermodel.json --output attempts/wave15-global-lift/subset-moment-certificate.json
  python -B attempts/wave15-global-lift/verify_subset_moment_certificate.py attempts/wave15-global-lift/subset-moment-certificate.json
  python -B -m unittest -v attempts/wave15-global-lift/test_subset_moment.py
outputs:
  attempts/wave15-global-lift/build_subset_moment_certificate.py: 22c87bb40fb860c981b61fca66af49f896548e8083fd069007f8b2b94cfd32ba
  attempts/wave15-global-lift/verify_subset_moment_certificate.py: 0429db33fa0a61864ff8456326379fab47a09e7b8ea7234130d12b018cd041c2
  attempts/wave15-global-lift/test_subset_moment.py: a1c981666166b97d0d84d9f90c4c977e3dff9f3e5cc61b1e57711b9d9ce642f7
  attempts/wave15-global-lift/subset-moment-certificate.json: cb02ab80f92d7d2c8ec5140e3be2916354976442aa2e1869524aa728c73bd386
  arithmetic_verifier: PASS
  focused_tests: "5/5 PASS"
  conditional_n3_48_exclusion: DERIVED_PENDING_INDEPENDENT_VERIFICATION
  conway_99_target: UNKNOWN
  novelty: UNKNOWN
limitations: conditional on the independently audited Wave14 residual and its semantic bridge from active points/support to original graph vertices; this discovery lane cannot mark its own result VERIFIED; no unconditional Conway-99 or novelty conclusion is claimed
```

The recorded commit is the full repository `HEAD` observed before this lane
wrote any assigned file.  The worktree is shared and may have moved since.
This lane made no Git changes.

During root integration, the pre-commit whitespace gate removed one trailing
blank line at EOF from this report and from the preinspection freeze.  The
freeze hash declared above is the resulting normalized hash.  This was a
metadata-only normalization; no mathematical statement or status changed.

### Public-newline repair

The initial discovery baseline commit `522260a` is retained as the failed
baseline for a public-provenance mismatch.  Before repair, the Windows
worktree certificate used CRLF bytes and had SHA-256
`42d1da171274d82fa87c9489f1ed3e3334c404ea7f8f1ddce27021893831a4df`,
while `.gitattributes` normalized its public Git blob to LF with SHA-256
`cb02ab80f92d7d2c8ec5140e3be2916354976442aa2e1869524aa728c73bd386`.
The generator now opens certificate output with `newline="\n"` explicitly.
Regeneration makes the worktree bytes identical to the public LF bytes and
the output hash declared above.  This repair changes only byte-level
provenance; no mathematical statement or status changed.

## 1. Independence and inspection timing

The human lift framework was frozen at `2026-07-23T09:43:15Z` in
`attempts/wave15-global-lift/preinspection-freeze.md`, after reading only
the frozen Wave 14 proof report and audit.  No Wave 14 computation artifact
had then been opened.  The permitted Wave 14 countermodel and validator were
first inspected after that freeze and before the hash snapshot at
`2026-07-23T09:47:18Z`.  The inspection confirmed the anticipated semantic
translation but was not used to discover the subset inequality.

No Wave 15 sibling work was read.  No Wave 14 catalog census or negative
search result is used.

## 2. Global dense-subset lemma

**Lemma.**  If `G` is an `srg(99,14,1,2)` and
`X subset V(G)` has minimum induced degree at least six, then

```text
|X| >= 27.                                                (1)
```

There are two exact derivations.

### 2.1 Spectral derivation

Let `A` be the adjacency matrix.  The SRG equations give

```text
A^2 = 12 I - A + 2 J.
```

On the space perpendicular to the all-ones vector, the eigenvalues therefore
satisfy

```text
theta^2 + theta - 12 = 0,
theta in {3,-4}.
```

For `m=|X|`, decompose its characteristic vector as

```text
1_X = (m/99) 1 + y,  y perpendicular to 1,
||y||^2 = m - m^2/99.
```

If `e(X)` is the induced edge count, the largest nontrivial eigenvalue gives

```text
2e(X)
 = 1_X^T A 1_X
 <= 14m^2/99 + 3(m-m^2/99)
 = 3m + 11m^2/99.                                       (2)
```

Minimum induced degree six gives `2e(X)>=6m`.  Combining with (2),

```text
6m <= 3m + 11m^2/99,
m >= 27.
```

This proves the lemma.

### 2.2 Common-neighbor moment derivation

This second proof directly exposes the omitted-vertex obstruction.  Write

```text
d_x = |N(x) intersect X|     for x in X,
a_z = |N(z) intersect X|     for z outside X,
e = e(X).
```

Counting incidences across the cut gives

```text
sum_z a_z = 14m - 2e.                                   (3)
```

Counting common neighbors of unordered pairs in `X` uses `lambda=1` for
the `e` adjacent pairs and `mu=2` for the other pairs:

```text
sum_z C(a_z,2)
 = m(m-1) - e - sum_x C(d_x,2).                         (4)
```

Equations (3)-(4) imply

```text
sum_z a_z^2
 = 2m^2 + 12m - sum_x(d_x^2+d_x).                       (5)
```

Put `d_x=6+s_x`, `T=sum s_x`, and `U=sum s_x^2`.  Cauchy
over the `99-m` outside vertices requires the defect

```text
Phi
 = (99-m)(2m^2-30m-13T-U) - (8m-T)^2
 = -2m(m-27)(m-55)
   + (29m-1287)T - (99-m)U - T^2                       (6)
```

to be nonnegative.  For `0<m<=24`, the first term is strictly negative,
`29m-1287<=-591`, and `T,U>=0`.  Thus `Phi<0`, a
contradiction.  This independently proves the needed range of (1).

## 3. The active vertices have minimum induced degree six

Assume the audited Wave 14 residual.  Let

```text
X = {u in V(G) : S_u is nonempty}.
```

Let `x_2,x_3` count its indexed active points of sizes two and three.
Every one of the sixteen active triangle labels occurs in exactly three
points, so

```text
2x_2 + 3x_3 = 48,
|X| = x_2+x_3 <= 24.                                    (7)
```

Fix `u in X` and put `s=|S_u|`.  Every label in `S_u` is an
actual graph triangle through `u` and supplies its other two vertices as
neighbors of `u` inside `X`.  The two neighbors supplied by distinct
triangles are disjoint: otherwise one graph edge through `u` would lie in
two triangles, contrary to `lambda=1`.  Hence the active triangles alone
supply exactly `2s` distinct induced neighbors.

- If `s=3`, this already gives `d_X(u)>=6`.
- If `s=2`, the support graph `R` supplies two distinct actual graph-edge
  neighbors in `X`, because `d_R(S_u)=2`.  Neither can be one of the four
  triangle neighbors.  Indeed, such a neighbor's point would meet `S_u`
  in an active label.  After deleting both copies of that label, its labeled
  crossing has dimensions at most `1 by 2`, hence at most two edges.  It
  cannot have the `H`-degree four required of an `R`-edge.  Therefore these
  two support neighbors are new and again `d_X(u)>=4+2=6`.

Thus

```text
delta(G[X]) >= 6.                                        (8)
```

Equations (7)-(8) contradict the dense-subset lemma, which demands
`|X|>=27`.  No active-point size profile survives.  Therefore the
conditional `n3=48` residual is excluded.

## 4. Direct refutation of a full lift of the all-size-two object

The frozen Wave 14 object has 24 active original vertices and its recorded
mandatory active adjacency is exactly 6-regular, with 72 edges.  If it
lifted without extra active-active edges, the 75 outside vertices would
have active degrees `a_z` satisfying

```text
sum a_z = 24(14-6) = 192.
```

Among the `C(24,2)=276` active pairs, 72 are adjacent and 204 are
nonadjacent.  Their total common-neighbor count would be

```text
72*1 + 204*2 = 480.
```

The 24 active vertices themselves contribute

```text
24*C(6,2) = 360,
```

so the outside vertices would have to satisfy

```text
sum C(a_z,2) = 120,
sum a_z^2 = 2*120+192 = 432.                             (9)
```

But among 75 nonnegative integers with sum 192, the square sum is minimized
by 33 twos and 42 threes:

```text
sum a_z^2 >= 33*2^2 + 42*3^2 = 510,                     (10)
```

contradicting (9) by 78.  Additional active-active edges do not rescue the
object; equation (6) shows that every nonnegative degree excess makes the
Cauchy defect still more negative.

The machine-readable certificate records both the general nine possible
`(x_2,x_3)` profiles and this exact replay.  It does not relabel the Wave 14
object itself as false: that object remains `CANDIDATE` for the narrower
active relaxation, while its full-SRG lift is `REFUTED`.

## 5. Failed or weaker approaches retained

1. **Active common-neighbor caps alone fail.**  The Wave 14 object passes
   `lambda<=1`, `mu<=2` inside its recorded active subgraph.  The new
   contradiction needs the *equalities* after aggregating common neighbors
   in the omitted vertices.
2. **Minimum degree five is insufficient.**  At `m=24`, replacing the
   support-derived lower bound six by five makes the same Cauchy defect
   positive.  The two nonmeeting support neighbors at a size-two point are
   therefore essential, not cosmetic.
3. **No inactive-triangle census was needed.**  Attempting to place the
   missing triangles individually is a much larger completion problem.
   Equations (3)-(5) collapse all omitted vertices to two exact moments and
   already contradict convexity.
4. **No computational non-hit is claimed.**  The computation exhausts only
   the nine arithmetic point-size profiles and checks symbolic identities.
   The exclusion is the human inequality, not a solver exit code.

## 6. Strongest objection and status boundary

The strongest remaining objection is the semantic bridge in Section 3:
an independent verifier should reconstruct from the frozen Wave 14
definitions that point objects are distinct original vertices, that the
`2s` triangle neighbors are distinct, that `R` is a simple graph of actual
edges with degree `s`, and that an `R`-edge incident to a size-two point
cannot be a meeting edge.  The arithmetic and spectral steps are exact, but
this discovery lane cannot certify its own bridge.

Subject to that audit, the status is:

```text
Wave14 active/local/support countermodel:  still CANDIDATE in its own scope
full SRG lift of that countermodel:        REFUTED / DERIVED
all size-two/size-three n3=48 residuals:   EXCLUDED / DERIVED
conditional n3=48 exclusion:              DERIVED, awaiting verifier
Conway-99 target:                          UNKNOWN
novelty:                                   UNKNOWN
```
