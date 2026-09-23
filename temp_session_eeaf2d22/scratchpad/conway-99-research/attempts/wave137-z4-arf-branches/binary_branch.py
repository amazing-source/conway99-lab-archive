"""Exact rational Wave132 binary branches with Arf and optional K1 cuts."""

from __future__ import annotations

import argparse
import importlib.util
import json
from fractions import Fraction
from math import comb
from pathlib import Path

from z3 import Real, Solver, Sum, sat


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WAVE132 = ROOT / "attempts" / "wave132-distinguished-biweight"
SPEC = importlib.util.spec_from_file_location(
    "wave132_discover", WAVE132 / "discover_rational.py"
)
BASE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(BASE)
ARF_MAGNITUDE = 1 << 27
KRAWTCHOUK_MULTIPLIERS = {
    2: 3465,
    3: -56595,
    4: 462924,
    5: -1821204,
}


def signed(weight: int) -> int:
    return 1 if (weight // 2) % 2 == 0 else -1


def encode(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def solve(
    sign: int,
    max_moment: int,
    shadow_lower: tuple[int, ...] = (),
    shadow_upper: tuple[int, ...] = (),
) -> dict:
    variables = {
        weight: Real(f"A_{weight}") for weight in BASE.IMAGE_WEIGHTS
    }
    solver = Solver()
    for weight in BASE.IMAGE_WEIGHTS:
        solver.add(
            variables[weight] >= BASE.IMAGE_LOWER.get(weight, 0)
        )
    solver.add(variables[0] == 1)
    solver.add(
        Sum(
            [variables[weight] for weight in BASE.IMAGE_WEIGHTS]
        )
        == BASE.ORDER
    )
    lower_dual = BASE.dual_lower()
    for degree in range(1, BASE.N + 1):
        numerator = Sum(
            [
                variables[weight]
                * BASE.krawtchouk(degree, weight)
                for weight in BASE.IMAGE_WEIGHTS
            ]
        )
        if degree <= 14:
            solver.add(numerator == 0)
        else:
            solver.add(
                numerator >= lower_dual.get(degree, 0) * BASE.ORDER
            )
    solver.add(
        Sum(
            [
                signed(weight) * variables[weight]
                for weight in BASE.IMAGE_WEIGHTS
            ]
        )
        == sign * ARF_MAGNITUDE
    )
    if max_moment >= 1:
        solver.add(
            Sum(
                [
                    signed(weight)
                    * (BASE.N - weight)
                    * variables[weight]
                    for weight in BASE.IMAGE_WEIGHTS
                ]
            )
            == 0
        )
    for moment in range(2, max_moment + 1):
        solver.add(
            Sum(
                [
                    signed(weight)
                    * BASE.krawtchouk(moment, weight)
                    * variables[weight]
                    for weight in BASE.IMAGE_WEIGHTS
                ]
            )
            == (
                KRAWTCHOUK_MULTIPLIERS[moment]
                * sign
                * ARF_MAGNITUDE
            )
        )
    for degree in shadow_lower:
        solver.add(
            Sum(
                [
                    signed(weight)
                    * BASE.krawtchouk(degree, weight)
                    * variables[weight]
                    for weight in BASE.IMAGE_WEIGHTS
                ]
            )
            >= -(ARF_MAGNITUDE * comb(BASE.N, degree))
        )
    for degree in shadow_upper:
        solver.add(
            Sum(
                [
                    signed(weight)
                    * BASE.krawtchouk(degree, weight)
                    * variables[weight]
                    for weight in BASE.IMAGE_WEIGHTS
                ]
            )
            <= ARF_MAGNITUDE * comb(BASE.N, degree)
        )
    status = solver.check()
    if status != sat:
        return {
            "format": "wave137-binary-arf-branch-v1",
            "claim_label": "UNKNOWN",
            "sign": sign,
            "max_moment": max_moment,
            "shadow_lower_degrees": list(shadow_lower),
            "shadow_upper_degrees": list(shadow_upper),
            "classification": "UNKNOWN_Z3_" + str(status).upper(),
            "limitations": [
                "A solver status without an exact Farkas certificate is not an infeasibility proof."
            ],
        }
    model = solver.model()
    image = {
        weight: BASE.from_z3(
            model.eval(variables[weight], model_completion=True)
        )
        for weight in BASE.IMAGE_WEIGHTS
    }
    dual = {
        degree: sum(
            image[weight] * BASE.krawtchouk(degree, weight)
            for weight in BASE.IMAGE_WEIGHTS
        )
        / BASE.ORDER
        for degree in range(BASE.N + 1)
    }
    if any(value < 0 for value in image.values()):
        raise AssertionError("negative image coefficient")
    if any(value < lower_dual.get(weight, 0) for weight, value in dual.items()):
        raise AssertionError("dual lower bound failure")

    image_vs_neighborhood = {
        weight: BASE.fill_shell(
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
        weight: BASE.fill_shell(
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
        weight: BASE.fill_shell(
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
        weight: BASE.fill_shell(
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
        "format": "wave137-binary-arf-branch-v1",
        "claim_label": "CANDIDATE",
        "classification": "EXACT_RATIONAL_FEASIBLE",
        "scope": (
            "Wave132 low-degree distinguished-row split projection plus "
            "global Arf/Gauss"
            + (
                f" and cumulative signed Krawtchouk moments K1..K{max_moment}"
                if max_moment
                else ""
            )
        ),
        "sign": sign,
        "include_k1": max_moment >= 1,
        "max_moment": max_moment,
        "moment_convention": (
            "K1 is sum_even (-1)^(w/2)(99-w)A_w=0; for "
            "t>=2, sum_even (-1)^(w/2)K_t(w)A_w=S_t*G_R"
        ),
        "moment_targets": {
            "K1_binomial": 0,
            **{
                f"K{moment}_multiplier": (
                    KRAWTCHOUK_MULTIPLIERS[moment]
                )
                for moment in range(2, max_moment + 1)
            },
        },
        "shadow_cuts": {
            "lower_degrees": list(shadow_lower),
            "upper_degrees": list(shadow_upper),
            "bound": "|M_t| <= 2^27 * binom(99,t)",
        },
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
                "ordered_diagonal": {"intersection_14": 99},
                "ordered_off_diagonal": {"intersection_2": 9702},
            },
        },
        "split_enumerators": {
            "image_vs_neighborhood": BASE.encode_split(
                image_vs_neighborhood
            ),
            "dual_vs_closed": BASE.encode_split(dual_vs_closed),
            "image_vs_closed": BASE.encode_split(image_vs_closed),
            "dual_vs_neighborhood": BASE.encode_split(
                dual_vs_neighborhood
            ),
        },
        "limitations": [
            "Formal rational low-degree split enumerator only.",
            "The full genus-two transform is not encoded.",
            "No binary code, graph, or adjacency matrix is constructed.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sign", type=int, choices=(-1, 1), required=True)
    parser.add_argument("--k1", action="store_true")
    parser.add_argument(
        "--max-moment",
        type=int,
        choices=range(0, 6),
        default=0,
    )
    parser.add_argument(
        "--shadow-lower",
        type=int,
        action="append",
        default=[],
    )
    parser.add_argument(
        "--shadow-upper",
        type=int,
        action="append",
        default=[],
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    max_moment = max(args.max_moment, 1 if args.k1 else 0)
    payload = solve(
        args.sign,
        max_moment,
        tuple(sorted(set(args.shadow_lower))),
        tuple(sorted(set(args.shadow_upper))),
    )
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        args.sign,
        f"K1..K{max_moment}" if max_moment else "global",
        payload["classification"],
    )


if __name__ == "__main__":
    main()
