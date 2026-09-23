"""Exact standard-library companion for the Wave 19 alternate frontier.

The script checks the conditional n3=60 reduction described in the paired
agent report.  It fetches pinned House of Graphs catalogs into memory, checks
all catalog records, performs the complete order-20 point-graph census, and
replays the exact rational / finite certificates.  It never treats a solver
exit code as evidence and has no dependency outside the Python standard
library.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Iterable, Iterator
import urllib.request


CATALOGS = {
    6: {
        "url": "https://houseofgraphs.org/data/cubics/cub06.g6",
        "bytes": 10,
        "sha256": "49a7391d96ad84fd13c8b5267ef23c215085ed317e6146e479df2bcdfd672949",
        "records": 2,
    },
    8: {
        "url": "https://houseofgraphs.org/data/cubics/cub08.g6",
        "bytes": 35,
        "sha256": "6946d13a0aec85386d47d087ad2a9f2561b05d8580f0ec937414f8d31359d34f",
        "records": 5,
    },
    10: {
        "url": "https://houseofgraphs.org/data/cubics/cub10.g6",
        "bytes": 190,
        "sha256": "0c3182bcbbfdc38fc7b84f3a1ac510834c3064524db00afeac212a3292f17c7b",
        "records": 19,
    },
    12: {
        "url": "https://houseofgraphs.org/data/cubics/cub12.g6",
        "bytes": 1105,
        "sha256": "21bab16fbf7db826928315b9ca1d64684c0b1f7014b02fab0c6f2fb2f247104b",
        "records": 85,
    },
    14: {
        "url": "https://houseofgraphs.org/data/cubics/cub14.g6",
        "bytes": 9162,
        "sha256": "6657f77868567a7e604a2325b5d748e5a04848b4ab75310ffa3ba695d26c66fe",
        "records": 509,
    },
    20: {
        "url": "https://houseofgraphs.org/data/cubics/cub20.g6",
        "bytes": 17_356_626,
        "sha256": "83e8d235435fb3aab83b0315ae39fe16cf0afdb4699bbdcd6fae31541ea8d458",
        "records": 510_489,
    },
}


Edge = tuple[int, int]
Rows = tuple[int, ...]
Point = Edge


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def edge(left: int, right: int) -> Edge:
    if left == right:
        raise ValueError("loop")
    return (left, right) if left < right else (right, left)


def fetch_catalog(order: int) -> tuple[bytes, ...]:
    metadata = CATALOGS[order]
    request = urllib.request.Request(
        str(metadata["url"]),
        headers={"User-Agent": "Conway99-Wave19-alternate-exact/1"},
    )
    with urllib.request.urlopen(request, timeout=60.0) as response:
        data = response.read()
    observed = (len(data), sha256_bytes(data))
    expected = (metadata["bytes"], metadata["sha256"])
    if observed != expected:
        raise AssertionError(f"order-{order} catalog bytes changed: {observed}")
    records = tuple(line for line in data.splitlines() if line)
    if len(records) != metadata["records"]:
        raise AssertionError(f"order-{order} record count changed")
    if len(records) != len(set(records)):
        raise AssertionError(f"order-{order} duplicate record")
    return records


def decode_graph6(record: bytes) -> Rows:
    if not record or record.startswith(b">>graph6<<"):
        raise ValueError("bare short graph6 required")
    order = record[0] - 63
    if not 0 <= order <= 62:
        raise ValueError("short graph6 order required")
    bits: list[int] = []
    for raw in record[1:]:
        value = raw - 63
        if not 0 <= value <= 63:
            raise ValueError("invalid graph6 byte")
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    needed = order * (order - 1) // 2
    if len(bits) < needed:
        raise ValueError("truncated graph6")
    rows = [0] * order
    cursor = 0
    for right in range(1, order):
        for left in range(right):
            if bits[cursor]:
                rows[left] |= 1 << right
                rows[right] |= 1 << left
            cursor += 1
    return tuple(rows)


def graph_edges(rows: Rows) -> tuple[Edge, ...]:
    return tuple(
        (left, right)
        for left in range(len(rows))
        for right in range(left + 1, len(rows))
        if rows[left] >> right & 1
    )


def validate_connected_cubic(rows: Rows) -> None:
    order = len(rows)
    if any(row.bit_count() != 3 for row in rows):
        raise AssertionError("catalog graph is not cubic")
    seen = 1
    frontier = 1
    while frontier:
        bit = frontier & -frontier
        frontier ^= bit
        vertex = bit.bit_length() - 1
        new = rows[vertex] & ~seen
        seen |= new
        frontier |= new
    if seen.bit_count() != order:
        raise AssertionError("catalog graph is not connected")


def is_triangle_free(rows: Rows) -> bool:
    return all(
        not (rows[left] & rows[right])
        for left, right in graph_edges(rows)
    )


def disjoint_union(parts: Iterable[Rows]) -> Rows:
    output: list[int] = []
    offset = 0
    for rows in parts:
        output.extend(row << offset for row in rows)
        offset += len(rows)
    return tuple(output)


def six_cycle_vertex_sets(rows: Rows) -> tuple[int, ...]:
    order = len(rows)
    found: set[int] = set()
    for root in range(order):
        def extend(path: tuple[int, ...], seen: int) -> None:
            current = path[-1]
            if len(path) == 6:
                if rows[current] >> root & 1:
                    found.add(sum(1 << vertex for vertex in path))
                return
            choices = rows[current] & ~seen
            while choices:
                bit = choices & -choices
                choices ^= bit
                vertex = bit.bit_length() - 1
                if vertex > root:
                    extend(path + (vertex,), seen | bit)

        extend((root,), 1 << root)
    return tuple(sorted(found))


def distance_two_closed(rows: Rows, root: int) -> int:
    result = (1 << root) | rows[root]
    neighbors = rows[root]
    while neighbors:
        bit = neighbors & -neighbors
        neighbors ^= bit
        result |= rows[bit.bit_length() - 1]
    return result


def local_cycle_domains(rows: Rows) -> tuple[frozenset[int], ...] | None:
    cycles = six_cycle_vertex_sets(rows)
    domains = []
    for root in range(len(rows)):
        forbidden = distance_two_closed(rows, root)
        domain = frozenset(cycle for cycle in cycles if not cycle & forbidden)
        if not domain:
            return None
        domains.append(domain)
    return tuple(domains)


def propagate_symmetric_domains(
    input_domains: tuple[frozenset[int], ...],
) -> tuple[frozenset[int], ...] | None:
    domains = [set(domain) for domain in input_domains]
    changed = True
    while changed:
        changed = False
        for left in range(len(domains)):
            if not domains[left]:
                return None
            for right in range(left + 1, len(domains)):
                left_has = (
                    any(not (mask >> right & 1) for mask in domains[left]),
                    any(mask >> right & 1 for mask in domains[left]),
                )
                right_has = (
                    any(not (mask >> left & 1) for mask in domains[right]),
                    any(mask >> left & 1 for mask in domains[right]),
                )
                new_left = {
                    mask
                    for mask in domains[left]
                    if right_has[bool(mask >> right & 1)]
                }
                new_right = {
                    mask
                    for mask in domains[right]
                    if left_has[bool(mask >> left & 1)]
                }
                if not new_left or not new_right:
                    return None
                if new_left != domains[left]:
                    domains[left] = new_left
                    changed = True
                if new_right != domains[right]:
                    domains[right] = new_right
                    changed = True
    return tuple(frozenset(domain) for domain in domains)


def symmetric_cycle_solutions(
    domains: tuple[frozenset[int], ...],
) -> tuple[tuple[int, ...], ...]:
    solutions: list[tuple[int, ...]] = []

    def search(current: tuple[frozenset[int], ...]) -> None:
        propagated = propagate_symmetric_domains(current)
        if propagated is None:
            return
        branch = min(
            (
                index
                for index, domain in enumerate(propagated)
                if len(domain) > 1
            ),
            key=lambda index: len(propagated[index]),
            default=None,
        )
        if branch is None:
            solutions.append(tuple(next(iter(domain)) for domain in propagated))
            return
        for value in sorted(propagated[branch]):
            child = list(propagated)
            child[branch] = frozenset((value,))
            search(tuple(child))

    search(domains)
    return tuple(solutions)


def point_edges(rows: Rows) -> tuple[Point, ...]:
    return tuple(sorted(graph_edges(rows)))


def compatible_supports(
    points: tuple[Point, ...], l_rows: tuple[int, ...]
) -> tuple[Edge, ...]:
    result = []
    for left, right in itertools.combinations(range(len(points)), 2):
        if set(points[left]) & set(points[right]):
            continue
        if all(
            l_rows[a] >> b & 1
            for a in points[left]
            for b in points[right]
        ):
            result.append((left, right))
    return tuple(result)


def support_degree_histogram(
    points: tuple[Point, ...], l_rows: tuple[int, ...]
) -> dict[str, int]:
    degrees = [0] * len(points)
    for left, right in compatible_supports(points, l_rows):
        degrees[left] += 1
        degrees[right] += 1
    return {
        str(value): count
        for value, count in sorted(Counter(degrees).items())
    }


def forced_zero_edges(
    f_rows: Rows, points: tuple[Point, ...], l_rows: tuple[int, ...]
) -> tuple[tuple[Edge, tuple[Edge, ...]], ...]:
    point_index = {point: index for index, point in enumerate(points)}
    forced: dict[Edge, list[Edge]] = {}
    for left, right in itertools.combinations(range(len(f_rows)), 2):
        if f_rows[left] >> right & 1 or l_rows[left] >> right & 1:
            continue
        common_mask = f_rows[left] & f_rows[right]
        common = tuple(
            vertex
            for vertex in range(len(f_rows))
            if common_mask >> vertex & 1
        )
        if len(common) != 2:
            continue
        left_remaining = next(
            vertex
            for vertex in range(len(f_rows))
            if f_rows[left] >> vertex & 1 and vertex not in common
        )
        right_remaining = next(
            vertex
            for vertex in range(len(f_rows))
            if f_rows[right] >> vertex & 1 and vertex not in common
        )
        point_pair = edge(
            point_index[edge(left, left_remaining)],
            point_index[edge(right, right_remaining)],
        )
        forced.setdefault(point_pair, []).append((left, right))
    return tuple(
        (key, tuple(sorted(value)))
        for key, value in sorted(forced.items())
    )


def connected_census(
    records: tuple[bytes, ...],
) -> tuple[dict[str, object], bytes]:
    disposition = bytearray()
    triangle_free = 0
    local_survivors = 0
    symmetric_failures = 0
    final_rows = []
    for index, record in enumerate(records):
        rows = decode_graph6(record)
        validate_connected_cubic(rows)
        if not is_triangle_free(rows):
            disposition.append(ord("T"))
            continue
        triangle_free += 1
        domains = local_cycle_domains(rows)
        if domains is None:
            disposition.append(ord("L"))
            continue
        local_survivors += 1
        solutions = symmetric_cycle_solutions(domains)
        if not solutions:
            symmetric_failures += 1
            disposition.append(ord("S"))
            continue
        if len(solutions) != 1:
            raise AssertionError("connected survivor is not unique")
        l_rows = solutions[0]
        points = point_edges(rows)
        forced = forced_zero_edges(rows, points, l_rows)
        degree_histogram = support_degree_histogram(points, l_rows)
        row = {
            "catalog_index": index,
            "record_sha256": sha256_bytes(record),
            "domain_size_histogram": {
                str(key): value
                for key, value in sorted(
                    Counter(map(len, domains)).items()
                )
            },
            "support_degree_histogram": degree_histogram,
            "forced_zero_edge_count": len(forced),
            "forced_codegree_two_pair_count": sum(
                len(value) for _, value in forced
            ),
            "l_rows": list(l_rows),
        }
        if len(forced) > 3:
            disposition.append(ord("Z"))
            row["disposition"] = "FORCED_Z_EXCEEDS_THREE"
        elif int(min(map(int, degree_histogram))) < 2:
            disposition.append(ord("D"))
            row["disposition"] = "SUPPORT_DEGREE_BELOW_TWO"
        else:
            raise AssertionError("unclassified connected survivor")
        final_rows.append(row)
    disposition.append(ord("\n"))
    summary = {
        "catalog_records": len(records),
        "triangle_containing": disposition.count(ord("T")),
        "triangle_free": triangle_free,
        "triangle_free_without_local_C6": disposition.count(ord("L")),
        "local_C6_survivors": local_survivors,
        "symmetric_L_failures": symmetric_failures,
        "forced_Z_exceeds_three": disposition.count(ord("Z")),
        "support_degree_below_two": disposition.count(ord("D")),
        "final_rows": final_rows,
    }
    if (
        summary["triangle_containing"] != 412_943
        or triangle_free != 97_546
        or summary["triangle_free_without_local_C6"] != 97_248
        or local_survivors != 298
        or symmetric_failures != 295
        or summary["forced_Z_exceeds_three"] != 2
        or summary["support_degree_below_two"] != 1
    ):
        raise AssertionError("connected census counts changed")
    return summary, bytes(disposition)


def triangle_free_catalog(
    order: int,
) -> tuple[tuple[int, bytes, Rows], ...]:
    result = []
    for index, record in enumerate(fetch_catalog(order)):
        rows = decode_graph6(record)
        validate_connected_cubic(rows)
        if is_triangle_free(rows):
            result.append((index, record, rows))
    return tuple(result)


def disconnected_cases() -> tuple[tuple[str, Rows], ...]:
    catalogs = {
        order: triangle_free_catalog(order)
        for order in (6, 8, 10, 12, 14)
    }
    expected = {6: 1, 8: 2, 10: 6, 12: 22, 14: 110}
    if {order: len(rows) for order, rows in catalogs.items()} != expected:
        raise AssertionError("small triangle-free catalog counts changed")
    cases: list[tuple[str, Rows]] = []
    for left in catalogs[14]:
        for right in catalogs[6]:
            cases.append(
                (
                    f"14-{left[0]:03d}+6-{right[0]:03d}",
                    disjoint_union((left[2], right[2])),
                )
            )
    for left in catalogs[12]:
        for right in catalogs[8]:
            cases.append(
                (
                    f"12-{left[0]:03d}+8-{right[0]:03d}",
                    disjoint_union((left[2], right[2])),
                )
            )
    for left_index, left in enumerate(catalogs[10]):
        for right in catalogs[10][left_index:]:
            cases.append(
                (
                    f"10-{left[0]:03d}+10-{right[0]:03d}",
                    disjoint_union((left[2], right[2])),
                )
            )
    for component8 in catalogs[8]:
        for left_index, component6a in enumerate(catalogs[6]):
            for component6b in catalogs[6][left_index:]:
                cases.append(
                    (
                        (
                            f"8-{component8[0]:03d}"
                            f"+6-{component6a[0]:03d}"
                            f"+6-{component6b[0]:03d}"
                        ),
                        disjoint_union(
                            (component8[2], component6a[2], component6b[2])
                        ),
                    )
                )
    if len(cases) != 177:
        raise AssertionError("disconnected case count changed")
    return tuple(cases)


def disconnected_census() -> tuple[dict[str, object], tuple[dict[str, object], ...], tuple[tuple[int, ...], ...], Rows]:
    rows_out = []
    status_counts: Counter[str] = Counter()
    petersen_solutions: tuple[tuple[int, ...], ...] | None = None
    petersen_rows: Rows | None = None
    for case_id, rows in disconnected_cases():
        domains = local_cycle_domains(rows)
        if domains is None:
            status = "NO_LOCAL_C6"
            solutions: tuple[tuple[int, ...], ...] = ()
        else:
            solutions = symmetric_cycle_solutions(domains)
            if not solutions:
                status = "NO_SYMMETRIC_L"
            else:
                forced_counts = []
                degree_histograms = []
                points = point_edges(rows)
                for l_rows in solutions:
                    forced_counts.append(
                        len(forced_zero_edges(rows, points, l_rows))
                    )
                    degree_histograms.append(
                        support_degree_histogram(points, l_rows)
                    )
                if all(count == 20 for count in forced_counts):
                    status = "FORCED_Z_EXCEEDS_THREE"
                elif (
                    len(solutions) == 120
                    and set(forced_counts) == {0}
                    and set(
                        tuple(sorted(item.items()))
                        for item in degree_histograms
                    ) == {(("2", 30),)}
                ):
                    status = "TWO_PETERSEN_RESIDUAL"
                    petersen_solutions = solutions
                    petersen_rows = rows
                else:
                    raise AssertionError(f"unclassified {case_id}")
        status_counts[status] += 1
        rows_out.append(
            {
                "case_id": case_id,
                "status": status,
                "symmetric_L_solution_count": len(solutions),
            }
        )
    expected = {
        "NO_LOCAL_C6": 5,
        "NO_SYMMETRIC_L": 168,
        "FORCED_Z_EXCEEDS_THREE": 3,
        "TWO_PETERSEN_RESIDUAL": 1,
    }
    if dict(status_counts) != expected:
        raise AssertionError("disconnected census counts changed")
    assert petersen_solutions is not None and petersen_rows is not None
    return (
        {
            "case_count": 177,
            "status_counts": dict(sorted(status_counts.items())),
            "triangle_free_component_counts": {
                "6": 1,
                "8": 2,
                "10": 6,
                "12": 22,
                "14": 110,
            },
        },
        tuple(rows_out),
        petersen_solutions,
        petersen_rows,
    )


def l_edges(l_rows: tuple[int, ...]) -> frozenset[Edge]:
    return frozenset(
        (left, right)
        for left in range(len(l_rows))
        for right in range(left + 1, len(l_rows))
        if l_rows[left] >> right & 1
    )


def unique_r_for_l(
    points: tuple[Point, ...], l_rows: tuple[int, ...]
) -> frozenset[Edge]:
    candidates = compatible_supports(points, l_rows)
    degrees = [0] * len(points)
    for left, right in candidates:
        degrees[left] += 1
        degrees[right] += 1
    if set(degrees) != {2}:
        raise AssertionError("two-Petersen compatible graph is not 2-regular")
    selected = frozenset(candidates)
    coverage: Counter[Edge] = Counter()
    for left, right in selected:
        for a in points[left]:
            for b in points[right]:
                coverage[edge(a, b)] += 1
    if set(coverage.values()) != {2} or set(coverage) != set(l_edges(l_rows)):
        raise AssertionError("rectangle coverage is not exactly twofold")
    for label_pair in coverage:
        covers = [
            support
            for support in selected
            if label_pair
            in {
                edge(a, b)
                for a in points[support[0]]
                for b in points[support[1]]
            }
        ]
        if len(covers) != 2:
            raise AssertionError("coverage cardinality changed")
        for side in label_pair:
            side_points = []
            for support in covers:
                side_points.append(
                    next(
                        point
                        for point in support
                        if side in points[point]
                    )
                )
            if len(set(side_points)) != 2:
                raise AssertionError("independent matching violation")
    return selected


def graph_automorphisms(rows: Rows) -> tuple[tuple[int, ...], ...]:
    order = len(rows)
    output = []
    mapping = [-1] * order
    used = 0

    def compatible(source: int, target: int) -> bool:
        for previous in range(source):
            image = mapping[previous]
            if bool(rows[source] >> previous & 1) != bool(
                rows[target] >> image & 1
            ):
                return False
        return True

    def search(source: int, occupied: int) -> None:
        if source == order:
            output.append(tuple(mapping))
            return
        for target in range(order):
            if occupied >> target & 1:
                continue
            if compatible(source, target):
                mapping[source] = target
                search(source + 1, occupied | (1 << target))
                mapping[source] = -1

    search(0, used)
    return tuple(output)


def apply_label_permutation_to_l(
    l_rows: tuple[int, ...], permutation: tuple[int, ...]
) -> tuple[int, ...]:
    output = [0] * len(l_rows)
    for left, right in l_edges(l_rows):
        image_left = permutation[left]
        image_right = permutation[right]
        output[image_left] |= 1 << image_right
        output[image_right] |= 1 << image_left
    return tuple(output)


def induce_point_permutation(
    points: tuple[Point, ...], label_permutation: tuple[int, ...]
) -> tuple[int, ...]:
    point_index = {point: index for index, point in enumerate(points)}
    return tuple(
        point_index[edge(label_permutation[a], label_permutation[b])]
        for a, b in points
    )


def apply_point_permutation(
    support: frozenset[Edge], permutation: tuple[int, ...]
) -> frozenset[Edge]:
    return frozenset(edge(permutation[a], permutation[b]) for a, b in support)


def petersen_orbit_data(
    f_rows: Rows,
    l_solutions: tuple[tuple[int, ...], ...],
) -> tuple[
    tuple[int, ...],
    frozenset[Edge],
    tuple[tuple[int, ...], ...],
    dict[str, object],
]:
    points = point_edges(f_rows)
    base_l = min(l_solutions)
    base_r = unique_r_for_l(points, base_l)
    component = tuple(row & ((1 << 10) - 1) for row in f_rows[:10])
    automorphisms = graph_automorphisms(component)
    if len(automorphisms) != 120:
        raise AssertionError("Petersen automorphism count changed")
    full_group = []
    label_group = []
    for left in automorphisms:
        for right in automorphisms:
            preserve = tuple(left) + tuple(value + 10 for value in right)
            point_permutation = induce_point_permutation(points, preserve)
            if apply_point_permutation(base_r, point_permutation) == base_r:
                full_group.append(point_permutation)
                label_group.append(preserve)
            swap = tuple(value + 10 for value in left) + tuple(right)
            point_permutation = induce_point_permutation(points, swap)
            if apply_point_permutation(base_r, point_permutation) == base_r:
                full_group.append(point_permutation)
                label_group.append(swap)
    point_group = tuple(sorted(set(full_group)))
    label_group_unique = tuple(
        label
        for _, label in sorted(
            {point: label for point, label in zip(full_group, label_group)}.items()
        )
    )
    if len(point_group) != 240 or len(label_group_unique) != 240:
        raise AssertionError("base stabilizer size changed")
    solution_set = set(l_solutions)
    orbit = {
        apply_label_permutation_to_l(base_l, permutation)
        for left in automorphisms
        for right in automorphisms
        for permutation in (
            tuple(left) + tuple(value + 10 for value in right),
            tuple(value + 10 for value in left) + tuple(right),
        )
    }
    if orbit != solution_set or len(orbit) != 120:
        raise AssertionError("two-Petersen orbit is not exhaustive")
    # Check closure of the 240 point permutations.
    group_set = set(point_group)
    for permutation in point_group:
        inverse = [0] * len(permutation)
        for source, target in enumerate(permutation):
            inverse[target] = source
        if tuple(inverse) not in group_set:
            raise AssertionError("stabilizer lacks inverse")
    return (
        base_l,
        base_r,
        point_group,
        {
            "petersen_automorphism_count": len(automorphisms),
            "full_F_automorphism_count": 2 * len(automorphisms) ** 2,
            "L_R_model_count": len(l_solutions),
            "base_stabilizer_order": len(point_group),
            "orbit_equals_all_models": True,
        },
    )


def active_rows(
    points: tuple[Point, ...],
    r_edges: frozenset[Edge],
    z_edges: Iterable[Edge] = (),
) -> tuple[int, ...]:
    rows = [0] * len(points)
    for left, right in itertools.combinations(range(len(points)), 2):
        if set(points[left]) & set(points[right]):
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    for left, right in itertools.chain(r_edges, z_edges):
        rows[left] |= 1 << right
        rows[right] |= 1 << left
    return tuple(rows)


def outside_gram(active: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    order = len(active)
    return tuple(
        tuple(
            12 * int(left == right)
            - int(active[left] >> right & 1)
            - (active[left] & active[right]).bit_count()
            + 2
            for right in range(order)
        )
        for left in range(order)
    )


def rref(
    matrix: Iterable[Iterable[int | Fraction]],
    variable_count: int,
) -> tuple[list[list[Fraction]], tuple[int, ...]]:
    work = [[Fraction(value) for value in row] for row in matrix]
    rank = 0
    pivots = []
    for column in range(variable_count):
        pivot = next(
            (
                row
                for row in range(rank, len(work))
                if work[row][column]
            ),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][column]
        work[rank] = [value / pivot_value for value in work[rank]]
        for row in range(len(work)):
            if row == rank or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                value - factor * pivot_entry
                for value, pivot_entry in zip(work[row], work[rank])
            ]
        pivots.append(column)
        rank += 1
    return work, tuple(pivots)


def nullspace(matrix: Iterable[Iterable[int]]) -> tuple[tuple[Fraction, ...], ...]:
    rows = [list(row) for row in matrix]
    if not rows:
        return ()
    reduced, pivots = rref(rows, len(rows[0]))
    pivot_set = set(pivots)
    output = []
    for free in range(len(rows[0])):
        if free in pivot_set:
            continue
        vector = [Fraction(0)] * len(rows[0])
        vector[free] = Fraction(1)
        for row, pivot in zip(reduced, pivots):
            vector[pivot] = -row[free]
        output.append(tuple(vector))
    return tuple(output)


def exact_rank(matrix: Iterable[Iterable[int]]) -> int:
    rows = [list(row) for row in matrix]
    if not rows:
        return 0
    _, pivots = rref(rows, len(rows[0]))
    return len(pivots)


def is_psd_exact(matrix: tuple[tuple[int, ...], ...]) -> bool:
    work = [[Fraction(value) for value in row] for row in matrix]
    order = len(work)
    for pivot_index in range(order):
        for row in range(pivot_index, order):
            if work[row][row] < 0:
                return False
            if work[row][row] == 0 and any(
                work[row][column] != 0
                for column in range(pivot_index, order)
                if column != row
            ):
                return False
        pivot = next(
            (
                row
                for row in range(pivot_index, order)
                if work[row][row] > 0
            ),
            None,
        )
        if pivot is None:
            return True
        if pivot != pivot_index:
            work[pivot_index], work[pivot] = work[pivot], work[pivot_index]
            for row in range(order):
                work[row][pivot_index], work[row][pivot] = (
                    work[row][pivot],
                    work[row][pivot_index],
                )
        pivot_value = work[pivot_index][pivot_index]
        for row in range(pivot_index + 1, order):
            for column in range(row, order):
                value = (
                    work[row][column]
                    - work[row][pivot_index]
                    * work[pivot_index][column]
                    / pivot_value
                )
                work[row][column] = value
                work[column][row] = value
        for row in range(pivot_index + 1, order):
            work[row][pivot_index] = Fraction(0)
            work[pivot_index][row] = Fraction(0)
    return True


def enumerate_binary_supports(
    active: tuple[int, ...],
    gram: tuple[tuple[int, ...], ...],
) -> tuple[int, ...]:
    order = len(active)
    kernel = nullspace(gram)
    positive = tuple(
        sum(
            1 << right
            for right in range(order)
            if right != left and gram[left][right] > 0
        )
        for left in range(order)
    )
    output: list[int] = []

    def search(prefix: int, candidates: int) -> None:
        if prefix:
            vertices = tuple(
                index for index in range(order) if prefix >> index & 1
            )
            if all(
                sum(vector[index] for index in vertices) == 0
                for vector in kernel
            ) and all(
                (active[index] & prefix).bit_count()
                <= 2 - int(prefix >> index & 1)
                for index in range(order)
            ):
                output.append(prefix)
        choices = candidates
        while choices:
            bit = choices & -choices
            choices ^= bit
            vertex = bit.bit_length() - 1
            extended = prefix | bit
            if any(
                (active[index] & extended).bit_count() > 1
                for index in range(order)
                if extended >> index & 1
            ):
                continue
            search(
                extended,
                choices & positive[vertex] & ~((1 << (vertex + 1)) - 1),
            )

    search(0, (1 << order) - 1)
    return tuple(sorted(set(output)))


def gram_linear_system(
    supports: tuple[int, ...],
    gram: tuple[tuple[int, ...], ...],
) -> tuple[list[list[int]], tuple[tuple[int, int], ...]]:
    coordinates = tuple(
        (left, right)
        for left in range(len(gram))
        for right in range(left, len(gram))
    )
    matrix = [
        [
            int(support >> left & 1 and support >> right & 1)
            for support in supports
        ]
        + [gram[left][right]]
        for left, right in coordinates
    ]
    return matrix, coordinates


def solve_gram_system(
    supports: tuple[int, ...],
    gram: tuple[tuple[int, ...], ...],
) -> dict[str, object]:
    matrix, _ = gram_linear_system(supports, gram)
    reduced, pivots = rref(matrix, len(supports))
    inconsistent = any(
        not any(row[: len(supports)]) and row[-1]
        for row in reduced
    )
    result: dict[str, object] = {
        "support_count": len(supports),
        "coefficient_rank": len(pivots),
        "augmented_inconsistent": inconsistent,
    }
    if not inconsistent and len(pivots) == len(supports):
        solution = [Fraction(0)] * len(supports)
        for row, pivot in zip(reduced, pivots):
            solution[pivot] = row[-1]
        result["unique_solution_histogram"] = {
            str(value): count
            for value, count in sorted(
                Counter(solution).items(), key=lambda item: item[0]
            )
        }
        result["negative_solution_count"] = sum(value < 0 for value in solution)
    return result


def mask_hash(masks: Iterable[int], width: int = 30) -> str:
    byte_width = (width + 7) // 8
    digest = hashlib.sha256()
    for mask in masks:
        digest.update(mask.to_bytes(byte_width, "little"))
    return digest.hexdigest()


def eligible_zero_edges(
    points: tuple[Point, ...],
    active: tuple[int, ...],
    l_rows: tuple[int, ...],
) -> tuple[Edge, ...]:
    result = []
    for left, right in itertools.combinations(range(len(points)), 2):
        if active[left] >> right & 1:
            continue
        if set(points[left]) & set(points[right]):
            continue
        if all(
            not (l_rows[a] >> b & 1)
            for a in points[left]
            for b in points[right]
        ):
            result.append((left, right))
    return tuple(result)


def apply_permutation_to_edges(
    selected: Iterable[Edge], permutation: tuple[int, ...]
) -> tuple[Edge, ...]:
    return tuple(
        sorted(edge(permutation[left], permutation[right]) for left, right in selected)
    )


def apply_permutation_to_mask(mask: int, permutation: tuple[int, ...]) -> int:
    image = 0
    while mask:
        bit = mask & -mask
        mask ^= bit
        image |= 1 << permutation[bit.bit_length() - 1]
    return image


def canonical_edge_set(
    selected: tuple[Edge, ...],
    group: tuple[tuple[int, ...], ...],
) -> tuple[Edge, ...]:
    return min(apply_permutation_to_edges(selected, permutation) for permutation in group)


FARKAS_WEIGHTS = {
    (0, 27): -1,
    (1, 25): -1,
    (2, 16): -1,
    (3, 16): 1,
    (3, 23): -1,
    (3, 25): 1,
    (3, 28): -1,
    (6, 16): 1,
    (6, 22): -1,
    (6, 27): 1,
    (6, 29): -1,
    (8, 15): -1,
    (8, 17): -1,
    (8, 25): 1,
    (8, 27): 1,
}

FINAL_Z_EDGES = ((0, 23), (1, 22), (2, 17))
FARKAS_SIGN_MUTATION = (3, 16)
FARKAS_SIGN_MUTATION_WITNESS = 69_640
FARKAS_INDEX_MUTATION = ((0, 27), (0, 28))
FARKAS_INDEX_MUTATION_WITNESS = 268_437_537


def support_weight(support: int, weights: dict[Edge, int]) -> int:
    return sum(
        coefficient
        for (left, right), coefficient in weights.items()
        if support >> left & 1 and support >> right & 1
    )


def farkas_signature(
    supports: tuple[int, ...],
    gram: tuple[tuple[int, ...], ...],
    weights: dict[Edge, int],
) -> tuple[int, Counter[int]]:
    target_value = sum(
        coefficient * gram[left][right]
        for (left, right), coefficient in weights.items()
    )
    scores = Counter(support_weight(support, weights) for support in supports)
    return target_value, scores


def assert_farkas_separator(
    supports: tuple[int, ...],
    gram: tuple[tuple[int, ...], ...],
    weights: dict[Edge, int],
) -> tuple[int, Counter[int]]:
    target_value, scores = farkas_signature(supports, gram, weights)
    if target_value >= 0 or not scores or min(scores) < 0:
        raise AssertionError("weights are not a Farkas separator")
    return target_value, scores


def petersen_zero_census(
    f_rows: Rows,
    base_l: tuple[int, ...],
    base_r: frozenset[Edge],
    group: tuple[tuple[int, ...], ...],
) -> dict[str, object]:
    points = point_edges(f_rows)
    base_active = active_rows(points, base_r)
    base_gram = outside_gram(base_active)
    base_supports = enumerate_binary_supports(base_active, base_gram)
    base_system = solve_gram_system(base_supports, base_gram)
    if (
        exact_rank(base_gram) != 25
        or len(base_supports) != 72
        or Counter(mask.bit_count() for mask in base_supports)
        != Counter({2: 15, 3: 10, 4: 15, 5: 12, 6: 20})
        or base_system.get("negative_solution_count") != 15
    ):
        raise AssertionError("Z-empty Gram obstruction changed")

    zero_candidates = eligible_zero_edges(points, base_active, base_l)
    if len(zero_candidates) != 165:
        raise AssertionError("eligible Z edge count changed")
    entrywise_valid: list[tuple[Edge, ...]] = []
    subset_count = 0
    for size in (1, 2, 3):
        for indices in itertools.combinations(range(len(zero_candidates)), size):
            subset_count += 1
            selected = tuple(zero_candidates[index] for index in indices)
            gram = outside_gram(active_rows(points, base_r, selected))
            if all(value >= 0 for row in gram for value in row):
                entrywise_valid.append(selected)
    if subset_count != 748_825 or len(entrywise_valid) != 8_935:
        raise AssertionError("corrected Z entrywise census changed")

    orbit_counts: Counter[tuple[Edge, ...]] = Counter(
        canonical_edge_set(selected, group) for selected in entrywise_valid
    )
    if len(orbit_counts) != 66 or sum(orbit_counts.values()) != 8_935:
        raise AssertionError("corrected Z orbit count changed")

    psd_rows = []
    for representative, orbit_slice_count in sorted(orbit_counts.items()):
        active = active_rows(points, base_r, representative)
        gram = outside_gram(active)
        if not is_psd_exact(gram):
            continue
        supports = enumerate_binary_supports(active, gram)
        system = solve_gram_system(supports, gram)
        psd_rows.append(
            {
                "z_edges": [list(item) for item in representative],
                "entrywise_slice_count": orbit_slice_count,
                "gram_rank": exact_rank(gram),
                "support_count": len(supports),
                "support_sha256": mask_hash(supports),
                "support_weight_histogram": {
                    str(key): value
                    for key, value in sorted(
                        Counter(mask.bit_count() for mask in supports).items()
                    )
                },
                **system,
            }
        )
    if len(psd_rows) != 16:
        raise AssertionError("corrected Z PSD orbit count changed")
    inconsistent = sum(bool(row["augmented_inconsistent"]) for row in psd_rows)
    if inconsistent != 15:
        raise AssertionError("corrected Z inconsistent Gram count changed")
    residual = next(
        row for row in psd_rows if not row["augmented_inconsistent"]
    )
    residual_edges = tuple(tuple(item) for item in residual["z_edges"])
    target_edges = FINAL_Z_EDGES
    if (
        canonical_edge_set(target_edges, group) != target_edges
        or target_edges != residual_edges
    ):
        raise AssertionError(
            "sole residual orbit changed: "
            f"expected canonical {target_edges}, exact census retained "
            f"{residual_edges}"
        )
    target_active = active_rows(points, base_r, target_edges)
    target_gram = outside_gram(target_active)
    target_supports = enumerate_binary_supports(target_active, target_gram)
    target_value, support_weights = assert_farkas_separator(
        target_supports, target_gram, FARKAS_WEIGHTS
    )
    if (
        len(target_supports) != 232
        or exact_rank(target_gram) != 28
        or not is_psd_exact(target_gram)
        or mask_hash(target_supports)
        != "19100d7ee88ee7e7a9fb5bbf4546066ee889c131275b275dd96e07486eeac394"
        or Counter(mask.bit_count() for mask in target_supports)
        != Counter({1: 6, 2: 21, 3: 80, 4: 81, 5: 36, 6: 8})
        or residual["coefficient_rank"] != 174
        or residual["support_sha256"] != mask_hash(target_supports)
        or target_value != -6
        or support_weights != Counter({0: 211, 1: 18, 2: 3})
    ):
        raise AssertionError("final Farkas obstruction changed")

    # Mutation controls make the hard-coded certificate sensitive to both a
    # sign transcription and a point-index transcription.
    if (
        FARKAS_SIGN_MUTATION_WITNESS not in target_supports
        or FARKAS_INDEX_MUTATION_WITNESS not in target_supports
    ):
        raise AssertionError("Farkas mutation witness is not a candidate support")
    sign_mutation = dict(FARKAS_WEIGHTS)
    sign_mutation[FARKAS_SIGN_MUTATION] *= -1
    index_mutation = dict(FARKAS_WEIGHTS)
    source_pair, replacement_pair = FARKAS_INDEX_MUTATION
    index_mutation[replacement_pair] = index_mutation.pop(source_pair)
    for witness, mutation in (
        (FARKAS_SIGN_MUTATION_WITNESS, sign_mutation),
        (FARKAS_INDEX_MUTATION_WITNESS, index_mutation),
    ):
        if support_weight(witness, mutation) >= 0:
            raise AssertionError("Farkas mutation control was not rejected")

    # One representative per image is enough to check that the exact Gram
    # system, complete support set, and transported separator are invariant
    # throughout this stabilizer orbit.
    orbit_witnesses = {
        apply_permutation_to_edges(target_edges, permutation): permutation
        for permutation in group
    }
    if len(orbit_witnesses) != 10:
        raise AssertionError("final Z orbit size changed")
    target_support_set = set(target_supports)
    for image_edges, permutation in orbit_witnesses.items():
        image_active = active_rows(points, base_r, image_edges)
        image_gram = outside_gram(image_active)
        for left in range(len(points)):
            for right in range(len(points)):
                if (
                    image_gram[permutation[left]][permutation[right]]
                    != target_gram[left][right]
                ):
                    raise AssertionError("Gram transport is not orbit invariant")
        image_supports = enumerate_binary_supports(image_active, image_gram)
        transported_supports = {
            apply_permutation_to_mask(support, permutation)
            for support in target_support_set
        }
        if set(image_supports) != transported_supports:
            raise AssertionError("support enumeration is not orbit invariant")
        transported_weights = {
            edge(permutation[left], permutation[right]): coefficient
            for (left, right), coefficient in FARKAS_WEIGHTS.items()
        }
        image_value, image_scores = assert_farkas_separator(
            image_supports, image_gram, transported_weights
        )
        if image_value != target_value or image_scores != support_weights:
            raise AssertionError("Farkas certificate is not orbit invariant")

    return {
        "Z_empty": {
            "gram_rank": exact_rank(base_gram),
            "gram_nullity": 30 - exact_rank(base_gram),
            "support_count": len(base_supports),
            "support_sha256": mask_hash(base_supports),
            "support_weight_histogram": {
                str(key): value
                for key, value in sorted(
                    Counter(mask.bit_count() for mask in base_supports).items()
                )
            },
            **base_system,
        },
        "nonempty_Z": {
            "eligible_edge_count": len(zero_candidates),
            "eligible_edges_sha256": sha256_bytes(
                json.dumps(zero_candidates, separators=(",", ":")).encode()
            ),
            "subsets_size_one_through_three": subset_count,
            "entrywise_nonnegative_B": len(entrywise_valid),
            "stabilizer_order": len(group),
            "entrywise_orbit_count": len(orbit_counts),
            "exact_PSD_orbit_count": len(psd_rows),
            "inconsistent_Gram_orbits": inconsistent,
            "psd_orbits": psd_rows,
            "final_Farkas": {
                "z_edges": [list(item) for item in target_edges],
                "gram_rank": exact_rank(target_gram),
                "support_count": len(target_supports),
                "support_sha256": mask_hash(target_supports),
                "coefficient_rank": residual["coefficient_rank"],
                "weights": {
                    f"{left},{right}": value
                    for (left, right), value in sorted(FARKAS_WEIGHTS.items())
                },
                "target_weighted_sum": target_value,
                "support_weight_histogram": {
                    str(key): value
                    for key, value in sorted(support_weights.items())
                },
                "orbit_image_count": len(orbit_witnesses),
                "transported_certificate_checked": True,
                "sign_mutation_rejected": True,
                "index_mutation_rejected": True,
            },
        },
    }


def integer_partitions(total: int, minimum: int = 2) -> Iterator[tuple[int, ...]]:
    if total == 0:
        yield ()
        return
    for first in range(minimum, total + 1):
        for rest in integer_partitions(total - first, first):
            yield (first,) + rest


def q_profiles() -> tuple[tuple[int, ...], ...]:
    return tuple(
        profile
        for profile in integer_partitions(40)
        if profile
        and all(len(profile) - 1 - 3 * value >= 4 for value in profile)
    )


def labeled_cubic_graphs_order_six() -> dict[str, object]:
    all_edges = tuple(itertools.combinations(range(6), 2))
    k33 = 0
    prism = 0
    for selected in itertools.combinations(all_edges, 9):
        degrees = Counter(vertex for item in selected for vertex in item)
        if set(degrees.values()) != {3} or len(degrees) != 6:
            continue
        rows = [set() for _ in range(6)]
        for left, right in selected:
            rows[left].add(right)
            rows[right].add(left)
        triangles = sum(
            right in rows[left]
            and third in rows[left]
            and third in rows[right]
            for left, right, third in itertools.combinations(range(6), 3)
        )
        if triangles == 0:
            k33 += 1
        elif triangles == 2:
            prism += 1
        else:
            raise AssertionError("unexpected cubic order-six graph")
    if (k33, prism) != (10, 60):
        raise AssertionError("labeled cubic order-six census changed")
    # K3,3 grid: every different-row/different-column pair occurs twice.
    grid = tuple((row, column) for row in range(3) for column in range(3))
    coverage: Counter[tuple[tuple[int, int], tuple[int, int]]] = Counter()
    for row in range(3):
        for column in range(3):
            residual_row = tuple((row, other) for other in range(3) if other != column)
            residual_column = tuple((other, column) for other in range(3) if other != row)
            for left in residual_row:
                for right in residual_column:
                    coverage[tuple(sorted((left, right)))] += 1
    expected_pairs = {
        tuple(sorted((left, right)))
        for left, right in itertools.combinations(grid, 2)
        if left[0] != right[0] and left[1] != right[1]
    }
    if set(coverage) != expected_pairs or set(coverage.values()) != {2}:
        raise AssertionError("K3,3 grid coverage changed")
    return {
        "labeled_cubic_graph_count": k33 + prism,
        "labeled_K3,3_count": k33,
        "labeled_prism_count": prism,
        "prism_alpha_beta_coverage": 3,
        "K3,3_grid_pair_count": len(coverage),
        "K3,3_grid_pair_coverage": 2,
        "K3,3_remaining_L_neighbors_per_grid_label": 2,
        "K3,3_R_endpoint_appearances_per_grid_label": 4,
        "K3,3_forced_identical_R_neighbor_points": True,
    }


def structural_arithmetic() -> dict[str, object]:
    profiles = q_profiles()
    profile_rows = [
        {
            "r": len(profile),
            "q": list(profile),
            "d_K": [len(profile) - 1 - 3 * value for value in profile],
            "point_count_upper": 3 * len(profile) // 2,
        }
        for profile in profiles
    ]
    if len(profiles) != 13:
        raise AssertionError("n3=60 q-profile count changed")
    # Exact projector checks used at m=29 and to exclude z=4,5 at m=30.
    m29_e90_global_square_sum = 63 * (29 * 29 + 27 * 29 - 18 * 90)
    if m29_e90_global_square_sum != 252:
        raise AssertionError
    m29_e89_global_square_sum = 63 * (29 * 29 + 27 * 29 - 18 * 89)
    if m29_e89_global_square_sum != 1386:
        raise AssertionError
    # Outside y=t-3 would have sum 18 and square sum 14: impossible.
    if not 14 < 18:
        raise AssertionError
    # For z=4, S2(Z)+sum outside (t-3)^2=25, but terms are at least 8+25.
    if not 25 < 8 + 25:
        raise AssertionError
    return {
        "q_profile_count": len(profiles),
        "q_profiles": profile_rows,
        "r_at_most_17_profile_count": sum(len(profile) <= 17 for profile in profiles),
        "r18_profile_count": sum(len(profile) == 18 for profile in profiles),
        "r19_profile_count": sum(len(profile) == 19 for profile in profiles),
        "r20_profile_count": sum(len(profile) == 20 for profile in profiles),
        "m27": labeled_cubic_graphs_order_six(),
        "m28_point_profiles": ["2^25 3^2 4", "2^24 3^4"],
        "m29_point_profiles": ["2^28 4", "2^27 3^2"],
        "m29_e90_projector_square_sum": m29_e90_global_square_sum,
        "m29_e89_projector_square_sum": m29_e89_global_square_sum,
        "m29_e89_outside_y_sum": 18,
        "m29_e89_outside_y_square_sum": 14,
        "m30_Z_spectral_cap": 3,
        "m30_z4_required_sum": 25,
        "m30_z4_lower_bound": 33,
    }


def build_results(
    connected_disposition_path: Path,
    disconnected_disposition_path: Path,
) -> dict[str, object]:
    connected_records = fetch_catalog(20)
    connected, connected_disposition = connected_census(connected_records)
    connected_disposition_path.write_bytes(connected_disposition)
    print("connected order-20 census complete", flush=True)
    disconnected, disconnected_rows, petersen_l, petersen_f = disconnected_census()
    disconnected_rendered = (
        json.dumps(disconnected_rows, indent=2, sort_keys=True) + "\n"
    ).encode()
    disconnected_disposition_path.write_bytes(disconnected_rendered)
    print("disconnected order-20 census complete", flush=True)
    base_l, base_r, group, orbit = petersen_orbit_data(
        petersen_f, petersen_l
    )
    print("two-Petersen 120-model orbit complete", flush=True)
    zero = petersen_zero_census(petersen_f, base_l, base_r, group)
    print("corrected Z orbit and Gram census complete", flush=True)
    return {
        "schema_version": 1,
        "scope": (
            "conditional exact exclusion of n3=60 for a putative "
            "srg(99,14,1,2), pending independent semantic audit"
        ),
        "catalogs": {
            str(order): dict(metadata)
            for order, metadata in sorted(CATALOGS.items())
        },
        "catalog_completeness_boundary": (
            "pairwise nonisomorphism and completeness of the official "
            "House of Graphs connected cubic catalogs are external premises"
        ),
        "structural_arithmetic": structural_arithmetic(),
        "connected_order20": {
            **connected,
            "disposition_path": connected_disposition_path.as_posix(),
            "disposition_sha256": sha256_bytes(connected_disposition),
            "disposition_codes": {
                "T": "triangle found",
                "L": "no remote local C6 for at least one label",
                "S": "no symmetric L-neighborhood selection",
                "Z": "twenty forced zero-crossing edges exceed spectral cap three",
                "D": "a point has fewer than two compatible positive supports",
            },
        },
        "disconnected_order20": {
            **disconnected,
            "disposition_path": disconnected_disposition_path.as_posix(),
            "disposition_sha256": sha256_bytes(disconnected_rendered),
        },
        "two_Petersen": {
            **orbit,
            "base_L_rows": list(base_l),
            "base_R_edges": [list(item) for item in sorted(base_r)],
            "base_R_sha256": sha256_bytes(
                json.dumps(sorted(base_r), separators=(",", ":")).encode()
            ),
            **zero,
        },
        "conditional_n3_60": "EXCLUDED_DERIVED_PENDING_INDEPENDENT_AUDIT",
        "prospective_conditional_n3_lower_bound": 63,
        "prospective_conditional_induced_C6_lower_bound": 209_349,
        "conway_99": "UNKNOWN",
        "novelty": "UNKNOWN",
        "limitations": [
            "imports the frozen audited H/L, indexed-point, crossing, fixed-point, and dense-subset semantics",
            "this discovery lane cannot promote its own claim to VERIFIED",
            "official catalog completeness/nonisomorphism is an external premise",
            "no completed 99-vertex graph, automorphism, or target existence conclusion is assumed",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--connected-dispositions", required=True, type=Path)
    parser.add_argument("--disconnected-dispositions", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_results(
        args.connected_dispositions,
        args.disconnected_dispositions,
    )
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.verify is not None:
        observed = args.verify.read_text(encoding="utf-8")
        if observed != rendered:
            raise AssertionError("exact results differ from replay")
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    if args.output is None and args.verify is None:
        print(rendered, end="")


if __name__ == "__main__":
    main()
