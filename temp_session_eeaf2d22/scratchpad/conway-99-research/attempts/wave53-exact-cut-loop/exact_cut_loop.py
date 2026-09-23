#!/usr/bin/env python3
"""Bounded exact rational cutting-plane loop for the endpoint count relaxation.

Floating point is used only to choose an LP active set and propose a direction.
Every retained witness, matrix quadratic, rank-one cut, and substitution is
checked with fractions or integers before it enters the output.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import importlib.util
import itertools
import json
import math
import os
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
from scipy.optimize import linprog


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "exact-result.json"
MAX_CUT_ITERATIONS = 3
MIN_FREE_PERCENT = 20.0
ACTIVE_TOLERANCES = (1e-8, 1e-9, 1e-10, 1e-11)
N = 99
SEVEN_TOTAL = math.comb(N, 7)
Y_SCALE = 4158

W43 = ROOT / "attempts/wave43-seven-deck-endpoint/exact-results.json"
W44 = ROOT / "attempts/wave44-rooted-flags/row-system.json"
W45_CUTS = (
    ROOT
    / "attempts/wave45-flag-moment/"
    "checkpoint-v1-seed0-17cuts-15witnesses.json"
)
W45_VERIFIED_COEFFICIENTS = (
    ROOT / "verification/wave45-flag-moment/independent-results.json"
)
W47_CUTS = ROOT / "attempts/wave47-three-root-moment/cuts.json"
W47_COEFFICIENTS = ROOT / "attempts/wave47-three-root-moment/coefficients.json"
W47_VERIFICATION = (
    ROOT / "verification/wave47-three-root-moment/verification-results.json"
)
W49_SCOUT = ROOT / "attempts/wave49-five-root-moment/combined-sdp-result.json"
W49_COEFFICIENTS = (
    ROOT / "verification/wave49-five-root-moment/independent-coefficients.json"
)
W51_SOURCE = ROOT / "verification/wave51-rankone-cut-relaxation/exact-result.json"
W51_INDEPENDENT = (
    ROOT
    / "verification/wave51-rankone-cut-relaxation-independent/"
    "verification-result.json"
)
W51_INDEPENDENT_MANIFEST = (
    ROOT
    / "verification/wave51-rankone-cut-relaxation-independent/"
    "package-manifest.sha256"
)
W51_PROBE = ROOT / "verification/wave51-rankone-cut-relaxation/probe.py"

EXPECTED = {
    W43: "06b498a736a511a7d6f5912bd4686e5d4eb30f4041477e3ee9cbc1704f1757c8",
    W44: "fb81601a9c97fc6860702403e56da65c2ba8fd69ee6a61007a0da53cade1d722",
    W45_CUTS: "96a50f9add4b12b2c86587da29ade8b9da34f88a7b7617c048ffb7139c12b64b",
    W45_VERIFIED_COEFFICIENTS: "8d9a004392e3f642c0aacf272a33f7cce2bc21254e79fe4123bec5a065ae0bac",
    W47_CUTS: "d2ea38ed74a1b9098c9cc8eae52f8d65723c2631335b0acedba647dc16aa313e",
    W47_COEFFICIENTS: "07b55f06ff8f7d5f2de53d92a3222366e122a7306028752ecd31c10962a824b3",
    W47_VERIFICATION: "1c80d2b70b8e6bef42d4d9df124cc82dc9baf642d36873c61e91e8f2acc99a43",
    W49_SCOUT: "1e41b1fd961714b24f69d1c31474f48b91dca88d938f5c97d5aa2424b8aac152",
    W49_COEFFICIENTS: "f3f1cd0bca98965a7893a8146ecee8dff755162f3b92eeb24e1dfbc003371d5f",
    W51_SOURCE: "527656f5d2d6a03d71234dc0fb110422ddfade1ac8b5a1d175168e857073edfc",
    W51_INDEPENDENT: "24cd2316c20beabe9ecd4e143eb310f8a200f45e49dda189e12d38bc46de1452",
    W51_INDEPENDENT_MANIFEST: "0372f7a810f8243e5972e8d902155ab4c3fca3256ecf71d52afeb809a61d7017",
    W51_PROBE: "e4ee9ae7e74d2a88ae5b10f07f10f773af8fe75db1103c26cebb4945e2d7e8ca",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def compact_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def pretty_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def object_hash(value: object) -> str:
    return hashlib.sha256(compact_bytes(value)).hexdigest()


def ftext(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def free_memory_percent() -> float:
    if os.name == "nt":
        class MemoryStatusEx(ctypes.Structure):
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

        state = MemoryStatusEx()
        state.dwLength = ctypes.sizeof(state)
        require(
            bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state))),
            "GlobalMemoryStatusEx failed",
        )
        return 100.0 * state.ullAvailPhys / state.ullTotalPhys
    available = os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
    total = os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
    return 100.0 * available / total


def memory_guard(stage: str, samples: list[dict[str, object]]) -> None:
    free = free_memory_percent()
    samples.append({"stage": stage, "free_percent": round(free, 2)})
    require(
        free > MIN_FREE_PERCENT,
        f"{stage}: {free:.2f}% free physical memory is not above "
        f"{MIN_FREE_PERCENT:.2f}%",
    )


def checked_json(path: Path) -> dict[str, Any]:
    require(file_hash(path) == EXPECTED[path], f"frozen hash changed: {path}")
    value = json.loads(path.read_bytes())
    require(isinstance(value, dict), f"expected JSON object: {path}")
    return value


def load_probe() -> Any:
    require(file_hash(W51_PROBE) == EXPECTED[W51_PROBE], "Wave51 probe hash changed")
    spec = importlib.util.spec_from_file_location("wave53_frozen_wave51_probe", W51_PROBE)
    require(spec is not None and spec.loader is not None, "cannot load Wave51 probe")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def edge_pairs(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, right)
        for left in range(order)
        for right in range(left + 1, order)
    )


def relabel_mask(mask: int, order: int, permutation: tuple[int, ...]) -> int:
    positions = {pair: index for index, pair in enumerate(edge_pairs(order))}
    image = 0
    for bit, (left, right) in enumerate(edge_pairs(order)):
        if (mask >> bit) & 1:
            mapped = tuple(sorted((permutation[left], permutation[right])))
            image |= 1 << positions[mapped]
    return image


def induced_mask(mask: int, order: int, subset: tuple[int, ...]) -> int:
    positions = {pair: index for index, pair in enumerate(edge_pairs(order))}
    child = 0
    for bit, (left, right) in enumerate(edge_pairs(len(subset))):
        old = tuple(sorted((subset[left], subset[right])))
        if (mask >> positions[old]) & 1:
            child |= 1 << bit
    return child


def orbit_lookup(classes: Sequence[int], order: int) -> dict[int, int]:
    lookup: dict[int, int] = {}
    for canonical in classes:
        for permutation in itertools.permutations(range(order)):
            image = relabel_mask(int(canonical), order, permutation)
            previous = lookup.setdefault(image, int(canonical))
            require(previous == int(canonical), "canonical orbits overlap")
    return lookup


def deck_tables(
    classes7: Sequence[int], class_sets: dict[int, tuple[int, ...]]
) -> dict[int, dict[int, Counter[int]]]:
    lookups = {
        order: orbit_lookup(class_sets[order], order) for order in (4, 5, 6)
    }
    tables: dict[int, dict[int, Counter[int]]] = {4: {}, 5: {}, 6: {}}
    for seven in classes7:
        for order in (4, 5, 6):
            counter: Counter[int] = Counter()
            for subset in itertools.combinations(range(7), order):
                labelled = induced_mask(int(seven), 7, subset)
                require(labelled in lookups[order], "inadmissible lower deck child")
                counter[lookups[order][labelled]] += 1
            require(sum(counter.values()) == math.comb(7, order), "deck size failed")
            tables[order][int(seven)] = counter
    return tables


def lower_counts(
    vector: Sequence[Fraction],
    classes7: Sequence[int],
    class_sets: dict[int, tuple[int, ...]],
    decks: dict[int, dict[int, Counter[int]]],
) -> dict[int, dict[int, Fraction]]:
    result: dict[int, dict[int, Fraction]] = {
        7: {
            int(mask): Fraction(value)
            for mask, value in zip(classes7, vector[:208], strict=True)
        }
    }
    for order in (4, 5, 6):
        numerator = {mask: Fraction() for mask in class_sets[order]}
        for seven, value in result[7].items():
            if not value:
                continue
            for child, multiplicity in decks[order][seven].items():
                numerator[child] += value * multiplicity
        divisor = math.comb(N - order, 7 - order)
        result[order] = {
            mask: value / divisor for mask, value in numerator.items()
        }
        require(
            sum(result[order].values()) == math.comb(N, order),
            f"order-{order} lower-deck total failed",
        )
    return result


def zero_matrix(size: int) -> list[list[Fraction]]:
    return [[Fraction() for _ in range(size)] for _ in range(size)]


def add_upper(
    matrix: list[list[Fraction]],
    entries: Sequence[Sequence[int]],
    multiplier: Fraction,
) -> None:
    if not multiplier:
        return
    for row_raw, column_raw, coefficient_raw in entries:
        row, column, coefficient = int(row_raw), int(column_raw), int(coefficient_raw)
        value = multiplier * coefficient
        matrix[row][column] += value
        if row != column:
            matrix[column][row] += value


def quadratic(
    matrix: Sequence[Sequence[Fraction]], vector: Sequence[int]
) -> Fraction:
    return sum(
        Fraction(vector[row]) * matrix[row][column] * vector[column]
        for row in range(len(vector))
        for column in range(len(vector))
    )


def primitive_integer_vector(vector: Sequence[int | Fraction]) -> list[int]:
    fractions = [Fraction(value) for value in vector]
    denominator = math.lcm(*(value.denominator for value in fractions))
    integers = [value.numerator * (denominator // value.denominator) for value in fractions]
    divisor = math.gcd(*(abs(value) for value in integers))
    require(divisor > 0, "zero direction")
    integers = [value // divisor for value in integers]
    first = next(value for value in integers if value)
    if first < 0:
        integers = [-value for value in integers]
    return integers


def solve_unit_lower_transpose(
    lower: Sequence[Sequence[Fraction]], z: Sequence[Fraction]
) -> list[Fraction]:
    size = len(z)
    output = [Fraction() for _ in range(size)]
    for row in range(size - 1, -1, -1):
        output[row] = Fraction(z[row]) - sum(
            lower[column][row] * output[column]
            for column in range(row + 1, size)
        )
    return output


def exact_ldl_direction_or_psd(
    matrix: Sequence[Sequence[Fraction]],
) -> tuple[str, list[int] | None, Fraction | None, dict[str, object]]:
    size = len(matrix)
    lower = [[Fraction() for _ in range(size)] for _ in range(size)]
    for index in range(size):
        lower[index][index] = Fraction(1)
    diagonal = [Fraction() for _ in range(size)]
    for pivot in range(size):
        residuals = []
        for row in range(pivot, size):
            residual = matrix[row][pivot] - sum(
                lower[row][before]
                * diagonal[before]
                * lower[pivot][before]
                for before in range(pivot)
            )
            residuals.append((row, residual))
        diagonal[pivot] = residuals[0][1]
        if diagonal[pivot] < 0:
            z = [Fraction() for _ in range(size)]
            z[pivot] = Fraction(1)
            direction = primitive_integer_vector(solve_unit_lower_transpose(lower, z))
            value = quadratic(matrix, direction)
            require(value < 0, "negative LDL pivot did not yield a direction")
            return "EXACTLY_INDEFINITE", direction, value, {
                "method": "exact_ldl_negative_pivot",
                "pivot": pivot,
                "pivot_value": ftext(diagonal[pivot]),
            }
        if diagonal[pivot] == 0:
            nonzero = [(row, value) for row, value in residuals[1:] if value]
            if nonzero:
                row, offdiag = nonzero[0]
                schur_diagonal = matrix[row][row] - sum(
                    lower[row][before] ** 2 * diagonal[before]
                    for before in range(pivot)
                )
                z = [Fraction() for _ in range(size)]
                z[row] = Fraction(1)
                z[pivot] = -schur_diagonal / (2 * offdiag)
                z[pivot] -= Fraction(1 if offdiag > 0 else -1)
                direction = primitive_integer_vector(
                    solve_unit_lower_transpose(lower, z)
                )
                value = quadratic(matrix, direction)
                require(value < 0, "zero-pivot LDL direction failed")
                return "EXACTLY_INDEFINITE", direction, value, {
                    "method": "exact_ldl_zero_pivot_offdiagonal",
                    "pivot": pivot,
                    "offdiagonal_row": row,
                }
            continue
        for row, residual in residuals[1:]:
            lower[row][pivot] = residual / diagonal[pivot]
    certificate = {
        "diagonal": [ftext(value) for value in diagonal],
        "lower": [
            [row, column, ftext(lower[row][column])]
            for row in range(size)
            for column in range(row)
            if lower[row][column]
        ],
    }
    return "EXACTLY_PSD", None, None, {
        "method": "exact_ldl",
        "rank": sum(value > 0 for value in diagonal),
        "certificate_sha256": object_hash(certificate),
    }


def propose_negative_direction(
    matrix: Sequence[Sequence[Fraction]],
) -> tuple[str, list[int] | None, Fraction | None, dict[str, object]]:
    array = np.asarray(
        [[float(value) for value in row] for row in matrix], dtype=np.float64
    )
    scale = float(np.max(np.abs(array)))
    if scale:
        values, vectors = np.linalg.eigh(array / scale)
        for eigen_index in np.argsort(values):
            eigenvector = vectors[:, eigen_index]
            maximum = float(np.max(np.abs(eigenvector)))
            if not maximum:
                continue
            for rounding_scale in (
                4,
                8,
                16,
                32,
                64,
                128,
                256,
                512,
                1024,
                4096,
                16384,
                65536,
                262144,
            ):
                raw = [
                    int(round(rounding_scale * float(value) / maximum))
                    for value in eigenvector
                ]
                if not any(raw):
                    continue
                direction = primitive_integer_vector(raw)
                value = quadratic(matrix, direction)
                if value < 0:
                    return "EXACTLY_INDEFINITE", direction, value, {
                        "method": "floating_eigenvector_proposal_exact_quadratic",
                        "floating_used_as_evidence": False,
                        "proposal_eigenvalue_scaled": float(values[eigen_index]),
                        "rounding_scale": rounding_scale,
                    }
            if values[eigen_index] >= 0:
                break
    return exact_ldl_direction_or_psd(matrix)


def family_models(
    wave45: dict[str, Any],
    wave47: dict[str, Any],
    wave49: dict[str, Any],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for name in ("edge", "nonedge", "vertex"):
        records = [
            {
                "order": int(record["order"]),
                "canonical_mask": int(record["canonical_mask"]),
                "upper_entries": record["entries"],
            }
            for record in wave45["coefficient_streams"][name]
        ]
        output.append(
            {
                "layer": "wave45",
                "family": name,
                "dimension": len(wave45["flag_sets"][name]["canonical_masks"]),
                "records": records,
            }
        )
    for name, family in sorted(wave47["families"].items()):
        output.append(
            {
                "layer": "wave47",
                "family": name,
                "dimension": int(family["matrix_size"]),
                "records": family["class_coefficients"],
            }
        )
    for family in wave49["families"]:
        output.append(
            {
                "layer": "wave49",
                "family": f"root_{int(family['root_mask'])}",
                "dimension": int(family["dimension"]),
                "records": [
                    {
                        "order": 6,
                        "canonical_mask": int(record["canonical_mask"]),
                        "upper_entries": record["upper_entries"],
                    }
                    for record in family["order6"]
                ]
                + [
                    {
                        "order": 7,
                        "canonical_mask": int(record["canonical_mask"]),
                        "upper_entries": record["upper_entries"],
                    }
                    for record in family["order7"]
                ],
            }
        )
    require(len(output) == 32, "moment family census changed")
    return output


def evaluate_family(
    model: dict[str, Any],
    counts: dict[int, dict[int, Fraction]],
) -> tuple[list[list[Fraction]], dict[str, object]]:
    matrix = zero_matrix(int(model["dimension"]))
    for record in model["records"]:
        multiplier = counts[int(record["order"])].get(
            int(record["canonical_mask"]), Fraction()
        )
        add_upper(matrix, record["upper_entries"], multiplier)
    status, direction, value, proof = propose_negative_direction(matrix)
    serialized = [[ftext(value) for value in row] for row in matrix]
    record: dict[str, object] = {
        "layer": model["layer"],
        "family": model["family"],
        "dimension": model["dimension"],
        "status": status,
        "matrix_sha256": object_hash(serialized),
        "proof": proof,
    }
    if direction is not None:
        require(value is not None and value < 0, "bad exact negative direction")
        trace_scale = max(
            Fraction(1), sum(abs(matrix[index][index]) for index in range(len(matrix)))
        )
        norm_squared = sum(component * component for component in direction)
        score = value / (trace_scale * norm_squared)
        record.update(
            {
                "primitive_integer_direction": direction,
                "exact_quadratic": ftext(value),
                "selection_score": ftext(score),
            }
        )
    return matrix, record


def quadratic_by_record(
    model: dict[str, Any], direction: Sequence[int]
) -> dict[int, dict[int, int]]:
    output: dict[int, dict[int, int]] = {}
    for record in model["records"]:
        order = int(record["order"])
        temporary = zero_matrix(int(model["dimension"]))
        add_upper(temporary, record["upper_entries"], Fraction(1))
        value = quadratic(temporary, direction)
        require(value.denominator == 1, "integer coefficient quadratic became rational")
        output.setdefault(order, {})[int(record["canonical_mask"])] = value.numerator
    return output


def cut_from_direction(
    model: dict[str, Any],
    direction: Sequence[int],
    classes7: Sequence[int],
    decks: dict[int, dict[int, Counter[int]]],
    matrix_value: Fraction,
    witness: Sequence[Fraction],
) -> dict[str, Any]:
    q_records = quadratic_by_record(model, direction)
    rational_coefficients: list[Fraction] = []
    for seven in classes7:
        coefficient = Fraction(q_records.get(7, {}).get(int(seven), 0))
        for order in (4, 5, 6):
            if order not in q_records:
                continue
            divisor = math.comb(N - order, 7 - order)
            coefficient += Fraction(
                sum(
                    multiplicity * q_records[order].get(child, 0)
                    for child, multiplicity in decks[order][int(seven)].items()
                ),
                divisor,
            )
        rational_coefficients.append(coefficient)
    denominator = math.lcm(
        *(coefficient.denominator for coefficient in rational_coefficients)
    )
    dense = [
        coefficient.numerator * (denominator // coefficient.denominator)
        for coefficient in rational_coefficients
    ]
    divisor = math.gcd(*(abs(value) for value in dense))
    require(divisor > 0, "zero rank-one cut")
    dense = [value // divisor for value in dense]
    multiplier = Fraction(denominator, divisor)
    exact_value = sum(
        Fraction(coefficient) * coordinate
        for coefficient, coordinate in zip(dense, witness[:208], strict=True)
    )
    require(exact_value == multiplier * matrix_value < 0, "cut linearization failed")
    sparse = [
        [int(mask), int(coefficient)]
        for mask, coefficient in zip(classes7, dense, strict=True)
        if coefficient
    ]
    core = {
        "layer": model["layer"],
        "family": model["family"],
        "direction": list(direction),
        "constant": 0,
        "coefficients": sparse,
        "sense": "sum(coefficient*x_mask) >= 0",
    }
    return {
        **core,
        "id": object_hash(core),
        "primitive_coefficient_divisor": divisor,
        "lower_deck_denominator_lcm": denominator,
        "exact_source_value": ftext(exact_value),
        "exact_matrix_value": ftext(matrix_value),
        "linearization_multiplier": ftext(multiplier),
    }


def dense_cut(
    cut: dict[str, Any], class_index: dict[int, int]
) -> tuple[list[int], int]:
    coefficients = [0] * 209
    for mask, value in cut["coefficients"]:
        coefficients[class_index[int(mask)]] = int(value)
    return coefficients, int(cut.get("constant", 0))


def exact_validate(
    equations: Sequence[tuple[list[int], int]],
    cuts: Sequence[dict[str, Any]],
    classes: Sequence[int],
    vector: Sequence[Fraction],
) -> dict[str, Any]:
    require(len(vector) == 209, "witness width changed")
    residuals = [
        sum(
            Fraction(coefficient) * value
            for coefficient, value in zip(row, vector, strict=True)
        )
        - rhs
        for row, rhs in equations
    ]
    require(not any(residuals), "Wave44 exact equation failed")
    require(min(vector[:208]) >= 0, "negative count")
    require(Fraction(2079) <= vector[208] <= Fraction(4158), "y bound failed")
    class_index = {int(mask): index for index, mask in enumerate(classes)}
    slacks: list[Fraction] = []
    for cut in cuts:
        coefficients, constant = dense_cut(cut, class_index)
        value = Fraction(constant) + sum(
            Fraction(coefficient) * coordinate
            for coefficient, coordinate in zip(coefficients, vector, strict=True)
        )
        require(value >= 0, f"cut failed: {cut['layer']}/{cut['id']}")
        slacks.append(value)
    support = [
        {"canonical_mask": int(mask), "value": ftext(value)}
        for mask, value in zip(classes, vector[:208], strict=True)
        if value
    ]
    catalog = [ftext(value) for value in vector]
    positives = [value for value in slacks if value > 0]
    return {
        "all_170_wave44_equations": True,
        "all_cumulative_cuts_nonnegative": True,
        "cumulative_cut_checks": len(cuts),
        "all_208_counts_nonnegative": True,
        "y_bounds_satisfied": True,
        "y_h11_over_4": ftext(vector[208]),
        "support_size": len(support),
        "zero_coordinates": sum(value == 0 for value in vector[:208]),
        "tight_cuts": sum(value == 0 for value in slacks),
        "minimum_positive_cut_slack": (
            ftext(min(positives)) if positives else None
        ),
        "maximum_denominator_digits": max(
            len(str(value.denominator)) for value in vector
        ),
        "witness_vector_sha256": object_hash(catalog),
        "support": support,
    }


def scaled_numeric_problem(
    equations: Sequence[tuple[list[int], int]],
    cuts: Sequence[dict[str, Any]],
    classes: Sequence[int],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    class_index = {int(mask): index for index, mask in enumerate(classes)}
    equalities: list[np.ndarray] = []
    equality_rhs: list[float] = []
    for row, target in equations:
        scaled = np.asarray(
            [value * SEVEN_TOTAL for value in row[:208]]
            + [row[208] * Y_SCALE],
            dtype=np.float64,
        )
        divisor = max(1.0, abs(float(target)), float(np.max(np.abs(scaled))))
        equalities.append(scaled / divisor)
        equality_rhs.append(target / divisor)
    inequalities: list[np.ndarray] = []
    upper: list[float] = []
    for cut in cuts:
        row, constant = dense_cut(cut, class_index)
        scaled = np.asarray(
            [value * SEVEN_TOTAL for value in row[:208]] + [0],
            dtype=np.float64,
        )
        divisor = max(1.0, abs(float(constant)), float(np.max(np.abs(scaled))))
        inequalities.append(-scaled / divisor)
        upper.append(constant / divisor)
    return (
        np.asarray(equalities),
        np.asarray(equality_rhs),
        np.asarray(inequalities),
        np.asarray(upper),
    )


def sparse_rref(
    input_rows: Iterable[dict[int, Fraction]], column_count: int
) -> tuple[list[dict[int, Fraction]], list[int]]:
    rows = [
        {column: Fraction(value) for column, value in row.items() if value}
        for row in input_rows
    ]
    pivot_row = 0
    pivots: list[int] = []
    for column in range(column_count):
        selected = next(
            (
                index
                for index in range(pivot_row, len(rows))
                if rows[index].get(column)
            ),
            None,
        )
        if selected is None:
            continue
        rows[pivot_row], rows[selected] = rows[selected], rows[pivot_row]
        pivot = rows[pivot_row][column]
        rows[pivot_row] = {
            key: value / pivot for key, value in rows[pivot_row].items()
        }
        pivot_data = rows[pivot_row]
        for index, row in enumerate(rows):
            if index == pivot_row:
                continue
            multiplier = row.get(column)
            if not multiplier:
                continue
            updated = dict(row)
            for key, value in pivot_data.items():
                candidate = updated.get(key, Fraction()) - multiplier * value
                if candidate:
                    updated[key] = candidate
                else:
                    updated.pop(key, None)
            rows[index] = updated
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return [row for row in rows if row], pivots


def active_rows_and_solution(
    equations: Sequence[tuple[list[int], int]],
    cuts: Sequence[dict[str, Any]],
    classes: Sequence[int],
    numeric_vector: np.ndarray,
    normalized_slacks: np.ndarray,
    tolerance: float,
) -> tuple[list[Fraction], dict[str, Any]] | None:
    zero_coordinates = [
        index for index in range(208) if numeric_vector[index] <= tolerance
    ]
    active_cuts = [
        index for index, slack in enumerate(normalized_slacks) if slack <= tolerance
    ]
    rows: list[dict[int, Fraction]] = []
    for coefficients, rhs in equations:
        row = {
            index: Fraction(value)
            for index, value in enumerate(coefficients)
            if value
        }
        if rhs:
            row[209] = Fraction(rhs)
        rows.append(row)
    rows.extend({index: Fraction(1)} for index in zero_coordinates)
    if abs(float(numeric_vector[208]) - 1.0) <= tolerance:
        rows.append({208: Fraction(1), 209: Fraction(Y_SCALE)})
        active_y_bound = "upper"
    elif abs(float(numeric_vector[208]) - 2079 / Y_SCALE) <= tolerance:
        rows.append({208: Fraction(1), 209: Fraction(2079)})
        active_y_bound = "lower"
    else:
        active_y_bound = "none"
    class_index = {int(mask): index for index, mask in enumerate(classes)}
    for cut_index in active_cuts:
        coefficients, constant = dense_cut(cuts[cut_index], class_index)
        row = {
            index: Fraction(value)
            for index, value in enumerate(coefficients)
            if value
        }
        if constant:
            row[209] = Fraction(-constant)
        rows.append(row)
    rref, pivots = sparse_rref(rows, 210)
    if 209 in pivots:
        return None
    coefficient_pivots = [pivot for pivot in pivots if pivot < 209]
    if len(coefficient_pivots) != 209:
        return None
    pivot_rows = {pivot: row for pivot, row in zip(pivots, rref, strict=True)}
    exact = [pivot_rows[index].get(209, Fraction()) for index in range(209)]
    try:
        exact_validate(equations, cuts, classes, exact)
    except AssertionError:
        return None
    return exact, {
        "active_tolerance": tolerance,
        "zero_coordinate_candidates": len(zero_coordinates),
        "active_cut_candidates": len(active_cuts),
        "active_y_bound": active_y_bound,
        "exact_active_system_rank": len(coefficient_pivots),
    }


def solve_exact_vertex(
    equations: Sequence[tuple[list[int], int]],
    cuts: Sequence[dict[str, Any]],
    classes: Sequence[int],
) -> tuple[list[Fraction] | None, dict[str, Any]]:
    aeq, beq, aub, bub = scaled_numeric_problem(equations, cuts, classes)
    numeric = linprog(
        np.zeros(209),
        A_ub=aub,
        b_ub=bub,
        A_eq=aeq,
        b_eq=beq,
        bounds=[(0, None)] * 208 + [(2079 / Y_SCALE, 1)],
        method="highs-ds",
        options={
            "primal_feasibility_tolerance": 1e-10,
            "dual_feasibility_tolerance": 1e-10,
        },
    )
    if not numeric.success:
        return None, {
            "engine": "scipy.optimize.linprog HiGHS dual simplex",
            "status": str(numeric.message),
            "used_as_evidence": False,
            "feasible_active_set_returned": False,
        }
    vector = np.asarray(numeric.x)
    slacks = bub - aub @ vector
    for tolerance in ACTIVE_TOLERANCES:
        candidate = active_rows_and_solution(
            equations, cuts, classes, vector, slacks, tolerance
        )
        if candidate is not None:
            exact, metadata = candidate
            return exact, {
                "engine": "scipy.optimize.linprog HiGHS dual simplex",
                "status": str(numeric.message),
                "used_as_evidence": False,
                **metadata,
            }
    raise AssertionError("no exact feasible vertex reconstructed from numerical active sets")


def farkas_generators(
    equations: Sequence[tuple[list[int], int]],
    cuts: Sequence[dict[str, Any]],
    classes: Sequence[int],
) -> list[dict[str, Any]]:
    """Return normalized generators for a nonnegative Farkas-combination LP."""

    class_index = {int(mask): index for index, mask in enumerate(classes)}
    raw: list[dict[str, Any]] = []
    for index, (row, rhs) in enumerate(equations):
        coefficients = list(map(int, row))
        constant = -int(rhs)
        raw.append(
            {
                "kind": "equality",
                "label": f"wave44_equation_{index}",
                "coefficients": coefficients,
                "constant": constant,
                "orientation": 1,
            }
        )
        raw.append(
            {
                "kind": "equality",
                "label": f"wave44_equation_{index}",
                "coefficients": coefficients,
                "constant": constant,
                "orientation": -1,
            }
        )
    for index, cut in enumerate(cuts):
        coefficients, constant = dense_cut(cut, class_index)
        raw.append(
            {
                "kind": "inequality",
                "label": f"cut_{index}_{cut['layer']}_{cut['id']}",
                "coefficients": coefficients,
                "constant": constant,
                "orientation": 1,
            }
        )
    for index, mask in enumerate(classes):
        coefficients = [0] * 209
        coefficients[index] = 1
        raw.append(
            {
                "kind": "inequality",
                "label": f"nonnegative_x_{int(mask)}",
                "coefficients": coefficients,
                "constant": 0,
                "orientation": 1,
            }
        )
    lower = [0] * 209
    lower[208] = 1
    raw.append(
        {
            "kind": "inequality",
            "label": "y_lower_2079",
            "coefficients": lower,
            "constant": -2079,
            "orientation": 1,
        }
    )
    upper = [0] * 209
    upper[208] = -1
    raw.append(
        {
            "kind": "inequality",
            "label": "y_upper_4158",
            "coefficients": upper,
            "constant": 4158,
            "orientation": 1,
        }
    )
    output = []
    for generator in raw:
        scale = max(
            1,
            abs(int(generator["constant"])),
            *(abs(int(value)) for value in generator["coefficients"]),
        )
        orientation = int(generator["orientation"])
        output.append(
            {
                **generator,
                "scale": scale,
                "normalized": [
                    Fraction(orientation * int(value), scale)
                    for value in generator["coefficients"]
                ]
                + [Fraction(orientation * int(generator["constant"]), scale)],
            }
        )
    return output


def exact_solution_on_support(
    generators: Sequence[dict[str, Any]],
    support: Sequence[int],
    approximate_weights: Sequence[float],
) -> list[Fraction] | None:
    width = len(support)
    rows: list[dict[int, Fraction]] = []
    target = [Fraction()] * 209 + [Fraction(-1)]
    for coordinate in range(210):
        row = {
            position: generators[index]["normalized"][coordinate]
            for position, index in enumerate(support)
            if generators[index]["normalized"][coordinate]
        }
        if target[coordinate]:
            row[width] = target[coordinate]
        rows.append(row)
    rref, pivots = sparse_rref(rows, width + 1)
    if width in pivots:
        return None
    pivot_rows = {pivot: row for pivot, row in zip(pivots, rref, strict=True)}
    pivot_set = {pivot for pivot in pivots if pivot < width}
    free = [column for column in range(width) if column not in pivot_set]
    for maximum_denominator in (1, 10**3, 10**6, 10**9, 10**12):
        solution = [Fraction() for _ in range(width)]
        if maximum_denominator > 1:
            for column in free:
                solution[column] = Fraction(
                    float(approximate_weights[column])
                ).limit_denominator(maximum_denominator)
        for pivot in reversed(pivots):
            if pivot >= width:
                continue
            row = pivot_rows[pivot]
            solution[pivot] = row.get(width, Fraction()) - sum(
                coefficient * solution[column]
                for column, coefficient in row.items()
                if column < width and column != pivot
            )
        if any(value < 0 for value in solution):
            continue
        if all(
            sum(
                generators[index]["normalized"][coordinate]
                * solution[position]
                for position, index in enumerate(support)
            )
            == target[coordinate]
            for coordinate in range(210)
        ):
            return solution
    return None


def exact_farkas_certificate(
    equations: Sequence[tuple[list[int], int]],
    cuts: Sequence[dict[str, Any]],
    classes: Sequence[int],
) -> dict[str, Any]:
    generators = farkas_generators(equations, cuts, classes)
    matrix = np.asarray(
        [
            [float(generator["normalized"][coordinate]) for generator in generators]
            for coordinate in range(210)
        ],
        dtype=np.float64,
    )
    target = np.zeros(210, dtype=np.float64)
    target[-1] = -1.0
    numerical = linprog(
        np.zeros(len(generators)),
        A_eq=matrix,
        b_eq=target,
        bounds=[(0, None)] * len(generators),
        method="highs-ds",
        options={
            "primal_feasibility_tolerance": 1e-10,
            "dual_feasibility_tolerance": 1e-10,
        },
    )
    require(
        numerical.success,
        "numerical certificate support scout failed: " + str(numerical.message),
    )
    weights = np.asarray(numerical.x)
    positive_values = sorted(
        (float(value) for value in weights if value > 0), reverse=True
    )
    print(
        "farkas_scout "
        f"positive={len(positive_values)} "
        f"max={positive_values[0] if positive_values else 0:.3e} "
        f"min={positive_values[-1] if positive_values else 0:.3e} "
        f"residual={float(np.max(np.abs(matrix @ weights - target))):.3e}",
        flush=True,
    )
    exact_support: list[int] | None = None
    exact_weights: list[Fraction] | None = None
    used_tolerance: float | None = None
    for tolerance in (
        1e-7,
        1e-8,
        1e-9,
        1e-10,
        1e-11,
        1e-12,
        1e-13,
        1e-14,
        0.0,
    ):
        support = [index for index, value in enumerate(weights) if value > tolerance]
        solution = exact_solution_on_support(
            generators, support, [float(weights[index]) for index in support]
        )
        if solution is not None:
            exact_support = support
            exact_weights = solution
            used_tolerance = tolerance
            break
    require(
        exact_support is not None and exact_weights is not None,
        "numerical Farkas support did not reconstruct exactly; support sizes "
        + str(
            {
                tolerance: sum(value > tolerance for value in weights)
                for tolerance in (
                    1e-7,
                    1e-8,
                    1e-9,
                    1e-10,
                    1e-11,
                    1e-12,
                    1e-13,
                    1e-14,
                    0.0,
                )
            }
        ),
    )
    combined: dict[tuple[str, str], Fraction] = {}
    for index, weight in zip(exact_support, exact_weights, strict=True):
        if not weight:
            continue
        generator = generators[index]
        raw_multiplier = (
            weight
            * int(generator["orientation"])
            / int(generator["scale"])
        )
        key = (str(generator["kind"]), str(generator["label"]))
        combined[key] = combined.get(key, Fraction()) + raw_multiplier
    combined = {key: value for key, value in combined.items() if value}
    require(
        all(
            multiplier >= 0
            for (kind, _label), multiplier in combined.items()
            if kind == "inequality"
        ),
        "negative inequality multiplier in Farkas combination",
    )
    denominator = math.lcm(*(value.denominator for value in combined.values()))
    integers = {
        key: value.numerator * (denominator // value.denominator)
        for key, value in combined.items()
    }
    divisor = math.gcd(*(abs(value) for value in integers.values()))
    integers = {key: value // divisor for key, value in integers.items()}

    base_lookup: dict[tuple[str, str], tuple[list[int], int]] = {}
    for generator in generators:
        key = (str(generator["kind"]), str(generator["label"]))
        base_lookup.setdefault(
            key,
            (
                list(map(int, generator["coefficients"])),
                int(generator["constant"]),
            ),
        )
    aggregate = [0] * 209
    constant = 0
    entries = []
    for key in sorted(integers):
        multiplier = integers[key]
        coefficients, base_constant = base_lookup[key]
        for coordinate, coefficient in enumerate(coefficients):
            aggregate[coordinate] += multiplier * coefficient
        constant += multiplier * base_constant
        entries.append(
            {
                "kind": key[0],
                "label": key[1],
                "integer_multiplier": multiplier,
            }
        )
    require(not any(aggregate), "Farkas variable coefficients do not cancel")
    require(constant < 0, "Farkas contradiction constant is not negative")
    require(
        all(
            entry["integer_multiplier"] >= 0
            for entry in entries
            if entry["kind"] == "inequality"
        ),
        "integer inequality multiplier became negative",
    )
    catalog = [
        {
            "kind": generator["kind"],
            "label": generator["label"],
            "orientation": generator["orientation"],
            "scale": generator["scale"],
            "coefficients_sha256": object_hash(generator["coefficients"]),
            "constant": generator["constant"],
        }
        for generator in generators
    ]
    return {
        "status": "EXACT_FARKAS_CONTRADICTION",
        "generator_catalog_sha256": object_hash(catalog),
        "generator_count": len(generators),
        "numerical_support_scout": {
            "engine": "scipy.optimize.linprog HiGHS dual simplex",
            "status": str(numerical.message),
            "used_as_evidence": False,
            "support_tolerance": used_tolerance,
        },
        "primitive_integer_multiplier_count": len(entries),
        "entries": entries,
        "aggregate_variable_coefficients_all_zero": True,
        "contradiction_constant": constant,
        "interpretation": (
            "A nonnegative integer combination of all listed inequalities plus "
            "an unrestricted integer combination of Wave44 equalities equals "
            f"the negative constant {constant}."
        ),
    }


def witness_from_source(
    source: dict[str, Any],
    independent: dict[str, Any],
    classes: Sequence[int],
) -> list[Fraction]:
    support = {
        int(record["canonical_mask"]): Fraction(record["value"])
        for record in source["exact_certificate"]["support"]
    }
    vector = [support.get(int(mask), Fraction()) for mask in classes]
    vector.append(Fraction(source["exact_certificate"]["y_h11_over_4"]))
    require(
        source["exact_certificate"]["witness_vector_sha256"]
        == independent["exact_witness"]["witness_vector_sha256"],
        "independent verifier and source witness hashes differ",
    )
    require(
        source["exact_certificate"]["support_size"]
        == independent["exact_witness"]["support_size"]
        == 136,
        "Wave51 support-136 premise changed",
    )
    return vector


def evaluate_all(
    models: Sequence[dict[str, Any]],
    counts: dict[int, dict[int, Fraction]],
) -> tuple[list[dict[str, object]], list[tuple[dict[str, Any], Fraction]]]:
    records: list[dict[str, object]] = []
    matrices: list[tuple[dict[str, Any], Fraction]] = []
    for model in models:
        matrix, record = evaluate_family(model, counts)
        records.append(record)
        if record["status"] == "EXACTLY_INDEFINITE":
            matrices.append((model, Fraction(str(record["exact_quadratic"]))))
        model["_last_matrix"] = matrix
    return records, matrices


def select_cut(
    models: Sequence[dict[str, Any]],
    records: Sequence[dict[str, object]],
    classes: Sequence[int],
    decks: dict[int, dict[int, Counter[int]]],
    witness: Sequence[Fraction],
    existing_ids: set[str],
) -> tuple[dict[str, Any], dict[str, object]]:
    candidates = []
    record_lookup = {
        (str(record["layer"]), str(record["family"])): record for record in records
    }
    for model in models:
        record = record_lookup[(model["layer"], model["family"])]
        if record["status"] != "EXACTLY_INDEFINITE":
            continue
        direction = [int(value) for value in record["primitive_integer_direction"]]
        matrix_value = Fraction(str(record["exact_quadratic"]))
        cut = cut_from_direction(
            model, direction, classes, decks, matrix_value, witness
        )
        if cut["id"] in existing_ids:
            continue
        candidates.append(
            (
                Fraction(str(record["selection_score"])),
                str(model["layer"]),
                str(model["family"]),
                cut,
                record,
            )
        )
    require(candidates, "all found negative directions duplicate existing cuts")
    score, layer, family, cut, record = min(candidates, key=lambda item: item[:3])
    selection = {
        "rule": (
            "Among nonduplicate exact negative directions, minimize the exact "
            "trace-scaled Rayleigh score q/(||v||^2*max(1,sum(abs(diagonal)))); "
            "break ties by layer and family."
        ),
        "eligible_nonduplicate_candidates": len(candidates),
        "selected_layer": layer,
        "selected_family": family,
        "selected_score": ftext(score),
        "source_matrix_sha256": record["matrix_sha256"],
    }
    return cut, selection


def load_vector(record: dict[str, Any], classes: Sequence[int]) -> list[Fraction]:
    support = {
        int(item["canonical_mask"]): Fraction(item["value"])
        for item in record["witness"]["support"]
    }
    vector = [support.get(int(mask), Fraction()) for mask in classes]
    vector.append(Fraction(record["witness"]["y_h11_over_4"]))
    return vector


def build_context() -> tuple[
    Any,
    list[int],
    list[tuple[list[int], int]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[int, tuple[int, ...]],
    dict[int, dict[int, Counter[int]]],
    list[Fraction],
]:
    for path in EXPECTED:
        require(file_hash(path) == EXPECTED[path], f"frozen hash changed: {path}")
    probe = load_probe()
    row_system, equations, base_cuts, bundle = probe.build_bundle()
    require(bundle["total"] == 174, "Wave51 baseline cut census changed")
    classes = [int(mask) for mask in row_system["classes"]]
    wave45 = checked_json(W45_VERIFIED_COEFFICIENTS)
    wave47 = checked_json(W47_COEFFICIENTS)
    wave49 = checked_json(W49_COEFFICIENTS)
    wave47_verification = checked_json(W47_VERIFICATION)
    require(
        wave47_verification["cuts"]["complete_ledger_exactly_equal_to_sealed"],
        "Wave47 coefficient/cut layer is not independently replayed",
    )
    independent = checked_json(W51_INDEPENDENT)
    source = checked_json(W51_SOURCE)
    require(
        independent["claim_label"] == "VERIFIED"
        and
        independent["conclusion"]["fixed_174_cut_rational_relaxation"]
        == "EXACTLY_FEASIBLE",
        "Wave51 independent premise is not verified",
    )
    class_sets = {
        int(order): tuple(map(int, values))
        for order, values in wave45["unrooted_class_sets"].items()
    }
    require(tuple(classes) == class_sets[7], "seven-class streams differ")
    decks = deck_tables(classes, class_sets)
    models = family_models(wave45, wave47, wave49)
    initial = witness_from_source(source, independent, classes)
    exact_validate(equations, base_cuts, classes, initial)
    return (
        probe,
        classes,
        equations,
        base_cuts,
        models,
        class_sets,
        decks,
        initial,
    )


def exact_iteration(
    iteration: int,
    vector: list[Fraction],
    equations: Sequence[tuple[list[int], int]],
    cuts: list[dict[str, Any]],
    models: Sequence[dict[str, Any]],
    classes: Sequence[int],
    class_sets: dict[int, tuple[int, ...]],
    decks: dict[int, dict[int, Counter[int]]],
    samples: list[dict[str, object]],
    add_cut: bool,
) -> tuple[dict[str, Any], list[Fraction] | None]:
    memory_guard(f"iteration-{iteration}-before-matrices", samples)
    witness = exact_validate(equations, cuts, classes, vector)
    counts = lower_counts(vector, classes, class_sets, decks)
    matrix_records, _ = evaluate_all(models, counts)
    indefinite = sum(
        record["status"] == "EXACTLY_INDEFINITE" for record in matrix_records
    )
    psd = sum(record["status"] == "EXACTLY_PSD" for record in matrix_records)
    require(indefinite + psd == 32, "not every matrix received an exact status")
    record: dict[str, Any] = {
        "iteration": iteration,
        "witness": witness,
        "matrix_evaluation": {
            "families_checked_exactly": len(matrix_records),
            "exactly_indefinite": indefinite,
            "exactly_psd": psd,
            "records": matrix_records,
        },
        "cumulative_cut_count_before_selection": len(cuts),
    }
    if not add_cut:
        record["bounded_stop"] = {
            "reason": "configured three-cut discovery limit reached",
            "remaining_exactly_indefinite_matrices": indefinite,
        }
        memory_guard(f"iteration-{iteration}-terminal", samples)
        return record, None
    existing_ids = {str(cut["id"]) for cut in cuts}
    selected, selection = select_cut(
        models, matrix_records, classes, decks, vector, existing_ids
    )
    require(Fraction(selected["exact_source_value"]) < 0, "new cut misses source")
    cuts.append(selected)
    record["selection"] = selection
    record["added_cut"] = selected
    memory_guard(f"iteration-{iteration}-before-lp", samples)
    next_vector, scout = solve_exact_vertex(equations, cuts, classes)
    record["numerical_active_set_scout"] = scout
    if next_vector is None:
        memory_guard(f"iteration-{iteration}-before-farkas", samples)
        certificate = exact_farkas_certificate(equations, cuts, classes)
        record["exact_farkas_certificate"] = certificate
        record["terminal"] = {
            "reason": "exact Farkas contradiction for the augmented finite LP",
            "new_cut_count": iteration + 1,
        }
        memory_guard(f"iteration-{iteration}-after-farkas", samples)
        return record, None
    next_certificate = exact_validate(equations, cuts, classes, next_vector)
    record["next_witness_exact_substitution"] = {
        key: next_certificate[key]
        for key in (
            "all_170_wave44_equations",
            "all_cumulative_cuts_nonnegative",
            "cumulative_cut_checks",
            "all_208_counts_nonnegative",
            "y_bounds_satisfied",
            "witness_vector_sha256",
        )
    }
    memory_guard(f"iteration-{iteration}-after-lp", samples)
    return record, next_vector


def compute() -> dict[str, Any]:
    samples: list[dict[str, object]] = []
    memory_guard("start", samples)
    (
        _probe,
        classes,
        equations,
        cuts,
        models,
        class_sets,
        decks,
        vector,
    ) = build_context()
    baseline_ids = [str(cut["id"]) for cut in cuts]
    iterations = []
    for iteration in range(MAX_CUT_ITERATIONS):
        record, next_vector = exact_iteration(
            iteration,
            vector,
            equations,
            cuts,
            models,
            classes,
            class_sets,
            decks,
            samples,
            add_cut=True,
        )
        iterations.append(record)
        if next_vector is None:
            break
        vector = next_vector
        print(
            f"iteration={iteration} cut={record['added_cut']['layer']}/"
            f"{record['added_cut']['family']} "
            f"next_support={record['next_witness_exact_substitution']['witness_vector_sha256'][:12]}",
            flush=True,
        )
    if iterations[-1].get("exact_farkas_certificate") is None:
        terminal, _ = exact_iteration(
            MAX_CUT_ITERATIONS,
            vector,
            equations,
            cuts,
            models,
            classes,
            class_sets,
            decks,
            samples,
            add_cut=False,
        )
        iterations.append(terminal)
    else:
        terminal = None
    new_cuts = [
        record["added_cut"] for record in iterations if "added_cut" in record
    ]
    farkas_found = "exact_farkas_certificate" in iterations[-1]
    witness_count = sum("witness" in record for record in iterations)
    result = {
        "format": "wave53-bounded-exact-cut-loop-v1",
        "role": "discovery",
        "claim_label": "CANDIDATE",
        "scope": (
            f"{len(new_cuts)} exact rank-one cut additions starting from the "
            "independently verified Wave51 support-136 rational witness; all "
            "32 available Wave45/Wave47/Wave49 moment families evaluated at "
            f"{witness_count} rational witnesses."
        ),
        "inputs": [
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": digest,
            }
            for path, digest in EXPECTED.items()
        ],
        "configuration": {
            "configured_maximum_cut_iterations": MAX_CUT_ITERATIONS,
            "completed_cut_iterations": len(new_cuts),
            "rational_witnesses_evaluated": witness_count,
            "moment_families_per_witness": {
                "wave45": 3,
                "wave47": 8,
                "wave49": 21,
                "total": 32,
            },
            "initial_cut_count": len(baseline_ids),
            "final_cut_count": len(cuts),
            "integrality_imposed": False,
        },
        "baseline_cut_ids_sha256": object_hash(baseline_ids),
        "new_cut_catalog_sha256": object_hash(
            [
                {
                    key: cut[key]
                    for key in (
                        "id",
                        "layer",
                        "family",
                        "direction",
                        "constant",
                        "coefficients",
                    )
                }
                for cut in new_cuts
            ]
        ),
        "iterations": iterations,
        "resource_guard": {
            "required_strictly_more_than_free_percent": MIN_FREE_PERCENT,
            "guard_check_count": len(samples),
            "all_guard_checks_passed": True,
            "live_telemetry_embedded": False,
        },
        "conclusion": {
            "augmented_finite_relaxation_after_last_new_cut": (
                "EXACTLY_INFEASIBLE_CANDIDATE"
                if farkas_found
                else "EXACTLY_FEASIBLE"
            ),
            "exact_farkas_certificate": (
                "CANDIDATE_EMITTED" if farkas_found else "NOT_FOUND"
            ),
            "full_psd_system_feasibility": "UNKNOWN",
            "full_verified_cut_ledger_feasibility": "UNKNOWN",
            "integer_count_feasibility": "UNKNOWN",
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "graph_constructed": False,
        },
        "limitations": [
            "This is discovery output and has not been independently verified.",
            "The loop is bounded to three added directions and does not exhaust any PSD cone.",
            "Numerical solvers selected active sets and proposed eigenvectors only; every retained object was checked exactly.",
            "Rational aggregate feasibility does not imply integer counts or a graph.",
            "No endpoint or Conway-99 status is promoted.",
        ],
    }
    memory_guard("finish", samples)
    result["resource_guard"]["guard_check_count"] = len(samples)
    payload = pretty_bytes(result)
    OUTPUT.write_bytes(payload)
    print(
        "CANDIDATE "
        f"iterations={len(new_cuts)} "
        f"farkas={farkas_found} "
        f"witnesses={witness_count}"
    )
    print(f"result_sha256={hashlib.sha256(payload).hexdigest()}")
    return result


def validate() -> dict[str, Any]:
    samples: list[dict[str, object]] = []
    memory_guard("validate-start", samples)
    stored_bytes = OUTPUT.read_bytes()
    stored = json.loads(stored_bytes)
    require(stored["claim_label"] == "CANDIDATE", "discovery label changed")
    (
        _probe,
        classes,
        equations,
        cuts,
        models,
        class_sets,
        decks,
        initial,
    ) = build_context()
    vector = initial
    for position, stored_iteration in enumerate(stored["iterations"]):
        require(position == stored_iteration["iteration"], "iteration order changed")
        exact_record, _ = exact_iteration(
            position,
            vector,
            equations,
            cuts,
            models,
            classes,
            class_sets,
            decks,
            samples,
            add_cut=False,
        )
        require(
            exact_record["witness"] == stored_iteration["witness"],
            f"iteration {position} witness replay differs",
        )
        require(
            exact_record["matrix_evaluation"]
            == stored_iteration["matrix_evaluation"],
            f"iteration {position} matrix replay differs",
        )
        if "added_cut" not in stored_iteration:
            break
        stored_cut = stored_iteration["added_cut"]
        matrix_records = exact_record["matrix_evaluation"]["records"]
        selected, selection = select_cut(
            models,
            matrix_records,
            classes,
            decks,
            vector,
            {str(cut["id"]) for cut in cuts},
        )
        require(selected == stored_cut, f"iteration {position} selected cut differs")
        require(
            selection == stored_iteration["selection"],
            f"iteration {position} selection metadata differs",
        )
        cuts.append(stored_cut)
        if "exact_farkas_certificate" in stored_iteration:
            certificate = exact_farkas_certificate(equations, cuts, classes)
            require(
                certificate == stored_iteration["exact_farkas_certificate"],
                f"iteration {position} Farkas certificate replay differs",
            )
            break
        require(
            position + 1 < len(stored["iterations"]),
            "feasible cut iteration lacks a successor witness",
        )
        next_record = stored["iterations"][position + 1]
        vector = load_vector(next_record, classes)
        exact_validate(equations, cuts, classes, vector)
    require(
        len(cuts) == int(stored["configuration"]["final_cut_count"]),
        "final cut count changed",
    )
    memory_guard("validate-finish", samples)
    print(
        "PASS_EXACT_REPLAY "
        f"sha256={hashlib.sha256(stored_bytes).hexdigest()} "
        f"witnesses={len(stored['iterations'])} "
        f"matrix_checks={sum(i['matrix_evaluation']['families_checked_exactly'] for i in stored['iterations'])} "
        f"new_cuts={len(cuts) - 174}"
    )
    return stored


def main() -> int:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--compute", action="store_true")
    action.add_argument("--validate", action="store_true")
    arguments = parser.parse_args()
    if arguments.compute:
        compute()
    else:
        validate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
