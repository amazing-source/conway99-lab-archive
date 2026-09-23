# Failed routes and retained boundaries

## Treating nonpercolating nonedges as prism counts

The exact identities are

```text
R=18H
and
6H<=P.
```

Therefore `R<=3P`; equality requires every induced prism to extend to a
`K3 square K3` closure.  No such extension theorem was found or proved.
A triangular prism may have all six central nonedges percolating.  Replacing
the inequality by `R=3P` would silently assume the missing result.

## Treating all non-N3 nonedges as nonpercolating

An arbitrary nonedge has zero, one, or two central `N3` channels.  Having
zero channels means both early opposite-tip edges are present, but it does
not force the ninth rook-graph vertex or stop later infection.  The exact
census has six locally admissible next-wave profiles in this two-tip-edge
case; only one is the single four-tip neighbor that completes the proper
nine-vertex closure.

Thus

```text
nonpercolating => zero central N3 channels
```

but the converse is not proved.

## Pair-deficit global sum

The endpoint next-wave CSP gives 35 profiles and the invariant pair-cover
sum 16 per nonedge.  Summing over all 4,158 nonedges fixes 66,528 pair-cover
incidences, but the number of next-wave vertices varies from 8 to 16 because
one vertex may cover one, three, or six deficits.

The required global counts of size-three and size-four masks are not fixed by
the strongly regular parameters or the current six-vertex identities.  The
resulting bounds

```text
33264 <= total seeded next-wave incidences <= 66528
```

do not contradict any known count.

## Local profile feasibility is not global realizability

Each of the 35 endpoint profiles exactly fills current pair deficits and
respects visible `lambda/mu` caps.  The census does not assign edges among
next-wave vertices, their remaining degrees, their common neighbors outside
the current set, or compatibility across different nonedge seeds.

The profile list is therefore a smaller exact CSP boundary, not 35 graph
constructions and not an endpoint exclusion.

## Source scope

The primary paper supplies the general closure lemma and states Theorem 4.19.
The package independently rederives the target parameter census and incidence
arithmetic, but discovery cannot independently verify its own derivation.
Novelty and the existence of the target graph remain `UNKNOWN`.
