"""Clean-room verifier for the Wave 190 residual-stability theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INPUT_FREEZE = HERE / "input-freeze.sha256"
HASH_LINE = re.compile(r"^([0-9a-fA-F]{64})\s+\*?(.+?)\s*$")
C = 4158


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_hash_list(path: Path) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = HASH_LINE.fullmatch(line)
        if match is None:
            raise ValueError(f"malformed hash line {path}:{number}: {raw!r}")
        result.append((match.group(1).lower(), match.group(2).replace("\\", "/")))
    if not result:
        raise ValueError(f"empty hash list: {path}")
    return result


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


def verify_frozen_inputs() -> dict[str, Any]:
    expected = {
        "AGENTS.md",
        "agents/2026-07-29-wave190-residual-stability-proof-b.md",
        "agents/2026-07-29-wave190-residual-stability-proof-a-audit.md",
        "attempts/wave190-residual-stability-proof-b/package-manifest.sha256",
        "verification/wave189-degree7-star-orbit-verifier/package-manifest.sha256",
    }
    entries = parse_hash_list(INPUT_FREEZE)
    actual = {relative for _, relative in entries}
    if actual != expected:
        raise AssertionError(f"unexpected input set: {sorted(actual ^ expected)}")
    failures = check_entries(entries)

    source = ROOT / "attempts/wave190-residual-stability-proof-b/package-manifest.sha256"
    wave189 = ROOT / "verification/wave189-degree7-star-orbit-verifier/package-manifest.sha256"
    assert sha256(source) == "e66987333e3f7119026520be9680699bcfdcfcddbf8877016d8d817193684a5a"
    assert sha256(wave189) == "fc17484bd8c32a5886ecdcc65d153903cef5f3b60a3de1c9905ed96697c273c4"
    nested = {
        "wave190_source": parse_hash_list(source),
        "wave189_verifier": parse_hash_list(wave189),
    }
    assert len(nested["wave190_source"]) == 9
    assert len(nested["wave189_verifier"]) == 8
    for name, nested_entries in nested.items():
        for failure in check_entries(nested_entries):
            failure["manifest"] = name
            failures.append(failure)
    return {
        "passed": not failures,
        "direct_files_checked": len(entries),
        "nested_entries_checked": {
            name: len(values) for name, values in nested.items()
        },
        "source_manifest_sha256": sha256(source),
        "wave189_verifier_manifest_sha256": sha256(wave189),
        "failures": failures,
        "discovery_checker_imported_or_executed_by_verifier": False,
    }


def add_rows(*rows: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sum(entries) for entries in zip(*rows))


def orbit_label_capacity_certificate() -> dict[str, Any]:
    # For each of the three labels of an exact-three companion orbit, the
    # permitted combined-use state is none, raw, or residual.  Raw+residual
    # for one label is excluded by the source-type split.
    states = tuple(product(("none", "raw", "residual"), repeat=3))
    occupancies = [
        sum(value != "none" for value in state) for state in states
    ]
    assert len(states) == 27
    assert max(occupancies) == 3

    # Center orientation independently rules out putting both type-two raw
    # extractions for one label into the same companion pair.
    exact_three_profiles = {
        "center_x": {(3, 1), (4, 1)},
        "center_y": {(1, 3), (1, 4)},
    }
    support_x, support_y = (6, 2), (2, 6)
    fits_x = {
        center: {
            profile
            for profile in profiles
            if profile[0] <= support_x[0] and profile[1] <= support_x[1]
        }
        for center, profiles in exact_three_profiles.items()
    }
    fits_y = {
        center: {
            profile
            for profile in profiles
            if profile[0] <= support_y[0] and profile[1] <= support_y[1]
        }
        for center, profiles in exact_three_profiles.items()
    }
    assert fits_x["center_x"] and not fits_x["center_y"]
    assert fits_y["center_y"] and not fits_y["center_x"]
    return {
        "per_label_states": ["none", "raw", "residual"],
        "three_label_state_rows_checked": len(states),
        "maximum_combined_raw_residual_uses_per_orbit": max(occupancies),
        "raw_and_residual_mutually_exclusive_per_label": True,
        "type2_support_profiles": [[6, 2], [2, 6]],
        "first_support_forces_center": "x",
        "second_support_forces_center": "y",
        "companions_share_center": True,
        "two_type2_raw_extractions_cannot_be_orbit_mates": True,
        "capacity_consequence": "a_H+b_H<=3*h",
    }


def residual_slack_certificate() -> dict[str, Any]:
    variables = ["p3", "delta", "h", "Y", "k", "bH", "r1", "qH", "aH"]
    # Each tuple is a linear form in the variable order above.
    new_capacity = (0, 0, 0, 3, -1, 1, 0, 0, 0)
    exact_two_landings = (-1, 0, 0, 0, 1, 0, 1, 1, 0)
    exact_one_slack = (0, 1, 0, 0, 0, 0, -1, 0, 0)
    raw_type_slack = (0, 0, 0, 0, 0, 0, 0, -1, 1)
    orbit_capacity = (0, 0, 3, 0, 0, -1, 0, 0, -1)
    target = (-1, 1, 3, 3, 0, 0, 0, 0, 0)
    assert add_rows(
        new_capacity,
        exact_two_landings,
        exact_one_slack,
        raw_type_slack,
        orbit_capacity,
    ) == target

    # delta-r1 is exactly the improvement from actual low-circuit capacity.
    # delta=2r+3h-A and A<=2r-r1+3h.
    return {
        "variable_order": variables,
        "nonnegative_slacks": {
            "new_residual_capacity_3Y_minus_k_plus_bH": list(new_capacity),
            "exact_two_landing_k_minus_p3_plus_r1_plus_qH": list(exact_two_landings),
            "exact_one_delta_minus_r1": list(exact_one_slack),
            "all_raw_minus_type3_raw_aH_minus_qH": list(raw_type_slack),
            "orbit_labels_3h_minus_aH_minus_bH": list(orbit_capacity),
        },
        "sum_row": list(target),
        "sum_identity": "3Y-p3+delta+3h>=0",
        "equivalent_master_inequality": "delta+3h+3Y>=p3",
        "exact_one_capacity": "A<=2r-r1+3h, so r1<=delta",
        "low_raw_collision_excluded": {
            "residual_exact_one": "another raw label would force multiplicity at least two",
            "residual_exact_two": "Wave181 uniqueness would make it r_e, whose coordinates are omitted",
        },
        "selected_and_selected_companion_collisions_excluded_by_privacy": True,
    }


def coefficient_certificate() -> dict[str, Any]:
    variable_order = ["n1", "n2", "n3", "p2", "p3"]
    six_q = (9, 6, 12, 6, 4)
    private_I = (2, 2, 3, 1, 1)
    four_I = tuple(4 * value for value in private_I)
    remainder = (1, -2, 0, 2, 0)
    assert add_rows(four_I, remainder) == six_q
    assert remainder == (1, -2, 0, 2, 0)  # n1+2(p2-n2)
    assert 8 * C == 6 * 5544
    return {
        "variable_order": variable_order,
        "raw_assignments": "A=n1+2*p2+p3",
        "base_pool": "B=n1+n2+2*n3",
        "closed_pool_identity": "2r+3h=A+delta",
        "disjoint_pool_bound": "Q>=B+r+2h+Y",
        "stability_bound": "Q>=B+A/2+p3/6",
        "six_Q_row": list(six_q),
        "four_private_I_row": list(four_I),
        "nonnegative_remainder_row": list(remainder),
        "remainder_decomposition": "n1+2*(p2-n2)",
        "private_incidence": "I>=2*C",
        "final_inequality": "6Q>=4I+n1+2*(p2-n2)>=8C",
        "nonedge_projective_circuit_lower": 5544,
    }


def sharp_control_certificate() -> dict[str, Any]:
    n1 = n2 = p2 = r = delta = Y = 0
    n3, p3, h, Q = 1386, 4158, 1386, 5544
    r1 = k = bH = 0
    aH = qH = p3
    A = n1 + 2 * p2 + p3
    N = n1 + n2 + n3
    I = 2 * n1 + 2 * n2 + 3 * n3 + p2 + p3
    assert delta == 2 * r + 3 * h - A == 0
    assert r1 <= delta
    assert k >= p3 - r1 - qH
    assert aH + bH <= 3 * h
    assert delta + 3 * h + 3 * Y == p3
    assert Q == N + n3 + r + 2 * h + Y
    assert 6 * Q == 4 * I + n1 + 2 * (p2 - n2) == 8 * C
    return {
        "n1": n1, "n2": n2, "n3": n3, "p2": p2, "p3": p3,
        "r": r, "h": h, "delta": delta, "Y": Y, "Q": Q,
        "aH": aH, "qH": qH, "k": k, "bH": bH,
        "all_displayed_scalar_rows_saturated": True,
        "asserted_to_be_cover_or_graph": False,
    }


def build_results() -> dict[str, Any]:
    integrity = verify_frozen_inputs()
    assert integrity["passed"]
    payload: dict[str, Any] = {
        "format": "wave190-residual-stability-clean-room-verification-v1",
        "verdict": "VERIFIED_WITH_SCOPE",
        "integrity": integrity,
        "conditional_setting": "prism-free rank-11 endpoint n3=4158, P=0",
        "orbit_label_collision_capacity": orbit_label_capacity_certificate(),
        "residual_slack": residual_slack_certificate(),
        "coefficient_certificate": coefficient_certificate(),
        "sharp_arithmetic_control": sharp_control_certificate(),
        "bounds": {
            "nonedge_projective_short_circuits_Q": 5544,
            "edge_isolated_projective_short_circuits": 693,
            "all_projective_short_circuits": 6237,
            "scalar_short_circuit_words": 12474,
            "wave188_all_short_word_bound_remains_stronger": 18018,
        },
        "boundary": {
            "conditional_theorem_verified": True,
            "sharp_row_realized_by_cover": False,
            "code_constructed": False,
            "graph_constructed": False,
            "rank_11_excluded": False,
            "endpoint_excluded": False,
            "strict_n3_improvement": False,
            "external_novelty": "UNKNOWN",
            "conway_99": "UNKNOWN",
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["result_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    result = build_results()
    if args.write:
        args.write.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"WROTE Wave 190 clean-room result: {args.write}")
        return 0
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            print("FAIL Wave 190 clean-room verification")
            return 1
        print(f"PASS Wave 190 clean-room verification: {args.verify}")
        return 0
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
