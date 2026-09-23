# Wave 16 structural audit: artifact-preinspection freeze

Date: 2026-07-23 UTC

This freeze was written after reading the submitted human report
`agents/2026-07-23-wave16-n3-51-structural.md`, because that report is the
object assigned for audit, but before opening any submitted file under
`attempts/wave16-n3-51-structural/`.  The accepted premises below were
checked against the named committed independent audits, rather than accepted
from the Wave 16 report.  No Wave 16 computational-lane report, source, or
artifact was opened.

## Accepted inherited premises

Assume a putative `srg(99,14,1,2)` and use the project's induced-`N3`
notation.

1. The triangle-side graph `L` is simple.  For every graph-triangle `T`,
   `d_L(T)=3q(T)`, with `q(T)=0` or `q(T)>=2`, and
   `sum_T q(T)=2n3/3`.
2. Active triangles are those with positive `q`.  If there are `r` active
   labels, every `L`-neighbor of an active label is active.  Thus, on the
   active labels, `K=complement(L)` is simple and
   `d_K(T)=r-1-3q(T)`.
3. For each original vertex `u`,
   `S_u={active graph-triangles containing u}`.  Every nonempty `S_u` has
   size at least two, is a clique of `K`, and is indexed by the original
   vertex `u`; no quotient by equal set values is taken.
4. The indexed family is linear.  Every active label occurs in exactly three
   indexed points, one for each original vertex of that graph-triangle.
   Three indexed points cannot meet pairwise at three distinct active labels.
5. If `uv` is an actual graph edge, remove both copies of the possible
   common active label from the labeled `L`-crossing between `S_u` and
   `S_v`.  Every remaining row and column has degree zero or two, and

   ```text
   d_H(uv)=e_L(S_u,S_v),
   sum_{v:uv in E(G)} d_H(uv)=2 sum_{T in S_u}q(T).
   ```

   These statements apply to actual graph edges, not arbitrary point pairs.
6. The target adjacency matrix satisfies

   ```text
   A^2=12I-A+2J.
   ```

   Hence its restricted eigenvalues are `3` and `-4`.  For an original
   vertex subset `X` of size `m`,

   ```text
   2e(G[X]) <= 3m+11m^2/99 = 3m+m^2/9.
   ```

7. The prior audited result is the conditional necessary bound `n3>=51`.
   Also `3|n3`, and the exact target-specialized identity is
   `induced_C6_count=209286+n3`.

## Independent predictions before submitted-artifact inspection

At `n3=51`, the profile equations are

```text
sum q=34, q>=2, 3q<=r-1.
```

An independent generator should find sixteen nondecreasing raw profiles.
Three non-singleton point cliques through a label give `d_K>=3`.  Equality
`d_K=3` should be impossible: if
`N_K(x)={a,b,c}`, the three points through `x` are
`{x,a},{x,b},{x,c}`.  Applying the actual-edge, overlap-deleted crossing
rule to `{x,a}` and each of the other two points through `a` forces those
points to be `{a,b}` and `{a,c}`.  Then
`{x,a},{x,b},{a,b}` already meet pairwise at the three distinct labels
`a,x,b`, a contradiction.  Therefore the numerical filter is `d_K>=4`.

The predicted surviving profiles are

```text
r=14: q=2^8 3^6
r=15: q=2^11 3^4
r=16: q=2^14 3^2
r=17: q=2^17.
```

For

```text
X={u:S_u is nonempty},
```

the indexing and incidence identity give

```text
sum_{u in X}|S_u|=3r,
|X|<=floor(3r/2)<=25.
```

For a size-two point `P=S_u`, the overlap-deleted crossing at every actual
edge `uv` should be:

- empty when `S_v` is empty;
- empty when `P` and `S_v` meet (the `P` side has one remaining row); or
- empty or exactly `K_(2,2)` when they are disjoint.

Thus every term incident with this fixed size-two endpoint is `0` or `4`.
The fixed sums for endpoint label types `(2,2)`, `(2,3)`, `(3,3)` are
respectively `8,10,12`.  The mixed type should be impossible; the other two
types should have exactly two and three distinct positive actual graph
neighbors.  Positivity should force the neighbor point to be active and
disjoint from `P`, so these vertices are additional to the four
active-triangle neighbors of `u`.

For `|S_u|>=3`, the active triangles through `u` alone should supply
`2|S_u|>=6` distinct vertices of `X`.  Therefore the expected conclusion is
`delta(G[X])>=6` without a global `H`-degree restriction, without defining a
support graph `R`, and without an upper bound on point sizes.

Finally, exact spectral arithmetic should give

```text
6m <= 2e(G[X]) <= 3m+m^2/9
```

and hence `m>=27`, contradicting `m<=25`.  If every bridge above survives
adversarial checking, the scoped conditional exclusion `n3!=51` is sound;
combined with the inherited lower bound and divisibility it yields the
conditional necessary bounds `n3>=54` and
`induced_C6_count>=209340`.  The Conway-99 target and novelty remain
`UNKNOWN`.

## Hostile cases to require

The independent checker/tests must reject or expose:

1. keeping a shared active label instead of deleting it;
2. enforcing row degrees but not column degrees;
3. treating multiple positive incidences as one graph neighbor;
4. allowing a positive crossing to an empty or meeting point;
5. counting active-triangle neighbors twice across two labels;
6. assuming `d_H in {0,4}` away from a fixed size-two endpoint;
7. assuming `d_R(P)=|P|`;
8. assuming all point sizes are at most three;
9. allowing `d_K=3`; and
10. replacing the exact restricted eigenvalue `3` by a weaker value.
