#!/usr/bin/env python3
"""Exact Wave 31 construction-side analysis of the T20 endpoint block.

This script enumerates the complete norm-four shell of the displayed T20
Gram matrix, freezes the exact 105-row endpoint equations, verifies an exact
rational second-moment relaxation witness, and exhausts a radius-two exchange
neighbourhood of one explicit integral near-frame.

The radius-two nonhit is deliberately restricted.  It is not a proof that a
105-row T20 frame, a projector/Schur package, or a Conway graph does not exist.
All certificate checks use Python integers or ``fractions.Fraction``.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "exact-results.json"

FROZEN_INPUTS = {
    "attempts/wave30-h729-construction/exact-results.json":
        "0d3723ba4c185dc7865858d16bfc6ada99fd87b4e21da616ef1b1d1ad6b67e11",
    "attempts/wave30-general-h729/exact-results.json":
        "cb0a58195506a51ca6a39aaab197a3592344f7aef8b5b0c2af51770c7069ad6c",
    "verification/wave24-n3-708-index/independent-results.json":
        "726807402388c02909171a689f3a7fe2d8d1b74307c24e322ae013d0a9cd486a",
    "verification/wave28-simultaneous-neighbor/independent_check.py":
        "2c8021769d47faebbcd544b364649a2cb93c066a369f76f725cffab1588982db",
}

ENUMERATOR_PATH = (
    REPO_ROOT / "verification" / "wave28-simultaneous-neighbor"
    / "independent_check.py"
)
CONSTRUCTION_PATH = (
    REPO_ROOT / "attempts" / "wave30-h729-construction"
    / "exact-results.json"
)
GENERAL_PATH = (
    REPO_ROOT / "attempts" / "wave30-general-h729"
    / "exact-results.json"
)
WAVE24_PATH = (
    REPO_ROOT / "verification" / "wave24-n3-708-index"
    / "independent-results.json"
)

# A deterministic basic feasible solution of the continuous line-selection
# relaxation has these 33 unit coordinates and 210 fractional coordinates.
# The weights themselves are reconstructed exactly by fraction-free
# elimination below, not imported from a floating-point solver.
RELAXATION_UNIT_INDICES = (
    2, 38, 49, 357, 363, 370, 605, 793, 795, 838, 868, 983, 1033,
    1334, 1336, 1337, 1338, 1339, 1377, 1549, 1693, 1789, 1878, 1883,
    1889, 1915, 1939, 1962, 1970, 2208, 2255, 2282, 2346,
)

RELAXATION_FRACTIONAL_INDICES = (
    6, 27, 44, 55, 59, 66, 67, 79, 87, 91, 93, 98, 109, 111, 131,
    137, 143, 149, 172, 188, 194, 209, 210, 218, 219, 256, 258, 259,
    265, 269, 297, 318, 344, 346, 350, 354, 362, 379, 387, 394, 397,
    413, 416, 417, 418, 422, 450, 456, 484, 486, 499, 526, 540, 556,
    586, 589, 608, 615, 626, 629, 678, 686, 689, 698, 725, 733, 736,
    749, 777, 787, 816, 824, 827, 835, 854, 856, 862, 863, 884, 891,
    905, 911, 913, 925, 927, 955, 960, 961, 968, 977, 986, 991, 994,
    997, 998, 1050, 1060, 1064, 1069, 1072, 1082, 1088, 1091, 1097,
    1100, 1138, 1154, 1405, 1455, 1456, 1507, 1522, 1525, 1530,
    1552, 1553, 1564, 1581, 1595, 1597, 1599, 1606, 1613, 1620,
    1623, 1626, 1654, 1655, 1685, 1691, 1717, 1724, 1730, 1738,
    1741, 1752, 1767, 1787, 1793, 1794, 1801, 1811, 1813, 1815,
    1817, 1825, 1826, 1837, 1857, 1864, 1866, 1874, 1879, 1904,
    1909, 1917, 1928, 1935, 1951, 1954, 1965, 1966, 1990, 2008,
    2033, 2047, 2061, 2064, 2065, 2071, 2082, 2088, 2109, 2113,
    2116, 2132, 2136, 2141, 2177, 2200, 2216, 2217, 2219, 2233,
    2241, 2251, 2259, 2262, 2265, 2266, 2270, 2278, 2281, 2290,
    2302, 2310, 2315, 2320, 2327, 2331, 2341, 2361, 2367, 2395,
    2408, 2409, 2413, 2419, 2450, 2521,
)

# This deterministic 105-line scout was obtained by exact-LP-guided local
# exchange descent.  It is not a frame: its Frobenius residual score is 121.
NEAR_FRAME_INDICES = (
    2412, 1928, 2021, 2108, 1970, 1692, 1773, 1827, 1455, 1438, 1407,
    1166, 510, 642, 778, 1060, 276, 214, 748, 1466, 1127, 1725, 1756,
    2283, 1178, 704, 1568, 2461, 2036, 1057, 1564, 1433, 1589, 455,
    1587, 2405, 1028, 2427, 2370, 471, 1246, 2200, 542, 1357, 1022,
    1255, 1791, 1952, 1582, 210, 467, 2234, 1991, 2306, 1059, 464,
    942, 499, 1094, 1072, 516, 2314, 711, 183, 2034, 726, 39, 219,
    1586, 508, 860, 331, 1124, 345, 1942, 2494, 24, 509, 1426, 1771,
    2477, 1315, 1002, 728, 802, 2282, 424, 1984, 1652, 74, 1949,
    1524, 2448, 770, 1738, 736, 370, 2194, 2191, 665, 1844, 1326,
    1836, 976, 2004,
)

MASK64 = (1 << 64) - 1


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load helper {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def validate_inputs() -> dict[str, str]:
    actual = {}
    for relative, expected in FROZEN_INPUTS.items():
        digest = sha256_file(REPO_ROOT / relative)
        if digest != expected:
            raise AssertionError(
                f"frozen input changed: {relative}: {digest} != {expected}"
            )
        actual[relative] = digest
    return actual


def matvec(
    matrix: Sequence[Sequence[int]], vector: Sequence[int]
) -> tuple[int, ...]:
    return tuple(
        sum(int(row[j]) * int(vector[j]) for j in range(len(vector)))
        for row in matrix
    )


def dot(left: Sequence[int], right: Sequence[int]) -> int:
    return sum(int(x) * int(y) for x, y in zip(left, right))


def upper_pairs(dimension: int) -> list[tuple[int, int]]:
    return [
        (i, j)
        for i in range(dimension)
        for j in range(i, dimension)
    ]


def outer_feature(
    vector: Sequence[int], pairs: Sequence[tuple[int, int]]
) -> tuple[int, ...]:
    return tuple(int(vector[i]) * int(vector[j]) for i, j in pairs)


def vector_add(
    left: Sequence[int], right: Sequence[int]
) -> tuple[int, ...]:
    return tuple(int(x) + int(y) for x, y in zip(left, right))


def vector_subtract(
    left: Sequence[int], right: Sequence[int]
) -> tuple[int, ...]:
    return tuple(int(x) - int(y) for x, y in zip(left, right))


def sum_features(
    features: Sequence[Sequence[int]], indices: Iterable[int]
) -> tuple[int, ...]:
    total = [0] * len(features[0])
    for index in indices:
        feature = features[int(index)]
        for position, value in enumerate(feature):
            total[position] += int(value)
    return tuple(total)


def gf2_augmented_rank(
    features: Sequence[Sequence[int]],
    target: Sequence[int],
) -> dict[str, int | bool]:
    variable_count = len(features)
    rows = []
    for equation in range(len(target)):
        bits = 0
        for variable, feature in enumerate(features):
            if int(feature[equation]) & 1:
                bits |= 1 << variable
        rows.append(bits | ((int(target[equation]) & 1) << variable_count))
    # The row-count condition is 105=1 modulo two.
    rows.append(((1 << variable_count) - 1) | (1 << variable_count))

    pivots: dict[int, int] = {}
    inconsistent = False
    for row in rows:
        coefficient_bits = row & ((1 << variable_count) - 1)
        while coefficient_bits:
            pivot = coefficient_bits.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
                coefficient_bits = row & ((1 << variable_count) - 1)
            else:
                pivots[pivot] = row
                break
        else:
            if (row >> variable_count) & 1:
                inconsistent = True
    return {
        "equations_including_row_count": len(rows),
        "rank": len(pivots),
        "dependencies": len(rows) - len(pivots),
        "inconsistent": inconsistent,
    }


def bareiss_solve(
    coefficients: Sequence[Sequence[int]], right_hand_side: Sequence[int]
) -> list[Fraction]:
    """Solve a nonsingular integer system by fraction-free elimination."""

    dimension = len(coefficients)
    if dimension == 0 or len(right_hand_side) != dimension:
        raise AssertionError("malformed exact system")
    augmented = [
        [int(value) for value in row] + [int(right_hand_side[i])]
        for i, row in enumerate(coefficients)
    ]
    if any(len(row) != dimension + 1 for row in augmented):
        raise AssertionError("exact system is not square")

    previous = 1
    for pivot_index in range(dimension - 1):
        if augmented[pivot_index][pivot_index] == 0:
            replacement = next(
                (
                    row
                    for row in range(pivot_index + 1, dimension)
                    if augmented[row][pivot_index] != 0
                ),
                None,
            )
            if replacement is None:
                raise AssertionError("singular exact relaxation basis")
            augmented[pivot_index], augmented[replacement] = (
                augmented[replacement],
                augmented[pivot_index],
            )
        pivot = augmented[pivot_index][pivot_index]
        for row in range(pivot_index + 1, dimension):
            leading = augmented[row][pivot_index]
            for column in range(pivot_index + 1, dimension + 1):
                numerator = (
                    augmented[row][column] * pivot
                    - leading * augmented[pivot_index][column]
                )
                quotient, remainder = divmod(numerator, previous)
                if remainder:
                    raise AssertionError("Bareiss exact division failed")
                augmented[row][column] = quotient
            augmented[row][pivot_index] = 0
        previous = pivot

    solution = [Fraction(0) for _ in range(dimension)]
    for row in range(dimension - 1, -1, -1):
        numerator = augmented[row][dimension] - sum(
            augmented[row][column] * solution[column]
            for column in range(row + 1, dimension)
        )
        solution[row] = Fraction(numerator, augmented[row][row])
    return solution


def exact_rational_relaxation(
    features: Sequence[Sequence[int]], target: Sequence[int]
) -> dict[str, Any]:
    unit = list(RELAXATION_UNIT_INDICES)
    fractional = list(RELAXATION_FRACTIONAL_INDICES)
    if len(unit) != 33 or len(fractional) != 210:
        raise AssertionError("relaxation support cardinalities drifted")
    if set(unit) & set(fractional):
        raise AssertionError("relaxation supports overlap")

    coefficients = [
        [int(features[index][equation]) for index in fractional]
        for equation in range(len(target))
    ]
    rhs = [
        int(target[equation])
        - sum(int(features[index][equation]) for index in unit)
        for equation in range(len(target))
    ]
    weights = bareiss_solve(coefficients, rhs)
    if not all(Fraction(0) < weight < Fraction(1) for weight in weights):
        raise AssertionError("relaxation basis weight left the open unit interval")
    if sum(weights, Fraction(len(unit))) != 105:
        raise AssertionError("relaxation weights do not sum to 105")

    reconstructed = [Fraction(0) for _ in target]
    for index in unit:
        for equation, value in enumerate(features[index]):
            reconstructed[equation] += int(value)
    for index, weight in zip(fractional, weights):
        for equation, value in enumerate(features[index]):
            reconstructed[equation] += weight * int(value)
    if reconstructed != [Fraction(value) for value in target]:
        raise AssertionError("rational relaxation certificate missed target")

    serialized_weights = [
        (
            str(weight.numerator)
            if weight.denominator == 1
            else f"{weight.numerator}/{weight.denominator}"
        )
        for weight in weights
    ]
    return {
        "status": "EXACT_RATIONAL_SECOND_MOMENT_RELAXATION_WITNESS",
        "meaning": (
            "The box relaxation 0<=lambda_l<=1, sum lambda_l=105, "
            "sum lambda_l*v_l*v_l^T=21*T20^-1 is nonempty. "
            "The weights are not Boolean and are not a frame."
        ),
        "unit_indices": unit,
        "fractional_indices": fractional,
        "fractional_weights": serialized_weights,
        "support_size": len(unit) + len(fractional),
        "unit_weight_count": len(unit),
        "fractional_weight_count": len(fractional),
        "minimum_fractional_weight": str(min(weights)),
        "maximum_fractional_weight": str(max(weights)),
        "weight_certificate_sha256": canonical_hash({
            "unit_indices": unit,
            "fractional_indices": fractional,
            "fractional_weights": serialized_weights,
        }),
    }


def splitmix64_coefficients(count: int) -> list[int]:
    state = 0x9E3779B97F4A7C15
    output = []
    for _ in range(count):
        state = (state + 0x9E3779B97F4A7C15) & MASK64
        value = state
        value = (
            ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
        )
        value = (
            ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK64
        )
        value ^= value >> 31
        output.append(value & MASK64)
    return output


def fingerprint(feature: Sequence[int], coefficients: Sequence[int]) -> int:
    return sum(
        (int(value) & MASK64) * coefficient
        for value, coefficient in zip(feature, coefficients)
    ) & MASK64


def radius_two_search(
    features: Sequence[Sequence[int]], target: Sequence[int]
) -> dict[str, Any]:
    selected = tuple(NEAR_FRAME_INDICES)
    if len(selected) != 105 or len(set(selected)) != 105:
        raise AssertionError("near-frame support is not 105 distinct lines")
    selected_set = set(selected)
    unselected = tuple(
        index for index in range(len(features)) if index not in selected_set
    )
    current = sum_features(features, selected)
    residual = vector_subtract(current, target)
    dimension = 20
    pairs = upper_pairs(dimension)
    score = sum(
        (1 if i == j else 2) * residual[position] ** 2
        for position, (i, j) in enumerate(pairs)
    )
    if score != 121:
        raise AssertionError(f"near-frame score drifted: {score}")
    if max(abs(value) for value in residual) != 2:
        raise AssertionError("near-frame maximum residual drifted")
    if sum(value != 0 for value in residual) != 63:
        raise AssertionError("near-frame residual support drifted")

    coefficients = splitmix64_coefficients(len(target))
    line_hashes = [
        fingerprint(feature, coefficients) for feature in features
    ]
    residual_hash = fingerprint(residual, coefficients)

    required_one: dict[int, list[int]] = defaultdict(list)
    for removed in selected:
        required_one[
            (line_hashes[removed] - residual_hash) & MASK64
        ].append(removed)
    radius_one_fingerprint_candidates = 0
    radius_one_exact_matches = []
    for added in unselected:
        removals = required_one.get(line_hashes[added], ())
        radius_one_fingerprint_candidates += len(removals)
        for removed in removals:
            if features[added] == vector_subtract(
                features[removed], residual
            ):
                radius_one_exact_matches.append([removed, added])

    required_two: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for left_position, left in enumerate(selected):
        for right in selected[left_position + 1:]:
            required_two[
                (
                    line_hashes[left] + line_hashes[right]
                    - residual_hash
                ) & MASK64
            ].append((left, right))

    radius_two_fingerprint_candidates = 0
    radius_two_exact_matches = []
    for left_position, left in enumerate(unselected):
        left_hash = line_hashes[left]
        for right in unselected[left_position + 1:]:
            removals = required_two.get(
                (left_hash + line_hashes[right]) & MASK64, ()
            )
            radius_two_fingerprint_candidates += len(removals)
            if not removals:
                continue
            added_sum = vector_add(features[left], features[right])
            for removed_left, removed_right in removals:
                required_sum = vector_subtract(
                    vector_add(
                        features[removed_left], features[removed_right]
                    ),
                    residual,
                )
                if added_sum == required_sum:
                    radius_two_exact_matches.append([
                        removed_left, removed_right, left, right
                    ])

    if radius_one_exact_matches or radius_two_exact_matches:
        raise AssertionError("stored near-frame neighbourhood now has a frame")
    if radius_two_fingerprint_candidates != 0:
        raise AssertionError(
            "radius-two fingerprint collision count changed; exact result "
            "is still checked, but the frozen certificate must be regenerated"
        )

    return {
        "near_frame_id": "W31-T20-NEAR-105-001",
        "near_frame_status": "NOT_A_FRAME",
        "canonical_line_indices": list(selected),
        "canonical_line_indices_sha256": canonical_hash(list(selected)),
        "moment_residual_upper_triangle": list(residual),
        "moment_residual_sha256": canonical_hash(list(residual)),
        "frobenius_residual_score": score,
        "nonzero_residual_entries_upper_triangle": 63,
        "maximum_absolute_residual_entry": 2,
        "restriction": (
            "Only selections obtained by replacing at most two of these "
            "105 canonical antipodal lines by the same number of the other "
            "2433 canonical lines are searched. Orientations, row sum, "
            "alphabet, Q, B, A4, the U block, and graphs are not searched "
            "because no exact second-moment selection occurs in this domain."
        ),
        "radius_zero_exact_matches": 0,
        "radius_one": {
            "removal_choices": len(selected),
            "addition_choices": len(unselected),
            "fingerprint_collision_candidates": (
                radius_one_fingerprint_candidates
            ),
            "exact_matches": radius_one_exact_matches,
        },
        "radius_two": {
            "removal_pair_count": len(selected) * (len(selected) - 1) // 2,
            "addition_pair_count": (
                len(unselected) * (len(unselected) - 1) // 2
            ),
            "fingerprint_collision_candidates": (
                radius_two_fingerprint_candidates
            ),
            "exact_matches": radius_two_exact_matches,
        },
        "fingerprint": {
            "ring": "Z/(2^64)",
            "definition": (
                "sum_e feature[e]*splitmix64_coefficient[e] modulo 2^64"
            ),
            "coefficient_seed": "0x9E3779B97F4A7C15",
            "coefficient_count": len(coefficients),
            "coefficient_sha256": canonical_hash(coefficients),
            "soundness": (
                "Exact equality of feature vectors implies fingerprint "
                "equality. Every matching fingerprint is checked entrywise; "
                "therefore collisions can add work but cannot hide a match."
            ),
        },
        "verdict": (
            "NO_EXACT_SECOND_MOMENT_SELECTION_WITHIN_TWO_EXCHANGES_OF_"
            "W31_T20_NEAR_105_001"
        ),
        "global_second_moment_frame": "UNKNOWN",
    }


def build_result() -> dict[str, Any]:
    frozen = validate_inputs()
    enumerator = load_module("wave31_t20_enumerator", ENUMERATOR_PATH)
    construction = json.loads(CONSTRUCTION_PATH.read_text(encoding="utf-8"))
    general = json.loads(GENERAL_PATH.read_text(encoding="utf-8"))
    wave24 = json.loads(WAVE24_PATH.read_text(encoding="utf-8"))

    t20_data = construction["rank20_construction"]["T20"]
    t20 = [[int(value) for value in row] for row in t20_data["gram"]]
    target_g = [
        [int(value) for value in row]
        for row in t20_data["scaled_dual_21_T20_inverse"]
    ]
    if t20_data["gram_sha256"] != (
        "1890fe1973eed47850c307d0975ae393f2a8ab32a9d0b16b35ebcab7012445d6"
    ):
        raise AssertionError("T20 Gram hash drifted")
    if len(t20) != 20 or any(len(row) != 20 for row in t20):
        raise AssertionError("T20 dimension drifted")

    vectors_with_norm, enumeration_stats = enumerator.enumerate_vectors(
        [[Fraction(value) for value in row] for row in t20], 4
    )
    norm_counts = Counter(int(norm) for _vector, norm in vectors_with_norm)
    if norm_counts != Counter({4: 5076, 0: 1}):
        raise AssertionError(f"T20 shell drifted: {norm_counts}")
    norm_four_vectors = [
        tuple(int(value) for value in vector)
        for vector, norm in vectors_with_norm
        if int(norm) == 4
    ]
    canonical_lines = [
        vector
        for vector in norm_four_vectors
        if next(value for value in vector if value) > 0
    ]
    if len(canonical_lines) != 2538:
        raise AssertionError("canonical antipodal line count drifted")
    canonical_line_set = set(canonical_lines)
    if any(
        tuple(-x for x in vector) in canonical_line_set
        for vector in canonical_lines
    ):
        raise AssertionError("both orientations entered canonical line list")

    pairs = upper_pairs(20)
    features = [outer_feature(vector, pairs) for vector in canonical_lines]
    target_upper = tuple(target_g[i][j] for i, j in pairs)

    transformed = [matvec(t20, vector) for vector in canonical_lines]
    signed_inner_counts: Counter[int] = Counter()
    degree_abs_two = [0] * len(canonical_lines)
    for left, transformed_left in enumerate(transformed):
        for right in range(left + 1, len(canonical_lines)):
            inner = dot(transformed_left, canonical_lines[right])
            signed_inner_counts[inner] += 1
            if abs(inner) == 2:
                degree_abs_two[left] += 1
                degree_abs_two[right] += 1
    expected_inner_counts = Counter({
        -2: 80883,
        -1: 671126,
        0: 1382670,
        1: 923008,
        2: 161766,
    })
    if signed_inner_counts != expected_inner_counts:
        raise AssertionError(
            f"canonical-line inner products drifted: {signed_inner_counts}"
        )
    degree_distribution = Counter(degree_abs_two)
    expected_degrees = Counter({
        160: 108,
        178: 840,
        196: 1242,
        214: 330,
        232: 15,
        322: 3,
    })
    if degree_distribution != expected_degrees:
        raise AssertionError(
            f"absolute-two degree distribution drifted: {degree_distribution}"
        )

    mod_two = {tuple(value % 2 for value in line) for line in canonical_lines}
    mod_three = {
        tuple(value % 3 for value in line) for line in canonical_lines
    }
    if len(mod_two) != 2538 or len(mod_three) != 2538:
        raise AssertionError("canonical lines are no longer residue-unique")

    coordinate_height_distribution = Counter(
        max(abs(value) for value in line) for line in canonical_lines
    )
    if coordinate_height_distribution != Counter({
        1: 1196, 2: 1019, 3: 278, 4: 36, 5: 9,
    }):
        raise AssertionError("coordinate-height distribution drifted")

    relaxation = exact_rational_relaxation(features, target_upper)
    neighbourhood = radius_two_search(features, target_upper)
    parity = gf2_augmented_rank(features, target_upper)
    if parity != {
        "equations_including_row_count": 211,
        "rank": 210,
        "dependencies": 1,
        "inconsistent": False,
    }:
        raise AssertionError(f"GF(2) relaxation drifted: {parity}")

    # B_U=I and Q_U=U^-1 imply, with A4_U=M_U W_U M_U,
    #
    # A4_U = X_U U (X_U^T W_U X_U) U X_U^T
    #      = X_U U Q_U U X_U^T
    #      = X_U U X_U^T = M_U.
    #
    # Therefore every U diagonal is four.  Wave 24 supplies 84 global
    # diagonal excess units at n3=708, so all 84 lie on the A/T20 block.
    endpoint = wave24["endpoint_reconstruction"]
    if endpoint["diagonal_excess_units"] != 84:
        raise AssertionError("Wave 24 diagonal excess changed")
    survivor = general["surviving_boundary"]
    if not survivor["schur_blocks"]["U"]["B_equals_identity"]:
        raise AssertionError("Wave 30 no longer forces B_U=I")
    if survivor["frame"] != {"A_rows": 105, "U_rows": 126, "total_rows": 231}:
        raise AssertionError("Wave 30 frame split changed")

    row_profiles = []
    for c_value in range(13):
        row_profiles.append({
            "c_minus_two": c_value,
            "a_plus_one": 32 - c_value,
            "b_minus_one": 36 - 3 * c_value,
            "zero_within_A_block": 36 + 3 * c_value,
            "zero_in_full_231_row": 162 + 3 * c_value,
            "q_actual_graph_notation": 12 - c_value,
            "cubic_row_sum": 60 - 6 * c_value,
        })

    restrictions = {
        "no_target_automorphism_assumed": True,
        "canonical_line_orientation": (
            "first nonzero coordinate positive; used only to name each "
            "antipodal line"
        ),
        "full_shell_enumerated": True,
        "integer_solver_search_complete": False,
        "radius_two_exchange_search_complete": True,
        "rootless_integrally_decomposable_T20_plus_U24_ansatz": True,
        "rooted_or_integrally_indecomposable_forms": "OUT_OF_SCOPE",
        "U24_matrix_chosen_in_this_lane": False,
        "graph_gap_imposed_on_matrix_search": False,
    }

    return {
        "schema": "wave31-t20-frame-construction-v1",
        "role": "construction",
        "claim_label": "UNKNOWN",
        "frozen_inputs": frozen,
        "scope": (
            "Complete T20 norm-four shell and exact necessary equations for "
            "the 105-row block; exact rational relaxation witness; complete "
            "radius-two exchange search around one explicit near-frame. "
            "No unrestricted integer frame or obstruction is obtained."
        ),
        "T20": {
            "rank": 20,
            "determinant": 729,
            "minimum": 4,
            "gram_sha256": t20_data["gram_sha256"],
            "scaled_dual_21_inverse_sha256":
                t20_data["scaled_dual_gram_sha256"],
            "norm_four_vector_count": len(norm_four_vectors),
            "antipodal_line_count": len(canonical_lines),
            "canonical_lines": [list(line) for line in canonical_lines],
            "canonical_lines_sha256": canonical_hash(
                [list(line) for line in canonical_lines]
            ),
            "shell_enumeration": enumeration_stats,
            "coordinate_height_distribution": {
                str(key): coordinate_height_distribution[key]
                for key in sorted(coordinate_height_distribution)
            },
            "distinct_residue_classes_mod_2": len(mod_two),
            "distinct_residue_classes_mod_3": len(mod_three),
        },
        "line_pair_geometry": {
            "unordered_pair_count":
                len(canonical_lines) * (len(canonical_lines) - 1) // 2,
            "signed_inner_product_counts": {
                str(key): signed_inner_counts[key]
                for key in sorted(signed_inner_counts)
            },
            "absolute_inner_product_counts": {
                "0": signed_inner_counts[0],
                "1": signed_inner_counts[-1] + signed_inner_counts[1],
                "2": signed_inner_counts[-2] + signed_inner_counts[2],
            },
            "absolute_two_graph_edges":
                signed_inner_counts[-2] + signed_inner_counts[2],
            "absolute_two_degree_distribution": {
                str(key): degree_distribution[key]
                for key in sorted(degree_distribution)
            },
            "alphabet_consequence": (
                "No distinct antipodal lines have absolute inner product "
                "above two. For canonical inner product +2 the selected "
                "orientations must have opposite signs; for -2 they must "
                "have equal signs. Inner products 0 and +/-1 need no sign "
                "restriction."
            ),
        },
        "exact_105_row_problem": {
            "line_selection_variables": 2538,
            "required_selected_lines": 105,
            "second_moment_equations": 210,
            "second_moment_identity": "sum_l z_l v_l v_l^T=21*T20^-1",
            "selection_domain": "z_l in {0,1}",
            "orientation_domain": "epsilon_l in {-1,+1} when z_l=1",
            "zero_sum_identity": "sum_l z_l epsilon_l v_l=0",
            "off_diagonal_alphabet": [0, 1, -1, -2],
            "GF2_relaxation": parity,
            "cap_one_coordinate_restriction": {
                "domain": (
                    "all 105 rows are restricted to canonical lines with "
                    "maximum absolute coordinate at most one"
                ),
                "available_lines": coordinate_height_distribution[1],
                "obstruction": (
                    "coordinate 1 (zero-based) has target diagonal 266, "
                    "but 105 selected rows with entries in {-1,0,1} "
                    "contribute at most 105"
                ),
                "status": "EXCLUDED_ONLY_IN_THIS_RESTRICTED_DOMAIN",
            },
            "rational_relaxation": relaxation,
            "bounded_integer_neighbourhood": neighbourhood,
        },
        "full_T20_block_constraints_after_a_frame": {
            "M_A": "X_A*T20*X_A^T",
            "W_A": "M_A o M_A",
            "Q_A": "X_A^T*W_A*X_A",
            "Q_A_requirements": {
                "even_integral_positive_definite": True,
                "determinant": 5,
            },
            "B_A": "T20*Q_A=I_20+2*C_A",
            "B_A_requirements": {
                "trace": 36,
                "determinant": 3645,
                "integral_and_G_self_adjoint_positive": True,
            },
            "A4_A": "M_A*W_A*M_A",
            "row_alphabet_table": row_profiles,
            "aggregate_directed_internal_counts": {
                "plus_one": 2316,
                "minus_one": 648,
                "minus_two": 1044,
                "zero": 6912,
                "sum_c_minus_two": 1044,
                "sum_q_actual_graph_notation": 216,
            },
            "A4_diagonal": {
                "form": "(A4_A)[i,i]=4*(1+e_i), e_i nonnegative integer",
                "excess_units_on_A_block": 84,
                "trace_A4_A": 756,
            },
            "status": (
                "NOT_EVALUATED: no exact Boolean second-moment selection was "
                "found in the unrestricted scouts or the complete radius-two "
                "domain"
            ),
        },
        "coupling_to_U_block": {
            "derivation": [
                "B_U=I_24 implies Q_U=U^-1.",
                "A4_U=M_U*(M_U o M_U)*M_U.",
                "Substituting M_U=X_U U X_U^T and Q_U=X_U^T*(M_U o M_U)*X_U gives A4_U=M_U.",
                "diag(M_U)=4, so all 126 U rows have zero A4 diagonal excess.",
                "The 84 global n3=708 excess units therefore all lie on the 105-row A/T20 block.",
            ],
            "matrix_level_U_profiles": (
                "c in {9,10,11}, n9=n11+4, n10=122-2*n11"
            ),
            "actual_graph_only_sharpening": {
                "extra_input": "q=0 or q>=2, where q=12-c",
                "U_profile": {"c9": 4, "c10": 122, "c11": 0},
                "not_imposed_on_matrix_search": True,
            },
        },
        "solver_scout_summary": {
            "status": "ALL_NONCERTIFYING",
            "details": "See failure-ledger.md.",
            "unrestricted_second_moment_witness": "NOT_FOUND",
            "unrestricted_second_moment_nonexistence": "NOT_PROVED",
            "unrestricted_oriented_frame": "NOT_FOUND_OR_EXCLUDED",
        },
        "restrictions": restrictions,
        "status": {
            "T20_shell": "EXACT_COMPLETE_ENUMERATION",
            "rational_second_moment_relaxation": "EXACT_WITNESS",
            "radius_two_near_frame_domain": "EXACT_RESTRICTED_NONHIT",
            "global_105_row_second_moment_frame": "UNKNOWN",
            "oriented_zero_sum_alphabet_frame": "UNKNOWN",
            "Q_A_B_A_A4_A_package": "UNKNOWN",
            "coupled_T20_U24_projector_Schur_package": "UNKNOWN",
            "n3_equals_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "runtime": {
            "implementation": platform.python_implementation(),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "replay_dependencies": "Python standard library plus frozen exact enumerator",
        },
    }


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(
        json.dumps(
            value, indent=2, sort_keys=True, ensure_ascii=True
        ).encode("utf-8") + b"\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = build_result()
    write_json(args.output, result)
    print(
        json.dumps({
            "status": result["status"],
            "canonical_lines_sha256":
                result["T20"]["canonical_lines_sha256"],
            "rational_weight_certificate_sha256":
                result["exact_105_row_problem"]["rational_relaxation"][
                    "weight_certificate_sha256"
                ],
            "radius_two_verdict":
                result["exact_105_row_problem"][
                    "bounded_integer_neighbourhood"
                ]["verdict"],
        }, sort_keys=True)
    )


if __name__ == "__main__":
    main()
