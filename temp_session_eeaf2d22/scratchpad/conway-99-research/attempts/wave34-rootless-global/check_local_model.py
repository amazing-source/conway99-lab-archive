#!/usr/bin/env python3
"""Exact finite check of the Wave 34 fixed-point matching reduction.

This is deliberately a radius-one/partial-incidence checker.  It constructs
the 39 vertices consisting of a base triangle T and its three 12-vertex
external-neighbour fibres.  The cross-fibre matchings have composition
(0 1), hence exactly ten fixed transversal triangles and q(T)=2.  It then
searches all triples drawn from the standard one-factorization of K_12 for
within-fibre matchings which:

* obey every currently decidable lambda/mu common-neighbour cap; and
* have no pair of fixed transversals joined in exactly two fibres.

Such an object is not an SRG extension and is not endpoint evidence.  Its
purpose is to test, exactly, whether the uncontracted one-triangle incidence
geometry alone forces the forbidden R2-R3-R3 motif.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from itertools import combinations, product


N = 12
MOVED = frozenset((0, 1))
FIXED = tuple(range(2, N))
COMPLETION_FACTOR_INDICES = (0, 1, 2)


def one_factor(round_index: int) -> tuple[tuple[int, int], ...]:
    """Return one round of the canonical round-robin K_12 factorization."""
    if not 0 <= round_index < N - 1:
        raise ValueError(round_index)
    modulus = N - 1
    pairs = [(N - 1, round_index)]
    for offset in range(1, N // 2):
        pairs.append(
            (
                (round_index + offset) % modulus,
                (round_index - offset) % modulus,
            )
        )
    normalized = tuple(sorted(tuple(sorted(pair)) for pair in pairs))
    assert len(normalized) == N // 2
    assert sorted(vertex for pair in normalized for vertex in pair) == list(range(N))
    return normalized


FACTORS = tuple(one_factor(round_index) for round_index in range(N - 1))


def partner_map(factor: tuple[tuple[int, int], ...]) -> tuple[int, ...]:
    result = [-1] * N
    for left, right in factor:
        result[left] = right
        result[right] = left
    assert all(value >= 0 for value in result)
    return tuple(result)


PARTNERS = tuple(partner_map(factor) for factor in FACTORS)


def t_vertex(index: int) -> str:
    return f"t{index}"


def x_vertex(fibre: int, label: int) -> str:
    return f"x{fibre}_{label}"


def add_edge(adjacency: dict[str, set[str]], left: str, right: str) -> None:
    assert left != right
    adjacency[left].add(right)
    adjacency[right].add(left)


def sigma(label: int) -> int:
    if label == 0:
        return 1
    if label == 1:
        return 0
    return label


def build_core(factor_indices: tuple[int, int, int]) -> dict[str, set[str]]:
    vertices = [t_vertex(i) for i in range(3)]
    vertices.extend(x_vertex(i, label) for i in range(3) for label in range(N))
    adjacency = {vertex: set() for vertex in vertices}

    for i in range(3):
        for j in range(i + 1, 3):
            add_edge(adjacency, t_vertex(i), t_vertex(j))

    for fibre in range(3):
        for label in range(N):
            add_edge(adjacency, t_vertex(fibre), x_vertex(fibre, label))

    for fibre, factor_index in enumerate(factor_indices):
        for left, right in FACTORS[factor_index]:
            add_edge(adjacency, x_vertex(fibre, left), x_vertex(fibre, right))

    for label in range(N):
        add_edge(adjacency, x_vertex(0, label), x_vertex(1, label))
        add_edge(adjacency, x_vertex(1, label), x_vertex(2, label))
        add_edge(adjacency, x_vertex(2, label), x_vertex(0, sigma(label)))

    return adjacency


def cap_findings(adjacency: dict[str, set[str]]) -> list[dict[str, object]]:
    vertices = sorted(adjacency)
    findings = []
    for left_index, left in enumerate(vertices):
        for right in vertices[left_index + 1 :]:
            common = sorted(adjacency[left] & adjacency[right])
            adjacent = right in adjacency[left]
            cap = 1 if adjacent else 2
            if len(common) > cap:
                findings.append(
                    {
                        "left": left,
                        "right": right,
                        "adjacent": adjacent,
                        "cap": cap,
                        "common": common,
                    }
                )
    return findings


def fixed_pair_multiplicities(
    factor_indices: tuple[int, int, int],
) -> dict[int, int]:
    counts = {multiplicity: 0 for multiplicity in range(4)}
    for left_index, left in enumerate(FIXED):
        for right in FIXED[left_index + 1 :]:
            multiplicity = sum(
                PARTNERS[factor_index][left] == right
                for factor_index in factor_indices
            )
            counts[multiplicity] += 1
    assert sum(counts.values()) == len(FIXED) * (len(FIXED) - 1) // 2
    return counts


def moved_cross_edges() -> tuple[tuple[str, str], ...]:
    """The six nonclosed cross-fibre edges for sigma=(0 1)."""
    edges = []
    for label in MOVED:
        edges.append((x_vertex(0, label), x_vertex(1, label)))
        edges.append((x_vertex(1, label), x_vertex(2, label)))
        edges.append((x_vertex(2, label), x_vertex(0, sigma(label))))
    return tuple(sorted(tuple(sorted(edge)) for edge in edges))


def fixed_transversals() -> tuple[tuple[str, str, str], ...]:
    return tuple(
        (x_vertex(0, label), x_vertex(1, label), x_vertex(2, label))
        for label in FIXED
    )


def pair_key(left: str, right: str) -> tuple[str, str]:
    return tuple(sorted((left, right)))


def base_common_counts(
    adjacency: dict[str, set[str]],
) -> dict[tuple[str, str], int]:
    vertices = sorted(adjacency)
    return {
        pair_key(left, right): len(adjacency[left] & adjacency[right])
        for left_index, left in enumerate(vertices)
        for right in vertices[left_index + 1 :]
    }


def completion_candidates(
    adjacency: dict[str, set[str]],
    endpoints: tuple[str, str],
) -> list[tuple[str, ...]]:
    """Enumerate admissible core neighborhoods for an edge-completion vertex.

    The new vertex y completes the triangle on ``endpoints``, is nonadjacent
    to the base triangle, and has exactly two neighbours in each fibre.  The
    latter is forced by mu=2 for the three pairs (y,t_i).  Only conditions
    decidable inside the current partial object are imposed.
    """
    endpoint_set = set(endpoints)
    fibre_vertices = [
        tuple(x_vertex(fibre, label) for label in range(N))
        for fibre in range(3)
    ]
    base_counts = base_common_counts(adjacency)
    per_fibre_choices: list[list[tuple[str, ...]]] = []

    for fibre in range(3):
        forced = tuple(sorted(endpoint_set & set(fibre_vertices[fibre])))
        need = 2 - len(forced)
        if need < 0:
            return []
        available = [
            vertex
            for vertex in fibre_vertices[fibre]
            if vertex not in endpoint_set
        ]
        per_fibre_choices.append(
            [tuple(sorted(forced + choice)) for choice in combinations(available, need)]
        )

    candidates = []
    for choices in product(*per_fibre_choices):
        neighborhood = tuple(sorted(vertex for choice in choices for vertex in choice))
        neighbors = set(neighborhood)
        assert len(neighbors) == 6
        assert endpoint_set <= neighbors

        # Adding y makes it a new common neighbour of every selected core pair.
        violates_existing_pair = False
        for left, right in combinations(neighborhood, 2):
            adjacent = right in adjacency[left]
            cap = 1 if adjacent else 2
            if base_counts[pair_key(left, right)] + 1 > cap:
                violates_existing_pair = True
                break
        if violates_existing_pair:
            continue

        # Every y-core edge/nonedge must stay below its eventual lambda/mu cap.
        violates_y_pair = False
        for vertex in adjacency:
            common = len(neighbors & adjacency[vertex])
            cap = 1 if vertex in neighbors else 2
            if common > cap:
                violates_y_pair = True
                break
        if violates_y_pair:
            continue

        # The completed R2 triangle U=endpoints+y must not have three cross
        # edges to any fixed transversal (an R3 neighbour of T).
        motif = False
        for transversal in fixed_transversals():
            cross_edges = sum(
                right in adjacency[left]
                for left in endpoints
                for right in transversal
            )
            cross_edges += sum(vertex in neighbors for vertex in transversal)
            if cross_edges == 3:
                motif = True
                break
        if motif:
            continue
        candidates.append(neighborhood)
    return candidates


def search_completion_layer(
    adjacency: dict[str, set[str]],
) -> dict[str, object]:
    """Search the complete product of admissible neighborhoods, with pruning."""
    edges = moved_cross_edges()
    candidate_map = {
        edge: completion_candidates(adjacency, edge)
        for edge in edges
    }
    ordered_edges = sorted(edges, key=lambda edge: (len(candidate_map[edge]), edge))
    base_counts = base_common_counts(adjacency)
    extra_common: dict[tuple[str, str], int] = {}
    chosen: dict[tuple[str, str], tuple[str, ...]] = {}
    nodes = 0

    def recurse(position: int) -> bool:
        nonlocal nodes
        nodes += 1
        if position == len(ordered_edges):
            return True
        edge = ordered_edges[position]
        for neighborhood in candidate_map[edge]:
            neighbors = set(neighborhood)

            # Distinct completion vertices are currently left undecided.  No
            # pair may already have more than two common core neighbours.
            if any(
                len(neighbors & set(previous)) > 2
                for previous in chosen.values()
            ):
                continue

            touched = []
            valid = True
            for left, right in combinations(neighborhood, 2):
                key = pair_key(left, right)
                adjacent = right in adjacency[left]
                cap = 1 if adjacent else 2
                new_extra = extra_common.get(key, 0) + 1
                if base_counts[key] + new_extra > cap:
                    valid = False
                    break
                touched.append(key)
            if not valid:
                continue

            for key in touched:
                extra_common[key] = extra_common.get(key, 0) + 1
            chosen[edge] = neighborhood
            if recurse(position + 1):
                return True
            del chosen[edge]
            for key in touched:
                extra_common[key] -= 1
                if extra_common[key] == 0:
                    del extra_common[key]
        return False

    found = recurse(0)
    result: dict[str, object] = {
        "candidate_counts_by_nonclosed_edge": {
            "|".join(edge): len(candidate_map[edge])
            for edge in edges
        },
        "backtracking_nodes": nodes,
        "completion_layer_found": found,
        "domain": (
            "all six-neighbour core patterns with exactly two neighbours per "
            "fibre, exact endpoint inclusion, all current lambda/mu caps, and "
            "no fixed-transversal R2-R3-R3 closure"
        ),
    }
    if found:
        result["completion_neighborhoods"] = {
            "|".join(edge): list(chosen[edge])
            for edge in edges
        }
        result["partial_vertex_count_with_completions"] = len(adjacency) + len(edges)
        result["partial_edge_count_with_completions"] = (
            sum(map(len, adjacency.values())) // 2
            + 6 * len(edges)
        )
    return result


def canonical_payload(max_witnesses: int) -> dict[str, object]:
    factorization_edges = {
        str(index): [list(edge) for edge in factor]
        for index, factor in enumerate(FACTORS)
    }
    witnesses = []
    triples_checked = 0
    cap_feasible = 0
    no_double_feasible = 0

    for factor_indices in product(range(N - 1), repeat=3):
        triples_checked += 1
        adjacency = build_core(factor_indices)
        findings = cap_findings(adjacency)
        if findings:
            continue
        cap_feasible += 1
        multiplicities = fixed_pair_multiplicities(factor_indices)
        if multiplicities[2] != 0:
            continue
        no_double_feasible += 1
        if len(witnesses) < max_witnesses:
            edge_count = sum(map(len, adjacency.values())) // 2
            witnesses.append(
                {
                    "factor_indices": list(factor_indices),
                    "factor_edges": [
                        [list(edge) for edge in FACTORS[index]]
                        for index in factor_indices
                    ],
                    "fixed_pair_multiplicities": {
                        str(key): value for key, value in multiplicities.items()
                    },
                    "core_vertex_count": len(adjacency),
                    "core_edge_count": edge_count,
                    "common_neighbor_cap_findings": findings,
                }
            )
    completion_adjacency = build_core(COMPLETION_FACTOR_INDICES)
    completion_layer = search_completion_layer(completion_adjacency)
    completion_layer["factor_indices"] = list(COMPLETION_FACTOR_INDICES)
    completion_layer["fixed_pair_multiplicities"] = {
        str(key): value
        for key, value in fixed_pair_multiplicities(COMPLETION_FACTOR_INDICES).items()
    }

    structural = {
        "base_triangle_size": 3,
        "fibre_sizes": [N, N, N],
        "sigma_cycles": [[0, 1]] + [[label] for label in FIXED],
        "sigma_fixed_points": list(FIXED),
        "q_T": len(MOVED),
        "R3_neighbors_of_T": len(FIXED),
        "R2_neighbors_of_T": 3 * len(MOVED),
        "fixed_transversals": [list(item) for item in fixed_transversals()],
        "nonclosed_cross_edges": [list(edge) for edge in moved_cross_edges()],
    }
    search = {
        "factor_triples_checked": triples_checked,
        "cap_feasible_factor_triples": cap_feasible,
        "cap_and_no_double_overlap_factor_triples": no_double_feasible,
        "witnesses_emitted": len(witnesses),
        "complete_domain": "all 11^3 ordered triples of factors from the canonical K12 one-factorization",
        "scope": "39-vertex base-triangle plus external-fibres partial incidence only",
    }
    payload = {
        "schema_version": 1,
        "claim_label": "CANDIDATE_FINITE_LOCAL_CONTROL",
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
        },
        "structural_instance": structural,
        "factorization": factorization_edges,
        "search": search,
        "witnesses": witnesses,
        "completion_layer": completion_layer,
        "limitations": [
            "Degrees of fibre vertices are partial.",
            "Missing lambda/mu witnesses are not assigned.",
            "Edges among the six completion vertices are undecided.",
            "No 99-vertex graph, endpoint frame, or global overlap system is constructed.",
        ],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["canonical_payload_sha256_before_self_hash"] = hashlib.sha256(canonical).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-witnesses", type=int, default=3)
    args = parser.parse_args()
    if args.max_witnesses < 0:
        parser.error("--max-witnesses must be nonnegative")
    payload = canonical_payload(args.max_witnesses)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
