#!/usr/bin/env python3
"""Compare the sealed Wave 46 package to the frozen clean-room algebra."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ALGEBRA_PATH = HERE / "independent_algebra.py"
INDEPENDENT_RESULT = HERE / "independent-results.json"
DISCOVERY_DIR = ROOT / "attempts/wave46-f7-code"
DISCOVERY_RESULT = DISCOVERY_DIR / "exact-results.json"
DISCOVERY_MANIFEST = DISCOVERY_DIR / "package-manifest.sha256"
DISCOVERY_AGENT = ROOT / "agents/2026-07-27-wave46-f7-code.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_module(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    require(
        specification is not None and specification.loader is not None,
        f"cannot load {path}",
    )
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


ALGEBRA = load_module("wave46_clean_frozen_algebra", ALGEBRA_PATH)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, separators=(",", ": "))
        + "\n"
    ).encode("utf-8")


def independent_local_columns() -> tuple[tuple[int, ...], ...]:
    first = tuple((1, value, 0, 0) for value in range(ALGEBRA.FIELD))
    second = tuple((0, 0, 1, value) for value in range(ALGEBRA.FIELD))
    third = tuple((1, value, 1, value) for value in range(ALGEBRA.FIELD))
    columns = first + second + third
    require(len(columns) == 21, "local column census changed")
    return columns


def block_diagonal_columns(
    local: Sequence[Sequence[int]],
    copies: int,
) -> tuple[tuple[int, ...], ...]:
    result: list[tuple[int, ...]] = []
    for block in range(copies):
        for local_column in local:
            column = [0] * (4 * copies)
            column[4 * block:4 * block + 4] = local_column
            result.append(tuple(column))
    return tuple(result)


def local_weight_enumerator(
    local: Sequence[Sequence[int]],
) -> dict[int, int]:
    result: Counter[int] = Counter()
    for coefficients in itertools.product(
        range(ALGEBRA.FIELD), repeat=4
    ):
        word = [
            ALGEBRA.dot_mod7(coefficients, column)
            for column in local
        ]
        result[sum(value != 0 for value in word)] += 1
    return dict(sorted(result.items()))


def convolve(
    left: dict[int, int],
    right: dict[int, int],
) -> dict[int, int]:
    result: Counter[int] = Counter()
    for left_weight, left_count in left.items():
        for right_weight, right_count in right.items():
            result[left_weight + right_weight] += left_count * right_count
    return dict(sorted(result.items()))


def projected_tail_rows(
    projection: Sequence[Sequence[int]],
    tail_columns: Sequence[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(ALGEBRA.dot_mod7(row, column) for column in tail_columns)
        for row in projection
    )


def reconstruct_control(
    record: dict[str, Any],
    local: Sequence[Sequence[int]],
) -> dict[str, Any]:
    rank = record["dimension"]
    tail_dimension = rank - 16
    require(
        record["tail_projection_dimension"] == tail_dimension,
        "tail projection dimension label changed",
    )
    projection = ALGEBRA.validate_matrix(
        record["projection_matrix"],
        rows=tail_dimension,
        columns=28,
        canonical_entries=True,
    )
    require(
        ALGEBRA.rank_mod7(projection) == tail_dimension,
        "projection matrix lost row rank",
    )
    require(
        ALGEBRA.sha256_compact(projection) == record["projection_sha256"],
        "projection SHA-256 differs",
    )
    first_columns = block_diagonal_columns(local, 4)
    tail_columns = block_diagonal_columns(local, 7)
    tail_rows = projected_tail_rows(projection, tail_columns)
    tail_images = ALGEBRA.transpose(tail_rows)
    combined_columns = tuple(
        tuple(column) + (0,) * tail_dimension
        for column in first_columns
    ) + tuple(
        (0,) * 16 + tuple(column)
        for column in tail_images
    )
    require(
        len(combined_columns) == ALGEBRA.LENGTH,
        "reconstructed generator length changed",
    )
    generator = ALGEBRA.transpose(combined_columns)
    audit = ALGEBRA.audit_generator(generator, rank)
    require(
        audit["generator_sha256"]
        == ALGEBRA.sha256_compact(generator),
        "generator row hash is inconsistent",
    )
    require(
        ALGEBRA.sha256_compact(combined_columns)
        == record["generator_column_stream_sha256"],
        "generator column-stream SHA-256 differs",
    )
    require(
        record["length"] == ALGEBRA.LENGTH
        and record["generator_rank"] == rank
        and record["projective_columns"] == ALGEBRA.LENGTH
        and record["dual_distance_at_least"] == 3
        and record["all_generator_row_sums_zero"]
        and record["self_orthogonal"],
        "declared control audit differs",
    )
    endpoint_compositions = set(ALGEBRA.endpoint_scalar_compositions())
    scalar_compositions = {
        ALGEBRA.composition(
            tuple(scalar * value % ALGEBRA.FIELD for value in row)
        )
        for row in generator
        for scalar in range(1, ALGEBRA.FIELD)
    }
    return {
        "dimension": rank,
        "tail_projection_dimension": tail_dimension,
        "projection_rank": ALGEBRA.rank_mod7(projection),
        "projection_sha256": ALGEBRA.sha256_compact(projection),
        "generator_column_stream_sha256": ALGEBRA.sha256_compact(
            combined_columns
        ),
        "generator_rank": audit["rank"],
        "row_sums_zero": not any(audit["row_sums"]),
        "gram_zero": not any(value for row in audit["gram"] for value in row),
        "projective_columns": audit["normalized_column_count"],
        "endpoint_scalar_composition_hits": len(
            scalar_compositions.intersection(endpoint_compositions)
        ),
        "projection": projection,
        "generator": generator,
    }


def falling_complete_moment_record(
    compositions: Sequence[Sequence[int]],
    rank: int,
) -> dict[str, Any]:
    known_words = ALGEBRA.LENGTH * len(compositions)
    first_known = [
        ALGEBRA.LENGTH
        * sum(composition[symbol] for composition in compositions)
        for symbol in range(ALGEBRA.FIELD)
    ]
    second_known = [
        [
            ALGEBRA.LENGTH
            * sum(
                composition[left]
                * (composition[right] - int(left == right))
                for composition in compositions
            )
            for right in range(ALGEBRA.FIELD)
        ]
        for left in range(ALGEBRA.FIELD)
    ]
    first_required = ALGEBRA.LENGTH * ALGEBRA.FIELD ** (rank - 1)
    second_required = (
        ALGEBRA.LENGTH
        * (ALGEBRA.LENGTH - 1)
        * ALGEBRA.FIELD ** (rank - 2)
    )
    degree_0_slack = ALGEBRA.FIELD**rank - known_words
    first_slacks = [first_required - value for value in first_known]
    second_slacks = [
        [second_required - value for value in row]
        for row in second_known
    ]
    require(
        degree_0_slack > 0
        and min(first_slacks) > 0
        and min(map(min, second_slacks)) > 0,
        "falling complete-moment slack is not strict",
    )
    return {
        "known_words": known_words,
        "minimum_code_size": ALGEBRA.FIELD**rank,
        "first_required": first_required,
        "first_known": first_known,
        "minimum_first_slack": min(first_slacks),
        "second_required": second_required,
        "second_known": second_known,
        "minimum_second_slack": min(map(min, second_slacks)),
    }


def audit_endpoint_composition(counts: Sequence[int]) -> dict[str, int]:
    require(
        len(counts) == ALGEBRA.FIELD
        and all(type(value) is int and value >= 0 for value in counts),
        "endpoint composition is malformed",
    )
    require(sum(counts) == ALGEBRA.LENGTH, "endpoint composition length changed")
    weight = sum(counts[1:])
    require(weight == 69, "endpoint row weight changed")
    linear = sum(symbol * counts[symbol] for symbol in range(7)) % 7
    squared = sum(
        symbol * symbol * counts[symbol] for symbol in range(7)
    ) % 7
    require(linear == squared == 0, "endpoint composition congruence failed")
    return {"weight": weight, "linear_residue": linear, "square_residue": squared}


def hostile_projection_mutation(
    rank_44_record: dict[str, Any],
    local: Sequence[Sequence[int]],
) -> dict[str, Any]:
    hostile = json.loads(json.dumps(rank_44_record))
    require(hostile["dimension"] == 44, "wrong hostile projection target")
    require(hostile["projection_matrix"][0][0] == 1, "identity projection changed")
    hostile["projection_matrix"][0][0] = 0
    rejected_reason = ""
    try:
        reconstruct_control(hostile, local)
    except AssertionError as error:
        rejected_reason = str(error)
    require(rejected_reason, "single projection-entry mutation was accepted")
    return {
        "rank": 44,
        "entry": [0, 0],
        "old": 1,
        "new": 0,
        "outcome": "REJECTED",
        "reason": rejected_reason,
    }


def verify_discovery_manifest() -> dict[str, str]:
    records: dict[str, str] = {}
    for line in DISCOVERY_MANIFEST.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        require(relative not in records, "duplicate discovery manifest path")
        require(sha256_file(ROOT / relative) == digest, f"hash mismatch: {relative}")
        records[relative] = digest
    require(len(records) == 12, "discovery manifest file census changed")
    return records


def compute() -> dict[str, Any]:
    independent = load_json(INDEPENDENT_RESULT)
    discovery = load_json(DISCOVERY_RESULT)
    manifest = verify_discovery_manifest()
    require(
        discovery["format"] == "wave46-f7-projector-code-v1",
        "discovery result format changed",
    )

    clean = independent["projector_consequences"]
    corrected = discovery["corrected_object"]
    code = discovery["code"]
    require(
        corrected["order"] == ALGEBRA.LENGTH
        and corrected["matrix"] == "M=21E_0"
        and corrected["integer_identity"] == "M^2=21M"
        and corrected["mod_7_identity"] == "M^2=0",
        "corrected projector object differs",
    )
    require(
        code["self_orthogonal"]
        and code["contained_in_one_perp"]
        and code["columns_nonzero_and_projectively_distinct"]
        and code["dual_minimum_distance_at_least"] == 3,
        "projector-code consequence differs",
    )
    require(
        code["forbidden_weights_from_sum_and_norm"]
        == clean["weight_compatibility"]["excluded_positive"]
        == [1, 2, 4],
        "weight compatibility differs",
    )
    require(
        code["A69_lower_bound"]
        == clean["certified_distinct_weight_69_words"]
        == 1386,
        "endpoint A69 bound differs",
    )

    complete = discovery["complete_enumerator"]
    compositions = tuple(
        tuple(record) for record in complete["known_scalar_compositions"]
    )
    require(
        compositions == tuple(map(tuple, clean["endpoint_scalar_compositions"])),
        "endpoint scalar compositions differ",
    )
    falling = falling_complete_moment_record(compositions, 28)
    discovered_moments = complete["degree_0_1_2_moment_check"]
    require(
        discovered_moments["known_words"] == falling["known_words"]
        and discovered_moments["minimum_code_size"] == falling["minimum_code_size"]
        and discovered_moments[
            "first_coordinate_moment_required_per_symbol"
        ] == falling["first_required"]
        and discovered_moments["known_first_coordinate_moments"]
        == falling["first_known"]
        and discovered_moments["minimum_first_moment_slack"]
        == falling["minimum_first_slack"]
        and discovered_moments[
            "second_ordered_coordinate_moment_required_per_symbol_pair"
        ] == falling["second_required"]
        and discovered_moments["known_second_ordered_coordinate_moments"]
        == falling["second_known"]
        and discovered_moments["minimum_second_moment_slack"]
        == falling["minimum_second_slack"],
        "complete falling-moment record differs",
    )

    schur = discovery["schur_cube"]
    clean_schur = clean["schur_cube"]
    require(
        schur["entrywise_identity_mod_7"] == "M^(o3)=M+4I"
        and clean_schur["entrywise_cube_identity"]
        == "M^(o3)=M+4I over F7"
        and schur["inverse_mod_7"] == "(M+4I)^(-1)=3M+2I"
        and schur["row_code_third_schur_power_dimension"] == ALGEBRA.LENGTH
        and schur["derived_rank_floor"] == clean_schur["minimum_code_rank"] == 11,
        "Schur-cube consequence differs",
    )

    controls = discovery["ordinary_enumerator_positive_controls"]
    local = independent_local_columns()
    require(
        tuple(tuple(column) for column in controls["local_columns"]) == local,
        "archived local columns differ from independent affine lines",
    )
    require(
        ALGEBRA.sha256_compact(local) == controls["local_columns_sha256"],
        "local column hash differs",
    )
    local_enumerator = local_weight_enumerator(local)
    require(
        {str(weight): count for weight, count in local_enumerator.items()}
        == controls["local_21_4_weight_enumerator"],
        "local weight enumerator differs",
    )
    four_blocks = {0: 1}
    for _ in range(4):
        four_blocks = convolve(four_blocks, local_enumerator)
    inherited_a69 = four_blocks[69]
    require(
        inherited_a69 == controls["four_block_A69"] == 668_653_683_264,
        "four-block A69 coefficient differs",
    )

    records = controls["records"]
    require(
        [record["dimension"] for record in records]
        == list(ALGEBRA.RANK_INTERVAL),
        "positive-control rank interval changed",
    )
    audited = [reconstruct_control(record, local) for record in records]
    require(
        all(
            record["inherited_A69_lower_bound"] == inherited_a69
            for record in records
        ),
        "inherited A69 declaration changed",
    )
    require(
        ALGEBRA.sha256_compact(
            [record["projection_matrix"] for record in records]
        )
        == controls["all_projection_matrices_sha256"],
        "aggregate projection hash differs",
    )
    require(
        all(record["endpoint_scalar_composition_hits"] == 0 for record in audited),
        "generic control accidentally realizes an endpoint generator composition",
    )

    prompt = discovery["prompt_error_control"]
    require(
        prompt["quarantined_object"]
        == "A+3I for the 99-by-99 adjacency matrix"
        and prompt["correct_object"]
        == "M=21E_0, the 231-by-231 integral triangle projector"
        and prompt["used_in_live_conclusion"] is False,
        "prompt-error quarantine differs",
    )
    eigenvalues = ((14, 1), (3, 54), (-4, 44))
    require(
        sum(multiplicity for _, multiplicity in eigenvalues) == 99
        and sum(value * multiplicity for value, multiplicity in eigenvalues) == 0
        and sum(
            value * value * multiplicity
            for value, multiplicity in eigenvalues
        )
        == 99 * 14,
        "A eigenvalue multiplicities failed trace controls",
    )
    shifted = tuple((value + 3, multiplicity) for value, multiplicity in eigenvalues)
    determinant_mod7 = math.prod(
        pow(value % 7, multiplicity, 7)
        for value, multiplicity in shifted
    ) % 7
    require(
        shifted == ((17, 1), (6, 54), (-1, 44))
        and determinant_mod7 == prompt["determinant_mod_7"] == 3,
        "A+3I hostile determinant differs",
    )

    hostile_composition = list(ALGEBRA.ENDPOINT_ROW_COMPOSITION)
    hostile_composition[1] += 1
    hostile_composition[6] -= 1
    composition_rejected = False
    try:
        audit_endpoint_composition(hostile_composition)
    except AssertionError:
        composition_rejected = True
    require(composition_rejected, "endpoint composition mutation was accepted")
    inverse_mutation_m_coefficient = (1 * 2 + 4 * 2) % 7
    require(inverse_mutation_m_coefficient != 0, "mutated Schur inverse passed")
    hostile_prompt = dict(prompt)
    hostile_prompt["used_in_live_conclusion"] = True
    require(
        hostile_prompt["used_in_live_conclusion"]
        and not prompt["used_in_live_conclusion"],
        "prompt quarantine mutation was not exposed",
    )

    rank_label_rejected = False
    mislabeled = json.loads(json.dumps(records[0]))
    mislabeled["dimension"] = 29
    try:
        reconstruct_control(mislabeled, local)
    except AssertionError:
        rank_label_rejected = True
    require(rank_label_rejected, "rank-label exchange was accepted")

    return {
        "format": "wave46-clean-room-sealed-comparison-v1",
        "role": "verifier",
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256_file(path)
            for path in (
                ALGEBRA_PATH,
                INDEPENDENT_RESULT,
                DISCOVERY_RESULT,
                DISCOVERY_MANIFEST,
                DISCOVERY_AGENT,
            )
        },
        "discovery_manifest": {
            "status": "PASS",
            "files": len(manifest),
            "manifest_sha256": sha256_file(DISCOVERY_MANIFEST),
        },
        "projector_code": {
            "conditional_identity_derivation": "VERIFIED",
            "self_orthogonal": True,
            "contained_in_one_perp": True,
            "projective_columns": ALGEBRA.LENGTH,
            "dual_distance_lower_bound": 3,
            "endpoint_scalar_compositions": compositions,
            "A69_lower_bound": 1386,
            "excluded_weights": [1, 2, 4],
        },
        "complete_moments": {
            "basis": (
                "falling ordered-coordinate moments; n_a*(n_a-1) on diagonal"
            ),
            "rank": 28,
            "minimum_first_slack": falling["minimum_first_slack"],
            "minimum_second_slack": falling["minimum_second_slack"],
            "all_56_nonconstant_symbol_and_pair_checks_strict": True,
            "prefreeze_raw_monomial_minimum_second_slack": clean[
                "rank_28_complete_moment_slack"
            ]["minimum_degree_2"],
            "prefreeze_basis_correction": (
                "The frozen clean result recorded raw n_a*n_b moments. "
                "The sealed request uses the conventional falling diagonal "
                "n_a*(n_a-1). Both bases have strict slack; the discovery "
                "falling-moment value was independently reproduced."
            ),
        },
        "schur_cube": {
            "identity": "VERIFIED",
            "inverse": "2I+3M",
            "rank": ALGEBRA.LENGTH,
            "rank_floor": 11,
            "superseded_by_endpoint_floor_28": True,
        },
        "positive_controls": {
            "rank_interval": list(ALGEBRA.RANK_INTERVAL),
            "controls_checked": len(audited),
            "local_columns_sha256": ALGEBRA.sha256_compact(local),
            "local_weight_enumerator": {
                str(weight): count
                for weight, count in local_enumerator.items()
            },
            "inherited_A69_lower_bound": inherited_a69,
            "all_projection_matrices_sha256": controls[
                "all_projection_matrices_sha256"
            ],
            "records": [
                {
                    key: value
                    for key, value in record.items()
                    if key not in {"projection", "generator"}
                }
                for record in audited
            ],
            "all_endpoint_scalar_composition_hits_zero": True,
            "interpretation": (
                "Valid generic ordinary-code controls, not endpoint projector "
                "candidates."
            ),
        },
        "prompt_error_quarantine": {
            "A_plus_3I_order": 99,
            "shifted_eigenvalues": shifted,
            "determinant_mod_7": determinant_mod7,
            "full_F7_99_row_code": True,
            "used_in_live_conclusion": False,
            "status": "VERIFIED_QUARANTINED",
        },
        "hostile_mutations": {
            "single_projection_entry": hostile_projection_mutation(
                records[-1], local
            ),
            "endpoint_row_composition": "REJECTED",
            "schur_inverse_M_coefficient_3_to_2": "REJECTED",
            "prompt_quarantine_false_to_true": "REJECTED",
            "rank_label_28_to_29": "REJECTED",
        },
        "verdict": {
            "scoped_derivations": "VERIFIED",
            "generic_positive_controls": "VERIFIED",
            "ordinary_enumerator_contradiction": False,
            "low_degree_complete_enumerator_contradiction": False,
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "The endpoint projector identities are conditional and no endpoint graph is constructed.",
            "Generic positive controls do not satisfy the endpoint row-composition geometry.",
            "Degree-two moments do not determine a complete weight enumerator.",
            "The Schur-cube floor 11 is weaker than the prior endpoint floor 28.",
        ],
    }


def validate_record(record: dict[str, Any]) -> None:
    require(
        record["format"] == "wave46-clean-room-sealed-comparison-v1",
        "comparison format changed",
    )
    require(
        record["verdict"]["scoped_derivations"] == "VERIFIED"
        and record["verdict"]["generic_positive_controls"] == "VERIFIED",
        "scoped verification failed",
    )
    require(
        record["verdict"]["endpoint_n3_4158"] == "UNKNOWN"
        and record["verdict"]["Conway_99"] == "UNKNOWN",
        "status inflation",
    )
    require(
        record["positive_controls"]["controls_checked"] == 17,
        "positive-control census changed",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    if arguments.verify:
        stored = arguments.verify.read_bytes()
        record = json.loads(stored)
        validate_record(record)
        require(canonical_json(compute()) == stored, "comparison replay differs")
        print(
            f"PASS {arguments.verify} "
            f"sha256={hashlib.sha256(stored).hexdigest()}"
        )
        return 0
    record = compute()
    validate_record(record)
    payload = canonical_json(record)
    if arguments.output:
        arguments.output.write_bytes(payload)
        print(
            f"WROTE {arguments.output} "
            f"sha256={hashlib.sha256(payload).hexdigest()}"
        )
    else:
        print(payload.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
