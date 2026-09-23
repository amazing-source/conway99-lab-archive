#!/usr/bin/env python3
"""Post-freeze comparison of Wave 45 discovery against clean-room matrices."""

from __future__ import annotations

import argparse
import functools
import hashlib
import importlib.util
import json
import math
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INDEPENDENT_CODE = HERE / "independent_verify.py"
INDEPENDENT_RESULT = HERE / "independent-results.json"
DISCOVERY_DIR = ROOT / "attempts/wave45-flag-moment"
DISCOVERY_COEFFICIENTS = (
    DISCOVERY_DIR / "checkpoint-v1-moment-coefficients.json"
)
DISCOVERY_RESULT = (
    DISCOVERY_DIR / "checkpoint-v1-stored-witness-results.json"
)
CUTTING_RESULT = (
    DISCOVERY_DIR / "checkpoint-v1-seed0-17cuts-15witnesses.json"
)
CHECKPOINT_MANIFEST = DISCOVERY_DIR / "checkpoint-v1-manifest.sha256"
W43_RESULT = ROOT / "attempts/wave43-seven-deck-endpoint/exact-results.json"
W44_WITNESS = ROOT / "attempts/wave44-rooted-flags/rooted-witness.json"
W44_ROWS = ROOT / "attempts/wave44-rooted-flags/row-system.json"
FAMILY_MAP = {
    "vertex": "vertex",
    "edge": "ordered_edge",
    "nonedge": "ordered_nonedge",
}


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


INDEPENDENT = load_module("wave45_clean_frozen", INDEPENDENT_CODE)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_compact(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, separators=(",", ": "))
        + "\n"
    ).encode("utf-8")


def expand_upper(size: int, entries: Sequence[Sequence[int]]) -> list[list[int]]:
    matrix = [[0] * size for _ in range(size)]
    for row, column, value in entries:
        require(
            type(row) is int
            and type(column) is int
            and type(value) is int
            and 0 <= row <= column < size,
            "malformed upper-triangle entry",
        )
        require(matrix[row][column] == 0, "duplicate upper-triangle entry")
        matrix[row][column] = value
        matrix[column][row] = value
    return matrix


def convert_discovery_stream(
    family_record: dict[str, Any],
) -> list[dict[str, Any]]:
    size = family_record["matrix_size"]
    converted: list[dict[str, Any]] = []
    for record in family_record["class_coefficients"]:
        matrix = expand_upper(size, record["upper_entries"])
        converted.append(
            {
                "order": record["order"],
                "canonical_mask": record["canonical_mask"],
                "entries": INDEPENDENT.sparse_entries(matrix),
            }
        )
    return converted


def coefficient_lookup(
    stream: Sequence[dict[str, Any]],
    dimension: int,
) -> dict[tuple[int, int], list[list[int]]]:
    lookup: dict[tuple[int, int], list[list[int]]] = {}
    for record in stream:
        key = (record["order"], record["canonical_mask"])
        require(key not in lookup, "duplicate coefficient class")
        matrix = [[0] * dimension for _ in range(dimension)]
        for row, column, value in record["entries"]:
            matrix[row][column] = value
        lookup[key] = matrix
    return lookup


def seven_counts(path: Path, class_masks: Sequence[int]) -> Counter[int]:
    payload = load_json(path)
    certificate = payload.get("certificate", payload)
    support = certificate["support"]
    counts: Counter[int] = Counter()
    allowed = set(class_masks)
    for record in support:
        mask, count = record["canonical_mask"], record["count"]
        require(
            mask in allowed and mask not in counts and type(count) is int and count > 0,
            f"malformed support in {path}",
        )
        counts[mask] = count
    require(sum(counts.values()) == math.comb(99, 7), "seven-count total changed")
    return counts


def exact_ldl_psd(matrix: Sequence[Sequence[int]]) -> dict[str, Any]:
    size = len(matrix)
    lower = [
        [Fraction(int(row == column)) for column in range(size)]
        for row in range(size)
    ]
    diagonal = [Fraction(0) for _ in range(size)]
    for pivot in range(size):
        diagonal[pivot] = Fraction(matrix[pivot][pivot]) - sum(
            lower[pivot][prior] ** 2 * diagonal[prior]
            for prior in range(pivot)
        )
        residuals = [
            (
                row,
                Fraction(matrix[row][pivot])
                - sum(
                    lower[row][prior]
                    * lower[pivot][prior]
                    * diagonal[prior]
                    for prior in range(pivot)
                ),
            )
            for row in range(pivot + 1, size)
        ]
        if diagonal[pivot] < 0:
            return {"is_psd": False, "negative_pivot_index": pivot}
        if diagonal[pivot] == 0:
            if any(value for _, value in residuals):
                return {"is_psd": False, "zero_pivot_nonzero_column": pivot}
            continue
        for row, residual in residuals:
            lower[row][pivot] = residual / diagonal[pivot]
    return {
        "is_psd": True,
        "rank": sum(value > 0 for value in diagonal),
    }


def normalized_cut(
    direction: Sequence[int],
    vertex_lookup: dict[tuple[int, int], list[list[int]]],
    lower_counts: dict[int, Counter[int]],
    classes7: Sequence[int],
) -> dict[str, Any]:
    constant = sum(
        count * INDEPENDENT.quadratic(vertex_lookup[(order, mask)], direction)
        for order in range(4, 7)
        for mask, count in lower_counts[order].items()
    )
    dense = [
        INDEPENDENT.quadratic(vertex_lookup[(7, mask)], direction)
        for mask in classes7
    ]
    divisor = math.gcd(abs(constant), *map(abs, dense))
    require(divisor > 0, "zero moment cut")
    core = {
        "family": "vertex",
        "direction": list(direction),
        "constant": constant // divisor,
        "coefficients": [
            {
                "canonical_mask": mask,
                "coefficient": coefficient // divisor,
            }
            for mask, coefficient in zip(classes7, dense)
            if coefficient
        ],
        "primitive_divisor": divisor,
        "sense": "constant + sum(coefficient*x_mask) >= 0",
    }
    return {**core, "cut_sha256": sha256_compact(core)}


def cut_value(
    cut: dict[str, Any],
    counts: Counter[int],
) -> int:
    return cut["constant"] + sum(
        record["coefficient"] * counts[record["canonical_mask"]]
        for record in cut["coefficients"]
    )


def support_counts(
    support: Sequence[dict[str, int]],
    class_masks: Sequence[int],
) -> Counter[int]:
    allowed = set(class_masks)
    counts: Counter[int] = Counter()
    for record in support:
        mask, count = record["canonical_mask"], record["count"]
        require(
            mask in allowed and mask not in counts and type(count) is int and count > 0,
            "malformed cutting witness support",
        )
        counts[mask] = count
    return counts


def verify_original_rows(
    witness: dict[str, Any],
    counts: Counter[int],
    row_system: dict[str, Any],
) -> None:
    classes = row_system["classes"]
    vector = [counts[mask] for mask in classes] + [witness["h11"] // 4]
    require(witness["h11"] % 4 == 0, "cutting witness h11 is malformed")
    for family in ("base", "vertex", "edge", "nonedge"):
        rows = row_system["families"][family]["rows"]
        rhs = row_system["families"][family]["rhs"]
        for row, target in zip(rows, rhs):
            require(
                sum(value * coefficient for value, coefficient in zip(vector, row))
                == target,
                "cutting witness violates an original exact row",
            )


def compute() -> dict[str, Any]:
    independent = load_json(INDEPENDENT_RESULT)
    discovery_coefficients = load_json(DISCOVERY_COEFFICIENTS)
    discovery_result = load_json(DISCOVERY_RESULT)
    cutting = load_json(CUTTING_RESULT)
    row_system = load_json(W44_ROWS)
    require(
        cutting["format"] == "wave45-immutable-cutting-checkpoint-v1",
        "wrong immutable checkpoint format",
    )
    manifest_records: dict[str, str] = {}
    for line in CHECKPOINT_MANIFEST.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        require(relative not in manifest_records, "duplicate checkpoint manifest path")
        manifest_records[relative] = digest
        require(
            sha256_file(ROOT / relative) == digest,
            f"checkpoint manifest mismatch for {relative}",
        )
    require(
        manifest_records
        == {
            "attempts/wave45-flag-moment/checkpoint-v1-seed0-17cuts-15witnesses.json":
                "96a50f9add4b12b2c86587da29ade8b9da34f88a7b7617c048ffb7139c12b64b",
            "attempts/wave45-flag-moment/checkpoint-v1-moment-coefficients.json":
                "ffcf9f9942446d66c3559d97954217af3ba17c1978ea9417c6e99920d4a45420",
            "attempts/wave45-flag-moment/checkpoint-v1-stored-witness-results.json":
                "2c55b6ab1af9cac7d8f5800466abadb8c0c2603b5f96013d3fd160b6816c24df",
        },
        "immutable checkpoint manifest content changed",
    )

    coefficient_copy = dict(discovery_coefficients)
    stored_payload_hash = coefficient_copy.pop(
        "coefficient_payload_sha256_without_this_field"
    )
    require(
        sha256_compact(coefficient_copy) == stored_payload_hash,
        "discovery coefficient payload hash failed",
    )
    require(
        discovery_result["coefficient_model"]["payload_sha256"]
        == stored_payload_hash,
        "result coefficient payload hash differs",
    )

    converted: dict[str, list[dict[str, Any]]] = {}
    family_comparison: dict[str, Any] = {}
    for clean_name, discovery_name in FAMILY_MAP.items():
        clean_record = independent["flag_sets"][clean_name]
        discovery_family = discovery_coefficients["families"][discovery_name]
        require(
            clean_record["canonical_masks"] == discovery_family["flags"],
            f"{clean_name} flag order differs",
        )
        stream = convert_discovery_stream(discovery_family)
        converted[clean_name] = stream
        clean_stream = independent["coefficient_streams"][clean_name]
        require(stream == clean_stream, f"{clean_name} coefficient stream differs")
        family_comparison[clean_name] = {
            "flags_exact_match": True,
            "records": len(stream),
            "entrywise_coefficient_match": True,
            "converted_stream_sha256": sha256_compact(stream),
        }
    require(
        sha256_compact(converted)
        == independent["sha256"]["coefficient_streams"]["combined"],
        "combined converted coefficient stream differs",
    )

    independent_controls = {
        control["name"]: control for control in independent["controls"]
    }
    for discovery_control in discovery_result["controls"]["known_srgs"]:
        clean_control = independent_controls[discovery_control["name"]]
        require(
            discovery_control["srg_parameters"] == clean_control["srg_parameters"],
            "control SRG parameters differ",
        )
        for clean_name, discovery_name in FAMILY_MAP.items():
            discovered = discovery_control["families"][discovery_name]
            clean = clean_control["root_types"][clean_name]
            require(
                discovered["direct_equals_unrooted_expansion"]
                and clean["direct_equals_linear"]
                and discovered["raw_matrix_sha256"] == clean["matrix_sha256"],
                f"{discovery_control['name']} {clean_name} control differs",
            )

    class_sets = {
        int(order): tuple(masks)
        for order, masks in independent["unrooted_class_sets"].items()
    }
    require(tuple(row_system["classes"]) == class_sets[7], "class order differs")
    target_counts = {
        "wave43_unrooted": seven_counts(W43_RESULT, class_sets[7]),
        "wave44_rooted": seven_counts(W44_WITNESS, class_sets[7]),
    }
    lower_counts = {
        target: INDEPENDENT.derive_lower_counts_from_seven(
            counts, 99, class_sets
        )
        for target, counts in target_counts.items()
    }
    for order in range(4, 7):
        require(
            lower_counts["wave43_unrooted"][order]
            == lower_counts["wave44_rooted"][order],
            "target lower-order counts differ",
        )
    common_lower = lower_counts["wave43_unrooted"]
    lookups = {
        clean_name: coefficient_lookup(
            independent["coefficient_streams"][clean_name],
            len(independent["flag_sets"][clean_name]["canonical_masks"]),
        )
        for clean_name in FAMILY_MAP
    }

    target_comparison: dict[str, Any] = {}
    supplied_directions: dict[str, list[dict[str, Any]]] = {
        target: [] for target in target_counts
    }
    for record in discovery_result["exact_negative_directions"]:
        require(
            record["family"] == "vertex" and record["target"] in supplied_directions,
            "unexpected stored-witness direction scope",
        )
        supplied_directions[record["target"]].append(record)
    for target, seven_count in target_counts.items():
        all_counts = dict(lower_counts[target])
        all_counts[7] = seven_count
        family_records: dict[str, Any] = {}
        discovery_target = discovery_result["targets"][target]
        for clean_name, discovery_name in FAMILY_MAP.items():
            dimension = len(independent["flag_sets"][clean_name]["canonical_masks"])
            matrix = INDEPENDENT.evaluate_stream(
                independent["coefficient_streams"][clean_name],
                all_counts,
                dimension,
            )
            matrix_hash = sha256_compact(matrix)
            discovered_family = discovery_target["families"][discovery_name]
            require(
                matrix_hash == discovered_family["raw_matrix_sha256"],
                f"{target} {clean_name} matrix differs",
            )
            ldl = exact_ldl_psd(matrix)
            expected_psd = clean_name != "vertex"
            require(
                ldl["is_psd"] == expected_psd,
                f"{target} {clean_name} exact PSD classification differs",
            )
            family_records[clean_name] = {
                "matrix_sha256": matrix_hash,
                "exact_psd": ldl,
            }
        vertex_matrix = INDEPENDENT.evaluate_stream(
            independent["coefficient_streams"]["vertex"],
            all_counts,
            17,
        )
        direction_records = supplied_directions[target]
        require(len(direction_records) == 6, "stored direction census changed")
        quadratics = []
        for direction_record in direction_records:
            quadratic = INDEPENDENT.quadratic(
                vertex_matrix, direction_record["vector"]
            )
            require(
                quadratic == direction_record["quadratic_numerator"] < 0,
                f"{target} negative quadratic differs",
            )
            quadratics.append(quadratic)
        target_comparison[target] = {
            "lower_order_deck_reconstruction": "PASS",
            "families": family_records,
            "negative_direction_count": len(direction_records),
            "exact_vertex_quadratics": quadratics,
        }

    cuts = cutting["cuts"]
    witnesses = cutting["witnesses"]
    require(len({cut["cut_sha256"] for cut in cuts}) == len(cuts), "duplicate cut")
    reconstructed_cuts: list[dict[str, Any]] = []
    for cut in cuts:
        rebuilt = normalized_cut(
            cut["direction"],
            lookups["vertex"],
            common_lower,
            class_sets[7],
        )
        require(
            all(cut[key] == rebuilt[key] for key in rebuilt),
            f"cut {cut['cut_sha256']} differs from independent coefficients",
        )
        reconstructed_cuts.append(rebuilt)

    source_counts = dict(target_counts)
    minimum_new_cut_violation: int | None = None
    for witness in witnesses:
        iteration = witness["iteration"]
        counts = support_counts(witness["support"], class_sets[7])
        require(
            sum(counts.values()) == math.comb(99, 7),
            "cutting witness total changed",
        )
        require(
            sha256_compact(witness["support"]) == witness["support_sha256"],
            "cutting witness support hash failed",
        )
        verify_original_rows(witness, counts, row_system)
        retained_count = 2 + iteration
        require(
            witness["exact_replay"]["retained_cut_count"] == retained_count,
            "retained-cut count differs",
        )
        retained_values = [
            cut_value(cut, counts) for cut in cuts[:retained_count]
        ]
        require(min(retained_values, default=0) >= 0, "retained cut violated")
        require(
            sha256_compact(retained_values)
            == witness["exact_replay"]["cut_values_sha256"],
            "retained cut-value hash differs",
        )
        require(
            min(retained_values, default=0)
            == witness["exact_replay"]["minimum_retained_cut_value"],
            "minimum retained cut value differs",
        )
        all_counts = dict(common_lower)
        all_counts[7] = counts
        matrix = INDEPENDENT.evaluate_stream(
            independent["coefficient_streams"]["vertex"],
            all_counts,
            17,
        )
        moment = witness["vertex_moment"]
        require(
            sha256_compact(matrix) == moment["raw_matrix_sha256"],
            "cutting witness vertex matrix differs",
        )
        direction = moment["exact_negative_direction"]
        require(direction is not None, "cutting witness lacks negative direction")
        value = INDEPENDENT.quadratic(matrix, direction["vector"])
        require(
            value == direction["quadratic_numerator"] < 0,
            "cutting witness negative quadratic differs",
        )
        new_cut_value = cut_value(cuts[retained_count], counts)
        require(new_cut_value < 0, "new cut does not reject source witness")
        minimum_new_cut_violation = (
            new_cut_value
            if minimum_new_cut_violation is None
            else min(minimum_new_cut_violation, new_cut_value)
        )
        source_counts[f"iteration_{iteration}"] = counts

    require(
        cut_value(cuts[0], target_counts["wave43_unrooted"]) < 0
        and cut_value(cuts[1], target_counts["wave44_rooted"]) < 0,
        "initial cuts do not reject their named witnesses",
    )
    require(
        cutting["status"] == "QF_LIA_UNKNOWN"
        and cutting["z3"]["last_status"] == "unknown"
        and cutting["scope_wall"]["endpoint_n3_4158"] == "UNKNOWN",
        "cutting-loop final status differs",
    )
    return {
        "format": "wave45-clean-room-discovery-comparison-v1",
        "role": "verifier",
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256_file(path)
            for path in (
                INDEPENDENT_CODE,
                INDEPENDENT_RESULT,
                DISCOVERY_COEFFICIENTS,
                DISCOVERY_RESULT,
                CUTTING_RESULT,
                CHECKPOINT_MANIFEST,
                W43_RESULT,
                W44_WITNESS,
                W44_ROWS,
            )
        },
        "coefficient_comparison": {
            "discovery_payload_hash": stored_payload_hash,
            "families": family_comparison,
            "combined_entrywise_match": True,
            "converted_combined_stream_sha256": sha256_compact(converted),
        },
        "control_comparison": {
            "Petersen": "EXACT_MATRIX_MATCH",
            "Clebsch": "EXACT_MATRIX_MATCH",
        },
        "target_comparison": target_comparison,
        "cutting_loop": {
            "immutable_checkpoint_manifest": "PASS",
            "cut_count": len(cuts),
            "witness_count": len(witnesses),
            "all_cut_streams_reconstructed": True,
            "all_witnesses_pass_original_170_rows": True,
            "all_witnesses_pass_prior_cuts": True,
            "all_new_cuts_exactly_reject_source": True,
            "minimum_new_cut_value": minimum_new_cut_violation,
            "final_status": cutting["status"],
            "last_solver_status": cutting["z3"]["last_status"],
            "last_reason_unknown": cutting["z3"]["last_reason_unknown"],
            "solver_unknown_is_not_certificate": True,
            "resource_samples_in_immutable_checkpoint": False,
        },
        "verdict": {
            "coefficient_streams": "VERIFIED_EXACT_MATCH",
            "controls": "VERIFIED_EXACT_MATCH",
            "stored_wave43_witness": "REFUTED_BY_EXACT_PSD_DIRECTION",
            "stored_wave44_witness": "REFUTED_BY_EXACT_PSD_DIRECTION",
            "finite_cutting_loop": "VERIFIED_INCOMPLETE_UNKNOWN",
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "Conway_99": "UNKNOWN",
        },
        "limitations": [
            "The exact negative directions refute only the supplied aggregate witnesses.",
            "The 17-cut loop ended solver-unknown and did not exhaust the PSD-feasible region.",
            "No graph or complete infeasibility certificate was produced.",
        ],
    }


def validate_record(record: dict[str, Any]) -> None:
    require(
        record["format"] == "wave45-clean-room-discovery-comparison-v1",
        "comparison format changed",
    )
    require(
        record["verdict"]["coefficient_streams"] == "VERIFIED_EXACT_MATCH",
        "coefficient comparison failed",
    )
    require(
        record["verdict"]["finite_cutting_loop"]
        == "VERIFIED_INCOMPLETE_UNKNOWN",
        "cutting status inflation",
    )
    require(
        record["verdict"]["endpoint_n3_4158"] == "UNKNOWN"
        and record["verdict"]["Conway_99"] == "UNKNOWN",
        "endpoint status inflation",
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
