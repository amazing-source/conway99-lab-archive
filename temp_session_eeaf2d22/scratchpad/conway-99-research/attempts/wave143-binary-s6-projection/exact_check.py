"""Independent exact replay of Wave143 rational endpoint witnesses."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from fractions import Fraction
from math import comb
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WAVE132 = ROOT / "attempts/wave132-distinguished-biweight"
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
MAX_N3 = Fraction(838878579, 128)


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load("wave143_wave132_exact", WAVE132 / "exact_check.py")


def parse(value: str | int) -> Fraction:
    return Fraction(value)


def signed(weight: int) -> int:
    return 1 if (weight // 2) % 2 == 0 else -1


def signed_moment(image: list[Fraction], degree: int) -> Fraction:
    return sum(
        (
            signed(weight)
            * BASE.krawtchouk(degree, weight)
            * coefficient
            for weight, coefficient in enumerate(image)
            if coefficient
        ),
        Fraction(0),
    )


def verify(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload["format"] != "wave143-binary-s6-witness-v1":
        raise AssertionError("wrong witness format")
    if payload["classification"] not in (
        "EXACT_RATIONAL_OPTIMUM",
        "EXACT_RATIONAL_FEASIBLE",
    ):
        raise AssertionError("witness is not classified exact rational")
    sign = int(payload["sign"])
    sense = payload["sense"]
    witness_kind = payload["witness_kind"]
    if sign not in (-1, 1):
        raise AssertionError("bad branch")
    if witness_kind == "projection_optimum":
        if sense not in ("min", "max"):
            raise AssertionError("bad projection optimum sense")
    elif witness_kind == "fixed_n3":
        if sense is not None:
            raise AssertionError("fixed witness unexpectedly has a sense")
    else:
        raise AssertionError("bad witness kind")

    image, dual = BASE.arrays(payload)
    ordinary = BASE.ordinary_audit(image, dual)
    BASE.pair_table_audit(payload)
    split = payload["split_enumerators"]
    split_audits = {
        "image_vs_neighborhood": BASE.split_audit(
            split["image_vs_neighborhood"],
            image,
            14,
            "weight",
            {14: {14: 99, 1: 1386, 2: 8316}},
        ),
        "dual_vs_closed": BASE.split_audit(
            split["dual_vs_closed"],
            dual,
            15,
            "weight",
            {15: {15: 99, 3: 1386, 2: 8316}},
        ),
        "image_vs_closed": BASE.split_audit(
            split["image_vs_closed"],
            image,
            15,
            "zero",
            {14: {14: 99, 2: 9702}},
        ),
        "dual_vs_neighborhood": BASE.split_audit(
            split["dual_vs_neighborhood"],
            dual,
            14,
            "zero",
            {15: {14: 99, 2: 9702}},
        ),
    }

    moments = {}
    for degree, multiplier in S_VALUES.items():
        value = signed_moment(image, degree)
        expected = sign * ARF_MAGNITUDE * multiplier
        if value != expected:
            raise AssertionError(f"K{degree} signed identity drift")
        moments[f"M{degree}"] = str(value)

    n3 = parse(payload["n3"])
    m6 = signed_moment(image, 6)
    expected_m6 = sign * ARF_MAGNITUDE * (
        S6_CONSTANT + Fraction(512, 3) * n3
    )
    if m6 != expected_m6 or m6 != parse(payload["M6"]):
        raise AssertionError("S6/n3 equation drift")

    active_shadow = []
    for degree in range(6, BASE.N + 1):
        value = signed_moment(image, degree)
        bound = ARF_MAGNITUDE * comb(BASE.N, degree)
        if not -bound <= value <= bound:
            raise AssertionError(f"K{degree} shadow bound fails")
        if abs(value) == bound:
            active_shadow.append(degree)

    # Exact optimality certificates are one-line inequalities:
    # n3 >= 0 is explicit; at the upper endpoint the sign-appropriate M6
    # shadow side gives S6 <= binom(99,6).
    if witness_kind == "projection_optimum":
        expected_n3 = Fraction(0) if sense == "min" else MAX_N3
        if n3 != expected_n3:
            raise AssertionError("projection optimum drift")
        if sense == "max":
            bound = ARF_MAGNITUDE * comb(BASE.N, 6)
            if m6 != sign * bound:
                raise AssertionError(
                    "upper shadow certificate is not active"
                )
            certificate = (
                "sign*M6<=2^27*binom(99,6), combined with "
                "M6=sign*2^27*(2024484+(512/3)n3)"
            )
        else:
            certificate = "explicit model constraint n3>=0"
    else:
        if n3 not in (708, 4158):
            raise AssertionError("unexpected fixed-n3 witness")
        certificate = "exact rational feasible witness replay"

    return {
        "path": str(path),
        "sign": sign,
        "sense": sense,
        "witness_kind": witness_kind,
        "n3": str(n3),
        "M6": str(m6),
        "optimality_certificate": certificate,
        "active_shadow_degrees": active_shadow,
        "all_94_shadow_bounds_pass": True,
        "ordinary": ordinary,
        "split_audits": split_audits,
        "moments_M0_through_M5": moments,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    results = [verify(path) for path in args.paths]
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
