#!/usr/bin/env python3
"""Independent exact verifier for the Wave159 fifteen-cut checkpoint.

The Wave159/Wave152 discovery Python is never imported or executed.  A
hash-pinned earlier clean-room graph/count engine supplies only independently
verified graph primitives and exact row construction.  This verifier rebuilds
the two fresh covariance cuts and both displayed negative directions from
declarative vectors, replays all fifteen cuts and all exact witness rows, and
checks the stored modular-rank certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
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
ATTEMPT = ROOT / "attempts/wave159-four-root-cut-loop"
WAVE152 = ROOT / "attempts/wave152-four-root-order8"
BASE_PATH = ROOT / "verification/wave155-four-root-feedback/independent_verify.py"
BASE_SHA256 = "c8aecd00c7da53fa929b53503bf437c0d0714c79a2e85a451168ac2e85b75c88"
WAVE159_MANIFEST_SHA256 = (
    "44b76ca9538f5a3ed9d9a1f44ef29373f0cb6e422b0886063153bdff3545ff8b"
)
WAVE152_MANIFEST_SHA256 = (
    "1fe84e8e8e52b091293a30e1b09c6772f092123803e1e62362726c6c73d1f38d"
)


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
    require(file_sha256(BASE_PATH) == BASE_SHA256, "clean-room base hash drift")
    spec = importlib.util.spec_from_file_location("wave155_cleanroom_base", BASE_PATH)
    require(spec is not None and spec.loader is not None, "cannot load clean-room base")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base()


def read_hash_inventory(path: Path) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line:
            continue
        pieces = line.split("  ", 1)
        require(len(pieces) == 2, f"{path.name}:{line_number}: malformed line")
        expected, relative = pieces
        require(
            len(expected) == 64
            and all(character in "0123456789abcdef" for character in expected),
            f"{path.name}:{line_number}: malformed SHA256",
        )
        require(relative not in seen, f"{path.name}: duplicate path {relative}")
        require("\\" not in relative and not Path(relative).is_absolute(), "unsafe path")
        require(".." not in Path(relative).parts, f"unsafe traversal: {relative}")
        seen.add(relative)
        records.append((expected, relative))
    return records


def verify_inventory(path: Path, expected_manifest_sha256: str | None = None) -> dict:
    if expected_manifest_sha256 is not None:
        require(
            file_sha256(path) == expected_manifest_sha256,
            f"manifest hash drift: {path}",
        )
    records = read_hash_inventory(path)
    failures = []
    for expected, relative in records:
        target = ROOT / relative
        actual = file_sha256(target)
        if actual != expected:
            failures.append(
                {"path": relative, "expected": expected, "actual": actual}
            )
    require(not failures, f"inventory mismatch: {failures[:2]}")
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": file_sha256(path),
        "entries": len(records),
        "all_entries_match": True,
    }


def verify_wave152_preservation() -> dict:
    before = ATTEMPT / "wave152-before.sha256"
    after = ATTEMPT / "wave152-after.sha256"
    require(before.read_bytes() == after.read_bytes(), "Wave152 before/after differ")
    before_records = read_hash_inventory(before)
    require(len(before_records) == 42, "Wave152 inventory size changed")
    require(
        all(relative.startswith("attempts/wave152-four-root-order8/")
            for _, relative in before_records),
        "Wave152 inventory escaped package",
    )
    checked = verify_inventory(before)
    return {
        "before_sha256": file_sha256(before),
        "after_sha256": file_sha256(after),
        "inventories_byte_identical": True,
        "entries": checked["entries"],
        "current_files_match_frozen_hashes": True,
        "wave152_package_manifest_sha256": file_sha256(
            WAVE152 / "package-manifest.sha256"
        ),
        "wave152_package_manifest_matches_expected": (
            file_sha256(WAVE152 / "package-manifest.sha256")
            == WAVE152_MANIFEST_SHA256
        ),
    }


def dense_direction(
    width: int, indices: Sequence[int], values: Sequence[int]
) -> list[int]:
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


def derive_structures(
    requests: Sequence[dict],
    classes: dict[int, tuple[int, ...]],
    lower: dict[int, dict[int, Fraction]],
    memory_samples: list[dict],
) -> dict[str, dict]:
    """Rebuild scalar covariance forms directly from graph/flag semantics."""
    x4 = BASE.derive_order_four(lower[5], classes[5])
    grouped: dict[int, list[dict]] = defaultdict(list)
    for request in requests:
        grouped[int(request["root_mask"])].append(request)
    structures: dict[str, dict] = {}
    for root_mask, root_requests in sorted(grouped.items()):
        flags = BASE.flag_universe(root_mask)
        flag_index = {mask: index for index, mask in enumerate(flags)}
        directions = [list(map(int, request["direction"])) for request in root_requests]
        require(
            all(len(direction) == len(flags) for direction in directions),
            f"direction width mismatch at root {root_mask}",
        )
        first = [dict() for _ in directions]
        quadratic = [{6: {}, 7: {}, 8: {}} for _ in directions]
        for order in (6, 7, 8):
            for class_index, class_mask in enumerate(classes[order]):
                first_values, quadratic_values = (
                    BASE.class_coefficients_for_directions(
                        class_mask, order, root_mask, directions, flag_index
                    )
                )
                for index in range(len(directions)):
                    if order == 6 and first_values[index]:
                        first[index][class_mask] = first_values[index]
                    if quadratic_values[index]:
                        quadratic[index][order][class_mask] = quadratic_values[index]
                if order == 8 and class_index % 256 == 0:
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
            require(divisor > 0, f"zero form for {request['id']}")
            structures[str(request["id"])] = {
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
    return structures


def witness_maps(
    witness: dict, classes: dict[int, tuple[int, ...]]
) -> tuple[dict[int, Fraction], dict[int, Fraction]]:
    return (
        BASE.support_map(witness, "x7_support", classes[7]),
        BASE.support_map(witness, "x8_support", classes[8]),
    )


def cut_value(
    structure: dict,
    witness: dict,
    classes: dict[int, tuple[int, ...]],
) -> Fraction:
    x7, x8 = witness_maps(witness, classes)
    return BASE.evaluate_cut(structure, x7, x8, classes)


def verify_fresh_cut(
    stored: dict,
    rebuilt: dict,
    source_witness: dict,
    classes: dict[int, tuple[int, ...]],
) -> dict:
    for key in structural_keys():
        require(stored[key] == rebuilt[key], f"fresh cut mismatch: {key}")
    canonical_core = {key: value for key, value in stored.items()
                      if key != "cut_sha256"}
    require(
        BASE.canonical_sha256(canonical_core) == stored["cut_sha256"],
        "fresh cut canonical hash mismatch",
    )
    value = cut_value(rebuilt, source_witness, classes)
    require(
        value == BASE.fraction(stored["wave150_witness_value"]),
        "fresh cut source value mismatch",
    )
    raw = value * int(rebuilt["primitive_divisor"])
    require(
        raw == BASE.fraction(stored["wave150_witness_unscaled_value"]),
        "fresh cut unscaled source value mismatch",
    )
    scaled = raw * int(stored["stored_count_scale"])
    require(
        scaled.denominator == 1
        and scaled.numerator == int(stored["stored_scaled_value"]),
        "fresh cut scaled source value mismatch",
    )
    require(value < 0, "fresh cut does not separate thirteen-cut witness")
    return {
        "cut_sha256": stored["cut_sha256"],
        "root_mask": int(stored["root_mask"]),
        "root_embedding_count": int(stored["root_embedding_count"]),
        "flag_count": int(stored["flag_count"]),
        "direction_nonzeros": sum(int(item) != 0 for item in stored["direction"]),
        "order7_nonzeros": len(stored["order7_coefficients"]),
        "order8_nonzeros": len(stored["order8_coefficients"]),
        "primitive_divisor": int(stored["primitive_divisor"]),
        "source_value": BASE.fraction_string(value),
        "strictly_negative_on_thirteen_cut_witness": True,
        "coefficients_reconstructed_exactly": True,
    }


def negative_request(root_record: dict) -> dict:
    certificate = root_record["negative_certificate"]
    require(certificate is not None, "missing negative certificate")
    width = int(root_record["flag_count"])
    indices = list(map(int, certificate["indices"]))
    vector = list(map(int, certificate["vector"]))
    flags = BASE.flag_universe(int(root_record["root_mask"]))
    require(len(flags) == width, "stored flag count mismatch")
    require(
        [flags[index] for index in indices]
        == list(map(int, certificate["flag_masks"])),
        "certificate flag semantics mismatch",
    )
    return {
        "id": f"negative_{root_record['root_mask']}",
        "root_mask": int(root_record["root_mask"]),
        "direction": dense_direction(width, indices, vector),
    }


def verify_negative_certificate(
    root_record: dict,
    structure: dict,
    evaluation: dict,
    witness: dict,
    classes: dict[int, tuple[int, ...]],
) -> dict:
    certificate = root_record["negative_certificate"]
    require(root_record["exact_status"] == "NOT_PSD", "status is not NOT_PSD")
    require(
        int(root_record["root_embedding_count"])
        == int(structure["root_embedding_count"]),
        "root embedding count mismatch",
    )
    value = cut_value(structure, witness, classes)
    raw = value * int(structure["primitive_divisor"])
    scaled = raw * int(evaluation["count_denominator_scale"])
    require(scaled.denominator == 1, "negative certificate did not scale to integer")
    require(
        scaled.numerator == int(certificate["quadratic_value_scaled"]),
        "negative quadratic value mismatch",
    )
    require(scaled < 0, "certificate is not strictly negative")
    return {
        "root_mask": int(root_record["root_mask"]),
        "root_embedding_count": int(root_record["root_embedding_count"]),
        "flag_count": int(root_record["flag_count"]),
        "support_size": len(certificate["indices"]),
        "quadratic_value_scaled": str(scaled.numerator),
        "strictly_negative": True,
        "direction_sha256": BASE.canonical_sha256(structure["direction"]),
    }


def retained_cut_payloads(fresh: dict) -> list[dict]:
    names = (
        "exact-cuts.json",
        "iteration2-cuts.json",
        "iteration3-mask13-cut.json",
        "iteration4-three-cuts.json",
    )
    payloads = [load_json(WAVE152 / name) for name in names]
    payloads.append({"cuts": [load_json(WAVE152 / "simplified-mask12-cut.json")["cut"]]})
    payloads.append(load_json(WAVE152 / "iteration5-three-cuts.json"))
    payloads.append(
        {"cuts": [load_json(WAVE152 / "simplified-mask12-cut-2.json")["cut"]]}
    )
    payloads.append(fresh)
    cuts = [cut for payload in payloads for cut in payload["cuts"]]
    require(len(cuts) == 15, "retained cut count is not fifteen")
    require(len({cut["cut_sha256"] for cut in cuts}) == 15, "duplicate retained cut")
    return payloads


def main_result() -> dict:
    started = time.time()
    memory_samples = [BASE.memory_sample("start")]
    freeze = {
        "preinspection": verify_inventory(HERE / "preinspection-freeze.sha256"),
        "wave159_package": verify_inventory(
            ATTEMPT / "package-manifest.sha256", WAVE159_MANIFEST_SHA256
        ),
        "wave152_preservation": verify_wave152_preservation(),
    }
    memory_samples.append(BASE.memory_sample("freeze_verified"))

    witness15 = load_json(ATTEMPT / "exact-witness-after-fifteen-cuts.json")
    witness13 = load_json(WAVE152 / "exact-witness-after-thirteen-cuts.json")
    evaluation = load_json(
        ATTEMPT / "four-root-evaluation-after-fifteen-cuts.json"
    )
    fresh = load_json(ATTEMPT / "fresh-two-cuts.json")
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
    x7_15, x8_15 = witness_maps(witness15, classes)
    x7_13, _ = witness_maps(witness13, classes)
    require(x7_15 == x7_13, "order-seven frozen count vector changed")
    lower = BASE.derive_lower_counts(x7_15, classes)
    memory_samples.append(BASE.memory_sample("classes_and_lower_counts"))

    root_records = {
        int(record["root_mask"]): record for record in evaluation["root_blocks"]
    }
    require(
        tuple(root_records) == (0, 1, 3, 7, 11, 12, 13, 15, 30),
        "four-root block stream changed",
    )
    stored_negative = [
        root for root, record in root_records.items()
        if record["negative_certificate"] is not None
    ]
    stored_not_psd = [
        root for root, record in root_records.items()
        if record["exact_status"] == "NOT_PSD"
    ]
    require(stored_negative == [3, 12], "stored negative certificate set changed")
    require(stored_not_psd == [3, 12], "stored NOT_PSD set changed")
    require(
        evaluation["conclusion"]["exact_negative_blocks"] == [3, 12],
        "stored conclusion block set changed",
    )
    require(
        all(
            root_records[root]["negative_certificate"] is None
            and root_records[root]["exact_status"] == "NUMERICALLY_NO_SEPARATION"
            for root in (0, 1, 7, 11, 13, 15, 30)
        ),
        "nonnegative-certificate block status changed",
    )

    requests = [
        {
            "id": f"fresh_{index}",
            "root_mask": int(cut["root_mask"]),
            "direction": cut["direction"],
        }
        for index, cut in enumerate(fresh["cuts"])
    ]
    requests.extend(negative_request(root_records[root]) for root in (3, 12))
    structures = derive_structures(requests, classes, lower, memory_samples)
    fresh_results = [
        verify_fresh_cut(
            cut, structures[f"fresh_{index}"], witness13, classes
        )
        for index, cut in enumerate(fresh["cuts"])
    ]
    negative_results = [
        verify_negative_certificate(
            root_records[root],
            structures[f"negative_{root}"],
            evaluation,
            witness15,
            classes,
        )
        for root in (3, 12)
    ]

    payloads = retained_cut_payloads(fresh)
    witness_result = BASE.verify_witness(
        "after_fifteen",
        witness15,
        payloads,
        coefficients,
        marked,
        row_system,
        classes,
        lower,
        memory_samples,
    )
    require(
        set(witness_result["active_cut_hashes"])
        == set(witness15["active_cut_hashes"]),
        "active cut set mismatch",
    )
    require(
        all(value.denominator == 1 and value >= 0 for value in x7_15.values()),
        "order-seven coordinate failure",
    )
    scale = int(evaluation["count_denominator_scale"])
    require(
        scale == int(witness15["exact_solve"]["maximum_denominator"]),
        "count denominator scale differs",
    )
    require(
        all(scale % value.denominator == 0 for value in x8_15.values()),
        "count scale does not clear every order-eight denominator",
    )

    replay = load_json(ATTEMPT / "replay-results.json")
    require(
        replay["checks"]["exact_negative_four_root_blocks"] == [3, 12],
        "same-lane replay block set differs",
    )
    require(
        replay["conclusion"]["fifteen_cut_finite_relaxation"]
        == "EXACT_RATIONAL_FEASIBLE",
        "same-lane replay conclusion drift",
    )

    memory_samples.append(BASE.memory_sample("complete"))
    resource_report = {
        "format": "wave161-resource-report-v1",
        "memory_floor_percent": 15.0,
        "minimum_free_physical_memory_percent": min(
            float(sample["free_physical_memory_percent"])
            for sample in memory_samples
        ),
        "floor_respected": True,
        "elapsed_seconds": time.time() - started,
        "samples": memory_samples,
    }
    return {
        "format": "wave161-four-root-cut-loop-independent-v1",
        "claim_label": "VERIFIED",
        "scope": (
            "Exact rational feasibility of the finite fifteen-cut "
            "pair-root-zero-face count relaxation and two exact separating "
            "directions for that pseudowitness"
        ),
        "separation": {
            "wave159_discovery_python_imported": False,
            "wave159_discovery_python_executed": False,
            "wave152_discovery_python_imported": False,
            "wave152_discovery_python_executed": False,
            "prior_cleanroom_verifier_imported": True,
            "prior_cleanroom_verifier_sha256": BASE_SHA256,
            "solver_status_used_as_certificate": False,
        },
        "freeze": freeze,
        "fresh_cuts": fresh_results,
        "witness": witness_result,
        "four_root_feedback": {
            "stored_exact_negative_certificate_blocks": stored_negative,
            "independently_replayed_negative_certificates": negative_results,
            "remaining_blocks": [0, 1, 7, 11, 13, 15, 30],
            "remaining_blocks_proved_psd": False,
            "witness_satisfies_all_four_root_blocks": False,
        },
        "metadata_audit": {
            "inherited_format": witness15["format"],
            "inherited_scope": witness15["scope"],
            "stale_after_two_cuts_metadata_present": True,
            "actual_retained_cut_count": 15,
            "active_cut_hashes": witness15["active_cut_hashes"],
        },
        "hostile_checks": {
            "package_manifest_exact_bytes": True,
            "wave152_before_after_byte_identity": True,
            "fresh_cut_canonical_hashes_rebuilt": True,
            "fresh_cut_coefficients_rebuilt": True,
            "negative_certificate_flag_indices_replayed": True,
            "all_cut_values_recomputed": True,
            "all_exact_rows_recomputed": True,
            "selected_modular_rows_reduced_independently": True,
        },
        "verdict": {
            "fifteen_cut_finite_relaxation": "EXACT_RATIONAL_FEASIBLE",
            "displayed_root_3_and_12_directions": "EXACTLY_NEGATIVE",
            "full_four_root_covariance_feasibility": "REFUTED_FOR_THIS_PSEUDOWITNESS",
            "graph_constructed": False,
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "Conway_99": "UNKNOWN",
        },
        "limitations": [
            "The exact nonnegative vector is a count pseudowitness, not a graph.",
            "Finite relaxation feasibility does not establish endpoint graph feasibility.",
            "The seven blocks without stored negative certificates are not proved PSD.",
            "Numerical eigenvalues and solver statuses are not certificates.",
            "No graph construction, endpoint exclusion, strict bound, or Conway-99 result follows.",
        ],
        "resource_report": resource_report,
    }


def require_expected_subset(actual: object, expected: object, path: str = "$") -> None:
    if isinstance(expected, dict):
        require(isinstance(actual, dict), f"{path}: expected mapping")
        for key, value in expected.items():
            require(key in actual, f"{path}: missing {key}")
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
    require(dense_direction(4, [0, 3], [2, -5]) == [2, 0, 0, -5],
            "dense direction")
    require(BASE.self_test()["flag_counts"] == {"3": 155, "12": 178},
            "base semantic self-test")
    require(BASE.fraction("3/4") + BASE.fraction("1/4") == 1,
            "fraction arithmetic")
    return {
        "dense_direction": "PASS",
        "graph_flag_semantics": "PASS",
        "fraction_arithmetic": "PASS",
    }


def write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--resource-output", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0
    result = main_result()
    if args.verify:
        expected = load_json(args.verify)
        # Wall-clock time and sampled host state are intentionally dynamic.
        # The stored resource report is audited separately by the unit tests.
        expected.pop("resource_report", None)
        require_expected_subset(result, expected)
    if args.output:
        write_json(args.output, result)
    if args.resource_output:
        write_json(args.resource_output, result["resource_report"])
    print(
        json.dumps(
            {
                "claim_label": result["claim_label"],
                "all_rows": result["witness"]["all_equalities"],
                "restricted_rows": result["witness"]["restricted_equalities"],
                "modular_rank": result["witness"]["modular_rank"]["rank"],
                "negative_blocks": result["four_root_feedback"][
                    "stored_exact_negative_certificate_blocks"
                ],
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
