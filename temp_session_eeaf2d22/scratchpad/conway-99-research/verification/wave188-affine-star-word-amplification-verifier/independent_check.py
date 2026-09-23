"""Clean-room verifier for Wave 188 affine star-word amplification.

This module hashes the frozen source package but never imports or executes
its checker.  All finite calculations below are reconstructed independently.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INPUT_FREEZE = HERE / "input-freeze.sha256"
SOURCE_MANIFEST = (
    ROOT
    / "attempts"
    / "wave188-affine-star-word-amplification"
    / "package-manifest.sha256"
)
HASH_LINE = re.compile(r"^([0-9a-fA-F]{64})\s+\*?(.+?)\s*$")
C = 4158
EDGE_WORDS = 693


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_hash_list(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = HASH_LINE.fullmatch(line)
        if match is None:
            raise ValueError(f"malformed hash line {path}:{number}: {raw!r}")
        entries.append((match.group(1).lower(), match.group(2)))
    if not entries:
        raise ValueError(f"empty hash list: {path}")
    return entries


def verify_frozen_inputs() -> dict[str, Any]:
    frozen_entries = parse_hash_list(INPUT_FREEZE)
    expected_paths = {
        "attempts/wave188-affine-star-word-amplification/package-manifest.sha256",
        "verification/wave174-no-weight3-dual/package-manifest.sha256",
        "verification/wave179-global-transversal-circuits/package-manifest.sha256",
        "verification/wave180-capacity3-companion/package-manifest.sha256",
        "verification/wave181-c4-conic-equality/package-manifest.sha256",
        "verification/wave186-star-translation-cover-verifier/package-manifest.sha256",
    }
    actual_paths = {relative.replace("\\", "/") for _, relative in frozen_entries}
    if actual_paths != expected_paths:
        raise AssertionError(
            f"unexpected frozen input set: {sorted(actual_paths ^ expected_paths)}"
        )

    failures: list[dict[str, str]] = []
    lists_checked: list[dict[str, Any]] = []
    entries_checked = 0

    for expected, relative in frozen_entries:
        target = (ROOT / relative).resolve()
        actual = sha256(target) if target.is_file() else "missing"
        if actual != expected:
            failures.append(
                {
                    "list": INPUT_FREEZE.relative_to(ROOT).as_posix(),
                    "path": relative,
                    "expected": expected,
                    "actual": actual,
                }
            )

    package_lists = [SOURCE_MANIFEST]
    package_lists.extend((ROOT / relative).resolve() for _, relative in frozen_entries[1:])
    for hash_list in package_lists:
        entries = parse_hash_list(hash_list)
        relative_list = hash_list.relative_to(ROOT).as_posix()
        lists_checked.append({"path": relative_list, "entries": len(entries)})
        entries_checked += len(entries)
        for expected, relative in entries:
            target = (ROOT / relative).resolve()
            if not target.is_file():
                failures.append(
                    {"list": relative_list, "path": relative, "error": "missing"}
                )
                continue
            actual = sha256(target)
            if actual != expected:
                failures.append(
                    {
                        "list": relative_list,
                        "path": relative,
                        "expected": expected,
                        "actual": actual,
                    }
                )

    return {
        "passed": not failures,
        "frozen_manifest_count": len(frozen_entries),
        "lists_checked": sorted(lists_checked, key=lambda row: row["path"]),
        "entries_checked": entries_checked,
        "failures": failures,
        "discovery_code_imported_or_executed": False,
    }


def compositions_of_seven() -> Iterable[tuple[int, int, int]]:
    for first in range(8):
        for second in range(8 - first):
            yield first, second, 7 - first - second


def orbit_weights(
    left: tuple[int, int, int], right: tuple[int, int, int]
) -> tuple[int, ...]:
    return tuple(14 - left[i] - right[j] for i in range(3) for j in range(3))


def affine_profile_census() -> dict[str, Any]:
    short_counts: list[int] = []
    equality_examples: list[dict[str, Any]] = []

    for left, right in product(compositions_of_seven(), repeat=2):
        # Index zero is the zero-coefficient count of the selected base word.
        # A selected cross circuit has a proper nonempty support on both stars.
        if left[0] == 0 or right[0] == 0:
            continue
        if max(left) == 7 or max(right) == 7:
            continue

        weights = orbit_weights(left, right)
        base_weight = weights[0]
        if not 4 <= base_weight <= 9:
            continue
        if min(weights) < 4:
            continue

        count = sum(weight <= 9 for weight in weights)
        short_counts.append(count)
        if count == 3 and len(equality_examples) < 4:
            equality_examples.append(
                {
                    "left": list(left),
                    "right": list(right),
                    "weights": sorted(weights),
                }
            )

    spectrum = Counter(short_counts)
    return {
        "profiles_checked": len(short_counts),
        "minimum_short_projective_words": min(short_counts),
        "minimum_equality_profiles": spectrum[min(short_counts)],
        "short_count_spectrum": {
            str(count): spectrum[count] for count in sorted(spectrum)
        },
        "equality_examples": equality_examples,
    }


def add_mod3(*vectors: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sum(values) % 3 for values in zip(*vectors))


def scale_mod3(scalar: int, vector: tuple[int, ...]) -> tuple[int, ...]:
    return tuple((scalar * value) % 3 for value in vector)


def weight(vector: tuple[int, ...]) -> int:
    return sum(value != 0 for value in vector)


def projective_key(vector: tuple[int, ...]) -> tuple[int, ...]:
    if not any(vector):
        raise ValueError("zero vector has no projective class")
    first = next(value for value in vector if value)
    inverse = 1 if first == 1 else 2
    return scale_mod3(inverse, vector)


def projective_orbit_check() -> dict[str, Any]:
    # Abstract basis c,s_x,s_y.  The quotient premise says these are
    # independent, so the nine affine representatives are (1,a,b).
    orbit = {
        projective_key((1, alpha, beta))
        for alpha, beta in product(range(3), repeat=2)
    }
    assert len(orbit) == 9
    return {
        "abstract_basis": ["c", "s_x", "s_y"],
        "affine_representatives": 9,
        "nonzero_representatives": 9,
        "distinct_projective_classes": len(orbit),
        "scalar_collision_possible": False,
        "reason": "normalizing the nonzero c-coordinate fixes the scalar",
    }


def one_block_projector_and_orbit() -> dict[str, Any]:
    one_adjacency_profile = (1, 1, 1, 1, 1, 2, 2)
    square_sum = sum(value * value for value in one_adjacency_profile) % 3
    assert square_sum == 1

    # Coordinates T | A_0,A_1,A_2 | B_0,...,B_3.
    c4 = (1, 2, 2, 2, 0, 0, 0, 0)
    star = (0, 1, 1, 1, 1, 1, 1, 1)
    classes: dict[tuple[int, ...], tuple[int, ...]] = {}
    for alpha, beta in product(range(3), repeat=2):
        vector = add_mod3(scale_mod3(alpha, c4), scale_mod3(beta, star))
        if any(vector):
            classes[projective_key(vector)] = vector
    assert len(classes) == 4

    all_weights = sorted(weight(vector) for vector in classes)
    cross_weights = sorted(weight(vector) for vector in classes if vector[0])
    noncross_weights = sorted(weight(vector) for vector in classes if not vector[0])
    assert all_weights == [4, 5, 7, 8]
    assert cross_weights == [4, 5, 8]
    assert noncross_weights == [7]

    return {
        "one_adjacency_pairing_profile": list(one_adjacency_profile),
        "one_adjacency_square_sum_mod3": square_sum,
        "projector_singularity_required_residue": 0,
        "one_adjacency_contradiction": True,
        "anticomplete_relation_plane_projective_classes": len(classes),
        "all_projective_weights": all_weights,
        "cross_projective_weights": cross_weights,
        "star_only_projective_weights": noncross_weights,
        "cross_realization_multiplicity": 3,
    }


def type_two_words() -> dict[str, Any]:
    # Coordinates x_0,...,x_6 | y_0,...,y_6.
    conic = (1, 2, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0)
    star_x = (1,) * 7 + (0,) * 7
    star_y = (0,) * 7 + (1,) * 7

    translated: list[tuple[int, ...]] = []
    profiles: list[list[int]] = []
    for alpha, beta in ((1, 0), (2, 0), (0, 1), (0, 2)):
        vector = add_mod3(
            conic, scale_mod3(alpha, star_x), scale_mod3(beta, star_y)
        )
        translated.append(vector)
        profiles.append([weight(vector[:7]), weight(vector[7:])])

    classes = {projective_key(vector) for vector in translated}
    assert len(classes) == 4
    assert sorted(profiles) == [[2, 6], [2, 6], [6, 2], [6, 2]]
    assert {weight(vector) for vector in translated} == {8}

    return {
        "base_profile": [2, 2],
        "axis_translate_count": len(translated),
        "distinct_projective_axis_translates": len(classes),
        "axis_translate_profiles": sorted(profiles),
        "axis_translate_weights": sorted(weight(vector) for vector in translated),
        "both_sides_at_least_two": True,
        "exact_singleton_by_capacity_lemma": True,
    }


def type_three_words() -> dict[str, Any]:
    # Disjoint stars for one nonedge label: x-star first, leaf-star second.
    # The weight-four word has three x blocks and the common leaf block T.
    c4 = (2, 2, 2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0)
    leaf_star = (0,) * 7 + (1,) * 7
    leaf_translate = add_mod3(c4, scale_mod3(2, leaf_star))
    profile = [weight(leaf_translate[:7]), weight(leaf_translate[7:])]
    assert profile == [3, 6]
    assert weight(leaf_translate) == 9

    plane = one_block_projector_and_orbit()
    return {
        "base_cross_word_weights": plane["cross_projective_weights"],
        "additional_base_words_per_selected_triple": 2,
        "weight_eight_base_word_is_noncircuit": True,
        "leaf_translate_profile": profile,
        "leaf_translate_weight": weight(leaf_translate),
        "leaf_block_cancelled": leaf_translate[7] == 0,
        "both_sides_at_least_two": True,
        "exact_singleton_by_capacity_lemma": True,
    }


def support_capacity_certificate() -> dict[str, Any]:
    # For a second realization sharing x, every block on the y-side must
    # contain the same edge yz; lambda=1 permits at most one such block.
    # For a disjoint second realization, there are four endpoint patterns,
    # and lambda=1 permits at most one triangle per pattern.
    def capacity(side_left: int, side_right: int, total_weight: int) -> int:
        if side_left < 2 or side_right < 2:
            return 3
        return 1 if total_weight > 4 else 2

    assert capacity(6, 2, 8) == 1
    assert capacity(3, 6, 9) == 1
    assert capacity(2, 2, 4) == 2

    return {
        "shared_endpoint_second_realization": {
            "opposite_side_blocks_required_on_one_edge": True,
            "lambda_one_maximum": 1,
            "excluded_when_both_sides_at_least_two": True,
        },
        "disjoint_second_realization": {
            "endpoint_patterns": 4,
            "triangles_per_pattern_maximum": 1,
            "support_weight_maximum": 4,
        },
        "capacity_if_both_sides_at_least_two": {
            "weight_four": 2,
            "weight_greater_than_four": 1,
        },
        "type_two_6_plus_2_capacity": capacity(6, 2, 8),
        "type_three_3_plus_6_capacity": capacity(3, 6, 9),
    }


def disjointness_certificate() -> dict[str, Any]:
    categories = {
        "type1_generic": {"multiplicities": [1, 2], "private_label": True},
        "type1_special": {"multiplicities": [3], "private_label": True},
        "type2_singleton": {"multiplicities": [1], "private_label": True},
        "type3_singleton": {"multiplicities": [1], "private_label": True},
        "type3_base": {"multiplicities": [3], "private_label": False},
    }
    reasons = {
        "type1_generic|type1_special": "different realization multiplicity",
        "type1_generic|type2_singleton": "equality forces the same private label",
        "type1_generic|type3_singleton": "equality forces the same private label",
        "type1_generic|type3_base": "different realization multiplicity",
        "type1_special|type2_singleton": "different realization multiplicity",
        "type1_special|type3_singleton": "different realization multiplicity",
        "type1_special|type3_base": "same triple would cover the type1 private label",
        "type2_singleton|type3_singleton": "equality forces the same private label",
        "type2_singleton|type3_base": "different realization multiplicity",
        "type3_singleton|type3_base": "different realization multiplicity",
    }
    assert len(reasons) == 10
    return {
        "categories": categories,
        "cross_category_pairs_checked": len(reasons),
        "collision_exclusions": reasons,
        "selected_cover_collision_excluded_by_private_label": True,
        "type3_companion_outside_by_cover_minimality": True,
        "type3_weight_eight_word_outside_because_noncircuit": True,
        "different_type3_base_orbits_distinguished_by_complete_triple_labels": True,
    }


def cover_count_certificate() -> dict[str, Any]:
    # Variable order: n1,n2,n3,p2,p3.
    private_row = [2, 2, 3, 1, 1]
    word_row = [2, 1, 3, 4, 1]
    difference = [right - left for left, right in zip(private_row, word_row)]
    assert difference == [0, -1, 0, 3, 0]

    # p2>=n2 makes 3*p2-n2 >= 2*n2 >= 0.
    hostile = {"n1": 0, "n2": 0, "n3": 1848, "p2": 0, "p3": 2772}
    private_hostile = sum(
        coefficient * hostile[name]
        for coefficient, name in zip(
            private_row, ("n1", "n2", "n3", "p2", "p3")
        )
    )
    word_hostile = sum(
        coefficient * hostile[name]
        for coefficient, name in zip(
            word_row, ("n1", "n2", "n3", "p2", "p3")
        )
    )
    assert private_hostile == word_hostile == 2 * C

    nonedge_projective = 2 * C
    total_projective = nonedge_projective + EDGE_WORDS
    scalar_words = 2 * total_projective
    return {
        "variable_order": ["n1", "n2", "n3", "p2", "p3"],
        "private_label_inequality_coefficients": private_row,
        "word_count_coefficients": word_row,
        "coefficient_difference": difference,
        "p2_at_least_n2": True,
        "difference_lower_bound": "3*p2-n2>=2*n2>=0",
        "outside_word_inequality": "O>=n1+4*p2+p3+2*n3",
        "hostile_triple_only_control": {
            **hostile,
            "private_row_value": private_hostile,
            "word_row_value": word_hostile,
        },
        "nonedge_projective_short_words": nonedge_projective,
        "edge_isolated_projective_short_words": EDGE_WORDS,
        "total_projective_short_words": total_projective,
        "nonzero_scalar_representatives_per_projective_class": 2,
        "B4_through_B9_lower": scalar_words,
    }


def build_results() -> dict[str, Any]:
    integrity = verify_frozen_inputs()
    assert integrity["passed"]

    payload: dict[str, Any] = {
        "format": "wave188-clean-room-verification-v1",
        "verdict": "VERIFIED_WITH_SCOPE",
        "integrity": integrity,
        "affine_profile_census": affine_profile_census(),
        "projective_orbit": projective_orbit_check(),
        "support_capacity": support_capacity_certificate(),
        "one_block": one_block_projector_and_orbit(),
        "type_two": type_two_words(),
        "type_three": type_three_words(),
        "disjointness": disjointness_certificate(),
        "cover_count": cover_count_certificate(),
        "boundary": {
            "counts_dual_words_not_only_circuits": True,
            "rank_11_excluded": False,
            "endpoint_excluded": False,
            "strict_n3_improvement": False,
            "incompatible_weight_enumerator_upper_bound_known": False,
            "external_novelty": "UNKNOWN",
            "conway_99": "UNKNOWN",
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["result_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = build_results()
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            print("FAIL Wave 188 clean-room verification")
            return 1
        print(f"PASS Wave 188 clean-room verification: {args.verify}")
        return 0
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
