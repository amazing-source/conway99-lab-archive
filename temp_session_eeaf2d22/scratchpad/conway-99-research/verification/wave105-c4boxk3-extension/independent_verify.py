"""Independent verifier for the Wave 105 C4 box K3 extension package.

This module does not import discovery code.  It reconstructs the motif,
incidence multiset, block equations, moment census, graphicality filters,
linear witness checks, and the logical coverage of the bounded SAT encoding.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Iterator, Sequence


ROOT = Path(__file__).resolve().parents[2]
DISCOVERY = ROOT / "attempts" / "wave105-c4boxk3-extension"
VERIFIER_RAW_LOGS = Path(__file__).with_name("raw-logs")
EXPECTED_DISCOVERY_MANIFEST = (
    "b0fd40eda5a3677d4a835788cea20dfcb9bb3c5764719fc04536893f1b5da4a1"
)
N_MOTIF = 12
N_OUTSIDE = 87


def demand(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_hash_list(path: Path) -> list[dict[str, str]]:
    checked: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        expected, separator, relative = line.partition("  ")
        demand(
            separator == "  " and len(expected) == 64,
            f"malformed hash line in {path}: {line!r}",
        )
        target = ROOT / relative
        demand(target.is_file(), f"frozen input missing: {relative}")
        observed = sha256_file(target)
        demand(observed == expected, f"frozen input hash mismatch: {relative}")
        checked.append({"path": relative, "sha256": observed})
    return checked


def validate_discovery_manifest() -> list[dict[str, str]]:
    manifest = DISCOVERY / "package-manifest.sha256"
    demand(
        sha256_file(manifest) == EXPECTED_DISCOVERY_MANIFEST,
        "discovery package manifest changed after assignment",
    )
    checked = validate_hash_list(manifest)
    demand(len(checked) == 11, "unexpected discovery manifest entry count")
    return checked


def motif_graph() -> tuple[tuple[int, ...], ...]:
    """Return C4 Cartesian K3 using vertices (cycle position, triangle label)."""

    neighbors: list[set[int]] = [set() for _ in range(N_MOTIF)]
    for left, right in itertools.combinations(range(N_MOTIF), 2):
        layer_l, label_l = divmod(left, 3)
        layer_r, label_r = divmod(right, 3)
        triangle_edge = layer_l == layer_r and label_l != label_r
        cycle_edge = (
            label_l == label_r and (layer_l - layer_r) % 4 in {1, 3}
        )
        if triangle_edge or cycle_edge:
            neighbors[left].add(right)
            neighbors[right].add(left)
    return tuple(tuple(sorted(row)) for row in neighbors)


def adjacent(graph: Sequence[Sequence[int]], left: int, right: int) -> int:
    return int(right in graph[left])


def common_count(
    graph: Sequence[Sequence[int]], left: int, right: int
) -> int:
    return len(set(graph[left]).intersection(graph[right]))


def residual_pair_capacities(
    motif: Sequence[Sequence[int]],
) -> dict[tuple[int, int], int]:
    residual: dict[tuple[int, int], int] = {}
    for left, right in itertools.combinations(range(N_MOTIF), 2):
        target = 1 if adjacent(motif, left, right) else 2
        capacity = target - common_count(motif, left, right)
        demand(capacity >= 0, "motif already exceeds an SRG pair codegree")
        residual[(left, right)] = capacity
    return residual


def residual_support_is_triangle_free(
    residual: dict[tuple[int, int], int]
) -> bool:
    def positive(left: int, right: int) -> bool:
        pair = (left, right) if left < right else (right, left)
        return residual[pair] > 0

    return not any(
        positive(a, b) and positive(a, c) and positive(b, c)
        for a, b, c in itertools.combinations(range(N_MOTIF), 3)
    )


def derive_outside_patterns() -> tuple[tuple[int, ...], ...]:
    """Derive the unique incidence-row multiset, in discovery archive order."""

    motif = motif_graph()
    residual = residual_pair_capacities(motif)
    demand(
        residual_support_is_triangle_free(residual),
        "positive residual-pair support unexpectedly has a triangle",
    )

    # Any outside motif-neighborhood of size at least three would give a
    # triangle in the positive residual-pair support.  Hence every row has
    # weight at most two and the residual pair multiplicities fix all X2 rows.
    pair_rows = [
        pair
        for pair in itertools.combinations(range(N_MOTIF), 2)
        for _ in range(residual[pair])
    ]
    demand(len(pair_rows) == 36, "residual pair-incidence total drift")

    appearances = Counter(vertex for pair in pair_rows for vertex in pair)
    singleton_counts = {vertex: 10 - appearances[vertex] for vertex in range(12)}
    demand(
        set(singleton_counts.values()) == {4},
        "motif-column residual degree does not force four singleton rows",
    )
    singleton_rows = [
        (vertex,)
        for vertex in range(N_MOTIF)
        for _ in range(singleton_counts[vertex])
    ]

    used = len(pair_rows) + len(singleton_rows)
    empty_rows = [()] * (N_OUTSIDE - used)
    demand(len(empty_rows) == 3, "empty-row count drift")
    patterns = tuple(empty_rows + singleton_rows + pair_rows)
    demand(
        Counter(map(len, patterns)) == {0: 3, 1: 48, 2: 36},
        "outside incidence histogram drift",
    )
    return patterns


def incidence_matrix(
    patterns: Sequence[Sequence[int]],
) -> list[list[int]]:
    return [
        [int(column in pattern) for column in range(N_MOTIF)]
        for pattern in patterns
    ]


def adjacency_matrix(graph: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [int(column in graph[row]) for column in range(len(graph))]
        for row in range(len(graph))
    ]


def multiply(left: Sequence[Sequence[int]], right: Sequence[Sequence[int]]) -> list[list[int]]:
    demand(len(left[0]) == len(right), "matrix shape mismatch")
    return [
        [
            sum(left[row][middle] * right[middle][column] for middle in range(len(right)))
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def transpose(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [list(column) for column in zip(*matrix)]


def linear_rhs(
    incidence: Sequence[Sequence[int]], motif_matrix: Sequence[Sequence[int]]
) -> list[list[int]]:
    product = multiply(incidence, motif_matrix)
    return [
        [
            2 - incidence[row][column] - product[row][column]
            for column in range(N_MOTIF)
        ]
        for row in range(N_OUTSIDE)
    ]


def check_top_left_block(
    motif_matrix: Sequence[Sequence[int]],
    incidence: Sequence[Sequence[int]],
) -> bool:
    h2 = multiply(motif_matrix, motif_matrix)
    ptp = multiply(transpose(incidence), incidence)
    return all(
        h2[i][j] + ptp[i][j]
        == 12 * int(i == j) - motif_matrix[i][j] + 2
        for i in range(N_MOTIF)
        for j in range(N_MOTIF)
    )


def canonical_x0(edge_count: int) -> set[tuple[int, int]]:
    return {
        0: set(),
        1: {(0, 1)},
        2: {(0, 1), (1, 2)},
        3: {(0, 1), (0, 2), (1, 2)},
    }[edge_count]


def x0_degrees(edge_count: int) -> tuple[int, int, int]:
    edges = canonical_x0(edge_count)
    return tuple(
        sum(vertex in pair for pair in edges) for vertex in range(3)
    )


def outside_profile(vertex_type: int, x2_degree: int) -> tuple[int, int, int]:
    """Derive (X0,X1,X2) neighbor counts from degree and DP row sums."""

    # Total outside degree is 14-i.  Summing DP across the 12 motif columns
    # gives n1+2*n2 = 24-5*i because H is 4-regular.
    n2 = x2_degree
    n1 = 24 - 5 * vertex_type - 2 * n2
    n0 = 14 - vertex_type - n1 - n2
    return n0, n1, n2


def type_edge_counts(edge_count_x0: int) -> dict[str, int]:
    t = edge_count_x0
    e00 = t
    e01 = sum(outside_profile(0, degree + 10)[1] for degree in x0_degrees(t))
    e02 = sum(outside_profile(0, degree + 10)[2] for degree in x0_degrees(t))

    # For X1, n0=c-6.  Summing n0=e01 fixes sum(c)=e12.
    e12 = e01 + 6 * 48
    e11 = (19 * 48 - 2 * e12) // 2

    # For X2, n0=c-2.  Summing n0=e02 fixes 2e22=sum(c).
    e22 = (e02 + 2 * 36) // 2
    demand(14 * 36 - 4 * e22 == e12, "X2-X1 edge sum inconsistent")
    return {
        "00": e00,
        "01": e01,
        "02": e02,
        "11": e11,
        "12": e12,
        "22": e22,
    }


PAIR_KEYS = ("00", "01", "02", "11", "12", "22")


def moment_targets(
    patterns: Sequence[Sequence[int]], edge_count_x0: int
) -> tuple[int, ...]:
    classes = tuple(len(pattern) for pattern in patterns)
    edge_counts = type_edge_counts(edge_count_x0)
    targets: list[int] = []
    for key in PAIR_KEYS:
        left_type, right_type = map(int, key)
        if left_type == right_type:
            pairs = (
                (left, right)
                for left, right in itertools.combinations(range(N_OUTSIDE), 2)
                if classes[left] == left_type and classes[right] == right_type
            )
        else:
            pairs = (
                (left, right)
                for left in range(N_OUTSIDE)
                for right in range(N_OUTSIDE)
                if classes[left] == left_type and classes[right] == right_type
            )
        total = sum(
            2 - len(set(patterns[left]).intersection(patterns[right]))
            for left, right in pairs
        )
        targets.append(total - edge_counts[key])
    return tuple(targets)


def neighbor_pair_moments(profile: tuple[int, int, int]) -> tuple[int, ...]:
    a, b, c = profile
    return (
        a * (a - 1) // 2,
        a * b,
        a * c,
        b * (b - 1) // 2,
        b * c,
        c * (c - 1) // 2,
    )


def compositions4(total: int) -> Iterator[tuple[int, int, int, int]]:
    for first in range(total + 1):
        for second in range(total - first + 1):
            for third in range(total - first - second + 1):
                yield first, second, third, total - first - second - third


def erdos_gallai(sequence: Iterable[int]) -> bool:
    degrees = sorted(sequence, reverse=True)
    order = len(degrees)
    if any(degree < 0 or degree >= order for degree in degrees):
        return False
    if sum(degrees) % 2:
        return False
    return all(
        sum(degrees[:k])
        <= k * (k - 1) + sum(min(degree, k) for degree in degrees[k:])
        for k in range(1, order + 1)
    )


def gale_ryser(left: Iterable[int], right: Iterable[int]) -> bool:
    rows = sorted(left, reverse=True)
    columns = sorted(right, reverse=True)
    if sum(rows) != sum(columns):
        return False
    if any(degree < 0 or degree > len(columns) for degree in rows):
        return False
    if any(degree < 0 or degree > len(rows) for degree in columns):
        return False
    return all(
        sum(rows[:k]) <= sum(min(k, degree) for degree in columns)
        for k in range(1, len(rows) + 1)
    )


def moment_census(
    patterns: Sequence[Sequence[int]], edge_count_x0: int
) -> list[dict[str, object]]:
    edges = type_edge_counts(edge_count_x0)
    profiles0 = [
        outside_profile(0, degree + 10)
        for degree in x0_degrees(edge_count_x0)
    ]
    candidates1 = [outside_profile(1, c) for c in range(6, 10)]
    candidates2 = [outside_profile(2, c) for c in range(2, 6)]
    histograms1 = [
        histogram
        for histogram in compositions4(48)
        if sum(count * profile[2] for count, profile in zip(histogram, candidates1))
        == edges["12"]
    ]
    histograms2 = [
        histogram
        for histogram in compositions4(36)
        if sum(count * profile[2] for count, profile in zip(histogram, candidates2))
        == 2 * edges["22"]
    ]
    target = moment_targets(patterns, edge_count_x0)
    records: list[dict[str, object]] = []
    for histogram1 in histograms1:
        profiles1 = [
            profile
            for count, profile in zip(histogram1, candidates1)
            for _ in range(count)
        ]
        for histogram2 in histograms2:
            profiles2 = [
                profile
                for count, profile in zip(histogram2, candidates2)
                for _ in range(count)
            ]
            profiles = profiles0 + profiles1 + profiles2
            observed = tuple(
                sum(neighbor_pair_moments(profile)[index] for profile in profiles)
                for index in range(6)
            )
            if observed != target:
                continue
            checks = (
                erdos_gallai(profile[0] for profile in profiles0),
                gale_ryser(
                    (profile[1] for profile in profiles0),
                    (profile[0] for profile in profiles1),
                ),
                gale_ryser(
                    (profile[2] for profile in profiles0),
                    (profile[0] for profile in profiles2),
                ),
                erdos_gallai(profile[1] for profile in profiles1),
                gale_ryser(
                    (profile[2] for profile in profiles1),
                    (profile[1] for profile in profiles2),
                ),
                erdos_gallai(profile[2] for profile in profiles2),
            )
            records.append(
                {
                    "x1_x2_neighbor_histogram": list(histogram1),
                    "x2_x2_neighbor_histogram": list(histogram2),
                    "six_type_graphical_tests": list(checks),
                    "all_six_type_graphical": all(checks),
                }
            )
    return records


def decode_outside_witness(payload: dict[str, object]) -> list[list[int]]:
    rows = payload["adjacency_lists"]
    demand(isinstance(rows, list) and len(rows) == N_OUTSIDE, "witness order drift")
    outside = [[0] * N_OUTSIDE for _ in range(N_OUTSIDE)]
    for row, neighbors_object in enumerate(rows):
        demand(isinstance(neighbors_object, list), "malformed adjacency row")
        neighbors = [int(value) for value in neighbors_object]
        demand(len(neighbors) == len(set(neighbors)), "duplicate adjacency entry")
        for column in neighbors:
            demand(0 <= column < N_OUTSIDE and column != row, "invalid neighbor")
            outside[row][column] = 1
    demand(
        all(outside[i][j] == outside[j][i] for i in range(87) for j in range(87)),
        "outside witness is asymmetric",
    )
    return outside


def verify_linear_witness(
    patterns: Sequence[Sequence[int]],
    motif_matrix: Sequence[Sequence[int]],
) -> dict[str, object]:
    payload_object = load_json(DISCOVERY / "linear-witness.json")
    demand(isinstance(payload_object, dict), "linear witness is not an object")
    payload = payload_object
    outside = decode_outside_witness(payload)
    incidence = incidence_matrix(patterns)
    rhs = linear_rhs(incidence, motif_matrix)

    degrees = [sum(row) for row in outside]
    demand(
        degrees == [14 - len(pattern) for pattern in patterns],
        "linear witness outside-degree row failed",
    )
    observed = multiply(outside, incidence)
    demand(observed == rhs, "linear witness failed DP=2J-P-PH")
    edge_count = sum(degrees) // 2
    demand(edge_count == 549, "linear witness edge total drift")

    upper_bits = "".join(
        str(outside[left][right])
        for left, right in itertools.combinations(range(N_OUTSIDE), 2)
    )
    upper_hash = hashlib.sha256(upper_bits.encode("ascii")).hexdigest()
    demand(
        upper_hash == payload["upper_triangle_sha256"],
        "linear witness upper-triangle hash mismatch",
    )

    x0_edges = sum(
        outside[left][right] for left, right in itertools.combinations(range(3), 2)
    )
    demand(x0_edges == payload["branch_eX0"] == 0, "linear witness branch drift")

    distinct_rows: set[tuple[tuple[tuple[int, int], ...], int]] = set()
    for row in range(N_OUTSIDE):
        for column in range(N_MOTIF):
            edge_tokens = tuple(
                sorted(
                    (min(row, other), max(row, other))
                    for other in range(N_OUTSIDE)
                    if other != row and incidence[other][column]
                )
            )
            distinct_rows.add((edge_tokens, rhs[row][column]))
    demand(len(distinct_rows) == 1044, "distinct DP incidence-row count drift")
    demand(1044 + 87 + 3 == payload["constraint_rows"], "linear row total drift")

    pair_failures = 0
    first_failure: dict[str, int] | None = None
    error_histogram: Counter[int] = Counter()
    for left, right in itertools.combinations(range(N_OUTSIDE), 2):
        overlap = sum(
            incidence[left][column] * incidence[right][column]
            for column in range(N_MOTIF)
        )
        lhs = outside[left][right] + sum(
            outside[left][center] * outside[center][right]
            for center in range(N_OUTSIDE)
        )
        rhs_pair = 2 - overlap
        if lhs != rhs_pair:
            pair_failures += 1
            error_histogram[lhs - rhs_pair] += 1
            if first_failure is None:
                first_failure = {
                    "left": left,
                    "right": right,
                    "lhs": lhs,
                    "rhs": rhs_pair,
                }
    demand(pair_failures > 0, "linear witness unexpectedly satisfies every pair row")
    return {
        "outside_edges": edge_count,
        "degree_histogram": dict(sorted(Counter(degrees).items())),
        "dp_entries_checked": N_OUTSIDE * N_MOTIF,
        "distinct_dp_incidence_rows": len(distinct_rows),
        "archived_constraint_rows": int(payload["constraint_rows"]),
        "branch_eX0": x0_edges,
        "upper_triangle_sha256": upper_hash,
        "outside_pair_equation_failures": pair_failures,
        "first_outside_pair_failure": first_failure,
        "outside_pair_error_histogram": {
            str(key): value for key, value in sorted(error_histogram.items())
        },
        "linear_layer_feasible": True,
        "full_extension_witness": False,
    }


def permuted_edges(
    edges: set[tuple[int, int]], permutation: tuple[int, int, int]
) -> set[tuple[int, int]]:
    return {
        tuple(sorted((permutation[left], permutation[right])))
        for left, right in edges
    }


def branch_coverage() -> dict[str, object]:
    all_pairs = ((0, 1), (0, 2), (1, 2))
    graphs = [
        {pair for bit, pair in enumerate(all_pairs) if mask & (1 << bit)}
        for mask in range(8)
    ]
    permutations = tuple(itertools.permutations(range(3)))
    assignments_by_t: Counter[int] = Counter()
    for graph in graphs:
        t = len(graph)
        canonical = canonical_x0(t)
        demand(
            any(permuted_edges(graph, permutation) == canonical for permutation in permutations),
            f"X0 graph with {t} edges missed by canonical branch",
        )
        assignments_by_t[t] += 1
    return {
        "labelled_x0_graphs_checked": len(graphs),
        "isomorphism_branches": [0, 1, 2, 3],
        "labelled_assignments_by_branch": {
            str(key): value for key, value in sorted(assignments_by_t.items())
        },
        "complete_up_to_permuting_three_identical_X0_rows": True,
    }


def conjunction_truth_table_check() -> bool:
    for left, right, conjunction in itertools.product((False, True), repeat=3):
        clauses = (
            (not conjunction) or left,
            (not conjunction) or right,
            conjunction or (not left) or (not right),
        )
        if all(clauses) != (conjunction == (left and right)):
            return False
    return True


def audit_discovery_source() -> dict[str, object]:
    path = DISCOVERY / "motif_search.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    solve_node = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "solve_extension"
    )
    solve_source = ast.get_source_segment(source, solve_node)
    demand(solve_source is not None, "could not isolate solve_extension source")
    required_fragments = {
        "all_outside_pairs": (
            "for left, right in combinations(range(OUTSIDE_VERTICES), 2):"
        ),
        "all_nonendpoint_centers": "for center in range(OUTSIDE_VERTICES):",
        "skip_pair_endpoints": "if center in (left, right):",
        "pair_edge_in_exact_row": "common_literals = [edge(left, right)]",
        "correct_pair_rhs": "bound = 2 - overlap",
        "forward_and_clauses": "solver.add_clause([-conjunction, left_edge])",
        "reverse_and_clause": (
            "solver.add_clause([conjunction, -left_edge, -right_edge])"
        ),
        "exact_pair_row": "exact(common_literals, bound)",
        "linear_incidence_rows": "seen_linear_rows",
        "outside_degree_rows": "14 - len(patterns[outside])",
        "canonical_x0_branch": "canonical = canonical_x0_edges(edge_count_x0)",
        "direct_sat_replay": "verify_full_adjacency(full)",
        "unsat_fail_closed": "UNSAT_WITHOUT_EXTERNAL_CERTIFICATE",
        "timeout_fail_closed": "UNKNOWN_TIMEOUT",
    }
    fragment_checks = {
        name: fragment in solve_source for name, fragment in required_fragments.items()
    }
    demand(all(fragment_checks.values()), "discovery SAT source audit marker missing")

    exact_node = next(
        node
        for node in ast.walk(solve_node)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "exact"
    )
    exact_source = ast.get_source_segment(source, exact_node)
    demand(exact_source is not None, "could not isolate exact-cardinality wrapper")
    exact_checks = {
        "at_most_bound": "solver.add_atmost(unique, bound)" in exact_source,
        "at_least_bound_via_negated_at_most": (
            "solver.add_atmost([-literal for literal in unique], len(unique) - bound)"
            in exact_source
        ),
    }
    demand(all(exact_checks.values()), "exact-cardinality wrapper audit failed")
    return {
        "source_sha256": sha256_file(path),
        "fragment_checks": fragment_checks,
        "exact_cardinality_checks": exact_checks,
        "and_gate_truth_table_complete": conjunction_truth_table_check(),
    }


def verify_raw_logs() -> dict[str, object]:
    bounded_object = load_json(DISCOVERY / "bounded-results.json")
    demand(isinstance(bounded_object, dict), "bounded results is not an object")
    bounded = bounded_object
    run_rows = bounded["runs"]
    demand(isinstance(run_rows, list) and len(run_rows) == 4, "bounded run count drift")
    verified: list[dict[str, object]] = []
    for archived in run_rows:
        demand(isinstance(archived, dict), "malformed bounded run row")
        branch = int(archived["branch_eX0"])
        raw_path = VERIFIER_RAW_LOGS / f"wave105-branch{branch}-45s.json"
        observed_hash = sha256_file(raw_path)
        demand(observed_hash == archived["raw_log_sha256"], "raw log hash mismatch")
        raw_object = load_json(raw_path)
        demand(isinstance(raw_object, dict), "raw run log is not an object")
        raw = raw_object
        for key in (
            "branch_eX0",
            "elapsed_seconds",
            "free_memory_fraction_before",
            "free_memory_fraction_after",
            "result",
        ):
            demand(raw[key] == archived[key], f"bounded/raw run mismatch: {key}")
        demand(raw["claim_label"] == "UNKNOWN", "timeout claim label inflated")
        demand(raw["result"] == "UNKNOWN_TIMEOUT", "bounded result is not timeout")
        demand(raw["timed_out"] is True, "raw timeout flag is false")
        demand(raw["edge_variables"] == 3741, "edge-variable count drift")
        demand(
            raw["common_conjunction_variables"] == 317985,
            "conjunction-variable count drift",
        )
        demand(raw["total_variables"] == 321726, "total-variable count drift")
        demand(
            raw["distinct_linear_incidence_rows"] == 1044,
            "linear incidence-row count drift",
        )
        verified.append(
            {
                "branch_eX0": branch,
                "sha256": observed_hash,
                "elapsed_seconds": raw["elapsed_seconds"],
                "result": raw["result"],
                "claim_label": raw["claim_label"],
            }
        )
    demand(
        sorted(row["branch_eX0"] for row in verified) == [0, 1, 2, 3],
        "bounded branches are not exactly 0,1,2,3",
    )
    return {
        "raw_logs_available": True,
        "runs": verified,
        "interpretation": "chronology only; every timeout remains UNKNOWN",
    }


def verify_all() -> dict[str, object]:
    discovery_files = validate_discovery_manifest()
    frozen_inputs = validate_hash_list(Path(__file__).with_name("input-freeze.sha256"))
    motif = motif_graph()
    motif_matrix = adjacency_matrix(motif)
    patterns = derive_outside_patterns()
    incidence = incidence_matrix(patterns)
    residual = residual_pair_capacities(motif)

    degrees = [len(row) for row in motif]
    demand(degrees == [4] * 12, "motif is not 4-regular")
    demand(sum(degrees) // 2 == 24, "motif edge count drift")
    demand(check_top_left_block(motif_matrix, incidence), "top-left block failed")

    edge_rows = {str(t): type_edge_counts(t) for t in range(4)}
    expected_edge_rows = {
        str(t): {
            "00": t,
            "01": 12 - 4 * t,
            "02": 30 + 2 * t,
            "11": 156 + 4 * t,
            "12": 300 - 4 * t,
            "22": 51 + t,
        }
        for t in range(4)
    }
    demand(edge_rows == expected_edge_rows, "type-edge formulas drift")
    demand(
        all(sum(row.values()) == 549 for row in edge_rows.values()),
        "outside edge total drift",
    )

    rows_by_t = {str(t): moment_census(patterns, t) for t in range(4)}
    moment_counts = {key: len(rows) for key, rows in rows_by_t.items()}
    graphical_counts = {
        key: sum(bool(row["all_six_type_graphical"]) for row in rows)
        for key, rows in rows_by_t.items()
    }
    demand(moment_counts == {"0": 18, "1": 11, "2": 5, "3": 1}, "moment census drift")
    demand(
        graphical_counts == {"0": 18, "1": 11, "2": 4, "3": 1},
        "graphical census drift",
    )
    rejected = [
        {"branch_eX0": int(t), **row}
        for t, rows in rows_by_t.items()
        for row in rows
        if not row["all_six_type_graphical"]
    ]
    demand(
        len(rejected) == 1
        and rejected[0]["branch_eX0"] == 2
        and rejected[0]["six_type_graphical_tests"]
        == [True, False, True, True, True, True],
        "single graphical rejection drift",
    )

    linear = verify_linear_witness(patterns, motif_matrix)
    branch = branch_coverage()
    source_audit = audit_discovery_source()
    raw_logs = verify_raw_logs()

    residual_histogram = Counter(residual.values())
    demand(residual_histogram == {0: 42, 1: 12, 2: 12}, "residual-pair histogram drift")
    pattern_histogram = Counter(map(len, patterns))
    demand(pattern_histogram == {0: 3, 1: 48, 2: 36}, "pattern histogram drift")
    incidence_total = sum(map(sum, incidence))
    pair_incidence_total = sum(
        len(pattern) * (len(pattern) - 1) // 2 for pattern in patterns
    )
    demand(incidence_total == 120 and pair_incidence_total == 36, "incidence totals drift")

    encoding_counts = {
        "edge_variables": N_OUTSIDE * (N_OUTSIDE - 1) // 2,
        "common_conjunction_variables": (
            N_OUTSIDE * (N_OUTSIDE - 1) // 2 * (N_OUTSIDE - 2)
        ),
    }
    encoding_counts["total_variables"] = (
        encoding_counts["edge_variables"]
        + encoding_counts["common_conjunction_variables"]
    )
    demand(
        encoding_counts
        == {
            "edge_variables": 3741,
            "common_conjunction_variables": 317985,
            "total_variables": 321726,
        },
        "symbolic encoding counts drift",
    )

    return {
        "format": "wave105-independent-verification-v1",
        "verdict": "VERIFIED_WITH_CLARIFICATIONS",
        "claim_label": "VERIFIED",
        "scope": (
            "Conditional on a hypothetical srg(99,14,1,2) containing the "
            "induced C4 box K3 motif."
        ),
        "provenance": {
            "discovery_manifest_sha256": EXPECTED_DISCOVERY_MANIFEST,
            "discovery_files_checked": len(discovery_files),
            "frozen_inputs_checked": frozen_inputs,
        },
        "motif": {
            "vertices": 12,
            "edges": 24,
            "degrees": sorted(set(degrees)),
            "residual_pair_capacity_histogram": {
                str(key): value for key, value in sorted(residual_histogram.items())
            },
            "positive_residual_support_triangle_free": True,
        },
        "forced_outside_incidence": {
            "type_counts": {
                f"X{key}": value for key, value in sorted(pattern_histogram.items())
            },
            "incidences": incidence_total,
            "pair_incidences": pair_incidence_total,
            "top_left_block_equation_checked": True,
            "clarification": (
                "The multiset is forced because every outside motif-neighborhood "
                "has size at most two: the positive residual-pair support is "
                "triangle-free."
            ),
        },
        "block_equations": {
            "top_left": "H^2+P^T P=12I-H+2J",
            "linear": "DP=2J-P-PH",
            "outside_pair": "D_ij+sum_k D_ik D_kj=2-(PP^T)_ij",
            "linear_rhs_entries": 87 * 12,
        },
        "outside_type_edges": {
            "total": 549,
            "rows_by_t_eX0": edge_rows,
        },
        "moment_census": {
            "target_order": list(PAIR_KEYS),
            "rows_by_t": rows_by_t,
            "counts_by_t": moment_counts,
            "six_graphical_filter_counts_by_t": graphical_counts,
            "rejected_rows": rejected,
        },
        "linear_witness": linear,
        "sat_encoding_audit": {
            "conditional_domain_complete": True,
            "no_target_graph_automorphism_assumed": True,
            "branch_coverage": branch,
            "counts": encoding_counts,
            "source_audit": source_audit,
            "logical_equivalence": (
                "Each auxiliary y has y iff (D_ik and D_kj); exact "
                "D_ij+sum(y)=2-(PP^T)_ij is equation (3) off diagonal."
            ),
        },
        "bounded_runs": raw_logs,
        "status_wall": {
            "linear_layer": "FEASIBLE",
            "motif_extension": "UNKNOWN",
            "motif_excluded": False,
            "Conway_99": "UNKNOWN",
            "global_construction": False,
            "global_nonexistence_proof": False,
            "literature_novelty": "UNKNOWN",
        },
        "clarifications": [
            (
                "The discovery write-up did not spell out the triangle-free "
                "residual-support argument needed for uniqueness of the forced "
                "incidence multiset; the independent verifier supplies and "
                "checks it explicitly."
            ),
            (
                "The archived linear witness actually fails many nonlinear "
                "outside-pair rows, so it certifies only linear-layer feasibility."
            ),
            (
                "The four raw run hashes are reproducible chronology, but "
                "timeouts are not solver certificates and remain UNKNOWN."
            ),
        ],
        "limitations": [
            "The motif is not proved to occur in every hypothetical target.",
            "The six graphicality tests are separate necessary filters, not simultaneous realizations.",
            "No SAT model or replayable UNSAT proof was produced.",
            "No graph construction, graph exclusion, Conway-99 resolution, or novelty claim follows.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("independent-results.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = verify_all()
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
