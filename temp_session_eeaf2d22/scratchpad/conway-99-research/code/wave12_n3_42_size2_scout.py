#!/usr/bin/env python3
"""Pinned SAT scout for a restricted all-size-two ``n3=42`` active model.

The SAT domain has 14 active triangles.  ``F`` is the graph of size-two point
sets and ``K`` is the complement of the active ``L`` graph.  The encoding
requires:

* ``F`` cubic and triangle-free;
* ``K`` 7-regular with ``F`` as a subgraph; and
* the three ``F``-neighbors of every active triangle form a clique in ``K``.

Those clauses are exactly the active-local point, common-point, and
singleton-crossing conditions in the all-size-two restriction.  A second SAT
instance finds a 2-factor in the graph of disjoint point pairs whose complete
2-by-2 crossing lies in ``L``.  The emitted object is a counterexample to an
overstrong *local* exclusion only; it is not a Conway-99 graph.
"""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
from pathlib import Path
from typing import Sequence

import pysat
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
VALIDATOR_PATH = HERE / "wave12_n3_42_active.py"
SPEC = importlib.util.spec_from_file_location(
    "wave12_n3_42_active_validator", VALIDATOR_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load the independent candidate validator")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)

ORDER = 14
SOLVER_NAME = "cadical195"


def edge(left: int, right: int) -> tuple[int, int]:
    return (left, right) if left < right else (right, left)


def base_instance() -> tuple[CNF, IDPool, object, object]:
    pool = IDPool()

    def f_var(left: int, right: int) -> int:
        return pool.id(("F", *edge(left, right)))

    def k_var(left: int, right: int) -> int:
        return pool.id(("K", *edge(left, right)))

    formula = CNF()
    for vertex in range(ORDER):
        formula.extend(
            CardEnc.equals(
                [
                    f_var(vertex, other)
                    for other in range(ORDER)
                    if other != vertex
                ],
                bound=3,
                vpool=pool,
                encoding=EncType.seqcounter,
            ).clauses
        )
        formula.extend(
            CardEnc.equals(
                [
                    k_var(vertex, other)
                    for other in range(ORDER)
                    if other != vertex
                ],
                bound=7,
                vpool=pool,
                encoding=EncType.seqcounter,
            ).clauses
        )

    for left, right in itertools.combinations(range(ORDER), 2):
        formula.append([-f_var(left, right), k_var(left, right)])

    for first, second, third in itertools.combinations(range(ORDER), 3):
        formula.append(
            [
                -f_var(first, second),
                -f_var(first, third),
                -f_var(second, third),
            ]
        )

    for root in range(ORDER):
        outside = [vertex for vertex in range(ORDER) if vertex != root]
        for left, right in itertools.combinations(outside, 2):
            formula.append(
                [
                    -f_var(root, left),
                    -f_var(root, right),
                    k_var(left, right),
                ]
            )
    return formula, pool, f_var, k_var


def compatibility_edges(
    point_edges: Sequence[tuple[int, int]],
    k_edges: frozenset[tuple[int, int]],
) -> tuple[tuple[int, int], ...]:
    output = []
    for left_index, right_index in itertools.combinations(
        range(len(point_edges)), 2
    ):
        left_point = point_edges[left_index]
        right_point = point_edges[right_index]
        if set(left_point) & set(right_point):
            continue
        cross = {
            edge(left, right)
            for left in left_point
            for right in right_point
        }
        if not cross & k_edges:
            output.append((left_index, right_index))
    return tuple(output)


def support_2factor(
    point_count: int, compatible: Sequence[tuple[int, int]]
) -> tuple[tuple[int, ...], dict[str, int]]:
    pool = IDPool()
    variables = {pair: pool.id(("support", *pair)) for pair in compatible}
    formula = CNF()
    for point in range(point_count):
        incident = [
            variable
            for pair, variable in variables.items()
            if point in pair
        ]
        if len(incident) < 2:
            raise AssertionError("support compatibility graph has degree below two")
        formula.extend(
            CardEnc.equals(
                incident,
                bound=2,
                vpool=pool,
                encoding=EncType.seqcounter,
            ).clauses
        )
    with Solver(name=SOLVER_NAME, bootstrap_with=formula.clauses) as solver:
        if not solver.solve():
            raise AssertionError("first active-local model has no support 2-factor")
        positive = {literal for literal in solver.get_model() if literal > 0}
    selected = tuple(
        pair for pair, variable in variables.items() if variable in positive
    )
    adjacency = {point: [] for point in range(point_count)}
    for left, right in selected:
        adjacency[left].append(right)
        adjacency[right].append(left)
    if any(len(values) != 2 for values in adjacency.values()):
        raise AssertionError("support model is not 2-regular")

    cycles = []
    unseen = set(range(point_count))
    while unseen:
        start = min(unseen)
        cycle = []
        previous = -1
        current = start
        while current in unseen:
            unseen.remove(current)
            cycle.append(current)
            first, second = sorted(adjacency[current])
            following = first if first != previous else second
            previous, current = current, following
        cycles.append(tuple(cycle))
    if len(cycles) != 1:
        raise AssertionError(
            "the deterministic first model did not yield one support cycle"
        )
    return cycles[0], {
        "variables": pool.top,
        "clauses": len(formula.clauses),
        "compatible_pairs": len(compatible),
        "selected_pairs": len(selected),
    }


def solve() -> dict[str, object]:
    formula, pool, f_var, k_var = base_instance()
    with Solver(name=SOLVER_NAME, bootstrap_with=formula.clauses) as solver:
        if not solver.solve():
            raise AssertionError("restricted all-size-two active model is UNSAT")
        positive = {literal for literal in solver.get_model() if literal > 0}
        statistics = {
            key: int(value)
            for key, value in solver.accum_stats().items()
        }

    point_edges = tuple(
        pair
        for pair in itertools.combinations(range(ORDER), 2)
        if f_var(*pair) in positive
    )
    k_edges = frozenset(
        pair
        for pair in itertools.combinations(range(ORDER), 2)
        if k_var(*pair) in positive
    )
    compatible = compatibility_edges(point_edges, k_edges)
    support_cycle, support_metadata = support_2factor(
        len(point_edges), compatible
    )
    certificate: dict[str, object] = {
        "schema": "wave12-n3-42-all-size2-active-local-v1",
        "claim_label": "CANDIDATE",
        "target_result": "UNKNOWN",
        "scope": "restricted_all_size_two_active_local_necessary_conditions",
        "active_order": ORDER,
        "q_values": [2] * ORDER,
        "point_sets": [list(pair) for pair in point_edges],
        "K_edges": [list(pair) for pair in sorted(k_edges)],
        "L_edges": [
            list(pair)
            for pair in sorted(VALIDATOR.all_edges(ORDER) - k_edges)
        ],
        "support_opportunity_cycle": list(support_cycle),
        "solver": {
            "python_sat": pysat.__version__,
            "solver": SOLVER_NAME,
            "base_variables": pool.top,
            "base_clauses": len(formula.clauses),
            "base_statistics": statistics,
            "support": support_metadata,
        },
        "restrictions": [
            "all_active_point_sets_have_size_2",
            "active_local_constraints_only",
            "no_99_vertex_adjacency_matrix",
            "no_global_lambda_mu_completion",
            "support_cycle_records_opportunities_not_asserted_graph_edges",
        ],
    }
    VALIDATOR.validate_size2_candidate(certificate)
    return certificate


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--compare",
        type=Path,
        help="solve afresh and compare with an archived candidate",
    )
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args(argv)
    candidate = solve()
    if arguments.compare is not None:
        archived = json.loads(arguments.compare.read_text(encoding="utf-8"))
        if candidate != archived:
            raise AssertionError("fresh SAT model differs from archived candidate")
    if arguments.json:
        print(canonical_bytes(candidate).decode("utf-8"), end="")
    else:
        checked = VALIDATOR.validate_size2_candidate(candidate)
        print("PASS pinned SAT restricted n3=42 active-local scout")
        print("base_variables", candidate["solver"]["base_variables"])
        print("base_clauses", candidate["solver"]["base_clauses"])
        print(
            "support_compatible_pairs",
            candidate["solver"]["support"]["compatible_pairs"],
        )
        print(
            "support_cycle_length",
            checked["support_opportunity_cycle_length"],
        )
        print("candidate_sha256", checked["candidate_sha256"])
        print("claim_label", checked["claim_label"])
        print("target_result", checked["target_result"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
