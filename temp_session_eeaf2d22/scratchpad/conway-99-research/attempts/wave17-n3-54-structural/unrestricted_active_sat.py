"""Unrestricted-label SAT scout for the n3=54 active equality residual.

This searches all labeled cubic point graphs F on 18 active labels, all
11-regular K supergraphs satisfying the forced point-clique constraints, and
all selected size-two support rectangles.  It enforces exact twofold coverage
of every L=complement(K) edge and the independent-cross-edge matching rule.

It does not encode the 72 outside original vertices, the full SRG equations,
the global triangle-free auxiliary H, or active-subgraph common-neighbor caps.
A SAT result is only a candidate for this stated relaxation.  An UNSAT solver
status is not a proof certificate.
"""

from __future__ import annotations

import itertools
import json

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


VERTICES = tuple(range(18))
LABEL_EDGES = tuple(itertools.combinations(VERTICES, 2))


def main() -> None:
    pool = IDPool()
    f = {item: pool.id(("F", item)) for item in LABEL_EDGES}
    k = {item: pool.id(("K", item)) for item in LABEL_EDGES}

    rectangles: list[
        tuple[
            tuple[int, int],
            tuple[int, int],
            tuple[tuple[int, int], ...],
        ]
    ] = []
    for index, left in enumerate(LABEL_EDGES):
        for right in LABEL_EDGES[index + 1 :]:
            if set(left) & set(right):
                continue
            cross = tuple(
                sorted(
                    tuple(sorted((a, b)))
                    for a in left
                    for b in right
                )
            )
            rectangles.append((left, right, cross))
    y = {
        index: pool.id(("R", index)) for index in range(len(rectangles))
    }
    cnf = CNF()

    def equals(literals, bound: int) -> None:
        cnf.extend(
            CardEnc.equals(
                list(literals),
                bound,
                vpool=pool,
                encoding=EncType.seqcounter,
            )
        )

    def at_most(literals, bound: int) -> None:
        cnf.extend(
            CardEnc.atmost(
                list(literals),
                bound,
                vpool=pool,
                encoding=EncType.seqcounter,
            )
        )

    def conditional_at_least(literals, bound: int, guard: int) -> None:
        encoded = CardEnc.atleast(
            list(literals),
            bound,
            vpool=pool,
            encoding=EncType.seqcounter,
        )
        for clause in encoded.clauses:
            cnf.append([-guard, *clause])

    # Safe global relabeling of the three F-neighbors of label zero.
    for neighbor in (1, 2, 3):
        cnf.append([f[(0, neighbor)]])
    for neighbor in range(4, 18):
        cnf.append([-f[(0, neighbor)]])

    # F is cubic.  K is 11-regular and contains every selected point edge.
    for root in VERTICES:
        equals(
            (f[tuple(sorted((root, other)))] for other in VERTICES if other != root),
            3,
        )
        equals(
            (k[tuple(sorted((root, other)))] for other in VERTICES if other != root),
            11,
        )
    for item in LABEL_EDGES:
        cnf.append([-f[item], k[item]])

    # F is triangle-free, and the three point sets through a label form a
    # K-clique (the singleton crossing between meeting size-two points is zero).
    for a, b, c in itertools.combinations(VERTICES, 3):
        cnf.append([-f[(a, b)], -f[(a, c)], -f[(b, c)]])
    for root in VERTICES:
        others = [item for item in VERTICES if item != root]
        for a, b in itertools.combinations(others, 2):
            cnf.append(
                [
                    -f[tuple(sorted((root, a)))],
                    -f[tuple(sorted((root, b)))],
                    k[tuple(sorted((a, b)))],
                ]
            )

    # A selected support is a pair of selected disjoint point edges and is
    # L-complete across its four endpoint pairs.
    for index, (left, right, cross) in enumerate(rectangles):
        literal = y[index]
        cnf.append([-literal, f[left]])
        cnf.append([-literal, f[right]])
        for crossed in cross:
            cnf.append([-literal, -k[crossed]])

    # Every selected F-edge point has support degree exactly two.  A
    # nonselected potential point has support degree zero.
    for point_edge in LABEL_EDGES:
        incident = [
            y[index]
            for index, (left, right, _) in enumerate(rectangles)
            if point_edge in (left, right)
        ]
        at_most(incident, 2)
        conditional_at_least(incident, 2, f[point_edge])

    # Every L-edge has exactly two covers; every K-edge has none.  On either
    # N3 side the two cross graph-edges use distinct original point objects.
    for label_edge in LABEL_EDGES:
        cover_indices = [
            index
            for index, (_, _, cross) in enumerate(rectangles)
            if label_edge in cross
        ]
        covers = [y[index] for index in cover_indices]
        for literal in covers:
            cnf.append([-literal, -k[label_edge]])
        at_most(covers, 2)
        conditional_at_least(covers, 2, -k[label_edge])

        for side in label_edge:
            for point_edge in LABEL_EDGES:
                if side not in point_edge:
                    continue
                same_point = [
                    y[index]
                    for index in cover_indices
                    if point_edge in rectangles[index][:2]
                ]
                at_most(same_point, 1)

    with Solver(name="cadical195", bootstrap_with=cnf) as solver:
        satisfiable = solver.solve()
        result: dict[str, object] = {
            "scope": "n3=54 all-size-two active incidence/support relaxation",
            "omissions": [
                "72 outside original vertices",
                "full SRG common-neighbor equalities",
                "triangle-free global auxiliary H",
                "active-subgraph common-neighbor caps",
            ],
            "variables": pool.top,
            "clauses": len(cnf.clauses),
            "rectangle_variables": len(rectangles),
            "sat": satisfiable,
            "status_is_not_a_proof_certificate": True,
        }
        if satisfiable:
            model = {literal for literal in solver.get_model() if literal > 0}
            selected_f = [item for item in LABEL_EDGES if f[item] in model]
            selected_k = [item for item in LABEL_EDGES if k[item] in model]
            selected_r = [
                (left, right)
                for index, (left, right, _) in enumerate(rectangles)
                if y[index] in model
            ]
            result["F_edges"] = [list(item) for item in selected_f]
            result["K_edges"] = [list(item) for item in selected_k]
            result["R_edges_as_F_edge_pairs"] = [
                [list(left), list(right)] for left, right in selected_r
            ]
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
