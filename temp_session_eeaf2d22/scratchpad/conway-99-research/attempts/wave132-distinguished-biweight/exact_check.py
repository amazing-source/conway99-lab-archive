"""Exact Wave132 distinguished-row biweight projection replay."""

from __future__ import annotations

import argparse
import ctypes
import json
import os
from fractions import Fraction
from math import comb
from pathlib import Path


N = 99
IMAGE_DIMENSION = 54
DUAL_DIMENSION = 45
IMAGE_ORDER = 1 << IMAGE_DIMENSION
DUAL_ORDER = 1 << DUAL_DIMENSION
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
WITNESS_PATH = HERE / "joint-witness.json"
SCOUT_PATH = HERE / "integral-scout.json"
WAVE131_WITNESS = (
    ROOT / "attempts/wave131-binary-lcd-enumerator/rational-witness.json"
)
DEFAULT_OUTPUT = HERE / "exact-results.json"
IMAGE_LOWER = {
    14: 99,
    24: 4158,
    26: 693,
    30: 70686,
    32: 41580,
    34: 36036,
    36: 8547,
}
DUAL_BASE_LOWER = {
    15: 99,
    24: 693,
    26: 4158,
    31: 41580,
    33: 79002,
    35: 8316,
    37: 27720,
    39: 231,
}


def free_memory_percent() -> float:
    if os.name != "nt":
        return 100.0

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


def parse(value: str | int) -> Fraction:
    return Fraction(value)


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


def arrays(payload: dict) -> tuple[list[Fraction], list[Fraction]]:
    image = [Fraction(0) for _ in range(N + 1)]
    dual = [Fraction(0) for _ in range(N + 1)]
    for weight, value in payload["ordinary"][
        "image_coefficients"
    ].items():
        image[int(weight)] = parse(value)
    for weight, value in payload["ordinary"][
        "dual_coefficients"
    ].items():
        dual[int(weight)] = parse(value)
    return image, dual


def ordinary_audit(image: list[Fraction], dual: list[Fraction]) -> dict:
    if any(value < 0 for value in image + dual):
        raise AssertionError("negative ordinary coefficient")
    if sum(image) != IMAGE_ORDER or sum(dual) != DUAL_ORDER:
        raise AssertionError("ordinary size drift")
    if image[0] != 1 or dual[0] != 1 or dual[99] != 1:
        raise AssertionError("zero/all-one coefficient drift")
    if any(image[weight] for weight in range(1, 14)):
        raise AssertionError("image minimum-distance drift")
    if any(image[weight] for weight in range(1, 100, 2)):
        raise AssertionError("image evenness drift")
    if any(dual[weight] for weight in range(1, 15)):
        raise AssertionError("dual minimum-distance drift")
    if any(dual[weight] != dual[N - weight] for weight in range(N + 1)):
        raise AssertionError("dual complement drift")
    for weight, lower in IMAGE_LOWER.items():
        if image[weight] < lower:
            raise AssertionError("image lower bound drift")
    dual_lower = dict(DUAL_BASE_LOWER)
    for weight, lower in list(dual_lower.items()):
        dual_lower[N - weight] = lower
    for weight, lower in dual_lower.items():
        if dual[weight] < lower:
            raise AssertionError("dual lower bound drift")
    for degree in range(N + 1):
        forward = sum(
            image[weight] * krawtchouk(degree, weight)
            for weight in range(N + 1)
        ) / IMAGE_ORDER
        if forward != dual[degree]:
            raise AssertionError(f"forward MacWilliams drift at {degree}")
        inverse = sum(
            dual[weight] * krawtchouk(degree, weight)
            for weight in range(N + 1)
        ) / DUAL_ORDER
        if inverse != image[degree]:
            raise AssertionError(f"inverse MacWilliams drift at {degree}")
    if any(image[weight] for weight in (94, 96, 98)):
        raise AssertionError("distinguished high-weight cut drift")
    return {
        "all_200_MacWilliams_rows_pass": True,
        "all_coefficients_nonnegative": True,
        "image_size": str(IMAGE_ORDER),
        "dual_size": str(DUAL_ORDER),
        "image_minimum_nonzero_weight": min(
            weight for weight, value in enumerate(image)
            if weight and value
        ),
        "dual_minimum_nonzero_weight": min(
            weight for weight, value in enumerate(dual)
            if weight and value
        ),
        "forced_zero_image_weights": [94, 96, 98],
        "image_nonintegral_coefficient_count": sum(
            value.denominator != 1 for value in image
        ),
        "dual_nonintegral_coefficient_count": sum(
            value.denominator != 1 for value in dual
        ),
    }


def pair_table_audit(payload: dict) -> dict:
    tables = payload["distinguished_pair_tables"]
    image = tables["image_neighborhood_rows"]
    dual = tables["dual_closed_neighborhood_rows"]
    mixed = tables["mixed_neighborhood_closed"]
    if image != {
        "14": {"intersection_14": 99},
        "ordered_distinct": {
            "intersection_1": 1386,
            "intersection_2": 8316,
        },
    }:
        raise AssertionError("image pair table drift")
    if dual != {
        "15": {"intersection_15": 99},
        "ordered_distinct": {
            "intersection_2": 8316,
            "intersection_3": 1386,
        },
    }:
        raise AssertionError("dual pair table drift")
    if mixed != {
        "ordered_diagonal": {"intersection_14": 99},
        "ordered_off_diagonal": {"intersection_2": 9702},
    }:
        raise AssertionError("mixed pair table drift")
    return {
        "image_ordered_pair_total": 99 + 1386 + 8316,
        "dual_ordered_pair_total": 99 + 1386 + 8316,
        "mixed_ordered_pair_total": 99 + 9702,
        "all_equal_99_squared": True,
        "ordered_edges": 1386,
        "ordered_nonedges": 8316,
        "compositions_n00_n01_n10_n11": {
            "image_diagonal_w14_t14": [85, 0, 0, 14],
            "image_ordered_edge_w14_t1": [72, 13, 13, 1],
            "image_ordered_nonedge_w14_t2": [73, 12, 12, 2],
            "dual_diagonal_w15_t15": [84, 0, 0, 15],
            "dual_ordered_edge_w15_t3": [72, 12, 12, 3],
            "dual_ordered_nonedge_w15_t2": [71, 13, 13, 2],
            "mixed_diagonal_w14_w15_t14": [84, 1, 0, 14],
            "mixed_offdiagonal_w14_w15_t2": [72, 13, 12, 2],
        },
    }


def split_audit(
    table: dict,
    enumerator: list[Fraction],
    distinguished_weight: int,
    odd_multiplier: str,
    forced_by_weight: dict[int, dict[int, int]],
) -> dict:
    nonzero_rows = 0
    rational_entries = 0
    for weight, coefficient in enumerate(enumerator):
        submitted = {
            int(intersection): parse(value)
            for intersection, value in table.get(str(weight), {}).items()
        }
        if not coefficient:
            if submitted:
                raise AssertionError("split row at zero coefficient")
            continue
        nonzero_rows += 1
        lower = max(0, weight + distinguished_weight - N)
        upper = min(weight, distinguished_weight)
        if any(
            intersection < lower or intersection > upper
            for intersection in submitted
        ):
            raise AssertionError("intersection range drift")
        if any(value < 0 for value in submitted.values()):
            raise AssertionError("negative split coefficient")
        if sum(submitted.values()) != 99 * coefficient:
            raise AssertionError("split row sum drift")
        if sum(
            intersection * value
            for intersection, value in submitted.items()
        ) != distinguished_weight * weight * coefficient:
            raise AssertionError("split first moment drift")
        odd_target = weight * coefficient if odd_multiplier == "weight" else 0
        if sum(
            value
            for intersection, value in submitted.items()
            if intersection % 2
        ) != odd_target:
            raise AssertionError("split parity count drift")
        for intersection, lower_count in forced_by_weight.get(
            weight, {}
        ).items():
            if submitted.get(intersection, Fraction(0)) < lower_count:
                raise AssertionError("forced split row drift")
        rational_entries += sum(
            value.denominator != 1 for value in submitted.values()
        )
    return {
        "nonzero_weight_rows": nonzero_rows,
        "all_row_sums_first_moments_and_parities_pass": True,
        "nonintegral_entry_count": rational_entries,
    }


def wave131_strictness() -> dict:
    old = json.loads(WAVE131_WITNESS.read_text(encoding="utf-8"))
    old_a98 = parse(old["image_coefficients"]["98"])
    if old_a98 <= 0:
        raise AssertionError("Wave131 strictness control drift")
    return {
        "Wave131_A98": (
            str(old_a98.numerator)
            if old_a98.denominator == 1
            else f"{old_a98.numerator}/{old_a98.denominator}"
        ),
        "Wave131_passed_ordinary_MacWilliams": True,
        "Wave131_fails_distinguished_moment_cut": True,
        "reason": (
            "for an image word of weight w, exactly w neighborhood-row "
            "intersections are odd; their total is at most "
            "13*w+14*(99-w)=1386-w but must equal 14*w, so w<=92"
        ),
    }


def exact_results() -> dict:
    payload = json.loads(WITNESS_PATH.read_text(encoding="utf-8"))
    image, dual = arrays(payload)
    ordinary = ordinary_audit(image, dual)
    pair_tables = pair_table_audit(payload)
    split = payload["split_enumerators"]
    split_audits = {
        "image_vs_neighborhood": split_audit(
            split["image_vs_neighborhood"],
            image,
            14,
            "weight",
            {14: {14: 99, 1: 1386, 2: 8316}},
        ),
        "dual_vs_closed": split_audit(
            split["dual_vs_closed"],
            dual,
            15,
            "weight",
            {15: {15: 99, 3: 1386, 2: 8316}},
        ),
        "image_vs_closed": split_audit(
            split["image_vs_closed"],
            image,
            15,
            "zero",
            {14: {14: 99, 2: 9702}},
        ),
        "dual_vs_neighborhood": split_audit(
            split["dual_vs_neighborhood"],
            dual,
            14,
            "zero",
            {15: {14: 99, 2: 9702}},
        ),
    }
    scout = json.loads(SCOUT_PATH.read_text(encoding="utf-8"))
    return {
        "format": "wave132-distinguished-biweight-v1",
        "claim_labels": {
            "distinguished_pair_compositions": "DERIVED",
            "high_weight_image_cut": "DERIVED",
            "rational_low_degree_split_feasibility": "CANDIDATE_EXACT",
            "integral_low_degree_split_feasibility": "UNKNOWN",
            "full_genus_two_MacWilliams_feasibility": "UNKNOWN",
        },
        "scope": {
            "target": "hypothetical srg(99,14,1,2)",
            "automorphism_assumed": False,
            "full_genus_two_encoded": False,
            "projection": (
                "ordinary MacWilliams plus exact distinguished pair "
                "tables and per-shell split row sums, first moments, "
                "intersection parity counts, and range constraints"
            ),
        },
        "distinguished_identities": {
            "r_u": "row_u(A), weight 14, in im(A)",
            "q_u": "row_u(I+A), weight 15, in ker(A)",
            "dot_r_u_r_v": "A_uv",
            "dot_q_u_q_v": "(I+A)_uv",
            "dot_r_u_q_v": "0",
            "image_shell": {
                "pair_count": "sum_j P[w,j]=99*A_w",
                "first_moment": "sum_j j*P[w,j]=14*w*A_w",
                "odd_count": "sum_odd_j P[w,j]=w*A_w",
            },
            "dual_shell": {
                "pair_count": "sum_j Q[w,j]=99*B_w",
                "first_moment": "sum_j j*Q[w,j]=15*w*B_w",
                "odd_count": "sum_odd_j Q[w,j]=w*B_w",
            },
            "mixed_shells": {
                "all_intersections_even": True,
                "image_vs_closed_first_moment": "15*w*A_w",
                "dual_vs_neighborhood_first_moment": "14*w*B_w",
            },
        },
        "pair_table_audit": pair_tables,
        "strictness_over_Wave131": wave131_strictness(),
        "high_weight_cut": {
            "inequality": "14*w <= 13*w+14*(99-w)=1386-w",
            "consequence": "15*w<=1386",
            "even_image_weight_upper": 92,
            "forced_zero_weights": [94, 96, 98],
        },
        "rational_witness": {
            "ordinary_audit": ordinary,
            "split_audits": split_audits,
            "formal_integral_split_enumerator": False,
            "binary_code_realized": False,
        },
        "integral_scout": scout,
        "full_genus_two_boundary": {
            "raw_four_composition_states": comb(102, 3),
            "C_times_C_even_weight_states": 42925,
            "GL2_orbits_on_C_times_C_states": 7803,
            "dense_partial_Hadamard_transform_materialized": False,
            "missing_constraints": [
                "second and higher intersection moments in each shell",
                "coupling of different distinguished roots",
                "full partial-Hadamard transform from CxC to CxD and DxD",
                "nonnegative genus-two coefficients in every transformed composition",
            ],
        },
        "status": {
            "Wave131_specific_rational_point_survives": False,
            "stronger_rational_projection_feasible": True,
            "integral_projection": "UNKNOWN",
            "full_genus_two": "UNKNOWN",
            "binary_code_constructed": False,
            "graph_constructed": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "The witness is a rational low-degree split enumerator, not a full genus-two enumerator.",
            "The bounded integral scout supplies no infeasibility evidence.",
            "Aggregate distinguished pair tables do not realize 99 labelled codewords.",
            "No binary code or graph is constructed.",
            "Discovery cannot verify itself.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    free = free_memory_percent()
    if free < 15.0:
        raise SystemExit(
            f"refusing to run with only {free:.1f}% free physical memory"
        )
    result = exact_results()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.verify is not None:
        if (
            not args.verify.exists()
            or args.verify.read_text(encoding="utf-8") != encoded
        ):
            raise SystemExit("canonical exact-results.json mismatch")
        print(
            "PASS: canonical Wave132 result verified; "
            f"free physical memory {free:.1f}%"
        )
        return
    args.output.write_text(encoded, encoding="utf-8")
    print(f"wrote {args.output}; free physical memory {free:.1f}%")


if __name__ == "__main__":
    main()
