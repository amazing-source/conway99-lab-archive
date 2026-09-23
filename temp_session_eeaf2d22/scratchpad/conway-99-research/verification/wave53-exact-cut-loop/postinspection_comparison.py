#!/usr/bin/env python3
"""Compare the frozen clean-room result with the Wave 53 discovery source."""

from __future__ import annotations

import argparse
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CHECKER_PATH = HERE / "independent_check.py"


def load_checker() -> Any:
    spec = importlib.util.spec_from_file_location(
        "wave53_frozen_independent_check", CHECKER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen independent checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def raw_baseline_cuts(checker: Any, data: dict[str, Any]) -> list[dict[str, Any]]:
    cuts = []
    for layer, source_name in (
        ("wave45", "wave45_cuts"),
        ("wave47", "wave47_cuts"),
    ):
        records = data[source_name]["cuts"]
        if layer == "wave47":
            records = [
                record
                for record in records
                if int(record["source_direction_index"]) == 0
            ]
        for record in records:
            cuts.append(
                {
                    "layer": layer,
                    "id": str(record["cut_sha256"]),
                    "family": str(record["family"]),
                    "constant": int(record["constant"]),
                    "coefficients": {
                        int(item["canonical_mask"]): int(item["coefficient"])
                        for item in record["coefficients"]
                    },
                }
            )
    for record in data["wave49_scout"]["solvers"][0]["candidate"][
        "wave49_families"
    ]:
        sealed = record["candidate_minimum_direction_exact_cut"]
        root = int(record["root_mask"])
        cuts.append(
            {
                "layer": "wave49",
                "id": f"root5_{root}",
                "family": f"root5_{root}",
                "constant": int(sealed["constant_raw_numerator"]),
                "coefficients": {
                    int(mask): int(value)
                    for mask, value in sealed["order7_count_coefficients"]
                },
            }
        )
    return cuts


def source_bug_wave45_records(
    independent_wave45: dict[str, Any], family: str
) -> list[dict[str, Any]]:
    return [
        {
            "order": int(record["order"]),
            "canonical_mask": int(record["canonical_mask"]),
            "upper_entries": record["entries"],
        }
        for record in independent_wave45["coefficient_streams"][family]
    ]


def source_bug_matrix(
    checker: Any,
    records: list[dict[str, Any]],
    counts: dict[int, dict[int, Fraction]],
    dimension: int,
) -> list[list[Fraction]]:
    matrix = checker.empty_matrix(dimension)
    # This intentionally reproduces the discovery defect: full symmetric
    # records are sent to a helper that mirrors every off-diagonal again.
    for record in records:
        multiplier = counts[int(record["order"])].get(
            int(record["canonical_mask"]), Fraction()
        )
        for left, right, coefficient in record["upper_entries"]:
            value = multiplier * int(coefficient)
            matrix[int(left)][int(right)] += value
            if int(left) != int(right):
                matrix[int(right)][int(left)] += value
    return matrix


def full_matrix_hash(checker: Any, matrix: list[list[Fraction]]) -> str:
    return checker.canonical_sha256(
        [
            [checker.fraction_text(value) for value in row]
            for row in matrix
        ]
    )


def compare() -> dict[str, Any]:
    checker = load_checker()
    data = {name: checker.load_json(path) for name, path in checker.PATHS.items()}
    clean = checker.load_json(HERE / "independent-result.json")
    wave53 = data["wave53"]
    classes = tuple(int(mask) for mask in data["row_system"]["classes"])
    profiles = checker.deck_profiles(classes)

    raw_cuts = raw_baseline_cuts(checker, data)
    baseline_ids = [cut["id"] for cut in raw_cuts]
    baseline_id_hash = checker.canonical_sha256(baseline_ids)

    raw_cut_replays = []
    retained = list(raw_cuts)
    witness_hash_checks = []
    for iteration in wave53["iterations"]:
        witness, y = checker.witness_from_report(iteration["witness"], classes)
        slacks = [checker.cut_value(cut, witness) for cut in retained]
        positive = [value for value in slacks if value > 0]
        vector_catalog = [
            checker.fraction_text(witness.get(mask, Fraction())) for mask in classes
        ] + [checker.fraction_text(y)]
        witness_hash = checker.canonical_sha256(vector_catalog)
        witness_hash_checks.append(
            {
                "iteration": iteration["iteration"],
                "reported": iteration["witness"]["witness_vector_sha256"],
                "recomputed": witness_hash,
                "match": witness_hash
                == iteration["witness"]["witness_vector_sha256"],
            }
        )
        raw_cut_replays.append(
            {
                "iteration": iteration["iteration"],
                "cut_count": len(retained),
                "all_nonnegative": all(value >= 0 for value in slacks),
                "tight_count": sum(value == 0 for value in slacks),
                "minimum_positive_slack": (
                    checker.fraction_text(min(positive)) if positive else None
                ),
                "reported_cut_count": iteration["witness"][
                    "cumulative_cut_checks"
                ],
                "reported_tight_count": iteration["witness"]["tight_cuts"],
                "reported_minimum_positive_slack": iteration["witness"][
                    "minimum_positive_cut_slack"
                ],
            }
        )
        if "added_cut" in iteration:
            added = iteration["added_cut"]
            retained.append(
                {
                    "layer": added["layer"],
                    "id": added["id"],
                    "family": added["family"],
                    "constant": int(added["constant"]),
                    "coefficients": {
                        int(mask): int(value)
                        for mask, value in added["coefficients"]
                    },
                }
            )

    new_cut_id_checks = []
    new_cut_catalog = []
    for iteration in wave53["iterations"]:
        if "added_cut" not in iteration:
            continue
        cut = iteration["added_cut"]
        core = {
            key: cut[key]
            for key in (
                "layer",
                "family",
                "direction",
                "constant",
                "coefficients",
                "sense",
            )
        }
        recomputed_id = checker.canonical_sha256(core)
        new_cut_id_checks.append(
            {
                "layer": cut["layer"],
                "family": cut["family"],
                "reported": cut["id"],
                "recomputed": recomputed_id,
                "match": cut["id"] == recomputed_id,
            }
        )
        new_cut_catalog.append(
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
        )
    new_cut_catalog_hash = checker.canonical_sha256(new_cut_catalog)

    wave45_stream_attacks = {}
    for family in ("edge", "nonedge", "vertex"):
        records = data["wave45_independent"]["coefficient_streams"][family]
        offdiagonal_entries = 0
        missing_reverse = 0
        for record in records:
            entries = {
                (int(left), int(right), int(value))
                for left, right, value in record["entries"]
            }
            for left, right, value in tuple(entries):
                if left != right:
                    offdiagonal_entries += 1
                    missing_reverse += int((right, left, value) not in entries)
        wave45_stream_attacks[family] = {
            "offdiagonal_full_matrix_entries": offdiagonal_entries,
            "missing_reverse_entries": missing_reverse,
            "is_full_symmetric_stream": missing_reverse == 0,
        }

    matrix_hash_checks = []
    wave45_defect_checks = []
    clean_by_iteration = {
        int(iteration["iteration"]): iteration for iteration in clean["iterations"]
    }
    for iteration in wave53["iterations"]:
        index = int(iteration["iteration"])
        witness, _ = checker.witness_from_report(iteration["witness"], classes)
        counts = checker.lower_deck(witness, classes, profiles)
        correct_matrices = checker.build_matrices(
            counts,
            data["wave45_coefficients"],
            data["wave47_coefficients"],
            data["wave49_coefficients"],
        )
        source_record_lookup = {
            (record["layer"], record["family"]): record
            for record in iteration["matrix_evaluation"]["records"]
        }
        clean_lookup = {
            (record["layer"], record["family"]): record
            for record in clean_by_iteration[index]["matrix_summary"]["wave45"]
        }
        for key, matrix in correct_matrices.items():
            source_record = source_record_lookup[key]
            correct_hash = full_matrix_hash(checker, matrix)
            matrix_hash_checks.append(
                {
                    "iteration": index,
                    "layer": key[0],
                    "family": key[1],
                    "reported": source_record["matrix_sha256"],
                    "correct_source_schema_sha256": correct_hash,
                    "match": source_record["matrix_sha256"] == correct_hash,
                }
            )
        for family in ("edge", "nonedge", "vertex"):
            full_records = source_bug_wave45_records(
                data["wave45_independent"], family
            )
            dimension = len(
                data["wave45_independent"]["flag_sets"][family][
                    "canonical_masks"
                ]
            )
            bad_matrix = source_bug_matrix(
                checker, full_records, counts, dimension
            )
            correct_matrix = correct_matrices[("wave45", family)]
            offdiagonal_doubled = all(
                bad_matrix[row][column]
                == (
                    correct_matrix[row][column]
                    if row == column
                    else 2 * correct_matrix[row][column]
                )
                for row in range(dimension)
                for column in range(dimension)
            )
            source_record = source_record_lookup[("wave45", family)]
            direction = tuple(source_record["primitive_integer_direction"])
            bad_q = checker.quadratic(bad_matrix, direction)
            correct_q = checker.quadratic(correct_matrix, direction)
            wave45_defect_checks.append(
                {
                    "iteration": index,
                    "family": family,
                    "source_matrix_equals_diagonal_plus_twice_correct_offdiagonal": offdiagonal_doubled,
                    "source_matrix_hash_reproduced": full_matrix_hash(
                        checker, bad_matrix
                    )
                    == source_record["matrix_sha256"],
                    "source_reported_quadratic_reproduced": bad_q
                    == checker.parse_fraction(source_record["exact_quadratic"]),
                    "source_bug_quadratic": checker.fraction_text(bad_q),
                    "correct_quadratic": checker.fraction_text(correct_q),
                    "correct_status": clean_lookup[("wave45", family)][
                        "independent_status"
                    ],
                    "correct_source_schema_matrix_sha256": full_matrix_hash(
                        checker, correct_matrix
                    ),
                }
            )

    terminal = wave53["iterations"][-1]
    terminal_witness, _ = checker.witness_from_report(terminal["witness"], classes)
    terminal_counts = checker.lower_deck(terminal_witness, classes, profiles)
    vertex_record = next(
        record
        for record in terminal["matrix_evaluation"]["records"]
        if record["layer"] == "wave45" and record["family"] == "vertex"
    )
    vertex_direction = tuple(vertex_record["primitive_integer_direction"])
    correct_vertex_records = data["wave45_coefficients"]["families"]["vertex"][
        "class_coefficients"
    ]
    full_vertex_records = source_bug_wave45_records(
        data["wave45_independent"], "vertex"
    )
    correct_fourth = checker.lift_quadratic_to_order7_cut(
        correct_vertex_records, vertex_direction, classes, profiles
    )
    source_bug_fourth = checker.lift_quadratic_to_order7_cut(
        full_vertex_records, vertex_direction, classes, profiles
    )
    exact_fourth = {
        "identified_terminal_selected_family": min(
            terminal["matrix_evaluation"]["records"],
            key=lambda record: (
                checker.parse_fraction(record["selection_score"]),
                record["layer"],
                record["family"],
            ),
        )["family"],
        "source_bug_nonzero_coefficients": len(source_bug_fourth["coefficients"]),
        "source_bug_cut_value": checker.fraction_text(
            checker.cut_value(source_bug_fourth, terminal_witness)
        ),
        "source_bug_matrix_value": vertex_record["exact_quadratic"],
        "correct_nonzero_coefficients": len(correct_fourth["coefficients"]),
        "correct_cut_value": checker.fraction_text(
            checker.cut_value(correct_fourth, terminal_witness)
        ),
        "correct_matrix_value": clean["excluded_fourth_dense_wave45_cut"][
            "correct_exact_quadratic"
        ],
        "numerical_residual": "7.431e-10",
        "exact_multiplier_certificate_in_discovery_package": False,
        "exact_farkas_certificate": False,
        "reason": "The residual is nonzero, and the discovery exact reconstruction explicitly failed.  No exact nonnegative multiplier identity was serialized.  The candidate was also derived from the duplicated-offdiagonal Wave45 matrix; the correctly expanded cut is positive at the terminal witness.",
    }

    candidate_deduplication = []
    for iteration in clean["iterations"]:
        attacks = iteration["candidate_normalization_attacks"]
        rejecting_records = int(attacks["exactly_rejecting_nonduplicate_candidates"])
        internal_duplicates = int(attacks["candidate_cut_key_duplicates"])
        candidate_deduplication.append(
            {
                "iteration": iteration["iteration"],
                "source_reported_eligible_nonduplicate_candidates": (
                    wave53["iterations"][iteration["iteration"]]
                    .get("selection", {})
                    .get("eligible_nonduplicate_candidates")
                ),
                "candidate_records": attacks["candidate_count"],
                "unique_normalized_candidate_rows": attacks["candidate_count"]
                - internal_duplicates,
                "records_rejecting_correct_source_matrix": rejecting_records,
                "unique_normalized_rows_rejecting_correct_source_matrix": (
                    rejecting_records - internal_duplicates
                ),
                "duplicate_groups": attacks["candidate_duplicate_groups"],
                "selected_cut_still_minimizes_correct_exact_rule": (
                    iteration["added_cut"] is None
                    or iteration["added_cut"]["selected_by_correct_exact_rule"]
                ),
            }
        )

    source_path = ROOT / "attempts/wave53-exact-cut-loop/exact_cut_loop.py"
    source_lines = source_path.read_text(encoding="utf-8").splitlines()
    return {
        "format": "wave53-exact-cut-loop-postinspection-comparison-v1",
        "role": "verifier",
        "claim_label": "REFUTED_IN_PART",
        "scope": "comparison of the preinspection-frozen clean-room result with Wave53 discovery source and sealed output",
        "source_code": {
            "path": source_path.relative_to(ROOT).as_posix(),
            "sha256": checker.sha256_file(source_path),
            "wave45_full_stream_relabel_lines_433_446_present": any(
                '"upper_entries": record["entries"]' in line
                for line in source_lines[432:446]
            ),
            "generic_upper_mirroring_lines_262_275_present": any(
                "matrix[column][row] += value" in line
                for line in source_lines[261:275]
            ),
            "defect": "family_models relabels already-full symmetric Wave45 verifier entries as upper_entries; add_upper then mirrors every off-diagonal a second time.",
        },
        "hash_checks": {
            "baseline_cut_ids": {
                "reported": wave53["baseline_cut_ids_sha256"],
                "recomputed": baseline_id_hash,
                "match": baseline_id_hash == wave53["baseline_cut_ids_sha256"],
            },
            "new_cut_ids": new_cut_id_checks,
            "new_cut_catalog": {
                "reported": wave53["new_cut_catalog_sha256"],
                "recomputed": new_cut_catalog_hash,
                "match": new_cut_catalog_hash == wave53["new_cut_catalog_sha256"],
            },
            "witness_vectors": witness_hash_checks,
            "matrices": {
                "checks": len(matrix_hash_checks),
                "reported_hashes_matching_correct_matrices": sum(
                    check["match"] for check in matrix_hash_checks
                ),
                "details": matrix_hash_checks,
            },
        },
        "exact_raw_174_to_177_cut_replay": {
            "baseline_count": len(raw_cuts),
            "iterations": raw_cut_replays,
            "all_reported_scalings_and_slacks_match": all(
                replay["cut_count"] == replay["reported_cut_count"]
                and replay["tight_count"] == replay["reported_tight_count"]
                and replay["minimum_positive_slack"]
                == replay["reported_minimum_positive_slack"]
                and replay["all_nonnegative"]
                for replay in raw_cut_replays
            ),
        },
        "wave45_full_stream_attack": wave45_stream_attacks,
        "wave45_double_offdiagonal_defect": {
            "checks": len(wave45_defect_checks),
            "all_source_matrices_and_quadratics_reproduced": all(
                check["source_matrix_equals_diagonal_plus_twice_correct_offdiagonal"]
                and check["source_matrix_hash_reproduced"]
                and check["source_reported_quadratic_reproduced"]
                for check in wave45_defect_checks
            ),
            "details": wave45_defect_checks,
        },
        "matrix_status_correction": clean["matrix_totals"],
        "candidate_deduplication_and_selection": candidate_deduplication,
        "excluded_fourth_dense_wave45_cut": exact_fourth,
        "conclusion": {
            "fixed_177_cut_rational_relaxation": "VERIFIED_EXACTLY_FEASIBLE",
            "wave49_roots_220_62_221_cuts": "VERIFIED_EXACT",
            "all_128_matrices_exactly_indefinite": "REFUTED",
            "correct_matrix_census": {
                "exactly_indefinite": 120,
                "exactly_psd": 8,
            },
            "wave45_reported_direction_evaluations": {
                "correct": 0,
                "incorrect": 12,
            },
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "Conway_99": "UNKNOWN",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = compare()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.output:
        arguments.output.write_text(text, encoding="utf-8", newline="\n")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
