# Wave 72 independent order-11 fixed-point audit

Date UTC: 2026-07-27T23:16:44Z

Verdict: **VERIFIED** for the fixed-point theorem.  The Wave 69 combination
remains explicitly conditional because this package does not audit Wave 69.

## Verified theorem

Let `G` be a hypothetical `srg(99,14,1,2)` and let `g` be an automorphism of
permutation order exactly 11.  Then `g` fixes no vertex.

No transitivity assumption is used.

## Independent proof

Let `F` be the fixed-vertex set, `f=|F|`, and `H=G[F]`.

Every vertex orbit under `g` has size 1 or 11, so

```text
f = 0 mod 11.
```

For a fixed vertex `x`, its 14-element neighborhood is invariant.  Nonfixed
vertices in that neighborhood occur in 11-orbits, hence the fixed degree
`d_x` in `H` satisfies

```text
d_x in {3,14}.
```

For distinct fixed vertices `x,y`, their common-neighbor set is invariant.
Its size is 1 if `x,y` are adjacent and 2 otherwise.  Both sizes are smaller
than 11, so neither set can contain a nontrivial 11-orbit.  Every common
neighbor is therefore fixed.

The `x` row sum of `A_H^2` may now be counted exactly:

```text
sum_(z adjacent_H x) d_z
  = d_x + 1*d_x + 2*(f-1-d_x)
  = 2f-2.                                           (1)
```

If all fixed degrees are 14, equation (1) gives `196=2f-2`, hence `f=99`.
That means `g` fixes every graph vertex and is the identity permutation,
whose order is 1, not exactly 11.

Otherwise some fixed vertex has degree 3.  Its three neighbors have degree at
most 14, so (1) gives `2f-2<=42`, or `f<=22`.  The only positive multiples of
11 to check are `f=11` and `f=22`.

- At `f=11`, degree 14 is impossible in a simple graph on 11 vertices.  All
  fixed degrees would be 3, but equation (1) reads `9=20`.
- At `f=22`, equation (1) forces every neighbor of a degree-3 vertex to have
  degree 14.  It also forces every neighbor of a degree-14 vertex to have
  degree 3.  Thus the fixed graph is bipartite between degree types.  Cross
  edges would satisfy `3|L|=14|R|` and `|L|+|R|=22`, giving
  `66=17|R|`, impossible.  Independently, any such cross edge would lie in no
  triangle, contradicting `lambda=1`.

Thus every positive fixed count is impossible and `f=0`.

## Identity and nonidentity scope

The exact-order wording is essential.  If one weakened the hypothesis to
`g^11=1`, the identity permutation would be included and would fix all 99
vertices.  The independent enumerator deliberately retains the `f=99`
identity model and excludes it only because its permutation order is 1.

## Conditional Wave 69 implication

A fixed-point-free order-11 action on 99 vertices has exactly nine 11-orbits,
so it is a semiregular `C11` action.  Therefore, **if** a separate complete
verification excludes every such semiregular action, the theorem above
excludes every order-11 automorphism.

If a realization were vertex-transitive, orbit-stabilizer would make its
finite automorphism-group order divisible by 99, hence by 11.  Cauchy's
theorem would then supply an automorphism of order 11.  Consequently, the
same separately verified combination would exclude vertex-transitive
realizations.

This is a conditional symmetry exclusion, not a global nonexistence proof.
Asymmetric targets remain in scope.

## Independence and hostile controls

The complete discovery directory was hashed by path and byte size before
inspection.  The independent derivation above was reconstructed before
discovery code or prose was read.  The verifier does not import or execute
discovery code.

The exact verifier independently enumerates the necessary fixed-degree
models, checks graph capacities and parity, and retains only:

```text
f=0,   empty fixed set;
f=99,  all degree 14, identity permutation.
```

Hostile tests cover:

- all fixed-count congruence classes;
- the strict `<11` condition in common-neighbor closure;
- fixed degree options `{3,14}`;
- the `f=11`, `f=22`, and `f=99` branches;
- cross-edge balance and parity;
- the difference between order exactly 11 and order dividing 11;
- the conditional status of the Wave 69 implication;
- semantic-result mutation;
- discovery-byte mutation; and
- disagreement between independent and discovery mathematics.

The six compared mathematical fields agree.

## Replay

```powershell
.\.venv\Scripts\python.exe `
  verification\wave72-order11-automorphism\independent_verify.py `
  --verify `
  --discovery-results `
  attempts\wave72-order11-automorphism\exact-results.json `
  --comparison-output `
  verification\wave72-order11-automorphism\comparison.json

.\.venv\Scripts\python.exe -m unittest -v `
  verification\wave72-order11-automorphism\test_independent_verify.py

.\.venv\Scripts\python.exe `
  attempts\wave72-order11-automorphism\exact_check.py --verify

.\.venv\Scripts\python.exe -m unittest discover -v `
  -s attempts\wave72-order11-automorphism -p "test_*.py"
```

Results:

```text
independent deterministic replay: PASS
independent hostile tests:         14 passed
discovery canonical replay:        PASS
discovery tests inspected:          9 passed
mathematical comparison:            6 fields, 0 mismatches
post-run discovery inventory:       12 files unchanged
```

## Boundary

Wave 69 is not verified here.  No claim is made about automorphisms of other
orders, asymmetric graphs, existence, endpoint resolution, or literature
priority.  Conway-99 remains `UNKNOWN`.
