#!/usr/bin/env python3
"""Clean-room exact checks for the Wave 33 rooted O-Q search package.

This module uses only the Python standard library.  It was written and frozen
before inspection of the Wave 33 rooted-construction discovery package.  The
only mathematical inputs are the public Wave 32 rooted support design and the
frozen Wave 33 claim synopsis.

The checker deliberately distinguishes three objects:

* the public 14-by-70 support/O incidence matrix B;
* a simple 2-(15,3,2) O-Q incidence matrix F;
* the still-missing 70-by-70 active O-O adjacency matrix D.

The 210 equations B F = 2 J are necessary before an active-graph search can
start.  They are not a graph certificate.  A timeout without a primal is not
an exclusion, even for the one fixed design searched.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence


PUBLIC_BASE_COMMIT = "b2595baa40d50e9c259051751fe27090bee6a449"
SEARCH_SCOPE = "ONE_FIXED_SIMPLE_2_15_3_2_DESIGN_ALL_BLOCK_TO_O_BIJECTIONS"
PARTIAL_STATUS = "PARTIAL_CONTROL_NOT_CONWAY_GRAPH"
UNKNOWN_STATUS = "UNKNOWN"


class VerificationError(ValueError):
    """Raised when an exact obligation or a status gate fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def is_exact_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def require_exact_int(value: Any, message: str) -> int:
    require(is_exact_int(value), message)
    return value


def no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise VerificationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return json.load(handle, object_pairs_hook=no_duplicate_object)
    except json.JSONDecodeError as exc:
        raise VerificationError(f"invalid JSON: {exc}") from exc


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def histogram(values: Iterable[int]) -> dict[str, int]:
    return {
        str(key): count
        for key, count in sorted(Counter(values).items(), key=lambda item: item[0])
    }


def canonical_cross_incidence() -> list[list[int]]:
    """Return the public Wave 32 symmetric 2-(7,4,2) cross incidence."""

    return [
        [1, 0, 1, 0, 1, 0, 1],
        [0, 1, 1, 0, 0, 1, 1],
        [1, 1, 0, 0, 1, 1, 0],
        [0, 0, 0, 1, 1, 1, 1],
        [1, 0, 1, 1, 0, 1, 0],
        [0, 1, 1, 1, 1, 0, 0],
        [1, 1, 0, 1, 0, 0, 1],
    ]


def check_cross_incidence(cross: Any) -> dict[str, Any]:
    require(isinstance(cross, list) and len(cross) == 7, "cross must have 7 rows")
    normalized: list[list[int]] = []
    for row_index, row in enumerate(cross):
        require(
            isinstance(row, list) and len(row) == 7,
            f"cross row {row_index} must have length 7",
        )
        normalized_row: list[int] = []
        for column_index, value in enumerate(row):
            require_exact_int(
                value, f"cross[{row_index}][{column_index}] must be an integer"
            )
            require(value in (0, 1), "cross entries must be binary")
            normalized_row.append(value)
        normalized.append(normalized_row)

    require(normalized == canonical_cross_incidence(), "cross bytes are not canonical")
    row_sums = [sum(row) for row in normalized]
    column_sums = [sum(normalized[i][j] for i in range(7)) for j in range(7)]
    row_pair_intersections = [
        sum(normalized[i][q] * normalized[j][q] for q in range(7))
        for i in range(7)
        for j in range(i + 1, 7)
    ]
    column_pair_intersections = [
        sum(normalized[q][i] * normalized[q][j] for q in range(7))
        for i in range(7)
        for j in range(i + 1, 7)
    ]
    require(row_sums == [4] * 7, "cross row sums must all be 4")
    require(column_sums == [4] * 7, "cross column sums must all be 4")
    require(
        row_pair_intersections == [2] * 21,
        "cross row-pair intersections must all be 2",
    )
    require(
        column_pair_intersections == [2] * 21,
        "cross column-pair intersections must all be 2",
    )
    return {
        "row_sums": row_sums,
        "column_sums": column_sums,
        "row_pair_intersections": histogram(row_pair_intersections),
        "column_pair_intersections": histogram(column_pair_intersections),
        "sha256": sha256_bytes(canonical_json_bytes(normalized)),
    }


def canonical_o_label_tuples(
    cross: Sequence[Sequence[int]] | None = None,
) -> list[tuple[int, int, int]]:
    """Return all 70 fixed O labels as (positive, negative, copy)."""

    if cross is None:
        cross = canonical_cross_incidence()
    labels: list[tuple[int, int, int]] = []
    for positive in range(7):
        for negative in range(7):
            multiplicity = 1 if cross[positive][negative] else 2
            for copy_index in range(multiplicity):
                labels.append((positive, negative, copy_index))
    require(len(labels) == 70, "internal O-label census failure")
    return labels


def canonical_o_labels() -> list[dict[str, int | str]]:
    return [
        {
            "id": f"O{positive}_{negative}_{copy_index}",
            "positive": positive,
            "negative": negative,
            "copy": copy_index,
        }
        for positive, negative, copy_index in canonical_o_label_tuples()
    ]


def normalize_o_labels(
    raw_labels: Any, cross: Sequence[Sequence[int]]
) -> list[tuple[int, int, int]]:
    require(
        isinstance(raw_labels, list) and len(raw_labels) == 70,
        "o_labels must contain exactly 70 labels",
    )
    labels: list[tuple[int, int, int]] = []
    identifiers: list[str] = []
    for index, raw in enumerate(raw_labels):
        require(isinstance(raw, dict), f"o_labels[{index}] must be an object")
        for key in ("positive", "negative", "copy"):
            require(key in raw, f"o_labels[{index}] is missing {key}")
            require_exact_int(raw[key], f"o_labels[{index}].{key} must be an integer")
        label = (raw["positive"], raw["negative"], raw["copy"])
        labels.append(label)
        if "id" in raw:
            require(isinstance(raw["id"], str), f"o_labels[{index}].id must be text")
            identifiers.append(raw["id"])
    require(len(set(labels)) == 70, "o_labels contain duplicates")
    require(
        set(labels) == set(canonical_o_label_tuples(cross)),
        "o_labels are not exactly the public 70-label multiset",
    )
    if identifiers:
        require(len(identifiers) == 70, "either every O label has an id or none do")
        require(len(set(identifiers)) == 70, "O-label ids must be distinct")
    return labels


def support_o_matrix(labels: Sequence[tuple[int, int, int]]) -> list[list[int]]:
    matrix = [[0] * len(labels) for _ in range(14)]
    for column, (positive, negative, _copy_index) in enumerate(labels):
        matrix[positive][column] = 1
        matrix[7 + negative][column] = 1
    return matrix


def support_adjacency(cross: Sequence[Sequence[int]]) -> list[list[int]]:
    adjacency = [[0] * 14 for _ in range(14)]
    for positive in range(7):
        for negative in range(7):
            value = cross[positive][negative]
            adjacency[positive][7 + negative] = value
            adjacency[7 + negative][positive] = value
    return adjacency


def matrix_product(
    left: Sequence[Sequence[int]], right: Sequence[Sequence[int]]
) -> list[list[int]]:
    require(bool(left) and bool(right), "matrix product requires nonempty matrices")
    inner = len(left[0])
    require(all(len(row) == inner for row in left), "ragged left matrix")
    require(len(right) == inner, "matrix dimensions do not agree")
    width = len(right[0])
    require(all(len(row) == width for row in right), "ragged right matrix")
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(inner))
            for j in range(width)
        ]
        for i in range(len(left))
    ]


def transpose(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    require(bool(matrix), "cannot transpose an empty matrix")
    width = len(matrix[0])
    require(all(len(row) == width for row in matrix), "ragged matrix")
    return [[matrix[i][j] for i in range(len(matrix))] for j in range(width)]


def check_public_support(
    cross: Any, raw_o_labels: Any
) -> tuple[list[tuple[int, int, int]], list[list[int]], dict[str, Any]]:
    cross_metrics = check_cross_incidence(cross)
    labels = normalize_o_labels(raw_o_labels, cross)
    support_o = support_o_matrix(labels)
    row_sums = [sum(row) for row in support_o]
    column_sums = [sum(support_o[row][column] for row in range(14)) for column in range(70)]
    require(row_sums == [10] * 14, "B row sums must all be 10")
    require(column_sums == [2] * 70, "B column sums must all be 2")

    support = support_adjacency(cross)
    left_square = matrix_product(support, support)
    bb_transpose = matrix_product(support_o, transpose(support_o))
    defects: list[tuple[int, int, int, int]] = []
    for i in range(14):
        for j in range(14):
            actual = left_square[i][j] + bb_transpose[i][j]
            target = (12 if i == j else 0) - support[i][j] + 2
            if actual != target:
                defects.append((i, j, actual, target))
    require(not defects, "public support block identity failed")

    signed = [1] * 7 + [-1] * 7
    support_image = [
        sum(support[i][j] * signed[j] for j in range(14)) for i in range(14)
    ]
    o_image = [
        sum(support_o[i][j] * signed[i] for i in range(14)) for j in range(70)
    ]
    require(
        support_image == [-4 * value for value in signed],
        "support signed vector is not a minus-four eigenvector",
    )
    require(o_image == [0] * 70, "each O label must meet one sign of each type")
    metrics = {
        "cross": cross_metrics,
        "B_row_sums": histogram(row_sums),
        "B_column_sums": histogram(column_sums),
        "B_sha256": sha256_bytes(canonical_json_bytes(support_o)),
        "support_block_identity": "PASS",
        "signed_vector_distribution": {"-1": 7, "0": 85, "1": 7},
        "signed_vector_eigenvalue_on_public_partial": -4,
    }
    return labels, support_o, metrics


def normalize_blocks(raw_blocks: Any, *, label: str) -> list[tuple[int, int, int]]:
    require(
        isinstance(raw_blocks, list) and len(raw_blocks) == 70,
        f"{label} must contain exactly 70 blocks",
    )
    blocks: list[tuple[int, int, int]] = []
    for block_index, raw_block in enumerate(raw_blocks):
        require(
            isinstance(raw_block, list) and len(raw_block) == 3,
            f"{label}[{block_index}] must contain exactly 3 points",
        )
        points: list[int] = []
        for point in raw_block:
            require_exact_int(point, f"{label}[{block_index}] point must be an integer")
            require(0 <= point < 15, f"{label}[{block_index}] point outside 0..14")
            points.append(point)
        require(len(set(points)) == 3, f"{label}[{block_index}] repeats a point")
        blocks.append(tuple(sorted(points)))
    require(len(set(blocks)) == 70, f"{label} is not simple")
    return blocks


def design_metrics(blocks: Sequence[tuple[int, int, int]]) -> dict[str, Any]:
    point_degrees = [0] * 15
    pair_counts = [[0] * 15 for _ in range(15)]
    for block in blocks:
        for point in block:
            point_degrees[point] += 1
        for left_index in range(3):
            for right_index in range(left_index + 1, 3):
                left = block[left_index]
                right = block[right_index]
                pair_counts[left][right] += 1
                pair_counts[right][left] += 1
    pair_values = [
        pair_counts[left][right]
        for left in range(15)
        for right in range(left + 1, 15)
    ]
    require(point_degrees == [14] * 15, "design point degrees must all be 14")
    require(pair_values == [2] * 105, "design pair intersections must all be 2")
    canonical_blocks = [list(block) for block in sorted(blocks)]
    return {
        "block_count": len(blocks),
        "block_size": 3,
        "simple": len(set(blocks)) == len(blocks),
        "point_degree_histogram": histogram(point_degrees),
        "pair_intersection_histogram": histogram(pair_values),
        "canonical_block_set_sha256": sha256_bytes(
            canonical_json_bytes(canonical_blocks)
        ),
    }


def normalize_assignment(raw_assignment: Any) -> list[int]:
    require(
        isinstance(raw_assignment, list) and len(raw_assignment) == 70,
        "assignment must have exactly 70 entries",
    )
    assignment: list[int] = []
    for index, value in enumerate(raw_assignment):
        require_exact_int(value, f"assignment[{index}] must be an integer")
        require(0 <= value < 70, f"assignment[{index}] outside 0..69")
        assignment.append(value)
    require(sorted(assignment) == list(range(70)), "assignment is not a bijection")
    return assignment


def incidence_from_blocks(
    blocks_by_o: Sequence[tuple[int, int, int]]
) -> list[list[int]]:
    incidence = [[0] * 15 for _ in range(70)]
    for o_index, block in enumerate(blocks_by_o):
        for point in block:
            incidence[o_index][point] = 1
    return incidence


def bf_metrics(
    support_o: Sequence[Sequence[int]], oq: Sequence[Sequence[int]]
) -> dict[str, Any]:
    product = matrix_product(support_o, oq)
    violations: list[dict[str, int]] = []
    defects: list[int] = []
    for support_index in range(14):
        for point in range(15):
            actual = product[support_index][point]
            defect = actual - 2
            if defect:
                violations.append(
                    {
                        "support": support_index,
                        "point": point,
                        "actual": actual,
                        "defect": defect,
                    }
                )
                defects.append(defect)
    return {
        "equation_count": 14 * 15,
        "violation_count": len(violations),
        "squared_defect": sum(defect * defect for defect in defects),
        "defect_histogram": histogram(defects),
        "violations": violations,
        "status": "PASS" if not violations else "FAIL",
    }


def normalize_d_matrix(raw_partial: dict[str, Any]) -> list[list[int]]:
    if "empty_d_control_matrix" in raw_partial:
        raw = raw_partial["empty_d_control_matrix"]
        require(
            isinstance(raw, list) and len(raw) == 70,
            "d_matrix must have 70 rows",
        )
        matrix: list[list[int]] = []
        for i, row in enumerate(raw):
            require(
                isinstance(row, list) and len(row) == 70,
                f"d_matrix row {i} must have length 70",
            )
            normalized_row: list[int] = []
            for j, value in enumerate(row):
                require_exact_int(value, f"d_matrix[{i}][{j}] must be an integer")
                require(value in (0, 1), "d_matrix must be binary")
                normalized_row.append(value)
            matrix.append(normalized_row)
    else:
        raw_edges = raw_partial.get("empty_d_control_edges")
        require(
            isinstance(raw_edges, list),
            "partial must contain empty_d_control_edges or empty_d_control_matrix",
        )
        matrix = [[0] * 70 for _ in range(70)]
        seen: set[tuple[int, int]] = set()
        for edge_index, raw_edge in enumerate(raw_edges):
            require(
                isinstance(raw_edge, list) and len(raw_edge) == 2,
                f"d_edges[{edge_index}] must be a pair",
            )
            left = require_exact_int(
                raw_edge[0], f"d_edges[{edge_index}][0] must be an integer"
            )
            right = require_exact_int(
                raw_edge[1], f"d_edges[{edge_index}][1] must be an integer"
            )
            require(0 <= left < 70 and 0 <= right < 70, "D edge outside 0..69")
            require(left != right, "D must be loopless")
            edge = (min(left, right), max(left, right))
            require(edge not in seen, "D contains a duplicate undirected edge")
            seen.add(edge)
            matrix[left][right] = 1
            matrix[right][left] = 1

    for i in range(70):
        require(matrix[i][i] == 0, "D must be hollow")
        for j in range(i + 1, 70):
            require(matrix[i][j] == matrix[j][i], "D must be symmetric")
    return matrix


def build_adjacency(
    cross: Sequence[Sequence[int]],
    support_o: Sequence[Sequence[int]],
    oq: Sequence[Sequence[int]],
    active: Sequence[Sequence[int]],
) -> list[list[int]]:
    """Build the full 99-by-99 adjacency in S(14), O(70), Q(15) order."""

    adjacency = [[0] * 99 for _ in range(99)]
    support = support_adjacency(cross)
    for i in range(14):
        for j in range(14):
            adjacency[i][j] = support[i][j]
    for support_index in range(14):
        for o_index in range(70):
            value = support_o[support_index][o_index]
            adjacency[support_index][14 + o_index] = value
            adjacency[14 + o_index][support_index] = value
    for left in range(70):
        for right in range(70):
            adjacency[14 + left][14 + right] = active[left][right]
    for o_index in range(70):
        for point in range(15):
            value = oq[o_index][point]
            adjacency[14 + o_index][84 + point] = value
            adjacency[84 + point][14 + o_index] = value
    return adjacency


def graph_metrics(adjacency: Sequence[Sequence[int]]) -> dict[str, Any]:
    require(len(adjacency) == 99, "adjacency must have 99 rows")
    for i, row in enumerate(adjacency):
        require(len(row) == 99, f"adjacency row {i} must have length 99")
        for j, value in enumerate(row):
            require_exact_int(value, f"adjacency[{i}][{j}] must be an integer")
            require(value in (0, 1), "adjacency must be binary")
            require(adjacency[i][j] == adjacency[j][i], "adjacency must be symmetric")
        require(adjacency[i][i] == 0, "adjacency must be hollow")

    degrees = [sum(row) for row in adjacency]
    identity_violations: list[dict[str, int]] = []
    adjacent_common: list[int] = []
    nonadjacent_common: list[int] = []
    for i in range(99):
        for j in range(99):
            common = sum(adjacency[i][k] * adjacency[k][j] for k in range(99))
            target = (12 if i == j else 0) - adjacency[i][j] + 2
            if common != target:
                identity_violations.append(
                    {"left": i, "right": j, "actual": common, "target": target}
                )
            if i < j:
                if adjacency[i][j]:
                    adjacent_common.append(common)
                else:
                    nonadjacent_common.append(common)
    return {
        "degree_histogram": histogram(degrees),
        "identity_violation_count": len(identity_violations),
        "identity_status": "PASS" if not identity_violations else "FAIL",
        "adjacent_common_neighbor_histogram": histogram(adjacent_common),
        "nonadjacent_common_neighbor_histogram": histogram(nonadjacent_common),
        "is_conway_graph": not identity_violations,
    }


def check_search_report(raw: Any) -> dict[str, Any]:
    require(isinstance(raw, dict), "search_report must be an object")
    expected_exact = {
        "scope": SEARCH_SCOPE,
        "fixed_design_count": 1,
        "o_label_count": 70,
        "block_count": 70,
        "assignment_binary_count": 4900,
        "o_bijection_equalities": 70,
        "block_bijection_equalities": 70,
        "support_point_equalities": 210,
        "total_equalities": 350,
        "scipy_status": 1,
    }
    for key, expected in expected_exact.items():
        require(key in raw, f"search_report is missing {key}")
        if is_exact_int(expected):
            require_exact_int(raw[key], f"search_report.{key} must be an integer")
        require(raw[key] == expected, f"search_report.{key} must equal {expected!r}")

    require(
        str(raw.get("solver_family", "")).upper().replace("/", "_")
        == "SCIPY_HIGHS",
        "solver_family must identify SciPy/HiGHS",
    )
    require(str(raw.get("objective", "")).upper() == "ZERO", "objective must be zero")
    time_limit = raw.get("time_limit_seconds")
    require(
        (is_exact_int(time_limit) or isinstance(time_limit, float))
        and not isinstance(time_limit, bool)
        and time_limit == 25,
        "time_limit_seconds must be 25",
    )
    require(
        str(raw.get("termination", "")).upper() == "TIME_LIMIT",
        "termination must be TIME_LIMIT",
    )
    for key in (
        "primal_found",
        "active_graph_phase_entered",
        "claimed_exclusion",
        "claimed_construction",
    ):
        require(raw.get(key) is False, f"search_report.{key} must be false")
    require(
        str(raw.get("conclusion", "")).upper() == UNKNOWN_STATUS,
        "timeout/no-primal conclusion must be UNKNOWN",
    )

    return {
        "scope": SEARCH_SCOPE,
        "fixed_design_count": 1,
        "assignment_binary_count": 70 * 70,
        "bijection_equalities": 70 + 70,
        "support_point_equalities": 14 * 15,
        "total_equalities": 70 + 70 + 14 * 15,
        "encoded_block_to_O_bijection_count": str(math.factorial(70)),
        "covers": "all block-to-O bijections of one fixed design",
        "does_not_cover": "other nonisomorphic simple 2-(15,3,2) designs",
        "termination": "TIME_LIMIT",
        "scipy_status": 1,
        "primal_found": False,
        "active_graph_phase_entered": False,
        "active_O_O_layer_status": "UNSUPPLIED_NO_PRIMAL_FOR_F",
        "evidentiary_conclusion": UNKNOWN_STATUS,
        "is_exclusion": False,
        "is_construction": False,
    }


def check_status_wall(payload: dict[str, Any], partial: dict[str, Any]) -> dict[str, str]:
    require(
        payload.get("claim_label") == UNKNOWN_STATUS,
        "package claim_label must remain UNKNOWN",
    )
    statuses = payload.get("global_status")
    require(isinstance(statuses, dict), "global_status must be an object")
    expected = {
        "Conway_99": UNKNOWN_STATUS,
        "n3_708": UNKNOWN_STATUS,
        "rooted_endpoint": UNKNOWN_STATUS,
        "fixed_design_search": "UNKNOWN_TIMEOUT_NO_PRIMAL",
        "root_exclusion": "NOT_OBTAINED",
        "full_graph_construction": "NOT_OBTAINED",
    }
    require(statuses == expected, "global_status inflates or changes the frozen boundary")
    require(
        partial.get("status") == PARTIAL_STATUS,
        "hostile partial status must deny a Conway-graph certificate",
    )
    require(
        partial.get("o_o_layer_scope")
        == "UNSUPPLIED_IN_CERTIFICATE_EMPTY_CONTROL_ONLY",
        "O-O scope must distinguish an unsupplied layer from the empty control",
    )
    require(
        partial.get("claimed_full_graph") is False,
        "hostile partial may not claim a full graph",
    )
    require(
        partial.get("claimed_exclusion") is False,
        "hostile partial may not claim an exclusion",
    )
    return expected


def check_expected_partial_claims(
    expected: Any, design: dict[str, Any], bf: dict[str, Any], d_edge_count: int
) -> None:
    require(isinstance(expected, dict), "hostile_partial.expected must be an object")
    exact = {
        "row_degree": 3,
        "column_degree": 14,
        "q_pair_intersection": 2,
        "q_pair_count": 105,
        "bf_equation_count": 210,
        "bf_violation_count": bf["violation_count"],
        "bf_squared_defect": bf["squared_defect"],
        "empty_d_control_edge_count": d_edge_count,
    }
    require(expected == exact, "stated hostile-partial metrics do not match recomputation")
    require(design["point_degree_histogram"] == {"14": 15}, "column-degree gate failed")
    require(
        design["pair_intersection_histogram"] == {"2": 105},
        "Q-pair intersection gate failed",
    )


def verify_payload(payload: Any, *, input_sha256: str | None = None) -> dict[str, Any]:
    require(isinstance(payload, dict), "payload must be a JSON object")
    require(payload.get("schema_version") == 1, "schema_version must be 1")
    require(
        payload.get("public_base_commit") == PUBLIC_BASE_COMMIT,
        "public base commit mismatch",
    )
    cross = payload.get("support_cross_incidence")
    labels, support_o, public_metrics = check_public_support(
        cross, payload.get("o_labels")
    )
    search_metrics = check_search_report(payload.get("search_report"))

    partial = payload.get("hostile_partial")
    require(isinstance(partial, dict), "hostile_partial must be an object")
    check_status_wall(payload, partial)

    fixed_blocks = normalize_blocks(
        partial.get("fixed_design_blocks"), label="fixed_design_blocks"
    )
    fixed_design_metrics = design_metrics(fixed_blocks)
    assignment = normalize_assignment(partial.get("assignment"))
    blocks_by_o = [fixed_blocks[block_index] for block_index in assignment]
    assigned_design_metrics = design_metrics(blocks_by_o)
    require(
        fixed_design_metrics["canonical_block_set_sha256"]
        == assigned_design_metrics["canonical_block_set_sha256"],
        "assigned O-Q blocks are not the fixed design",
    )
    oq = incidence_from_blocks(blocks_by_o)
    row_degrees = [sum(row) for row in oq]
    column_degrees = [sum(oq[o][q] for o in range(70)) for q in range(15)]
    require(row_degrees == [3] * 70, "F row degrees must all be 3")
    require(column_degrees == [14] * 15, "F column degrees must all be 14")
    bf = bf_metrics(support_o, oq)

    active = normalize_d_matrix(partial)
    d_edge_count = sum(sum(row) for row in active) // 2
    require(d_edge_count == 0, "hostile control must use empty D")
    adjacency = build_adjacency(cross, support_o, oq, active)
    full_graph = graph_metrics(adjacency)
    require(not full_graph["is_conway_graph"], "hostile partial unexpectedly is full graph")
    require(
        full_graph["degree_histogram"] == {"5": 70, "14": 29},
        "empty-D partial must have degree histogram 5^70,14^29",
    )
    check_expected_partial_claims(
        partial.get("expected"), assigned_design_metrics, bf, d_edge_count
    )
    bf_output = {
        key: value for key, value in bf.items() if key != "violations"
    }
    bf_output["violations_sha256"] = sha256_bytes(
        canonical_json_bytes(bf["violations"])
    )

    return {
        "schema_version": 1,
        "role": "verifier",
        "claim_label": "DERIVED",
        "scope": (
            "clean-room exact validation of one fixed-design assignment encoding "
            "and one hostile partial O-Q object"
        ),
        "input_sha256": input_sha256,
        "public_base_commit": PUBLIC_BASE_COMMIT,
        "public_support": public_metrics,
        "search_encoding": search_metrics,
        "hostile_partial": {
            "fixed_design": fixed_design_metrics,
            "assigned_design": assigned_design_metrics,
            "F_row_degree_histogram": histogram(row_degrees),
            "F_column_degree_histogram": histogram(column_degrees),
            "BF": bf_output,
            "O_O_layer_certificate_status": "UNSUPPLIED",
            "empty_D_control_edge_count": d_edge_count,
            "empty_D_control_full_graph_check": full_graph,
            "status": PARTIAL_STATUS,
        },
        "status_wall": {
            "Conway_99": UNKNOWN_STATUS,
            "n3_708": UNKNOWN_STATUS,
            "rooted_endpoint": UNKNOWN_STATUS,
            "fixed_design_search": "UNKNOWN_TIMEOUT_NO_PRIMAL",
            "root_exclusion": "NOT_OBTAINED",
            "full_graph_construction": "NOT_OBTAINED",
            "verifier_conclusion": (
                "timeout is no exclusion; hostile F is a design but has BF "
                "defects, its O-O layer is unsupplied, and the separate empty-D "
                "control fails the graph certificate"
            ),
        },
    }


def verify_path(path: Path) -> dict[str, Any]:
    return verify_payload(load_json(path), input_sha256=sha256_path(path))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = verify_path(args.input)
    except (OSError, VerificationError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
