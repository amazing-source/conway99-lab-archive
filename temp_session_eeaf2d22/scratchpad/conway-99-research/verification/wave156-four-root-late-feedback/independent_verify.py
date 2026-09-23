#!/usr/bin/env python3
"""Clean-room verifier for Wave152 late four-root feedback.

No discovery Python is imported or executed.  The graph/flag primitives come
from the previously sealed Wave155 clean-room verifier, whose hash is checked
before import.  All late cuts, witness equalities, and negative directions are
then reconstructed from declarative certificates.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import itertools
import json
import math
import sys
import time
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ATTEMPT = ROOT / "attempts/wave152-four-root-order8"
BASE_PATH = ROOT / "verification/wave155-four-root-feedback/independent_verify.py"
BASE_SHA256 = "c8aecd00c7da53fa929b53503bf437c0d0714c79a2e85a451168ac2e85b75c88"
KNOWN_POST_FREEZE_DRIFT = {
    "attempts/wave152-four-root-order8/build_simplified_mask12_cut.py":
        "73d25f17dca5ce3c43a24f881d93846465d1004f5b7306cfbe7a633adcc7d1f2",
    "attempts/wave152-four-root-order8/test_wave152.py":
        "7da8791f6bb310e787c24f488f7449bb594afd9fc26b197465a25763e974f51f",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_base():
    require(file_sha256(BASE_PATH) == BASE_SHA256, "Wave155 verifier hash drift")
    spec = importlib.util.spec_from_file_location("wave155_cleanroom_base", BASE_PATH)
    require(spec is not None and spec.loader is not None, "cannot load verifier base")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base()


def verify_freeze(path: Path) -> dict:
    passed = 0
    failed = 0
    post_freeze_drift = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        actual = file_sha256(ROOT / relative)
        if actual == expected:
            passed += 1
        elif (
            relative in KNOWN_POST_FREEZE_DRIFT
            and actual == KNOWN_POST_FREEZE_DRIFT[relative]
        ):
            post_freeze_drift[relative] = {
                "frozen_sha256": expected,
                "current_sha256": actual,
                "used_as_input": False,
            }
        else:
            failed += 1
    require(failed == 0, f"freeze drift in {path.name}")
    return {
        "passed_unchanged": passed,
        "failed": failed,
        "known_post_freeze_drift": post_freeze_drift,
    }


def dense_direction(width: int, indices: Sequence[int], values: Sequence[int]) -> list[int]:
    require(len(indices) == len(values), "direction support mismatch")
    result = [0] * width
    for index, value in zip(indices, values, strict=True):
        require(0 <= index < width and result[index] == 0, "bad direction index")
        result[index] = int(value)
    return result


def structural_keys() -> tuple[str, ...]:
    return (
        "root_mask",
        "root_embedding_count",
        "flag_count",
        "direction",
        "sense",
        "constant",
        "order7_coefficients",
        "order8_coefficients",
        "primitive_divisor",
        "projected_first_moment",
        "order6_quadratic_nonzeros",
    )


def derive_cut_structures(
    requests: Sequence[dict],
    classes: dict[int, tuple[int, ...]],
    lower: dict[int, dict[int, Fraction]],
    memory_samples: list[dict],
) -> dict[str, dict]:
    """Independently enumerate every requested covariance direction."""
    x4 = BASE.derive_order_four(lower[5], classes[5])
    grouped: dict[int, list[dict]] = defaultdict(list)
    for request in requests:
        grouped[int(request["root_mask"])].append(request)
    results: dict[str, dict] = {}
    for root_mask, root_requests in sorted(grouped.items()):
        flags = BASE.flag_universe(root_mask)
        flag_index = {mask: index for index, mask in enumerate(flags)}
        directions = [list(map(int, request["direction"])) for request in root_requests]
        require(
            all(len(direction) == len(flags) for direction in directions),
            f"direction width mismatch for root {root_mask}",
        )
        first = [dict() for _ in directions]
        quadratic = [{6: {}, 7: {}, 8: {}} for _ in directions]
        for order in (6, 7, 8):
            for class_index, class_mask in enumerate(classes[order]):
                first_values, quadratic_values = BASE.class_coefficients_for_directions(
                    class_mask,
                    order,
                    root_mask,
                    directions,
                    flag_index,
                )
                for direction_index in range(len(directions)):
                    if order == 6 and first_values[direction_index]:
                        first[direction_index][class_mask] = first_values[direction_index]
                    if quadratic_values[direction_index]:
                        quadratic[direction_index][order][class_mask] = (
                            quadratic_values[direction_index]
                        )
                if order == 8 and class_index % 192 == 0:
                    memory_samples.append(
                        BASE.memory_sample(
                            f"root_{root_mask}_order8_class_{class_index}"
                        )
                    )
        root_count = BASE.root_embedding_count(x4, root_mask)
        for index, request in enumerate(root_requests):
            projected = sum(
                int(lower[6][mask]) * coefficient
                for mask, coefficient in first[index].items()
            )
            raw_constant = (
                root_count
                * sum(
                    int(lower[6][mask]) * coefficient
                    for mask, coefficient in quadratic[index][6].items()
                )
                - projected * projected
            )
            dense7 = [
                root_count * quadratic[index][7].get(mask, 0)
                for mask in classes[7]
            ]
            dense8 = [
                root_count * quadratic[index][8].get(mask, 0)
                for mask in classes[8]
            ]
            divisor = math.gcd(
                abs(raw_constant), *map(abs, dense7), *map(abs, dense8)
            )
            require(divisor > 0, f"zero cut direction {request['id']}")
            results[str(request["id"])] = {
                "root_mask": root_mask,
                "root_embedding_count": root_count,
                "flag_count": len(flags),
                "direction": directions[index],
                "sense": "constant + sum(a7_H*x7_H) + sum(a8_H*x8_H) >= 0",
                "constant": str(raw_constant // divisor),
                "order7_coefficients": [
                    {"canonical_mask": mask, "coefficient": str(value // divisor)}
                    for mask, value in zip(classes[7], dense7, strict=True)
                    if value
                ],
                "order8_coefficients": [
                    {"canonical_mask": mask, "coefficient": str(value // divisor)}
                    for mask, value in zip(classes[8], dense8, strict=True)
                    if value
                ],
                "primitive_divisor": str(divisor),
                "projected_first_moment": str(projected),
                "order6_quadratic_nonzeros": len(quadratic[index][6]),
            }
        memory_samples.append(BASE.memory_sample(f"root_{root_mask}_complete"))
    return results


def witness_maps(
    witness: dict, classes: dict[int, tuple[int, ...]]
) -> tuple[dict[int, Fraction], dict[int, Fraction]]:
    return (
        BASE.support_map(witness, "x7_support", classes[7]),
        BASE.support_map(witness, "x8_support", classes[8]),
    )


def evaluate_structure(
    structure: dict,
    witness: dict,
    classes: dict[int, tuple[int, ...]],
) -> Fraction:
    x7, x8 = witness_maps(witness, classes)
    return BASE.evaluate_cut(structure, x7, x8, classes)


def raw_value(
    structure: dict,
    witness: dict,
    classes: dict[int, tuple[int, ...]],
) -> Fraction:
    return evaluate_structure(structure, witness, classes) * int(
        structure["primitive_divisor"]
    )


def verify_stored_cut(
    stored: dict,
    reconstructed: dict,
    source_witness: dict,
    classes: dict[int, tuple[int, ...]],
) -> dict:
    for key in structural_keys():
        require(stored[key] == reconstructed[key], f"cut structural mismatch: {key}")
    core = {key: value for key, value in stored.items() if key != "cut_sha256"}
    rebuilt_hash = BASE.canonical_sha256(core)
    require(rebuilt_hash == stored["cut_sha256"], "stored cut hash mismatch")
    primitive_value = evaluate_structure(reconstructed, source_witness, classes)
    require(
        primitive_value == BASE.fraction(stored["wave150_witness_value"]),
        "stored source-witness value mismatch",
    )
    raw = primitive_value * int(reconstructed["primitive_divisor"])
    require(
        raw == BASE.fraction(stored["wave150_witness_unscaled_value"]),
        "stored source raw value mismatch",
    )
    if "stored_scaled_value" in stored:
        require(
            raw * int(stored["stored_count_scale"])
            == int(stored["stored_scaled_value"]),
            "stored scaled cut value mismatch",
        )
    else:
        require(
            raw * 4 == int(stored["stored_four_times_value"]),
            "stored four-times cut value mismatch",
        )
    require(primitive_value < 0, "source witness is not separated")
    return {
        "cut_sha256": stored["cut_sha256"],
        "root_mask": int(stored["root_mask"]),
        "constant": stored["constant"],
        "direction_nonzeros": sum(int(value) != 0 for value in stored["direction"]),
        "order7_nonzeros": len(stored["order7_coefficients"]),
        "order8_nonzeros": len(stored["order8_coefficients"]),
        "primitive_divisor": stored["primitive_divisor"],
        "source_witness_value": BASE.fraction_string(primitive_value),
        "reconstructed_exactly": True,
    }


def certificate_direction(root_record: dict) -> list[int]:
    certificate = root_record["negative_certificate"]
    direction = dense_direction(
        int(root_record["flag_count"]),
        list(map(int, certificate["indices"])),
        list(map(int, certificate["vector"])),
    )
    flags = BASE.flag_universe(int(root_record["root_mask"]))
    require(
        [flags[index] for index in map(int, certificate["indices"])]
        == list(map(int, certificate["flag_masks"])),
        "negative certificate flag semantics mismatch",
    )
    return direction


def replay_negative_certificate(
    root_record: dict,
    evaluation: dict,
    witness: dict,
    structure: dict,
    classes: dict[int, tuple[int, ...]],
) -> dict:
    certificate = root_record["negative_certificate"]
    require(certificate is not None, "missing negative certificate")
    require(
        list(map(int, structure["direction"])) == certificate_direction(root_record),
        "negative direction differs from reconstructed cut direction",
    )
    raw = raw_value(structure, witness, classes)
    scale = int(evaluation["count_denominator_scale"])
    scaled = raw * scale
    require(scaled.denominator == 1, "scaled quadratic is fractional")
    require(
        scaled.numerator == int(certificate["quadratic_value_scaled"]),
        "negative quadratic replay mismatch",
    )
    require(scaled < 0, "certificate is not negative")
    hostile = list(map(int, structure["direction"]))
    first_nonzero = next(index for index, value in enumerate(hostile) if value)
    hostile[first_nonzero] += 1
    return {
        "root_mask": int(root_record["root_mask"]),
        "kind": certificate["kind"],
        "support_size": len(certificate["indices"]),
        "quadratic_value_scaled": str(scaled.numerator),
        "strictly_negative": True,
        "direction_sha256": BASE.canonical_sha256(structure["direction"]),
        "hostile_first_nonzero_plus_one_differs": hostile != structure["direction"],
    }


def replay_principal(
    root_record: dict,
    evaluation: dict,
    witness: dict,
    structures: dict[str, dict],
    ids: tuple[str, str, str],
    direction_structure: dict,
    classes: dict[int, tuple[int, ...]],
) -> dict:
    certificate = root_record["negative_certificate"]
    require(certificate["kind"] == "negative_2x2_principal_minor", "not principal")
    scale = int(evaluation["count_denominator_scale"])
    q_i = raw_value(structures[ids[0]], witness, classes) * scale
    q_j = raw_value(structures[ids[1]], witness, classes) * scale
    q_sum = raw_value(structures[ids[2]], witness, classes) * scale
    require(
        q_i.denominator == q_j.denominator == q_sum.denominator == 1,
        "principal entries not integral after scaling",
    )
    diagonal_i = q_i.numerator
    diagonal_j = q_j.numerator
    off_diagonal_numerator = q_sum.numerator - diagonal_i - diagonal_j
    require(off_diagonal_numerator % 2 == 0, "odd polarized off diagonal")
    off_diagonal = off_diagonal_numerator // 2
    entries = [diagonal_i, off_diagonal, diagonal_j]
    require(
        entries == list(map(int, certificate["principal_entries_scaled"])),
        "principal entries mismatch",
    )
    determinant = diagonal_i * diagonal_j - off_diagonal * off_diagonal
    require(
        determinant == int(certificate["determinant_scaled_squared"]),
        "principal determinant mismatch",
    )
    require(determinant < 0, "principal minor is not negative")
    direction_scaled = raw_value(direction_structure, witness, classes) * scale
    require(
        direction_scaled.denominator == 1
        and direction_scaled.numerator
        == int(certificate["quadratic_value_scaled"]),
        "principal direction value mismatch",
    )
    return {
        "indices": list(map(int, certificate["indices"])),
        "flag_masks": list(map(int, certificate["flag_masks"])),
        "principal_entries_scaled": list(map(str, entries)),
        "determinant_scaled_squared": str(determinant),
        "direction_quadratic_value_scaled": str(direction_scaled.numerator),
        "negative_determinant": True,
    }


def root_record(evaluation: dict, root_mask: int) -> dict:
    record = next(
        item for item in evaluation["root_blocks"] if int(item["root_mask"]) == root_mask
    )
    require(record["exact_status"] == "NOT_PSD", f"root {root_mask} not marked NOT_PSD")
    return record


def basis_requests(prefix: str, root_mask: int, width: int, i: int, j: int) -> list[dict]:
    first = dense_direction(width, [i], [1])
    second = dense_direction(width, [j], [1])
    summed = [left + right for left, right in zip(first, second, strict=True)]
    return [
        {"id": f"{prefix}_i", "root_mask": root_mask, "direction": first},
        {"id": f"{prefix}_j", "root_mask": root_mask, "direction": second},
        {"id": f"{prefix}_sum", "root_mask": root_mask, "direction": summed},
    ]


def main_result() -> dict:
    started = time.time()
    memory_samples = [BASE.memory_sample("start")]
    freeze = {
        "discovery": verify_freeze(HERE / "discovery-freeze.sha256"),
        "supporting": verify_freeze(HERE / "supporting-input-freeze.sha256"),
    }

    exact_cuts = load_json(ATTEMPT / "exact-cuts.json")
    iteration2 = load_json(ATTEMPT / "iteration2-cuts.json")
    iteration3 = load_json(ATTEMPT / "iteration3-mask13-cut.json")
    iteration4 = load_json(ATTEMPT / "iteration4-three-cuts.json")
    simplified1_payload = load_json(ATTEMPT / "simplified-mask12-cut.json")
    replay9 = load_json(ATTEMPT / "exact-nine-cut-replay.json")

    witness4 = load_json(ATTEMPT / "exact-witness-after-four-cuts.json")
    witness5 = load_json(ATTEMPT / "exact-witness-after-five-cuts.json")
    witness8 = load_json(ATTEMPT / "exact-witness-after-eight-cuts.json")
    evaluation4 = load_json(ATTEMPT / "four-root-evaluation-after-four-cuts.json")
    evaluation5 = load_json(ATTEMPT / "four-root-evaluation-after-five-cuts.json")
    evaluation8 = load_json(ATTEMPT / "four-root-evaluation-after-eight-cuts.json")

    row_system = load_json(ROOT / "attempts/wave44-rooted-flags/row-system.json")
    coefficients = BASE.load_gzip_json(
        "attempts/wave147-alternative-lane/coefficients.json.gz"
    )
    marked = BASE.load_gzip_json(
        "attempts/wave148-marked-order8/marked-rows.json.gz"
    )
    exact_results = load_json(
        ROOT / "attempts/wave147-alternative-lane/exact-results.json"
    )
    classes = BASE.class_sets(coefficients, row_system, exact_results)
    x7_5, _ = witness_maps(witness5, classes)
    lower = BASE.derive_lower_counts(x7_5, classes)
    x7_8, _ = witness_maps(witness8, classes)
    lower8 = BASE.derive_lower_counts(x7_8, classes)
    require(lower[5] == lower8[5] and lower[6] == lower8[6], "lower counts drift")
    memory_samples.append(BASE.memory_sample("classes_and_lower_counts"))

    r4_13 = root_record(evaluation4, 13)
    r5 = {mask: root_record(evaluation5, mask) for mask in (3, 12, 13)}
    r8 = {mask: root_record(evaluation8, mask) for mask in (3, 12, 13)}
    cut3 = iteration3["cuts"][0]
    cut4 = {int(cut["root_mask"]): cut for cut in iteration4["cuts"]}
    simple1 = simplified1_payload["cut"]

    require(certificate_direction(r4_13) == list(map(int, cut3["direction"])),
            "iteration3 direction differs from mask13 principal certificate")
    for mask in (3, 12, 13):
        require(
            certificate_direction(r5[mask]) == list(map(int, cut4[mask]["direction"])),
            f"iteration4 direction differs from after-five root {mask}",
        )

    requests = [
        {"id": "iteration3_mask13", "root_mask": 13, "direction": cut3["direction"]},
        *[
            {
                "id": f"iteration4_mask{mask}",
                "root_mask": mask,
                "direction": cut4[mask]["direction"],
            }
            for mask in (3, 12, 13)
        ],
        {"id": "simplified1_mask12", "root_mask": 12, "direction": simple1["direction"]},
        *[
            {
                "id": f"evaluation8_mask{mask}",
                "root_mask": mask,
                "direction": certificate_direction(r8[mask]),
            }
            for mask in (3, 12, 13)
        ],
        {
            "id": "simplified2_mask12",
            "root_mask": 12,
            "direction": dense_direction(178, [160, 166], [1, -1]),
        },
        *basis_requests("principal4_mask13", 13, 125, 5, 49),
        *basis_requests("principal5_mask12", 12, 178, 59, 71),
        *basis_requests("principal8_mask12", 12, 178, 160, 166),
    ]
    structures = derive_cut_structures(requests, classes, lower, memory_samples)

    stored_cut_results = [
        verify_stored_cut(
            cut3, structures["iteration3_mask13"], witness4, classes
        ),
        *[
            verify_stored_cut(
                cut4[mask], structures[f"iteration4_mask{mask}"], witness5, classes
            )
            for mask in (3, 12, 13)
        ],
        verify_stored_cut(
            simple1, structures["simplified1_mask12"], witness5, classes
        ),
    ]

    cut_payloads5 = [exact_cuts, iteration2, iteration3]
    cut_payloads8 = [exact_cuts, iteration2, iteration3, iteration4]
    witness_results = {
        "after_five": BASE.verify_witness(
            "after_five",
            witness5,
            cut_payloads5,
            coefficients,
            marked,
            row_system,
            classes,
            lower,
            memory_samples,
        ),
        "after_eight": BASE.verify_witness(
            "after_eight",
            witness8,
            cut_payloads8,
            coefficients,
            marked,
            row_system,
            classes,
            lower,
            memory_samples,
        ),
    }

    negatives = {
        "after_four_mask13": replay_negative_certificate(
            r4_13,
            evaluation4,
            witness4,
            structures["iteration3_mask13"],
            classes,
        ),
        "after_five": [
            replay_negative_certificate(
                r5[mask],
                evaluation5,
                witness5,
                structures[f"iteration4_mask{mask}"],
                classes,
            )
            for mask in (3, 12, 13)
        ],
        "after_eight": [
            replay_negative_certificate(
                r8[mask],
                evaluation8,
                witness8,
                structures[f"evaluation8_mask{mask}"],
                classes,
            )
            for mask in (3, 12, 13)
        ],
    }
    principals = {
        "after_four_mask13": replay_principal(
            r4_13,
            evaluation4,
            witness4,
            structures,
            (
                "principal4_mask13_i",
                "principal4_mask13_j",
                "principal4_mask13_sum",
            ),
            structures["iteration3_mask13"],
            classes,
        ),
        "after_five_mask12": replay_principal(
            r5[12],
            evaluation5,
            witness5,
            structures,
            (
                "principal5_mask12_i",
                "principal5_mask12_j",
                "principal5_mask12_sum",
            ),
            structures["iteration4_mask12"],
            classes,
        ),
        "after_eight_mask12": replay_principal(
            r8[12],
            evaluation8,
            witness8,
            structures,
            (
                "principal8_mask12_i",
                "principal8_mask12_j",
                "principal8_mask12_sum",
            ),
            structures["evaluation8_mask12"],
            classes,
        ),
    }

    # The first simplified direction is (1,-1) on flags 5428 and 6324.
    simple1_scaled = (
        raw_value(structures["simplified1_mask12"], witness5, classes)
        * int(evaluation5["count_denominator_scale"])
    )
    require(
        simple1_scaled.denominator == 1
        and simple1_scaled.numerator
        == int(simplified1_payload["derivation"]["scaled_quadratic_value"]),
        "first simplified principal value mismatch",
    )
    positive_on_eight = evaluate_structure(
        structures["simplified1_mask12"], witness8, classes
    )
    require(positive_on_eight > 0, "first simplified cut is not positive on witness8")
    require(
        BASE.fraction(replay9["exact_value"]) == positive_on_eight
        and replay9["strictly_positive"] is True,
        "late exact-nine replay mismatch",
    )

    # The second simplified cut is derived without reading its late serialized
    # artifact.  It comes from the already frozen equal-diagonal pair 160,166.
    simple2 = structures["simplified2_mask12"]
    require(simple2["constant"] == "18711", "second simplified constant")
    require(simple2["order7_coefficients"] == [], "second simplified x7 terms")
    require(
        simple2["order8_coefficients"]
        == [
            {"canonical_mask": 2022000, "coefficient": "6"},
            {"canonical_mask": 5683824, "coefficient": "-2"},
        ],
        "second simplified x8 terms",
    )
    simple2_value = evaluate_structure(simple2, witness8, classes)
    require(simple2_value < 0, "second simplified cut does not separate witness8")
    simple2_scaled = raw_value(simple2, witness8, classes) * int(
        evaluation8["count_denominator_scale"]
    )
    require(
        simple2_scaled.denominator == 1
        and simple2_scaled.numerator
        == (
            int(principals["after_eight_mask12"]["principal_entries_scaled"][0])
            + int(principals["after_eight_mask12"]["principal_entries_scaled"][2])
            - 2 * int(principals["after_eight_mask12"]["principal_entries_scaled"][1])
        ),
        "second simplified quadratic/principal mismatch",
    )

    # Hostile controls.
    mutated = dict(simple1)
    mutated["constant"] = str(int(simple1["constant"]) + 1)
    mutated_value = evaluate_structure(mutated, witness8, classes)
    require(mutated_value == positive_on_eight + 1, "constant mutation control failed")
    bad_direction = list(map(int, cut3["direction"]))
    bad_direction[5] += 1
    require(bad_direction != structures["iteration3_mask13"]["direction"],
            "direction mutation control failed")

    numerical = {}
    for name in (
        "zero-face-five-cuts-highs.json",
        "zero-face-eight-cuts-highs.json",
        "zero-face-nine-cuts-highs.json",
    ):
        payload = load_json(ATTEMPT / name)
        numerical[name] = {
            "solver": payload["solver"]["name"],
            "status": payload["solver"]["status"],
            "used_as_certificate": False,
        }

    memory_samples.append(BASE.memory_sample("complete"))
    return {
        "format": "wave156-four-root-late-feedback-independent-v1",
        "claim_label": "VERIFIED",
        "scope": (
            "Late finite four-root covariance cuts, exact five/eight-cut "
            "pseudowitness replays, and negative directions; not endpoint or graph"
        ),
        "separation": {
            "discovery_python_imported": False,
            "discovery_python_executed": False,
            "prior_cleanroom_verifier_imported": True,
            "prior_cleanroom_verifier_sha256": BASE_SHA256,
            "solver_status_used_as_evidence": False,
        },
        "freeze": freeze,
        "stored_late_cuts": stored_cut_results,
        "witnesses": witness_results,
        "negative_directions": negatives,
        "principal_minors": principals,
        "simplified_mask12_first": {
            "constant": simple1["constant"],
            "order7_coefficients": simple1["order7_coefficients"],
            "order8_coefficients": simple1["order8_coefficients"],
            "primitive_divisor": simple1["primitive_divisor"],
            "scaled_value_on_five_cut_witness": str(simple1_scaled.numerator),
            "exact_value_on_eight_cut_witness": BASE.fraction_string(
                positive_on_eight
            ),
            "strictly_positive_on_eight_cut_witness": True,
            "exact_nine_replay_sha256":
                "64f961e21d6b01a9767588caa691171913bf3c8f4704aa4d38f085cc73fb8b39",
        },
        "simplified_mask12_second": {
            "source_serialization_status": "OUTSIDE_CLOSED_FREEZE_NOT_INSPECTED",
            "direction_indices": [160, 166],
            "direction": [1, -1],
            "constant": simple2["constant"],
            "order7_coefficients": simple2["order7_coefficients"],
            "order8_coefficients": simple2["order8_coefficients"],
            "primitive_divisor": simple2["primitive_divisor"],
            "exact_value_on_eight_cut_witness": BASE.fraction_string(simple2_value),
            "strictly_negative_on_eight_cut_witness": True,
            "scaled_quadratic_value": str(simple2_scaled.numerator),
        },
        "numerical_statuses": numerical,
        "hostile_tests": {
            "simplified_constant_plus_one_changes_value_by_one": True,
            "mask13_direction_coordinate_mutation_rejected": True,
            "principal_entry_polarization_replayed": True,
            "all_frozen_hashes_replayed": True,
        },
        "verdict": {
            "late_stored_covariance_cuts": "VERIFIED",
            "five_cut_finite_relaxation": "EXACT_RATIONAL_FEASIBLE",
            "eight_cut_finite_relaxation": "EXACT_RATIONAL_FEASIBLE",
            "first_simplified_cut_on_eight_witness": "STRICTLY_POSITIVE",
            "second_simplified_cut_on_eight_witness": "STRICTLY_NEGATIVE",
            "nine_cut_finite_relaxation_via_eight_witness": "EXACT_RATIONAL_FEASIBLE",
            "ten_cut_finite_relaxation": "UNKNOWN",
            "graph_constructed": False,
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "Conway_99": "UNKNOWN",
        },
        "limitations": [
            "All witnesses are rational pseudowitnesses for finite relaxations.",
            "A negative direction separates only the displayed pseudowitness.",
            "Numerical solver statuses are diagnostics, not proof certificates.",
            "No endpoint infeasibility, graph realization, strict bound, or conjecture result follows.",
        ],
        "resource_report": {
            "elapsed_seconds": time.time() - started,
            "minimum_free_physical_memory_percent": min(
                float(sample["free_physical_memory_percent"])
                for sample in memory_samples
            ),
            "samples": memory_samples,
        },
    }


def require_expected_subset(actual: object, expected: object, path: str = "$") -> None:
    """Require every stored certificate field while permitting richer replay output."""
    if isinstance(expected, dict):
        require(isinstance(actual, dict), f"{path}: expected mapping")
        for key, value in expected.items():
            require(key in actual, f"{path}: missing key {key}")
            require_expected_subset(actual[key], value, f"{path}.{key}")
        return
    if isinstance(expected, list):
        require(isinstance(actual, list), f"{path}: expected list")
        require(len(actual) == len(expected), f"{path}: list length mismatch")
        for index, (actual_item, expected_item) in enumerate(
            zip(actual, expected, strict=True)
        ):
            require_expected_subset(actual_item, expected_item, f"{path}[{index}]")
        return
    require(actual == expected, f"{path}: value mismatch")


def self_test() -> dict:
    require(dense_direction(4, [1, 3], [2, -5]) == [0, 2, 0, -5],
            "dense direction self-test")
    require(structural_keys()[0] == "root_mask", "structural key self-test")
    require(BASE.self_test()["flag_counts"] == {"3": 155, "12": 178},
            "base semantic self-test")
    return {
        "dense_direction": "PASS",
        "base_graph_flag_semantics": "PASS",
        "fraction_arithmetic": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--print-json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0
    result = main_result()
    if args.verify:
        expected = load_json(args.verify)
        require_expected_subset(result, expected)
    if args.print_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    print(
        json.dumps(
            {
                "claim_label": result["claim_label"],
                "five_rows": result["witnesses"]["after_five"]["all_equalities"],
                "eight_rows": result["witnesses"]["after_eight"]["all_equalities"],
                "first_simple_value_on_eight": result[
                    "simplified_mask12_first"
                ]["exact_value_on_eight_cut_witness"],
                "second_simple_value_on_eight": result[
                    "simplified_mask12_second"
                ]["exact_value_on_eight_cut_witness"],
                "minimum_free_percent": result["resource_report"][
                    "minimum_free_physical_memory_percent"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
