#!/usr/bin/env python3
"""Exact Wave56 bootstrap-percolation and closure-space discovery.

All enumerations are labeled.  Dihedral orbit data is added only as a compact
summary after the complete labeled lists have been retained.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import math
import os
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Iterable


V = 99
K = 14
LAMBDA = 1
MU = 2
EDGE_COUNT = V * K // 2
NONEDGE_COUNT = math.comb(V, 2) - EDGE_COUNT
MIN_FREE_MEMORY_PERCENT = 15.0

CURRENT = tuple(range(8))
CYCLE = tuple(range(4))
TIPS = tuple(range(4, 8))
LABELS = (
    "c0",
    "c1",
    "c2",
    "c3",
    "t01",
    "t12",
    "t23",
    "t30",
)
PAIRS = tuple(combinations(CURRENT, 2))
TIP_PAIRS = tuple(combinations(TIPS, 2))
PAIR_INDEX = {pair: index for index, pair in enumerate(PAIRS)}

HERE = Path(__file__).resolve().parent


def edge(u: int, v: int) -> tuple[int, int]:
    return tuple(sorted((u, v)))


def base_edges() -> set[tuple[int, int]]:
    result = {edge(0, 1), edge(1, 2), edge(2, 3), edge(3, 0)}
    for i in range(4):
        tip = 4 + i
        result.add(edge(tip, i))
        result.add(edge(tip, (i + 1) % 4))
    return result


def adjacent(edges: set[tuple[int, int]], u: int, v: int) -> bool:
    return edge(u, v) in edges


def internal_common_neighbors(
    edges: set[tuple[int, int]],
    u: int,
    v: int,
    vertices: Iterable[int] = CURRENT,
) -> int:
    return sum(
        adjacent(edges, u, w) and adjacent(edges, v, w)
        for w in vertices
        if w not in (u, v)
    )


def induced_triangle_count(
    edges: set[tuple[int, int]], vertices: Iterable[int]
) -> int:
    return sum(
        all(adjacent(edges, *pair) for pair in combinations(triple, 2))
        for triple in combinations(tuple(vertices), 3)
    )


def is_induced_triangular_prism(
    edges: set[tuple[int, int]], vertices: Iterable[int]
) -> bool:
    vertices = tuple(vertices)
    if len(vertices) != 6:
        return False
    degrees = [
        sum(adjacent(edges, u, w) for w in vertices if w != u)
        for u in vertices
    ]
    return all(degree == 3 for degree in degrees) and (
        induced_triangle_count(edges, vertices) == 2
    )


def induced_prisms(
    edges: set[tuple[int, int]], vertices: Iterable[int]
) -> list[tuple[int, ...]]:
    vertices = tuple(vertices)
    return [
        subset
        for subset in combinations(vertices, 6)
        if is_induced_triangular_prism(edges, subset)
    ]


def is_induced_n3(
    edges: set[tuple[int, int]], vertices: Iterable[int]
) -> bool:
    """Recognize two disjoint triangles joined by exactly two matching edges."""

    vertices = tuple(vertices)
    if len(vertices) != 6:
        return False
    first = vertices[0]
    for rest in combinations(vertices[1:], 2):
        left = (first,) + rest
        right = tuple(v for v in vertices if v not in left)
        if not all(adjacent(edges, *p) for p in combinations(left, 2)):
            continue
        if not all(adjacent(edges, *p) for p in combinations(right, 2)):
            continue
        cross = [(u, v) for u in left for v in right if adjacent(edges, u, v)]
        if len(cross) != 2:
            continue
        if len({u for u, _ in cross}) == 2 and len({v for _, v in cross}) == 2:
            return True
    return False


def induced_n3s(
    edges: set[tuple[int, int]], vertices: Iterable[int]
) -> list[tuple[int, ...]]:
    vertices = tuple(vertices)
    return [
        subset
        for subset in combinations(vertices, 6)
        if is_induced_n3(edges, subset)
    ]


def free_memory_percent() -> float:
    if os.name == "nt":
        class MemoryStatus(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MemoryStatus()
        status.dwLength = ctypes.sizeof(MemoryStatus)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise OSError("GlobalMemoryStatusEx failed")
        return 100.0 * status.ullAvailPhys / status.ullTotalPhys
    page_size = os.sysconf("SC_PAGE_SIZE")
    available = os.sysconf("SC_AVPHYS_PAGES") * page_size
    total = os.sysconf("SC_PHYS_PAGES") * page_size
    return 100.0 * available / total


def enforce_memory_floor() -> None:
    percent = free_memory_percent()
    if percent < MIN_FREE_MEMORY_PERCENT:
        raise MemoryError(
            f"free memory {percent:.2f}% is below "
            f"{MIN_FREE_MEMORY_PERCENT:.2f}%"
        )


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def pair_deficits(edges: set[tuple[int, int]]) -> tuple[int, ...]:
    values = []
    for u, v in PAIRS:
        target = LAMBDA if adjacent(edges, u, v) else MU
        values.append(target - internal_common_neighbors(edges, u, v))
    return tuple(values)


def local_pair_caps_pass(edges: set[tuple[int, int]]) -> bool:
    return all(value >= 0 for value in pair_deficits(edges))


def tip_graph_records() -> list[dict[str, object]]:
    records = []
    base = base_edges()
    for bits in range(1 << len(TIP_PAIRS)):
        edges = set(base)
        selected = []
        for index, pair in enumerate(TIP_PAIRS):
            if (bits >> index) & 1:
                edges.add(edge(*pair))
                selected.append(pair)
        if not local_pair_caps_pass(edges):
            continue
        prisms = induced_prisms(edges, CURRENT)
        opposite_edges = sum(
            edge(*pair) in edges for pair in ((4, 6), (5, 7))
        )
        records.append(
            {
                "bits": bits,
                "bitstring_in_tip_pair_order": "".join(
                    str((bits >> i) & 1) for i in range(len(TIP_PAIRS))
                ),
                "tip_edges": [
                    [LABELS[u], LABELS[v]] for u, v in selected
                ],
                "tip_edge_count": len(selected),
                "opposite_tip_edge_count": opposite_edges,
                "central_n3_channels": 2 - opposite_edges,
                "central_prism_channels": opposite_edges,
                "internal_prisms": [
                    [LABELS[v] for v in prism] for prism in prisms
                ],
                "prism_free_endpoint_admissible": not prisms,
                "_edges": edges,
            }
        )
    return records


def mask_vertices(mask: int) -> tuple[int, ...]:
    return tuple(v for v in CURRENT if (mask >> v) & 1)


def outside_mask_allowed(
    edges: set[tuple[int, int]],
    mask: int,
    deficits: tuple[int, ...],
    *,
    require_prism_free: bool,
) -> bool:
    neighbors = set(mask_vertices(mask))
    if len(neighbors) < 2:
        return False

    for u in CURRENT:
        internal = sum(
            adjacent(edges, u, w) for w in neighbors if w != u
        )
        if u in neighbors and internal > LAMBDA:
            return False
        if u not in neighbors and internal > MU:
            return False

    covered = [
        index
        for index, pair in enumerate(PAIRS)
        if set(pair).issubset(neighbors)
    ]
    if not covered or any(deficits[index] == 0 for index in covered):
        return False

    if require_prism_free:
        extended = set(edges)
        for u in neighbors:
            extended.add(edge(u, 8))
        if induced_prisms(extended, tuple(range(9))):
            return False
    return True


def allowed_outside_masks(
    edges: set[tuple[int, int]], *, require_prism_free: bool
) -> list[tuple[int, tuple[int, ...]]]:
    deficits = pair_deficits(edges)
    result = []
    for mask in range(1 << len(CURRENT)):
        if not outside_mask_allowed(
            edges, mask, deficits, require_prism_free=require_prism_free
        ):
            continue
        covered = tuple(
            index
            for index, pair in enumerate(PAIRS)
            if all((mask >> vertex) & 1 for vertex in pair)
        )
        result.append((mask, covered))
    return result


def exact_multicover_profiles(
    deficits: tuple[int, ...],
    masks: list[tuple[int, tuple[int, ...]]],
) -> list[tuple[int, ...]]:
    coverers = {index: [] for index in range(len(PAIRS))}
    for mask_index, (_, covered) in enumerate(masks):
        for pair_index in covered:
            coverers[pair_index].append(mask_index)

    solutions: set[tuple[int, ...]] = set()
    seen: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()

    def recurse(
        remaining: tuple[int, ...], counts: tuple[int, ...]
    ) -> None:
        state = (remaining, counts)
        if state in seen:
            return
        seen.add(state)
        if not any(remaining):
            solutions.add(counts)
            return

        options = None
        for pair_index, needed in enumerate(remaining):
            if not needed:
                continue
            candidates = [
                mask_index
                for mask_index in coverers[pair_index]
                if all(
                    remaining[covered_index] > 0
                    for covered_index in masks[mask_index][1]
                )
            ]
            if not candidates:
                return
            if options is None or len(candidates) < len(options):
                options = candidates
        assert options is not None

        for mask_index in options:
            new_remaining = list(remaining)
            for covered_index in masks[mask_index][1]:
                new_remaining[covered_index] -= 1
            new_counts = list(counts)
            new_counts[mask_index] += 1
            recurse(tuple(new_remaining), tuple(new_counts))

    recurse(deficits, tuple(0 for _ in masks))
    return sorted(solutions, key=lambda values: (sum(values), values))


def profile_key(
    counts: tuple[int, ...], masks: list[tuple[int, tuple[int, ...]]]
) -> tuple[tuple[int, int], ...]:
    return tuple(
        sorted(
            (masks[index][0], count)
            for index, count in enumerate(counts)
            if count
        )
    )


def cycle_dihedral_permutations() -> list[dict[int, int]]:
    permutations = []
    for reflected in (False, True):
        for shift in range(4):
            if reflected:
                image = lambda i, shift=shift: (shift - i) % 4
            else:
                image = lambda i, shift=shift: (i + shift) % 4
            permutation = {i: image(i) for i in CYCLE}
            for i in CYCLE:
                image_edge = {image(i), image((i + 1) % 4)}
                target = next(
                    j
                    for j in CYCLE
                    if {j, (j + 1) % 4} == image_edge
                )
                permutation[4 + i] = 4 + target
            permutations.append(permutation)
    return permutations


def permute_mask(mask: int, permutation: dict[int, int]) -> int:
    result = 0
    for vertex in CURRENT:
        if (mask >> vertex) & 1:
            result |= 1 << permutation[vertex]
    return result


def permute_profile(
    key: tuple[tuple[int, int], ...], permutation: dict[int, int]
) -> tuple[tuple[int, int], ...]:
    return tuple(
        sorted((permute_mask(mask, permutation), count) for mask, count in key)
    )


def endpoint_orbits(
    keys: list[tuple[tuple[int, int], ...]]
) -> tuple[dict[tuple[tuple[int, int], ...], int], list[dict[str, object]]]:
    key_set = set(keys)
    remaining = set(keys)
    membership = {}
    records = []
    group = cycle_dihedral_permutations()
    while remaining:
        representative = min(remaining)
        orbit = {
            permute_profile(representative, permutation)
            for permutation in group
        } & key_set
        orbit_id = len(records)
        for member in orbit:
            membership[member] = orbit_id
        remaining -= orbit
        records.append(
            {
                "orbit_id": orbit_id,
                "labeled_size": len(orbit),
                "canonical_profile": [
                    {
                        "mask": mask,
                        "neighbors": [
                            LABELS[v] for v in mask_vertices(mask)
                        ],
                        "count": count,
                    }
                    for mask, count in representative
                ],
            }
        )
    return membership, records


def serialize_profile(
    counts: tuple[int, ...],
    masks: list[tuple[int, tuple[int, ...]]],
    *,
    orbit_id: int | None,
) -> dict[str, object]:
    multiplicities = []
    arity_counts = Counter()
    pair_cover_total = 0
    for index, count in enumerate(counts):
        if not count:
            continue
        mask, covered = masks[index]
        arity = mask.bit_count()
        arity_counts[arity] += count
        pair_cover_total += len(covered) * count
        multiplicities.append(
            {
                "mask": mask,
                "neighbors": [LABELS[v] for v in mask_vertices(mask)],
                "count": count,
            }
        )
    result = {
        "wave_size": sum(counts),
        "arity_counts": {
            str(arity): arity_counts.get(arity, 0) for arity in (2, 3, 4)
        },
        "pair_cover_total": pair_cover_total,
        "multiplicities": multiplicities,
    }
    if orbit_id is not None:
        result["formal_D4_orbit_id"] = orbit_id
    return result


def tip_profile_package(record: dict[str, object]) -> dict[str, object]:
    edges = record["_edges"]
    assert isinstance(edges, set)
    endpoint = bool(record["prism_free_endpoint_admissible"])
    deficits = pair_deficits(edges)
    masks = allowed_outside_masks(edges, require_prism_free=endpoint)
    profiles = exact_multicover_profiles(deficits, masks)
    keys = [profile_key(counts, masks) for counts in profiles]

    orbit_membership = {}
    orbit_records = []
    if endpoint:
        orbit_membership, orbit_records = endpoint_orbits(keys)

    public_record = {
        key: value for key, value in record.items() if not key.startswith("_")
    }
    public_record.update(
        {
            "pair_deficit_histogram": {
                str(value): count
                for value, count in sorted(Counter(deficits).items())
            },
            "pair_deficit_sum": sum(deficits),
            "allowed_outside_mask_count": len(masks),
            "allowed_outside_mask_arity_histogram": {
                str(value): count
                for value, count in sorted(
                    Counter(mask.bit_count() for mask, _ in masks).items()
                )
            },
            "allowed_outside_masks": [
                {
                    "mask": mask,
                    "neighbors": [LABELS[v] for v in mask_vertices(mask)],
                    "covered_pair_indices": list(covered),
                }
                for mask, covered in masks
            ],
            "next_wave_profile_count": len(profiles),
            "next_wave_size_histogram": {
                str(value): count
                for value, count in sorted(
                    Counter(sum(profile) for profile in profiles).items()
                )
            },
            "next_wave_arity_triple_histogram": {
                ",".join(map(str, triple)): count
                for triple, count in sorted(
                    Counter(
                        tuple(
                            sum(
                                multiplicity
                                for index, multiplicity in enumerate(profile)
                                if masks[index][0].bit_count() == arity
                            )
                            for arity in (2, 3, 4)
                        )
                        for profile in profiles
                    ).items()
                )
            },
            "next_wave_profiles": [
                serialize_profile(
                    profile,
                    masks,
                    orbit_id=(
                        orbit_membership[profile_key(profile, masks)]
                        if endpoint
                        else None
                    ),
                )
                for profile in profiles
            ],
            "formal_D4_orbits": orbit_records,
        }
    )
    return public_record


def rook_graph_3x3() -> tuple[tuple[tuple[int, int], ...], set[tuple[int, int]]]:
    points = tuple((row, column) for row in range(3) for column in range(3))
    edges = {
        edge(i, j)
        for i, first in enumerate(points)
        for j, second in enumerate(points)
        if i < j and (first[0] == second[0] or first[1] == second[1])
    }
    return points, edges


def forced_nine_vertex_closure() -> set[tuple[int, int]]:
    edges = base_edges()
    edges.add(edge(4, 6))
    edges.add(edge(5, 7))
    for tip in TIPS:
        edges.add(edge(8, tip))
    return edges


def exact_pair_parameters(
    edges: set[tuple[int, int]], vertices: Iterable[int]
) -> dict[str, object]:
    vertices = tuple(vertices)
    degrees = {
        sum(adjacent(edges, u, v) for v in vertices if v != u)
        for u in vertices
    }
    adjacent_common = {
        internal_common_neighbors(edges, u, v, vertices)
        for u, v in combinations(vertices, 2)
        if adjacent(edges, u, v)
    }
    nonadjacent_common = {
        internal_common_neighbors(edges, u, v, vertices)
        for u, v in combinations(vertices, 2)
        if not adjacent(edges, u, v)
    }
    return {
        "degree_values": sorted(degrees),
        "adjacent_common_neighbor_values": sorted(adjacent_common),
        "nonadjacent_common_neighbor_values": sorted(nonadjacent_common),
    }


def bootstrap_closure(
    vertices: Iterable[int],
    edges: set[tuple[int, int]],
    seed: Iterable[int],
) -> tuple[int, ...]:
    infected = set(seed)
    vertices = tuple(vertices)
    while True:
        added = {
            vertex
            for vertex in vertices
            if vertex not in infected
            and sum(adjacent(edges, vertex, other) for other in infected) >= 2
        }
        if not added:
            return tuple(sorted(infected))
        infected |= added


def closure_parameter_census() -> list[dict[str, object]]:
    records = []
    for degree in range(2, K + 1, 2):
        order = 1 + degree * degree // 2
        discriminant = 4 * degree - 7
        square_root = math.isqrt(discriminant)
        numerator = 2 * degree - (order - 1)
        if square_root * square_root != discriminant:
            feasible = numerator == 0
            multiplicities = None
            reason = (
                "irrational eigenvalues would have unequal conjugate "
                "multiplicities"
            )
        else:
            first = Fraction(
                (order - 1) * square_root - numerator,
                2 * square_root,
            )
            second = Fraction(order - 1, 1) - first
            feasible = first.denominator == second.denominator == 1
            multiplicities = [str(first), str(second)]
            reason = (
                "integral eigenvalue multiplicities"
                if feasible
                else "nonintegral eigenvalue multiplicity"
            )
        records.append(
            {
                "degree": degree,
                "order": order,
                "eigen_discriminant": discriminant,
                "multiplicities": multiplicities,
                "parameter_feasible": feasible,
                "reason": reason,
                "role": (
                    "complete K3 case"
                    if degree == 2
                    else (
                        "proper nonedge closure"
                        if degree == 4
                        else ("ambient target" if degree == 14 else "excluded")
                    )
                ),
            }
        )
    return records


def build_result() -> dict[str, object]:
    enforce_memory_floor()
    tip_records = tip_graph_records()
    packaged_tips = [tip_profile_package(record) for record in tip_records]
    endpoint_records = [
        record
        for record in packaged_tips
        if record["prism_free_endpoint_admissible"]
    ]
    if len(endpoint_records) != 1:
        raise AssertionError("expected a unique endpoint tip relation")
    endpoint = endpoint_records[0]

    rook_points, rook_edges = rook_graph_3x3()
    rook_vertices = tuple(range(9))
    rook_nonedges = [
        pair for pair in combinations(rook_vertices, 2) if edge(*pair) not in rook_edges
    ]
    rook_closure_sizes = Counter(
        len(bootstrap_closure(rook_vertices, rook_edges, pair))
        for pair in rook_nonedges
    )
    rook_prisms = induced_prisms(rook_edges, rook_vertices)
    rook_n3s = induced_n3s(rook_edges, rook_vertices)
    forced_nine_edges = forced_nine_vertex_closure()
    forced_nine_parameters = exact_pair_parameters(
        forced_nine_edges, rook_vertices
    )

    parameter_census = closure_parameter_census()
    proper_feasible = [
        record
        for record in parameter_census
        if record["parameter_feasible"] and record["degree"] not in (2, K)
    ]

    result = {
        "schema_version": 1,
        "role": "proof_b",
        "claim_label": "DERIVED",
        "scope": (
            "Conditional bootstrap-percolation closure space for a "
            "hypothetical prism-free srg(99,14,1,2)"
        ),
        "parameters": {
            "v": V,
            "k": K,
            "lambda": LAMBDA,
            "mu": MU,
            "edges": EDGE_COUNT,
            "nonedges": NONEDGE_COUNT,
        },
        "source": {
            "metadata_path": "attempts/wave56-percolation-closure/source-metadata.json",
            "metadata_sha256": sha256_path(HERE / "source-metadata.json"),
            "primary_result_used": "Ibrahim-LaFayette-McCall Lemma 4.9",
            "theorem_4_19_rederived": True,
        },
        "closure_classification": {
            "parameter_census": parameter_census,
            "proper_parameter_feasible_cases": proper_feasible,
            "nonedge_closure_dichotomy": (
                "all 99 vertices, or the unique srg(9,4,1,2)=K3 square K3"
            ),
            "derivation": [
                "A nonedge seed rules out the K3 closure.",
                "mu=2 rules out the irregular closure in Theorem 4.8.",
                "The SRG parameter equation gives n'=1+k'^2/2.",
                "Exact eigenvalue multiplicities leave only k'=4 below k=14.",
                "Degree completion of the forced eight vertices uniquely adds one vertex adjacent to all four tips.",
            ],
            "forced_nine_vertex_reconstruction": {
                "tip_edges": [["t01", "t23"], ["t12", "t30"]],
                "ninth_vertex_neighbors": ["t01", "t12", "t23", "t30"],
                "edge_count": len(forced_nine_edges),
                "exact_pair_parameters": forced_nine_parameters,
                "rook_coordinate_map": {
                    "c0": [0, 0],
                    "c1": [0, 1],
                    "c2": [1, 1],
                    "c3": [1, 0],
                    "t01": [0, 2],
                    "t12": [2, 1],
                    "t23": [1, 2],
                    "t30": [2, 0],
                    "ninth": [2, 2],
                },
            },
        },
        "rook_graph_control": {
            "point_order": [list(point) for point in rook_points],
            "edge_count": len(rook_edges),
            "nonedge_count": len(rook_nonedges),
            "triangle_count": induced_triangle_count(rook_edges, rook_vertices),
            "induced_triangular_prism_count": len(rook_prisms),
            "induced_n3_count": len(rook_n3s),
            "nonedge_bootstrap_closure_size_histogram": {
                str(size): count
                for size, count in sorted(rook_closure_sizes.items())
            },
        },
        "global_exact_relations": {
            "variables": {
                "n3": "number of induced N3 copies",
                "P": "number of induced triangular prisms",
                "H": "number of induced K3 square K3 closures",
                "R": "number of nonpercolating nonedges",
                "S": "number of percolating nonedges",
            },
            "identities": [
                "n3 + 3*P = 4158",
                "R = 18*H",
                "S = 4158 - R",
            ],
            "proved_inequalities": [
                "H <= 231",
                "6*H <= P",
                "R <= 3*P = 4158 - n3",
                "S >= n3",
            ],
            "equality_condition": (
                "R=3*P (equivalently S=n3) iff every induced triangular "
                "prism lies in an induced K3 square K3 closure"
            ),
            "incidence_multiplicities": {
                "central_nonedges_per_N3": 2,
                "central_nonedges_per_triangular_prism": 6,
                "nonedges_per_K3_square_K3": 18,
                "triangular_prisms_per_K3_square_K3": 6,
                "K3_square_K3_containing_a_fixed_nonedge_at_most": 1,
                "K3_square_K3_containing_a_fixed_prism_at_most": 1,
            },
            "endpoint_specialization": {
                "n3": 4158,
                "P": 0,
                "H": 0,
                "R": 0,
                "S": 4158,
                "every_nonedge_2_percolates": True,
            },
            "percolation_number": {
                "range": [2, 3],
                "m_equals_3_iff": "H=231 (equivalently R=4158)",
                "m_equals_2_iff": "H<231 (equivalently some nonedge percolates)",
                "H_equals_0_iff": "every nonedge percolates",
                "three_set_argument": (
                    "if a nonedge closes to a 9-vertex rook graph, adding "
                    "any outside vertex forces a strictly larger closure, "
                    "which the closure census allows only at order 99"
                ),
            },
            "N3_percolation_boundary": {
                "induced_N3_in_K3_square_K3": 0,
                "each_N3_has_two_central_nonedges": True,
                "each_central_N3_nonedge_percolates": True,
                "reason": (
                    "a nonpercolating closure would be K3 square K3 and "
                    "would contain the induced N3, but that graph has none"
                ),
                "consequence": "n3>0 implies m(G,2)=2",
            },
        },
        "arbitrary_nonedge_early_waves": {
            "wave_0_seed": ["c0", "c2"],
            "wave_1_exact": ["c1", "c3"],
            "wave_2_exact": ["t01", "t12", "t23", "t30"],
            "tip_pair_order": [
                [LABELS[u], LABELS[v]] for u, v in TIP_PAIRS
            ],
            "all_labeled_tip_graph_count": 64,
            "lambda_mu_admissible_tip_graph_count": len(packaged_tips),
            "tip_graphs": packaged_tips,
            "endpoint": {
                "admissible_tip_graph_count": len(endpoint_records),
                "tip_edges": endpoint["tip_edges"],
                "allowed_outside_mask_count": endpoint[
                    "allowed_outside_mask_count"
                ],
                "next_wave_profile_count": endpoint[
                    "next_wave_profile_count"
                ],
                "formal_D4_orbit_count": len(endpoint["formal_D4_orbits"]),
                "next_wave_size_histogram": endpoint[
                    "next_wave_size_histogram"
                ],
                "next_wave_arity_triple_histogram": endpoint[
                    "next_wave_arity_triple_histogram"
                ],
                "pair_deficit_equation": "x2 + 3*x3 + 6*x4 = 16",
                "total_infected_after_wave_3_range": [16, 24],
            },
        },
        "status": {
            "local_tip_and_profile_census": "DERIVED_PENDING_VERIFIER",
            "global_counting_contradiction": "NOT_FOUND",
            "smaller_exact_csp": (
                "23 masks and 35 labeled endpoint profiles; 11 formal D4 "
                "label-orbits"
            ),
            "endpoint_excluded": False,
            "upper_bound_improved_below_4158": False,
            "conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "resources": {
            "minimum_free_memory_percent": MIN_FREE_MEMORY_PERCENT,
            "free_memory_floor_passed": True,
        },
        "limitations": [
            "Discovery cannot verify itself.",
            "The 35 endpoint profiles satisfy local pair deficits only; they are not completed graphs.",
            "Formal D4 grouping is label bookkeeping, not a graph automorphism assumption.",
            "The source closure lemma is cited; target arithmetic is independently rederived.",
            "No endpoint contradiction, graph, stricter n3 upper bound, or novelty claim follows.",
        ],
    }

    expected = {
        "tip_records": 4,
        "endpoint_tip_records": 1,
        "endpoint_masks": 23,
        "endpoint_profiles": 35,
        "endpoint_orbits": 11,
        "rook_prisms": 6,
        "rook_n3s": 0,
        "proper_feasible": 1,
    }
    observed = {
        "tip_records": len(packaged_tips),
        "endpoint_tip_records": len(endpoint_records),
        "endpoint_masks": endpoint["allowed_outside_mask_count"],
        "endpoint_profiles": endpoint["next_wave_profile_count"],
        "endpoint_orbits": len(endpoint["formal_D4_orbits"]),
        "rook_prisms": len(rook_prisms),
        "rook_n3s": len(rook_n3s),
        "proper_feasible": len(proper_feasible),
    }
    if observed != expected:
        raise AssertionError({"expected": expected, "observed": observed})
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path)
    group.add_argument("--verify", type=Path)
    options = parser.parse_args()

    text = canonical_json(build_result())
    if options.output is not None:
        options.output.write_text(text, encoding="utf-8", newline="\n")
        print(f"WROTE {options.output}")
        print(f"sha256={sha256_bytes(text.encode('utf-8'))}")
        return 0
    expected = options.verify.read_text(encoding="utf-8")
    if expected != text:
        print(f"MISMATCH {options.verify}")
        return 1
    print(f"VERIFIED {options.verify}")
    print(f"sha256={sha256_bytes(text.encode('utf-8'))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
