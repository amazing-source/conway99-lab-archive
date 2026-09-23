#!/usr/bin/env python3
"""Independent verifier for the Wave-23 weighted-extension certificate.

This module deliberately does not import or execute any code from
``attempts/wave23-weighted-extensions``.  It reconstructs the locally
admissible graph census, automorphism orbits, transition matrices, source
six-count gate, and exact affine certificate with a separate implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter
from fractions import Fraction
from functools import cache
from itertools import combinations, permutations
from pathlib import Path
from typing import Iterable, Mapping, Sequence


N = 99
K = 14
LAMBDA = 1
MU = 2
N3 = 705
Z_MIN = 353
Z_MAX = 705

CANDIDATE_COMMIT = "c82f49be256f79fed45b7a4f1458d751d2ec0d9f"
SOURCE21_SHA256 = "5e7b6f526985fb719754145944579aacb0e8f38e9e14a54d2075552a3756ff2b"
SOURCE22_SHA256 = "ca5d9d116f6a9d6e355600429652e2bf4474b73dcf281bbcb564420d820acbd2"
EXPECTED_UNLABELED = (1, 2, 4, 9, 21, 62, 208)
EXPECTED_LABELED_SEVEN = 394_020

DRIVE_PATH = re.compile(r"(?<![A-Za-z0-9])(?:[A-Za-z]:[\\/])")
POSIX_HOME_PATH = re.compile(
    r"(?:^|[^A-Za-z0-9\"'])/(?:users|home)/[^/\s]+/",
    re.IGNORECASE,
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require_plain_int(value: object, label: str) -> int:
    if type(value) is not int:
        raise AssertionError(f"{label} is not a plain integer")
    return value


def reject_private_paths(value: object, label: str = "payload") -> None:
    if isinstance(value, str):
        if DRIVE_PATH.search(value) or POSIX_HOME_PATH.search(value.replace("\\", "/")):
            raise AssertionError(f"{label} contains a private absolute path")
    elif isinstance(value, Mapping):
        for key, child in value.items():
            reject_private_paths(child, f"{label}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            reject_private_paths(child, f"{label}[{index}]")


@cache
def edge_list(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(combinations(range(order), 2))


@cache
def edge_positions(order: int) -> dict[tuple[int, int], int]:
    return {edge: index for index, edge in enumerate(edge_list(order))}


@cache
def relabel_maps(order: int) -> tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]:
    """Return permutations and old-edge-index to new-edge-bit maps."""
    positions = edge_positions(order)
    result = []
    for permutation in permutations(range(order)):
        image_bits = []
        for left, right in edge_list(order):
            image = tuple(sorted((permutation[left], permutation[right])))
            image_bits.append(1 << positions[image])
        result.append((permutation, tuple(image_bits)))
    return tuple(result)


def relabel_mask(mask: int, image_bits: Sequence[int]) -> int:
    result = 0
    for edge_index, image_bit in enumerate(image_bits):
        if mask & (1 << edge_index):
            result |= image_bit
    return result


@cache
def adjacency(mask: int, order: int) -> tuple[int, ...]:
    rows = [0] * order
    for index, (left, right) in enumerate(edge_list(order)):
        if mask & (1 << index):
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return tuple(rows)


def locally_admissible(mask: int, order: int) -> bool:
    rows = adjacency(mask, order)
    positions = edge_positions(order)
    for left, right in edge_list(order):
        common = (rows[left] & rows[right]).bit_count()
        allowed = LAMBDA if mask & (1 << positions[(left, right)]) else MU
        if common > allowed:
            return False
    return True


@cache
def labeled_admissible(order: int) -> tuple[int, ...]:
    return tuple(
        mask
        for mask in range(1 << math.comb(order, 2))
        if locally_admissible(mask, order)
    )


@cache
def unlabeled_classes(order: int) -> tuple[int, ...]:
    """Partition the complete labeled census into permutation orbits."""
    remaining = set(labeled_admissible(order))
    classes: list[int] = []
    maps = tuple(image for _, image in relabel_maps(order))
    while remaining:
        seed = min(remaining)
        orbit = {relabel_mask(seed, image) for image in maps}
        if not orbit <= set(labeled_admissible(order)):
            raise AssertionError("admissibility is not relabeling invariant")
        if seed != min(orbit):
            raise AssertionError("orbit partition lost its canonical element")
        classes.append(seed)
        remaining.difference_update(orbit)
    return tuple(classes)


@cache
def canonical_isomorphisms(mask: int, order: int) -> tuple[int, tuple[tuple[int, ...], ...]]:
    best: int | None = None
    witnesses: list[tuple[int, ...]] = []
    for permutation, image in relabel_maps(order):
        transformed = relabel_mask(mask, image)
        if best is None or transformed < best:
            best = transformed
            witnesses = [permutation]
        elif transformed == best:
            witnesses.append(permutation)
    assert best is not None
    return best, tuple(witnesses)


@cache
def automorphisms(mask: int, order: int) -> tuple[tuple[int, ...], ...]:
    return tuple(
        permutation
        for permutation, image in relabel_maps(order)
        if relabel_mask(mask, image) == mask
    )


def partition_orbits(
    items: Iterable[tuple[int, ...]],
    group: Sequence[Sequence[int]],
) -> tuple[tuple[tuple[int, ...], ...], ...]:
    remaining = set(items)
    result = []
    while remaining:
        seed = min(remaining)
        orbit = {
            tuple(sorted(action[vertex] for vertex in seed))
            for action in group
        }
        result.append(tuple(sorted(orbit)))
        remaining.difference_update(orbit)
    return tuple(sorted(result))


@cache
def vertex_orbits(mask: int, order: int) -> tuple[tuple[int, ...], ...]:
    raw = partition_orbits(
        ((vertex,) for vertex in range(order)),
        automorphisms(mask, order),
    )
    return tuple(tuple(item[0] for item in orbit) for orbit in raw)


@cache
def pair_orbits(mask: int, order: int) -> tuple[tuple[tuple[int, int], ...], ...]:
    return partition_orbits(edge_list(order), automorphisms(mask, order))


def delete_vertex(mask: int, order: int, deleted: int) -> int:
    survivors = [vertex for vertex in range(order) if vertex != deleted]
    new_label = {vertex: index for index, vertex in enumerate(survivors)}
    new_positions = edge_positions(order - 1)
    result = 0
    for index, (left, right) in enumerate(edge_list(order)):
        if left == deleted or right == deleted or not mask & (1 << index):
            continue
        edge = tuple(sorted((new_label[left], new_label[right])))
        result |= 1 << new_positions[edge]
    return result


def orbit_signature(
    raw_neighbors: Sequence[int],
    isomorphism: Sequence[int],
    vertex_lookup: Mapping[int, int],
    pair_lookup: Mapping[tuple[int, int], int],
) -> tuple[tuple[tuple[int, int], ...], tuple[tuple[int, int], ...]]:
    mapped = sorted(isomorphism[vertex] for vertex in raw_neighbors)
    vertex_counts = Counter(vertex_lookup[vertex] for vertex in mapped)
    pair_counts = Counter(pair_lookup[pair] for pair in combinations(mapped, 2))
    return tuple(sorted(vertex_counts.items())), tuple(sorted(pair_counts.items()))


@cache
def build_transition(order: int) -> dict[str, object]:
    """Rebuild every orbit-refined ``order -> order+1`` row."""
    if order < 1 or order > 6:
        raise ValueError("transition order must be in 1,...,6")
    lower = unlabeled_classes(order)
    upper = unlabeled_classes(order + 1)
    lower_index = {mask: index for index, mask in enumerate(lower)}
    row_meta: list[dict[str, object]] = []
    matrix: list[list[int]] = []
    row_lookup: dict[tuple[str, int, int], int] = {}

    for lower_i, mask in enumerate(lower):
        rows = adjacency(mask, order)
        positions = edge_positions(order)
        records: list[dict[str, object]] = [{
            "kind": "deletion",
            "lower_index": lower_i,
            "lower_mask": mask,
            "orbit_index": 0,
            "orbit": (),
            "orbit_size": 1,
            "rhs_multiplier": N - order,
        }]
        for orbit_i, orbit in enumerate(vertex_orbits(mask, order)):
            degrees = {rows[vertex].bit_count() for vertex in orbit}
            if len(degrees) != 1:
                raise AssertionError("vertex orbit mixes internal degrees")
            degree = next(iter(degrees))
            records.append({
                "kind": "vertex",
                "lower_index": lower_i,
                "lower_mask": mask,
                "orbit_index": orbit_i,
                "orbit": orbit,
                "orbit_size": len(orbit),
                "internal_degree": degree,
                "rhs_multiplier": len(orbit) * (K - degree),
            })
        for orbit_i, orbit in enumerate(pair_orbits(mask, order)):
            edge_flags = {
                bool(mask & (1 << positions[pair]))
                for pair in orbit
            }
            commons = {
                (rows[left] & rows[right]).bit_count()
                for left, right in orbit
            }
            if len(edge_flags) != 1 or len(commons) != 1:
                raise AssertionError("pair orbit mixes edge/common-neighbor data")
            is_edge = next(iter(edge_flags))
            internal_common = next(iter(commons))
            target = LAMBDA if is_edge else MU
            records.append({
                "kind": "pair",
                "lower_index": lower_i,
                "lower_mask": mask,
                "orbit_index": orbit_i,
                "orbit": orbit,
                "orbit_size": len(orbit),
                "is_edge": is_edge,
                "internal_common_neighbors": internal_common,
                "rhs_multiplier": len(orbit) * (target - internal_common),
            })
        for record in records:
            key = (
                str(record["kind"]),
                lower_i,
                int(record["orbit_index"]),
            )
            row_lookup[key] = len(row_meta)
            row_meta.append(record)
            matrix.append([0] * len(upper))

    isomorphism_checks = 0
    rooted_cards = 0
    for column, upper_mask in enumerate(upper):
        upper_rows = adjacency(upper_mask, order + 1)
        for root in range(order + 1):
            raw_card = delete_vertex(upper_mask, order + 1, root)
            canonical, isomorphisms = canonical_isomorphisms(raw_card, order)
            lower_i = lower_index[canonical]
            v_orbits = vertex_orbits(canonical, order)
            p_orbits = pair_orbits(canonical, order)
            v_lookup = {
                vertex: orbit_i
                for orbit_i, orbit in enumerate(v_orbits)
                for vertex in orbit
            }
            p_lookup = {
                pair: orbit_i
                for orbit_i, orbit in enumerate(p_orbits)
                for pair in orbit
            }
            survivors = [vertex for vertex in range(order + 1) if vertex != root]
            raw_neighbors = [
                raw_vertex
                for raw_vertex, old_vertex in enumerate(survivors)
                if upper_rows[root] & (1 << old_vertex)
            ]
            signatures = {
                orbit_signature(raw_neighbors, iso, v_lookup, p_lookup)
                for iso in isomorphisms
            }
            if len(signatures) != 1:
                raise AssertionError("orbit coefficient depends on chosen isomorphism")
            isomorphism_checks += len(isomorphisms)
            rooted_cards += 1
            vertex_signature, pair_signature = next(iter(signatures))
            matrix[row_lookup[("deletion", lower_i, 0)]][column] += 1
            for orbit_i, count in vertex_signature:
                matrix[row_lookup[("vertex", lower_i, orbit_i)]][column] += count
            for orbit_i, count in pair_signature:
                matrix[row_lookup[("pair", lower_i, orbit_i)]][column] += count

    # Direct partition checks give the coefficient semantics independently of
    # any right-hand-side identity.
    semantic_checks = 0
    for lower_i, lower_mask in enumerate(lower):
        deletion_row = matrix[row_lookup[("deletion", lower_i, 0)]]
        vertex_rows = [
            matrix[row_lookup[("vertex", lower_i, orbit_i)]]
            for orbit_i in range(len(vertex_orbits(lower_mask, order)))
        ]
        pair_rows = [
            matrix[row_lookup[("pair", lower_i, orbit_i)]]
            for orbit_i in range(len(pair_orbits(lower_mask, order)))
        ]
        for column, upper_mask in enumerate(upper):
            root_degrees = []
            for root in range(order + 1):
                card, _ = canonical_isomorphisms(
                    delete_vertex(upper_mask, order + 1, root),
                    order,
                )
                if card == lower_mask:
                    root_degrees.append(adjacency(upper_mask, order + 1)[root].bit_count())
            if deletion_row[column] != len(root_degrees):
                raise AssertionError("deletion coefficient has wrong rooted count")
            if sum(row[column] for row in vertex_rows) != sum(root_degrees):
                raise AssertionError("vertex-orbit coefficients do not partition neighbors")
            if sum(row[column] for row in pair_rows) != sum(
                math.comb(degree, 2) for degree in root_degrees
            ):
                raise AssertionError("pair-orbit coefficients do not partition neighbor pairs")
            semantic_checks += 3

    return {
        "order": order,
        "lower": lower,
        "upper": upper,
        "row_meta": tuple(row_meta),
        "matrix": tuple(tuple(row) for row in matrix),
        "rooted_cards": rooted_cards,
        "isomorphism_invariance_checks": isomorphism_checks,
        "coefficient_semantic_checks": semantic_checks,
    }


def transition_rhs(
    transition: Mapping[str, object],
    lower_counts: Sequence[int],
) -> tuple[int, ...]:
    if len(lower_counts) != len(transition["lower"]):
        raise AssertionError("lower-count vector has wrong length")
    return tuple(
        int(record["rhs_multiplier"]) * int(lower_counts[int(record["lower_index"])])
        for record in transition["row_meta"]
    )


def matvec(
    matrix: Sequence[Sequence[int]],
    vector: Sequence[int],
) -> tuple[int, ...]:
    return tuple(
        sum(coefficient * value for coefficient, value in zip(row, vector))
        for row in matrix
    )


def modular_rank(
    matrix: Sequence[Sequence[int]],
    prime: int,
) -> int:
    work = [[value % prime for value in row] for row in matrix]
    if not work:
        return 0
    pivot_row = 0
    columns = len(work[0])
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        inverse = pow(work[pivot_row][column], -1, prime)
        for index in range(column, columns):
            work[pivot_row][index] = work[pivot_row][index] * inverse % prime
        for row in range(pivot_row + 1, len(work)):
            factor = work[row][column]
            if not factor:
                continue
            for index in range(column, columns):
                work[row][index] = (
                    work[row][index] - factor * work[pivot_row][index]
                ) % prime
        pivot_row += 1
        if pivot_row == len(work):
            break
    return pivot_row


@cache
def transition_rank(order: int, prime: int, selector_column: int = -1) -> int:
    transition = build_transition(order)
    matrix = transition["matrix"]
    if selector_column < 0:
        augmented = matrix
    else:
        selector = tuple(
            1 if index == selector_column else 0
            for index in range(len(transition["upper"]))
        )
        augmented = matrix + (selector,)
    return modular_rank(augmented, prime)


def parse_fraction(value: object, label: str) -> Fraction:
    if not isinstance(value, str):
        raise AssertionError(f"{label} is not an exact string")
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as error:
        raise AssertionError(f"{label} is not a valid exact rational") from error


def evaluate_affine_formula(
    record: Mapping[str, object],
    n3: int,
    h11: int,
) -> int:
    expected = {"constant", "n3_coefficient", "h11_coefficient"}
    if set(record) != expected:
        raise AssertionError("source formula record has unexpected keys")
    value = (
        parse_fraction(record["constant"], "constant")
        + parse_fraction(record["n3_coefficient"], "n3 coefficient") * n3
        + parse_fraction(record["h11_coefficient"], "h11 coefficient") * h11
    )
    if value.denominator != 1:
        raise AssertionError("source formula is nonintegral at the checked point")
    return value.numerator


def source_six_counts(
    source21: Mapping[str, object],
    classes6: Sequence[int],
) -> tuple[tuple[int, ...], int]:
    try:
        formulas = source21["formula_tables"]["six"]
        mapping = source21["independent_graph_census"]["source_index_alignment"][
            "N_to_canonical_positions_zero_based"
        ]
    except (KeyError, TypeError) as error:
        raise AssertionError("Wave-21 source result lacks six-count data") from error
    if not isinstance(formulas, Mapping) or set(formulas) != {
        str(index) for index in range(1, 63)
    }:
        raise AssertionError("Wave-21 six-formula table is incomplete")
    if not isinstance(mapping, list) or len(mapping) != 62:
        raise AssertionError("Wave-21 N-to-canonical mapping is incomplete")
    positions = [
        require_plain_int(value, f"source mapping {index}")
        for index, value in enumerate(mapping)
    ]
    if sorted(positions) != list(range(62)):
        raise AssertionError("Wave-21 N-to-canonical mapping is not bijective")
    counts = [None] * 62
    for source_index, canonical_position in enumerate(positions, start=1):
        count = evaluate_affine_formula(formulas[str(source_index)], N3, 0)
        if count < 0:
            raise AssertionError("source six-count is negative")
        counts[canonical_position] = count
    parsed = tuple(int(value) for value in counts)
    if sum(parsed) != math.comb(N, 6):
        raise AssertionError("source six-count total is wrong")
    n3_position = positions[2]
    alignment = source21["independent_graph_census"]["N3_definition_alignment"]
    if (
        alignment.get("source_index") != 3
        or alignment.get("canonical_mask") != classes6[n3_position]
        or parsed[n3_position] != N3
    ):
        raise AssertionError("N3 source coordinate does not align at 705")
    return parsed, n3_position


def c7_with_chords(chords: Sequence[Sequence[int]]) -> int:
    edges = {
        tuple(sorted((vertex, (vertex + 1) % 7)))
        for vertex in range(7)
    }
    for chord in chords:
        if (
            not isinstance(chord, list)
            or len(chord) != 2
            or any(type(vertex) is not int for vertex in chord)
        ):
            raise AssertionError("source Hamiltonian chord is malformed")
        edge = tuple(sorted(chord))
        if edge[0] == edge[1] or not (0 <= edge[0] < edge[1] < 7):
            raise AssertionError("source Hamiltonian chord is invalid")
        edges.add(edge)
    positions = edge_positions(7)
    return sum(1 << positions[edge] for edge in edges)


def source_hamiltonian_masks(
    source22: Mapping[str, object],
    classes7: Sequence[int],
) -> tuple[int, ...]:
    try:
        alignment = source22["hamiltonian_alignment"]
        records = alignment["source_H_records"]
        mapping = alignment["source_H_to_canonical_mask"]
    except (KeyError, TypeError) as error:
        raise AssertionError("Wave-22 result lacks Hamiltonian alignment") from error
    if not isinstance(records, list) or len(records) != 19:
        raise AssertionError("Wave-22 Hamiltonian record list is incomplete")
    masks = []
    for index, record in enumerate(records):
        if not isinstance(record, Mapping) or record.get("source_index") != index:
            raise AssertionError("Wave-22 Hamiltonian records are reordered")
        raw = c7_with_chords(record.get("extra_chords"))
        canonical, _ = canonical_isomorphisms(raw, 7)
        if record.get("canonical_mask") != canonical:
            raise AssertionError(f"Wave-22 H_{index} canonical mask is wrong")
        if mapping.get(str(index)) != canonical:
            raise AssertionError(f"Wave-22 H_{index} mapping disagrees with record")
        if canonical not in classes7:
            raise AssertionError(f"Wave-22 H_{index} is outside the admissible census")
        masks.append(canonical)
    if len(set(masks)) != 19:
        raise AssertionError("Hamiltonian alignment repeats a graph class")
    return tuple(masks)


def verify_freeze(repo_root: Path, freeze_path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in freeze_path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        digest, relative = line.split(None, 1)
        relative = relative.strip()
        if relative in entries:
            raise AssertionError("preinspection freeze repeats a path")
        current = sha256_file(repo_root / relative)
        if current != digest:
            raise AssertionError(f"candidate file changed after preinspection: {relative}")
        entries[relative] = digest
    if len(entries) != 10:
        raise AssertionError("preinspection freeze must cover exactly 10 discovery files")
    return entries


def scan_candidate_texts(repo_root: Path, frozen: Mapping[str, str]) -> None:
    for relative in frozen:
        path = repo_root / relative
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if DRIVE_PATH.search(text) or POSIX_HOME_PATH.search(text.replace("\\", "/")):
            raise AssertionError(f"candidate artifact leaks an absolute path: {relative}")


def validate_candidate(
    witness: Mapping[str, object],
    source21: Mapping[str, object],
    source22: Mapping[str, object],
) -> dict[str, object]:
    reject_private_paths(witness)
    expected_top = {
        "schema_version",
        "claim_label",
        "scope",
        "parameters",
        "independent_lower_counts",
        "source_six_count_gate",
        "order_seven_affine_family",
        "hamiltonian_comparison",
        "discovery_runs",
        "warnings",
    }
    if set(witness) != expected_top:
        raise AssertionError("witness top-level fields are missing or unexpected")
    if witness["schema_version"] != 1:
        raise AssertionError("unsupported witness schema")
    if witness["claim_label"] != "CANDIDATE_PENDING_INDEPENDENT_VERIFICATION":
        raise AssertionError("candidate discovery label is not frozen")
    expected_parameters = {
        "n": N,
        "k": K,
        "lambda": LAMBDA,
        "mu": MU,
        "n3": N3,
        "z_min": Z_MIN,
        "z_max": Z_MAX,
        "h11_min": 4 * Z_MIN,
        "h11_max": 4 * Z_MAX,
    }
    if witness["parameters"] != expected_parameters:
        raise AssertionError("witness parameter block differs from the frozen scope")

    # Complete labeled and unlabeled census, orders one through seven.
    labeled_counts = {
        str(order): len(labeled_admissible(order))
        for order in range(1, 8)
    }
    unlabeled_counts = {
        str(order): len(unlabeled_classes(order))
        for order in range(1, 8)
    }
    if tuple(unlabeled_counts[str(order)] for order in range(1, 8)) != EXPECTED_UNLABELED:
        raise AssertionError("independent unlabeled census differs")
    if labeled_counts["7"] != EXPECTED_LABELED_SEVEN:
        raise AssertionError("independent labeled order-seven census differs")

    lower_records = witness["independent_lower_counts"]
    if not isinstance(lower_records, list) or len(lower_records) != 5:
        raise AssertionError("lower-count witness must contain orders 1,...,5")
    lower_counts: tuple[int, ...] | None = None
    lower_rank_records: dict[str, int] = {}
    full_rank_primes = {1: 3, 2: 2, 3: 5, 4: 3}
    for order, record in enumerate(lower_records, start=1):
        if not isinstance(record, Mapping) or record.get("order") != order:
            raise AssertionError("lower-count records are missing or reordered")
        allowed_keys = {"order", "canonical_masks", "counts"}
        if order > 1:
            allowed_keys.add("maximum_rounding_error")
        if set(record) != allowed_keys:
            raise AssertionError(f"order-{order} lower-count record has unexpected fields")
        masks = record["canonical_masks"]
        if masks != list(unlabeled_classes(order)):
            raise AssertionError(f"order-{order} lower masks differ or are reordered")
        raw_counts = record["counts"]
        if not isinstance(raw_counts, list) or len(raw_counts) != len(masks):
            raise AssertionError(f"order-{order} lower count vector has wrong length")
        parsed = tuple(
            require_plain_int(value, f"order-{order} count {index}")
            for index, value in enumerate(raw_counts)
        )
        if any(value < 0 for value in parsed) or sum(parsed) != math.comb(N, order):
            raise AssertionError(f"order-{order} lower counts fail positivity or total")
        if order == 1:
            if parsed != (N,):
                raise AssertionError("order-one count must equal n")
        else:
            assert lower_counts is not None
            transition = build_transition(order - 1)
            if matvec(transition["matrix"], parsed) != transition_rhs(
                transition, lower_counts
            ):
                raise AssertionError(f"order-{order-1}->{order} exact rows fail")
            prime = full_rank_primes[order - 1]
            rank = transition_rank(order - 1, prime)
            if rank != len(parsed):
                raise AssertionError(f"order-{order-1}->{order} uniqueness rank fails")
            lower_rank_records[f"{order-1}->{order}_mod_{prime}"] = rank
        lower_counts = parsed
    assert lower_counts is not None

    transition5 = build_transition(5)
    source6, n3_column = source_six_counts(source21, transition5["upper"])
    expected5 = transition_rhs(transition5, lower_counts)
    actual5 = matvec(transition5["matrix"], source6)
    if actual5 != expected5:
        bad = [
            index
            for index, (left, right) in enumerate(zip(actual5, expected5))
            if left != right
        ]
        raise AssertionError(f"source six-count gate fails rows {bad[:10]}")
    if witness["source_six_count_gate"] != {
        "transition": "5->6",
        "rows_checked": len(transition5["matrix"]),
        "exact_maximum_residual": 0,
    }:
        raise AssertionError("source six-count gate disclosure differs")
    rank5 = transition_rank(5, 7)
    rank5_closed = transition_rank(5, 7, n3_column)
    if rank5 != 61 or rank5_closed != 62:
        raise AssertionError("5->6 rank or n3 closure differs")

    transition6 = build_transition(6)
    matrix6 = transition6["matrix"]
    classes7 = transition6["upper"]
    family = witness["order_seven_affine_family"]
    expected_family_keys = {
        "coordinate",
        "records",
        "exact_rows_checked",
        "minimum_count_at_z_min",
        "minimum_count_at_z_max",
        "support_size_at_z_min",
        "support_size_at_z_max",
        "total_at_every_z",
    }
    if not isinstance(family, Mapping) or set(family) != expected_family_keys:
        raise AssertionError("affine-family block is missing or has hidden fields")
    if family["coordinate"] != "z=h11/4":
        raise AssertionError("affine coordinate differs")
    records = family["records"]
    if not isinstance(records, list) or len(records) != len(classes7):
        raise AssertionError("affine family does not cover all 208 classes")
    base: list[int] = []
    delta: list[int] = []
    for index, (record, expected_mask) in enumerate(zip(records, classes7)):
        if not isinstance(record, Mapping) or set(record) != {
            "canonical_mask", "count_at_z_min", "delta_per_z"
        }:
            raise AssertionError(f"seven-record {index} is malformed")
        mask = require_plain_int(record["canonical_mask"], f"seven mask {index}")
        if mask != expected_mask:
            raise AssertionError("seven-class records are missing or reordered")
        base.append(require_plain_int(record["count_at_z_min"], f"base {index}"))
        delta.append(require_plain_int(record["delta_per_z"], f"delta {index}"))
    base_tuple = tuple(base)
    delta_tuple = tuple(delta)
    if not any(delta_tuple):
        raise AssertionError("kernel delta is zero")
    rhs6 = transition_rhs(transition6, source6)
    if matvec(matrix6, base_tuple) != rhs6:
        raise AssertionError("affine base fails an exact extension row")
    zero = (0,) * len(matrix6)
    if matvec(matrix6, delta_tuple) != zero:
        raise AssertionError("affine delta is not an exact integer kernel vector")
    if sum(base_tuple) != math.comb(N, 7) or sum(delta_tuple) != 0:
        raise AssertionError("affine family total is wrong")

    endpoint_max = tuple(
        base_value + (Z_MAX - Z_MIN) * step
        for base_value, step in zip(base_tuple, delta_tuple)
    )
    if min(base_tuple) < 0 or min(endpoint_max) < 0:
        raise AssertionError("affine family is negative at an endpoint")
    # Explicitly replay all 353 allowed integer parameter values.
    minimum_over_all_z = None
    all_z_checks = 0
    for z in range(Z_MIN, Z_MAX + 1):
        vector = tuple(
            base_value + (z - Z_MIN) * step
            for base_value, step in zip(base_tuple, delta_tuple)
        )
        if min(vector) < 0 or sum(vector) != math.comb(N, 7):
            raise AssertionError(f"affine family fails at z={z}")
        minimum_over_all_z = (
            min(vector)
            if minimum_over_all_z is None
            else min(minimum_over_all_z, min(vector))
        )
        all_z_checks += 1

    expected_family_summary = {
        "exact_rows_checked": len(matrix6),
        "minimum_count_at_z_min": min(base_tuple),
        "minimum_count_at_z_max": min(endpoint_max),
        "support_size_at_z_min": sum(value > 0 for value in base_tuple),
        "support_size_at_z_max": sum(value > 0 for value in endpoint_max),
        "total_at_every_z": math.comb(N, 7),
    }
    for key, expected in expected_family_summary.items():
        if family[key] != expected:
            raise AssertionError(f"affine summary field {key} differs")

    rank6 = transition_rank(6, 5)
    if rank6 != 207:
        raise AssertionError(f"6->7 rank mod 5 is {rank6}, not 207")

    h_masks = source_hamiltonian_masks(source22, classes7)
    h11_column = classes7.index(h_masks[11])
    rank6_closed = transition_rank(6, 5, h11_column)
    if rank6_closed != 208:
        raise AssertionError("H11 coordinate does not close rank to 208 mod 5")
    if base_tuple[h11_column] != 4 * Z_MIN or delta_tuple[h11_column] != 4:
        raise AssertionError("affine coordinate is not H11=4z")

    comparison = witness["hamiltonian_comparison"]
    if not isinstance(comparison, Mapping) or set(comparison) != {
        "solver_inputs",
        "not_solver_inputs",
        "records",
        "all_19_source_affine_formulas_match",
    }:
        raise AssertionError("Hamiltonian comparison has hidden or missing fields")
    if comparison["solver_inputs"] != ["H_11=4z"]:
        raise AssertionError("Hamiltonian solver-input disclosure differs")
    if comparison["not_solver_inputs"] != [
        f"H_{index}" for index in range(19) if index != 11
    ]:
        raise AssertionError("Hamiltonian non-input disclosure differs")
    if comparison["all_19_source_affine_formulas_match"] is not True:
        raise AssertionError("Hamiltonian formula match disclosure differs")
    h_records = comparison["records"]
    if not isinstance(h_records, list) or len(h_records) != 19:
        raise AssertionError("Hamiltonian comparison does not cover 19 classes")
    formulas7 = source21["formula_tables"]["seven"]
    if not isinstance(formulas7, Mapping) or set(formulas7) != {
        str(index) for index in range(19)
    }:
        raise AssertionError("Wave-21 Hamiltonian formula table is incomplete")
    for index, (record, mask) in enumerate(zip(h_records, h_masks)):
        column = classes7.index(mask)
        expected_record = {
            "source_index": index,
            "canonical_mask": mask,
            "count_at_z_min": base_tuple[column],
            "delta_per_z": delta_tuple[column],
            "used_as_solver_input": index == 11,
        }
        if record != expected_record:
            raise AssertionError(f"H_{index} comparison record differs")
        source_min = evaluate_affine_formula(
            formulas7[str(index)], N3, 4 * Z_MIN
        )
        source_next = evaluate_affine_formula(
            formulas7[str(index)], N3, 4 * (Z_MIN + 1)
        )
        if (
            base_tuple[column] != source_min
            or base_tuple[column] + delta_tuple[column] != source_next
        ):
            raise AssertionError(f"H_{index} formula does not match post hoc")

    row_breakdown = {
        "deletion": sum(record["kind"] == "deletion" for record in transition6["row_meta"]),
        "vertex_orbit": sum(record["kind"] == "vertex" for record in transition6["row_meta"]),
        "edge_pair_orbit": sum(
            record["kind"] == "pair" and bool(record["is_edge"])
            for record in transition6["row_meta"]
        ),
        "nonedge_pair_orbit": sum(
            record["kind"] == "pair" and not bool(record["is_edge"])
            for record in transition6["row_meta"]
        ),
    }
    if row_breakdown != {
        "deletion": 62,
        "vertex_orbit": 207,
        "edge_pair_orbit": 180,
        "nonedge_pair_orbit": 263,
    }:
        raise AssertionError("6->7 row inventory differs")

    return {
        "schema_version": 1,
        "role": "verifier",
        "claim_label": "VERIFIED",
        "candidate_commit": CANDIDATE_COMMIT,
        "scope": (
            "Exact feasibility of the encoded orbit-refined one-vertex "
            "extension relaxation through order seven at n3=705, for every "
            "h11=4z with integer z in 353,...,705"
        ),
        "parameters": expected_parameters,
        "independent_census": {
            "labeled_admissible_by_order": labeled_counts,
            "unlabeled_classes_by_order": unlabeled_counts,
            "canonicalization": "least edge mask under all vertex relabelings",
            "complete_labeled_enumeration": True,
        },
        "lower_source_gate": {
            "orders_1_through_5_exact": True,
            "lower_transition_full_column_ranks": lower_rank_records,
            "five_to_six_rows": len(transition5["matrix"]),
            "five_to_six_rank_mod_7": rank5,
            "five_to_six_rank_with_n3_mod_7": rank5_closed,
            "n3_coordinate_mask": transition5["upper"][n3_column],
            "source_six_vector_exact_rows": "PASS",
        },
        "order_seven_system": {
            "shape": [len(matrix6), len(classes7)],
            "row_breakdown": row_breakdown,
            "rooted_upper_classes_checked": transition6["rooted_cards"],
            "isomorphism_choice_checks": transition6["isomorphism_invariance_checks"],
            "coefficient_partition_checks": transition6["coefficient_semantic_checks"],
            "pair_coefficient_semantics": (
                "Each b_F,P coefficient is the number of pairs in orbit P "
                "whose vertices are both adjacent to the deleted root, summed "
                "over all roots with card F"
            ),
            "matrix_sha256": sha256_bytes(canonical_json_bytes(matrix6)),
            "rhs_sha256": sha256_bytes(canonical_json_bytes(rhs6)),
            "rank_mod_5": rank6,
            "rational_rank": 207,
            "rank_upper_certificate": "nonzero integer delta with A*delta=0",
            "h11_column": h11_column,
            "rank_with_h11_coordinate_mod_5": rank6_closed,
        },
        "affine_certificate": {
            "base_sha256": sha256_bytes(canonical_json_bytes(base_tuple)),
            "delta_sha256": sha256_bytes(canonical_json_bytes(delta_tuple)),
            "A_base_equals_rhs": True,
            "A_delta_equals_zero": True,
            "plain_integer_coordinates": True,
            "z_values_checked": all_z_checks,
            "minimum_at_z_min": min(base_tuple),
            "minimum_at_z_max": min(endpoint_max),
            "minimum_over_all_allowed_z": minimum_over_all_z,
            "support_at_z_min": sum(value > 0 for value in base_tuple),
            "support_at_z_max": sum(value > 0 for value in endpoint_max),
            "nonnegative_on_real_interval_by_affinity": True,
        },
        "hamiltonian_comparison": {
            "H11_is_only_coordinate_needed": True,
            "H11_closes_rank_to_208_mod_5": True,
            "all_19_pinned_source_formulas_match_post_hoc": True,
            "other_18_not_used_by_independent_replay": True,
            "source_panel_alignment_remains_cited_input": True,
        },
        "scope_wall": {
            "relaxation_feasible": True,
            "graph_constructed": False,
            "target_existence_status": "UNKNOWN",
            "bound_improvement": None,
            "overlap_consistency_encoded": False,
        },
    }


def load_json(path: Path) -> Mapping[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise AssertionError(f"{path} is not a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument(
        "--witness",
        type=Path,
        default=Path("attempts/wave23-weighted-extensions/affine-witness.json"),
    )
    parser.add_argument(
        "--source21",
        type=Path,
        default=Path("attempts/wave21-six-vertex-lp/exact-results.json"),
    )
    parser.add_argument(
        "--source22",
        type=Path,
        default=Path("attempts/wave22-full-seven-deck/exact-results.json"),
    )
    parser.add_argument(
        "--freeze",
        type=Path,
        default=Path(
            "verification/wave23-weighted-extensions/preinspection-freeze.sha256"
        ),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    try:
        frozen = verify_freeze(repo_root, repo_root / args.freeze)
        scan_candidate_texts(repo_root, frozen)
        source21_path = repo_root / args.source21
        source22_path = repo_root / args.source22
        if sha256_file(source21_path) != SOURCE21_SHA256:
            raise AssertionError("Wave-21 source input hash differs")
        if sha256_file(source22_path) != SOURCE22_SHA256:
            raise AssertionError("Wave-22 source input hash differs")
        witness_path = repo_root / args.witness
        result = validate_candidate(
            load_json(witness_path),
            load_json(source21_path),
            load_json(source22_path),
        )
        result["frozen_inputs"] = {
            "candidate_files": dict(sorted(frozen.items())),
            "witness_sha256": sha256_file(witness_path),
            "wave21_result_sha256": SOURCE21_SHA256,
            "wave22_result_sha256": SOURCE22_SHA256,
            "privacy_scan": "PASS",
        }
        encoded = canonical_json_bytes(result)
        if args.output:
            output_path = repo_root / args.output
            output_path.write_bytes(encoded)
        else:
            sys.stdout.buffer.write(encoded)
    except (
        AssertionError,
        KeyError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
        OSError,
    ) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
