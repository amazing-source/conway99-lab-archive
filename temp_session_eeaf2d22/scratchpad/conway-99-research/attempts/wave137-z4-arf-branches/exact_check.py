"""Independent exact replay for Wave137 binary Arf/K1 branch witnesses."""

from __future__ import annotations

import argparse
import importlib.util
import json
from fractions import Fraction
from math import comb
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WAVE132 = ROOT / "attempts" / "wave132-distinguished-biweight"
SPEC = importlib.util.spec_from_file_location(
    "wave132_exact_check", WAVE132 / "exact_check.py"
)
BASE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(BASE)
ARF_MAGNITUDE = 1 << 27
DUAL_GAUSS_MAGNITUDE = 1 << 22
KRAWTCHOUK_MULTIPLIERS = {
    2: 3465,
    3: -56595,
    4: 462924,
    5: -1821204,
}


def signed_even_sum(values: list[Fraction]) -> Fraction:
    return sum(
        (
            (1 if (weight // 2) % 2 == 0 else -1) * value
            for weight, value in enumerate(values)
            if weight % 2 == 0
        ),
        Fraction(0),
    )


def signed_k1(values: list[Fraction]) -> Fraction:
    return sum(
        (
            (1 if (weight // 2) % 2 == 0 else -1)
            * (BASE.N - weight)
            * value
            for weight, value in enumerate(values)
            if weight % 2 == 0
        ),
        Fraction(0),
    )


def signed_krawtchouk(
    values: list[Fraction], degree: int
) -> Fraction:
    return sum(
        (
            (1 if (weight // 2) % 2 == 0 else -1)
            * BASE.krawtchouk(degree, weight)
            * value
            for weight, value in enumerate(values)
            if weight % 2 == 0
        ),
        Fraction(0),
    )


def verify(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload["format"] != "wave137-binary-arf-branch-v1":
        raise AssertionError("wrong branch format")
    if payload["classification"] != "EXACT_RATIONAL_FEASIBLE":
        return {
            "classification": payload["classification"],
            "terminal_witness_replayed": False,
        }
    sign = payload["sign"]
    if sign not in (-1, 1):
        raise AssertionError("bad Arf sign")
    image, dual = BASE.arrays(payload)
    ordinary = BASE.ordinary_audit(image, dual)
    BASE.pair_table_audit(payload)
    split = payload["split_enumerators"]
    audits = {
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
    g_r = signed_even_sum(image)
    g_e = signed_even_sum(dual)
    if g_r != sign * ARF_MAGNITUDE:
        raise AssertionError("primal Arf/Gauss branch fails")
    if g_e != -sign * DUAL_GAUSS_MAGNITUDE:
        raise AssertionError("dual Gauss relation fails")
    if g_e != -g_r / 32:
        raise AssertionError("ordinary Gauss ratio fails")
    k1 = signed_k1(image)
    max_moment = payload.get(
        "max_moment", 1 if payload["include_k1"] else 0
    )
    if max_moment >= 1 and k1:
        raise AssertionError("K1 signed moment fails")
    krawtchouk_moments = {}
    for degree in range(2, max_moment + 1):
        value = signed_krawtchouk(image, degree)
        expected = KRAWTCHOUK_MULTIPLIERS[degree] * g_r
        if value != expected:
            raise AssertionError(f"K{degree} signed moment fails")
        krawtchouk_moments[f"K{degree}"] = str(value)
    shadow_cuts = payload.get(
        "shadow_cuts",
        {"lower_degrees": [], "upper_degrees": []},
    )
    shadow_values = {}
    for degree in sorted(
        set(shadow_cuts.get("lower_degrees", []))
        | set(shadow_cuts.get("upper_degrees", []))
    ):
        value = signed_krawtchouk(image, degree)
        bound = ARF_MAGNITUDE * comb(BASE.N, degree)
        if (
            degree in shadow_cuts.get("lower_degrees", [])
            and value < -bound
        ):
            raise AssertionError(f"K{degree} shadow lower bound fails")
        if (
            degree in shadow_cuts.get("upper_degrees", [])
            and value > bound
        ):
            raise AssertionError(f"K{degree} shadow upper bound fails")
        shadow_values[f"K{degree}"] = str(value)
    return {
        "classification": "EXACT_RATIONAL_FEASIBLE",
        "terminal_witness_replayed": True,
        "sign": sign,
        "include_k1": payload["include_k1"],
        "max_moment": max_moment,
        "G_R": str(g_r),
        "G_E": str(g_e),
        "G_E_equals_minus_G_R_over_32": True,
        "K1_signed_moment": str(k1),
        "signed_krawtchouk_moments": krawtchouk_moments,
        "shadow_cut_values": shadow_values,
        "ordinary": ordinary,
        "split_audits": audits,
        "scope_wall": (
            "Formal rational Wave132 projection only; not a binary code."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    results = {
        str(path): verify(path)
        for path in args.paths
    }
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
