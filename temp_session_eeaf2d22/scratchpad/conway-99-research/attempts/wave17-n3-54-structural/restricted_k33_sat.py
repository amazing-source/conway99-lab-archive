"""Restricted exact SAT scout for the n3=54 equality residual.

Restriction (essential): the cubic point graph F is fixed to three disjoint
copies of K_3,3.  This is not a complete equality-case search.

The selected graph R is a 2-factor on E(F).  A selected R-edge pairs two
disjoint F-edges.  Its four endpoint pairs are required to have exact
twofold rectangle coverage; every covered label pair has two covers whose
cross graph-edges form a matching on both N3 sides.

The program prints either UNSAT in this explicitly restricted model or one
machine-readable candidate.  Solver status alone is not a proof certificate.
"""

from __future__ import annotations

import argparse
import itertools
import json

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


def edge(left: int, right: int) -> tuple[int, int]:
    return (left, right) if left < right else (right, left)


def build_f() -> tuple[tuple[int, int], ...]:
    result: list[tuple[int, int]] = []
    for component in range(3):
        offset = 6 * component
        left = range(offset, offset + 3)
        right = range(offset + 3, offset + 6)
        result.extend((a, b) for a in left for b in right)
    return tuple(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--omit-matching",
        action="store_true",
        help="hostile control: omit independent N3 cross-edge matching",
    )
    args = parser.parse_args()
    f_edges = build_f()
    point_component = tuple(index // 9 for index in range(27))
    candidates: list[tuple[int, int, tuple[tuple[int, int], ...]]] = []
    for first, second in itertools.combinations(range(27), 2):
        if point_component[first] == point_component[second]:
            continue
        rectangle = tuple(
            sorted(
                edge(a, b)
                for a in f_edges[first]
                for b in f_edges[second]
            )
        )
        candidates.append((first, second, rectangle))

    pool = IDPool()
    selected = {
        index: pool.id(("R", index)) for index in range(len(candidates))
    }
    cnf = CNF()

    def equals(literals: list[int], bound: int) -> None:
        cnf.extend(
            CardEnc.equals(
                literals,
                bound,
                vpool=pool,
                encoding=EncType.seqcounter,
            )
        )

    def at_most(literals: list[int], bound: int) -> None:
        cnf.extend(
            CardEnc.atmost(
                literals,
                bound,
                vpool=pool,
                encoding=EncType.seqcounter,
            )
        )

    # R is exactly 2-regular on the 27 point objects.
    for point in range(27):
        equals(
            [
                selected[index]
                for index, (left, right, _) in enumerate(candidates)
                if point in (left, right)
            ],
            2,
        )

    # A label pair has either zero or exactly two selected rectangle covers.
    # If covered, the two covers use distinct original point objects at each
    # side label, as required by the two independent N3 cross-edges.
    all_label_pairs = tuple(itertools.combinations(range(18), 2))
    for label_pair in all_label_pairs:
        covers = [
            index
            for index, (_, _, rectangle) in enumerate(candidates)
            if label_pair in rectangle
        ]
        literals = [selected[index] for index in covers]
        if not literals:
            continue
        at_most(literals, 2)
        for index in covers:
            other_literals = [
                selected[other] for other in covers if other != index
            ]
            cnf.append([-selected[index], *other_literals])

        if not args.omit_matching:
            for side_label in label_pair:
                incident_points = [
                    point
                    for point, point_edge in enumerate(f_edges)
                    if side_label in point_edge
                ]
                for point in incident_points:
                    same_point = [
                        selected[index]
                        for index in covers
                        if point in candidates[index][:2]
                    ]
                    at_most(same_point, 1)

    with Solver(name="cadical195", bootstrap_with=cnf) as solver:
        satisfiable = solver.solve()
        output: dict[str, object] = {
            "scope": "F=3K3,3 restricted n3=54 all-size-two residual",
            "restriction": "point graph fixed to three disjoint K3,3 components",
            "independent_cross_edge_matching_enforced": not args.omit_matching,
            "variables": pool.top,
            "clauses": len(cnf.clauses),
            "candidate_R_edges": len(candidates),
            "sat": satisfiable,
            "status_is_not_a_proof_certificate": True,
        }
        if satisfiable:
            model = {literal for literal in solver.get_model() if literal > 0}
            chosen = [
                (left, right)
                for index, (left, right, _) in enumerate(candidates)
                if selected[index] in model
            ]
            coverage = {
                f"{left}-{right}": sum(
                    label_pair in rectangle
                    for index, (_, _, rectangle) in enumerate(candidates)
                    if selected[index] in model
                )
                for label_pair in all_label_pairs
                for left, right in (label_pair,)
            }
            output["F_edges"] = [list(item) for item in f_edges]
            output["R_edges"] = [list(item) for item in chosen]
            output["covered_label_pairs"] = {
                key: value for key, value in coverage.items() if value
            }
        print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
