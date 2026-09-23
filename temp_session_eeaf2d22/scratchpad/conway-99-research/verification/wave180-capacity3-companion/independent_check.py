"""Clean-room local algebra and cover arithmetic for Wave 180."""

from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Any


Q = 3


def matvec(matrix: list[list[int]], vector: list[int]) -> list[int]:
    return [
        sum(a * b for a, b in zip(row, vector)) % Q for row in matrix
    ]


def rank3(matrix: list[list[int]]) -> int:
    rows = [[entry % Q for entry in row] for row in matrix]
    pivot = 0
    for column in range(len(rows[0])):
        source = next(
            (i for i in range(pivot, len(rows)) if rows[i][column]), None
        )
        if source is None:
            continue
        rows[pivot], rows[source] = rows[source], rows[pivot]
        if rows[pivot][column] == 2:
            rows[pivot] = [(2 * value) % Q for value in rows[pivot]]
        for i in range(len(rows)):
            factor = rows[i][column] if i != pivot else 0
            if factor:
                rows[i] = [
                    (rows[i][j] - factor * rows[pivot][j]) % Q
                    for j in range(len(rows[i]))
                ]
        pivot += 1
    return pivot


def extended_gram(h: list[int]) -> list[list[int]]:
    star = [[0 if i == j else 1 for j in range(7)] for i in range(7)]
    return [[0] + h] + [[h[i]] + star[i] for i in range(7)]


def projective_weights(first: list[int], second: list[int]) -> list[int]:
    representatives: dict[tuple[int, ...], int] = {}
    for a, b in product(range(Q), repeat=2):
        word = tuple((a * x + b * y) % Q for x, y in zip(first, second))
        if not any(word):
            continue
        lead = next(value for value in word if value)
        canonical = word if lead == 1 else tuple(2 * value % Q for value in word)
        representatives[canonical] = sum(value != 0 for value in canonical)
    return sorted(representatives.values())


def analyze() -> dict[str, Any]:
    star = [0] + [1] * 7
    h0 = [1] * 6 + [0]
    duplicate = [1] + [0] * 6 + [2]
    g0 = extended_gram(h0)
    assert matvec(g0, duplicate) == [0] * 8
    assert matvec(g0, star) == [0] * 8

    h3 = [2] * 3 + [0] * 4
    conic = [1, 2, 2, 2, 0, 0, 0, 0]
    g3 = extended_gram(h3)
    assert matvec(g3, conic) == [0] * 8
    assert matvec(g3, star) == [0] * 8
    support = [i for i, value in enumerate(conic) if value]
    switched_gram = [
        [conic[i] * conic[j] * g3[i][j] % Q for j in support]
        for i in support
    ]

    profiles = {
        str(t): {
            "m0": 1 + t,
            "m1": 6 - 2 * t,
            "m2": t,
            "projector_residue": (6 - t) % Q,
        }
        for t in range(4)
    }
    nonedges = 4158
    nonedge_projective = nonedges // 2
    total_projective = 693 + nonedge_projective
    result = {
        "profiles": profiles,
        "projector_admissible_t": [t for t in range(4) if (6 - t) % Q == 0],
        "t0": {
            "gram_rank": rank3(g0),
            "projective_weights": projective_weights(star, duplicate),
            "duplicate_weight": 2,
        },
        "t3": {
            "gram_rank": rank3(g3),
            "projective_weights": projective_weights(star, conic),
            "switched_conic_gram": switched_gram,
            "companion_weights": [4, 5],
            "same_label_count": 3,
            "fixed_point_free": True,
        },
        "cover": {
            "nonedges": nonedges,
            "nonedge_projective_lower": nonedge_projective,
            "edge_projective": 693,
            "total_projective_lower": total_projective,
            "dual_word_lower": 2 * total_projective,
        },
        "scope": "necessary condition only; endpoint remains unknown",
    }
    verify(result)
    return result


def verify(result: dict[str, Any]) -> None:
    assert result["projector_admissible_t"] == [0, 3]
    assert result["t0"]["projective_weights"] == [2, 7, 7, 8]
    assert result["t3"]["projective_weights"] == [4, 5, 7, 8]
    assert result["t3"]["switched_conic_gram"] == [
        [0, 1, 1, 1],
        [1, 0, 1, 1],
        [1, 1, 0, 1],
        [1, 1, 1, 0],
    ]
    assert result["cover"] == {
        "nonedges": 4158,
        "nonedge_projective_lower": 2079,
        "edge_projective": 693,
        "total_projective_lower": 2772,
        "dual_word_lower": 5544,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = analyze()
    if args.verify:
        assert json.loads(args.verify.read_text(encoding="utf-8")) == result
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS: independent Wave180 verification")


if __name__ == "__main__":
    main()

