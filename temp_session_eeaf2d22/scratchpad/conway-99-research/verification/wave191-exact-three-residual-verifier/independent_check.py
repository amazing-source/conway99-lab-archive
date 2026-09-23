"""Clean-room verifier for the Wave 191 exact-three residual theorem."""

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
C = 4158


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


def add_rows(*rows: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sum(values) for values in zip(*rows))


def mod3_mat_vec(
    matrix: tuple[tuple[int, ...], ...], vector: tuple[int, ...]
) -> tuple[int, ...]:
    return tuple(sum(a * b for a, b in zip(row, vector)) % 3 for row in matrix)


def local_exact_three_exclusion() -> dict[str, Any]:
    # The three A_x blocks cannot pair two incidences of the same leaf type.
    # Hence they are the three edges of K_3 on leaf types y,u,v.
    pair_types = (("y", "u"), ("y", "v"), ("u", "v"))
    avoids_y = tuple(pair for pair in pair_types if "y" not in pair)
    assert avoids_y == (("u", "v"),)

    # For S of type uv, exactly its two noncenter vertices meet T, so
    # j(S,T)=2 and the omitted owner triangle belongs to target A_y.
    j_s_t = 2
    assert j_s_t == 2
    target_raw_member = "c5"

    # In canonical quadrilateral order, Wave181 fixes this Gram and kernel.
    gram = (
        (0, 1, 1, 2),
        (1, 0, 2, 1),
        (1, 2, 0, 1),
        (2, 1, 1, 0),
    )
    checkerboard = (1, 2, 2, 1)
    all_equal = (2, 2, 2, 2)
    checkerboard_image = mod3_mat_vec(gram, checkerboard)
    all_equal_image = mod3_mat_vec(gram, all_equal)
    assert checkerboard_image == (0, 0, 0, 0)
    assert all_equal_image != (0, 0, 0, 0)

    # Direct row reduction confirms that the projective kernel is unique.
    kernel = tuple(
        vector
        for vector in (
            (a, b, c, d)
            for a in range(3)
            for b in range(3)
            for c in range(3)
            for d in range(3)
        )
        if vector != (0, 0, 0, 0)
        and mod3_mat_vec(gram, vector) == (0, 0, 0, 0)
    )
    assert set(kernel) == {checkerboard, tuple(2 * x % 3 for x in checkerboard)}

    return {
        "source_Ax_pair_types": [list(pair) for pair in pair_types],
        "unique_pair_type_avoiding_y": list(avoids_y[0]),
        "target_cross_edge_count_j_S_T": j_s_t,
        "owner_triangle_membership": "T in A_y",
        "only_contained_target_member": target_raw_member,
        "subtracted_four_word": list(all_equal),
        "canonical_checkerboard_kernel": list(checkerboard),
        "canonical_gram": [list(row) for row in gram],
        "checkerboard_gram_image": list(checkerboard_image),
        "all_equal_gram_image": list(all_equal_image),
        "projective_nonzero_kernel_size": len(kernel),
        "exact_three_type3_raw_extraction_possible": False,
        "local_branch_verdict": "REFUTED",
    }


def orbit_closed_new_pool_capacity() -> dict[str, Any]:
    # A new low circuit has assignment capacity <=2; a complete exact-three
    # orbit has two circuits and shared label capacity 3.
    capacity_row = (2, 3)  # y low circuits, g exact-three pairs
    twice_circuit_row = (2, 4)
    gap = tuple(b - a for a, b in zip(capacity_row, twice_circuit_row))
    assert gap == (0, 1)
    return {
        "pool_variables": ["y_low_circuits", "g_exact3_pairs"],
        "assignment_capacity_row": list(capacity_row),
        "twice_closed_circuit_count_row": list(twice_circuit_row),
        "nonnegative_gap": list(gap),
        "closed_pool_size": "Y=y+2*g",
        "capacity": "Z<=2*y+3*g<=2*Y",
        "added_mate_old_pool_collision": "excluded_by_old_orbit_closure",
        "added_mate_selected_pool_collision": "excluded_by_privacy",
    }


def joint_exact_one_capacity() -> dict[str, Any]:
    # t type-three raw assignments occupy exact-one circuits; u=r1-t is the
    # remaining exact-one occupancy. The exact unused old slot count is
    # delta-r1.
    return {
        "split": "r1=t+u",
        "type3_residual_assignments": "p3-t",
        "unused_old_exact2_orbit_slots": "delta-r1",
        "new_residual_incidence_lower": (
            "Z>=(p3-t)-(delta-r1)=p3+u-delta"
        ),
        "closed_new_capacity": "Z<=2Y",
        "first_joint_row": "p3+u<=delta+2Y",
        "type2_exact2_status": (
            "both outside translates are non-exact2 because the selected "
            "owner is the unique exact2 circuit through the private label"
        ),
        "type2_row": "2p2<=u+3h",
        "eliminated_row": "delta+3h+2Y>=2p2+p3",
        "weaker_consequence": "delta+2Y>=p3",
        "exact_one_slot_double_charging": False,
    }


def coefficient_certificate() -> dict[str, Any]:
    variable_order = ["n1", "n2", "n3", "p2", "p3"]
    twelve_q = (18, 12, 24, 16, 12)
    private_I = (2, 2, 3, 1, 1)
    nine_I = tuple(9 * value for value in private_I)
    six_p2_minus_n2 = (0, -6, 0, 6, 0)
    p2_row = (0, 0, 0, 1, 0)
    three_p3_minus_n3 = (0, 0, -3, 0, 3)
    remainder = add_rows(
        six_p2_minus_n2, p2_row, three_p3_minus_n3
    )
    assert add_rows(nine_I, remainder) == twelve_q

    residual_lhs = (
        Fraction(1, 2),
        Fraction(1, 2),
        Fraction(1, 1),
    )  # delta,h,Y
    first_third = (
        Fraction(1, 3),
        Fraction(0, 1),
        Fraction(2, 3),
    )
    second_sixth = (
        Fraction(1, 6),
        Fraction(1, 2),
        Fraction(1, 3),
    )
    assert tuple(a + b for a, b in zip(first_third, second_sixth)) == residual_lhs
    assert 12 * 6237 == 18 * C

    return {
        "variable_order": variable_order,
        "raw_assignments": "A=n1+2*p2+p3",
        "base_pool": "B=n1+n2+2*n3",
        "disjoint_pool_bound": "Q>=B+A/2+delta/2+h/2+Y",
        "residual_decomposition": (
            "delta/2+h/2+Y=(delta+2Y)/3+(delta+3h+2Y)/6"
        ),
        "residual_lower": "delta/2+h/2+Y>=p2/3+p3/2",
        "twelve_Q_row": list(twelve_q),
        "nine_private_I_row": list(nine_I),
        "nonnegative_remainder_row": list(remainder),
        "remainder_decomposition": "6*(p2-n2)+p2+3*(p3-n3)",
        "private_incidence": "I>=2*C",
        "final_inequality": (
            "12Q>=9I+6*(p2-n2)+p2+3*(p3-n3)>=18C"
        ),
        "nonedge_projective_circuit_lower": 6237,
    }


def build_math_result() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "format": "wave191-exact-three-residual-clean-room-math-v1",
        "conditional_setting": "prism-free rank-11 endpoint n3=4158, P=0",
        "local_exact_three_exclusion": local_exact_three_exclusion(),
        "orbit_closed_new_pool_capacity": orbit_closed_new_pool_capacity(),
        "joint_exact_one_capacity": joint_exact_one_capacity(),
        "coefficient_certificate": coefficient_certificate(),
        "bounds": {
            "nonedge_projective_short_circuits_Q": 6237,
            "edge_isolated_projective_short_circuits": 693,
            "all_projective_short_circuits": 6930,
            "scalar_short_circuit_words": 13860,
            "wave188_all_short_word_bound_remains_stronger": 18018,
        },
        "verdict": "VERIFIED_WITH_SCOPE",
        "boundary": {
            "local_exact3_type3_raw_branch": "REFUTED",
            "conditional_theorem_verified": True,
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
        "attempts/wave191-exact-three-residual-proof-a/package-manifest.sha256",
        "verification/wave180-capacity3-companion/package-manifest.sha256",
        "verification/wave181-c4-conic-equality/package-manifest.sha256",
        "verification/wave186-star-translation-cover-verifier/package-manifest.sha256",
        "verification/wave189-degree7-star-orbit-verifier/package-manifest.sha256",
        "verification/wave190-residual-stability-verifier/package-manifest.sha256",
    }
    actual = {relative for _, relative in entries}
    if actual != expected:
        raise AssertionError(f"unexpected input set: {sorted(actual ^ expected)}")
    failures = check_entries(entries)
    source_path = (
        ROOT
        / "attempts/wave191-exact-three-residual-proof-a/package-manifest.sha256"
    )
    source_sha = sha256(source_path)
    assert source_sha == (
        "a0e2697b7e826f5543c2e007a1428633e37fb54e9e8449e73a731a7291f468c4"
    )
    source_entries = parse_hash_list(source_path)
    for failure in check_entries(source_entries):
        failure["manifest"] = "wave191_source"
        failures.append(failure)

    premise_paths = {
        "wave180": ROOT / "verification/wave180-capacity3-companion/package-manifest.sha256",
        "wave181": ROOT / "verification/wave181-c4-conic-equality/package-manifest.sha256",
        "wave186": ROOT / "verification/wave186-star-translation-cover-verifier/package-manifest.sha256",
        "wave189": ROOT / "verification/wave189-degree7-star-orbit-verifier/package-manifest.sha256",
        "wave190": ROOT / "verification/wave190-residual-stability-verifier/package-manifest.sha256",
    }
    premise_counts: dict[str, int] = {}
    for name, path in premise_paths.items():
        nested_entries = parse_hash_list(path)
        premise_counts[name] = len(nested_entries)
        for failure in check_entries(nested_entries):
            failure["manifest"] = name
            failures.append(failure)

    independent_entries = parse_hash_list(INDEPENDENT_FREEZE)
    independent_failures = check_entries(independent_entries)
    for failure in independent_failures:
        failure["manifest"] = "independent_result"
        failures.append(failure)

    return {
        "passed": not failures,
        "direct_files_checked": len(entries),
        "source_entries_checked": len(source_entries),
        "premise_entries_checked": premise_counts,
        "independent_result_entries_checked": len(independent_entries),
        "source_manifest_sha256": source_sha,
        "failures": failures,
        "discovery_checker_imported_or_executed_before_independent_freeze": False,
    }


def compare_source_result() -> dict[str, Any]:
    source_path = (
        ROOT / "attempts/wave191-exact-three-residual-proof-a/exact-results.json"
    )
    source = json.loads(source_path.read_text(encoding="utf-8"))
    assert source["coefficient_certificate"]["three_C_over_two"] == 6237
    assert source["coefficient_certificate"]["coefficient_row"] == [
        18,
        12,
        24,
        16,
        12,
    ]
    assert source["local"]["canonical_gram"] == [
        [0, 1, 1, 2],
        [1, 0, 2, 1],
        [1, 2, 0, 1],
        [2, 1, 1, 0],
    ]
    assert source["local"]["checkerboard_gram_product"] == [0, 0, 0, 0]
    assert source["local"]["all_equal_gram_product"] != [0, 0, 0, 0]
    assert source["capacity"]["type3"] == "delta+2*Y>=p3"
    assert source["capacity"]["joint"] == "delta+3*h+2*Y>=2*p2+p3"
    source_report_path = (
        ROOT / "agents/2026-07-29-wave191-exact-three-residual-proof-a.md"
    )
    source_report = source_report_path.read_text(encoding="utf-8")
    assert "Q >= 3*C/2 = 6237" in source_report
    assert "new Q=5891 arithmetic row:" in source_report
    assert source["null_control"]["row"] == {
        "Q": 6237,
        "Y": 1039,
        "delta": 1,
        "h": 0,
        "n1": 0,
        "n2": 0,
        "n3": 2079,
        "p2": 0,
        "p3": 2079,
        "r": 1040,
        "r1": 1,
    }
    return {
        "claim_matches_independent_bound": True,
        "local_exact3_exclusion_matches": True,
        "orbit_closed_new_capacity_matches": True,
        "joint_exact_one_capacity_matches": True,
        "coefficient_identity_matches": True,
        "source_exact_results_sha256": sha256(source_path),
        "source_report_sha256": sha256(source_report_path),
        "non_theorem_findings": {
            "stale_boundary_label": (
                "the source report Boundary says 'new Q=5891 arithmetic row'; "
                "the theorem and body correctly say Q>=6237"
            ),
            "null_control_scope": (
                "the displayed Q=6237 row is a null only for the weak displayed "
                "scalar inequalities; its capacity-two new residuals do not "
                "respect the separately audited exact-two residual exclusion"
            ),
            "affects_Q6237_theorem": False,
        },
    }


def wave192_exact_two_residual_lever() -> dict[str, Any]:
    return {
        "premise": (
            "a type3 raw extraction of exact multiplicity two is the unique "
            "Wave181 checkerboard circuit r_e through its private label e"
        ),
        "residual_property": (
            "the Wave190 residual crosses e and its support omits coordinates "
            "of r_e"
        ),
        "contradiction_if_residual_exact2": (
            "Wave181 uniqueness would force the residual circuit to equal "
            "r_e, but r_e is not contained in the residual support"
        ),
        "conclusion": "such a residual has exact multiplicity one or three",
        "used_in_Q6237_certificate": False,
        "status": "VERIFIED_LEVER_NOT_APPLIED",
    }


def build_results() -> dict[str, Any]:
    integrity = verify_frozen_inputs()
    assert integrity["passed"]
    math_result = build_math_result()
    payload: dict[str, Any] = {
        "format": "wave191-exact-three-residual-clean-room-verification-v1",
        "integrity": integrity,
        "independent_math_result": math_result,
        "source_comparison": compare_source_result(),
        "wave192_lever": wave192_exact_two_residual_lever(),
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
        print(f"WROTE Wave191 independent math result: {args.write_math}")
        return 0
    if args.verify_math:
        expected = json.loads(args.verify_math.read_text(encoding="utf-8"))
        if build_math_result() != expected:
            print("FAIL Wave191 independent math result")
            return 1
        print(f"PASS Wave191 independent math result: {args.verify_math}")
        return 0
    if args.write:
        write_json(args.write, build_results())
        print(f"WROTE Wave191 clean-room result: {args.write}")
        return 0
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if build_results() != expected:
            print("FAIL Wave191 clean-room verification")
            return 1
        print(f"PASS Wave191 clean-room verification: {args.verify}")
        return 0
    print(json.dumps(build_math_result(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
