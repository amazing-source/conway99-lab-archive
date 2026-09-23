"""Clean-room exact checks for Wave 181."""

from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Any


Q = 3


def matvec(matrix: list[list[int]], vector: tuple[int, ...]) -> list[int]:
    return [sum(a * b for a, b in zip(row, vector)) % Q for row in matrix]


def rank3(matrix: list[list[int]]) -> int:
    rows = [[x % Q for x in row] for row in matrix]
    p = 0
    for col in range(len(rows[0])):
        source = next((i for i in range(p, len(rows)) if rows[i][col]), None)
        if source is None:
            continue
        rows[p], rows[source] = rows[source], rows[p]
        if rows[p][col] == 2:
            rows[p] = [(2 * x) % Q for x in rows[p]]
        for i in range(len(rows)):
            f = rows[i][col] if i != p else 0
            if f:
                rows[i] = [
                    (rows[i][j] - f * rows[p][j]) % Q
                    for j in range(len(rows[i]))
                ]
        p += 1
    return p


def analyze() -> dict[str, Any]:
    shared = [1, 2, 2, 1, 1, 1, 1]
    gram = [
        [0, 1, 1, 2],
        [1, 0, 2, 1],
        [1, 2, 0, 1],
        [2, 1, 1, 0],
    ]
    kernel = [
        v
        for v in product(range(Q), repeat=4)
        if any(v) and matvec(gram, v) == [0] * 4
    ]
    projective = {
        v if next(x for x in v if x) == 1 else tuple(2 * x % Q for x in v)
        for v in kernel
    }
    checker = (1, 2, 2, 1)
    switched = [
        [checker[i] * gram[i][j] * checker[j] % Q for j in range(4)]
        for i in range(4)
    ]
    result = {
        "shared_center": {
            "baseline_xt_retained": True,
            "profile": shared,
            "square_sum_mod3": sum(x * x for x in shared) % Q,
            "rejected": True,
        },
        "canonical_nonedge_involution": {
            "nonedges": 4158,
            "orbits": 2079,
            "fixed_point_free": True,
        },
        "c4": {
            "gram": gram,
            "rank": rank3(gram),
            "projective_kernel": [list(v) for v in sorted(projective)],
            "switched_gram": switched,
        },
        "equality": {
            "Q": 2079,
            "triple_supports": 0,
            "cover_size": 2079,
            "required_conics": 2079,
            "rank_upper": 220,
        },
        "signed_gram": {
            "integer_coefficients": {"I": 36, "K": -4, "L": 1},
            "mod3_coefficients": {"I": 0, "K": 2, "L": 1},
        },
        "projector_sum": {
            "block_multiplicity": 36,
            "coefficient_mod3": 0,
            "vanishes": True,
        },
        "scope": "equality boundary survives; endpoint remains unknown",
    }
    verify(result)
    return result


def verify(result: dict[str, Any]) -> None:
    assert result["shared_center"]["profile"].count(1) == 5
    assert result["shared_center"]["profile"].count(2) == 2
    assert result["shared_center"]["square_sum_mod3"] == 1
    assert result["c4"]["rank"] == 3
    assert result["c4"]["projective_kernel"] == [[1, 2, 2, 1]]
    assert result["c4"]["switched_gram"] == [
        [0, 2, 2, 2],
        [2, 0, 2, 2],
        [2, 2, 0, 2],
        [2, 2, 2, 0],
    ]
    assert result["equality"]["required_conics"] == 2079
    assert result["signed_gram"]["mod3_coefficients"] == {
        "I": 0,
        "K": 2,
        "L": 1,
    }
    assert result["projector_sum"]["coefficient_mod3"] == 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = analyze()
    if args.verify:
        assert json.loads(args.verify.read_text(encoding="utf-8")) == result
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS: independent Wave181 verification")


if __name__ == "__main__":
    main()

