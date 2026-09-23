"""Exact Wave131 binary LCD enumerator and MacWilliams replay.

The graph-derived low-weight counts and the stored rational witness are
checked independently with Python integers and Fractions.  This module does
not construct a binary code or a graph.
"""

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
WITNESS_PATH = HERE / "rational-witness.json"
SCOUT_PATH = HERE / "integral-scout.json"
DEFAULT_OUTPUT = HERE / "exact-results.json"


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


def forced_distributions() -> dict:
    vertices = 99
    degree = 14
    edges = vertices * degree // 2
    nonedges = comb(vertices, 2) - edges
    triangles = edges // 3

    # Each neighborhood is 7K2.  A P3 is determined by its center and a
    # nonadjacent neighbor pair.
    paths = vertices * (comb(degree, 2) - degree // 2)

    # For an edge, 72 third vertices meet neither endpoint.  Twelve of them
    # meet the unique triangle vertex; the remaining sixty do not.
    one_edge_common = edges * (degree - 2)
    one_edge_plain = edges * 60
    one_edge_total = one_edge_common + one_edge_plain

    independent_total = (
        comb(vertices, 3)
        - triangles
        - paths
        - one_edge_total
    )
    # A common neighbor chooses one vertex from each of three of the seven
    # matched pairs in its neighborhood.  There cannot be two common
    # neighbors, since any vertex pair has at most two common neighbors and
    # would then need to contain the entire independent triple.
    independent_common = vertices * comb(7, 3) * (2**3)
    independent_plain = independent_total - independent_common

    if (
        edges,
        nonedges,
        triangles,
        paths,
        one_edge_plain,
        one_edge_common,
        independent_plain,
        independent_common,
    ) != (693, 4158, 231, 8316, 41580, 8316, 70686, 27720):
        raise AssertionError("three-set census drift")

    image = {
        14: vertices,
        24: nonedges,
        26: edges,
        30: independent_plain,
        32: one_edge_plain,
        34: paths + independent_common,
        36: triangles + one_edge_common,
    }
    dual = {
        15: vertices,
        24: edges,
        26: nonedges,
        31: one_edge_plain,
        33: paths + independent_plain,
        35: one_edge_common,
        37: independent_common,
        39: triangles,
    }
    expected_image = {
        14: 99,
        24: 4158,
        26: 693,
        30: 70686,
        32: 41580,
        34: 36036,
        36: 8547,
    }
    expected_dual = {
        15: 99,
        24: 693,
        26: 4158,
        31: 41580,
        33: 79002,
        35: 8316,
        37: 27720,
        39: 231,
    }
    if image != expected_image or dual != expected_dual:
        raise AssertionError("forced enumerator table drift")

    complement = {
        N - weight: count
        for weight, count in dual.items()
    }
    return {
        "subset_census": {
            "vertices": vertices,
            "edges": edges,
            "nonedges": nonedges,
            "triangles": triangles,
            "induced_P3": paths,
            "one_edge_no_common_all_three": one_edge_plain,
            "one_edge_one_common_all_three": one_edge_common,
            "independent_no_common_neighbor": independent_plain,
            "independent_one_common_neighbor": independent_common,
            "all_three_subsets": comb(vertices, 3),
        },
        "injectivity": {
            "A_map": (
                "A*1_S=A*1_T implies 1_(S symmetric_difference T) "
                "lies in ker(A) with weight at most 6; dual minimum >=8 "
                "forces S=T"
            ),
            "I_plus_A_map": (
                "(I+A)*1_S=(I+A)*1_T implies the symmetric difference "
                "lies in ker(I+A)=im(A) with weight at most 6; image "
                "minimum >=8 forces S=T"
            ),
            "domain": "all vertex subsets of size at most 3",
            "both_maps_injective": True,
        },
        "image_forced_lower": {
            str(weight): count for weight, count in image.items()
        },
        "dual_forced_lower": {
            str(weight): count for weight, count in dual.items()
        },
        "dual_complement_forced_lower": {
            str(weight): count for weight, count in sorted(complement.items())
        },
    }


def witness_audit(forced: dict) -> dict:
    payload = json.loads(WITNESS_PATH.read_text(encoding="utf-8"))
    image = [Fraction(0) for _ in range(N + 1)]
    dual = [Fraction(0) for _ in range(N + 1)]
    for weight, value in payload["image_coefficients"].items():
        image[int(weight)] = parse(value)
    for weight, value in payload["dual_coefficients"].items():
        dual[int(weight)] = parse(value)

    if any(value < 0 for value in image + dual):
        raise AssertionError("negative witness coefficient")
    if sum(image) != IMAGE_ORDER or sum(dual) != DUAL_ORDER:
        raise AssertionError("enumerator size drift")
    if image[0] != 1 or dual[0] != 1 or dual[N] != 1:
        raise AssertionError("zero/all-one coefficient drift")
    if any(image[weight] for weight in range(1, 14)):
        raise AssertionError("image distance drift")
    if any(dual[weight] for weight in range(1, 15)):
        raise AssertionError("dual distance drift")
    if any(image[weight] for weight in range(1, N + 1, 2)):
        raise AssertionError("image evenness drift")
    if any(dual[weight] != dual[N - weight] for weight in range(N + 1)):
        raise AssertionError("dual complement symmetry drift")

    for weight, lower in forced["image_forced_lower"].items():
        if image[int(weight)] < lower:
            raise AssertionError("image forced bound drift")
    for table in (
        forced["dual_forced_lower"],
        forced["dual_complement_forced_lower"],
    ):
        for weight, lower in table.items():
            if dual[int(weight)] < lower:
                raise AssertionError("dual forced bound drift")

    for degree in range(N + 1):
        transformed = sum(
            image[weight] * krawtchouk(degree, weight)
            for weight in range(N + 1)
        ) / IMAGE_ORDER
        if transformed != dual[degree]:
            raise AssertionError(f"forward MacWilliams drift at {degree}")
    for degree in range(N + 1):
        transformed = sum(
            dual[weight] * krawtchouk(degree, weight)
            for weight in range(N + 1)
        ) / DUAL_ORDER
        if transformed != image[degree]:
            raise AssertionError(f"inverse MacWilliams drift at {degree}")

    image_nonintegral = [
        weight for weight, value in enumerate(image)
        if value.denominator != 1
    ]
    dual_nonintegral = [
        weight for weight, value in enumerate(dual)
        if value.denominator != 1
    ]
    return {
        "all_200_forward_and_inverse_MacWilliams_rows_pass": True,
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
        "image_even": True,
        "dual_complement_symmetric": True,
        "image_nonintegral_coefficient_count": len(image_nonintegral),
        "dual_nonintegral_coefficient_count": len(dual_nonintegral),
        "image_nonintegral_weights": image_nonintegral,
        "dual_nonintegral_weights": dual_nonintegral,
        "formal_integral_enumerator": False,
        "realized_binary_code": False,
    }


def exact_results() -> dict:
    forced = forced_distributions()
    witness = witness_audit(forced)
    integral_scout = json.loads(SCOUT_PATH.read_text(encoding="utf-8"))
    return {
        "format": "wave131-binary-lcd-enumerator-v1",
        "claim_labels": {
            "forced_low_weight_counts": "DERIVED",
            "rational_ordinary_MacWilliams_feasibility": "CANDIDATE_EXACT",
            "integral_ordinary_MacWilliams_feasibility": "UNKNOWN",
            "binary_code_realization": "UNKNOWN",
            "graph_realization": "UNKNOWN",
        },
        "frozen_binary_facts": {
            "A_mod2_idempotent": True,
            "image": {
                "parameters": "[99,54]",
                "even": True,
                "LCD": True,
                "minimum_weight_lower": 8,
                "row_weight_upper": 14,
            },
            "kernel": {
                "parameters": "[99,45]",
                "LCD": True,
                "minimum_weight_lower": 8,
                "contains_all_one": True,
                "I_plus_A_row_weight_upper": 15,
            },
            "dual_pair": "im(A)^perp=ker(A)",
        },
        "forced_distributions": forced,
        "rational_witness_audit": witness,
        "integral_scout": integral_scout,
        "ordinary_enumerator_boundary": {
            "rational_cone_excludes_target": False,
            "integral_formal_system_status": integral_scout["result"]["status"],
            "LCD_intersection_encoded": False,
            "distinguished_99_rows_encoded": False,
            "joint_support_intersections_encoded": False,
        },
        "next_boundary": [
            "joint weight enumerators for distinguished neighborhood and closed-neighborhood rows",
            "split enumerators conditioned on one or two graph vertices",
            "LCD-compatible generator/dual-generator intersection data",
            "simultaneous realization of the 99 weight-14 image rows and 99 weight-15 kernel rows",
        ],
        "status": {
            "image_distance_14_ordinary_enumerator_feasible_over_Q": True,
            "dual_distance_15_ordinary_enumerator_feasible_over_Q": True,
            "integral_formal_enumerator": "UNKNOWN",
            "binary_code_constructed": False,
            "graph_constructed": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "The stored witness has rational, not integral, coefficients.",
            "Ordinary MacWilliams identities forget intersections among distinguished graph rows.",
            "LCD is a generator-dual intersection condition not certified by an ordinary enumerator.",
            "The integral scout is bounded and non-evidentiary.",
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
            "PASS: canonical Wave131 result verified; "
            f"free physical memory {free:.1f}%"
        )
        return
    args.output.write_text(encoded, encoding="utf-8")
    print(f"wrote {args.output}; free physical memory {free:.1f}%")


if __name__ == "__main__":
    main()
