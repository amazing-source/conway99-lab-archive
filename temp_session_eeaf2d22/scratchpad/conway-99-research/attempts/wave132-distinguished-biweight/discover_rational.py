"""Discover an exact rational distinguished-row biweight witness.

The full genus-two MacWilliams transform is not encoded.  This script solves
the ordinary MacWilliams system with the exact distinguished-row support
cut A_94=A_96=A_98=0, then extends every weight shell to four exact split
intersection distributions.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from math import comb
from pathlib import Path

from z3 import Real, Solver, Sum, sat


N = 99
K = 54
ORDER = 1 << K
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "joint-witness.json"
IMAGE_WEIGHTS = [0] + list(range(14, 94, 2))
IMAGE_LOWER = {
    0: 1,
    14: 99,
    24: 4158,
    26: 693,
    30: 70686,
    32: 41580,
    34: 36036,
    36: 8547,
}
DUAL_BASE_LOWER = {
    0: 1,
    15: 99,
    24: 693,
    26: 4158,
    31: 41580,
    33: 79002,
    35: 8316,
    37: 27720,
    39: 231,
    99: 1,
}


def krawtchouk(degree: int, weight: int) -> int:
    return sum(
        (-1) ** overlap
        * comb(weight, overlap)
        * comb(N - weight, degree - overlap)
        for overlap in range(
            max(0, degree - (N - weight)),
            min(weight, degree) + 1,
        )
    )


def dual_lower() -> dict[int, int]:
    result = dict(DUAL_BASE_LOWER)
    for weight, value in list(result.items()):
        result[N - weight] = max(result.get(N - weight, 0), value)
    return result


def from_z3(value) -> Fraction:
    return Fraction(value.numerator_as_long(), value.denominator_as_long())


def encode(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def fill_shell(
    coefficient: Fraction,
    weight: int,
    distinguished_weight: int,
    odd_per_word: int,
    forced: dict[int, int],
) -> dict[int, Fraction]:
    """Construct an exact shell distribution from parity and first moment."""
    lower = max(0, weight + distinguished_weight - N)
    upper = min(weight, distinguished_weight)
    levels = list(range(lower, upper + 1))
    total = 99 * coefficient - sum(Fraction(value) for value in forced.values())
    moment = (
        distinguished_weight * weight * coefficient
        - sum(Fraction(level * value) for level, value in forced.items())
    )
    odd = (
        odd_per_word * coefficient
        - sum(
            Fraction(value)
            for level, value in forced.items()
            if level % 2
        )
    )
    even = total - odd
    if total < 0 or odd < 0 or even < 0:
        raise AssertionError("forced split count exceeds shell")

    groups = []
    for parity, count in ((1, odd), (0, even)):
        parity_levels = [level for level in levels if level % 2 == parity]
        if count and not parity_levels:
            raise AssertionError("required parity unavailable")
        groups.append((count, parity_levels))
    minimum = sum(
        count * min(parity_levels)
        for count, parity_levels in groups
        if count
    )
    maximum = sum(
        count * max(parity_levels)
        for count, parity_levels in groups
        if count
    )
    if not minimum <= moment <= maximum:
        raise AssertionError(
            f"shell moment infeasible at weight {weight}: "
            f"{minimum} <= {moment} <= {maximum}"
        )

    result = {
        level: Fraction(value)
        for level, value in forced.items()
        if value
    }
    excess = moment - minimum
    for count, parity_levels in groups:
        if not count:
            continue
        low = min(parity_levels)
        high = max(parity_levels)
        capacity = count * (high - low)
        used = min(excess, capacity)
        excess -= used
        if high == low:
            result[low] = result.get(low, Fraction(0)) + count
            continue
        high_count = used / (high - low)
        result[high] = result.get(high, Fraction(0)) + high_count
        result[low] = result.get(low, Fraction(0)) + count - high_count
    if excess:
        raise AssertionError("unallocated shell moment")
    return {
        level: value for level, value in sorted(result.items()) if value
    }


def encode_split(table: dict[int, dict[int, Fraction]]) -> dict:
    return {
        str(weight): {
            str(intersection): encode(value)
            for intersection, value in row.items()
        }
        for weight, row in table.items()
    }


def discover() -> dict:
    variables = {
        weight: Real(f"A_{weight}") for weight in IMAGE_WEIGHTS
    }
    lower_dual = dual_lower()
    solver = Solver()
    for weight in IMAGE_WEIGHTS:
        solver.add(variables[weight] >= IMAGE_LOWER.get(weight, 0))
    solver.add(variables[0] == 1)
    solver.add(
        Sum([variables[weight] for weight in IMAGE_WEIGHTS]) == ORDER
    )
    for degree in range(1, N + 1):
        numerator = Sum(
            [
                variables[weight] * krawtchouk(degree, weight)
                for weight in IMAGE_WEIGHTS
            ]
        )
        if degree <= 14:
            solver.add(numerator == 0)
        else:
            solver.add(
                numerator >= lower_dual.get(degree, 0) * ORDER
            )
    status = solver.check()
    if status != sat:
        raise SystemExit(f"distinguished-row rational scout returned {status}")
    model = solver.model()
    image = {
        weight: from_z3(
            model.eval(variables[weight], model_completion=True)
        )
        for weight in IMAGE_WEIGHTS
    }
    dual = {
        degree: sum(
            image[weight] * krawtchouk(degree, weight)
            for weight in IMAGE_WEIGHTS
        )
        / ORDER
        for degree in range(N + 1)
    }
    if any(value < 0 for value in image.values()) or any(
        value < 0 for value in dual.values()
    ):
        raise AssertionError("negative ordinary coefficient")

    image_vs_neighborhood = {
        weight: fill_shell(
            coefficient,
            weight,
            14,
            weight,
            {14: 99, 1: 1386, 2: 8316} if weight == 14 else {},
        )
        for weight, coefficient in image.items()
        if coefficient
    }
    dual_vs_closed = {
        weight: fill_shell(
            coefficient,
            weight,
            15,
            weight,
            {15: 99, 3: 1386, 2: 8316} if weight == 15 else {},
        )
        for weight, coefficient in dual.items()
        if coefficient
    }
    image_vs_closed = {
        weight: fill_shell(
            coefficient,
            weight,
            15,
            0,
            {14: 99, 2: 9702} if weight == 14 else {},
        )
        for weight, coefficient in image.items()
        if coefficient
    }
    dual_vs_neighborhood = {
        weight: fill_shell(
            coefficient,
            weight,
            14,
            0,
            {14: 99, 2: 9702} if weight == 15 else {},
        )
        for weight, coefficient in dual.items()
        if coefficient
    }

    return {
        "format": "wave132-distinguished-biweight-witness-v1",
        "claim_label": "CANDIDATE",
        "scope": (
            "Exact low-degree distinguished-row split-enumerator "
            "projection; not the full genus-two MacWilliams system."
        ),
        "ordinary": {
            "image_coefficients": {
                str(weight): encode(value)
                for weight, value in image.items()
                if value
            },
            "dual_coefficients": {
                str(weight): encode(value)
                for weight, value in dual.items()
                if value
            },
        },
        "distinguished_pair_tables": {
            "image_neighborhood_rows": {
                "14": {"intersection_14": 99},
                "ordered_distinct": {
                    "intersection_1": 1386,
                    "intersection_2": 8316,
                },
            },
            "dual_closed_neighborhood_rows": {
                "15": {"intersection_15": 99},
                "ordered_distinct": {
                    "intersection_3": 1386,
                    "intersection_2": 8316,
                },
            },
            "mixed_neighborhood_closed": {
                "ordered_diagonal": {
                    "intersection_14": 99
                },
                "ordered_off_diagonal": {
                    "intersection_2": 9702
                },
            },
        },
        "split_enumerators": {
            "image_vs_neighborhood": encode_split(
                image_vs_neighborhood
            ),
            "dual_vs_closed": encode_split(dual_vs_closed),
            "image_vs_closed": encode_split(image_vs_closed),
            "dual_vs_neighborhood": encode_split(
                dual_vs_neighborhood
            ),
        },
        "limitations": [
            "All coefficients are formal nonnegative rationals.",
            "The full genus-two partial-Hadamard/MacWilliams transform is not encoded.",
            "Different distinguished roots are coupled only through the exact aggregate pair tables.",
            "No binary code, adjacency matrix, or graph is constructed.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = discover()
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
