#!/usr/bin/env python3
"""Clean-room, no-cache verification of the Wave 130 cutoff-28 primal.

The verifier imports no discovery module and reads no serialized Fourier
column cache.  It reconstructs the 239 Jacobi columns from the defining
theta/Eisenstein series, rebuilds every original row, and substitutes the
stored rational primal with fractions.Fraction arithmetic.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import math
import os
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


Q = Fraction
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DISCOVERY = ROOT / "attempts" / "wave130-cdd-exact-lp"
CANDIDATE = DISCOVERY / "result-cutoff28-warm.json"
DISCOVERY_MANIFEST = DISCOVERY / "MANIFEST.sha256"
EXPECTED_MANIFEST_SHA256 = (
    "8b1da27e3acaa059934704a85aaa380e101e1db330925ced6e048330d318e3ae"
)

LEVEL = 7
WEIGHT = 22
INDEX_L = 10
INDEX_K = 70
CUTOFF = 28
CHARACTER = (0, 1, 1, -1, 1, -1, -1)
EXPECTED_DIMENSIONS = (15, 17, 17, 19, 21, 21, 23, 25, 25, 27, 29)
EXPECTED_COUNTS = (454, 1686, 506)

LaurentSeries = dict[tuple[int, int], Q]
GroupProduct = tuple[tuple[int, str], tuple[int, str]]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def json_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def free_memory_percent() -> float:
    if os.name != "nt":
        return 100.0

    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("load", ctypes.c_ulong),
            ("total_phys", ctypes.c_ulonglong),
            ("available_phys", ctypes.c_ulonglong),
            ("total_page", ctypes.c_ulonglong),
            ("available_page", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("available_virtual", ctypes.c_ulonglong),
            ("available_extended", ctypes.c_ulonglong),
        ]

    state = MemoryStatus()
    state.length = ctypes.sizeof(state)
    require(
        bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state))),
        "GlobalMemoryStatusEx failed",
    )
    return 100.0 * state.available_phys / state.total_phys


def verify_manifest() -> dict[str, object]:
    require(EXPECTED_MANIFEST_SHA256 != "PENDING", "manifest hash is not frozen")
    require(
        file_hash(DISCOVERY_MANIFEST) == EXPECTED_MANIFEST_SHA256,
        "Wave130 manifest hash drift",
    )
    entries = 0
    for line in DISCOVERY_MANIFEST.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        target = DISCOVERY / relative
        require(target.is_file(), f"manifest target missing: {relative}")
        require(file_hash(target) == expected, f"manifest target drift: {relative}")
        entries += 1
    return {
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "entries_checked": entries,
    }


def cleaned(series: LaurentSeries) -> LaurentSeries:
    return {key: value for key, value in series.items() if value}


def laurent_product(
    left: LaurentSeries, right: LaurentSeries, q_limit: int
) -> LaurentSeries:
    output: defaultdict[tuple[int, int], Q] = defaultdict(Q)
    for (n_left, r_left), a in left.items():
        for (n_right, r_right), b in right.items():
            if n_left + n_right <= q_limit:
                output[n_left + n_right, r_left + r_right] += a * b
    return cleaned(dict(output))


def phi_minus_two(q_limit: int) -> LaurentSeries:
    """Product expansion of phi_{-2,1}."""

    result: LaurentSeries = {(0, -1): Q(1), (0, 0): Q(-2), (0, 1): Q(1)}
    for degree in range(1, q_limit + 1):
        eta_inverse_fourth = {
            (multiple * degree, 0): Q(math.comb(multiple + 3, 3))
            for multiple in range(q_limit // degree + 1)
        }
        positive_y = {
            (0, 0): Q(1),
            (degree, 1): Q(-2),
            (2 * degree, 2): Q(1),
        }
        negative_y = {
            (0, 0): Q(1),
            (degree, -1): Q(-2),
            (2 * degree, -2): Q(1),
        }
        for factor in (eta_inverse_fourth, positive_y, negative_y):
            result = laurent_product(result, factor, q_limit)
    return result


def theta_square(kind: str, q8_limit: int) -> dict[tuple[int, int], Q]:
    theta: defaultdict[tuple[int, int], Q] = defaultdict(Q)
    radius = math.isqrt(q8_limit + 8) + 3
    for integer in range(-radius, radius + 1):
        if kind == "theta2":
            q8 = (2 * integer + 1) ** 2
            y2 = 2 * integer + 1
            coefficient = 1
        elif kind == "theta3":
            q8 = 4 * integer * integer
            y2 = 2 * integer
            coefficient = 1
        elif kind == "theta4":
            q8 = 4 * integer * integer
            y2 = 2 * integer
            coefficient = -1 if integer % 2 else 1
        else:
            raise ValueError(kind)
        if q8 <= q8_limit + 8:
            theta[q8, y2] += Q(coefficient)
    output: defaultdict[tuple[int, int], Q] = defaultdict(Q)
    for (q_left, y_left), a in theta.items():
        for (q_right, y_right), b in theta.items():
            if q_left + q_right <= q8_limit:
                output[q_left + q_right, y_left + y_right] += a * b
    return cleaned(dict(output))


def theta_ratio(kind: str, q_limit: int) -> dict[tuple[int, int], Q]:
    q8_limit = 8 * q_limit + 2
    numerator = theta_square(kind, q8_limit)
    denominator: defaultdict[int, Q] = defaultdict(Q)
    for (q8, _y2), coefficient in numerator.items():
        denominator[q8] += coefficient
    shift = min(q8 for q8, coefficient in denominator.items() if coefficient)
    numerator = {(q8 - shift, y2): c for (q8, y2), c in numerator.items()}
    denominator = defaultdict(
        Q, {q8 - shift: c for q8, c in denominator.items()}
    )
    leading = denominator[0]
    reciprocal = {0: Q(1) / leading}
    for degree in range(1, 8 * q_limit + 1):
        reciprocal[degree] = -sum(
            denominator[j] * reciprocal.get(degree - j, Q(0))
            for j in range(1, degree + 1)
        ) / leading
    result: defaultdict[tuple[int, int], Q] = defaultdict(Q)
    for (q8, y2), coefficient in numerator.items():
        for extra, inverse_coefficient in reciprocal.items():
            if q8 + extra <= 8 * q_limit:
                result[q8 + extra, y2] += coefficient * inverse_coefficient
    return cleaned(dict(result))


def phi_zero(q_limit: int) -> LaurentSeries:
    accumulated: defaultdict[tuple[int, int], Q] = defaultdict(Q)
    for kind in ("theta2", "theta3", "theta4"):
        for key, value in theta_ratio(kind, q_limit).items():
            accumulated[key] += 4 * value
    result: defaultdict[tuple[int, int], Q] = defaultdict(Q)
    for (q8, y2), value in accumulated.items():
        if value:
            require(q8 % 8 == 0 and y2 % 2 == 0, "fractional Jacobi exponent")
            result[q8 // 8, y2 // 2] += value
    return cleaned(dict(result))


def bernoulli_table(limit: int) -> list[Q]:
    table = [Q(0)] * (limit + 1)
    table[0] = Q(1)
    for degree in range(1, limit + 1):
        table[degree] = -sum(
            Q(math.comb(degree + 1, lower)) * table[lower]
            for lower in range(degree)
        ) / Q(degree + 1)
    return table


BERNOULLI = bernoulli_table(42)


def chi(value: int) -> int:
    return CHARACTER[value % LEVEL]


def generalized_bernoulli(degree: int) -> Q:
    def polynomial(x: Q) -> Q:
        return sum(
            Q(math.comb(degree, lower))
            * BERNOULLI[lower]
            * x ** (degree - lower)
            for lower in range(degree + 1)
        )

    return Q(LEVEL ** (degree - 1)) * sum(
        Q(chi(residue)) * polynomial(Q(residue, LEVEL))
        for residue in range(1, LEVEL + 1)
    )


def odd_eisenstein(weight: int, cusp: str, q_limit: int) -> list[Q]:
    coefficients = [Q(0)] * (q_limit + 1)
    if cusp == "C":
        coefficients[0] = -generalized_bernoulli(weight) / Q(2 * weight)
    else:
        require(cusp == "T", "bad Eisenstein cusp")
    for divisor in range(1, q_limit + 1):
        power = divisor ** (weight - 1)
        for degree in range(divisor, q_limit + 1, divisor):
            if cusp == "C":
                coefficients[degree] += Q(chi(divisor)) * power
            else:
                coefficients[degree] += Q(chi(degree // divisor)) * power
    return coefficients


def q_product(left: Sequence[Q], right: Sequence[Q], q_limit: int) -> list[Q]:
    return [
        sum(left[lower] * right[degree - lower] for lower in range(degree + 1))
        for degree in range(q_limit + 1)
    ]


def rref(matrix: Sequence[Sequence[Q]]) -> tuple[list[list[Q]], list[int]]:
    work = [list(row) for row in matrix]
    if not work:
        return work, []
    pivot_columns: list[int] = []
    pivot_row = 0
    for column in range(len(work[0])):
        pivot = next(
            (row for row in range(pivot_row, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        divisor = work[pivot_row][column]
        work[pivot_row] = [value / divisor for value in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row or not work[row][column]:
                continue
            multiplier = work[row][column]
            work[row] = [
                value - multiplier * pivot_value
                for value, pivot_value in zip(work[row], work[pivot_row], strict=True)
            ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == len(work):
            break
    return work, pivot_columns


def matrix_rank(matrix: Sequence[Sequence[Q]]) -> int:
    return len(rref(matrix)[1])


def matrix_inverse(matrix: Sequence[Sequence[Q]]) -> list[list[Q]]:
    size = len(matrix)
    augmented = [
        list(row) + [Q(int(row_index == column)) for column in range(size)]
        for row_index, row in enumerate(matrix)
    ]
    reduced, pivots = rref(augmented)
    require(pivots[:size] == list(range(size)), "singular normalization matrix")
    return [row[size:] for row in reduced]


def null_basis(matrix: Sequence[Sequence[Q]]) -> list[list[Q]]:
    reduced, pivots = rref(matrix)
    width = len(matrix[0]) if matrix else 0
    free = [column for column in range(width) if column not in pivots]
    basis = []
    for free_column in free:
        vector = [Q(0)] * width
        vector[free_column] = Q(1)
        for row, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row][free_column]
        basis.append(vector)
    return basis


def choose_modular_block(weight: int, q_limit: int) -> list[dict[str, object]]:
    """Construct the exact Fricke-eigen Fourier-echelon basis for one c-block."""

    sturm = 2 * weight // 3
    work_limit = max(sturm, q_limit)
    eisenstein = {
        (odd, cusp): odd_eisenstein(odd, cusp, work_limit)
        for odd in range(3, weight - 1, 2)
        for cusp in ("C", "T")
    }
    candidates: list[GroupProduct] = []
    for left_weight in range(3, weight - 2, 2):
        right_weight = weight - left_weight
        if right_weight >= 3 and right_weight % 2:
            for left_cusp in ("C", "T"):
                for right_cusp in ("C", "T"):
                    candidates.append(
                        (
                            (left_weight, left_cusp),
                            (right_weight, right_cusp),
                        )
                    )
    candidates.sort(key=repr, reverse=True)
    expansions = {
        product: q_product(
            eisenstein[product[0]], eisenstein[product[1]], work_limit
        )
        for product in candidates
    }

    target_dimension = 1 + 2 * (weight // 3)
    selected: list[GroupProduct] = []
    current_rank = 0
    for candidate in candidates:
        trial = selected + [candidate]
        trial_rank = matrix_rank(
            [[expansions[product][n] for product in trial] for n in range(sturm + 1)]
        )
        if trial_rank > current_rank:
            selected.append(candidate)
            current_rank = trial_rank
        if current_rank == target_dimension:
            break
    require(current_rank == target_dimension, f"modular rank failed at {weight}")

    ordinary = [expansions[product] for product in selected]
    fricke = []
    for product in selected:
        mapped = []
        factor = Q(-1)
        for factor_weight, cusp in product:
            exponent = (
                (factor_weight - 1) // 2
                if cusp == "C"
                else (1 - factor_weight) // 2
            )
            factor *= Q(LEVEL) ** exponent
            mapped.append((factor_weight, "T" if cusp == "C" else "C"))
        fricke.append(
            [factor * value for value in expansions[(mapped[0], mapped[1])]]
        )

    coefficient_rows = [
        [ordinary[column][degree] for column in range(target_dimension)]
        for degree in range(sturm + 1)
    ]
    pivots: list[int] = []
    current_rank = 0
    for degree, row in enumerate(coefficient_rows):
        trial_rank = matrix_rank([coefficient_rows[index] for index in pivots] + [row])
        if trial_rank > current_rank:
            pivots.append(degree)
            current_rank = trial_rank
        if current_rank == target_dimension:
            break
    transform = matrix_inverse([coefficient_rows[degree] for degree in pivots])
    echelon = [
        [
            sum(
                ordinary[source][degree] * transform[source][column]
                for source in range(target_dimension)
            )
            for degree in range(work_limit + 1)
        ]
        for column in range(target_dimension)
    ]
    echelon_fricke = [
        [
            sum(
                fricke[source][degree] * transform[source][column]
                for source in range(target_dimension)
            )
            for degree in range(work_limit + 1)
        ]
        for column in range(target_dimension)
    ]
    fricke_matrix = [
        [echelon_fricke[column][degree] for column in range(target_dimension)]
        for degree in pivots
    ]
    square = [
        [
            sum(
                fricke_matrix[row][middle] * fricke_matrix[middle][column]
                for middle in range(target_dimension)
            )
            for column in range(target_dimension)
        ]
        for row in range(target_dimension)
    ]
    require(
        square
        == [
            [Q(int(row == column)) for column in range(target_dimension)]
            for row in range(target_dimension)
        ],
        f"Fricke involution failed at {weight}",
    )

    result: list[dict[str, object]] = []
    for eigenvalue in (1, -1):
        eigenspace = null_basis(
            [
                [
                    fricke_matrix[row][column]
                    - Q(eigenvalue * int(row == column))
                    for column in range(target_dimension)
                ]
                for row in range(target_dimension)
            ]
        )
        raw = [
            [
                sum(
                    echelon[column][degree] * vector[column]
                    for column in range(target_dimension)
                )
                for degree in range(work_limit + 1)
            ]
            for vector in eigenspace
        ]
        eigen_pivots: list[int] = []
        current_rank = 0
        for degree in range(sturm + 1):
            row = [series[degree] for series in raw]
            trial_rank = matrix_rank(
                [[series[pivot] for series in raw] for pivot in eigen_pivots] + [row]
            )
            if trial_rank > current_rank:
                eigen_pivots.append(degree)
                current_rank = trial_rank
            if current_rank == len(eigenspace):
                break
        eigen_transform = matrix_inverse(
            [[series[degree] for series in raw] for degree in eigen_pivots]
        )
        for column in range(len(eigenspace)):
            series = [
                sum(
                    raw[source][degree] * eigen_transform[source][column]
                    for source in range(len(eigenspace))
                )
                for degree in range(work_limit + 1)
            ]
            result.append(
                {
                    "pivot_q": eigen_pivots[column],
                    "fricke_eigenvalue": eigenvalue,
                    "series": series,
                }
            )
    require(len(result) == target_dimension, f"eigenspace dimension at {weight}")
    return result


def modular_times_jacobi(
    modular: Sequence[Q], jacobi: LaurentSeries, q_limit: int
) -> LaurentSeries:
    output: defaultdict[tuple[int, int], Q] = defaultdict(Q)
    for modular_degree, modular_coefficient in enumerate(modular):
        if not modular_coefficient:
            continue
        for (jacobi_degree, radius), jacobi_coefficient in jacobi.items():
            if modular_degree + jacobi_degree <= q_limit:
                output[modular_degree + jacobi_degree, radius] += (
                    modular_coefficient * jacobi_coefficient
                )
    return cleaned(dict(output))


def reconstruct_columns(q_limit: int) -> tuple[list[dict[str, object]], dict[str, object]]:
    require(free_memory_percent() >= 15.0, "memory floor before reconstruction")
    generator_a = phi_minus_two(q_limit)
    generator_b = phi_zero(q_limit)
    require(
        [generator_a.get((0, r), Q(0)) for r in (-1, 0, 1)] == [1, -2, 1],
        "phi_-2 normalization",
    )
    require(
        [generator_b.get((0, r), Q(0)) for r in (-1, 0, 1)] == [1, 10, 1],
        "phi_0 normalization",
    )

    powers_a = [{(0, 0): Q(1)}]
    powers_b = [{(0, 0): Q(1)}]
    for _ in range(INDEX_L):
        powers_a.append(laurent_product(powers_a[-1], generator_a, q_limit))
        powers_b.append(laurent_product(powers_b[-1], generator_b, q_limit))
    jacobi_blocks = [
        laurent_product(powers_a[c], powers_b[INDEX_L - c], q_limit)
        for c in range(INDEX_L + 1)
    ]
    scaled_blocks = [
        {
            (LEVEL * n, LEVEL * r): value
            for (n, r), value in block.items()
            if LEVEL * n <= q_limit
        }
        for block in jacobi_blocks
    ]

    columns: list[dict[str, object]] = []
    dimensions = []
    for c in range(INDEX_L + 1):
        weight = WEIGHT + 2 * c
        basis = choose_modular_block(weight, q_limit)
        dimensions.append(len(basis))
        cusp_scale = -Q(1, LEVEL ** (3 + c))
        for basis_index, row in enumerate(basis):
            ordinary = row["series"]
            eigenvalue = row["fricke_eigenvalue"]
            columns.append(
                {
                    "c": c,
                    "weight": weight,
                    "basis_index": basis_index,
                    "pivot_q": row["pivot_q"],
                    "fricke_eigenvalue": eigenvalue,
                    "L": modular_times_jacobi(ordinary, jacobi_blocks[c], q_limit),
                    "K": modular_times_jacobi(
                        [cusp_scale * eigenvalue * value for value in ordinary],
                        scaled_blocks[c],
                        q_limit,
                    ),
                }
            )
        require(free_memory_percent() >= 15.0, "memory floor during reconstruction")
    require(tuple(dimensions) == EXPECTED_DIMENSIONS, "module dimensions")
    require(len(columns) == 239, "column count")
    return columns, {
        "dimensions_by_c": dimensions,
        "total_dimension": len(columns),
        "A_q0": [str(generator_a.get((0, r), Q(0))) for r in (-1, 0, 1)],
        "B_q0": [str(generator_b.get((0, r), Q(0))) for r in (-1, 0, 1)],
    }


def serialized_column_digest(columns: Sequence[dict[str, object]]) -> str:
    normalized = []
    for column in columns:
        normalized.append(
            {
                key: column[key]
                for key in (
                    "c",
                    "weight",
                    "basis_index",
                    "pivot_q",
                    "fricke_eigenvalue",
                )
            }
            | {
                side: [
                    [n, r, str(value)]
                    for (n, r), value in sorted(column[side].items())
                ]
                for side in ("L", "K")
            }
        )
    return json_hash(normalized)


def linear_coefficient(
    columns: Sequence[dict[str, object]],
    solution: Sequence[Q],
    side: str,
    key: tuple[int, int],
) -> Q:
    return sum(
        solution[index] * column[side].get(key, Q(0))
        for index, column in enumerate(columns)
    )


def verify_primal(columns: Sequence[dict[str, object]]) -> dict[str, object]:
    payload = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    require(payload.get("classification") == "EXACT_RATIONAL_FEASIBLE", "status")
    require(payload.get("cutoff") == CUTOFF, "candidate cutoff")
    require(payload.get("failed_equalities") == [], "stored failed equality")
    require(payload.get("failed_inequalities") == [], "stored failed inequality")
    solution = [Q(value) for value in payload.get("solution", [])]
    require(len(solution) == len(columns) == 239, "solution length")

    equality_count = 0
    inequality_count = 0
    failed_equalities: list[str] = []
    failed_inequalities: list[str] = []
    tight: list[str] = []
    for side, index in (("L", INDEX_L), ("K", INDEX_K)):
        equality_count += 1
        if linear_coefficient(columns, solution, side, (0, 0)) != 2079:
            failed_equalities.append(f"{side}:constant")
        keys = sorted(
            {
                key
                for column in columns
                for key in column[side]
                if key[0] <= CUTOFF
            }
        )
        for n, r in keys:
            outside = r * r > 4 * index * n
            graph_zero = side == "K" and (
                1 <= n <= 6 or (7 <= n <= 10 and abs(r) > 28)
            )
            value = linear_coefficient(columns, solution, side, (n, r))
            if outside or graph_zero:
                equality_count += 1
                if value:
                    suffix = "hol" if outside else "graph"
                    failed_equalities.append(f"{side}:zero:n{n}:r{r}:{suffix}")
            else:
                inequality_count += 1
                label = f"{side}:positive:n{n}:r{r}"
                if value < 0:
                    failed_inequalities.append(label)
                elif value == 0:
                    tight.append(label)

        moment_index = INDEX_L if side == "L" else INDEX_K
        for n in range(1, CUTOFF + 1):
            radii = sorted(
                {
                    r
                    for column in columns
                    for nn, r in column[side]
                    if nn == n
                }
            )
            if not radii:
                continue
            moment_row = [
                sum(
                    (11 * r * r - moment_index * n)
                    * column[side].get((n, r), Q(0))
                    for r in radii
                )
                for column in columns
            ]
            if not any(moment_row):
                continue
            equality_count += 1
            value = sum(
                moment_row[index] * solution[index]
                for index in range(len(columns))
            )
            if value:
                failed_equalities.append(f"{side}:moment:n{n}")

    require(
        (equality_count, inequality_count, len(tight)) == EXPECTED_COUNTS,
        "row or tight count mismatch",
    )
    require(tight == payload.get("tight_inequalities"), "tight label mismatch")
    require(not failed_equalities, "candidate fails an original equality")
    require(not failed_inequalities, "candidate fails an original inequality")
    return {
        "classification": "VERIFIED_EXACT_RATIONAL_FEASIBLE",
        "cutoff": CUTOFF,
        "variables": len(solution),
        "equalities_checked": equality_count,
        "inequalities_checked": inequality_count,
        "tight_inequalities": len(tight),
        "failed_equalities": failed_equalities,
        "failed_inequalities": failed_inequalities,
        "candidate_sha256": file_hash(CANDIDATE),
        "solution_sha256": json_hash([str(value) for value in solution]),
    }


def build_result(*, check_seal: bool = True) -> dict[str, object]:
    initial_memory = free_memory_percent()
    require(initial_memory >= 15.0, "memory floor before verifier")
    preinspection = verify_manifest() if check_seal else {
        "manifest_sha256": "DEVELOPMENT_UNSEALED",
        "entries_checked": 0,
    }
    columns, module = reconstruct_columns(CUTOFF)
    primal = verify_primal(columns)
    require(free_memory_percent() >= 15.0, "memory floor after verifier")
    return {
        "format": "wave130-independent-no-cache-verification-v1",
        "claim_label": (
            "VERIFIED" if check_seal else "DEVELOPMENT_PRECHECK"
        ),
        "scope": (
            "Exact rational feasibility of the cutoff-28 level-7 "
            "index-10/index-70 Jacobi necessary-condition relaxation only."
        ),
        "preinspection": preinspection,
        "implementation_separation": {
            "discovery_module_imported": False,
            "discovery_verifier_imported": False,
            "serialized_column_cache_read": False,
            "candidate_generator_reused": False,
            "column_source": (
                "independent theta/Eisenstein/Fricke reconstruction"
            ),
        },
        "module": module,
        "reconstructed_columns": {
            "count": len(columns),
            "sha256": serialized_column_digest(columns),
        },
        "cutoff_28": primal,
        "status_wall": {
            "finite_relaxation": "VERIFIED_EXACT_RATIONAL_FEASIBLE",
            "rank28_realized": False,
            "rank28_excluded": False,
            "graph_constructed": False,
            "lattice_constructed": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "memory": {
            "floor_percent": 15,
            "initial_floor_check_passed": initial_memory >= 15.0,
            "floor_respected": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--development-unsealed", action="store_true")
    args = parser.parse_args()
    result = build_result(check_seal=not args.development_unsealed)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        require(result == expected, "stored independent result differs")
        print(f"verified {args.verify}")
    elif args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"wrote {args.output}")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
