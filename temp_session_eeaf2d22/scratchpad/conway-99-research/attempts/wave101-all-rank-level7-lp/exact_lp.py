#!/usr/bin/env python3
"""Exact all-rank level-7 scalar theta linear programs for Wave 101.

Discovery package only.  The modular-form and lattice inputs are frozen
verified dependencies, but the new LP certificates require an independent
verifier before any promotion beyond DERIVED.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from types import ModuleType


Q = Fraction
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = Path(__file__).with_name("exact-results.json")
SURVIVING_Q = tuple(range(2, 15, 2))
RANK = 44

FROZEN_INPUTS = {
    "verification/wave66-spherical-code-shift/package-manifest.sha256":
        "a6051ebcfccab0fc9b3f9698f0024cc3284549f5148c9a12a4c6bbe08c786486",
    "verification/wave71-modular-theta-extension/package-manifest.sha256":
        "0eede2ebc625534360dda3f8e62456e582f5184fd18d3820dd44748de95a5237",
    "attempts/wave86-level7-exact/package-manifest.sha256":
        "c6066fd10258578c15e511f3802217e4ff613ffe3d3b3b8f11e804f0316ac75d",
    "verification/wave86-level7-exact/package-manifest.sha256":
        "cbfafc03db11ad7f103e532e0f5e0b2e85ff6b568ad327b947a2d394a1d1dfa2",
}

# A dual support contains seven nonnegative coordinate forms, enough to
# reproduce the seven-variable objective exactly after eliminating x14.
TOTAL_SUPPORT = {
    2: ("x8", "x10", "x11", "x12", "x13", "x14", "y1"),
    4: ("x8", "x10", "x11", "x12", "x13", "x14", "y1"),
    6: ("x8", "x10", "x11", "x12", "x13", "x14", "y1"),
    8: ("x8", "x10", "x11", "x12", "x13", "x14", "y1"),
    10: ("x8", "x10", "x11", "x12", "x13", "x14", "y1"),
    12: ("x8", "x10", "x11", "x12", "x13", "y1", "y5"),
    14: ("x8", "x11", "x12", "y1", "y2", "y4", "y5"),
}

PREFIX_SUPPORT = {
    (2, 13): ("x7", "x8", "x10", "x11", "x12", "x13", "y1"),
    (4, 12): ("x8", "x9", "x10", "x11", "x12", "y1", "y2"),
    (4, 13): ("x7", "x8", "x10", "x11", "x12", "x13", "y1"),
    (6, 12): ("x8", "x9", "x10", "x11", "x12", "y1", "y2"),
    (6, 13): ("x7", "x8", "x10", "x11", "x12", "x13", "y1"),
    (8, 12): ("x8", "x9", "x10", "x11", "x12", "y1", "y2"),
    (8, 13): ("x7", "x8", "x10", "x11", "x12", "x13", "y1"),
    (10, 11): ("x8", "x9", "x10", "x11", "y1", "y2", "y3"),
    (10, 12): ("x8", "x9", "x10", "x11", "x12", "y1", "y2"),
    (10, 13): ("x8", "x10", "x11", "x12", "x13", "y1", "y4"),
    (12, 11): ("x8", "x9", "x10", "x11", "y1", "y2", "y3"),
    (12, 12): ("x9", "x10", "x11", "x12", "y1", "y2", "y5"),
    (12, 13): ("x8", "x10", "x11", "x12", "x13", "y1", "y4"),
    (14, 10): ("x8", "x9", "x10", "y1", "y2", "y3", "y4"),
    (14, 11): ("x7", "x10", "x11", "y1", "y2", "y3", "y5"),
    (14, 12): ("x8", "x11", "x12", "y1", "y2", "y4", "y5"),
    (14, 13): ("x8", "x10", "x12", "y1", "y2", "y4", "y5"),
}

LAST_ZERO_PREFIX = {
    2: 12,
    4: 11,
    6: 11,
    8: 11,
    10: 10,
    12: 10,
    14: 9,
}


def free_memory_percent() -> float:
    """Return free physical memory percentage, enforcing the host budget."""

    if os.name != "nt":
        return 100.0
    import ctypes

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MEMORYSTATUSEX()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * status.ullAvailPhys / status.ullTotalPhys


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check_frozen_inputs() -> None:
    for relative, expected in FROZEN_INPUTS.items():
        actual = sha256_file(ROOT / relative)
        if actual != expected:
            raise AssertionError(
                f"frozen input mismatch for {relative}: {actual} != {expected}"
            )


def load_module(name: str, relative: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    if spec is None or spec.loader is None:
        raise ImportError(relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fraction_text(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def decimal_text(value: Q, precision: int = 24) -> str:
    with localcontext() as context:
        context.prec = precision
        return format(Decimal(value.numerator) / Decimal(value.denominator), "f")


def solve_square(matrix: list[list[Q]], rhs: list[Q]) -> list[Q]:
    """Solve a square rational system by exact Gauss-Jordan elimination."""

    n = len(rhs)
    if len(matrix) != n or any(len(row) != n for row in matrix):
        raise ValueError("system is not square")
    work = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    for column in range(n):
        pivot = next(
            (row for row in range(column, n) if work[row][column]),
            None,
        )
        if pivot is None:
            raise ValueError("singular exact system")
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [entry / scale for entry in work[column]]
        for row in range(n):
            if row == column or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                entry - scale * pivot_entry
                for entry, pivot_entry in zip(work[row], work[column])
            ]
    return [work[row][-1] for row in range(n)]


def matmul(left: list[list[Q]], right: list[list[Q]]) -> list[list[Q]]:
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(len(right)))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def affine_pair(
    fricke: list[list[Q]], q_value: int
) -> tuple[list[Q], list[list[Q]], Q, list[Q]]:
    """Eliminate x14 from y0=1 for the requested discriminant length q."""

    exponent = 11 - q_value // 2
    scale = -Q(7**exponent)
    raw_constants = [scale * fricke[n][0] for n in range(15)]
    raw_rows = [
        [scale * fricke[n][j] for j in range(7, 15)]
        for n in range(15)
    ]
    pivot = raw_rows[0][7]
    if not pivot:
        raise AssertionError("x14 does not control y0")
    x14_constant = (Q(1) - raw_constants[0]) / pivot
    x14_linear = [-raw_rows[0][j] / pivot for j in range(7)]
    constants = [
        raw_constants[n] + raw_rows[n][7] * x14_constant
        for n in range(15)
    ]
    rows = [
        [
            raw_rows[n][j] + raw_rows[n][7] * x14_linear[j]
            for j in range(7)
        ]
        for n in range(15)
    ]
    assert constants[0] == 1 and not any(rows[0])
    return constants, rows, x14_constant, x14_linear


def nonnegative_forms(
    constants: list[Q],
    rows: list[list[Q]],
    x14_constant: Q,
    x14_linear: list[Q],
) -> dict[str, tuple[Q, list[Q]]]:
    forms = {
        f"x{7 + j}": (
            Q(0),
            [Q(int(k == j)) for k in range(7)],
        )
        for j in range(7)
    }
    forms["x14"] = (x14_constant, x14_linear)
    for n in range(1, 15):
        forms[f"y{n}"] = (constants[n], rows[n])
    return forms


def objective_affine(
    weights: dict[int, int],
    x14_constant: Q,
    x14_linear: list[Q],
) -> tuple[Q, list[Q]]:
    constant = Q(weights.get(14, 0)) * x14_constant
    linear = [
        Q(weights.get(7 + j, 0))
        + Q(weights.get(14, 0)) * x14_linear[j]
        for j in range(7)
    ]
    return constant, linear


def even_ceiling(value: Q) -> int:
    ceiling = -(-value.numerator // value.denominator)
    return ceiling if ceiling % 2 == 0 else ceiling + 1


def upper_bound_for(weights: dict[int, int]) -> dict[str, object]:
    """Return a rigorous elementary lattice upper bound for comparison.

    Through norm 26, reduction modulo 2K is injective up to sign.  Through
    norm 28, representatives in one nonzero mod-2 coset are either antipodal
    or mutually orthogonal norm-28 vectors, so there are at most 44 pairs.
    """

    end = max(index for index, weight in weights.items() if weight)
    max_weight = max(weights.values())
    if end <= 13:
        count_upper = 2 * (2**RANK - 1)
        argument = "mod-2 injection up to sign below twice the minimum"
    else:
        count_upper = 2 * RANK * (2**RANK - 1)
        argument = "at most 44 orthogonal antipodal pairs per nonzero mod-2 coset"
    return {
        "count_upper": count_upper,
        "weighted_objective_upper": max_weight * count_upper,
        "argument": argument,
    }


def mod7_objective_check(
    wave71: ModuleType,
    q_value: int,
    weights: dict[int, int],
) -> dict[str, object]:
    """Test whether Wave71's level-one affine family fixes this objective."""

    weight = wave71.elementary_divisor_weight(RANK - q_value)
    solved = wave71.theta_gap_system(weight, 6, 14)
    monomials = solved["monomials"]
    solution = solved["solution"]
    particular = solution["particular"]
    directions = solution["directions"]
    if particular is None:
        raise AssertionError("Wave71 gap system unexpectedly inconsistent")

    def evaluate(vector: list[int]) -> int:
        return sum(
            coefficient
            * wave71.evaluate_coefficient(monomials, vector, exponent)
            for exponent, coefficient in weights.items()
        ) % 7

    direction_residues = [evaluate(direction) for direction in directions]
    fixed = not any(direction_residues)
    return {
        "level_one_weight": weight,
        "particular_residue_mod_7": evaluate(particular),
        "direction_residues_mod_7": direction_residues,
        "fixed_residue": fixed,
        "conclusion": (
            "fixed modulo 7"
            if fixed
            else "no objective residue follows from the Wave71 affine family"
        ),
    }


def exact_certificate(
    q_value: int,
    name: str,
    weights: dict[int, int],
    support: tuple[str, ...],
    forms: dict[str, tuple[Q, list[Q]]],
    x14_constant: Q,
    x14_linear: list[Q],
    wave71: ModuleType,
) -> dict[str, object]:
    """Construct matching exact dual and primal LP certificates."""

    objective_constant, objective_linear = objective_affine(
        weights, x14_constant, x14_linear
    )

    # Exact dual: objective - bound = sum lambda_i * form_i.
    dual_matrix = [
        [forms[form_name][1][coordinate] for form_name in support]
        for coordinate in range(7)
    ]
    multipliers = solve_square(dual_matrix, objective_linear)
    if not all(value >= 0 for value in multipliers):
        raise AssertionError(f"negative dual multiplier for q={q_value}, {name}")

    # Exact primal optimizer: every form with positive dual multiplier is zero.
    primal_matrix = [forms[form_name][1] for form_name in support]
    primal_rhs = [-forms[form_name][0] for form_name in support]
    z = solve_square(primal_matrix, primal_rhs)
    form_values = {
        form_name: constant
        + sum(linear[j] * z[j] for j in range(7))
        for form_name, (constant, linear) in forms.items()
    }
    if not all(value >= 0 for value in form_values.values()):
        bad = {
            form_name: fraction_text(value)
            for form_name, value in form_values.items()
            if value < 0
        }
        raise AssertionError(f"infeasible exact primal for q={q_value}: {bad}")

    bound = objective_constant - sum(
        multiplier * forms[form_name][0]
        for multiplier, form_name in zip(multipliers, support)
    )
    primal_value = objective_constant + sum(
        objective_linear[j] * z[j] for j in range(7)
    )
    if bound != primal_value:
        raise AssertionError("primal and dual values differ")

    upper = upper_bound_for(weights)
    rounded = even_ceiling(bound)
    comparison_upper = int(upper["weighted_objective_upper"])
    congruence = mod7_objective_check(wave71, q_value, weights)
    if congruence["fixed_residue"]:
        raise AssertionError(
            f"unexpected fixed mod-7 objective for q={q_value}, {name}"
        )

    x_values = {f"x{7 + j}": z[j] for j in range(7)}
    x_values["x14"] = form_values["x14"]
    y_values = {f"y{n}": form_values[f"y{n}"] for n in range(1, 15)}
    return {
        "name": name,
        "objective": " + ".join(
            (
                f"{coefficient}*x{index}"
                if coefficient != 1
                else f"x{index}"
            )
            for index, coefficient in sorted(weights.items())
            if coefficient
        ),
        "weights_x7_to_x14": [weights.get(index, 0) for index in range(7, 15)],
        "rational_lp_optimum": fraction_text(bound),
        "decimal_lp_optimum": decimal_text(bound),
        "even_integer_lower_bound": rounded,
        "parity_reason": "each nonzero theta coefficient counts vectors in pairs v,-v",
        "dual_identity": {
            "left": f"{name} - {fraction_text(bound)}",
            "nonnegative_terms": {
                form_name: fraction_text(multiplier)
                for form_name, multiplier in zip(support, multipliers)
            },
            "all_multipliers_nonnegative": True,
        },
        "exact_primal_optimizer": {
            "formal_scalar_pair_only": True,
            "x7_to_x14": {
                name: fraction_text(value) for name, value in x_values.items()
            },
            "y1_to_y14": {
                name: fraction_text(value) for name, value in y_values.items()
            },
            "all_required_coefficients_nonnegative": True,
            "active_zero_forms": [
                form_name for form_name, value in form_values.items() if value == 0
            ],
        },
        "wave71_mod7_check": congruence,
        "rigorous_upper_comparison": {
            **upper,
            "lower_bound_exceeds_upper": rounded > comparison_upper,
            "contradiction": False,
        },
    }


def zero_prefix_control(
    q_value: int,
    end: int,
    forms: dict[str, tuple[Q, list[Q]]],
) -> dict[str, object]:
    """Exhibit an exact feasible scalar point with x7=...=x_end=0."""

    x_zero_forms = [f"x{index}" for index in range(7, end + 1)]
    y_zero_count = 7 - len(x_zero_forms)
    active = tuple(x_zero_forms + [f"y{n}" for n in range(1, y_zero_count + 1)])
    matrix = [forms[name][1] for name in active]
    rhs = [-forms[name][0] for name in active]
    z = solve_square(matrix, rhs)
    values = {
        name: constant + sum(linear[j] * z[j] for j in range(7))
        for name, (constant, linear) in forms.items()
    }
    if not all(value >= 0 for value in values.values()):
        raise AssertionError(f"zero-prefix control infeasible for q={q_value}")
    if any(values[f"x{index}"] for index in range(7, end + 1)):
        raise AssertionError("zero-prefix objective is not zero")
    scalar_values = [values[f"x{index}"] for index in range(7, 15)]
    scalar_values += [values[f"y{index}"] for index in range(1, 15)]
    if not all(value.denominator == 1 for value in scalar_values):
        raise AssertionError("zero-prefix control unexpectedly nonintegral")
    if not all(value.numerator % 2 == 0 for value in scalar_values):
        raise AssertionError("zero-prefix control unexpectedly violates parity")
    return {
        "last_prefix_with_exact_zero_lp_optimum": f"x7+...+x{end}",
        "conclusion": (
            "scalar level-7 positivity alone cannot force a vector "
            f"of squared norm at most {2 * end}"
        ),
        "formal_scalar_control_not_a_lattice": True,
        "x7_to_x14": {
            f"x{index}": fraction_text(values[f"x{index}"])
            for index in range(7, 15)
        },
        "y1_to_y14": {
            f"y{index}": fraction_text(values[f"y{index}"])
            for index in range(1, 15)
        },
        "integral_even_nonnegative_first_15_coefficients": True,
    }


def weights_prefix(end: int) -> dict[int, int]:
    return {index: 1 for index in range(7, end + 1)}


def weights_total() -> dict[int, int]:
    return weights_prefix(14)


def weights_triangular() -> dict[int, int]:
    return {index: 15 - index for index in range(7, 15)}


def build_results() -> dict[str, object]:
    check_frozen_inputs()
    wave86 = load_module(
        "wave86_level7_exact",
        "attempts/wave86-level7-exact/exact_check.py",
    )
    wave71 = load_module(
        "wave71_modular_theta",
        "attempts/wave71-modular-theta-extension/exact_check.py",
    )
    basis, fricke = wave86.fricke_matrix()
    if len(basis) != 15:
        raise AssertionError("incomplete M_22(Gamma0(7)) basis")
    square = matmul(fricke, fricke)
    if not all(
        square[i][j] == Q(i == j)
        for i in range(15)
        for j in range(15)
    ):
        raise AssertionError("Fricke matrix is not an exact involution")

    rows = []
    for q_value in SURVIVING_Q:
        constants, affine, x14_constant, x14_linear = affine_pair(
            fricke, q_value
        )
        forms = nonnegative_forms(
            constants, affine, x14_constant, x14_linear
        )
        certificates = [
            exact_certificate(
                q_value,
                "total_through_norm_28",
                weights_total(),
                TOTAL_SUPPORT[q_value],
                forms,
                x14_constant,
                x14_linear,
                wave71,
            )
        ]
        for (prefix_q, end), support in PREFIX_SUPPORT.items():
            if prefix_q != q_value:
                continue
            certificates.append(
                exact_certificate(
                    q_value,
                    f"prefix_through_norm_{2 * end}",
                    weights_prefix(end),
                    support,
                    forms,
                    x14_constant,
                    x14_linear,
                    wave71,
                )
            )
        certificates.append(
            exact_certificate(
                q_value,
                "triangular_low_shell_weight",
                weights_triangular(),
                TOTAL_SUPPORT[q_value],
                forms,
                x14_constant,
                x14_linear,
                wave71,
            )
        )
        rows.append(
            {
                "q_discriminant_length_L": q_value,
                "r_rank_F7_Seidel": RANK - q_value,
                "poisson_relation": (
                    "Theta_L=-7^"
                    f"{11 - q_value // 2}*(Theta_K|W_7)"
                ),
                "x_initial_gap": "x1=...=x6=0",
                "x14_elimination": {
                    "constant": fraction_text(x14_constant),
                    "coefficients_on_x7_to_x13": [
                        fraction_text(value) for value in x14_linear
                    ],
                },
                "certificates": certificates,
                "zero_prefix_null_control": zero_prefix_control(
                    q_value,
                    LAST_ZERO_PREFIX[q_value],
                    forms,
                ),
            }
        )

    total_bounds = {
        str(row["q_discriminant_length_L"]): row["certificates"][0][
            "even_integer_lower_bound"
        ]
        for row in rows
    }
    return {
        "format": "wave101-all-rank-level7-lp-v1",
        "claim_label": "DERIVED",
        "scope": (
            "conditional q=2,4,...,14 scalar theta consequences for a "
            "hypothetical srg(99,14,1,2)"
        ),
        "frozen_inputs": FROZEN_INPUTS,
        "modular_space": {
            "space": "complete M_22(Gamma0(7)) with trivial character",
            "dimension": 15,
            "sturm_bound": 14,
            "basis_products": [list(form) for form in basis],
            "fricke_involution_exact": True,
        },
        "theta_normalization": "Theta=sum_v q^((v,v)/2)",
        "total_even_lower_bounds_by_q": total_bounds,
        "rows": rows,
        "global_assessment": {
            "any_rigorous_upper_bound_contradiction": False,
            "short_signed_unit_range": (
                "only x7,x8,x9 (norms 14,16,18) have the verified "
                "signed-unit graph dictionary"
            ),
            "scalar_short_range_outcome": (
                "for every q=2,...,14 the exact scalar LP allows "
                "x7=x8=x9=0"
            ),
            "mod7_outcome": (
                "none of the reported objectives has a fixed residue in "
                "the Wave71 level-one affine family; parity is the only "
                "unconditional rounding used"
            ),
            "conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "Discovery only; the new certificates have not been independently verified.",
            "Every result is conditional on the verified Wave66/71 lattice transfer.",
            "A rational formal scalar theta pair is not a lattice, marked frame, or graph.",
            "Only coefficients through the Sturm bound enter the LP.",
            "No signed-unit eigenvector interpretation is used beyond norm 18.",
            "No surviving q row is excluded, so Conway-99 remains UNKNOWN.",
        ],
    }


def canonical_bytes(payload: dict[str, object]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    free = free_memory_percent()
    if free < 15.0:
        raise SystemExit(
            f"refusing to run with only {free:.1f}% free physical memory"
        )
    encoded = canonical_bytes(build_results())
    if args.verify:
        if not args.output.exists() or args.output.read_bytes() != encoded:
            raise SystemExit("canonical exact-results.json mismatch")
        print(
            "PASS: Wave101 canonical result matches exact recomputation; "
            f"free physical memory {free:.1f}%"
        )
        return 0
    args.output.write_bytes(encoded)
    print(f"wrote {args.output}; free physical memory {free:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
