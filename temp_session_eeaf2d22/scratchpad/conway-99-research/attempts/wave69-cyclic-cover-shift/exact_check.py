#!/usr/bin/env python3
"""Fail-closed checker for the Wave 69 discovery artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import exact_search as subject


PACKAGE = Path(__file__).resolve().parent
RESULT_PATH = PACKAGE / "exact-results.json"


def load_result() -> dict[str, object]:
    with RESULT_PATH.open("r", encoding="ascii") as handle:
        result = json.load(handle)
    if not isinstance(result, dict):
        raise AssertionError("result root must be an object")
    return result


def check_semantic_hash(result: dict[str, object]) -> None:
    stored = result.get("semantic_sha256")
    semantic = dict(result)
    semantic.pop("semantic_sha256", None)
    computed = subject.sha256_bytes(subject.canonical_json_bytes(semantic))
    if stored != computed:
        raise AssertionError(
            f"semantic hash mismatch: stored={stored!r}, computed={computed!r}"
        )


def check_structure(result: dict[str, object]) -> None:
    expected_parameters = {"v": 99, "k": 14, "lambda": 1, "mu": 2}
    if result.get("schema") != "wave69-cyclic-cover-shift-exact-v1":
        raise AssertionError("wrong schema")
    if result.get("claim_label") != "DERIVED":
        raise AssertionError("discovery label must remain DERIVED")
    if result.get("novelty") != "UNKNOWN":
        raise AssertionError("novelty must remain UNKNOWN")
    if result.get("parameters") != expected_parameters:
        raise AssertionError("parameter drift")
    if result.get("quotient_candidate_count") != 0:
        raise AssertionError("sealed result unexpectedly has quotient candidates")
    if result.get("order_11_automorphism_candidate_count") != 0:
        raise AssertionError("sealed result unexpectedly allows order-11 symmetry")
    if result.get("vertex_transitive_target_status") != (
        "EXCLUDED_IN_RESTRICTED_DERIVATION"
    ):
        raise AssertionError("vertex-transitive consequence is not sealed")
    if result.get("cyclic_11_lift_status") != (
        "EMPTY_AFTER_EXHAUSTIVE_QUOTIENT_SEARCH"
    ):
        raise AssertionError("full unpruned quotient search is not sealed")

    expected_shapes = {
        str(diagonal): [list(shape) for shape in shapes]
        for diagonal, shapes in subject.derive_row_shapes().items()
    }
    if result.get("row_shapes_off_diagonal") != expected_shapes:
        raise AssertionError("row-shape mismatch")
    if result.get("sorted_diagonal_cases") != [
        list(diagonal) for diagonal in subject.derive_diagonal_cases()
    ]:
        raise AssertionError("diagonal-case mismatch")
    if result.get("row_template_counts") != {"0": 2716, "2": 3360, "4": 28}:
        raise AssertionError("row-template count mismatch")
    if result.get("quotient_eigenvalue_multiplicities") != {
        "14": 1,
        "3": 4,
        "-4": 4,
    }:
        raise AssertionError("quotient spectrum mismatch")

    searches = result.get("searches")
    if not isinstance(searches, dict) or set(searches) != {"canonical", "unpruned"}:
        raise AssertionError("both search modes must be sealed")
    for mode in ("canonical", "unpruned"):
        records = searches[mode]
        if not isinstance(records, list) or len(records) != 3:
            raise AssertionError(f"wrong {mode} record count")
        if [record.get("diagonal") for record in records] != [
            list(diagonal) for diagonal in subject.EXPECTED_DIAGONALS
        ]:
            raise AssertionError(f"{mode} diagonal order changed")
        for record in records:
            if record.get("mode") != mode:
                raise AssertionError(f"{mode} tag mismatch")
            if record.get("solutions") != 0:
                raise AssertionError(f"{mode} found a quotient")
            digest = record.get("transcript_sha256")
            if not isinstance(digest, str) or len(digest) != 64:
                raise AssertionError(f"{mode} transcript digest malformed")
            if mode == "unpruned" and any(
                value != 0
                for value in record.get(
                    "canonical_rejections_by_depth", {}
                ).values()
            ):
                raise AssertionError("unpruned search used canonical rejection")

    obstruction = result.get("cayley_fourier_obstruction")
    if obstruction != subject.derive_cayley_fourier_obstruction():
        raise AssertionError("Cayley Fourier arithmetic mismatch")
    fixed_points = result.get("order_11_fixed_point_obstruction")
    if fixed_points != subject.derive_order_11_fixed_point_obstruction():
        raise AssertionError("order-11 fixed-point arithmetic mismatch")


def check_replay(result: dict[str, object], full: bool) -> str:
    if full:
        fresh = subject.generate_results("both")
        if subject.canonical_json_bytes(fresh) != subject.canonical_json_bytes(result):
            raise AssertionError("full byte-stable replay mismatch")
        return "full_unpruned_and_canonical"

    fresh = subject.generate_results("canonical")
    if fresh["searches"]["canonical"] != result["searches"]["canonical"]:
        raise AssertionError("canonical transcript replay mismatch")
    return "canonical"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full",
        action="store_true",
        help="rerun both searches; without this flag only the quick canonical tree is replayed",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="optional path for the checker result JSON",
    )
    args = parser.parse_args()

    result = load_result()
    check_semantic_hash(result)
    check_structure(result)
    replay = check_replay(result, args.full)
    payload = {
        "schema": "wave69-cyclic-cover-shift-check-v1",
        "claim_label": "DERIVED",
        "artifact_semantic_sha256": result["semantic_sha256"],
        "replay": replay,
        "status": "PASS",
        "scope": "restricted_order_11_vertex_transitive_and_Cayley_lanes",
        "verification_boundary": (
            "This is a discovery-package consistency check, not independent "
            "verification and not a global Conway-99 result."
        ),
    }
    output = subject.canonical_json_bytes(payload)
    if args.output is None:
        print(output.decode("ascii"), end="")
    else:
        args.output.write_bytes(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
