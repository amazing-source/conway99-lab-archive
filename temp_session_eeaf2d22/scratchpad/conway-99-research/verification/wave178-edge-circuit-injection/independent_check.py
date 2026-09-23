"""Independent recurrence check for Wave 178 local profiles."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Any


Q = 3


def biadjacency(parts: tuple[int, ...]) -> list[list[int]]:
    matrix = [[0] * 6 for _ in range(6)]
    start = 0
    for size in parts:
        for i in range(size):
            matrix[start + i][start + i] = 1
            matrix[start + i][start + (i + 1) % size] = 1
        start += size
    return matrix


def y_basis(parts: tuple[int, ...]) -> list[list[int]]:
    """Periodic affine solutions of (I-A^T A)y=0."""

    basis: list[list[int]] = []
    start = 0
    for size in parts:
        constant = [0] * 6
        for i in range(size):
            constant[start + i] = 1
        basis.append(constant)
        if size % Q == 0:
            slope = [0] * 6
            for i in range(size):
                slope[start + i] = i % Q
            basis.append(slope)
        start += size
    return basis


def add_scaled(target: list[int], source: list[int], scalar: int) -> None:
    for i in range(6):
        target[i] = (target[i] + scalar * source[i]) % Q


def profiles(parts: tuple[int, ...]) -> dict[str, Any]:
    matrix = biadjacency(parts)
    basis = y_basis(parts)
    counts: Counter[tuple[int, int, int, int, int]] = Counter()
    inspected = 0
    for coefficients in product(range(Q), repeat=len(basis)):
        inspected += 1
        y = [0] * 6
        for scalar, vector in zip(coefficients, basis):
            add_scaled(y, vector, scalar)
        x = [
            sum(matrix[i][j] * y[j] for j in range(6)) % Q
            for i in range(6)
        ]
        word = x + y
        # At common coefficient zero, the individual-star span is precisely
        # the global-constant y lane.
        if len(set(y)) == 1:
            continue
        weight = sum(value != 0 for value in word)
        if weight > 8:
            continue
        counts[
            (
                weight,
                sum(value != 0 for value in x),
                sum(value != 0 for value in y),
                word.count(1),
                word.count(2),
            )
        ] += 1
    return {
        "outer_kernel_dimension": len(basis),
        "vectors_inspected": inspected,
        "profiles": [
            {
                "weight": key[0],
                "left_support": key[1],
                "right_support": key[2],
                "coefficient_1_count": key[3],
                "coefficient_2_count": key[4],
                "word_count": count,
            }
            for key, count in sorted(counts.items())
        ],
    }


def analyze() -> dict[str, Any]:
    types = {
        "+".join(map(str, parts)): profiles(parts)
        for parts in ((6,), (4, 2), (3, 3), (2, 2, 2))
    }
    result = {
        "field": Q,
        "edge_count": 99 * 14 // 2,
        "support_multiplicity_upper": 1,
        "projective_circuit_lower": 693,
        "word_bound": 2 * 693,
        "cycle_types": types,
        "all_profiles_balanced": all(
            profile["weight"] in (4, 6, 8)
            and profile["left_support"] == profile["right_support"]
            and profile["coefficient_1_count"]
            == profile["coefficient_2_count"]
            for item in types.values()
            for profile in item["profiles"]
        ),
        "scope": "necessary condition only; endpoint remains unknown",
    }
    verify(result)
    return result


def verify(result: dict[str, Any]) -> None:
    assert result["edge_count"] == 693
    assert result["support_multiplicity_upper"] == 1
    assert result["word_bound"] == 1386
    assert result["all_profiles_balanced"]
    expected = {
        "6": [(8, 4, 4, 4, 4, 6)],
        "4+2": [(4, 2, 2, 2, 2, 2), (8, 4, 4, 4, 4, 2)],
        "3+3": [
            (4, 2, 2, 2, 2, 12),
            (6, 3, 3, 3, 3, 4),
            (8, 4, 4, 4, 4, 36),
        ],
        "2+2+2": [(4, 2, 2, 2, 2, 6), (8, 4, 4, 4, 4, 12)],
    }
    observed = {
        name: [
            (
                p["weight"],
                p["left_support"],
                p["right_support"],
                p["coefficient_1_count"],
                p["coefficient_2_count"],
                p["word_count"],
            )
            for p in item["profiles"]
        ]
        for name, item in result["cycle_types"].items()
    }
    assert observed == expected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = analyze()
    if args.verify:
        assert json.loads(args.verify.read_text(encoding="utf-8")) == result
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS: independent Wave178 verification")


if __name__ == "__main__":
    main()

