#!/usr/bin/env python3
"""Exact checks for the Wave 33 rooted construction lane.

The module uses only the Python standard library.  It reconstructs the
labeled Wave 32 support, verifies the exact strongly-regular block
equations, and checks explicit bounded-relaxation certificates.  It does not
call a solver and cannot turn a missing certificate into nonexistence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

FROZEN = {
    "AGENTS.md":
        "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3",
    "CONJECTURE.md":
        "7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58",
    "STRUCTURE.md":
        "45640fecaa5834b24063c682c7edd0898f2746253a7708a2c70c3610e4bcb99a",
    "agents/2026-07-24-wave32-rooted-proof.md":
        "04990231e3b42cded363e39ffea771556e52ec66fe03a97164ae99f40ddbefe0",
    "verification/wave32-rooted-vector/audit.md":
        "36d83232d82e30205e0aefa30aedff0a517de1edb0adbaa54575ea68d04ce1a5",
    "verification/wave32-rooted-vector/independent-results.json":
        "4ed239e997e4485abdab4e26a2e28e2a981b6fff069c4d926ccff3d2241dbe6f",
    "verification/wave32-rooted-vector/artifact-manifest.sha256":
        "2607c3000944e6d31ab5491a7d959ae4f97f05ac3e0d754baaf2830efcd085df",
    "verification/wave33-continuation-protocol.md":
        "b98b6bb8228b54b67cd949ee1bf6eb05ebd6ebe74f1cbc9e49b041a55e2d2fe6",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_frozen_inputs() -> dict[str, str]:
    observed = {name: sha256(REPO / name) for name in FROZEN}
    if observed != FROZEN:
        raise AssertionError(f"frozen input drift: {observed}")
    return observed


def canonical_json(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True)
        .encode("utf-8")
        + b"\n"
    )


def cross_edge(p: int, r: int) -> bool:
    return ((p + 1) & (r + 1)).bit_count() % 2 == 1


def build_model() -> dict[str, object]:
    support = [f"P{i}" for i in range(7)] + [f"R{i}" for i in range(7)]
    active: list[str] = []
    endpoints: dict[str, tuple[int, int]] = {}
    active_kind: dict[str, str] = {}

    for p in range(7):
        for r in range(7):
            if cross_edge(p, r):
                name = f"E_{p}_{r}"
                active.append(name)
                endpoints[name] = (p, 7 + r)
                active_kind[name] = "E"
    for p in range(7):
        for r in range(7):
            if not cross_edge(p, r):
                for copy in range(2):
                    name = f"N_{p}_{r}_{copy}"
                    active.append(name)
                    endpoints[name] = (p, 7 + r)
                    active_kind[name] = "N"

    zeros = [f"Z{i}" for i in range(15)]
    outside = active + zeros
    if len(active) != 70 or len(outside) != 85:
        raise AssertionError("outside label census failed")

    a_support = [[0] * 14 for _ in range(14)]
    for p in range(7):
        for r in range(7):
            if cross_edge(p, r):
                a_support[p][7 + r] = 1
                a_support[7 + r][p] = 1

    b = [[0] * 85 for _ in range(14)]
    for column, name in enumerate(active):
        for endpoint in endpoints[name]:
            b[endpoint][column] = 1

    outside_index = {name: i for i, name in enumerate(outside)}
    active_index = {name: i for i, name in enumerate(active)}
    support_index = {name: i for i, name in enumerate(support)}
    support_groups = [
        [active_index[name] for name in active if support_vertex in endpoints[name]]
        for support_vertex in range(14)
    ]
    if [len(group) for group in support_groups] != [10] * 14:
        raise AssertionError("support-outside group census failed")

    return {
        "support": support,
        "active": active,
        "zeros": zeros,
        "outside": outside,
        "endpoints": endpoints,
        "active_kind": active_kind,
        "a_support": a_support,
        "b": b,
        "outside_index": outside_index,
        "active_index": active_index,
        "support_index": support_index,
        "support_groups": support_groups,
    }


def matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    if len(left[0]) != len(right):
        raise AssertionError("matrix dimension mismatch")
    columns = list(zip(*right))
    return [
        [sum(a * b for a, b in zip(row, column)) for column in columns]
        for row in left
    ]


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    return [list(column) for column in zip(*matrix)]


def support_block_checks(model: dict[str, object]) -> dict[str, object]:
    a_support = model["a_support"]
    b = model["b"]
    left = matmul(a_support, a_support)
    bbt = matmul(b, transpose(b))
    residual = []
    for i in range(14):
        row = []
        for j in range(14):
            observed = left[i][j] + bbt[i][j]
            expected = 12 * (i == j) - a_support[i][j] + 2
            row.append(observed - expected)
        residual.append(row)
    if any(value for row in residual for value in row):
        raise AssertionError("fixed support-support SRG block failed")
    support_degrees = [
        sum(a_support[i]) + sum(b[i])
        for i in range(14)
    ]
    if support_degrees != [14] * 14:
        raise AssertionError("fixed support degrees failed")
    return {
        "support_degrees": support_degrees,
        "cross_edge_count": sum(map(sum, a_support)) // 2,
        "outside_type_counts": {"E": 28, "N": 42, "Z": 15},
        "support_support_block": "PASS",
    }


def support_outside_rhs(model: dict[str, object]) -> list[list[int]]:
    a_support = model["a_support"]
    b = model["b"]
    asb = matmul(a_support, b)
    return [
        [2 - b[i][j] - asb[i][j] for j in range(85)]
        for i in range(14)
    ]


def derive_linear_consequences(model: dict[str, object]) -> dict[str, object]:
    rhs = support_outside_rhs(model)
    active = model["active"]
    b = model["b"]
    profiles = Counter(
        tuple(rhs[s][column] for s in range(14))
        for column in range(70)
    )
    column_sums = [sum(rhs[s][column] for s in range(14)) for column in range(85)]
    if column_sums[:70] != [18] * 70 or column_sums[70:] != [28] * 15:
        raise AssertionError("support-outside RHS column sums failed")

    # Every active outside neighbor contributes two support incidences to a
    # column sum of B D.  Thus an active vertex has nine active neighbors.
    active_active_degree = [value // 2 for value in column_sums[:70]]
    if active_active_degree != [9] * 70:
        raise AssertionError("active-active degree deduction failed")

    outside_support_degrees = [sum(b[s][j] for s in range(14)) for j in range(85)]
    total_outside_degrees = [14 - value for value in outside_support_degrees]
    active_zero_degree = [
        total_outside_degrees[j] - active_active_degree[j]
        for j in range(70)
    ]
    if active_zero_degree != [3] * 70:
        raise AssertionError("active-zero degree deduction failed")

    # For a Z column, every support group must contribute two neighbors.
    zero_support_group_targets = [
        tuple(rhs[s][column] for s in range(14))
        for column in range(70, 85)
    ]
    if zero_support_group_targets != [(2,) * 14] * 15:
        raise AssertionError("Z support-balance deduction failed")

    return {
        "rhs_active_profile_count": len(profiles),
        "rhs_active_profile_multiplicities":
            sorted(profiles.values()),
        "active_active_degree": 9,
        "active_zero_degree": 3,
        "zero_degree": 14,
        "zero_zero_edges": 0,
        "zero_support_group_target": 2,
        "active_graph_edge_count": 70 * 9 // 2,
        "active_zero_edge_count": 70 * 3,
        "outside_edge_count": (70 * 12 + 15 * 14) // 2,
        "full_graph_edge_count": 99 * 14 // 2,
        "identity": "A_S B + B D = -B + 2J",
    }


def cyclic_sts15() -> list[tuple[int, int, int]]:
    bases = ((0, 1, 4), (0, 2, 8), (0, 5, 10))
    blocks = {
        tuple(sorted((value + shift) % 15 for value in base))
        for base in bases
        for shift in range(15)
    }
    result = sorted(blocks)
    if len(result) != 35:
        raise AssertionError("cyclic STS(15) block count failed")
    pair_counts = Counter(
        pair
        for block in result
        for pair in combinations(block, 2)
    )
    if set(pair_counts.values()) != {1} or len(pair_counts) != 105:
        raise AssertionError("cyclic STS(15) pair census failed")
    return result


def simple_twofold_triple_design() -> list[tuple[int, int, int]]:
    first = cyclic_sts15()
    permutation = (5, 4, 0, 9, 12, 3, 13, 6, 1, 2, 14, 7, 8, 10, 11)
    second = sorted(
        tuple(sorted(permutation[value] for value in block))
        for block in first
    )
    if set(first) & set(second):
        raise AssertionError("the two STS(15) copies are not block-disjoint")
    result = sorted(first + second)
    pair_counts = Counter(
        pair
        for block in result
        for pair in combinations(block, 2)
    )
    point_counts = Counter(value for block in result for value in block)
    if not (
        len(result) == len(set(result)) == 70
        and set(pair_counts.values()) == {2}
        and len(pair_counts) == 105
        and point_counts == Counter({value: 14 for value in range(15)})
    ):
        raise AssertionError("simple 2-(15,3,2) design failed")
    return result


def partial_design_certificate(
    chosen_blocks: list[int] | None = None,
    discovery: dict[str, object] | None = None,
) -> dict[str, object]:
    """Return an explicit labeled active-to-Z partial object.

    ``chosen_blocks[active_index]`` selects one of the 70 blocks in the
    frozen simple twofold triple design.  A permutation is required, so the
    Z-Z common-neighbor equations and all active/Z degrees are exact.
    """
    model = build_model()
    blocks = simple_twofold_triple_design()
    if chosen_blocks is None:
        chosen_blocks = list(range(70))
    if sorted(chosen_blocks) != list(range(70)):
        raise AssertionError("partial-design assignment must be a permutation")
    return {
        "schema_version": 1,
        "claim_label": "CANDIDATE",
        "evidence_kind": "EXPLICIT_HOSTILE_PARTIAL_OBJECT",
        "scope": (
            "LABELED_ACTIVE_TO_Z_LAYER_WITH_EXACT_DEGREES_AND_Z_ZERO_BLOCK"
        ),
        "active_to_zero_triples": [
            {
                "active": name,
                "zeros": [f"Z{zero}" for zero in blocks[chosen_blocks[index]]],
            }
            for index, name in enumerate(model["active"])
        ],
        "design_construction": {
            "first_sts_bases_mod_15": [[0, 1, 4], [0, 2, 8], [0, 5, 10]],
            "second_sts_point_permutation": [
                5, 4, 0, 9, 12, 3, 13, 6, 1, 2, 14, 7, 8, 10, 11
            ],
        },
        "restrictions": [
            (
                "The active-to-Z triples are restricted to one explicit "
                "simple 2-(15,3,2) design; this is not without loss of "
                "generality."
            ),
            (
                "Only the active-to-Z layer is supplied; no active-active "
                "edges are supplied."
            ),
        ],
        "limitations": [
            (
                "Support-group balance may fail and is measured rather than "
                "assumed."
            ),
            "The support-active block and active-active SRG block are absent.",
            (
                "The projector/lattice/tensor/Schur rooted endpoint layer is "
                "absent."
            ),
            "This is not a graph-extension certificate.",
        ],
        "discovery": discovery or {
            "method": "canonical block-to-active ordering",
            "status_is_certificate": False,
        },
    }


def verify_partial_design_certificate(
    certificate: dict[str, object],
) -> dict[str, object]:
    """Independently check the explicit active-to-Z partial object."""
    model = build_model()
    active = model["active"]
    zeros = model["zeros"]
    active_index = model["active_index"]
    support_groups = model["support_groups"]

    if certificate.get("schema_version") != 1:
        raise AssertionError("unsupported partial-certificate schema")
    if certificate.get("claim_label") != "CANDIDATE":
        raise AssertionError("partial certificate must remain CANDIDATE")
    records = certificate.get("active_to_zero_triples")
    if not isinstance(records, list) or len(records) != 70:
        raise AssertionError("partial certificate must contain 70 records")

    assigned: list[tuple[int, int, int] | None] = [None] * 70
    for record in records:
        if not isinstance(record, dict) or set(record) != {"active", "zeros"}:
            raise AssertionError(f"malformed active-to-Z record: {record}")
        name = record["active"]
        raw_zeros = record["zeros"]
        if name not in active_index or assigned[active_index[name]] is not None:
            raise AssertionError(f"unknown or duplicate active label: {name}")
        if (
            not isinstance(raw_zeros, list)
            or len(raw_zeros) != 3
            or len(set(raw_zeros)) != 3
            or any(name not in zeros for name in raw_zeros)
        ):
            raise AssertionError(f"invalid Z triple for {name}: {raw_zeros}")
        assigned[active_index[name]] = tuple(sorted(
            int(zero_name[1:]) for zero_name in raw_zeros
        ))
    if any(block is None for block in assigned):
        raise AssertionError("active label set is incomplete")

    triples = [block for block in assigned if block is not None]
    frozen_design = simple_twofold_triple_design()
    if sorted(triples) != frozen_design:
        raise AssertionError("explicit simple twofold triple design drifted")

    point_counts = Counter(zero for block in triples for zero in block)
    pair_counts = Counter(
        pair for block in triples for pair in combinations(block, 2)
    )
    if point_counts != Counter({zero: 14 for zero in range(15)}):
        raise AssertionError("Z-degree census failed")
    if (
        len(pair_counts) != 105
        or set(pair_counts.values()) != {2}
    ):
        raise AssertionError("Z-Z common-neighbor census failed")

    group_counts = [
        [
            sum(zero in triples[vertex] for vertex in group)
            for zero in range(15)
        ]
        for group in support_groups
    ]
    defects = [
        count - 2
        for row in group_counts
        for count in row
    ]
    violation_count = sum(defect != 0 for defect in defects)
    exact_groups = sum(row == [2] * 15 for row in group_counts)
    return {
        "classification": "EXACT_HOSTILE_PARTIAL_OBJECT_NOT_A_GRAPH",
        "claim_label": "FINITE_COMPUTATIONAL_EVIDENCE",
        "active_count": 70,
        "zero_count": 15,
        "active_zero_edge_count": 210,
        "active_zero_degrees": {"3": 70},
        "zero_degrees": {"14": 15},
        "zero_zero_pair_count": 105,
        "zero_zero_common_neighbor_histogram": {"2": 105},
        "simple_twofold_triple_design": "PASS",
        "support_group_zero_count_histogram": dict(sorted(Counter(
            count for row in group_counts for count in row
        ).items())),
        "support_group_balance_violation_count": violation_count,
        "support_group_balance_exact_group_count": exact_groups,
        "support_group_balance_squared_defect": sum(
            defect * defect for defect in defects
        ),
        "support_group_balance_pass": violation_count == 0,
        "restrictions": certificate["restrictions"],
        "limitations": certificate["limitations"],
    }


def adjacency_from_certificate(
    model: dict[str, object],
    certificate: dict[str, object],
) -> tuple[list[set[int]], dict[str, object]]:
    support = model["support"]
    active = model["active"]
    zeros = model["zeros"]
    outside = model["outside"]
    a_support = model["a_support"]
    b = model["b"]
    active_index = model["active_index"]
    outside_index = model["outside_index"]

    adjacency = [set() for _ in range(99)]

    def connect(left: int, right: int) -> None:
        if left == right or right in adjacency[left]:
            raise AssertionError(f"invalid duplicate/loop edge: {left}, {right}")
        adjacency[left].add(right)
        adjacency[right].add(left)

    for i in range(14):
        for j in range(i + 1, 14):
            if a_support[i][j]:
                connect(i, j)
    for s in range(14):
        for column in range(85):
            if b[s][column]:
                connect(s, 14 + column)

    active_edge_set: set[tuple[int, int]] = set()
    for raw in certificate["active_edges"]:
        if not isinstance(raw, list) or len(raw) != 2:
            raise AssertionError(f"invalid active edge record: {raw}")
        left_name, right_name = raw
        if left_name not in active_index or right_name not in active_index:
            raise AssertionError(f"unknown active label: {raw}")
        left, right = sorted((active_index[left_name], active_index[right_name]))
        if left == right or (left, right) in active_edge_set:
            raise AssertionError(f"duplicate/loop active edge: {raw}")
        active_edge_set.add((left, right))
        connect(14 + left, 14 + right)

    zero_blocks = certificate["zero_blocks"]
    if set(zero_blocks) != set(zeros):
        raise AssertionError("zero-block label set failed")
    assigned_triples: dict[str, list[int]] = {name: [] for name in active}
    for zero_name in zeros:
        block = zero_blocks[zero_name]
        if len(block) != 14 or len(set(block)) != 14:
            raise AssertionError(f"invalid zero block size: {zero_name}")
        for active_name in block:
            if active_name not in active_index:
                raise AssertionError(f"unknown active block label: {active_name}")
            assigned_triples[active_name].append(int(zero_name[1:]))
            connect(
                14 + active_index[active_name],
                14 + outside_index[zero_name],
            )

    triples = [tuple(sorted(assigned_triples[name])) for name in active]
    if any(len(block) != 3 for block in triples):
        raise AssertionError("active-to-zero degree is not three")
    if len(set(triples)) != 70:
        raise AssertionError("zero-neighborhood triples are not simple")
    if sorted(triples) != simple_twofold_triple_design():
        raise AssertionError("zero-neighborhood triple design drifted")

    metadata = {
        "active_edge_count": len(active_edge_set),
        "active_zero_edge_count": sum(len(zero_blocks[name]) for name in zeros),
        "zero_neighborhood_triples": [list(block) for block in triples],
    }
    return adjacency, metadata


def classify_pair(
    model: dict[str, object],
    left: int,
    right: int,
) -> str:
    if left == right:
        return "diagonal"
    if right < left:
        left, right = right, left
    if right < 14:
        return "support_support"
    if left < 14:
        outside_position = right - 14
        return "support_active" if outside_position < 70 else "support_zero"
    left_out = left - 14
    right_out = right - 14
    if right_out < 70:
        return "active_active"
    if left_out < 70:
        return "active_zero"
    return "zero_zero"


def verify_relaxation_certificate(
    certificate: dict[str, object],
) -> dict[str, object]:
    model = build_model()
    support_block = support_block_checks(model)
    consequences = derive_linear_consequences(model)
    adjacency, metadata = adjacency_from_certificate(model, certificate)
    degrees = [len(neighbors) for neighbors in adjacency]
    if degrees != [14] * 99:
        raise AssertionError(f"full degree condition failed: {Counter(degrees)}")

    pair_results: dict[str, dict[str, object]] = {}
    raw: dict[str, list[tuple[bool, int, int]]] = {}
    for left in range(99):
        for right in range(left, 99):
            category = classify_pair(model, left, right)
            observed = (
                degrees[left]
                if left == right
                else len(adjacency[left] & adjacency[right])
            )
            adjacent = right in adjacency[left] if left != right else False
            expected = 14 if left == right else (1 if adjacent else 2)
            raw.setdefault(category, []).append((adjacent, observed, expected))

    for category, rows in raw.items():
        violations = [row for row in rows if row[1] != row[2]]
        pair_results[category] = {
            "pair_count": len(rows),
            "violation_count": len(violations),
            "edge_common_count_histogram": dict(sorted(Counter(
                observed for adjacent, observed, _ in rows if adjacent
            ).items())),
            "nonedge_common_count_histogram": dict(sorted(Counter(
                observed for adjacent, observed, _ in rows if not adjacent
            ).items())),
        }

    enforced = set(certificate["enforced_pair_categories"])
    permitted = {
        "support_support",
        "support_active",
        "support_zero",
        "active_zero",
        "zero_zero",
        "diagonal",
    }
    if not enforced <= permitted or "active_active" in enforced:
        raise AssertionError(f"invalid enforced category declaration: {enforced}")
    if any(pair_results[category]["violation_count"] for category in enforced):
        raise AssertionError(f"declared enforced category failed: {pair_results}")

    # The signed Wave 32 support vector remains an exact -4 eigenvector.
    signed = [1] * 7 + [-1] * 7 + [0] * 85
    image = [
        sum(signed[neighbor] for neighbor in adjacency[vertex])
        for vertex in range(99)
    ]
    if image != [-4 * value for value in signed]:
        raise AssertionError("signed support eigenvector failed")

    visited = {0}
    frontier = [0]
    while frontier:
        vertex = frontier.pop()
        for neighbor in adjacency[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                frontier.append(neighbor)
    if len(visited) != 99:
        raise AssertionError("relaxation graph is disconnected")

    full_violation_count = sum(
        result["violation_count"] for result in pair_results.values()
    )
    if full_violation_count == 0:
        classification = "COMPLETE_SRG_WITNESS"
    else:
        classification = "FINITE_RELAXATION_WITNESS_NOT_A_TARGET_GRAPH"

    return {
        "classification": classification,
        "claim_label": "CANDIDATE" if full_violation_count == 0
            else "FINITE_COMPUTATIONAL_EVIDENCE",
        "support_block": support_block,
        "linear_consequences": consequences,
        "certificate_metadata": metadata,
        "full_degree_histogram": {"14": 99},
        "full_edge_count": sum(degrees) // 2,
        "connected": True,
        "signed_support_eigenvalue": -4,
        "pair_categories": pair_results,
        "full_srg_violation_count": full_violation_count,
        "enforced_pair_categories": sorted(enforced),
        "omitted_pair_categories": sorted(
            set(pair_results) - enforced
        ),
        "restrictions": certificate["restrictions"],
        "limitations": certificate["limitations"],
    }


def base_results() -> dict[str, object]:
    model = build_model()
    return {
        "schema_version": 1,
        "claim_label": "UNKNOWN",
        "frozen_inputs": verify_frozen_inputs(),
        "fixed_support": support_block_checks(model),
        "linear_consequences": derive_linear_consequences(model),
        "simple_twofold_triple_design": {
            "parameters": "2-(15,3,2)",
            "block_count": len(simple_twofold_triple_design()),
            "simple": True,
        },
        "status_wall": {
            "complete_graph_extension": "UNKNOWN",
            "complete_domain_UNSAT_certificate": "NONE",
            "full_rooted_endpoint": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path)
    parser.add_argument("--partial-certificate", type=Path)
    parser.add_argument("--emit-partial-certificate", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.emit_partial_certificate:
        args.emit_partial_certificate.write_bytes(
            canonical_json(partial_design_certificate())
        )

    results = base_results()
    if args.partial_certificate:
        partial = json.loads(
            args.partial_certificate.read_text(encoding="utf-8")
        )
        results["hostile_partial_object"] = (
            verify_partial_design_certificate(partial)
        )
        results["claim_label"] = "CANDIDATE"
    if args.certificate:
        certificate = json.loads(args.certificate.read_text(encoding="utf-8"))
        results["bounded_relaxation"] = verify_relaxation_certificate(certificate)
        if results["bounded_relaxation"]["classification"] == "COMPLETE_SRG_WITNESS":
            results["claim_label"] = "CANDIDATE"
        else:
            results["claim_label"] = "CANDIDATE"
    encoded = canonical_json(results)
    if args.output:
        args.output.write_bytes(encoded)
    else:
        print(encoded.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
