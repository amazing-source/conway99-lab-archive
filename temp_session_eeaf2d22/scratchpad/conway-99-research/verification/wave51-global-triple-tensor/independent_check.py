#!/usr/bin/env python3
"""Clean-room verifier for the Wave 51 aggregate triple tensor.

This module intentionally does not import the discovery implementation.
It reconstructs the tensor and all local tables from the JSON certificate,
then checks the combinatorial, spectral, balance, and associativity claims
with Python integer arithmetic.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
import os
from pathlib import Path
from typing import Any


RELATIONS = ("I", "K", "D", "C", "B")
RELATION_INDEX = {name: index for index, name in enumerate(RELATIONS)}
VALENCIES = (1, 18, 32, 144, 36)
TRIANGLE_COUNT = 231
EXPECTED_INPUT_SHA256 = (
    "8d42c51b5e6b5137466a4adf95442f4d67cf2708c29ac134f7972b8cfbc16d1e"
)
MEMORY_FLOOR_PERCENT = 20.0


class VerificationError(AssertionError):
    """Raised when a certificate or one of its claims is invalid."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def free_physical_memory_percent() -> float | None:
    if os.name != "nt":
        return None

    class MemoryStatusEx(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(status)
    require(bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))),
            "GlobalMemoryStatusEx failed")
    return 100.0 * status.ullAvailPhys / status.ullTotalPhys


def enforce_memory_floor() -> float | None:
    free = free_physical_memory_percent()
    if free is not None:
        require(
            free >= MEMORY_FLOOR_PERCENT,
            f"free physical memory {free:.2f}% is below {MEMORY_FLOOR_PERCENT:.2f}%",
        )
    return free


def derive_endpoint_arithmetic() -> dict[str, Any]:
    """Rebuild the endpoint arithmetic from SRG(99,14,1,2)."""

    vertices, degree, lam, mu = 99, 14, 1, 2
    edges = vertices * degree // 2
    require(2 * edges == vertices * degree, "edge handshaking failed")
    triangles = edges * lam // 3
    require(3 * triangles == edges * lam, "triangle count is nonintegral")
    require(triangles == TRIANGLE_COUNT, "triangle count is not 231")

    # Restricted SRG roots solve x^2 + (mu-lambda)x + (mu-degree)=0.
    restricted_roots = (3, -4)
    f = 54
    g = vertices - 1 - f
    require(f == 54 and g == 44, "SRG multiplicities changed")
    require(degree + f * restricted_roots[0] + g * restricted_roots[1] == 0,
            "SRG trace equation failed")
    require(
        degree * degree
        + f * restricted_roots[0] ** 2
        + g * restricted_roots[1] ** 2
        == vertices * degree,
        "SRG trace-of-square equation failed",
    )

    # For vertex-triangle incidence N, NN^T=7I+A and N^TN=3I+K.
    triangles_per_vertex = degree * lam // 2
    require(triangles_per_vertex == 7, "triangles per graph vertex changed")
    k_degree = 3 * (triangles_per_vertex - 1)
    require(k_degree == 18, "triangle-intersection valency changed")
    k_spectrum = {18: 1, 7: f, 0: g, -3: triangles - vertices}
    require(k_spectrum == {18: 1, 7: 54, 0: 44, -3: 132},
            "triangle-intersection spectrum changed")
    require(sum(k_spectrum.values()) == triangles, "K multiplicities do not sum")
    require(sum(eigenvalue * multiplicity
                for eigenvalue, multiplicity in k_spectrum.items()) == 0,
            "K trace equation failed")
    require(
        sum(eigenvalue * eigenvalue * multiplicity
            for eigenvalue, multiplicity in k_spectrum.items())
        == triangles * k_degree,
        "K trace-of-square equation failed",
    )

    # Neighbors of a triangle split by which of its three vertices is shared.
    local_cliques = 3
    local_clique_size = triangles_per_vertex - 1
    require((local_cliques, local_clique_size) == (3, 6),
            "local graph is not the derived 3K6")
    local_spectrum = {5: 3, -1: 15}

    # Cross edges between disjoint triangles form a matching, so q<=3.
    # At a prism-free endpoint x_3=0.  The first q moment counts the six
    # disjoint triangles through each endpoint of the 36 edges leaving T.
    # The second factorial moment counts the unique mu=2 completion for each
    # of the 12 outside neighbors and each of the three edges of T.
    disjoint_pairs_per_fixed_triangle = triangles - 1 - k_degree
    outside_neighbors_per_triangle_vertex = degree - 2
    q_first_moment = (
        3 * outside_neighbors_per_triangle_vertex
        * (triangles_per_vertex - 1)
    )
    q_second_binomial_moment = 3 * outside_neighbors_per_triangle_vertex
    require(disjoint_pairs_per_fixed_triangle == 212, "disjoint valency changed")
    require(q_first_moment == 216, "first q moment changed")
    require(q_second_binomial_moment == 36, "second q moment changed")
    x3 = 0
    x2 = q_second_binomial_moment - 3 * x3
    x1 = q_first_moment - 2 * x2 - 3 * x3
    x0 = disjoint_pairs_per_fixed_triangle - x1 - x2 - x3
    require((x0, x1, x2, x3) == (32, 144, 36, 0),
            "prism-free q distribution changed")

    # K^2 is the number q of cross edges for disjoint triangle pairs.
    k_squared_relation_values = (18, 5, 0, 1, 2)
    s_spectrum: dict[int, int] = {}
    for k_eigenvalue, multiplicity in k_spectrum.items():
        j_eigenvalue = triangles if k_eigenvalue == k_degree else 0
        s_eigenvalue = (
            k_eigenvalue * k_eigenvalue
            - 17
            - 4 * k_eigenvalue
            - j_eigenvalue
        )
        s_spectrum[s_eigenvalue] = s_spectrum.get(s_eigenvalue, 0) + multiplicity
        require(k_eigenvalue * s_eigenvalue == 4 * k_eigenvalue,
                "KS=4K fails on a K eigenspace")
    require(s_spectrum == {4: 187, -17: 44}, "S spectrum changed")
    require(all(value * value + 13 * value - 68 == 0 for value in s_spectrum),
            "S polynomial fails")
    projector_spectrum = {
        k_eigenvalue: 4 - (
            k_eigenvalue * k_eigenvalue
            - 17
            - 4 * k_eigenvalue
            - (triangles if k_eigenvalue == k_degree else 0)
        )
        for k_eigenvalue in k_spectrum
    }
    require(projector_spectrum == {18: 0, 7: 0, 0: 21, -3: 0},
            "4I-S is not 21 times the K-zero projector")

    return {
        "srg_parameters": [vertices, degree, lam, mu],
        "edge_count": edges,
        "graph_triangle_count": triangles,
        "triangles_per_graph_vertex": triangles_per_vertex,
        "triangle_intersection_degree": k_degree,
        "triangle_intersection_local_graph": "3K6",
        "triangle_intersection_local_spectrum": {"5": 3, "-1": 15},
        "K_spectrum": {str(key): value for key, value in k_spectrum.items()},
        "cross_edges_between_disjoint_triangles": {
            "matching_bound": 3,
            "q_equals_3_iff_induced_triangular_prism": True,
        },
        "prism_free_q_distribution": {"0": x0, "1": x1, "2": x2, "3": x3},
        "q_moment_equations": {
            "sum_xq": disjoint_pairs_per_fixed_triangle,
            "sum_q_xq": q_first_moment,
            "sum_binomial_q_2_xq": q_second_binomial_moment,
        },
        "K_squared_relation_values": list(k_squared_relation_values),
        "S_definition": "K^2-17I-4K-J=B-D",
        "S_valency": VALENCIES[4] - VALENCIES[2],
        "S_spectrum": {str(key): value for key, value in s_spectrum.items()},
        "S_polynomial": "S^2+13S-68I=0",
        "KS_equals_SK_equals_4K": True,
        "four_I_minus_S": "21E_0",
    }


def parse_tensor(document: dict[str, Any]) -> dict[tuple[int, int, int], int]:
    entries = document.get("normalized_symmetric_tensor_nonzero_entries")
    require(isinstance(entries, list), "tensor entry list is missing")
    tensor: dict[tuple[int, int, int], int] = {}
    for offset, entry in enumerate(entries):
        require(isinstance(entry, dict), f"tensor entry {offset} is not an object")
        names = entry.get("relations")
        value = entry.get("value")
        require(isinstance(names, list) and len(names) == 3,
                f"tensor entry {offset} has invalid relation names")
        require(all(name in RELATION_INDEX for name in names),
                f"tensor entry {offset} has an unknown relation")
        indices = tuple(RELATION_INDEX[name] for name in names)
        require(tuple(sorted(indices)) == indices,
                f"tensor entry {offset} is not canonical")
        require(indices not in tensor, f"duplicate tensor entry {indices}")
        require(type(value) is int and value > 0,
                f"tensor entry {indices} is not a positive integer")
        tensor[indices] = value
    require(tensor, "tensor is empty")
    return tensor


def tensor_value(tensor: dict[tuple[int, int, int], int],
                 i: int, j: int, k: int) -> int:
    return tensor.get(tuple(sorted((i, j, k))), 0)


def reconstruct_tables(
    tensor: dict[tuple[int, int, int], int],
) -> list[list[list[int]]]:
    tables: list[list[list[int]]] = []
    for k, valency in enumerate(VALENCIES):
        table: list[list[int]] = []
        for i in range(5):
            row: list[int] = []
            for j in range(5):
                value = tensor_value(tensor, i, j, k)
                require(value % valency == 0,
                        f"t[{i},{j},{k}]={value} not divisible by v[{k}]")
                row.append(value // valency)
            table.append(row)
        tables.append(table)
    return tables


def association_failures(
    tables: list[list[list[int]]],
) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for i, j, m, k in itertools.product(range(5), repeat=4):
        left = sum(tables[h][i][j] * tables[k][h][m] for h in range(5))
        right = sum(tables[h][j][m] * tables[k][i][h] for h in range(5))
        if left != right:
            failures.append({
                "indices_i_j_m_k": [i, j, m, k],
                "left_association": left,
                "right_association": right,
            })
    return failures


def verify_document(document: dict[str, Any]) -> dict[str, Any]:
    require(document.get("format") == "wave51-global-triple-tensor-v1",
            "unexpected certificate format")
    relations = document.get("relations")
    require(isinstance(relations, dict), "relations section missing")
    require(tuple(relations.get("order", ())) == RELATIONS, "relation order changed")
    require(tuple(relations.get("valencies", ())) == VALENCIES,
            "relation valencies changed")

    endpoint = document.get("endpoint_input")
    require(isinstance(endpoint, dict), "endpoint_input missing")
    require(endpoint.get("graph_triangle_count") == TRIANGLE_COUNT,
            "claimed triangle count changed")
    require(endpoint.get("prism_count") == 0, "certificate is not prism-free")
    require(endpoint.get("fixed_row_disjoint_q_distribution")
            == {"0": 32, "1": 144, "2": 36},
            "claimed q distribution changed")
    require(endpoint.get("K_spectrum")
            == {"-3": 132, "0": 44, "18": 1, "7": 54},
            "claimed K spectrum changed")
    require(endpoint.get("S_spectrum") == {"-17": 44, "4": 187},
            "claimed S spectrum changed")
    require(endpoint.get("S_polynomial") == "S^2 + 13S - 68I = 0",
            "claimed S polynomial changed")

    tensor = parse_tensor(document)
    tables = reconstruct_tables(tensor)
    supplied_tables = document.get("local_average_tables_p_k_ij")
    require(isinstance(supplied_tables, dict), "supplied local tables missing")
    require(set(supplied_tables) == set(RELATIONS), "local table labels changed")
    for k, relation in enumerate(RELATIONS):
        require(supplied_tables[relation] == tables[k],
                f"supplied {relation} table differs from reconstructed table")

    # Repeated-vertex identities.
    for i, j in itertools.product(range(5), repeat=2):
        expected = VALENCIES[i] if i == j else 0
        require(tensor_value(tensor, 0, i, j) == expected,
                f"identity tensor entry failed at {(i, j)}")

    # Each of the five slices is an integral transportation table.
    for k, table in enumerate(tables):
        require(all(type(value) is int and value >= 0
                    for row in table for value in row),
                f"table {k} is not nonnegative integral")
        row_margins = tuple(sum(row) for row in table)
        column_margins = tuple(sum(table[i][j] for i in range(5))
                               for j in range(5))
        require(row_margins == VALENCIES,
                f"row margins fail in table {k}: {row_margins}")
        require(column_margins == VALENCIES,
                f"column margins fail in table {k}: {column_margins}")

    k_squared = (18, 5, 0, 1, 2)
    ks = (0, 4, 0, 0, 0)
    s_squared = (68, 0, 13, 0, -13)
    for k, table in enumerate(tables):
        require(table[1][1] == k_squared[k], f"K^2 fails in relation {k}")
        require(table[1][4] - table[1][2] == ks[k],
                f"KS fails in relation {k}")
        require(table[4][1] - table[2][1] == ks[k],
                f"SK fails in relation {k}")
        require(table[4][4] + table[2][2] - 2 * table[2][4]
                == s_squared[k], f"S^2 fails in relation {k}")
    require(tuple(tables[1][1]) == (1, 5, 0, 8, 4),
            "the local 3K6 row fails")
    require(tuple(tables[1][i][1] for i in range(5)) == (1, 5, 0, 8, 4),
            "the transposed local 3K6 row fails")

    # All 125 normalized global balance equations.
    balance_checks = 0
    for k, i, j in itertools.product(range(5), repeat=3):
        common = tensor_value(tensor, i, j, k)
        require(VALENCIES[k] * tables[k][i][j] == common,
                f"normalization fails at {(i, j, k)}")
        require(VALENCIES[i] * tables[i][k][j] == common,
                f"global balance fails at {(i, j, k)}")
        balance_checks += 1

    # Necessary orientation divisibilities for actual unordered triples.
    orientation_checks = 0
    for i, j, k in itertools.combinations_with_replacement(range(1, 5), 3):
        total = TRIANGLE_COUNT * tensor_value(tensor, i, j, k)
        divisor = 6 if i == j == k else 2
        require(total % divisor == 0,
                f"orientation divisibility fails at {(i, j, k)}")
        orientation_checks += 1

    # Check the displayed point in the independently restated affine family.
    a, f_parameter, i_parameter = 288, 0, 288
    family = {
        (1, 2, 2): a,
        (1, 2, 3): 576 - 2 * a,
        (1, 2, 4): a,
        (1, 3, 3): 1296 + 4 * a,
        (1, 3, 4): 576 - 2 * a,
        (1, 4, 4): a,
        (2, 2, 2): 416 - i_parameter + 2 * f_parameter,
        (2, 2, 3): 576 - a + i_parameter - 3 * f_parameter,
        (2, 2, 4): f_parameter,
        (2, 3, 3): 2304 + 4 * a + 4 * f_parameter,
        (2, 3, 4): 1152 - a - f_parameter - i_parameter,
        (2, 4, 4): i_parameter,
        (3, 3, 3): 15264 - 12 * a - 4 * f_parameter - 4 * i_parameter,
        (3, 3, 4): 1728 + 4 * a + 4 * i_parameter,
        (3, 4, 4): 1728 - a - 3 * i_parameter + f_parameter,
        (4, 4, 4): 2 * i_parameter - f_parameter - 468,
    }
    for key, expected in family.items():
        require(expected >= 0, f"family point is negative at {key}")
        require(tensor_value(tensor, *key) == expected,
                f"family point mismatch at {key}")

    failures = association_failures(tables)
    failure_json = json.dumps(
        failures, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    first_failure = {
        "indices_i_j_m_k": [1, 1, 2, 2],
        "left_association": 81,
        "right_association": 153,
    }
    require(len(failures) == 100,
            f"association diagnostic has {len(failures)} failures, not 100")
    require(failures[0] == first_failure, "first association failure changed")
    supplied_diagnostic = document.get("associativity_diagnostic")
    require(isinstance(supplied_diagnostic, dict),
            "supplied associativity diagnostic missing")
    require(supplied_diagnostic.get(
        "failure_count_over_625_ordered_index_tests") == 100,
        "supplied association failure count changed")
    require(supplied_diagnostic.get("first_failure") == first_failure,
            "supplied first association failure changed")

    result_claim = document.get("result")
    require(isinstance(result_claim, dict), "result claim missing")
    require(result_claim.get("exact_contradiction") is False,
            "exact contradiction status was inflated")
    require(result_claim.get("positive_aggregate_control") is True,
            "aggregate control status changed")
    boundary = document.get("claim_boundary")
    require(isinstance(boundary, dict), "claim boundary missing")
    require(boundary.get("prism_free_endpoint") == "UNKNOWN",
            "endpoint status must remain UNKNOWN")
    require(boundary.get("conway_99") == "UNKNOWN",
            "Conway-99 status must remain UNKNOWN")
    require(boundary.get("novelty") == "UNKNOWN",
            "novelty status must remain UNKNOWN")

    return {
        "format": "wave51-independent-verification-v1",
        "claim_label": "VERIFIED",
        "scope": (
            "exact arithmetic and positive-control interpretation for the "
            "aggregate Wave 51 relaxation only"
        ),
        "endpoint": "UNKNOWN",
        "conway_99": "UNKNOWN",
        "novelty": "UNKNOWN",
        "derivation": derive_endpoint_arithmetic(),
        "tensor": {
            "canonical_nonzero_entries": len(tensor),
            "nonnegative": True,
            "integral_local_slices": 5,
            "row_margin_vectors_checked": 5,
            "column_margin_vectors_checked": 5,
            "identity_entries_checked": 25,
            "global_balance_equations_checked": balance_checks,
            "orientation_divisibilities_checked": orientation_checks,
            "K_squared_entries_checked": 5,
            "KS_entries_checked": 5,
            "SK_entries_checked": 5,
            "S_squared_entries_checked": 5,
            "local_3K6_row_checked": True,
            "family_point": {"a": a, "f": f_parameter, "i": i_parameter},
        },
        "association_scheme_diagnostic": {
            "ordered_checks": 625,
            "failure_count": len(failures),
            "first_failure": failures[0],
            "failure_list_sha256": hashlib.sha256(failure_json).hexdigest(),
            "failures": failures,
            "interpretation": (
                "The displayed average tables are not the intersection "
                "numbers of an association scheme."
            ),
        },
        "logical_boundary": {
            "positive_aggregate_control": "VERIFIED",
            "association_scheme_for_displayed_averages": "REFUTED",
            "graph_realization_supplied": False,
            "pairwise_local_table_assignment_supplied": False,
            "quadruple_consistency_supplied": False,
            "automorphism_assumed": False,
            "endpoint": "UNKNOWN",
        },
    }


def load_and_verify(path: Path, require_frozen_hash: bool = True) -> dict[str, Any]:
    if require_frozen_hash:
        actual_hash = file_sha256(path)
        require(actual_hash == EXPECTED_INPUT_SHA256,
                f"input hash drifted: {actual_hash}")
    with path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)
    require(isinstance(document, dict), "certificate root is not an object")
    return verify_document(document)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    free = enforce_memory_floor()
    result = load_and_verify(args.input)
    result["input"] = {
        "path": args.input.as_posix(),
        "sha256": file_sha256(args.input),
    }
    result["memory_guard"] = {
        "floor_percent": MEMORY_FLOOR_PERCENT,
        "passed": True,
    }
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8", newline="\n")
        print(f"PASS_INDEPENDENT_VERIFY output={args.output.as_posix()}")
        print(f"sha256={file_sha256(args.output)}")
        if free is not None:
            print(f"free_physical_memory_percent={free:.2f}")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
