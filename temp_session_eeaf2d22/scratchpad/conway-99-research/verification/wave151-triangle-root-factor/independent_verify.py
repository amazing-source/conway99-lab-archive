#!/usr/bin/env python3
"""Clean-room exact verifier for the Wave151 partial binary factor.

Discovery Python files are hash-checked but never imported or executed.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY = ROOT / "attempts/wave151-triangle-root-factor"
DISCOVERY_MANIFEST = DISCOVERY / "package-manifest.sha256"
DISCOVERY_RESULT = DISCOVERY / "exact-results.json"
FIXED_Q_SCOUT = DISCOVERY / "fixed-q1-q2-scout.json"
WAVE149_MANIFEST = ROOT / "attempts/wave149-terwilliger-triple/package-manifest.sha256"
WAVE149_RESULT = ROOT / "attempts/wave149-terwilliger-triple/exact-results.json"

EXPECTED_DISCOVERY_MANIFEST_SHA256 = (
    "0e9ea04bad3fb41fda4224684663d828d3d19baea02387303775dd599d34d490"
)
EXPECTED_DISCOVERY_RESULT_SHA256 = (
    "74bc48e2dd0434f3e36a183d724a1ae4a52d7ec9a1e109c92b14f64985da37a4"
)
EXPECTED_FIXED_Q_SCOUT_SHA256 = (
    "f8694a6c996afc55d75f35884029918eb9e8028092e8d1216e232f95f73e8c4d"
)
EXPECTED_WAVE149_MANIFEST_SHA256 = (
    "84bea47182b6a59b69f5df29d4f7a8cdf71bff63cfbc47947b1e65013d09d70f"
)
EXPECTED_WAVE149_RESULT_SHA256 = (
    "6fed4da32fbeefce54d1802136dc8c9a328f112bb0f295a86230f0e6175f5ee6"
)
EXPECTED_TARGET_GRAM_SHA256 = (
    "1cfd0442e69b621c4a82fbeddeec9e7afbfcd04cd8eb458e29170cfd345c7ffc"
)
MIN_FREE_MEMORY_PERCENT = 15.0


class MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_ulong),
        ("memory_load", ctypes.c_ulong),
        ("total_phys", ctypes.c_ulonglong),
        ("avail_phys", ctypes.c_ulonglong),
        ("total_page_file", ctypes.c_ulonglong),
        ("avail_page_file", ctypes.c_ulonglong),
        ("total_virtual", ctypes.c_ulonglong),
        ("avail_virtual", ctypes.c_ulonglong),
        ("avail_extended_virtual", ctypes.c_ulonglong),
    ]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def value_sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def memory_record(label: str) -> dict[str, float | str]:
    status = MemoryStatusEx()
    status.length = ctypes.sizeof(status)
    ok = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
    require(bool(ok), "GlobalMemoryStatusEx failed")
    free_percent = 100.0 * status.avail_phys / status.total_phys
    require(
        free_percent >= MIN_FREE_MEMORY_PERCENT,
        f"free physical memory {free_percent:.2f}% below 15% floor",
    )
    return {
        "label": label,
        "free_physical_memory_percent": free_percent,
        "available_physical_gib": status.avail_phys / 2**30,
        "total_physical_gib": status.total_phys / 2**30,
    }


def verify_manifest() -> tuple[list[dict[str, str]], list[str]]:
    require(
        sha256_file(DISCOVERY_MANIFEST) == EXPECTED_DISCOVERY_MANIFEST_SHA256,
        "Wave151 manifest hash drift",
    )
    records = []
    paths = []
    for line in DISCOVERY_MANIFEST.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        path = ROOT / relative
        require(path.is_file(), f"missing discovery artifact {relative}")
        require(sha256_file(path) == digest, f"artifact hash drift {relative}")
        records.append({"path": relative, "sha256": digest})
        paths.append(relative)
    return records, paths


def nonmatching_edges() -> tuple[tuple[int, int], ...]:
    matching = {(left, left + 1) for left in range(0, 12, 2)}
    result = tuple(
        (left, right)
        for left in range(12)
        for right in range(left + 1, 12)
        if (left, right) not in matching
    )
    require(len(result) == 60, "K12-M edge count")
    return result


def incidence(edge_columns: Sequence[tuple[int, int]]) -> list[list[int]]:
    return [
        [int(row in edge) for edge in edge_columns]
        for row in range(12)
    ]


def row_gram(
    left: Sequence[Sequence[int]], right: Sequence[Sequence[int]]
) -> list[list[int]]:
    return [
        [sum(a * b for a, b in zip(left_row, right_row)) for right_row in right]
        for left_row in left
    ]


def transpose(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*matrix)]


def block_matrix(
    top_left: Sequence[Sequence[int]],
    top_right: Sequence[Sequence[int]],
    bottom_left: Sequence[Sequence[int]],
    bottom_right: Sequence[Sequence[int]],
) -> list[list[int]]:
    result = []
    for left, right in zip(top_left, top_right):
        result.append(list(left) + list(right))
    for left, right in zip(bottom_left, bottom_right):
        result.append(list(left) + list(right))
    return result


def target_block(
    matrix: Sequence[Sequence[int]],
    row_start: int,
    column_start: int,
    size: int = 12,
) -> list[list[int]]:
    return [
        list(row[column_start : column_start + size])
        for row in matrix[row_start : row_start + size]
    ]


def expected_diagonal_block() -> list[list[int]]:
    return [
        [
            10
            if row == column
            else (0 if column == (row ^ 1) else 1)
            for column in range(12)
        ]
        for row in range(12)
    ]


def validate_permutation(permutation: Sequence[int], label: str) -> None:
    require(
        sorted(permutation) == list(range(60)),
        f"{label} is not a permutation",
    )


def validate_partial_factor(
    binary: Sequence[Sequence[int]],
    target_partial_gram: Sequence[Sequence[int]],
    expected_hash: str,
) -> None:
    require(len(binary) == 24, "partial factor row count")
    require(all(len(row) == 60 for row in binary), "partial factor column count")
    require(
        all(value in (0, 1) for row in binary for value in row),
        "partial factor not binary",
    )
    require(all(sum(row) == 10 for row in binary), "partial factor row sum")
    require(
        all(sum(binary[row][column] for row in range(12)) == 2 for column in range(60)),
        "group-zero column sum",
    )
    require(
        all(
            sum(binary[row][column] for row in range(12, 24)) == 2
            for column in range(60)
        ),
        "group-one column sum",
    )
    require(row_gram(binary, binary) == target_partial_gram, "partial Gram mismatch")
    require(value_sha256(binary) == expected_hash, "partial factor hash mismatch")


def squared_residual(
    actual: Sequence[Sequence[int]], target: Sequence[Sequence[int]]
) -> tuple[int, list[list[int]]]:
    residual = [
        [
            actual[row][column] - target[row][column]
            for column in range(len(actual[0]))
        ]
        for row in range(len(actual))
    ]
    return sum(value * value for row in residual for value in row), residual


def fixed_q_allowed_mappings(
    c0: Sequence[Sequence[int]],
    c1: Sequence[Sequence[int]],
    target02: Sequence[Sequence[int]],
    target12: Sequence[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    result = []
    for domain in range(60):
        left0 = tuple(row for row in range(12) if c0[row][domain])
        left1 = tuple(row for row in range(12) if c1[row][domain])
        allowed = []
        for image in range(60):
            right = tuple(row for row in range(12) if c0[row][image])
            if (
                all(target02[left][target] > 0 for left in left0 for target in right)
                and all(
                    target12[left][target] > 0
                    for left in left1
                    for target in right
                )
            ):
                allowed.append(image)
        result.append(tuple(allowed))
    return tuple(result)


def build_result() -> dict[str, object]:
    memory = [memory_record("start")]
    manifest_records, manifest_paths = verify_manifest()
    require(
        sha256_file(DISCOVERY_RESULT) == EXPECTED_DISCOVERY_RESULT_SHA256,
        "Wave151 result hash drift",
    )
    require(
        sha256_file(FIXED_Q_SCOUT) == EXPECTED_FIXED_Q_SCOUT_SHA256,
        "fixed-Q scout result hash drift",
    )
    require(
        sha256_file(WAVE149_MANIFEST) == EXPECTED_WAVE149_MANIFEST_SHA256,
        "Wave149 manifest hash drift",
    )
    require(
        sha256_file(WAVE149_RESULT) == EXPECTED_WAVE149_RESULT_SHA256,
        "Wave149 result hash drift",
    )
    stored = json.loads(DISCOVERY_RESULT.read_text(encoding="utf-8"))
    scout = json.loads(FIXED_Q_SCOUT.read_text(encoding="utf-8"))
    parent = json.loads(WAVE149_RESULT.read_text(encoding="utf-8"))

    gram = parent["minimal_surviving_witness"]["gram_rows"]
    require(len(gram) == 36 and all(len(row) == 36 for row in gram), "target Gram shape")
    require(value_sha256(gram) == EXPECTED_TARGET_GRAM_SHA256, "target Gram hash")
    require(
        stored["finite_problem"]["target_gram_sha256"]
        == EXPECTED_TARGET_GRAM_SHA256,
        "stored target Gram hash",
    )

    partial = stored["exact_partial_factor"]
    edges = nonmatching_edges()
    require(
        [list(edge) for edge in edges] == partial["edge_columns"],
        "stored edge universe mismatch",
    )
    q1 = tuple(int(value) for value in partial["Q1"])
    validate_permutation(q1, "Q1")
    c0 = incidence(edges)
    c1_edges = tuple(edges[index] for index in q1)
    c1 = incidence(c1_edges)
    binary = c0 + c1

    g00_target = target_block(gram, 0, 0)
    g11_target = target_block(gram, 12, 12)
    g01_target = target_block(gram, 0, 12)
    g10_target = target_block(gram, 12, 0)
    expected_diagonal = expected_diagonal_block()
    require(g00_target == expected_diagonal, "G00 formula")
    require(g11_target == expected_diagonal, "G11 formula")
    g00 = row_gram(c0, c0)
    g11 = row_gram(c1, c1)
    g01 = row_gram(c0, c1)
    g10 = row_gram(c1, c0)
    require(g00 == g00_target, "G00 replay")
    require(g11 == g11_target, "G11 replay")
    require(g01 == g01_target, "G01 replay")
    require(g10 == g10_target == transpose(g01), "G10 replay")
    partial_target = block_matrix(g00_target, g01_target, g10_target, g11_target)
    validate_partial_factor(
        binary,
        partial_target,
        partial["binary_matrix_sha256"],
    )
    require(partial["shape"] == [24, 60], "stored partial shape")
    require(partial["groups_constructed"] == 2, "stored group count")

    q2 = tuple(
        int(value)
        for value in stored["third_group_search"]["best_retained_Q2_permutation"]
    )
    validate_permutation(q2, "retained Q2")
    c2 = incidence(tuple(edges[index] for index in q2))
    g02_target = target_block(gram, 0, 24)
    g12_target = target_block(gram, 12, 24)
    g02_actual = row_gram(c0, c2)
    g12_actual = row_gram(c1, c2)
    residual02_score, residual02 = squared_residual(g02_actual, g02_target)
    residual12_score, residual12 = squared_residual(g12_actual, g12_target)
    retained_score = residual02_score + residual12_score
    require((residual02_score, residual12_score, retained_score) == (40, 40, 80),
            "retained Q2 residual")
    require(
        retained_score
        == stored["third_group_search"]["best_exact_squared_residual"],
        "stored retained residual",
    )

    allowed = fixed_q_allowed_mappings(c0, c1, g02_target, g12_target)
    boolean_variables = sum(map(len, allowed))
    require(boolean_variables == 1620, "fixed-Q Boolean variable count")
    require(scout["boolean_variables"] == boolean_variables, "stored Boolean variables")
    require(scout["status"].lower() == "unsat", "stored solver status")
    require(scout["candidate_Q2"] is None, "unexpected solver candidate")
    require(scout["negative_status_is_not_certificate"] is True,
            "solver diagnostic boundary")
    require(
        scout["scope"] == "extension of the one stored Q1 only",
        "solver scope drift",
    )
    proof_extensions = {
        ".proof", ".drat", ".lrat", ".frat", ".lfsc", ".alethe"
    }
    proof_paths = [
        path
        for path in manifest_paths
        if Path(path).suffix.lower() in proof_extensions
    ]
    proof_fields = [
        key
        for key in ("proof", "proof_trace", "certificate", "unsat_core")
        if scout.get(key)
    ]
    require(not proof_paths and not proof_fields, "unexpected proof artifact")

    hostile_q1 = list(q1)
    hostile_q1[0], hostile_q1[1] = hostile_q1[1], hostile_q1[0]
    hostile_c1 = incidence(tuple(edges[index] for index in hostile_q1))
    hostile_binary = c0 + hostile_c1
    hostile_rejected = False
    try:
        validate_partial_factor(
            hostile_binary,
            partial_target,
            partial["binary_matrix_sha256"],
        )
    except AssertionError:
        hostile_rejected = True
    require(hostile_rejected, "hostile Q1 swap survived")
    hostile_nonpermutation = list(q1)
    hostile_nonpermutation[0] = hostile_nonpermutation[1]
    hostile_permutation_rejected = False
    try:
        validate_permutation(hostile_nonpermutation, "hostile Q1")
    except AssertionError:
        hostile_permutation_rejected = True
    require(hostile_permutation_rejected, "duplicate Q1 survived")

    memory.append(memory_record("complete"))
    return {
        "format": "wave151-independent-triangle-root-factor-v1",
        "role": "verifier",
        "claim_label": "VERIFIED_PARTIAL_CONSTRUCTION_UNKNOWN_FULL",
        "scope": (
            "Exact 24x60 binary factor for the frozen Wave149 G00,G11,G01 "
            "blocks; fixed-Q1 solver status remains diagnostic"
        ),
        "frozen_inputs": {
            "wave151_manifest_sha256": EXPECTED_DISCOVERY_MANIFEST_SHA256,
            "wave151_manifest_entries": manifest_records,
            "wave149_manifest_sha256": EXPECTED_WAVE149_MANIFEST_SHA256,
            "wave149_result_sha256": EXPECTED_WAVE149_RESULT_SHA256,
            "discovery_code_imported_or_executed": False,
        },
        "factor_semantics": {
            "group_order": 12,
            "groups_constructed": 2,
            "columns": 60,
            "matching_removed": [[left, left + 1] for left in range(0, 12, 2)],
            "edge_columns": [list(edge) for edge in edges],
            "Q1": list(q1),
            "Q1_is_permutation": True,
            "group_zero": "vertex-edge incidence of K12 minus the fixed matching",
            "group_one": "column c is incidence of edge edge_columns[Q1[c]]",
        },
        "partial_factor": {
            "shape": [24, 60],
            "binary_rows": binary,
            "binary_matrix_sha256": value_sha256(binary),
            "all_entries_binary": True,
            "row_sums": [sum(row) for row in binary],
            "all_row_sums_10": True,
            "group_zero_column_sums": [
                sum(c0[row][column] for row in range(12))
                for column in range(60)
            ],
            "group_one_column_sums": [
                sum(c1[row][column] for row in range(12))
                for column in range(60)
            ],
            "all_group_column_sums_2": True,
            "combined_column_sums": [
                sum(binary[row][column] for row in range(24))
                for column in range(60)
            ],
            "partial_gram_sha256": value_sha256(row_gram(binary, binary)),
        },
        "gram_blocks": {
            "target_full_gram_sha256": value_sha256(gram),
            "G00": {
                "sha256": value_sha256(g00),
                "exact_match": True,
                "entries_checked": 144,
            },
            "G11": {
                "sha256": value_sha256(g11),
                "exact_match": True,
                "entries_checked": 144,
            },
            "G01": {
                "sha256": value_sha256(g01),
                "exact_match": True,
                "entries_checked": 144,
            },
            "G10": {
                "sha256": value_sha256(g10),
                "exact_match": True,
                "entries_checked": 144,
            },
            "total_entries_checked": 576,
        },
        "retained_Q2_residual": {
            "scope": "the stored Q2 permutation with the single stored Q1",
            "Q2": list(q2),
            "Q2_is_permutation": True,
            "G02_squared_residual": residual02_score,
            "G12_squared_residual": residual12_score,
            "total_squared_residual": retained_score,
            "G02_residual_sha256": value_sha256(residual02),
            "G12_residual_sha256": value_sha256(residual12),
            "G02_nonzero_entries": sum(value != 0 for row in residual02 for value in row),
            "G12_nonzero_entries": sum(value != 0 for row in residual12 for value in row),
            "is_exact_third_group": False,
            "certificate_authority": False,
        },
        "fixed_Q1_solver_audit": {
            "independently_reconstructed_boolean_variables": boolean_variables,
            "domain_exact_one_constraints": 60,
            "image_exact_one_constraints": 60,
            "vertex_pair_capacity_constraints": 288,
            "stored_status": scout["status"],
            "stored_elapsed_seconds": scout["elapsed_seconds"],
            "scope": scout["scope"],
            "proof_artifact_present": False,
            "proof_paths": proof_paths,
            "proof_fields": proof_fields,
            "verdict": "UNVERIFIED_SOLVER_DIAGNOSTIC",
            "reason": (
                "a bare solver status without an independently replayable "
                "proof does not certify UNSAT"
            ),
        },
        "unrestricted_joint_residual": {
            "stored_score": stored["third_group_search"][
                "unrestricted_joint_best_squared_residual"
            ],
            "replay_status": "UNREPLAYABLE_SCORE_ONLY",
            "reason": "no corresponding pair of permutations is stored",
            "certificate_authority": False,
        },
        "hostile_tests": {
            "Q1_value_swap_rejected": hostile_rejected,
            "Q1_duplicate_rejected": hostile_permutation_rejected,
        },
        "verdict": {
            "24x60_binary_factor": "VERIFIED",
            "36x60_C": "UNKNOWN",
            "60x60_D": "UNKNOWN_NOT_REACHED",
            "graph_realization": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "strict_n3_upper_bound": "NOT_IMPROVED",
        },
        "limitations": [
            "The construction covers only two of the three 12-row groups.",
            "The fixed-Q1 UNSAT status has no exported checkable proof.",
            "The exact residual 80 is a failed candidate score, not negative evidence.",
            "The unrestricted residual 108 has no stored permutations and is not replayed.",
            "No full C, residual D, graph, Conway-99 resolution, or strict bound follows.",
        ],
        "resource_report": {
            "memory_samples": memory,
            "minimum_free_physical_memory_percent": min(
                float(record["free_physical_memory_percent"])
                for record in memory
            ),
            "required_floor_percent": MIN_FREE_MEMORY_PERCENT,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = build_result()
    if args.verify is not None:
        stored = json.loads(args.verify.read_text(encoding="utf-8"))
        result_without_memory = dict(result)
        stored_without_memory = dict(stored)
        result_without_memory.pop("resource_report")
        stored_without_memory.pop("resource_report")
        require(result_without_memory == stored_without_memory, "stored result mismatch")
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "semantic_sha256": value_sha256(result_without_memory),
                },
                sort_keys=True,
            )
        )
        return
    output = args.output or HERE / "independent-results.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "WROTE",
                "path": str(output),
                "semantic_sha256": value_sha256(
                    {key: value for key, value in result.items() if key != "resource_report"}
                ),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
