"""Exact C4 box K3 extension equations for the Conway-99 target.

The 12-vertex motif is the Cartesian product C4 box K3.  Its forced
outside-to-motif incidence multiset has 87 rows.  This module derives the
linear and second-moment boundary exactly and can build the complete
outside common-neighbor SAT instance without assuming a graph automorphism.

A solver timeout is recorded as UNKNOWN.  A SAT model is checked directly
against A^2 = 12I-A+2J before it is emitted.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import threading
import time
from collections import Counter
from itertools import combinations
from math import comb
from pathlib import Path
from typing import Iterable


MOTIF_VERTICES = 12
OUTSIDE_VERTICES = 87
TARGET_VERTICES = 99


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def free_memory_fraction() -> float:
    """Return the Windows free-memory fraction, or 1 outside Windows."""

    if not hasattr(ctypes, "windll"):
        return 1.0

    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("load", ctypes.c_ulong),
            ("total_physical", ctypes.c_ulonglong),
            ("available_physical", ctypes.c_ulonglong),
            ("total_page", ctypes.c_ulonglong),
            ("available_page", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("available_virtual", ctypes.c_ulonglong),
            ("available_extended", ctypes.c_ulonglong),
        ]

    status = MemoryStatus()
    status.length = ctypes.sizeof(MemoryStatus)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return status.available_physical / status.total_physical


def motif_vertices() -> tuple[tuple[int, int], ...]:
    return tuple((layer, label) for layer in range(4) for label in range(3))


def motif_adjacency() -> list[list[int]]:
    vertices = motif_vertices()
    index = {vertex: i for i, vertex in enumerate(vertices)}
    adjacency = [[0] * MOTIF_VERTICES for _ in range(MOTIF_VERTICES)]
    for left, right in combinations(vertices, 2):
        same_triangle = left[0] == right[0] and left[1] != right[1]
        cycle_matching = (
            left[1] == right[1]
            and (left[0] - right[0]) % 4 in (1, 3)
        )
        if same_triangle or cycle_matching:
            i, j = index[left], index[right]
            adjacency[i][j] = adjacency[j][i] = 1
    return adjacency


def matrix_product(
    left: list[list[int]], right: list[list[int]]
) -> list[list[int]]:
    require(len(left[0]) == len(right), "matrix dimensions do not match")
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(len(right)))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    return [list(column) for column in zip(*matrix)]


def internal_common(adjacency: list[list[int]], left: int, right: int) -> int:
    return sum(
        adjacency[left][vertex] * adjacency[right][vertex]
        for vertex in range(len(adjacency))
    )


def forced_patterns() -> tuple[tuple[int, ...], ...]:
    """Return the forced 87-row outside-to-motif incidence multiset."""

    adjacency = motif_adjacency()
    patterns: list[tuple[int, ...]] = [()] * 3
    for vertex in range(MOTIF_VERTICES):
        patterns.extend([(vertex,)] * 4)
    for left, right in combinations(range(MOTIF_VERTICES), 2):
        target = 1 if adjacency[left][right] else 2
        multiplicity = target - internal_common(adjacency, left, right)
        require(multiplicity >= 0, "motif already exceeds a target codegree")
        patterns.extend([(left, right)] * multiplicity)

    require(len(patterns) == OUTSIDE_VERTICES, "outside pattern count drift")
    require(
        Counter(map(len, patterns)) == {0: 3, 1: 48, 2: 36},
        "outside type histogram drift",
    )
    return tuple(patterns)


def pattern_matrix(patterns: tuple[tuple[int, ...], ...]) -> list[list[int]]:
    matrix = [[0] * MOTIF_VERTICES for _ in patterns]
    for row, pattern in enumerate(patterns):
        for column in pattern:
            matrix[row][column] = 1
    return matrix


def expected_pattern_gram(adjacency: list[list[int]]) -> list[list[int]]:
    square = matrix_product(adjacency, adjacency)
    return [
        [
            12 * int(i == j)
            - adjacency[i][j]
            + 2
            - square[i][j]
            for j in range(MOTIF_VERTICES)
        ]
        for i in range(MOTIF_VERTICES)
    ]


def linear_right_side(
    incidence: list[list[int]], adjacency: list[list[int]]
) -> list[list[int]]:
    product = matrix_product(incidence, adjacency)
    return [
        [
            2 - incidence[row][column] - product[row][column]
            for column in range(MOTIF_VERTICES)
        ]
        for row in range(OUTSIDE_VERTICES)
    ]


def compositions(total: int, parts: int) -> Iterable[tuple[int, ...]]:
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for remainder in compositions(total - first, parts - 1):
            yield (first,) + remainder


def degree_profile(vertex_type: int, x2_neighbors: int) -> tuple[int, int, int]:
    """Return outside neighbor counts in X0, X1, X2."""

    return (
        x2_neighbors + 4 * vertex_type - 10,
        24 - 5 * vertex_type - 2 * x2_neighbors,
        x2_neighbors,
    )


def moment_vector(profile: tuple[int, int, int]) -> tuple[int, ...]:
    a, b, c = profile
    return (
        comb(a, 2),
        a * b,
        a * c,
        comb(b, 2),
        b * c,
        comb(c, 2),
    )


def erdos_gallai(sequence: Iterable[int]) -> bool:
    degrees = sorted(sequence, reverse=True)
    order = len(degrees)
    if any(degree < 0 or degree >= order for degree in degrees):
        return False
    if sum(degrees) % 2:
        return False
    prefixes = [0]
    for degree in degrees:
        prefixes.append(prefixes[-1] + degree)
    return all(
        prefixes[k]
        <= k * (k - 1) + sum(min(degree, k) for degree in degrees[k:])
        for k in range(1, order + 1)
    )


def gale_ryser(left: Iterable[int], right: Iterable[int]) -> bool:
    left_degrees = sorted(left, reverse=True)
    right_degrees = sorted(right, reverse=True)
    if sum(left_degrees) != sum(right_degrees):
        return False
    if any(
        degree < 0 or degree > len(right_degrees) for degree in left_degrees
    ):
        return False
    if any(
        degree < 0 or degree > len(left_degrees) for degree in right_degrees
    ):
        return False
    return all(
        sum(left_degrees[:k])
        <= sum(min(degree, k) for degree in right_degrees)
        for k in range(1, len(left_degrees) + 1)
    )


def x0_degrees(edge_count: int) -> tuple[int, int, int]:
    rows = {
        0: (0, 0, 0),
        1: (1, 1, 0),
        2: (2, 1, 1),
        3: (2, 2, 2),
    }
    return rows[edge_count]


def type_edge_counts(edge_count_x0: int) -> dict[str, int]:
    t = edge_count_x0
    return {
        "00": t,
        "01": 12 - 4 * t,
        "02": 30 + 2 * t,
        "11": 156 + 4 * t,
        "12": 300 - 4 * t,
        "22": 51 + t,
    }


def moment_targets(edge_count_x0: int) -> tuple[int, ...]:
    t = edge_count_x0
    return (
        6 - t,
        276 + 4 * t,
        186 - 2 * t,
        2028 - 4 * t,
        2868 + 4 * t,
        1029 - t,
    )


def degree_histogram_rows(edge_count_x0: int) -> list[dict[str, object]]:
    """Enumerate all aggregate outside degree-moment rows."""

    t = edge_count_x0
    edges = type_edge_counts(t)
    profiles0 = [
        degree_profile(0, degree + 10) for degree in x0_degrees(t)
    ]
    profiles1 = [degree_profile(1, value) for value in range(6, 10)]
    profiles2 = [degree_profile(2, value) for value in range(2, 6)]

    histograms1 = [
        row
        for row in compositions(48, len(profiles1))
        if sum(count * profile[2] for count, profile in zip(row, profiles1))
        == edges["12"]
    ]
    histograms2 = [
        row
        for row in compositions(36, len(profiles2))
        if sum(count * profile[2] for count, profile in zip(row, profiles2))
        == 2 * edges["22"]
    ]

    target = moment_targets(t)
    records: list[dict[str, object]] = []
    for histogram1 in histograms1:
        expanded1 = [
            profile
            for count, profile in zip(histogram1, profiles1)
            for _ in range(count)
        ]
        for histogram2 in histograms2:
            expanded2 = [
                profile
                for count, profile in zip(histogram2, profiles2)
                for _ in range(count)
            ]
            all_profiles = profiles0 + expanded1 + expanded2
            observed = tuple(
                sum(moment_vector(profile)[index] for profile in all_profiles)
                for index in range(6)
            )
            if observed != target:
                continue

            graphical = (
                erdos_gallai(profile[0] for profile in profiles0),
                gale_ryser(
                    (profile[1] for profile in profiles0),
                    (profile[0] for profile in expanded1),
                ),
                gale_ryser(
                    (profile[2] for profile in profiles0),
                    (profile[0] for profile in expanded2),
                ),
                erdos_gallai(profile[1] for profile in expanded1),
                gale_ryser(
                    (profile[2] for profile in expanded1),
                    (profile[1] for profile in expanded2),
                ),
                erdos_gallai(profile[2] for profile in expanded2),
            )
            records.append(
                {
                    "x1_x2_neighbor_histogram": list(histogram1),
                    "x2_x2_neighbor_histogram": list(histogram2),
                    "six_type_graphical_tests": list(graphical),
                    "all_six_type_graphical": all(graphical),
                }
            )
    return records


def necessary_summary() -> dict[str, object]:
    adjacency = motif_adjacency()
    patterns = forced_patterns()
    incidence = pattern_matrix(patterns)
    gram = matrix_product(transpose(incidence), incidence)
    require(
        gram == expected_pattern_gram(adjacency),
        "forced pattern Gram matrix drift",
    )

    per_type_edges = {
        str(t): type_edge_counts(t) for t in range(4)
    }
    rows_by_t = {
        str(t): degree_histogram_rows(t) for t in range(4)
    }
    counts = {key: len(rows) for key, rows in rows_by_t.items()}
    graphical_counts = {
        key: sum(bool(row["all_six_type_graphical"]) for row in rows)
        for key, rows in rows_by_t.items()
    }
    require(counts == {"0": 18, "1": 11, "2": 5, "3": 1}, "moment census drift")
    require(
        graphical_counts == {"0": 18, "1": 11, "2": 4, "3": 1},
        "graphical census drift",
    )

    return {
        "format": "wave105-c4boxk3-extension-v1",
        "claim_label": "DERIVED",
        "motif": {
            "name": "C4 box K3",
            "vertices": 12,
            "edges": sum(map(sum, adjacency)) // 2,
            "internal_degree": sorted(set(map(sum, adjacency))),
        },
        "forced_outside_incidence": {
            "type_counts": {"X0": 3, "X1": 48, "X2": 36},
            "incidences": sum(map(len, patterns)),
            "pair_incidences": sum(comb(len(pattern), 2) for pattern in patterns),
            "pattern_gram_matches_block_equation": True,
            "linear_block_equation": "D*P=2J-P-P*H",
        },
        "outside_edges": {
            "total": 549,
            "type_counts_by_t_eX0": per_type_edges,
        },
        "outside_degree_moments": {
            "targets_order": ["00", "01", "02", "11", "12", "22"],
            "moment_row_counts_by_t": counts,
            "six_type_graphical_counts_by_t": graphical_counts,
            "rows_by_t": rows_by_t,
        },
        "status_wall": {
            "linear_extension": "FEASIBLE",
            "full_common_neighbor_extension": "UNKNOWN",
            "motif_excluded": False,
            "Conway_99": "UNKNOWN",
        },
    }


def verify_full_adjacency(adjacency: list[list[int]]) -> None:
    require(len(adjacency) == TARGET_VERTICES, "adjacency order is not 99")
    require(
        all(len(row) == TARGET_VERTICES for row in adjacency),
        "adjacency is not square",
    )
    for i in range(TARGET_VERTICES):
        require(adjacency[i][i] == 0, "adjacency diagonal is nonzero")
        require(sum(adjacency[i]) == 14, "adjacency row sum is not 14")
        for j in range(TARGET_VERTICES):
            require(adjacency[i][j] in (0, 1), "adjacency is not binary")
            require(adjacency[i][j] == adjacency[j][i], "adjacency is asymmetric")
    square = matrix_product(adjacency, adjacency)
    target = [
        [
            12 * int(i == j) - adjacency[i][j] + 2
            for j in range(TARGET_VERTICES)
        ]
        for i in range(TARGET_VERTICES)
    ]
    require(square == target, "adjacency fails the SRG matrix equation")


def canonical_x0_edges(edge_count: int) -> set[tuple[int, int]]:
    rows = {
        0: set(),
        1: {(0, 1)},
        2: {(0, 1), (1, 2)},
        3: {(0, 1), (0, 2), (1, 2)},
    }
    return rows[edge_count]


def verify_linear_outside(outside: list[list[int]]) -> None:
    """Check the complete linear block and degree equations."""

    require(len(outside) == OUTSIDE_VERTICES, "outside order is not 87")
    require(
        all(len(row) == OUTSIDE_VERTICES for row in outside),
        "outside adjacency is not square",
    )
    patterns = forced_patterns()
    incidence = pattern_matrix(patterns)
    right_side = linear_right_side(incidence, motif_adjacency())
    for row in range(OUTSIDE_VERTICES):
        require(outside[row][row] == 0, "outside diagonal is nonzero")
        require(
            sum(outside[row]) == 14 - len(patterns[row]),
            "outside degree equation fails",
        )
        for column in range(OUTSIDE_VERTICES):
            require(outside[row][column] in (0, 1), "outside matrix is not binary")
            require(
                outside[row][column] == outside[column][row],
                "outside matrix is asymmetric",
            )
    observed = matrix_product(outside, incidence)
    require(observed == right_side, "outside matrix fails D*P=2J-P-P*H")


def linear_extension_witness(edge_count_x0: int = 0) -> dict[str, object]:
    """Construct and directly check one vertex-level linear skeleton."""

    require(edge_count_x0 in range(4), "X0 edge branch must be 0,1,2,3")
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, milp
    from scipy.sparse import coo_array

    patterns = forced_patterns()
    incidence = pattern_matrix(patterns)
    right_side = linear_right_side(incidence, motif_adjacency())
    edge_pairs = tuple(combinations(range(OUTSIDE_VERTICES), 2))
    edge_variables = {
        pair: index for index, pair in enumerate(edge_pairs)
    }

    def edge(left: int, right: int) -> int:
        pair = (left, right) if left < right else (right, left)
        return edge_variables[pair]

    constraint_rows: list[tuple[tuple[int, ...], int]] = []

    def exact(indices: Iterable[int], bound: int) -> None:
        unique = tuple(dict.fromkeys(indices))
        require(0 <= bound <= len(unique), "invalid exact-cardinality row")
        constraint_rows.append((unique, bound))

    seen: set[tuple[tuple[int, ...], int]] = set()
    for outside in range(OUTSIDE_VERTICES):
        for motif_vertex in range(MOTIF_VERTICES):
            indices = tuple(
                sorted(
                    edge(outside, other)
                    for other in range(OUTSIDE_VERTICES)
                    if other != outside and incidence[other][motif_vertex]
                )
            )
            row = (indices, right_side[outside][motif_vertex])
            if row not in seen:
                exact(*row)
                seen.add(row)
    for outside in range(OUTSIDE_VERTICES):
        exact(
            (
                edge(outside, other)
                for other in range(OUTSIDE_VERTICES)
                if other != outside
            ),
            14 - len(patterns[outside]),
        )
    canonical = canonical_x0_edges(edge_count_x0)
    for left, right in combinations(range(3), 2):
        exact([edge(left, right)], int((left, right) in canonical))

    matrix_rows: list[int] = []
    matrix_columns: list[int] = []
    matrix_values: list[int] = []
    bounds: list[int] = []
    for row_index, (indices, bound) in enumerate(constraint_rows):
        matrix_rows.extend([row_index] * len(indices))
        matrix_columns.extend(indices)
        matrix_values.extend([1] * len(indices))
        bounds.append(bound)
    matrix = coo_array(
        (matrix_values, (matrix_rows, matrix_columns)),
        shape=(len(constraint_rows), len(edge_pairs)),
        dtype=np.float64,
    ).tocsr()
    result = milp(
        c=np.zeros(len(edge_pairs)),
        integrality=np.ones(len(edge_pairs)),
        bounds=Bounds(0, 1),
        constraints=LinearConstraint(matrix, bounds, bounds),
        options={"presolve": True},
    )
    require(result.success and result.x is not None, "linear MILP has no witness")
    selected = {
        index for index, value in enumerate(result.x) if round(float(value)) == 1
    }
    outside = [[0] * OUTSIDE_VERTICES for _ in range(OUTSIDE_VERTICES)]
    for (left, right), variable in edge_variables.items():
        if variable in selected:
            outside[left][right] = outside[right][left] = 1
    verify_linear_outside(outside)
    upper_bits = "".join(
        str(outside[left][right])
        for left in range(OUTSIDE_VERTICES)
        for right in range(left + 1, OUTSIDE_VERTICES)
    )
    return {
        "format": "wave105-linear-extension-witness-v1",
        "claim_label": "CANDIDATE",
        "branch_eX0": edge_count_x0,
        "solver": "SciPy milp / HiGHS",
        "solver_status": int(result.status),
        "constraint_rows": len(constraint_rows),
        "outside_edges": sum(map(sum, outside)) // 2,
        "direct_linear_check": True,
        "upper_triangle_sha256": hashlib.sha256(
            upper_bits.encode("ascii")
        ).hexdigest(),
        "adjacency_lists": [
            [column for column, value in enumerate(row) if value]
            for row in outside
        ],
        "limitations": [
            "This witness satisfies only degrees and D*P=2J-P-P*H.",
            "It does not satisfy or test the outside pair common-neighbor equations.",
        ],
    }


def solve_extension(seconds: int, edge_count_x0: int) -> dict[str, object]:
    """Run a bounded, complete-domain solve for one encoding-symmetry branch."""

    require(seconds >= 1, "time limit must be positive")
    require(edge_count_x0 in range(4), "X0 edge branch must be 0,1,2,3")
    free_before = free_memory_fraction()
    require(free_before >= 0.20, "refusing SAT build below 20% free memory")

    from pysat.formula import IDPool
    from pysat.solvers import Solver

    motif = motif_adjacency()
    patterns = forced_patterns()
    incidence = pattern_matrix(patterns)
    right_side = linear_right_side(incidence, motif)
    pool = IDPool()
    edge_variables = {
        pair: pool.id(("edge",) + pair)
        for pair in combinations(range(OUTSIDE_VERTICES), 2)
    }

    def edge(left: int, right: int) -> int:
        pair = (left, right) if left < right else (right, left)
        return edge_variables[pair]

    solver = Solver(name="minicard", use_timer=True)

    def exact(literals: Iterable[int], bound: int) -> None:
        unique = list(dict.fromkeys(literals))
        require(0 <= bound <= len(unique), "invalid exact-cardinality row")
        solver.add_atmost(unique, bound)
        solver.add_atmost([-literal for literal in unique], len(unique) - bound)

    seen_linear_rows: set[tuple[tuple[int, ...], int]] = set()
    for outside in range(OUTSIDE_VERTICES):
        for motif_vertex in range(MOTIF_VERTICES):
            literals = tuple(
                sorted(
                    edge(outside, other)
                    for other in range(OUTSIDE_VERTICES)
                    if other != outside and incidence[other][motif_vertex]
                )
            )
            row = (literals, right_side[outside][motif_vertex])
            if row not in seen_linear_rows:
                exact(*row)
                seen_linear_rows.add(row)

    for outside in range(OUTSIDE_VERTICES):
        exact(
            (
                edge(outside, other)
                for other in range(OUTSIDE_VERTICES)
                if other != outside
            ),
            14 - len(patterns[outside]),
        )

    canonical = canonical_x0_edges(edge_count_x0)
    for left, right in combinations(range(3), 2):
        literal = edge(left, right)
        solver.add_clause([literal if (left, right) in canonical else -literal])

    conjunction_variables = 0
    for left, right in combinations(range(OUTSIDE_VERTICES), 2):
        overlap = len(set(patterns[left]) & set(patterns[right]))
        bound = 2 - overlap
        common_literals = [edge(left, right)]
        for center in range(OUTSIDE_VERTICES):
            if center in (left, right):
                continue
            left_edge = edge(left, center)
            right_edge = edge(right, center)
            conjunction = pool.id(("common", left, right, center))
            conjunction_variables += 1
            solver.add_clause([-conjunction, left_edge])
            solver.add_clause([-conjunction, right_edge])
            solver.add_clause([conjunction, -left_edge, -right_edge])
            common_literals.append(conjunction)
        exact(common_literals, bound)

    timed_out = {"value": False}

    def interrupt() -> None:
        timed_out["value"] = True
        solver.interrupt()

    timer = threading.Timer(float(seconds), interrupt)
    started = time.time()
    timer.start()
    try:
        sat = solver.solve_limited(expect_interrupt=True)
    finally:
        timer.cancel()
    elapsed = time.time() - started

    result: dict[str, object] = {
        "format": "wave105-c4boxk3-extension-run-v1",
        "branch_eX0": edge_count_x0,
        "solver": "PySAT MiniCard 1.9.dev7",
        "time_limit_seconds": seconds,
        "elapsed_seconds": round(elapsed, 6),
        "solver_cpu_seconds": round(solver.time(), 6),
        "timed_out": timed_out["value"],
        "edge_variables": len(edge_variables),
        "common_conjunction_variables": conjunction_variables,
        "total_variables": pool.top,
        "distinct_linear_incidence_rows": len(seen_linear_rows),
        "claim_label": "UNKNOWN",
        "result": "UNKNOWN",
        "free_memory_fraction_before": free_before,
    }

    if sat is True:
        positive = {literal for literal in solver.get_model() if literal > 0}
        outside = [[0] * OUTSIDE_VERTICES for _ in range(OUTSIDE_VERTICES)]
        for (left, right), variable in edge_variables.items():
            if variable in positive:
                outside[left][right] = outside[right][left] = 1
        full = [
            motif[row] + transpose(incidence)[row]
            for row in range(MOTIF_VERTICES)
        ] + [
            incidence[row] + outside[row] for row in range(OUTSIDE_VERTICES)
        ]
        verify_full_adjacency(full)
        upper_bits = "".join(
            str(full[left][right])
            for left in range(TARGET_VERTICES)
            for right in range(left + 1, TARGET_VERTICES)
        )
        result.update(
            {
                "claim_label": "CANDIDATE",
                "result": "SAT_CHECKED",
                "adjacency_lists": [
                    [column for column, value in enumerate(row) if value]
                    for row in full
                ],
                "upper_triangle_sha256": hashlib.sha256(
                    upper_bits.encode("ascii")
                ).hexdigest(),
                "direct_srg_matrix_check": True,
            }
        )
    elif sat is False:
        result.update(
            {
                "result": "UNSAT_WITHOUT_EXTERNAL_CERTIFICATE",
                "limitations": [
                    "The solver conclusion has no independently replayed proof trace.",
                    "Do not promote this run to a mathematical nonexistence result.",
                ],
            }
        )
    else:
        result.update(
            {
                "result": "UNKNOWN_TIMEOUT",
                "limitations": [
                    "A timeout is not evidence of satisfiability or unsatisfiability."
                ],
            }
        )

    solver.delete()
    result["free_memory_fraction_after"] = free_memory_fraction()
    return result


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--linear-witness", action="store_true")
    parser.add_argument("--solve-seconds", type=int)
    parser.add_argument("--branch-eX0", type=int, choices=range(4))
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.solve_seconds is not None:
        require(args.branch_eX0 is not None, "--branch-eX0 is required")
        result = solve_extension(args.solve_seconds, args.branch_eX0)
    elif args.linear_witness:
        result = linear_extension_witness(args.branch_eX0 or 0)
    else:
        result = necessary_summary()
    if args.output:
        write_json(args.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
