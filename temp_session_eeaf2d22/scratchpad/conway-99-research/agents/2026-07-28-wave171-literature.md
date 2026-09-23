# Wave 171 literature report: partial quadrangles and triad centers

```yaml
role: literature
date_utc: 2026-07-28T20:46:28Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: CITED
scope: >-
  Exact scope of Makhnev--Nirova 2006 for t<=6 and Pech 2021 for
  partial-quadrangle 5-vertex, triad-center, and 3-isoregularity results.
inputs:
  - https://www.mathnet.ru/eng/al161
  - https://www.mathnet.ru/links/7ad01020d38d8d20caa3d6190476927f/al161.pdf
  - https://doi.org/10.1007/s10469-006-0031-6
  - https://www.numdam.org/item/10.5802/alco.183.pdf
method: >-
  Primary-source theorem inspection followed by exact substitution of
  (s,t,mu)=(2,6,2) into Pech's triad-center inequality.
command: >-
  Primary-source PDF inspection and exact integer arithmetic; no broad
  novelty or exhaustive-openness claim.
outputs: []
limitations:
  - The freely accessible Makhnev--Nirova full text inspected here is Russian.
  - The source pass is focused and non-exhaustive.
  - It supplies no construction or nonexistence theorem.
```

## Findings

Makhnev--Nirova's advertised classification for `t<=6` is a classification
of admissible parameter cases.  Theorem 1 item (3) explicitly retains
`srg(99,14,1,2)`, and Lemma 2.4 reaches it at
`m=4,t=6,s=2,mu=2`.  The paper neither constructs nor excludes the target.
Its automorphism conclusions cannot rule out an asymmetric graph.

Pech's Theorem 5.7 makes the 5-vertex condition automatic for every
partial-quadrangle point graph, but does not imply 3-isoregularity.  In the
target there are

```text
27,720 triads with one center,
70,686 triads with no center.
```

Thus the graph would not be 3-isoregular.  This is permitted.  Pech's
Theorem 5.10 specializes to

```text
710>=200,
```

strictly; equality would require one center for every triad.  Proposition
5.14 assumes uniform triad-center counts, so it cannot be used to manufacture
that missing premise.

The focused literature route therefore closes a tempting shortcut: neither
the `t<=6` classification nor the automatic 5-vertex condition resolves
`PQ(2,6,2)`.
