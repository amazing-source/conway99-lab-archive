# Wave 94 independent audit: general prism-sensitive norm-14 bound

Date UTC: 2026-07-28

## Verdict

**`VERIFIED` in the stated conditional scope, with no mathematical
correction.**

For every hypothetical `srg(99,14,1,2)`, let:

- `P` be the number of induced triangular prisms, meaning two disjoint
  triangles joined by all three matching cross edges;
- `n3` be the number of induced configurations consisting of two disjoint
  triangles joined by exactly two matching cross edges; and
- `N14` count every integer `-4` eigenvector of squared norm 14, counting
  `t` and `-t` separately.

Then

```text
7*N14 <= 38808+12P

N14 <= floor((38808+12P)/7)
     = floor((55440-4*n3)/7).
```

This assumes neither `P=0`, rank 28, nor a graph automorphism. It bounds
only `N14`; it supplies no upper bound for `N16` or `N18`, no strict upper
bound on `n3`, and no Conway-99 resolution.

## Independence and frozen inputs

Before inspecting the discovery derivation, the verifier recorded the path,
byte length, and SHA-256 of all ten discovery files. The discovery manifest
hash was

```text
6c6c12690b59c9d86daf25190e3c89b0616aef525498246295974f1d27c30bf8
```

and remained unchanged. The imported Wave 64 and Wave 71 verifier-manifest
hashes also match their frozen values. `independent_verify.py` imports no
discovery module and reconstructs all finite objects directly.

## 1. The exact meaning of `P` and the identity `n3+3P=4158`

The target graph has

```text
99*14/2 = 693 edges
C(99,2)-693 = 4158 nonedges.
```

Each nonedge has exactly `mu=2` common neighbors. Those common neighbors
cannot be adjacent: otherwise their edge would have both endpoints of the
nonedge as common neighbors, contradicting `lambda=1`. Thus every nonedge
is an opposite pair of a unique induced `C4`, and every induced `C4` has
two opposite nonedges. Hence the number of induced four-cycles is

```text
4158/2 = 2079.
```

Now take either pair of opposite edges in an induced `C4`. Each edge lies
in a unique triangle because `lambda=1`. The two completed triangles are
disjoint, and the two remaining cycle edges are matching cross edges
between them. Cross edges between disjoint triangles must form a matching,
again by `lambda=1`, so the resulting six-vertex graph has either exactly
two cross edges (an `n3` object) or all three (a triangular prism).

Conversely, a two-cross-edge object contains one such induced `C4`; a prism
contains three, one for each choice of two matching cross edges. Double
counting a four-cycle together with a choice of opposite-edge pair gives

```text
n3+3P = 2*2079 = 4158.
```

The checker independently constructs the four possible two-triangle shapes:
cross-matching sizes `0,1,2,3` contain respectively `0,0,1,3` induced
four-cycles.

## 2. Rooted prisms and the factor six

Fix a vertex `o`. Its 14 neighbors induce seven disjoint mate edges. Every
one of the remaining 84 vertices is uniquely labelled by the nonmate pair
of neighbors it has in `N(o)`.

For each base point `s`, the 12 residual labels incident with `s` are paired
by six residual edges: for an incident residual vertex, the unique common
neighbor it has with `s` is another incident residual vertex. There are
therefore 84 selected transitions at the root.

A selected transition

```text
{s,a} -- {s,b}
```

is mate-forbidden when `a` and `b` are the two endpoints of one mate edge.
Then the six vertices form the induced prism with triangles

```text
{o,a,b} and {s,{s,a},{s,b}},
```

and matching edges `o-s`, `a-{s,a}`, and `b-{s,b}`.

Conversely, for a prism containing `o`, the vertex matched to `o` in the
opposite triangle is unique, and the other two matching edges recover the
unique mate-forbidden transition. Therefore

```text
f_o = number of induced prisms containing o.
```

An explicit six-root reconstruction checks all six choices of `o` in the
abstract prism. Each prism is consequently counted once at each of its six
vertices:

```text
sum_o f_o = 6P.
```

This rules out the dangerous alternatives `3P`, `5P`, or `12P`. The later
coefficient `12P` arises only after multiplying this identity by the factor
two in the rooted seed bound.

## 3. Why a norm-14 vector injects into a transition-free seed

Let `t` be a norm-14 integer `-4` eigenvector. The independently verified
low-norm reduction gives seven `+1` and seven `-1` coordinates. Write their
supports as `P+` and `P-`.

If `h` is the number of edges in either same-sign class, summing
`At=-4t` over each class gives

```text
e(P+,P-) = 2h+28,
e(P+ union P-) = 4h+28.
```

The standard restricted-eigenvalue bound with positive restricted
eigenvalue 3 gives at most 31 edges on any 14 vertices. Hence `h=0`.
Both sign classes are independent and their bipartite graph is 4-regular.

Every pair in one sign class is nonadjacent and has at most `mu=2` common
neighbors. The opposite sign class contributes

```text
7*C(4,2) = 42 = 2*C(7,2)
```

pair incidences, saturating every one of those common-neighbor slots. Thus
each pair has exactly two common neighbors in the opposite class. This is
the symmetric complementary-Fano `2-(7,4,2)` incidence design; the argument
uses only the parameters and does not assume a chosen labelling of the
Fano plane.

Fix `o` in `P+` and put

```text
Q = P- intersect N(o).
```

It has four points. Since `P-` is independent, `Q` contains at most one
endpoint from each of the seven mate pairs, so it is one of

```text
C(7,4)*2^4 = 560
```

seeds.

For each pair `{a,b}` in `Q`, its two common positive neighbors are `o` and
the unique rooted residual vertex labelled `{a,b}`. The six pairs in `Q`
therefore recover all six vertices of `P+ - {o}`. Conversely, the same
42-incidence saturation says every vertex outside `P-` meets `P+` at most
once, while each vertex of `P-` meets it four times. Thus `P-` is recovered
from `P+` as the set of vertices with four neighbors in `P+`. The seed
determines the oriented vector, so the map is injective.

If a selected transition were supported by three points of `Q`, its two
residual labels would both be in `P+` and would be adjacent. This contradicts
the independence of `P+`. Every image seed is therefore transition-free.

## 4. Exact seed incidence count and cap

A mate-forbidden transition is contained in no seed, because a seed cannot
use both endpoints of one mate pair. Every other transition has its three
base points in distinct mate groups and is contained in exactly

```text
(7-3)*2 = 8
```

seeds. Thus the `84-f_o` non-forbidden selected transitions give

```text
8*(84-f_o)
```

transition-seed incidences.

At one of the four base points of a seed, only three incident residual
labels lie inside that seed. A local perfect matching can select at most one
pair among three. A seed consequently contains at most four transitions.
The verifier exhausts all

```text
11!! = 10395
```

perfect matchings on 12 labels and all 160 three-endpoint local seed
sections. The maximum is exactly one locally. A separately constructed
global selection attains load four, so replacing the cap by three would be
false.

If `B_o` is the number of bad seeds, then

```text
4*B_o >= 8*(84-f_o),
B_o >= 168-2*f_o.
```

There are 560 seeds, so the number of transition-free seeds is at most

```text
560-(168-2*f_o) = 392+2*f_o.
```

By the injective seed map,

```text
a14(o) <= 392+2*f_o,
```

where `a14(o)` counts norm-14 vectors having coordinate `+1` at `o`.

## 5. Orientation, global sum, floor, and endpoints

`N14` counts both signs. Each oriented vector has exactly seven positive
coordinates, so

```text
sum_o a14(o) = 7*N14.
```

For one sign pair `{t,-t}`, both vectors contribute seven roots, giving
`14=7*2`; there is no extra division by two. Summing the rooted bound and
using the prism multiplicity gives

```text
7*N14
 <= 99*392 + 2*sum_o f_o
 = 38808+12P.
```

Since `N14` is integral,

```text
N14 <= floor((38808+12P)/7).
```

Substituting `P=(4158-n3)/3` gives exactly

```text
N14 <= floor((55440-4*n3)/7).
```

The verifier checks all 1,387 compatible nonnegative identity rows
`P=0,...,1386`, including numerator residues before flooring. The requested
specializations are:

| `n3` | `P` | numerator mod 7 | `N14` upper bound |
|---:|---:|---:|---:|
| 4158 | 0 | 0 | 5544 |
| 4155 | 1 | 5 | 5545 |
| 708 | 1150 | 3 | 7515 |
| 0 | 1386 | 0 | 7920 |

The `n3=0` row is an arithmetic endpoint of the identity, not a claim that
it survives the repository's stronger independently verified lower bound.

## Hostile checks and boundary

Twelve independent tests pass. They reject or expose:

- a local transition selection that is not a perfect matching;
- a false per-seed cap of three;
- counting a prism at only five roots;
- identifying `N14` with sign pairs rather than oriented vectors;
- using ceiling instead of floor at nonzero residues;
- incompatible values such as `n3=4157`;
- drift in any frozen discovery byte or imported manifest; and
- promotion of `N16`, `N18`, a strict `n3` upper bound, graph existence, or
  novelty.

The discovery result agrees field-for-field with the independent theorem.
The final label is `VERIFIED`, conditional on a hypothetical target graph.
Conway-99 and literature novelty remain `UNKNOWN`.

## Reproduce

```powershell
python -B verification/wave94-general-n3-norm14-bound/independent_verify.py `
  --verify verification/wave94-general-n3-norm14-bound/independent-results.json
python -B -m unittest discover `
  -s verification/wave94-general-n3-norm14-bound `
  -p "test_*.py" -v
```
