#!/usr/bin/env python3
"""Static clean-room comparison for the Wave 33 rooted-extension package.

This checker reads frozen candidate files as inert bytes, text, JSON, and
Python syntax trees.  It never imports or executes candidate code.  The
high-risk arithmetic, PG(3,2) hostile control, and spectral consequences are
reconstructed here with Python's standard library.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import re
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[2]
VERIFY_DIR = ROOT / "verification" / "wave33-rooted-extension"
CANDIDATE_INVENTORY = (
    ROOT / "verification" / "wave33-rooted-extension-candidate-freeze.sha256"
)
PRECOMPARISON_MANIFEST = VERIFY_DIR / "artifact-manifest.sha256"
CANDIDATE_REPORT = ROOT / "agents" / "2026-07-24-wave33-rooted-extension.md"
CANDIDATE_DIR = ROOT / "attempts" / "wave33-rooted-extension"
CANDIDATE_RESULTS = CANDIDATE_DIR / "exact-results.json"
INDEPENDENT_RESULTS = VERIFY_DIR / "independent-results.json"

CANDIDATE_INVENTORY_SHA256 = (
    "f10119fecdbd226ca5a89180e2c8663b88c8f7d929ed8a619015070e0f637566"
)
PRECOMPARISON_MANIFEST_SHA256 = (
    "a0cd7d284a23aba5576f2da2a1282c9acb209953c3da5d01e706d793f61d3ea7"
)

EXPECTED_CANDIDATE_INVENTORY = {
    "attempts/wave33-rooted-extension/artifact-manifest.sha256":
        "153860d39fe7274a2f55ee952bcad1135cf4134ccc36d9aec07f6da379c5ca04",
    "attempts/wave33-rooted-extension/exact_check.py":
        "8712281e7b3819f466df9a35ec2303069737d75fe1af0f32e9eb9e6c1a543f8f",
    "attempts/wave33-rooted-extension/exact-results.json":
        "193db8ee0c155cc3a97489b4471c4a82ae09823dd9344d043a81778e1a6ba5a1",
    "attempts/wave33-rooted-extension/failed-routes.md":
        "1fb7b1ab26c0bcd08b0ac5d348e685b9616d396084145d6f4c1b7646b6dc3e1f",
    "attempts/wave33-rooted-extension/initial-derivation-freeze.md":
        "f222b78c2be4f41f8e66ea05265aaa3c55206577e94cf3f9746625c78a54868b",
    "attempts/wave33-rooted-extension/input-freeze.sha256":
        "74f98a5a79f53c35b8dce47feab8812b9b8f82ef4414c9c4ace759183d37ba64",
    "attempts/wave33-rooted-extension/run-report.yaml":
        "516538dcc0ef1cfddc0754732b5aedfe785082894f5589a27eeb9d4b17e40ffb",
    "attempts/wave33-rooted-extension/test_exact_check.py":
        "2149c793297b281d04011819c724f8236e2a386b1063b31feabc10a767ba0e71",
    "agents/2026-07-24-wave33-rooted-extension.md":
        "c324dc48f5c7b9524b8b2ac02fae3acb8b9ec342d0a61081ee86ae4771434c0c",
}

EXPECTED_CANDIDATE_EQUATIONS = [
    "A_S^2+F F^T=12I-A_S+2J",
    "A_S F+F D=2J-F",
    "F B=2J",
    "F^T F+D^2+B B^T=12I-D+2J",
    "D B=2J-B",
    "B^T B=12I+2J",
]

EXPECTED_SPECTRUM = {
    "9": 1,
    "-1": 14,
    "-1-sqrt(2)": 6,
    "-1+sqrt(2)": 6,
    "3": 27,
    "-4": 16,
}

Matrix = list[list[int]]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True)
        .encode("utf-8")
        + b"\n"
    )


def hash_payload(payload: object) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def parse_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not raw_line:
            continue
        match = re.fullmatch(r"([0-9a-f]{64})\s+\*?(.+)", raw_line)
        if match is None:
            raise AssertionError(f"invalid manifest line {path}:{line_number}")
        digest, relative = match.groups()
        if relative in entries:
            raise AssertionError(f"duplicate manifest path: {relative}")
        entries[relative] = digest
    return entries


def validate_manifest(path: Path) -> dict[str, str]:
    entries = parse_manifest(path)
    root_resolved = ROOT.resolve()
    for relative, expected in entries.items():
        target = (ROOT / relative).resolve()
        if root_resolved not in target.parents:
            raise AssertionError(f"manifest target escapes repository: {relative}")
        observed = sha256_file(target)
        if observed != expected:
            raise AssertionError(
                f"hash mismatch for {relative}: {observed} != {expected}"
            )
    return entries


def validate_release_integrity() -> dict[str, object]:
    if sha256_file(CANDIDATE_INVENTORY) != CANDIDATE_INVENTORY_SHA256:
        raise AssertionError("candidate release inventory bytes drifted")
    candidate_inventory = validate_manifest(CANDIDATE_INVENTORY)
    if candidate_inventory != EXPECTED_CANDIDATE_INVENTORY:
        raise AssertionError("candidate release inventory membership drifted")

    candidate_inner_path = CANDIDATE_DIR / "artifact-manifest.sha256"
    candidate_inner = validate_manifest(candidate_inner_path)
    expected_inner = {
        path: digest
        for path, digest in candidate_inventory.items()
        if path != "attempts/wave33-rooted-extension/artifact-manifest.sha256"
    }
    if candidate_inner != expected_inner:
        raise AssertionError("candidate inner manifest is not self-excluding inventory")

    if sha256_file(PRECOMPARISON_MANIFEST) != PRECOMPARISON_MANIFEST_SHA256:
        raise AssertionError("precomparison artifact manifest bytes drifted")
    precomparison = validate_manifest(PRECOMPARISON_MANIFEST)
    if len(precomparison) != 8:
        raise AssertionError("precomparison artifact count drifted")

    candidate_input_freeze = validate_manifest(
        CANDIDATE_DIR / "input-freeze.sha256"
    )
    if len(candidate_input_freeze) != 6:
        raise AssertionError("candidate input freeze count drifted")

    return {
        "candidate_release_inventory_sha256": CANDIDATE_INVENTORY_SHA256,
        "candidate_release_inventory_entries": len(candidate_inventory),
        "candidate_release_inventory_composition":
            "1 report + 8 attempts files, including the inner manifest",
        "candidate_inner_manifest_sha256": sha256_file(candidate_inner_path),
        "candidate_inner_manifest_entries": len(candidate_inner),
        "candidate_inner_manifest_composition":
            "1 report + 7 other attempts files; self-hash intentionally omitted",
        "precomparison_manifest_sha256": PRECOMPARISON_MANIFEST_SHA256,
        "precomparison_manifest_entries": len(precomparison),
        "candidate_input_freeze_entries": len(candidate_input_freeze),
        "all_hashes_pass": True,
    }


def load_json_static(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def static_python_review(path: Path) -> dict[str, object]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    calls = [
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    ]
    return {
        "syntax_parse": "PASS",
        "imports": sorted(set(imports)),
        "dynamic_execution_calls": sorted(
            set(calls) & {"eval", "exec", "compile", "__import__"}
        ),
    }


def static_candidate_code_review() -> dict[str, object]:
    code_path = CANDIDATE_DIR / "exact_check.py"
    test_path = CANDIDATE_DIR / "test_exact_check.py"
    code = static_python_review(code_path)
    tests = static_python_review(test_path)
    test_tree = ast.parse(test_path.read_text(encoding="utf-8"))
    test_methods = sorted(
        node.name
        for node in ast.walk(test_tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    )
    return {
        "mode": "AST_AND_TEXT_ONLY",
        "candidate_code_imported": False,
        "candidate_code_executed": False,
        "exact_check": code,
        "test_exact_check": tests,
        "test_method_count": len(test_methods),
        "test_methods": test_methods,
    }


def zeros(rows: int, columns: int) -> Matrix:
    return [[0 for _ in range(columns)] for _ in range(rows)]


def transpose(matrix: Sequence[Sequence[int]]) -> Matrix:
    return [list(column) for column in zip(*matrix)]


def matmul(
    left: Sequence[Sequence[int]],
    right: Sequence[Sequence[int]],
) -> Matrix:
    right_t = transpose(right)
    return [
        [sum(a * b for a, b in zip(row, column)) for column in right_t]
        for row in left
    ]


def pg_3_2_lines() -> list[tuple[int, int, int]]:
    """Lines of PG(3,2), independently from nonzero F_2^4 vectors."""
    lines = {
        tuple(sorted((left - 1, right - 1, (left ^ right) - 1)))
        for left, right in itertools.combinations(range(1, 16), 2)
    }
    if len(lines) != 35:
        raise AssertionError("PG(3,2) line count is not 35")
    return sorted(lines)


def build_candidate_canonical_support() -> tuple[Matrix, Matrix, list[tuple]]:
    """Rebuild inert declared labeling, without using candidate functions."""
    fano_lines = (
        (0, 1, 2),
        (0, 3, 4),
        (0, 5, 6),
        (1, 3, 5),
        (1, 4, 6),
        (2, 3, 6),
        (2, 4, 5),
    )
    cross = [
        [0 if point in fano_lines[line] else 1 for line in range(7)]
        for point in range(7)
    ]
    adjacency = zeros(14, 14)
    for point in range(7):
        for line in range(7):
            adjacency[point][7 + line] = cross[point][line]
            adjacency[7 + line][point] = cross[point][line]

    labels: list[tuple] = []
    for point in range(7):
        for line in range(7):
            multiplicity = 1 if cross[point][line] else 2
            kind = (
                "support_edge_completion"
                if multiplicity == 1
                else "support_nonedge_completion"
            )
            for copy in range(multiplicity):
                labels.append((point, line, copy, kind))

    incidence = zeros(14, 70)
    for column, (point, line, _copy, _kind) in enumerate(labels):
        incidence[point][column] = 1
        incidence[7 + line][column] = 1
    return adjacency, incidence, labels


def hostile_design_reconstruction(candidate: dict[str, object]) -> dict[str, object]:
    hostile = candidate["hostile_design_only_control"]
    if not isinstance(hostile, dict):
        raise AssertionError("hostile control payload is not an object")
    permutation = hostile["point_permutation"]
    if not isinstance(permutation, list) or sorted(permutation) != list(range(15)):
        raise AssertionError("hostile point map is not a permutation")

    first = pg_3_2_lines()
    second = sorted(
        tuple(sorted(permutation[point] for point in block))
        for block in first
    )
    if set(first) & set(second):
        raise AssertionError("the two PG(3,2) line designs are not disjoint")
    blocks = first + second
    if len(set(blocks)) != 70:
        raise AssertionError("the hostile union is not simple")

    incidence = zeros(70, 15)
    for row, block in enumerate(blocks):
        for point in block:
            incidence[row][point] = 1
    row_sums = [sum(row) for row in incidence]
    column_sums = [sum(column) for column in transpose(incidence)]
    pair_intersections = {
        sum(incidence[row][left] * incidence[row][right] for row in range(70))
        for left, right in itertools.combinations(range(15), 2)
    }

    adjacency, support_to_o, labels = build_candidate_canonical_support()
    coupling = matmul(support_to_o, incidence)
    histogram = {
        str(value): sum(entry == value for row in coupling for entry in row)
        for value in sorted({entry for row in coupling for entry in row})
    }
    mismatch_count = sum(entry != 2 for row in coupling for entry in row)

    fixed = candidate["fixed_support"]
    if not isinstance(fixed, dict):
        raise AssertionError("fixed support payload is not an object")
    checks = {
        "70_distinct_blocks": len(set(blocks)) == 70,
        "row_weight_3": row_sums == [3] * 70,
        "column_weight_14": column_sums == [14] * 15,
        "pair_intersection_2": pair_intersections == {2},
        "candidate_B_hash_matches": hash_payload(incidence) == hostile["B_sha256"],
        "candidate_support_adjacency_hash_matches":
            hash_payload(adjacency) == fixed["support_adjacency_sha256"],
        "candidate_support_to_O_hash_matches":
            hash_payload(support_to_o) == fixed["support_to_O_sha256"],
        "candidate_O_label_hash_matches":
            hash_payload(labels) == fixed["O_label_sha256"],
        "candidate_FB_histogram_matches":
            histogram == hostile["arbitrary_O_label_order_FB_histogram"],
        "candidate_FB_mismatch_matches":
            mismatch_count == hostile[
                "arbitrary_O_label_order_FB_mismatch_count"
            ],
        "FB_equals_2J": mismatch_count == 0,
    }
    if not all(value for key, value in checks.items() if key != "FB_equals_2J"):
        raise AssertionError(f"hostile design reconstruction failed: {checks}")
    if checks["FB_equals_2J"]:
        raise AssertionError("hostile design unexpectedly satisfies coupling")

    return {
        "construction": "two disjoint PG(3,2) line designs",
        "permutation": permutation,
        "block_count": len(blocks),
        "B_sha256": hash_payload(incidence),
        "row_weight_set": sorted(set(row_sums)),
        "column_weight_set": sorted(set(column_sums)),
        "pair_intersection_set": sorted(pair_intersections),
        "FB_histogram": histogram,
        "FB_mismatch_count": mismatch_count,
        "checks": checks,
        "verdict": "EXACT_ABSTRACT_DESIGN_BUT_NOT_FIXED_LABEL_COUPLING",
    }


def quadratic_multiply(
    left: tuple[int, int],
    right: tuple[int, int],
) -> tuple[int, int]:
    """Multiply a+b*sqrt(2) and c+d*sqrt(2)."""
    a, b = left
    c, d = right
    return a * c + 2 * b * d, a * d + b * c


def quadratic_power(base: tuple[int, int], exponent: int) -> tuple[int, int]:
    result = (1, 0)
    for _ in range(exponent):
        result = quadratic_multiply(result, base)
    return result


def spectral_reconstruction(candidate: dict[str, object]) -> dict[str, object]:
    forced = candidate["forced_O_graph_spectrum"]
    if not isinstance(forced, dict):
        raise AssertionError("forced spectrum payload is not an object")
    if forced["spectrum"] != EXPECTED_SPECTRUM:
        raise AssertionError("candidate spectrum differs from clean-room spectrum")

    moments: dict[str, int] = {}
    for exponent in range(5):
        plus = quadratic_power((-1, 1), exponent)
        minus = quadratic_power((-1, -1), exponent)
        if plus[1] + minus[1] != 0:
            raise AssertionError("quadratic conjugates failed to cancel")
        value = (
            9 ** exponent
            + 14 * ((-1) ** exponent)
            + 6 * (plus[0] + minus[0])
            + 27 * (3 ** exponent)
            + 16 * ((-4) ** exponent)
        )
        moments[str(exponent)] = value
    expected_moments = {"0": 70, "1": 0, "2": 630, "3": 336, "4": 13062}
    if moments != expected_moments or moments != forced["spectral_moments"]:
        raise AssertionError("spectral moment reconstruction failed")

    edges = moments["2"] // 2
    triangles = moments["3"] // 6
    closed_walk_base = 2 * edges + 4 * 70 * (9 * 8 // 2)
    four_cycles, remainder = divmod(moments["4"] - closed_walk_base, 8)
    if remainder:
        raise AssertionError("four-cycle formula is nonintegral")
    if (edges, triangles, four_cycles) != (315, 56, 294):
        raise AssertionError("small-cycle reconstruction drifted")

    determinant = "2^32*3^29"
    if forced["determinant"] != determinant:
        raise AssertionError("determinant factorization drifted")

    return {
        "spectrum": EXPECTED_SPECTRUM,
        "moments": moments,
        "edge_count": edges,
        "triangle_count": triangles,
        "four_cycle_formula":
            "tr(H^4)=2|E|+4*n*binom(d,2)+8*C4",
        "four_cycle_count": four_cycles,
        "determinant": determinant,
        "connected_reason":
            "the degree-9 eigenvalue has multiplicity one in a 9-regular graph",
    }


def semantic_comparison(
    candidate: dict[str, object],
    independent: dict[str, object],
) -> dict[str, object]:
    candidate_partition = candidate["equitable_partition"]
    independent_partition = independent["quotient"]
    if not isinstance(candidate_partition, dict) or not isinstance(
        independent_partition, dict
    ):
        raise AssertionError("partition payload malformed")
    partition_pass = (
        candidate_partition["cell_sizes"] == independent_partition["cell_sizes"]
        == [14, 70, 15]
        and candidate_partition["quotient"] == independent_partition["quotient"]
        == [[4, 10, 0], [2, 9, 3], [0, 14, 0]]
        and candidate_partition["Q_is_independent"]
        and independent_partition["Q_independent"]
    )

    candidate_design = candidate["O_Q_design"]
    independent_design = independent["O_Q_design"]
    if not isinstance(candidate_design, dict) or not isinstance(
        independent_design, dict
    ):
        raise AssertionError("design payload malformed")
    design_pass = (
        candidate_design["matrix_dimensions"]
        == independent_design["B_shape"]
        == [70, 15]
        and candidate_design["row_weight"]
        == independent_design["B_row_weight"]
        == 3
        and candidate_design["column_weight"]
        == independent_design["B_column_weight"]
        == 14
        and candidate_design["pairwise_column_intersection"]
        == independent_design["pair_lambda"]
        == 2
        and candidate_design["design"]
        == "simple 2-(15,3,2) with 70 blocks"
        and independent_design["design"] == "simple 2-(15,3,2)"
    )

    candidate_criterion = candidate["extension_criterion"]
    independent_criterion = independent["finite_binary_criterion"]
    if not isinstance(candidate_criterion, dict) or not isinstance(
        independent_criterion, dict
    ):
        raise AssertionError("criterion payload malformed")
    equations_pass = (
        candidate_criterion["block_equations"] == EXPECTED_CANDIDATE_EQUATIONS
        and independent_criterion["block_equations"]
        == {
            "OO": "D^T*D+H^2+B*B^T=12I_70-H+2J_70",
            "OQ": "H*B=2J_(70x15)-B",
            "QQ": "B^T*B=12I_15+2J_15",
            "SO": "F*D+D*H=2J_(14x70)-D",
            "SQ": "D*B=2J_(14x15)",
            "SS": "F^2+D*D^T=12I_14-F+2J_14",
        }
    )
    search_space_pass = (
        candidate_criterion["finite_search_space"]["total_raw_binary_variables"]
        == 3465
        and candidate_criterion["finite_search_space"]["automorphism_assumption"]
        == "none"
        and independent["uses_automorphism_restriction"] is False
    )

    candidate_spectrum = candidate["forced_O_graph_spectrum"]
    independent_spectrum = independent["H_spectrum"]
    if not isinstance(candidate_spectrum, dict) or not isinstance(
        independent_spectrum, dict
    ):
        raise AssertionError("spectrum payload malformed")
    independent_spectrum_dict = {
        item["eigenvalue"]: item["multiplicity"]
        for item in independent_spectrum["spectrum"]
    }
    spectrum_pass = (
        candidate_spectrum["spectrum"]
        == independent_spectrum_dict
        == EXPECTED_SPECTRUM
        and candidate_spectrum["edge_count"]
        == independent_spectrum["edge_count"]
        == 315
        and candidate_spectrum["triangle_count"]
        == independent_spectrum["triangle_count"]
        == 56
    )

    candidate_status = candidate["status"]
    independent_status = independent["status"]
    if not isinstance(candidate_status, dict) or not isinstance(
        independent_status, dict
    ):
        raise AssertionError("status payload malformed")
    status_wall_pass = (
        candidate_status["full_extension_found"] is False
        and candidate_status["rooted_endpoint"] == "UNKNOWN"
        and candidate_status["n3_708"] == "UNKNOWN"
        and candidate_status["Conway_99"] == "UNKNOWN"
        and candidate_status["novelty"] == "UNKNOWN"
        and independent_status["criterion_has_binary_solution"] == "UNKNOWN"
        and independent_status["rooted_endpoint_extension_or_exclusion"]
        == "UNKNOWN"
        and independent_status["Conway_99"] == "UNKNOWN"
    )

    checks = {
        "partition_quotient_Q_independence": partition_pass,
        "simple_2_design": design_pass,
        "six_block_equations_under_notation_map": equations_pass,
        "raw_binary_space_and_no_automorphism": search_space_pass,
        "conditional_induced_graph_spectrum": spectrum_pass,
        "status_wall": status_wall_pass,
    }
    if not all(checks.values()):
        raise AssertionError(f"semantic comparison failed: {checks}")
    return {
        "notation_map_candidate_to_cleanroom": {
            "A_S": "F (support adjacency)",
            "F": "D (support-to-O incidence)",
            "D": "H (induced O adjacency)",
            "B": "B (O-Q incidence)",
        },
        "checks": checks,
        "block_scope":
            "necessary and sufficient for the 99-vertex SRG graph extension",
        "endpoint_scope":
            "projector, lattice, tensor, and Schur filters remain additional",
    }


def report_scope_review(candidate: dict[str, object]) -> dict[str, object]:
    report = re.sub(r"\s+", " ", CANDIDATE_REPORT.read_text(encoding="utf-8"))
    failed_routes = re.sub(
        r"\s+",
        " ",
        (CANDIDATE_DIR / "failed-routes.md").read_text(encoding="utf-8"),
    )
    required_report = [
        "complete finite criterion for the graph extension, not a solution",
        "This theorem is deliberately graph-scoped.",
        "full rooted extension found: NO",
        "rooted endpoint: UNKNOWN",
        "Conway-99 existence/nonexistence: UNKNOWN",
        "No automorphism is assumed beyond relabeling the forced Fano support.",
    ]
    missing_report = [
        fragment for fragment in required_report if fragment not in report
    ]
    required_failures = [
        "No satisfying pair is constructed.",
        "No complete enumeration, proof of infeasibility, or checkable solver certificate is supplied.",
        "not sufficient for the complete endpoint package",
        "A heuristic nonhit says nothing about existence or nonexistence.",
    ]
    missing_failures = [
        fragment for fragment in required_failures if fragment not in failed_routes
    ]
    limitations = candidate["limitations"]
    limitation_pass = (
        isinstance(limitations, list)
        and any("No D,B pair" in item for item in limitations)
        and any("No complete search" in item for item in limitations)
        and any("Projector, lattice, tensor" in item for item in limitations)
        and any("No automorphism" in item for item in limitations)
    )
    if missing_report or missing_failures or not limitation_pass:
        raise AssertionError(
            "scope wall missing: "
            f"report={missing_report}, failed={missing_failures}, "
            f"limitations={limitation_pass}"
        )
    return {
        "report_graph_only_scope": "PASS",
        "failed_routes_status_wall": "PASS",
        "machine_readable_limitations": "PASS",
        "binary_solution_claimed": False,
        "endpoint_solution_claimed": False,
    }


def triangle_census_review(candidate: dict[str, object]) -> dict[str, object]:
    census = candidate["triangle_and_edge_census"]
    if not isinstance(census, dict):
        raise AssertionError("triangle census payload malformed")
    d_edges = 70 * 9 // 2
    by_support = 14 * 3
    by_q = 15 * 7
    by_o = d_edges - by_support - by_q
    d_triangles = by_o // 3
    target_edges = 99 * 14 // 2
    target_triangles = target_edges // 3
    partition = {
        "two_S_one_O": 28,
        "one_S_two_O": by_support,
        "two_O_one_Q": by_q,
        "three_O": d_triangles,
    }
    if census["D_edge_partition_by_unique_common_neighbor_cell"] != {
        "S": 42,
        "Q": 105,
        "O": 168,
        "total": 315,
    }:
        raise AssertionError("candidate D edge partition drifted")
    if census["target_triangle_partition"] != partition:
        raise AssertionError("candidate target triangle partition drifted")
    if sum(partition.values()) != target_triangles:
        raise AssertionError("triangle partition does not close")
    return {
        "D_edge_partition": {"S": by_support, "Q": by_q, "O": by_o},
        "D_triangle_count": d_triangles,
        "target_edge_count": target_edges,
        "target_triangle_count": target_triangles,
        "target_triangle_partition": partition,
    }


def build_results() -> dict[str, object]:
    integrity = validate_release_integrity()
    candidate_object = load_json_static(CANDIDATE_RESULTS)
    independent_object = load_json_static(INDEPENDENT_RESULTS)
    if not isinstance(candidate_object, dict) or not isinstance(
        independent_object, dict
    ):
        raise AssertionError("comparison JSON roots must be objects")
    if CANDIDATE_RESULTS.read_bytes() != canonical_bytes(candidate_object):
        raise AssertionError("candidate exact results are not canonical LF-only JSON")

    code_review = static_candidate_code_review()
    if code_review["test_method_count"] != 15:
        raise AssertionError("candidate static test count is not 15")
    hostile = hostile_design_reconstruction(candidate_object)
    spectral = spectral_reconstruction(candidate_object)
    semantic = semantic_comparison(candidate_object, independent_object)
    scope = report_scope_review(candidate_object)
    triangles = triangle_census_review(candidate_object)

    return {
        "schema_version": 1,
        "role": "verifier",
        "comparison_mode": "STATIC_CLEAN_ROOM_NO_CANDIDATE_EXECUTION",
        "input_integrity": integrity,
        "candidate_static_code_review": code_review,
        "semantic_comparison": semantic,
        "spectral_reconstruction": spectral,
        "triangle_census_reconstruction": triangles,
        "hostile_PG_3_2_reconstruction": hostile,
        "scope_review": scope,
        "release_metadata_corrections": {
            "manifest_hash": {
                "superseded_release_note": "17f9...",
                "validated_candidate_inner_manifest_sha256":
                    "153860d39fe7274a2f55ee952bcad1135cf4134ccc36d9aec07f6da379c5ca04",
            },
            "inventory_count": {
                "validated_total": 9,
                "composition":
                    "1 report + 8 attempts files, including the inner manifest",
                "inner_manifest_entries": 8,
                "inner_manifest_note":
                    "self-hash omitted, so it lists the report plus 7 other attempts files",
            },
        },
        "verdict": {
            "candidate_core_structural_claims": "VERIFIED",
            "candidate_manifest_and_results_consistency": "VERIFIED",
            "material_discrepancy": "NONE_FOUND",
            "binary_criterion_solution": "UNKNOWN",
            "rooted_graph_extension_or_exclusion": "UNKNOWN",
            "rooted_endpoint": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "Candidate Python was parsed statically but never imported or executed.",
            "Verification certifies the structural reduction and conditional "
            "consequences, not existence of binary D,B matrices.",
            "The finite criterion is graph-complete but does not itself satisfy "
            "the projector, lattice, tensor, or Schur endpoint filters.",
            "No complete search or infeasibility certificate is present.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    encoded = canonical_bytes(build_results())
    if args.output:
        args.output.write_bytes(encoded)
    else:
        print(encoded.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
