#!/usr/bin/env python3
"""Exact checker for Wave-64 finite censuses and candidate witnesses.

This checker does not import the discovery enumerator and never trusts a
solver status.  All accepted claims are reconstructed from integer sets and
``fractions.Fraction`` arithmetic.
"""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent


def group(v: int) -> int:
    return v // 2


def conjugate(v: int) -> int:
    return v ^ 1


VERTICES = tuple(range(14))
EDGES = tuple(
    (a, b)
    for a in VERTICES
    for b in range(a + 1, 14)
    if group(a) != group(b)
)
EDGE_ID = {e: i for i, e in enumerate(EDGES)}


def canonical_edge(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def relation(i: int, j: int) -> int:
    """0/1/2 = support-union 2/3/4 for disjoint H-edges."""
    a, b = EDGES[i], EDGES[j]
    if not set(a).isdisjoint(b):
        raise ValueError("relation called on intersecting edges")
    return 4 - len({group(x) for x in a + b})


def candidate_blocks() -> tuple[tuple[int, int, int], ...]:
    answer = []
    for triple in itertools.combinations(range(84), 3):
        endpoints = EDGES[triple[0]] + EDGES[triple[1]] + EDGES[triple[2]]
        if len(set(endpoints)) == 6:
            answer.append(triple)
    return tuple(answer)


BLOCKS = candidate_blocks()


def block_signature(block: tuple[int, int, int]) -> tuple[int, int, int]:
    c = Counter(relation(i, j) for i, j in itertools.combinations(block, 2))
    return (c[2], c[1], c[0])


def doubled_groups(block: tuple[int, int, int]) -> set[int]:
    endpoints = set(sum((EDGES[i] for i in block), ()))
    return {g for g in range(7) if 2 * g in endpoints and 2 * g + 1 in endpoints}


def all_transitions() -> tuple[tuple[int, int, int], ...]:
    answer = []
    for s in VERTICES:
        incident = [i for i, e in enumerate(EDGES) if s in e]
        for i, j in itertools.combinations(incident, 2):
            oi = EDGES[i][0] if EDGES[i][1] == s else EDGES[i][1]
            oj = EDGES[j][0] if EDGES[j][1] == s else EDGES[j][1]
            if conjugate(oi) != oj:
                answer.append((s, i, j))
    return tuple(answer)


TRANSITIONS = all_transitions()


def matching_count(items: tuple[int, ...], forbidden: set[tuple[int, int]]) -> int:
    if not items:
        return 1
    first = items[0]
    return sum(
        matching_count(items[1:k] + items[k + 1 :], forbidden)
        for k in range(1, len(items))
        if tuple(sorted((first, items[k]))) not in forbidden
    )


def check_census() -> dict[str, object]:
    type_counts = Counter(block_signature(block) for block in BLOCKS)
    matching_counts = []
    for s in VERTICES:
        incident = tuple(i for i, e in enumerate(EDGES) if s in e)
        forbidden = set()
        for i, j in itertools.combinations(incident, 2):
            oi = EDGES[i][0] if EDGES[i][1] == s else EDGES[i][1]
            oj = EDGES[j][0] if EDGES[j][1] == s else EDGES[j][1]
            if conjugate(oi) == oj:
                forbidden.add((i, j))
        matching_counts.append(matching_count(incident, forbidden))
    transition_triangles = sum(
        len({group(v) for v in triple}) == 3
        for triple in itertools.combinations(VERTICES, 3)
    )
    expected_types = {
        (0, 0, 3): 6720,
        (0, 1, 2): 20160,
        (0, 2, 1): 6720,
        (0, 3, 0): 280,
        (1, 0, 2): 1680,
    }
    passed = (
        len(EDGES) == 84
        and len(BLOCKS) == 35560
        and type_counts == expected_types
        and len(TRANSITIONS) == 840
        and set(matching_counts) == {6040}
        and transition_triangles == 280
    )
    return {
        "passed": passed,
        "H_edges": len(EDGES),
        "candidate_blocks": len(BLOCKS),
        "block_type_counts": {str(k): v for k, v in sorted(type_counts.items())},
        "allowed_transitions": len(TRANSITIONS),
        "transition_perfect_matching_counts": matching_counts,
        "transition_triangle_count": transition_triangles,
    }


def parse_blocks(payload: dict[str, object]) -> set[int]:
    records = payload["selected_blocks"]
    assert isinstance(records, list)
    selected: set[int] = set()
    for item in records:
        assert isinstance(item, dict)
        idx = int(item["index"])
        assert 0 <= idx < len(BLOCKS)
        assert idx not in selected
        selected.add(idx)
        block = BLOCKS[idx]
        assert [int(x) for x in item["label_indices"]] == list(block)
        assert [[int(x) for x in e] for e in item["labels"]] == [
            list(EDGES[i]) for i in block
        ]
        assert [int(x) for x in item["type_union_2_3_4"]] == list(
            block_signature(block)
        )
        assert {int(x) for x in item["doubled_supports"]} == doubled_groups(block)
    return selected


def block_adjacency(selected: set[int]) -> dict[tuple[int, int], int]:
    result: dict[tuple[int, int], int] = defaultdict(int)
    for z in selected:
        for i, j in itertools.combinations(BLOCKS[z], 2):
            result[(i, j)] += 1
    return result


def check_block_witness(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    selected = parse_blocks(payload)
    label_degrees = Counter(i for z in selected for i in BLOCKS[z])
    pair_loads = block_adjacency(selected)
    support_occupancies = Counter(
        g for z in selected for g in doubled_groups(BLOCKS[z])
    )
    local_values = []
    for p in range(84):
        value = 0
        for (i, j), load in pair_loads.items():
            if p not in (i, j):
                continue
            q = j if i == p else i
            r = relation(p, q)
            value += load * (2 if r == 2 else 1 if r == 1 else 0)
        local_values.append(value)
    relation_counts = Counter()
    for (i, j), load in pair_loads.items():
        relation_counts[relation(i, j)] += load
    occupancy_profiles = []
    for g in range(7):
        counts = Counter()
        for z in selected:
            endpoints = sum((EDGES[i] for i in BLOCKS[z]), ())
            counts[sum(group(v) == g for v in endpoints)] += 1
        occupancy_profiles.append([counts[k] for k in range(3)])
    passed = (
        len(selected) == 140
        and set(label_degrees.values()) == {5}
        and len(label_degrees) == 84
        and max(pair_loads.values(), default=0) <= 1
        and [support_occupancies[g] for g in range(7)] == [12] * 7
        and local_values == [2] * 84
        and occupancy_profiles == [[32, 96, 12]] * 7
        and [relation_counts[k] for k in (2, 1, 0)]
        == [int(x) for x in payload["relation_counts_union_2_3_4"]]
    )
    return {
        "passed": passed,
        "path": path.name,
        "selected_blocks": len(selected),
        "label_degree_census": dict(sorted(Counter(label_degrees.values()).items())),
        "max_pair_load": max(pair_loads.values(), default=0),
        "used_disjoint_pairs": len(pair_loads),
        "support_occupancies": [support_occupancies[g] for g in range(7)],
        "occupancy_n0_n1_n2": occupancy_profiles,
        "local_dichotomy_census": dict(sorted(Counter(local_values).items())),
        "relation_counts_union_2_3_4": [relation_counts[k] for k in (2, 1, 0)],
    }


def parse_transitions(payload: dict[str, object]) -> set[int]:
    records = payload["selected_transitions"]
    assert isinstance(records, list)
    selected = set()
    for item in records:
        idx = int(item["index"])
        assert 0 <= idx < len(TRANSITIONS) and idx not in selected
        selected.add(idx)
        s, p, q = TRANSITIONS[idx]
        assert int(item["common_base_vertex"]) == s
        assert [int(x) for x in item["label_indices"]] == [p, q]
        assert [[int(x) for x in e] for e in item["labels"]] == [
            list(EDGES[p]),
            list(EDGES[q]),
        ]
    return selected


def check_strong_witness(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    blocks = parse_blocks(payload)
    transitions = parse_transitions(payload)
    block_check = check_block_witness(path)
    pair_loads = block_adjacency(blocks)
    transition_degree = Counter()
    transition_edges = set()
    for tid in transitions:
        s, p, q = TRANSITIONS[tid]
        transition_degree[(s, p)] += 1
        transition_degree[(s, q)] += 1
        transition_edges.add((min(p, q), max(p, q)))
    profile_failures = []
    for p, edge in enumerate(EDGES):
        neighbors = {
            q
            for (i, j), load in pair_loads.items()
            if load and p in (i, j)
            for q in [j if i == p else i]
        }
        neighbors |= {
            q
            for i, j in transition_edges
            if p in (i, j)
            for q in [j if i == p else i]
        }
        for s in VERTICES:
            lhs = sum(s in EDGES[q] for q in neighbors)
            rhs = 2 - int(s in edge) - int(conjugate(s) in edge)
            if lhs != rhs:
                profile_failures.append([p, s, lhs, rhs])
    triangle_violations = 0
    for triple in itertools.combinations(VERTICES, 3):
        if len({group(v) for v in triple}) < 3:
            continue
        hs = [
            EDGE_ID[canonical_edge(a, b)]
            for a, b in itertools.combinations(triple, 2)
        ]
        if all(tuple(sorted(pair)) in transition_edges for pair in itertools.combinations(hs, 2)):
            triangle_violations += 1
    expected_degree_keys = {
        (s, p) for p, edge in enumerate(EDGES) for s in edge
    }
    passed = (
        block_check["passed"]
        and len(transitions) == 84
        and set(transition_degree) == expected_degree_keys
        and set(transition_degree.values()) == {1}
        and not profile_failures
        and triangle_violations == 0
    )
    return {
        "passed": passed,
        "path": path.name,
        "block_check": block_check,
        "selected_transitions": len(transitions),
        "transition_degree_census": dict(
            sorted(Counter(transition_degree.values()).items())
        ),
        "endpoint_profile_failures": profile_failures[:10],
        "endpoint_profile_failure_count": len(profile_failures),
        "transition_triangle_violations": triangle_violations,
    }


def check_fractional() -> dict[str, object]:
    weights = {
        (0, 0, 3): Fraction(1, 120),
        (0, 1, 2): Fraction(1, 240),
    }
    z = [weights.get(block_signature(block), Fraction()) for block in BLOCKS]
    t = Fraction(1, 10)
    label_values = [
        sum((z[k] for k, block in enumerate(BLOCKS) if p in block), Fraction())
        for p in range(84)
    ]
    support_values = [
        sum(
            (z[k] for k, block in enumerate(BLOCKS) if g in doubled_groups(block)),
            Fraction(),
        )
        for g in range(7)
    ]
    pair_values = {}
    for i, j in itertools.combinations(range(84), 2):
        if not set(EDGES[i]).isdisjoint(EDGES[j]):
            continue
        pair_values[(i, j)] = sum(
            (
                z[k]
                for k, block in enumerate(BLOCKS)
                if i in block and j in block
            ),
            Fraction(),
        )
    local_values = []
    for p in range(84):
        local_values.append(
            sum(
                pair_values[tuple(sorted((p, q)))]
                * (2 if relation(p, q) == 2 else 1 if relation(p, q) == 1 else 0)
                for q in range(84)
                if q != p and tuple(sorted((p, q))) in pair_values
            )
        )
    profile_residuals = []
    for p, edge in enumerate(EDGES):
        for s in VERTICES:
            block_part = sum(
                load
                for (i, j), load in pair_values.items()
                if p in (i, j) and s in EDGES[j if i == p else i]
            )
            transition_part = sum(
                t
                for _common, i, j in TRANSITIONS
                if (i == p and s in EDGES[j]) or (j == p and s in EDGES[i])
            )
            rhs = Fraction(2 - int(s in edge) - int(conjugate(s) in edge))
            profile_residuals.append(block_part + transition_part - rhs)
    passed = (
        set(label_values) == {Fraction(5)}
        and set(support_values) == {Fraction(12)}
        and max(pair_values.values()) == Fraction(1, 5)
        and set(local_values) == {Fraction(2)}
        and set(profile_residuals) == {Fraction(0)}
    )
    return {
        "passed": passed,
        "label_values": sorted({str(x) for x in label_values}),
        "support_values": sorted({str(x) for x in support_values}),
        "pair_value_census": dict(sorted(Counter(str(x) for x in pair_values.values()).items())),
        "local_values": sorted({str(x) for x in local_values}),
        "profile_residuals": sorted({str(x) for x in profile_residuals}),
        "transition_triangle_lhs": str(3 * t),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--block", default="block-witness.json")
    parser.add_argument("--strong", default="transition-block-witness.json")
    parser.add_argument("--output", default="exact-check-result.json")
    args = parser.parse_args()
    census = check_census()
    block = check_block_witness(HERE / args.block)
    strong_path = HERE / args.strong
    strong = check_strong_witness(strong_path) if strong_path.exists() else {
        "passed": None,
        "status": "NOT_AVAILABLE",
    }
    fractional = check_fractional()
    result = {
        "format": "wave64-rooted-transition-design-exact-check-v1",
        "claim_label": "DERIVED",
        "passed": census["passed"] and block["passed"] and fractional["passed"],
        "census": census,
        "block_witness": block,
        "strong_witness": strong,
        "fractional_control": fractional,
        "endpoint_status": "UNKNOWN",
        "limitations": [
            "Discovery cannot promote its own work to VERIFIED.",
            "The integral witness satisfies only the block master.",
            "No integral witness for the stronger master is currently available.",
            "No solver nonhit is treated as nonexistence evidence.",
            "The full residual codegree constraints are not encoded here.",
        ],
    }
    (HERE / args.output).write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
