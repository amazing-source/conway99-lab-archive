#!/usr/bin/env python3
"""Exact Wave 51 global triple-count relaxation.

The certificate is an aggregate tensor, not a graph and not an association
scheme.  Everything is checked with Python integers.  The calculation is
small, but a 20 percent free-physical-memory guard preserves the host reserve.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import sys
from itertools import combinations_with_replacement, product
from pathlib import Path
from typing import Iterable


VERTEX_COUNT = 231
RELATIONS = ("I", "K", "D", "C", "B")
VALENCIES = (1, 18, 32, 144, 36)
K2_COMMON_NEIGHBORS = (18, 5, 0, 1, 2)
S2_RIGHT_HAND_SIDE = (68, 0, 13, 0, -13)
MEMORY_FLOOR_PERCENT = 20.0

# t[i,j,k] is the ordered-triple count divided by 231, stored only for
# sorted relation triples.  Missing sorted triples have value zero.
CERTIFICATE_ENTRIES = (
    ((0, 0, 0), 1),
    ((0, 1, 1), 18),
    ((0, 2, 2), 32),
    ((0, 3, 3), 144),
    ((0, 4, 4), 36),
    ((1, 1, 1), 90),
    ((1, 1, 3), 144),
    ((1, 1, 4), 72),
    ((1, 2, 2), 288),
    ((1, 2, 4), 288),
    ((1, 3, 3), 2448),
    ((1, 4, 4), 288),
    ((2, 2, 2), 128),
    ((2, 2, 3), 576),
    ((2, 3, 3), 3456),
    ((2, 3, 4), 576),
    ((2, 4, 4), 288),
    ((3, 3, 3), 10656),
    ((3, 3, 4), 4032),
    ((3, 4, 4), 576),
    ((4, 4, 4), 108),
)


class MemoryStatus(ctypes.Structure):
    _fields_ = (
        ("length", ctypes.c_ulong),
        ("memory_load", ctypes.c_ulong),
        ("total_physical", ctypes.c_ulonglong),
        ("available_physical", ctypes.c_ulonglong),
        ("total_page_file", ctypes.c_ulonglong),
        ("available_page_file", ctypes.c_ulonglong),
        ("total_virtual", ctypes.c_ulonglong),
        ("available_virtual", ctypes.c_ulonglong),
        ("available_extended_virtual", ctypes.c_ulonglong),
    )


def free_physical_memory_percent() -> float:
    if sys.platform != "win32":
        return 100.0
    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * status.available_physical / status.total_physical


def enforce_memory_floor() -> float:
    free_percent = free_physical_memory_percent()
    if free_percent < MEMORY_FLOOR_PERCENT:
        raise MemoryError(
            f"free physical memory {free_percent:.2f}% is below "
            f"{MEMORY_FLOOR_PERCENT:.2f}%"
        )
    return free_percent


def certificate_dict(
    entries: Iterable[tuple[tuple[int, int, int], int]] = CERTIFICATE_ENTRIES,
) -> dict[tuple[int, int, int], int]:
    result: dict[tuple[int, int, int], int] = {}
    for key, value in entries:
        if tuple(sorted(key)) != key or any(not 0 <= index < 5 for index in key):
            raise AssertionError(f"invalid tensor key {key}")
        if key in result:
            raise AssertionError(f"duplicate tensor key {key}")
        if not isinstance(value, int) or value < 0:
            raise AssertionError(f"invalid tensor value {key}: {value}")
        if value:
            result[key] = value
    return result


def tensor_value(
    certificate: dict[tuple[int, int, int], int],
    left: int,
    middle: int,
    right: int,
) -> int:
    return certificate.get(tuple(sorted((left, middle, right))), 0)


def build_tables(
    certificate: dict[tuple[int, int, int], int],
) -> tuple[tuple[tuple[int, ...], ...], ...]:
    tables = []
    for relation in range(5):
        table = []
        for left in range(5):
            row = []
            for right in range(5):
                value = tensor_value(certificate, left, right, relation)
                divisor = VALENCIES[relation]
                if value % divisor:
                    raise AssertionError(
                        f"t[{left},{right},{relation}]={value} is not "
                        f"divisible by v[{relation}]={divisor}"
                    )
                row.append(value // divisor)
            table.append(tuple(row))
        tables.append(tuple(table))
    return tuple(tables)


def verify_parameter_family(
    certificate: dict[tuple[int, int, int], int],
) -> dict[str, int]:
    """Check the three-parameter solution used to obtain the certificate."""

    a = 288
    f = 0
    i_parameter = 288
    expected = {
        (1, 2, 2): a,
        (1, 2, 3): 576 - 2 * a,
        (1, 2, 4): a,
        (1, 3, 3): 1296 + 4 * a,
        (1, 3, 4): 576 - 2 * a,
        (1, 4, 4): a,
        (2, 2, 2): 416 - i_parameter + 2 * f,
        (2, 2, 3): 576 - a + i_parameter - 3 * f,
        (2, 2, 4): f,
        (2, 3, 3): 2304 + 4 * a + 4 * f,
        (2, 3, 4): 1152 - a - f - i_parameter,
        (2, 4, 4): i_parameter,
        (3, 3, 3): 15264 - 12 * a - 4 * f - 4 * i_parameter,
        (3, 3, 4): 1728 + 4 * a + 4 * i_parameter,
        (3, 4, 4): 1728 - a - 3 * i_parameter + f,
        (4, 4, 4): 2 * i_parameter - f - 468,
    }
    for key, value in expected.items():
        if tensor_value(certificate, *key) != value:
            raise AssertionError(
                f"parameter-family mismatch at {key}: "
                f"{tensor_value(certificate, *key)} != {value}"
            )
        if value < 0:
            raise AssertionError(f"negative family value at {key}: {value}")
    return {"a": a, "f": f, "i": i_parameter}


def verify_certificate(
    entries: Iterable[tuple[tuple[int, int, int], int]] = CERTIFICATE_ENTRIES,
) -> dict[str, object]:
    certificate = certificate_dict(entries)
    tables = build_tables(certificate)

    # Repeated-vertex triples force the identity-relation slice.
    for left, right in product(range(5), repeat=2):
        expected = VALENCIES[left] if left == right else 0
        actual = tensor_value(certificate, 0, left, right)
        if actual != expected:
            raise AssertionError(
                f"identity tensor entry t[0,{left},{right}]={actual}, "
                f"expected {expected}"
            )

    # Every slice is an integral point of its local transportation polytope.
    for relation, table in enumerate(tables):
        row_sums = tuple(sum(row) for row in table)
        column_sums = tuple(
            sum(table[row][column] for row in range(5))
            for column in range(5)
        )
        if row_sums != VALENCIES or column_sums != VALENCIES:
            raise AssertionError(
                f"bad margins in relation {relation}: "
                f"{row_sums}, {column_sums}"
            )
        if table[1][1] != K2_COMMON_NEIGHBORS[relation]:
            raise AssertionError(f"bad K^2 entry in relation {relation}")

        expected_ks = 4 if relation == 1 else 0
        if table[1][4] - table[1][2] != expected_ks:
            raise AssertionError(f"bad KS entry in relation {relation}")
        if table[4][1] - table[2][1] != expected_ks:
            raise AssertionError(f"bad SK entry in relation {relation}")

        signed_square = (
            table[4][4]
            + table[2][2]
            - table[4][2]
            - table[2][4]
        )
        if signed_square != S2_RIGHT_HAND_SIDE[relation]:
            raise AssertionError(f"bad S^2 entry in relation {relation}")

    # The local graph at a K-neighbor pair is 3K6.
    k_table = tables[1]
    required_k_row = (1, 5, 0, 8, 4)
    if k_table[1] != required_k_row:
        raise AssertionError(f"bad local 3K6 row: {k_table[1]}")
    if tuple(k_table[row][1] for row in range(5)) != required_k_row:
        raise AssertionError("bad transposed local 3K6 column")

    # Full triple-count symmetry is the global balance condition.
    for relation, left, right in product(range(5), repeat=3):
        common = tensor_value(certificate, left, right, relation)
        if VALENCIES[relation] * tables[relation][left][right] != common:
            raise AssertionError("tensor-to-table normalization failed")
        if VALENCIES[left] * tables[left][relation][right] != common:
            raise AssertionError(
                f"global balance failed for ({left},{right},{relation})"
            )

    # Necessary orientation divisibilities for actual ordered triple counts.
    for left, middle, right in combinations_with_replacement(range(1, 5), 3):
        total = VERTEX_COUNT * tensor_value(
            certificate, left, middle, right
        )
        divisor = 6 if left == middle == right else 2
        if total % divisor:
            raise AssertionError(
                f"orientation divisibility failed at "
                f"{(left, middle, right)}"
            )

    parameters = verify_parameter_family(certificate)
    return {
        "global_balance_equations_checked": 125,
        "identity_entries_checked": 25,
        "local_tables_checked": 5,
        "memory_floor_percent": MEMORY_FLOOR_PERCENT,
        "parameter_family_point": parameters,
        "slices_integral": True,
        "tensor_nonnegative": True,
        "triple_orientation_divisibility": True,
    }


def associativity_failures(
    tables: tuple[tuple[tuple[int, ...], ...], ...],
) -> list[dict[str, object]]:
    """Return failures if averages are misread as scheme intersection numbers."""

    failures = []
    for left, middle, right, output in product(range(5), repeat=4):
        lhs = sum(
            tables[inner][left][middle] * tables[output][inner][right]
            for inner in range(5)
        )
        rhs = sum(
            tables[inner][middle][right] * tables[output][left][inner]
            for inner in range(5)
        )
        if lhs != rhs:
            failures.append(
                {
                    "indices_i_j_m_k": [left, middle, right, output],
                    "left_association": lhs,
                    "right_association": rhs,
                }
            )
    return failures


def serialized_tables(
    tables: tuple[tuple[tuple[int, ...], ...], ...],
) -> dict[str, list[list[int]]]:
    return {
        RELATIONS[index]: [list(row) for row in table]
        for index, table in enumerate(tables)
    }


def build_results() -> dict[str, object]:
    enforce_memory_floor()
    certificate = certificate_dict()
    checks = verify_certificate()
    tables = build_tables(certificate)
    failures = associativity_failures(tables)
    if len(failures) != 100:
        raise AssertionError(
            f"associativity diagnostic changed: {len(failures)} != 100"
        )

    # Independent spectral arithmetic for the two matrices used in the setup.
    k_spectrum = {18: 1, 7: 54, 0: 44, -3: 132}
    if sum(k_spectrum.values()) != VERTEX_COUNT:
        raise AssertionError("bad K multiplicities")
    if sum(value * multiplicity for value, multiplicity in k_spectrum.items()):
        raise AssertionError("bad K trace")
    if (
        sum(value * value * multiplicity for value, multiplicity in k_spectrum.items())
        != VERTEX_COUNT * 18
    ):
        raise AssertionError("bad K square trace")

    s_spectrum = {4: 187, -17: 44}
    if sum(s_spectrum.values()) != VERTEX_COUNT:
        raise AssertionError("bad S multiplicities")
    if sum(value * multiplicity for value, multiplicity in s_spectrum.items()):
        raise AssertionError("bad S trace")
    if (
        sum(value * value * multiplicity for value, multiplicity in s_spectrum.items())
        != VERTEX_COUNT * 68
    ):
        raise AssertionError("bad S square trace")

    return {
        "claim_boundary": {
            "global_symmetric_triple_count_relaxation": "FEASIBLE_EXACT_CANDIDATE",
            "association_scheme_realization": "REFUTED_FOR_DISPLAYED_AVERAGES_ONLY",
            "prism_free_endpoint": "UNKNOWN",
            "conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "format": "wave51-global-triple-tensor-v1",
        "relations": {
            "order": list(RELATIONS),
            "valencies": list(VALENCIES),
            "meaning": {
                "I": "equal triangles",
                "K": "triangles sharing one graph vertex",
                "D": "disjoint triangles with zero cross edges",
                "C": "disjoint triangles with one cross edge",
                "B": "disjoint triangles with two cross edges",
            },
        },
        "endpoint_input": {
            "graph_triangle_count": VERTEX_COUNT,
            "prism_count": 0,
            "fixed_row_disjoint_q_distribution": {"0": 32, "1": 144, "2": 36},
            "K_spectrum": {str(key): value for key, value in k_spectrum.items()},
            "S_definition": "K^2 - 17I - 4K - J = B - D",
            "S_polynomial": "S^2 + 13S - 68I = 0",
            "S_spectrum": {str(key): value for key, value in s_spectrum.items()},
            "M_identification": "M = 4I - S = 21E_0 (previous projector)",
        },
        "minimal_linear_system": {
            "variables": (
                "symmetric t_{ijk}=v_k p^k_{ij}, "
                "0<=i<=j<=k<=4 (35 variables before forced zeros)"
            ),
            "constraints": [
                "t is nonnegative and invariant under all index permutations",
                "sum_j t_{ijk}=v_i v_k, with identity entries included",
                "t_{11k}=v_k*(18,5,0,1,2)_k",
                "t_{14k}-t_{12k}=4 v_k when k=K and zero otherwise",
                "t_{44k}+t_{22k}-2t_{24k}=v_k*(68,0,13,0,-13)_k",
                "the k=K slice has local row (1,5,0,8,4)",
            ],
            "certificate_type": (
                "one explicit integral point; no floating-point LP status used"
            ),
        },
        "normalized_symmetric_tensor_nonzero_entries": [
            {"relations": [RELATIONS[index] for index in key], "value": value}
            for key, value in sorted(certificate.items())
        ],
        "local_average_tables_p_k_ij": serialized_tables(tables),
        "checks": {
            **checks,
            "free_physical_memory_at_start_at_least_percent": (
                MEMORY_FLOOR_PERCENT
            ),
            "K_spectral_arithmetic": True,
            "S_spectral_arithmetic": True,
        },
        "associativity_diagnostic": {
            "failure_count_over_625_ordered_index_tests": len(failures),
            "first_failure": failures[0],
            "interpretation": (
                "The feasible tensor is an aggregate relaxation point, not "
                "the intersection algebra of an association scheme."
            ),
        },
        "result": {
            "exact_contradiction": False,
            "positive_aggregate_control": True,
            "disposition": "NULL_RESULT_FOR_THIS_LINEAR_RELAXATION",
        },
        "limitations": [
            "This is a discovery-agent certificate and is not independently verified.",
            "The tensor records only averaged ordered-triple counts.",
            "It does not assign local tables consistently to the 231 triangle vertices.",
            "It does not satisfy association-scheme associativity.",
            "Higher-order quadruple consistency, realizability, and graph adjacency are absent.",
            "A feasible relaxation is not evidence that the endpoint graph exists.",
            "No automorphism of a completed graph is assumed.",
            "The prism-free endpoint and Conway-99 remain UNKNOWN.",
        ],
    }


def canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()

    encoded = canonical_bytes(build_results())
    digest = hashlib.sha256(encoded).hexdigest()
    if arguments.verify is not None:
        if arguments.verify.read_bytes() != encoded:
            print(f"FAIL: {arguments.verify} differs", file=sys.stderr)
            return 1
        print("PASS_EXACT_REPLAY")
        print(f"sha256={digest}")
        return 0
    if arguments.output is not None:
        arguments.output.write_bytes(encoded)
        print(arguments.output)
        print(f"sha256={digest}")
        return 0
    sys.stdout.buffer.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
