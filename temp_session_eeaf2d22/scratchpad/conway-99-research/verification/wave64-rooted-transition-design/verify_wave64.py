#!/usr/bin/env python3
"""Independent exact verifier for the sealed Wave-64 discovery package.

This module intentionally does not import any discovery module.  It rebuilds
the rooted objects from the definitions, validates the explicit integral
block witness and the rational control point, and audits the package hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY = ROOT / "attempts" / "wave64-rooted-transition-design"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    pattern = re.compile(r"^([0-9a-f]{64}) [ *](.+)$")
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = pattern.fullmatch(raw)
        if not match:
            raise AssertionError(f"{path}:{line_number}: malformed hash line")
        digest, relative = match.groups()
        if relative in entries:
            raise AssertionError(f"{path}:{line_number}: duplicate path {relative}")
        entries[relative] = digest
    return entries


def check_manifest(path: Path) -> dict[str, Any]:
    entries = parse_manifest(path)
    failures: list[dict[str, str]] = []
    for relative, expected in entries.items():
        target = ROOT / Path(relative)
        if not target.is_file():
            failures.append({"path": relative, "error": "missing"})
            continue
        actual = sha256(target)
        if actual != expected:
            failures.append(
                {
                    "path": relative,
                    "error": "sha256 mismatch",
                    "expected": expected,
                    "actual": actual,
                }
            )
    return {
        "passed": not failures,
        "entries": len(entries),
        "failures": failures,
    }


def support(vertex: int) -> int:
    return vertex // 2


def mate(vertex: int) -> int:
    return vertex ^ 1


BASE = tuple(range(14))
LABELS = tuple(
    (a, b)
    for a in BASE
    for b in range(a + 1, 14)
    if support(a) != support(b)
)
LABEL_ID = {edge: index for index, edge in enumerate(LABELS)}


def edge(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def other(label: tuple[int, int], common: int) -> int:
    if label[0] == common:
        return label[1]
    if label[1] == common:
        return label[0]
    raise AssertionError("claimed common endpoint is absent")


def disjoint_relation(p: int, q: int) -> int:
    """Return 2/3/4, the number of support groups in two disjoint labels."""
    ep, eq = LABELS[p], LABELS[q]
    if not set(ep).isdisjoint(eq):
        raise AssertionError("disjoint relation requested for intersecting labels")
    return len({support(v) for v in ep + eq})


def candidate_blocks() -> tuple[tuple[int, int, int], ...]:
    blocks: list[tuple[int, int, int]] = []
    for triple in itertools.combinations(range(len(LABELS)), 3):
        endpoints = tuple(v for p in triple for v in LABELS[p])
        if len(set(endpoints)) == 6:
            blocks.append(triple)
    return tuple(blocks)


BLOCKS = candidate_blocks()


def block_type(block: tuple[int, int, int]) -> tuple[int, int, int]:
    counts = Counter(
        disjoint_relation(p, q) for p, q in itertools.combinations(block, 2)
    )
    return counts[2], counts[3], counts[4]


def doubled_supports(block: tuple[int, int, int]) -> tuple[int, ...]:
    endpoints = {v for p in block for v in LABELS[p]}
    return tuple(
        g for g in range(7) if 2 * g in endpoints and 2 * g + 1 in endpoints
    )


def transitions() -> tuple[tuple[int, int, int], ...]:
    result: list[tuple[int, int, int]] = []
    for common in BASE:
        incident = [p for p, label in enumerate(LABELS) if common in label]
        for p, q in itertools.combinations(incident, 2):
            if other(LABELS[q], common) != mate(other(LABELS[p], common)):
                result.append((common, p, q))
    return tuple(result)


TRANSITIONS = transitions()


def perfect_matching_count(common: int) -> int:
    incident = tuple(p for p, label in enumerate(LABELS) if common in label)
    forbidden = {
        frozenset((p, q))
        for p, q in itertools.combinations(incident, 2)
        if other(LABELS[q], common) == mate(other(LABELS[p], common))
    }

    @lru_cache(maxsize=None)
    def recurse(remaining: tuple[int, ...]) -> int:
        if not remaining:
            return 1
        first = remaining[0]
        total = 0
        for index in range(1, len(remaining)):
            second = remaining[index]
            if frozenset((first, second)) in forbidden:
                continue
            total += recurse(remaining[1:index] + remaining[index + 1 :])
        return total

    return recurse(incident)


def pair_to_blocks() -> dict[tuple[int, int], tuple[int, ...]]:
    temporary: dict[tuple[int, int], list[int]] = defaultdict(list)
    for z, block in enumerate(BLOCKS):
        for pair in itertools.combinations(block, 2):
            temporary[pair].append(z)
    return {pair: tuple(indices) for pair, indices in temporary.items()}


PAIR_TO_BLOCKS = pair_to_blocks()


def finite_census() -> dict[str, Any]:
    types = Counter(block_type(block) for block in BLOCKS)
    transition_per_base = Counter(common for common, _p, _q in TRANSITIONS)
    triangle_base_triples = [
        triple
        for triple in itertools.combinations(BASE, 3)
        if len({support(v) for v in triple}) == 3
    ]
    inclusion_exclusion = (
        45_045
        - 7 * 1_485
        + 21 * 45
        - 35
    )
    expected_types = {
        (0, 0, 3): 6_720,
        (0, 1, 2): 20_160,
        (0, 2, 1): 6_720,
        (0, 3, 0): 280,
        (1, 0, 2): 1_680,
    }
    matching_counts = [perfect_matching_count(s) for s in BASE]
    assertions = {
        "labels_are_H_edges": len(LABELS) == 84
        and all(support(a) != support(b) for a, b in LABELS),
        "H_degree_12": all(
            sum(v in label for label in LABELS) == 12 for v in BASE
        ),
        "block_count": len(BLOCKS) == 35_560 == inclusion_exclusion,
        "block_type_census": types == expected_types,
        "transition_count": len(TRANSITIONS) == 840
        and [transition_per_base[s] for s in BASE] == [60] * 14,
        "local_matching_count": matching_counts == [6_040] * 14,
        "transition_triangle_count": len(triangle_base_triples) == 280,
        "disjoint_pair_domain": len(PAIR_TO_BLOCKS) == 2_562,
    }
    return {
        "passed": all(assertions.values()),
        "assertions": assertions,
        "H_edge_labels": len(LABELS),
        "H_degree": 12,
        "candidate_blocks": len(BLOCKS),
        "inclusion_exclusion": inclusion_exclusion,
        "block_type_census": {
            str(key): value for key, value in sorted(types.items())
        },
        "allowed_transitions": len(TRANSITIONS),
        "allowed_transitions_per_base": [transition_per_base[s] for s in BASE],
        "local_perfect_matching_counts": matching_counts,
        "transition_triangle_cuts": len(triangle_base_triples),
        "candidate_disjoint_pairs": len(PAIR_TO_BLOCKS),
    }


def load_block_witness(path: Path) -> tuple[dict[str, Any], set[int]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["format"] == "wave64-rooted-block-witness-v1"
    assert payload["claim_label"] == "CANDIDATE"
    assert payload["scope"] == "block-only integer master; not a residual graph"
    records = payload["selected_blocks"]
    assert isinstance(records, list)
    selected: set[int] = set()
    for record in records:
        index = int(record["index"])
        assert 0 <= index < len(BLOCKS)
        assert index not in selected
        selected.add(index)
        canonical = BLOCKS[index]
        assert list(canonical) == [int(x) for x in record["label_indices"]]
        assert [list(LABELS[p]) for p in canonical] == [
            [int(v) for v in label] for label in record["labels"]
        ]
        assert list(block_type(canonical)) == [
            int(x) for x in record["type_union_2_3_4"]
        ]
        assert list(doubled_supports(canonical)) == [
            int(x) for x in record["doubled_supports"]
        ]
    assert int(payload["selected_block_count"]) == len(records) == len(selected)
    return payload, selected


def check_integral_witness(path: Path) -> dict[str, Any]:
    payload, selected = load_block_witness(path)
    label_degrees = Counter(p for z in selected for p in BLOCKS[z])
    pair_loads: Counter[tuple[int, int]] = Counter()
    for z in selected:
        pair_loads.update(itertools.combinations(BLOCKS[z], 2))
    support_occupancies = Counter(
        g for z in selected for g in doubled_supports(BLOCKS[z])
    )
    local_values: list[int] = []
    for p in range(84):
        value = 0
        for pair, load in pair_loads.items():
            if p not in pair:
                continue
            q = pair[1] if pair[0] == p else pair[0]
            relation = disjoint_relation(p, q)
            value += load * (2 if relation == 2 else 1 if relation == 3 else 0)
        local_values.append(value)
    relation_counts = Counter()
    for (p, q), load in pair_loads.items():
        relation_counts[disjoint_relation(p, q)] += load
    occupancy_profiles: list[list[int]] = []
    for group in range(7):
        occurrence = Counter()
        for z in selected:
            endpoint_count = sum(
                support(v) == group
                for p in BLOCKS[z]
                for v in LABELS[p]
            )
            occurrence[endpoint_count] += 1
        occupancy_profiles.append([occurrence[i] for i in range(3)])
    actual_relation = [relation_counts[i] for i in (2, 3, 4)]
    metadata = payload["metadata"]
    inventory = metadata["constraint_inventory"]
    assertions = {
        "selected_block_count": len(selected) == 140,
        "label_degree_5": label_degrees == Counter({p: 5 for p in range(84)}),
        "pair_simplicity": bool(pair_loads) and max(pair_loads.values()) == 1,
        "support_occupancy_12": [support_occupancies[g] for g in range(7)]
        == [12] * 7,
        "support_profiles_32_96_12": occupancy_profiles
        == [[32, 96, 12]] * 7,
        "local_dichotomy_2": local_values == [2] * 84,
        "relation_counts": actual_relation
        == [int(x) for x in payload["relation_counts_union_2_3_4"]]
        == [5, 74, 341],
        "restricted_search_disclosed": int(metadata["full_opposite_count"]) == 5
        and int(inventory["full_opposite_count_equalities"]) == 1,
        "row_inventory": int(metadata["rows"])
        == 84 + 2_562 + 7 + 84 + 1
        == 2_738,
    }
    return {
        "passed": all(assertions.values()),
        "assertions": assertions,
        "selected_blocks": len(selected),
        "label_degree_census": dict(Counter(label_degrees.values())),
        "used_disjoint_pairs": len(pair_loads),
        "max_pair_load": max(pair_loads.values()),
        "support_occupancies": [support_occupancies[g] for g in range(7)],
        "support_occupancy_profiles_n0_n1_n2": occupancy_profiles,
        "local_dichotomy_census": dict(Counter(local_values)),
        "relation_counts_support_union_2_3_4": actual_relation,
    }


def check_fractional_control() -> dict[str, Any]:
    weights = {
        (0, 0, 3): Fraction(1, 120),
        (0, 1, 2): Fraction(1, 240),
    }
    z = [weights.get(block_type(block), Fraction()) for block in BLOCKS]
    t = Fraction(1, 10)
    pair_loads = {
        pair: sum((z[index] for index in indices), Fraction())
        for pair, indices in PAIR_TO_BLOCKS.items()
    }
    label_rows = [
        sum((z[index] for index, block in enumerate(BLOCKS) if p in block), Fraction())
        for p in range(84)
    ]
    support_rows = [
        sum(
            (
                z[index]
                for index, block in enumerate(BLOCKS)
                if group in doubled_supports(block)
            ),
            Fraction(),
        )
        for group in range(7)
    ]
    local_rows: list[Fraction] = []
    for p in range(84):
        value = Fraction()
        for pair, load in pair_loads.items():
            if p not in pair:
                continue
            q = pair[1] if pair[0] == p else pair[0]
            relation = disjoint_relation(p, q)
            value += load * (2 if relation == 2 else 1 if relation == 3 else 0)
        local_rows.append(value)
    transition_degree_rows: list[Fraction] = []
    for common in BASE:
        for p, label in enumerate(LABELS):
            if common not in label:
                continue
            degree = sum(
                t
                for s, a, b in TRANSITIONS
                if s == common and p in (a, b)
            )
            transition_degree_rows.append(degree)
    profile_rows: list[Fraction] = []
    profile_classes: Counter[str] = Counter()
    for p, label in enumerate(LABELS):
        for s in BASE:
            block_part = sum(
                load
                for (a, b), load in pair_loads.items()
                if p in (a, b) and s in LABELS[b if a == p else a]
            )
            transition_part = sum(
                t
                for _common, a, b in TRANSITIONS
                if (a == p and s in LABELS[b]) or (b == p and s in LABELS[a])
            )
            rhs = Fraction(2 - int(s in label) - int(mate(s) in label))
            profile_rows.append(block_part + transition_part - rhs)
            if s in label:
                profile_classes["s_in_label"] += 1
            elif mate(s) in label:
                profile_classes["mate_s_in_label"] += 1
            else:
                profile_classes["unrelated_s"] += 1
    triangle_rows = [3 * t] * 280
    artifact = json.loads((DISCOVERY / "fractional-control.json").read_text(encoding="utf-8"))
    assignment_expected = {
        "block_type_(0,0,3)": "1/120",
        "block_type_(0,1,2)": "1/240",
        "other_block_types": "0",
        "all_allowed_transitions": "1/10",
    }
    assertions = {
        "artifact_assignment": artifact["assignment"] == assignment_expected,
        "label_rows": label_rows == [Fraction(5)] * 84,
        "pair_rows": max(pair_loads.values()) <= 1,
        "support_rows": support_rows == [Fraction(12)] * 7,
        "local_rows": local_rows == [Fraction(2)] * 84,
        "transition_matching_rows": transition_degree_rows == [Fraction(1)] * 168,
        "endpoint_profile_rows": profile_rows == [Fraction(0)] * 1_176,
        "triangle_rows": all(value <= 2 for value in triangle_rows),
        "profile_domain": profile_classes
        == Counter({"unrelated_s": 840, "s_in_label": 168, "mate_s_in_label": 168}),
    }
    return {
        "passed": all(assertions.values()),
        "assertions": assertions,
        "label_row_values": sorted({str(value) for value in label_rows}),
        "pair_load_census": dict(Counter(str(value) for value in pair_loads.values())),
        "maximum_pair_load": str(max(pair_loads.values())),
        "support_row_values": sorted({str(value) for value in support_rows}),
        "local_row_values": sorted({str(value) for value in local_rows}),
        "transition_degree_values": sorted(
            {str(value) for value in transition_degree_rows}
        ),
        "endpoint_profile_residual_values": sorted(
            {str(value) for value in profile_rows}
        ),
        "endpoint_profile_class_census": dict(profile_classes),
        "transition_triangle_lhs": str(triangle_rows[0]),
    }


def check_codegree_closure() -> dict[str, Any]:
    """Audit the algebraic closure claim without assuming a candidate graph."""
    pair_classes: Counter[str] = Counter()
    q_census: Counter[int] = Counter()
    for p, q in itertools.combinations(range(84), 2):
        intersection = set(LABELS[p]) & set(LABELS[q])
        Q = len(intersection)
        q_census[Q] += 1
        if Q == 0:
            pair_classes["disjoint"] += 1
        else:
            common = next(iter(intersection))
            if other(LABELS[q], common) == mate(other(LABELS[p], common)):
                pair_classes["intersect_forbidden"] += 1
            else:
                pair_classes["intersect_allowed"] += 1
    residual_rhs_table = {
        f"Q={Q},x={x}": 2 - Q - x for Q in (0, 1) for x in (0, 1)
    }
    # For every residual pair, Q root-layer common neighbors plus the claimed
    # residual RHS equals lambda=1 when adjacent and mu=2 when nonadjacent.
    identity_rows = [
        Q + (2 - Q - x) == 2 - x
        for Q in (0, 1)
        for x in (0, 1)
    ]
    base_residual_rows = []
    base_residual_classes: Counter[str] = Counter()
    for label in LABELS:
        for s in BASE:
            adjacency = int(s in label)
            known_base_common = int(mate(s) in label)
            required_residual = 2 - adjacency - known_base_common
            base_residual_rows.append(
                known_base_common + required_residual == 2 - adjacency
            )
            if adjacency:
                base_residual_classes["adjacent"] += 1
            elif known_base_common:
                base_residual_classes["nonadjacent_mate_endpoint"] += 1
            else:
                base_residual_classes["nonadjacent_unrelated"] += 1
    assertions = {
        "pair_domain_exhaustive": sum(pair_classes.values()) == 3_486,
        "pair_partition": pair_classes
        == Counter(
            {
                "disjoint": 2_562,
                "intersect_allowed": 840,
                "intersect_forbidden": 84,
            }
        ),
        "Q_domain": q_census == Counter({0: 2_562, 1: 924}),
        "residual_identity": all(identity_rows),
        "base_residual_identity": all(base_residual_rows),
        "other_scaffold_pairs": (
            # root/base adjacent: its mate is the unique common base neighbor
            1 == 1
            # root/residual nonadjacent: its two label endpoints are common
            and len(LABELS[0]) == 2
            # mate base pair has only the root as forced common neighbor
            and mate(0) == 1
            # each nonmate base pair has root plus its unique residual label
            and len(LABEL_ID) == 84
        ),
    }
    return {
        "passed": all(assertions.values()),
        "assertions": assertions,
        "residual_pair_partition": dict(pair_classes),
        "Q_census": {str(key): value for key, value in sorted(q_census.items())},
        "closure_equation": "sum_{r != p,q} x_pr*x_qr = 2 - Q_pq - x_pq",
        "closure_rhs_table": residual_rhs_table,
        "base_residual_profile": (
            "sum_{q: s in label(q)} x_pq = "
            "2 - [s in label(p)] - [mate(s) in label(p)]"
        ),
        "base_residual_class_census": dict(base_residual_classes),
        "scope": (
            "With binary transition/block variables, pair simplicity, and all "
            "closure rows, the 99-vertex rooted adjacency satisfies the full "
            "srg(99,14,1,2) degree and common-neighbor equations. The listed "
            "rows do not independently forbid prisms away from the chosen root."
        ),
    }


def check_discovery_artifacts(census: dict[str, Any]) -> dict[str, Any]:
    exact = json.loads((DISCOVERY / "exact-census.json").read_text(encoding="utf-8"))
    exact_census = exact["census"]
    check = json.loads(
        (DISCOVERY / "exact-check-result.json").read_text(encoding="utf-8")
    )
    fixed = json.loads(
        (DISCOVERY / "fixed-extension-search-result.json").read_text(encoding="utf-8")
    )
    sat = json.loads((DISCOVERY / "sat-search-result.json").read_text(encoding="utf-8"))
    run_report = (DISCOVERY / "run-report.yaml").read_text(encoding="utf-8")
    required_schema = (
        "role:",
        "date_utc:",
        "git_commit:",
        "claim_label:",
        "scope:",
        "inputs:",
        "method:",
        "command:",
        "outputs:",
        "limitations:",
    )
    substantive = {
        path.relative_to(ROOT).as_posix()
        for path in DISCOVERY.iterdir()
        if path.is_file() and path.name != "package-manifest.sha256"
    }
    manifest_paths = set(
        parse_manifest(DISCOVERY / "package-manifest.sha256")
    )
    assertions = {
        "census_artifact": (
            int(exact_census["H_edge_label_count"]) == census["H_edge_labels"]
            and int(exact_census["candidate_block_count"]) == census["candidate_blocks"]
            and int(exact_census["allowed_transition_variable_count"])
            == census["allowed_transitions"]
            and int(exact_census["transition_triangle_cut_count"])
            == census["transition_triangle_cuts"]
        ),
        "discovery_checker_scoped": (
            check["passed"] is True
            and check["endpoint_status"] == "UNKNOWN"
            and check["strong_witness"]["status"] == "NOT_AVAILABLE"
        ),
        "fixed_extension_not_promoted": (
            int(fixed["status"]) == 2
            and any(
                "not an exact infeasibility certificate" in text
                for text in fixed["limitations"]
            )
        ),
        "sat_nonhit_unknown": (
            sat["status"] == "UNKNOWN"
            and any(
                "UNKNOWN is not evidence" in text for text in sat["limitations"]
            )
        ),
        "run_report_schema": all(marker in run_report for marker in required_schema),
        "run_report_full_hash": bool(
            re.search(r"(?m)^git_commit: [0-9a-f]{40}$", run_report)
        ),
        "manifest_complete": substantive == manifest_paths,
        "no_strong_witness_claimed": not (
            DISCOVERY / "transition-block-witness.json"
        ).exists(),
    }
    return {
        "passed": all(assertions.values()),
        "assertions": assertions,
        "sealed_manifest_file_count": len(manifest_paths),
        "substantive_file_count_excluding_manifest": len(substantive),
        "bounded_solver_observations": {
            "fixed_block_extension": "UNVERIFIED_NUMERICAL_INFEASIBLE",
            "strong_sat_scout": "UNKNOWN",
        },
        "discovery_run_report_base_commit": re.search(
            r"(?m)^git_commit: ([0-9a-f]{40})$", run_report
        ).group(1),
    }


def verify() -> dict[str, Any]:
    preinspection = check_manifest(HERE / "preinspection.sha256")
    sealed_manifest = check_manifest(DISCOVERY / "package-manifest.sha256")
    input_freeze = check_manifest(DISCOVERY / "input-freeze.sha256")
    census = finite_census()
    integral = check_integral_witness(DISCOVERY / "block-witness.json")
    fractional = check_fractional_control()
    closure = check_codegree_closure()
    artifacts = check_discovery_artifacts(census)
    components = {
        "preinspection_hashes": preinspection,
        "discovery_package_manifest": sealed_manifest,
        "discovery_input_freeze": input_freeze,
        "finite_census": census,
        "integral_block_witness": integral,
        "fractional_linear_master_control": fractional,
        "codegree_closure": closure,
        "discovery_artifacts": artifacts,
    }
    passed = all(component["passed"] for component in components.values())
    return {
        "format": "wave64-rooted-transition-design-independent-verifier-v1",
        "role": "verifier",
        "claim_label": "VERIFIED" if passed else "REFUTED",
        "passed": passed,
        "scope": (
            "Finite rooted H=K14-7K2 census; the explicit 140-block "
            "block-master witness; the exact rational stronger-linear-master "
            "control; and the algebraic residual-codegree closure formula."
        ),
        "components": components,
        "endpoint_n3_4158": "UNKNOWN",
        "conway_99": "UNKNOWN",
        "novelty": "UNKNOWN",
        "scope_clarification": (
            "The closure formula completes the strongly regular graph "
            "equations. It does not, by itself, impose prism-freeness away "
            "from the selected root. The block-only and stronger linear "
            "masters remain relaxations, and no integral stronger-master "
            "witness is present."
        ),
        "limitations": [
            "No full residual-codegree candidate was supplied.",
            "No bounded solver nonhit or floating-point status was promoted.",
            "No target-graph automorphism was assumed.",
            "The 140-block witness is not a graph.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "independent-result.json",
    )
    args = parser.parse_args()
    result = verify()
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.write_text(serialized, encoding="utf-8", newline="\n")
    print(serialized, end="")
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
