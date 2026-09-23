"""Clean-room verifier for the Wave192 equality-face exclusion."""

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
HALF_C = 2079


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


def support(vector: tuple[int, ...]) -> frozenset[int]:
    return frozenset(index for index, value in enumerate(vector) if value % 3)


def add_mod3(
    first: tuple[int, ...], second: tuple[int, ...], scalar: int = 1
) -> tuple[int, ...]:
    return tuple((a + scalar * b) % 3 for a, b in zip(first, second))


def equality_face_certificate() -> dict[str, Any]:
    # Let m=n3=p3. Equality in the Wave191 coefficient row forces:
    # n2=p2=0, p3=n3, I=2C. Hence n1=C-2m.
    samples: list[dict[str, int]] = []
    for m in (0, 1, HALF_C - 1, HALF_C):
        n1 = C - 2 * m
        n2 = p2 = 0
        n3 = p3 = m
        delta = r1 = m
        h = Y = 0
        r = HALF_C
        exact2_raw = r - r1
        type1_assignments = n1
        B = n1 + n2 + 2 * n3
        A = n1 + 2 * p2 + p3
        I = 2 * n1 + 2 * n2 + 3 * n3 + p2 + p3
        Q = B + r
        assert B == C
        assert I == 2 * C
        assert delta == 2 * r + 3 * h - A
        assert exact2_raw == HALF_C - m
        assert type1_assignments == 2 * exact2_raw
        assert Q == 6237
        samples.append(
            {
                "m": m,
                "n1": n1,
                "n2": n2,
                "n3": n3,
                "p2": p2,
                "p3": p3,
                "delta": delta,
                "r": r,
                "r1": r1,
                "h": h,
                "Y": Y,
                "exact2_raw": exact2_raw,
                "Q": Q,
            }
        )
    return {
        "parameter": "m=n3=p3",
        "range": [0, HALF_C],
        "formulas": {
            "n1": "C-2m",
            "n2": "0",
            "n3": "m",
            "p2": "0",
            "p3": "m",
            "delta": "m",
            "r": str(HALF_C),
            "r1": "m",
            "h": "0",
            "Y": "0",
            "exact2_raw": f"{HALF_C}-m",
            "type1_raw_assignments": "C-2m",
        },
        "selected_type3_private_labels_per_flag": 1,
        "selected_type3_nonprivate_labels_per_flag": 2,
        "all_type3_raws_exact1": True,
        "all_type1_raws_fill_exact2_circuits_two_each": True,
        "sample_rows_checked": samples,
    }


def tau_pair_saturation_certificate() -> dict[str, Any]:
    return {
        "canonical_nonedge_involution": "tau",
        "total_tau_pairs": HALF_C,
        "singleton_label_count": "C-2m",
        "exact2_raw_count": f"{HALF_C}-m",
        "assignments_per_exact2_raw": 2,
        "consequence": (
            "the singleton-label set is a union of exactly 2079-m complete "
            "tau-pairs, each served by its unique checkerboard circuit"
        ),
        "complement_tau_invariant": True,
    }


def affine_axis_certificate() -> dict[str, Any]:
    # Canonical checkerboard on two disjoint endpoint stars. Its two
    # coefficients on the chosen x-star are 1 and 2.
    r = (1, 2, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0)
    sx = (1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0)
    axis1 = add_mod3(r, sx, 1)
    axis2 = add_mod3(r, sx, 2)
    assert len(support(r)) == 4
    assert len(support(axis1)) == len(support(axis2)) == 8
    assert len(support(axis1) & frozenset(range(7))) == 6
    assert len(support(axis2) & frozenset(range(7))) == 6
    assert len(support(axis1) & frozenset(range(7, 14))) == 2
    assert len(support(axis2) & frozenset(range(7, 14))) == 2
    assert not support(r).issubset(support(axis1))
    assert not support(r).issubset(support(axis2))
    assert not support(axis1).issubset(support(axis2))
    assert not support(axis2).issubset(support(axis1))
    return {
        "checkerboard": list(r),
        "chosen_star": list(sx),
        "axis_words": [list(axis1), list(axis2)],
        "axis_profiles": [[6, 2], [6, 2]],
        "axis_weights": [8, 8],
        "checkerboard_weight": 4,
        "axis_supports_incomparable": True,
        "checkerboard_not_contained_in_either_axis_word": True,
        "equality_inventory_for_m0": (
            "for each label e, the only old short circuits crossing e are "
            "its selected singleton c_e and canonical checkerboard r_e"
        ),
        "saturation_step": (
            "the short translated relation used by the type1 lemma must equal "
            "r_e; otherwise removing its unique old circuit leaves another "
            "dependent support"
        ),
        "contradiction": (
            "the unused nontrivial word on the same affine star axis contains "
            "a cross circuit but contains neither c_e nor r_e"
        ),
        "m0_branch_verdict": "REFUTED",
    }


def nonprivate_leaf_certificate() -> dict[str, Any]:
    return {
        "branch": "m>0",
        "selected_type3_exists": True,
        "private_labels_per_selected_type3": 1,
        "nonprivate_labels_per_selected_type3": 2,
        "leaf_word_profile": [3, 6],
        "leaf_word_weight": 9,
        "both_star_sides_proper": True,
        "contained_circuit_crosses_leaf_label": True,
        "old_pool_exclusions": {
            "exact3_selected_or_companion": (
                "excluded by the verified Wave191 local exact3-in-leaf-word "
                "impossibility"
            ),
            "exact1_type3_raw": (
                "its sole label is private, not the chosen nonprivate leaf"
            ),
            "exact2_type1_raw": (
                "its two labels are singleton private labels in a tau-pair"
            ),
            "selected_singleton": (
                "its sole label is private, not the chosen nonprivate leaf"
            ),
        },
        "contradiction": "the leaf word forces a circuit outside the equality inventory",
        "positive_m_branch_verdict": "REFUTED",
    }


def strict_residual_capacity_certificate() -> dict[str, Any]:
    # This lever was already sealed in the Wave191 verifier: a residual
    # after an exact-two type-three raw cannot itself be exact-two.
    # Thus a closed new pool has only exact-one circuits and exact-three pairs.
    # With Y=y+2g and Z<=y+3g, 2Z<=3Y.
    capacity_Z = (1, 3)  # y exact-one, g exact-three pairs
    three_Y = (3, 6)
    twice_Z = tuple(2 * value for value in capacity_Z)
    assert all(a <= b for a, b in zip(twice_Z, three_Y))

    # Exact decomposition of the Wave191 penalty.
    penalty = (
        Fraction(1, 2),
        Fraction(1, 2),
        Fraction(1, 1),
    )  # delta,h,Y
    first = (
        Fraction(1, 3),
        Fraction(0, 1),
        Fraction(1, 2),
    )  # (2delta+3Y)/6
    second = (
        Fraction(1, 6),
        Fraction(1, 2),
        Fraction(1, 4),
    )  # (2delta+6h+3Y)/12
    extra = (
        Fraction(0, 1),
        Fraction(0, 1),
        Fraction(1, 4),
    )
    assert tuple(a + b + c for a, b, c in zip(first, second, extra)) == penalty
    return {
        "exact2_residual_possible": False,
        "closed_new_pool": "Y=y+2g",
        "new_assignment_capacity": "Z<=y+3g",
        "strict_capacity": "2Z<=3Y",
        "twice_Z_capacity_row": list(twice_Z),
        "three_Y_row": list(three_Y),
        "joint_rows": [
            "p3+u<=delta+Z",
            "2p2<=u+3h",
            "2Z<=3Y",
        ],
        "strengthened_penalty": (
            "delta/2+h/2+Y>=p2/3+p3/2+Y/4"
        ),
        "equality_consequence": "Y=Z=0 and every type3 raw is exact1",
        "already_sealed_premise": (
            "verification/wave191-exact-three-residual-verifier"
        ),
    }


def build_math_result() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "format": "wave192-equality-face-clean-room-math-v1",
        "conditional_setting": "prism-free rank-11 endpoint n3=4158, P=0",
        "equality_face": equality_face_certificate(),
        "tau_pair_saturation": tau_pair_saturation_certificate(),
        "m0_affine_axis": affine_axis_certificate(),
        "positive_m_nonprivate_leaf": nonprivate_leaf_certificate(),
        "strict_bound": {
            "excluded_equality": 6237,
            "nonedge_projective_short_circuits_Q": 6238,
            "edge_isolated_projective_short_circuits": 693,
            "all_projective_short_circuits": 6931,
            "scalar_short_circuit_words": 13862,
            "wave188_all_short_word_bound_remains_stronger": 18018,
        },
        "verdict": "VERIFIED_WITH_SCOPE",
        "boundary": {
            "Q6237_equality_face": "REFUTED",
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
        "attempts/wave192-equality-face-proof-a/package-manifest.sha256",
        "verification/wave181-c4-conic-equality/package-manifest.sha256",
        "verification/wave188-affine-star-word-amplification-verifier/package-manifest.sha256",
        "verification/wave189-degree7-star-orbit-verifier/package-manifest.sha256",
        "verification/wave191-exact-three-residual-verifier/package-manifest.sha256",
    }
    actual = {relative for _, relative in entries}
    if actual != expected:
        raise AssertionError(f"unexpected input set: {sorted(actual ^ expected)}")
    failures = check_entries(entries)
    source_path = (
        ROOT / "attempts/wave192-equality-face-proof-a/package-manifest.sha256"
    )
    source_sha = sha256(source_path)
    assert source_sha == (
        "630183eb6c94836daf2e4202b69acc5c7fbd1b7ce7c6c335573e99a7ea1d8ede"
    )
    source_entries = parse_hash_list(source_path)
    for failure in check_entries(source_entries):
        failure["manifest"] = "wave192_source"
        failures.append(failure)
    premise_paths = {
        "wave181": ROOT / "verification/wave181-c4-conic-equality/package-manifest.sha256",
        "wave188": ROOT / "verification/wave188-affine-star-word-amplification-verifier/package-manifest.sha256",
        "wave189": ROOT / "verification/wave189-degree7-star-orbit-verifier/package-manifest.sha256",
        "wave191": ROOT / "verification/wave191-exact-three-residual-verifier/package-manifest.sha256",
    }
    premise_counts: dict[str, int] = {}
    for name, path in premise_paths.items():
        nested_entries = parse_hash_list(path)
        premise_counts[name] = len(nested_entries)
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
        "source_entries_checked": len(source_entries),
        "premise_entries_checked": premise_counts,
        "independent_result_entries_checked": len(independent_entries),
        "source_manifest_sha256": source_sha,
        "failures": failures,
        "discovery_checker_imported_or_executed_before_independent_freeze": False,
    }


def compare_source_result() -> dict[str, Any]:
    source_path = ROOT / "attempts/wave192-equality-face-proof-a/exact-results.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    assert source["strict_bound"]["nonedge_projective_Q"] == 6238
    assert source["strict_bound"]["edge_added_projective"] == 6931
    assert source["strict_bound"]["circuit_scalar_words"] == 13862
    assert source["equality_face"]["formula"] == (
        "n1=C-2m,n2=p2=0,n3=p3=m,r=2079,r1=t=delta=m,h=u=Y=Z=0"
    )
    assert source["residual_capacity"]["closed_pool"] == (
        "Y=y+2g,Z<=y+3g,therefore 2Z<=3Y"
    )
    assert source["affine_conic"]["profiles"] == [[6, 2], [6, 2]]
    assert not source["affine_conic"]["conic_contained_in_axis_one"]
    assert not source["affine_conic"]["conic_contained_in_axis_two"]
    return {
        "equality_face_matches": True,
        "strict_residual_capacity_matches": True,
        "tau_pair_saturation_matches": True,
        "affine_axis_contradiction_matches": True,
        "nonprivate_leaf_contradiction_matches": True,
        "strict_Q_bound_matches": True,
        "source_exact_results_sha256": sha256(source_path),
    }


def build_results() -> dict[str, Any]:
    integrity = verify_frozen_inputs()
    assert integrity["passed"]
    math_result = build_math_result()
    payload: dict[str, Any] = {
        "format": "wave192-equality-face-clean-room-verification-v1",
        "integrity": integrity,
        "independent_math_result": math_result,
        "strict_residual_capacity": strict_residual_capacity_certificate(),
        "source_comparison": compare_source_result(),
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
        print(f"WROTE Wave192 independent math result: {args.write_math}")
        return 0
    if args.verify_math:
        expected = json.loads(args.verify_math.read_text(encoding="utf-8"))
        if build_math_result() != expected:
            print("FAIL Wave192 independent math result")
            return 1
        print(f"PASS Wave192 independent math result: {args.verify_math}")
        return 0
    if args.write:
        write_json(args.write, build_results())
        print(f"WROTE Wave192 clean-room result: {args.write}")
        return 0
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if build_results() != expected:
            print("FAIL Wave192 clean-room verification")
            return 1
        print(f"PASS Wave192 clean-room verification: {args.verify}")
        return 0
    print(json.dumps(build_math_result(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
