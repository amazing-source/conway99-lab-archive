#!/usr/bin/env python3
"""Generate the independent rooted-flower replay for the n3=39 proof.

The replay begins after the human reduction to thirteen active triangles.  It
uses ordered roots and ordered petal slots, deliberately retaining symmetry
duplicates.  The emitted certificate stores hashes of canonical JSONL streams;
the streams can optionally be dumped, but are cheap enough to regenerate.

This is regression evidence for a conditional proof.  It is not a standalone
certificate for nonexistence of ``srg(99,14,1,2)``.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable, Iterator, Sequence


ACTIVE_ORDER = 13
K_DEGREE = 6
STREAM_ORDER = (
    "premises.jsonl",
    "crossing_matrices.jsonl",
    "collision_pairs.jsonl",
    "size_bounds.jsonl",
    "degree_table.jsonl",
    "owner_motifs.jsonl",
    "root4_profiles.jsonl",
    "root3_profiles.jsonl",
    "parity.jsonl",
)
PREMISES = (
    "active_triangle_count=13",
    "K_is_simple_complement_of_L_on_distinct_active_triangles",
    "K_is_6_regular",
    "each_active_triangle_has_exactly_three_point_sets",
    "active_point_sets_have_size_at_least_two",
    "every_active_point_set_is_a_clique_in_K",
    "point_hypergraph_is_linear",
    "common_point_Berge_triangle_is_forbidden",
    "every_labeled_crossing_degree_is_zero_or_two",
)


def canonical_line(record: object) -> bytes:
    return (
        json.dumps(record, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        .encode("utf-8")
        + b"\n"
    )


def premise_records() -> Iterator[dict[str, object]]:
    """Bind the proof boundary into the same digest as every replay record."""

    yield {
        "claim_label": "UNKNOWN",
        "kind": "premises",
        "premises": list(PREMISES),
        "schema": "conditional-n3-39-local-replay-v1",
        "scope": "conditional_n3_39_active_triangle_replay",
    }


def crossing_degrees(left: int, right: int, mask: int) -> tuple[list[int], list[int]]:
    rows = [0] * left
    columns = [0] * right
    for row in range(left):
        for column in range(right):
            if mask >> (row * right + column) & 1:
                rows[row] += 1
                columns[column] += 1
    return rows, columns


def accepted_crossing_masks(left: int, right: int) -> tuple[int, ...]:
    accepted = []
    for mask in range(1 << (left * right)):
        rows, columns = crossing_degrees(left, right, mask)
        if all(value in (0, 2) for value in (*rows, *columns)):
            accepted.append(mask)
    return tuple(accepted)


def crossing_records() -> Iterator[dict[str, object]]:
    for left in range(1, 4):
        for right in range(1, 4):
            for mask in range(1 << (left * right)):
                rows, columns = crossing_degrees(left, right, mask)
                allowed = all(value in (0, 2) for value in (*rows, *columns))
                yield {
                    "allowed": allowed,
                    "col_degrees": columns,
                    "kind": "crossing",
                    "left_size": left,
                    "mask": mask,
                    "reason": "all_degrees_zero_or_two" if allowed else "forbidden_degree",
                    "right_size": right,
                    "row_degrees": rows,
                }


def collision_records() -> Iterator[dict[str, object]]:
    for root_size in range(2, ACTIVE_ORDER + 1):
        for left, right in itertools.combinations(range(2 * root_size), 2):
            occurrences = (left // 2, right // 2)
            rejection = "linearity" if occurrences[0] == occurrences[1] else "common_point"
            yield {
                "kind": "collision",
                "petal_slots": [left, right],
                "rejection": rejection,
                "root_occurrences": list(occurrences),
                "root_size": root_size,
            }


def bound_records() -> Iterator[dict[str, object]]:
    for root_size in range(2, ACTIVE_ORDER + 1):
        available = ACTIVE_ORDER - root_size
        required = 2 * root_size
        survives = required <= available
        yield {
            "available_outside": available,
            "kind": "bound",
            "rejection": None if survives else "external_capacity",
            "required_representatives": required,
            "root_size": root_size,
            "survives": survives,
        }


def degree_records() -> Iterator[dict[str, object]]:
    for size_three_points in range(4):
        size_two_points = 3 - size_three_points
        f_degree = size_two_points + 2 * size_three_points
        yield {
            "f_degree": f_degree,
            "k_degree": K_DEGREE,
            "kind": "degree",
            "size2_points": size_two_points,
            "size3_points": size_three_points,
            "u_degree": K_DEGREE - f_degree,
        }


def owner_records() -> Iterator[dict[str, object]]:
    for left_size in range(2, 5):
        for right_size in range(2, 5):
            for left_index in range(left_size - 1):
                for right_index in range(right_size - 1):
                    left_point = frozenset((0, *range(1, left_size)))
                    right_point = frozenset(
                        (0, *range(left_size, left_size + right_size - 1))
                    )
                    left_external = sorted(left_point - {0})[left_index]
                    right_external = sorted(right_point - {0})[right_index]
                    attempted_owner = frozenset((left_external, right_external))
                    intersections = (
                        left_point & right_point,
                        left_point & attempted_owner,
                        right_point & attempted_owner,
                    )
                    forbidden = (
                        all(len(value) == 1 for value in intersections)
                        and len(set().union(*intersections)) == 3
                    )
                    if not forbidden:
                        raise AssertionError("a forced cross-edge acquired a legal F-owner")
                    yield {
                        "kind": "owner",
                        "left_external_index": left_index,
                        "left_point_size": left_size,
                        "rejection": "common_point",
                        "right_external_index": right_index,
                        "right_point_size": right_size,
                    }


def edge(left: int, right: int) -> tuple[int, int]:
    if left == right:
        raise ValueError("loops are not edges")
    return (left, right) if left < right else (right, left)


def clique_edges(vertices: Iterable[int]) -> set[tuple[int, int]]:
    return {edge(left, right) for left, right in itertools.combinations(sorted(vertices), 2)}


def explicit_flower(
    root_size: int, petals: Sequence[int]
) -> tuple[
    frozenset[int],
    tuple[tuple[frozenset[int], frozenset[int]], ...],
    set[tuple[int, int]],
    set[tuple[int, int]],
]:
    """Construct canonical point sets and all singleton-forced K-edges.

    External parts are assigned disjoint labels in slot order.  ``F`` is the
    union of point-clique edges.  ``mandatory_k`` adds every cross-pair whose
    labeled L-crossing has a singleton side and is therefore empty.  This is
    an explicit local construction, not the degree formulas used in the
    compact checker.
    """

    if len(petals) != 2 * root_size:
        raise ValueError("a rooted flower has two petals at each occurrence")
    root = frozenset(range(root_size))
    next_vertex = root_size
    occurrences = []
    point_sets: list[frozenset[int]] = [root]
    for occurrence in range(root_size):
        pair = []
        for petal_size in petals[2 * occurrence : 2 * occurrence + 2]:
            external = tuple(range(next_vertex, next_vertex + petal_size - 1))
            next_vertex += petal_size - 1
            point = frozenset((occurrence, *external))
            pair.append(point)
            point_sets.append(point)
        occurrences.append((pair[0], pair[1]))
    if next_vertex > ACTIVE_ORDER:
        raise ValueError("flower exceeds the active vertex budget")

    f_edges: set[tuple[int, int]] = set()
    for point in point_sets:
        f_edges.update(clique_edges(point))
    mandatory_k = set(f_edges)
    for occurrence, petals_at_root in enumerate(occurrences):
        local_points = (root, *petals_at_root)
        for left_point, right_point in itertools.combinations(local_points, 2):
            left_external = left_point - {occurrence}
            right_external = right_point - {occurrence}
            if min(len(left_external), len(right_external)) != 1:
                continue
            if accepted_crossing_masks(len(left_external), len(right_external)) != (0,):
                raise AssertionError("singleton-side crossing was not uniquely empty")
            mandatory_k.update(
                edge(left, right)
                for left in left_external
                for right in right_external
            )
    return root, tuple(occurrences), f_edges, mandatory_k


def degrees(vertices: Iterable[int], edges: Iterable[tuple[int, int]]) -> dict[int, int]:
    output = {vertex: 0 for vertex in vertices}
    for left, right in edges:
        if left in output:
            output[left] += 1
        if right in output:
            output[right] += 1
    return output


def flower_crossing_extensions(root_size: int, petals: Sequence[int]) -> int:
    count = 1
    for offset in range(0, len(petals), 2):
        left = petals[offset] - 1
        right = petals[offset + 1] - 1
        count *= len(accepted_crossing_masks(root_size - 1, left))
        count *= len(accepted_crossing_masks(root_size - 1, right))
        count *= len(accepted_crossing_masks(left, right))
    return count


def root4_records(outside_budget: int = 9) -> Iterator[dict[str, object]]:
    for petals in itertools.product((2, 3, 4), repeat=8):
        external_slots = sum(size - 1 for size in petals)
        type_224 = [
            occurrence
            for occurrence in range(4)
            if petals[2 * occurrence] == petals[2 * occurrence + 1] == 2
        ]
        if external_slots > outside_budget:
            yield {
                "capacity": outside_budget,
                "chosen_224": [],
                "crossing_extensions": 0,
                "external_slots": external_slots,
                "kind": "root4",
                "petal_sizes": list(petals),
                "rejection": "external_capacity",
                "root_degree_lower": None,
                "root_size": 4,
                "type224_occurrences": type_224,
            }
            continue
        chosen = type_224[:2]
        root, _occurrences, _f_edges, mandatory_k = explicit_flower(4, petals)
        root_degree_lower = min(degrees(root, mandatory_k).values())
        if len(type_224) < 3 or root_degree_lower <= K_DEGREE:
            raise AssertionError("a feasible size-four flower escaped")
        yield {
            "capacity": outside_budget,
            "chosen_224": chosen,
            "crossing_extensions": flower_crossing_extensions(4, petals),
            "external_slots": external_slots,
            "kind": "root4",
            "petal_sizes": list(petals),
            "rejection": "K_degree",
            "root_degree_lower": root_degree_lower,
            "root_size": 4,
            "type224_occurrences": type_224,
        }


def root3_records() -> Iterator[dict[str, object]]:
    for petals in itertools.product((2, 3), repeat=6):
        pairs = tuple((petals[2 * index], petals[2 * index + 1]) for index in range(3))
        external_slots = sum(size - 1 for size in petals)
        type_223 = sum(pair == (2, 2) for pair in pairs)
        type_233 = sum(pair[0] != pair[1] for pair in pairs)
        type_333 = sum(pair == (3, 3) for pair in pairs)
        d_u = [2 - sum(size == 3 for size in pair) for pair in pairs]
        forced_u = [0, 0, 0]
        violating: list[int] = []

        if external_slots > 10:
            rejection = "external_capacity"
            extensions = 0
        else:
            extensions = flower_crossing_extensions(3, petals)
            root, occurrences, f_edges, mandatory_k = explicit_flower(3, petals)
            u_edges = mandatory_k - f_edges
            root_u_degrees = degrees(root, u_edges)
            forced_u = [root_u_degrees[index] for index in range(3)]
            violating = [index for index in range(3) if forced_u[index] > d_u[index]]
            if type_233:
                size_two_endpoints = []
                for pair in occurrences:
                    for point in pair:
                        if len(point) == 2:
                            size_two_endpoints.extend(point - root)
                external_u_degrees = degrees(size_two_endpoints, u_edges)
                if not external_u_degrees or max(external_u_degrees.values()) < 4:
                    raise AssertionError("the explicit type-233 U-degree witness disappeared")
                rejection = "type_233_U_degree"
            else:
                if not violating:
                    raise AssertionError("a 223/333 flower escaped")
                rejection = "root_U_degree"

        yield {
            "capacity": 10,
            "crossing_extensions": extensions,
            "d_u": d_u,
            "external_slots": external_slots,
            "external_u_capacity": 3,
            "external_u_lower": 4 if type_233 else 0,
            "forced_u_lower": forced_u,
            "kind": "root3",
            "petal_sizes": list(petals),
            "rejection": rejection,
            "root_size": 3,
            "type223_occurrences": type_223,
            "type233_occurrences": type_233,
            "type333_occurrences": type_333,
            "violating_root_vertices": violating,
        }


def parity_records() -> Iterator[dict[str, object]]:
    incidence_total = ACTIVE_ORDER * 3
    yield {
        "active_triangles": ACTIVE_ORDER,
        "incidence_total": incidence_total,
        "kind": "parity",
        "point_size": 2,
        "points_per_triangle": 3,
        "rejection": "odd_incidence",
        "remainder": incidence_total % 2,
    }


def streams() -> tuple[tuple[str, Iterable[dict[str, object]]], ...]:
    return (
        (STREAM_ORDER[0], premise_records()),
        (STREAM_ORDER[1], crossing_records()),
        (STREAM_ORDER[2], collision_records()),
        (STREAM_ORDER[3], bound_records()),
        (STREAM_ORDER[4], degree_records()),
        (STREAM_ORDER[5], owner_records()),
        (STREAM_ORDER[6], root4_records()),
        (STREAM_ORDER[7], root3_records()),
        (STREAM_ORDER[8], parity_records()),
    )


def summarize_stream(records: Iterable[dict[str, object]]) -> tuple[dict[str, object], bytes]:
    payload = b"".join(canonical_line(record) for record in records)
    return (
        {
            "bytes": len(payload),
            "records": payload.count(b"\n"),
            "sha256": hashlib.sha256(payload).hexdigest(),
        },
        payload,
    )


def build_certificate(git_commit: str, dump_dir: Path | None = None) -> dict[str, object]:
    if len(git_commit) != 40 or any(character not in "0123456789abcdef" for character in git_commit):
        raise ValueError("git commit must be a lowercase forty-digit SHA-1")
    if dump_dir is not None:
        dump_dir.mkdir(parents=True, exist_ok=True)

    stream_table = []
    combined = hashlib.sha256()
    total_bytes = 0
    total_records = 0
    for name, records in streams():
        summary, payload = summarize_stream(records)
        stream_table.append({"name": name, **summary})
        combined.update(payload)
        total_bytes += int(summary["bytes"])
        total_records += int(summary["records"])
        if dump_dir is not None:
            (dump_dir / name).write_bytes(payload)

    premise_stream = next(item for item in stream_table if item["name"] == "premises.jsonl")
    root4 = next(item for item in stream_table if item["name"] == "root4_profiles.jsonl")
    root3 = next(item for item in stream_table if item["name"] == "root3_profiles.jsonl")
    if premise_stream["records"] != 1 or root4["records"] != 6_561 or root3["records"] != 64:
        raise AssertionError("rooted flower stream size changed")

    root4_values = list(root4_records())
    root3_values = list(root3_records())
    root4_extensions = sum(int(item["crossing_extensions"]) for item in root4_values)
    root3_extensions = sum(int(item["crossing_extensions"]) for item in root3_values)
    root4_rejections = {
        reason: sum(item["rejection"] == reason for item in root4_values)
        for reason in ("external_capacity", "K_degree")
    }
    root3_rejections = {
        reason: sum(item["rejection"] == reason for item in root3_values)
        for reason in ("external_capacity", "type_233_U_degree", "root_U_degree")
    }
    if root4_rejections != {"external_capacity": 6_552, "K_degree": 9}:
        raise AssertionError("size-four rejection histogram changed")
    if root3_rejections != {
        "external_capacity": 7,
        "type_233_U_degree": 50,
        "root_U_degree": 7,
    }:
        raise AssertionError("size-three rejection histogram changed")
    if (root4_extensions, root3_extensions) != (33, 917):
        raise AssertionError("crossing-extension totals changed")

    return {
        "claim_label": "UNKNOWN",
        "conclusion": {
            "conditional_global_n3_lower_bound": 42,
            "conditional_induced_C6_lower_bound": 209_328,
            "conditional_n3_39_survivors": 0,
            "target_result": "UNKNOWN",
        },
        "git_commit": git_commit,
        "premises": list(PREMISES),
        "schema": "conditional-n3-39-local-replay-v1",
        "scope": "conditional_n3_39_active_triangle_replay",
        "statistics": {
            "crossing_matrices_total": 682,
            "external_collision_pairs": 1_546,
            "root3_feasible_crossing_extensions": root3_extensions,
            "root3_profiles": 64,
            "root4_feasible_crossing_extensions": root4_extensions,
            "root4_profiles": 6_561,
        },
        "streams": stream_table,
        "combined": {
            "bytes": total_bytes,
            "records": total_records,
            "sha256": combined.hexdigest(),
        },
    }


def write_certificate(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(payload)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--dump-dir", type=Path)
    arguments = parser.parse_args(argv)
    certificate = build_certificate(arguments.git_commit, arguments.dump_dir)
    write_certificate(arguments.certificate, certificate)
    print("PASS generated conditional n3=39 local replay")
    print("records", certificate["combined"]["records"])
    print("bytes", certificate["combined"]["bytes"])
    print("combined_sha256", certificate["combined"]["sha256"])
    print("target_result", certificate["conclusion"]["target_result"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
