# Independent verification report

## Verdict

`VERIFIED_WITH_SCOPE`.

Let `D=C+J` over `F_3` at the prism-free endpoint.  If a weight-three vector
`y` belongs to `ker(D)`, restriction of `D*y=0` to its support and elimination
over `F_3` force all three pairwise entries `D_ij` to vanish.  The endpoint
entry table then forces `C_ij=+2`, so the three support blocks are disjoint
with no cross edges and induce `3K3`.

There are two coefficient orbits.  For the mixed orbit `(1,1,-1)`, the
integer vector

```text
z=(C_i+C_j-C_k+1)/3
```

would have squared norm 168 from `C^2=441I` and the row sums.  Its three
support coordinates already contribute 68, while each of the 228 outside
coordinates is `+1` or `-1`, contributing at least 228.  This contradiction
excludes the mixed orbit.

For the all-plus orbit, the outside residue triples are only `000`, `111`,
`222`, or permutations of `012`.  The sum of the three pairwise integer
row-distance squares is 2646.  The three support coordinates contribute
1350, and every `012` position contributes 24, so there are exactly

```text
(2646-1350)/24=54
```

permutation positions.  The three row margins
`(0^33,1^162,2^36)` then force

```text
N000=15,
N111=144,
N222=18.
```

This independently agrees with the discovery derivation.

## Scope

- `P=0` is required to translate the residue class of `C_ij` to `+2` and to
  use the endpoint entry alphabet.
- `r3=12`, projectivity, and the Wave 54 formal enumerator are not required.
- The lemma constrains possible weight-three dual words but neither proves
  nor disproves their existence.
- No graph, endpoint exclusion, strict `n3` bound, or Conway-99 resolution
  follows.
