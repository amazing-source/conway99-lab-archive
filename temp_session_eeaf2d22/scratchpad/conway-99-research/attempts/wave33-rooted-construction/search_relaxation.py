#!/usr/bin/env python3
"""Discovery-only MILP search for an explicit Wave 33 relaxation witness.

SciPy/HiGHS is used only to locate a positive edge list.  The emitted JSON is
accepted only after the standard-library exact checker reconstructs and
checks it.  Solver failure or an absent model has no mathematical status.
"""

from __future__ import annotations

import argparse
import json
import math
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_array

import exact_check as exact


def solve_binary_equalities(
    variable_count: int,
    rows: list[dict[int, int]],
    rhs: list[int],
    time_limit: float,
    seed: int,
):
    row_indices: list[int] = []
    column_indices: list[int] = []
    values: list[int] = []
    for row_index, row in enumerate(rows):
        for column_index, value in row.items():
            if value:
                row_indices.append(row_index)
                column_indices.append(column_index)
                values.append(value)
    matrix = coo_array(
        (np.array(values, dtype=float), (
            np.array(row_indices, dtype=np.int32),
            np.array(column_indices, dtype=np.int32),
        )),
        shape=(len(rows), variable_count),
    ).tocsc()

    # This is a pure feasibility problem.  A zero objective avoids spending
    # discovery time optimizing an arbitrary tie-breaker.
    objective = np.zeros(variable_count, dtype=float)
    bounds = Bounds(np.zeros(variable_count), np.ones(variable_count))
    constraints = LinearConstraint(
        matrix,
        np.array(rhs, dtype=float),
        np.array(rhs, dtype=float),
    )
    return milp(
        c=objective,
        integrality=np.ones(variable_count, dtype=np.uint8),
        bounds=bounds,
        constraints=constraints,
        options={
            "disp": False,
            "presolve": True,
            "time_limit": time_limit,
            "mip_rel_gap": 0.0,
        },
    )


def solver_metadata(result) -> dict[str, object]:
    raw_nodes = getattr(result, "mip_node_count", None)
    raw_gap = getattr(result, "mip_gap", None)
    nodes = (
        int(raw_nodes)
        if raw_nodes is not None and math.isfinite(float(raw_nodes))
        else None
    )
    gap = (
        float(raw_gap)
        if raw_gap is not None and math.isfinite(float(raw_gap))
        else None
    )
    return {
        "status": int(result.status),
        "message": str(result.message),
        "mip_node_count": nodes,
        "mip_gap": gap,
    }


def assignment_problem(
    model: dict[str, object],
    time_limit: float,
    seed: int,
) -> tuple[list[int], dict[str, object]]:
    blocks = exact.simple_twofold_triple_design()
    size = 70

    def variable(vertex: int, block: int) -> int:
        return vertex * size + block

    rows: list[dict[int, int]] = []
    rhs: list[int] = []
    for vertex in range(size):
        rows.append({variable(vertex, block): 1 for block in range(size)})
        rhs.append(1)
    for block in range(size):
        rows.append({variable(vertex, block): 1 for vertex in range(size)})
        rhs.append(1)
    for support_group in model["support_groups"]:
        for zero in range(15):
            row = {
                variable(vertex, block_index): 1
                for vertex in support_group
                for block_index, block in enumerate(blocks)
                if zero in block
            }
            rows.append(row)
            rhs.append(2)

    result = solve_binary_equalities(size * size, rows, rhs, time_limit, seed)
    if result.x is None:
        raise RuntimeError(
            f"assignment search produced no witness: status={result.status}, "
            f"message={result.message}"
        )
    chosen = [
        max(range(size), key=lambda block: result.x[variable(vertex, block)])
        for vertex in range(size)
    ]
    if sorted(chosen) != list(range(size)):
        raise AssertionError("rounded assignment is not a permutation")
    for support_group in model["support_groups"]:
        for zero in range(15):
            count = sum(zero in blocks[chosen[vertex]] for vertex in support_group)
            if count != 2:
                raise AssertionError("rounded assignment lost support balance")
    return chosen, solver_metadata(result)


def active_graph_problem(
    model: dict[str, object],
    chosen_blocks: list[int],
    enforce_active_zero: bool,
    time_limit: float,
    seed: int,
) -> tuple[list[tuple[int, int]], dict[str, object]]:
    blocks = exact.simple_twofold_triple_design()
    pairs = list(combinations(range(70), 2))
    edge_variable = {pair: index for index, pair in enumerate(pairs)}

    def edge(left: int, right: int) -> int | None:
        if left == right:
            return None
        return edge_variable[tuple(sorted((left, right)))]

    rows: list[dict[int, int]] = []
    rhs_values: list[int] = []
    for vertex in range(70):
        rows.append({
            edge(vertex, other): 1
            for other in range(70)
            if other != vertex
        })
        rhs_values.append(9)

    support_rhs = exact.support_outside_rhs(model)
    for vertex in range(70):
        for support, group in enumerate(model["support_groups"]):
            row = {}
            for other in group:
                variable = edge(vertex, other)
                if variable is not None:
                    row[variable] = 1
            rows.append(row)
            rhs_values.append(support_rhs[support][vertex])

    if enforce_active_zero:
        assigned = [blocks[index] for index in chosen_blocks]
        for vertex in range(70):
            for zero in range(15):
                row = {}
                for other in range(70):
                    if zero in assigned[other]:
                        variable = edge(vertex, other)
                        if variable is not None:
                            row[variable] = 1
                rows.append(row)
                rhs_values.append(1 if zero in assigned[vertex] else 2)

    result = solve_binary_equalities(
        len(pairs), rows, rhs_values, time_limit, seed
    )
    if result.x is None:
        raise RuntimeError(
            f"active graph search produced no witness: status={result.status}, "
            f"message={result.message}"
        )
    chosen_edges = [
        pair for pair, value in zip(pairs, result.x)
        if value > 0.5
    ]
    chosen_set = set(chosen_edges)
    if any(
        sum(tuple(sorted((vertex, other))) in chosen_set for other in range(70)
            if other != vertex) != 9
        for vertex in range(70)
    ):
        raise AssertionError("rounded active graph lost degree nine")
    for vertex in range(70):
        for support, group in enumerate(model["support_groups"]):
            count = sum(
                tuple(sorted((vertex, other))) in chosen_set
                for other in group if other != vertex
            )
            if count != support_rhs[support][vertex]:
                raise AssertionError("rounded active graph lost support equation")
    if enforce_active_zero:
        assigned = [blocks[index] for index in chosen_blocks]
        for vertex in range(70):
            for zero in range(15):
                count = sum(
                    tuple(sorted((vertex, other))) in chosen_set
                    for other in range(70)
                    if other != vertex and zero in assigned[other]
                )
                if count != (1 if zero in assigned[vertex] else 2):
                    raise AssertionError("rounded graph lost active-zero equation")
    return chosen_edges, solver_metadata(result)


def build_certificate(
    model: dict[str, object],
    chosen_blocks: list[int],
    chosen_edges: list[tuple[int, int]],
    enforce_active_zero: bool,
    assignment_metadata: dict[str, object],
    graph_metadata: dict[str, object],
    seed: int,
) -> dict[str, object]:
    blocks = exact.simple_twofold_triple_design()
    assigned = [blocks[index] for index in chosen_blocks]
    zero_blocks = {
        f"Z{zero}": [
            model["active"][vertex]
            for vertex, block in enumerate(assigned)
            if zero in block
        ]
        for zero in range(15)
    }
    enforced = [
        "diagonal",
        "support_support",
        "support_active",
        "support_zero",
        "zero_zero",
    ]
    if enforce_active_zero:
        enforced.append("active_zero")
    return {
        "schema_version": 1,
        "claim_label": "CANDIDATE",
        "scope": (
            "FIXED_SIMPLE_2_15_3_2_ZERO_DESIGN_WITH_SUPPORT_LINEAR_GRAPH"
            + ("_AND_ACTIVE_ZERO_BLOCK" if enforce_active_zero else "")
        ),
        "active_edges": [
            [model["active"][left], model["active"][right]]
            for left, right in chosen_edges
        ],
        "zero_blocks": zero_blocks,
        "enforced_pair_categories": enforced,
        "restrictions": [
            (
                "The 70 active-to-Z neighborhoods are restricted to one "
                "explicit simple 2-(15,3,2) design; this is not without loss "
                "of generality."
            ),
            (
                "The witness enforces the support-side linear block, degrees, "
                "and the Z-Z quadratic block."
            ),
        ] + ([
            "The active-Z quadratic block is also enforced."
        ] if enforce_active_zero else []),
        "limitations": [
            "The active-active quadratic SRG block is not enforced.",
            "The frozen n3=708 projector/lattice/tensor/Schur endpoint layer is not enforced.",
            "This positive relaxation witness is not a graph extension certificate.",
            "No solver nonhit or status is used as negative evidence.",
        ],
        "discovery_solver": {
            "engine": "SciPy 1.18.0 milp with bundled HiGHS",
            "seed": seed,
            "assignment": assignment_metadata,
            "active_graph": graph_metadata,
            "status_is_certificate": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--time-limit", type=float, default=120.0)
    parser.add_argument("--seed", type=int, default=3301)
    parser.add_argument("--enforce-active-zero", action="store_true")
    args = parser.parse_args()

    model = exact.build_model()
    chosen_blocks, assignment_metadata = assignment_problem(
        model, args.time_limit, args.seed
    )
    chosen_edges, graph_metadata = active_graph_problem(
        model,
        chosen_blocks,
        args.enforce_active_zero,
        args.time_limit,
        args.seed + 1,
    )
    certificate = build_certificate(
        model,
        chosen_blocks,
        chosen_edges,
        args.enforce_active_zero,
        assignment_metadata,
        graph_metadata,
        args.seed,
    )
    # Exact standard-library verification before emitting the artifact.
    exact.verify_relaxation_certificate(certificate)
    args.output.write_bytes(exact.canonical_json(certificate))


if __name__ == "__main__":
    main()
