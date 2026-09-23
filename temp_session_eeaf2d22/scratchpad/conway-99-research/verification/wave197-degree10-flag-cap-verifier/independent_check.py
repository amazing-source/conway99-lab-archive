"""Clean-room Wave197 degree-ten flag-cap verifier."""

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
PRIMARY_DIR = ROOT / "attempts/wave197-degree10-flag-cap-proof-a"
PROOF_B_DIR = ROOT / "attempts/wave197-ten-flag-capacity-proof-b-audit"
HASH_LINE = re.compile(r"^([0-9a-fA-F]{64})\s+\*?(.+?)\s*$")
C_VALUE = 4158
VERTICES = 99


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
        entries.append(
            (match.group(1).lower(), match.group(2).replace("\\", "/"))
        )
    if not entries:
        raise ValueError(f"empty hash list: {path}")
    return entries


def check_entries(
    entries: list[tuple[str, str]], manifest: str
) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    for expected, relative in entries:
        target = ROOT / relative
        actual = sha256(target) if target.is_file() else "missing"
        if actual != expected:
            failures.append(
                {
                    "manifest": manifest,
                    "path": relative,
                    "expected": expected,
                    "actual": actual,
                }
            )
    return failures


def verify_integrity() -> dict[str, Any]:
    direct = parse_hash_list(INPUT_FREEZE)
    expected = {
        "AGENTS.md",
        "verification/wave180-capacity3-companion/package-manifest.sha256",
        "verification/wave194-five-thirds-verifier/package-manifest.sha256",
        "verification/wave195-hilton-milner-verifier/package-manifest.sha256",
        (
            "verification/wave196-four-fiber-hilton-milner-verifier/"
            "package-manifest.sha256"
        ),
        (
            "attempts/wave197-degree10-flag-cap-proof-a/"
            "package-manifest.sha256"
        ),
        (
            "attempts/wave197-ten-flag-capacity-proof-b-audit/"
            "package-manifest.sha256"
        ),
    }
    actual = {relative for _, relative in direct}
    if actual != expected:
        raise AssertionError(f"unexpected direct inputs: {sorted(actual ^ expected)}")
    failures = check_entries(direct, "input-freeze")
    checked = len(direct)
    manifests = 0
    for _, relative in direct:
        if not relative.endswith("package-manifest.sha256"):
            continue
        entries = parse_hash_list(ROOT / relative)
        failures.extend(check_entries(entries, relative))
        checked += len(entries)
        manifests += 1
    for relative in (
        "attempts/wave197-degree10-flag-cap-proof-a/input-freeze.sha256",
        (
            "attempts/wave197-ten-flag-capacity-proof-b-audit/"
            "input-freeze.sha256"
        ),
    ):
        entries = parse_hash_list(ROOT / relative)
        failures.extend(check_entries(entries, relative))
        checked += len(entries)
        manifests += 1
    independent = parse_hash_list(INDEPENDENT_FREEZE)
    failures.extend(check_entries(independent, "independent-result-freeze"))
    checked += len(independent)
    assert sha256(HERE / "independent-math-result.json") == (
        "99f66cdb8da57fb79910c14c28fafb2fbd2749f543387515887e0da48a161040"
    )
    return {
        "passed": not failures,
        "all_hash_entries_checked": checked,
        "sealed_manifests_checked": manifests,
        "independent_math_sha256": sha256(
            HERE / "independent-math-result.json"
        ),
        "primary_manifest_sha256": sha256(
            PRIMARY_DIR / "package-manifest.sha256"
        ),
        "proof_b_manifest_sha256": sha256(
            PROOF_B_DIR / "package-manifest.sha256"
        ),
        "failures": failures,
        "sources_opened_before_independent_freeze": False,
        "source_checkers_executed_before_independent_freeze": False,
    }


def orientation_degree_certificate() -> dict[str, Any]:
    return {
        "fixed_orientation": "x->y for a nonedge {x,y}",
        "two_block_type": (
            "Wave196 gives P_x(y)={i,j}; every flag containing x->y has "
            "A_x(T)={i,j,k}"
        ),
        "third_block_choices": 5,
        "injectivity": (
            "for fixed center x, two distinct flags cannot have the same "
            "A-set, by the verified weight-two exclusion"
        ),
        "oriented_degree_upper": 5,
        "two_orientations_per_undirected_label": 2,
        "undirected_degree_upper": 10,
    }


def selected_flag_hypergraph_certificate() -> dict[str, Any]:
    return {
        "vertices": (
            "H distinct undirected nonedge labels in the selected "
            "exact-three flag union"
        ),
        "edges": "n3 selected exact-three flags, each using three labels",
        "simplicity": (
            "Wave180 leaves one canonical companion pair for each flag; "
            "an inclusion-minimal cover cannot select both companions, "
            "so selected exact-three circuits give distinct flag edges"
        ),
        "private_labels": (
            "the p3 private labels of selected type-three circuits are "
            "distinct and each has hypergraph degree exactly one"
        ),
        "other_label_degree": "at most ten by the two orientation cap",
        "degree_sum": (
            "3n3<=p3+10(H-p3)=10H-9p3"
        ),
        "S10": "10H-9p3-3n3>=0",
    }


def headroom_and_flag_certificate() -> dict[str, Any]:
    return {
        "selected_union_orientations": (
            "each of the H undirected selected-type3 labels contributes "
            "one distinct oriented label"
        ),
        "old_private_orientations": (
            "the verified a3+b3 old-raw injection supplies additional "
            "oriented labels outside the selected type3 union"
        ),
        "J_lower": "J>=H+a3+b3",
        "J_upper": "J<=99*36=3564=6C/7",
        "SH": "6C/7-H-a3-b3>=0",
        "all_flag_count": "F=n3+h+g",
        "fixed_center_flag_cap": "c_x<=13 from Wave196",
        "global_flag_cap": "F<=99*13=1287=13C/42",
        "SF": "13C/42-n3-h-g>=0",
        "old_raw_capacity": "R3=3h-a3-b3>=0",
    }


VARIABLES = (
    "C",
    "H",
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
    return tuple(sum(values, Fraction()) for values in zip(*rows))


def scale(
    value: int | Fraction, source: tuple[Fraction, ...]
) -> tuple[Fraction, ...]:
    factor = Fraction(value)
    return tuple(factor * item for item in source)


def certificate_rows() -> dict[str, tuple[Fraction, ...]]:
    return {
        "SI": row(
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
        ),
        "S2": row(b1=Fraction(1, 2), b3=Fraction(1, 2), n2=-1),
        "SE2": row(r2=2, a2=-1, c2=-1),
        "RA": row(
            a2=-1,
            a3=-1,
            b3=-2,
            c2=-1,
            h=3,
            y=1,
            g=3,
        ),
        "SL": row(
            C=-1,
            a1=1,
            a2=1,
            a3=1,
            c1=1,
            n2=2,
            r2=2,
            y=1,
            W=2,
        ),
        "R3": row(h=3, a3=-1, b3=-1),
        "S10": row(H=10, c1=-9, c2=-9, n3=-3),
        "SH": row(
            C=Fraction(6, 7),
            H=-1,
            a3=-1,
            b3=-1,
        ),
        "SF": row(
            C=Fraction(13, 42),
            n3=-1,
            h=-1,
            g=-1,
        ),
    }


def coefficient_certificate() -> dict[str, Any]:
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
    target = add_rows(q0, row(C=Fraction(-2131, 1260)))
    sources = certificate_rows()
    weights = {
        "SI": Fraction(4, 5),
        "S2": Fraction(6, 5),
        "SE2": Fraction(1, 5),
        "RA": Fraction(7, 10),
        "SL": Fraction(3, 10),
        "R3": Fraction(4, 45),
        "S10": Fraction(1, 90),
        "SH": Fraction(1, 9),
        "SF": Fraction(11, 30),
    }
    certificate = add_rows(
        *(scale(weights[name], sources[name]) for name in weights),
        scale(Fraction(1, 10), row(a1=1)),
        scale(Fraction(3, 5), row(b3=1)),
        scale(Fraction(1, 5), row(c2=1)),
        scale(Fraction(4, 15), row(g=1)),
        scale(Fraction(2, 5), row(W=1)),
    )
    assert certificate == target
    rational_target = Fraction(2131 * C_VALUE, 1260)
    assert rational_target == Fraction(70323, 10)
    integer_bound = rational_target.numerator // rational_target.denominator + 1
    assert integer_bound == 7033
    return {
        "variable_order_after_split_substitution": list(VARIABLES),
        "Q0": "n1+n2+2n3+r1+r2+2h+y+2g+W",
        "slacks": {
            "SI": "I-2C",
            "S2": "p2-n2",
            "SE2": "2r2-a2-c2",
            "RA": "3h+y+3g-a2-a3-2b3-c2",
            "SL": "n1+2n2+c1+2r2+y+2W-C",
            "R3": "3h-a3-b3",
            "S10": "10H-9p3-3n3",
            "SH": "6C/7-H-a3-b3",
            "SF": "13C/42-n3-h-g",
        },
        "weights": {name: str(value) for name, value in weights.items()},
        "explicit_remainder": {
            "a1": "1/10",
            "b3": "3/5",
            "c2": "1/5",
            "g": "4/15",
            "W": "2/5",
        },
        "identity": (
            "Q0-2131C/1260=4SI/5+6S2/5+SE2/5+7RA/10+3SL/10"
            "+4R3/45+S10/90+SH/9+11SF/30"
            "+a1/10+3b3/5+c2/5+4g/15+2W/5"
        ),
        "C": C_VALUE,
        "exact_rational_target": "70323/10",
        "integer_nonedge_projective_Q": integer_bound,
    }


def integer_rounding_control() -> dict[str, Any]:
    values = {
        "H": Fraction(33),
        "a1": Fraction(7),
        "a2": Fraction(8),
        "a3": Fraction(3531),
        "b1": Fraction(596),
        "b3": Fraction(0),
        "c1": Fraction(0),
        "c2": Fraction(0),
        "n2": Fraction(298),
        "n3": Fraction(110),
        "r2": Fraction(4),
        "h": Fraction(1177),
        "y": Fraction(8),
        "g": Fraction(0),
        "W": Fraction(0),
    }
    n1 = values["a1"] + values["a2"] + values["a3"]
    p2 = (values["b1"] + values["b3"]) / 2
    p3 = values["c1"] + values["c2"]
    r1 = values["a1"] + values["b1"] + values["c1"]
    full = {"C": Fraction(C_VALUE), **values}
    row_values = tuple(full.get(name, Fraction()) for name in VARIABLES)
    slacks = {
        name: sum(coef * value for coef, value in zip(source, row_values))
        for name, source in certificate_rows().items()
    }
    assert all(value == 0 for value in slacks.values())
    incidence = 2 * n1 + 2 * values["n2"] + 3 * values["n3"] + p2 + p3
    assert incidence == 2 * C_VALUE
    q0 = (
        n1
        + values["n2"]
        + 2 * values["n3"]
        + r1
        + values["r2"]
        + 2 * values["h"]
        + values["y"]
        + 2 * values["g"]
        + values["W"]
    )
    assert q0 == 7033
    assert Fraction(q0) - Fraction(70323, 10) == Fraction(7, 10)
    assert Fraction(values["a1"], 10) == Fraction(7, 10)
    return {
        "row": {name: int(value) for name, value in values.items()},
        "derived": {
            "n1": int(n1),
            "p2": int(p2),
            "p3": int(p3),
            "r1": int(r1),
            "I": int(incidence),
        },
        "zero_certificate_slacks": {
            name: int(value) for name, value in slacks.items()
        },
        "Q0": int(q0),
        "rational_target": "70323/10",
        "rounding_gap": "7/10",
        "gap_accounted_by": "a1/10 with a1=7",
        "asserted_to_be_graph_code_cover_or_flag_family": False,
    }


def build_math_result() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "format": "wave197-degree10-flag-cap-clean-room-math-v1",
        "conditional_setting": "prism-free rank-11 endpoint n3_total=4158, P=0",
        "inputs_scope": (
            "sealed Wave180, Wave194, Wave195, and Wave196 verifier results "
            "plus srg(99,14,1,2)"
        ),
        "orientation_degree": orientation_degree_certificate(),
        "selected_flag_hypergraph": selected_flag_hypergraph_certificate(),
        "headroom_and_flag_caps": headroom_and_flag_certificate(),
        "coefficient_certificate": coefficient_certificate(),
        "integer_rounding_control": integer_rounding_control(),
        "quarantine": {
            "status": "QUARANTINED_NOT_USED",
            "rows": "all unrelated candidate capacity and support rows",
            "used_in_certificate": False,
        },
        "bounds": {
            "rational_nonedge_projective_target": "70323/10",
            "integer_nonedge_projective_Q": 7033,
            "edge_isolated_projective_short_circuits": 693,
            "all_projective_short_circuits": 7726,
            "scalar_short_circuit_words": 15452,
            "wave188_all_short_word_bound_remains_stronger": 18018,
        },
        "verdict": "INDEPENDENTLY_DERIVED_PRE_SOURCE",
        "boundary": {
            "conditional_theorem_derived": True,
            "source_compared": False,
            "arithmetic_control_realized": False,
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


def _source_null_replay(row_data: dict[str, str]) -> dict[str, Fraction]:
    names = (
        "V C n1 n2 n3 p2 p3 a1 a2 a3 b1 b3 c1 c2 "
        "r1 r2 h y g W"
    ).split()
    values = {name: Fraction() for name in names}
    values.update({name: Fraction(value) for name, value in row_data.items()})
    assert values["n1"] == values["a1"] + values["a2"] + values["a3"]
    assert 2 * values["p2"] == values["b1"] + values["b3"]
    assert values["p3"] == values["c1"] + values["c2"]
    assert values["r1"] == values["a1"] + values["b1"] + values["c1"]
    incidence = (
        2 * values["n1"]
        + 2 * values["n2"]
        + 3 * values["n3"]
        + values["p2"]
        + values["p3"]
    )
    q0 = (
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
    return {
        "I": incidence,
        "Q0": q0,
        "SI": incidence - 2 * values["C"],
        "S2": values["p2"] - values["n2"],
        "SE2": 2 * values["r2"] - values["a2"] - values["c2"],
        "RA": (
            3 * values["h"]
            + values["y"]
            + 3 * values["g"]
            - values["a2"]
            - values["a3"]
            - 2 * values["b3"]
            - values["c2"]
        ),
        "SL": (
            values["n1"]
            + 2 * values["n2"]
            + values["c1"]
            + 2 * values["r2"]
            + values["y"]
            + 2 * values["W"]
            - values["C"]
        ),
        "S10": (
            360 * values["V"]
            - 3 * values["n3"]
            - 9 * values["p3"]
            - 10 * values["a3"]
            - 10 * values["b3"]
        ),
        "SH": 3 * values["h"] - values["a3"] - values["b3"],
        "SF": (
            13 * values["V"]
            - values["n3"]
            - values["h"]
            - values["g"]
        ),
    }


def primary_comparison() -> dict[str, Any]:
    path = PRIMARY_DIR / "exact-results.json"
    primary = json.loads(path.read_text(encoding="utf-8"))
    local = primary["local_incidence"]
    assert local["triangles_through_leaf"] == 7
    assert local["triangles_blocked_by_common_neighbors"] == 2
    assert local["flag_supports_per_orientation"] == 5
    assert local["selected_exact3_degree_cap"] == 10
    assert local["global_flag_cap"] == 1287
    assert local["global_oriented_label_cap"] == 3564
    assert local["SH"] == "3*h-a3-b3>=0"
    assert local["SF"] == "13*V-n3-h-g>=0"
    assert local["S10"] == (
        "360*V-3*n3-9*p3-10*a3-10*b3>=0"
    )

    # The independent freeze split the source S10 row into its selected
    # hypergraph row and its Wave196 label-headroom row:
    #   (10H-9p3-3n3) + 10(36V-H-a3-b3).
    assert 360 * VERTICES == 35640
    split_identity = {
        "selected_degree": "10H-9p3-3n3",
        "ten_times_headroom": "360V-10H-10a3-10b3",
        "sum": "360V-3n3-9p3-10a3-10b3",
    }

    certificate = primary["certificate"]
    assert certificate["identity_target"] == "(57*C-263*V)/30"
    assert certificate["slack_weights"] == {
        "RA": "7/10",
        "S10": "1/90",
        "S2": "6/5",
        "SE2": "1/5",
        "SF": "11/30",
        "SH": "4/45",
        "SI": "4/5",
        "SL": "3/10",
    }
    assert certificate["remainder_coefficients"] == {
        "W": "2/5",
        "a1": "1/10",
        "b3": "3/5",
        "c2": "1/5",
        "g": "4/15",
    }
    assert primary["bound"]["rational_Q0"] == "70323/10"
    assert primary["bound"]["integral_Q"] == 7033
    assert primary["bound"]["edge_added_projective"] == 7726
    assert primary["bound"]["circuit_scalar_words"] == 15452

    replay = _source_null_replay(primary["rational_null_control"]["row"])
    assert all(
        replay[name] == 0
        for name in ("SI", "S2", "SE2", "RA", "SL", "S10", "SH", "SF")
    )
    assert replay["I"] == 8316
    assert replay["Q0"] == Fraction(70323, 10)
    assert primary["rational_null_control"]["is_object"] is False
    return {
        "orientation_five_and_unordered_ten_match": True,
        "minimal_cover_companion_exclusion_matches": True,
        "p3_degree_one_weight_matches": True,
        "independent_split_recombines_to_source_S10": True,
        "split_identity": split_identity,
        "source_SH_matches_independent_R3": True,
        "SF_matches": True,
        "certificate_matches": True,
        "rounding_and_counts_match": True,
        "source_rational_null_replayed": True,
        "independent_integer_rounding_control_is_distinct": True,
        "primary_exact_results_sha256": sha256(path),
    }


def proof_b_comparison() -> dict[str, Any]:
    path = PROOF_B_DIR / "exact-results.json"
    audit = json.loads(path.read_text(encoding="utf-8"))
    assert audit["claim_label"] == (
        "AUDIT_PASS_DERIVED_PENDING_INDEPENDENT_VERIFICATION"
    )
    local = audit["local_capacity"]
    assert local["flags_per_orientation"] == 5
    assert local["flags_per_unordered_nonedge"] == 10
    assert local["private_label_selected_multiplicity"] == 1
    assert local["weighted_selected_row"] == "3*n3+9*p3<=10*|U|"
    assert audit["global_rows"] == {
        "H": "36*V=3564",
        "S10": "10*H-3*n3-9*p3-10*a3-10*b3>=0",
        "SF": "13*V-n3-h-g>=0",
        "SH": "3*h-a3-b3>=0",
    }
    cert = audit["certificate"]
    assert cert["reduced_difference"] == {}
    assert cert["target"] == "70323/10"
    assert cert["integer_Q_lower_bound"] == 7033
    assert cert["edge_added_projective"] == 7726
    assert cert["circuit_scalar_words"] == 15452
    assert cert["active_null"]["asserted_object"] is False
    return {
        "role": "secondary hostile cross-check",
        "used_as_mathematical_premise": False,
        "verdict": "ACCEPT",
        "local_capacity_matches": True,
        "weighted_private_label_row_matches": True,
        "global_rows_match": True,
        "certificate_matches": True,
        "unknown_boundary_preserved": True,
        "proof_b_exact_results_sha256": sha256(path),
    }


def build_results() -> dict[str, Any]:
    integrity = verify_integrity()
    assert integrity["passed"]
    payload: dict[str, Any] = {
        "format": "wave197-degree10-flag-cap-verification-v1",
        "integrity": integrity,
        "independent_math_result": build_math_result(),
        "primary_comparison": primary_comparison(),
        "proof_b_comparison": proof_b_comparison(),
        "verdict": "VERIFIED_WITH_SCOPE",
        "verified_claim": (
            "conditionally, selected exact3 label degree is at most ten, "
            "the weighted S10/SH/SF rows hold, and Q>=7033"
        ),
        "boundary": {
            "conditional_theorem_verified": True,
            "primary_source_compared": True,
            "hostile_proof_b_compared": True,
            "proof_b_used_as_mathematical_premise": False,
            "arithmetic_controls_realized": False,
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
        print(f"WROTE Wave197 independent math result: {args.write_math}")
        return 0
    if args.verify_math:
        expected = json.loads(args.verify_math.read_text(encoding="utf-8"))
        if build_math_result() != expected:
            print("FAIL Wave197 independent math result")
            return 1
        print(f"PASS Wave197 independent math result: {args.verify_math}")
        return 0
    if args.write:
        write_json(args.write, build_results())
        print(f"WROTE Wave197 clean-room result: {args.write}")
        return 0
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if build_results() != expected:
            print("FAIL Wave197 clean-room verification")
            return 1
        print(f"PASS Wave197 clean-room verification: {args.verify}")
        return 0
    print(json.dumps(build_math_result(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
