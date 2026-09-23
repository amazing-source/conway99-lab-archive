"""Exploratory all-size-two active-incidence plus exact N3-support SAT model.

This includes substantially more than ``local_incidence_sat.py``:

* F is the selected cubic point graph on 14 active triangles;
* K is 7-regular, contains F, and contains every pair of F-neighbors;
* selected positive-support graph edges are L-complete rectangles between
  disjoint F-edges;
* every F-edge point has exactly two support partners;
* every L-edge is covered by exactly two support rectangles, as required by
  its two independent N3 cross-edges; and
* the two covers form a matching on each N3 side.

The model still omits the 85 inactive graph-triangles, completion to 99
vertices, and the triangle-free condition on the resulting H.  SAT is only a
countermodel to a too-strong local claim; UNSAT would concern this restricted
all-size-two reduction only.
"""

from __future__ import annotations

import itertools
import json

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


VERTICES = tuple(range(14))
EDGES = tuple(itertools.combinations(VERTICES, 2))


def main() -> None:
    pool = IDPool()
    f = {edge: pool.id(("f", edge)) for edge in EDGES}
    k = {edge: pool.id(("k", edge)) for edge in EDGES}

    rectangles = []
    for ei, edge in enumerate(EDGES):
        for other in EDGES[ei + 1 :]:
            if set(edge) & set(other):
                continue
            cross = frozenset(
                tuple(sorted((u, v))) for u in edge for v in other
            )
            rectangles.append((edge, other, cross))
    y = {idx: pool.id(("y", idx)) for idx in range(len(rectangles))}
    cnf = CNF()

    def equals(lits, bound):
        cnf.extend(CardEnc.equals(
            list(lits),
            bound,
            vpool=pool,
            encoding=EncType.seqcounter,
        ))

    def conditional_atleast(lits, bound, guard_lit):
        encoded = CardEnc.atleast(
            list(lits),
            bound,
            vpool=pool,
            encoding=EncType.seqcounter,
        )
        for clause in encoded.clauses:
            cnf.append([-guard_lit, *clause])

    # Safe global relabeling: fix the three F-neighbors of active label zero.
    for j in (1, 2, 3):
        cnf.append([f[(0, j)]])
    for j in range(4, 14):
        cnf.append([-f[(0, j)]])

    # F cubic and K 7-regular.
    for i in VERTICES:
        equals((f[tuple(sorted((i, j)))] for j in VERTICES if j != i), 3)
        equals((k[tuple(sorted((i, j)))] for j in VERTICES if j != i), 7)

    # F point edges lie in K; F is triangle-free by the common-point rule.
    for edge in EDGES:
        cnf.append([-f[edge], k[edge]])
    for a, b, c in itertools.combinations(VERTICES, 3):
        cnf.append([-f[(a, b)], -f[(a, c)], -f[(b, c)]])

    # At a type-222 active triangle, its three F-neighbors form a K-clique.
    for root in VERTICES:
        others = [v for v in VERTICES if v != root]
        for a, b in itertools.combinations(others, 2):
            cnf.append([
                -f[tuple(sorted((root, a)))],
                -f[tuple(sorted((root, b)))],
                k[tuple(sorted((a, b)))],
            ])

    # A support rectangle selects two F-edge points and is L-complete.
    for idx, (edge, other, cross) in enumerate(rectangles):
        lit = y[idx]
        cnf.append([-lit, f[edge]])
        cnf.append([-lit, f[other]])
        for crossed in cross:
            cnf.append([-lit, -k[crossed]])

    # Every selected size-two point has precisely two H-degree-four support
    # graph edges; unselected F candidates have none.
    for edge in EDGES:
        incident = [
            y[idx]
            for idx, (left, right, _) in enumerate(rectangles)
            if edge in (left, right)
        ]
        cnf.extend(CardEnc.atmost(
            incident,
            2,
            vpool=pool,
            encoding=EncType.seqcounter,
        ))
        conditional_atleast(incident, 2, f[edge])

    # Every L edge is an N3 and therefore has exactly two selected cross-edge
    # rectangles.  K edges have no selected rectangle covering them.
    for active_edge in EDGES:
        covering = [
            y[idx]
            for idx, (_, _, cross) in enumerate(rectangles)
            if active_edge in cross
        ]
        for lit in covering:
            cnf.append([-lit, -k[active_edge]])
        cnf.extend(CardEnc.atmost(
            covering,
            2,
            vpool=pool,
            encoding=EncType.seqcounter,
        ))
        # Here guard_lit = -k means: if the edge lies in L, require >=2.
        encoded = CardEnc.atleast(
            covering,
            2,
            vpool=pool,
            encoding=EncType.seqcounter,
        )
        for clause in encoded.clauses:
            cnf.append([k[active_edge], *clause])

        # The two cross graph edges of this N3 may not share an original point
        # object on either side.
        x0, x1 = active_edge
        for side in (x0, x1):
            for point_edge in EDGES:
                if side not in point_edge:
                    continue
                same_point = [
                    y[idx]
                    for idx, (left, right, cross) in enumerate(rectangles)
                    if active_edge in cross and point_edge in (left, right)
                ]
                if len(same_point) > 1:
                    cnf.extend(CardEnc.atmost(
                        same_point,
                        1,
                        vpool=pool,
                        encoding=EncType.seqcounter,
                    ))

    with Solver(name="cadical195", bootstrap_with=cnf) as solver:
        sat = solver.solve()
        summary = {
            "sat": sat,
            "variables": pool.top,
            "clauses": len(cnf.clauses),
            "rectangles": len(rectangles),
        }
        print(json.dumps(summary, sort_keys=True))
        if not sat:
            return
        model = {lit for lit in solver.get_model() if lit > 0}
        selected_f = [edge for edge in EDGES if f[edge] in model]
        selected_k = [edge for edge in EDGES if k[edge] in model]
        selected_y = [
            (edge, other)
            for idx, (edge, other, _) in enumerate(rectangles)
            if y[idx] in model
        ]
        print(json.dumps({
            "F": selected_f,
            "K": selected_k,
            "support": selected_y,
        }))


if __name__ == "__main__":
    main()
