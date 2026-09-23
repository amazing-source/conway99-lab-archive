"""Compare frozen Wave 101 discovery claims to independent exact results.

This script parses discovery JSON but never imports or executes discovery
Python.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY = ROOT / "attempts" / "wave101-all-rank-level7-lp"
EXPECTED_MANIFEST = (
    "54d620a8644d7efe5d2e418869b035331127862c2125ef3da325272417307619"
)
SPEC = importlib.util.spec_from_file_location(
    "wave101_independent", HERE / "independent_verify.py"
)
assert SPEC and SPEC.loader
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_manifest(path: Path) -> dict[str, str]:
    entries = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        entries[relative] = digest
    return entries


def discovery_label(certificate: dict[str, object]) -> str:
    name = certificate["name"]
    if name == "total_through_norm_28":
        return "prefix14"
    if name == "triangular_low_shell_weight":
        return "triangular"
    prefix = "prefix_through_norm_"
    if not name.startswith(prefix):
        raise ValueError(name)
    return f"prefix{int(name[len(prefix):]) // 2}"


def independent_certificate(
    row: dict[str, object], label: str
) -> dict[str, object]:
    if label == "triangular":
        return row["triangular_weighted_bound"]
    return row["prefix_bounds"][label]


def compare() -> dict[str, object]:
    manifest_path = DISCOVERY / "package-manifest.sha256"
    if sha256(manifest_path) != EXPECTED_MANIFEST:
        raise AssertionError("discovery manifest hash drift")
    manifest = parse_manifest(manifest_path)
    manifest_checks = {
        relative: sha256(ROOT / relative) == digest
        for relative, digest in manifest.items()
    }
    if not all(manifest_checks.values()):
        raise AssertionError(
            [
                relative
                for relative, valid in manifest_checks.items()
                if not valid
            ]
        )

    discovery = json.loads(
        (DISCOVERY / "exact-results.json").read_text(encoding="utf-8")
    )
    independent = json.loads(
        (HERE / "independent-results.json").read_text(encoding="utf-8")
    )
    discovery_rows = {
        row["q_discriminant_length_L"]: row for row in discovery["rows"]
    }
    independent_rows = {row["q"]: row for row in independent["rows"]}
    if set(discovery_rows) != set(independent_rows):
        raise AssertionError("q-row mismatch")

    independent_fricke = VERIFIER.fricke_matrix(VERIFIER.select_basis())
    row_comparisons = []
    for q_value in sorted(discovery_rows):
        submitted = discovery_rows[q_value]
        checked = independent_rows[q_value]
        expected_poisson = (
            f"Theta_L=-7^{11 - q_value // 2}*(Theta_K|W_7)"
        )
        if int(checked["poisson_factor"]) != -(7 ** (11 - q_value // 2)):
            raise AssertionError((q_value, checked["poisson_factor"]))
        if submitted["poisson_relation"] != expected_poisson:
            raise AssertionError(
                (q_value, submitted["poisson_relation"], expected_poisson)
            )

        certificate_comparisons = []
        for submitted_certificate in submitted["certificates"]:
            label = discovery_label(submitted_certificate)
            checked_certificate = independent_certificate(checked, label)
            submitted_x = submitted_certificate[
                "exact_primal_optimizer"
            ]["x7_to_x14"]
            submitted_y = submitted_certificate[
                "exact_primal_optimizer"
            ]["y1_to_y14"]
            checked_x = {
                f"x{n}": (
                    checked_certificate["primal_x7_to_x13"][n - 7]
                    if n <= 13
                    else checked_certificate["primal_x14"]
                )
                for n in range(7, 15)
            }
            checked_y = {
                f"y{n}": checked_certificate["primal_y1_to_y14"][n - 1]
                for n in range(1, 15)
            }
            fields = {
                "rational_bound": (
                    submitted_certificate["rational_lp_optimum"]
                    == checked_certificate["bound"]
                ),
                "parity_rounding": (
                    submitted_certificate["even_integer_lower_bound"]
                    == checked_certificate["parity_rounded_bound"]
                ),
                "active_constraints": (
                    submitted_certificate["exact_primal_optimizer"][
                        "active_zero_forms"
                    ]
                    == checked_certificate["active_constraints"]
                ),
                "primal_x": submitted_x == checked_x,
                "primal_y": submitted_y == checked_y,
                "dual_multipliers": (
                    submitted_certificate["dual_identity"][
                        "nonnegative_terms"
                    ]
                    == checked_certificate["dual_multipliers"]
                ),
                "mod7_not_fixed": (
                    not submitted_certificate["wave71_mod7_check"][
                        "fixed_residue"
                    ]
                    and not independent["mod7_scope"]["rows"][
                        q_value // 2 - 1
                    ]["objectives"][label]["fixed_residue"]
                ),
            }
            if not all(fields.values()):
                raise AssertionError((q_value, label, fields))
            certificate_comparisons.append(
                {
                    "label": label,
                    "bound": checked_certificate["bound"],
                    "parity_rounded_bound": checked_certificate[
                        "parity_rounded_bound"
                    ],
                    "fields": fields,
                }
            )

        submitted_null = submitted["zero_prefix_null_control"]
        checked_null = checked["zero_prefix_control"]
        null_x = submitted_null["x7_to_x14"]
        null_y = submitted_null["y1_to_y14"]
        system = VERIFIER.affine_system(q_value, independent_fricke)
        point = [Fraction(null_x[f"x{n}"]) for n in range(7, 14)]
        forms = {form[0]: form for form in system["forms"]}
        reconstructed = {
            label: VERIFIER.evaluate(form, point)
            for label, form in forms.items()
        }
        null_fields = {
            "submitted_x14_satisfies_independent_affine_form": (
                reconstructed["x14"] == Fraction(null_x["x14"])
            ),
            "submitted_y_satisfies_independent_affine_forms": all(
                reconstructed[f"y{n}"] == Fraction(null_y[f"y{n}"])
                for n in range(1, 15)
            ),
            "integral_even_nonnegative": (
                submitted_null[
                    "integral_even_nonnegative_first_15_coefficients"
                ]
                and all(
                    int(value) >= 0 and int(value) % 2 == 0
                    for value in [*null_x.values(), *null_y.values()]
                )
            ),
            "x7_x8_x9_zero": all(null_x[f"x{n}"] == "0" for n in (7, 8, 9)),
            "independent_rational_zero_control_feasible": (
                checked_null["all_22_coordinates_nonnegative"]
                and checked_null["x7_x8_x9_are_zero"]
            ),
        }
        if not all(null_fields.values()):
            raise AssertionError((q_value, "null", null_fields))
        row_comparisons.append(
            {
                "q": q_value,
                "poisson_relation": expected_poisson,
                "certificates": certificate_comparisons,
                "zero_prefix_null": null_fields,
            }
        )

    independent_total_bounds = {
        str(row["q"]): row["prefix_bounds"]["prefix14"][
            "parity_rounded_bound"
        ]
        for row in independent["rows"]
    }
    if (
        discovery["total_even_lower_bounds_by_q"]
        != independent_total_bounds
    ):
        raise AssertionError("summary lower-bound mismatch")

    mod2 = independent["mod2_lattice_upper_comparisons"]
    discovery_s26 = 2 * (2**44 - 1)
    discovery_s28 = 88 * (2**44 - 1)
    if (
        mod2["prefix_x7_to_x13_upper"] != discovery_s26
        or mod2["prefix_x7_to_x14_upper"] != discovery_s28
    ):
        raise AssertionError("mod-2 unweighted comparison mismatch")
    submitted_triangular_upper = 8 * discovery_s28
    if not all(
        certificate["rigorous_upper_comparison"]["weighted_objective_upper"]
        == submitted_triangular_upper
        for row in discovery["rows"]
        for certificate in row["certificates"]
        if certificate["name"] == "triangular_low_shell_weight"
    ):
        raise AssertionError("discovery triangular upper drift")

    return {
        "format": "wave101-independent-comparison-v1",
        "discovery_manifest_sha256": EXPECTED_MANIFEST,
        "manifest_entries_matching": sum(manifest_checks.values()),
        "manifest_entry_count": len(manifest_checks),
        "all_reported_exact_certificates_match": True,
        "all_zero_prefix_controls_match": True,
        "all_mod7_nonfixed_objective_conclusions_match": True,
        "row_comparisons": row_comparisons,
        "mod2_comparison": {
            "submitted_s26_upper_valid": True,
            "submitted_s28_upper_valid": True,
            "submitted_triangular_upper_valid": True,
            "submitted_triangular_upper": submitted_triangular_upper,
            "independent_sharper_triangular_upper": mod2[
                "triangular_weighted_upper"
            ],
            "sharpening_reason": (
                "a coset containing a vector below norm 28 contains only "
                "its antipode in the range, while a norm-28-only coset has "
                "at most 44 orthogonal antipodal pairs"
            ),
            "no_lower_upper_collision": True,
        },
        "verdict": "VERIFIED_WITH_SHARPENING",
        "boundary": {
            "all_rows_excluded": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def main() -> int:
    result = compare()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    canonical = HERE / "comparison.json"
    if canonical.exists():
        if canonical.read_text(encoding="utf-8") != encoded:
            raise SystemExit("comparison.json is stale")
    else:
        canonical.write_text(encoded, encoding="utf-8", newline="\n")
    print(
        "PASS: all Wave 101 reported exact certificates match; "
        "mod-2 weighted upper sharpened; Conway-99 UNKNOWN"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
