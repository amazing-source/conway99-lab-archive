#!/usr/bin/env python3
"""Exact, lightweight replay of the Wave159 fifteen-cut checkpoint.

This script does not reconstruct the witness or certify the discovery
independently.  It checks frozen hashes, canonical cut hashes, exact rational
cut values, support totals, and the stored exact negative certificates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "replay-results.json"

CUT_PATHS = (
    "attempts/wave152-four-root-order8/exact-cuts.json",
    "attempts/wave152-four-root-order8/iteration2-cuts.json",
    "attempts/wave152-four-root-order8/iteration3-mask13-cut.json",
    "attempts/wave152-four-root-order8/iteration4-three-cuts.json",
    "attempts/wave152-four-root-order8/simplified-mask12-cut.json",
    "attempts/wave152-four-root-order8/iteration5-three-cuts.json",
    "attempts/wave152-four-root-order8/simplified-mask12-cut-2.json",
    "attempts/wave159-four-root-cut-loop/fresh-two-cuts.json",
)

EXPECTED_HASHES = {
    "attempts/wave152-four-root-order8/exact-witness-after-thirteen-cuts.json":
        "4a676ca77af60fe0cf925d9b9967c641994897245f9d2322b4f33781c54a7b32",
    "attempts/wave152-four-root-order8/four-root-evaluation-after-thirteen-cuts.json":
        "dab774d8d2e7ae6981c4d3540e4063fd61a94661339901c95bcad6043cc2f1f7",
    "attempts/wave152-four-root-order8/exact-cuts.json":
        "055b8253636167b85f68e09b1a470d4fe94e2d8bcfbe5eb02ade0e69ad73603d",
    "attempts/wave152-four-root-order8/iteration2-cuts.json":
        "3652888b035ba2675cb860dcf59414f0b9e7e353e7f943ecfd1e37646718aa25",
    "attempts/wave152-four-root-order8/iteration3-mask13-cut.json":
        "93961e88b6466b2bde7446ad589c7b9957d620b277eb8fdb64c0c05aa655e4d3",
    "attempts/wave152-four-root-order8/iteration4-three-cuts.json":
        "73b301a0fec491c0336d400d2d0f0fce128de28d5450501a8abcd773d1a76b7b",
    "attempts/wave152-four-root-order8/simplified-mask12-cut.json":
        "0e9d9dd80fcd016281eaad847deecd6748aa6bfea391b49d0017b4d518a7978e",
    "attempts/wave152-four-root-order8/iteration5-three-cuts.json":
        "d5a63d57de3bf994d9f6e476ab1f7621225aaba129f27e9394d480f5dce1fb73",
    "attempts/wave152-four-root-order8/simplified-mask12-cut-2.json":
        "8bed853973bb5964a3a9d4f37c8b808e6149701c00fd62c7e607f5e543cdb965",
    "attempts/wave159-four-root-cut-loop/fresh-two-cuts.json":
        "1ef4d68a89017e006186e11f6a7e01282c6862c3219867597d34ff8395816ada",
    "attempts/wave159-four-root-cut-loop/zero-face-fifteen-cuts-highs-tight.json":
        "b8ec462af44916eaf71753757f6dbe1f198cfb5d0a82025ebc692730acfac240",
    "attempts/wave159-four-root-cut-loop/exact-witness-after-fifteen-cuts.json":
        "0073ac9d0d6053eedeb4f9357c10e40a7004e26cedbeee119601a6e1996bea1e",
    "attempts/wave159-four-root-cut-loop/four-root-evaluation-after-fifteen-cuts.json":
        "cdb94ff9719882a9b956bbdb7f489928b3a2d7c278f646fb3244aef25025ac01",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_json(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def load_cuts() -> list[dict[str, Any]]:
    cuts: list[dict[str, Any]] = []
    for relative in CUT_PATHS:
        payload = read_json(relative)
        if "cuts" in payload:
            cuts.extend(payload["cuts"])
        else:
            cuts.append(payload["cut"])
    return cuts


def count_map(witness: dict[str, Any], key: str) -> dict[int, Fraction]:
    return {
        int(record["canonical_mask"]): Fraction(str(record["count"]))
        for record in witness[key]
    }


def evaluate_cut(
    cut: dict[str, Any],
    x7: dict[int, Fraction],
    x8: dict[int, Fraction],
) -> Fraction:
    value = Fraction(str(cut["constant"]))
    value += sum(
        Fraction(str(record["coefficient"]))
        * x7.get(int(record["canonical_mask"]), Fraction(0))
        for record in cut["order7_coefficients"]
    )
    value += sum(
        Fraction(str(record["coefficient"]))
        * x8.get(int(record["canonical_mask"]), Fraction(0))
        for record in cut["order8_coefficients"]
    )
    return value


def build_results() -> dict[str, Any]:
    observed_hashes = {
        relative: sha256_file(ROOT / relative)
        for relative in EXPECTED_HASHES
    }
    require(observed_hashes == EXPECTED_HASHES, "frozen input hash mismatch")

    cuts = load_cuts()
    require(len(cuts) == 15, "expected exactly fifteen retained cuts")
    cut_hashes = [str(cut["cut_sha256"]) for cut in cuts]
    require(len(set(cut_hashes)) == 15, "cut hashes are not unique")
    for cut in cuts:
        core = dict(cut)
        stored_hash = str(core.pop("cut_sha256"))
        require(
            canonical_sha256(core) == stored_hash,
            f"canonical cut hash mismatch: {stored_hash}",
        )

    prior = read_json(
        "attempts/wave152-four-root-order8/exact-witness-after-thirteen-cuts.json"
    )
    fresh = read_json(
        "attempts/wave159-four-root-cut-loop/fresh-two-cuts.json"
    )["cuts"]
    prior_x7 = count_map(prior, "x7_support")
    prior_x8 = count_map(prior, "x8_support")
    fresh_values = {
        str(cut["cut_sha256"]): evaluate_cut(cut, prior_x7, prior_x8)
        for cut in fresh
    }
    require(
        all(value < 0 for value in fresh_values.values()),
        "fresh cuts do not both separate the thirteen-cut witness",
    )
    for cut in fresh:
        require(
            fresh_values[str(cut["cut_sha256"])]
            == Fraction(str(cut["wave150_witness_value"])),
            "stored fresh-cut value disagrees with exact replay",
        )

    witness = read_json(
        "attempts/wave159-four-root-cut-loop/exact-witness-after-fifteen-cuts.json"
    )
    x7 = count_map(witness, "x7_support")
    x8 = count_map(witness, "x8_support")
    require(len(x7) == 204 and len(x8) == 887, "support size mismatch")
    require(all(value >= 0 for value in x7.values()), "negative x7 count")
    require(all(value >= 0 for value in x8.values()), "negative x8 count")
    require(
        all(value.denominator == 1 for value in x7.values()),
        "order-seven count is not integral",
    )
    require(sum(x7.values()) == math.comb(99, 7), "x7 total mismatch")
    require(sum(x8.values()) == math.comb(99, 8), "x8 total mismatch")

    replayed_values = {
        str(cut["cut_sha256"]): evaluate_cut(cut, x7, x8)
        for cut in cuts
    }
    stored_values = {
        cut_hash: Fraction(str(record["value"]))
        for cut_hash, record in witness["exact_cut_values"].items()
    }
    require(replayed_values == stored_values, "exact cut replay mismatch")
    require(all(value >= 0 for value in replayed_values.values()), "cut violated")
    active = sorted(
        cut_hash for cut_hash, value in replayed_values.items() if value == 0
    )
    require(active == sorted(witness["active_cut_hashes"]), "active set mismatch")
    require(len(active) == 3, "expected three active cuts")
    require(
        witness["exact_solve"]["all_rows_passed"] == 10313,
        "stored all-row replay count mismatch",
    )
    require(
        witness["exact_solve"]["restricted_rows_passed"] == 10274,
        "stored restricted-row replay count mismatch",
    )
    rank = witness["selection"]["modular_rank"]
    require(
        rank["rank"] == rank["variables"] == 887 and rank["full_column_rank"],
        "stored modular rank is not full",
    )

    evaluation = read_json(
        "attempts/wave159-four-root-cut-loop/"
        "four-root-evaluation-after-fifteen-cuts.json"
    )
    negative_blocks = [
        int(block["root_mask"])
        for block in evaluation["root_blocks"]
        if block["negative_certificate"] is not None
    ]
    require(negative_blocks == [3, 12], "unexpected exact negative blocks")
    negative_values = {
        str(block["root_mask"]):
            int(block["negative_certificate"]["quadratic_value_scaled"])
        for block in evaluation["root_blocks"]
        if block["negative_certificate"] is not None
    }
    require(
        all(value < 0 for value in negative_values.values()),
        "stored covariance certificate is not negative",
    )

    scout = read_json(
        "attempts/wave159-four-root-cut-loop/"
        "zero-face-fifteen-cuts-highs-tight.json"
    )
    require(
        scout["solver"]["numerical_status_is_not_a_certificate"] is True,
        "numerical evidence boundary missing",
    )

    return {
        "format": "wave159-exact-replay-v1",
        "claim_label": "DERIVED",
        "checks": {
            "frozen_hashes": len(observed_hashes),
            "retained_cut_count": len(cuts),
            "fresh_cuts_negative_on_thirteen_cut_witness": True,
            "support_size_x7": len(x7),
            "support_size_x8": len(x8),
            "order7_integral": True,
            "order7_total": str(sum(x7.values())),
            "order8_total": str(sum(x8.values())),
            "all_fifteen_cut_values_nonnegative": True,
            "active_cut_hashes": active,
            "all_rows_passed": witness["exact_solve"]["all_rows_passed"],
            "restricted_rows_passed":
                witness["exact_solve"]["restricted_rows_passed"],
            "modular_rank": rank["rank"],
            "modular_variables": rank["variables"],
            "exact_negative_four_root_blocks": negative_blocks,
            "negative_quadratic_values_scaled": negative_values,
        },
        "conclusion": {
            "fifteen_cut_finite_relaxation": "EXACT_RATIONAL_FEASIBLE",
            "fifteen_cut_witness_passes_all_four_root_blocks": False,
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "Conway_99": "UNKNOWN",
        },
        "limitations": [
            "This same-lane replay is not independent verification.",
            "The witness is a count pseudowitness, not a graph.",
            "Stored all-row and rank claims are checked for consistency, not recomputed here.",
            "HiGHS status and floating residuals are diagnostic, not certificates.",
            "The inherited witness scope text says after two cuts and is stale metadata.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = build_results()
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result["conclusion"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
