"""Exact fixed-C4 sum/difference and pairwise-relaxation checks.

Discovery only.  This module proves conditional finite consequences and
checks a formal pairwise witness.  It does not construct an SRG, an
integer eigenvector family, or the required local extension cap.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from collections import Counter
from fractions import Fraction
from pathlib import Path


Q = Fraction
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "exact-results.json"
WITNESS_PATH = HERE / "witness.json"
NORMS = (16, 18, 20)


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


def fraction_text(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def invert(matrix: list[list[Q]]) -> list[list[Q]]:
    n = len(matrix)
    work = [
        row[:] + [Q(i == j) for j in range(n)]
        for i, row in enumerate(matrix)
    ]
    for column in range(n):
        pivot = next(row for row in range(column, n) if work[row][column])
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [entry / scale for entry in work[column]]
        for row in range(n):
            if row == column or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                left - scale * right
                for left, right in zip(work[row], work[column])
            ]
    return [row[n:] for row in work]


def quadratic(vector: list[Q], matrix: list[list[Q]]) -> Q:
    return sum(
        vector[i] * matrix[i][j] * vector[j]
        for i in range(len(vector))
        for j in range(len(vector))
    )


def c4_projector() -> tuple[list[list[Q]], list[list[Q]]]:
    edges = {(0, 1), (1, 2), (2, 3), (0, 3)}
    gram = []
    for i in range(4):
        row = []
        for j in range(4):
            adjacent = int((min(i, j), max(i, j)) in edges)
            row.append((Q(3 * (i == j) - adjacent) + Q(1, 9)) / 7)
        gram.append(row)
    return gram, invert(gram)


def multiply(left: list[list[Q]], right: list[list[Q]]) -> list[list[Q]]:
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(len(right)))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def ldlt_positive_definite(
    matrix: list[list[Q]],
) -> tuple[bool, list[Q]]:
    """Return an exact no-pivot LDL^T positivity certificate."""
    n = len(matrix)
    lower = [[Q(0) for _ in range(n)] for _ in range(n)]
    pivots: list[Q] = []
    for i in range(n):
        for j in range(i):
            numerator = matrix[i][j] - sum(
                lower[i][k] * pivots[k] * lower[j][k]
                for k in range(j)
            )
            if not pivots[j]:
                return False, pivots
            lower[i][j] = numerator / pivots[j]
        pivot = matrix[i][i] - sum(
            lower[i][k] * lower[i][k] * pivots[k]
            for k in range(i)
        )
        pivots.append(pivot)
        if pivot <= 0:
            return False, pivots
        lower[i][i] = Q(1)
    return True, pivots


def pairwise_rows() -> list[dict]:
    rows = []
    for index, left in enumerate(NORMS):
        for right in NORMS[index:]:
            lower = (32 - left - right) // 2
            upper = (left + right - 14) // 2
            low_difference_rows = []
            for difference_norm in (14, 16, 18, 20):
                numerator = left + right - difference_norm
                if numerator % 2:
                    continue
                inner = numerator // 2
                if lower <= inner <= upper:
                    low_difference_rows.append(
                        {
                            "difference_norm": difference_norm,
                            "inner_product": inner,
                            "forced_difference_profile": (
                                f"{difference_norm // 2} plus units and "
                                f"{difference_norm // 2} minus units"
                            ),
                            "opposite_sign_overlap": 0,
                        }
                    )
            rows.append(
                {
                    "norm_pair": [left, right],
                    "inner_product_interval": [lower, upper],
                    "lower_source": "norm(x+y)>=32",
                    "upper_source": "nonzero norm(x-y)>=14",
                    "classified_difference_rows": low_difference_rows,
                }
            )
    return rows


def load_witness() -> dict:
    return json.loads(WITNESS_PATH.read_text(encoding="utf-8"))


def validate_witness() -> dict:
    witness = load_witness()
    sizes = witness["block_sizes"]
    records = witness["records"]
    if sizes != [10, 10, 25, 10, 10, 26]:
        raise AssertionError("block sizes drift")
    if len(records) != 40:
        raise AssertionError("witness must contain forty records")
    normalized = []
    for record in records:
        if len(record) != len(sizes):
            raise AssertionError("record block count drift")
        blocks = []
        for block, size in zip(record, sizes):
            if len(block) != 2 or len(set(block)) != 2:
                raise AssertionError("each block must select two coordinates")
            if not all(isinstance(value, int) and 0 <= value < size for value in block):
                raise AssertionError("block coordinate out of range")
            blocks.append(frozenset(block))
        normalized.append(blocks)

    overlap_histogram: Counter[int] = Counter()
    difference_histogram: Counter[int] = Counter()
    gram = [[Q(0) for _ in records] for _ in records]
    residual = [[Q(0) for _ in records] for _ in records]
    pair_rows = []
    for i, left in enumerate(normalized):
        gram[i][i] = Q(16)
        residual[i][i] = Q(52, 5)
        for j in range(i):
            right = normalized[j]
            overlap = sum(len(a & b) for a, b in zip(left, right))
            if overlap > 5:
                raise AssertionError("pair overlap exceeds five")
            inner = 4 + overlap
            difference_norm = 32 - 2 * inner
            sum_norm = 32 + 2 * inner
            plus_units = 12 - overlap
            minus_units = 12 - overlap
            if difference_norm != plus_units + minus_units:
                raise AssertionError("difference profile arithmetic drift")
            if difference_norm <= 20:
                if difference_norm not in (14, 16, 18, 20):
                    raise AssertionError("unexpected classified norm")
                if plus_units != difference_norm // 2:
                    raise AssertionError("classified balanced profile drift")
            overlap_histogram[overlap] += 1
            difference_histogram[difference_norm] += 1
            gram[i][j] = gram[j][i] = Q(inner)
            residual[i][j] = residual[j][i] = Q(inner) - Q(28, 5)
            pair_rows.append(
                {
                    "overlap": overlap,
                    "inner": inner,
                    "difference_norm": difference_norm,
                    "sum_norm": sum_norm,
                }
            )

    positive, pivots = ldlt_positive_definite(residual)
    if not positive or len(pivots) != 40:
        raise AssertionError("residual Gram is not exact positive definite")
    if sum(overlap_histogram.values()) != 40 * 39 // 2:
        raise AssertionError("pair count drift")

    total_pair_inner_product = sum(
        (4 + overlap) * count
        for overlap, count in overlap_histogram.items()
    )
    full_family_sum_norm = 40 * 16 + 2 * total_pair_inner_product
    if total_pair_inner_product != 4598 or full_family_sum_norm != 9836:
        raise AssertionError("full-family sum arithmetic drift")

    witness_hash = hashlib.sha256(
        WITNESS_PATH.read_bytes()
    ).hexdigest()
    return {
        "family_size": len(records),
        "individual_norm": 16,
        "fixed_anchor_profile": {
            "positive_cycle_anchors": 2,
            "negative_cycle_anchors": 2,
            "positive_outside_units": 6,
            "negative_outside_units": 6,
        },
        "fixed_C4_type_counts_per_record": {
            "positive_from_each_N_anchor_only_fiber": 2,
            "positive_from_type00": 2,
            "negative_from_each_P_anchor_only_fiber": 2,
            "negative_from_type00": 2,
            "type11_used": 0,
        },
        "anchor_eigen_equations_satisfied": True,
        "outside_eigen_equations_encoded": False,
        "opposite_sign_overlap_between_records": 0,
        "overlap_histogram": {
            str(key): overlap_histogram[key]
            for key in sorted(overlap_histogram)
        },
        "inner_product_histogram": {
            str(4 + key): overlap_histogram[key]
            for key in sorted(overlap_histogram)
        },
        "difference_norm_histogram": {
            str(key): difference_histogram[key]
            for key in sorted(difference_histogram)
        },
        "binary_support_minimum_distance": min(
            row["difference_norm"] for row in pair_rows
        ),
        "maximum_pair_overlap": max(
            row["overlap"] for row in pair_rows
        ),
        "minimum_pair_sum_norm": min(
            row["sum_norm"] for row in pair_rows
        ),
        "total_pair_inner_product": total_pair_inner_product,
        "full_family_sum_squared_norm": full_family_sum_norm,
        "full_family_anchor_lower": 4 * 40 * 40 + 8 * 40,
        "every_positive_subset_anchor_lower_satisfied": True,
        "residual_gram_size": 40,
        "residual_gram_rank": 40,
        "residual_gram_positive_definite": True,
        "residual_gram_diagonal": "52/5",
        "normalized_residual_inner_products": [
            "-2/13",
            "-3/52",
            "1/26",
            "7/52",
            "3/13",
            "17/52",
        ],
        "ldlt_positive_pivot_count": len(pivots),
        "ldlt_minimum_pivot": fraction_text(min(pivots)),
        "witness_sha256": witness_hash,
    }


def exact_results() -> dict:
    gram, inverse = c4_projector()
    identity = multiply(gram, inverse)
    if identity != [
        [Q(i == j) for j in range(4)] for i in range(4)
    ]:
        raise AssertionError("projector inverse drift")
    alternating = [Q(1), Q(-1), Q(1), Q(-1)]
    doubled = [2 * value for value in alternating]
    unit_minimum = quadratic(alternating, inverse)
    doubled_minimum = quadratic(doubled, inverse)
    if unit_minimum != Q(28, 5) or doubled_minimum != Q(112, 5):
        raise AssertionError("affine interpolation norm drift")

    witness = validate_witness()
    rows = pairwise_rows()
    if [row["inner_product_interval"] for row in rows] != [
        [0, 9],
        [-1, 10],
        [-2, 11],
        [-2, 11],
        [-3, 12],
        [-4, 13],
    ]:
        raise AssertionError("pairwise interval table drift")

    return {
        "format": "wave120-fixedc4-sumdiff-v1",
        "claim_labels": {
            "projector_and_anchor_bounds": "DERIVED",
            "pairwise_cap_route": "REFUTED_AS_A_RELAXATION",
            "actual_extension_cap": "UNKNOWN",
        },
        "scope": {
            "target": "hypothetical srg(99,14,1,2)",
            "fixed_cycle_orientation": [1, -1, 1, -1],
            "family_norms": list(NORMS),
            "automorphism_assumed": False,
            "norm20_profile_source": (
                "Wave96 DERIVED discovery; independent verification pending"
            ),
        },
        "projector_affine_slice": {
            "projector_formula": "E=(27I-9A+J)/63",
            "C4_principal_gram": [
                [fraction_text(value) for value in row] for row in gram
            ],
            "C4_principal_inverse": [
                [fraction_text(value) for value in row] for row in inverse
            ],
            "unit_alternating_minimum_squared_norm": fraction_text(
                unit_minimum
            ),
            "doubled_alternating_minimum_squared_norm": fraction_text(
                doubled_minimum
            ),
            "doubled_minimum_is_exact_real_affine_minimum": True,
            "doubled_minimum_is_not_an_integer_lattice_attainment_claim": True,
            "coordinate_kernel_dimension": 40,
        },
        "integer_anchor_sharpening": {
            "universal_squared_norm_lower": 32,
            "positive_r_fold_sum_lower": "4*r^2+8*r",
            "proof": [
                "the four anchors contribute squared norm 16",
                "each positive anchor needs outside negative mass at least 4",
                "the two positive anchors have disjoint outside neighborhoods",
                "there is therefore at least 8 total outside negative mass",
                "the negative anchors similarly force at least 8 positive mass",
                "integer a satisfies a^2>=abs(a), so outside energy is at least 16",
            ],
            "local_relaxation_equality_profile": {
                "cycle_coordinates": [2, -2, 2, -2],
                "outside_positive_units": 8,
                "outside_negative_units": 8,
                "other_coordinates": 0,
            },
            "sharp_for_anchor_equation_relaxation": True,
            "attained_by_actual_integer_eigenvector": "UNKNOWN",
        },
        "pairwise_inner_products": {
            "definition": "k=<x,y> for distinct same-oriented extensions",
            "sum_identity": "norm(x+y)=norm(x)+norm(y)+2k",
            "difference_identity": "norm(x-y)=norm(x)+norm(y)-2k",
            "rows": rows,
            "classified_differences_use_only_magnitude_profiles": True,
            "full_support_graph_compatibility_encoded": False,
        },
        "formal_pairwise_witness": witness,
        "null_control": {
            "witness_size": 40,
            "rank28_needed_cap": 25,
            "rank30_needed_cap": 24,
            "derived_norm_profile_PSD_or_Gram_relaxation_can_prove_either_cap": False,
            "binary_minimum_distance_or_constant_weight_Delsarte_can_prove_either_cap": False,
            "reason": (
                "the explicit size-40 witness satisfies the fixed-C4 type "
                "counts, anchor equations, all derived pairwise norm/profile "
                "conditions, every positive subset-sum anchor inequality, a "
                "positive-definite rank-40 residual Gram, and binary support "
                "minimum distance 14"
            ),
            "not_refuted": (
                "a stronger bound using simultaneous outside adjacency, the "
                "common graph parity code with its dual constraints, or "
                "three-point and higher compatibility"
            ),
        },
        "status": {
            "rank28_excluded": False,
            "rank30_excluded": False,
            "local_cap25_proved": False,
            "local_cap24_proved": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "The size-40 object is a formal pairwise relaxation witness, not an eigenvector family.",
            "Its individual signed supports satisfy only the fixed-anchor equations, not all 99 eigen-equations.",
            "The PSD realization need not preserve the witness's integer coordinates away from the fixed C4.",
            "The binary supports are a constant-weight code, not proved to lie in one target graph kernel.",
            "Wave96 norm20 input remains discovery-level until independently verified.",
            "Discovery cannot verify itself.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_positional", nargs="?", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", nargs="?", const=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    if args.output is not None and args.output_positional is not None:
        parser.error("choose positional output or --output, not both")
    free = free_memory_percent()
    if free < 15.0:
        raise SystemExit(
            f"refusing to run with only {free:.1f}% free physical memory"
        )
    result = exact_results()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.verify is not None:
        target = Path(args.verify)
        if (
            not target.exists()
            or target.read_text(encoding="utf-8") != encoded
        ):
            raise SystemExit("canonical exact-results.json mismatch")
        print(
            "PASS: canonical Wave120 result verified; "
            f"free physical memory {free:.1f}%"
        )
        return
    output = args.output or args.output_positional or DEFAULT_OUTPUT
    output.write_text(encoded, encoding="utf-8")
    print(f"wrote {output}; free physical memory {free:.1f}%")


if __name__ == "__main__":
    main()
