"""Exploratory SAT model for the Wave 12 r=14 local incidence premises.

This is deliberately a countermodel finder, not a certificate generator.
It includes only the active point-hypergraph, K-complement, linearity,
common-point, and meeting-crossing premises.  It does not encode a completed
99-vertex strongly regular graph.
"""

from __future__ import annotations

import argparse
import itertools
import json

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


def pairs(items):
    return itertools.combinations(sorted(items), 2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--size3", type=int, default=None)
    args = parser.parse_args()

    vertices = tuple(range(14))
    points = [
        frozenset(c)
        for size in (2, 3)
        for c in itertools.combinations(vertices, size)
    ]
    point_index = {point: idx for idx, point in enumerate(points)}
    edge_list = list(itertools.combinations(vertices, 2))

    pool = IDPool()
    x = {point: pool.id(("point", tuple(sorted(point)))) for point in points}
    k = {edge: pool.id(("k", edge)) for edge in edge_list}
    cnf = CNF()

    def add_equals(lits, bound):
        enc = CardEnc.equals(
            lits=list(lits),
            bound=bound,
            vpool=pool,
            encoding=EncType.seqcounter,
        )
        cnf.extend(enc.clauses)

    # Every active triangle has exactly three original points.
    for i in vertices:
        add_equals((x[p] for p in points if i in p), 3)

    # Optional exact number of size-three points.
    if args.size3 is not None:
        add_equals((x[p] for p in points if len(p) == 3), args.size3)

    # Point hypergraph linearity and point-clique edges in K.
    for edge in edge_list:
        owners = [x[p] for p in points if set(edge) <= p]
        cnf.extend(CardEnc.atmost(owners, 1, vpool=pool, encoding=EncType.seqcounter))
    for p in points:
        for edge in pairs(p):
            cnf.append([-x[p], k[edge]])

    # The common-point/Berge-triangle rule, expressed around each meeting.
    for ai, a in enumerate(points):
        for b in points[ai + 1 :]:
            meet = a & b
            if len(meet) != 1:
                continue
            i = next(iter(meet))
            for u in a - {i}:
                for v in b - {i}:
                    for c in points:
                        if u in c and v in c:
                            cnf.append([-x[a], -x[b], -x[c]])

    # Meeting crossing rule after deleting the common active triangle.
    for ai, a in enumerate(points):
        for b in points[ai + 1 :]:
            meet = a & b
            if len(meet) != 1:
                continue
            i = next(iter(meet))
            aa = sorted(a - {i})
            bb = sorted(b - {i})
            cross = [k[tuple(sorted((u, v)))] for u in aa for v in bb]
            if len(aa) == 1 or len(bb) == 1:
                for lit in cross:
                    cnf.append([-x[a], -x[b], lit])
            else:
                # L-crossing is empty or K_2,2, so the complementary K block
                # is respectively complete or empty.
                first = cross[0]
                for lit in cross[1:]:
                    cnf.append([-x[a], -x[b], -first, lit])
                    cnf.append([-x[a], -x[b], first, -lit])

    # K is 7-regular.
    for i in vertices:
        add_equals((k[tuple(sorted((i, j)))] for j in vertices if j != i), 7)

    with Solver(name="cadical195", bootstrap_with=cnf) as solver:
        sat = solver.solve()
        print(json.dumps({"sat": sat, "size3": args.size3, "vars": pool.top, "clauses": len(cnf.clauses)}))
        if not sat:
            return
        model = set(lit for lit in solver.get_model() if lit > 0)
        selected_points = [sorted(p) for p in points if x[p] in model]
        selected_k = [list(edge) for edge in edge_list if k[edge] in model]
        print(json.dumps({"points": selected_points, "k_edges": selected_k}, sort_keys=True))


if __name__ == "__main__":
    main()
