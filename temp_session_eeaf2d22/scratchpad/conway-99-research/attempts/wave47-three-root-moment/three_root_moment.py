#!/usr/bin/env python3
"""Exact three-labelled-root, order-five flag moments for Conway-99.

Each flag has three pointwise-labelled roots and two unordered free vertices.
Products of two flags therefore use five, six, or seven vertices.  Every
coefficient is obtained by direct labelled embedding enumeration; no
automorphism of a hypothetical target graph is assumed.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import importlib.util
import itertools
import json
import math
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
W45_PATH = ROOT / "attempts/wave45-flag-moment/flag_moment-v1.py"
W45_COEFFICIENTS = (
    ROOT / "attempts/wave45-flag-moment/checkpoint-v1-moment-coefficients.json"
)
W45_CHECKPOINT = (
    ROOT
    / "attempts/wave45-flag-moment/checkpoint-v1-seed0-17cuts-15witnesses.json"
)
W45_STORED = (
    ROOT
    / "attempts/wave45-flag-moment/checkpoint-v1-stored-witness-results.json"
)
W43_WITNESS = ROOT / "attempts/wave43-seven-deck-endpoint/exact-results.json"
W44_WITNESS = ROOT / "attempts/wave44-rooted-flags/rooted-witness.json"

EXPECTED_INPUT_SHA256 = {
    W45_PATH: "21ed58592eeced3433fdff0b98ae4f963b269ed0b39be05322f1dac42ce1be70",
    W45_COEFFICIENTS: "ffcf9f9942446d66c3559d97954217af3ba17c1978ea9417c6e99920d4a45420",
    W45_CHECKPOINT: "96a50f9add4b12b2c86587da29ade8b9da34f88a7b7617c048ffb7139c12b64b",
    W45_STORED: "2c55b6ab1af9cac7d8f5800466abadb8c0c2603b5f96013d3fd160b6816c24df",
    W43_WITNESS: "06b498a736a511a7d6f5912bd4686e5d4eb30f4041477e3ee9cbc1704f1757c8",
    W44_WITNESS: "9be153b2487c3e07e20bffeb7ee6c890e69caa6e8d6b6e2936fbc5d8927bd5b9",
}

N = 99
K = 14
N3 = 4158
ROOT_COUNT = 3
FLAG_ORDER = 5
FREE_COUNT = 2
UNION_ORDERS = (5, 6, 7)
# Stop before the user's hard 15% floor is approached.  The five-point margin
# covers transient allocations between explicit continuation samples.
MIN_FREE_MEMORY_PERCENT = 20.0


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def sha256_json(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


for dependency, expected in EXPECTED_INPUT_SHA256.items():
    actual = sha256_file(dependency)
    if actual != expected:
        raise RuntimeError(f"frozen dependency changed: {dependency}: {actual} != {expected}")

W45 = load_module("wave47_frozen_wave45", W45_PATH)
W43 = W45.W43


def memory_sample(label: str) -> dict[str, object]:
    sample = W43.memory_sample(label)
    require(
        float(sample["free_percent_floor"]) >= MIN_FREE_MEMORY_PERCENT,
        f"{label}: memory floor violated",
    )
    return sample


@functools.lru_cache(maxsize=None)
def edge_positions(order: int) -> dict[tuple[int, int], int]:
    return W43.edge_positions(order)


def root_pattern(mask: int, order: int) -> int:
    """Return the three bits (01,02,12) induced by vertices 0,1,2."""
    positions = edge_positions(order)
    return sum(
        ((mask >> positions[edge]) & 1) << bit
        for bit, edge in enumerate(((0, 1), (0, 2), (1, 2)))
    )


@functools.lru_cache(maxsize=None)
def free_swap_maps() -> tuple[tuple[int, ...], ...]:
    positions = edge_positions(FLAG_ORDER)
    original_edges = W43.edges(FLAG_ORDER)
    maps = []
    for permutation in ((0, 1, 2, 3, 4), (0, 1, 2, 4, 3)):
        maps.append(
            tuple(
                positions[tuple(sorted((permutation[left], permutation[right])))]
                for left, right in original_edges
            )
        )
    return tuple(maps)


@functools.lru_cache(maxsize=None)
def canonical_flag(mask: int) -> int:
    """Canonicalize only the two free vertices; roots stay pointwise fixed."""
    return min(W43.transform_mask(mask, mapping) for mapping in free_swap_maps())


def induced_relabelled_mask(
    mask: int,
    order: int,
    roots: Sequence[int],
    free_vertices: Sequence[int],
) -> int:
    chosen = tuple(roots) + tuple(free_vertices)
    original_positions = edge_positions(order)
    result = 0
    for new_position, (left_index, right_index) in enumerate(W43.edges(len(chosen))):
        edge = tuple(sorted((chosen[left_index], chosen[right_index])))
        if mask >> original_positions[edge] & 1:
            result |= 1 << new_position
    return result


def root_embedding_count_at_n99(pattern: int) -> int:
    """Number of ordered triples inducing one exact labelled root pattern."""
    edge_count = pattern.bit_count()
    if edge_count == 0:
        independent_unordered = (
            math.comb(N, 3)
            - N * K // 6
            - (N * (N - 1 - K) // 2) * 2
            - (N * K // 2) * (N - 2 * K + 1)
        )
        return 6 * independent_unordered
    if edge_count == 1:
        # Every edge has n-(2k-lambda)=n-2k+1 vertices adjacent to neither end.
        return 2 * (N * K // 2) * (N - 2 * K + 1)
    if edge_count == 2:
        # Every nonedge has mu=2 common neighbors; each labelled P3 pattern
        # receives the two orderings that swap its endpoints.
        return 2 * (N * (N - 1 - K) // 2) * 2
    # There are nk*lambda/6 triangles and six ordered embeddings per triangle.
    return 6 * (N * K // 6)


@dataclass(frozen=True)
class Family:
    root_pattern: int
    flags: tuple[int, ...]

    @property
    def name(self) -> str:
        return f"root_{self.root_pattern:03b}"

    @property
    def root_embeddings_at_target(self) -> int:
        return root_embedding_count_at_n99(self.root_pattern)

    @property
    def free_subsets_per_root_at_target(self) -> int:
        return math.comb(N - ROOT_COUNT, FREE_COUNT)

    @property
    def normalized_denominator(self) -> int:
        return (
            self.root_embeddings_at_target
            * self.free_subsets_per_root_at_target**2
        )


def flag_universe(pattern: int) -> tuple[int, ...]:
    flags = {
        canonical_flag(mask)
        for mask in range(1 << math.comb(FLAG_ORDER, 2))
        if root_pattern(mask, FLAG_ORDER) == pattern
        and W43.locally_admissible(mask, FLAG_ORDER)
    }
    return tuple(sorted(flags))


def families() -> tuple[Family, ...]:
    result = tuple(Family(pattern, flag_universe(pattern)) for pattern in range(8))
    require(
        tuple(len(family.flags) for family in result)
        == (64, 56, 56, 42, 56, 42, 42, 20),
        "three-root flag census changed",
    )
    require(
        sum(family.root_embeddings_at_target for family in result)
        == N * (N - 1) * (N - 2),
        "labelled root patterns do not partition ordered triples",
    )
    return result


@functools.lru_cache(maxsize=None)
def roots_by_pattern(
    mask: int, order: int
) -> tuple[tuple[tuple[int, int, int], ...], ...]:
    positions = edge_positions(order)
    groups: list[list[tuple[int, int, int]]] = [[] for _ in range(8)]
    for roots in itertools.permutations(range(order), ROOT_COUNT):
        pattern = 0
        for bit, (left_index, right_index) in enumerate(((0, 1), (0, 2), (1, 2))):
            edge = tuple(sorted((roots[left_index], roots[right_index])))
            pattern |= ((mask >> positions[edge]) & 1) << bit
        groups[pattern].append(roots)
    return tuple(tuple(group) for group in groups)


def roots_matching(
    mask: int, order: int, family: Family
) -> Iterable[tuple[int, int, int]]:
    yield from roots_by_pattern(mask, order)[family.root_pattern]


def coefficient_matrix_for_class(
    mask: int, order: int, family: Family
) -> list[list[int]]:
    index = {flag: position for position, flag in enumerate(family.flags)}
    result = [[0] * len(family.flags) for _ in family.flags]
    all_vertices = set(range(order))
    for roots in roots_matching(mask, order, family):
        remaining = tuple(sorted(all_vertices.difference(roots)))
        remaining_set = set(remaining)
        for first_free in itertools.combinations(remaining, FREE_COUNT):
            first_set = set(first_free)
            for second_free in itertools.combinations(remaining, FREE_COUNT):
                if first_set.union(second_free) != remaining_set:
                    continue
                first = canonical_flag(
                    induced_relabelled_mask(mask, order, roots, first_free)
                )
                second = canonical_flag(
                    induced_relabelled_mask(mask, order, roots, second_free)
                )
                require(first in index and second in index, "flag left its root family")
                result[index[first]][index[second]] += 1
    require(result == [list(row) for row in zip(*result)], "coefficient not symmetric")
    union_pair_count = {5: 1, 6: 6, 7: 6}[order]
    expected_total = len(roots_by_pattern(mask, order)[family.root_pattern]) * union_pair_count
    require(sum(map(sum, result)) == expected_total, "coefficient total mismatch")
    return result


def upper_entries(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [row, column, int(matrix[row][column])]
        for row in range(len(matrix))
        for column in range(row, len(matrix))
        if matrix[row][column]
    ]


def expand_upper(size: int, entries: Sequence[Sequence[int]]) -> list[list[int]]:
    result = [[0] * size for _ in range(size)]
    for row, column, value in entries:
        result[int(row)][int(column)] = int(value)
        result[int(column)][int(row)] = int(value)
    return result


def frozen_classes() -> dict[int, tuple[int, ...]]:
    payload = json.loads(W45_COEFFICIENTS.read_text(encoding="utf-8"))
    records = payload["families"]["vertex"]["class_coefficients"]
    classes = {
        order: tuple(
            sorted(
                int(record["canonical_mask"])
                for record in records
                if int(record["order"]) == order
            )
        )
        for order in range(4, 8)
    }
    require(
        tuple(len(classes[order]) for order in range(4, 8)) == (9, 21, 62, 208),
        "frozen class census changed",
    )
    require(
        all(
            W43.locally_admissible(mask, order)
            for order in classes
            for mask in classes[order]
        ),
        "frozen stream contains a locally inadmissible class",
    )
    return classes


def build_coefficients(
    family_values: Sequence[Family], classes: dict[int, tuple[int, ...]]
) -> dict[str, object]:
    output: dict[str, object] = {
        "format": "wave47-three-root-five-vertex-flag-coefficients-v1",
        "convention": {
            "root_labels": [0, 1, 2],
            "root_pattern_bits": ["01", "02", "12"],
            "root_labels_fixed_pointwise": True,
            "free_vertices": "unordered pair",
            "pair_of_flags": "ordered",
            "automorphism_division": "none",
            "union_orders": list(UNION_ORDERS),
        },
        "input_freeze": {
            str(path.relative_to(ROOT)).replace("\\", "/"): digest
            for path, digest in EXPECTED_INPUT_SHA256.items()
        },
        "class_streams": {
            str(order): {
                "count": len(classes[order]),
                "sha256": sha256_json(list(classes[order])),
            }
            for order in UNION_ORDERS
        },
        "families": {},
    }
    output_families: dict[str, object] = {}
    for family in family_values:
        memory_sample(f"wave47-before-coefficients-{family.name}")
        print(f"coefficients {family.name} start", flush=True)
        records = []
        for order in UNION_ORDERS:
            for mask in classes[order]:
                matrix = coefficient_matrix_for_class(mask, order, family)
                records.append(
                    {
                        "order": order,
                        "canonical_mask": mask,
                        "upper_entries": upper_entries(matrix),
                    }
                )
        output_families[family.name] = {
            "root_pattern": family.root_pattern,
            "root_pattern_binary": f"{family.root_pattern:03b}",
            "root_embeddings_at_n99": family.root_embeddings_at_target,
            "free_subsets_per_root_at_n99": family.free_subsets_per_root_at_target,
            "normalization_denominator_at_n99": family.normalized_denominator,
            "matrix_size": len(family.flags),
            "flags": list(family.flags),
            "class_coefficients": records,
        }
        print(f"coefficients {family.name} finish", flush=True)
    output["families"] = output_families
    output["payload_sha256_without_this_field"] = sha256_json(output)
    return output


def coefficient_lookup(
    coefficients: dict[str, object], family: Family
) -> dict[tuple[int, int], list[list[int]]]:
    record = coefficients["families"][family.name]
    size = int(record["matrix_size"])
    return {
        (int(item["order"]), int(item["canonical_mask"])): expand_upper(
            size, item["upper_entries"]
        )
        for item in record["class_coefficients"]
    }


def add_scaled(
    destination: list[list[int]], source: Sequence[Sequence[int]], scalar: int
) -> None:
    if scalar == 0:
        return
    for row in range(len(destination)):
        for column in range(len(destination)):
            destination[row][column] += scalar * int(source[row][column])


def evaluate(
    coefficients: dict[str, object],
    family: Family,
    counts: dict[int, dict[int, int]],
) -> list[list[int]]:
    lookup = coefficient_lookup(coefficients, family)
    matrix = [[0] * len(family.flags) for _ in family.flags]
    for order in UNION_ORDERS:
        for mask, count in counts[order].items():
            add_scaled(matrix, lookup[(order, mask)], int(count))
    require(matrix == [list(row) for row in zip(*matrix)], "moment not symmetric")
    require(
        sum(map(sum, matrix)) == family.normalized_denominator,
        f"{family.name}: all-ones normalization failed",
    )
    return matrix


def exact_quadratic(matrix: Sequence[Sequence[int]], vector: Sequence[int]) -> int:
    return sum(
        int(vector[row]) * int(matrix[row][column]) * int(vector[column])
        for row in range(len(vector))
        for column in range(len(vector))
    )


def primitive_vector(vector: Sequence[int]) -> list[int]:
    values = [int(value) for value in vector]
    divisor = math.gcd(*map(abs, values))
    if divisor:
        values = [value // divisor for value in values]
    first = next((value for value in values if value), 1)
    if first < 0:
        values = [-value for value in values]
    return values


def negative_direction_record(
    matrix: Sequence[Sequence[int]], family: Family
) -> dict[str, object]:
    array = np.asarray(matrix, dtype=np.float64)
    eigenvalues, eigenvectors = np.linalg.eigh(array)
    scale = max(1.0, float(np.linalg.norm(array, ord=2)))
    negative_indices = [
        index for index, value in enumerate(eigenvalues) if value < -1e-8 * scale
    ]
    exact_directions = []
    for index in negative_indices:
        try:
            vector, quadratic = W45.rationalize_negative_vector(
                matrix, eigenvectors[:, index]
            )
        except AssertionError:
            continue
        vector = primitive_vector(vector)
        quadratic = exact_quadratic(matrix, vector)
        require(quadratic < 0, "rationalized direction is not negative")
        exact_directions.append(
            {
                "eigenvalue_index": index,
                "vector": vector,
                "quadratic_numerator": quadratic,
            }
        )
    return {
        "matrix_size": len(matrix),
        "matrix_sha256": sha256_json(matrix),
        "normalization_denominator": family.normalized_denominator,
        "minimum_raw_eigenvalue_float": float(eigenvalues[0]),
        "minimum_normalized_eigenvalue_float": float(
            eigenvalues[0] / family.normalized_denominator
        ),
        "numerical_negative_eigenvalue_count": len(negative_indices),
        "exact_negative_direction_count": len(exact_directions),
        "status": (
            "EXACTLY_INDEFINITE"
            if exact_directions
            else "NO_EXACT_NEGATIVE_DIRECTION_FOUND"
        ),
        "exact_negative_directions": exact_directions,
    }


def quadratic_coefficient(
    matrix: Sequence[Sequence[int]], vector: Sequence[int]
) -> int:
    return exact_quadratic(matrix, vector)


def cut_from_direction(
    coefficients: dict[str, object],
    family: Family,
    lower: dict[int, dict[int, int]],
    classes7: Sequence[int],
    vector: Sequence[int],
    source: str,
    source_support_sha256: str,
) -> dict[str, object]:
    lookup = coefficient_lookup(coefficients, family)
    constant = sum(
        int(count) * quadratic_coefficient(lookup[(order, mask)], vector)
        for order in (5, 6)
        for mask, count in lower[order].items()
    )
    values7 = {
        mask: quadratic_coefficient(lookup[(7, mask)], vector)
        for mask in classes7
    }
    divisor = math.gcd(abs(constant), *(abs(value) for value in values7.values()))
    divisor = max(divisor, 1)
    core = {
        "family": family.name,
        "root_pattern": family.root_pattern,
        "vector": list(map(int, vector)),
        "primitive_divisor": divisor,
        "constant": constant // divisor,
        "coefficients": [
            {"canonical_mask": mask, "coefficient": value // divisor}
            for mask, value in values7.items()
            if value
        ],
    }
    return {
        **core,
        "source": source,
        "source_support_sha256": source_support_sha256,
        "cut_sha256": sha256_json(core),
    }


def support_counts(
    support: Sequence[dict[str, object]], classes7: Sequence[int]
) -> dict[int, int]:
    counts = {mask: 0 for mask in classes7}
    for record in support:
        mask = int(record["canonical_mask"])
        count = int(record["count"])
        require(mask in counts and counts[mask] == 0 and count > 0, "bad support")
        counts[mask] = count
    require(sum(counts.values()) == math.comb(N, 7), "seven-count total changed")
    return counts


def source_targets(classes7: Sequence[int]) -> list[dict[str, object]]:
    result = []
    for name, path in (
        ("wave43_unrooted", W43_WITNESS),
        ("wave44_rooted", W44_WITNESS),
    ):
        payload = json.loads(path.read_text(encoding="utf-8"))
        certificate = payload.get("certificate", payload)
        support = certificate["support"]
        result.append(
            {
                "name": name,
                "input_path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "input_sha256": sha256_file(path),
                "support_sha256": sha256_json(support),
                "counts7": support_counts(support, classes7),
            }
        )
    checkpoint = json.loads(W45_CHECKPOINT.read_text(encoding="utf-8"))
    for witness in checkpoint["witnesses"]:
        support = witness["support"]
        computed = sha256_json(support)
        require(computed == witness["support_sha256"], "Wave45 support hash changed")
        result.append(
            {
                "name": f"wave45_iteration_{int(witness['iteration'])}",
                "input_path": str(W45_CHECKPOINT.relative_to(ROOT)).replace("\\", "/"),
                "input_sha256": sha256_file(W45_CHECKPOINT),
                "support_sha256": computed,
                "counts7": support_counts(support, classes7),
            }
        )
    require(len(result) == 17, "expected two stored plus fifteen Wave45 witnesses")
    return result


@functools.lru_cache(maxsize=None)
def canonical_unrooted(mask: int, order: int) -> int:
    return min(
        W43.transform_mask(mask, mapping)
        for mapping in unrooted_maps(order)
    )


@functools.lru_cache(maxsize=None)
def unrooted_maps(order: int) -> tuple[tuple[int, ...], ...]:
    return W43.permutation_bit_maps(order)


def mask_from_graph(adjacency: Sequence[set[int]], vertices: Sequence[int]) -> int:
    mask = 0
    for position, (left_index, right_index) in enumerate(W43.edges(len(vertices))):
        if vertices[right_index] in adjacency[vertices[left_index]]:
            mask |= 1 << position
    return mask


def induced_census(
    adjacency: Sequence[set[int]], classes: dict[int, tuple[int, ...]]
) -> dict[int, dict[int, int]]:
    result = {}
    for order in UNION_ORDERS:
        counts: Counter[int] = Counter()
        allowed = set(classes[order])
        for vertices in itertools.combinations(range(len(adjacency)), order):
            canonical = canonical_unrooted(mask_from_graph(adjacency, vertices), order)
            require(canonical in allowed, "control induced a forbidden local class")
            counts[canonical] += 1
        result[order] = dict(counts)
    return result


def direct_gram(adjacency: Sequence[set[int]], family: Family) -> list[list[int]]:
    index = {flag: position for position, flag in enumerate(family.flags)}
    matrix = [[0] * len(family.flags) for _ in family.flags]
    order = len(adjacency)
    full_mask = mask_from_graph(adjacency, tuple(range(order)))
    for roots in roots_matching(full_mask, order, family):
        remaining = tuple(vertex for vertex in range(order) if vertex not in roots)
        vector = [0] * len(family.flags)
        for free in itertools.combinations(remaining, FREE_COUNT):
            flag = canonical_flag(
                induced_relabelled_mask(full_mask, order, roots, free)
            )
            vector[index[flag]] += 1
        for row, left in enumerate(vector):
            if left:
                for column, right in enumerate(vector):
                    if right:
                        matrix[row][column] += left * right
    return matrix


def root_embedding_count_in_graph(
    adjacency: Sequence[set[int]], family: Family
) -> int:
    full_mask = mask_from_graph(adjacency, tuple(range(len(adjacency))))
    return sum(1 for _ in roots_matching(full_mask, len(adjacency), family))


def control_record(
    name: str,
    adjacency: Sequence[set[int]],
    coefficients: dict[str, object],
    family_values: Sequence[Family],
    classes: dict[int, tuple[int, ...]],
) -> dict[str, object]:
    census = induced_census(adjacency, classes)
    family_records = {}
    for family in family_values:
        expanded = [[0] * len(family.flags) for _ in family.flags]
        lookup = coefficient_lookup(coefficients, family)
        for order in UNION_ORDERS:
            for mask, count in census[order].items():
                add_scaled(expanded, lookup[(order, mask)], count)
        direct = direct_gram(adjacency, family)
        require(direct == expanded, f"{name}/{family.name}: expansion mismatch")
        expected_total = (
            root_embedding_count_in_graph(adjacency, family)
            * math.comb(len(adjacency) - ROOT_COUNT, FREE_COUNT) ** 2
        )
        require(sum(map(sum, direct)) == expected_total, "control normalization")
        family_records[family.name] = {
            "direct_equals_unrooted_expansion": True,
            "matrix_sha256": sha256_json(direct),
            "root_embeddings": root_embedding_count_in_graph(adjacency, family),
            "all_ones_quadratic": sum(map(sum, direct)),
            "exact_psd_reason": "direct sum of integer outer products",
        }
    return {
        "name": name,
        "order": len(adjacency),
        "induced_subset_totals": {
            str(order): sum(census[order].values()) for order in UNION_ORDERS
        },
        "families": family_records,
    }


def evaluate_targets(
    coefficients: dict[str, object],
    family_values: Sequence[Family],
    classes: dict[int, tuple[int, ...]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    lower_all = W45.target_lower_counts(classes)
    lower = {5: lower_all[5], 6: lower_all[6]}
    targets = source_targets(classes[7])
    target_records = []
    cuts: list[dict[str, object]] = []
    for target in targets:
        memory_sample(f"wave47-before-target-{target['name']}")
        counts = {5: lower[5], 6: lower[6], 7: target["counts7"]}
        family_records = {}
        for family in family_values:
            matrix = evaluate(coefficients, family, counts)
            spectral = negative_direction_record(matrix, family)
            family_records[family.name] = spectral
            for direction_index, direction in enumerate(
                spectral["exact_negative_directions"]
            ):
                cut = cut_from_direction(
                    coefficients,
                    family,
                    lower,
                    classes[7],
                    direction["vector"],
                    str(target["name"]),
                    str(target["support_sha256"]),
                )
                cut_value = cut["constant"] + sum(
                    item["coefficient"] * target["counts7"][item["canonical_mask"]]
                    for item in cut["coefficients"]
                )
                require(cut_value < 0, "new PSD cut does not separate its source")
                cut["source_direction_index"] = direction_index
                cut["source_cut_value"] = cut_value
                cuts.append(cut)
        target_records.append(
            {
                key: value
                for key, value in target.items()
                if key != "counts7"
            }
            | {
                "family_results": family_records,
                "exactly_indefinite_family_count": sum(
                    record["status"] == "EXACTLY_INDEFINITE"
                    for record in family_records.values()
                ),
            }
        )
    require(cuts, "three-root layer found no exact separating direction")
    unique_by_sha: dict[str, dict[str, object]] = {}
    for cut in cuts:
        unique_by_sha.setdefault(str(cut["cut_sha256"]), cut)
    return target_records, list(unique_by_sha.values())


def compute() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    samples = [memory_sample("wave47-start")]
    classes = frozen_classes()
    family_values = families()
    samples.append(memory_sample("wave47-after-flags"))
    coefficients = build_coefficients(family_values, classes)
    print("coefficient construction complete", flush=True)
    samples.append(memory_sample("wave47-after-coefficients"))

    print("control calibration start", flush=True)
    controls = [
        control_record(
            "Petersen",
            W45.petersen_graph(),
            coefficients,
            family_values,
            classes,
        ),
        control_record(
            "Clebsch",
            W45.clebsch_graph(),
            coefficients,
            family_values,
            classes,
        ),
    ]
    print("control calibration complete", flush=True)
    samples.append(memory_sample("wave47-after-controls"))
    print("immutable witness evaluation start", flush=True)
    targets, cuts = evaluate_targets(coefficients, family_values, classes)
    print("immutable witness evaluation complete", flush=True)
    samples.append(memory_sample("wave47-finish"))

    result = {
        "format": "wave47-three-root-five-vertex-flag-results-v1",
        "role": "construction",
        "claim_label": "DERIVED",
        "scope": (
            "Exact finite Gram constraints for every labelled three-vertex "
            "root type and locally admissible five-vertex flag, evaluated on "
            "the 17 immutable Wave45-v1 endpoint count witnesses."
        ),
        "parameters": {"n": N, "k": K, "lambda": 1, "mu": 2, "n3": N3},
        "coefficient_model": {
            "file": "attempts/wave47-three-root-moment/coefficients.json",
            "payload_sha256": coefficients["payload_sha256_without_this_field"],
            "family_count": len(family_values),
            "matrix_sizes": {
                family.name: len(family.flags) for family in family_values
            },
            "root_embeddings_at_n99": {
                family.name: family.root_embeddings_at_target
                for family in family_values
            },
            "union_orders": list(UNION_ORDERS),
        },
        "controls": controls,
        "targets": targets,
        "cut_ledger": {
            "file": "attempts/wave47-three-root-moment/cuts.json",
            "generated_cut_count_before_deduplication": sum(
                record["exact_negative_direction_count"]
                for target in targets
                for record in target["family_results"].values()
            ),
            "unique_cut_count": len(cuts),
            "all_source_values_strictly_negative": all(
                int(cut["source_cut_value"]) < 0 for cut in cuts
            ),
        },
        "conclusion": {
            "all_17_immutable_witnesses_refuted_by_three_root_layer": all(
                target["exactly_indefinite_family_count"] > 0 for target in targets
            ),
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "graph_constructed": False,
            "full_psd_constrained_count_system_tested": False,
        },
        "limitations": [
            "Each exact negative direction refutes only its source aggregate witness.",
            "The finite cut ledger is not a complete search of the integer count region.",
            "A surviving aggregate moment vector would still not construct a graph.",
            "No target-graph automorphism was assumed; root labels remain pointwise fixed.",
        ],
        "memory_samples": samples,
    }
    cuts_payload = {
        "format": "wave47-three-root-psd-cuts-v1",
        "claim_label": "DERIVED",
        "inequality_convention": "constant + sum(coefficient[H] * x_H) >= 0",
        "cuts": cuts,
        "scope_wall": {
            "endpoint_n3_4158": "UNKNOWN",
            "complete_search": False,
        },
    }
    return coefficients, result, cuts_payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=HERE)
    arguments = parser.parse_args()
    arguments.output_dir.mkdir(parents=True, exist_ok=True)
    coefficients, results, cuts = compute()
    write_json(arguments.output_dir / "coefficients.json", coefficients)
    write_json(arguments.output_dir / "results.json", results)
    write_json(arguments.output_dir / "cuts.json", cuts)
    print(
        json.dumps(
            {
                "claim_label": results["claim_label"],
                "targets": len(results["targets"]),
                "all_targets_refuted": results["conclusion"][
                    "all_17_immutable_witnesses_refuted_by_three_root_layer"
                ],
                "unique_cuts": results["cut_ledger"]["unique_cut_count"],
                "endpoint_n3_4158": results["conclusion"]["endpoint_n3_4158"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
