#!/usr/bin/env python3
"""Clean-room exact verifier for the Wave152 four-root feedback artifacts.

This file uses only the Python standard library.  It never imports or executes
discovery code.  It reconstructs the four stored covariance cuts from graph
and flag semantics, replays their discovery-input values, and checks the two
replacement witnesses against every retained exact equality.

The result concerns only a finite rational relaxation at n3=4158.  It is not a
graph construction, a proof of endpoint feasibility, or a Conway-99 result.
"""

from __future__ import annotations

import argparse
import ctypes
import gzip
import hashlib
import itertools
import json
import math
import time
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Iterator, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ATTEMPT = ROOT / "attempts" / "wave152-four-root-order8"
N = 99
Y = 4158
C7 = math.comb(N, 7)
C8 = math.comb(N, 8)
MODULUS = 1_000_003
MIN_FREE_PERCENT = 15.0

PRIMARY_HASHES = {
    "attempts/wave152-four-root-order8/build_exact_cuts.py":
        "ffc57ca81560e90ac3f0f3cf27f84b5ed9af0e8fffb0c6e32079dfcc9bb73b70",
    "attempts/wave152-four-root-order8/exact-cuts.json":
        "055b8253636167b85f68e09b1a470d4fe94e2d8bcfbe5eb02ade0e69ad73603d",
    "attempts/wave152-four-root-order8/iteration2-cuts.json":
        "3652888b035ba2675cb860dcf59414f0b9e7e353e7f943ecfd1e37646718aa25",
    "attempts/wave152-four-root-order8/zero-face-two-cuts-highs.json":
        "11a06307d898b10f0472a0908c5c775b00260672d9054f67c9adb7b30b6da005",
    "attempts/wave152-four-root-order8/zero-face-four-cuts-highs.json":
        "22dc59c5d78660131bd755855029deab757e236ffc633fa75a4751b30bc86372",
    "attempts/wave152-four-root-order8/exact-witness-after-two-cuts.json":
        "b36c592546f5e5b3f9159a82267a3cb7cefaf37e6ee7588b4e2ba0a5c65d07af",
    "attempts/wave152-four-root-order8/exact-witness-after-four-cuts.json":
        "13fcdecd15da2a0c23abb71950fcda58e7f5e91b8caadc99d1e6e352aebeaeb9",
}

SUPPORT_HASHES = {
    "attempts/wave150-order8-sdp-scout/exact-rank1-witness.json":
        "e63afbe9ca36b4b1571b3dde75309d0cce45f3bc862d6e8c08bfe62f78dc130d",
    "attempts/wave44-rooted-flags/row-system.json":
        "fb81601a9c97fc6860702403e56da65c2ba8fd69ee6a61007a0da53cade1d722",
    "attempts/wave148-marked-order8/marked-rows.json.gz":
        "e7a39699584fe60ff251119063d66d8eed2a14a69d671c183533806cddc92aa1",
    "attempts/wave147-alternative-lane/coefficients.json.gz":
        "a46d8a8b6fd3ae339cdf7c9b633a661d917e3481bed762ae6aa70f1b4886cf1e",
    "attempts/wave147-alternative-lane/exact-results.json":
        "8baea3d7fdf69ff6653ff859d30ea975dcbef44330445ace73ae051c7db1373c",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_json(relative: str) -> dict:
    with (ROOT / relative).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_gzip_json(relative: str) -> dict:
    with gzip.open(ROOT / relative, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def fraction(value: str | int) -> Fraction:
    return Fraction(str(value))


def fraction_string(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def memory_sample(label: str) -> dict[str, float | str]:
    class MemoryStatusEx(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("memory_load", ctypes.c_ulong),
            ("total_phys", ctypes.c_ulonglong),
            ("avail_phys", ctypes.c_ulonglong),
            ("total_page", ctypes.c_ulonglong),
            ("avail_page", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("avail_virtual", ctypes.c_ulonglong),
            ("avail_extended_virtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatusEx()
    status.length = ctypes.sizeof(status)
    require(
        bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))),
        "GlobalMemoryStatusEx failed",
    )
    free_percent = 100.0 * status.avail_phys / status.total_phys
    require(
        free_percent >= MIN_FREE_PERCENT,
        f"free physical memory {free_percent:.2f}% is below the 15% floor",
    )
    return {
        "label": label,
        "free_physical_memory_percent": free_percent,
        "available_physical_gib": status.avail_phys / 2**30,
        "total_physical_gib": status.total_phys / 2**30,
    }


@lru_cache(maxsize=None)
def edges(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, right)
        for left in range(order)
        for right in range(left + 1, order)
    )


@lru_cache(maxsize=None)
def edge_positions(order: int) -> dict[tuple[int, int], int]:
    return {edge: index for index, edge in enumerate(edges(order))}


def adjacency_rows(mask: int, order: int) -> tuple[int, ...]:
    rows = [0] * order
    for position, (left, right) in enumerate(edges(order)):
        if mask >> position & 1:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return tuple(rows)


def locally_admissible(mask: int, order: int) -> bool:
    """Necessary induced-subgraph conditions for lambda=1 and mu=2."""
    rows = adjacency_rows(mask, order)
    for left in range(order):
        if rows[left].bit_count() > 14:
            return False
        for right in range(left + 1, order):
            common = (rows[left] & rows[right]).bit_count()
            if rows[left] >> right & 1:
                if common > 1:
                    return False
            elif common > 2:
                return False
    return True


def transform_mask(
    mask: int, order: int, permutation: Sequence[int]
) -> int:
    positions = edge_positions(order)
    result = 0
    for position, (left, right) in enumerate(edges(order)):
        if mask >> position & 1:
            image = tuple(sorted((permutation[left], permutation[right])))
            result |= 1 << positions[image]
    return result


@lru_cache(maxsize=None)
def canonical_unrooted(mask: int, order: int) -> int:
    """Complete canonicalization, enumerating only equal-degree cells."""
    rows = adjacency_rows(mask, order)
    degree_groups: dict[int, list[int]] = {}
    for vertex, row in enumerate(rows):
        degree_groups.setdefault(row.bit_count(), []).append(vertex)
    cells: list[tuple[dict[int, int], ...]] = []
    target_start = 0
    for degree in sorted(degree_groups):
        vertices = degree_groups[degree]
        targets = tuple(range(target_start, target_start + len(vertices)))
        target_start += len(vertices)
        cells.append(
            tuple(
                dict(zip(vertices, image, strict=True))
                for image in itertools.permutations(targets)
            )
        )
    best: int | None = None
    for choices in itertools.product(*cells):
        permutation = [0] * order
        for mapping in choices:
            for source, target in mapping.items():
                permutation[source] = target
        image = transform_mask(mask, order, permutation)
        best = image if best is None else min(best, image)
    require(best is not None, "canonicalization produced no image")
    return best


def induced_mask(
    graph_mask: int, graph_order: int, chosen_vertices: Sequence[int]
) -> int:
    positions = edge_positions(graph_order)
    result = 0
    target_position = 0
    for left_index, left in enumerate(chosen_vertices):
        for right in chosen_vertices[left_index + 1 :]:
            edge = tuple(sorted((left, right)))
            if graph_mask >> positions[edge] & 1:
                result |= 1 << target_position
            target_position += 1
    return result


def delete_vertex_mask(mask: int, order: int, deleted: int) -> int:
    chosen = tuple(vertex for vertex in range(order) if vertex != deleted)
    return induced_mask(mask, order, chosen)


def embed_root_mask(root_mask: int) -> int:
    source = edge_positions(4)
    target = edge_positions(6)
    result = 0
    for edge, position in source.items():
        if root_mask >> position & 1:
            result |= 1 << target[edge]
    return result


def canonical_four_root_flag(mask: int) -> int:
    """Fix roots 0..3 pointwise and quotient only the free-vertex swap."""
    swapped = transform_mask(mask, 6, (0, 1, 2, 3, 5, 4))
    return min(mask, swapped)


def flag_universe(root_mask: int) -> tuple[int, ...]:
    base = embed_root_mask(root_mask)
    root_edges = set(edge_positions(4))
    extension_positions = [
        position
        for edge, position in edge_positions(6).items()
        if edge not in root_edges
    ]
    require(len(extension_positions) == 9, "four-root flag width changed")
    flags: set[int] = set()
    for extension in range(1 << 9):
        mask = base
        for bit, position in enumerate(extension_positions):
            if extension >> bit & 1:
                mask |= 1 << position
        if locally_admissible(mask, 6):
            flags.add(canonical_four_root_flag(mask))
    return tuple(sorted(flags))


@lru_cache(maxsize=None)
def covering_pair_indices(
    complement_size: int,
) -> tuple[tuple[int, int], ...]:
    pairs = tuple(itertools.combinations(range(complement_size), 2))
    return tuple(
        (left, right)
        for left, first in enumerate(pairs)
        for right, second in enumerate(pairs)
        if len(set(first).union(second)) == complement_size
    )


def class_coefficients_for_directions(
    graph_mask: int,
    graph_order: int,
    root_mask: int,
    directions: Sequence[Sequence[int]],
    flag_index: dict[int, int],
) -> tuple[list[int], list[int]]:
    first = [0] * len(directions)
    quadratic = [0] * len(directions)
    vertices = tuple(range(graph_order))
    pair_indices = covering_pair_indices(graph_order - 4)
    for roots in itertools.permutations(vertices, 4):
        if induced_mask(graph_mask, graph_order, roots) != root_mask:
            continue
        complement = tuple(v for v in vertices if v not in roots)
        free_pairs = tuple(itertools.combinations(complement, 2))
        flag_indices = [
            flag_index[
                canonical_four_root_flag(
                    induced_mask(graph_mask, graph_order, roots + free_pair)
                )
            ]
            for free_pair in free_pairs
        ]
        for direction_index, direction in enumerate(directions):
            values = [direction[index] for index in flag_indices]
            if graph_order == 6:
                require(len(values) == 1, "order-six free complement changed")
                first[direction_index] += values[0]
            quadratic[direction_index] += sum(
                values[left] * values[right] for left, right in pair_indices
            )
    return first, quadratic


def class_sets(
    coefficients: dict, row_system: dict, exact_results: dict
) -> dict[int, tuple[int, ...]]:
    family_sets: dict[str, dict[int, tuple[int, ...]]] = {}
    for family_name in ("ordered_edge", "ordered_nonedge"):
        by_order: dict[int, list[int]] = {5: [], 6: [], 7: [], 8: []}
        for record in coefficients["families"][family_name]["class_coefficients"]:
            by_order[int(record["order"])].append(int(record["canonical_mask"]))
        family_sets[family_name] = {
            order: tuple(values) for order, values in by_order.items()
        }
        require(
            {order: len(values) for order, values in by_order.items()}
            == {5: 21, 6: 62, 7: 208, 8: 916},
            f"{family_name} class stream counts changed",
        )
    for order in (5, 6, 7, 8):
        require(
            family_sets["ordered_edge"][order]
            == family_sets["ordered_nonedge"][order],
            f"pair-root family class streams disagree at order {order}",
        )
    classes = dict(family_sets["ordered_edge"])
    require(tuple(map(int, row_system["classes"])) == classes[7], "order-seven stream mismatch")
    require(
        tuple(map(int, exact_results["class_streams"]["8"]["canonical_masks"]))
        == classes[8],
        "order-eight stream mismatch",
    )
    for order, expected in ((5, 21), (6, 62), (7, 208), (8, 916)):
        translation = {canonical_unrooted(mask, order): mask for mask in classes[order]}
        require(len(translation) == expected, f"canonical collision at order {order}")
        require(
            all(locally_admissible(mask, order) for mask in classes[order]),
            f"nonadmissible class in order-{order} stream",
        )
    return classes


def support_map(
    witness: dict, key: str, classes: Sequence[int]
) -> dict[int, Fraction]:
    result = {int(mask): Fraction(0) for mask in classes}
    for record in witness[key]:
        mask = int(record["canonical_mask"])
        require(mask in result, f"{key} mask {mask} outside class stream")
        require(result[mask] == 0, f"duplicate {key} mask {mask}")
        result[mask] = fraction(record["count"])
    return result


def derive_lower_counts(
    x7: dict[int, Fraction], classes: dict[int, tuple[int, ...]]
) -> dict[int, dict[int, Fraction]]:
    counts: dict[int, dict[int, Fraction]] = {7: dict(x7)}
    for lower_order in (6, 5):
        upper_order = lower_order + 1
        translation = {
            canonical_unrooted(mask, lower_order): mask
            for mask in classes[lower_order]
        }
        accum = {mask: Fraction(0) for mask in classes[lower_order]}
        for upper_mask, upper_count in counts[upper_order].items():
            if not upper_count:
                continue
            multiplicities: Counter[int] = Counter()
            for deleted in range(upper_order):
                canonical = canonical_unrooted(
                    delete_vertex_mask(upper_mask, upper_order, deleted),
                    lower_order,
                )
                require(canonical in translation, "deletion left frozen stream")
                multiplicities[translation[canonical]] += 1
            for lower_mask, multiplicity in multiplicities.items():
                accum[lower_mask] += multiplicity * upper_count
        divisor = N - lower_order
        counts[lower_order] = {
            mask: value / divisor for mask, value in accum.items()
        }
        require(
            all(value.denominator == 1 for value in counts[lower_order].values()),
            f"nonintegral derived order-{lower_order} counts",
        )
        require(
            sum(counts[lower_order].values()) == math.comb(N, lower_order),
            f"order-{lower_order} total failed",
        )
    return counts


def derive_order_four(
    x5: dict[int, Fraction], classes5: Sequence[int]
) -> dict[int, Fraction]:
    canonical4 = sorted(
        {
            canonical_unrooted(delete_vertex_mask(mask, 5, deleted), 4)
            for mask in classes5
            for deleted in range(5)
        }
    )
    # There are 11 unlabeled simple graphs on four vertices.  K4 and the
    # diamond both violate the adjacent-pair common-neighbor cap, leaving 9.
    require(len(canonical4) == 9, "unexpected admissible order-four class count")
    accum = {mask: Fraction(0) for mask in canonical4}
    for mask5, count in x5.items():
        for deleted in range(5):
            mask4 = canonical_unrooted(delete_vertex_mask(mask5, 5, deleted), 4)
            accum[mask4] += count
    counts4 = {mask: value / (N - 4) for mask, value in accum.items()}
    require(all(value.denominator == 1 for value in counts4.values()), "nonintegral x4")
    require(sum(counts4.values()) == math.comb(N, 4), "order-four total failed")
    return counts4


def root_embedding_count(x4: dict[int, Fraction], root_mask: int) -> int:
    total = 0
    for class_mask, count in x4.items():
        embeddings = sum(
            induced_mask(class_mask, 4, permutation) == root_mask
            for permutation in itertools.permutations(range(4))
        )
        total += int(count) * embeddings
    return total


def cut_dense_maps(
    cut: dict, classes: dict[int, tuple[int, ...]]
) -> tuple[int, dict[int, int], dict[int, int]]:
    a7 = {mask: 0 for mask in classes[7]}
    a8 = {mask: 0 for mask in classes[8]}
    for record in cut["order7_coefficients"]:
        mask = int(record["canonical_mask"])
        require(mask in a7 and a7[mask] == 0, "bad or duplicate order-seven cut term")
        a7[mask] = int(record["coefficient"])
    for record in cut["order8_coefficients"]:
        mask = int(record["canonical_mask"])
        require(mask in a8 and a8[mask] == 0, "bad or duplicate order-eight cut term")
        a8[mask] = int(record["coefficient"])
    return int(cut["constant"]), a7, a8


def evaluate_cut(
    cut: dict,
    x7: dict[int, Fraction],
    x8: dict[int, Fraction],
    classes: dict[int, tuple[int, ...]],
) -> Fraction:
    constant, a7, a8 = cut_dense_maps(cut, classes)
    return (
        Fraction(constant)
        + sum(a7[mask] * x7[mask] for mask in classes[7])
        + sum(a8[mask] * x8[mask] for mask in classes[8])
    )


def reconstruct_cuts(
    cut_payloads: Sequence[dict],
    classes: dict[int, tuple[int, ...]],
    lower: dict[int, dict[int, Fraction]],
    discovery_inputs: Sequence[dict],
    memory_samples: list[dict[str, float | str]],
) -> list[dict]:
    cuts = [cut for payload in cut_payloads for cut in payload["cuts"]]
    require(len(cuts) == 4, "expected exactly four feedback cuts")
    reconstructed: dict[str, dict] = {}
    root_counts: dict[int, int] = {}
    x4 = derive_order_four(lower[5], classes[5])
    for root_mask in sorted({int(cut["root_mask"]) for cut in cuts}):
        root_cuts = [cut for cut in cuts if int(cut["root_mask"]) == root_mask]
        require(len(root_cuts) == 2, f"expected two cuts for root {root_mask}")
        flags = flag_universe(root_mask)
        directions = [list(map(int, cut["direction"])) for cut in root_cuts]
        require(
            all(len(direction) == len(flags) for direction in directions),
            f"flag count/direction width mismatch for root {root_mask}",
        )
        require(
            all(int(cut["flag_count"]) == len(flags) for cut in root_cuts),
            f"stored flag count mismatch for root {root_mask}",
        )
        flag_index = {mask: index for index, mask in enumerate(flags)}
        first_by_cut: list[dict[int, int]] = [{}, {}]
        quadratic_by_cut: list[dict[int, dict[int, int]]] = [
            {6: {}, 7: {}, 8: {}},
            {6: {}, 7: {}, 8: {}},
        ]
        for order in (6, 7, 8):
            for class_index, class_mask in enumerate(classes[order]):
                first, quadratic = class_coefficients_for_directions(
                    class_mask,
                    order,
                    root_mask,
                    directions,
                    flag_index,
                )
                for cut_index in range(2):
                    if order == 6 and first[cut_index]:
                        first_by_cut[cut_index][class_mask] = first[cut_index]
                    if quadratic[cut_index]:
                        quadratic_by_cut[cut_index][order][class_mask] = quadratic[
                            cut_index
                        ]
                if order == 8 and class_index % 128 == 0:
                    memory_samples.append(
                        memory_sample(f"root_{root_mask}_order8_class_{class_index}")
                    )
        independently_counted_roots = root_embedding_count(x4, root_mask)
        root_counts[root_mask] = independently_counted_roots
        for cut_index, stored in enumerate(root_cuts):
            root_count = int(stored["root_embedding_count"])
            require(
                root_count == independently_counted_roots,
                f"root embedding count mismatch for root {root_mask}",
            )
            projected_first = sum(
                int(lower[6][mask]) * coefficient
                for mask, coefficient in first_by_cut[cut_index].items()
            )
            raw_constant = (
                root_count
                * sum(
                    int(lower[6][mask]) * coefficient
                    for mask, coefficient in quadratic_by_cut[cut_index][6].items()
                )
                - projected_first * projected_first
            )
            dense7 = [
                root_count * quadratic_by_cut[cut_index][7].get(mask, 0)
                for mask in classes[7]
            ]
            dense8 = [
                root_count * quadratic_by_cut[cut_index][8].get(mask, 0)
                for mask in classes[8]
            ]
            divisor = math.gcd(
                abs(raw_constant), *map(abs, dense7), *map(abs, dense8)
            )
            require(divisor > 0, "zero covariance cut")
            core = {
                "root_mask": root_mask,
                "root_embedding_count": root_count,
                "flag_count": len(flags),
                "direction": directions[cut_index],
                "sense": "constant + sum(a7_H*x7_H) + sum(a8_H*x8_H) >= 0",
                "constant": str(raw_constant // divisor),
                "order7_coefficients": [
                    {"canonical_mask": mask, "coefficient": str(value // divisor)}
                    for mask, value in zip(classes[7], dense7, strict=True)
                    if value
                ],
                "order8_coefficients": [
                    {"canonical_mask": mask, "coefficient": str(value // divisor)}
                    for mask, value in zip(classes[8], dense8, strict=True)
                    if value
                ],
                "primitive_divisor": str(divisor),
                "wave150_witness_value": stored["wave150_witness_value"],
                "wave150_witness_unscaled_value": stored[
                    "wave150_witness_unscaled_value"
                ],
                "projected_first_moment": str(projected_first),
                "order6_quadratic_nonzeros": len(
                    quadratic_by_cut[cut_index][6]
                ),
            }
            if "stored_four_times_value" in stored:
                core["stored_four_times_value"] = stored["stored_four_times_value"]
            else:
                core["stored_scaled_value"] = stored["stored_scaled_value"]
                core["stored_count_scale"] = int(stored["stored_count_scale"])
            require(core == {k: v for k, v in stored.items() if k != "cut_sha256"},
                    f"reconstructed coefficient payload differs for {stored['cut_sha256']}")
            rebuilt_hash = canonical_sha256(core)
            require(rebuilt_hash == stored["cut_sha256"], "cut hash mismatch")
            reconstructed[rebuilt_hash] = {
                "root_mask": root_mask,
                "flag_count": len(flags),
                "direction_nonzeros": sum(v != 0 for v in directions[cut_index]),
                "root_embedding_count": root_count,
                "projected_first_moment": projected_first,
                "primitive_divisor": divisor,
                "order6_quadratic_nonzeros": len(
                    quadratic_by_cut[cut_index][6]
                ),
                "order7_nonzeros": len(core["order7_coefficients"]),
                "order8_nonzeros": len(core["order8_coefficients"]),
                "cut_sha256": rebuilt_hash,
                "covariance_validity": (
                    "VERIFIED: raw form is R times a sum of v_i*v_j products "
                    "minus the square of the fixed first moment"
                ),
            }
    # Replay each cut on the witness from which its direction was obtained.
    for payload, witness in zip(cut_payloads, discovery_inputs, strict=True):
        x7 = support_map(witness, "x7_support", classes[7])
        x8 = support_map(witness, "x8_support", classes[8])
        for stored in payload["cuts"]:
            value = evaluate_cut(stored, x7, x8, classes)
            require(
                fraction(stored["wave150_witness_value"]) == value,
                "stored primitive discovery-witness value differs",
            )
            raw = value * int(stored["primitive_divisor"])
            require(
                fraction(stored["wave150_witness_unscaled_value"]) == raw,
                "stored raw discovery-witness value differs",
            )
            if "stored_four_times_value" in stored:
                require(
                    raw * 4 == int(stored["stored_four_times_value"]),
                    "stored four-times value differs",
                )
            else:
                require(
                    raw * int(stored["stored_count_scale"])
                    == int(stored["stored_scaled_value"]),
                    "stored scaled value differs",
                )
            require(value < 0, "discovery input is not separated by its cut")
            reconstructed[stored["cut_sha256"]]["discovery_input_value"] = (
                fraction_string(value)
            )
            reconstructed[stored["cut_sha256"]]["discovery_input_raw_value"] = (
                fraction_string(raw)
            )
    return [reconstructed[cut["cut_sha256"]] for cut in cuts]


@dataclass(frozen=True)
class ExactRow:
    label: str
    coefficients: dict[int, int]
    rhs: int


class ModularRank:
    def __init__(self, variables: int) -> None:
        self.variables = variables
        self.pivots: dict[int, dict[int, int]] = {}
        self.selected: list[int] = []
        self.rows_scanned: int | None = None

    def consume(self, row_index: int, coefficients: dict[int, int]) -> None:
        if len(self.selected) == self.variables:
            return
        vector = {
            column: value % MODULUS
            for column, value in coefficients.items()
            if value % MODULUS
        }
        while vector:
            pivot = min(vector)
            if pivot not in self.pivots:
                inverse = pow(vector[pivot], -1, MODULUS)
                vector = {
                    column: (value * inverse) % MODULUS
                    for column, value in vector.items()
                    if (value * inverse) % MODULUS
                }
                self.pivots[pivot] = vector
                self.selected.append(row_index)
                if len(self.selected) == self.variables:
                    self.rows_scanned = row_index + 1
                return
            factor = vector[pivot]
            for column, value in self.pivots[pivot].items():
                updated = (vector.get(column, 0) - factor * value) % MODULUS
                if updated:
                    vector[column] = updated
                else:
                    vector.pop(column, None)

    def record(self, restricted_rows: int) -> dict:
        return {
            "modulus": MODULUS,
            "rank": len(self.selected),
            "variables": self.variables,
            "full_column_rank": len(self.selected) == self.variables,
            "rows_scanned": (
                self.rows_scanned
                if self.rows_scanned is not None
                else restricted_rows
            ),
        }


def dense_cut_row(
    cut: dict,
    x7: dict[int, Fraction],
    classes: dict[int, tuple[int, ...]],
    class8_index: dict[int, int],
) -> ExactRow:
    constant, a7, a8 = cut_dense_maps(cut, classes)
    fixed = Fraction(constant) + sum(
        a7[mask] * x7[mask] for mask in classes[7]
    )
    require(fixed.denominator == 1, "active cut has nonintegral fixed part")
    return ExactRow(
        label=f"active_cut:{cut['cut_sha256']}",
        coefficients={
            class8_index[mask]: value for mask, value in a8.items() if value
        },
        rhs=-int(fixed),
    )


def base_rows(
    coefficients: dict,
    marked: dict,
    lower: dict[int, dict[int, Fraction]],
    x7: dict[int, Fraction],
    classes: dict[int, tuple[int, ...]],
) -> tuple[Iterator[ExactRow], dict]:
    class7_index = {mask: index for index, mask in enumerate(classes[7])}
    class8_index = {mask: index for index, mask in enumerate(classes[8])}
    require(all(v.denominator == 1 for v in x7.values()), "x7 is not integral")

    deletion_rows: list[ExactRow] = []
    for record in coefficients["order7_to_order8_deletion_equations"]:
        mask7 = int(record["order7_mask"])
        deletion_rows.append(
            ExactRow(
                f"D:{mask7}",
                {
                    class8_index[int(mask8)]: int(multiplicity)
                    for mask8, multiplicity in record[
                        "terms_order8_mask_multiplicity"
                    ]
                },
                int(record["left_multiplier"]) * int(x7[mask7]),
            )
        )

    marked_rows: list[ExactRow] = []
    marked_seen = 0
    for family_name in ("vertex_rows", "ordered_pair_rows"):
        for record in marked[family_name]:
            marked_seen += 1
            mask7 = int(record["order7_mask"])
            terms = {
                class8_index[int(mask8)]: int(value)
                for mask8, value in record["terms_order8_mask_coefficient"]
                if int(value)
            }
            rhs = int(record["lhs_coefficient"]) * int(x7[mask7])
            if terms:
                marked_rows.append(ExactRow(str(record["row_id"]), terms, rhs))
            else:
                require(rhs == 0, "trivial marked row is a contradiction")

    moment_rows: list[ExactRow] = []
    emitted_counts: dict[str, int] = {}
    for family_name, root_count in (
        ("ordered_edge", N * 14),
        ("ordered_nonedge", N * 84),
    ):
        family = coefficients["families"][family_name]
        size = int(family["matrix_size"])
        mean = [0] * size
        fixed: dict[tuple[int, int], int] = {}
        order8: dict[tuple[int, int], dict[int, int]] = {}
        for record in family["class_coefficients"]:
            order = int(record["order"])
            mask = int(record["canonical_mask"])
            if order in (5, 6):
                count = int(lower[order][mask])
            elif order == 7:
                count = int(x7[mask])
            else:
                count = 0
            for row, column, value in record["upper_entries"]:
                row, column, value = int(row), int(column), int(value)
                require(0 <= row <= column < size, "bad upper-triangle entry")
                key = (row, column)
                if order <= 7:
                    fixed[key] = fixed.get(key, 0) + count * value
                    if order == 5:
                        require(row == column, "order-five moment is not diagonal")
                        mean[row] += count * value
                else:
                    bucket = order8.setdefault(key, {})
                    require(class8_index[mask] not in bucket, "duplicate order-eight entry")
                    bucket[class8_index[mask]] = value
        require(
            sum(mean) == root_count * math.comb(N - 2, 3),
            f"{family_name} first-moment total failed",
        )
        emitted = 0
        for row in range(size):
            for column in range(row, size):
                key = (row, column)
                raw_coefficients = {
                    variable: root_count * value
                    for variable, value in order8.get(key, {}).items()
                }
                rhs = mean[row] * mean[column] - root_count * fixed.get(key, 0)
                cleaned = {
                    variable: value
                    for variable, value in raw_coefficients.items()
                    if value
                }
                if cleaned:
                    moment_rows.append(
                        ExactRow(
                            f"M:{family_name}:{row}:{column}", cleaned, rhs
                        )
                    )
                else:
                    require(rhs == 0, "trivial moment row is a contradiction")
                emitted += 1
        emitted_counts[family_name] = emitted

    def iterator() -> Iterator[ExactRow]:
        yield ExactRow(
            "sum_x8", {column: 1 for column in range(len(classes[8]))}, C8
        )
        yield from deletion_rows
        yield from marked_rows
        yield from moment_rows

    nontrivial_count = 1 + len(deletion_rows) + len(marked_rows) + len(moment_rows)
    record = {
        "rows_after_trivial_removal": nontrivial_count,
        "deletion_rows": len(deletion_rows),
        "marked_rows_seen": marked_seen,
        "moment_upper_entries": emitted_counts,
    }
    return iterator(), record


def wave44_check(row_system: dict, x7_values: Sequence[int]) -> int:
    passed = 0
    for family_name in ("base", "vertex", "edge", "nonedge"):
        family = row_system["families"][family_name]
        require(len(family["rows"]) == len(family["rhs"]), "Wave44 row/rhs mismatch")
        for row, rhs in zip(family["rows"], family["rhs"], strict=True):
            require(len(row) == len(x7_values) + 1, "Wave44 row width changed")
            value = sum(
                int(a) * int(b)
                for a, b in zip(row[:-1], x7_values, strict=True)
            ) + int(row[-1]) * Y
            require(value == int(rhs), f"Wave44 {family_name} equality failed")
            passed += 1
    return passed


def verify_witness(
    name: str,
    witness: dict,
    cut_payloads: Sequence[dict],
    coefficients: dict,
    marked: dict,
    row_system: dict,
    classes: dict[int, tuple[int, ...]],
    reference_lower: dict[int, dict[int, Fraction]],
    memory_samples: list[dict[str, float | str]],
) -> dict:
    x7 = support_map(witness, "x7_support", classes[7])
    x8 = support_map(witness, "x8_support", classes[8])
    require(all(v >= 0 for v in x7.values()), f"{name}: negative x7")
    require(all(v >= 0 for v in x8.values()), f"{name}: negative x8")
    require(all(v.denominator == 1 for v in x7.values()), f"{name}: fractional x7")
    require(sum(x7.values()) == C7, f"{name}: x7 total failed")
    require(sum(x8.values()) == C8, f"{name}: x8 total failed")
    require(len(witness["x7_support"]) == sum(v > 0 for v in x7.values()),
            f"{name}: x7 support contains zero")
    require(len(witness["x8_support"]) == sum(v > 0 for v in x8.values()),
            f"{name}: x8 support contains zero")
    x7_values = [int(x7[mask]) for mask in classes[7]]
    wave44_rows = wave44_check(row_system, x7_values)
    require(wave44_rows == 170, f"{name}: Wave44 row count changed")
    require(witness["x7_record"]["sum"] == C7, f"{name}: stored x7 total differs")
    require(witness["x7_record"]["support"] == len(witness["x7_support"]),
            f"{name}: stored x7 support differs")
    require(witness["x7_record"]["wave44_rows_passed"] == wave44_rows,
            f"{name}: stored Wave44 count differs")
    require(witness["x7_record"]["y"] == Y, f"{name}: y changed")
    require(witness["x7_record"]["h11"] == 4 * Y, f"{name}: h11 changed")

    lower = derive_lower_counts(x7, classes)
    require(
        lower[5] == reference_lower[5] and lower[6] == reference_lower[6],
        f"{name}: lower counts differ from cut reconstruction counts",
    )
    rows, row_record = base_rows(coefficients, marked, lower, x7, classes)
    require(row_record == witness["row_record"], f"{name}: row record differs")

    all_cuts = [cut for payload in cut_payloads for cut in payload["cuts"]]
    cut_by_hash = {cut["cut_sha256"]: cut for cut in all_cuts}
    stored_values = witness["exact_cut_values"]
    exact_cut_values: dict[str, dict] = {}
    if name == "after_two":
        relevant_cuts = list(cut_payloads[0]["cuts"])
        require(
            set(stored_values) == {str(cut["root_mask"]) for cut in relevant_cuts},
            f"{name}: cut-value root key set changed",
        )
    else:
        relevant_cuts = all_cuts
        require(
            set(stored_values) == set(cut_by_hash),
            f"{name}: cut-value hash key set changed",
        )
    for cut in relevant_cuts:
        cut_hash = str(cut["cut_sha256"])
        value = evaluate_cut(cut, x7, x8, classes)
        stored_record = (
            stored_values[str(cut["root_mask"])]
            if name == "after_two"
            else stored_values[cut_hash]
        )
        if isinstance(stored_record, str):
            stored_value = fraction(stored_record)
            active = stored_value == 0
            stored_root = int(cut["root_mask"])
        else:
            stored_value = fraction(stored_record["value"])
            active = bool(stored_record["active"])
            stored_root = int(stored_record["root_mask"])
        require(value == stored_value, f"{name}: stored cut value differs")
        require(value >= 0, f"{name}: cut {cut_hash} is violated")
        require(stored_root == int(cut["root_mask"]), f"{name}: cut root differs")
        require((value == 0) == active, f"{name}: active flag differs")
        exact_cut_values[cut_hash] = {
            "root_mask": int(cut["root_mask"]),
            "value": fraction_string(value),
            "active": active,
        }

    if name == "after_two":
        active_hashes = [
            cut["cut_sha256"]
            for cut in cut_payloads[0]["cuts"]
            if int(cut["root_mask"]) in set(map(int, witness["active_cut_roots"]))
        ]
    else:
        active_hashes = [
            cut["cut_sha256"]
            for cut in all_cuts
            if cut["cut_sha256"] in set(witness["active_cut_hashes"])
        ]
    require(
        set(active_hashes)
        == {cut_hash for cut_hash, record in exact_cut_values.items() if record["active"]},
        f"{name}: active cut set differs",
    )
    class8_index = {mask: index for index, mask in enumerate(classes[8])}
    active_rows = [
        dense_cut_row(cut_by_hash[cut_hash], x7, classes, class8_index)
        for cut_hash in active_hashes
    ]
    all_rows = itertools.chain(rows, active_rows)

    support_global = [index for index, mask in enumerate(classes[8]) if x8[mask] > 0]
    require(support_global == list(map(int, witness["selection"]["support"])),
            f"{name}: stored support indices differ")
    support_local = {
        global_index: local_index
        for local_index, global_index in enumerate(support_global)
    }
    rank = ModularRank(len(support_global))
    stored_selected = list(map(int, witness["selection"]["selected_row_indices"]))
    require(
        stored_selected == sorted(set(stored_selected)),
        f"{name}: stored modular row selection is not strictly increasing",
    )
    selected_set = set(stored_selected)
    all_row_count = 0
    restricted_count = 0
    for row in all_rows:
        all_row_count += 1
        lhs = sum(
            coefficient * x8[classes[8][column]]
            for column, coefficient in row.coefficients.items()
        )
        require(lhs == row.rhs, f"{name}: exact row failed: {row.label}")
        restricted = {
            support_local[column]: value
            for column, value in row.coefficients.items()
            if column in support_local
        }
        if not restricted:
            require(row.rhs == 0, f"{name}: support contradicts {row.label}")
            continue
        # Full rank is certified by independence of the stored square row
        # selection.  Replaying all omitted dependent rows exactly above is
        # still mandatory; only their redundant modular reductions are skipped.
        if restricted_count in selected_set:
            rank.consume(restricted_count, restricted)
        restricted_count += 1
    rank_record = rank.record(restricted_count)
    require(all_row_count == int(witness["exact_solve"]["all_rows_passed"]),
            f"{name}: all-row count differs")
    require(restricted_count == int(witness["exact_solve"]["restricted_rows_passed"]),
            f"{name}: restricted-row count differs")
    require(rank_record == witness["selection"]["modular_rank"],
            f"{name}: modular rank record differs: {rank_record}")
    require(rank.selected == stored_selected,
            f"{name}: modular independent-row selection differs")

    positive_values = [value for value in x8.values() if value > 0]
    denominators = [value.denominator for value in positive_values]
    numerators = [value.numerator for value in positive_values]
    solve_record = {
        "all_rows_passed": all_row_count,
        "restricted_rows_passed": restricted_count,
        "minimum_numerator": min(numerators),
        "maximum_numerator": max(numerators),
        "maximum_denominator": max(denominators),
        "distinct_denominators": len(set(denominators)),
        "integer_coordinates": sum(value == 1 for value in denominators),
    }
    require(solve_record == witness["exact_solve"], f"{name}: solve statistics differ")
    memory_samples.append(memory_sample(f"{name}_complete"))
    return {
        "claim_label": "VERIFIED",
        "scope": "exact feasibility of the retained finite linear relaxation",
        "x7_total": C7,
        "x7_support": len(witness["x7_support"]),
        "x8_total": C8,
        "x8_support": len(witness["x8_support"]),
        "nonnegative_coordinates": True,
        "wave44_equalities": wave44_rows,
        "deletion_equalities": row_record["deletion_rows"],
        "marked_equalities": row_record["marked_rows_seen"],
        "pair_root_upper_entries": row_record["moment_upper_entries"],
        "base_nontrivial_equalities": row_record["rows_after_trivial_removal"],
        "active_cut_equalities": len(active_rows),
        "all_equalities": all_row_count,
        "restricted_equalities": restricted_count,
        "modular_rank": rank_record,
        "selected_row_indices_exact_match": True,
        "exact_cut_values": exact_cut_values,
        "active_cut_hashes": active_hashes,
        "denominator_statistics": {
            "maximum": max(denominators),
            "distinct": len(set(denominators)),
            "integer_coordinates": sum(value == 1 for value in denominators),
        },
    }


def self_test() -> dict:
    # Canonicalization is invariant under relabeling.
    path4 = 0
    positions = edge_positions(4)
    for edge in ((0, 1), (1, 2), (2, 3)):
        path4 |= 1 << positions[edge]
    images = {
        canonical_unrooted(transform_mask(path4, 4, permutation), 4)
        for permutation in itertools.permutations(range(4))
    }
    require(len(images) == 1, "canonicalization self-test failed")
    require(locally_admissible(path4, 4), "admissibility self-test failed")
    triangle = sum(
        1 << positions[edge] for edge in ((0, 1), (0, 2), (1, 2))
    )
    require(locally_admissible(triangle, 4), "triangle should meet lambda cap")
    k4 = (1 << math.comb(4, 2)) - 1
    require(not locally_admissible(k4, 4), "K4 should violate lambda cap")
    require(len(covering_pair_indices(2)) == 1, "order-six product count failed")
    require(len(covering_pair_indices(3)) == 6, "order-seven product count failed")
    require(len(covering_pair_indices(4)) == 6, "order-eight product count failed")
    require(len(flag_universe(3)) == 155, "root-3 flag universe changed")
    require(len(flag_universe(12)) == 178, "root-12 flag universe changed")
    return {
        "canonicalization_relabelings": 24,
        "admissibility_cases": 3,
        "covering_pair_counts": {"2": 1, "3": 6, "4": 6},
        "flag_counts": {"3": 155, "12": 178},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "verification-results.json",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0

    started = time.time()
    memory_samples = [memory_sample("start")]
    verified_hashes = {}
    for relative, expected in {**PRIMARY_HASHES, **SUPPORT_HASHES}.items():
        observed = file_sha256(ROOT / relative)
        require(observed == expected, f"input hash mismatch: {relative}")
        verified_hashes[relative] = observed
    memory_samples.append(memory_sample("hashes_verified"))

    cut_payloads = [
        load_json("attempts/wave152-four-root-order8/exact-cuts.json"),
        load_json("attempts/wave152-four-root-order8/iteration2-cuts.json"),
    ]
    initial_witness = load_json(
        "attempts/wave150-order8-sdp-scout/exact-rank1-witness.json"
    )
    after_two = load_json(
        "attempts/wave152-four-root-order8/exact-witness-after-two-cuts.json"
    )
    after_four = load_json(
        "attempts/wave152-four-root-order8/exact-witness-after-four-cuts.json"
    )
    row_system = load_json("attempts/wave44-rooted-flags/row-system.json")
    coefficients = load_gzip_json(
        "attempts/wave147-alternative-lane/coefficients.json.gz"
    )
    marked = load_gzip_json("attempts/wave148-marked-order8/marked-rows.json.gz")
    exact_results = load_json(
        "attempts/wave147-alternative-lane/exact-results.json"
    )

    classes = class_sets(coefficients, row_system, exact_results)
    initial_x7 = support_map(initial_witness, "x7_support", classes[7])
    after_two_x7 = support_map(after_two, "x7_support", classes[7])
    initial_lower = derive_lower_counts(initial_x7, classes)
    reference_lower = derive_lower_counts(after_two_x7, classes)
    require(
        initial_lower[5] == reference_lower[5]
        and initial_lower[6] == reference_lower[6],
        "fixed lower counts differ between discovery and replacement witnesses",
    )
    memory_samples.append(memory_sample("lower_counts_derived"))
    cut_results = reconstruct_cuts(
        cut_payloads,
        classes,
        reference_lower,
        [initial_witness, after_two],
        memory_samples,
    )
    memory_samples.append(memory_sample("cuts_reconstructed"))
    witness_results = {
        "after_two": verify_witness(
            "after_two",
            after_two,
            cut_payloads,
            coefficients,
            marked,
            row_system,
            classes,
            reference_lower,
            memory_samples,
        ),
        "after_four": verify_witness(
            "after_four",
            after_four,
            cut_payloads,
            coefficients,
            marked,
            row_system,
            classes,
            reference_lower,
            memory_samples,
        ),
    }
    tests = self_test()
    memory_samples.append(memory_sample("complete"))
    result = {
        "format": "wave155-four-root-feedback-independent-verification-v1",
        "claim_label": "VERIFIED",
        "scope": (
            "Four exact covariance cuts and exact rational feasibility of the "
            "retained finite relaxation after the first two and all four cuts."
        ),
        "input_location_note": (
            "The assigned attempts/wave155-four-root-feedback directory was "
            "absent; the seven exact named artifacts were found and frozen "
            "under attempts/wave152-four-root-order8."
        ),
        "separation": {
            "discovery_python_imported": False,
            "discovery_python_executed": False,
            "verifier_runtime": "Python standard library only",
            "solver_status_used_as_evidence": False,
        },
        "inputs_sha256": verified_hashes,
        "class_streams": {
            str(order): {"count": len(classes[order])}
            for order in (5, 6, 7, 8)
        },
        "fixed_lower_counts": {
            "order5_total": fraction_string(sum(reference_lower[5].values())),
            "order5_support": sum(v > 0 for v in reference_lower[5].values()),
            "order6_total": fraction_string(sum(reference_lower[6].values())),
            "order6_support": sum(v > 0 for v in reference_lower[6].values()),
        },
        "cuts": cut_results,
        "witnesses": witness_results,
        "tests": tests,
        "verdict": {
            "four_primitive_covariance_cuts": "VERIFIED",
            "finite_relaxation_after_two_cuts": "EXACT_RATIONAL_FEASIBLE",
            "finite_relaxation_after_four_cuts": "EXACT_RATIONAL_FEASIBLE",
            "graph_constructed": False,
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "Conway_99": "UNKNOWN",
        },
        "metadata_observation": (
            "The after-four witness retains an after-two format/scope/conclusion "
            "label.  Its actual inputs, four exact cut values, and two active "
            "cut rows establish the after-four finite-relaxation claim."
        ),
        "limitations": [
            "Exact finite-relaxation feasibility does not construct a graph.",
            "The retained equality system is only a relaxation of graph existence.",
            "The HiGHS files are support-selection diagnostics, not certificates.",
            "No endpoint theorem, strict upper bound, or conjecture resolution follows.",
        ],
        "resource_report": {
            "elapsed_seconds": time.time() - started,
            "minimum_free_physical_memory_percent": min(
                float(sample["free_physical_memory_percent"])
                for sample in memory_samples
            ),
            "samples": memory_samples,
        },
    }
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "claim_label": result["claim_label"],
                "cuts": len(cut_results),
                "after_two_rows": witness_results["after_two"]["all_equalities"],
                "after_four_rows": witness_results["after_four"]["all_equalities"],
                "minimum_free_percent": result["resource_report"][
                    "minimum_free_physical_memory_percent"
                ],
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
