"""Exact rational optimization of the Wave137 ordinary projection with S6."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from fractions import Fraction
from math import comb
from pathlib import Path

from z3 import Optimize, Real, Sum, sat


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WAVE132 = ROOT / "attempts/wave132-distinguished-biweight"
WAVE137 = ROOT / "attempts/wave137-z4-arf-branches"
ARF_MAGNITUDE = 1 << 27
S_VALUES = {
    0: 1,
    1: -99,
    2: 3465,
    3: -56595,
    4: 462924,
    5: -1821204,
}
S6_CONSTANT = 2024484
S6_N3_NUMERATOR = 512
S6_N3_DENOMINATOR = 3


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load("wave143_wave132_discover", WAVE132 / "discover_rational.py")


def signed(weight: int) -> int:
    return 1 if (weight // 2) % 2 == 0 else -1


def moment(variables: dict[int, object], degree: int):
    return Sum(
        [
            signed(weight)
            * BASE.krawtchouk(degree, weight)
            * variables[weight]
            for weight in BASE.IMAGE_WEIGHTS
        ]
    )


def encode(value: Fraction | int) -> str:
    value = Fraction(value)
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def from_z3(value) -> Fraction:
    if value.is_int():
        return Fraction(value.as_long())
    return Fraction(value.numerator_as_long(), value.denominator_as_long())


def add_rational_constraints(
    optimizer: Optimize,
    variables: dict[int, object],
    n3,
    sign: int,
) -> None:
    for weight in BASE.IMAGE_WEIGHTS:
        optimizer.add(variables[weight] >= BASE.IMAGE_LOWER.get(weight, 0))
    optimizer.add(variables[0] == 1)
    optimizer.add(
        Sum([variables[weight] for weight in BASE.IMAGE_WEIGHTS])
        == BASE.ORDER
    )

    dual_lower = BASE.dual_lower()
    for degree in range(1, BASE.N + 1):
        numerator = Sum(
            [
                variables[weight] * BASE.krawtchouk(degree, weight)
                for weight in BASE.IMAGE_WEIGHTS
            ]
        )
        if degree <= 14:
            optimizer.add(numerator == 0)
        else:
            optimizer.add(
                numerator >= dual_lower.get(degree, 0) * BASE.ORDER
            )

    for degree, multiplier in S_VALUES.items():
        optimizer.add(
            moment(variables, degree)
            == sign * ARF_MAGNITUDE * multiplier
        )

    for degree in range(6, BASE.N + 1):
        bound = ARF_MAGNITUDE * comb(BASE.N, degree)
        value = moment(variables, degree)
        optimizer.add(value >= -bound, value <= bound)

    optimizer.add(n3 >= 0)
    optimizer.add(
        S6_N3_DENOMINATOR * moment(variables, 6)
        == sign
        * ARF_MAGNITUDE
        * (
            S6_N3_DENOMINATOR * S6_CONSTANT
            + S6_N3_NUMERATOR * n3
        )
    )


def split_payload(
    image: dict[int, Fraction],
    dual: dict[int, Fraction],
) -> dict:
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
        "image_vs_neighborhood": BASE.encode_split(image_vs_neighborhood),
        "dual_vs_closed": BASE.encode_split(dual_vs_closed),
        "image_vs_closed": BASE.encode_split(image_vs_closed),
        "dual_vs_neighborhood": BASE.encode_split(dual_vs_neighborhood),
    }


def solve(
    sign: int,
    sense: str | None = None,
    fixed_n3: int | None = None,
) -> dict:
    if (sense is None) == (fixed_n3 is None):
        raise ValueError("choose exactly one of sense or fixed_n3")
    variables = {
        weight: Real(f"A_{weight}") for weight in BASE.IMAGE_WEIGHTS
    }
    n3 = Real("n3")
    optimizer = Optimize()
    optimizer.set(priority="lex")
    add_rational_constraints(optimizer, variables, n3, sign)
    if fixed_n3 is not None:
        optimizer.add(n3 == fixed_n3)
        handle = None
    else:
        handle = (
            optimizer.maximize(n3)
            if sense == "max"
            else optimizer.minimize(n3)
        )
    status = optimizer.check()
    if status != sat:
        raise RuntimeError(f"exact rational optimization returned {status}")
    model = optimizer.model()
    optimum = (
        Fraction(fixed_n3)
        if fixed_n3 is not None
        else from_z3(handle.value())
    )
    model_n3 = from_z3(model.eval(n3, model_completion=True))
    if model_n3 != optimum:
        raise AssertionError(f"model/handle optimum drift: {model_n3} != {optimum}")
    image = {
        weight: from_z3(model.eval(variable, model_completion=True))
        for weight, variable in variables.items()
    }
    dual = {
        degree: sum(
            image[weight] * BASE.krawtchouk(degree, weight)
            for weight in BASE.IMAGE_WEIGHTS
        )
        / BASE.ORDER
        for degree in range(BASE.N + 1)
    }
    s6_moment = sum(
        signed(weight)
        * BASE.krawtchouk(6, weight)
        * image[weight]
        for weight in BASE.IMAGE_WEIGHTS
    )
    expected_s6 = sign * ARF_MAGNITUDE * (
        Fraction(S6_CONSTANT)
        + Fraction(S6_N3_NUMERATOR, S6_N3_DENOMINATOR) * optimum
    )
    if s6_moment != expected_s6:
        raise AssertionError("S6 endpoint equation drift")

    return {
        "format": "wave143-binary-s6-witness-v1",
        "claim_label": "CANDIDATE_EXACT",
        "classification": (
            "EXACT_RATIONAL_FEASIBLE"
            if fixed_n3 is not None
            else "EXACT_RATIONAL_OPTIMUM"
        ),
        "scope": (
            "Wave137 ordinary/distinguished-split rational projection, "
            "both Arf/K0..K5 identities, all K6..K99 shadow bounds, "
            "and the exact Wave141 S6/n3 equation"
        ),
        "sign": sign,
        "sense": sense,
        "witness_kind": (
            "fixed_n3" if fixed_n3 is not None else "projection_optimum"
        ),
        "n3": encode(optimum),
        "S6_multiplier": encode(
            Fraction(S6_CONSTANT)
            + Fraction(S6_N3_NUMERATOR, S6_N3_DENOMINATOR) * optimum
        ),
        "M6": encode(s6_moment),
        "optimization": {
            "engine": "Z3 Optimize exact linear rational arithmetic",
            "objective": (
                f"feasibility at n3={fixed_n3}"
                if fixed_n3 is not None
                else sense + " n3"
            ),
            "optimum": encode(optimum),
            "all_shadow_degrees": list(range(6, BASE.N + 1)),
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
        "split_enumerators": split_payload(image, dual),
        "limitations": [
            "Formal rational projection only.",
            "The bivariate transform and full genus-two transform are absent.",
            "No integral enumerator, binary code, graph, or adjacency matrix is constructed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sign", type=int, choices=(-1, 1), required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sense", choices=("min", "max"))
    group.add_argument("--fixed-n3", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = solve(args.sign, args.sense, args.fixed_n3)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(args.sign, payload["witness_kind"], payload["n3"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
