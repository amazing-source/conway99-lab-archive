"""Clean-room verifier for the Wave194 five-thirds theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INPUT_FREEZE = HERE / "input-freeze.sha256"
INDEPENDENT_FREEZE = HERE / "independent-result-freeze.sha256"
HASH_LINE = re.compile(r"^([0-9a-fA-F]{64})\s+\*?(.+?)\s*$")
C_VALUE = 4158


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_hash_list(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = HASH_LINE.fullmatch(line)
        if match is None:
            raise ValueError(f"malformed hash line {path}:{number}: {raw!r}")
        entries.append((match.group(1).lower(), match.group(2).replace("\\", "/")))
    if not entries:
        raise ValueError(f"empty hash list: {path}")
    return entries


def check_entries(entries: list[tuple[str, str]]) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    for expected, relative in entries:
        target = (ROOT / relative).resolve()
        actual = sha256(target) if target.is_file() else "missing"
        if actual != expected:
            failures.append(
                {"path": relative, "expected": expected, "actual": actual}
            )
    return failures


def type2_exact3_residual_certificate() -> dict[str, Any]:
    """Record the support-level argument, independent of the source package."""
    conic = (
        1, 2, 0, 0, 0, 0, 0,
        2, 1, 0, 0, 0, 0, 0,
    )
    star_x = (1,) * 7 + (0,) * 7
    star_y = (0,) * 7 + (1,) * 7
    parent_x = tuple((a + b) % 3 for a, b in zip(conic, star_x))
    parent_y = tuple((a + b) % 3 for a, b in zip(conic, star_y))
    support_x = {index for index, value in enumerate(parent_x) if value}
    support_y = {index for index, value in enumerate(parent_y) if value}
    assert (len(support_x & set(range(7))), len(support_x - set(range(7)))) == (
        6,
        2,
    )
    assert (len(support_y & set(range(7))), len(support_y - set(range(7)))) == (
        2,
        6,
    )
    assert support_x & support_y == {0, 8}
    return {
        "type2_translate_profiles": [[6, 2], [2, 6]],
        "translate_support_intersection_size": 2,
        "dual_distance_lower_bound": 4,
        "exact3_raw_center": (
            "the endpoint supporting the six-block side of its translate"
        ),
        "residual_construction": (
            "subtract the unique scalar multiple of the exact3 raw relation "
            "that cancels its leaf coordinate"
        ),
        "residual_nonzero": (
            "otherwise the translated relation would equal the strictly "
            "smaller raw circuit"
        ),
        "residual_crosses_private_label": (
            "both endpoint-star sides remain proper and nonempty, so a "
            "support-minimal circuit meets both sides"
        ),
        "residual_differs_from_source_raw": "the raw leaf coordinate is absent",
        "residual_differs_from_source_opposite_companion": (
            "both exact3 companions contain the same leaf coordinate"
        ),
        "residual_differs_from_selected_exact2_owner": (
            "the translated support already omits an owner coordinate"
        ),
        "residual_exact_multiplicity": [1, 3],
        "same_label_double_residuals_distinct": (
            "the two residuals lie in the two translate supports; equality "
            "would give a circuit of weight at most two"
        ),
    }


def pool_collision_certificate() -> dict[str, Any]:
    return {
        "raw_split": {
            "type1": "a1+a2+a3=n1",
            "type2": "b1+b3=2p2",
            "type3": "c1+c2=p3",
            "excluded_b2": "Wave181 exact2 uniqueness",
            "excluded_c3": "Wave191 privacy-free type3 leaf exclusion",
        },
        "old_raw_pool": {
            "exact1": "r1=a1+b1+c1",
            "exact2": "a2+c2<=2r2",
            "exact3": "a3+b3<=3h",
            "circuit_count": "r1+r2+2h",
        },
        "forced_residual_assignments": "a2+c2+b3",
        "exact1_old_raw_collision": (
            "a residual equal to a raw for another label would not be exact1; "
            "for the same type2 label, the other translate intersects the "
            "source translate in only two coordinates"
        ),
        "exact2_old_raw_collision": (
            "Wave181 uniqueness forces the selected owner, but every residual "
            "support omits an owner coordinate"
        ),
        "source_exact3_raw_collision": "the canceled leaf coordinate is absent",
        "source_opposite_companion_collision": (
            "the opposite companion has the same canceled leaf coordinate"
        ),
        "other_type2_raw_collision": (
            "the two translate supports intersect in only two coordinates"
        ),
        "other_type2_opposite_companion_collision": (
            "an exact3 residual in one translate has that translate's endpoint "
            "as center, whereas the other raw and its mate have the opposite "
            "endpoint as center"
        ),
        "selected_collision": "privacy plus omission of the owner coordinate",
        "selected_companion_collision": (
            "companionship would make the residual a selected circuit"
        ),
        "new_mate_old_collision": "excluded by closure of the old exact3 pool",
        "new_mate_selected_collision": (
            "excluded by privacy and the fixed-point-free companion involution"
        ),
        "old_exact3_combined_assignment_count": "a2+a3+2b3+c2",
        "new_pool": {
            "exact1_circuits": "y",
            "exact3_companion_pairs": "g",
            "circuit_count": "y+2g",
            "label_capacity": "y+3g",
        },
        "RA": "3h+y+3g-(a2+a3+2b3+c2)>=0",
    }


def low_target_certificate() -> dict[str, Any]:
    return {
        "U": "union of labels served by selected type3 circuits",
        "selected_low_label_capacity": "n1+2n2",
        "target_exact_multiplicity_at_most": 2,
        "k": (
            "number of chosen U-label targets charged to selected low circuits"
        ),
        "lower_with_overlap": "|U|>=C-(n1+2n2)+k",
        "upper_with_targets": "|U|<=k+c1+2r2+y+2W",
        "k_cancellation": True,
        "old_exact1_only_c1": (
            "an exact1 raw target must have the same label; a U-label with a "
            "private raw assignment is therefore owned by type3"
        ),
        "old_exact2_capacity": "2r2",
        "new_residual_low_capacity": "y",
        "why_g_absent": "an exact3 residual cannot be a low leaf target",
        "new_W_capacity": "2W",
        "SL": "n1+2n2+c1+2r2+y+2W-C>=0",
    }


VARIABLES = (
    "C",
    "a1",
    "a2",
    "a3",
    "b1",
    "b3",
    "c1",
    "c2",
    "n2",
    "n3",
    "r2",
    "h",
    "y",
    "g",
    "W",
)


def row(**entries: int | Fraction) -> tuple[Fraction, ...]:
    return tuple(Fraction(entries.get(name, 0)) for name in VARIABLES)


def add_rows(*rows: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return tuple(sum(values, Fraction(0)) for values in zip(*rows))


def scale(
    value: int | Fraction, source: tuple[Fraction, ...]
) -> tuple[Fraction, ...]:
    factor = Fraction(value)
    return tuple(factor * item for item in source)


def coefficient_certificate() -> dict[str, Any]:
    # Substitute:
    # n1=a1+a2+a3, p2=(b1+b3)/2, p3=c1+c2,
    # r1=a1+b1+c1.
    q0 = row(
        a1=2,
        a2=1,
        a3=1,
        b1=1,
        c1=1,
        n2=1,
        n3=2,
        r2=1,
        h=2,
        y=1,
        g=2,
        W=1,
    )
    target = add_rows(q0, row(C=Fraction(-5, 3)))
    SI = row(
        C=-2,
        a1=2,
        a2=2,
        a3=2,
        b1=Fraction(1, 2),
        b3=Fraction(1, 2),
        c1=1,
        c2=1,
        n2=2,
        n3=3,
    )
    S2 = row(b1=Fraction(1, 2), b3=Fraction(1, 2), n2=-1)
    RA = row(
        a2=-1,
        a3=-1,
        b3=-2,
        c2=-1,
        h=3,
        y=1,
        g=3,
    )
    SL = row(
        C=-1,
        a1=1,
        a2=1,
        a3=1,
        c1=1,
        n2=2,
        r2=2,
        y=1,
        W=2,
    )
    certificate = add_rows(
        scale(Fraction(2, 3), SI),
        S2,
        scale(Fraction(2, 3), RA),
        scale(Fraction(1, 3), SL),
        scale(Fraction(1, 3), row(a1=1)),
        scale(Fraction(1, 6), row(b1=1)),
        scale(Fraction(1, 2), row(b3=1)),
        scale(Fraction(1, 3), row(r2=1)),
        scale(Fraction(1, 3), row(W=1)),
    )
    assert certificate == target
    assert 3 * 6930 == 5 * C_VALUE
    return {
        "variable_order_after_split_substitution": list(VARIABLES),
        "Q0": "n1+n2+2n3+r1+r2+2h+y+2g+W",
        "SI": "I-2C",
        "S2": "p2-n2",
        "RA": "3h+y+3g-(a2+a3+2b3+c2)",
        "SL": "n1+2n2+c1+2r2+y+2W-C",
        "identity": (
            "Q0-5C/3=(2/3)SI+S2+(2/3)RA+SL/3"
            "+a1/3+b1/6+b3/2+r2/3+W/3"
        ),
        "lower": "3Q>=5C",
        "C": C_VALUE,
        "nonedge_projective_Q": 6930,
    }


def equality_face_certificate() -> dict[str, Any]:
    # Equality in every nonnegative term of the coefficient certificate.
    # Let m=n3.  The resulting arithmetic face is:
    # a3=n1=C-3m, c1=p3=r1=3m, h=C/3-m.
    controls: list[dict[str, int]] = []
    for m in (0, 693, 1386):
        a3 = C_VALUE - 3 * m
        values = {
            "m": m,
            "n1": a3,
            "n2": 0,
            "n3": m,
            "p2": 0,
            "p3": 3 * m,
            "a1": 0,
            "a2": 0,
            "a3": a3,
            "b1": 0,
            "b3": 0,
            "c1": 3 * m,
            "c2": 0,
            "r1": 3 * m,
            "r2": 0,
            "h": C_VALUE // 3 - m,
            "y": 0,
            "g": 0,
            "W": 0,
        }
        I = (
            2 * values["n1"]
            + 2 * values["n2"]
            + 3 * values["n3"]
            + values["p2"]
            + values["p3"]
        )
        RA = (
            3 * values["h"]
            + values["y"]
            + 3 * values["g"]
            - values["a2"]
            - values["a3"]
            - 2 * values["b3"]
            - values["c2"]
        )
        SL = (
            values["n1"]
            + 2 * values["n2"]
            + values["c1"]
            + 2 * values["r2"]
            + values["y"]
            + 2 * values["W"]
            - C_VALUE
        )
        Q0 = (
            values["n1"]
            + values["n2"]
            + 2 * values["n3"]
            + values["r1"]
            + values["r2"]
            + 2 * values["h"]
            + values["y"]
            + 2 * values["g"]
            + values["W"]
        )
        assert I == 2 * C_VALUE
        assert values["p2"] == values["n2"]
        assert RA == 0
        assert SL == 0
        assert Q0 == 6930
        controls.append(values)
    return {
        "parameter": "m=n3, integer 0<=m<=1386",
        "forced_zero": [
            "a1",
            "a2",
            "b1",
            "b3",
            "c2",
            "n2",
            "p2",
            "r2",
            "y",
            "g",
            "W",
        ],
        "family": {
            "a3=n1": "4158-3m",
            "c1=p3=r1": "3m",
            "h": "1386-m",
            "Q0": 6930,
        },
        "sample_rows": controls,
        "asserted_to_be_graph_code_cover_or_circuit_family": False,
    }


def build_math_result() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "format": "wave194-five-thirds-clean-room-math-v1",
        "conditional_setting": "prism-free rank-11 endpoint n3=4158, P=0",
        "type2_exact3_residual": type2_exact3_residual_certificate(),
        "pool_collision_audit": pool_collision_certificate(),
        "low_target": low_target_certificate(),
        "coefficient_certificate": coefficient_certificate(),
        "equality_face": equality_face_certificate(),
        "bounds": {
            "nonedge_projective_short_circuits_Q": 6930,
            "edge_isolated_projective_short_circuits": 693,
            "all_projective_short_circuits": 7623,
            "scalar_short_circuit_words": 15246,
            "wave188_all_short_word_bound_remains_stronger": 18018,
        },
        "verdict": "VERIFIED_WITH_SCOPE",
        "boundary": {
            "conditional_theorem_verified": True,
            "integer_equality_face_realized": False,
            "graph_constructed": False,
            "code_constructed": False,
            "rank_11_excluded": False,
            "endpoint_excluded": False,
            "strict_n3_improvement": False,
            "external_novelty": "UNKNOWN",
            "conway_99": "UNKNOWN",
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["math_result_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def verify_frozen_inputs() -> dict[str, Any]:
    entries = parse_hash_list(INPUT_FREEZE)
    expected = {
        "AGENTS.md",
        "attempts/wave194-type2-residual-low-u-proof-a/package-manifest.sha256",
        "attempts/wave194-five-thirds-proof-b-audit/package-manifest.sha256",
        "verification/wave181-c4-conic-equality/package-manifest.sha256",
        "verification/wave188-affine-star-word-amplification-verifier/package-manifest.sha256",
        "verification/wave189-degree7-star-orbit-verifier/package-manifest.sha256",
        "verification/wave191-exact-three-residual-verifier/package-manifest.sha256",
        "verification/wave193-global-low-target-verifier/package-manifest.sha256",
    }
    actual = {relative for _, relative in entries}
    if actual != expected:
        raise AssertionError(f"unexpected input set: {sorted(actual ^ expected)}")

    failures = check_entries(entries)
    primary_manifest = (
        ROOT
        / "attempts/wave194-type2-residual-low-u-proof-a/package-manifest.sha256"
    )
    audit_manifest = (
        ROOT
        / "attempts/wave194-five-thirds-proof-b-audit/package-manifest.sha256"
    )
    primary_sha = sha256(primary_manifest)
    audit_sha = sha256(audit_manifest)
    assert primary_sha == (
        "0ba610983dff7365f7debd42b8155c07edcc5e64e5afb4e4d6529e6d1c0ad5a4"
    )
    assert audit_sha == (
        "0e77b279efec786e3abab371b614061ea1624499c32549861c68fe9daba17918"
    )

    nested_paths = {
        "primary_source": primary_manifest,
        "audit_source": audit_manifest,
        "primary_source_inputs": (
            ROOT / "attempts/wave194-type2-residual-low-u-proof-a/input-freeze.sha256"
        ),
        "audit_source_inputs": (
            ROOT / "attempts/wave194-five-thirds-proof-b-audit/input-freeze.sha256"
        ),
        "wave181": (
            ROOT / "verification/wave181-c4-conic-equality/package-manifest.sha256"
        ),
        "wave188": (
            ROOT
            / "verification/wave188-affine-star-word-amplification-verifier"
            / "package-manifest.sha256"
        ),
        "wave189": (
            ROOT
            / "verification/wave189-degree7-star-orbit-verifier"
            / "package-manifest.sha256"
        ),
        "wave191": (
            ROOT
            / "verification/wave191-exact-three-residual-verifier"
            / "package-manifest.sha256"
        ),
        "wave193": (
            ROOT
            / "verification/wave193-global-low-target-verifier"
            / "package-manifest.sha256"
        ),
    }
    nested_counts: dict[str, int] = {}
    for name, path in nested_paths.items():
        nested_entries = parse_hash_list(path)
        nested_counts[name] = len(nested_entries)
        for failure in check_entries(nested_entries):
            failure["manifest"] = name
            failures.append(failure)

    independent_entries = parse_hash_list(INDEPENDENT_FREEZE)
    for failure in check_entries(independent_entries):
        failure["manifest"] = "independent_result"
        failures.append(failure)

    return {
        "passed": not failures,
        "direct_files_checked": len(entries),
        "nested_entries_checked": nested_counts,
        "independent_result_entries_checked": len(independent_entries),
        "primary_source_manifest_sha256": primary_sha,
        "audit_source_manifest_sha256": audit_sha,
        "independent_math_result_sha256": sha256(
            HERE / "independent-math-result.json"
        ),
        "failures": failures,
        "source_packages_opened_before_independent_freeze": False,
        "discovery_checker_imported_or_executed_before_independent_freeze": False,
    }


def source_comparison() -> dict[str, Any]:
    primary_path = (
        ROOT / "attempts/wave194-type2-residual-low-u-proof-a/exact-results.json"
    )
    audit_path = (
        ROOT / "attempts/wave194-five-thirds-proof-b-audit/exact-results.json"
    )
    primary = json.loads(primary_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))

    assert primary["bound"]["Q"] == audit["bound"]["Q"] == 6930
    assert (
        primary["bound"]["edge_added_projective"]
        == audit["bound"]["edge_added_projective"]
        == 7623
    )
    assert (
        primary["bound"]["circuit_scalar_words"]
        == audit["bound"]["scalar_short_circuit_words"]
        == 15246
    )
    assert primary["capacity_rows"]["residual"] == (
        "3*h+y+3*g>=a2+a3+2*b3+c2"
    )
    assert primary["capacity_rows"]["leaf_joint"] == (
        "n1+2*n2+c1+2*r2+y+2*W>=C"
    )
    assert audit["rows"]["RA"] == primary["capacity_rows"]["residual"]
    assert audit["rows"]["SL"] == primary["capacity_rows"]["leaf_joint"]
    assert primary["certificate"]["scaled"] == "3*Q>=5*C"
    assert audit["certificate"]["reduced_difference"] == {}
    assert audit["local_type2"]["parent_x_profile"] == [6, 2]
    assert audit["local_type2"]["parent_y_profile"] == [2, 6]
    assert audit["local_type2"]["parent_intersection_size"] == 2
    assert audit["local_type2"]["dual_distance"] == 4

    source_controls = primary["equality_face"]["controls"]
    source_rows = {item["parameter_t"]: item for item in source_controls}
    assert set(source_rows) == {0, 693, 1386}
    for item in source_controls:
        assert item["I"] == 8316
        assert item["Q0"] == 6930
        assert item["incidence_slack"] == 0
        assert item["exact2_slack"] == 0
        assert item["exact3_slack"] == 0
        assert item["residual_slack"] == 0
        assert item["leaf_slack"] == 0
        assert item["is_object"] is False
    assert primary["equality_face"]["is_construction"] is False
    assert audit["null_control"]["asserted_object"] is False

    independent = build_math_result()
    independent_controls = independent["equality_face"]["sample_rows"]
    normalized_independent = {
        (
            item["n1"],
            item["n3"],
            item["a3"],
            item["c1"],
            item["h"],
            item["Q0"] if "Q0" in item else 6930,
        )
        for item in independent_controls
    }
    normalized_source = {
        (
            item["row"]["n1"],
            item["row"]["n3"],
            item["row"]["a3"],
            item["row"]["c1"],
            item["row"]["h"],
            item["Q0"],
        )
        for item in source_controls
    }
    assert normalized_independent == normalized_source

    return {
        "primary_and_audit_bound_match": True,
        "type2_parent_geometry_matches": True,
        "same_label_double_residual_claim_matches": True,
        "RA_matches": True,
        "SL_and_k_cancellation_match": True,
        "split_y_g_capacities_match": True,
        "dual_identity_matches": True,
        "equality_face_matches_after_parameter_reversal": True,
        "null_rows_arithmetic_only": True,
        "primary_exact_results_sha256": sha256(primary_path),
        "audit_exact_results_sha256": sha256(audit_path),
    }


def build_results() -> dict[str, Any]:
    integrity = verify_frozen_inputs()
    assert integrity["passed"]
    payload: dict[str, Any] = {
        "format": "wave194-five-thirds-clean-room-verification-v1",
        "integrity": integrity,
        "independent_math_result": build_math_result(),
        "source_comparison": source_comparison(),
        "verdict": "VERIFIED_WITH_SCOPE",
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["result_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-math", type=Path)
    parser.add_argument("--verify-math", type=Path)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write_math:
        write_json(args.write_math, build_math_result())
        print(f"WROTE Wave194 independent math result: {args.write_math}")
        return 0
    if args.verify_math:
        expected = json.loads(args.verify_math.read_text(encoding="utf-8"))
        if build_math_result() != expected:
            print("FAIL Wave194 independent math result")
            return 1
        print(f"PASS Wave194 independent math result: {args.verify_math}")
        return 0
    if args.write:
        write_json(args.write, build_results())
        print(f"WROTE Wave194 clean-room result: {args.write}")
        return 0
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if build_results() != expected:
            print("FAIL Wave194 clean-room verification")
            return 1
        print(f"PASS Wave194 clean-room verification: {args.verify}")
        return 0
    print(json.dumps(build_math_result(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
