# Wave 133: rooted-triangle holonomy and the missing twist class

## Verdict

This lane derives a stronger exact identity, but it does not exclude the
prism-free endpoint.

For a graph triangle `T=(a,b,c)`, the three twelve-vertex outside fibres

```text
X=N(a)-{b,c}, Y=N(b)-{a,c}, Z=N(c)-{a,b}
```

each induce `6K2`, and every pair of fibres is joined by a perfect matching.
Composing the three cross matchings gives a permutation

```text
h_T = m_ZX o m_YZ o m_XY : X -> X.
```

Fibre relabellings conjugate `h_T`, reversing the triangle orientation
inverts it, and a fixed point is exactly an induced triangular prism based
at `T`.  Thus the endpoint makes every `h_T` a derangement.

## What the sign actually measures

A `k`-cycle of `h_T` gives a `3k`-cycle in the cross-fibre two-factor and
one component of the link of `T` in the Wave 40 edge/triangle surface.
Writing `h(T)` for the number of cycles of `h_T` and

```text
H = sum_T h(T),
```

gives

```text
sign(h_T)=(-1)^h(T),
product_T sign(h_T)=(-1)^H=(-1)^(chi+E-F).
```

For the all-`222` case, `E=4158` and `F=2079`.  If all normalized surface
components were orientable, `chi` would be even, forcing the global sign
product to be `-1`.  The missing step is exactly orientability, or an
equivalent constraint on the edge-twist class.

## Exact controls

The checker emits two 39-vertex partial triangle stars.  Both have a cubic,
triangle-free 36-vertex core, respect the inherited common-neighbor caps,
and have nonnegative forced one-triangle Gram entries.  One holonomy has
cycle type `2^6` and sign `+1`; the other is a 12-cycle and has sign `-1`.
Derangement alone therefore has no sign preference.

The global control starts from a two-vertex, six-edge, three-square
nonorientable cellulation.  A connected regular 693-sheet cover over
`(C7 semidirect C3) x C33`, followed by an exactly checked balanced
partition, gives:

```text
231 quotient vertices;
4158 distinct edges in a simple 36-regular quotient;
2079 distinct quadrilateral faces;
two faces incident with every edge;
six disjoint C6 link components at every quotient vertex;
H=1386, chi=-693, global holonomy-sign product +1.
```

This is an endpoint-scale positive control for the holonomy plus surface
incidence relaxation.  It is necessarily nonorientable because it is
connected and has odd Euler characteristic.

## Boundary

The surface is not a 99-vertex graph.  It does not construct the sixty-block
`B` system, the outside graph `H`, or a full `N3` relation with every
intersection law inherited from an SRG.  It proves that a parity argument
using only derangement, the Wave 40 face counts, simple 36-regular `L`, and
the stated link cycles cannot work.  A successful continuation must derive
orientability, constrain the first Stiefel-Whitney (edge-twist) class, or
couple holonomy to additional point-level `B/H` equations.

## Replay

```powershell
python -B attempts/wave133-triangle-holonomy-topology/exact_check.py `
  --verify attempts/wave133-triangle-holonomy-topology/exact-results.json
python -B -m unittest discover `
  -s attempts/wave133-triangle-holonomy-topology -p "test_*.py" -v
```
