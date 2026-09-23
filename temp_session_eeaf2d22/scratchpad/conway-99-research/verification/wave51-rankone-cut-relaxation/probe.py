#!/usr/bin/env python3
"""Exact probe of a fixed 174-cut endpoint count relaxation."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
import math
import os
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy.optimize import linprog


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
W43 = ROOT / "attempts/wave43-seven-deck-endpoint/exact-results.json"
ROW_SYSTEM = ROOT / "attempts/wave44-rooted-flags/row-system.json"
W45 = ROOT / "attempts/wave45-flag-moment/checkpoint-v1-seed0-17cuts-15witnesses.json"
W45_MANIFEST = ROOT / "verification/wave45-flag-moment/package-manifest.sha256"
W47 = ROOT / "attempts/wave47-three-root-moment/cuts.json"
W47_VERIFICATION = ROOT / "verification/wave47-three-root-moment/verification-results.json"
W49_SCOUT = ROOT / "attempts/wave49-five-root-moment/combined-sdp-result.json"
W49_COEFFICIENTS = ROOT / "verification/wave49-five-root-moment/independent-coefficients.json"
OUTPUT = HERE / "exact-result.json"
EXPECTED = {
    W43: "06b498a736a511a7d6f5912bd4686e5d4eb30f4041477e3ee9cbc1704f1757c8",
    ROW_SYSTEM: "fb81601a9c97fc6860702403e56da65c2ba8fd69ee6a61007a0da53cade1d722",
    W45: "96a50f9add4b12b2c86587da29ade8b9da34f88a7b7617c048ffb7139c12b64b",
    W45_MANIFEST: "d6e4d8b0b549318cd5d109718cff0bc94eb615956e7e3c5ade7d1e0362a10bf0",
    W47: "d2ea38ed74a1b9098c9cc8eae52f8d65723c2631335b0acedba647dc16aa313e",
    W47_VERIFICATION: "1c80d2b70b8e6bef42d4d9df124cc82dc9baf642d36873c61e91e8f2acc99a43",
    W49_SCOUT: "1e41b1fd961714b24f69d1c31474f48b91dca88d938f5c97d5aa2424b8aac152",
    W49_COEFFICIENTS: "f3f1cd0bca98965a7893a8146ecee8dff755162f3b92eeb24e1dfbc003371d5f",
}
N = 99
SEVEN_TOTAL = math.comb(N, 7)
Y_SCALE = 4158
MIN_FREE_PERCENT = 15.0
ACTIVE_TOLERANCE = 1e-10


def canonical_payload(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def fstr(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def parse_fraction(value: str | int) -> Fraction:
    return Fraction(value)


def free_memory_percent() -> float:
    if os.name == "nt":
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
        state = MEMORYSTATUSEX()
        state.dwLength = ctypes.sizeof(state)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state)):
            raise OSError("GlobalMemoryStatusEx failed")
        return 100 * state.ullAvailPhys / state.ullTotalPhys
    available = os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
    total = os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
    return 100 * available / total


def guard(stage: str) -> float:
    free = free_memory_percent()
    if free < MIN_FREE_PERCENT:
        raise MemoryError(f"{stage}: only {free:.2f}% physical memory free")
    return free


def checked_bytes(path: Path) -> bytes:
    payload = path.read_bytes()
    if sha256_bytes(payload) != EXPECTED[path]:
        raise ValueError(f"frozen hash mismatch: {path}")
    return payload


def checked_json(path: Path) -> dict[str, Any]:
    value = json.loads(checked_bytes(path))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def pairs(order: int) -> list[tuple[int, int]]:
    return [(left, right) for left in range(order) for right in range(left + 1, order)]


def relabel_mask(mask: int, order: int, permutation: tuple[int, ...]) -> int:
    positions = {pair: index for index, pair in enumerate(pairs(order))}
    output = 0
    for index, (left, right) in enumerate(pairs(order)):
        if (mask >> index) & 1:
            image = tuple(sorted((permutation[left], permutation[right])))
            output |= 1 << positions[image]
    return output


_CANONICAL: dict[tuple[int, int], int] = {}


def canonical_mask(mask: int, order: int) -> int:
    key = (order, mask)
    if key not in _CANONICAL:
        _CANONICAL[key] = min(
            relabel_mask(mask, order, permutation)
            for permutation in itertools.permutations(range(order))
        )
    return _CANONICAL[key]


def induced_mask(mask: int, order: int, subset: tuple[int, ...]) -> int:
    positions = {pair: index for index, pair in enumerate(pairs(order))}
    output = 0
    for bit, (left, right) in enumerate(pairs(len(subset))):
        old = tuple(sorted((subset[left], subset[right])))
        if (mask >> positions[old]) & 1:
            output |= 1 << bit
    return output


def derive_order6_counts(w43: dict[str, Any]) -> dict[int, int]:
    counts: dict[int, int] = {}
    for item in w43["certificate"]["support"]:
        host = int(item["canonical_mask"])
        host_count = int(item["count"])
        for subset in itertools.combinations(range(7), 6):
            target = canonical_mask(induced_mask(host, 7, subset), 6)
            counts[target] = counts.get(target, 0) + host_count
    if any(value % 93 for value in counts.values()):
        raise ValueError("order-six deletion total is not divisible by 93")
    return {mask: value // 93 for mask, value in counts.items()}


def quadratic(entries: list[list[int]], vector: list[int]) -> int:
    value = 0
    for row, column, coefficient in entries:
        multiplier = 1 if int(row) == int(column) else 2
        value += (
            multiplier
            * int(coefficient)
            * int(vector[int(row)])
            * int(vector[int(column)])
        )
    return value


def sparse_coefficients(records: list[dict[str, int]]) -> list[list[int]]:
    return [
        [int(record["canonical_mask"]), int(record["coefficient"])]
        for record in records
        if int(record["coefficient"])
    ]


def reconstruct_wave49_cuts(
    scout: dict[str, Any],
    coefficients: dict[str, Any],
    order6_counts: dict[int, int],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    family_lookup = {
        int(family["root_mask"]): family for family in coefficients["families"]
    }
    scout_families = scout["solvers"][0]["candidate"]["wave49_families"]
    if len(scout_families) != 21:
        raise ValueError("Wave49 direction family count changed")
    output = []
    checks = 0
    for candidate in scout_families:
        root_mask = int(candidate["root_mask"])
        family = family_lookup[root_mask]
        sealed = candidate["candidate_minimum_direction_exact_cut"]
        vector = [int(value) for value in sealed["primitive_integer_vector"]]
        if len(vector) != int(family["dimension"]):
            raise ValueError("Wave49 direction dimension mismatch")
        constant = sum(
            quadratic(record["upper_entries"], vector)
            * order6_counts.get(int(record["canonical_mask"]), 0)
            for record in family["order6"]
        )
        order7 = [
            [
                int(record["canonical_mask"]),
                quadratic(record["upper_entries"], vector),
            ]
            for record in family["order7"]
        ]
        order7 = [record for record in order7 if record[1]]
        if constant != int(sealed["constant_raw_numerator"]):
            raise ValueError(f"Wave49 constant mismatch at root {root_mask}")
        if order7 != [
            [int(mask), int(value)]
            for mask, value in sealed["order7_count_coefficients"]
        ]:
            raise ValueError(f"Wave49 coefficient mismatch at root {root_mask}")
        checks += 1 + len(family["order6"]) + len(family["order7"])
        output.append(
            {
                "layer": "wave49",
                "id": f"root5_{root_mask}",
                "family": f"root5_{root_mask}",
                "constant": constant,
                "coefficients": order7,
                "direction": vector,
                "sealed_cut_payload_sha256": sealed[
                    "payload_sha256_without_this_field"
                ],
            }
        )
    return output, {
        "families": len(output),
        "exact_reconstruction_checks": checks,
        "status": "PASS_EXACT",
    }


def normalize_old_cut(layer: str, cut: dict[str, Any]) -> dict[str, Any]:
    return {
        "layer": layer,
        "id": str(cut["cut_sha256"]),
        "family": str(cut["family"]),
        "constant": int(cut["constant"]),
        "coefficients": sparse_coefficients(cut["coefficients"]),
        "direction": [
            int(value) for value in cut.get("direction", cut.get("vector", []))
        ],
    }


def build_bundle() -> tuple[
    dict[str, Any], list[tuple[list[int], int]], list[dict[str, Any]], dict[str, Any]
]:
    checked_bytes(W45_MANIFEST)
    row_system = checked_json(ROW_SYSTEM)
    w43 = checked_json(W43)
    w45 = checked_json(W45)
    w47 = checked_json(W47)
    w47_verification = checked_json(W47_VERIFICATION)
    scout = checked_json(W49_SCOUT)
    w49_coefficients = checked_json(W49_COEFFICIENTS)
    if not w47_verification["cuts"]["complete_ledger_exactly_equal_to_sealed"]:
        raise ValueError("Wave47 cut ledger lacks exact verification")
    if not w47_verification["cuts"]["all_2664_raw_quadratics_exactly_replayed"]:
        raise ValueError("Wave47 raw quadratics were not all replayed")
    order6_counts = derive_order6_counts(w43)
    wave49, wave49_checks = reconstruct_wave49_cuts(
        scout, w49_coefficients, order6_counts
    )
    wave45 = [normalize_old_cut("wave45", cut) for cut in w45["cuts"]]
    selected47_raw = [
        cut for cut in w47["cuts"] if int(cut["source_direction_index"]) == 0
    ]
    wave47 = [normalize_old_cut("wave47", cut) for cut in selected47_raw]
    if len(wave45) != 17 or len(wave47) != 136 or len(wave49) != 21:
        raise ValueError("cut bundle census changed")
    pair_census = {
        (str(cut["source"]), str(cut["family"])) for cut in selected47_raw
    }
    if len(pair_census) != 136:
        raise ValueError("Wave47 first-direction source/family coverage changed")
    cuts = wave45 + wave47 + wave49
    catalog = [
        {
            key: cut[key]
            for key in ("layer", "id", "family", "constant", "coefficients")
        }
        for cut in cuts
    ]
    record = {
        "total": len(cuts),
        "layers": {"wave45": 17, "wave47": 136, "wave49": 21},
        "selection": {
            "wave45": "all frozen cuts",
            "wave47": "source_direction_index == 0 for every source/family pair",
            "wave49": "one sealed candidate minimum direction per family",
        },
        "catalog_sha256": sha256_bytes(canonical_payload(catalog)),
        "wave49_reconstruction": wave49_checks,
        "wave47_source_family_pairs": len(pair_census),
    }
    equations = []
    for family_name in ("base", "vertex", "edge", "nonedge"):
        family = row_system["families"][family_name]
        equations.extend(
            (list(map(int, row)), int(rhs))
            for row, rhs in zip(family["rows"], family["rhs"], strict=True)
        )
    if len(equations) != 170:
        raise ValueError("Wave44 row count changed")
    return row_system, equations, cuts, record


def dense_cut(cut: dict[str, Any], class_index: dict[int, int]) -> tuple[list[int], int]:
    coefficients = [0] * 209
    for mask, value in cut["coefficients"]:
        coefficients[class_index[int(mask)]] = int(value)
    return coefficients, int(cut["constant"])


def scaled_numeric_problem(
    equations: list[tuple[list[int], int]],
    cuts: list[dict[str, Any]],
    classes: list[int],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    class_index = {mask: index for index, mask in enumerate(classes)}
    equalities = []
    rhs = []
    for row, target in equations:
        scaled = np.asarray(
            [value * SEVEN_TOTAL for value in row[:208]]
            + [row[208] * Y_SCALE],
            dtype=np.float64,
        )
        divisor = max(1, abs(target), float(np.max(np.abs(scaled))))
        equalities.append(scaled / divisor)
        rhs.append(target / divisor)
    inequalities = []
    upper = []
    for cut in cuts:
        row, constant = dense_cut(cut, class_index)
        scaled = np.asarray(
            [value * SEVEN_TOTAL for value in row[:208]] + [0],
            dtype=np.float64,
        )
        divisor = max(1, abs(constant), float(np.max(np.abs(scaled))))
        inequalities.append(-scaled / divisor)
        upper.append(constant / divisor)
    return (
        np.asarray(equalities),
        np.asarray(rhs),
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
    pivots = []
    for column in range(column_count):
        selected = next(
            (index for index in range(pivot_row, len(rows)) if rows[index].get(column)),
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


def exact_active_vertex(
    equations: list[tuple[list[int], int]],
    cuts: list[dict[str, Any]],
    classes: list[int],
) -> tuple[list[Fraction], dict[str, Any]]:
    aeq, beq, aub, bub = scaled_numeric_problem(equations, cuts, classes)
    numeric = linprog(
        np.zeros(209),
        A_ub=aub,
        b_ub=bub,
        A_eq=aeq,
        b_eq=beq,
        bounds=[(0, None)] * 208 + [(2079 / Y_SCALE, 1)],
        method="highs-ds",
    )
    if not numeric.success:
        raise RuntimeError(f"numerical active-set scout failed: {numeric.message}")
    vector = np.asarray(numeric.x)
    slacks = bub - aub @ vector
    zero_coordinates = [
        index for index in range(208) if vector[index] <= ACTIVE_TOLERANCE
    ]
    active_cuts = [
        index for index, slack in enumerate(slacks)
        if slack <= ACTIVE_TOLERANCE
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
    if abs(vector[208] - 1) <= ACTIVE_TOLERANCE:
        rows.append({208: Fraction(1), 209: Fraction(Y_SCALE)})
        active_y_bound = "upper"
    elif abs(vector[208] - 2079 / Y_SCALE) <= ACTIVE_TOLERANCE:
        rows.append({208: Fraction(1), 209: Fraction(2079)})
        active_y_bound = "lower"
    else:
        active_y_bound = "none"
    class_index = {mask: index for index, mask in enumerate(classes)}
    for cut_index in active_cuts:
        coefficients, constant = dense_cut(cuts[cut_index], class_index)
        row = {
            index: Fraction(value)
            for index, value in enumerate(coefficients)
            if value
        }
        row[209] = Fraction(-constant)
        rows.append(row)
    rref, pivots = sparse_rref(rows, 210)
    if 209 in pivots:
        raise ValueError("numeric active set is exactly inconsistent")
    coefficient_pivots = [pivot for pivot in pivots if pivot < 209]
    if len(coefficient_pivots) != 209:
        raise ValueError(f"active set rank is {len(coefficient_pivots)}, not 209")
    pivot_rows = {
        pivot: row for pivot, row in zip(pivots, rref, strict=True)
    }
    exact = [
        pivot_rows[index].get(209, Fraction()) for index in range(209)
    ]
    active_by_layer = {
        layer: sum(cuts[index]["layer"] == layer for index in active_cuts)
        for layer in ("wave45", "wave47", "wave49")
    }
    return exact, {
        "engine": "scipy.optimize.linprog HiGHS dual simplex",
        "status": str(numeric.message),
        "used_as_evidence": False,
        "active_tolerance": ACTIVE_TOLERANCE,
        "zero_coordinate_candidates": len(zero_coordinates),
        "active_cut_candidates": len(active_cuts),
        "active_cuts_by_layer": active_by_layer,
        "active_y_bound": active_y_bound,
        "exact_active_system_rank": len(coefficient_pivots),
    }


def exact_validate(
    equations: list[tuple[list[int], int]],
    cuts: list[dict[str, Any]],
    classes: list[int],
    vector: list[Fraction],
) -> dict[str, Any]:
    if len(vector) != 209:
        raise ValueError("witness width changed")
    equation_values = [
        sum(Fraction(coefficient) * value for coefficient, value in zip(row, vector))
        - rhs
        for row, rhs in equations
    ]
    if any(equation_values):
        raise ValueError("exact Wave44 equation failed")
    class_index = {mask: index for index, mask in enumerate(classes)}
    cut_values = []
    layer_zeros = {"wave45": 0, "wave47": 0, "wave49": 0}
    for cut in cuts:
        coefficients, constant = dense_cut(cut, class_index)
        value = Fraction(constant) + sum(
            Fraction(coefficient) * coordinate
            for coefficient, coordinate in zip(coefficients, vector)
        )
        if value < 0:
            raise ValueError(f"exact cut failed: {cut['layer']}/{cut['id']}")
        cut_values.append(value)
        if value == 0:
            layer_zeros[cut["layer"]] += 1
    if min(vector[:208]) < 0:
        raise ValueError("negative order-seven count")
    if not Fraction(2079) <= vector[208] <= Fraction(4158):
        raise ValueError("y bound failed")
    positives = [value for value in cut_values if value > 0]
    support = [
        {
            "canonical_mask": int(mask),
            "value": fstr(value),
        }
        for mask, value in zip(classes, vector[:208], strict=True)
        if value
    ]
    witness_catalog = [fstr(value) for value in vector]
    return {
        "all_170_wave44_equations": True,
        "exact_equation_checks": len(equations),
        "all_174_rank_one_cuts_nonnegative": True,
        "exact_cut_checks": len(cuts),
        "zero_cut_slacks": sum(value == 0 for value in cut_values),
        "zero_cut_slacks_by_layer": layer_zeros,
        "strictly_positive_cut_slacks": len(positives),
        "minimum_strictly_positive_cut_slack": fstr(min(positives)),
        "all_208_counts_nonnegative": True,
        "support_size": len(support),
        "y_h11_over_4": fstr(vector[208]),
        "y_bounds_satisfied": True,
        "maximum_denominator_digits": max(
            len(str(value.denominator)) for value in vector
        ),
        "witness_vector_sha256": sha256_bytes(canonical_payload(witness_catalog)),
        "support": support,
    }


def compute() -> dict[str, Any]:
    memory_start = guard("start")
    row_system, equations, cuts, bundle = build_bundle()
    classes = [int(mask) for mask in row_system["classes"]]
    exact, scout = exact_active_vertex(equations, cuts, classes)
    certificate = exact_validate(equations, cuts, classes, exact)
    result = {
        "format": "wave51-exact-rankone-cut-relaxation-v1",
        "role": "strategy_scout_verifier",
        "claim_label": "VERIFIED_SCOPED",
        "scope": "exact real rational feasibility of one fixed 174-cut aggregate relaxation",
        "inputs": [
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": digest,
            }
            for path, digest in EXPECTED.items()
        ],
        "variables": {
            "order7_nonnegative_counts": 208,
            "y": "h11/4",
            "y_bounds": [2079, 4158],
            "integrality_imposed": False,
        },
        "wave44": {
            "equations": len(equations),
            "classes": len(classes),
        },
        "cut_bundle": bundle,
        "numerical_active_set_scout": scout,
        "exact_certificate": certificate,
        "resource_guard": {
            "minimum_free_physical_memory_percent": MIN_FREE_PERCENT,
            "free_percent_at_start": round(memory_start, 2),
            "free_percent_at_finish": round(guard("finish"), 2),
        },
        "conclusion": {
            "fixed_174_cut_real_relaxation": "EXACTLY_FEASIBLE",
            "farkas_contradiction_from_this_bundle": "REFUTED",
            "full_rank_one_cut_region": "UNKNOWN",
            "full_psd_constrained_region": "UNKNOWN",
            "integer_count_feasibility": "UNKNOWN",
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "graph_constructed": False,
        },
        "limitations": [
            "The witness is rational and aggregate; it is not an integer count vector.",
            "Only one balanced finite direction bundle is tested.",
            "The numerical solve selected an active set but is not evidence.",
            "Exact feasibility of this relaxation does not imply graph or SDP feasibility.",
        ],
    }
    payload = canonical_payload(result)
    OUTPUT.write_bytes(payload)
    print(
        f"status={result['conclusion']['fixed_174_cut_real_relaxation']} "
        f"support={certificate['support_size']} "
        f"zero_cuts={certificate['zero_cut_slacks']}"
    )
    print(f"result_sha256={sha256_bytes(payload)}")
    return result


def validate() -> dict[str, Any]:
    stored_payload = OUTPUT.read_bytes()
    stored = json.loads(stored_payload)
    row_system, equations, cuts, bundle = build_bundle()
    if bundle != stored["cut_bundle"]:
        raise ValueError("stored cut bundle differs from frozen inputs")
    classes = [int(mask) for mask in row_system["classes"]]
    support = {
        int(record["canonical_mask"]): parse_fraction(record["value"])
        for record in stored["exact_certificate"]["support"]
    }
    vector = [support.get(mask, Fraction()) for mask in classes]
    vector.append(parse_fraction(stored["exact_certificate"]["y_h11_over_4"]))
    certificate = exact_validate(equations, cuts, classes, vector)
    if certificate != stored["exact_certificate"]:
        raise ValueError("stored certificate summary differs from exact replay")
    print(
        "PASS_EXACT_REPLAY "
        f"result_sha256={sha256_bytes(stored_payload)} "
        f"equations={certificate['exact_equation_checks']} "
        f"cuts={certificate['exact_cut_checks']}"
    )
    return stored


def main() -> int:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--compute", action="store_true")
    action.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if args.compute:
        compute()
    else:
        validate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
