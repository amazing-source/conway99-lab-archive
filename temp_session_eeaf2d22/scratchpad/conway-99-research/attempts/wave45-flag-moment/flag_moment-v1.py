#!/usr/bin/env python3
"""Exact finite flag-moment matrices for the Conway-99 endpoint relaxation.

The matrices are finite Gram matrices, including every overlap size.  Their
entries are expanded as exact integer linear combinations of unrooted induced
graph counts of orders four through seven.
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
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
W43_CHECKER = (
    ROOT / "verification/wave43-seven-deck-endpoint/independent_check.py"
)
W43_WITNESS = ROOT / "attempts/wave43-seven-deck-endpoint/exact-results.json"
W44_WITNESS = ROOT / "attempts/wave44-rooted-flags/rooted-witness.json"
EXPECTED_EXTERNAL_SHA256 = {
    W43_CHECKER: "324a4b84c081c8d2ad8a6a11bae45e0327c03ee2158036156c27efa66fcf790b",
    W43_WITNESS: "06b498a736a511a7d6f5912bd4686e5d4eb30f4041477e3ee9cbc1704f1757c8",
    W44_WITNESS: "9be153b2487c3e07e20bffeb7ee6c890e69caa6e8d6b6e2936fbc5d8927bd5b9",
}

N = 99
K = 14
N3 = 4158
MIN_FREE_MEMORY_PERCENT = 15.0

L_TO_CANONICAL_POSITIONS = (0, 1, 5, 2, 6, 3, 4, 8, 7)
M_TO_CANONICAL_POSITIONS = (
    0, 1, 2, 6, 3, 9, 7, 5, 4, 12, 10, 8, 13, 16, 15, 14, 11, 19, 18, 20, 17
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


for external_path, expected_digest in EXPECTED_EXTERNAL_SHA256.items():
    actual_digest = hashlib.sha256(external_path.read_bytes()).hexdigest()
    if actual_digest != expected_digest:
        raise RuntimeError(
            f"frozen v1 dependency changed: {external_path} "
            f"{actual_digest} != {expected_digest}"
        )

W43 = load_module("wave45_verified_w43_checker", W43_CHECKER)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def sha256_json(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def memory_sample(label: str) -> dict[str, object]:
    sample = W43.memory_sample(label)
    require(
        float(sample["free_percent_floor"]) >= MIN_FREE_MEMORY_PERCENT,
        "memory floor violated",
    )
    return sample


def mask_from_graph(adjacency: Sequence[set[int]], vertices: Sequence[int]) -> int:
    mask = 0
    position = 0
    for left_index, left in enumerate(vertices):
        for right in vertices[left_index + 1 :]:
            if right in adjacency[left]:
                mask |= 1 << position
            position += 1
    return mask


def induced_relabelled_mask(
    mask: int,
    order: int,
    roots: Sequence[int],
    free_vertices: Sequence[int],
) -> int:
    chosen = tuple(roots) + tuple(free_vertices)
    result = 0
    new_position = 0
    original_positions = W43.edge_positions(order)
    for left_index, left in enumerate(chosen):
        for right in chosen[left_index + 1 :]:
            original_edge = tuple(sorted((left, right)))
            if mask >> original_positions[original_edge] & 1:
                result |= 1 << new_position
            new_position += 1
    return result


@functools.lru_cache(maxsize=None)
def flag_permutation_maps(root_count: int, order: int = 4) -> tuple[tuple[int, ...], ...]:
    original_edges = W43.edges(order)
    positions = W43.edge_positions(order)
    free = tuple(range(root_count, order))
    maps = []
    for free_permutation in itertools.permutations(free):
        permutation = tuple(range(root_count)) + free_permutation
        maps.append(
            tuple(
                positions[tuple(sorted((permutation[left], permutation[right])))]
                for left, right in original_edges
            )
        )
    return tuple(maps)


@functools.lru_cache(maxsize=None)
def canonical_flag(mask: int, root_count: int) -> int:
    return min(
        W43.transform_mask(mask, bit_map)
        for bit_map in flag_permutation_maps(root_count)
    )


@dataclass(frozen=True)
class Family:
    name: str
    root_count: int
    free_count: int
    root_relation: bool | None
    flags: tuple[int, ...]
    root_embeddings_at_target: int
    free_subsets_per_root_at_target: int

    @property
    def maximum_union_order(self) -> int:
        return self.root_count + 2 * self.free_count

    @property
    def normalized_denominator(self) -> int:
        return self.root_embeddings_at_target * self.free_subsets_per_root_at_target**2


def flag_universe(root_count: int, root_relation: bool | None) -> tuple[int, ...]:
    classes = set()
    for mask in range(1 << math.comb(4, 2)):
        if not W43.locally_admissible(mask, 4):
            continue
        relation = bool(mask & 1)  # edge (0,1) is bit zero in lexicographic order
        if root_count == 2 and relation != root_relation:
            continue
        classes.add(canonical_flag(mask, root_count))
    return tuple(sorted(classes))


def families() -> tuple[Family, ...]:
    return (
        Family(
            name="vertex",
            root_count=1,
            free_count=3,
            root_relation=None,
            flags=flag_universe(1, None),
            root_embeddings_at_target=N,
            free_subsets_per_root_at_target=math.comb(N - 1, 3),
        ),
        Family(
            name="ordered_edge",
            root_count=2,
            free_count=2,
            root_relation=True,
            flags=flag_universe(2, True),
            root_embeddings_at_target=N * K,
            free_subsets_per_root_at_target=math.comb(N - 2, 2),
        ),
        Family(
            name="ordered_nonedge",
            root_count=2,
            free_count=2,
            root_relation=False,
            flags=flag_universe(2, False),
            root_embeddings_at_target=N * (N - 1 - K),
            free_subsets_per_root_at_target=math.comb(N - 2, 2),
        ),
    )


def root_embeddings(mask: int, order: int, family: Family) -> Iterable[tuple[int, ...]]:
    if family.root_count == 1:
        yield from ((vertex,) for vertex in range(order))
        return
    for first in range(order):
        for second in range(order):
            if first == second:
                continue
            relation = W43.adjacency_rows(mask, order)[first] >> second & 1
            if bool(relation) == family.root_relation:
                yield (first, second)


def coefficient_matrix_for_class(
    mask: int,
    order: int,
    family: Family,
) -> tuple[tuple[int, ...], ...]:
    """Embedding coefficient for one unrooted H class."""
    flag_index = {flag: index for index, flag in enumerate(family.flags)}
    size = len(family.flags)
    result = [[0] * size for _ in range(size)]
    all_vertices = set(range(order))
    expected_union_free = order - family.root_count
    intersection = 2 * family.free_count - expected_union_free
    require(0 <= intersection <= family.free_count, "bad overlap order")

    for roots in root_embeddings(mask, order, family):
        remaining = tuple(sorted(all_vertices.difference(roots)))
        for first_free in itertools.combinations(remaining, family.free_count):
            first_set = set(first_free)
            for second_free in itertools.combinations(remaining, family.free_count):
                if first_set.union(second_free) != set(remaining):
                    continue
                first_mask = induced_relabelled_mask(mask, order, roots, first_free)
                second_mask = induced_relabelled_mask(mask, order, roots, second_free)
                first_flag = canonical_flag(first_mask, family.root_count)
                second_flag = canonical_flag(second_mask, family.root_count)
                result[flag_index[first_flag]][flag_index[second_flag]] += 1

    require(
        result == [list(row) for row in zip(*result)],
        f"{family.name} coefficient matrix is not symmetric",
    )
    return tuple(tuple(row) for row in result)


def upper_entries(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [row, column, matrix[row][column]]
        for row in range(len(matrix))
        for column in range(row, len(matrix))
        if matrix[row][column]
    ]


def expand_upper(size: int, entries: Sequence[Sequence[int]]) -> list[list[int]]:
    matrix = [[0] * size for _ in range(size)]
    for row, column, value in entries:
        matrix[row][column] = int(value)
        matrix[column][row] = int(value)
    return matrix


def four_counts() -> tuple[int, ...]:
    n, k = N, K
    common = n * k * (k - 2)
    values = (
        Fraction(common * (k - 4) * (k**3 - 6 * k**2 + 10 * k - 12), 192),
        Fraction(common * (k - 4) * (k**2 - 4 * k + 6), 16),
        Fraction(common * (k**2 - 6 * k + 10), 16),
        Fraction(common * (n - 3 * k + 4), 2),
        Fraction(common * (k - 3), 2),
        Fraction(common * (k - 4), 6),
        Fraction(common * (k - 4), 12),
        Fraction(common, 8),
        Fraction(common, 2),
    )
    require(all(value.denominator == 1 for value in values), "four-count nonintegral")
    return tuple(value.numerator for value in values)


def five_counts() -> tuple[int, ...]:
    n, k = N, K
    common = n * k * (k - 2)
    values = (
        Fraction(common * (k - 4) * (n - 4 * k + 6) * (k**3 - 6 * k**2 + 14 * k - 36), 960),
        Fraction(common * (k - 4) ** 2 * (k**3 - 8 * k**2 + 26 * k - 48), 96),
        Fraction(common * (k - 4) * (k**3 - 10 * k**2 + 38 * k - 60), 16),
        Fraction(common * (k - 4) * (k**3 - 10 * k**2 + 40 * k - 68), 32),
        Fraction(common * (k - 4) * (n - 4 * k + 8), 6),
        Fraction(common * (k - 4) * (k**2 - 8 * k + 20), 8),
        Fraction(common * (k - 4) * (k**2 - 7 * k + 16), 4),
        Fraction(common * (k - 4) * (n - 4 * k + 8), 24),
        Fraction(common * (k - 4) * (k - 6), 24),
        Fraction(common * (n - 4 * k + 8), 8),
        Fraction(common * (k - 4) ** 2, 2),
        Fraction(common * (k - 4) ** 2, 4),
        Fraction(common * (k**2 - 8 * k + 17), 2),
        Fraction(common * (k - 4) * (k - 6), 24),
        Fraction(common * (k - 4), 2),
        Fraction(common * (k - 3), 2),
        Fraction(common * (k - 4), 4),
        Fraction(common * (k - 4), 5),
        Fraction(common, 8),
        Fraction(common, 2),
        Fraction(common * (k - 4), 2),
    )
    require(all(value.denominator == 1 for value in values), "five-count nonintegral")
    return tuple(value.numerator for value in values)


def build_catalogues() -> dict[int, Any]:
    return {order: W43.build_complete_catalogue(order) for order in range(4, 8)}


def admissible_classes(catalogues: dict[int, Any]) -> dict[int, tuple[int, ...]]:
    result = {
        order: W43.locally_admissible_classes(catalogue)
        for order, catalogue in catalogues.items()
    }
    require(
        tuple(len(result[order]) for order in range(4, 8)) == (9, 21, 62, 208),
        "admissible census changed",
    )
    return result


def target_lower_counts(
    classes: dict[int, tuple[int, ...]],
) -> dict[int, dict[int, int]]:
    values4 = four_counts()
    values5 = five_counts()
    values6 = W43.evaluate_integral(W43.six_formulae(), N3)
    counts4 = {
        classes[4][position]: values4[source]
        for source, position in enumerate(L_TO_CANONICAL_POSITIONS)
    }
    counts5 = {
        classes[5][position]: values5[source]
        for source, position in enumerate(M_TO_CANONICAL_POSITIONS)
    }
    counts6 = dict(zip(W43.SOURCE_N_MASKS, values6))
    require(set(counts4) == set(classes[4]), "four-count mapping incomplete")
    require(set(counts5) == set(classes[5]), "five-count mapping incomplete")
    require(set(counts6) == set(classes[6]), "six-count mapping incomplete")
    require(sum(counts4.values()) == math.comb(N, 4), "four-count total")
    require(sum(counts5.values()) == math.comb(N, 5), "five-count total")
    require(sum(counts6.values()) == math.comb(N, 6), "six-count total")
    return {4: counts4, 5: counts5, 6: counts6}


def load_seven_counts(path: Path, classes7: Sequence[int]) -> dict[int, int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    certificate = payload.get("certificate", payload)
    support = certificate["support"]
    counts = {mask: 0 for mask in classes7}
    for record in support:
        mask, count = record["canonical_mask"], record["count"]
        require(mask in counts and counts[mask] == 0 and count > 0, "bad support")
        counts[mask] = count
    require(sum(counts.values()) == math.comb(N, 7), "seven-count total")
    return counts


def build_coefficients(
    families_value: Sequence[Family],
    classes: dict[int, tuple[int, ...]],
) -> dict[str, object]:
    payload: dict[str, object] = {
        "format": "wave45-exact-finite-flag-coefficients-v1",
        "convention": {
            "flag_size": 4,
            "free_subsets": "unordered",
            "pair_of_free_subsets": "ordered",
            "pair_roots": "ordered and labelled",
            "unrooted_variables": "number of induced vertex subsets of each canonical type",
            "automorphism_division": "none",
        },
        "families": {},
    }
    output_families: dict[str, object] = {}
    for family in families_value:
        records = []
        for order in range(4, family.maximum_union_order + 1):
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
            "root_count": family.root_count,
            "free_count": family.free_count,
            "root_relation": family.root_relation,
            "flags": list(family.flags),
            "matrix_size": len(family.flags),
            "maximum_union_order": family.maximum_union_order,
            "root_embeddings_at_n99": family.root_embeddings_at_target,
            "free_subsets_per_root_at_n99": family.free_subsets_per_root_at_target,
            "probability_normalization_denominator_at_n99": family.normalized_denominator,
            "class_coefficients": records,
        }
    payload["families"] = output_families
    return payload


def coefficient_lookup(
    coefficients: dict[str, object],
    family: Family,
) -> dict[tuple[int, int], list[list[int]]]:
    record = coefficients["families"][family.name]
    return {
        (entry["order"], entry["canonical_mask"]): expand_upper(
            record["matrix_size"], entry["upper_entries"]
        )
        for entry in record["class_coefficients"]
    }


def add_scaled_matrix(
    destination: list[list[int]],
    source: Sequence[Sequence[int]],
    scalar: int,
) -> None:
    for row in range(len(destination)):
        for column in range(len(destination)):
            destination[row][column] += scalar * source[row][column]


def evaluate_expansion(
    coefficients: dict[str, object],
    family: Family,
    counts: dict[int, dict[int, int]],
) -> list[list[int]]:
    size = len(family.flags)
    result = [[0] * size for _ in range(size)]
    lookup = coefficient_lookup(coefficients, family)
    for order in range(4, family.maximum_union_order + 1):
        for mask, count in counts[order].items():
            if count:
                add_scaled_matrix(result, lookup[(order, mask)], count)
    require(result == [list(row) for row in zip(*result)], "moment not symmetric")
    return result


def exact_quadratic(matrix: Sequence[Sequence[int]], vector: Sequence[int]) -> int:
    return sum(
        vector[row] * matrix[row][column] * vector[column]
        for row in range(len(vector))
        for column in range(len(vector))
    )


def exact_ldl_psd(matrix: Sequence[Sequence[int]]) -> dict[str, object]:
    """Exact unpivoted LDL^T test.

    For a PSD matrix, a zero residual pivot must have a zero residual column.
    Thus nonnegative pivots plus that zero-column condition are an exact PSD
    certificate.
    """
    size = len(matrix)
    lower = [[Fraction(int(row == column)) for column in range(size)] for row in range(size)]
    diagonal = [Fraction(0) for _ in range(size)]
    for pivot in range(size):
        diagonal[pivot] = Fraction(matrix[pivot][pivot]) - sum(
            lower[pivot][prior] ** 2 * diagonal[prior]
            for prior in range(pivot)
        )
        residuals = []
        for row in range(pivot + 1, size):
            residual = Fraction(matrix[row][pivot]) - sum(
                lower[row][prior] * lower[pivot][prior] * diagonal[prior]
                for prior in range(pivot)
            )
            residuals.append((row, residual))
        if diagonal[pivot] < 0:
            return {
                "is_psd": False,
                "failure": "negative_ldl_pivot",
                "pivot_index": pivot,
                "pivot": fraction_text(diagonal[pivot]),
            }
        if diagonal[pivot] == 0:
            nonzero = [(row, value) for row, value in residuals if value]
            if nonzero:
                return {
                    "is_psd": False,
                    "failure": "zero_pivot_nonzero_residual_column",
                    "pivot_index": pivot,
                    "first_nonzero_row": nonzero[0][0],
                    "first_nonzero_residual": fraction_text(nonzero[0][1]),
                }
            continue
        for row, residual in residuals:
            lower[row][pivot] = residual / diagonal[pivot]

    certificate = {
        "diagonal": [fraction_text(value) for value in diagonal],
        "lower_triangle": [
            [row, column, fraction_text(lower[row][column])]
            for row in range(size)
            for column in range(row)
            if lower[row][column]
        ],
    }
    return {
        "is_psd": True,
        "rank": sum(value > 0 for value in diagonal),
        "certificate_sha256": sha256_json(certificate),
        "certificate": certificate,
    }


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def rationalize_negative_vector(
    matrix: Sequence[Sequence[int]],
    eigenvector: np.ndarray,
) -> tuple[list[int], int]:
    candidates = []
    for scale in (10, 30, 100, 300, 1000, 3000, 10000, 100000):
        vector = [int(round(scale * value / np.max(np.abs(eigenvector)))) for value in eigenvector]
        if not any(vector):
            continue
        divisor = math.gcd(*map(abs, vector))
        if divisor:
            vector = [value // divisor for value in vector]
        first = next((value for value in vector if value), 1)
        if first < 0:
            vector = [-value for value in vector]
        quadratic = exact_quadratic(matrix, vector)
        if quadratic < 0:
            candidates.append((max(map(abs, vector)), sum(map(abs, vector)), vector, quadratic))
    if not candidates:
        raise AssertionError("negative numerical eigenvalue lacked an exact integer direction")
    _, _, vector, quadratic = min(candidates)
    return vector, quadratic


def integer_negative_directions(
    matrix: Sequence[Sequence[int]],
) -> tuple[tuple[list[int], int], ...]:
    array = np.asarray(matrix, dtype=np.float64)
    values, vectors = np.linalg.eigh(array)
    threshold = -1e-7 * max(1.0, np.linalg.norm(array, ord=2))
    directions = []
    seen = set()
    for index, eigenvalue in enumerate(values):
        if eigenvalue >= threshold:
            continue
        vector, quadratic = rationalize_negative_vector(matrix, vectors[:, index])
        key = tuple(vector)
        if key not in seen:
            directions.append((vector, quadratic))
            seen.add(key)
    return tuple(directions)


def integer_negative_direction(
    matrix: Sequence[Sequence[int]],
) -> tuple[list[int], int] | None:
    directions = integer_negative_directions(matrix)
    return directions[0] if directions else None


def spectral_record(
    matrix: Sequence[Sequence[int]],
    family: Family,
) -> dict[str, object]:
    array = np.asarray(matrix, dtype=np.float64)
    eigenvalues = np.linalg.eigvalsh(array)
    normalized = eigenvalues / family.normalized_denominator
    directions = integer_negative_directions(matrix)
    direction = directions[0] if directions else None
    result = {
        "matrix_size": len(matrix),
        "raw_matrix_sha256": sha256_json(matrix),
        "normalization_denominator": family.normalized_denominator,
        "minimum_raw_eigenvalue_float": float(eigenvalues[0]),
        "minimum_normalized_eigenvalue_float": float(normalized[0]),
        "maximum_normalized_eigenvalue_float": float(normalized[-1]),
        "numerical_negative_eigenvalue_count": int(
            np.sum(eigenvalues < -1e-7 * max(1.0, np.linalg.norm(array, ord=2)))
        ),
        "exact_negative_direction": None,
        "exact_negative_directions": [
            {
                "vector": vector,
                "quadratic_numerator": quadratic,
                "normalized_quadratic_denominator": family.normalized_denominator,
            }
            for vector, quadratic in directions
        ],
        "status": "NO_EXACT_NEGATIVE_DIRECTION_FOUND",
    }
    if direction is not None:
        vector, quadratic = direction
        result["exact_negative_direction"] = {
            "vector": vector,
            "quadratic_numerator": quadratic,
            "normalized_quadratic_denominator": family.normalized_denominator,
        }
        result["status"] = "EXACTLY_INDEFINITE"
    ldl = exact_ldl_psd(matrix)
    result["exact_ldl"] = ldl
    if ldl["is_psd"]:
        require(direction is None, "PSD LDL conflicts with negative direction")
        result["status"] = "EXACTLY_PSD"
    else:
        require(direction is not None, "exactly indefinite matrix lacks direction")
    return result


def direct_gram(
    adjacency: Sequence[set[int]],
    family: Family,
) -> list[list[int]]:
    size = len(family.flags)
    index = {flag: position for position, flag in enumerate(family.flags)}
    result = [[0] * size for _ in range(size)]
    order = len(adjacency)
    full_mask = mask_from_graph(adjacency, tuple(range(order)))
    for roots in root_embeddings(full_mask, order, family):
        remaining = tuple(vertex for vertex in range(order) if vertex not in roots)
        counts = [0] * size
        for free in itertools.combinations(remaining, family.free_count):
            flag_mask = induced_relabelled_mask(full_mask, order, roots, free)
            counts[index[canonical_flag(flag_mask, family.root_count)]] += 1
        for row in range(size):
            for column in range(size):
                result[row][column] += counts[row] * counts[column]
    return result


def induced_census(
    adjacency: Sequence[set[int]],
    catalogues: dict[int, Any],
    maximum_order: int,
) -> dict[int, dict[int, int]]:
    result: dict[int, dict[int, int]] = {}
    for order in range(4, maximum_order + 1):
        counts: Counter[int] = Counter()
        catalogue = catalogues[order]
        for vertices in itertools.combinations(range(len(adjacency)), order):
            labelled = mask_from_graph(adjacency, vertices)
            counts[catalogue.canonical_by_labelled_mask[labelled]] += 1
        result[order] = dict(counts)
    return result


def petersen_graph() -> list[set[int]]:
    vertices = tuple(itertools.combinations(range(5), 2))
    adjacency = [set() for _ in vertices]
    for left, first in enumerate(vertices):
        for right in range(left + 1, len(vertices)):
            if set(first).isdisjoint(vertices[right]):
                adjacency[left].add(right)
                adjacency[right].add(left)
    return adjacency


def clebsch_graph() -> list[set[int]]:
    # Folded 5-cube: antipodal classes represented by 5-bit words with bit 0=0.
    vertices = tuple(mask for mask in range(32) if not (mask & 1))
    adjacency = [set() for _ in vertices]
    for left, first in enumerate(vertices):
        for right in range(left + 1, len(vertices)):
            distance = (first ^ vertices[right]).bit_count()
            if distance in (1, 4):
                adjacency[left].add(right)
                adjacency[right].add(left)
    return adjacency


def srg_parameters(adjacency: Sequence[set[int]]) -> tuple[int, int, int, int]:
    n = len(adjacency)
    degrees = {len(neighbors) for neighbors in adjacency}
    require(len(degrees) == 1, "control graph is not regular")
    k = next(iter(degrees))
    adjacent_common = set()
    nonadjacent_common = set()
    for left in range(n):
        for right in range(left + 1, n):
            common = len(adjacency[left] & adjacency[right])
            (adjacent_common if right in adjacency[left] else nonadjacent_common).add(common)
    require(len(adjacent_common) == len(nonadjacent_common) == 1, "not strongly regular")
    return n, k, next(iter(adjacent_common)), next(iter(nonadjacent_common))


def control_record(
    name: str,
    adjacency: Sequence[set[int]],
    catalogues: dict[int, Any],
    coefficients: dict[str, object],
    families_value: Sequence[Family],
) -> dict[str, object]:
    census = induced_census(adjacency, catalogues, 7)
    family_records = {}
    for family in families_value:
        direct = direct_gram(adjacency, family)
        expanded = evaluate_expansion(coefficients, family, census)
        require(direct == expanded, f"{name} {family.name} expansion mismatch")
        eigenvalues = np.linalg.eigvalsh(np.asarray(direct, dtype=np.float64))
        require(
            min(direct[index][index] for index in range(len(direct))) >= 0,
            "negative diagonal",
        )
        family_records[family.name] = {
            "direct_equals_unrooted_expansion": True,
            "raw_matrix_sha256": sha256_json(direct),
            "minimum_raw_eigenvalue_float": float(eigenvalues[0]),
            "exact_psd_reason": "direct sum of integer outer products",
        }
    return {
        "name": name,
        "srg_parameters": list(srg_parameters(adjacency)),
        "induced_subset_totals": {
            str(order): sum(census[order].values()) for order in census
        },
        "families": family_records,
    }


def hostile_controls(
    coefficients: dict[str, object],
    families_value: Sequence[Family],
    petersen: Sequence[set[int]],
    catalogues: dict[int, Any],
) -> list[dict[str, object]]:
    family = families_value[0]
    census = induced_census(petersen, catalogues, 7)
    valid = evaluate_expansion(coefficients, family, census)
    direct = direct_gram(petersen, family)
    require(valid == direct, "positive control failed before hostile mutation")

    mutated = [row[:] for row in valid]
    mutated[0][0] = -1
    negative_diagonal_rejected = mutated[0][0] < 0

    lookup = coefficient_lookup(coefficients, family)
    first_key = next(key for key, matrix in lookup.items() if any(any(row) for row in matrix))
    lookup[first_key][0][0] += 1
    wrong = [[0] * len(family.flags) for _ in family.flags]
    for order in range(4, 8):
        for mask, count in census[order].items():
            add_scaled_matrix(wrong, lookup[(order, mask)], count)
    coefficient_mutation_rejected = wrong != direct

    return [
        {
            "label": "negative diagonal mutation",
            "outcome": "REJECTED" if negative_diagonal_rejected else "ACCEPTED_IN_ERROR",
        },
        {
            "label": "one embedding coefficient incremented",
            "outcome": "REJECTED" if coefficient_mutation_rejected else "ACCEPTED_IN_ERROR",
            "mutated_class": {"order": first_key[0], "canonical_mask": first_key[1]},
        },
    ]


def compute() -> tuple[dict[str, object], dict[str, object]]:
    samples = [memory_sample("wave45-start")]
    catalogues = build_catalogues()
    classes = admissible_classes(catalogues)
    family_values = families()
    require(
        tuple(len(family.flags) for family in family_values) == (17, 16, 19),
        "unexpected flag census",
    )
    samples.append(memory_sample("after-catalogues"))

    coefficients = build_coefficients(family_values, classes)
    coefficients["class_streams"] = {
        str(order): {
            "count": len(classes[order]),
            "sha256": W43.class_stream_sha256(classes[order], 1 if order <= 4 else 2 if order <= 6 else 3),
        }
        for order in classes
    }
    coefficients["coefficient_payload_sha256_without_this_field"] = sha256_json(coefficients)
    samples.append(memory_sample("after-coefficients"))

    lower = target_lower_counts(classes)
    targets = {
        "wave43_unrooted": W43_WITNESS,
        "wave44_rooted": W44_WITNESS,
    }
    target_records = {}
    exact_directions = []
    for target_name, path in targets.items():
        counts = dict(lower)
        counts[7] = load_seven_counts(path, classes[7])
        family_records = {}
        for family in family_values:
            matrix = evaluate_expansion(coefficients, family, counts)
            record = spectral_record(matrix, family)
            family_records[family.name] = record
            for direction_index, direction in enumerate(
                record["exact_negative_directions"]
            ):
                exact_directions.append(
                    {
                        "target": target_name,
                        "family": family.name,
                        "direction_index": direction_index,
                        **direction,
                    }
                )
        target_records[target_name] = {
            "input_path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "input_sha256": sha256_file(path),
            "families": family_records,
        }

    controls = [
        control_record(
            "Petersen",
            petersen_graph(),
            catalogues,
            coefficients,
            family_values,
        ),
        control_record(
            "Clebsch",
            clebsch_graph(),
            catalogues,
            coefficients,
            family_values,
        ),
    ]
    hostiles = hostile_controls(
        coefficients, family_values, petersen_graph(), catalogues
    )
    require(all(item["outcome"] == "REJECTED" for item in hostiles), "hostile accepted")
    samples.append(memory_sample("wave45-finish"))

    any_exact_indefinite = any(
        family_record["status"] == "EXACTLY_INDEFINITE"
        for target in target_records.values()
        for family_record in target["families"].values()
    )
    result = {
        "format": "wave45-exact-finite-flag-moment-v1",
        "role": "construction",
        "claim_label": "DERIVED",
        "scope": (
            "Exact finite Gram-moment tests of the frozen Wave43 and Wave44 "
            "n3=4158 aggregate count witnesses."
        ),
        "parameters": {"n": N, "k": K, "lambda": 1, "mu": 2, "n3": N3},
        "coefficient_model": {
            "file": "attempts/wave45-flag-moment/moment-coefficients.json",
            "payload_sha256": coefficients[
                "coefficient_payload_sha256_without_this_field"
            ],
            "families": {
                family.name: {
                    "matrix_size": len(family.flags),
                    "flags": list(family.flags),
                    "union_orders": list(range(4, family.maximum_union_order + 1)),
                    "root_embeddings": family.root_embeddings_at_target,
                    "free_subsets_per_root": family.free_subsets_per_root_at_target,
                    "normalization_denominator": family.normalized_denominator,
                }
                for family in family_values
            },
        },
        "targets": target_records,
        "exact_negative_directions": exact_directions,
        "controls": {"known_srgs": controls, "hostile_mutations": hostiles},
        "resource_guard": {
            "minimum_free_memory_percent": MIN_FREE_MEMORY_PERCENT,
            "samples": samples,
        },
        "conclusion": {
            "one_or_more_stored_witnesses_refuted": any_exact_indefinite,
            "entire_wave44_linear_feasible_region_psd_feasibility": "NOT_TESTED",
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "graph_constructed": False,
            "Conway_99": "UNKNOWN",
        },
        "limitations": [
            "An indefinite stored count witness only refutes that witness.",
            "The PSD-constrained feasibility problem over all count vectors is not yet certified.",
            "Floating eigenvalues are diagnostics; only exact integer negative directions are claims.",
            "No automorphism of a target graph is assumed.",
        ],
    }
    return coefficients, result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--coefficients",
        type=Path,
        default=HERE / "moment-coefficients.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "exact-results.json",
    )
    args = parser.parse_args()
    coefficients, result = compute()
    args.coefficients.write_text(
        json.dumps(coefficients, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "coefficient_families": list(coefficients["families"]),
                "exact_negative_directions": len(result["exact_negative_directions"]),
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
