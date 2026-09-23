#!/usr/bin/env python3
"""Exact Wave 46 scout for the characteristic-seven triangle-projector code.

This is a discovery-side checker.  It derives consequences of the supplied
endpoint identities for M=21E_0 and constructs generic positive-control codes.
It does not construct or verify an endpoint matrix.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
import math
import os
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence


P = 7
N = 231
RANKS = tuple(range(28, 45))
# Leave a safety margin above the user's hard 15% availability floor.
MIN_FREE_PERCENT = 20.0
HERE = Path(__file__).resolve().parent


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compact_hash(value: object) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    )


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("ascii")


def memory_guard(label: str) -> None:
    if sys.platform == "win32":
        class Status(ctypes.Structure):
            _fields_ = [
                ("length", ctypes.c_ulong),
                ("load", ctypes.c_ulong),
                ("total", ctypes.c_ulonglong),
                ("available", ctypes.c_ulonglong),
                ("total_page", ctypes.c_ulonglong),
                ("available_page", ctypes.c_ulonglong),
                ("total_virtual", ctypes.c_ulonglong),
                ("available_virtual", ctypes.c_ulonglong),
                ("extended", ctypes.c_ulonglong),
            ]

        status = Status()
        status.length = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise OSError("memory query failed")
        total, available = int(status.total), int(status.available)
    else:
        page = os.sysconf("SC_PAGE_SIZE")
        total = int(os.sysconf("SC_PHYS_PAGES") * page)
        available = int(os.sysconf("SC_AVPHYS_PAGES") * page)
    percent = 100.0 * available / total
    if percent < MIN_FREE_PERCENT:
        raise MemoryError(f"{label}: only {percent:.2f}% physical memory free")


def rank_mod(rows: Sequence[Sequence[int]], prime: int = P) -> int:
    if not rows:
        return 0
    work = [[int(value) % prime for value in row] for row in rows]
    rank = 0
    for column in range(len(work[0])):
        pivot = next(
            (row for row in range(rank, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, prime)
        work[rank] = [(value * inverse) % prime for value in work[rank]]
        for row in range(len(work)):
            if row == rank:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    (left - factor * right) % prime
                    for left, right in zip(work[row], work[rank])
                ]
        rank += 1
        if rank == len(work):
            break
    return rank


def canonical_projective(column: Sequence[int]) -> tuple[int, ...]:
    values = tuple(int(value) % P for value in column)
    first = next((value for value in values if value), None)
    if first is None:
        raise ValueError("zero projective column")
    inverse = pow(first, -1, P)
    return tuple(value * inverse % P for value in values)


def dot(left: Sequence[int], right: Sequence[int]) -> int:
    return sum(a * b for a, b in zip(left, right)) % P


def local_affine_columns() -> tuple[tuple[int, ...], ...]:
    """A projective, self-orthogonal [21,4]_7 building block."""
    basis = tuple(
        tuple(int(i == j) for i in range(4))
        for j in range(4)
    )
    lines = (
        (basis[0], basis[1]),
        (basis[2], basis[3]),
        ((1, 0, 1, 0), (0, 1, 0, 1)),
    )
    columns = tuple(
        tuple((v[index] + t * w[index]) % P for index in range(4))
        for v, w in lines
        for t in range(P)
    )
    if len(columns) != 21:
        raise AssertionError("local block length changed")
    if len({canonical_projective(column) for column in columns}) != 21:
        raise AssertionError("local block is not projective")
    if any(sum(column[index] for column in columns) % P for index in range(4)):
        raise AssertionError("local block row sum is nonzero")
    gram = [
        [
            sum(column[i] * column[j] for column in columns) % P
            for j in range(4)
        ]
        for i in range(4)
    ]
    if any(any(row) for row in gram):
        raise AssertionError("local block is not self-orthogonal")
    rows = tuple(
        tuple(column[index] for column in columns)
        for index in range(4)
    )
    if rank_mod(rows) != 4:
        raise AssertionError("local block lost rank")
    return columns


def local_weight_enumerator(
    columns: Sequence[Sequence[int]],
) -> dict[int, int]:
    result: Counter[int] = Counter()
    for coefficients in itertools.product(range(P), repeat=4):
        word = tuple(dot(coefficients, column) for column in columns)
        result[sum(value != 0 for value in word)] += 1
    return dict(sorted(result.items()))


def convolution(
    left: dict[int, int], right: dict[int, int]
) -> dict[int, int]:
    result: Counter[int] = Counter()
    for first_weight, first_count in left.items():
        for second_weight, second_count in right.items():
            result[first_weight + second_weight] += first_count * second_count
    return dict(sorted(result.items()))


def block_diagonal_columns(
    local: Sequence[Sequence[int]], copies: int
) -> tuple[tuple[int, ...], ...]:
    columns: list[tuple[int, ...]] = []
    for block in range(copies):
        for column in local:
            expanded = [0] * (4 * copies)
            expanded[4 * block:4 * block + 4] = column
            columns.append(tuple(expanded))
    return tuple(columns)


def projected_columns(
    projection: Sequence[Sequence[int]],
    columns: Sequence[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(dot(row, column) for row in projection)
        for column in columns
    )


def find_projective_projection(
    output_dimension: int,
    columns: Sequence[Sequence[int]],
) -> tuple[tuple[tuple[int, ...], ...], int]:
    """Deterministically find a full-rank projection injective on points."""
    input_dimension = len(columns[0])
    if output_dimension == input_dimension:
        identity = tuple(
            tuple(int(i == j) for j in range(input_dimension))
            for i in range(input_dimension)
        )
        return identity, 0
    generator = random.Random(46_000_000 + output_dimension)
    for attempt in range(1, 10001):
        matrix = tuple(
            tuple(generator.randrange(P) for _ in range(input_dimension))
            for _ in range(output_dimension)
        )
        if rank_mod(matrix) != output_dimension:
            continue
        images = projected_columns(matrix, columns)
        try:
            normalized = tuple(canonical_projective(column) for column in images)
        except ValueError:
            continue
        if len(set(normalized)) == len(columns):
            return matrix, attempt
    raise RuntimeError(f"no projective projection found in dimension {output_dimension}")


def positive_controls() -> tuple[dict[str, object], dict[str, object]]:
    local = local_affine_columns()
    local_enumerator = local_weight_enumerator(local)
    expected_local = {0: 1, 12: 126, 14: 18, 18: 1470, 19: 756, 21: 30}
    if local_enumerator != expected_local:
        raise AssertionError("local weight enumerator changed")

    first_four_enumerator = {0: 1}
    for _ in range(4):
        first_four_enumerator = convolution(first_four_enumerator, local_enumerator)
    inherited_a69 = first_four_enumerator.get(69, 0)
    if inherited_a69 != 668_653_683_264:
        raise AssertionError("four-block weight-69 count changed")

    first_columns = block_diagonal_columns(local, 4)
    last_columns = block_diagonal_columns(local, 7)
    records: list[dict[str, object]] = []
    for rank in RANKS:
        tail_dimension = rank - 16
        projection, attempts = find_projective_projection(tail_dimension, last_columns)
        tail_images = projected_columns(projection, last_columns)
        combined = tuple(
            tuple(column) + (0,) * tail_dimension
            for column in first_columns
        ) + tuple(
            (0,) * 16 + tuple(column)
            for column in tail_images
        )
        normalized = tuple(canonical_projective(column) for column in combined)
        if len(combined) != N or len(set(normalized)) != N:
            raise AssertionError(f"rank-{rank} control is not projective")

        rows = tuple(
            tuple(column[index] for column in combined)
            for index in range(rank)
        )
        if rank_mod(rows) != rank:
            raise AssertionError(f"rank-{rank} control lost dimension")
        if any(sum(row) % P for row in rows):
            raise AssertionError(f"rank-{rank} control is not in one-perp")
        gram = [
            [dot(rows[i], rows[j]) for j in range(rank)]
            for i in range(rank)
        ]
        if any(any(row) for row in gram):
            raise AssertionError(f"rank-{rank} control is not self-orthogonal")

        records.append(
            {
                "dimension": rank,
                "tail_projection_dimension": tail_dimension,
                "projection_attempt": attempts,
                "projection_matrix": [list(row) for row in projection],
                "projection_sha256": compact_hash(projection),
                "generator_column_stream_sha256": compact_hash(combined),
                "length": len(combined),
                "generator_rank": rank,
                "projective_columns": len(set(normalized)),
                "dual_distance_at_least": 3,
                "all_generator_row_sums_zero": True,
                "self_orthogonal": True,
                "inherited_A69_lower_bound": inherited_a69,
            }
        )
    control_certificate = {
        "format": "wave46-generic-positive-controls-v1",
        "scope": (
            "Generic codes satisfying the ordinary length/dimension/"
            "self-orthogonality/one-perp/projectivity/A69 constraints; "
            "they are not endpoint projector codes."
        ),
        "construction": (
            "Four direct-sum copies of the explicit [21,4]_7 affine-line "
            "block, followed by seven copies projected by each archived "
            "matrix from dimension 28 to dimension r-16."
        ),
        "local_columns": [list(column) for column in local],
        "local_columns_sha256": compact_hash(local),
        "local_21_4_weight_enumerator": {
            str(weight): count for weight, count in local_enumerator.items()
        },
        "four_block_A69": inherited_a69,
        "records": records,
    }
    control_certificate["all_projection_matrices_sha256"] = compact_hash(
        [record["projection_matrix"] for record in records]
    )
    return (
        control_certificate,
        {
            "local_columns": local,
            "first_four_enumerator": first_four_enumerator,
        },
    )


def endpoint_scalar_compositions() -> tuple[tuple[int, ...], ...]:
    base = (162, 32, 0, 0, 1, 0, 36)
    result = []
    for scalar in range(1, P):
        composition = [0] * P
        composition[0] = base[0]
        for symbol in range(1, P):
            composition[scalar * symbol % P] = base[symbol]
        result.append(tuple(composition))
    if len(set(result)) != 6:
        raise AssertionError("scalar compositions collide")
    return tuple(result)


def allowed_weights() -> tuple[int, ...]:
    """Weights admitting nonzero symbols with sum and square-sum zero."""
    states = {(0, 0)}
    allowed: list[int] = []
    for weight in range(N + 1):
        if (0, 0) in states:
            allowed.append(weight)
        states = {
            ((total + value) % P, (square + value * value) % P)
            for total, square in states
            for value in range(1, P)
        }
    return tuple(allowed)


def complete_moment_check(
    compositions: Sequence[Sequence[int]],
) -> dict[str, object]:
    known_words = 231 * len(compositions)
    first_known = [
        231 * sum(composition[symbol] for composition in compositions)
        for symbol in range(P)
    ]
    second_known = [
        [
            231
            * sum(
                composition[first]
                * (composition[second] - int(first == second))
                for composition in compositions
            )
            for second in range(P)
        ]
        for first in range(P)
    ]
    minimum_rank = min(RANKS)
    total_words = P ** minimum_rank
    first_required = N * P ** (minimum_rank - 1)
    second_required = N * (N - 1) * P ** (minimum_rank - 2)
    if known_words >= total_words:
        raise AssertionError("known words exhaust the minimum-rank code")
    if any(value >= first_required for value in first_known):
        raise AssertionError("known compositions violate a first moment")
    if any(
        value >= second_required
        for row in second_known
        for value in row
    ):
        raise AssertionError("known compositions violate a second moment")
    return {
        "known_words": known_words,
        "minimum_tested_dimension": minimum_rank,
        "minimum_code_size": total_words,
        "first_coordinate_moment_required_per_symbol": first_required,
        "known_first_coordinate_moments": first_known,
        "minimum_first_moment_slack": min(
            first_required - value for value in first_known
        ),
        "second_ordered_coordinate_moment_required_per_symbol_pair": second_required,
        "known_second_ordered_coordinate_moments": second_known,
        "minimum_second_moment_slack": min(
            second_required - value
            for row in second_known
            for value in row
        ),
        "degree_0_1_2_complete_moments": "PASS_WITH_STRICT_SLACK",
        "interpretation": (
            "These are only the complete-enumerator moments forced by "
            "projectivity (dual distance at least three). Higher composition "
            "coefficients remain undetermined."
        ),
    }


def prompt_error_control() -> dict[str, object]:
    """Quarantine the superseded A+3I interpretation."""
    determinant = 17 * 6 ** 54 * (-1) ** 44
    determinant_mod_7 = determinant % P
    if determinant_mod_7 != 3:
        raise AssertionError("A+3I prompt-error determinant changed")
    return {
        "quarantined_object": "A+3I for the 99-by-99 adjacency matrix",
        "reason": (
            "This is not the project's M. Its eigenvalues are 17, 6, -1, "
            "so it is invertible modulo seven and its row code is F7^99."
        ),
        "determinant_mod_7": determinant_mod_7,
        "used_in_live_conclusion": False,
        "correct_object": "M=21E_0, the 231-by-231 integral triangle projector",
    }


def compute() -> dict[str, object]:
    memory_guard("wave46-start")
    compositions = endpoint_scalar_compositions()
    for composition in compositions:
        if sum(composition) != N:
            raise AssertionError("endpoint row composition length changed")
        coordinate_sum = sum(symbol * count for symbol, count in enumerate(composition))
        norm = sum(symbol * symbol * count for symbol, count in enumerate(composition))
        if coordinate_sum % P or norm % P:
            raise AssertionError("endpoint row composition violates code congruences")

    allowed = allowed_weights()
    if tuple(weight for weight in range(N + 1) if weight not in allowed) != (1, 2, 4):
        raise AssertionError("sum/norm weight obstruction changed")

    controls, control_internal = positive_controls()
    complete_moments = complete_moment_check(compositions)

    # M^(o3)=M+4I.  Since M^2=0 mod 7,
    # (M+4I)(3M+2I)=I, so the Schur cube spans the whole coordinate space.
    inverse_product_i = 4 * 2 % P
    inverse_product_m = (4 * 3 + 2) % P
    if (inverse_product_i, inverse_product_m) != (1, 0):
        raise AssertionError("Hadamard-cube inverse identity failed")
    schur_rank_floor = next(
        rank for rank in range(1, N + 1)
        if math.comb(rank + 2, 3) >= N
    )
    if schur_rank_floor != 11:
        raise AssertionError("Schur-cube dimension floor changed")

    result = {
        "format": "wave46-f7-projector-code-v1",
        "role": "proof_a",
        "claim_label": "DERIVED_NULL_RESULT_PENDING_VERIFICATION",
        "scope": (
            "Conditional prism-free endpoint n3=4158: ordinary and low-degree "
            "complete weight-enumerator consequences for the F7 row code of "
            "the 231-by-231 integral triangle projector M=21E_0."
        ),
        "corrected_object": {
            "matrix": "M=21E_0",
            "order": N,
            "integer_identity": "M^2=21M",
            "mod_7_identity": "M^2=0",
            "diagonal": 4,
            "endpoint_off_diagonal_alphabet": [0, 1, -1],
            "endpoint_row_composition": {
                "0": 162,
                "1": 32,
                "4": 1,
                "6": 36,
            },
            "row_sum_mod_7": 0,
            "row_norm_mod_7": 0,
        },
        "code": {
            "field": "F7",
            "length": N,
            "dimension": "r7",
            "endpoint_dimension_range": [min(RANKS), max(RANKS)],
            "self_orthogonal": True,
            "contained_in_one_perp": True,
            "dual_dimension": "231-r7",
            "columns_nonzero_and_projectively_distinct": True,
            "dual_minimum_distance_at_least": 3,
            "orthogonal_array_strength": 2,
            "known_projective_generator_lines": 231,
            "known_weight_69_words": 1386,
            "A69_lower_bound": 1386,
            "B69_at_least_A69": True,
            "forbidden_weights_from_sum_and_norm": [1, 2, 4],
            "all_other_weights_not_excluded_by_these_two_congruences": True,
            "ordinary_macwilliams_formula": (
                "B_j=7^(-r7)*sum_i A_i*K_j^(231,7)(i)"
            ),
            "self_orthogonal_inequalities": "B_j>=A_j for every j",
            "projective_equalities": {"B_1": 0, "B_2": 0},
        },
        "complete_enumerator": {
            "known_scalar_compositions": [list(value) for value in compositions],
            "known_coefficient_lower_bound_per_composition": 231,
            "linear_congruence": "sum_a a*n_a=0 mod 7",
            "quadratic_congruence": "sum_a a^2*n_a=0 mod 7",
            "degree_0_1_2_moment_check": complete_moments,
            "higher_complete_transform_status": "UNDERDETERMINED",
        },
        "schur_cube": {
            "entrywise_identity_mod_7": "M^(o3)=M+4I",
            "inverse_mod_7": "(M+4I)^(-1)=3M+2I",
            "row_code_third_schur_power_dimension": N,
            "symmetric_cube_dimension_bound": "binom(r7+2,3)>=231",
            "derived_rank_floor": schur_rank_floor,
            "comparison_to_current_endpoint_floor": "strictly superseded by r7>=28",
        },
        "ordinary_enumerator_positive_controls": controls,
        "prompt_error_control": prompt_error_control(),
        "conclusion": {
            "ordinary_weight_enumerator_contradiction": False,
            "low_degree_complete_enumerator_contradiction": False,
            "divisibility_contradiction": False,
            "new_endpoint_rank_floor": False,
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "precise_missing_information": [
            (
                "The symbol compositions, or equivalent character sums, of "
                "the other 7^r7-1-1386 nonzero codewords."
            ),
            (
                "Higher dual composition coefficients beyond B1=B2=0, or a "
                "proved dual-distance/low-weight exclusion strong enough to "
                "turn MacWilliams identities into a contradiction."
            ),
            (
                "A constraint retaining the distinguished 231 projector rows "
                "and their mutual coordinatewise products; the ordinary row "
                "span forgets that generator geometry."
            ),
        ],
        "limitations": [
            (
                "The generic positive controls satisfy all ordinary code "
                "constraints but do not satisfy the six exact endpoint "
                "generator compositions; they are separation controls, not "
                "endpoint candidates."
            ),
            (
                "Passing degree-zero, one, and two complete moments does not "
                "prove existence of a full complete weight enumerator or code."
            ),
            "Discovery cannot verify itself.",
        ],
        "resource_guard": {
            "minimum_free_physical_memory_percent": MIN_FREE_PERCENT,
            "checkpoints": ["wave46-start", "wave46-finish"],
            "all_runtime_samples_met_minimum": True,
            "runtime_values_archived": False,
        },
    }
    del control_internal
    memory_guard("wave46-finish")
    validate(result)
    return result


def validate(result: dict[str, object]) -> None:
    if result.get("claim_label") != "DERIVED_NULL_RESULT_PENDING_VERIFICATION":
        raise ValueError("claim label inflation")
    code = result["code"]
    if code["endpoint_dimension_range"] != [28, 44]:
        raise ValueError("endpoint rank range changed")
    if not code["self_orthogonal"] or code["A69_lower_bound"] != 1386:
        raise ValueError("basic code facts changed")
    if code["forbidden_weights_from_sum_and_norm"] != [1, 2, 4]:
        raise ValueError("weight congruence result changed")
    records = result["ordinary_enumerator_positive_controls"]["records"]
    if [record["dimension"] for record in records] != list(RANKS):
        raise ValueError("positive controls do not cover every endpoint rank")
    if any(
        record["length"] != N
        or record["generator_rank"] != record["dimension"]
        or record["projective_columns"] != N
        or not record["self_orthogonal"]
        or record["inherited_A69_lower_bound"] < 1386
        or record["projection_sha256"]
        != compact_hash(record["projection_matrix"])
        for record in records
    ):
        raise ValueError("positive control failed")
    if result["ordinary_enumerator_positive_controls"][
        "all_projection_matrices_sha256"
    ] != compact_hash([record["projection_matrix"] for record in records]):
        raise ValueError("positive-control aggregate hash failed")
    moments = result["complete_enumerator"]["degree_0_1_2_moment_check"]
    if moments["degree_0_1_2_complete_moments"] != "PASS_WITH_STRICT_SLACK":
        raise ValueError("complete moment control failed")
    if result["schur_cube"]["derived_rank_floor"] != 11:
        raise ValueError("Schur-cube boundary changed")
    conclusion = result["conclusion"]
    if (
        conclusion["ordinary_weight_enumerator_contradiction"]
        or conclusion["low_degree_complete_enumerator_contradiction"]
        or conclusion["divisibility_contradiction"]
        or conclusion["new_endpoint_rank_floor"]
        or conclusion["endpoint_n3_4158"] != "UNKNOWN"
        or conclusion["conway_99"] != "UNKNOWN"
    ):
        raise ValueError("status inflation")
    if result["prompt_error_control"]["used_in_live_conclusion"]:
        raise ValueError("prompt-error route escaped quarantine")


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path)
    group.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = compute()
    payload = canonical(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    else:
        expected = json.loads(args.verify.read_text(encoding="ascii"))
        validate(expected)
        if payload != canonical(expected):
            raise ValueError("live Wave46 result differs from archived result")
    print("PASS: Wave46 F7 projector-code null boundary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
