#!/usr/bin/env python3
"""Post-freeze comparison for Wave 100."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ATTEMPT = ROOT / "attempts" / "wave100-general-pair-moment"
ATTEMPT_MANIFEST = ATTEMPT / "package-manifest.sha256"
INDEPENDENT = HERE / "independent-results.json"
OUTPUT = HERE / "comparison.json"
EXPECTED_MANIFEST_HASH = (
    "0dedf60c7994f842887c084bae7f6585f8fc98be568c940efb5b5ea90320bc88"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_attempt_manifest() -> dict[str, str]:
    require(
        sha256(ATTEMPT_MANIFEST) == EXPECTED_MANIFEST_HASH,
        "Wave100 manifest changed after freeze",
    )
    entries = {}
    for line in ATTEMPT_MANIFEST.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split(maxsplit=1)
        relative = relative.strip().lstrip("*")
        require(relative not in entries, f"duplicate path: {relative}")
        path = ROOT / relative
        require(path.is_file(), f"missing attempt file: {relative}")
        require(sha256(path) == expected, f"hash mismatch: {relative}")
        entries[relative] = expected
    actual = {
        path.relative_to(ROOT).as_posix()
        for path in ATTEMPT.iterdir()
        if path.is_file() and path.name != ATTEMPT_MANIFEST.name
    }
    require(actual == set(entries), "attempt manifest is not file-complete")
    return entries


def comparison() -> dict[str, Any]:
    entries = verify_attempt_manifest()
    independent = json.loads(INDEPENDENT.read_text(encoding="utf-8"))
    discovery = json.loads(
        (ATTEMPT / "exact-results.json").read_text(encoding="utf-8")
    )
    require(
        independent["precomparison_verdict"]["discovery_comparison"]
        == "NOT_YET_PERFORMED",
        "independent artifact is not a precomparison seal",
    )
    require(discovery["claim_label"] == "DERIVED", "discovery self-promoted")

    root_formula = discovery["rooted_formula"]
    require(
        root_formula["valid_seed_upper"] == "350+floor(5*f_o/2)",
        "rooted formula disagrees",
    )
    require(root_formula["checked_f_values"] == 85, "root domain incomplete")
    require(
        root_formula["minimum"]["valid_seed_upper"] == 350
        and root_formula["maximum"]["valid_seed_upper"] == 560,
        "root endpoints disagree",
    )

    independent_global = independent["global_bound"]
    discovery_global = discovery["global_formula"]
    require(
        discovery_global["raw"]
        == "7*N14<=34650+15*P=55440-5*n3",
        "raw global formula disagrees",
    )
    require(
        discovery_global["antipodal_even_rounding"]
        == "N14<=2*floor((55440-5*n3)/14)",
        "antipodal formula disagrees",
    )
    require(
        discovery_global["compatible_rows_checked"]
        == independent_global["compatible_rows_checked"]
        == 1387,
        "compatible row census differs",
    )
    for key in ("4158", "4155", "708", "0"):
        discovery_row = discovery_global["selected_rows"][key]
        independent_row = independent_global["endpoint_rows"][key]
        require(
            discovery_row["P"] == independent_row["P"]
            and discovery_row["seven_N14_upper"]
            == independent_row["rooted_numerator"]
            and discovery_row["N14_floor_upper"]
            == independent_row["integer_floor"]
            and discovery_row["N14_even_upper"]
            == independent_row["even_N14_upper"],
            f"endpoint row differs: n3={key}",
        )

    scope = discovery["scope"]
    require(not scope["requires_rank_28"], "rank-28 scope was added")
    require(not scope["requires_prism_free"], "P=0 scope was added")
    require(scope["N14_counts_both_signs"], "sign convention missing")
    status = discovery["status"]
    require(
        status["strict_n3_upper_bound"] == "NOT_PROVED",
        "strict n3 status inflated",
    )
    require(status["Conway_99"] == "UNKNOWN", "global status inflated")

    return {
        "format": "wave100-general-pair-moment-comparison-v1",
        "role": "verifier",
        "claim_label": "VERIFIED",
        "attempt_manifest_sha256": EXPECTED_MANIFEST_HASH,
        "attempt_manifest_entries_verified": len(entries),
        "clean_room_seal": {
            "precomparison_hashes": "precomparison.sha256",
            "independent_result_claim_label": independent["claim_label"],
        },
        "agreement": {
            "rootwise_bound": "a14(o)<=350+floor(5*f_o/2)",
            "floor_sum_upper": "34650+15P",
            "sum_f_identity": "sum_o f_o=6P",
            "n3_coefficient": independent_global["coefficient_of_n3"],
            "even_bound": independent_global["n3_form"],
            "compatible_rows_checked": 1387,
            "rows_strictly_improved_by_even_rounding": independent_global[
                "rows_tightened_by_antipodal_even_rounding"
            ],
        },
        "scope_audit": {
            "requires_P0": False,
            "requires_rank_28": False,
            "scope_mixing_found": False,
        },
        "verdict": (
            "VERIFIED SCOPED: every hypothetical srg(99,14,1,2) satisfies "
            "N14<=2*floor((55440-5*n3)/14)"
        ),
        "status_boundary": {
            "strict_n3_upper_bound": "NOT_PROVED",
            "graph_nonexistence": "NOT_PROVED",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "dependency_note": (
            "Discovery correctly marked Wave99 unverified at creation time; "
            "the separated Wave99 verifier now independently certifies the "
            "local cap used here."
        ),
    }


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--verify", action="store_true")
    arguments = parser.parse_args()
    rendered = canonical_json(comparison())
    if arguments.verify:
        require(arguments.output.is_file(), "comparison output missing")
        require(
            arguments.output.read_text(encoding="utf-8") == rendered,
            "comparison output mismatch",
        )
    else:
        arguments.output.write_text(rendered, encoding="utf-8", newline="\n")
    print("PASS: Wave100 discovery agrees with independent reconstruction")


if __name__ == "__main__":
    main()
