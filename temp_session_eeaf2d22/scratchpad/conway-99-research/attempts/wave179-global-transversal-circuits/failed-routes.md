# Boundary and failed continuations

## Average coverage is not all-symbol locality

The 2,079 projective circuits contribute at least 8,316 support incidences,
but this is an average statement.  It does not prove that every one of the
231 coordinates lies in a short circuit, much less in several circuits
with pairwise-disjoint recovery sets.

## The ordinary LRC bound is slack even under a stronger assumption

If one granted all-symbol locality seven for the primal `[231,11]` code,
the standard Singleton-type locality bound would only give distance at
most 220.  The 99 distinguished primal words already have weight 198, so
this supplies no contradiction.

## Circuit elimination still loses localization

Eliminating one shared coordinate from two circuits of size at most nine
can leave support as large as 16.  The exact-transversal theorem controls
reuse of an entire support, not coefficient-compatible overlaps between
different supports.

## A three-realization star is not excluded

The multiplicity-three case has realizing pairs

```text
{x,y_0}, {x,y_1}, {x,y_2}
```

and a support triangle `{y_0,y_1,y_2}` avoiding `x`.  The parameter
`lambda=1` shows that at most one of the three pairs can be a graph edge,
but it does not exclude the two or three nonedge cases.  Therefore the
denominator three in the global count cannot currently be replaced by two.

## Enumerator feasibility is still open

No checked complete-weight or MacWilliams argument currently supplies an
upper bound below 4,158 for `B_4+...+B_9`.  Treating the new lower bound as
an endpoint contradiction would be status inflation.
