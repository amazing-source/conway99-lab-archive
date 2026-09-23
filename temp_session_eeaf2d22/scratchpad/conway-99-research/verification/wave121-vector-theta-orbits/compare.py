"""Post-derivation comparison with sealed Wave 121 and Wave 124 artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "comparison.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    verified = json.loads((HERE / "independent-results.json").read_text(encoding="utf-8"))
    discovery = json.loads(
        (
            ROOT
            / "attempts"
            / "wave121-vector-theta-orbits"
            / "exact-results.json"
        ).read_text(encoding="utf-8")
    )
    scalar = json.loads(
        (
            ROOT
            / "attempts"
            / "wave121-vector-theta-orbits"
            / "scalar-jacobi-results.json"
        ).read_text(encoding="utf-8")
    )
    wave124 = json.loads(
        (
            ROOT
            / "attempts"
            / "wave124-c4-index70-jacobi"
            / "exact-results.json"
        ).read_text(encoding="utf-8")
    )

    checks = {
        "D_L_type": verified["orthogonal_spaces"]["D_L"]
        == discovery["quadratic_spaces"]["L_discriminant"]["orthogonal_type"],
        "D_K_type": verified["orthogonal_spaces"]["D_K"]
        == discovery["quadratic_spaces"]["K_discriminant"]["orthogonal_type"],
        "orbit14_each_nonzero": verified["orthogonal_spaces"]["orbit_counts"][
            "dimension14"
        ]["each_exact_nonzero_value"]
        == discovery["quadratic_spaces"]["L_discriminant"]["orbit_counts"][
            "each_exact_nonzero_value"
        ],
        "orbit30_each_nonzero": verified["orthogonal_spaces"]["orbit_counts"][
            "dimension30"
        ]["each_exact_nonzero_value"]
        == discovery["quadratic_spaces"]["K_discriminant"]["orbit_counts"][
            "each_exact_nonzero_value"
        ],
        "prefix10_optimum": verified["extended_scalar_model"]["prefix10"][
            "old_exact_optimum"
        ]
        == discovery["prefix_bounds"]["through_norm_20"]["exact_optimum"],
        "prefix11_optimum": verified["extended_scalar_model"]["prefix11"][
            "old_exact_optimum"
        ]
        == discovery["prefix_bounds"]["through_norm_22"]["exact_optimum"],
        "formal_control_x": verified["extended_scalar_model"][
            "formal_even_integral_control"
        ]["x7_to_x14"]
        == [
            discovery["conditional_no_norm_14_16_18"][
                "formal_even_integral_null_control"
            ]["x7_to_x14"][f"x{n}"]
            for n in range(7, 15)
        ],
        "code_upper": verified["short_code_upper"]["each_anisotropic_value_upper"]
        == discovery["coordinate_and_code_boundary"][
            "abstract_anisotropic_codeword_upper_each_exact_value"
        ],
        "scalar_indices": (
            verified["scalar_c4_jacobi"]["marking"]["K_index"],
            verified["scalar_c4_jacobi"]["marking"]["L_index"],
        )
        == (
            scalar["markings"]["K"]["ordinary_scalar_Jacobi_index"],
            scalar["markings"]["L_Fricke_partner"]["ordinary_scalar_Jacobi_index"],
        ),
        "component_reduction": (
            verified["scalar_c4_jacobi"]["components"][
                "divisibility_reduced_residues"
            ],
            verified["scalar_c4_jacobi"]["components"][
                "even_independent_components"
            ],
        )
        == (
            scalar["theta_decomposition"]["reduced_component_count"],
            scalar["theta_decomposition"]["after_z_to_minus_z_symmetry"],
        ),
        "truncated_target": verified["scalar_c4_jacobi"]["truncated_null"][
            "coefficients_n_r"
        ]["7,28"]
        == scalar["truncated_coefficient_cone"]["explicit_control"]["c(7,28)"],
        "wave124_shared_marking": (
            verified["scalar_c4_jacobi"]["marking"]["d_norm"],
            verified["scalar_c4_jacobi"]["marking"]["b_norm"],
            verified["scalar_c4_jacobi"]["marking"]["b_divisibility_in_K"],
        )
        == (
            wave124["c4_marking"]["norm_d"],
            wave124["c4_marking"]["norm_b"],
            wave124["c4_marking"]["divisibility_in_K"],
        ),
        "wave124_shared_indices": (
            verified["scalar_c4_jacobi"]["marking"]["K_index"],
            verified["scalar_c4_jacobi"]["marking"]["L_index"],
        )
        == (
            wave124["c4_marking"]["K_index"],
            wave124["c4_marking"]["L_partner_index"],
        ),
    }
    mismatches = [label for label, passed in checks.items() if not passed]
    payload = {
        "format": "wave121-post-independent-comparison-v1",
        "discovery_manifest_sha256": sha256(
            ROOT
            / "attempts"
            / "wave121-vector-theta-orbits"
            / "package-manifest.sha256"
        ),
        "wave124_manifest_sha256": sha256(
            ROOT
            / "attempts"
            / "wave124-c4-index70-jacobi"
            / "package-manifest.sha256"
        ),
        "checks": checks,
        "checks_total": len(checks),
        "checks_passed": sum(checks.values()),
        "mismatches": mismatches,
        "wave124_comparison_status": (
            "CONSISTENCY_ONLY_NOT_VERIFICATION; Wave124 independently extends "
            "the coefficient interpretation to norm20 using verified Wave96 "
            "and adds the C4 tight-frame identity, neither of which is imported "
            "into the frozen Wave121 verdict."
        ),
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if mismatches:
        raise SystemExit(f"comparison mismatches: {mismatches}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
