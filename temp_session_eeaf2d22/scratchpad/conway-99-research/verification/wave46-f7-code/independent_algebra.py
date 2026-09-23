#!/usr/bin/env python3
"""Independent characteristic-seven algebra for the Wave 46 verifier."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence


FIELD = 7
LENGTH = 231
ENDPOINT_ROW_COMPOSITION = (162, 32, 0, 0, 1, 0, 36)
RANK_INTERVAL = tuple(range(28, 45))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, separators=(",", ": "))
        + "\n"
    ).encode("utf-8")


def compact_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_compact(value: object) -> str:
    return hashlib.sha256(compact_json(value)).hexdigest()


def canonical_field(value: int) -> int:
    require(type(value) is int, "field entry is not an integer")
    return value % FIELD


def validate_matrix(
    matrix: Sequence[Sequence[int]],
    *,
    rows: int | None = None,
    columns: int | None = None,
    canonical_entries: bool = True,
) -> tuple[tuple[int, ...], ...]:
    require(isinstance(matrix, (list, tuple)), "matrix is not a sequence")
    if rows is not None:
        require(len(matrix) == rows, "matrix row count changed")
    if not matrix:
        require(columns in (None, 0), "empty matrix has declared columns")
        return ()
    width = len(matrix[0])
    if columns is not None:
        require(width == columns, "matrix column count changed")
    result: list[tuple[int, ...]] = []
    for row in matrix:
        require(
            isinstance(row, (list, tuple)) and len(row) == width,
            "ragged matrix",
        )
        values = tuple(canonical_field(value) for value in row)
        if canonical_entries:
            require(
                all(value == original for value, original in zip(values, row)),
                "matrix entry is not a canonical F7 representative",
            )
        result.append(values)
    return tuple(result)


def rref_mod7(
    matrix: Sequence[Sequence[int]],
) -> tuple[tuple[tuple[int, ...], ...], tuple[int, ...]]:
    work = [list(map(lambda value: value % FIELD, row)) for row in matrix]
    if not work:
        return (), ()
    row = 0
    pivots: list[int] = []
    for column in range(len(work[0])):
        pivot = next(
            (
                candidate
                for candidate in range(row, len(work))
                if work[candidate][column] % FIELD
            ),
            None,
        )
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        inverse = pow(work[row][column] % FIELD, -1, FIELD)
        require(
            work[row][column] * inverse % FIELD == 1,
            "modular inverse failed",
        )
        work[row] = [value * inverse % FIELD for value in work[row]]
        for other in range(len(work)):
            if other == row:
                continue
            factor = work[other][column] % FIELD
            if factor:
                work[other] = [
                    (value - factor * pivot_value) % FIELD
                    for value, pivot_value in zip(work[other], work[row])
                ]
        pivots.append(column)
        row += 1
        if row == len(work):
            break
    return tuple(tuple(values) for values in work), tuple(pivots)


def rank_mod7(matrix: Sequence[Sequence[int]]) -> int:
    return len(rref_mod7(matrix)[1])


def dot_mod7(left: Sequence[int], right: Sequence[int]) -> int:
    require(len(left) == len(right), "dot-product length mismatch")
    return sum(a * b for a, b in zip(left, right)) % FIELD


def gram_mod7(matrix: Sequence[Sequence[int]]) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(dot_mod7(left, right) for right in matrix)
        for left in matrix
    )


def transpose(matrix: Sequence[Sequence[int]]) -> tuple[tuple[int, ...], ...]:
    if not matrix:
        return ()
    return tuple(tuple(row[column] for row in matrix) for column in range(len(matrix[0])))


def normalize_projective_column(column: Sequence[int]) -> tuple[int, ...]:
    values = tuple(value % FIELD for value in column)
    first = next((value for value in values if value), None)
    require(first is not None, "zero generator column")
    inverse = pow(first, -1, FIELD)
    return tuple(value * inverse % FIELD for value in values)


def normalized_columns(
    generator: Sequence[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    return tuple(
        normalize_projective_column(column)
        for column in transpose(generator)
    )


def audit_generator(
    generator: Sequence[Sequence[int]],
    declared_rank: int,
) -> dict[str, Any]:
    matrix = validate_matrix(
        generator,
        rows=declared_rank,
        columns=LENGTH,
        canonical_entries=True,
    )
    rank = rank_mod7(matrix)
    require(rank == declared_rank, "generator row rank changed")
    gram = gram_mod7(matrix)
    require(
        all(value == 0 for row in gram for value in row),
        "generator is not self-orthogonal",
    )
    row_sums = tuple(sum(row) % FIELD for row in matrix)
    require(not any(row_sums), "generator is not orthogonal to all-ones")
    columns = normalized_columns(matrix)
    require(len(set(columns)) == LENGTH, "proportional generator columns")
    return {
        "declared_rank": declared_rank,
        "length": LENGTH,
        "rank": rank,
        "row_sums": row_sums,
        "gram": gram,
        "zero_columns": 0,
        "normalized_column_count": len(set(columns)),
        "dual_distance_lower_bound": 3,
        "generator_sha256": sha256_compact(matrix),
        "normalized_columns_sha256": sha256_compact(columns),
        "matrix": matrix,
        "normalized_columns": columns,
    }


def multiply_projection_columns(
    projection: Sequence[Sequence[int]],
    local_columns: Sequence[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    project = validate_matrix(projection, canonical_entries=True)
    require(project, "projection is empty")
    columns = validate_matrix(local_columns, columns=len(project[0]))
    require(
        all(len(row) == len(project[0]) for row in project),
        "projection is ragged",
    )
    return tuple(
        tuple(
            sum(project_row[index] * column[index] for index in range(len(column)))
            % FIELD
            for column in columns
        )
        for project_row in project
    )


def composition(word: Sequence[int]) -> tuple[int, ...]:
    values = tuple(canonical_field(value) for value in word)
    counts = Counter(values)
    result = tuple(counts[symbol] for symbol in range(FIELD))
    require(sum(result) == len(word), "composition total changed")
    return result


def scale_composition(
    counts: Sequence[int],
    scalar: int,
) -> tuple[int, ...]:
    require(len(counts) == FIELD, "composition must have seven symbols")
    scalar %= FIELD
    require(scalar != 0, "scalar must be nonzero")
    result = [0] * FIELD
    for symbol, count in enumerate(counts):
        require(type(count) is int and count >= 0, "bad composition count")
        result[scalar * symbol % FIELD] += count
    require(sum(result) == sum(counts), "scaled composition total changed")
    return tuple(result)


def endpoint_scalar_compositions() -> tuple[tuple[int, ...], ...]:
    values = tuple(
        scale_composition(ENDPOINT_ROW_COMPOSITION, scalar)
        for scalar in range(1, FIELD)
    )
    require(len(set(values)) == FIELD - 1, "scalar compositions are not distinct")
    require(
        all(sum(record[1:]) == 69 for record in values),
        "endpoint scalar weight changed",
    )
    return values


def compatible_weights(maximum: int = LENGTH) -> dict[str, Any]:
    reachable = {(0, 0)}
    compatible = [0]
    for weight in range(1, maximum + 1):
        reachable = {
            ((total + symbol) % FIELD, (squared + symbol * symbol) % FIELD)
            for total, squared in reachable
            for symbol in range(1, FIELD)
        }
        if (0, 0) in reachable:
            compatible.append(weight)
    excluded = [
        weight for weight in range(1, maximum + 1) if weight not in compatible
    ]
    return {
        "maximum": maximum,
        "compatible": compatible,
        "excluded_positive": excluded,
        "state_counts_by_weight": _state_counts_by_weight(maximum),
    }


def _state_counts_by_weight(maximum: int) -> list[int]:
    reachable = {(0, 0)}
    counts = [1]
    for _ in range(maximum):
        reachable = {
            ((total + symbol) % FIELD, (squared + symbol * symbol) % FIELD)
            for total, squared in reachable
            for symbol in range(1, FIELD)
        }
        counts.append(len(reachable))
    return counts


def theoretical_complete_moments(rank: int) -> dict[str, Any]:
    require(rank >= 2, "rank too small for degree-two moments")
    total = FIELD**rank
    degree_one = LENGTH * FIELD ** (rank - 1)
    off_diagonal = LENGTH * (LENGTH - 1) * FIELD ** (rank - 2)
    diagonal = degree_one + off_diagonal
    return {
        "rank": rank,
        "degree_0": total,
        "degree_1": [degree_one] * FIELD,
        "degree_2": [
            [
                diagonal if left == right else off_diagonal
                for right in range(FIELD)
            ]
            for left in range(FIELD)
        ],
    }


def reserved_endpoint_moments() -> dict[str, Any]:
    compositions = endpoint_scalar_compositions()
    multiplicity = LENGTH
    return {
        "degree_0": LENGTH * (FIELD - 1),
        "degree_1": [
            multiplicity * sum(record[symbol] for record in compositions)
            for symbol in range(FIELD)
        ],
        "degree_2": [
            [
                multiplicity
                * sum(record[left] * record[right] for record in compositions)
                for right in range(FIELD)
            ]
            for left in range(FIELD)
        ],
    }


def moment_slack(rank: int) -> dict[str, Any]:
    theoretical = theoretical_complete_moments(rank)
    reserved = reserved_endpoint_moments()
    degree_0 = theoretical["degree_0"] - reserved["degree_0"]
    degree_1 = [
        total - used
        for total, used in zip(theoretical["degree_1"], reserved["degree_1"])
    ]
    degree_2 = [
        [
            theoretical["degree_2"][left][right]
            - reserved["degree_2"][left][right]
            for right in range(FIELD)
        ]
        for left in range(FIELD)
    ]
    require(
        degree_0 > 0
        and min(degree_1) > 0
        and min(map(min, degree_2)) > 0,
        "complete-moment slack is not strict",
    )
    return {
        "rank": rank,
        "degree_0": degree_0,
        "degree_1": degree_1,
        "degree_2": degree_2,
        "minimum_degree_1": min(degree_1),
        "minimum_degree_2": min(map(min, degree_2)),
    }


def schur_cube_formal_record() -> dict[str, Any]:
    # If X^2=0, then (X+4I)(2I+3X)
    # has I coefficient 4*2=1 and X coefficient 1*2+4*3=0 in F7.
    identity_coefficient = 4 * 2 % FIELD
    x_coefficient = (1 * 2 + 4 * 3) % FIELD
    x_squared_coefficient = 1 * 3 % FIELD
    require(
        identity_coefficient == 1 and x_coefficient == 0,
        "claimed Schur inverse coefficients failed",
    )
    dimensions = {
        rank: math.comb(rank + 2, 3)
        for rank in range(1, 13)
    }
    minimum_rank = next(
        rank for rank, dimension in dimensions.items() if dimension >= LENGTH
    )
    require(minimum_rank == 11, "Schur-cube rank floor changed")
    return {
        "entrywise_cube_identity": "M^(o3)=M+4I over F7",
        "reason": (
            "off-diagonal entries are 0,+1,-1 and 4^3=1=4+4 mod 7"
        ),
        "claimed_inverse": "2I+3M",
        "formal_product_coefficients_mod7": {
            "I": identity_coefficient,
            "M": x_coefficient,
            "M_squared": x_squared_coefficient,
        },
        "uses_relation": "M^2=0 over F7",
        "cube_rank": LENGTH,
        "symmetric_cube_dimensions": dimensions,
        "minimum_code_rank": minimum_rank,
    }


def projector_consequence_record() -> dict[str, Any]:
    compositions = endpoint_scalar_compositions()
    weight_record = compatible_weights()
    require(
        weight_record["excluded_positive"] == [1, 2, 4],
        "compatible-weight census changed",
    )
    return {
        "integer_identities_assumed": {
            "shape": [LENGTH, LENGTH],
            "symmetric": True,
            "M_squared": "21M",
            "row_sums": 0,
            "diagonal": 4,
            "off_diagonal_alphabet": [-1, 0, 1],
            "row_composition_values": {
                "0": 162,
                "1": 32,
                "-1": 36,
                "4": 1,
            },
        },
        "mod7_consequences": {
            "M_squared": "0",
            "row_code_self_orthogonal": True,
            "row_code_in_one_perp": True,
            "columns_nonzero": True,
            "columns_pairwise_nonproportional": True,
            "dual_distance_lower_bound": 3,
        },
        "projective_column_argument": (
            "If col_j=a col_i and x=M_ij, then x=4a and 4=ax, "
            "so 4=2*x^2 mod 7; x in {0,+1,-1} makes this impossible."
        ),
        "endpoint_scalar_compositions": compositions,
        "distinct_scalar_compositions": len(set(compositions)),
        "certified_distinct_weight_69_words": LENGTH * (FIELD - 1),
        "weight_compatibility": weight_record,
        "rank_28_complete_moment_slack": moment_slack(28),
        "schur_cube": schur_cube_formal_record(),
    }


def compute() -> dict[str, Any]:
    consequence = projector_consequence_record()
    return {
        "format": "wave46-clean-room-f7-algebra-v1",
        "role": "verifier",
        "field": FIELD,
        "length": LENGTH,
        "projector_consequences": consequence,
        "positive_control_rank_interval": list(RANK_INTERVAL),
        "prompt_error_quarantine": {
            "required": True,
            "discovery_inspected": False,
            "accepted_as_assumption": False,
        },
        "status": {
            "independent_derivation": "PASS",
            "positive_controls_inspected": False,
            "endpoint_n3_4158": "UNKNOWN",
            "Conway_99": "UNKNOWN",
        },
        "limitations": [
            "The 231 by 231 matrix identities are conditional endpoint consequences.",
            "No concrete endpoint matrix or graph is constructed.",
            "Degree-two complete moments do not determine a complete enumerator.",
            "Positive-control artifacts have not yet been inspected.",
        ],
    }


def validate_record(record: dict[str, Any]) -> None:
    require(record["format"] == "wave46-clean-room-f7-algebra-v1", "bad format")
    consequence = record["projector_consequences"]
    require(
        consequence["mod7_consequences"]["row_code_self_orthogonal"],
        "self-orthogonality derivation failed",
    )
    require(
        consequence["weight_compatibility"]["excluded_positive"] == [1, 2, 4],
        "weight exclusion changed",
    )
    require(
        consequence["schur_cube"]["minimum_code_rank"] == 11,
        "Schur rank floor changed",
    )
    require(
        consequence["rank_28_complete_moment_slack"]["minimum_degree_2"] > 0,
        "degree-two moment slack is not strict",
    )
    require(
        record["prompt_error_quarantine"]["required"]
        and record["prompt_error_quarantine"]["discovery_inspected"] is False
        and record["prompt_error_quarantine"]["accepted_as_assumption"] is False,
        "prompt-error quarantine failed",
    )
    require(
        record["status"]["endpoint_n3_4158"] == "UNKNOWN"
        and record["status"]["Conway_99"] == "UNKNOWN",
        "status inflation",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    if arguments.verify:
        stored = arguments.verify.read_bytes()
        record = json.loads(stored)
        validate_record(record)
        require(canonical_json(compute()) == stored, "independent replay differs")
        print(
            f"PASS {arguments.verify} "
            f"sha256={hashlib.sha256(stored).hexdigest()}"
        )
        return 0
    record = compute()
    validate_record(record)
    payload = canonical_json(record)
    if arguments.output:
        arguments.output.write_bytes(payload)
        print(
            f"WROTE {arguments.output} "
            f"sha256={hashlib.sha256(payload).hexdigest()}"
        )
    else:
        print(payload.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
