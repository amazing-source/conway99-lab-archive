"""Find and emit an exact rational ordinary MacWilliams witness.

This is discovery tooling.  A SAT result is only a formal weight-enumerator
candidate, not a binary code, adjacency matrix, or graph.
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
DEFAULT_OUTPUT = HERE / "rational-witness.json"
WEIGHTS = [0] + list(range(14, 100, 2))
A_LOWER = {
    0: 1,
    14: 99,
    24: 4158,
    26: 693,
    30: 70686,
    32: 41580,
    34: 36036,
    36: 8547,
}
B_BASE_LOWER = {
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


def lower_with_complements() -> dict[int, int]:
    lower = dict(B_BASE_LOWER)
    for weight, value in list(lower.items()):
        lower[N - weight] = max(lower.get(N - weight, 0), value)
    return lower


def fraction_from_z3(value) -> Fraction:
    return Fraction(value.numerator_as_long(), value.denominator_as_long())


def encode(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def discover() -> dict:
    variables = {weight: Real(f"A_{weight}") for weight in WEIGHTS}
    dual_lower = lower_with_complements()
    solver = Solver()
    for weight in WEIGHTS:
        solver.add(variables[weight] >= A_LOWER.get(weight, 0))
    solver.add(variables[0] == 1)
    solver.add(Sum([variables[weight] for weight in WEIGHTS]) == ORDER)

    for degree in range(1, N + 1):
        numerator = Sum(
            [
                variables[weight] * krawtchouk(degree, weight)
                for weight in WEIGHTS
            ]
        )
        if degree <= 14:
            solver.add(numerator == 0)
        else:
            solver.add(numerator >= dual_lower.get(degree, 0) * ORDER)

    status = solver.check()
    if status != sat:
        raise SystemExit(f"rational MacWilliams scout returned {status}")
    model = solver.model()
    image = {
        weight: fraction_from_z3(
            model.eval(variables[weight], model_completion=True)
        )
        for weight in WEIGHTS
    }
    dual = {
        degree: sum(
            image[weight] * krawtchouk(degree, weight)
            for weight in WEIGHTS
        )
        / ORDER
        for degree in range(N + 1)
    }

    if sum(image.values()) != ORDER:
        raise AssertionError("image size drift")
    if any(value < 0 for value in image.values()):
        raise AssertionError("negative image coefficient")
    if any(dual[degree] != 0 for degree in range(1, 15)):
        raise AssertionError("dual distance drift")
    if any(value < 0 for value in dual.values()):
        raise AssertionError("negative dual coefficient")
    if any(
        image.get(weight, Fraction(0)) < lower
        for weight, lower in A_LOWER.items()
    ):
        raise AssertionError("image forced lower bound drift")
    if any(
        dual[weight] < lower
        for weight, lower in dual_lower.items()
    ):
        raise AssertionError("dual forced lower bound drift")
    if any(dual[weight] != dual[N - weight] for weight in range(N + 1)):
        raise AssertionError("dual complement symmetry drift")
    if sum(dual.values()) != (1 << 45):
        raise AssertionError("dual size drift")

    return {
        "format": "wave131-rational-macwilliams-witness-v1",
        "claim_label": "CANDIDATE",
        "length": N,
        "image_dimension": 54,
        "dual_dimension": 45,
        "image_minimum_nonzero_weight": min(
            weight for weight, value in image.items() if weight and value
        ),
        "dual_minimum_nonzero_weight": min(
            weight for weight, value in dual.items() if weight and value
        ),
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
        "limitations": [
            "Coefficients are nonnegative rationals, not necessarily integers.",
            "An ordinary formal enumerator is not a realized binary code.",
            "LCD intersection data and distinguished graph rows are not encoded.",
            "No graph or Conway-99 resolution is claimed.",
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
