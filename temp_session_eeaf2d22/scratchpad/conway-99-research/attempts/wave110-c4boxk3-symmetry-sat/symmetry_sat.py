"""Symmetry-reduced bounded SAT search for the Wave 105 motif extension.

The mathematical domain is exactly the 87-vertex extension of the induced
``C4 box K3`` motif frozen by Wave 105.  The only new constraints sort
outside-adjacency rows lexicographically inside classes of vertices having
the same fixed motif-neighborhood pattern.

These are encoding-symmetry constraints, not an assumed automorphism of a
target graph.  See ``derivation.md`` for the orbit-potential proof.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import importlib.util
import json
import threading
import time
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from types import ModuleType
from typing import Callable, Iterable


PACKAGE = Path(__file__).resolve().parent
REPOSITORY = PACKAGE.parents[1]
WAVE105_SOURCE = (
    REPOSITORY
    / "attempts"
    / "wave105-c4boxk3-extension"
    / "motif_search.py"
)
OUTSIDE_VERTICES = 87
TARGET_VERTICES = 99
RAM_BUILD_FLOOR = 0.20
RAM_REQUIRED_RESERVE = 0.15


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_wave105() -> ModuleType:
    """Load the frozen discovery implementation without making it a package."""

    spec = importlib.util.spec_from_file_location("wave105_frozen", WAVE105_SOURCE)
    require(spec is not None and spec.loader is not None, "cannot load Wave 105")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def free_memory_fraction() -> float:
    """Return the Windows free-memory fraction, or 1 on another platform."""

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


def pattern_classes(
    patterns: tuple[tuple[int, ...], ...],
) -> tuple[tuple[int, ...], ...]:
    """Return fixed-pattern classes in first-occurrence order."""

    by_pattern: dict[tuple[int, ...], list[int]] = defaultdict(list)
    for vertex, pattern in enumerate(patterns):
        by_pattern[pattern].append(vertex)
    return tuple(tuple(vertices) for vertices in by_pattern.values())


def add_lex_leq(
    left: tuple[int, ...],
    right: tuple[int, ...],
    new_variable: Callable[[tuple[object, ...]], int],
    add_clause: Callable[[list[int]], None],
    key: tuple[object, ...],
) -> tuple[int, int]:
    """Encode ``left <=_lex right`` for positive Boolean variable IDs.

    Prefix variables are bi-implications, not one-way hints, so the encoding
    is logically equivalent to lexicographic nondecrease under existential
    quantification of the auxiliaries.
    """

    require(len(left) == len(right), "lex vectors have different lengths")
    require(all(value > 0 for value in left + right), "nonpositive variable ID")
    length = len(left)
    if length == 0:
        return 0, 0

    clauses = 0
    add_clause([-left[0], right[0]])
    clauses += 1
    if length == 1:
        return 0, clauses

    prefix = new_variable(("lex-prefix",) + key + (1,))
    # prefix <=> (left[0] == right[0])
    for clause in (
        [-prefix, -left[0], right[0]],
        [-prefix, left[0], -right[0]],
        [prefix, left[0], right[0]],
        [prefix, -left[0], -right[0]],
    ):
        add_clause(clause)
        clauses += 1
    auxiliaries = 1

    for position in range(1, length):
        add_clause([-prefix, -left[position], right[position]])
        clauses += 1
        if position == length - 1:
            break

        next_prefix = new_variable(
            ("lex-prefix",) + key + (position + 1,)
        )
        # next_prefix <=> prefix and (left[position] == right[position])
        for clause in (
            [-next_prefix, prefix],
            [-next_prefix, -left[position], right[position]],
            [-next_prefix, left[position], -right[position]],
            [-prefix, left[position], right[position], next_prefix],
            [-prefix, -left[position], -right[position], next_prefix],
        ):
            add_clause(clause)
            clauses += 1
        prefix = next_prefix
        auxiliaries += 1

    return auxiliaries, clauses


def symmetry_domain_audit() -> dict[str, object]:
    """Derive exact class and lex-encoding counts without invoking a solver."""

    wave105 = load_wave105()
    patterns = wave105.forced_patterns()
    classes = pattern_classes(patterns)
    multiplicity_histogram: dict[str, int] = defaultdict(int)
    comparisons = 0
    vector_positions = 0
    auxiliaries = 0
    clauses = 0
    class_rows: list[dict[str, object]] = []
    for vertices in classes:
        size = len(vertices)
        multiplicity_histogram[str(size)] += 1
        class_comparisons = max(0, size - 1)
        vector_length = OUTSIDE_VERTICES - size
        class_auxiliaries = class_comparisons * max(0, vector_length - 1)
        class_clauses = class_comparisons * (
            0
            if vector_length == 0
            else 1
            if vector_length == 1
            else 6 * vector_length - 6
        )
        comparisons += class_comparisons
        vector_positions += class_comparisons * vector_length
        auxiliaries += class_auxiliaries
        clauses += class_clauses
        class_rows.append(
            {
                "pattern": list(patterns[vertices[0]]),
                "vertices": list(vertices),
                "multiplicity": size,
                "consecutive_comparisons": class_comparisons,
                "comparison_vector_length": vector_length,
                "lex_auxiliary_variables": class_auxiliaries,
                "lex_cnf_clauses": class_clauses,
            }
        )

    require(
        dict(multiplicity_histogram) == {"3": 1, "4": 12, "2": 12, "1": 12},
        "pattern multiplicity census drift",
    )
    require(comparisons == 50, "lex comparison count drift")
    require(vector_positions == 4176, "lex vector-position count drift")
    require(auxiliaries == 4126, "lex auxiliary count drift")
    require(clauses == 24756, "lex clause count drift")
    return {
        "format": "wave110-symmetry-domain-audit-v1",
        "claim_label": "DERIVED",
        "wave105_domain": {
            "outside_vertices": OUTSIDE_VERTICES,
            "edge_variables": 3741,
            "common_conjunction_variables": 317985,
            "distinct_linear_incidence_rows": 1044,
            "outside_pair_rows": 3741,
        },
        "fixed_pattern_classes": {
            "count": len(classes),
            "multiplicity_histogram": dict(multiplicity_histogram),
            "rows": class_rows,
        },
        "lex_encoding": {
            "comparison_rule": (
                "consecutive rows within each exact motif-pattern class; "
                "columns are all vertices outside that class"
            ),
            "comparisons": comparisons,
            "compared_bit_positions": vector_positions,
            "auxiliary_variables": auxiliaries,
            "cnf_clauses": clauses,
        },
        "full_solver_submission": {
            "edge_variables": 3741,
            "common_conjunction_variables": 317985,
            "lex_auxiliary_variables": auxiliaries,
            "total_variables": 3741 + 317985 + auxiliaries,
            "conjunction_cnf_clauses": 3 * 317985,
            "lex_cnf_clauses": clauses,
            "total_cnf_clauses": 3 * 317985 + clauses,
            "exact_cardinality_rows": 1044 + 87 + 1 + 3741,
            "native_atmost_constraints": 2 * (1044 + 87 + 1 + 3741),
        },
        "branch_partition": {
            "invariant": "number of edges induced by the three X0 vertices",
            "values": [0, 1, 2, 3],
            "implementation": (
                "one exact-cardinality row over the three X0 edges; no "
                "labelled representative is fixed"
            ),
        },
    }


def solve_extension(seconds: int, edge_count_x0: int) -> dict[str, object]:
    """Run one RAM-gated, bounded, symmetry-reduced complete-domain branch."""

    require(seconds >= 1, "time limit must be positive")
    require(edge_count_x0 in range(4), "X0 edge branch must be 0,1,2,3")
    free_before = free_memory_fraction()
    require(
        free_before >= RAM_BUILD_FLOOR,
        "refusing SAT build below 20% free host memory",
    )

    from pysat.formula import IDPool
    from pysat.solvers import Solver

    wave105 = load_wave105()
    motif = wave105.motif_adjacency()
    patterns = wave105.forced_patterns()
    incidence = wave105.pattern_matrix(patterns)
    right_side = wave105.linear_right_side(incidence, motif)
    classes = pattern_classes(patterns)
    pool = IDPool()
    edge_variables = {
        pair: pool.id(("edge",) + pair)
        for pair in combinations(range(OUTSIDE_VERTICES), 2)
    }

    def edge(left: int, right: int) -> int:
        pair = (left, right) if left < right else (right, left)
        return edge_variables[pair]

    solver = Solver(name="minicard", use_timer=True)
    submitted_cnf_clauses = 0
    exact_cardinality_rows = 0

    def clause(literals: list[int]) -> None:
        nonlocal submitted_cnf_clauses
        solver.add_clause(literals)
        submitted_cnf_clauses += 1

    def exact(literals: Iterable[int], bound: int) -> None:
        nonlocal exact_cardinality_rows
        unique = list(dict.fromkeys(literals))
        require(0 <= bound <= len(unique), "invalid exact-cardinality row")
        solver.add_atmost(unique, bound)
        solver.add_atmost([-literal for literal in unique], len(unique) - bound)
        exact_cardinality_rows += 1

    seen_linear_rows: set[tuple[tuple[int, ...], int]] = set()
    for outside in range(OUTSIDE_VERTICES):
        for motif_vertex in range(12):
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

    # This invariant branch is compatible with all permutations of X0.
    exact((edge(left, right) for left, right in combinations(range(3), 2)),
          edge_count_x0)

    lex_auxiliaries = 0
    lex_clauses = 0
    lex_comparisons = 0
    for class_index, vertices in enumerate(classes):
        columns = tuple(
            vertex
            for vertex in range(OUTSIDE_VERTICES)
            if vertex not in vertices
        )
        for position in range(len(vertices) - 1):
            left_vertex = vertices[position]
            right_vertex = vertices[position + 1]
            added_auxiliaries, added_clauses = add_lex_leq(
                tuple(edge(left_vertex, column) for column in columns),
                tuple(edge(right_vertex, column) for column in columns),
                pool.id,
                clause,
                (class_index, position),
            )
            lex_auxiliaries += added_auxiliaries
            lex_clauses += added_clauses
            lex_comparisons += 1

    conjunction_variables = 0
    conjunction_clauses = 0
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
            clause([-conjunction, left_edge])
            clause([-conjunction, right_edge])
            clause([conjunction, -left_edge, -right_edge])
            conjunction_clauses += 3
            common_literals.append(conjunction)
        exact(common_literals, bound)

    audit = symmetry_domain_audit()
    expected = audit["full_solver_submission"]
    require(len(edge_variables) == expected["edge_variables"], "edge count drift")
    require(
        conjunction_variables == expected["common_conjunction_variables"],
        "conjunction count drift",
    )
    require(
        lex_auxiliaries == expected["lex_auxiliary_variables"],
        "lex auxiliary count drift",
    )
    require(lex_clauses == expected["lex_cnf_clauses"], "lex clause count drift")
    require(
        submitted_cnf_clauses == expected["total_cnf_clauses"],
        "submitted CNF clause count drift",
    )
    require(
        exact_cardinality_rows == expected["exact_cardinality_rows"],
        "cardinality row count drift",
    )
    require(pool.top == expected["total_variables"], "total variable count drift")

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
        "format": "wave110-c4boxk3-symmetry-sat-run-v1",
        "branch_eX0": edge_count_x0,
        "solver": "PySAT MiniCard 1.9.dev7",
        "time_limit_seconds": seconds,
        "elapsed_seconds": round(elapsed, 6),
        "solver_cpu_seconds": round(solver.time(), 6),
        "timed_out": timed_out["value"],
        "edge_variables": len(edge_variables),
        "common_conjunction_variables": conjunction_variables,
        "lex_auxiliary_variables": lex_auxiliaries,
        "total_variables": pool.top,
        "conjunction_cnf_clauses": conjunction_clauses,
        "lex_cnf_clauses": lex_clauses,
        "total_cnf_clauses_submitted": submitted_cnf_clauses,
        "exact_cardinality_rows": exact_cardinality_rows,
        "native_atmost_constraints_submitted": 2 * exact_cardinality_rows,
        "distinct_linear_incidence_rows": len(seen_linear_rows),
        "lex_comparisons": lex_comparisons,
        "claim_label": "UNKNOWN",
        "result": "UNKNOWN",
        "free_memory_fraction_before": free_before,
        "ram_build_floor": RAM_BUILD_FLOOR,
        "ram_required_reserve": RAM_REQUIRED_RESERVE,
    }

    if sat is True:
        positive = {literal for literal in solver.get_model() if literal > 0}
        outside = [[0] * OUTSIDE_VERTICES for _ in range(OUTSIDE_VERTICES)]
        for (left, right), variable in edge_variables.items():
            if variable in positive:
                outside[left][right] = outside[right][left] = 1
        full = [
            motif[row] + wave105.transpose(incidence)[row] for row in range(12)
        ] + [
            incidence[row] + outside[row] for row in range(OUTSIDE_VERTICES)
        ]
        wave105.verify_full_adjacency(full)
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
                    "No independently replayed proof trace accompanies UNSAT.",
                    "This remains UNKNOWN and is not a nonexistence result.",
                ],
            }
        )
    else:
        result.update(
            {
                "result": "UNKNOWN_TIMEOUT",
                "limitations": [
                    "Timeout is not evidence of satisfiability or unsatisfiability."
                ],
            }
        )

    solver.delete()
    free_after = free_memory_fraction()
    result["free_memory_fraction_after"] = free_after
    result["reserve_preserved_after_run"] = free_after >= RAM_REQUIRED_RESERVE
    require(
        free_after >= RAM_REQUIRED_RESERVE,
        "host free-memory reserve fell below 15%",
    )
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
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--solve-seconds", type=int)
    parser.add_argument("--branch-eX0", type=int, choices=range(4))
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.solve_seconds is not None:
        require(args.branch_eX0 is not None, "--branch-eX0 is required")
        result = solve_extension(args.solve_seconds, args.branch_eX0)
    else:
        result = symmetry_domain_audit()
    if args.output:
        write_json(args.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
