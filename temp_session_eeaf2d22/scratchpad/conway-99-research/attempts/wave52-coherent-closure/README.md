# Wave 52 rooted coherent closure

Status: discovery-only `DERIVED` null result. This package finds no new
intersection-number or integrality obstruction. The prism-free endpoint and
Conway-99 remain `UNKNOWN`.

## Forced local structure

Fix one graph triangle `R={a,b,c}`. Its eighteen other incident graph
triangles split into six through `a`, six through `b`, and six through `c`.
In the triangle-intersection relation `K`, these eighteen vertices induce
exactly `3K6`.

For petals in different sectors, the root edge gives one cross edge. At the
prism-free endpoint, the pair is therefore in relation `C` or `B`, never `D`.
The SRG common-neighbor equations further force, between each two sectors,
the `B` relation to be a simple 2-regular bipartite graph on `6+6` petals.
Equivalently, every petal has two `B` and four `C` neighbors in each opposite
sector. The proof is in [derivation.md](derivation.md).

This uses the relation order

```text
I: equal
K: share one graph vertex
D: disjoint, zero cross edges
C: disjoint, one cross edge
B: disjoint, two cross edges
```

and assumes no automorphism, transitivity, or association scheme for a
completed graph.

## Completion-free lift

The smallest lift used here keeps all unresolved choices instead of selecting
one `B/C` completion:

```text
19 triangle nodes
108 possible cross-sector B-pair nodes
36 exact-two cap nodes
163 total nodes
```

Each cap belongs to one petal and one opposite sector and contains its six
possible `B` choices. Its required right side is two. Exact 2-dimensional
Weisfeiler-Leman refinement of this binary incidence structure starts with 26
colors, stabilizes after two proper refinement rounds with 47 colors, and has
diagonal class sizes

```text
1, 18, 36, 108.
```

Thus it distinguishes relation roles but does not single out any petal,
candidate `B` choice, or cap. All stable intersection numbers are integral,
as they must be for this realized finite template.

The still smaller partial structure on only the root and its 18 petals starts
and ends with six colors: 2-WL makes no refinement at all.

## Completion dependence

For each pair of six-petal sectors, a simple bipartite 2-factor has one of four
cycle partitions:

```text
(6), (4,2), (3,3), (2,2,2).
```

The program checks all `4^3=64` canonical triples of these cycle profiles.
They give 39 distinct stable intersection fingerprints and stable color counts
ranging from 8 to 361. In particular, the all-`(6)` and all-`(2,2,2)`
examples stabilize at 13 and 8 colors respectively.

These 64 objects are diagnostics, not an exhaustive classification of all
joint labelled completions. Their variation proves that a coherent closure
after choosing `B/C` edges depends on arbitrary completion data. Such colors
are conditional and cannot be promoted to forced endpoint relations.

## Result

There is no obstruction at this scope:

- the forced 19-triangle relation structure has no additional 2-WL split;
- the exact cap CSP has explicit integral completions;
- the completion-free incidence closure gives no forced truth assignment;
- completed coherent closures vary with the chosen local 2-factors.

The useful boundary is now clear. A stronger coherent-configuration route must
add genuinely forced compatibility between different roots, or include
larger point/triangle incidence constraints from the 99-vertex SRG. Refining
one arbitrary local completion cannot prove the endpoint impossible.

## Reproduce

```powershell
python -B attempts\wave52-coherent-closure\coherent_closure.py `
  --output attempts\wave52-coherent-closure\exact-result.json

python -B attempts\wave52-coherent-closure\coherent_closure.py `
  --verify attempts\wave52-coherent-closure\exact-result.json

python -B -m unittest discover `
  -s attempts\wave52-coherent-closure -p "test_*.py" -v
```

The implementation uses standard-library integer arithmetic and enforces a
20 percent free-physical-memory floor. The full stable pair-color matrices and
nonzero intersection tensors are retained in `exact-result.json`.

## Boundary

- This is discovery-agent work and is not independently verified.
- Exact-two cap values are checked by explicit integral completions; 2-WL
  itself only refines the incidence structure.
- The scope contains one root and eighteen neighbors, not all 231 graph
  triangles or all 99 graph vertices.
- A local cap completion is not a graph construction.
- No endpoint exclusion or improved upper bound for `n3` follows.

