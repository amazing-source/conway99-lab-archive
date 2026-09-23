#!/usr/bin/env python3
"""Exact three-fibre characteristic-seven coupling census for Conway-99.

This discovery program proves a candidate universal lower bound for the
characteristic-seven rank by coupling the Wave 39 edge-local block to the
twelve vertices in the third fibre of its triangle mate.

Only the Python standard library is used.  The finite exhaustion is over:

* all 10,395 pulled-back perfect matchings, grouped into the eleven positive
  partitions of six; and
* every observed-vector-spanned subspace below the first dimension that can
  support a permutation of the twelve third-fibre neighbour signatures.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Sequence


FORMAT = "wave40-exact-three-fibre-rank-coupling-v1"
CERTIFICATE_FORMAT = "wave40-projection-subspace-certificate-v1"
PUBLIC_BASE_COMMIT = "6b28af70c67f062d687251494a047debe70a246f"
PRIME = 7
SIDE_SIZE = 12
LOCAL_SIZE = 27
THREE_FIBRE_SIZE = 39
TARGET_VERTEX_COUNT = 99
PREVIOUS_VERIFIED_RANK_FLOOR = 19
INPUTS = {
    "CONJECTURE.md": (
        "7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58"
    ),
    "verification/wave39-edge-local-rank/independent-results.json": (
        "85b8d36d6ce5ebd638e957e1731864eff75f38405935f5e51ad5b629edea5966"
    ),
    "verification/wave39-edge-local-rank/README.md": (
        "ed749e5788c19a23629cee9f331cce0ef161500d9cb0d939eef3211085c0a405"
    ),
}


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def compact_json(value: object) -> bytes:
    return (json.dumps(value, separators=(",", ":"), sort_keys=True) + "\n").encode(
        "utf-8"
    )


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def partition_key(partition: Sequence[int]) -> str:
    return "+".join(str(part) for part in partition)


def integer_partitions(total: int, minimum: int = 1) -> Iterable[tuple[int, ...]]:
    if total == 0:
        yield ()
        return
    for first in range(minimum, total + 1):
        for tail in integer_partitions(total - first, first):
            yield (first,) + tail


def pairings(vertices: tuple[int, ...]) -> Iterable[tuple[tuple[int, int], ...]]:
    """Yield every perfect matching as a sorted tuple of ordered pairs."""

    if not vertices:
        yield ()
        return
    first = vertices[0]
    for index in range(1, len(vertices)):
        second = vertices[index]
        remainder = vertices[1:index] + vertices[index + 1 :]
        for tail in pairings(remainder):
            yield ((first, second),) + tail


def matching_map(edges: Sequence[tuple[int, int]]) -> tuple[int, ...]:
    result = [-1] * SIDE_SIZE
    for left, right in edges:
        if left == right or result[left] != -1 or result[right] != -1:
            raise ValueError("edges do not define a perfect matching")
        result[left] = right
        result[right] = left
    if any(value == -1 for value in result):
        raise ValueError("matching does not cover twelve points")
    return tuple(result)


STANDARD_MATCHING = tuple(index ^ 1 for index in range(SIDE_SIZE))


def cycle_partition(
    first: Sequence[int], second: Sequence[int]
) -> tuple[int, ...]:
    """Return the Wave 39 partition of six for two perfect matchings.

    A union component on ``2m`` pulled-back points corresponds to a local
    three-matching cycle on ``4m`` vertices and therefore contributes part
    ``m``.
    """

    unseen = set(range(SIDE_SIZE))
    parts: list[int] = []
    while unseen:
        start = min(unseen)
        vertex = start
        relation = 0
        size = 0
        while vertex in unseen:
            unseen.remove(vertex)
            size += 1
            vertex = (first if relation == 0 else second)[vertex]
            relation ^= 1
        if size % 2:
            raise AssertionError("two matchings produced an odd union component")
        parts.append(size // 2)
    return tuple(sorted(parts))


def alternating_components(matching: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    unseen = set(range(SIDE_SIZE))
    components: list[tuple[int, ...]] = []
    while unseen:
        start = min(unseen)
        component: list[int] = []
        vertex = start
        relation = 0
        while vertex in unseen:
            unseen.remove(vertex)
            component.append(vertex)
            vertex = (
                STANDARD_MATCHING if relation == 0 else matching
            )[vertex]
            relation ^= 1
        components.append(tuple(component))
    return tuple(sorted(components, key=lambda component: (len(component), min(component))))


def matching_conjugator(
    source: Sequence[int], target: Sequence[int]
) -> tuple[int, ...]:
    """Construct a relabelling fixing P and sending source Q to target Q.

    The alternating component lengths are a complete invariant for the pair
    of edge-coloured perfect matchings.  Pair equal-sized components in
    canonical order and map their alternating P,Q traversals.
    """

    if cycle_partition(STANDARD_MATCHING, source) != cycle_partition(
        STANDARD_MATCHING, target
    ):
        raise ValueError("matchings have different alternating partitions")
    source_components = alternating_components(source)
    target_components = alternating_components(target)
    permutation = [-1] * SIDE_SIZE
    for source_component, target_component in zip(
        source_components, target_components, strict=True
    ):
        if len(source_component) != len(target_component):
            raise AssertionError("paired alternating components have different sizes")
        source_start = min(source_component)
        target_start = min(target_component)
        source_vertex = source_start
        target_vertex = target_start
        relation = 0
        for _ in range(len(source_component)):
            if permutation[source_vertex] not in (-1, target_vertex):
                raise AssertionError("component relabelling is inconsistent")
            permutation[source_vertex] = target_vertex
            source_vertex = (
                STANDARD_MATCHING if relation == 0 else source
            )[source_vertex]
            target_vertex = (
                STANDARD_MATCHING if relation == 0 else target
            )[target_vertex]
            relation ^= 1
        if source_vertex != source_start or target_vertex != target_start:
            raise AssertionError("alternating traversal did not close")
    if sorted(permutation) != list(range(SIDE_SIZE)):
        raise AssertionError("matching conjugator is not a permutation")
    for vertex in range(SIDE_SIZE):
        image = permutation[vertex]
        if permutation[STANDARD_MATCHING[vertex]] != STANDARD_MATCHING[image]:
            raise AssertionError("matching conjugator does not centralize P")
        if permutation[source[vertex]] != target[image]:
            raise AssertionError("matching conjugator does not map source Q to target Q")
    return tuple(permutation)


def matching_catalog() -> dict[tuple[int, ...], dict[str, object]]:
    catalog: dict[tuple[int, ...], dict[str, object]] = {
        partition: {"count": 0, "representative": None}
        for partition in integer_partitions(6)
    }
    total = 0
    all_matchings: list[tuple[int, ...]] = []
    for edges in pairings(tuple(range(SIDE_SIZE))):
        matching = matching_map(edges)
        all_matchings.append(matching)
        partition = cycle_partition(STANDARD_MATCHING, matching)
        entry = catalog[partition]
        entry["count"] = int(entry["count"]) + 1
        representative = entry["representative"]
        if representative is None or matching < representative:
            entry["representative"] = matching
        total += 1
    if total != 10_395:
        raise AssertionError(f"perfect-matching census changed: {total}")
    if len(catalog) != 11 or any(entry["representative"] is None for entry in catalog.values()):
        raise AssertionError("partition catalog is incomplete")
    for matching in all_matchings:
        partition = cycle_partition(STANDARD_MATCHING, matching)
        representative = catalog[partition]["representative"]
        matching_conjugator(representative, matching)
    for entry in catalog.values():
        entry["conjugacy_checks"] = int(entry["count"])
    return catalog


def add_edge(adjacency: list[list[int]], left: int, right: int) -> None:
    if left == right or adjacency[left][right]:
        raise AssertionError("invalid repeated or loop edge")
    adjacency[left][right] = 1
    adjacency[right][left] = 1


def edge_local_adjacency(pulled_y_matching: Sequence[int]) -> list[list[int]]:
    """Build the 27-vertex block for base triangle xyz and fibres X,Y."""

    adjacency = [[0] * LOCAL_SIZE for _ in range(LOCAL_SIZE)]
    x, y, z = 0, 1, 2
    x_vertices = range(3, 15)
    y_vertices = range(15, 27)
    for left, right in ((x, y), (x, z), (y, z)):
        add_edge(adjacency, left, right)
    for index in range(SIDE_SIZE):
        add_edge(adjacency, x, 3 + index)
        add_edge(adjacency, y, 15 + index)
        add_edge(adjacency, 3 + index, 15 + index)
    for matching, offset in (
        (STANDARD_MATCHING, 3),
        (pulled_y_matching, 15),
    ):
        for left, right in enumerate(matching):
            if left < right:
                add_edge(adjacency, offset + left, offset + right)
    return adjacency


def seidel_matrix(adjacency: Sequence[Sequence[int]]) -> list[list[int]]:
    """Return ``J-I-2A``, equal to ``27I-9A+J`` over F_7."""

    return [
        [
            1 - int(row == column) - 2 * adjacency[row][column]
            for column in range(len(adjacency))
        ]
        for row in range(len(adjacency))
    ]


def rref(
    matrix: Sequence[Sequence[int]], prime: int = PRIME
) -> tuple[list[list[int]], tuple[int, ...]]:
    if not matrix:
        return [], ()
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("matrix is ragged")
    work = [[entry % prime for entry in row] for row in matrix]
    rank = 0
    pivots: list[int] = []
    for column in range(width):
        pivot = next(
            (row for row in range(rank, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, prime)
        work[rank] = [(entry * inverse) % prime for entry in work[rank]]
        for row in range(len(work)):
            if row == rank or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                (left - factor * right) % prime
                for left, right in zip(work[row], work[rank])
            ]
        pivots.append(column)
        rank += 1
        if rank == len(work):
            break
    return work, tuple(pivots)


def rank_mod_prime(matrix: Sequence[Sequence[int]], prime: int = PRIME) -> int:
    return len(rref(matrix, prime)[1])


def kernel_basis(
    matrix: Sequence[Sequence[int]], prime: int = PRIME
) -> tuple[tuple[int, ...], ...]:
    reduced, pivots = rref(matrix, prime)
    width = len(matrix[0])
    free = [column for column in range(width) if column not in pivots]
    basis: list[tuple[int, ...]] = []
    for free_column in free:
        vector = [0] * width
        vector[free_column] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = (-reduced[row][free_column]) % prime
        if any(
            sum(matrix[row][column] * vector[column] for column in range(width))
            % prime
            for row in range(len(matrix))
        ):
            raise AssertionError("kernel reconstruction failed")
        basis.append(tuple(vector))
    return tuple(basis)


def border_vector(x_index: int, y_index: int) -> tuple[int, ...]:
    """Seidel column of one third-fibre vertex against the 27-point block."""

    if not 0 <= x_index < SIDE_SIZE or not 0 <= y_index < SIDE_SIZE:
        raise ValueError("border signature indices must lie in 0..11")
    vector = [1] * LOCAL_SIZE
    # The vertex sees z, its unique X neighbour, and its unique Y neighbour.
    for vertex in (2, 3 + x_index, 15 + y_index):
        vector[vertex] = -1
    return tuple(vector)


def projection_catalog(
    kernel: Sequence[Sequence[int]],
) -> dict[tuple[int, int], tuple[int, ...]]:
    return {
        (x_index, y_index): tuple(
            sum(
                kernel_vector[column] * border[column]
                for column in range(LOCAL_SIZE)
            )
            % PRIME
            for kernel_vector in kernel
        )
        for x_index in range(SIDE_SIZE)
        for y_index in range(SIDE_SIZE)
        for border in (border_vector(x_index, y_index),)
    }


Basis = tuple[tuple[int, ...], ...]


def canonical_basis(vectors: Sequence[Sequence[int]], width: int) -> Basis:
    if not vectors:
        return ()
    if any(len(vector) != width for vector in vectors):
        raise ValueError("subspace vector has the wrong width")
    reduced, pivots = rref(vectors)
    return tuple(tuple(reduced[row]) for row in range(len(pivots)))


def in_span(vector: Sequence[int], basis: Basis) -> bool:
    if not any(entry % PRIME for entry in vector):
        return True
    work = [entry % PRIME for entry in vector]
    for row in basis:
        pivot = next(index for index, entry in enumerate(row) if entry)
        if work[pivot]:
            factor = work[pivot]
            work = [
                (left - factor * right) % PRIME
                for left, right in zip(work, row)
            ]
    return not any(work)


def maximum_bipartite_matching(
    projections: Mapping[tuple[int, int], tuple[int, ...]], basis: Basis
) -> tuple[int, tuple[int, ...] | None]:
    """Maximum matching in the signature positions whose vectors lie in basis."""

    allowed = {
        left: tuple(
            right
            for right in range(SIDE_SIZE)
            if in_span(projections[(left, right)], basis)
        )
        for left in range(SIDE_SIZE)
    }
    right_owner: dict[int, int] = {}

    def augment(left: int, seen: set[int]) -> bool:
        for right in allowed[left]:
            if right in seen:
                continue
            seen.add(right)
            owner = right_owner.get(right)
            if owner is None or augment(owner, seen):
                right_owner[right] = left
                return True
        return False

    size = sum(augment(left, set()) for left in range(SIDE_SIZE))
    if size != SIDE_SIZE:
        return size, None
    permutation = [-1] * SIDE_SIZE
    for right, left in right_owner.items():
        permutation[left] = right
    if sorted(permutation) != list(range(SIDE_SIZE)):
        raise AssertionError("full bipartite matching is not a permutation")
    return size, tuple(permutation)


def observed_lines(
    projections: Mapping[tuple[int, int], tuple[int, ...]], width: int
) -> tuple[Basis, ...]:
    lines = {
        canonical_basis((vector,), width)
        for vector in projections.values()
        if any(vector)
    }
    return tuple(sorted(lines))


def extend_subspaces(
    previous: Sequence[Basis], lines: Sequence[Basis], target_dimension: int, width: int
) -> tuple[Basis, ...]:
    result: set[Basis] = set()
    for basis in previous:
        for line in lines:
            candidate = canonical_basis((*basis, line[0]), width)
            if len(candidate) == target_dimension:
                result.add(candidate)
    return tuple(sorted(result))


def projection_subspace_census(
    projections: Mapping[tuple[int, int], tuple[int, ...]],
    width: int,
) -> tuple[dict[str, object], dict[str, object]]:
    """Find the minimum projection rank over all twelve-point permutations.

    A permutation ``f`` is supported by a subspace ``L`` precisely when every
    signature ``(i,f(i))`` has projection in ``L``.  Bipartite matching tests
    that condition without iterating over ``12!`` permutations.

    Every minimum span is generated by its selected observed vectors.  Hence
    recursively adjoining all observed projective lines enumerates every
    subspace that can be minimal; no ambient subspace is silently omitted.
    """

    zero_basis: Basis = ()
    zero_size, zero_permutation = maximum_bipartite_matching(
        projections, zero_basis
    )
    level_records: list[dict[str, object]] = [
        {
            "dimension": 0,
            "subspace_count": 1,
            "maximum_support_matching": zero_size,
            "support_matching_histogram": {str(zero_size): 1},
        }
    ]
    rejected: list[dict[str, object]] = []
    if zero_size == SIDE_SIZE:
        if zero_permutation is None:
            raise AssertionError("missing dimension-zero permutation")
        witness_basis = zero_basis
        witness_permutation = zero_permutation
        minimum_dimension = 0
    else:
        rejected.append(
            {
                "basis": [],
                "dimension": 0,
                "maximum_support_matching": zero_size,
            }
        )
        lines = observed_lines(projections, width)
        previous = lines
        minimum_dimension = -1
        witness_basis = ()
        witness_permutation: tuple[int, ...] | None = None
        for dimension in range(1, width + 1):
            if dimension > 1:
                previous = extend_subspaces(
                    previous, lines, dimension, width
                )
            histogram: Counter[int] = Counter()
            level_maximum = 0
            first_full: tuple[Basis, tuple[int, ...]] | None = None
            level_rejected: list[dict[str, object]] = []
            for basis in previous:
                size, permutation = maximum_bipartite_matching(
                    projections, basis
                )
                histogram[size] += 1
                level_maximum = max(level_maximum, size)
                if size == SIDE_SIZE and first_full is None:
                    if permutation is None:
                        raise AssertionError("full support lost its permutation")
                    first_full = (basis, permutation)
                if size < SIDE_SIZE:
                    level_rejected.append(
                        {
                            "basis": [list(row) for row in basis],
                            "dimension": dimension,
                            "maximum_support_matching": size,
                        }
                    )
            level_records.append(
                {
                    "dimension": dimension,
                    "subspace_count": len(previous),
                    "maximum_support_matching": level_maximum,
                    "support_matching_histogram": {
                        str(size): histogram[size] for size in sorted(histogram)
                    },
                }
            )
            if first_full is not None:
                minimum_dimension = dimension
                witness_basis, witness_permutation = first_full
                # At the first successful dimension every smaller subspace is
                # retained above; successful same-dimension subspaces are not
                # needed for the lower-bound certificate.
                break
            rejected.extend(level_rejected)
        if minimum_dimension < 0 or witness_permutation is None:
            raise AssertionError("no projection subspace supports a permutation")

    selected_columns = [
        projections[(left, witness_permutation[left])]
        for left in range(SIDE_SIZE)
    ]
    selected_rank = rank_mod_prime(
        [
            [selected_columns[column][row] for column in range(SIDE_SIZE)]
            for row in range(width)
        ]
        if width
        else []
    )
    if selected_rank != minimum_dimension:
        raise AssertionError("witness permutation has the wrong projection rank")

    rejected_payload = canonical_json(rejected)
    result = {
        "minimum_projection_rank_over_permutations": minimum_dimension,
        "observed_nonzero_projective_line_count": len(
            observed_lines(projections, width)
        ),
        "zero_signature_count": sum(not any(vector) for vector in projections.values()),
        "levels_through_first_success": level_records,
        "witness": {
            "basis": [list(row) for row in witness_basis],
            "permutation": list(witness_permutation),
            "projection_rank": selected_rank,
            "selected_projection_columns": [
                list(vector) for vector in selected_columns
            ],
        },
        "rejected_subspace_count": len(rejected),
        "rejected_subspaces_sha256": sha256_bytes(rejected_payload),
    }
    certificate = {
        "minimum_projection_rank": minimum_dimension,
        "rejected_subspaces": rejected,
        "witness": result["witness"],
    }
    return result, certificate


def three_fibre_relaxation_matrix(
    local_seidel: Sequence[Sequence[int]],
    permutation: Sequence[int],
) -> list[list[int]]:
    """Build a positive-control 39-block with a canonical Z matching.

    The matrix uses the theorem-forced border signatures and a perfect
    matching inside Z.  It is only a one-triangle local control: it need not
    satisfy every SRG equation or the other two edge-type restrictions.
    """

    order = THREE_FIBRE_SIZE
    result = [[0] * order for _ in range(order)]
    for row in range(LOCAL_SIZE):
        for column in range(LOCAL_SIZE):
            result[row][column] = local_seidel[row][column]
    for index, y_index in enumerate(permutation):
        border = border_vector(index, y_index)
        for row, value in enumerate(border):
            result[row][LOCAL_SIZE + index] = value
            result[LOCAL_SIZE + index][row] = value
    for left in range(SIDE_SIZE):
        for right in range(SIDE_SIZE):
            if left == right:
                value = 0
            elif STANDARD_MATCHING[left] == right:
                value = -1
            else:
                value = 1
            result[LOCAL_SIZE + left][LOCAL_SIZE + right] = value
    return result


def admissible_rank_pairs() -> list[list[int]]:
    return [
        [rank_three, rank_seven]
        for rank_three in range(12, 45)
        for rank_seven in range(25, 45)
        if (rank_three + rank_seven) % 2 == 0
    ]


def derive() -> tuple[dict[str, object], dict[str, object]]:
    catalog = matching_catalog()
    type_records: list[dict[str, object]] = []
    certificate_types: dict[str, object] = {}
    all_lower_bounds: list[int] = []

    for partition in sorted(catalog):
        entry = catalog[partition]
        representative = tuple(int(value) for value in entry["representative"])
        adjacency = edge_local_adjacency(representative)
        local_seidel = seidel_matrix(adjacency)
        base_rank = rank_mod_prime(local_seidel)
        kernel = kernel_basis(local_seidel)
        if len(kernel) != LOCAL_SIZE - base_rank:
            raise AssertionError("rank-nullity failed")
        projections = projection_catalog(kernel)
        projection_result, projection_certificate = projection_subspace_census(
            projections, len(kernel)
        )
        minimum_projection_rank = int(
            projection_result["minimum_projection_rank_over_permutations"]
        )
        coupled_lower_bound = base_rank + 2 * minimum_projection_rank
        if coupled_lower_bound != 25:
            raise AssertionError(
                f"unexpected coupled floor for {partition}: {coupled_lower_bound}"
            )
        all_lower_bounds.append(coupled_lower_bound)
        witness_permutation = projection_result["witness"]["permutation"]
        control = three_fibre_relaxation_matrix(
            local_seidel, witness_permutation
        )
        control_rank = rank_mod_prime(control)
        key = partition_key(partition)
        projection_catalog_json = [
            {
                "signature": [left, right],
                "projection": list(projections[(left, right)]),
            }
            for left in range(SIDE_SIZE)
            for right in range(SIDE_SIZE)
        ]
        type_records.append(
            {
                "partition": list(partition),
                "partition_key": key,
                "labelled_pulled_matching_count": int(entry["count"]),
                "explicit_partition_conjugacy_checks": int(
                    entry["conjugacy_checks"]
                ),
                "partition_complete_invariant": (
                    "An explicit permutation centralizing the standard X "
                    "matching sends every labelled matching of this partition "
                    "to the retained representative."
                ),
                "representative_pulled_y_matching": list(representative),
                "representative_matching_sha256": sha256_bytes(
                    compact_json(list(representative))
                ),
                "base_27_rank_F7": base_rank,
                "base_27_nullity_F7": len(kernel),
                "base_27_seidel_sha256": sha256_bytes(
                    compact_json(local_seidel)
                ),
                "projection_catalog_sha256": sha256_bytes(
                    compact_json(projection_catalog_json)
                ),
                "projection_census": projection_result,
                "coupled_39_rank_lower_bound_F7": coupled_lower_bound,
                "canonical_local_control_rank_F7": control_rank,
                "control_scope": (
                    "one-triangle three-fibre local control only; the canonical "
                    "Z matching is not asserted to extend to a 99-vertex graph"
                ),
            }
        )
        certificate_types[key] = {
            "partition": list(partition),
            "representative_pulled_y_matching": list(representative),
            "base_27_rank_F7": base_rank,
            "kernel_basis": [list(vector) for vector in kernel],
            "projection_catalog": projection_catalog_json,
            "projection_subspace_certificate": projection_certificate,
        }

    if sum(int(entry["count"]) for entry in catalog.values()) != 10_395:
        raise AssertionError("matching multiplicities no longer sum to 10,395")
    universal_floor = min(all_lower_bounds)
    if universal_floor != 25:
        raise AssertionError("universal rank floor changed")
    pairs = admissible_rank_pairs()
    if len(pairs) != 330:
        raise AssertionError("updated arithmetic rank-pair count changed")
    rank_three_twelve = [
        rank_seven for rank_three, rank_seven in pairs if rank_three == 12
    ]
    if rank_three_twelve != list(range(26, 45, 2)):
        raise AssertionError("r3=12 parity boundary changed")

    certificate = {
        "format": CERTIFICATE_FORMAT,
        "claim_label": "CANDIDATE_FINITE_EXHAUSTION",
        "field": PRIME,
        "normalization": (
            "Fix the X matching and pull Y through the X-Y perfect matching; "
            "the third-fibre X- and Y-neighbour signatures are (i,f(i)) for "
            "an arbitrary permutation f."
        ),
        "completeness": {
            "pulled_perfect_matchings": 10_395,
            "edge_partition_types": 11,
            "signature_positions_per_type": 144,
            "permutations_covered_implicitly": "12! via exact bipartite matching",
            "subspace_rule": (
                "Every minimum projection span is generated by selected "
                "observed projection lines; all such lower-dimensional spans "
                "are listed and rejected."
            ),
        },
        "types": certificate_types,
    }
    certificate_hash = sha256_bytes(canonical_json(certificate))
    result = {
        "format": FORMAT,
        "role": "construction",
        "claim_label": "CANDIDATE",
        "git_commit": PUBLIC_BASE_COMMIT,
        "scope": (
            "universal three-fibre characteristic-seven rank consequence for "
            "a hypothetical srg(99,14,1,2)"
        ),
        "inputs": INPUTS,
        "target_parameters": {
            "v": 99,
            "k": 14,
            "lambda": 1,
            "mu": 2,
        },
        "transport": {
            "frozen_identity": "N M N^T = 27I - 9A + J",
            "modulo_seven_matrix": "27I-9A+J = J-I-2A over F_7",
            "frozen_rank_equality": "rank_F7(M)=rank_F7(NMN^T)",
            "principal_block_use": (
                "Every 39-vertex three-fibre principal block lower-bounds "
                "rank_F7(M)."
            ),
        },
        "three_fibre_geometry": {
            "base_triangle": ["x", "y", "z"],
            "fibres": {
                "X": "N(x)-{y,z}",
                "Y": "N(y)-{x,z}",
                "Z": "N(z)-{x,y}",
            },
            "fibre_sizes": [12, 12, 12],
            "why_signatures_form_a_permutation": (
                "For c in Z, nonedge (c,x) has common neighbour z and exactly "
                "one further common neighbour in X; the same holds for Y. "
                "The resulting X-Z and Y-Z relations are perfect matchings. "
                "After indexing Z through X-Z, the Y indices are f(i) for a "
                "bijection f of twelve points."
            ),
            "normalization_uses_completed_graph_automorphism": False,
            "normalization_explanation": (
                "Only labels inside the chosen fibres are changed: fix the X "
                "matching and pull Y labels through X-Y. Every pulled Y "
                "matching is explicitly included in the 10,395 census."
            ),
        },
        "rank_congruence_lemma": {
            "statement": (
                "For symmetric S and any U,W over a field, if K has columns "
                "forming a basis of ker(S), then rank([[S,U],[U^T,W]]) "
                "is at least rank(S)+2*rank(K^T U)."
            ),
            "proof": (
                "An invertible congruence sends S to diag(D,0) with D "
                "nonsingular. Eliminating the U rows alongside D leaves "
                "diag(D, [[0,U0],[U0^T,W']]), where rank(U0)=rank(K^T U). "
                "Row and column basis changes expose rank(U0) hyperbolic "
                "pairs, so the second block has rank at least 2*rank(U0)."
            ),
            "unknown_third_fibre_block": (
                "W may be arbitrary; its entries cannot reduce the displayed "
                "lower bound."
            ),
        },
        "finite_census": {
            "pulled_perfect_matching_count": 10_395,
            "partition_type_count": len(type_records),
            "types": type_records,
            "certificate_format": CERTIFICATE_FORMAT,
            "certificate_sha256": certificate_hash,
        },
        "candidate_universal_result": {
            "rank_F7_M_lower_bound": universal_floor,
            "previous_verified_lower_bound": PREVIOUS_VERIFIED_RANK_FLOOR,
            "improvement": universal_floor - PREVIOUS_VERIFIED_RANK_FLOOR,
            "proof_summary": (
                "For every edge partition, the exact minimum over all "
                "third-fibre permutation signatures satisfies "
                "rank(S_pi)+2*t_pi=25."
            ),
        },
        "conditional_endpoint_arithmetic": {
            "condition": "n3=4158, equivalently no induced triangular prism",
            "admissible_rank_pair_count_after_candidate": len(pairs),
            "previous_wave39_pair_count": 429,
            "if_r3_equals_12": {
                "r7_parity": "even",
                "r7_lower_bound": 26,
                "admissible_r7_values": rank_three_twelve,
            },
            "endpoint_excluded": False,
            "upper_bound_improved_below_4158": False,
        },
        "status": {
            "candidate_rank_floor": 25,
            "endpoint": "UNKNOWN",
            "conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
            "strongest_general_upper_bound_on_n3": 4158,
        },
        "limitations": [
            "Discovery cannot verify itself; clean-room verification is required.",
            "The theorem is a rank restriction, not a graph construction.",
            "The canonical local controls are relaxations, not 99-vertex graphs.",
            "No endpoint contradiction or upper bound below n3=4158 follows.",
            "Literature novelty and priority remain UNKNOWN.",
        ],
    }
    return result, certificate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--output", type=Path)
    mode.add_argument("--verify", type=Path)
    parser.add_argument("--certificate", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result, certificate = derive()
    result_payload = canonical_json(result)
    certificate_payload = canonical_json(certificate)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.certificate.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(result_payload)
        args.certificate.write_bytes(certificate_payload)
        print(
            json.dumps(
                {
                    "result": str(args.output),
                    "result_sha256": sha256_bytes(result_payload),
                    "certificate": str(args.certificate),
                    "certificate_sha256": sha256_bytes(certificate_payload),
                },
                sort_keys=True,
            )
        )
        return 0
    if args.verify.read_bytes() != result_payload:
        raise SystemExit("stored exact result differs from exact regeneration")
    if args.certificate.read_bytes() != certificate_payload:
        raise SystemExit("stored subspace certificate differs from exact regeneration")
    print(
        "PASS: exact result and complete subspace certificate match regeneration"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
