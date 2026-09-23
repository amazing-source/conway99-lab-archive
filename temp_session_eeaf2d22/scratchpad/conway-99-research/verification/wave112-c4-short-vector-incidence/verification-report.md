# Wave 112 independent verification report

Date UTC: 2026-07-28.

Verdict: **VERIFIED**, conditional on the frozen verified Wave 71/74/78/86
support and rank-28 inputs.  No discovery code was imported.

## Independent arithmetic

The target has `99*14/2=693` edges and `C(99,2)-693=4158` nonedges.  Each
nonedge has two common neighbours.  They cannot be adjacent, since they
would then have both endpoints as common neighbours, against `lambda=1`.
Every nonedge is therefore a diagonal of one induced four-cycle, and each
cycle has two diagonals:

```text
4158 / 2 = 2079 induced C4s.
```

For an `h=0` sign side of size `s`, the independent checker exhausts all
histograms of `C(s,2)` codegrees in `{0,1,2}` with sum
`s*C(4,2)=6s`.  The minimum number of codegree-two pairs is respectively
`21,20,18` for `s=7,8,9`.  Each such pair gives exactly one alternating
cycle, counted once by the chosen sign-side diagonal.

For norm-18 `h=1`, the opposite-side degree multiset is `5,5,4^7`, so the
pair-intersection sum is

```text
2*C(5,2) + 7*C(4,2) = 62.
```

The one adjacent same-sign pair has capacity one and is not an alternating
cycle.  Exhausting its codegree `0` or `1` and all 35 nonadjacent
codegrees in `{0,1,2}` gives a minimum of 26 codegree-two nonadjacent
pairs.  Thus the signs and same-sign edge do not invalidate the bound.

## Oriented counts and the off-by-two check

The imported rank-28 inequality is for oriented theta coefficients:

```text
N14 + N16 + N18 >= 5868.
```

Using the weakest cycle bound 18 gives at least 105,624 oriented
vector-cycle incidences.  Dividing by 2,079 has raw ceiling 51, not 52.
However negation pairs every nonzero vector with a distinct antipode and
preserves all alternating support cycles.  The multiplicity at every rooted
cycle is therefore even, so the forced value is at least 52 oriented
occurrences, equivalently 26 antipodal support pairs.

A universal cap of 25 pairs would give at most
`2079*50=103950` incidences, 1,674 below the lower bound.  This implication
is verified; the cap itself is not.

## Rooted partition

No outside vertex can meet both same-sign anchors because that diagonal
already has the two opposite anchors as all of its common neighbours.  Each
of the four cross edges has exactly one external common neighbour.  These
four witnesses are distinct; a shared witness would meet both anchors of
one same-sign diagonal.  Each anchor has 12 outside neighbours, two of
which are cross-edge witnesses, leaving ten singleton neighbours.  The
outside partition is therefore:

```text
neither 51, P-only 20, N-only 20, one-P-and-one-N 4.
```

For an `h=0` side, each opposite anchor still needs two cross neighbours.
No new vertex can meet both anchors, so four distinct one-anchor vertices
are selected.  After the two cycle anchors, the remaining neither-anchor
counts are `1,2,3` for side sizes `7,8,9`.

## Boundary

This verifies a reduction and a sufficient future cap, not the cap itself.
It neither excludes rank 28 nor proves graph nonexistence.  Conway-99 and
literature novelty remain `UNKNOWN`.
