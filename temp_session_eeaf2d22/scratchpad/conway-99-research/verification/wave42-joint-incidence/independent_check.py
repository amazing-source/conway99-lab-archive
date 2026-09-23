#!/usr/bin/env python3
"""Clean-room verifier for the Wave 42 canonical joint-incidence reduction.

This module uses only the Python standard library and the frozen Wave 41
independent result.  It never imports Wave 42 discovery code.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections import Counter, deque
from pathlib import Path
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = ROOT / "verification" / "wave41-allquotient-lifts" / "independent-results.json"
EXPECTED_INPUT_SHA256 = "062785a47ddb8f85ddec10a76a663c262ec9c60c133b681be5228639b022260b"

# Generated independently before discovery comparison.  Entry i pairs the
# i-th lexicographic allowed pair in fibre 0 with this indexed allowed pair in
# fibre 1.
TWO_FIBRE_PERMUTATION = (
    44, 40, 54, 7, 35, 27, 42, 33, 48, 37, 58, 36, 52, 47, 49,
    16, 41, 23, 18, 29, 22, 13, 9, 55, 53, 50, 20, 38, 59, 57,
    15, 46, 32, 45, 5, 4, 34, 39, 0, 11, 3, 19, 56, 30, 8,
    10, 28, 25, 21, 2, 17, 24, 12, 6, 26, 1, 31, 14, 51, 43,
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def digest_json(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_frozen_input(path: Path = INPUT) -> dict:
    actual = sha256_file(path)
    if actual != EXPECTED_INPUT_SHA256:
        raise ValueError(f"frozen input hash mismatch: {actual}")
    return json.loads(path.read_text(encoding="utf-8"))


def rank_mod(matrix: Sequence[Sequence[int]], prime: int) -> int:
    a = [[value % prime for value in row] for row in matrix]
    rows = len(a)
    cols = len(a[0]) if rows else 0
    rank = 0
    for col in range(cols):
        pivot = next((r for r in range(rank, rows) if a[r][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        inv = pow(a[rank][col], -1, prime)
        a[rank] = [(inv * x) % prime for x in a[rank]]
        for r in range(rows):
            if r != rank and a[r][col]:
                factor = a[r][col]
                a[r] = [(x - factor * y) % prime for x, y in zip(a[r], a[rank])]
        rank += 1
        if rank == rows:
            break
    return rank


def witness_record(data: dict) -> dict:
    record = data["canonical_exhaustive_lift_census"][
        "canonical_first_witness_by_core_rank"
    ]["32"]
    if record["mask"] != 51739:
        raise ValueError("selected Wave 41 witness is not mask 51739")
    expected_bits = [(record["mask"] >> i) & 1 for i in range(18)]
    if record["mask_bits_vertex_0_first"] != expected_bits:
        raise ValueError("mask bits do not encode mask 51739")
    if record["rank_F7_3I_minus_A_core"] != 32 or record["rank_F7_K39"] != 33:
        raise ValueError("selected Wave 41 witness has the wrong recorded ranks")
    return record


def build_adjacency(edges: Iterable[Sequence[int]], order: int = 36) -> list[list[int]]:
    adjacency = [[0] * order for _ in range(order)]
    seen: set[tuple[int, int]] = set()
    for pair in edges:
        if len(pair) != 2:
            raise ValueError("an edge does not have two endpoints")
        u, v = map(int, pair)
        if not (0 <= u < v < order):
            raise ValueError(f"invalid canonical edge {(u, v)}")
        if (u, v) in seen:
            raise ValueError(f"duplicate canonical edge {(u, v)}")
        seen.add((u, v))
        adjacency[u][v] = adjacency[v][u] = 1
    return adjacency


def connected_components(adjacency: Sequence[Sequence[int]]) -> list[list[int]]:
    unseen = set(range(len(adjacency)))
    components: list[list[int]] = []
    while unseen:
        start = min(unseen)
        unseen.remove(start)
        queue = deque([start])
        component: list[int] = []
        while queue:
            u = queue.popleft()
            component.append(u)
            for v, is_edge in enumerate(adjacency[u]):
                if is_edge and v in unseen:
                    unseen.remove(v)
                    queue.append(v)
        components.append(sorted(component))
    return sorted(components, key=lambda c: (len(c), c))


def reconstruct_core(data: dict, edges_override: Iterable[Sequence[int]] | None = None) -> dict:
    record = witness_record(data)
    edges = list(record["core_edges"] if edges_override is None else edges_override)
    adjacency = build_adjacency(edges)
    degree_set = sorted({sum(row) for row in adjacency})
    if degree_set != [3]:
        raise ValueError(f"core is not cubic: degree set {degree_set}")
    triangle_count = sum(
        adjacency[u][v] and adjacency[u][w] and adjacency[v][w]
        for u in range(36)
        for v in range(u + 1, 36)
        for w in range(v + 1, 36)
    )
    if triangle_count:
        raise ValueError(f"core is not triangle-free: {triangle_count} triangles")
    if len(edges) != 54:
        raise ValueError(f"core edge count is {len(edges)}, not 54")

    components = connected_components(adjacency)
    if [len(c) for c in components] != [12, 24]:
        raise ValueError(f"wrong component orders: {[len(c) for c in components]}")
    balances = [[sum(v // 12 == fibre for v in c) for fibre in range(3)] for c in components]
    if balances != [[4, 4, 4], [8, 8, 8]]:
        raise ValueError(f"components are not fibre-balanced: {balances}")

    # Reconstruct the triangle T plus its three 12-vertex fibres.
    a39 = [[0] * 39 for _ in range(39)]
    for i in range(3):
        for j in range(i + 1, 3):
            a39[i][j] = a39[j][i] = 1
    for fibre in range(3):
        for u in range(12 * fibre, 12 * fibre + 12):
            a39[fibre][u + 3] = a39[u + 3][fibre] = 1
    for u, v in edges:
        a39[u + 3][v + 3] = a39[v + 3][u + 3] = 1
    k39 = [
        [
            (1 - (i == j) - 2 * a39[i][j]) % 7
            for j in range(39)
        ]
        for i in range(39)
    ]
    rank_k39 = rank_mod(k39, 7)
    core_matrix = [
        [(3 * (i == j) - adjacency[i][j]) % 7 for j in range(36)]
        for i in range(36)
    ]
    rank_core = rank_mod(core_matrix, 7)
    if (rank_core, rank_k39) != (32, 33):
        raise ValueError(f"reconstructed ranks are {(rank_core, rank_k39)}, not (32,33)")

    return {
        "adjacency": adjacency,
        "components": components,
        "component_fibre_balances": balances,
        "core_edge_count": len(edges),
        "core_edges_digest": digest_json(edges),
        "core_triangle_count": triangle_count,
        "rank_F7_3I_minus_A_core": rank_core,
        "rank_F7_K39": rank_k39,
    }


def derive_gram(adjacency: Sequence[Sequence[int]]) -> list[list[int]]:
    """Derive Q=B B^T using the SRG common-neighbour equations."""
    q = [[0] * 36 for _ in range(36)]
    for u in range(36):
        q[u][u] = 14 - 1 - sum(adjacency[u])  # outside degree = 10
        for v in range(u + 1, 36):
            total_common = 1 if adjacency[u][v] else 2
            known_common = int(u // 12 == v // 12)
            known_common += sum(adjacency[u][z] * adjacency[v][z] for z in range(36))
            value = total_common - known_common
            if value < 0:
                raise ValueError(f"negative required concurrence at {(u, v)}")
            q[u][v] = q[v][u] = value
    if any(q[u][u] != 10 for u in range(36)):
        raise ValueError("Gram diagonal is not uniformly 10")
    if {sum(row) for row in q} != {60}:
        raise ValueError("Gram row sums are not uniformly 60")
    return q


def cauchy_component_check(q: Sequence[Sequence[int]], components: Sequence[Sequence[int]]) -> dict:
    summaries = []
    outside_columns = 60
    for component in components:
        order = len(component)
        incidence_sum = 10 * order
        square_sum = sum(q[u][v] for u in component for v in component)
        cauchy_floor = incidence_sum * incidence_sum // outside_columns
        if incidence_sum * incidence_sum % outside_columns:
            raise ValueError("unexpected nonintegral Cauchy average")
        if square_sum != cauchy_floor:
            raise ValueError("Cauchy is not at equality for a core component")
        forced_per_column = incidence_sum // outside_columns
        summaries.append(
            {
                "component_order": order,
                "sum_column_component_sizes": incidence_sum,
                "sum_squared_column_component_sizes": square_sum,
                "cauchy_floor": cauchy_floor,
                "forced_component_vertices_per_column": forced_per_column,
            }
        )
    if [x["forced_component_vertices_per_column"] for x in summaries] != [2, 4]:
        raise ValueError("component equality did not force the 2+4 split")
    return {"outside_columns": outside_columns, "components": summaries}


def fibre_pairs(q: Sequence[Sequence[int]]) -> list[list[tuple[int, int]]]:
    pairs: list[list[tuple[int, int]]] = []
    for fibre in range(3):
        vertices = range(12 * fibre, 12 * fibre + 12)
        current = [(u, v) for u, v in itertools.combinations(vertices, 2) if q[u][v] == 1]
        if len(current) != 60:
            raise ValueError(f"fibre {fibre} has {len(current)} allowed pairs, not 60")
        pairs.append(current)
    return pairs


def pair_inventory(
    pairs: Sequence[Sequence[tuple[int, int]]],
    small_component: set[int],
) -> dict:
    distributions = []
    for fibre_pairs_ in pairs:
        distribution = Counter(sum(v in small_component for v in pair) for pair in fibre_pairs_)
        if distribution != Counter({0: 24, 1: 32, 2: 4}):
            raise ValueError(f"unexpected component-pair inventory: {distribution}")
        distributions.append({str(k): distribution[k] for k in range(3)})

    # Every pair is used once.  Since every column has small-component total 2,
    # only (2,0,0) and (1,1,0) permutations occur.  The per-fibre inventory
    # solves their multiplicities uniquely.
    patterns = {
        "2,0,0": 4,
        "0,2,0": 4,
        "0,0,2": 4,
        "1,1,0": 16,
        "1,0,1": 16,
        "0,1,1": 16,
    }
    for fibre in range(3):
        count_two = sum(count for pattern, count in patterns.items() if int(pattern.split(",")[fibre]) == 2)
        count_one = sum(count for pattern, count in patterns.items() if int(pattern.split(",")[fibre]) == 1)
        count_zero = sum(count for pattern, count in patterns.items() if int(pattern.split(",")[fibre]) == 0)
        if (count_zero, count_one, count_two) != (24, 32, 4):
            raise ValueError("component-pattern solution does not reproduce pair inventory")
    return {
        "allowed_pair_count_per_fibre": [len(x) for x in pairs],
        "component_count_per_pair": distributions,
        "forced_column_component_patterns": patterns,
    }


def gram_supported(
    triple: Sequence[tuple[int, int]],
    q: Sequence[Sequence[int]],
) -> bool:
    for first, second in ((0, 1), (1, 2), (2, 0)):
        if any(q[u][v] < 1 for u in triple[first] for v in triple[second]):
            return False
    return True


def local_srg_feasible(
    triple: Sequence[tuple[int, int]],
    adjacency: Sequence[Sequence[int]],
) -> bool:
    selected = {v for pair in triple for v in pair}
    if len(selected) != 6:
        return False
    # If u is selected, u and the outside vertex are adjacent and can have at
    # most lambda=1 common core neighbour.  If u is unselected, they are
    # nonadjacent and can have at most mu=2 common core neighbours.
    for u in range(36):
        common_in_core = sum(adjacency[u][v] for v in selected)
        limit = 1 if u in selected else 2
        if common_in_core > limit:
            return False
    return True


def exhaustive_six_sets(
    pairs: Sequence[Sequence[tuple[int, int]]],
    q: Sequence[Sequence[int]],
    adjacency: Sequence[Sequence[int]],
    small_component: set[int],
) -> dict:
    total = supported = component_equal = locally_feasible = 0
    final_sets: list[list[int]] = []
    first_local_rejection: list[int] | None = None
    for triple in itertools.product(*pairs):
        total += 1
        if not gram_supported(triple, q):
            continue
        supported += 1
        flat = tuple(v for pair in triple for v in pair)
        if sum(v in small_component for v in flat) != 2:
            continue
        component_equal += 1
        if not local_srg_feasible(triple, adjacency):
            if first_local_rejection is None:
                first_local_rejection = list(flat)
            continue
        locally_feasible += 1
        final_sets.append(list(flat))
    counts = [total, supported, component_equal, locally_feasible]
    if counts != [216000, 118718, 49736, 45032]:
        raise ValueError(f"unexpected six-set census {counts}")
    return {
        "filter_order": [
            "all triples of one allowed pair per fibre",
            "positive support in the exact Gram matrix",
            "Cauchy-forced two vertices in the 12-component",
            "local lambda/mu common-neighbour feasibility",
        ],
        "counts": counts,
        "final_six_sets_sha256": digest_json(final_sets),
        "first_hostile_local_rejection": first_local_rejection,
    }


def two_fibre_certificate(
    pairs: Sequence[Sequence[tuple[int, int]]],
    q: Sequence[Sequence[int]],
) -> dict:
    left = list(pairs[0])
    right = list(pairs[1])
    permutation = list(TWO_FIBRE_PERMUTATION)
    if sorted(permutation) != list(range(60)):
        raise ValueError("two-fibre certificate is not a permutation")
    concurrence = [[0] * 12 for _ in range(12)]
    for left_index, right_index in enumerate(permutation):
        for u in left[left_index]:
            for v in right[right_index]:
                concurrence[u][v - 12] += 1
    target = [[q[u][v] for v in range(12, 24)] for u in range(12)]
    if concurrence != target:
        raise ValueError("two-fibre certificate does not realize the exact Gram block")
    payload = {
        "format": "wave42-independent-two-fibre-concurrence-v1",
        "scope": "Positive certificate for fibres 0 and 1 only; not a three-fibre B completion.",
        "left_fibre": 0,
        "right_fibre": 1,
        "left_pairs_lexicographic": [list(x) for x in left],
        "right_pairs_lexicographic": [list(x) for x in right],
        "right_pair_index_for_each_left_pair": permutation,
        "target_gram_block": target,
        "target_gram_block_sha256": digest_json(target),
    }
    payload["certificate_sha256"] = digest_json(payload)
    return payload


def verify_two_fibre_payload(payload: dict) -> None:
    left = [tuple(x) for x in payload["left_pairs_lexicographic"]]
    right = [tuple(x) for x in payload["right_pairs_lexicographic"]]
    permutation = payload["right_pair_index_for_each_left_pair"]
    if len(left) != 60 or len(right) != 60 or sorted(permutation) != list(range(60)):
        raise ValueError("malformed two-fibre permutation certificate")
    concurrence = [[0] * 12 for _ in range(12)]
    for i, j in enumerate(permutation):
        for u in left[i]:
            for v in right[j]:
                concurrence[u][v - 12] += 1
    if concurrence != payload["target_gram_block"]:
        raise ValueError("two-fibre payload concurrence mismatch")
    if digest_json(payload["target_gram_block"]) != payload["target_gram_block_sha256"]:
        raise ValueError("two-fibre target digest mismatch")
    unsigned = dict(payload)
    claimed = unsigned.pop("certificate_sha256")
    if digest_json(unsigned) != claimed:
        raise ValueError("two-fibre certificate digest mismatch")


def conditional_outside_counts(
    q: Sequence[Sequence[int]],
    adjacency: Sequence[Sequence[int]],
) -> dict:
    # A pair of outside columns can meet in at most mu=2 core vertices.
    overlap_two = sum(math.comb(q[u][v], 2) for u in range(36) for v in range(u + 1, 36))
    overlap_moment = sum(math.comb(q[u][u], 2) for u in range(36))
    overlap_one = overlap_moment - 2 * overlap_two
    overlap_zero = math.comb(60, 2) - overlap_one - overlap_two
    overlaps = [overlap_zero, overlap_one, overlap_two]
    if overlaps != [458, 1004, 308]:
        raise ValueError(f"unexpected outside-column overlap counts {overlaps}")

    # For each core vertex u, N(u) is seven disjoint edges.  Among the root
    # and the three core neighbours there is one root--same-fibre edge; the
    # two other core neighbours pair with outside vertices, leaving four H
    # edges among the ten outside neighbours.
    per_core_h_edges = []
    for u in range(36):
        core_neighbours = [v for v in range(36) if adjacency[u][v]]
        same_fibre = [v for v in core_neighbours if v // 12 == u // 12]
        if len(same_fibre) != 1:
            raise ValueError("core vertex does not have one same-fibre neighbour")
        known_vertices = core_neighbours
        known_core_edges = sum(
            adjacency[v][w]
            for i, v in enumerate(known_vertices)
            for w in known_vertices[i + 1 :]
        )
        if known_core_edges != 0:
            raise ValueError("triangle-free local core neighbourhood was violated")
        per_core_h_edges.append(4)
    weighted_h_edge_overlaps = sum(per_core_h_edges)
    overlap_two_edges = 0  # adjacent vertices have only lambda=1 common neighbour
    overlap_one_edges = weighted_h_edge_overlaps
    total_h_edges = 60 * 8 // 2
    overlap_zero_edges = total_h_edges - overlap_one_edges
    edge_overlaps = [overlap_zero_edges, overlap_one_edges, overlap_two_edges]
    if edge_overlaps != [96, 144, 0]:
        raise ValueError(f"unexpected H-edge overlap counts {edge_overlaps}")

    nonedge_overlaps = [overlaps[i] - edge_overlaps[i] for i in range(3)]
    triangle_count = sum(edge_overlaps[s] * (1 - s) for s in range(2)) // 3
    four_cycle_count = sum(
        nonedge_overlaps[s] * math.comb(2 - s, 2) for s in range(3)
    ) // 2
    if (triangle_count, four_cycle_count) != (32, 181):
        raise ValueError("unexpected conditional triangle/four-cycle counts")
    return {
        "outside_vertex_count": 60,
        "outside_degree_in_H": 8,
        "outside_edge_count": total_h_edges,
        "column_pair_overlap_0_1_2": overlaps,
        "H_edges_by_column_overlap_0_1_2": edge_overlaps,
        "H_nonedges_by_column_overlap_0_1_2": nonedge_overlaps,
        "H_triangle_count": triangle_count,
        "H_four_cycle_count": four_cycle_count,
        "derivation_scope": (
            "Necessary counts for any full B and H satisfying the hypothetical "
            "SRG equations; not an existence certificate."
        ),
    }


def build_results() -> tuple[dict, dict]:
    data = load_frozen_input()
    core = reconstruct_core(data)
    adjacency = core.pop("adjacency")
    components = core.pop("components")
    q = derive_gram(adjacency)
    small = set(components[0])
    pairs = fibre_pairs(q)
    certificate = two_fibre_certificate(pairs, q)
    verify_two_fibre_payload(certificate)
    q_distribution = Counter(
        q[u][v] for u in range(36) for v in range(u + 1, 36)
    )
    results = {
        "format": "wave42-joint-incidence-independent-v1",
        "role": "verifier",
        "claim_label": "VERIFIED_SCOPED_CONDITIONAL_REDUCTION",
        "scope": (
            "Conditional canonical mask-51739 rank-33 triangle block: exact "
            "Gram/component/pair/six-set reductions and necessary H counts."
        ),
        "input": {
            "path": "verification/wave41-allquotient-lifts/independent-results.json",
            "sha256": EXPECTED_INPUT_SHA256,
            "selected_mask": 51739,
        },
        "reconstruction": {
            **core,
            "component_orders": [len(c) for c in components],
            "component_vertices": components,
        },
        "gram": {
            "order": 36,
            "diagonal_set": sorted({q[u][u] for u in range(36)}),
            "row_sum_set": sorted({sum(row) for row in q}),
            "off_diagonal_distribution": {
                str(k): q_distribution[k] for k in sorted(q_distribution)
            },
            "matrix_sha256": digest_json(q),
            "matrix": q,
        },
        "component_cauchy": cauchy_component_check(q, components),
        "pair_inventory": pair_inventory(pairs, small),
        "six_set_census": exhaustive_six_sets(pairs, q, adjacency, small),
        "two_fibre_positive_certificate": {
            "path": "verification/wave42-joint-incidence/two-fibre-certificate.json",
            "certificate_sha256": certificate["certificate_sha256"],
            "stage_variable_count": 60 * 60,
            "scope": certificate["scope"],
        },
        "conditional_outside_counts": conditional_outside_counts(q, adjacency),
        "status_wall": {
            "full_60_column_B": "NOT_CONSTRUCTED_OR_EXCLUDED",
            "full_three_fibre_concurrence": "NOT_CONSTRUCTED_OR_EXCLUDED",
            "outside_graph_H": "NOT_CONSTRUCTED_OR_EXCLUDED",
            "endpoint_excluded": False,
            "general_upper_bound_below_4158": "NOT_PROVED",
            "graph_or_counterexample": "NONE",
            "solution": "NONE",
            "novelty_or_priority": "UNKNOWN",
        },
    }
    return results, certificate


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--certificate", type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    results, certificate = build_results()
    if args.output:
        write_json(args.output, results)
    if args.certificate:
        write_json(args.certificate, certificate)
    if args.verify or not (args.output or args.certificate):
        print(json.dumps({
            "claim_label": results["claim_label"],
            "six_set_counts": results["six_set_census"]["counts"],
            "overlap_counts": results["conditional_outside_counts"][
                "column_pair_overlap_0_1_2"
            ],
            "H_counts": {
                "edges_by_overlap": results["conditional_outside_counts"][
                    "H_edges_by_column_overlap_0_1_2"
                ],
                "triangles": results["conditional_outside_counts"]["H_triangle_count"],
                "four_cycles": results["conditional_outside_counts"]["H_four_cycle_count"],
            },
        }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

