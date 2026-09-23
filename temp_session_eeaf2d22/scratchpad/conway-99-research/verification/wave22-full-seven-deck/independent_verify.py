#!/usr/bin/env python3
"""Independent exact verifier for the Wave-22 seven-vertex count witness.

This file deliberately does not import or execute any code from
attempts/wave22-full-seven-deck.  Graph classes, deletion decks, finite-field
ranks, Hamiltonian classes, source formulas, and the frozen witness equations
are rebuilt here using only the Python standard library.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
WITNESS_PATH = ROOT / "attempts" / "wave22-full-seven-deck" / "witness.json"
WAVE21_PATH = ROOT / "attempts" / "wave21-six-vertex-lp" / "exact-results.json"
EXPECTED_WITNESS_SHA256 = (
    "d74453faa91e42abbe2343d428296818ae051be579305277eff6f113fe66c47d"
)
EXPECTED_WAVE21_SHA256 = (
    "5e7b6f526985fb719754145944579aacb0e8f38e9e14a54d2075552a3756ff2b"
)

N = 99
K = 14
LAMBDA = 1
MU = 2
N3 = 705
H11 = 2820


class VerificationError(ValueError):
    """Raised when a claimed exact certificate fails a check."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def edge_list(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(itertools.combinations(range(order), 2))


def edge_index(order: int) -> dict[tuple[int, int], int]:
    return {edge: index for index, edge in enumerate(edge_list(order))}


def edge_mask(order: int, edges: Iterable[tuple[int, int]]) -> int:
    indices = edge_index(order)
    result = 0
    for left, right in edges:
        if left == right:
            raise VerificationError("loops are not allowed")
        if left > right:
            left, right = right, left
        result |= 1 << indices[(left, right)]
    return result


def permutation_edge_maps(order: int) -> tuple[tuple[int, ...], ...]:
    """Return old-edge-bit to new-edge-mask maps for every vertex permutation."""

    edges = edge_list(order)
    indices = edge_index(order)
    maps: list[tuple[int, ...]] = []
    for permutation in itertools.permutations(range(order)):
        mapped: list[int] = []
        for left, right in edges:
            new_left, new_right = sorted((permutation[left], permutation[right]))
            mapped.append(1 << indices[(new_left, new_right)])
        maps.append(tuple(mapped))
    return tuple(maps)


def set_bit_positions(mask: int) -> tuple[int, ...]:
    positions: list[int] = []
    while mask:
        lowest = mask & -mask
        positions.append(lowest.bit_length() - 1)
        mask ^= lowest
    return tuple(positions)


def permuted_orbit(mask: int, maps: Sequence[Sequence[int]]) -> set[int]:
    positions = set_bit_positions(mask)
    orbit: set[int] = set()
    for mapping in maps:
        transformed = 0
        for position in positions:
            transformed |= mapping[position]
        orbit.add(transformed)
    return orbit


def canonical_mask(mask: int, maps: Sequence[Sequence[int]]) -> int:
    positions = set_bit_positions(mask)
    best: int | None = None
    for mapping in maps:
        transformed = 0
        for position in positions:
            transformed |= mapping[position]
        if best is None or transformed < best:
            best = transformed
    if best is None:
        raise AssertionError("permutation collection must be nonempty")
    return best


def adjacency_bits(order: int, mask: int) -> tuple[int, ...]:
    adjacency = [0] * order
    for bit, (left, right) in enumerate(edge_list(order)):
        if (mask >> bit) & 1:
            adjacency[left] |= 1 << right
            adjacency[right] |= 1 << left
    return tuple(adjacency)


def locally_admissible(order: int, mask: int) -> bool:
    """Check the inherited lambda<=1 / mu<=2 common-neighbor inequalities."""

    adjacency = adjacency_bits(order, mask)
    indices = edge_index(order)
    for left, right in edge_list(order):
        common = (adjacency[left] & adjacency[right]).bit_count()
        is_edge = (mask >> indices[(left, right)]) & 1
        if is_edge:
            if common > LAMBDA:
                return False
        elif common > MU:
            return False
    return True


@dataclass(frozen=True)
class Census:
    order: int
    total_unlabeled_classes: int
    admissible_representatives: tuple[int, ...]
    admissible_labeled_masks: int
    representative_of: tuple[int, ...] | None


def enumerate_unlabeled_census(
    order: int,
    maps: Sequence[Sequence[int]],
    *,
    retain_representative_map: bool,
) -> Census:
    """Partition every labeled graph into exact S_order orbits.

    Masks are scanned in increasing order, so the first unmarked member of an
    orbit is necessarily its least numerical representative.  Orbit sizes
    therefore also give the exact labeled count without testing every labeled
    graph separately.
    """

    mask_count = 1 << len(edge_list(order))
    seen = bytearray(mask_count)
    representatives = [0] * mask_count if retain_representative_map else None
    admissible: list[int] = []
    labeled_admissible = 0
    total_classes = 0

    for mask in range(mask_count):
        if seen[mask]:
            continue
        orbit = permuted_orbit(mask, maps)
        if min(orbit) != mask:
            raise AssertionError("increasing scan did not find the orbit minimum")
        total_classes += 1
        for member in orbit:
            seen[member] = 1
            if representatives is not None:
                representatives[member] = mask
        if locally_admissible(order, mask):
            admissible.append(mask)
            labeled_admissible += len(orbit)

    if 0 in seen:
        raise AssertionError("census failed to cover the full labeled universe")

    return Census(
        order=order,
        total_unlabeled_classes=total_classes,
        admissible_representatives=tuple(admissible),
        admissible_labeled_masks=labeled_admissible,
        representative_of=tuple(representatives) if representatives is not None else None,
    )


def deletion_mask(order: int, mask: int, deleted_vertex: int) -> int:
    """Delete one vertex and compact the remaining labels in increasing order."""

    old_to_new: dict[int, int] = {}
    next_label = 0
    for old_label in range(order):
        if old_label == deleted_vertex:
            continue
        old_to_new[old_label] = next_label
        next_label += 1

    reduced_edges: list[tuple[int, int]] = []
    for bit, (left, right) in enumerate(edge_list(order)):
        if not ((mask >> bit) & 1):
            continue
        if left == deleted_vertex or right == deleted_vertex:
            continue
        reduced_edges.append((old_to_new[left], old_to_new[right]))
    return edge_mask(order - 1, reduced_edges)


def deletion_deck_matrix(
    six_census: Census, seven_census: Census
) -> tuple[tuple[int, ...], ...]:
    if six_census.representative_of is None:
        raise AssertionError("six-vertex representative lookup was not retained")
    six_representatives = six_census.admissible_representatives
    six_position = {mask: index for index, mask in enumerate(six_representatives)}
    rows = [
        [0 for _ in seven_census.admissible_representatives]
        for _ in six_representatives
    ]

    for column, seven_mask in enumerate(seven_census.admissible_representatives):
        for deleted in range(7):
            reduced = deletion_mask(7, seven_mask, deleted)
            canonical_six = six_census.representative_of[reduced]
            if canonical_six not in six_position:
                raise AssertionError("admissible seven-graph had inadmissible deletion")
            rows[six_position[canonical_six]][column] += 1

    if any(sum(rows[row][column] for row in range(len(rows))) != 7
           for column in range(len(rows[0]))):
        raise AssertionError("a deletion-deck column does not sum to seven")
    return tuple(tuple(row) for row in rows)


def rank_mod_prime(matrix: Sequence[Sequence[int]], prime: int) -> int:
    work = [[entry % prime for entry in row] for row in matrix]
    row_count = len(work)
    column_count = len(work[0]) if work else 0
    pivot_row = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(pivot_row, row_count) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        inverse = pow(work[pivot_row][column], -1, prime)
        work[pivot_row] = [(entry * inverse) % prime for entry in work[pivot_row]]
        for row in range(row_count):
            if row == pivot_row or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                (entry - factor * pivot_entry) % prime
                for entry, pivot_entry in zip(work[row], work[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def hamiltonian_cycle_masks() -> tuple[int, ...]:
    """Enumerate the (7-1)!/2 undirected Hamiltonian cycles exactly once."""

    cycles: set[int] = set()
    for tail in itertools.permutations(range(1, 7)):
        if tail[0] > tail[-1]:
            continue
        order = (0,) + tail
        edges = [
            (order[index], order[(index + 1) % 7])
            for index in range(7)
        ]
        cycles.add(edge_mask(7, edges))
    if len(cycles) != math.factorial(6) // 2:
        raise AssertionError("Hamiltonian-cycle enumeration is incomplete")
    return tuple(sorted(cycles))


def contains_hamiltonian_cycle(mask: int, cycles: Sequence[int]) -> bool:
    return any(mask & cycle == cycle for cycle in cycles)


# Independent visual transcription of the green panels in hamiltonian_7.jpg.
# Perimeter vertices are 0 at the top, then 1,...,6 clockwise.
FIGURE_EXTRA_CHORDS: tuple[tuple[tuple[int, int], ...], ...] = (
    (),
    ((6, 1),),
    ((5, 2),),
    ((0, 5), (0, 2)),
    ((0, 5), (0, 3)),
    ((0, 4), (0, 3)),
    ((6, 4), (1, 3)),
    ((6, 1), (5, 2)),
    ((6, 1), (0, 4)),
    ((6, 3), (1, 4)),
    ((6, 1), (6, 4), (1, 3)),
    ((0, 2), (0, 5), (1, 4)),
    ((0, 4), (0, 3), (6, 1)),
    ((0, 4), (0, 3), (5, 2)),
    ((0, 5), (0, 3), (4, 2)),
    ((6, 4), (1, 3), (5, 2)),
    ((6, 1), (5, 2), (0, 3)),
    ((6, 1), (5, 2), (6, 4), (1, 3)),
    ((6, 1), (5, 2), (0, 4), (0, 3)),
)


def figure_hamiltonian_masks(
    seven_maps: Sequence[Sequence[int]],
) -> tuple[int, ...]:
    perimeter = tuple((vertex, (vertex + 1) % 7) for vertex in range(7))
    perimeter_mask = edge_mask(7, perimeter)
    result: list[int] = []
    for chords in FIGURE_EXTRA_CHORDS:
        labeled = perimeter_mask | edge_mask(7, chords)
        result.append(canonical_mask(labeled, seven_maps))
    return tuple(result)


def published_hamiltonian_values() -> tuple[int, ...]:
    """Evaluate the paper's displayed lines 177--195 at the frozen point."""

    n, k, n3, h11 = N, K, N3, H11
    base = n * k * (k - 2) * (k - 4)
    values = (
        Fraction(n * k * (k - 2) * (k - 4) * (2 * k * k - 30 * k + 133), 14)
        - 10 * n3
        - h11,
        Fraction(n * k * (k - 2) * (2 * k * k - 25 * k + 68), 2)
        + 16 * n3
        + Fraction(3 * h11, 2),
        n * k * (k - 2) * (k - 4) * (k - 8)
        + 12 * n3
        + Fraction(5 * h11, 2),
        base - 2 * n3 - Fraction(h11, 2),
        base - 4 * n3,
        Fraction(base, 2) - Fraction(h11, 2),
        base - 8 * n3,
        Fraction(base, 2) - Fraction(3 * h11, 2),
        2 * base - 8 * n3 - 2 * h11,
        base - 2 * n3 - Fraction(3 * h11, 2),
        2 * n3,
        h11,
        Fraction(n * k * (k - 2), 4) - n3 + Fraction(h11, 4),
        Fraction(h11, 2),
        4 * n3,
        2 * n3,
        h11 - 2 * n3,
        Fraction(n * k * (k - 2), 4) - n3,
        n3 - Fraction(h11, 4),
    )
    if any(value.denominator != 1 for value in values):
        raise VerificationError("a published Hamiltonian count is nonintegral")
    integers = tuple(int(value) for value in values)
    if any(value < 0 for value in integers):
        raise VerificationError("a published Hamiltonian count is negative")
    return integers


@dataclass(frozen=True)
class Context:
    six_census: Census
    seven_census: Census
    deck: tuple[tuple[int, ...], ...]
    ranks: dict[int, int]
    hamiltonian_class_masks: tuple[int, ...]
    figure_masks: tuple[int, ...]
    hamiltonian_values: tuple[int, ...]
    six_counts_canonical_order: tuple[int, ...]
    wave21_sha256: str


def evaluate_six_counts(
    six_census: Census,
) -> tuple[tuple[int, ...], str]:
    wave21_hash = sha256_file(WAVE21_PATH)
    if wave21_hash != EXPECTED_WAVE21_SHA256:
        raise VerificationError(
            f"Wave-21 input hash drifted: {wave21_hash} != {EXPECTED_WAVE21_SHA256}"
        )
    artifact = json.loads(WAVE21_PATH.read_text(encoding="utf-8"))
    formulas = artifact["formula_tables"]["six"]
    mapping = artifact["independent_graph_census"]["source_index_alignment"][
        "N_to_canonical_positions_zero_based"
    ]
    if len(formulas) != 62 or len(mapping) != 62:
        raise VerificationError("Wave-21 six-type input does not have 62 entries")
    if sorted(mapping) != list(range(62)):
        raise VerificationError("Wave-21 N-to-canonical alignment is not bijective")
    if len(six_census.admissible_representatives) != 62:
        raise VerificationError("independent six-vertex census did not find 62 classes")

    counts = [0] * 62
    for source_index in range(1, 63):
        record = formulas[str(source_index)]
        value = (
            Fraction(record["constant"])
            + Fraction(record["n3_coefficient"]) * N3
            + Fraction(record["h11_coefficient"]) * H11
        )
        if value.denominator != 1 or value < 0:
            raise VerificationError(
                f"N_{source_index} is not a nonnegative integer at n3={N3}"
            )
        counts[mapping[source_index - 1]] = int(value)
    if sum(counts) != math.comb(N, 6):
        raise VerificationError("six-vertex counts do not total C(99,6)")
    return tuple(counts), wave21_hash


def build_context() -> Context:
    six_maps = permutation_edge_maps(6)
    seven_maps = permutation_edge_maps(7)
    six_census = enumerate_unlabeled_census(
        6, six_maps, retain_representative_map=True
    )
    seven_census = enumerate_unlabeled_census(
        7, seven_maps, retain_representative_map=False
    )

    if six_census.total_unlabeled_classes != 156:
        raise VerificationError("order-six full census does not have 156 classes")
    if len(six_census.admissible_representatives) != 62:
        raise VerificationError("order-six admissible census does not have 62 classes")
    if seven_census.total_unlabeled_classes != 1044:
        raise VerificationError("order-seven full census does not have 1044 classes")
    if len(seven_census.admissible_representatives) != 208:
        raise VerificationError("order-seven admissible census does not have 208 classes")
    if seven_census.admissible_labeled_masks != 394020:
        raise VerificationError("order-seven admissible labeled count is not 394020")

    deck = deletion_deck_matrix(six_census, seven_census)
    ranks = {prime: rank_mod_prime(deck, prime) for prime in (2, 3, 5, 7, 11)}

    cycles = hamiltonian_cycle_masks()
    hamiltonian_masks = tuple(
        mask
        for mask in seven_census.admissible_representatives
        if contains_hamiltonian_cycle(mask, cycles)
    )
    figure_masks = figure_hamiltonian_masks(seven_maps)
    if len(hamiltonian_masks) != 19:
        raise VerificationError("independent Hamiltonian census did not find 19 classes")
    if len(set(figure_masks)) != 19:
        raise VerificationError("the 19 source drawings are not distinct classes")
    if set(figure_masks) != set(hamiltonian_masks):
        raise VerificationError("the source drawings do not cover the independent census")

    hamiltonian_values = published_hamiltonian_values()
    six_counts, wave21_hash = evaluate_six_counts(six_census)
    return Context(
        six_census=six_census,
        seven_census=seven_census,
        deck=deck,
        ranks=ranks,
        hamiltonian_class_masks=hamiltonian_masks,
        figure_masks=figure_masks,
        hamiltonian_values=hamiltonian_values,
        six_counts_canonical_order=six_counts,
        wave21_sha256=wave21_hash,
    )


def require_exact_int(value: Any, label: str) -> int:
    if type(value) is not int:
        raise VerificationError(f"{label} must have JSON integer type")
    return value


def validate_witness_data(data: Any, context: Context) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise VerificationError("witness root must be an object")
    parameters = data.get("parameters")
    if not isinstance(parameters, dict):
        raise VerificationError("parameters must be an object")
    expected_parameters = {
        "n": N,
        "k": K,
        "lambda": LAMBDA,
        "mu": MU,
        "n3": N3,
        "h11": H11,
    }
    if set(parameters) != set(expected_parameters):
        raise VerificationError("parameter keys are incomplete or contain extras")
    for key, expected in expected_parameters.items():
        if require_exact_int(parameters[key], f"parameters.{key}") != expected:
            raise VerificationError(f"parameters.{key} changed")

    classes = data.get("classes")
    if not isinstance(classes, list):
        raise VerificationError("classes must be a list")
    expected_masks = context.seven_census.admissible_representatives
    if len(classes) != len(expected_masks):
        raise VerificationError("witness must contain exactly all 208 classes")

    counts: list[int] = []
    observed_masks: list[int] = []
    for index, record in enumerate(classes):
        if not isinstance(record, dict) or set(record) != {"canonical_mask", "count"}:
            raise VerificationError(f"classes[{index}] has the wrong schema")
        mask = require_exact_int(record["canonical_mask"], f"classes[{index}].canonical_mask")
        count = require_exact_int(record["count"], f"classes[{index}].count")
        if count < 0:
            raise VerificationError(f"classes[{index}].count is negative")
        observed_masks.append(mask)
        counts.append(count)
    if tuple(observed_masks) != expected_masks:
        raise VerificationError("class masks/order differ from independent census")

    count_by_mask = dict(zip(observed_masks, counts))
    hamiltonian_observed = tuple(count_by_mask[mask] for mask in context.figure_masks)
    if hamiltonian_observed != context.hamiltonian_values:
        bad = [
            index
            for index, (observed, expected) in enumerate(
                zip(hamiltonian_observed, context.hamiltonian_values)
            )
            if observed != expected
        ]
        raise VerificationError(f"published Hamiltonian counts fail at H indices {bad}")

    total = sum(counts)
    expected_total = math.comb(N, 7)
    if total != expected_total:
        raise VerificationError(f"witness total {total} != C(99,7)={expected_total}")

    residuals: list[int] = []
    for row, six_count in zip(context.deck, context.six_counts_canonical_order):
        left = sum(coefficient * count for coefficient, count in zip(row, counts))
        residuals.append(left - (N - 6) * six_count)
    if any(residuals):
        bad = [index for index, residual in enumerate(residuals) if residual]
        raise VerificationError(f"deletion equations fail in canonical rows {bad}")

    support = [(mask, count) for mask, count in zip(observed_masks, counts) if count]
    support_text = "".join(f"{mask}:{count}\n" for mask, count in support)
    return {
        "class_count": len(counts),
        "support_size": len(support),
        "zero_class_count": len(counts) - len(support),
        "minimum_positive_count": min(count for _, count in support),
        "maximum_count": max(counts),
        "total": total,
        "deletion_rows_passed": len(context.deck),
        "hamiltonian_counts_passed": len(context.figure_masks),
        "support_sha256_verifier_format": hashlib.sha256(
            support_text.encode("ascii")
        ).hexdigest(),
    }


def load_witness() -> tuple[Any, str]:
    witness_hash = sha256_file(WITNESS_PATH)
    if witness_hash != EXPECTED_WITNESS_SHA256:
        raise VerificationError(
            f"witness hash drifted: {witness_hash} != {EXPECTED_WITNESS_SHA256}"
        )
    return json.loads(WITNESS_PATH.read_text(encoding="utf-8")), witness_hash


def exact_results(context: Context, validation: dict[str, Any], witness_hash: str) -> dict[str, Any]:
    seven_reps = context.seven_census.admissible_representatives
    edge_distribution: dict[str, int] = {}
    for mask in context.hamiltonian_class_masks:
        edges = mask.bit_count()
        edge_distribution[str(edges)] = edge_distribution.get(str(edges), 0) + 1

    return {
        "claim_label": "VERIFIED_SCOPED_COUNT_FEASIBILITY",
        "scope": (
            "Exact feasibility at n3=705,h11=2820 of the 62 order-seven "
            "vertex-deletion count equations plus the 19 pinned Hamiltonian "
            "type counts; this is not a graph construction."
        ),
        "parameters": {
            "n": N,
            "k": K,
            "lambda": LAMBDA,
            "mu": MU,
            "n3": N3,
            "h11": H11,
        },
        "source_inputs": {
            "wave21_exact_results": {
                "path": str(WAVE21_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sha256": context.wave21_sha256,
            },
            "witness": {
                "path": str(WITNESS_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sha256": witness_hash,
            },
            "arxiv_2511_06572v1_archive_sha256": (
                "10f8d9ea09dc72f4ca6bce4e9427ff1df32718d2978bb35a16db1af3c27cc39a"
            ),
            "tex_sha256": (
                "0b06fdc1c2951a344592c6af23abd133c4a8a68d717f199e7a0e2d7ceb909d0a"
            ),
            "figure_sha256": (
                "e37f794e7765c947d3ea76104e9c4c61a00517b649d8b7bea9eb67644fe08a2e"
            ),
        },
        "census": {
            "order_6_all_unlabeled": context.six_census.total_unlabeled_classes,
            "order_6_admissible_unlabeled": len(
                context.six_census.admissible_representatives
            ),
            "order_6_admissible_labeled": context.six_census.admissible_labeled_masks,
            "order_7_all_unlabeled": context.seven_census.total_unlabeled_classes,
            "order_7_admissible_unlabeled": len(seven_reps),
            "order_7_admissible_labeled": context.seven_census.admissible_labeled_masks,
            "order_7_hamiltonian_unlabeled": len(context.hamiltonian_class_masks),
            "hamiltonian_edge_distribution": edge_distribution,
        },
        "deletion_matrix": {
            "shape": [len(context.deck), len(context.deck[0])],
            "all_column_sums": 7,
            "finite_field_ranks": {
                str(prime): rank for prime, rank in context.ranks.items()
            },
        },
        "hamiltonian_alignment": {
            "figure_masks_H0_through_H18": list(context.figure_masks),
            "independent_hamiltonian_masks": list(context.hamiltonian_class_masks),
            "formula_values_H0_through_H18": list(context.hamiltonian_values),
            "distinct_figure_classes": len(set(context.figure_masks)),
            "figure_set_equals_independent_census": (
                set(context.figure_masks) == set(context.hamiltonian_class_masks)
            ),
        },
        "witness_validation": validation,
        "conclusion": {
            "count_system_feasible": True,
            "graph_construction": False,
            "target_status": "UNKNOWN",
            "new_bound_beyond_n3_705": None,
            "warning": (
                "The witness is an aggregate vector of induced-type counts. "
                "It supplies no consistent assignment to overlapping subsets "
                "and no 99-vertex adjacency matrix."
            ),
        },
    }


def write_json(path: Path, data: Any) -> None:
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("independent-results.json"),
    )
    args = parser.parse_args()

    context = build_context()
    witness, witness_hash = load_witness()
    validation = validate_witness_data(witness, context)
    result = exact_results(context, validation, witness_hash)
    write_json(args.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
