"""Independent exact reconstruction of sealed Wave133 controls.

No Wave133 implementation is imported.  This verifier rebuilds the local
triangle stars, voltage cover, balanced quotient, link normalization, Euler
data, and certificate hashes from the sealed constants with standard-library
integer arithmetic.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Iterable


EXPECTED_MANIFEST = (
    "dae34acdfd3a95c99db79567bf9b8ed20aa1423812dcb4dbe7681730b6d9870a"
)
FIBRE = 12
TRIANGLES = 231
SHEETS = 693
EDGES = 4158
FACES = 2079


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_hash(value: object) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(raw).hexdigest()


def bind_hash_list(
    repository: Path, list_path: Path, expected_list_hash: str | None
) -> dict[str, object]:
    failures: list[str] = []
    entries = 0
    for line in list_path.read_text(encoding="utf-8").splitlines():
        entries += 1
        try:
            expected, relative = line.split("  ", 1)
        except ValueError:
            failures.append(f"malformed:{line}")
            continue
        target = repository / Path(relative)
        if not target.is_file():
            failures.append(f"missing:{relative}")
        elif file_hash(target) != expected:
            failures.append(f"hash:{relative}")
    actual = file_hash(list_path)
    return {
        "entries": entries,
        "expected_sha256": expected_list_hash,
        "actual_sha256": actual,
        "failures": failures,
        "verified": (
            not failures
            and (
                expected_list_hash is None
                or actual == expected_list_hash
            )
        ),
    }


def connect(graph: list[set[int]], left: int, right: int) -> None:
    if left == right or right in graph[left]:
        raise ValueError("loop or repeated edge")
    graph[left].add(right)
    graph[right].add(left)


def standard_factor(round_index: int) -> tuple[tuple[int, int], ...]:
    pairs = [(FIBRE - 1, round_index)]
    for offset in range(1, FIBRE // 2):
        pairs.append(
            (
                (round_index + offset) % (FIBRE - 1),
                (round_index - offset) % (FIBRE - 1),
            )
        )
    return tuple(sorted(tuple(sorted(pair)) for pair in pairs))


FACTORS = tuple(
    standard_factor(index) for index in range(FIBRE - 1)
)


def factor_map(factor: tuple[tuple[int, int], ...]) -> tuple[int, ...]:
    result = [-1] * FIBRE
    for left, right in factor:
        result[left] = right
        result[right] = left
    if sorted(result) != list(range(FIBRE)):
        raise ValueError("not a perfect matching")
    return tuple(result)


def cycles(permutation: tuple[int, ...]) -> list[list[int]]:
    unseen = set(range(len(permutation)))
    result = []
    while unseen:
        start = min(unseen)
        orbit = []
        current = start
        while current in unseen:
            unseen.remove(current)
            orbit.append(current)
            current = permutation[current]
        if current != start:
            raise ValueError("bad permutation orbit")
        result.append(orbit)
    return result


def permutation_sign(permutation: tuple[int, ...]) -> int:
    inversions = sum(
        permutation[left] > permutation[right]
        for left in range(len(permutation))
        for right in range(left + 1, len(permutation))
    )
    return -1 if inversions % 2 else 1


def count_triangles(graph: list[set[int]]) -> int:
    return sum(
        1
        for left in range(len(graph))
        for middle in graph[left]
        if left < middle
        for right in graph[left] & graph[middle]
        if middle < right
    )


def local_control(
    name: str, holonomy: tuple[int, ...]
) -> dict[str, object]:
    core = [set() for _ in range(36)]
    for fibre, factor_index in enumerate((1, 2, 3)):
        for left, right in FACTORS[factor_index]:
            connect(
                core,
                fibre * FIBRE + left,
                fibre * FIBRE + right,
            )
    for label in range(FIBRE):
        connect(core, label, FIBRE + label)
        connect(core, FIBRE + label, 2 * FIBRE + label)
        connect(core, 2 * FIBRE + label, holonomy[label])

    star = [set() for _ in range(39)]
    connect(star, 0, 1)
    connect(star, 1, 2)
    connect(star, 2, 0)
    for fibre in range(3):
        for label in range(FIBRE):
            connect(star, fibre, 3 + fibre * FIBRE + label)
    for left in range(36):
        for right in core[left]:
            if left < right:
                connect(star, 3 + left, 3 + right)

    histogram: Counter[tuple[int, int]] = Counter()
    adjacent_cap = 0
    nonadjacent_cap = 0
    for left in range(39):
        for right in range(left + 1, 39):
            common = len(star[left] & star[right])
            adjacent = int(right in star[left])
            histogram[(adjacent, common)] += 1
            if adjacent:
                adjacent_cap = max(adjacent_cap, common)
            else:
                nonadjacent_cap = max(nonadjacent_cap, common)

    gram = []
    for left in range(36):
        row = []
        for right in range(36):
            row.append(
                (12 if left == right else 0)
                - int(right in core[left])
                + 2
                - int(left // FIBRE == right // FIBRE)
                - len(core[left] & core[right])
            )
        gram.append(row)
    orbit_list = cycles(holonomy)
    return {
        "name": name,
        "holonomy": list(holonomy),
        "holonomy_cycle_type": sorted(
            len(orbit) for orbit in orbit_list
        ),
        "holonomy_cycle_count": len(orbit_list),
        "holonomy_fixed_points": sum(
            holonomy[index] == index for index in range(FIBRE)
        ),
        "holonomy_sign": permutation_sign(holonomy),
        "cross_two_factor_cycle_type": sorted(
            3 * len(orbit) for orbit in orbit_list
        ),
        "within_fibre_factor_indices": [1, 2, 3],
        "core_vertices": 36,
        "core_degree": min(map(len, core)),
        "core_edges": sum(map(len, core)) // 2,
        "core_triangle_count": count_triangles(core),
        "partial_star_vertices": 39,
        "partial_star_degree_sequence": sorted(map(len, star)),
        "partial_star_common_neighbor_cap_adjacent": adjacent_cap,
        "partial_star_common_neighbor_cap_nonadjacent": nonadjacent_cap,
        "partial_star_common_neighbor_histogram": {
            f"adjacent_{adjacent}_common_{common}": count
            for (adjacent, common), count in sorted(
                histogram.items()
            )
        },
        "forced_gram_entry_range": [
            min(min(row) for row in gram),
            max(max(row) for row in gram),
        ],
        "certificate_sha256": json_hash(
            {
                "holonomy": list(holonomy),
                "core": [sorted(neighbors) for neighbors in core],
            }
        ),
    }


Group = tuple[int, int, int]
IDENTITY: Group = (0, 0, 0)


def multiply(left: Group, right: Group) -> Group:
    a, b, c = left
    d, e, f = right
    return (
        (a + pow(2, b, 7) * d) % 7,
        (b + e) % 3,
        (c + f) % 33,
    )


def invert(value: Group) -> Group:
    a, b, c = value
    ib = (-b) % 3
    return (
        (-pow(2, ib, 7) * a) % 7,
        ib,
        (-c) % 33,
    )


GROUP = tuple(
    (a, b, c)
    for a in range(7)
    for b in range(3)
    for c in range(33)
)
GROUP_INDEX = {value: index for index, value in enumerate(GROUP)}


def generated(generators: Iterable[Group]) -> set[Group]:
    moves = tuple(generators)
    moves += tuple(invert(value) for value in moves)
    seen = {IDENTITY}
    queue = deque([IDENTITY])
    while queue:
        current = queue.popleft()
        for move in moves:
            nxt = multiply(current, move)
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def base_and_cover(
    pairs: tuple[tuple[int, int], ...],
    twists: tuple[int, ...],
    voltages: tuple[Group, ...],
) -> dict[str, object]:
    # Build links of the quotient vertices directly from face corners and
    # glued side endpoints.
    half_links = [set() for _ in range(24)]
    for face in range(3):
        for position in range(4):
            side = 4 * face + position
            previous = 4 * face + (position - 1) % 4
            connect(half_links, 2 * side, 2 * previous + 1)

    occurrence: dict[int, tuple[int, int]] = {}
    for edge, ((left, right), twist) in enumerate(
        zip(pairs, twists, strict=True)
    ):
        occurrence[left] = (edge, 1)
        occurrence[right] = (edge, 1 if twist else -1)
        endpoint_pairs = (
            ((0, 0), (1, 1))
            if twist
            else ((0, 1), (1, 0))
        )
        for left_end, right_end in endpoint_pairs:
            connect(
                half_links,
                2 * left + left_end,
                2 * right + right_end,
            )

    component = [-1] * 24
    components: list[list[int]] = []
    for start in range(24):
        if component[start] >= 0:
            continue
        label = len(components)
        stack = [start]
        nodes = []
        while stack:
            current = stack.pop()
            if component[current] >= 0:
                continue
            component[current] = label
            nodes.append(current)
            stack.extend(half_links[current])
        components.append(sorted(nodes))
    if sorted(len(nodes) // 2 for nodes in components) != [6, 6]:
        raise ValueError("base vertex links changed")

    face_words = [
        [occurrence[4 * face + position] for position in range(4)]
        for face in range(3)
    ]
    for word in face_words:
        product = IDENTITY
        for edge, sign in word:
            product = multiply(
                product,
                voltages[edge]
                if sign == 1
                else invert(voltages[edge]),
            )
        if product != IDENTITY:
            raise ValueError("face voltage does not close")

    orientations = [
        (component[2 * left], component[2 * left + 1])
        for left, _right in pairs
    ]
    normalized = tuple(
        voltage
        if orientation == (0, 1)
        else invert(voltage)
        for voltage, orientation in zip(
            voltages, orientations, strict=True
        )
    )
    differences = [
        multiply(invert(normalized[0]), value)
        for value in normalized[1:]
    ]
    subgroup_order = len(generated(differences))

    cover_edges = []
    for sheet_index, sheet in enumerate(GROUP):
        for voltage in normalized:
            target = GROUP_INDEX[multiply(sheet, voltage)]
            cover_edges.append((sheet_index, SHEETS + target))
    cover_edge_index = {
        tuple(sorted(edge)): index
        for index, edge in enumerate(cover_edges)
    }
    cover_faces = []
    for face in range(3):
        first_side = 4 * face
        for initial_sheet in GROUP:
            sheet = initial_sheet
            boundary = []
            for position in range(4):
                side = 4 * face + position
                base_vertex = component[2 * side]
                boundary.append(
                    base_vertex * SHEETS + GROUP_INDEX[sheet]
                )
                edge, sign = occurrence[side]
                sheet = multiply(
                    sheet,
                    voltages[edge]
                    if sign == 1
                    else invert(voltages[edge]),
                )
            if sheet != initial_sheet or len(set(boundary)) != 4:
                raise ValueError("bad lifted face")
            cover_faces.append(tuple(boundary))

    edge_multiplicity = [0] * len(cover_edges)
    cover_face_edges = []
    for boundary in cover_faces:
        ids = []
        for position in range(4):
            pair = tuple(
                sorted(
                    (
                        boundary[position],
                        boundary[(position + 1) % 4],
                    )
                )
            )
            ids.append(cover_edge_index[pair])
            edge_multiplicity[cover_edge_index[pair]] += 1
        cover_face_edges.append(tuple(ids))

    adjacency = [set() for _ in range(2 * SHEETS)]
    for left, right in cover_edges:
        connect(adjacency, left, right)
    seen = {0}
    queue = deque([0])
    while queue:
        current = queue.popleft()
        for neighbor in adjacency[current]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)

    incident_edges = [set() for _ in range(2 * SHEETS)]
    links: list[dict[int, set[int]]] = [
        defaultdict(set) for _ in range(2 * SHEETS)
    ]
    for edge, (left, right) in enumerate(cover_edges):
        incident_edges[left].add(edge)
        incident_edges[right].add(edge)
    for boundary, edge_ids in zip(
        cover_faces, cover_face_edges, strict=True
    ):
        for position, vertex in enumerate(boundary):
            previous = edge_ids[(position - 1) % 4]
            following = edge_ids[position]
            links[vertex][previous].add(following)
            links[vertex][following].add(previous)
    link_types = []
    for vertex in range(2 * SHEETS):
        unseen = set(links[vertex])
        lengths = []
        while unseen:
            start = min(unseen)
            stack = [start]
            found = set()
            while stack:
                current = stack.pop()
                if current in found:
                    continue
                found.add(current)
                stack.extend(links[vertex][current])
            unseen -= found
            lengths.append(len(found))
        link_types.append(sorted(lengths))

    return {
        "base_components": components,
        "base_component": component,
        "base_occurrence": occurrence,
        "base_orientations": orientations,
        "normalized": normalized,
        "subgroup_order": subgroup_order,
        "edges": cover_edges,
        "faces": cover_faces,
        "cover_face_edges": cover_face_edges,
        "edge_multiplicity": edge_multiplicity,
        "cover_adjacency": adjacency,
        "cover_connected_vertices": len(seen),
        "cover_link_types": link_types,
    }


def qpair(left: int, right: int) -> tuple[int, int]:
    return (left, right) if left <= right else (right, left)


def collision_cost(pair: tuple[int, int], multiplicity: int) -> int:
    if pair[0] == pair[1]:
        return multiplicity
    return max(0, multiplicity - 1)


def balanced_partition(
    edges: list[tuple[int, int]],
) -> tuple[list[int], int]:
    rng = random.Random(133)
    labels = [
        group for group in range(TRIANGLES) for _ in range(6)
    ]
    rng.shuffle(labels)
    incident = [[] for _ in range(2 * SHEETS)]
    for edge, (left, right) in enumerate(edges):
        incident[left].append(edge)
        incident[right].append(edge)

    multiplicities: Counter[tuple[int, int]] = Counter()
    buckets: defaultdict[tuple[int, int], set[int]] = defaultdict(set)
    for edge, (left, right) in enumerate(edges):
        pair = qpair(labels[left], labels[right])
        multiplicities[pair] += 1
        buckets[pair].add(edge)
    cost = sum(
        collision_cost(pair, count)
        for pair, count in multiplicities.items()
    )
    bad = {
        pair
        for pair, count in multiplicities.items()
        if collision_cost(pair, count)
    }

    for iteration in range(100_000):
        if cost == 0:
            return labels, iteration
        bad_pair = rng.choice(sorted(bad))
        edge = rng.choice(sorted(buckets[bad_pair]))
        endpoints = edges[edge]
        first = rng.choice(endpoints)
        second = rng.randrange(2 * SHEETS)
        if labels[first] == labels[second]:
            continue
        affected = set(incident[first]) | set(incident[second])
        old_pairs = {
            item: qpair(
                labels[edges[item][0]], labels[edges[item][1]]
            )
            for item in affected
        }
        old_first, old_second = labels[first], labels[second]
        labels[first], labels[second] = old_second, old_first
        new_pairs = {
            item: qpair(
                labels[edges[item][0]], labels[edges[item][1]]
            )
            for item in affected
        }
        touched = set(old_pairs.values()) | set(new_pairs.values())
        old_counts = {
            pair: multiplicities.get(pair, 0) for pair in touched
        }
        for item in affected:
            old_pair = old_pairs[item]
            new_pair = new_pairs[item]
            if old_pair == new_pair:
                continue
            multiplicities[old_pair] -= 1
            buckets[old_pair].remove(item)
            multiplicities[new_pair] += 1
            buckets[new_pair].add(item)
        delta = sum(
            collision_cost(pair, multiplicities[pair])
            - collision_cost(pair, old_counts[pair])
            for pair in touched
        )
        temperature = max(
            0.01, 0.8 * (1 - iteration / 5_000_000)
        )
        accept = (
            delta <= 0
            or rng.random() < math.exp(-delta / temperature)
        )
        if accept:
            cost += delta
            for pair in touched:
                if collision_cost(pair, multiplicities[pair]):
                    bad.add(pair)
                else:
                    bad.discard(pair)
        else:
            labels[first], labels[second] = old_first, old_second
            for item in affected:
                old_pair = old_pairs[item]
                new_pair = new_pairs[item]
                if old_pair == new_pair:
                    continue
                multiplicities[new_pair] -= 1
                buckets[new_pair].remove(item)
                multiplicities[old_pair] += 1
                buckets[old_pair].add(item)
    raise RuntimeError("balanced partition did not finish")


def quotient_control(
    cover: dict[str, object],
) -> dict[str, object]:
    edges: list[tuple[int, int]] = cover["edges"]
    faces: list[tuple[int, int, int, int]] = cover["faces"]
    labels, iterations = balanced_partition(edges)
    quotient_edges = [
        qpair(labels[left], labels[right])
        for left, right in edges
    ]
    adjacency = [set() for _ in range(TRIANGLES)]
    for left, right in quotient_edges:
        connect(adjacency, left, right)
    quotient_faces = [
        tuple(labels[vertex] for vertex in face)
        for face in faces
    ]
    edge_index = {
        edge: index
        for index, edge in enumerate(sorted(set(quotient_edges)))
    }
    edge_multiplicity = [0] * EDGES
    links: list[dict[int, set[int]]] = [
        defaultdict(set) for _ in range(TRIANGLES)
    ]
    for boundary in quotient_faces:
        ids = []
        for position in range(4):
            pair = qpair(
                boundary[position],
                boundary[(position + 1) % 4],
            )
            edge = edge_index[pair]
            ids.append(edge)
            edge_multiplicity[edge] += 1
        for position, vertex in enumerate(boundary):
            previous = ids[(position - 1) % 4]
            following = ids[position]
            links[vertex][previous].add(following)
            links[vertex][following].add(previous)

    link_components: list[list[set[int]]] = []
    link_types = []
    for vertex in range(TRIANGLES):
        unseen = set(links[vertex])
        components = []
        while unseen:
            start = min(unseen)
            stack = [start]
            found = set()
            while stack:
                current = stack.pop()
                if current in found:
                    continue
                found.add(current)
                stack.extend(links[vertex][current])
            unseen -= found
            components.append(found)
        link_components.append(components)
        link_types.append(sorted(map(len, components)))

    # Check connectivity after normalizing every disconnected vertex link.
    split_index: dict[tuple[int, int], int] = {}
    edge_to_split: dict[tuple[int, int], int] = {}
    for vertex, components in enumerate(link_components):
        for component_index, component in enumerate(components):
            split = len(split_index)
            split_index[(vertex, component_index)] = split
            for edge in component:
                edge_to_split[(vertex, edge)] = split
    split_graph = [set() for _ in range(len(split_index))]
    for edge, (left, right) in enumerate(
        sorted(set(quotient_edges))
    ):
        split_left = edge_to_split[(left, edge)]
        split_right = edge_to_split[(right, edge)]
        connect(split_graph, split_left, split_right)
    normalized_component_sizes = []
    unseen_split = set(range(len(split_graph)))
    while unseen_split:
        start = min(unseen_split)
        stack = [start]
        found = set()
        while stack:
            current = stack.pop()
            if current in found:
                continue
            found.add(current)
            stack.extend(split_graph[current])
        unseen_split -= found
        normalized_component_sizes.append(len(found))

    h_total = sum(len(value) for value in link_components)
    euler = h_total - EDGES + FACES
    product_sign = math.prod(
        (-1) ** len(value) for value in link_components
    )
    return {
        "partition_seed": 133,
        "partition_acceptance_iteration": iterations,
        "partition_sha256": json_hash(labels),
        "split_surface_vertices": h_total,
        "quotient_vertices": TRIANGLES,
        "quotient_edges": len(quotient_edges),
        "quotient_degree": min(map(len, adjacency)),
        "quotient_simple": (
            all(left != right for left, right in quotient_edges)
            and len(set(quotient_edges)) == len(quotient_edges)
        ),
        "quadrilateral_faces": len(quotient_faces),
        "distinct_quadrilateral_faces": (
            len(set(quotient_faces)) == len(quotient_faces)
            and all(len(set(face)) == 4 for face in quotient_faces)
        ),
        "edge_face_multiplicity_values": sorted(
            set(edge_multiplicity)
        ),
        "link_cycle_types_all": link_types,
        "link_component_total_H": h_total,
        "global_holonomy_sign_product": product_sign,
        "euler_characteristic": euler,
        "normalized_surface_component_count": len(
            normalized_component_sizes
        ),
        "normalized_surface_component_vertex_counts": sorted(
            normalized_component_sizes
        ),
        "quotient_certificate_sha256": json_hash(
            {
                "labels": labels,
                "edges": quotient_edges,
                "faces": quotient_faces,
            }
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument(
        "--package",
        type=Path,
        default=Path(
            "attempts/wave133-triangle-holonomy-topology"
        ),
    )
    parser.add_argument(
        "--expected-manifest", default=EXPECTED_MANIFEST
    )
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    repository = args.repository.resolve()
    package = (
        args.package
        if args.package.is_absolute()
        else repository / args.package
    ).resolve()
    sealed = json.loads(
        (package / "exact-results.json").read_text(encoding="utf-8")
    )
    manifest = bind_hash_list(
        repository,
        package / "package-manifest.sha256",
        args.expected_manifest,
    )
    inputs = bind_hash_list(
        repository, package / "input-freeze.sha256", None
    )

    positive_h = factor_map(FACTORS[0])
    negative_h = tuple(range(1, FIBRE)) + (0,)
    local = [
        local_control("positive_six_transpositions", positive_h),
        local_control("negative_twelve_cycle", negative_h),
    ]
    local_match = (
        local == sealed["local_opposite_sign_controls"]
    )

    base_data = sealed["topological_twist_control"][
        "base_surface"
    ]
    pairs = tuple(
        tuple(value) for value in base_data["side_pairings"]
    )
    twists = tuple(base_data["twist_bits"])
    voltages = tuple(
        tuple(value) for value in base_data["voltages"]
    )
    cover = base_and_cover(pairs, twists, voltages)
    quotient = quotient_control(cover)
    published_q = sealed["topological_twist_control"][
        "balanced_quotient"
    ]
    quotient_checks = {
        "partition_acceptance_iteration": (
            quotient["partition_acceptance_iteration"]
            == published_q["partition_acceptance_iteration"]
        ),
        "partition_sha256": (
            quotient["partition_sha256"]
            == published_q["partition_sha256"]
        ),
        "quotient_certificate_sha256": (
            quotient["quotient_certificate_sha256"]
            == published_q["quotient_certificate_sha256"]
        ),
        "simple_36_regular": (
            quotient["quotient_simple"]
            and quotient["quotient_degree"] == 36
            and quotient["quotient_edges"] == EDGES
        ),
        "faces": (
            quotient["quadrilateral_faces"] == FACES
            and quotient["distinct_quadrilateral_faces"]
            and quotient["edge_face_multiplicity_values"] == [2]
        ),
        "links": all(
            value == [6] * 6
            for value in quotient["link_cycle_types_all"]
        ),
        "euler_sign": (
            quotient["link_component_total_H"] == 1386
            and quotient["euler_characteristic"] == -693
            and quotient["global_holonomy_sign_product"] == 1
            and quotient["global_holonomy_sign_product"]
            == (-1)
            ** (
                quotient["euler_characteristic"]
                + EDGES
                - FACES
            )
        ),
    }
    cover_checks = {
        "base_two_vertices_six_edges_three_faces": (
            len(cover["base_components"]) == 2
            and sorted(
                len(value) // 2
                for value in cover["base_components"]
            )
            == [6, 6]
            and len(pairs) == 6
        ),
        "voltages_generate_full_cover": (
            cover["subgroup_order"] == SHEETS
        ),
        "cover_counts": (
            len(cover["edges"]) == EDGES
            and len(set(cover["edges"])) == EDGES
            and len(cover["faces"]) == FACES
        ),
        "two_faces_per_edge": (
            set(cover["edge_multiplicity"]) == {2}
        ),
        "connected": (
            cover["cover_connected_vertices"] == 2 * SHEETS
        ),
        "six_regular": all(
            len(neighbors) == 6
            for neighbors in cover["cover_adjacency"]
        ),
        "one_C6_link": all(
            value == [6] for value in cover["cover_link_types"]
        ),
    }

    holonomy_identity = {
        "even_degree_sign_formula": all(
            value["holonomy_sign"]
            == (-1) ** value["holonomy_cycle_count"]
            for value in local
        ),
        "both_derangement_signs_realized": (
            {value["holonomy_sign"] for value in local}
            == {-1, 1}
            and all(
                value["holonomy_fixed_points"] == 0
                for value in local
            )
        ),
        "cross_cycle_lengths_are_three_times_holonomy": all(
            value["cross_two_factor_cycle_type"]
            == [
                3 * length
                for length in value["holonomy_cycle_type"]
            ]
            for value in local
        ),
        "global_identity": quotient_checks["euler_sign"],
        "orientable_all_222_would_force_minus_one": (
            (-1) ** (0 + EDGES - FACES) == -1
        ),
    }
    verified = all(
        (
            manifest["verified"],
            inputs["verified"],
            local_match,
            all(cover_checks.values()),
            all(quotient_checks.values()),
            all(holonomy_identity.values()),
        )
    )
    correction = None
    if quotient["normalized_surface_component_count"] != 1:
        correction = (
            "The normalized surface is disconnected; odd total Euler "
            "characteristic proves at least one nonorientable component, "
            "not connectedness."
        )
    result = {
        "format": "wave133-independent-verification-v1",
        "role": "verifier",
        "classification": (
            "VERIFIED_WITH_SCOPE_CORRECTION"
            if verified and correction
            else "VERIFIED"
            if verified
            else "REFUTED_OR_UNVERIFIED"
        ),
        "manifest": manifest,
        "input_freeze": inputs,
        "local_controls": {
            "reconstructed": local,
            "exactly_match_sealed_records": local_match,
        },
        "cover_checks": cover_checks,
        "quotient_checks": quotient_checks,
        "quotient_reconstruction": quotient,
        "holonomy_identity": holonomy_identity,
        "scope_correction": correction,
        "promoted_claims": {
            "rooted_triangle_holonomy_identities": (
                "VERIFIED"
                if all(holonomy_identity.values())
                else "REFUTED"
            ),
            "opposite_sign_local_controls": (
                "VERIFIED" if local_match else "REFUTED"
            ),
            "endpoint_scale_surface_relaxation_control": (
                "VERIFIED"
                if all(cover_checks.values())
                and all(quotient_checks.values())
                else "REFUTED"
            ),
        },
        "unchanged_unknowns": {
            "endpoint_excluded": False,
            "upper_bound_improved": False,
            "target_status": "UNKNOWN",
            "Conway_99": "UNKNOWN",
        },
        "independence": {
            "discovery_module_imported": False,
            "solver_used": False,
            "construction_rebuilt_from_sealed_constants": True,
        },
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.write.write_text(text, encoding="utf-8", newline="\n")
    else:
        print(text, end="")
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
