#!/usr/bin/env python3
"""Independent exact replay of Wave 45 coefficients, cuts, and witnesses.

This checker does not use Z3.  It validates retained QF_LIA models by ordinary
Python integer arithmetic and validates PSD/indefiniteness by exact LDL or an
exact integer quadratic direction.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
FLAG_PATH = HERE / "flag_moment-v1.py"
W44_PATH = ROOT / "attempts/wave44-rooted-flags/exact_check.py"
COEFFICIENTS_PATH = HERE / "checkpoint-v1-moment-coefficients.json"
RESULT_PATH = HERE / "checkpoint-v1-stored-witness-results.json"
CUTTING_PATH = HERE / "checkpoint-v1-seed0-17cuts-15witnesses.json"
EXPECTED_W44_SHA256 = "dac369a7cdea1bdd81e3bca689a428664e4cb6f89756e0095bac94d5e1947dfa"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FLAG = load_module("wave45_replay_flag", FLAG_PATH)
if hashlib.sha256(W44_PATH.read_bytes()).hexdigest() != EXPECTED_W44_SHA256:
    raise RuntimeError("frozen v1 Wave44 row-system dependency changed")
W44 = load_module("wave45_replay_w44", W44_PATH)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def recompute_cut(
    stored: dict[str, object],
    family: Any,
    coefficients: dict[str, object],
    lower_counts: dict[int, dict[int, int]],
    classes7: Sequence[int],
) -> dict[str, object]:
    direction = stored["direction"]
    lookup = FLAG.coefficient_lookup(coefficients, family)
    constant = sum(
        count * FLAG.exact_quadratic(lookup[(order, mask)], direction)
        for order in range(4, 7)
        for mask, count in lower_counts[order].items()
    )
    dense = [
        FLAG.exact_quadratic(lookup[(7, mask)], direction) for mask in classes7
    ]
    divisor = math.gcd(abs(constant), *map(abs, dense))
    require(divisor > 0, "zero cut")
    constant //= divisor
    dense = [value // divisor for value in dense]
    core = {
        "family": "vertex",
        "direction": list(direction),
        "constant": constant,
        "coefficients": [
            {"canonical_mask": mask, "coefficient": value}
            for mask, value in zip(classes7, dense)
            if value
        ],
        "primitive_divisor": divisor,
        "sense": "constant + sum(coefficient*x_mask) >= 0",
    }
    return {**core, "cut_sha256": canonical_sha256(core)}


def cut_value(
    cut: dict[str, object],
    counts: Sequence[int],
    class_index: dict[int, int],
) -> int:
    return cut["constant"] + sum(
        record["coefficient"] * counts[class_index[record["canonical_mask"]]]
        for record in cut["coefficients"]
    )


def load_counts(
    support: Sequence[dict[str, int]],
    classes: Sequence[int],
) -> tuple[int, ...]:
    index = {mask: position for position, mask in enumerate(classes)}
    counts = [0] * len(classes)
    seen = set()
    for record in support:
        require(
            set(record) == {"canonical_mask", "count"},
            "malformed witness support",
        )
        mask, count = record["canonical_mask"], record["count"]
        require(
            type(mask) is int
            and type(count) is int
            and count > 0
            and mask in index
            and mask not in seen,
            "invalid witness support entry",
        )
        seen.add(mask)
        counts[index[mask]] = count
    require(canonical_sha256(list(support)) == canonical_sha256([
        {"canonical_mask": mask, "count": count}
        for mask, count in zip(classes, counts)
        if count
    ]), "support order/content mismatch")
    return tuple(counts)


def main() -> int:
    coefficients = json.loads(COEFFICIENTS_PATH.read_text(encoding="utf-8"))
    stored_payload_sha = coefficients[
        "coefficient_payload_sha256_without_this_field"
    ]
    unhashed = dict(coefficients)
    unhashed.pop("coefficient_payload_sha256_without_this_field")
    require(FLAG.sha256_json(unhashed) == stored_payload_sha, "coefficient hash")

    catalogues = FLAG.build_catalogues()
    classes = FLAG.admissible_classes(catalogues)
    family_values = FLAG.families()
    family = next(item for item in family_values if item.name == "vertex")
    recomputed = FLAG.build_coefficients(family_values, classes)
    recomputed["class_streams"] = {
        str(order): {
            "count": len(classes[order]),
            "sha256": FLAG.W43.class_stream_sha256(
                classes[order],
                1 if order <= 4 else 2 if order <= 6 else 3,
            ),
        }
        for order in classes
    }
    require(unhashed == recomputed, "stored coefficient tensors changed")

    lower = FLAG.target_lower_counts(classes)
    stored_result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    require(
        stored_result["coefficient_model"]["payload_sha256"] == stored_payload_sha,
        "result coefficient pointer changed",
    )
    target_summaries = {}
    for target_name, target in stored_result["targets"].items():
        counts = dict(lower)
        counts[7] = FLAG.load_seven_counts(
            ROOT / target["input_path"], classes[7]
        )
        family_summary = {}
        for current_family in family_values:
            matrix = FLAG.evaluate_expansion(
                coefficients, current_family, counts
            )
            record = target["families"][current_family.name]
            require(
                FLAG.sha256_json(matrix) == record["raw_matrix_sha256"],
                f"{target_name} matrix hash changed",
            )
            ldl = FLAG.exact_ldl_psd(matrix)
            require(
                ldl["is_psd"] == record["exact_ldl"]["is_psd"],
                f"{target_name} LDL status changed",
            )
            direction = record["exact_negative_direction"]
            if direction is not None:
                quadratic = FLAG.exact_quadratic(matrix, direction["vector"])
                require(
                    quadratic == direction["quadratic_numerator"] < 0,
                    f"{target_name} negative direction failed",
                )
            else:
                require(ldl["is_psd"], f"{target_name} lacks PSD/negative proof")
            family_summary[current_family.name] = {
                "status": record["status"],
                "exact_replay": "PASS",
            }
        target_summaries[target_name] = family_summary

    cutting = json.loads(CUTTING_PATH.read_text(encoding="utf-8"))
    require(
        cutting["coefficient_payload_sha256"] == stored_payload_sha,
        "cutting-plane coefficient pointer changed",
    )
    cuts = cutting["cuts"]
    for cut in cuts:
        fresh = recompute_cut(cut, family, coefficients, lower, classes[7])
        for key in (
            "family",
            "direction",
            "constant",
            "coefficients",
            "primitive_divisor",
            "sense",
            "cut_sha256",
        ):
            require(fresh[key] == cut[key], f"cut {cut['cut_sha256']} changed")

    system = W44.endpoint_system()
    rows = (
        system["base_rows"]
        + system["vertex_rows"]
        + system["edge_rows"]
        + system["nonedge_rows"]
    )
    rhs = (
        system["base_rhs"]
        + system["vertex_rhs"]
        + system["edge_rhs"]
        + system["nonedge_rhs"]
    )
    require(len(rows) == 170 and tuple(system["classes"]) == classes[7], "row system")
    class_index = {mask: index for index, mask in enumerate(classes[7])}
    witness_summaries = []
    for witness in cutting["witnesses"]:
        counts = load_counts(witness["support"], classes[7])
        require(
            canonical_sha256(witness["support"]) == witness["support_sha256"],
            "witness support hash changed",
        )
        vector = counts + (witness["h11"] // 4,)
        require(witness["h11"] % 4 == 0, "h11 not divisible by four")
        require(not any(W44.residuals(rows, rhs, vector)), "170-row replay failed")
        require(sum(counts) == math.comb(99, 7), "witness total changed")
        retained = witness["exact_replay"]["retained_cut_count"]
        values = [cut_value(cut, counts, class_index) for cut in cuts[:retained]]
        require(min(values, default=0) >= 0, "retained cut replay failed")
        require(
            canonical_sha256(values)
            == witness["exact_replay"]["cut_values_sha256"],
            "retained cut values changed",
        )
        target_counts = dict(lower)
        target_counts[7] = dict(zip(classes[7], counts))
        matrix = FLAG.evaluate_expansion(coefficients, family, target_counts)
        moment = witness["vertex_moment"]
        require(
            FLAG.sha256_json(matrix) == moment["raw_matrix_sha256"],
            "witness matrix hash changed",
        )
        ldl = FLAG.exact_ldl_psd(matrix)
        require(
            ldl["is_psd"] == moment["exact_ldl"]["is_psd"],
            "witness LDL status changed",
        )
        direction = moment["exact_negative_direction"]
        if direction is None:
            require(ldl["is_psd"], "final witness lacks exact PSD certificate")
        else:
            require(
                FLAG.exact_quadratic(matrix, direction["vector"])
                == direction["quadratic_numerator"]
                < 0,
                "witness exact negative direction failed",
            )
            origin_prefix = f"iteration_{witness['iteration']}"
            source_cuts = [
                cut
                for cut in cuts
                if cut["origin"] == origin_prefix
                or cut["origin"].startswith(origin_prefix + "_direction_")
            ]
            require(source_cuts, "source witness has no retained separating cut")
            require(
                all(
                    cut_value(source_cut, counts, class_index) < 0
                    for source_cut in source_cuts
                ),
                "a source cut does not reject its source witness",
            )
        witness_summaries.append(
            {
                "iteration": witness["iteration"],
                "support_sha256": witness["support_sha256"],
                "moment_status": moment["status"],
                "exact_replay": "PASS",
            }
        )

    if cutting["status"] == "EXACT_INTEGER_PSD_SURVIVOR":
        require(witness_summaries, "PSD survivor status without witness")
        require(
            witness_summaries[-1]["moment_status"] == "EXACTLY_PSD",
            "final witness is not exact PSD",
        )
    else:
        require(
            cutting["claim_label"] != "VERIFIED_PSD_FEASIBLE_CONTROL",
            "status inflation without survivor",
        )

    output = {
        "format": "wave45-immutable-checkpoint-replay-v1",
        "claim_label": (
            "VERIFIED"
            if cutting["status"] == "EXACT_INTEGER_PSD_SURVIVOR"
            else "UNKNOWN"
        ),
        "coefficient_payload_sha256": stored_payload_sha,
        "coefficient_tensors_recomputed": "PASS",
        "stored_target_replay": target_summaries,
        "cut_count": len(cuts),
        "all_cuts_recomputed": "PASS",
        "witness_count": len(witness_summaries),
        "witnesses": witness_summaries,
        "cutting_plane_status": cutting["status"],
        "scope_wall": {
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "Conway_99": "UNKNOWN",
        },
    }
    output_path = HERE / "replay-v1-results.json"
    output_path.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
