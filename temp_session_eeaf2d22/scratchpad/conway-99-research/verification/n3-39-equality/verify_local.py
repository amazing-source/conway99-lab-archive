#!/usr/bin/env python3
"""Independent replay verifier for the Wave 11 rooted-flower certificate.

This implementation imports no discovery or primary-audit code.  It uses
integer-coded profile enumeration and a closed crossing-count table, then
reconstructs the same canonical record streams and attacks the certificate
with eight in-memory mutations.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Iterable, Iterator, Sequence


ORDER = 13
K_DEGREE = 6
STREAM_NAMES = (
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
EXPECTED_PREMISES = (
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
ALLOWED_CROSSING_COUNTS = {
    (1, 1): 1,
    (1, 2): 1,
    (1, 3): 1,
    (2, 1): 1,
    (2, 2): 2,
    (2, 3): 4,
    (3, 1): 1,
    (3, 2): 4,
    (3, 3): 16,
}

# Filled from a separately generated, independently replayed frozen stream.
# These constants deliberately make coordinated changes to both algorithms a
# review-visible event rather than silently accepting new digests.
EXPECTED_STREAM_SUMMARIES: tuple[dict[str, object], ...] = (
    {
        "name": "premises.jsonl",
        "bytes": 512,
        "records": 1,
        "sha256": "1c7925ef36a023738279dcf3c7e5fba5ea29055c609f7ca79a24b27a49020100",
    },
    {
        "name": "crossing_matrices.jsonl",
        "bytes": 100_338,
        "records": 682,
        "sha256": "58d91ba3cd113431183d29a51e5b43c7580bc9815767df35269cfb0f49ddb304",
    },
    {
        "name": "collision_pairs.jsonl",
        "bytes": 167_922,
        "records": 1_546,
        "sha256": "2e12039f9a70a27f093cd5dbf8d4b8931138eb1b9db0d75908574459190ba8fc",
    },
    {
        "name": "size_bounds.jsonl",
        "bytes": 1_539,
        "records": 12,
        "sha256": "b4948bf52f4b49253003fa2587c63f8f1f4f9d6883de64d78ef4a82db92ae222",
    },
    {
        "name": "degree_table.jsonl",
        "bytes": 364,
        "records": 4,
        "sha256": "752f167eed12daf3e9d12429c6fbe45dd5b9fab22edeb7f75179b212fbc552b9",
    },
    {
        "name": "owner_motifs.jsonl",
        "bytes": 4_824,
        "records": 36,
        "sha256": "701c339f54f9305429e388e129d38b9f9fa5f73491b473cb6295355f3830a3ff",
    },
    {
        "name": "root4_profiles.jsonl",
        "bytes": 1_433_584,
        "records": 6_561,
        "sha256": "417ccd654d8938a8cb9436306078d9a99643fc129a96e377b1599d3be6d71225",
    },
    {
        "name": "root3_profiles.jsonl",
        "bytes": 21_504,
        "records": 64,
        "sha256": "a2523cf95f35a59cd9e405553ddfa324b7b640ae8ce53888c77896952fc789df",
    },
    {
        "name": "parity.jsonl",
        "bytes": 142,
        "records": 1,
        "sha256": "3db91a9a63245986dd93ddbf99fdb9514257a93cb11091f79906d9abdae32969",
    },
)
EXPECTED_COMBINED: dict[str, object] = {
    "bytes": 1_730_729,
    "records": 8_907,
    "sha256": "452850018ad13362694f5bfff2e4beac03288a113a0391c3456a47cd6fbfe9a1",
}


def line(record: object) -> bytes:
    encoded = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return encoded.encode("utf-8") + b"\n"


def premise_stream() -> Iterator[dict[str, object]]:
    yield {
        "claim_label": "UNKNOWN",
        "kind": "premises",
        "premises": list(EXPECTED_PREMISES),
        "schema": "conditional-n3-39-local-replay-v1",
        "scope": "conditional_n3_39_active_triangle_replay",
    }


def matrix_degrees(rows: int, columns: int, mask: int) -> tuple[list[int], list[int]]:
    row_degrees = [
        sum((mask >> (row * columns + column)) & 1 for column in range(columns))
        for row in range(rows)
    ]
    column_degrees = [
        sum((mask >> (row * columns + column)) & 1 for row in range(rows))
        for column in range(columns)
    ]
    return row_degrees, column_degrees


def crossing_stream() -> Iterator[dict[str, object]]:
    for rows in (1, 2, 3):
        for columns in (1, 2, 3):
            for mask in range(2 ** (rows * columns)):
                row_degrees, column_degrees = matrix_degrees(rows, columns, mask)
                allowed = not any(value not in (0, 2) for value in row_degrees + column_degrees)
                yield {
                    "allowed": allowed,
                    "col_degrees": column_degrees,
                    "kind": "crossing",
                    "left_size": rows,
                    "mask": mask,
                    "reason": "all_degrees_zero_or_two" if allowed else "forbidden_degree",
                    "right_size": columns,
                    "row_degrees": row_degrees,
                }


def collision_stream() -> Iterator[dict[str, object]]:
    for root_size in range(2, 14):
        slot_count = 2 * root_size
        for left in range(slot_count):
            for right in range(left + 1, slot_count):
                left_root = left >> 1
                right_root = right >> 1
                yield {
                    "kind": "collision",
                    "petal_slots": [left, right],
                    "rejection": "linearity" if left_root == right_root else "common_point",
                    "root_occurrences": [left_root, right_root],
                    "root_size": root_size,
                }


def bound_stream() -> Iterator[dict[str, object]]:
    for root_size in range(2, 14):
        available = 13 - root_size
        required = root_size << 1
        survives = required <= available
        yield {
            "available_outside": available,
            "kind": "bound",
            "rejection": None if survives else "external_capacity",
            "required_representatives": required,
            "root_size": root_size,
            "survives": survives,
        }


def degree_stream() -> Iterator[dict[str, object]]:
    for count3 in (0, 1, 2, 3):
        count2 = 3 - count3
        f_degree = count2 + 2 * count3
        yield {
            "f_degree": f_degree,
            "k_degree": 6,
            "kind": "degree",
            "size2_points": count2,
            "size3_points": count3,
            "u_degree": 6 - f_degree,
        }


def owner_stream() -> Iterator[dict[str, object]]:
    for left_size in (2, 3, 4):
        for right_size in (2, 3, 4):
            pair_count = (left_size - 1) * (right_size - 1)
            for pair_index in range(pair_count):
                left_index, right_index = divmod(pair_index, right_size - 1)
                left_point = frozenset((0, *range(1, left_size)))
                right_point = frozenset(
                    (0, *range(left_size, left_size + right_size - 1))
                )
                left_external = tuple(sorted(left_point - {0}))[left_index]
                right_external = tuple(sorted(right_point - {0}))[right_index]
                attempted_owner = frozenset((left_external, right_external))
                witnesses = (
                    left_point & right_point,
                    left_point & attempted_owner,
                    right_point & attempted_owner,
                )
                forbidden = (
                    all(len(witness) == 1 for witness in witnesses)
                    and len(frozenset().union(*witnesses)) == 3
                )
                if not forbidden:
                    raise AssertionError("independent owner witness was not a Berge triangle")
                yield {
                    "kind": "owner",
                    "left_external_index": left_index,
                    "left_point_size": left_size,
                    "rejection": "common_point",
                    "right_external_index": right_index,
                    "right_point_size": right_size,
                }


def decode_base(code: int, base: int, length: int, offset: int) -> tuple[int, ...]:
    values = []
    for power in reversed(range(length)):
        values.append(offset + (code // (base**power)) % base)
    return tuple(values)


def extension_count(root_size: int, petals: Sequence[int]) -> int:
    result = 1
    root_external = root_size - 1
    for occurrence in range(len(petals) // 2):
        left = petals[2 * occurrence] - 1
        right = petals[2 * occurrence + 1] - 1
        result *= ALLOWED_CROSSING_COUNTS[(root_external, left)]
        result *= ALLOWED_CROSSING_COUNTS[(root_external, right)]
        result *= ALLOWED_CROSSING_COUNTS[(left, right)]
    return result


def root4_stream(budget: int = 9) -> Iterator[dict[str, object]]:
    for code in range(3**8):
        petals = decode_base(code, 3, 8, 2)
        external = sum(petals) - 8
        occurrences = [
            root for root in range(4) if petals[2 * root : 2 * root + 2] == (2, 2)
        ]
        if external > budget:
            chosen: list[int] = []
            extensions = 0
            rejection = "external_capacity"
            degree_lower = None
        else:
            chosen = occurrences[:2]
            extensions = extension_count(4, petals)
            rejection = "K_degree"
            # The primary implementation constructs every mandatory K-edge.
            # Independently, each size-two petal has one endpoint which is
            # K-adjacent to all four root vertices, so the exact lower degree
            # is the internal K3 plus the number of size-two petals.
            degree_lower = 3 + petals.count(2)
            if len(occurrences) < 3 or degree_lower <= 6:
                raise AssertionError("independent size-four replay found a survivor")
        yield {
            "capacity": budget,
            "chosen_224": chosen,
            "crossing_extensions": extensions,
            "external_slots": external,
            "kind": "root4",
            "petal_sizes": list(petals),
            "rejection": rejection,
            "root_degree_lower": degree_lower,
            "root_size": 4,
            "type224_occurrences": occurrences,
        }


def root3_stream() -> Iterator[dict[str, object]]:
    for code in range(1 << 6):
        petals = tuple(2 + ((code >> bit) & 1) for bit in reversed(range(6)))
        pairs = tuple(petals[2 * root : 2 * root + 2] for root in range(3))
        external = sum(petals) - 6
        count223 = pairs.count((2, 2))
        count333 = pairs.count((3, 3))
        count233 = 3 - count223 - count333
        capacities = [2 - pair.count(3) for pair in pairs]
        forced = [0, 0, 0]
        violations: list[int] = []
        if external > 10:
            extensions = 0
            rejection = "external_capacity"
        else:
            extensions = extension_count(3, petals)
            # A size-two petal based at i contributes one forced U-edge to
            # each other root vertex.  Count endpoints, not an occurrence
            # coefficient: forcedU(v) = total size-two petals - those at v.
            total_size_two_petals = sum(capacities)
            forced = [total_size_two_petals - capacity for capacity in capacities]
            violations = [root for root in range(3) if forced[root] > capacities[root]]
            if count233:
                rejection = "type_233_U_degree"
            else:
                if not violations:
                    raise AssertionError("independent size-three replay found a survivor")
                rejection = "root_U_degree"
        yield {
            "capacity": 10,
            "crossing_extensions": extensions,
            "d_u": capacities,
            "external_slots": external,
            "external_u_capacity": 3,
            "external_u_lower": 4 if count233 else 0,
            "forced_u_lower": forced,
            "kind": "root3",
            "petal_sizes": list(petals),
            "rejection": rejection,
            "root_size": 3,
            "type223_occurrences": count223,
            "type233_occurrences": count233,
            "type333_occurrences": count333,
            "violating_root_vertices": violations,
        }


def parity_stream() -> Iterator[dict[str, object]]:
    total = 39
    yield {
        "active_triangles": 13,
        "incidence_total": total,
        "kind": "parity",
        "point_size": 2,
        "points_per_triangle": 3,
        "rejection": "odd_incidence",
        "remainder": total & 1,
    }


def all_streams() -> tuple[tuple[str, Iterable[dict[str, object]]], ...]:
    return (
        (STREAM_NAMES[0], premise_stream()),
        (STREAM_NAMES[1], crossing_stream()),
        (STREAM_NAMES[2], collision_stream()),
        (STREAM_NAMES[3], bound_stream()),
        (STREAM_NAMES[4], degree_stream()),
        (STREAM_NAMES[5], owner_stream()),
        (STREAM_NAMES[6], root4_stream()),
        (STREAM_NAMES[7], root3_stream()),
        (STREAM_NAMES[8], parity_stream()),
    )


def summarize(records: Iterable[dict[str, object]]) -> tuple[dict[str, object], bytes]:
    digest = hashlib.sha256()
    size = 0
    count = 0
    payload_parts = []
    for record in records:
        payload = line(record)
        payload_parts.append(payload)
        digest.update(payload)
        size += len(payload)
        count += 1
    return {"bytes": size, "records": count, "sha256": digest.hexdigest()}, b"".join(payload_parts)


def expected_stream_table() -> tuple[list[dict[str, object]], dict[str, object]]:
    table = []
    combined = hashlib.sha256()
    total_bytes = 0
    total_records = 0
    for name, records in all_streams():
        summary, payload = summarize(records)
        table.append({"name": name, **summary})
        combined.update(payload)
        total_bytes += int(summary["bytes"])
        total_records += int(summary["records"])
    return table, {"bytes": total_bytes, "records": total_records, "sha256": combined.hexdigest()}


def validate_certificate(certificate: dict[str, object]) -> None:
    if certificate.get("schema") != "conditional-n3-39-local-replay-v1":
        raise AssertionError("wrong certificate schema")
    commit = certificate.get("git_commit")
    if not isinstance(commit, str) or len(commit) != 40 or any(char not in "0123456789abcdef" for char in commit):
        raise AssertionError("bad certificate commit")
    if certificate.get("scope") != "conditional_n3_39_active_triangle_replay":
        raise AssertionError("wrong certificate scope")
    if tuple(certificate.get("premises", ())) != EXPECTED_PREMISES:
        raise AssertionError("frozen premise list changed")
    if certificate.get("claim_label") != "UNKNOWN":
        raise AssertionError("claim label inflation")

    table, combined = expected_stream_table()
    if certificate.get("streams") != table:
        raise AssertionError("stream table mismatch")
    if certificate.get("combined") != combined:
        raise AssertionError("combined stream mismatch")
    if combined["records"] != 8_907:
        raise AssertionError("unexpected total record count")
    if EXPECTED_STREAM_SUMMARIES and tuple(table) != EXPECTED_STREAM_SUMMARIES:
        raise AssertionError("frozen stream summaries changed")
    if EXPECTED_COMBINED and combined != EXPECTED_COMBINED:
        raise AssertionError("frozen combined digest changed")

    statistics = certificate.get("statistics")
    expected_statistics = {
        "crossing_matrices_total": 682,
        "external_collision_pairs": 1_546,
        "root3_feasible_crossing_extensions": 917,
        "root3_profiles": 64,
        "root4_feasible_crossing_extensions": 33,
        "root4_profiles": 6_561,
    }
    if statistics != expected_statistics:
        raise AssertionError("certificate statistics changed")
    conclusion = certificate.get("conclusion")
    expected_conclusion = {
        "conditional_global_n3_lower_bound": 42,
        "conditional_induced_C6_lower_bound": 209_328,
        "conditional_n3_39_survivors": 0,
        "target_result": "UNKNOWN",
    }
    if conclusion != expected_conclusion:
        raise AssertionError("certificate conclusion changed")


def rejected_mutations(certificate: dict[str, object]) -> list[str]:
    mutations: list[tuple[str, dict[str, object]]] = []

    dropped = copy.deepcopy(certificate)
    dropped["streams"].pop()
    mutations.append(("drop_stream", dropped))

    changed_digest = copy.deepcopy(certificate)
    changed_digest["combined"]["sha256"] = "0" * 64
    mutations.append(("alter_combined_digest", changed_digest))

    dropped_bridge = copy.deepcopy(certificate)
    dropped_bridge["premises"].remove("K_is_simple_complement_of_L_on_distinct_active_triangles")
    mutations.append(("drop_complement_bridge", dropped_bridge))

    dropped_common_point = copy.deepcopy(certificate)
    dropped_common_point["premises"].remove("common_point_Berge_triangle_is_forbidden")
    mutations.append(("drop_common_point_premise", dropped_common_point))

    dropped_point_clique = copy.deepcopy(certificate)
    dropped_point_clique["premises"].remove("every_active_point_set_is_a_clique_in_K")
    mutations.append(("drop_point_clique_premise", dropped_point_clique))

    dropped_crossing = copy.deepcopy(certificate)
    dropped_crossing["premises"].remove("every_labeled_crossing_degree_is_zero_or_two")
    mutations.append(("drop_crossing_degree_premise", dropped_crossing))

    false_survivor = copy.deepcopy(certificate)
    false_survivor["conclusion"]["conditional_n3_39_survivors"] = 1
    mutations.append(("restore_false_survivor", false_survivor))

    inflated = copy.deepcopy(certificate)
    inflated["claim_label"] = "FORMALLY_CHECKED_CANDIDATE"
    inflated["conclusion"]["target_result"] = "NONEXISTENT"
    mutations.append(("inflate_target_status", inflated))

    rejected = []
    for name, mutation in mutations:
        try:
            validate_certificate(mutation)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError(f"certificate mutation survived: {name}")
    return rejected


def semantic_checks() -> dict[str, object]:
    crossing = list(crossing_stream())
    accepted_counts = {
        f"{left}x{right}": sum(
            bool(record["allowed"])
            for record in crossing
            if record["left_size"] == left and record["right_size"] == right
        )
        for left in range(1, 4)
        for right in range(1, 4)
    }
    if accepted_counts != {f"{left}x{right}": count for (left, right), count in ALLOWED_CROSSING_COUNTS.items()}:
        raise AssertionError("crossing acceptance table changed")
    bad_singleton = next(
        record for record in crossing if record["left_size"] == 1 and record["right_size"] == 2 and record["mask"] == 3
    )
    if bad_singleton["allowed"]:
        raise AssertionError("nonempty singleton crossing survived")
    singleton_rows, singleton_columns = matrix_degrees(1, 2, 3)
    one_sided_accepts = all(value in (0, 2) for value in singleton_rows)
    two_sided_accepts = all(
        value in (0, 2) for value in singleton_rows + singleton_columns
    )
    if not one_sided_accepts or two_sided_accepts:
        raise AssertionError("singleton-side semantic mutation fixture changed")

    collisions = list(collision_stream())
    collision_histogram = {
        reason: sum(record["rejection"] == reason for record in collisions)
        for reason in ("linearity", "common_point")
    }
    if collision_histogram != {"linearity": 90, "common_point": 1_456}:
        raise AssertionError("collision basis changed")
    common_point_disabled_survivors = collision_histogram["common_point"]
    owner_disabled_survivors = sum(1 for _record in owner_stream())
    if (common_point_disabled_survivors, owner_disabled_survivors) != (1_456, 36):
        raise AssertionError("common-point mutation fixtures changed")

    # Explicitly build the canonical two-occurrence 224 witness.  With the
    # complement bridge, empty singleton crossings add all endpoint/root
    # cross-pairs and every root vertex has degree seven.  Without that bridge
    # only point-clique F-edges remain and the witness disappears.
    root = frozenset((0, 1, 2, 3))
    petals = (
        frozenset((0, 4)),
        frozenset((0, 5)),
        frozenset((1, 6)),
        frozenset((1, 7)),
    )
    local_points = (root, *petals)
    f_edges = {
        tuple(sorted((left, right)))
        for point in local_points
        for left in point
        for right in point
        if left < right
    }

    def root_minimum_degree(with_complement: bool) -> int:
        forced = set(f_edges)
        if with_complement:
            for occurrence, pair in ((0, petals[:2]), (1, petals[2:])):
                for point in pair:
                    endpoint = next(iter(point - {occurrence}))
                    forced.update(
                        tuple(sorted((endpoint, root_vertex)))
                        for root_vertex in root
                    )
        return min(
            sum(vertex in edge for edge in forced)
            for vertex in root
        )

    complement_degree = root_minimum_degree(True)
    no_complement_degree = root_minimum_degree(False)
    if complement_degree != 7 or no_complement_degree >= 7:
        raise AssertionError("complement semantic mutation fixture changed")

    # Count the deliberately weakened budget directly.  Calling the production
    # root4 stream with budget ten would correctly trip its degree-proof
    # assertion on profiles that exist only in the mutated domain.
    root4_petals = (decode_base(code, 3, 8, 2) for code in range(3**8))
    external_counts = [sum(petals) - 8 for petals in root4_petals]
    feasible_budget9 = sum(value <= 9 for value in external_counts)
    feasible_budget10 = sum(value <= 10 for value in external_counts)
    if (feasible_budget9, feasible_budget10) != (9, 45):
        raise AssertionError("size-four budget mutation changed")
    if [record["u_degree"] for record in degree_stream()] != [3, 2, 1, 0]:
        raise AssertionError("F/U degree fixtures changed")

    root4 = list(root4_stream())
    root4_histogram = {
        reason: sum(record["rejection"] == reason for record in root4)
        for reason in ("external_capacity", "K_degree")
    }
    if root4_histogram != {"external_capacity": 6_552, "K_degree": 9}:
        raise AssertionError("size-four rejection histogram changed")
    root4_degree_histogram = {
        value: sum(record["root_degree_lower"] == value for record in root4)
        for value in (None, 10, 11)
    }
    if root4_degree_histogram != {None: 6_552, 10: 8, 11: 1}:
        raise AssertionError("size-four explicit degree histogram changed")
    root4_extensions = sum(int(record["crossing_extensions"]) for record in root4)

    root3 = list(root3_stream())
    root3_histogram = {
        reason: sum(record["rejection"] == reason for record in root3)
        for reason in ("external_capacity", "type_233_U_degree", "root_U_degree")
    }
    if root3_histogram != {"external_capacity": 7, "type_233_U_degree": 50, "root_U_degree": 7}:
        raise AssertionError("size-three rejection histogram changed")
    raw_root3_classes = {
        "has_233": sum(int(record["type233_occurrences"]) > 0 for record in root3),
        "all_333": sum(int(record["type333_occurrences"]) == 3 for record in root3),
        "has_223_no_233": sum(
            int(record["type223_occurrences"]) > 0
            and int(record["type233_occurrences"]) == 0
            for record in root3
        ),
    }
    if raw_root3_classes != {"has_233": 56, "all_333": 1, "has_223_no_233": 7}:
        raise AssertionError("size-three raw proof branches changed")
    old_formula_differences = 0
    for record in root3:
        pairs = tuple(
            tuple(record["petal_sizes"][2 * root : 2 * root + 2])
            for root in range(3)
        )
        old_forced = [
            2 * (int(record["type223_occurrences"]) - int(pair == (2, 2)))
            for pair in pairs
        ]
        if record["rejection"] != "external_capacity" and old_forced != record["forced_u_lower"]:
            old_formula_differences += 1
    if old_formula_differences != 50:
        raise AssertionError("the rejected homogeneous-only root-three formula changed")

    root3_fixtures = {
        tuple(record["petal_sizes"]): record
        for record in root3
        if tuple(record["petal_sizes"])
        in {
            (2, 2, 2, 2, 2, 3),
            (2, 2, 2, 2, 3, 3),
            (2, 2, 3, 3, 3, 3),
            (2, 2, 2, 2, 2, 2),
            (3, 3, 3, 3, 3, 3),
        }
    }
    expected_fixture_forced = {
        (2, 2, 2, 2, 2, 3): [3, 3, 4],
        (2, 2, 2, 2, 3, 3): [2, 2, 4],
        (2, 2, 3, 3, 3, 3): [0, 2, 2],
        (2, 2, 2, 2, 2, 2): [4, 4, 4],
        (3, 3, 3, 3, 3, 3): [0, 0, 0],
    }
    if {
        petals: root3_fixtures[petals]["forced_u_lower"]
        for petals in expected_fixture_forced
    } != expected_fixture_forced:
        raise AssertionError("root-three exact endpoint fixtures changed")
    root3_extensions = sum(int(record["crossing_extensions"]) for record in root3)
    if (root4_extensions, root3_extensions) != (33, 917):
        raise AssertionError("crossing-extension totals changed")
    return {
        "accepted_crossing_counts": accepted_counts,
        "collision_histogram": collision_histogram,
        "complement_224_root_degree_with_without": [complement_degree, no_complement_degree],
        "common_point_disabled_collision_owner_survivors": [
            common_point_disabled_survivors,
            owner_disabled_survivors,
        ],
        "old_root3_formula_differences": old_formula_differences,
        "raw_root3_classes": raw_root3_classes,
        "root3_fixture_forced_u": {
            "-".join(map(str, petals)): expected_fixture_forced[petals]
            for petals in expected_fixture_forced
        },
        "root3_rejection_histogram": root3_histogram,
        "root4_degree_histogram": {
            "capacity": root4_degree_histogram[None],
            "10": root4_degree_histogram[10],
            "11": root4_degree_histogram[11],
        },
        "root4_rejection_histogram": root4_histogram,
        "root3_root4_crossing_extensions": [root3_extensions, root4_extensions],
        "singleton_mask3_one_sided_two_sided": [one_sided_accepts, two_sided_accepts],
        "size4_feasible_budget_9_10": [feasible_budget9, feasible_budget10],
    }


def replay(path: Path) -> dict[str, object]:
    certificate = json.loads(path.read_text(encoding="utf-8"))
    validate_certificate(certificate)
    return {
        "combined": certificate["combined"],
        "mutations_rejected": rejected_mutations(certificate),
        "semantic_checks": semantic_checks(),
        "status": "PASS independent n3=39 local replay",
        "target_result": "UNKNOWN",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args(argv)
    result = replay(arguments.certificate)
    if arguments.output is not None:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        payload = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8")
        arguments.output.write_bytes(payload)
    print(result["status"])
    print("records", result["combined"]["records"])
    print("combined_sha256", result["combined"]["sha256"])
    print("mutations_rejected", result["mutations_rejected"])
    print("target_result", result["target_result"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
