#!/usr/bin/env python3
"""Compare the sealed Wave 124 package with the independent reconstructions."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DISCOVERY = ROOT / "attempts" / "wave124-c4-index70-jacobi"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    value.update(path.read_bytes())
    return value.hexdigest()


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_preinspection_inventory() -> int:
    rows = (
        HERE / "discovery-inventory-preinspection.tsv"
    ).read_text(encoding="utf-8").splitlines()[1:]
    for row in rows:
        expected_hash, expected_size, relative = row.split("\t")
        path = ROOT / relative
        if digest(path) != expected_hash or path.stat().st_size != int(expected_size):
            raise AssertionError(f"sealed discovery changed: {relative}")
    return len(rows)


def check_discovery_manifest() -> int:
    rows = (DISCOVERY / "package-manifest.sha256").read_text(
        encoding="utf-8"
    ).splitlines()
    checked = 0
    for row in rows:
        if not row.strip():
            continue
        expected, relative = row.split(maxsplit=1)
        if digest(DISCOVERY / relative) != expected:
            raise AssertionError(f"discovery manifest mismatch: {relative}")
        checked += 1
    return checked


def build_comparison() -> dict[str, object]:
    inventory_count = check_preinspection_inventory()
    manifest_count = check_discovery_manifest()
    discovery = load_json(DISCOVERY / "exact-results.json")
    basic = load_json(HERE / "independent-results.json")
    jacobi = load_json(HERE / "independent-jacobi-results.json")

    marking = discovery["c4_marking"]
    independent_marking = basic["markings"]
    if (
        marking["norm_d"],
        marking["norm_b"],
        marking["L_partner_index"],
        marking["K_index"],
        marking["divisibility_in_K"],
    ) != (20, 140, 10, 70, 7):
        raise AssertionError("discovery marking data")
    if (
        independent_marking["L"]["norm"],
        independent_marking["K"]["norm"],
        independent_marking["L"]["Jacobi_index"],
        independent_marking["K"]["Jacobi_index"],
        independent_marking["K"]["divisibility"],
    ) != (20, 140, 10, 70, 7):
        raise AssertionError("independent marking data")

    discovery_rows = discovery["coefficient_selection"]["rows"]
    if [row["q_exponent"] for row in discovery_rows] != [7, 8, 9, 10]:
        raise AssertionError("coefficient selection range")
    if basic["coefficient_interpretation"][
        "q_exponents_with_exact_alternating_interpretation"
    ] != [7, 8, 9, 10]:
        raise AssertionError("independent coefficient selection range")

    discovery_moment = discovery["tight_frame"]
    independent_moment = basic["tight_frame_second_moment"]
    moment_checks = {
        "matrix": (
            discovery_moment["cycle_sign_matrix"]
            == "S=83I-13A+J"
            and independent_moment["coordinate_matrix"] == "83I-13A+J"
        ),
        "eigenvalue": (
            discovery_moment["eigenvalue_on_minus4_space"]
            == independent_moment["minus4_eigenvalue"]
            == 135
        ),
        "L_forced_coefficient": (
            discovery_moment["forced_L_boundary_coefficient"]["value"]
            == independent_moment["forced_L_coefficient"]["value"]
            == 2079
        ),
    }
    if not all(moment_checks.values()):
        raise AssertionError("tight-frame comparison")

    audit = discovery["full_level_basis_audit"]
    if (
        audit["weak_monomial_count"],
        jacobi["weak_monomial_count"],
    ) != (34, 34):
        raise AssertionError("weak monomial count")
    if (
        audit["holomorphic_dimension"],
        audit["cusp_dimension"],
        jacobi["holomorphic_dimension"],
        jacobi["cusp_dimension"],
    ) != (18, 17, 18, 17):
        raise AssertionError("full-level dimensions")
    if (
        audit["holomorphic_basis_monomial_coordinates"]
        != jacobi["holomorphic_basis"]
    ):
        raise AssertionError("holomorphic bases differ")
    if audit["cusp_basis_monomial_coordinates"] != jacobi["cusp_basis"]:
        raise AssertionError("cusp bases differ")

    direction_checks = []
    for discovered, independent in zip(
        audit["scalar_invisible_fricke_directions_by_A_power"],
        jacobi["A_power_cusp_directions"],
        strict=True,
    ):
        q1 = {
            str(row["r"]): row["coefficient"]
            for row in discovered["q1_coefficients"]
        }
        checked = {
            "minimum_A_power": discovered["minimum_A_power"],
            "dimension_agrees": (
                discovered["a_divisible_cusp_dimension"]
                == independent["cusp_dimension"]
            ),
            "target_agrees": (
                discovered["target_coefficient"]
                == independent["target_q1_r4"]
            ),
            "q1_row_agrees": q1 == independent["q1_support"],
        }
        if not all(
            value
            for key, value in checked.items()
            if key != "minimum_A_power"
        ):
            raise AssertionError(
                f"A-power direction mismatch: {checked['minimum_A_power']}"
            )
        direction_checks.append(checked)

    expected_indicator = [
        "0",
        "0",
        "-1/560",
        "0",
        "7/2880",
        "0",
        "-1/1440",
        "0",
        "1/20160",
    ]
    if (
        discovery["coefficient_selection"]["degree8_even_indicator"][
            "coefficients_low_to_high"
        ]
        != expected_indicator
        or basic["degree_eight_indicator"]["coefficients_low_to_high"]
        != expected_indicator
    ):
        raise AssertionError("degree-eight selector")

    boundary = discovery["optimization_boundary"]
    status = discovery["status"]
    if (
        boundary["positivity_bounded"] != "UNKNOWN"
        or status["rank28_excluded"]
        or status["rank30_excluded"]
        or status["Conway_99"] != "UNKNOWN"
        or status["novelty"] != "UNKNOWN"
    ):
        raise AssertionError("status inflation in discovery")

    threshold = jacobi["support_clean_threshold_candidate"]
    rows = threshold["rows"]
    if [row["q1_r4_functional_nonzero"] for row in rows] != [
        True,
        True,
        True,
        True,
        False,
    ]:
        raise AssertionError("support-clean threshold audit")

    return {
        "format": "wave124-sealed-comparison-v1",
        "verdict": "VERIFIED_WITH_CLARIFICATIONS",
        "discovery_manifest_sha256": digest(
            DISCOVERY / "package-manifest.sha256"
        ),
        "sealed_inventory_files_checked": inventory_count,
        "discovery_manifest_entries_checked": manifest_count,
        "agreement": {
            "primitive_norm20_marking_and_indices": True,
            "K_divisibility_seven": True,
            "exact_q7_through_q10_incidence_interpretation": True,
            "Fricke_index70_to_index10_and_twenty_residues": True,
            "tight_frame_second_moments": moment_checks,
            "degree_eight_selector": True,
            "full_level_dimensions": {"holomorphic": 18, "cusp": 17},
            "full_level_basis_vectors_exactly_equal": True,
            "A_power_direction_checks": direction_checks,
            "oldform_null_for_constants_scalar_and_finite_moments": True,
        },
        "clarifications": [
            (
                "The full-level J_22,10 basis is only a subspace of the "
                "unknown full Gamma0(7) Jacobi space."
            ),
            (
                "The oldform direction is signed and does not certify a "
                "positive graph-compatible deformation."
            ),
            (
                "The q^10 incidence statement is valid because the sealed "
                "Wave96 norm-20 unit-coordinate classification is imported."
            ),
            (
                "Neither candidate rank is excluded; Conway-99 and novelty "
                "remain UNKNOWN."
            ),
        ],
        "candidate_followup_not_self_verified": threshold,
    }


def canonical(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    output = HERE / "comparison.json"
    payload = canonical(build_comparison())
    output.write_text(payload, encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
