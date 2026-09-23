# Wave 15 algebraic lane: preinspection freeze

This note was written **before** opening
`agents/2026-07-23-wave15-algebraic.md` or any file under
`attempts/wave15-algebraic/`.  It records the independently expected bridge
from the already audited Wave 14 residual to a possible subset-spectral
contradiction.

The only sources inspected for this freeze were:

| source | SHA-256 |
|---|---|
| `agents/2026-07-22-wave14-n3-48-proof-a.md` | `f0a7d7b5638415cff7d5ad4ef176542de9aa89a2b46a03347f90a2133f18999c` |
| `verification/2026-07-22-wave14-n3-48-proof-audit.md` | `44d1383548b26660dfb5d4b140c831774f6ca81e58ae140e3ceb2f80a9740802` |

Neither the Wave 15 global-lift report nor any global-lift verifier path was
opened.

## Frozen reconstruction

Assume a putative `srg(99,14,1,2)` with `n3=48`.  Wave 14 reduces it to
sixteen active triangle labels, all with `q=2`, and an indexed family

```text
mathcal P = {S_u : S_u is nonempty}
```

of active points.  A point is indexed by an original graph vertex `u`.
Every active label is one graph triangle and consequently lies in exactly
three indexed points, one for each of its three original vertices.  Wave 14
proves

```text
|S_u| in {2,3},
sum_(P in mathcal P) |P| = 16*3 = 48.
```

Thus, for the original-vertex subset

```text
X = {u : S_u is nonempty},
```

the point indexing gives `|X|=|mathcal P|`, and

```text
|X| <= 48/2 = 24.                                      (F1)
```

The indexing must not be silently replaced by a set of *unindexed* block
values.  The map needed below is the literal map `P=S_u -> u`.

Every point of size `s` has `2s` distinct meeting co-points: for each active
triangle through `u`, the other two triangle vertices give two points, and
linearity makes the `2s` vertices distinct.  They are all adjacent to `u`
in the original graph and all belong to `X`.

Wave 14 also supplies a simple support graph `R` on the indexed point
objects.  An `R`-edge is an actual original-graph edge with `H`-degree four,
and

```text
d_R(P)=|P|.
```

For `|P|=3`, the six meeting co-points already imply
`d_(G[X])(u)>=6`.

For `|P|=2`, there are four meeting co-points and two distinct `R`-neighbors.
The essential gap to attack is whether those two support neighbors are new.
They should be: if `Q` meets `P`, then after deleting their one common
active label the `P` side has only one label.  Its labeled crossing with
`Q` cannot have four edges (indeed the two-sided `0/2` rule makes it empty).
Hence this actual edge cannot have `H`-degree four and cannot be an
`R`-edge.  Therefore the two support neighbors are disjoint from the four
meeting neighbors, giving

```text
delta(G[X]) >= 6.                                      (F2)
```

This size-two meeting/support exclusion is the most delicate bridge and
must be stated explicitly.

## Frozen spectral calculation

For `srg(99,14,1,2)`, the restricted adjacency eigenvalues are the roots of

```text
theta^2 - (lambda-mu)theta - (k-mu) = 0,
```

namely `3` and `-4`.  If `m=|X|`, `e=e(G[X])`, and
`1_X=(m/99)1+z` with `z` perpendicular to `1`, then the upper restricted
eigenvalue gives the exact one-sided subset bound

```text
2e = 1_X^T A 1_X
   <= 14m^2/99 + 3(m-m^2/99)
    = 3m + m^2/9.                                     (F3)
```

On the other hand, (F2) gives `2e>=6m`.  Since `X` is nonempty, combining
the inequalities requires

```text
6m <= 3m+m^2/9,
m >= 27,
```

contradicting (F1).  Thus this bridge, if the submitted lane establishes
every mapping and distinctness assertion without adding an unaudited
assumption, should exclude the conditional case `n3=48`.

The companion lower spectral bound, useful as a consistency check but not
needed for the contradiction, is

```text
2e >= 14m^2/99 - 4(m-m^2/99)
    = -4m + 2m^2/11.
```

## Frozen status expectations and attack list

1. A valid proof may promote only the **conditional exclusion**
   `n3 != 48`, not existence or nonexistence of Conway-99.
2. The numerical consequence `n3>=51` additionally needs the previously
   audited lower bound `n3>=48` and the general divisibility `3 | n3`.
   The latter follows from the inherited integer identity
   `sum_T q(T)=2n3/3`; its scope must be cited rather than inferred merely
   from the special value 48.
3. No automorphism, transitivity, connectedness, or completion assumption is
   needed for (F1)--(F3).
4. I will check that support adjacency is adjacency in the original
   99-vertex graph, that `R` is simple, that every meeting co-point lies in
   `X`, and that size-two support neighbors cannot be meeting neighbors.
5. Any extra trace, moment, quotient, or interlacing claim must be derived
   independently.  It is not needed to validate the short contradiction and
   cannot strengthen the publication status without its own checked bridge.

At freeze time the expected conditional conclusion is `DERIVED` pending
independent audit.  Conway-99 and novelty remain `UNKNOWN`.
