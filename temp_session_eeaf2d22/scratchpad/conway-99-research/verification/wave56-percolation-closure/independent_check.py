#!/usr/bin/env python3
"""Clean-room checker for the Wave 56 percolation-closure package.

This module deliberately does not import discovery code.  It reconstructs
the rooted eight-vertex configurations, local endpoint CSP, small control
graphs, and exact arithmetic from definitions.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


ROOTED_VERTICES = (
    "c0",
    "c1",
    "c2",
    "c3",
    "t01",
    "t12",
    "t23",
    "t30",
)
CYCLE = ("c0", "c1", "c2", "c3")
TIPS = ("t01", "t12", "t23", "t30")
TIP_EDGE_ENDPOINTS = {
    "t01": frozenset((0, 1)),
    "t12": frozenset((1, 2)),
    "t23": frozenset((2, 3)),
    "t30": frozenset((3, 0)),
}
TIP_BY_ENDPOINTS = {value: key for key, value in TIP_EDGE_ENDPOINTS.items()}
TIP_PAIRS = tuple(itertools.combinations(TIPS, 2))


def edge(u: str, v: str) -> frozenset[str]:
    if u == v:
        raise ValueError("loops are not allowed")
    return frozenset((u, v))


def rooted_edges(tip_mask: int = 0) -> set[frozenset[str]]:
    edges = {
        edge("c0", "c1"),
        edge("c1", "c2"),
        edge("c2", "c3"),
        edge("c3", "c0"),
        edge("t01", "c0"),
        edge("t01", "c1"),
        edge("t12", "c1"),
        edge("t12", "c2"),
        edge("t23", "c2"),
        edge("t23", "c3"),
        edge("t30", "c3"),
        edge("t30", "c0"),
    }
    for index, (u, v) in enumerate(TIP_PAIRS):
        if tip_mask & (1 << index):
            edges.add(edge(u, v))
    return edges


def neighbors(
    vertex: str, vertices: Sequence[str], edges: set[frozenset[str]]
) -> set[str]:
    return {other for other in vertices if other != vertex and edge(vertex, other) in edges}


def common_neighbor_count(
    u: str, v: str, vertices: Sequence[str], edges: set[frozenset[str]]
) -> int:
    return len(neighbors(u, vertices, edges) & neighbors(v, vertices, edges))


def parameter_caps_hold(
    vertices: Sequence[str],
    edges: set[frozenset[str]],
    lam: int = 1,
    mu: int = 2,
) -> bool:
    for u, v in itertools.combinations(vertices, 2):
        cap = lam if edge(u, v) in edges else mu
        if common_neighbor_count(u, v, vertices, edges) > cap:
            return False
    return True


def induced_edges(
    subset: Iterable[str], edges: set[frozenset[str]]
) -> set[frozenset[str]]:
    selected = set(subset)
    return {item for item in edges if item <= selected}


def graph_signature(
    vertices: Sequence[str], edges: set[frozenset[str]]
) -> tuple[int, ...]:
    """Canonical bit signature under every relabeling; used only at order six."""
    size = len(vertices)
    pair_positions = tuple(itertools.combinations(range(size), 2))
    signatures: list[int] = []
    for permutation in itertools.permutations(vertices):
        value = 0
        for bit, (i, j) in enumerate(pair_positions):
            if edge(permutation[i], permutation[j]) in edges:
                value |= 1 << bit
        signatures.append(value)
    return min(signatures)


def two_triangle_graph(cross_edges: int) -> tuple[tuple[str, ...], set[frozenset[str]]]:
    vertices = ("a0", "a1", "a2", "b0", "b1", "b2")
    edges = {
        edge("a0", "a1"),
        edge("a0", "a2"),
        edge("a1", "a2"),
        edge("b0", "b1"),
        edge("b0", "b2"),
        edge("b1", "b2"),
    }
    for index in range(cross_edges):
        edges.add(edge(f"a{index}", f"b{index}"))
    return vertices, edges


N3_VERTICES, N3_EDGES = two_triangle_graph(2)
PRISM_VERTICES, PRISM_EDGES = two_triangle_graph(3)
N3_SIGNATURE = graph_signature(N3_VERTICES, N3_EDGES)
PRISM_SIGNATURE = graph_signature(PRISM_VERTICES, PRISM_EDGES)


def is_n3(vertices: Sequence[str], edges: set[frozenset[str]]) -> bool:
    return len(vertices) == 6 and graph_signature(vertices, edges) == N3_SIGNATURE


def is_prism(vertices: Sequence[str], edges: set[frozenset[str]]) -> bool:
    return len(vertices) == 6 and graph_signature(vertices, edges) == PRISM_SIGNATURE


def count_induced_six_graphs(
    vertices: Sequence[str],
    edges: set[frozenset[str]],
    signature: int,
) -> int:
    count = 0
    for subset in itertools.combinations(vertices, 6):
        if graph_signature(subset, induced_edges(subset, edges)) == signature:
            count += 1
    return count


def bootstrap_waves(
    vertices: Sequence[str],
    edges: set[frozenset[str]],
    seed: Iterable[str],
) -> list[tuple[str, ...]]:
    infected = set(seed)
    waves = [tuple(sorted(infected))]
    while True:
        new = {
            vertex
            for vertex in vertices
            if vertex not in infected
            and len(neighbors(vertex, vertices, edges) & infected) >= 2
        }
        if not new:
            return waves
        infected |= new
        waves.append(tuple(sorted(new)))


def closure(
    vertices: Sequence[str],
    edges: set[frozenset[str]],
    seed: Iterable[str],
) -> frozenset[str]:
    return frozenset(itertools.chain.from_iterable(bootstrap_waves(vertices, edges, seed)))


def percolating_nonedges(
    vertices: Sequence[str], edges: set[frozenset[str]]
) -> tuple[tuple[str, str], ...]:
    result = []
    for u, v in itertools.combinations(vertices, 2):
        if edge(u, v) not in edges and closure(vertices, edges, (u, v)) == frozenset(vertices):
            result.append((u, v))
    return tuple(result)


def central_channel_nonedges(
    vertices: Sequence[str], edges: set[frozenset[str]]
) -> tuple[tuple[str, str], ...]:
    """Nonedges whose two common neighbors already lie in the six-vertex graph.

    For an induced N3 or prism inside the target, these are exactly the
    diagonals of the four-cycle used by the nonedge-channel construction.
    Other nonedges may bootstrap through the small graph but are not central
    channel incidences in the global double count.
    """
    result = []
    for u, v in itertools.combinations(vertices, 2):
        if edge(u, v) in edges:
            continue
        common = neighbors(u, vertices, edges) & neighbors(v, vertices, edges)
        if len(common) != 2:
            continue
        x, y = sorted(common)
        if edge(x, y) not in edges:
            result.append((u, v))
    return tuple(result)


def rook_graph() -> tuple[tuple[str, ...], set[frozenset[str]]]:
    vertices = tuple(f"r{i}{j}" for i in range(3) for j in range(3))
    edges = {
        edge(f"r{i}{j}", f"r{k}{ell}")
        for i, j in itertools.product(range(3), repeat=2)
        for k, ell in itertools.product(range(3), repeat=2)
        if (i, j) < (k, ell) and (i == k or j == ell)
    }
    return vertices, edges


def target_parameter_census() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for degree in range(2, 15, 2):
        order = 1 + degree * degree // 2
        discriminant = 4 * degree - 7
        root = math.isqrt(discriminant)
        multiplicities: list[str] | None = None
        feasible = False
        reason = ""
        if root * root != discriminant:
            # Irrational conjugate eigenvalues of an integer matrix have equal
            # multiplicity.  Trace and dimension would force degree=4, whose
            # discriminant is in fact rational.
            reason = "irrational conjugates cannot satisfy trace and dimension"
        else:
            positive = Fraction(-1 + root, 2)
            negative = Fraction(-1 - root, 2)
            positive_mult = Fraction(-degree - negative * (order - 1), positive - negative)
            negative_mult = order - 1 - positive_mult
            multiplicities = [str(positive_mult), str(negative_mult)]
            feasible = (
                positive_mult.denominator == 1
                and negative_mult.denominator == 1
                and positive_mult >= 0
                and negative_mult >= 0
            )
            reason = "integral nonnegative multiplicities" if feasible else "nonintegral multiplicity"
        rows.append(
            {
                "degree": degree,
                "order": order,
                "discriminant": discriminant,
                "multiplicities": multiplicities,
                "feasible": feasible,
                "reason": reason,
            }
        )
    return {
        "rows": rows,
        "feasible_degrees": [row["degree"] for row in rows if row["feasible"]],
        "proper_nonedge_degree": 4,
    }


def rooted_tip_census() -> dict[str, object]:
    records = []
    for tip_mask in range(64):
        edges = rooted_edges(tip_mask)
        valid = parameter_caps_hold(ROOTED_VERTICES, edges)
        channel_sets = (
            ("c0", "c1", "t01", "c2", "c3", "t23"),
            ("c1", "c2", "t12", "c3", "c0", "t30"),
        )
        n3_channels = 0
        prism_channels = 0
        for channel in channel_sets:
            channel_edges = induced_edges(channel, edges)
            n3_channels += int(is_n3(channel, channel_edges))
            prism_channels += int(is_prism(channel, channel_edges))
        records.append(
            {
                "tip_mask": tip_mask,
                "valid": valid,
                "tip_edges": [
                    list(pair)
                    for index, pair in enumerate(TIP_PAIRS)
                    if tip_mask & (1 << index)
                ],
                "n3_channels": n3_channels,
                "prism_channels": prism_channels,
            }
        )
    valid_records = [record for record in records if record["valid"]]
    endpoint_records = [
        record
        for record in valid_records
        if record["prism_channels"] == 0
    ]
    return {
        "all_count": len(records),
        "valid_count": len(valid_records),
        "valid_masks": [record["tip_mask"] for record in valid_records],
        "valid_channel_pairs": [
            [record["n3_channels"], record["prism_channels"]]
            for record in valid_records
        ],
        "prism_free_count": len(endpoint_records),
        "prism_free_masks": [record["tip_mask"] for record in endpoint_records],
    }


def pair_deficits(
    vertices: Sequence[str],
    edges: set[frozenset[str]],
    lam: int = 1,
    mu: int = 2,
) -> tuple[tuple[tuple[str, str], ...], tuple[int, ...]]:
    pairs = tuple(itertools.combinations(vertices, 2))
    deficits = tuple(
        (lam if edge(u, v) in edges else mu)
        - common_neighbor_count(u, v, vertices, edges)
        for u, v in pairs
    )
    if min(deficits) < 0:
        raise AssertionError("rooted graph already violates a common-neighbor cap")
    return pairs, deficits


def contains_induced_prism(
    vertices: Sequence[str], edges: set[frozenset[str]]
) -> bool:
    return count_induced_six_graphs(vertices, edges, PRISM_SIGNATURE) > 0


def allowed_endpoint_masks() -> tuple[
    tuple[tuple[str, str], ...],
    tuple[int, ...],
    dict[int, tuple[int, ...]],
]:
    base_edges = rooted_edges(0)
    pairs, deficits = pair_deficits(ROOTED_VERTICES, base_edges)
    allowed: dict[int, tuple[int, ...]] = {}
    for mask in range(1 << len(ROOTED_VERTICES)):
        selected = {
            ROOTED_VERTICES[index]
            for index in range(len(ROOTED_VERTICES))
            if mask & (1 << index)
        }
        if len(selected) < 2:
            continue

        covered = tuple(
            index
            for index, pair in enumerate(pairs)
            if set(pair) <= selected
        )
        if any(deficits[index] == 0 for index in covered):
            continue

        compatible = True
        for vertex in ROOTED_VERTICES:
            visible_common = len(neighbors(vertex, ROOTED_VERTICES, base_edges) & selected)
            cap = 1 if vertex in selected else 2
            if visible_common > cap:
                compatible = False
                break
        if not compatible:
            continue

        extended_vertices = ROOTED_VERTICES + ("z",)
        extended_edges = set(base_edges)
        extended_edges.update(edge("z", vertex) for vertex in selected)
        if contains_induced_prism(extended_vertices, extended_edges):
            continue

        allowed[mask] = covered
    return pairs, deficits, allowed


def enumerate_exact_profiles(
    deficits: tuple[int, ...],
    allowed: dict[int, tuple[int, ...]],
) -> tuple[tuple[int, ...], ...]:
    cover_vectors = {
        mask: tuple(int(index in covered) for index in range(len(deficits)))
        for mask, covered in allowed.items()
    }
    by_pair = {
        index: tuple(
            mask for mask, vector in cover_vectors.items() if vector[index]
        )
        for index in range(len(deficits))
    }
    memo: dict[tuple[int, ...], frozenset[tuple[int, ...]]] = {}

    def solve(remaining: tuple[int, ...]) -> frozenset[tuple[int, ...]]:
        if not any(remaining):
            return frozenset(((),))
        if remaining in memo:
            return memo[remaining]
        pivot = next(index for index, value in enumerate(remaining) if value)
        solutions: set[tuple[int, ...]] = set()
        for mask in by_pair[pivot]:
            vector = cover_vectors[mask]
            if any(vector[index] > remaining[index] for index in range(len(remaining))):
                continue
            reduced = tuple(
                remaining[index] - vector[index]
                for index in range(len(remaining))
            )
            for suffix in solve(reduced):
                solutions.add(tuple(sorted((mask,) + suffix)))
        result = frozenset(solutions)
        memo[remaining] = result
        return result

    return tuple(sorted(solve(deficits)))


def d4_vertex_permutations() -> tuple[dict[str, str], ...]:
    permutations = []
    for direction in (1, -1):
        for offset in range(4):
            cycle_image = {
                index: (direction * index + offset) % 4
                for index in range(4)
            }
            mapping = {
                f"c{index}": f"c{cycle_image[index]}"
                for index in range(4)
            }
            for tip, endpoints in TIP_EDGE_ENDPOINTS.items():
                mapped_endpoints = frozenset(cycle_image[index] for index in endpoints)
                mapping[tip] = TIP_BY_ENDPOINTS[mapped_endpoints]
            permutations.append(mapping)
    unique = {
        tuple(mapping[vertex] for vertex in ROOTED_VERTICES): mapping
        for mapping in permutations
    }
    return tuple(unique[key] for key in sorted(unique))


def transform_mask(mask: int, mapping: dict[str, str]) -> int:
    result = 0
    for index, vertex in enumerate(ROOTED_VERTICES):
        if mask & (1 << index):
            result |= 1 << ROOTED_VERTICES.index(mapping[vertex])
    return result


def profile_orbits(
    profiles: tuple[tuple[int, ...], ...]
) -> tuple[
    tuple[tuple[int, ...], ...],
    dict[tuple[int, ...], int],
    tuple[tuple[tuple[int, ...], ...], ...],
]:
    profile_set = set(profiles)
    transformations = d4_vertex_permutations()
    canonical_to_members: dict[tuple[int, ...], set[tuple[int, ...]]] = {}
    for profile in profiles:
        images = {
            tuple(sorted(transform_mask(mask, mapping) for mask in profile))
            for mapping in transformations
        }
        if not images <= profile_set:
            raise AssertionError("formal D4 relabeling left the exact profile set")
        canonical = min(images)
        canonical_to_members.setdefault(canonical, set()).update(images)
    canonical_profiles = tuple(sorted(canonical_to_members))
    orbit_sizes = {
        canonical: len(canonical_to_members[canonical])
        for canonical in canonical_profiles
    }
    member_sets = tuple(
        tuple(sorted(canonical_to_members[canonical]))
        for canonical in canonical_profiles
    )
    return canonical_profiles, orbit_sizes, member_sets


def endpoint_census() -> dict[str, object]:
    pairs, deficits, allowed = allowed_endpoint_masks()
    profiles = enumerate_exact_profiles(deficits, allowed)
    canonical_profiles, orbit_sizes, orbit_member_sets = profile_orbits(profiles)

    mask_size_histogram = Counter(
        (mask.bit_count()) for mask in allowed
    )
    arity_histogram: Counter[str] = Counter()
    wave_size_histogram: Counter[str] = Counter()
    equation_failures = []
    new_pair_cap_failures = []
    base_degree_cap_failures = []
    forced_new_pair_relation_histogram: Counter[str] = Counter()
    base_edges = rooted_edges(0)
    for profile in profiles:
        arities = Counter(mask.bit_count() for mask in profile)
        x2, x3, x4 = arities[2], arities[3], arities[4]
        key = f"{x2},{x3},{x4}"
        arity_histogram[key] += 1
        wave_size_histogram[str(len(profile))] += 1
        if x2 + 3 * x3 + 6 * x4 != sum(deficits):
            equation_failures.append(list(profile))
        for first, second in itertools.combinations(profile, 2):
            visible_common = (first & second).bit_count()
            if visible_common > 2:
                new_pair_cap_failures.append(
                    {
                        "profile": list(profile),
                        "masks": [first, second],
                        "visible_common": visible_common,
                    }
                )
            elif visible_common == 2:
                forced_new_pair_relation_histogram["nonadjacent"] += 1
            elif visible_common == 1:
                forced_new_pair_relation_histogram["not_yet_fixed"] += 1
            else:
                forced_new_pair_relation_histogram["not_yet_fixed"] += 1
        for index, vertex in enumerate(ROOTED_VERTICES):
            new_neighbors = sum(bool(mask & (1 << index)) for mask in profile)
            current_degree = len(neighbors(vertex, ROOTED_VERTICES, base_edges))
            if current_degree + new_neighbors > 14:
                base_degree_cap_failures.append(
                    {
                        "profile": list(profile),
                        "vertex": vertex,
                        "current_degree": current_degree,
                        "new_neighbors": new_neighbors,
                    }
                )

    return {
        "pair_count": len(pairs),
        "pair_deficit_histogram": {
            str(value): count
            for value, count in sorted(Counter(deficits).items())
        },
        "pair_deficit_sum": sum(deficits),
        "allowed_mask_count": len(allowed),
        "allowed_masks": sorted(allowed),
        "allowed_mask_size_histogram": {
            str(value): count
            for value, count in sorted(mask_size_histogram.items())
        },
        "profile_count": len(profiles),
        "profiles": [list(profile) for profile in profiles],
        "arity_triple_histogram": dict(sorted(arity_histogram.items())),
        "wave_size_histogram": dict(
            sorted(wave_size_histogram.items(), key=lambda item: int(item[0]))
        ),
        "wave_size_range": [min(map(len, profiles)), max(map(len, profiles))],
        "total_infected_after_wave_3_range": [
            8 + min(map(len, profiles)),
            8 + max(map(len, profiles)),
        ],
        "formal_d4_group_order": len(d4_vertex_permutations()),
        "formal_d4_orbit_count": len(canonical_profiles),
        "formal_d4_canonical_profiles": [
            list(profile) for profile in canonical_profiles
        ],
        "formal_d4_orbit_sizes": [
            orbit_sizes[profile] for profile in canonical_profiles
        ],
        "formal_d4_orbit_member_sets": [
            [list(profile) for profile in member_set]
            for member_set in orbit_member_sets
        ],
        "formal_d4_orbit_size_histogram": {
            str(value): count
            for value, count in sorted(Counter(orbit_sizes.values()).items())
        },
        "pair_deficit_equation": "x2 + 3*x3 + 6*x4 = 16",
        "equation_failure_count": len(equation_failures),
        "new_pair_visible_cap_failure_count": len(new_pair_cap_failures),
        "base_degree_cap_failure_count": len(base_degree_cap_failures),
        "forced_new_pair_relation_histogram": dict(
            sorted(forced_new_pair_relation_histogram.items())
        ),
        "completability_claimed": False,
        "target_graph_automorphism_assumed": False,
    }


def control_graph_census() -> dict[str, object]:
    rook_vertices, rook_edges = rook_graph()
    rook_degrees = sorted(
        {len(neighbors(vertex, rook_vertices, rook_edges)) for vertex in rook_vertices}
    )
    adjacent_common = sorted(
        {
            common_neighbor_count(u, v, rook_vertices, rook_edges)
            for u, v in itertools.combinations(rook_vertices, 2)
            if edge(u, v) in rook_edges
        }
    )
    nonadjacent_common = sorted(
        {
            common_neighbor_count(u, v, rook_vertices, rook_edges)
            for u, v in itertools.combinations(rook_vertices, 2)
            if edge(u, v) not in rook_edges
        }
    )
    return {
        "n3_central_channel_nonedges": len(
            central_channel_nonedges(N3_VERTICES, N3_EDGES)
        ),
        "prism_central_channel_nonedges": len(
            central_channel_nonedges(PRISM_VERTICES, PRISM_EDGES)
        ),
        "n3_internal_percolating_nonedges": len(
            percolating_nonedges(N3_VERTICES, N3_EDGES)
        ),
        "prism_internal_percolating_nonedges": len(
            percolating_nonedges(PRISM_VERTICES, PRISM_EDGES)
        ),
        "rook": {
            "vertices": len(rook_vertices),
            "edges": len(rook_edges),
            "nonedges": math.comb(len(rook_vertices), 2) - len(rook_edges),
            "degree_values": rook_degrees,
            "adjacent_common_neighbor_values": adjacent_common,
            "nonadjacent_common_neighbor_values": nonadjacent_common,
            "n3_count": count_induced_six_graphs(
                rook_vertices, rook_edges, N3_SIGNATURE
            ),
            "prism_count": count_induced_six_graphs(
                rook_vertices, rook_edges, PRISM_SIGNATURE
            ),
            "nonedge_closure_size_histogram": {
                str(value): count
                for value, count in sorted(
                    Counter(
                        len(closure(rook_vertices, rook_edges, (u, v)))
                        for u, v in itertools.combinations(rook_vertices, 2)
                        if edge(u, v) not in rook_edges
                    ).items()
                )
            },
        },
    }


def incidence_arithmetic() -> dict[str, object]:
    v, k, lam, mu = 99, 14, 1, 2
    edges = v * k // 2
    nonedges = math.comb(v, 2) - edges
    triangles = edges * lam // 3

    feasible_rows = 0
    equality_rows = 0
    for prism_count in range(nonedges // 3 + 1):
        n3 = nonedges - 3 * prism_count
        for closures in range(min(231, prism_count // 6) + 1):
            feasible_rows += 1
            nonpercolating = 18 * closures
            percolating = nonedges - nonpercolating
            if not nonpercolating <= 3 * prism_count:
                raise AssertionError("R<=3P failed under the incidence hypotheses")
            if not percolating >= n3:
                raise AssertionError("S>=n3 failed under the incidence hypotheses")
            if (nonpercolating == 3 * prism_count) != (
                prism_count == 6 * closures
            ):
                raise AssertionError("equality condition failed")
            equality_rows += int(nonpercolating == 3 * prism_count)

    # Hostile factor changes are false on the exact rook control.
    controls = control_graph_census()
    rook = controls["rook"]
    hostile_rejections = {
        "R_equals_17H": rook["nonedges"] != 17,
        "five_prisms_per_H": rook["prism_count"] != 5,
        "N3_has_three_central_seeds": controls["n3_central_channel_nonedges"] != 3,
        "prism_has_five_central_seeds": controls[
            "prism_central_channel_nonedges"
        ]
        != 5,
    }
    return {
        "target": {
            "v": v,
            "k": k,
            "lambda": lam,
            "mu": mu,
            "edges": edges,
            "nonedges": nonedges,
            "triangles": triangles,
        },
        "channel_identity": "n3 + 3*P = 4158",
        "closure_identity": "R = 18*H",
        "percolating_identity": "S = 4158 - R",
        "proved_from_multiplicities": [
            "6*H <= P",
            "R <= 3*P = 4158 - n3",
            "S >= n3",
        ],
        "enumerated_symbolic_incidence_rows": feasible_rows,
        "equality_rows": equality_rows,
        "hostile_factor_rejections": hostile_rejections,
        "endpoint": {
            "n3": 4158,
            "P": 0,
            "H": 0,
            "R": 0,
            "S": 4158,
            "every_nonedge_percolates": True,
        },
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compare_discovery(
    independent: dict[str, object], discovery_path: Path
) -> dict[str, object]:
    discovery = json.loads(discovery_path.read_text(encoding="utf-8"))
    early = discovery["arbitrary_nonedge_early_waves"]
    endpoint = early["endpoint"]
    local = independent["endpoint_census"]
    controls = independent["control_graphs"]
    global_relations = discovery["global_exact_relations"]
    endpoint_record = next(
        record for record in early["tip_graphs"] if record["bits"] == 0
    )
    discovery_masks = sorted(
        record["mask"] for record in endpoint_record["allowed_outside_masks"]
    )
    discovery_profiles = sorted(
        tuple(
            sorted(
                multiplicity["mask"]
                for multiplicity in profile["multiplicities"]
                for _ in range(multiplicity["count"])
            )
        )
        for profile in endpoint_record["next_wave_profiles"]
    )
    discovery_canonical_profiles = sorted(
        tuple(
            sorted(
                multiplicity["mask"]
                for multiplicity in orbit["canonical_profile"]
                for _ in range(multiplicity["count"])
            )
        )
        for orbit in endpoint_record["formal_D4_orbits"]
    )
    discovery_orbit_members: dict[int, list[tuple[int, ...]]] = {}
    for profile in endpoint_record["next_wave_profiles"]:
        expanded = tuple(
            sorted(
                multiplicity["mask"]
                for multiplicity in profile["multiplicities"]
                for _ in range(multiplicity["count"])
            )
        )
        discovery_orbit_members.setdefault(
            profile["formal_D4_orbit_id"], []
        ).append(expanded)
    discovery_orbit_partition = sorted(
        tuple(sorted(members))
        for members in discovery_orbit_members.values()
    )
    independent_orbit_partition = sorted(
        tuple(tuple(profile) for profile in member_set)
        for member_set in local["formal_d4_orbit_member_sets"]
    )

    checks = {
        "all_labeled_tip_graph_count": early["all_labeled_tip_graph_count"]
        == independent["tip_census"]["all_count"],
        "admissible_tip_graph_count": early["lambda_mu_admissible_tip_graph_count"]
        == independent["tip_census"]["valid_count"],
        "endpoint_tip_count": endpoint["admissible_tip_graph_count"]
        == independent["tip_census"]["prism_free_count"],
        "endpoint_allowed_masks": endpoint["allowed_outside_mask_count"]
        == local["allowed_mask_count"],
        "exact_allowed_mask_list": discovery_masks == local["allowed_masks"],
        "endpoint_profiles": endpoint["next_wave_profile_count"]
        == local["profile_count"],
        "exact_profile_list": discovery_profiles
        == [tuple(profile) for profile in local["profiles"]],
        "endpoint_D4_orbits": endpoint["formal_D4_orbit_count"]
        == local["formal_d4_orbit_count"],
        "exact_D4_orbit_partition": discovery_orbit_partition
        == independent_orbit_partition,
        "displayed_D4_representatives_belong_to_orbits": all(
            any(representative in members for members in discovery_orbit_partition)
            for representative in discovery_canonical_profiles
        ),
        "arity_histogram": endpoint["next_wave_arity_triple_histogram"]
        == local["arity_triple_histogram"],
        "wave_histogram": endpoint["next_wave_size_histogram"]
        == local["wave_size_histogram"],
        "infected_range": endpoint["total_infected_after_wave_3_range"]
        == local["total_infected_after_wave_3_range"],
        "rook_nonedges": discovery["rook_graph_control"]["nonedge_count"]
        == controls["rook"]["nonedges"],
        "rook_prisms": discovery["rook_graph_control"]["induced_triangular_prism_count"]
        == controls["rook"]["prism_count"],
        "rook_n3": discovery["rook_graph_control"]["induced_n3_count"]
        == controls["rook"]["n3_count"],
        "identity_n3_P": "n3 + 3*P = 4158" in global_relations["identities"],
        "identity_R_H": "R = 18*H" in global_relations["identities"],
        "inequality_6H_P": "6*H <= P" in global_relations["proved_inequalities"],
        "inequality_R_P": "R <= 3*P = 4158 - n3"
        in global_relations["proved_inequalities"],
        "inequality_S_n3": "S >= n3" in global_relations["proved_inequalities"],
        "no_completability_overclaim": any(
            "not completed graphs" in text
            for text in discovery.get("limitations", [])
        ),
        "no_target_automorphism_claim": any(
            "not a graph automorphism" in text
            for text in discovery.get("limitations", [])
        ),
    }
    return {
        "discovery_path": str(discovery_path).replace("\\", "/"),
        "discovery_sha256": sha256(discovery_path),
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "corrections": [],
    }


def build_result(discovery_path: Path | None = None) -> dict[str, object]:
    result: dict[str, object] = {
        "schema_version": 1,
        "role": "verifier",
        "claim_label": "VERIFIED",
        "scope": (
            "Conditional source classification, target arithmetic, incidence "
            "relations, and exact local endpoint census only"
        ),
        "source_check": {
            "paper": (
                "Ibrahim, LaFayette, McCall, Australasian Journal of "
                "Combinatorics 93(1) (2025), 60-89"
            ),
            "pdf_sha256": (
                "3bcbb35f6bac46bf943970fa53918fa2b126684375a325efff308371e785fb0f"
            ),
            "lemma_4_9_scope": (
                "A 2-bootstrap closure in an SRG is K_(lambda+2), an "
                "irregular (lambda,mu)-graph, or an SRG with the same "
                "lambda and mu."
            ),
            "theorem_4_8_scope": (
                "An irregular (lambda,mu)-graph requires mu=0 or mu=1; "
                "therefore mu=2 excludes that branch."
            ),
            "theorem_4_19_scope": (
                "The paper states the 231 rook-copy bound and its "
                "percolation equivalences for the hypothetical target."
            ),
        },
        "parameter_census": target_parameter_census(),
        "tip_census": rooted_tip_census(),
        "endpoint_census": endpoint_census(),
        "control_graphs": control_graph_census(),
        "incidence_arithmetic": incidence_arithmetic(),
        "mathematical_audit": {
            "closure_dichotomy": "VERIFIED",
            "n3_plus_3P": "VERIFIED",
            "R_equals_18H": "VERIFIED",
            "sixH_le_P": "VERIFIED",
            "R_le_3P": "VERIFIED",
            "S_ge_n3": "VERIFIED",
            "endpoint_every_nonedge_percolates": "VERIFIED",
            "profiles_global_completability": "UNKNOWN_AND_NOT_CLAIMED",
            "target_graph_existence": "UNKNOWN",
            "strict_n3_upper_bound": "NOT_OBTAINED",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "The finite profiles are local necessary configurations only.",
            "No edges among wave-3 vertices or later completion are assigned.",
            "D4 acts only on formal labels; no target automorphism is assumed.",
            "The source theorem is cited rather than reproved in full.",
            "No graph, endpoint exclusion, or strict n3 upper bound follows.",
        ],
    }
    if discovery_path is not None:
        result["discovery_comparison"] = compare_discovery(result, discovery_path)
        if not result["discovery_comparison"]["all_checks_pass"]:
            result["claim_label"] = "REFUTED"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--discovery", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-output", type=Path)
    args = parser.parse_args()

    result = build_result(args.discovery)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.verify_output is not None:
        expected = args.verify_output.read_text(encoding="utf-8")
        if expected != encoded:
            raise SystemExit("stored independent result does not reproduce")
    if args.output is not None:
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
    elif args.verify_output is None:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
