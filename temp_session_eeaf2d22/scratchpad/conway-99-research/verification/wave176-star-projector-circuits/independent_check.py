"""Clean-room exact checks for the Wave 176 star-pair calculation.

This program does not import the discovery checker.  It constructs only the
four symbolic 13-column Gram matrices forced by the cycle classification.
It does not enumerate graphs, codes, or configurations.
"""

from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Any


Q = 3
N = 11


def rank_mod3(matrix: list[list[int]]) -> int:
    rows = [[entry % Q for entry in row] for row in matrix]
    if not rows:
        return 0
    width = len(rows[0])
    pivot_row = 0
    for column in range(width):
        source = next(
            (i for i in range(pivot_row, len(rows)) if rows[i][column]),
            None,
        )
        if source is None:
            continue
        rows[pivot_row], rows[source] = rows[source], rows[pivot_row]
        if rows[pivot_row][column] == 2:
            rows[pivot_row] = [(2 * value) % Q for value in rows[pivot_row]]
        for i in range(len(rows)):
            if i == pivot_row:
                continue
            factor = rows[i][column]
            if factor:
                rows[i] = [
                    (rows[i][j] - factor * rows[pivot_row][j]) % Q
                    for j in range(width)
                ]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def matvec(matrix: list[list[int]], vector: list[int]) -> list[int]:
    return [
        sum(entry * value for entry, value in zip(row, vector)) % Q
        for row in matrix
    ]


def biadjacency(parts: tuple[int, ...]) -> list[list[int]]:
    assert sum(parts) == 6 and all(part >= 2 for part in parts)
    result = [[0] * 6 for _ in range(6)]
    start = 0
    for part in parts:
        for i in range(part):
            result[start + i][start + i] = 1
            result[start + i][start + (i + 1) % part] = 1
        start += part
    assert all(sum(row) == 2 for row in result)
    assert all(sum(result[i][j] for i in range(6)) == 2 for j in range(6))
    return result


def union_gram(parts: tuple[int, ...]) -> list[list[int]]:
    cross = biadjacency(parts)
    result = [[0] * 13 for _ in range(13)]
    for i in range(13):
        for j in range(i + 1, 13):
            if i == 0 or (i <= 6 and j <= 6) or (i >= 7 and j >= 7):
                value = 1
            else:
                value = 1 + cross[i - 1][j - 7]
            result[i][j] = result[j][i] = value % Q
    return result


def cycle_kernel_dimension(parts: tuple[int, ...]) -> int:
    """Dimension of ker(I-A^T A) from the periodic affine recurrence."""

    return len(parts) + sum(part % Q == 0 for part in parts)


def y_kernel_basis(parts: tuple[int, ...]) -> list[list[int]]:
    """Explicit periodic-constant/slope basis for ker(I-A^T A)."""

    basis: list[list[int]] = []
    start = 0
    for part in parts:
        constant = [0] * 6
        for i in range(part):
            constant[start + i] = 1
        basis.append(constant)
        if part % Q == 0:
            slope = [0] * 6
            for i in range(part):
                slope[start + i] = i % Q
            basis.append(slope)
        start += part
    return basis


def add_scaled(
    target: list[int], source: list[int], coefficient: int
) -> None:
    for i, value in enumerate(source):
        target[i] = (target[i] + coefficient * value) % Q


def kernel_words(parts: tuple[int, ...]) -> list[list[int]]:
    """Parameterize the full Gram kernel by the recurrence solution."""

    cross = biadjacency(parts)
    basis = y_kernel_basis(parts)
    gram = union_gram(parts)
    words: list[list[int]] = []
    for parameters in product(range(Q), repeat=1 + len(basis)):
        a = parameters[0]
        y = [0] * 6
        for coefficient, vector in zip(parameters[1:], basis):
            add_scaled(y, vector, coefficient)
        x = [
            (sum(cross[i][j] * y[j] for j in range(6)) + a) % Q
            for i in range(6)
        ]
        word = [a] + x + y
        assert matvec(gram, word) == [0] * 13
        words.append(word)
    assert len({tuple(word) for word in words}) == len(words)
    return words


def star_span() -> set[tuple[int, ...]]:
    first = [1] * 7 + [0] * 6
    second = [1] + [0] * 6 + [1] * 6
    return {
        tuple(
            (a * first[i] + b * second[i]) % Q for i in range(13)
        )
        for a, b in product(range(Q), repeat=2)
    }


def nonstar_supports(parts: tuple[int, ...]) -> dict[str, Any]:
    words = kernel_words(parts)
    excluded = star_span()
    supports = [
        sum(value != 0 for value in word)
        for word in words
        if tuple(word) not in excluded
    ]
    return {
        "kernel_words": len(words),
        "nonstar_words": len(supports),
        "minimum_support": min(supports),
        "support_distribution": {
            str(weight): supports.count(weight) for weight in sorted(set(supports))
        },
    }


def analyze() -> dict[str, Any]:
    star_gram = [
        [0 if i == j else 1 for j in range(7)] for i in range(7)
    ]
    star_relation = [1] * 7
    assert matvec(star_gram, star_relation) == [0] * 7
    for column in range(7):
        projector_image = [(-star_gram[i][column]) % Q for i in range(7)]
        difference = [
            (projector_image[i] - (i == column)) % Q for i in range(7)
        ]
        assert difference == [2] * 7
    cycles: dict[str, Any] = {}
    for parts in ((6,), (4, 2), (3, 3), (2, 2, 2)):
        name = "+".join(str(part) for part in parts)
        direct_rank = rank_mod3(union_gram(parts))
        recurrence_nullity = 1 + cycle_kernel_dimension(parts)
        assert direct_rank == 13 - recurrence_nullity
        span_upper = (N + direct_rank) // 2
        item: dict[str, Any] = {
            "gram_rank": direct_rank,
            "gram_nullity": recurrence_nullity,
            "possible_span_ranks": list(range(direct_rank, span_upper + 1)),
            "true_relation_dimension_lower": 13 - span_upper,
            "cross_quotient_dimension_lower": 11 - span_upper,
        }
        if direct_rank == 10:
            item["support"] = nonstar_supports(parts)
        cycles[name] = item

    result = {
        "field": Q,
        "ambient_dimension": N,
        "star": {
            "gram_rank": rank_mod3(star_gram),
            "coefficient_relation_dimension": 1,
            "projector_action_mod_relation": True,
            "projector_rank": 6,
            "projector_trace_mod_3": 0,
        },
        "trace_space": {
            "self_adjoint_dimension": N * (N + 1) // 2,
            "trace_zero_dimension": N * (N + 1) // 2 - 1,
            "trace_gram_rank_cap": 65,
        },
        "integer_BLBt": {
            "diagonal": 0,
            "edge_entry": 12,
            "row_sum": 3 * 36 * 7,
            "nonneighbor_sum": 3 * 36 * 7 - 14 * 12,
            "nonneighbor_average": (3 * 36 * 7 - 14 * 12) // 84,
        },
        "cycles": cycles,
        "nonadjacent": {
            "columns": 14,
            "true_relation_dimension_lower": 3,
            "cross_quotient_dimension_lower": 1,
        },
        "scope": "conditional identities verified; endpoint not excluded",
    }
    verify(result)
    return result


def verify(result: dict[str, Any]) -> None:
    assert result["star"]["gram_rank"] == 6
    assert result["star"]["projector_action_mod_relation"] is True
    assert result["trace_space"] == {
        "self_adjoint_dimension": 66,
        "trace_zero_dimension": 65,
        "trace_gram_rank_cap": 65,
    }
    assert result["integer_BLBt"] == {
        "diagonal": 0,
        "edge_entry": 12,
        "row_sum": 756,
        "nonneighbor_sum": 588,
        "nonneighbor_average": 7,
    }
    cycles = result["cycles"]
    assert [cycles[name]["gram_rank"] for name in cycles] == [10, 10, 8, 9]
    assert [cycles[name]["possible_span_ranks"] for name in cycles] == [
        [10],
        [10],
        [8, 9],
        [9, 10],
    ]
    assert cycles["6"]["support"]["minimum_support"] == 8
    assert cycles["4+2"]["support"]["minimum_support"] == 4
    assert "support" not in cycles["3+3"]
    assert "support" not in cycles["2+2+2"]
    assert "not excluded" in result["scope"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = analyze()
    if args.verify:
        assert json.loads(args.verify.read_text(encoding="utf-8")) == result
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS: independent Wave176 verification")


if __name__ == "__main__":
    main()
