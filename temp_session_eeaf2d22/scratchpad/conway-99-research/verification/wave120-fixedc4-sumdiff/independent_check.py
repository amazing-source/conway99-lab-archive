"""Independent verifier for Wave 120 fixed-C4 sum/difference claims.

This checker does not import discovery code.  It authenticates the frozen
discovery package, reconstructs the exact arithmetic, and checks the
machine-readable forty-record object only as a formal relaxation witness.
It does not construct graph-compatible eigenvectors.
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
ROOT = HERE.parents[1]
DISCOVERY = ROOT / "attempts" / "wave120-fixedc4-sumdiff"
WAVE96 = ROOT / "verification" / "wave96-norm16-norm18-upper"
WAVE112 = ROOT / "verification" / "wave112-c4-short-vector-incidence"
DEFAULT_OUTPUT = HERE / "independent-results.json"

FROZEN_MANIFESTS = {
    "attempts/wave120-fixedc4-sumdiff/package-manifest.sha256":
        "e2e35519158556a1810affdee4bc148a333ee95a63557ea1a1e687dfcd883017",
    "verification/wave96-norm16-norm18-upper/package-manifest.sha256":
        "8b3f9f90de931dc152ccf1b9e0705409492a6c5eb5246643ddce55aad8afe6e9",
    "verification/wave112-c4-short-vector-incidence/package-manifest.sha256":
        "56845bcdf221c16ec46d40c630a8cdb3d63beed1314dd2683e17bf5c929ff024",
}
FROZEN_AGENTS_SHA256 = (
    "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3"
)
EXPECTED_INTERVALS = [
    ((16, 16), (0, 9)),
    ((16, 18), (-1, 10)),
    ((16, 20), (-2, 11)),
    ((18, 18), (-2, 11)),
    ((18, 20), (-3, 12)),
    ((20, 20), (-4, 13)),
]
BLOCK_SIZES = (10, 10, 25, 10, 10, 26)
BLOCK_SIGNS = (1, 1, 1, -1, -1, -1)
EXPECTED_HISTOGRAM = {0: 92, 1: 230, 2: 222, 3: 157, 4: 62, 5: 17}


def demand(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_json(value: object) -> str:
    payload = json.dumps(value, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


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


def parse_and_authenticate_manifest(
    relative_manifest: str,
    expected_digest: str,
) -> dict[str, str]:
    manifest = ROOT / relative_manifest
    demand(sha256_file(manifest) == expected_digest, f"manifest drift: {relative_manifest}")
    package = manifest.parent.resolve()
    entries: dict[str, str] = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        demand(len(digest) == 64, f"invalid digest in {relative_manifest}")
        demand(relative not in entries, f"duplicate manifest path: {relative}")
        target = (ROOT / relative).resolve()
        demand(target.is_relative_to(package), f"manifest path escape: {relative}")
        demand(target.is_file(), f"manifest input missing: {relative}")
        demand(sha256_file(target) == digest, f"manifest entry drift: {relative}")
        entries[relative] = digest

    actual = {
        path.relative_to(ROOT).as_posix()
        for path in package.rglob("*")
        if path.is_file()
        and path.name != "package-manifest.sha256"
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    }
    demand(set(entries) == actual, f"manifest is not file-complete: {relative_manifest}")
    return entries


def authenticate_inputs() -> dict[str, object]:
    demand(
        sha256_file(ROOT / "AGENTS.md") == FROZEN_AGENTS_SHA256,
        "AGENTS.md protocol drift",
    )
    packages = {
        relative: parse_and_authenticate_manifest(relative, digest)
        for relative, digest in FROZEN_MANIFESTS.items()
    }

    wave96 = json.loads(
        (WAVE96 / "independent-results.json").read_text(encoding="utf-8")
    )
    demand(
        wave96["status"]["finite_arithmetic"] == "VERIFIED",
        "Wave96 finite arithmetic is not verified",
    )
    demand(
        wave96["status"]["norm20_profile_theorem"]
        == "VERIFIED_CONDITIONAL_ON_FROZEN_INPUTS",
        "Wave96 norm20 classification is not verified",
    )
    demand(
        wave96["norm20_dictionary"]["surviving_profile"]
        == {"plus_one": 10, "minus_one": 10, "other": 0},
        "Wave96 norm20 surviving profile drift",
    )

    wave112 = json.loads(
        (WAVE112 / "independent-results.json").read_text(encoding="utf-8")
    )
    demand(
        wave112["verdict"] == "VERIFIED_CONDITIONAL",
        "Wave112 rooted partition is not verified",
    )
    demand(
        wave112["fixed_C4"]["partition"]
        == {
            "neither": 51,
            "p_only": 20,
            "n_only": 20,
            "one_p_and_one_n": 4,
        },
        "Wave112 fixed-C4 partition drift",
    )
    return {
        "manifest_sha256": FROZEN_MANIFESTS,
        "agents_sha256": FROZEN_AGENTS_SHA256,
        "manifest_entry_counts": {
            relative: len(entries) for relative, entries in packages.items()
        },
        "wave96_norm20_source": (
            "VERIFIED_CONDITIONAL_ON_FROZEN_INPUTS"
        ),
        "wave112_rooted_partition_source": "VERIFIED_CONDITIONAL",
        "discovery_norm20_pending_text_is_superseded": True,
    }


def inverse(matrix: list[list[Q]]) -> list[list[Q]]:
    """Gauss-Jordan inversion over Q, implemented independently."""
    n = len(matrix)
    augmented = [
        row[:] + [Q(int(i == j)) for j in range(n)]
        for i, row in enumerate(matrix)
    ]
    for column in range(n):
        pivot_row = next(
            (row for row in range(column, n) if augmented[row][column]),
            None,
        )
        demand(pivot_row is not None, "singular matrix")
        augmented[column], augmented[pivot_row] = (
            augmented[pivot_row],
            augmented[column],
        )
        pivot = augmented[column][column]
        augmented[column] = [entry / pivot for entry in augmented[column]]
        for row in range(n):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor:
                augmented[row] = [
                    left - factor * right
                    for left, right in zip(augmented[row], augmented[column])
                ]
    return [row[n:] for row in augmented]


def product(left: list[list[Q]], right: list[list[Q]]) -> list[list[Q]]:
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(len(right)))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def determinant(matrix: list[list[Q]]) -> Q:
    work = [row[:] for row in matrix]
    n = len(work)
    value = Q(1)
    for column in range(n):
        pivot_row = next(
            (row for row in range(column, n) if work[row][column]),
            None,
        )
        if pivot_row is None:
            return Q(0)
        if pivot_row != column:
            work[column], work[pivot_row] = work[pivot_row], work[column]
            value = -value
        pivot = work[column][column]
        value *= pivot
        for row in range(column + 1, n):
            factor = work[row][column] / pivot
            for index in range(column + 1, n):
                work[row][index] -= factor * work[column][index]
    return value


def quadratic(vector: list[Q], matrix: list[list[Q]]) -> Q:
    return sum(
        vector[i] * matrix[i][j] * vector[j]
        for i in range(len(vector))
        for j in range(len(vector))
    )


def fraction_text(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def verify_projector() -> dict[str, object]:
    cycle_edges = {
        frozenset((0, 1)),
        frozenset((1, 2)),
        frozenset((2, 3)),
        frozenset((3, 0)),
    }
    gram = [
        [
            (
                Q(3 * int(i == j))
                - Q(int(frozenset((i, j)) in cycle_edges and i != j))
                + Q(1, 9)
            )
            / 7
            for j in range(4)
        ]
        for i in range(4)
    ]
    gram_inverse = inverse(gram)
    demand(
        product(gram, gram_inverse)
        == [[Q(int(i == j)) for j in range(4)] for i in range(4)],
        "C4 principal inverse failed",
    )
    alternating = [Q(1), Q(-1), Q(1), Q(-1)]
    doubled = [2 * entry for entry in alternating]
    unit_minimum = quadratic(alternating, gram_inverse)
    doubled_minimum = quadratic(doubled, gram_inverse)
    gram_determinant = determinant(gram)
    demand(unit_minimum == Q(28, 5), "unit affine minimum drift")
    demand(doubled_minimum == Q(112, 5), "doubled affine minimum drift")
    demand(gram_determinant == Q(65, 2401), "principal determinant drift")
    return {
        "principal_gram": [
            [fraction_text(entry) for entry in row] for row in gram
        ],
        "principal_inverse": [
            [fraction_text(entry) for entry in row] for row in gram_inverse
        ],
        "principal_determinant": fraction_text(gram_determinant),
        "unit_alternating_real_minimum": "28/5",
        "doubled_alternating_real_minimum": "112/5",
        "real_minimum_is_integral_attainment": False,
        "coordinate_restriction_rank": 4,
        "coordinate_kernel_dimension": 40,
    }


def verify_anchor_bound() -> dict[str, object]:
    # For z_C=(r,-r,r,-r), each positive anchor receives -2r from
    # the cycle and must receive another -2r outside.  The two positive
    # anchors have no common outside neighbour because mu=2 is exhausted
    # by the two negative anchors.  The negative anchors are symmetric.
    anchor_energy_quadratic_coefficient = 4
    outside_negative_mass_coefficient = 4
    outside_positive_mass_coefficient = 4
    outside_l1_coefficient = (
        outside_negative_mass_coefficient + outside_positive_mass_coefficient
    )
    demand(outside_l1_coefficient == 8, "outside mass coefficient drift")
    samples = {
        str(r): (
            anchor_energy_quadratic_coefficient * r * r
            + outside_l1_coefficient * r
        )
        for r in range(1, 41)
    }
    demand(samples["2"] == 32, "two-vector integer bound drift")
    return {
        "mu": 2,
        "same_sign_anchor_outside_neighborhoods_disjoint": True,
        "anchor_energy": "4*r^2",
        "outside_negative_mass_lower": "4*r",
        "outside_positive_mass_lower": "4*r",
        "integer_energy_dominates_l1": True,
        "general_squared_norm_lower": "4*r^2+8*r",
        "r2_squared_norm_lower": 32,
        "local_anchor_relaxation_equality_at_r2": {
            "anchor_energy": 16,
            "outside_negative_unit_energy": 8,
            "outside_positive_unit_energy": 8,
            "total": 32,
        },
        "actual_norm32_eigenvector_exists": "UNKNOWN",
        "sample_values_r1_through_r40": samples,
    }


def ceil_div(numerator: int, denominator: int) -> int:
    return -((-numerator) // denominator)


def verify_intervals() -> list[dict[str, object]]:
    rows = []
    for (left, right), expected in EXPECTED_INTERVALS:
        lower = ceil_div(32 - left - right, 2)
        upper = (left + right - 14) // 2
        demand((lower, upper) == expected, f"interval drift for {(left, right)}")
        classified = []
        for difference_norm in (14, 16, 18, 20):
            numerator = left + right - difference_norm
            if numerator % 2:
                continue
            inner = numerator // 2
            if lower <= inner <= upper:
                classified.append(
                    {
                        "difference_norm": difference_norm,
                        "inner_product": inner,
                        "verified_imported_magnitude_profile":
                            f"{difference_norm // 2}+ and "
                            f"{difference_norm // 2}- unit coordinates",
                        "opposite_sign_overlap": 0,
                    }
                )
        rows.append(
            {
                "norm_pair": [left, right],
                "integer_inner_product_interval": [lower, upper],
                "sum_bound_used": 32,
                "nonzero_difference_minimum_used": 14,
                "classified_difference_rows": classified,
            }
        )
    return rows


def normalize_records(raw: dict[str, object]) -> list[list[frozenset[int]]]:
    demand(raw["block_sizes"] == list(BLOCK_SIZES), "block-size drift")
    records = raw["records"]
    demand(isinstance(records, list) and len(records) == 40, "record-count drift")
    normalized = []
    seen_records = set()
    for record in records:
        demand(isinstance(record, list) and len(record) == 6, "record-width drift")
        blocks = []
        canonical = []
        for selection, size in zip(record, BLOCK_SIZES):
            demand(
                isinstance(selection, list)
                and len(selection) == 2
                and len(set(selection)) == 2,
                "each block must select two distinct coordinates",
            )
            demand(
                all(isinstance(index, int) and 0 <= index < size for index in selection),
                "block coordinate out of range",
            )
            block = frozenset(selection)
            blocks.append(block)
            canonical.append(tuple(sorted(block)))
        key = tuple(canonical)
        demand(key not in seen_records, "duplicate witness record")
        seen_records.add(key)
        normalized.append(blocks)
    return normalized


def signed_record(blocks: list[frozenset[int]]) -> dict[tuple[object, ...], int]:
    vector = {
        ("anchor", "P1"): 1,
        ("anchor", "P2"): 1,
        ("anchor", "N1"): -1,
        ("anchor", "N2"): -1,
    }
    for block_index, (selection, sign) in enumerate(zip(blocks, BLOCK_SIGNS)):
        for coordinate in selection:
            vector[("outside", block_index, coordinate)] = sign
    return vector


def vector_inner(
    left: dict[tuple[object, ...], int],
    right: dict[tuple[object, ...], int],
) -> int:
    return sum(value * right.get(coordinate, 0) for coordinate, value in left.items())


def vector_combination_norm(
    left: dict[tuple[object, ...], int],
    right: dict[tuple[object, ...], int],
    right_scale: int,
) -> tuple[int, Counter[int]]:
    values = {
        coordinate: left.get(coordinate, 0) + right_scale * right.get(coordinate, 0)
        for coordinate in set(left) | set(right)
    }
    nonzero = Counter(value for value in values.values() if value)
    return sum(value * value for value in values.values()), nonzero


def anchor_equations(vector: dict[tuple[object, ...], int]) -> dict[str, int]:
    cycle_contribution = {"P1": -2, "P2": -2, "N1": 2, "N2": 2}
    outside_blocks = {"P1": 3, "P2": 4, "N1": 0, "N2": 1}
    rows = {}
    for anchor in ("P1", "P2", "N1", "N2"):
        block = outside_blocks[anchor]
        outside = sum(
            value
            for coordinate, value in vector.items()
            if coordinate[0] == "outside" and coordinate[1] == block
        )
        neighbour_sum = cycle_contribution[anchor] + outside
        demand(
            neighbour_sum == -4 * vector[("anchor", anchor)],
            f"anchor equation failed at {anchor}",
        )
        rows[anchor] = neighbour_sum
    return rows


def bareiss_leading_determinants(matrix: list[list[int]]) -> list[int]:
    """Return all leading principal determinants by fraction-free elimination."""
    n = len(matrix)
    demand(n and all(len(row) == n for row in matrix), "matrix is not square")
    work = [row[:] for row in matrix]
    previous = 1
    determinants = []
    for pivot_index in range(n - 1):
        pivot = work[pivot_index][pivot_index]
        demand(pivot != 0, "zero leading pivot")
        determinants.append(pivot)
        for row in range(pivot_index + 1, n):
            for column in range(pivot_index + 1, n):
                numerator = (
                    work[row][column] * pivot
                    - work[row][pivot_index] * work[pivot_index][column]
                )
                demand(
                    numerator % previous == 0,
                    "Bareiss exact-division failure",
                )
                work[row][column] = numerator // previous
        previous = pivot
    determinants.append(work[-1][-1])
    return determinants


def verify_witness() -> dict[str, object]:
    raw = json.loads((DISCOVERY / "witness.json").read_text(encoding="utf-8"))
    records = normalize_records(raw)
    vectors = [signed_record(record) for record in records]

    # The six pools use 91 outside vertices.  The remaining four verified
    # type-11 vertices are explicitly unused, giving ambient length 99.
    demand(sum(BLOCK_SIZES) == 91, "used outside partition drift")
    ambient_length = 4 + sum(BLOCK_SIZES) + 4
    demand(ambient_length == 99, "ambient length drift")

    type_counts = Counter()
    anchor_rows = []
    for vector in vectors:
        positives = {coordinate for coordinate, value in vector.items() if value == 1}
        negatives = {coordinate for coordinate, value in vector.items() if value == -1}
        demand(len(positives) == len(negatives) == 8, "norm16 balance drift")
        demand(not (positives & negatives), "record sign collision")
        demand(sum(value * value for value in vector.values()) == 16, "norm drift")
        anchor_rows.append(anchor_equations(vector))
        for block_index in range(6):
            count = sum(
                coordinate[0] == "outside" and coordinate[1] == block_index
                for coordinate in vector
            )
            demand(count == 2, "fixed-C4 type count drift")
            type_counts[(block_index, count)] += 1

    overlap_histogram: Counter[int] = Counter()
    difference_histogram: Counter[int] = Counter()
    inner_histogram: Counter[int] = Counter()
    pair_data: dict[tuple[int, int], tuple[int, int, int]] = {}
    minimum_binary_distance = 99
    maximum_opposite_overlap = 0
    for left_index in range(40):
        for right_index in range(left_index):
            left_blocks = records[left_index]
            right_blocks = records[right_index]
            overlap = sum(
                len(left & right) for left, right in zip(left_blocks, right_blocks)
            )
            left = vectors[left_index]
            right = vectors[right_index]
            inner = vector_inner(left, right)
            difference_norm, difference_profile = vector_combination_norm(left, right, -1)
            sum_norm, _ = vector_combination_norm(left, right, 1)
            binary_distance = len(set(left) ^ set(right))
            opposite_overlap = sum(
                left[coordinate] == -right[coordinate]
                for coordinate in set(left) & set(right)
            )
            demand(inner == 4 + overlap, "pair inner-product drift")
            demand(difference_norm == 24 - 2 * overlap, "difference norm drift")
            demand(sum_norm == 40 + 2 * overlap, "sum norm drift")
            demand(binary_distance == difference_norm, "binary distance drift")
            demand(opposite_overlap == 0, "opposite-sign overlap found")
            demand(sum_norm >= 32 and difference_norm >= 14, "pair bound failure")
            if difference_norm <= 20:
                demand(
                    set(difference_profile) <= {-1, 1}
                    and difference_profile[1] == difference_norm // 2
                    and difference_profile[-1] == difference_norm // 2,
                    "classified difference profile failure",
                )
            overlap_histogram[overlap] += 1
            difference_histogram[difference_norm] += 1
            inner_histogram[inner] += 1
            minimum_binary_distance = min(minimum_binary_distance, binary_distance)
            maximum_opposite_overlap = max(maximum_opposite_overlap, opposite_overlap)
            pair_data[(left_index, right_index)] = (overlap, inner, difference_norm)

    demand(dict(sorted(overlap_histogram.items())) == EXPECTED_HISTOGRAM, "histogram drift")
    demand(sum(overlap_histogram.values()) == 780, "pair-count drift")
    demand(minimum_binary_distance == 14, "binary minimum-distance drift")

    gram = [[0 for _ in range(40)] for _ in range(40)]
    residual_scaled = [[0 for _ in range(40)] for _ in range(40)]
    for i in range(40):
        gram[i][i] = 16
        residual_scaled[i][i] = 52
        for j in range(i):
            overlap, inner, _ = pair_data[(i, j)]
            gram[i][j] = gram[j][i] = inner
            residual_scaled[i][j] = residual_scaled[j][i] = 5 * overlap - 8

    leading_determinants = bareiss_leading_determinants(residual_scaled)
    demand(len(leading_determinants) == 40, "leading-minor count drift")
    demand(all(value > 0 for value in leading_determinants), "residual Gram is not PD")

    # Sign consistency proves every positive-subset inequality at once:
    # for any selected subset, each outside coordinate has one fixed sign,
    # so sum m_v^2 >= sum m_v = 12r.
    outside_signs: dict[tuple[object, ...], set[int]] = {}
    for vector in vectors:
        for coordinate, sign in vector.items():
            if coordinate[0] == "outside":
                outside_signs.setdefault(coordinate, set()).add(sign)
    demand(all(len(signs) == 1 for signs in outside_signs.values()), "sign consistency failed")
    demand(
        all(
            sum(coordinate[0] == "outside" for coordinate in vector) == 12
            for vector in vectors
        ),
        "outside weight drift",
    )

    full_sum: Counter[tuple[object, ...]] = Counter()
    for vector in vectors:
        full_sum.update(vector)
    full_family_norm = sum(value * value for value in full_sum.values())
    total_pair_inner = sum(
        inner * count for inner, count in inner_histogram.items()
    )
    demand(total_pair_inner == 4598, "total pair inner-product drift")
    demand(full_family_norm == 40 * 16 + 2 * total_pair_inner == 9836, "full sum drift")
    demand(full_family_norm >= 4 * 40 * 40 + 8 * 40, "full subset bound failure")

    normalized_inner_products = [
        fraction_text(Q(5 * overlap - 8, 52)) for overlap in range(6)
    ]
    return {
        "witness_sha256": sha256_file(DISCOVERY / "witness.json"),
        "record_count": 40,
        "records_distinct": True,
        "ambient_binary_length": ambient_length,
        "unused_type11_coordinates": 4,
        "individual_profile": {
            "positive_units": 8,
            "negative_units": 8,
            "squared_norm": 16,
            "binary_weight": 16,
        },
        "fixed_C4_type_counts_per_record": {
            "positive_N1_only": 2,
            "positive_N2_only": 2,
            "positive_neither": 2,
            "negative_P1_only": 2,
            "negative_P2_only": 2,
            "negative_neither": 2,
            "type11": 0,
        },
        "all_four_anchor_equations_checked_per_record": True,
        "anchor_equation_rows": anchor_rows[0],
        "outside_eigen_equations_checked": False,
        "one_common_adjacency_matrix_encoded": False,
        "overlap_histogram": {
            str(key): overlap_histogram[key] for key in sorted(overlap_histogram)
        },
        "inner_product_histogram": {
            str(key): inner_histogram[key] for key in sorted(inner_histogram)
        },
        "difference_norm_histogram": {
            str(key): difference_histogram[key]
            for key in sorted(difference_histogram)
        },
        "opposite_sign_overlap_maximum": maximum_opposite_overlap,
        "classified_difference_profiles_checked": True,
        "binary_minimum_distance": minimum_binary_distance,
        "positive_subset_inequality": {
            "all_outside_coordinate_signs_family_consistent": True,
            "outside_L1_with_multiplicity": "12*r",
            "formal_support_squared_norm_lower": "4*r^2+12*r",
            "required_anchor_lower": "4*r^2+8*r",
            "proof_applies_to_every_positive_subset": True,
        },
        "full_family": {
            "total_pair_inner_product": total_pair_inner,
            "squared_norm": full_family_norm,
            "anchor_lower": 6720,
        },
        "residual_gram": {
            "construction": "5R has diagonal 52 and off-diagonal 5q-8",
            "size": 40,
            "rank": 40,
            "positive_definite_by_sylvester": True,
            "all_leading_principal_determinants_positive": True,
            "leading_principal_determinants": [
                str(value) for value in leading_determinants
            ],
            "scaled_matrix_sha256": sha256_json(residual_scaled),
            "normalized_inner_products": normalized_inner_products,
        },
    }


def compare_discovery(
    projector: dict[str, object],
    anchor: dict[str, object],
    intervals: list[dict[str, object]],
    witness: dict[str, object],
) -> dict[str, object]:
    archived = json.loads(
        (DISCOVERY / "exact-results.json").read_text(encoding="utf-8")
    )
    archived_rows = archived["pairwise_inner_products"]["rows"]
    checks = {
        "real_minimum_112_over_5": (
            projector["doubled_alternating_real_minimum"]
            == archived["projector_affine_slice"][
                "doubled_alternating_minimum_squared_norm"
            ]
        ),
        "integer_lower_32": (
            anchor["r2_squared_norm_lower"]
            == archived["integer_anchor_sharpening"]["universal_squared_norm_lower"]
        ),
        "general_r_bound": (
            anchor["general_squared_norm_lower"]
            == archived["integer_anchor_sharpening"]["positive_r_fold_sum_lower"]
        ),
        "six_interval_rows": (
            [row["integer_inner_product_interval"] for row in intervals]
            == [row["inner_product_interval"] for row in archived_rows]
        ),
        "witness_overlap_histogram": (
            witness["overlap_histogram"]
            == archived["formal_pairwise_witness"]["overlap_histogram"]
        ),
        "witness_binary_distance": (
            witness["binary_minimum_distance"]
            == archived["formal_pairwise_witness"]["binary_support_minimum_distance"]
        ),
        "witness_residual_rank": (
            witness["residual_gram"]["rank"]
            == archived["formal_pairwise_witness"]["residual_gram_rank"]
        ),
        "caps_and_ranks_remain_unproved": (
            not archived["status"]["local_cap25_proved"]
            and not archived["status"]["local_cap24_proved"]
            and not archived["status"]["rank28_excluded"]
            and not archived["status"]["rank30_excluded"]
        ),
    }
    demand(all(checks.values()), "independent/discovery comparison mismatch")
    return {
        "all_selected_claims_match": True,
        "checks": checks,
        "discovery_stale_text_clarification": (
            "Wave120 called Wave96 norm20 verification pending; the sealed "
            "Wave96 verifier package now verifies it conditional on its "
            "frozen inputs."
        ),
    }


def independent_results() -> dict[str, object]:
    provenance = authenticate_inputs()
    projector = verify_projector()
    anchor = verify_anchor_bound()
    intervals = verify_intervals()
    witness = verify_witness()
    comparison = compare_discovery(projector, anchor, intervals, witness)
    return {
        "format": "wave120-independent-verification-v1",
        "verdict": "VERIFIED_WITH_CLARIFICATION",
        "provenance": provenance,
        "projector": projector,
        "integer_anchor_bound": anchor,
        "pairwise_intervals": intervals,
        "formal_witness": witness,
        "comparison": comparison,
        "evidence_boundary": {
            "witness_is_formal_relaxation_only": True,
            "witness_is_integer_eigenvector_family": False,
            "outside_eigen_equations_encoded": False,
            "one_common_graph_adjacency_encoded": False,
            "target_kernel_code_membership_encoded": False,
            "abstract_residual_realization_preserves_integer_coordinates": False,
            "pairwise_Gram_and_binary_distance_route_refuted_below_40": True,
            "cap25": "UNKNOWN",
            "cap24": "UNKNOWN",
            "rank28": "UNKNOWN",
            "rank30": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "literature_novelty": "UNKNOWN",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", nargs="?", const=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    free = free_memory_percent()
    if free < 15.0:
        raise SystemExit(f"refusing to run with only {free:.1f}% free physical memory")
    result = independent_results()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.verify is not None:
        target = Path(args.verify)
        if not target.is_file() or target.read_text(encoding="utf-8") != encoded:
            raise SystemExit("canonical independent-results.json mismatch")
        print(f"PASS: Wave120 independently verified; {free:.1f}% RAM free")
    elif args.write is not None:
        args.write.write_text(encoded, encoding="utf-8")
        print(f"wrote {args.write}; {free:.1f}% RAM free")
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
