"""Clean-room verifier for the Wave 43 unrooted seven-deck witness.

This module imports no discovery code.  It constructs the complete unlabeled
graph catalogues on six and seven vertices from the labelled universes,
recomputes local admissibility and the deletion deck, evaluates the published
count formulas with Fraction arithmetic, and checks only the public sparse
witness in the frozen discovery JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DISCOVERY_RESULT = ROOT / "attempts" / "wave43-seven-deck-endpoint" / "exact-results.json"
DISCOVERY_RESULT_SHA256 = "06b498a736a511a7d6f5912bd4686e5d4eb30f4041477e3ee9cbc1704f1757c8"

N = 99
K = 14
N3 = 4158
H11 = 16632
MIN_FREE_MEMORY_PERCENT = 15.0

# Published correspondence N_1,...,N_62 -> canonical six-vertex graph masks.
# It is treated as formula metadata, not as a discovery implementation result.
SOURCE_N_MASKS = (
    7100, 1883, 5941, 1916, 5907, 1749, 926, 1881, 1884, 956, 922, 1880,
    920, 5905, 671, 761, 701, 762, 63, 123, 691, 663, 694, 633, 760, 126,
    693, 246, 700, 31, 61, 121, 659, 122, 692, 0, 1, 3, 36, 7, 44, 37,
    35, 15, 102, 45, 39, 106, 616, 110, 107, 47, 684, 655, 685, 617, 656,
    657, 60, 662, 120, 632,
)

# Published representatives: fixed 7-cycle plus the listed extra chords.
SOURCE_H_CHORDS = (
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


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def sha256_json(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def physical_memory() -> tuple[int, int]:
    """Return total and available physical bytes without third-party modules."""
    if sys.platform == "win32":
        import ctypes

        class MemoryStatusEx(ctypes.Structure):
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

        status = MemoryStatusEx()
        status.dwLength = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise OSError("GlobalMemoryStatusEx failed")
        return int(status.ullTotalPhys), int(status.ullAvailPhys)

    page_size = os.sysconf("SC_PAGE_SIZE")
    total = os.sysconf("SC_PHYS_PAGES") * page_size
    available = os.sysconf("SC_AVPHYS_PAGES") * page_size
    return int(total), int(available)


def memory_sample(label: str) -> dict[str, object]:
    total, available = physical_memory()
    free_percent = 100.0 * available / total
    if free_percent < MIN_FREE_MEMORY_PERCENT:
        raise MemoryError(
            f"{label}: physical memory free {free_percent:.2f}% is below "
            f"{MIN_FREE_MEMORY_PERCENT:.2f}%"
        )
    return {
        "label": label,
        "total_bytes": total,
        "available_bytes": available,
        "free_percent_floor": int(free_percent * 100) / 100,
    }


def edges(order: int) -> tuple[tuple[int, int], ...]:
    return tuple((left, right) for left in range(order) for right in range(left + 1, order))


def edge_positions(order: int) -> dict[tuple[int, int], int]:
    return {edge: index for index, edge in enumerate(edges(order))}


def permutation_bit_maps(order: int) -> tuple[tuple[int, ...], ...]:
    original_edges = edges(order)
    positions = edge_positions(order)
    result = []
    for permutation in itertools.permutations(range(order)):
        result.append(
            tuple(
                positions[tuple(sorted((permutation[left], permutation[right])))]
                for left, right in original_edges
            )
        )
    return tuple(result)


def transform_mask(mask: int, bit_map: Sequence[int]) -> int:
    transformed = 0
    current = mask
    while current:
        low = current & -current
        source_bit = low.bit_length() - 1
        transformed |= 1 << bit_map[source_bit]
        current ^= low
    return transformed


@dataclass(frozen=True)
class Catalogue:
    order: int
    classes: tuple[int, ...]
    canonical_by_labelled_mask: tuple[int, ...]
    orbit_sizes: tuple[int, ...]
    memory_samples: tuple[dict[str, object], ...]


def build_complete_catalogue(order: int) -> Catalogue:
    """Partition the full labelled graph universe into permutation orbits."""
    number_of_edges = math.comb(order, 2)
    universe_size = 1 << number_of_edges
    samples = [memory_sample(f"order-{order}-catalogue-start")]
    maps = permutation_bit_maps(order)
    remaining = set(range(universe_size))
    canonical_by_labelled = [-1] * universe_size
    class_to_orbit_size: dict[int, int] = {}
    orbit_counter = 0

    while remaining:
        representative = next(iter(remaining))
        orbit = {transform_mask(representative, bit_map) for bit_map in maps}
        canonical = min(orbit)
        if canonical in class_to_orbit_size:
            raise AssertionError("orbit partition repeated a canonical class")
        class_to_orbit_size[canonical] = len(orbit)
        for labelled in orbit:
            if canonical_by_labelled[labelled] != -1:
                raise AssertionError("labelled graph appeared in two orbits")
            canonical_by_labelled[labelled] = canonical
        remaining.difference_update(orbit)
        orbit_counter += 1
        if orbit_counter % 128 == 0:
            samples.append(memory_sample(f"order-{order}-catalogue-orbit-{orbit_counter}"))

    classes = tuple(sorted(class_to_orbit_size))
    orbit_sizes = tuple(class_to_orbit_size[mask] for mask in classes)
    if any(mask < 0 for mask in canonical_by_labelled):
        raise AssertionError("catalogue left a labelled graph unassigned")
    if sum(orbit_sizes) != universe_size:
        raise AssertionError("orbit-size sum does not cover the labelled universe")
    expected_classes = {3: 4, 6: 156, 7: 1044}.get(order)
    if expected_classes is not None and len(classes) != expected_classes:
        raise AssertionError(
            f"order {order} catalogue has {len(classes)}, expected {expected_classes}"
        )
    samples.append(memory_sample(f"order-{order}-catalogue-finish"))
    return Catalogue(
        order=order,
        classes=classes,
        canonical_by_labelled_mask=tuple(canonical_by_labelled),
        orbit_sizes=orbit_sizes,
        memory_samples=tuple(samples),
    )


def adjacency_rows(mask: int, order: int) -> tuple[int, ...]:
    rows = [0] * order
    for index, (left, right) in enumerate(edges(order)):
        if mask >> index & 1:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return tuple(rows)


def locally_admissible(mask: int, order: int) -> bool:
    rows = adjacency_rows(mask, order)
    for left in range(order):
        for right in range(left + 1, order):
            common = (rows[left] & rows[right]).bit_count()
            adjacent = bool(rows[left] >> right & 1)
            if adjacent and common > 1:
                return False
            if not adjacent and common > 2:
                return False
    return True


def locally_admissible_classes(catalogue: Catalogue) -> tuple[int, ...]:
    return tuple(mask for mask in catalogue.classes if locally_admissible(mask, catalogue.order))


def mask_from_edges(order: int, edge_list: Iterable[tuple[int, int]]) -> int:
    positions = edge_positions(order)
    mask = 0
    for edge in edge_list:
        normalized = tuple(sorted(edge))
        if normalized not in positions:
            raise ValueError(f"invalid edge {edge!r} for order {order}")
        mask |= 1 << positions[normalized]
    return mask


def delete_vertex(mask: int, order: int, deleted: int) -> int:
    positions = edge_positions(order - 1)
    remaining = [vertex for vertex in range(order) if vertex != deleted]
    relabel = {vertex: index for index, vertex in enumerate(remaining)}
    result = 0
    for edge_index, (left, right) in enumerate(edges(order)):
        if left == deleted or right == deleted or not (mask >> edge_index & 1):
            continue
        mapped = tuple(sorted((relabel[left], relabel[right])))
        result |= 1 << positions[mapped]
    return result


def build_deletion_matrix(
    classes7: Sequence[int],
    catalogue6: Catalogue,
) -> tuple[tuple[int, ...], ...]:
    source_row = {mask: index for index, mask in enumerate(SOURCE_N_MASKS)}
    rows = [[0] * len(classes7) for _ in SOURCE_N_MASKS]
    for column, mask in enumerate(classes7):
        for deleted in range(7):
            labelled_card = delete_vertex(mask, 7, deleted)
            canonical_card = catalogue6.canonical_by_labelled_mask[labelled_card]
            try:
                row = source_row[canonical_card]
            except KeyError as exc:
                raise AssertionError(
                    f"seven-class {mask} has inadmissible six-card {canonical_card}"
                ) from exc
            rows[row][column] += 1
    matrix = tuple(tuple(row) for row in rows)
    if any(sum(matrix[row][column] for row in range(62)) != 7 for column in range(len(classes7))):
        raise AssertionError("a deletion column does not sum to seven")
    return matrix


@dataclass(frozen=True)
class Affine:
    constant: Fraction
    n3_coefficient: Fraction = Fraction(0)
    h11_coefficient: Fraction = Fraction(0)

    def evaluate(self, n3: int, h11: int = 0) -> Fraction:
        return self.constant + self.n3_coefficient * n3 + self.h11_coefficient * h11


def A(
    constant: int | Fraction,
    n3_coefficient: int | Fraction = 0,
    h11_coefficient: int | Fraction = 0,
) -> Affine:
    return Affine(Fraction(constant), Fraction(n3_coefficient), Fraction(h11_coefficient))


def Q(numerator: int, denominator: int) -> Fraction:
    return Fraction(numerator, denominator)


def six_formulae(n: int = N, k: int = K) -> tuple[Affine, ...]:
    """Published N_1,...,N_62 formulas, independently transcribed."""
    common = n * k * (k - 2)
    b = common * (k - 4)
    return (
        A(Q(common, 12), Q(-1, 3)),
        A(Q(common, 2)),
        A(0, 1),
        A(0, 2),
        A(Q(b, 8), -1),
        A(Q(common * (k - 3), 2), -2),
        A(Q(b, 4)),
        A(b, -2),
        A(Q(b, 4), -1),
        A(Q(b, 2), -2),
        A(Q(b * (k - 6), 2), 4),
        A(Q(common * (2 * k**2 - 21 * k + 53), 12), 1),
        A(Q(b * (k**2 - 12 * k + 42), 32), -1),
        A(Q(b * (k - 12), 144), Q(1, 3)),
        A(Q(b, 8)),
        A(Q(b, 2)),
        A(b),
        A(b, -4),
        A(Q(b * (k - 6), 12)),
        A(Q(b * (k - 4), 2)),
        A(Q(common * (k - 3) * (k - 4), 6), Q(2, 3)),
        A(Q(b * (k - 5), 2)),
        A(b * (k - 5), 4),
        A(Q(b * (k - 6), 4), 2),
        A(Q(b * (k - 7), 2), 4),
        A(Q(b * (k - 6), 4)),
        A(Q(b * (k - 5), 2), 2),
        A(Q(b * (k - 6), 4), 2),
        A(b * (k - 6), 6),
        A(Q(b * (k - 6) * (k - 8), 120)),
        A(Q(b * (k - 5) * (k - 6), 6)),
        A(Q(b * (k**2 - 10 * k + 26), 8), -1),
        A(Q(b * (k**2 - 10 * k + 28), 2), -6),
        A(Q(b * (k**2 - 11 * k + 34), 2), -8),
        A(Q(b * (k**2 - 11 * k + 36), 2), -10),
        A(
            Q(
                b
                * (
                    k**7
                    - 24 * k**6
                    + 248 * k**5
                    - 1520 * k**4
                    + 6436 * k**3
                    - 19520 * k**2
                    + 38896 * k
                    - 40704
                ),
                23040,
            ),
            Q(1, 3),
        ),
        A(
            Q(
                b
                * (
                    k**6
                    - 22 * k**5
                    + 212 * k**4
                    - 1208 * k**3
                    + 4484 * k**2
                    - 10456 * k
                    + 12288
                ),
                768,
            ),
            -3,
        ),
        A(
            Q(
                b
                * (
                    k**5
                    - 20 * k**4
                    + 172 * k**3
                    - 828 * k**2
                    + 2300 * k
                    - 3048
                ),
                96,
            ),
            6,
        ),
        A(
            Q(
                b
                * (
                    k**5
                    - 20 * k**4
                    + 176 * k**3
                    - 884 * k**2
                    + 2588 * k
                    - 3624
                ),
                128,
            ),
            6,
        ),
        A(Q(b * (k**4 - 18 * k**3 + 130 * k**2 - 460 * k + 696), 48), -2),
        A(Q(b * (k**4 - 18 * k**3 + 136 * k**2 - 524 * k + 892), 16), -14),
        A(Q(b * (k**4 - 17 * k**3 + 120 * k**2 - 430 * k + 684), 16), -10),
        A(
            Q(b * (k**4 - 18 * k**3 + 130 * k**2 - 460 * k + 720), 288),
            Q(-2, 3),
        ),
        A(Q(b * (k - 6) * (n - 5 * k + 13), 24)),
        A(Q(b * (k - 6) * (k**2 - 8 * k + 26), 64), 1),
        A(Q(b * (k**3 - 14 * k**2 + 72 * k - 140), 4), 8),
        A(Q(b * (k - 6) * (k**2 - 8 * k + 22), 16), 2),
        A(Q(b * (k**3 - 14 * k**2 + 75 * k - 160), 4), 14),
        A(Q(b * (k**3 - 16 * k**2 + 94 * k - 216), 48), 2),
        A(Q(b * (k**2 - 10 * k + 30), 4), -4),
        A(Q(b * (k**2 - 9 * k + 22), 4), -2),
        A(Q(b * (n - 5 * k + 12), 4)),
        A(Q(b * (n - 5 * k + 15), 5), -2),
        A(Q(b * (k - 6), 16)),
        A(Q(b * (k - 6), 4), 2),
        A(Q(b * (k**2 - 10 * k + 30), 4), -4),
        A(Q(b * (k**4 - 18 * k**3 + 140 * k**2 - 564 * k + 996), 192), Q(-4, 3)),
        A(Q(b * (k**3 - 15 * k**2 + 86 * k - 190), 8), 8),
        A(Q(b * (k - 6) * (k**2 - 10 * k + 34), 24), 2),
        A(Q(b * (k**2 - 12 * k + 38), 8), -2),
        A(Q(b * (k**3 - 16 * k**2 + 96 * k - 220), 16), 5),
        A(Q(b * (k**2 - 14 * k + 54), 24), -2),
    )


def seven_formulae(n: int = N, k: int = K) -> tuple[Affine, ...]:
    """Published h_0,...,h_18 formulas, independently transcribed."""
    common = n * k * (k - 2)
    b = common * (k - 4)
    return (
        A(Q(b * (2 * k**2 - 30 * k + 133), 14), -10, -1),
        A(Q(common * (2 * k**2 - 25 * k + 68), 2), 16, Q(3, 2)),
        A(b * (k - 8), 12, Q(5, 2)),
        A(b, -2, Q(-1, 2)),
        A(b, -4),
        A(Q(b, 2), 0, Q(-1, 2)),
        A(b, -8),
        A(Q(b, 2), 0, Q(-3, 2)),
        A(2 * b, -8, -2),
        A(b, -2, Q(-3, 2)),
        A(0, 2),
        A(0, 0, 1),
        A(Q(common, 4), -1, Q(1, 4)),
        A(0, 0, Q(1, 2)),
        A(0, 4),
        A(0, 2),
        A(0, -2, 1),
        A(Q(common, 4), -1),
        A(0, 1, Q(-1, 4)),
    )


def evaluate_integral(formulae: Sequence[Affine], n3: int, h11: int = 0) -> tuple[int, ...]:
    result = []
    for index, form in enumerate(formulae):
        value = form.evaluate(n3, h11)
        if value.denominator != 1:
            raise AssertionError(f"formula {index} is nonintegral: {value}")
        if value < 0:
            raise AssertionError(f"formula {index} is negative: {value}")
        result.append(value.numerator)
    return tuple(result)


def hamiltonian_masks(catalogue7: Catalogue) -> tuple[int, ...]:
    positions = edge_positions(7)
    cycle_edges = tuple((vertex, (vertex + 1) % 7) for vertex in range(7))
    cycle = mask_from_edges(7, cycle_edges)
    chord_positions = tuple(
        index for index in range(21) if not (cycle >> index & 1)
    )
    classes = set()
    for subset in range(1 << len(chord_positions)):
        mask = cycle
        for offset, position in enumerate(chord_positions):
            if subset >> offset & 1:
                mask |= 1 << position
        if locally_admissible(mask, 7):
            classes.add(catalogue7.canonical_by_labelled_mask[mask])
    return tuple(sorted(classes))


def source_hamiltonian_masks(catalogue7: Catalogue) -> tuple[int, ...]:
    cycle = tuple((vertex, (vertex + 1) % 7) for vertex in range(7))
    result = []
    for chords in SOURCE_H_CHORDS:
        labelled = mask_from_edges(7, cycle + chords)
        result.append(catalogue7.canonical_by_labelled_mask[labelled])
    if len(set(result)) != 19:
        raise AssertionError("published Hamiltonian representatives are not distinct")
    return tuple(result)


def load_sparse_witness(
    path: Path,
    classes7: Sequence[int],
) -> tuple[tuple[int, ...], int, list[dict[str, int]]]:
    if sha256_path(path) != DISCOVERY_RESULT_SHA256:
        raise AssertionError("frozen discovery-result hash changed")
    payload = json.loads(path.read_text(encoding="utf-8"))
    certificate = payload.get("certificate")
    if type(certificate) is not dict:
        raise AssertionError("public certificate is absent")
    support = certificate.get("support")
    h11 = certificate.get("h11")
    if type(support) is not list or type(h11) is not int:
        raise AssertionError("public certificate has malformed top-level fields")
    if h11 % 4:
        raise AssertionError("public h11 is not a multiple of four")

    index = {mask: position for position, mask in enumerate(classes7)}
    counts = [0] * len(classes7)
    normalized_support: list[dict[str, int]] = []
    seen: set[int] = set()
    for record in support:
        if type(record) is not dict or set(record) != {"canonical_mask", "count"}:
            raise AssertionError("malformed sparse support record")
        mask = record["canonical_mask"]
        count = record["count"]
        if type(mask) is not int or type(count) is not int or count <= 0:
            raise AssertionError("support mask/count is not a positive integer pair")
        if mask in seen or mask not in index:
            raise AssertionError("support mask is duplicate or outside the independent census")
        if classes7[index[mask]] != mask:
            raise AssertionError("support mask is not canonical")
        seen.add(mask)
        counts[index[mask]] = count
        normalized_support.append({"canonical_mask": mask, "count": count})
    if normalized_support != sorted(normalized_support, key=lambda item: item["canonical_mask"]):
        raise AssertionError("support is not in canonical-mask order")
    return tuple(counts), h11, normalized_support


@dataclass(frozen=True)
class Validation:
    total: int
    deck_left: tuple[int, ...]
    deck_right: tuple[int, ...]
    hamiltonian_masks: tuple[int, ...]
    hamiltonian_left: tuple[int, ...]
    hamiltonian_right: tuple[int, ...]
    prism_class_indices: tuple[int, ...]
    deletion_sparse_nonzeros: int


def validate_counts(
    counts: Sequence[int],
    classes7: Sequence[int],
    deletion_matrix: Sequence[Sequence[int]],
    six_counts: Sequence[int],
    h_masks: Sequence[int],
    h_values: Sequence[int],
) -> Validation:
    if len(counts) != len(classes7):
        raise AssertionError("count-vector length mismatch")
    if any(type(value) is not int or value < 0 for value in counts):
        raise AssertionError("count vector is not nonnegative integral")

    total = sum(counts)
    expected_total = math.comb(N, 7)
    if total != expected_total:
        raise AssertionError(f"seven-subset total mismatch: {total} != {expected_total}")

    deck_left = tuple(
        sum(coefficient * count for coefficient, count in zip(row, counts))
        for row in deletion_matrix
    )
    deck_right = tuple((N - 6) * value for value in six_counts)
    if deck_left != deck_right:
        bad = [index + 1 for index, pair in enumerate(zip(deck_left, deck_right)) if pair[0] != pair[1]]
        raise AssertionError(f"deletion equations fail in rows {bad}")

    class_index = {mask: position for position, mask in enumerate(classes7)}
    h_left = tuple(counts[class_index[mask]] for mask in h_masks)
    h_right = tuple(h_values)
    if h_left != h_right:
        bad = [index for index, pair in enumerate(zip(h_left, h_right)) if pair[0] != pair[1]]
        raise AssertionError(f"Hamiltonian equations fail at formula indices {bad}")

    prism_indices = tuple(
        column for column, coefficient in enumerate(deletion_matrix[0]) if coefficient
    )
    if any(counts[index] != 0 for index in prism_indices):
        raise AssertionError("a prism-containing seven-class has nonzero count")

    deletion_sparse_nonzeros = sum(
        1 for row in deletion_matrix for coefficient in row if coefficient
    )
    return Validation(
        total=total,
        deck_left=deck_left,
        deck_right=deck_right,
        hamiltonian_masks=tuple(h_masks),
        hamiltonian_left=h_left,
        hamiltonian_right=h_right,
        prism_class_indices=prism_indices,
        deletion_sparse_nonzeros=deletion_sparse_nonzeros,
    )


def expect_failure(label: str, operation) -> dict[str, str]:
    try:
        operation()
    except (AssertionError, ValueError, TypeError) as exc:
        return {"label": label, "outcome": "REJECTED", "reason": str(exc)}
    raise AssertionError(f"hostile control {label!r} was accepted")


def class_stream_sha256(classes: Sequence[int], width: int) -> str:
    return hashlib.sha256(
        b"".join(mask.to_bytes(width, "big") for mask in classes)
    ).hexdigest()


def build_result() -> dict[str, object]:
    samples = [memory_sample("verifier-start")]

    # Positive control: exhaustive order-three orbit partition.
    catalogue3 = build_complete_catalogue(3)
    if catalogue3.classes != (0, 1, 3, 7):
        raise AssertionError("small-census positive control failed")

    catalogue6 = build_complete_catalogue(6)
    classes6 = locally_admissible_classes(catalogue6)
    if len(classes6) != 62:
        raise AssertionError(f"locally admissible order-six census is {len(classes6)}, not 62")
    if len(SOURCE_N_MASKS) != 62 or len(set(SOURCE_N_MASKS)) != 62:
        raise AssertionError("published N-mask metadata is not a 62-element set")
    if set(SOURCE_N_MASKS) != set(classes6):
        raise AssertionError("published N masks do not cover the independent order-six census")

    samples.append(memory_sample("before-order-seven-catalogue"))
    catalogue7 = build_complete_catalogue(7)
    classes7 = locally_admissible_classes(catalogue7)
    if len(classes7) != 208:
        raise AssertionError(f"locally admissible order-seven census is {len(classes7)}, not 208")
    samples.append(memory_sample("after-order-seven-catalogue"))

    deletion_matrix = build_deletion_matrix(classes7, catalogue6)
    six_values = evaluate_integral(six_formulae(), N3)
    if sum(six_values) != math.comb(N, 6):
        raise AssertionError("six-vertex formula total is not C(99,6)")
    if six_values[0] != 0:
        raise AssertionError("endpoint prism count N_1 is not zero")

    independent_h_masks = hamiltonian_masks(catalogue7)
    if len(independent_h_masks) != 19:
        raise AssertionError(
            f"independent Hamiltonian census is {len(independent_h_masks)}, not 19"
        )
    h_masks = source_hamiltonian_masks(catalogue7)
    if set(h_masks) != set(independent_h_masks):
        raise AssertionError("published Hamiltonian representatives miss an independent class")
    h_values = evaluate_integral(seven_formulae(), N3, H11)

    counts, candidate_h11, support = load_sparse_witness(DISCOVERY_RESULT, classes7)
    if candidate_h11 != H11:
        raise AssertionError(f"candidate h11 is {candidate_h11}, expected {H11}")
    validation = validate_counts(
        counts,
        classes7,
        deletion_matrix,
        six_values,
        h_masks,
        h_values,
    )
    if len(support) != 99 or sum(value > 0 for value in counts) != 99:
        raise AssertionError("reconstructed support size is not 99")
    if len(validation.prism_class_indices) != 3:
        raise AssertionError("independent deck does not identify exactly three prism-containing classes")

    # Hostile local graphs: K4 violates lambda<=1 and K_{2,3} violates mu<=2.
    k4_mask = mask_from_edges(4, itertools.combinations(range(4), 2))
    k23_mask = mask_from_edges(
        5,
        ((left, right) for left in (0, 1) for right in (2, 3, 4)),
    )
    if locally_admissible(k4_mask, 4) or locally_admissible(k23_mask, 5):
        raise AssertionError("local-admissibility hostile graphs were accepted")

    positive_index = next(index for index, value in enumerate(counts) if value > 0)
    forbidden_index = validation.prism_class_indices[0]

    mutated_count = list(counts)
    mutated_count[positive_index] += 1
    count_control = expect_failure(
        "increment one support coefficient",
        lambda: validate_counts(
            mutated_count,
            classes7,
            deletion_matrix,
            six_values,
            h_masks,
            h_values,
        ),
    )

    mutated_matrix = [list(row) for row in deletion_matrix]
    mutated_matrix[0][positive_index] += 1
    matrix_control = expect_failure(
        "increment one deletion multiplicity",
        lambda: validate_counts(
            counts,
            classes7,
            mutated_matrix,
            six_values,
            h_masks,
            h_values,
        ),
    )

    mutated_h_values = list(h_values)
    mutated_h_values[0] += 1
    formula_control = expect_failure(
        "increment one Hamiltonian formula value",
        lambda: validate_counts(
            counts,
            classes7,
            deletion_matrix,
            six_values,
            h_masks,
            mutated_h_values,
        ),
    )

    mutated_prism = list(counts)
    mutated_prism[forbidden_index] = 1
    prism_control = expect_failure(
        "set one prism-containing class positive",
        lambda: (
            None
            if all(mutated_prism[index] == 0 for index in validation.prism_class_indices)
            else (_ for _ in ()).throw(AssertionError("prism-zero condition fails"))
        ),
    )

    hostile_controls = [
        count_control,
        matrix_control,
        formula_control,
        prism_control,
        {
            "label": "K4 adjacent-pair common-neighbor violation",
            "outcome": "REJECTED",
            "reason": "adjacent pair has two common neighbors",
        },
        {
            "label": "K2,3 nonadjacent-pair common-neighbor violation",
            "outcome": "REJECTED",
            "reason": "nonadjacent pair has three common neighbors",
        },
    ]

    admissible6_labelled = sum(
        orbit for mask, orbit in zip(catalogue6.classes, catalogue6.orbit_sizes)
        if locally_admissible(mask, 6)
    )
    admissible7_labelled = sum(
        orbit for mask, orbit in zip(catalogue7.classes, catalogue7.orbit_sizes)
        if locally_admissible(mask, 7)
    )

    samples.extend(catalogue3.memory_samples)
    samples.extend(catalogue6.memory_samples)
    samples.extend(catalogue7.memory_samples)
    samples.append(memory_sample("verifier-finish"))

    support_sha = sha256_json(support)
    result = {
        "format": "wave43-seven-deck-independent-verifier-v1",
        "claim_label": "VERIFIED",
        "scope": (
            "Exact feasibility of the specified unrooted order-seven deletion/count "
            "relaxation at n3=4158 and h11=16632."
        ),
        "parameters": {"n": N, "k": K, "lambda": 1, "mu": 2, "n3": N3, "h11": H11},
        "catalogues": {
            "order_3": {
                "unlabeled_classes": len(catalogue3.classes),
                "labelled_orbit_sum": sum(catalogue3.orbit_sizes),
            },
            "order_6": {
                "all_unlabeled_classes": len(catalogue6.classes),
                "all_labelled_orbit_sum": sum(catalogue6.orbit_sizes),
                "locally_admissible_unlabeled_classes": len(classes6),
                "locally_admissible_labelled_graphs": admissible6_labelled,
                "class_stream_sha256": class_stream_sha256(classes6, 2),
            },
            "order_7": {
                "all_unlabeled_classes": len(catalogue7.classes),
                "all_labelled_orbit_sum": sum(catalogue7.orbit_sizes),
                "locally_admissible_unlabeled_classes": len(classes7),
                "locally_admissible_labelled_graphs": admissible7_labelled,
                "class_stream_sha256": class_stream_sha256(classes7, 3),
            },
        },
        "model": {
            "seven_vertex_classes": len(classes7),
            "deletion_equations": len(deletion_matrix),
            "hamiltonian_equations": len(h_masks),
            "deletion_sparse_nonzeros": validation.deletion_sparse_nonzeros,
            "full_constraint_sparse_nonzeros": (
                validation.deletion_sparse_nonzeros
                + len(h_masks)
                + sum(form.h11_coefficient != 0 for form in seven_formulae())
            ),
            "deletion_matrix_sha256": sha256_json(deletion_matrix),
            "six_source_masks_sha256": sha256_json(SOURCE_N_MASKS),
            "six_counts": list(six_values),
            "six_counts_sha256": sha256_json(six_values),
            "hamiltonian_masks": list(h_masks),
            "hamiltonian_masks_sha256": sha256_json(h_masks),
            "hamiltonian_counts": list(h_values),
            "hamiltonian_counts_sha256": sha256_json(h_values),
        },
        "certificate": {
            "input_path": str(DISCOVERY_RESULT.relative_to(ROOT)).replace("\\", "/"),
            "input_sha256": DISCOVERY_RESULT_SHA256,
            "support_size": len(support),
            "zero_count_classes": len(classes7) - len(support),
            "support_sha256": support_sha,
            "support": support,
            "seven_subset_total": validation.total,
            "expected_seven_subset_total": math.comb(N, 7),
            "deck_left_sha256": sha256_json(validation.deck_left),
            "deck_right_sha256": sha256_json(validation.deck_right),
            "all_deck_residuals_zero": validation.deck_left == validation.deck_right,
            "hamiltonian_left_sha256": sha256_json(validation.hamiltonian_left),
            "hamiltonian_right_sha256": sha256_json(validation.hamiltonian_right),
            "all_hamiltonian_residuals_zero": validation.hamiltonian_left
            == validation.hamiltonian_right,
            "prism_containing_class_count": len(validation.prism_class_indices),
            "prism_containing_canonical_masks": [
                classes7[index] for index in validation.prism_class_indices
            ],
            "all_prism_containing_classes_zero": all(
                counts[index] == 0 for index in validation.prism_class_indices
            ),
        },
        "controls": {
            "positive": [
                {
                    "label": "complete order-three orbit census",
                    "outcome": "ACCEPTED",
                    "classes": list(catalogue3.classes),
                    "labelled_orbit_sum": sum(catalogue3.orbit_sizes),
                },
                {
                    "label": "published sparse witness",
                    "outcome": "ACCEPTED",
                },
            ],
            "hostile": hostile_controls,
        },
        "resource_guard": {
            "minimum_free_memory_percent": MIN_FREE_MEMORY_PERCENT,
            "samples": samples,
        },
        "conclusion": {
            "unrooted_order_seven_count_system": "FEASIBLE",
            "graph_construction": False,
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "conway_99": "UNKNOWN",
        },
        "limitations": [
            "The sparse count vector does not realize a 99-vertex graph.",
            "Overlapping seven-subset compatibility is not enforced.",
            "Rooted extension compatibility is not enforced.",
            "No automorphism of a putative graph is assumed.",
            "This result supplies no evidence that the endpoint or Conway-99 graph exists.",
        ],
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "independent-result.json",
    )
    args = parser.parse_args()
    result = build_result()
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "claim_label": result["claim_label"],
                "output": str(args.output),
                "support_size": result["certificate"]["support_size"],
                "order_7_classes": result["model"]["seven_vertex_classes"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
