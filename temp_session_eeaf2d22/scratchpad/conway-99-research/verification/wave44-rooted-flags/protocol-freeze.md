# Wave 44 rooted aggregate verifier protocol

Frozen before any `attempts/wave44-rooted-flags/**` file was opened:
2026-07-27T16:25:04Z.

## Trusted public boundary

The only project-specific interface inspected before this freeze is the
already independently verified Wave 43 unrooted seven-deck package:

```text
324a4b84c081c8d2ad8a6a11bae45e0327c03ee2158036156c27efa66fcf790b
  verification/wave43-seven-deck-endpoint/independent_check.py
e38f369d338fada4a561d48019f306511961dd1fd7816e54a12a9ecb09e69f3b
  verification/wave43-seven-deck-endpoint/independent-result.json
fde3a83d28a53b1fdbe56a010605d7aa1a7bee34811d8186e286ac7432ca2c64
  verification/wave43-seven-deck-endpoint/comparison.json
```

It supplies the public canonical interface for 208 locally admissible
unlabeled seven-vertex classes, 62 six-vertex deletion equations, and 19
Hamiltonian formula rows. The Wave 44 discovery implementation, result,
tests, reports, and protocols remain opaque at this freeze.

## Supplied scoped claim

At

```text
n = 99, k = 14, lambda = 1, mu = 2,
n3 = 4158, y = h11/4 = 4158,
```

the 208 unrooted class counts together with the integer variable `y` are
claimed to satisfy an exact nonnegative integer system having 170 rows and
209 variables. A discovery witness is expected to have support 91.

Only feasibility of this finite aggregate rooted relaxation may be promoted.
It is not a graph, a compatible assignment to overlapping subsets, endpoint
evidence, a strict upper bound, or a Conway-99 solution.

## Independently derived rows

Rows and variables are frozen in this exact order:

1. 62 Wave 43 six-to-seven deletion-deck rows `N1,...,N62`.
2. 19 Hamiltonian rows `h0,...,h18`, with every public occurrence of
   `h11` replaced by `4y`.
3. Seven vertex-root rows, ordered by root degree `d=0,...,6`.
4. Thirty-six ordered adjacent-root rows, ordered lexicographically by
   `(a,b,c,d)` with `a in {0,1}` and `a+b+c+d=5`.
5. Forty-six ordered nonadjacent-root rows, ordered lexicographically by
   `(a,b,c,d)` with `a in {0,1,2}` and `a+b+c+d=5`.

This gives `62+19+7+36+46=170` rows. The variables are the 208 canonical
seven-class counts followed by `y`, giving 209 integer variables.

For a seven-vertex graph `H`, the vertex-root coefficient in row `d` is the
number of vertices of degree `d` in `H`. Its right side is

```text
99 * C(14,d) * C(84,6-d).
```

For every ordered adjacent pair `(u,v)` in `H`, classify each of the other
five vertices as adjacent to both roots (`a`), only `u` (`b`), only `v`
(`c`), or neither (`d`). The coefficient is the number of ordered adjacent
root pairs with that exact signature. In an `srg(99,14,1,2)`, an ordered
adjacent root has category sizes `(1,12,12,72)`, so the right side is

```text
99*14 * C(1,a)*C(12,b)*C(12,c)*C(72,d).
```

For an ordered nonadjacent pair, the category sizes are `(2,12,12,71)`, so
the corresponding right side is

```text
99*84 * C(2,a)*C(12,b)*C(12,c)*C(71,d).
```

These equations follow by double-counting a root (or ordered root pair) and
the remaining chosen vertices by their adjacency category. They use no
automorphism of a completed graph and no discovery-specific selection rule.

## Independent verification method

1. Rebuild the complete unlabeled order-seven catalogue and filter it using
   the local `lambda<=1`, `mu<=2` conditions. Bind the class stream to the
   public Wave 43 hash.
2. Rebuild all 170 integer rows directly from canonical graphs and public
   Wave 43 formula metadata. Check signature-set cardinalities, row sums, and
   exact right sides.
3. After this protocol is frozen, open the Wave 44 package, bind every input
   and output hash, and reconstruct its sparse witness into all 209 variables.
4. Check integrality, nonnegativity, `y=4158`, support 91, and every row by
   exact Python integer arithmetic. Compare complete normalized row streams
   and residual streams, not only row counts.
5. Hostile controls must change a positive support coefficient, `y`, a
   vertex-root coefficient, an adjacent-root signature coefficient, a
   nonadjacent-root signature coefficient, and one right side. Every mutation
   must be rejected by exact replay.
6. Run SciPy/HiGHS on the discovery's floating-point scaling route only as a
   diagnostic. Reproduce the claimed false-infeasible status if possible,
   then prove it false by feeding the exact integer witness through the
   unscaled integer rows. Solver exit codes, model prose, and numerical
   tolerances are never certificates.

## Resource and status rules

- One foreground process; no background or orphan workers.
- Abort before free physical memory falls below 15 percent.
- Do not import Wave 44 discovery code.
- Retain any discrepancy rather than silently repairing discovery.
- Promote only `VERIFIED_SCOPED_FEASIBILITY` of the frozen aggregate system.
- Endpoint existence, endpoint exclusion, a strict upper bound, graph
  construction, Conway-99, novelty, and priority remain `UNKNOWN`.
