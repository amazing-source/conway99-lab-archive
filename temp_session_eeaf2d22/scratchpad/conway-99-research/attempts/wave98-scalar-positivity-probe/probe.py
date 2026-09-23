"""Exact long-prefix probe for the sealed Wave 86 scalar modular control.

Exploratory only: a finite nonnegative prefix is not a theta-series
realization and a negative coefficient would refute only this formal control.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from fractions import Fraction
from pathlib import Path


Q = Fraction
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
WAVE86 = REPO / "attempts" / "wave86-level7-exact" / "exact_check.py"


def free_memory_percent() -> float:
    if os.name != "nt":
        return 100.0
    import ctypes

    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("memory_load", ctypes.c_ulong),
            ("total_phys", ctypes.c_ulonglong),
            ("avail_phys", ctypes.c_ulonglong),
            ("total_page", ctypes.c_ulonglong),
            ("avail_page", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("avail_virtual", ctypes.c_ulonglong),
            ("avail_extended", ctypes.c_ulonglong),
        ]

    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * status.avail_phys / status.total_phys


def load_wave86():
    spec = importlib.util.spec_from_file_location("wave86_probe_import", WAVE86)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load sealed Wave 86 checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def nonconstant_eisenstein(module, precision: int) -> dict[tuple[int, str], list[int]]:
    result: dict[tuple[int, str], list[int]] = {}
    for weight in range(3, 20, 2):
        for orientation in "AB":
            values = [0] * (precision + 1)
            if orientation == "A":
                for divisor in range(1, precision + 1):
                    character = module.chi7(divisor)
                    if not character:
                        continue
                    term = character * divisor ** (weight - 1)
                    for n in range(divisor, precision + 1, divisor):
                        values[n] += term
            else:
                for quotient in range(1, precision + 1):
                    character = module.chi7(quotient)
                    if not character:
                        continue
                    max_divisor = precision // quotient
                    for divisor in range(1, max_divisor + 1):
                        values[divisor * quotient] += (
                            character * divisor ** (weight - 1)
                        )
            result[(weight, orientation)] = values
    return result


def constants(module) -> dict[tuple[int, str], Q]:
    return {
        (weight, orientation): (
            -module.generalized_bernoulli(weight) / Q(2 * weight)
            if orientation == "A"
            else Q(0)
        )
        for weight in range(3, 20, 2)
        for orientation in "AB"
    }


def product_coefficients(
    form,
    precision: int,
    series: dict[tuple[int, str], list[int]],
    constant: dict[tuple[int, str], Q],
) -> list[Q]:
    a, oa, b, ob = form
    left = series[(a, oa)]
    right = series[(b, ob)]
    left_zero = constant[(a, oa)]
    right_zero = constant[(b, ob)]
    output = [left_zero * right_zero]
    for n in range(1, precision + 1):
        convolution = 0
        for j in range(1, n):
            convolution += left[j] * right[n - j]
        output.append(
            Q(convolution) + left_zero * right[n] + right_zero * left[n]
        )
    return output


def exact_probe(precision: int) -> dict:
    if free_memory_percent() < 20:
        raise RuntimeError("refusing to run below 20% free physical memory")
    module = load_wave86()
    basis, _ = module.fricke_matrix()
    coefficient_matrix = [
        [module.product_series(form)[n] for form in basis] for n in range(15)
    ]
    inverse = module.invert(coefficient_matrix)
    extremal_x = [
        Q(1),
        *([Q(0)] * 6),
        Q(5868),
        Q(0),
        Q(0),
        Q(28852082),
        Q(26264),
        Q(582557668),
        Q(2681235704),
        Q(12272379984),
    ]
    coordinates = [
        sum(inverse[i][j] * extremal_x[j] for j in range(15))
        for i in range(15)
    ]

    series = nonconstant_eisenstein(module, precision)
    constant = constants(module)
    forms = set(basis)
    forms.update(module.fricke_image(form)[1] for form in basis)
    products = {
        form: product_coefficients(form, precision, series, constant)
        for form in forms
    }
    x_values = [
        sum(coordinates[i] * products[basis[i]][n] for i in range(15))
        for n in range(precision + 1)
    ]
    y_values = []
    for n in range(precision + 1):
        transformed = sum(
            coordinates[i]
            * module.fricke_image(basis[i])[0]
            * products[module.fricke_image(basis[i])[1]][n]
            for i in range(15)
        )
        y_values.append(-Q(7**3) * transformed)

    expected_y = [
        1,
        0,
        0,
        0,
        0,
        358916,
        34393854,
        600737200,
        11946196274,
        132636715536,
        1237054839912,
        9122211909000,
        56682577580992,
        304577760235536,
        1443860798777424,
    ]
    prefix_matches = x_values[:15] == extremal_x and y_values[:15] == expected_y
    first_bad = {}
    for name, values in (("x", x_values), ("y", y_values)):
        for index, value in enumerate(values):
            if value.denominator != 1 or value < 0 or (index and value % 2):
                first_bad[name] = {
                    "index": index,
                    "value": str(value),
                    "nonintegral": value.denominator != 1,
                    "negative": value < 0,
                    "odd_nonconstant": bool(index and value.denominator == 1 and value % 2),
                }
                break

    return {
        "format": "wave98-scalar-positivity-probe-v1",
        "claim_label": "UNKNOWN",
        "precision": precision,
        "wave86_prefix_matches": prefix_matches,
        "first_bad": first_bad,
        "integral_even_nonnegative_through_prefix": prefix_matches and not first_bad,
        "last_coefficients": {
            "x": str(x_values[-1]),
            "y": str(y_values[-1]),
        },
        "limitations": [
            "A finite positive prefix is not an all-orders theorem.",
            "The formal scalar pair is not a lattice, marked frame, or graph.",
            "This probe imports discovery code and is not independent verification.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--precision", type=int, default=1000)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.precision < 50:
        raise SystemExit("precision must be at least 50")
    result = exact_probe(args.precision)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.verify:
        archived = json.loads(args.verify.read_text(encoding="utf-8"))
        if archived != result:
            raise SystemExit("archived result mismatch")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    print(payload, end="")


if __name__ == "__main__":
    main()
