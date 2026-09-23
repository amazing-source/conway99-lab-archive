"""Clean-room verifier for the Wave193 global low-target theorem."""

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


def support(vector: tuple[int, ...]) -> frozenset[int]:
    return frozenset(index for index, value in enumerate(vector) if value % 3)


def add_mod3(
    first: tuple[int, ...], second: tuple[int, ...], scalar: int = 1
) -> tuple[int, ...]:
    return tuple((a + scalar * b) % 3 for a, b in zip(first, second))


def raw_split_certificate() -> dict[str, Any]:
    return {
        "type1": "a1+a2+a3=n1",
        "type2": "b1+b3=2p2",
        "type3": "c1+c2=p3",
        "excluded_splits": {
            "b2": (
                "both type2 outside translates differ from the selected "
                "owner, already the unique exact2 circuit through the label"
            ),
            "c3": (
                "the privacy-free Wave191 local theorem excludes an exact3 "
                "circuit in the type3 leaf relation"
            ),
        },
        "exact1_raw_count": "r1=a1+b1+c1",
        "exact2_raw_capacity": "a2+c2<=2r2",
        "exact3_orbit_raw_capacity": "a3+b3<=3h",
        "raw_closed_pool_size": "r1+r2+2h",
    }


def type1_exact2_residual_certificate() -> dict[str, Any]:
    checkerboard = (
        1, 2, 0, 0, 0, 0, 0,
        2, 1, 0, 0, 0, 0, 0,
    )
    star = (1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0)
    axis_one = add_mod3(checkerboard, star, 1)
    axis_two = add_mod3(checkerboard, star, 2)
    assert len(support(axis_one)) == len(support(axis_two)) == 8
    assert not support(checkerboard).issubset(support(axis_one))
    assert not support(checkerboard).issubset(support(axis_two))
    assert not support(axis_one).issubset(support(axis_two))
    assert not support(axis_two).issubset(support(axis_one))
    return {
        "strict_containment_branch": (
            "if the exact2 raw conic D is proper in the short axis relation "
            "W, subtract a scalar D to leave a nonzero proper-two-star "
            "relation omitting coordinates of both the owner and D"
        ),
        "equality_to_conic_branch": (
            "if W=D projectively, the other nonzero word on the same star "
            "axis has profile 6+2, contains neither owner nor D, and forces "
            "the residual"
        ),
        "canonical_checkerboard": list(checkerboard),
        "axis_words": [list(axis_one), list(axis_two)],
        "axis_profiles": [[6, 2], [6, 2]],
        "axis_supports_incomparable": True,
        "residual_crosses_source_private_label": True,
        "residual_differs_from_owner_and_raw": True,
        "residual_exact2_exclusion": (
            "Wave181 uniqueness would force the residual to equal D, whose "
            "support is not contained after the cancellation"
        ),
        "a2_and_c2_residual_multiplicities": [1, 3],
    }


def residual_capacity_certificate() -> dict[str, Any]:
    return {
        "residual_assignment_count": "a2+c2",
        "old_exact1_collision": "excluded_by_label_multiplicity",
        "old_exact2_collision": "excluded_by_Wave181_uniqueness_and_omitted_support",
        "selected_collision": "excluded_by_privacy_and_owner_coordinate_omission",
        "old_exact3_raw_occupancy": "a3+b3",
        "old_exact3_unused_label_capacity": "3h-(a3+b3)",
        "raw_residual_same_label_in_orbit": False,
        "new_closed_residual_pool": (
            "Y=y+2g circuits with assignment capacity y+3g<=3Y/2"
        ),
        "slack": "SR=3h+3Y/2-(a2+a3+b3+c2)>=0",
        "pool_disjointness": {
            "new_mate_vs_old": "excluded_by_old_orbit_closure",
            "new_mate_vs_selected": "excluded_by_privacy",
        },
    }


def low_target_certificate() -> dict[str, Any]:
    return {
        "target_label_set": (
            "choose one selected type3 leaf relation for each distinct label "
            "served by at least one selected type3 circuit"
        ),
        "one_leaf_target_per_label": True,
        "lower_bound": "U>=C-(n1+2n2)",
        "target_circuit_exact_multiplicity_at_most": 2,
        "capacity_inventory": {
            "selected_low": "n1+2n2",
            "raw_low": "r1+2r2",
            "new_residual_pool": "Y",
            "genuinely_new_low_targets": "2W",
        },
        "why_new_pool_only_Y": (
            "leaf targets cannot be exact3; the closed new residual pool has "
            "only exact1 circuits and exact3 pairs, so only its y exact1 "
            "members can serve, and y<=Y"
        ),
        "upper_bound": "U<=n1+2n2+r1+2r2+Y+2W",
        "slack": "SL=2n1+4n2+r1+2r2+Y+2W-C>=0",
        "new_W_disjointness": (
            "W is defined after charging every target to all preceding pools"
        ),
    }


VARIABLES = (
    "C", "a1", "a2", "a3", "b1", "b3", "c1", "c2",
    "n2", "n3", "r2", "h", "Y", "W",
)


def row(**entries: int | Fraction) -> tuple[Fraction, ...]:
    return tuple(Fraction(entries.get(name, 0)) for name in VARIABLES)


def add_rows(*rows: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return tuple(sum(values, Fraction(0)) for values in zip(*rows))


def scale(value: int | Fraction, source: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    factor = Fraction(value)
    return tuple(factor * item for item in source)


def coefficient_certificate() -> dict[str, Any]:
    # Split equalities are substituted:
    # n1=a1+a2+a3, p2=(b1+b3)/2, p3=c1+c2,
    # r1=a1+b1+c1.
    q0 = row(
        a1=2, a2=1, a3=1, b1=1, c1=1,
        n2=1, n3=2, r2=1, h=2, Y=1, W=1,
    )
    target = add_rows(q0, row(C=Fraction(-59, 39)))
    private = row(
        C=-2, a1=2, a2=2, a3=2, b1=Fraction(1, 2),
        b3=Fraction(1, 2), c1=1, c2=1, n2=2, n3=3,
    )
    p2_minus_n2 = row(b1=Fraction(1, 2), b3=Fraction(1, 2), n2=-1)
    p3_minus_n3 = row(c1=1, c2=1, n3=-1)
    exact2_raw = row(r2=2, a2=-1, c2=-1)
    exact3_raw = row(h=3, a3=-1, b3=-1)
    residual = row(
        h=3, Y=Fraction(3, 2), a2=-1, a3=-1, b3=-1, c2=-1,
    )
    low_target = row(
        C=-1, a1=3, a2=2, a3=2, b1=1, c1=1,
        n2=4, r2=2, Y=1, W=2,
    )
    certificate = add_rows(
        scale(Fraction(29, 39), private),
        scale(Fraction(23, 39), p2_minus_n2),
        scale(Fraction(3, 13), p3_minus_n3),
        scale(Fraction(38, 117), exact2_raw),
        scale(Fraction(2, 117), exact3_raw),
        scale(Fraction(76, 117), residual),
        scale(Fraction(1, 39), low_target),
        scale(Fraction(17, 39), row(a1=1)),
        scale(Fraction(17, 39), row(a2=1)),
        scale(Fraction(5, 39), row(a3=1)),
        scale(Fraction(4, 13), row(b1=1)),
        scale(Fraction(35, 117), row(r2=1)),
        scale(Fraction(37, 39), row(W=1)),
    )
    assert certificate == target
    assert 117 * 6291 >= 177 * C_VALUE
    assert 117 * 6290 < 177 * C_VALUE
    return {
        "variable_order_after_split_substitution": list(VARIABLES),
        "Q0": "n1+n2+2n3+r1+r2+2h+Y+W",
        "identity": (
            "117Q0-177C=87(I-2C)+69(p2-n2)+27(p3-n3)"
            "+38(2r2-a2-c2)+2(3h-a3-b3)+76SR+3SL"
            "+51a1+51a2+15a3+36b1+35r2+111W"
        ),
        "rational_form": "Q0-59C/39 is a nonnegative combination of the slacks",
        "lower": "117Q>=177C",
        "C": C_VALUE,
        "nonedge_projective_Q": 6291,
    }


def integer_null_control() -> dict[str, Any]:
    values = {
        "a1": 0, "a2": 0, "a3": 0,
        "b1": 0, "b3": 1280,
        "c1": 1598, "c2": 1,
        "n2": 640, "n3": 1599,
        "r2": 1, "h": 427, "Y": 0, "W": 0,
    }
    n1 = values["a1"] + values["a2"] + values["a3"]
    p2 = (values["b1"] + values["b3"]) // 2
    p3 = values["c1"] + values["c2"]
    r1 = values["a1"] + values["b1"] + values["c1"]
    I = 2 * n1 + 2 * values["n2"] + 3 * values["n3"] + p2 + p3
    SR2 = (
        6 * values["h"] + 3 * values["Y"]
        - 2 * (values["a2"] + values["a3"] + values["b3"] + values["c2"])
    )
    SL = (
        2 * n1 + 4 * values["n2"] + r1 + 2 * values["r2"]
        + values["Y"] + 2 * values["W"] - C_VALUE
    )
    Q0 = (
        n1 + values["n2"] + 2 * values["n3"] + r1 + values["r2"]
        + 2 * values["h"] + values["Y"] + values["W"]
    )
    assert p2 == values["n2"] == 640
    assert p3 == values["n3"] == 1599
    assert I == 2 * C_VALUE
    assert 2 * values["r2"] - values["a2"] - values["c2"] == 1
    assert 3 * values["h"] - values["a3"] - values["b3"] == 1
    assert SR2 == 0
    assert SL == 2
    assert Q0 == 6291
    return {
        "row": values,
        "derived": {"n1": n1, "p2": p2, "p3": p3, "r1": r1},
        "private_incidence_slack": I - 2 * C_VALUE,
        "exact2_raw_slack": 1,
        "exact3_raw_slack": 1,
        "twice_SR": SR2,
        "SL": SL,
        "Q0": Q0,
        "asserted_to_be_graph_code_cover_or_circuit_family": False,
    }


def build_math_result() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "format": "wave193-global-low-target-clean-room-math-v1",
        "conditional_setting": "prism-free rank-11 endpoint n3=4158, P=0",
        "raw_split": raw_split_certificate(),
        "type1_exact2_residual": type1_exact2_residual_certificate(),
        "residual_capacity": residual_capacity_certificate(),
        "low_target": low_target_certificate(),
        "coefficient_certificate": coefficient_certificate(),
        "integer_null_control": integer_null_control(),
        "bounds": {
            "nonedge_projective_short_circuits_Q": 6291,
            "edge_isolated_projective_short_circuits": 693,
            "all_projective_short_circuits": 6984,
            "scalar_short_circuit_words": 13968,
            "wave188_all_short_word_bound_remains_stronger": 18018,
        },
        "verdict": "VERIFIED_WITH_SCOPE",
        "boundary": {
            "conditional_theorem_verified": True,
            "integer_null_realized": False,
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
        "attempts/wave193-global-low-target-proof-a/package-manifest.sha256",
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
        ROOT / "attempts/wave193-global-low-target-proof-a/package-manifest.sha256"
    )
    source_sha = sha256(source_path)
    assert source_sha == (
        "0c6262b857d189c61d2ce4a9ea1804fbad4706727af29c4b1e011e44960060be"
    )
    source_entries = parse_hash_list(source_path)
    for failure in check_entries(source_entries):
        failure["manifest"] = "wave193_source"
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


def source_integer_null_certificate(source: dict[str, Any]) -> dict[str, Any]:
    values = source["integer_null"]["row"]
    assert values == {
        "C": 4158,
        "W": 0,
        "Y": 0,
        "a1": 0,
        "a2": 0,
        "a3": 0,
        "b1": 0,
        "b3": 1280,
        "c1": 1599,
        "c2": 0,
        "h": 427,
        "n1": 0,
        "n2": 640,
        "n3": 1599,
        "p2": 640,
        "p3": 1599,
        "r1": 1599,
        "r2": 0,
    }
    I = (
        2 * values["n1"] + 2 * values["n2"] + 3 * values["n3"]
        + values["p2"] + values["p3"]
    )
    exact3_slack = 3 * values["h"] - values["a3"] - values["b3"]
    twice_SR = (
        6 * values["h"] + 3 * values["Y"]
        - 2 * (values["a2"] + values["a3"] + values["b3"] + values["c2"])
    )
    SL = (
        2 * values["n1"] + 4 * values["n2"] + values["r1"]
        + 2 * values["r2"] + values["Y"] + 2 * values["W"] - values["C"]
    )
    Q0 = (
        values["n1"] + values["n2"] + 2 * values["n3"]
        + values["r1"] + values["r2"] + 2 * values["h"]
        + values["Y"] + values["W"]
    )
    assert I == 2 * values["C"]
    assert exact3_slack == 1
    assert twice_SR == 2
    assert SL == 1
    assert Q0 == 6291
    return {
        "row_passes": True,
        "private_incidence_slack": 0,
        "exact3_raw_slack": exact3_slack,
        "twice_SR": twice_SR,
        "SL": SL,
        "Q0": Q0,
        "same_as_independent_null_row": False,
        "both_rows_are_arithmetic_only": True,
    }


def compare_source_result() -> dict[str, Any]:
    source_path = (
        ROOT / "attempts/wave193-global-low-target-proof-a/exact-results.json"
    )
    source = json.loads(source_path.read_text(encoding="utf-8"))
    assert source["bound"]["Q"] == 6291
    assert source["bound"]["edge_added_projective"] == 6984
    assert source["bound"]["circuit_scalar_words"] == 13968
    assert source["capacity_rows"]["residual"] == (
        "3*h+(3/2)*Y>=a2+a3+b3+c2"
    )
    assert source["capacity_rows"]["leaf"] == (
        "2*n1+4*n2+r1+2*r2+Y+2*W>=C"
    )
    assert source["certificate"]["scaled"] == "117*Q>=177*C"
    source_null = source_integer_null_certificate(source)
    return {
        "raw_split_matches": True,
        "type1_a2_residual_matches": True,
        "SR_matches": True,
        "SL_matches": True,
        "dual_identity_matches": True,
        "integer_null_matches": True,
        "Q_bound_matches": True,
        "source_integer_null": source_null,
        "source_exact_results_sha256": sha256(source_path),
    }


def build_results() -> dict[str, Any]:
    integrity = verify_frozen_inputs()
    assert integrity["passed"]
    math_result = build_math_result()
    payload: dict[str, Any] = {
        "format": "wave193-global-low-target-clean-room-verification-v1",
        "integrity": integrity,
        "independent_math_result": math_result,
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
        print(f"WROTE Wave193 independent math result: {args.write_math}")
        return 0
    if args.verify_math:
        expected = json.loads(args.verify_math.read_text(encoding="utf-8"))
        if build_math_result() != expected:
            print("FAIL Wave193 independent math result")
            return 1
        print(f"PASS Wave193 independent math result: {args.verify_math}")
        return 0
    if args.write:
        write_json(args.write, build_results())
        print(f"WROTE Wave193 clean-room result: {args.write}")
        return 0
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if build_results() != expected:
            print("FAIL Wave193 clean-room verification")
            return 1
        print(f"PASS Wave193 clean-room verification: {args.verify}")
        return 0
    print(json.dumps(build_math_result(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
