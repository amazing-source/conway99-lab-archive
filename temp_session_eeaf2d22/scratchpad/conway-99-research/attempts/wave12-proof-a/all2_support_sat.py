"""Exact support test for the all-size-two local countermodel found by SAT.

The 21 selected point sets are the edges of a cubic graph F.  K is its
distance-at-most-two graph and L is the complement.  A candidate positive
original graph edge joins two F-edges whose four endpoint pairs all lie in L.
Such a support edge has H-degree four.

The SAT instance asks for:
* support degree two at every F-edge point;
* exact double coverage of every L-edge (the two N3 cross-edges); and
* matching coverage on each side of every L-edge.

It still does not encode the full 99-vertex graph or triangle-freeness of H.
"""

from __future__ import annotations

import itertools

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


F_EDGES = [
    (0, 3), (0, 4), (0, 8), (1, 9), (1, 10), (1, 13), (2, 5),
    (2, 9), (2, 11), (3, 5), (3, 11), (4, 6), (4, 11), (5, 12),
    (6, 8), (6, 10), (7, 8), (7, 10), (7, 13), (9, 12), (12, 13),
]


def main() -> None:
    vertices = range(14)
    f = {tuple(sorted(edge)) for edge in F_EDGES}
    adj = {i: set() for i in vertices}
    for u, v in f:
        adj[u].add(v)
        adj[v].add(u)

    k = set(f)
    for root in vertices:
        for edge in itertools.combinations(adj[root], 2):
            k.add(tuple(sorted(edge)))
    l = {
        edge
        for edge in itertools.combinations(vertices, 2)
        if tuple(sorted(edge)) not in k
    }

    point_pairs = []
    for ei, e in enumerate(F_EDGES):
        for fi in range(ei + 1, len(F_EDGES)):
            g = F_EDGES[fi]
            cross = {
                tuple(sorted((u, v)))
                for u in e
                for v in g
                if u != v
            }
            if len(cross) == 4 and cross <= l:
                point_pairs.append((ei, fi, cross))

    pool = IDPool()
    y = {idx: pool.id(("support", idx)) for idx in range(len(point_pairs))}
    cnf = CNF()

    for ei in range(len(F_EDGES)):
        lits = [
            y[idx]
            for idx, (a, b, _) in enumerate(point_pairs)
            if ei in (a, b)
        ]
        cnf.extend(CardEnc.equals(lits, 2, vpool=pool, encoding=EncType.seqcounter))

    for ledge in sorted(l):
        covering = [
            y[idx]
            for idx, (_, _, cross) in enumerate(point_pairs)
            if ledge in cross
        ]
        if len(covering) < 2:
            print({
                "sat": False,
                "reason": "L edge has fewer than two compatible support rectangles",
                "L_edge": ledge,
                "compatible_rectangles": len(covering),
            })
            return
        cnf.extend(CardEnc.equals(covering, 2, vpool=pool, encoding=EncType.seqcounter))

        # At either endpoint triangle, the two selected cross graph edges must
        # use different original point objects.
        for side in ledge:
            incident_points = [
                ei for ei, edge in enumerate(F_EDGES) if side in edge
            ]
            for ei in incident_points:
                same_point_cover = [
                    y[idx]
                    for idx, (a, b, cross) in enumerate(point_pairs)
                    if ledge in cross and ei in (a, b)
                ]
                cnf.extend(CardEnc.atmost(
                    same_point_cover,
                    1,
                    vpool=pool,
                    encoding=EncType.seqcounter,
                ))

    with Solver(name="cadical195", bootstrap_with=cnf) as solver:
        sat = solver.solve()
        print({
            "sat": sat,
            "F_edges": len(F_EDGES),
            "K_edges": len(k),
            "L_edges": len(l),
            "candidate_support_edges": len(point_pairs),
            "clauses": len(cnf.clauses),
        })
        if sat:
            model = {lit for lit in solver.get_model() if lit > 0}
            selected = [
                (F_EDGES[a], F_EDGES[b])
                for idx, (a, b, _) in enumerate(point_pairs)
                if y[idx] in model
            ]
            print({"support_edges": selected})


if __name__ == "__main__":
    main()
