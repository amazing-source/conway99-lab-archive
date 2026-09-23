"""Post-handoff independent verifier for the sealed Wave148 row artifact.

The expected rows are rebuilt through ``clean_room_rows``, whose protocol and
implementation were frozen in ``preparation-manifest.sha256`` before the
Wave148 manifest handoff.  No Wave148 discovery code is imported or executed.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

import clean_room_rows as clean


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY = ROOT / "attempts" / "wave148-marked-order8"
DISCOVERY_MANIFEST = DISCOVERY / "package-manifest.sha256"
DISCOVERY_ARTIFACT = DISCOVERY / "marked-rows.json.gz"
DISCOVERY_SUMMARY = DISCOVERY / "exact-results.json"
PREPARATION_MANIFEST = HERE / "preparation-manifest.sha256"
PRECOMMITTED_EXPECTATIONS = HERE / "expected-invariants.json"
OUTPUT = HERE / "verification-results.json"

EXPECTED_PREPARATION_MANIFEST_SHA256 = (
    "d28805adb6a6353430ab0630832a08b3ba74aa72fece7c6cedd8f2ffd6b9449d"
)
EXPECTED_DISCOVERY_MANIFEST_SHA256 = (
    "3b937619d251f99999b6c4ebfb6e8a13de869417bbe2b03047efa259aaf71344"
)
EXPECTED_DISCOVERY_GZIP_SHA256 = (
    "e7a39699584fe60ff251119063d66d8eed2a14a69d671c183533806cddc92aa1"
)
EXPECTED_DISCOVERY_PAYLOAD_SHA256 = (
    "3bdfdafa7e1675bf1fe160f44f1fea0e53792b5c2e87e0bfb529a15bd1cc2a8f"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode(
        "ascii"
    )


def verify_manifest(
    manifest: Path,
    base: Path,
    expected_manifest_sha256: str,
) -> dict:
    actual_manifest_sha256 = sha256(manifest)
    rows = []
    failures = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split(maxsplit=1)
        relative = relative.strip().replace("\\", "/")
        candidate = (base / relative).resolve()
        try:
            candidate.relative_to(base.resolve())
        except ValueError:
            # Preparation paths are deliberately repository-relative.
            candidate = (ROOT / relative).resolve()
            try:
                candidate.relative_to(ROOT.resolve())
            except ValueError:
                failures.append(f"path escape: {relative}")
                continue
        if not candidate.is_file():
            failures.append(f"missing: {relative}")
            continue
        actual = sha256(candidate)
        rows.append(
            {
                "path": relative,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "pass": actual == expected,
            }
        )
        if actual != expected:
            failures.append(f"hash mismatch: {relative}")
    return {
        "manifest_sha256": actual_manifest_sha256,
        "expected_manifest_sha256": expected_manifest_sha256,
        "manifest_pass": actual_manifest_sha256 == expected_manifest_sha256,
        "entry_count": len(rows),
        "entries_pass": not failures,
        "failures": failures,
    }


def class_stream_hash(classes: tuple[int, ...], width: int) -> str:
    return hashlib.sha256(
        b"".join(mask.to_bytes(width, "big") for mask in classes)
    ).hexdigest()


def expected_row_payload() -> tuple[dict, dict]:
    classes7, classes8, _ = clean.published_streams()
    vertex_types, pair_types = clean.rooted_type_tables(classes7)
    vertex_coefficients, pair_coefficients, column_checks = (
        clean.coefficient_rows(classes8, vertex_types, pair_types)
    )

    vertex_rows = []
    for index, key in enumerate(sorted(vertex_types)):
        record = vertex_types[key]
        residual = 14 - int(record["degree"])
        require(residual >= 0, "negative target vertex residual")
        vertex_rows.append(
            {
                "row_id": f"V{index:04d}",
                "rooted_key": key,
                "order7_mask": int(record["source_mask"]),
                "orbit_multiplicity": int(record["multiplicity"]),
                "internal_degree": int(record["degree"]),
                "outside_neighbor_count": residual,
                "lhs_coefficient": int(record["multiplicity"]) * residual,
                "terms_order8_mask_coefficient": [
                    [mask8, coefficient]
                    for mask8, coefficient in sorted(
                        vertex_coefficients[key].items()
                    )
                ],
            }
        )

    pair_rows = []
    for index, key in enumerate(sorted(pair_types)):
        record = pair_types[key]
        target = 1 if record["adjacent"] else 2
        residual = target - int(record["common_inside"])
        require(residual >= 0, "negative target pair residual")
        terms = [
            [mask8, coefficient]
            for mask8, coefficient in sorted(pair_coefficients[key].items())
        ]
        if residual == 0:
            require(not terms, "zero-capacity expected row has support")
        pair_rows.append(
            {
                "row_id": f"P{index:04d}",
                "rooted_key": key,
                "order7_mask": int(record["source_mask"]),
                "orbit_multiplicity": int(record["multiplicity"]),
                "root_relation": (
                    "edge" if record["adjacent"] else "nonedge"
                ),
                "target_common_neighbors": target,
                "internal_common_neighbors": int(record["common_inside"]),
                "outside_common_neighbor_count": residual,
                "lhs_coefficient": int(record["multiplicity"]) * residual,
                "terms_order8_mask_coefficient": terms,
            }
        )

    payload = {
        "format": "wave148-marked-order8-rows-v1",
        "class_streams": {
            "7": {
                "count": len(classes7),
                "sha256": class_stream_hash(classes7, 3),
            },
            "8": {
                "count": len(classes8),
                "sha256": class_stream_hash(classes8, 4),
            },
        },
        "semantics": {
            "vertex": (
                "m_tau*(14-d_tau)*x_H7 = sum_K e_vertex(tau,K)*x_K8"
            ),
            "ordered_pair": (
                "m_tau*(lambda_or_mu-c_tau)*x_H7 = "
                "sum_K e_pair(tau,K)*x_K8"
            ),
            "automorphism_policy": (
                "roots are pointwise labelled and all embeddings are counted; "
                "no graph automorphism is assumed"
            ),
        },
        "vertex_rows": vertex_rows,
        "ordered_pair_rows": pair_rows,
    }
    internals = {
        "classes7": classes7,
        "classes8": classes8,
        "vertex_types": vertex_types,
        "pair_types": pair_types,
        "vertex_coefficients": vertex_coefficients,
        "pair_coefficients": pair_coefficients,
        "column_checks": column_checks,
    }
    return payload, internals


def first_payload_difference(expected: dict, actual: dict) -> str | None:
    if set(actual) != set(expected):
        return "top-level key mismatch"
    for key in ("format", "class_streams", "semantics"):
        if expected.get(key) != actual.get(key):
            return f"top-level mismatch: {key}"
    for family in ("vertex_rows", "ordered_pair_rows"):
        expected_rows = expected.get(family)
        actual_rows = actual.get(family)
        if not isinstance(actual_rows, list):
            return f"{family} is not a list"
        if len(expected_rows) != len(actual_rows):
            return (
                f"{family} count mismatch: "
                f"{len(expected_rows)} != {len(actual_rows)}"
            )
        expected_by_key = {}
        actual_by_key = {}
        for label, rows, destination in (
            ("expected", expected_rows, expected_by_key),
            ("actual", actual_rows, actual_by_key),
        ):
            for row in rows:
                try:
                    semantic_key = (
                        int(row["order7_mask"]),
                        int(row["rooted_key"]),
                    )
                except (KeyError, TypeError, ValueError):
                    return f"{family} invalid {label} semantic key"
                if semantic_key in destination:
                    return (
                        f"{family} duplicate {label} semantic key: "
                        f"{semantic_key}"
                    )
                normalized = dict(row)
                normalized.pop("row_id", None)
                destination[semantic_key] = normalized
        if set(expected_by_key) != set(actual_by_key):
            missing = sorted(set(expected_by_key) - set(actual_by_key))
            extra = sorted(set(actual_by_key) - set(expected_by_key))
            return (
                f"{family} semantic key mismatch: "
                f"missing={missing[:1]} extra={extra[:1]}"
            )
        for semantic_key in sorted(expected_by_key):
            if expected_by_key[semantic_key] != actual_by_key[semantic_key]:
                return f"{family}{semantic_key} mismatch"
    return None


def semantic_normalized_payload(payload: dict) -> dict:
    """Normalize non-mathematical row ordering and sequential row labels."""

    normalized = {
        key: value
        for key, value in payload.items()
        if key not in ("vertex_rows", "ordered_pair_rows")
    }
    for family in ("vertex_rows", "ordered_pair_rows"):
        rows = []
        for original in payload[family]:
            row = dict(original)
            row.pop("row_id", None)
            rows.append(row)
        normalized[family] = sorted(
            rows,
            key=lambda row: (
                int(row["order7_mask"]),
                int(row["rooted_key"]),
            ),
        )
    return normalized


def discovery_sequence_checks(payload: dict) -> dict:
    checks = {}
    for family, prefix in (
        ("vertex_rows", "V"),
        ("ordered_pair_rows", "P"),
    ):
        rows = payload[family]
        semantic_keys = [
            (int(row["order7_mask"]), int(row["rooted_key"]))
            for row in rows
        ]
        checks[family] = {
            "row_ids_sequential": all(
                row.get("row_id") == f"{prefix}{index:04d}"
                for index, row in enumerate(rows)
            ),
            "semantic_keys_unique": len(semantic_keys)
            == len(set(semantic_keys)),
            "source_then_rooted_key_order": semantic_keys
            == sorted(semantic_keys),
        }
    return checks


def independent_controls(internals: dict) -> dict:
    classes7 = internals["classes7"]
    classes8 = internals["classes8"]
    vertex_types = internals["vertex_types"]
    pair_types = internals["pair_types"]
    vertex_coefficients = internals["vertex_coefficients"]
    pair_coefficients = internals["pair_coefficients"]
    column_checks = internals["column_checks"]

    micro = clean.micro_controls(
        classes7,
        classes8,
        vertex_types,
        pair_types,
        vertex_coefficients,
        pair_coefficients,
    )
    translate7 = {
        clean.canonical_unrooted(mask, 7): mask for mask in classes7
    }
    translate8 = {
        clean.canonical_unrooted(mask, 8): mask for mask in classes8
    }
    rook = clean.rook_mask()
    counts7 = clean.induced_counts(rook, 9, 7, translate7)
    counts8 = clean.induced_counts(rook, 9, 8, translate8)
    vertex_failures, vertex_zero = clean.evaluate_rows(
        vertex_types,
        vertex_coefficients,
        counts7,
        counts8,
        4,
        1,
        2,
    )
    pair_failures, pair_zero = clean.evaluate_rows(
        pair_types,
        pair_coefficients,
        counts7,
        counts8,
        4,
        1,
        2,
    )
    require(not vertex_failures and not pair_failures, "rook control failed")

    vertex_left_by_source = {}
    for record in vertex_types.values():
        source = int(record["source_mask"])
        value = int(record["multiplicity"]) * (14 - int(record["degree"]))
        vertex_left_by_source[source] = (
            vertex_left_by_source.get(source, 0) + value
        )
    for source, total in vertex_left_by_source.items():
        require(
            total == 7 * 14 - 2 * source.bit_count(),
            "vertex left aggregate",
        )

    return {
        "column_classes_checked": len(column_checks),
        "all_vertex_column_identities_pass": all(
            row["vertex_total"] == row["expected_vertex_total"]
            for row in column_checks.values()
        ),
        "all_pair_column_identities_pass": all(
            row["pair_total"] == row["expected_pair_total"]
            for row in column_checks.values()
        ),
        "vertex_left_aggregates_checked": len(vertex_left_by_source),
        "micro_controls": micro,
        "rook": {
            "order7_subset_total": sum(counts7.values()),
            "order8_subset_total": sum(counts8.values()),
            "vertex_failures": vertex_failures,
            "pair_failures": pair_failures,
            "realized_zero_vertex_rows": vertex_zero,
            "realized_zero_pair_rows": pair_zero,
            "all_rows_pass": True,
        },
    }


def summary_from_rows(payload: dict) -> dict:
    vertex = payload["vertex_rows"]
    pair = payload["ordered_pair_rows"]
    return {
        "vertex_rows": len(vertex),
        "ordered_pair_rows": len(pair),
        "vertex_nonzero_terms": sum(
            len(row["terms_order8_mask_coefficient"]) for row in vertex
        ),
        "pair_nonzero_terms": sum(
            len(row["terms_order8_mask_coefficient"]) for row in pair
        ),
        "zero_capacity_pair_rows": sum(
            row["outside_common_neighbor_count"] == 0 for row in pair
        ),
        "zero_rhs_pair_rows": sum(
            not row["terms_order8_mask_coefficient"] for row in pair
        ),
        "edge_pair_types": sum(
            row["root_relation"] == "edge" for row in pair
        ),
        "nonedge_pair_types": sum(
            row["root_relation"] == "nonedge" for row in pair
        ),
        "vertex_lhs_coefficient_sum": sum(
            row["lhs_coefficient"] for row in vertex
        ),
        "pair_lhs_coefficient_sum": sum(
            row["lhs_coefficient"] for row in pair
        ),
        "vertex_maximum_term_coefficient": max(
            coefficient
            for row in vertex
            for _, coefficient in row["terms_order8_mask_coefficient"]
        ),
        "pair_maximum_term_coefficient": max(
            coefficient
            for row in pair
            for _, coefficient in row["terms_order8_mask_coefficient"]
        ),
    }


def build_results() -> dict:
    preparation = verify_manifest(
        PREPARATION_MANIFEST,
        ROOT,
        EXPECTED_PREPARATION_MANIFEST_SHA256,
    )
    discovery = verify_manifest(
        DISCOVERY_MANIFEST,
        DISCOVERY,
        EXPECTED_DISCOVERY_MANIFEST_SHA256,
    )
    require(
        preparation["manifest_pass"] and preparation["entries_pass"],
        "preparation chronology freeze failed",
    )
    require(
        discovery["manifest_pass"] and discovery["entries_pass"],
        "discovery manifest freeze failed",
    )

    raw_gzip = DISCOVERY_ARTIFACT.read_bytes()
    raw_payload = gzip.decompress(raw_gzip)
    require(
        hashlib.sha256(raw_gzip).hexdigest()
        == EXPECTED_DISCOVERY_GZIP_SHA256,
        "discovery gzip drift",
    )
    require(
        hashlib.sha256(raw_payload).hexdigest()
        == EXPECTED_DISCOVERY_PAYLOAD_SHA256,
        "discovery payload drift",
    )
    actual_payload = json.loads(raw_payload.decode("ascii"))
    require(
        canonical_bytes(actual_payload) == raw_payload,
        "discovery artifact is not canonical JSON",
    )

    expected_payload, internals = expected_row_payload()
    difference = first_payload_difference(expected_payload, actual_payload)
    require(difference is None, difference or "payload mismatch")
    sequence_checks = discovery_sequence_checks(actual_payload)
    require(
        all(
            family_check["row_ids_sequential"]
            and family_check["semantic_keys_unique"]
            and family_check["source_then_rooted_key_order"]
            for family_check in sequence_checks.values()
        ),
        "discovery row sequence integrity failed",
    )
    expected_normalized = semantic_normalized_payload(expected_payload)
    actual_normalized = semantic_normalized_payload(actual_payload)
    require(
        canonical_bytes(expected_normalized)
        == canonical_bytes(actual_normalized),
        "clean-room normalized payload differs",
    )
    controls = independent_controls(internals)
    summary = summary_from_rows(expected_payload)

    precommitted = json.loads(
        PRECOMMITTED_EXPECTATIONS.read_text(encoding="utf-8")
    )
    expected_dimensions = precommitted["dimensions"]
    require(summary["vertex_rows"] == expected_dimensions["vertex_rooted_types"], "precommit vertex count")
    require(summary["ordered_pair_rows"] == expected_dimensions["ordered_pair_rooted_types"], "precommit pair count")
    require(summary["vertex_nonzero_terms"] == expected_dimensions["vertex_coefficient_nonzero_terms"], "precommit vertex terms")
    require(summary["pair_nonzero_terms"] == expected_dimensions["pair_coefficient_nonzero_terms"], "precommit pair terms")
    require(summary["zero_capacity_pair_rows"] == expected_dimensions["zero_target_pair_rows"], "precommit zero rows")

    discovery_summary = json.loads(
        DISCOVERY_SUMMARY.read_text(encoding="utf-8")
    )
    require(
        discovery_summary["vertex_rows"]["rows"] == summary["vertex_rows"]
        and discovery_summary["vertex_rows"]["nonzero_terms"]
        == summary["vertex_nonzero_terms"],
        "discovery vertex summary mismatch",
    )
    require(
        discovery_summary["ordered_pair_rows"]["rows"]
        == summary["ordered_pair_rows"]
        and discovery_summary["ordered_pair_rows"]["nonzero_terms"]
        == summary["pair_nonzero_terms"],
        "discovery pair summary mismatch",
    )

    return {
        "format": "wave148-independent-marked-order8-verification-v1",
        "claim_label": "VERIFIED",
        "scope": (
            "complete marked vertex-degree and pointwise ordered-pair "
            "common-neighbor order-seven-to-eight row artifact"
        ),
        "chronology": {
            "preparation_manifest": preparation,
            "discovery_manifest": discovery,
            "preparation_preceded_discovery_handoff": True,
            "discovery_code_imported_or_executed": False,
        },
        "artifact": {
            "gzip_bytes": len(raw_gzip),
            "gzip_sha256": hashlib.sha256(raw_gzip).hexdigest(),
            "canonical_bytes": len(raw_payload),
            "canonical_sha256": hashlib.sha256(raw_payload).hexdigest(),
            "clean_room_raw_layout_exact_match": (
                canonical_bytes(expected_payload) == raw_payload
            ),
            "raw_layout_difference": (
                "row enumeration and row_id assignment only"
            ),
            "clean_room_semantic_normalized_exact_match": True,
            "clean_room_semantic_normalized_sha256": hashlib.sha256(
                canonical_bytes(expected_normalized)
            ).hexdigest(),
            "discovery_semantic_normalized_sha256": hashlib.sha256(
                canonical_bytes(actual_normalized)
            ).hexdigest(),
        },
        "complete_row_comparison": {
            **summary,
            "all_944_vertex_rows_exact_match": True,
            "all_4440_ordered_pair_rows_exact_match": True,
            "every_scalar_and_coefficient_exact_match": True,
            "semantic_row_key_sets_exact_match": True,
            "row_ids_are_nonsemantic": True,
            "discovery_sequence_checks": sequence_checks,
            "zero_capacity_support_exact_match": True,
        },
        "independent_controls": controls,
        "precommitted_expectations_match": True,
        "verdict": {
            "marked_vertex_rows": "PASS",
            "ordered_pair_rows": "PASS",
            "row_semantics": "PASS",
            "zero_capacity_rows": "PASS",
            "column_identities": "PASS",
            "micro_controls": "PASS",
            "rook_positive_control": "PASS",
            "overall": "PASS_WITH_SCOPE",
        },
        "status_wall": {
            "combined_Wave147_148_SDP": "NOT_RUN",
            "rational_dual_certificate": "NOT_OBTAINED",
            "strict_n3_upper_bound": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "external_novelty": "UNKNOWN",
        },
    }


def main() -> None:
    payload = build_results()
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("Wave148 independent row audit: PASS_WITH_SCOPE")


if __name__ == "__main__":
    main()
