# Failed and superseded routes

## One-border and two-border ranks

The first calculation adjoined only one vertex of the third fibre. For edge
type `2+2+2`, all 17,280 labelled `(pulled Y matching, X/Y neighbour
signature)` cases had 28-point rank 21. This improved the local rank 19 but
did not use the other eleven third-fibre vertices.

A second calculation adjoined two vertices. For canonical type `2+2+2`, the
144 signature positions form a rank-22 compatibility graph with 96 edges and
maximum clique four, forcing some pair among twelve signatures to have rank
23. This was correct but weaker than the final kernel-projection argument.

Both routes are superseded by the exact all-twelve-signature census, which
proves the candidate floor 25 uniformly.

## Direct enumeration of the fully specified 39-block

After normalizing `X-Z`, the remaining labelled data consists of an arbitrary
`Y-Z` permutation and an arbitrary perfect matching inside `Z`:

```text
12! * 10,395
```

possibilities for each edge type before quotienting. No complete orbit
quotient of this domain was finished. The deterministic 512-sample-per-type
scout found only ranks 34, 35, and 36. The separately aligned exact
relaxation has rank 31, demonstrating that the random minima were not
extremal. Absence of a lower sample is not evidence. The universal proof
deliberately treats `W` as arbitrary and therefore remains complete despite
this unfinished strengthening.

## Full rooted SAT with fourteen type-222 selectors

An exploratory native-cardinality formula imposed one of the 120 type-222
matchings at each of the fourteen root-neighbour coordinates in the complete
rooted SRG model. The resulting formula had 291,018 variables, 295,933
ordinary clauses, and 5,866 native AtMost constraints. MiniCard reached
100,002 conflicts without a terminal answer.

This bounded run is non-evidentiary, has no retained proof, and is not part of
the rank-25 theorem.

## Incorrectly identifying two fibre matchings

In a separate attempted `r7=22` quotient route, one must exclude the standard
`X` matching for `X` nonedge pairs and the actual pulled-back `Y` matching for
`Y` nonedge pairs. Replacing the latter by the `X` matching is invalid.
With the correction, all 32 syndrome three-spaces in that relaxation support
both the twelve-edge `Z`-neighbour matching and the full sixty-pair matching.
That relaxation is a positive control, not a contradiction.

## Scope wall

The new characteristic-seven floor is a necessary matrix consequence. It does
not force a triangular prism, exclude the prism-free endpoint, improve
`n3<=4158`, or establish literature novelty.
