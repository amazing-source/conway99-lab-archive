# Wave 204 statement/literature and hostile-control lane

## Verdict

`REFUTED_PENDING_INDEPENDENT_VERIFICATION`:

> The 99-center degree/complement data, local `(7,3)` Hilton--Milner
> families, four-point pair fibers, the Wave201 equality row, and the
> Wave203 five-slot capacity force a bidirectional selected label.

An exact rational `0/1` countermodel satisfies that entire restricted
interface with

```text
J=3561, delta=3,
n3=1200, p3=3123, q=237,
profile(nonprivate)=2^234 3^3,
epsilon=708,
L=delta-3q+epsilon=0,
b=0.
```

All 237 nonprivate labels occur as three outgoing labels at each of 79
centers; 20 centers have none. Every occurrence has an explicit
four-point pair fiber and a distinct Wave203 third-block slot. All full
labels obey one global orientation of an 84-regular complement, so even
the full two-orientation multiplicity is at most three.

This is a decisive countermodel only to the displayed local-interface
lemma. The 14-regular circulant skeleton is visibly not strongly regular;
the declared block/fiber types are not induced by its adjacency; and no
ternary columns, rank-11 code, canonical relations, or circuit cover are
provided. It is not endpoint-existence evidence.

```yaml
role: literature
date_utc: 2026-07-29T18:57:01Z
git_commit: e6ac24b5728ae8f2dc13b5a6ee0f50e965843b71
claim_label: REFUTED
scope: >-
  Refute the restricted lemma that 99-center degree/complement data,
  local Hilton--Milner families, four-point pair fibers, Wave201 equality,
  and Wave203 five-slot capacity force b>0; audit current primary-source
  candidates for a genuine global obstruction.
inputs:
  attempts/wave204-literature-hostile-controls/input-freeze.sha256: SELF_HASHED_IN_PACKAGE
method: >-
  Deterministic exact construction on Z/99Z, explicit 99-center local
  incidence and slot certificate, exact integer replay, focused tests,
  and primary-source theorem/hypothesis audit.
command: >-
  .\.venv\Scripts\python.exe -B
  attempts\wave204-literature-hostile-controls\build_countermodel.py
  --verify
  attempts\wave204-literature-hostile-controls\countermodel.json;
  .\.venv\Scripts\python.exe -B -m unittest -v
  attempts\wave204-literature-hostile-controls\test_countermodel.py
outputs:
  - agents/2026-07-29-wave204-literature-hostile-controls.md
  - attempts/wave204-literature-hostile-controls/
limitations:
  - Discovery cannot promote its own countermodel to VERIFIED.
  - The circulant skeleton is not an SRG.
  - No rank-11 ternary column or circuit realization is supplied.
  - Primary-source coverage is focused rather than exhaustive.
  - Conway 99, the prism-free endpoint, and external novelty remain UNKNOWN.
```

## Exact construction

Let the centers be `Z/99Z`. The skeleton joins differences `+-1,...,+-7`
and therefore has degree 14 and complement degree 84. Orient complement
edges by positive differences `8,...,49`.

At every center place the 13-member Hilton--Milner `H` family on seven
blocks. Its three degree-five pairs are `{0,1},{0,2},{0,3}`. The first 79
centers select all thirteen flags and put one nonprivate selected label in
each degree-five fiber. Three labels have multiplicity three and the other
234 have multiplicity two. The remaining twenty centers select 173 flags
in total with every selected leaf label private. This gives 1,200 selected
flags and the exact multiplicity profile above.

The 297 compulsory full-fiber repetitions plus the three extra losses from
multiplicity-three groups give

```text
J=99*39-297-3=3561.
```

For a pair `P` in a local triple `A`, the certificate records the Wave203
slot `A-P`. Repeated labels use distinct triples, hence distinct slots.
Because every used label follows the global complement orientation, no
reverse occupancy occurs.

The exact selected capacity slack is

```text
5*3360-(3*1200+4*3123)=708=epsilon.
```

Thus the restricted equations do not force `b>0`.

## Literature boundary

The focused primary-source audit covers the current target status,
cellular sheaf/CSP cohomology, gain and biased graphs, frame/lifted-graphic
matroids, strong circuit elimination, orthogonal matroids, finite-field
zero-tight frames, classical fusion frames, partial geometric designs,
polar caps, Hilton--Milner equality, and higher-order
association-scheme/Terwilliger bounds.

No retained theorem applies to the exact conjunction of the 231 ternary
columns, 99 star decompositions, zero fusion-frame sum, canonical
quadrilateral relation, and partial directional slots. The recurring
hypothesis failures are exact:

- sheaf/gain theorems need derived restriction or group-valued transition
  maps, whereas Wave203 has only partial injections;
- symmetric strong elimination needs no skew circuits;
- classical fusion-frame bounds need positive Hilbert geometry;
- polar cap bounds exclude orthogonal pairs, while the target has 3,696;
- Hilton--Milner is saturated locally and has no cross-center conclusion;
- higher-order bounds need a specified scheme/orbit algebra and exact PSD
  moments not yet derived.

The best next theorem in this lane is:

> Derive, from the globally fixed ternary columns rather than from slot
> counts, a nontrivial transition map on two-center overlaps whose cycle
> product is forced and is violated by every `b=0` section.

Without that column-derived transition law, cohomology is analogy rather
than an obstruction.
