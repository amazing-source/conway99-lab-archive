"""Mechanical comparison after the independent Wave 43 result was frozen."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INDEPENDENT = HERE / "independent-result.json"
DISCOVERY = ROOT / "attempts" / "wave43-seven-deck-endpoint" / "exact-results.json"
EXPECTED_INDEPENDENT_SHA256 = "e38f369d338fada4a561d48019f306511961dd1fd7816e54a12a9ecb09e69f3b"
EXPECTED_DISCOVERY_SHA256 = "06b498a736a511a7d6f5912bd4686e5d4eb30f4041477e3ee9cbc1704f1757c8"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def require_equal(label: str, independent: object, discovery: object) -> dict[str, object]:
    if independent != discovery:
        raise AssertionError(f"{label}: {independent!r} != {discovery!r}")
    return {"field": label, "value": independent, "outcome": "MATCH"}


def compare() -> dict[str, object]:
    independent_sha = sha256(INDEPENDENT)
    discovery_sha = sha256(DISCOVERY)
    if independent_sha != EXPECTED_INDEPENDENT_SHA256:
        raise AssertionError("independent result changed after its pre-comparison freeze")
    if discovery_sha != EXPECTED_DISCOVERY_SHA256:
        raise AssertionError("frozen discovery result changed")

    independent = json.loads(INDEPENDENT.read_text(encoding="utf-8"))
    discovery = json.loads(DISCOVERY.read_text(encoding="utf-8"))
    independent_model = independent["model"]
    independent_certificate = independent["certificate"]
    discovery_model = discovery["model"]
    discovery_certificate = discovery["certificate"]

    checks = [
        require_equal(
            "seven_vertex_classes",
            independent_model["seven_vertex_classes"],
            discovery_model["seven_vertex_classes"],
        ),
        require_equal(
            "deletion_equations",
            independent_model["deletion_equations"],
            discovery_model["deletion_equations"],
        ),
        require_equal(
            "hamiltonian_equations",
            independent_model["hamiltonian_equations"],
            discovery_model["hamiltonian_equations"],
        ),
        require_equal(
            "full_constraint_sparse_nonzeros",
            independent_model["full_constraint_sparse_nonzeros"],
            discovery_model["sparse_nonzeros"],
        ),
        require_equal(
            "h11",
            independent["parameters"]["h11"],
            discovery_certificate["h11"],
        ),
        require_equal(
            "support_size",
            independent_certificate["support_size"],
            discovery_certificate["support_size"],
        ),
        require_equal(
            "zero_count_classes",
            independent_certificate["zero_count_classes"],
            discovery_certificate["zero_count_classes"],
        ),
        require_equal(
            "seven_subset_total",
            independent_certificate["seven_subset_total"],
            discovery_certificate["seven_subset_total"],
        ),
        require_equal(
            "prism_containing_class_count",
            independent_certificate["prism_containing_class_count"],
            discovery_certificate["prism_containing_class_count"],
        ),
        require_equal(
            "all_prism_containing_classes_zero",
            independent_certificate["all_prism_containing_classes_zero"],
            discovery_certificate["all_prism_containing_classes_zero"],
        ),
        require_equal(
            "support_sha256",
            independent_certificate["support_sha256"],
            discovery_certificate["support_sha256"],
        ),
        require_equal(
            "support_records",
            canonical_sha256(independent_certificate["support"]),
            canonical_sha256(discovery_certificate["support"]),
        ),
        require_equal(
            "order_seven_feasibility",
            independent["conclusion"]["unrooted_order_seven_count_system"],
            discovery["conclusion"]["order_seven_count_system"],
        ),
    ]
    if not independent_certificate["all_deck_residuals_zero"]:
        raise AssertionError("independent deletion residuals are nonzero")
    if not independent_certificate["all_hamiltonian_residuals_zero"]:
        raise AssertionError("independent Hamiltonian residuals are nonzero")

    return {
        "format": "wave43-seven-deck-frozen-comparison-v1",
        "claim_label": "VERIFIED",
        "independent_result_sha256": independent_sha,
        "discovery_result_sha256": discovery_sha,
        "checks": checks,
        "independent_only_recomputations": {
            "all_62_deck_residuals_zero": True,
            "all_19_hamiltonian_residuals_zero": True,
            "six_class_stream_sha256": independent["catalogues"]["order_6"][
                "class_stream_sha256"
            ],
            "seven_class_stream_sha256": independent["catalogues"]["order_7"][
                "class_stream_sha256"
            ],
            "deletion_matrix_sha256": independent_model["deletion_matrix_sha256"],
            "six_counts_sha256": independent_model["six_counts_sha256"],
            "hamiltonian_counts_sha256": independent_model[
                "hamiltonian_counts_sha256"
            ],
        },
        "scope_wall": (
            "The comparison verifies feasibility of the finite unrooted count "
            "relaxation only; it is not a graph realization or endpoint result."
        ),
    }


def main() -> int:
    result = compare()
    output = HERE / "comparison.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"claim_label": result["claim_label"], "checks": len(result["checks"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
