"""Clean-room verifier for the Wave195 Hilton--Milner theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INPUT_FREEZE = HERE / "input-freeze.sha256"
INDEPENDENT_FREEZE = HERE / "independent-result-freeze.sha256"
HASH_LINE = re.compile(r"^([0-9a-fA-F]{64})\s+\*?(.+?)\s*$")
C_VALUE = 4158
VERTICES = 99
NONNEIGHBORS_PER_VERTEX = 84


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


def exact_three_flag_certificate() -> dict[str, Any]:
    return {
        "flag": "(x,T), where T is a triangle anticomplete to x",
        "star_ground_set_size": 7,
        "A_size": 3,
        "relation": "z_T+2*sum_(S in A_x(T)) z_S=0",
        "companion_relation": (
            "z_T+sum_(S in S_x minus A_x(T)) z_S=0"
        ),
        "same_center_same_A_injective": (
            "subtracting the two four-circuit relations would give a "
            "weight-two relation z_T-z_Tprime"
        ),
        "dual_distance_lower_bound": 4,
        "one_flag_one_companion_pair": True,
    }


def pairwise_intersection_certificate() -> dict[str, Any]:
    return {
        "claim": (
            "for distinct exact3 flags with fixed center x, their A_x "
            "three-subsets intersect"
        ),
        "disjoint_case": (
            "if A and Aprime are disjoint, let r be the unique star block "
            "outside A union Aprime"
        ),
        "relation_sum": (
            "(z_T+2 sum_A z)+(z_Tprime+sum_(S_x minus Aprime) z)"
            "=z_T+z_Tprime+z_r"
        ),
        "contradiction_weight": 3,
        "dual_distance_lower_bound": 4,
    }


def hilton_milner_certificate() -> dict[str, Any]:
    n = 7
    k = 3
    bound = comb(n - 1, k - 1) - comb(n - k - 1, k - 1) + 1
    assert n > 2 * k
    assert bound == 13
    return {
        "theorem_hypotheses": {
            "uniform_family": "distinct 3-subsets of a 7-set",
            "pairwise_intersecting": True,
            "empty_total_intersection": True,
            "range": "n>2k",
        },
        "formula": "C(n-1,k-1)-C(n-k-1,k-1)+1",
        "n": n,
        "k": k,
        "calculation": "C(6,2)-C(3,2)+1=15-3+1=13",
        "bound": bound,
        "non_common_star_leaf_union_bound": 3 * bound,
    }


def common_star_certificate() -> dict[str, Any]:
    star_family_bound = comb(6, 2)
    assert star_family_bound == 15
    return {
        "common_block": "S={x,p,q} belongs to every A_x(T)",
        "fixed_center_injectivity_bound": "c_x<=C(6,2)=15",
        "c_x_upper": star_family_bound,
        "six_incidence_simplicity": (
            "the two incidences inside S use p and q separately and have "
            "distinct leaf types"
        ),
        "p_leaf_options": (
            "at most deg(p)-2=12 after excluding the two neighbors x and q"
        ),
        "q_leaf_options": (
            "at most deg(q)-2=12 after excluding the two neighbors x and p"
        ),
        "remaining_leaf_options": "at most one per flag, hence at most c_x",
        "union_logic": (
            "every leaf lies in the p-leaf set, q-leaf set, or the one "
            "remaining-leaf choice of its flag"
        ),
        "j_x_upper": "12+12+c_x<=39",
        "universal_j_x_upper": 39,
    }


def oriented_label_certificate() -> dict[str, Any]:
    return {
        "J": (
            "number of distinct oriented nonedge labels (center,leaf) in "
            "the union of all selected, old, and new exact3 flags"
        ),
        "upper": "J=sum_x j_x<=99*39=3861=13C/14",
        "U": "undirected label union of selected type3 circuits",
        "cover_lower": "|U|>=C-n1-2n2",
        "selected_type3_contribution": (
            "each distinct undirected label in U supplies at least one "
            "oriented label"
        ),
        "a3_injection": (
            "one exact3 raw orientation for each distinct type1 private label"
        ),
        "b3_injection": (
            "the two type2 endpoint translates of one private undirected "
            "label, when exact3, have opposite centers and hence opposite "
            "oriented labels"
        ),
        "different_sources": (
            "different private source labels have different underlying "
            "undirected nonedges"
        ),
        "outside_U": (
            "type1/type2 private labels cannot occur in a selected type3 "
            "label set"
        ),
        "lower": "J>=|U|+a3+b3>=C-n1-2n2+a3+b3",
        "SG": "n1+2n2-a3-b3-C/14>=0",
    }


def inherited_pool_separation_certificate() -> dict[str, Any]:
    return {
        "exact3_flag_families": {
            "selected": "n3 selected/companion pairs",
            "old": "h orbit-closed raw pairs",
            "new": "g orbit-closed residual pairs",
        },
        "selected_pair_simplicity": (
            "a minimal cover cannot select both members of one companion pair"
        ),
        "old_vs_selected": "Wave189 privacy and orbit-closure separation",
        "new_vs_old": "Wave194 old-pool closure separation",
        "new_vs_selected": (
            "Wave194 privacy and fixed-point-free companion separation"
        ),
        "flag_injectivity_across_pools": (
            "one flag determines one companion pair, so disjoint circuit "
            "pairs give distinct flags"
        ),
        "all_relevant_exact3_flags_form_one_simple_family": True,
    }


def failed_route_quarantine() -> dict[str, Any]:
    return {
        "route": "mixed type-one endpoint-orientation amplification",
        "status": "QUARANTINED_FAILED_ROUTE",
        "reason": (
            "the type-one argument guarantees only one chosen short "
            "majority translation; it does not guarantee both endpoint "
            "translations or both orientations"
        ),
        "safe_use": (
            "each a3 assignment contributes exactly one oriented private "
            "label to J, with no factor two"
        ),
        "used_in_certificate": False,
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
    return tuple(sum(values, Fraction()) for values in zip(*rows))


def scale(
    value: int | Fraction, source: tuple[Fraction, ...]
) -> tuple[Fraction, ...]:
    factor = Fraction(value)
    return tuple(factor * item for item in source)


def coefficient_certificate() -> dict[str, Any]:
    # Substitute n1=a1+a2+a3, p2=(b1+b3)/2, p3=c1+c2,
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
    target = add_rows(q0, row(C=Fraction(-47, 28)))
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
    SG = row(
        C=Fraction(-1, 14),
        a1=1,
        a2=1,
        n2=2,
        b3=-1,
    )
    SE2 = row(r2=2, a2=-1, c2=-1)
    certificate = add_rows(
        scale(Fraction(2, 3), SI),
        scale(Fraction(4, 3), S2),
        scale(Fraction(2, 3), RA),
        scale(Fraction(1, 3), SL),
        scale(Fraction(1, 6), SG),
        scale(Fraction(1, 6), SE2),
        scale(Fraction(1, 6), row(a1=1)),
        scale(Fraction(1, 2), row(b3=1)),
        scale(Fraction(1, 6), row(c2=1)),
        scale(Fraction(1, 3), row(W=1)),
    )
    assert certificate == target
    exact_bound = Fraction(47 * C_VALUE, 28)
    assert exact_bound == Fraction(13959, 2)
    assert int(exact_bound) + 1 == 6980
    return {
        "variable_order_after_split_substitution": list(VARIABLES),
        "Q0": "n1+n2+2n3+r1+r2+2h+y+2g+W",
        "SI": "I-2C",
        "S2": "p2-n2",
        "RA": "3h+y+3g-(a2+a3+2b3+c2)",
        "SL": "n1+2n2+c1+2r2+y+2W-C",
        "SG": "n1+2n2-a3-b3-C/14",
        "SE2": "2r2-a2-c2",
        "identity": (
            "Q0-47C/28=(2/3)SI+(4/3)S2+(2/3)RA+SL/3"
            "+SG/6+SE2/6+a1/6+b3/2+c2/6+W/3"
        ),
        "lower": "Q>=47C/28",
        "C": C_VALUE,
        "exact_rational_lower": "13959/2",
        "integer_nonedge_projective_Q": 6980,
    }


def _json_fraction(value: Fraction) -> int | str:
    return value.numerator if value.denominator == 1 else str(value)


def rational_null_control() -> dict[str, Any]:
    values = {
        "a1": Fraction(0),
        "a2": Fraction(297),
        "a3": Fraction(0),
        "b1": Fraction(0),
        "b3": Fraction(0),
        "c1": Fraction(3564),
        "c2": Fraction(0),
        "n2": Fraction(0),
        "n3": Fraction(1386),
        "r2": Fraction(297, 2),
        "h": Fraction(99),
        "y": Fraction(0),
        "g": Fraction(0),
        "W": Fraction(0),
    }
    n1 = values["a1"] + values["a2"] + values["a3"]
    p2 = (values["b1"] + values["b3"]) / 2
    p3 = values["c1"] + values["c2"]
    r1 = values["a1"] + values["b1"] + values["c1"]
    I = 2 * n1 + 2 * values["n2"] + 3 * values["n3"] + p2 + p3
    slacks = {
        "SI": I - 2 * C_VALUE,
        "S2": p2 - values["n2"],
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
            n1
            + 2 * values["n2"]
            + values["c1"]
            + 2 * values["r2"]
            + values["y"]
            + 2 * values["W"]
            - C_VALUE
        ),
        "SG": (
            n1
            + 2 * values["n2"]
            - values["a3"]
            - values["b3"]
            - Fraction(C_VALUE, 14)
        ),
        "SE2": 2 * values["r2"] - values["a2"] - values["c2"],
    }
    assert all(value == 0 for value in slacks.values())
    Q0 = (
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
    assert Q0 == Fraction(13959, 2)
    return {
        "row": {name: _json_fraction(value) for name, value in values.items()},
        "derived": {
            "n1": _json_fraction(n1),
            "p2": _json_fraction(p2),
            "p3": _json_fraction(p3),
            "r1": _json_fraction(r1),
        },
        "zero_certificate_slacks": {
            name: _json_fraction(value) for name, value in slacks.items()
        },
        "Q0": _json_fraction(Q0),
        "integral_at_C_4158": False,
        "asserted_to_be_graph_code_cover_or_flag_family": False,
    }


def build_math_result() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "format": "wave195-hilton-milner-clean-room-math-v1",
        "conditional_setting": "prism-free rank-11 endpoint n3=4158, P=0",
        "exact_three_flags": exact_three_flag_certificate(),
        "pairwise_intersection": pairwise_intersection_certificate(),
        "hilton_milner": hilton_milner_certificate(),
        "common_star": common_star_certificate(),
        "oriented_labels": oriented_label_certificate(),
        "pool_separation": inherited_pool_separation_certificate(),
        "failed_route": failed_route_quarantine(),
        "coefficient_certificate": coefficient_certificate(),
        "rational_null": rational_null_control(),
        "bounds": {
            "nonedge_projective_short_circuits_Q": 6980,
            "edge_isolated_projective_short_circuits": 693,
            "all_projective_short_circuits": 7673,
            "scalar_short_circuit_words": 15346,
            "wave188_all_short_word_bound_remains_stronger": 18018,
        },
        "verdict": "VERIFIED_WITH_SCOPE",
        "boundary": {
            "conditional_theorem_verified": True,
            "rational_null_realized": False,
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
        "attempts/wave195-leaf-packet-intersection-proof-a/package-manifest.sha256",
        "attempts/wave195-packet-cohomology-proof-b/package-manifest.sha256",
        "verification/wave174-no-weight3-dual/package-manifest.sha256",
        "verification/wave180-capacity3-companion/package-manifest.sha256",
        "verification/wave186-star-translation-cover-verifier/package-manifest.sha256",
        "verification/wave188-affine-star-word-amplification-verifier/package-manifest.sha256",
        "verification/wave189-degree7-star-orbit-verifier/package-manifest.sha256",
        "verification/wave191-exact-three-residual-verifier/package-manifest.sha256",
        "verification/wave194-five-thirds-verifier/package-manifest.sha256",
    }
    actual = {relative for _, relative in entries}
    if actual != expected:
        raise AssertionError(f"unexpected input set: {sorted(actual ^ expected)}")
    failures = check_entries(entries)

    primary_manifest = (
        ROOT
        / "attempts/wave195-leaf-packet-intersection-proof-a"
        / "package-manifest.sha256"
    )
    audit_manifest = (
        ROOT
        / "attempts/wave195-packet-cohomology-proof-b"
        / "package-manifest.sha256"
    )
    primary_sha = sha256(primary_manifest)
    audit_sha = sha256(audit_manifest)
    assert primary_sha == (
        "1055402dac438ad8f13e9e3fc91ec71a6da0f936306f379fa8f3deedb5b0c45b"
    )
    assert audit_sha == (
        "feb5cbd767f8e7f223a012818b6177119a233b3a8bb3cbbb148d52fa7a2706c3"
    )

    nested_paths = {
        "primary_source": primary_manifest,
        "audit_source": audit_manifest,
        "primary_source_inputs": (
            ROOT
            / "attempts/wave195-leaf-packet-intersection-proof-a"
            / "input-freeze.sha256"
        ),
        "audit_source_inputs": (
            ROOT
            / "attempts/wave195-packet-cohomology-proof-b"
            / "input-freeze.sha256"
        ),
        "wave174": (
            ROOT / "verification/wave174-no-weight3-dual/package-manifest.sha256"
        ),
        "wave180": (
            ROOT
            / "verification/wave180-capacity3-companion/package-manifest.sha256"
        ),
        "wave186": (
            ROOT
            / "verification/wave186-star-translation-cover-verifier"
            / "package-manifest.sha256"
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
        "wave194": (
            ROOT
            / "verification/wave194-five-thirds-verifier"
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


def _evaluate_source_null(values: dict[str, Fraction]) -> dict[str, Fraction]:
    n1 = values["a1"] + values["a2"] + values["a3"]
    p2 = (values["b1"] + values["b3"]) / 2
    p3 = values["c1"] + values["c2"]
    r1 = values["a1"] + values["b1"] + values["c1"]
    assert n1 == values["n1"]
    assert p2 == values["p2"]
    assert p3 == values["p3"]
    assert r1 == values["r1"]
    I = 2 * n1 + 2 * values["n2"] + 3 * values["n3"] + p2 + p3
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
    return {
        "SI": I - 2 * values["C"],
        "S2": p2 - values["n2"],
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
            n1
            + 2 * values["n2"]
            + values["c1"]
            + 2 * values["r2"]
            + values["y"]
            + 2 * values["W"]
            - values["C"]
        ),
        "SG": (
            values["K"]
            - values["C"]
            + n1
            + 2 * values["n2"]
            - values["a3"]
            - values["b3"]
        ),
        "Q0": q0,
    }


def source_comparison() -> dict[str, Any]:
    primary_path = (
        ROOT
        / "attempts/wave195-leaf-packet-intersection-proof-a"
        / "exact-results.json"
    )
    audit_path = (
        ROOT
        / "attempts/wave195-packet-cohomology-proof-b"
        / "exact-results.json"
    )
    primary = json.loads(primary_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))

    assert primary["ternary_cancellations"]["equal_A_cancellation_weight"] == 2
    assert primary["ternary_cancellations"]["disjoint_A_cancellation_weight"] == 3
    assert audit["local_coefficients"]["equal_A_difference_weight"] == 2
    assert audit["local_coefficients"]["disjoint_A_plus_star_weight"] == 3

    hm = primary["local_set_system"]["hilton_milner"]
    assert hm["hypothesis"] == (
        "n>2k, pairwise intersecting, empty total intersection"
    )
    assert hm["formula"] == "C(n-1,k-1)-C(n-k-1,k-1)+1"
    assert hm["first_term"] == 15
    assert hm["subtracted_term"] == 3
    assert hm["nontrivial_cap"] == 13
    assert audit["fixed_center_theorem"]["hilton_milner_nontrivial_cap"] == 13
    assert audit["fixed_center_theorem"]["erdos_ko_rado_trivial_cap"] == 15
    assert audit["fixed_center_theorem"]["trivial_common_block_neighbor_base"] == 12
    assert primary["local_set_system"]["unified_local_row"] == "j_x<=39"
    assert audit["fixed_center_theorem"]["universal_oriented_label_cap"] == (
        "j_x<=39"
    )

    assert primary["local_set_system"]["affine_constant_H"] == 3861
    assert primary["claim"]["new_slack"] == (
        "H-C+n1+2*n2-a3-b3>=0"
    )
    assert audit["global_row"]["definition"] == (
        "SG=K-C+n1+2*n2-a3-b3>=0"
    )
    assert primary["local_set_system"]["cover_lower_row"] == (
        "J>=C-n1-2*n2+a3+b3"
    )
    assert audit["global_row"]["lower"] == "J>=C-n1-2*n2+a3+b3"

    primary_certificate = primary["certificate"]
    audit_certificate = audit["certificate"]
    assert primary_certificate["target"] == "(11*C-H)/6"
    assert primary_certificate["slack_weights"] == {
        "RA": "2/3",
        "S2": "4/3",
        "SE2": "1/6",
        "SG": "1/6",
        "SI": "2/3",
        "SL": "1/3",
    }
    assert audit_certificate["reduced_difference"] == {}
    assert audit_certificate["rational_Q_target"] == "13959/2"
    assert audit_certificate["integer_Q_lower_bound"] == 6980
    assert audit_certificate["edge_added_projective"] == 7673
    assert audit_certificate["circuit_scalar_words"] == 15346
    assert Fraction(11 * C_VALUE - 3861, 6) == Fraction(47 * C_VALUE, 28)

    names = (
        "C K n1 n2 n3 p2 p3 a1 a2 a3 b1 b3 c1 c2 "
        "r1 r2 h y g W"
    ).split()
    primary_row = {name: Fraction() for name in names}
    primary_row.update(
        {
            name: Fraction(value)
            for name, value in primary["rational_null_control"]["row"].items()
        }
    )
    primary_row["K"] = primary_row.pop("H")
    primary_null = _evaluate_source_null(primary_row)
    assert all(
        primary_null[name] == 0
        for name in ("SI", "S2", "SE2", "RA", "SL", "SG")
    )
    assert primary_null["Q0"] == Fraction(13959, 2)

    audit_row = {name: Fraction() for name in names}
    audit_row.update(
        {
            "C": Fraction(4158),
            "K": Fraction(3861),
            "n1": Fraction(99),
            "a2": Fraction(99),
            "n2": Fraction(99),
            "p2": Fraction(99),
            "b1": Fraction(198),
            "n3": Fraction(1386),
            "p3": Fraction(3663),
            "c1": Fraction(3663),
            "r1": Fraction(3861),
            "r2": Fraction(99, 2),
            "y": Fraction(99),
        }
    )
    audit_null = _evaluate_source_null(audit_row)
    assert all(
        audit_null[name] == 0
        for name in ("SI", "S2", "SE2", "RA", "SL", "SG")
    )
    assert audit_null["Q0"] == Fraction(13959, 2)
    assert audit_certificate["rational_null"]["asserted_object"] is False
    assert primary["rational_null_control"]["is_object"] is False

    primary_failed = (
        ROOT
        / "attempts/wave195-leaf-packet-intersection-proof-a"
        / "failed-routes.md"
    ).read_text(encoding="utf-8").lower()
    audit_failed = (
        ROOT / "attempts/wave195-packet-cohomology-proof-b/failed-routes.md"
    ).read_text(encoding="utf-8").lower()
    assert "mixed-orientation" in primary_failed
    assert "gap" in primary_failed
    assert "not used" in primary_failed
    assert "no canonical-leaf conclusion is used" in audit_failed

    return {
        "flag_injectivity_matches": True,
        "pairwise_intersection_matches": True,
        "hilton_milner_hypotheses_and_formula_match": True,
        "common_star_jx_bound_matches": True,
        "oriented_b3_and_J_rows_match": True,
        "SG_matches": True,
        "dual_identity_matches": True,
        "integer_rounding_and_counts_match": True,
        "source_null_rows_replayed_independently": True,
        "all_null_rows_arithmetic_only": True,
        "failed_mixed_type1_route_quarantined": True,
        "primary_exact_results_sha256": sha256(primary_path),
        "audit_exact_results_sha256": sha256(audit_path),
    }


def build_results() -> dict[str, Any]:
    integrity = verify_frozen_inputs()
    assert integrity["passed"]
    payload: dict[str, Any] = {
        "format": "wave195-hilton-milner-clean-room-verification-v1",
        "integrity": integrity,
        "independent_math_result": build_math_result(),
        "source_comparison": source_comparison(),
        "external_theorem_check": {
            "original_article_doi": "10.1093/qmath/18.1.369",
            "original_metadata_verified": True,
            "independent_primary_proof_formula_verified": True,
            "specialization": "C(6,2)-C(3,2)+1=13",
        },
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
        print(f"WROTE Wave195 independent math result: {args.write_math}")
        return 0
    if args.verify_math:
        expected = json.loads(args.verify_math.read_text(encoding="utf-8"))
        if build_math_result() != expected:
            print("FAIL Wave195 independent math result")
            return 1
        print(f"PASS Wave195 independent math result: {args.verify_math}")
        return 0
    if args.write:
        write_json(args.write, build_results())
        print(f"WROTE Wave195 clean-room result: {args.write}")
        return 0
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if build_results() != expected:
            print("FAIL Wave195 clean-room verification")
            return 1
        print(f"PASS Wave195 clean-room verification: {args.verify}")
        return 0
    print(json.dumps(build_math_result(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
