#!/usr/bin/env python3
"""Independent adversarial verifier for the Wave 16 n3=51 computation.

This module intentionally does not import any ``wave16_n3_51_*`` discovery
module.  It reconstructs the arithmetic, finite cover, CNF streams, and raw
positive candidate from the stated mathematical encoding.
"""

from __future__ import annotations

import argparse
import copy
import gc
import hashlib
import itertools
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import pysat
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


ROOT = Path(__file__).resolve().parents[2]
ATTEMPTS = ROOT / "attempts" / "wave16-n3-51-computation"
PROFILE_PATH = ATTEMPTS / "n3-51-profile-census.json"
SCAN_PATH = ATTEMPTS / "n3-51-active-local-scan.json"
CANDIDATE_PATH = (
    ATTEMPTS
    / "n3-51-r16-q2x14-q3x2-no-size3-active-local-candidate.json"
)
FAILURES_PATH = ATTEMPTS / "n3-51-run-failures.json"
DISCOVERY_VALIDATION_PATH = (
    ATTEMPTS / "n3-51-discovery-validation.json"
)
DISCOVERY_REPORT_PATH = (
    ROOT / "agents" / "2026-07-23-wave16-n3-51-computational.md"
)
ACTIVE_SOURCE_PATH = ROOT / "code" / "wave16_n3_51_active_sat.py"
PROFILE_SOURCE_PATH = ROOT / "code" / "wave16_n3_51_profiles.py"
VERIFY_SOURCE_PATH = ROOT / "code" / "wave16_n3_51_verify.py"
TEST_SOURCE_PATH = ROOT / "code" / "wave16_n3_51_test.py"
PREINSPECTION_PATH = (
    ROOT / "verification" / "n3-51-computation" / "preinspection-freeze.md"
)
INDEPENDENT_SOURCE_PATH = (
    ROOT / "verification" / "n3-51-computation" / "independent_check.py"
)
INDEPENDENT_TEST_PATH = (
    ROOT
    / "verification"
    / "n3-51-computation"
    / "test_independent_check.py"
)
REGENERATED_PROFILE_PATH = (
    ROOT
    / "verification"
    / "n3-51-computation"
    / "regenerated-profile-census.json"
)
SUBMITTED_REPLAY_PATH = (
    ROOT
    / "verification"
    / "n3-51-computation"
    / "submitted-validation-replay.json"
)

STARTING_COMMIT = "861cfeb6195b19b08feceff07be88a6ab5093fd4"

EXPECTED_ENCODED_PREMISES = [
    (
        "exactly three selected non-singleton point sets pass "
        "through each active label"
    ),
    "all selected point sizes are two or three",
    "the selected point family is linear",
    "F is exactly the union of selected point-clique edges",
    "every selected point is a clique in K",
    "every F-triangle is its selected size-three point",
    (
        "meeting crossings have two-sided L-degrees in {0,2}: "
        "singleton-side crossings are L-empty and 2-by-2 "
        "crossings are L-empty or L-complete"
    ),
    (
        "full 2-by-2 L-overlap counts obey the inherited "
        "fixed-point upper cap at each selected triple"
    ),
    "every active label has its exact profile-specific K-degree",
]

EXPECTED_UNENCODED_PREMISES = [
    "inactive point sets and inactive graph vertices",
    "which disjoint selected points are adjacent original vertices",
    "fixed support contributed by disjoint point sets",
    "equality completion of every fixed-point support sum",
    "the 693-vertex H graph",
    "a 99-vertex adjacency matrix",
    "global SRG lambda/mu equations",
]

ALLOWED_STATUSES = {
    "SAT_CANDIDATE",
    "UNSAT_UNVERIFIED",
    "TIMEOUT_UNKNOWN",
    "BUDGET_UNKNOWN",
}


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    check(isinstance(value, dict), f"{path} is not a JSON object")
    return value


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("ascii")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def require_keys(
    value: dict[str, object],
    expected: set[str],
    context: str,
) -> None:
    observed = set(value)
    check(
        observed == expected,
        (
            f"{context} keys differ: missing={sorted(expected-observed)}, "
            f"extra={sorted(observed-expected)}"
        ),
    )


def histogram(values: Iterable[int]) -> dict[str, int]:
    return {
        str(key): count
        for key, count in sorted(Counter(values).items())
    }


def profile_name(q_values: Sequence[int]) -> str:
    suffix = "-".join(
        f"q{key}x{count}"
        for key, count in sorted(Counter(q_values).items())
    )
    return f"r{len(q_values)}-{suffix}"


def independently_enumerate_profiles() -> tuple[tuple[int, ...], ...]:
    """Enumerate fixed-length nondecreasing partitions, not discovery DFS."""

    answers: list[tuple[int, ...]] = []
    for order in range(17, 0, -1):
        maximum = (order - 1) // 3
        if maximum < 2:
            continue

        def extend(
            prefix: tuple[int, ...],
            remaining_parts: int,
            remaining_sum: int,
            lower: int,
        ) -> None:
            if remaining_parts == 0:
                if remaining_sum == 0:
                    answers.append(prefix)
                return
            minimum_possible = lower * remaining_parts
            maximum_possible = maximum * remaining_parts
            if not minimum_possible <= remaining_sum <= maximum_possible:
                return
            upper = min(maximum, remaining_sum // remaining_parts)
            for next_value in range(lower, upper + 1):
                extend(
                    (*prefix, next_value),
                    remaining_parts - 1,
                    remaining_sum - next_value,
                    next_value,
                )

        extend((), order, 34, 2)
    return tuple(answers)


def degree_sequence(q_values: Sequence[int]) -> tuple[int, ...]:
    order = len(q_values)
    return tuple(order - 1 - 3 * value for value in q_values)


def profile_rows_from_scratch() -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for q_values in independently_enumerate_profiles():
        degrees = degree_sequence(q_values)
        minimum_ok = min(degrees) >= 3
        obstruction_ok = minimum_ok and min(degrees) >= 4
        rows.append(
            {
                "profile_id": profile_name(q_values),
                "active_order": len(q_values),
                "q_values": list(q_values),
                "q_histogram": histogram(q_values),
                "q_sum": sum(q_values),
                "k_degrees": list(degrees),
                "k_degree_histogram": histogram(degrees),
                "k_edge_count": sum(degrees) // 2,
                "k_handshake_even": sum(degrees) % 2 == 0,
                "survives_minimum_degree_three": minimum_ok,
                "survives_degree_three_obstruction": obstruction_ok,
            }
        )
    return tuple(rows)


def rooted_states(
    order: int,
    root_q: Sequence[int],
) -> tuple[dict[str, object], ...]:
    q_values = tuple(map(int, root_q))
    caps = tuple(order - 1 - 3 * q for q in q_values)
    fixed_total = 2 * sum(q_values)
    states: list[dict[str, object]] = []
    for triple_counts in itertools.product((1, 2, 3), repeat=3):
        if 3 + sum(triple_counts) > order - 3:
            continue
        residual_caps = tuple(
            cap - (3 + count)
            for cap, count in zip(caps, triple_counts, strict=True)
        )
        if min(residual_caps) < 0:
            continue
        for zero_counts in itertools.product(
            *(range(count) for count in triple_counts)
        ):
            lower_bounds = tuple(
                sum(
                    3 - triple_counts[other]
                    + 2 * zero_counts[other]
                    for other in range(3)
                    if other != root
                )
                for root in range(3)
            )
            if any(
                lower > upper
                for lower, upper in zip(
                    lower_bounds, residual_caps, strict=True
                )
            ):
                continue
            full = sum(
                count - 1 - zero
                for count, zero in zip(
                    triple_counts, zero_counts, strict=True
                )
            )
            contribution = 4 * full
            if contribution > fixed_total:
                continue
            states.append(
                {
                    "t_values": list(triple_counts),
                    "empty_l_crossing_counts": list(zero_counts),
                    "u_capacities": list(residual_caps),
                    "forced_u_degree_lower_bounds": list(lower_bounds),
                    "full_l_crossings": full,
                    "overlap_contribution": contribution,
                    "fixed_point_total": fixed_total,
                }
            )
    return tuple(states)


def rooted_state_orbit_key(
    root_q: Sequence[int],
    state: dict[str, object],
) -> tuple[object, ...]:
    groups: list[object] = []
    for q_value in sorted(set(root_q)):
        records = []
        for index, observed in enumerate(root_q):
            if observed != q_value:
                continue
            records.append(
                (
                    int(state["t_values"][index]),
                    int(state["empty_l_crossing_counts"][index]),
                    int(state["u_capacities"][index]),
                    int(
                        state[
                            "forced_u_degree_lower_bounds"
                        ][index]
                    ),
                )
            )
        groups.append((q_value, tuple(sorted(records))))
    groups.append(("full_l_crossings", int(state["full_l_crossings"])))
    return tuple(groups)


def independently_reduce_branches(
    surviving_rows: Sequence[dict[str, object]],
    local_counts: dict[tuple[int, tuple[int, int, int]], int],
) -> tuple[
    tuple[dict[str, object], ...],
    tuple[dict[str, object], ...],
]:
    raw: list[dict[str, object]] = []
    reduced: list[dict[str, object]] = []
    for row in surviving_rows:
        name = str(row["profile_id"])
        order = int(row["active_order"])
        q_values = tuple(map(int, row["q_values"]))
        possibilities: list[int | None] = [None]
        possibilities.extend(
            count
            for count in range(min(3, q_values.count(3)) + 1)
            if 3 - count <= q_values.count(2)
        )
        for count in possibilities:
            if count is None:
                branch_id = "no-size3"
                normalization = (
                    "all selected size-three point variables are false"
                )
            else:
                branch_id = f"root-q3x{count}"
                normalization = (
                    "choose one selected triple of this q-type and "
                    "name it using permutations within equal-q classes"
                )
            branch = {
                "profile_id": name,
                "branch_id": branch_id,
                "root_q3_count": count,
                "normalization": normalization,
            }
            raw.append(branch)
            survives = True
            reason = "retained for exact active-local SAT exploration"
            certificate = None
            if count is None and order % 2:
                survives = False
                reason = (
                    "incidence parity: 3r is odd while size-two points "
                    "contribute even total incidence"
                )
                certificate = {"total_incidence": 3 * order, "modulus": 2}
            elif count is not None:
                root_type = tuple([2] * (3 - count) + [3] * count)
                state_count = local_counts.get((order, root_type), 0)
                if state_count == 0:
                    survives = False
                    reason = (
                        "the exhaustive rooted size-three local-state "
                        "census is empty"
                    )
                    certificate = {
                        "root_q3_count": count,
                        "labeled_local_state_count": 0,
                    }
            if (
                survives
                and name == "r14-q2x8-q3x6"
                and count is None
            ):
                # In the cubic, triangle-free point graph F, choose a
                # neighbour a of a q=3 root v.  The other two F-neighbours
                # of a are distinct and outside N_F(v), and singleton-side
                # meeting crossings force both to be K-neighbours of v.
                survives = False
                reason = (
                    "at a q=3 label, cubic triangle-free F forces its "
                    "three neighbours and two new distance-two labels "
                    "as distinct K-neighbours, so d_K>=5>4"
                )
                certificate = {
                    "forced_k_degree_lower_bound": 5,
                    "profile_k_degree": 4,
                }
            reduced.append(
                {
                    **branch,
                    "survives_finite_reductions": survives,
                    "finite_reduction_reason": reason,
                    "finite_reduction_certificate": certificate,
                }
            )
    return tuple(raw), tuple(reduced)


def validate_profile_document(
    report: dict[str, object],
) -> dict[str, object]:
    require_keys(
        report,
        {
            "schema",
            "claim_label",
            "target_result",
            "conditional_n3_51_exclusion",
            "novelty",
            "starting_git_commit",
            "source_manifest",
            "encoded_premises",
            "unencoded_premises",
            "method",
            "python",
            "platform",
            "semantic",
            "semantic_sha256",
        },
        "profile artifact",
    )
    check(
        report["schema"]
        == "conway99-wave16-n3-51-profile-census-v1",
        "profile schema changed",
    )
    check(
        report["claim_label"] == "DERIVED_PENDING_AUDIT",
        "profile claim label inflated",
    )
    for field in (
        "target_result",
        "conditional_n3_51_exclusion",
        "novelty",
    ):
        check(report[field] == "UNKNOWN", f"profile {field} inflated")
    check(
        report["starting_git_commit"] == STARTING_COMMIT,
        "profile starting commit differs",
    )
    for relative, archived_hash in report["source_manifest"].items():
        source = ROOT / str(relative)
        check(source.is_file(), f"profile input missing: {relative}")
        check(
            sha256_file(source) == archived_hash,
            f"profile input hash differs: {relative}",
        )

    semantic = report["semantic"]
    check(
        report["semantic_sha256"]
        == sha256_bytes(canonical_json_bytes(semantic)),
        "profile semantic digest differs",
    )
    independent_rows = profile_rows_from_scratch()
    check(len(independent_rows) == 16, "independent profile count is not 16")
    check(
        tuple(semantic["raw_profiles"]) == independent_rows,
        "archived profile rows differ from independent enumeration",
    )
    survivors = tuple(
        row
        for row in independent_rows
        if row["survives_degree_three_obstruction"]
    )
    survivor_names = [row["profile_id"] for row in survivors]
    check(
        semantic["surviving_profiles"] == survivor_names,
        "surviving profile filter differs",
    )

    large = semantic["large_point_reductions"]
    for row in survivors:
        name = str(row["profile_id"])
        order = int(row["active_order"])
        maximum_degree = max(map(int, row["k_degrees"]))
        details = large[name]
        check(
            details["maximum_size_from_expansion"] == order // 3,
            f"{name} expansion size cap differs",
        )
        check(
            details["maximum_root_k_degree_used"] == maximum_degree,
            f"{name} maximum degree differs",
        )
        expected_sizes = list(range(4, order // 3 + 1))
        check(
            sorted(map(int, details["size_obstructions"]))
            == expected_sizes,
            f"{name} large-point sizes differ",
        )
        for size in expected_sizes:
            observed = details["size_obstructions"][str(size)]
            forced = 2 * size * size
            capacity = (
                size * maximum_degree - size * (size - 1)
            )
            check(
                observed["forced_external_k_incidence"] == forced,
                f"{name} size {size} forced incidence differs",
            )
            check(
                observed["available_external_k_incidence"] == capacity,
                f"{name} size {size} capacity differs",
            )
            check(
                forced > capacity
                and observed["strict_contradiction"] is True,
                f"{name} size {size} is not contradictory",
            )
        check(
            details["remaining_point_sizes"] == [2, 3],
            f"{name} remaining sizes differ",
        )

    mode_rows = {}
    local_counts: dict[
        tuple[int, tuple[int, int, int]], int
    ] = {}
    for block in semantic["local_size3_mode_census"]:
        order = int(block["active_order"])
        for mode in block["root_compositions"]:
            root_q = tuple(map(int, mode["root_q_values"]))
            states = rooted_states(order, root_q)
            orbits = {
                rooted_state_orbit_key(root_q, state)
                for state in states
            }
            check(
                mode["labeled_state_count"] == len(states),
                f"local state count differs for {(order, root_q)}",
            )
            check(
                mode["equal_q_coordinate_orbit_count"] == len(orbits),
                f"local orbit count differs for {(order, root_q)}",
            )
            check(
                mode["state_sha256"]
                == sha256_bytes(canonical_json_bytes(states)),
                f"local state digest differs for {(order, root_q)}",
            )
            local_counts[(order, root_q)] = len(states)
            mode_rows[f"{order}:{''.join(map(str, root_q))}"] = {
                "labeled_states": len(states),
                "equal_q_orbits": len(orbits),
            }

    raw_cover, reduced_cover = independently_reduce_branches(
        survivors, local_counts
    )
    check(
        tuple(semantic["raw_branch_cover"]) == raw_cover,
        "raw sixteen-branch cover differs",
    )
    check(
        tuple(semantic["finite_branch_reduction"]) == reduced_cover,
        "finite branch reduction differs",
    )
    surviving_cover = tuple(
        {
            "profile_id": row["profile_id"],
            "branch_id": row["branch_id"],
        }
        for row in reduced_cover
        if row["survives_finite_reductions"]
    )
    check(
        tuple(semantic["post_finite_surviving_branches"])
        == surviving_cover,
        "post-reduction seven-branch cover differs",
    )
    check(len(raw_cover) == 16, "raw branch count is not 16")
    check(len(surviving_cover) == 7, "surviving branch count is not 7")
    return {
        "raw_profile_count": len(independent_rows),
        "surviving_profile_count": len(survivors),
        "raw_branch_count": len(raw_cover),
        "surviving_branch_count": len(surviving_cover),
        "surviving_cover": list(surviving_cover),
        "local_modes": mode_rows,
        "semantic_sha256": report["semantic_sha256"],
    }


def all_edges(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(itertools.combinations(range(order), 2))


def all_points(order: int) -> tuple[tuple[int, ...], ...]:
    return tuple(
        point
        for size in (2, 3)
        for point in itertools.combinations(range(order), size)
    )


def canonical_edge(left: int, right: int) -> tuple[int, int]:
    check(left != right, "loop requested")
    return (left, right) if left < right else (right, left)


def add_exactly(
    cnf: CNF,
    pool: IDPool,
    literals: Iterable[int],
    bound: int,
) -> None:
    encoded = CardEnc.equals(
        lits=list(literals),
        bound=bound,
        vpool=pool,
        encoding=EncType.seqcounter,
    )
    cnf.extend(encoded.clauses)


def add_upper_bound(
    cnf: CNF,
    pool: IDPool,
    literals: Iterable[int],
    bound: int,
) -> None:
    values = list(literals)
    if len(values) <= bound:
        return
    encoded = CardEnc.atmost(
        lits=values,
        bound=bound,
        vpool=pool,
        encoding=EncType.seqcounter,
    )
    cnf.extend(encoded.clauses)


@dataclass
class IndependentInstance:
    q_values: tuple[int, ...]
    degrees: tuple[int, ...]
    cnf: CNF
    pool: IDPool
    points: tuple[tuple[int, ...], ...]
    selected: dict[tuple[int, ...], int]
    k_edge: dict[tuple[int, int], int]

    @property
    def order(self) -> int:
        return len(self.q_values)


def build_formula_independently(
    q_values: Sequence[int],
) -> IndependentInstance:
    q_tuple = tuple(map(int, q_values))
    order = len(q_tuple)
    degrees = degree_sequence(q_tuple)
    points = all_points(order)
    edges = all_edges(order)
    pool = IDPool()
    selected = {
        point: pool.id(("independent-point", point)) for point in points
    }
    k_edge = {
        item: pool.id(("independent-K", item)) for item in edges
    }
    f_edge = {
        item: pool.id(("independent-F", item)) for item in edges
    }
    cnf = CNF()

    for vertex in range(order):
        add_exactly(
            cnf,
            pool,
            (
                selected[point]
                for point in points
                if vertex in point
            ),
            3,
        )

    for item in edges:
        owners = [
            selected[point]
            for point in points
            if item[0] in point and item[1] in point
        ]
        add_upper_bound(cnf, pool, owners, 1)
        for owner in owners:
            cnf.append([-owner, f_edge[item]])
        cnf.append([-f_edge[item], *owners])

    for point in points:
        for item in itertools.combinations(point, 2):
            cnf.append([-selected[point], k_edge[item]])

    for triple in itertools.combinations(range(order), 3):
        ab, ac, bc = itertools.combinations(triple, 2)
        cnf.append(
            [
                -f_edge[ab],
                -f_edge[ac],
                -f_edge[bc],
                selected[triple],
            ]
        )

    triples = tuple(point for point in points if len(point) == 3)
    overlap_witnesses: dict[tuple[int, ...], list[int]] = {
        point: [] for point in triples
    }
    for left_index, left in enumerate(points):
        left_set = set(left)
        for right in points[left_index + 1 :]:
            intersection = left_set.intersection(right)
            if len(intersection) != 1:
                continue
            common = next(iter(intersection))
            left_external = tuple(v for v in left if v != common)
            right_external = tuple(v for v in right if v != common)
            crossing = [
                k_edge[canonical_edge(first, second)]
                for first in left_external
                for second in right_external
            ]
            guard = [-selected[left], -selected[right]]
            if len(left_external) == 1 or len(right_external) == 1:
                for literal in crossing:
                    cnf.append([*guard, literal])
                continue
            first = crossing[0]
            for literal in crossing[1:]:
                cnf.append([*guard, -first, literal])
                cnf.append([*guard, first, -literal])
            witness = pool.id(
                ("independent-full-L", left, right)
            )
            overlap_witnesses[left].append(witness)
            overlap_witnesses[right].append(witness)
            cnf.append([-witness, selected[left]])
            cnf.append([-witness, selected[right]])
            cnf.append([-witness, -first])
            cnf.append(
                [-selected[left], -selected[right], first, witness]
            )

    for triple in triples:
        cap = sum(q_tuple[v] for v in triple) // 2
        add_upper_bound(
            cnf, pool, overlap_witnesses[triple], cap
        )

    for vertex, degree in enumerate(degrees):
        add_exactly(
            cnf,
            pool,
            (
                k_edge[canonical_edge(vertex, other)]
                for other in range(order)
                if other != vertex
            ),
            degree,
        )

    return IndependentInstance(
        q_values=q_tuple,
        degrees=degrees,
        cnf=cnf,
        pool=pool,
        points=points,
        selected=selected,
        k_edge=k_edge,
    )


def branch_units(
    instance: IndependentInstance,
    branch_id: str,
) -> tuple[int, ...]:
    triples = tuple(
        point for point in instance.points if len(point) == 3
    )
    if branch_id == "no-size3":
        return tuple(-instance.selected[point] for point in triples)
    match = re.fullmatch(r"root-q3x([0-3])", branch_id)
    check(match is not None, f"invalid branch id {branch_id}")
    q3_count = int(match.group(1))
    q2_count = instance.q_values.count(2)
    q3_total = instance.q_values.count(3)
    check(q3_count <= q3_total, "root requests too many q=3 labels")
    q2_needed = 3 - q3_count
    check(q2_needed <= q2_count, "root requests too many q=2 labels")
    root = tuple(
        (
            *range(q2_needed),
            *range(q2_count, q2_count + q3_count),
        )
    )
    check(len(root) == 3, "canonical root has wrong size")
    return (instance.selected[root],)


def materialized_formula_sha256(
    instance: IndependentInstance,
    units: Sequence[int],
) -> str:
    digest = hashlib.sha256()
    digest.update(
        (
            f"p cnf {instance.pool.top} "
            f"{len(instance.cnf.clauses) + len(units)}\n"
        ).encode("ascii")
    )
    for clause in instance.cnf.clauses:
        digest.update(" ".join(map(str, clause)).encode("ascii"))
        digest.update(b" 0\n")
    for literal in units:
        digest.update(f"{literal} 0\n".encode("ascii"))
    return digest.hexdigest()


def normalize_point(raw: object, order: int) -> tuple[int, ...]:
    check(
        isinstance(raw, list)
        and len(raw) in (2, 3)
        and all(type(v) is int for v in raw),
        "malformed candidate point",
    )
    check(raw == sorted(raw), "candidate point is not sorted")
    check(len(set(raw)) == len(raw), "candidate point repeats a label")
    check(all(0 <= v < order for v in raw), "candidate point out of range")
    return tuple(raw)


def normalize_k_edge(raw: object, order: int) -> tuple[int, int]:
    check(
        isinstance(raw, list)
        and len(raw) == 2
        and all(type(v) is int for v in raw),
        "malformed candidate K edge",
    )
    left, right = raw
    check(0 <= left < right < order, "candidate K edge not canonical")
    return left, right


def candidate_diagnostics(
    q_values: Sequence[int],
    points: Sequence[tuple[int, ...]],
    k_edges: frozenset[tuple[int, int]],
) -> dict[str, object]:
    order = len(q_values)
    incidence = Counter(v for point in points for v in point)
    owners: dict[tuple[int, int], list[int]] = {
        item: [] for item in all_edges(order)
    }
    missing = []
    for index, point in enumerate(points):
        for item in itertools.combinations(point, 2):
            owners[item].append(index)
            if item not in k_edges:
                missing.append(item)
    point_set = set(points)
    berge = []
    for triple in itertools.combinations(range(order), 3):
        pairs = tuple(itertools.combinations(triple, 2))
        if all(owners[item] for item in pairs) and triple not in point_set:
            berge.append(list(triple))

    crossings = []
    overlap_degree: Counter[tuple[int, ...]] = Counter()
    full_overlaps: list[list[list[int]]] = []
    meeting_count = 0
    for left_index, left in enumerate(points):
        left_set = set(left)
        for right in points[left_index + 1 :]:
            intersection = left_set.intersection(right)
            if len(intersection) != 1:
                continue
            meeting_count += 1
            common = next(iter(intersection))
            left_external = tuple(v for v in left if v != common)
            right_external = tuple(v for v in right if v != common)
            l_matrix = [
                [
                    canonical_edge(first, second) not in k_edges
                    for second in right_external
                ]
                for first in left_external
            ]
            row_degrees = [sum(row) for row in l_matrix]
            column_degrees = [
                sum(l_matrix[row][column] for row in range(len(l_matrix)))
                for column in range(len(right_external))
            ]
            if any(
                degree not in (0, 2)
                for degree in (*row_degrees, *column_degrees)
            ):
                crossings.append(
                    {
                        "left": list(left),
                        "right": list(right),
                        "row_degrees": row_degrees,
                        "column_degrees": column_degrees,
                    }
                )
            if (
                len(left) == len(right) == 3
                and sum(row_degrees) == 4
            ):
                overlap_degree[left] += 1
                overlap_degree[right] += 1
                full_overlaps.append([list(left), list(right)])

    overlap_violations = []
    for point in points:
        if len(point) != 3:
            continue
        cap = sum(q_values[v] for v in point) // 2
        if overlap_degree[point] > cap:
            overlap_violations.append(
                {
                    "point": list(point),
                    "observed": overlap_degree[point],
                    "cap": cap,
                }
            )

    degrees = [0] * order
    for left, right in k_edges:
        degrees[left] += 1
        degrees[right] += 1
    return {
        "point_count": len(points),
        "size2_point_count": sum(len(point) == 2 for point in points),
        "size3_point_count": sum(len(point) == 3 for point in points),
        "incidence_degrees": [incidence[v] for v in range(order)],
        "linear_pair_owner_violation_count": sum(
            len(indices) > 1 for indices in owners.values()
        ),
        "missing_point_clique_edges": [
            list(item) for item in sorted(set(missing))
        ],
        "k_edge_count": len(k_edges),
        "k_degree_sequence": degrees,
        "common_point_Berge_triangle_count": len(berge),
        "common_point_Berge_triangles": berge,
        "meeting_crossings_checked": meeting_count,
        "meeting_crossing_violation_count": len(crossings),
        "meeting_crossing_violations": crossings,
        "full_L_overlap_count": len(full_overlaps),
        "full_L_overlaps": full_overlaps,
        "overlap_cap_violation_count": len(overlap_violations),
        "overlap_cap_violations": overlap_violations,
    }


def expected_source_provenance() -> dict[str, str]:
    return {
        "code/wave16_n3_51_active_sat.py": sha256_file(
            ACTIVE_SOURCE_PATH
        ),
        "code/wave16_n3_51_profiles.py": sha256_file(
            PROFILE_SOURCE_PATH
        ),
        (
            "attempts/wave16-n3-51-computation/"
            "n3-51-profile-census.json"
        ): sha256_file(PROFILE_PATH),
    }


def expected_branch_description(
    q_values: Sequence[int], branch_id: str
) -> dict[str, object]:
    if branch_id == "no-size3":
        return {
            "branch_id": branch_id,
            "root_q3_count": None,
            "root_point": None,
            "root_q_values": None,
            "normalization": "all selected size-three points are absent",
        }
    match = re.fullmatch(r"root-q3x([0-3])", branch_id)
    check(match is not None, "candidate branch id malformed")
    count = int(match.group(1))
    q2_count = tuple(q_values).count(2)
    root = tuple(
        (*range(3 - count), *range(q2_count, q2_count + count))
    )
    return {
        "branch_id": branch_id,
        "root_q3_count": count,
        "root_point": list(root),
        "root_q_values": sorted(q_values[v] for v in root),
        "normalization": (
            "one selected triple is named using only permutations "
            "within the equal-q label classes; no completed-graph "
            "automorphism is assumed"
        ),
    }


def validate_candidate_document(
    candidate: dict[str, object],
    surviving_cover: Sequence[dict[str, object]],
) -> dict[str, object]:
    require_keys(
        candidate,
        {
            "schema",
            "claim_label",
            "target_result",
            "conditional_n3_51_exclusion",
            "novelty",
            "scope",
            "target_n3",
            "starting_git_commit",
            "source_provenance",
            "profile_id",
            "active_order",
            "q_values",
            "k_degree_targets",
            "branch",
            "variant",
            "encoded_premises",
            "unencoded_premises",
            "symmetry_boundary",
            "point_sets",
            "K_edges",
            "diagnostics",
            "semantic_core",
            "semantic_sha256",
            "formula",
        },
        "candidate",
    )
    check(
        candidate["schema"]
        == "conway99-wave16-n3-51-active-local-candidate-v1",
        "candidate schema changed",
    )
    check(candidate["claim_label"] == "CANDIDATE", "candidate claim inflated")
    for field in (
        "target_result",
        "conditional_n3_51_exclusion",
        "novelty",
    ):
        check(candidate[field] == "UNKNOWN", f"candidate {field} inflated")
    check(
        candidate["scope"] == "active-label auxiliary object only",
        "candidate scope inflated",
    )
    check(candidate["target_n3"] == 51, "candidate n3 changed")
    check(
        candidate["starting_git_commit"] == STARTING_COMMIT,
        "candidate starting commit differs",
    )
    check(
        candidate["source_provenance"] == expected_source_provenance(),
        "candidate source provenance differs",
    )
    check(candidate["variant"] == "full", "candidate variant changed")
    check(
        candidate["encoded_premises"] == EXPECTED_ENCODED_PREMISES,
        "candidate encoded premises differ",
    )
    check(
        candidate["unencoded_premises"] == EXPECTED_UNENCODED_PREMISES,
        "candidate unencoded premises differ",
    )
    check(
        candidate["symmetry_boundary"]
        == (
            "q labels are sorted; a positive root branch uses only "
            "permutations inside equal-q classes; no completed-graph "
            "automorphism is assumed"
        ),
        "candidate symmetry boundary differs",
    )
    q_values = tuple(map(int, candidate["q_values"]))
    order = len(q_values)
    check(candidate["active_order"] == order, "candidate order differs")
    check(
        candidate["profile_id"] == profile_name(q_values),
        "candidate profile id differs",
    )
    targets = list(degree_sequence(q_values))
    check(
        candidate["k_degree_targets"] == targets,
        "candidate K-degree targets differ",
    )
    branch_id = str(candidate["branch"]["branch_id"])
    check(
        {
            "profile_id": candidate["profile_id"],
            "branch_id": branch_id,
        }
        in surviving_cover,
        "candidate lies outside independently reconstructed cover",
    )
    check(
        candidate["branch"]
        == expected_branch_description(q_values, branch_id),
        "candidate branch metadata differs",
    )
    points = tuple(
        normalize_point(raw, order) for raw in candidate["point_sets"]
    )
    check(len(points) == len(set(points)), "candidate duplicates a point")
    check(
        list(points) == sorted(points, key=lambda p: (len(p), p)),
        "candidate point order is not canonical",
    )
    edges = tuple(
        normalize_k_edge(raw, order) for raw in candidate["K_edges"]
    )
    check(len(edges) == len(set(edges)), "candidate duplicates a K edge")
    check(list(edges) == sorted(edges), "candidate K-edge order differs")
    diagnostics = candidate_diagnostics(
        q_values, points, frozenset(edges)
    )
    check(
        candidate["diagnostics"] == diagnostics,
        "candidate diagnostics differ from raw reconstruction",
    )
    check(
        diagnostics["incidence_degrees"] == [3] * order,
        "candidate incidence is not exactly three",
    )
    for key in (
        "linear_pair_owner_violation_count",
        "common_point_Berge_triangle_count",
        "meeting_crossing_violation_count",
        "overlap_cap_violation_count",
    ):
        check(diagnostics[key] == 0, f"candidate violates {key}")
    check(
        diagnostics["missing_point_clique_edges"] == [],
        "candidate omits a point-clique K edge",
    )
    check(
        diagnostics["k_degree_sequence"] == targets,
        "candidate K degrees differ",
    )
    formula = candidate["formula"]
    require_keys(
        formula,
        {
            "builder_source",
            "builder_source_sha256",
            "profile_source",
            "profile_source_sha256",
            "encoded_premises_sha256",
            "variable_count",
            "base_clause_count",
            "branch_unit_count",
            "materialized_clause_count",
            "materialized_dimacs_sha256",
            "branch_units_are_solver_assumptions",
            "build_seconds",
        },
        "candidate formula metadata",
    )
    check(
        formula["builder_source"] == "code/wave16_n3_51_active_sat.py"
        and formula["builder_source_sha256"]
        == sha256_file(ACTIVE_SOURCE_PATH),
        "candidate builder provenance differs",
    )
    check(
        formula["profile_source"] == "code/wave16_n3_51_profiles.py"
        and formula["profile_source_sha256"]
        == sha256_file(PROFILE_SOURCE_PATH),
        "candidate profile-source provenance differs",
    )
    check(
        formula["encoded_premises_sha256"]
        == sha256_bytes(canonical_json_bytes(EXPECTED_ENCODED_PREMISES)),
        "candidate encoded-premise digest differs",
    )
    expected_units = (
        len(tuple(itertools.combinations(range(order), 3)))
        if branch_id == "no-size3"
        else 1
    )
    check(
        formula["branch_unit_count"] == expected_units,
        "candidate branch-unit count differs",
    )
    check(
        formula["materialized_clause_count"]
        == formula["base_clause_count"] + expected_units,
        "candidate materialized clause count differs",
    )
    check(
        formula["branch_units_are_solver_assumptions"] is True,
        "candidate branch-unit policy differs",
    )
    core = {
        "starting_git_commit": candidate["starting_git_commit"],
        "source_provenance": candidate["source_provenance"],
        "profile_id": candidate["profile_id"],
        "q_values": candidate["q_values"],
        "branch": candidate["branch"],
        "point_sets": candidate["point_sets"],
        "K_edges": candidate["K_edges"],
        "formula_materialized_dimacs_sha256": formula[
            "materialized_dimacs_sha256"
        ],
        "encoded_premises_sha256": formula[
            "encoded_premises_sha256"
        ],
    }
    check(candidate["semantic_core"] == core, "candidate semantic core differs")
    digest = sha256_bytes(canonical_json_bytes(core))
    check(candidate["semantic_sha256"] == digest, "candidate semantic hash differs")
    return {
        "profile_id": candidate["profile_id"],
        "branch_id": branch_id,
        "point_count": len(points),
        "size2_point_count": diagnostics["size2_point_count"],
        "size3_point_count": diagnostics["size3_point_count"],
        "k_edge_count": len(edges),
        "meeting_crossings_checked": diagnostics[
            "meeting_crossings_checked"
        ],
        "semantic_sha256": digest,
    }


def validate_scan_document(
    scan: dict[str, object],
    surviving_cover: Sequence[dict[str, object]],
    candidate: dict[str, object],
    formula_records: dict[tuple[str, str], dict[str, object]] | None = None,
) -> dict[str, object]:
    require_keys(
        scan,
        {
            "schema",
            "claim_label",
            "target_result",
            "conditional_n3_51_exclusion",
            "novelty",
            "scope",
            "starting_git_commit",
            "source_provenance",
            "coverage_argument",
            "encoded_premises",
            "unencoded_premises",
            "negative_result_policy",
            "python",
            "python_sat",
            "platform",
            "solver_name",
            "conflict_budget_per_branch",
            "wall_timeout_seconds_per_branch",
            "results",
            "candidate_paths",
            "semantic",
            "semantic_sha256",
        },
        "scan",
    )
    check(
        scan["schema"]
        == "conway99-wave16-n3-51-active-local-scan-v1",
        "scan schema differs",
    )
    check(scan["claim_label"] == "CANDIDATE", "scan claim inflated")
    for field in (
        "target_result",
        "conditional_n3_51_exclusion",
        "novelty",
    ):
        check(scan[field] == "UNKNOWN", f"scan {field} inflated")
    check(
        scan["scope"]
        == (
            "complete seven-branch cover of the encoded active-local "
            "relaxation after the pending-audit finite reductions"
        ),
        "scan scope differs",
    )
    check(
        scan["starting_git_commit"] == STARTING_COMMIT,
        "scan starting commit differs",
    )
    check(
        scan["source_provenance"] == expected_source_provenance(),
        "scan source provenance differs",
    )
    check(
        scan["encoded_premises"] == EXPECTED_ENCODED_PREMISES,
        "scan encoded premises differ",
    )
    check(
        scan["unencoded_premises"] == EXPECTED_UNENCODED_PREMISES,
        "scan unencoded premises differ",
    )
    check(
        scan["negative_result_policy"]
        == (
            "UNSAT, budget, and timeout returns have no force "
            "without an emitted and independently checked proof trace"
        ),
        "scan negative-result policy differs",
    )
    check(
        scan["semantic_sha256"]
        == sha256_bytes(canonical_json_bytes(scan["semantic"])),
        "scan semantic hash differs",
    )
    observed_cover = [
        {
            "profile_id": row["profile_id"],
            "branch_id": row["branch"]["branch_id"],
        }
        for row in scan["results"]
    ]
    check(
        observed_cover == list(surviving_cover),
        "scan cover differs from independent finite cover",
    )
    check(
        scan["semantic"]["coverage"] == list(surviving_cover),
        "scan semantic cover differs",
    )
    check(
        len(set((r["profile_id"], r["branch"]["branch_id"]) for r in scan["results"]))
        == len(scan["results"]),
        "scan contains a duplicate branch",
    )
    archived_candidates = []
    status_counts: Counter[str] = Counter()
    for row in scan["results"]:
        status = str(row["status"])
        check(status in ALLOWED_STATUSES, f"invalid scan status {status}")
        status_counts[status] += 1
        solver = row["solver"]
        q_by_profile = {
            str(profile["profile_id"]): tuple(
                map(int, profile["q_values"])
            )
            for profile in profile_rows_from_scratch()
        }
        expected_branch = expected_branch_description(
            q_by_profile[str(row["profile_id"])],
            str(row["branch"]["branch_id"]),
        )
        check(
            row["branch"] == expected_branch,
            "scan branch metadata differs",
        )
        formula = row["formula"]
        require_keys(
            formula,
            {
                "builder_source",
                "builder_source_sha256",
                "profile_source",
                "profile_source_sha256",
                "encoded_premises_sha256",
                "variable_count",
                "base_clause_count",
                "branch_unit_count",
                "materialized_clause_count",
                "materialized_dimacs_sha256",
                "branch_units_are_solver_assumptions",
                "build_seconds",
            },
            "scan formula metadata",
        )
        check(
            formula["builder_source"]
            == "code/wave16_n3_51_active_sat.py"
            and formula["builder_source_sha256"]
            == sha256_file(ACTIVE_SOURCE_PATH),
            "scan builder provenance differs",
        )
        check(
            formula["profile_source"]
            == "code/wave16_n3_51_profiles.py"
            and formula["profile_source_sha256"]
            == sha256_file(PROFILE_SOURCE_PATH),
            "scan profile-source provenance differs",
        )
        check(
            formula["encoded_premises_sha256"]
            == sha256_bytes(
                canonical_json_bytes(EXPECTED_ENCODED_PREMISES)
            ),
            "scan encoded-premise digest differs",
        )
        check(
            formula["branch_units_are_solver_assumptions"] is True,
            "scan branch-unit policy differs",
        )
        check(
            formula["materialized_clause_count"]
            == formula["base_clause_count"]
            + formula["branch_unit_count"],
            "scan materialized clause arithmetic differs",
        )
        check(
            solver["proof_trace_emitted"] is False
            and solver["proof_trace_checked"] is False,
            "scan forges proof-trace evidence",
        )
        if status == "SAT_CANDIDATE":
            check(
                row["evidentiary_status"]
                == "POSITIVE_ASSIGNMENT_REQUIRES_EXACT_VALIDATION",
                "positive evidentiary label differs",
            )
            check(
                row["candidate_path"]
                == CANDIDATE_PATH.relative_to(ROOT).as_posix(),
                "scan redirects the positive candidate",
            )
            check(
                row["candidate_file_sha256"] == sha256_file(CANDIDATE_PATH),
                "scan candidate file hash differs",
            )
            check(
                row["candidate_semantic_sha256"]
                == candidate["semantic_sha256"],
                "scan candidate semantic link differs",
            )
            archived_candidates.append(row["candidate_path"])
        else:
            check(
                row["evidentiary_status"]
                == "NON_EVIDENTIARY_NO_CHECKED_PROOF_TRACE",
                "negative evidentiary label inflated",
            )
            check(
                not any(
                    key in row
                    for key in (
                        "candidate_path",
                        "candidate_file_sha256",
                        "candidate_semantic_sha256",
                    )
                ),
                "negative row has candidate metadata",
            )
            if status == "TIMEOUT_UNKNOWN":
                check(
                    solver["timer_fired"] is True
                    and solver["wall_timeout_enforced"] is True,
                    "timeout row lacks an enforced fired timer",
                )
            if status in {"UNSAT_UNVERIFIED", "BUDGET_UNKNOWN"}:
                check(
                    solver["timer_fired"] is False,
                    f"{status} row incorrectly records a fired timer",
                )
        if formula_records is not None:
            key = (str(row["profile_id"]), str(row["branch"]["branch_id"]))
            check(key in formula_records, f"formula record missing for {key}")
            expected = formula_records[key]
            for field in (
                "variable_count",
                "base_clause_count",
                "branch_unit_count",
                "materialized_clause_count",
                "materialized_dimacs_sha256",
            ):
                check(
                    row["formula"][field] == expected[field],
                    f"formula {field} differs for {key}",
                )
    check(
        archived_candidates == scan["candidate_paths"],
        "scan candidate path list differs",
    )
    projection = [
        {
            "profile_id": row["profile_id"],
            "branch_id": row["branch"]["branch_id"],
            "status": row["status"],
            "formula_sha256": row["formula"][
                "materialized_dimacs_sha256"
            ],
            "candidate_file_sha256": row.get("candidate_file_sha256"),
            "candidate_semantic_sha256": row.get(
                "candidate_semantic_sha256"
            ),
        }
        for row in scan["results"]
    ]
    check(
        scan["semantic"]["results"] == projection,
        "scan semantic result projection differs",
    )
    return {
        "branch_count": len(scan["results"]),
        "status_histogram": dict(sorted(status_counts.items())),
        "semantic_sha256": scan["semantic_sha256"],
    }


def fixed_candidate_literals(
    instance: IndependentInstance,
    candidate: dict[str, object],
) -> list[int]:
    chosen_points = {
        tuple(map(int, point)) for point in candidate["point_sets"]
    }
    chosen_edges = {
        tuple(map(int, item)) for item in candidate["K_edges"]
    }
    literals = list(
        branch_units(instance, str(candidate["branch"]["branch_id"]))
    )
    literals.extend(
        variable if point in chosen_points else -variable
        for point, variable in instance.selected.items()
    )
    literals.extend(
        variable if item in chosen_edges else -variable
        for item, variable in instance.k_edge.items()
    )
    return literals


def validate_failure_archive(
    archive: dict[str, object],
    scan: dict[str, object],
) -> dict[str, object]:
    require_keys(
        archive,
        {
            "schema",
            "claim_label",
            "target_result",
            "conditional_n3_51_exclusion",
            "novelty",
            "starting_git_commit",
            "final_archive",
            "historical_probe_before_final_source_freeze",
        },
        "failure archive",
    )
    check(
        archive["schema"] == "conway99-wave16-n3-51-run-failures-v1",
        "failure schema differs",
    )
    check(archive["claim_label"] == "CANDIDATE", "failure claim inflated")
    for field in (
        "target_result",
        "conditional_n3_51_exclusion",
        "novelty",
    ):
        check(archive[field] == "UNKNOWN", f"failure {field} inflated")
    check(
        archive["starting_git_commit"] == STARTING_COMMIT,
        "failure starting commit differs",
    )
    final = archive["final_archive"]
    check(
        final["active_local_scan_path"]
        == SCAN_PATH.relative_to(ROOT).as_posix(),
        "failure archive scan path differs",
    )
    check(
        final["active_local_scan_sha256"] == sha256_file(SCAN_PATH),
        "failure archive scan hash differs",
    )
    negative_counts = Counter(
        str(row["status"])
        for row in scan["results"]
        if row["status"] != "SAT_CANDIDATE"
    )
    check(
        final["negative_status_histogram"]
        == dict(sorted(negative_counts.items())),
        "failure archive final histogram differs",
    )
    probe = archive["historical_probe_before_final_source_freeze"]
    check(probe["status"] == "BUDGET_UNKNOWN", "historical budget status inflated")
    check(
        probe["proof_trace_emitted"] is False
        and probe["proof_trace_checked"] is False,
        "historical probe forges proof evidence",
    )
    check(
        probe["evidentiary_status"]
        == "NON_EVIDENTIARY_NO_CHECKED_PROOF_TRACE",
        "historical probe evidentiary status inflated",
    )
    matching = next(
        row
        for row in scan["results"]
        if row["profile_id"] == probe["profile_id"]
        and row["branch"]["branch_id"] == probe["branch_id"]
    )
    for field in (
        "variable_count",
        "base_clause_count",
        "branch_unit_count",
        "materialized_clause_count",
        "materialized_dimacs_sha256",
    ):
        check(
            probe["formula"][field] == matching["formula"][field],
            f"historical probe formula {field} differs",
        )
    check(
        probe["builder_source_sha256_at_run"]
        != sha256_file(ACTIVE_SOURCE_PATH),
        "historical intermediate source is not distinguished",
    )
    return {
        "historical_budget_unknown_count": 1,
        "final_negative_status_histogram": dict(
            sorted(negative_counts.items())
        ),
        "historical_source_bytes_available": False,
    }


def validate_discovery_validation_artifact(
    artifact: dict[str, object],
) -> dict[str, object]:
    check(
        artifact["schema"]
        == "conway99-wave16-n3-51-discovery-validation-v1",
        "discovery validation schema differs",
    )
    check(artifact["claim_label"] == "CANDIDATE", "validator claim inflated")
    for field in (
        "target_result",
        "conditional_n3_51_exclusion",
        "novelty",
    ):
        check(artifact[field] == "UNKNOWN", f"validator {field} inflated")
    check(
        artifact["starting_git_commit"] == STARTING_COMMIT,
        "validator starting commit differs",
    )
    check(
        artifact["negative_solver_results_evidentiary"] is False,
        "validator promotes negative solver results",
    )
    mutation = artifact["mutation_validation"]
    check(mutation["status"] == "PASS", "submitted mutation suite did not pass")
    check(mutation["mutation_count"] == 20, "submitted mutation count differs")
    check(
        len(mutation["mutations"]) == 20,
        "submitted mutation result map does not contain 20 entries",
    )
    check(
        artifact["semantic_sha256"]
        == sha256_bytes(canonical_json_bytes(artifact["semantic"])),
        "discovery-validation semantic hash differs",
    )
    return {
        "submitted_mutation_count": mutation["mutation_count"],
        "semantic_sha256": artifact["semantic_sha256"],
    }


def validate_report_provenance(text: str) -> dict[str, object]:
    check(
        re.search(r"^git_commit: " + STARTING_COMMIT + r"$", text, re.M)
        is not None,
        "discovery report starting commit differs",
    )
    for field, value in (
        ("claim_label", "CANDIDATE"),
        ("target_result", "UNKNOWN"),
        ("conditional_n3_51_exclusion", "UNKNOWN"),
        ("novelty", "UNKNOWN"),
    ):
        check(
            re.search(rf"^\s*{field}: {value}$", text, re.M) is not None,
            f"discovery report {field} differs",
        )
    path_hashes = re.findall(
        r"^\s{2}([^:\r\n]+): ([0-9a-f]{64})$", text, re.M
    )
    checked_paths = {}
    for relative, declared in path_hashes:
        candidate = ROOT / relative
        if candidate.is_file():
            observed = sha256_file(candidate)
            check(
                observed == declared,
                f"report path hash differs for {relative}",
            )
            checked_paths[relative] = observed
    expected_report_paths = {
        "AGENTS.md",
        "CONJECTURE.md",
        "verification/2026-07-22-n3-side-incidence-audit.md",
        "verification/2026-07-22-wave14-n3-48-computation-audit.md",
        "code/wave16_n3_51_profiles.py",
        "code/wave16_n3_51_active_sat.py",
        "code/wave16_n3_51_verify.py",
        "code/wave16_n3_51_test.py",
        (
            "attempts/wave16-n3-51-computation/"
            "n3-51-profile-census.json"
        ),
        (
            "attempts/wave16-n3-51-computation/"
            "n3-51-active-local-scan.json"
        ),
        (
            "attempts/wave16-n3-51-computation/"
            "n3-51-r16-q2x14-q3x2-no-size3-"
            "active-local-candidate.json"
        ),
        (
            "attempts/wave16-n3-51-computation/"
            "n3-51-run-failures.json"
        ),
        (
            "attempts/wave16-n3-51-computation/"
            "n3-51-discovery-validation.json"
        ),
    }
    check(
        expected_report_paths.issubset(checked_paths),
        "discovery report omits a required path hash",
    )
    for scalar in (
        "raw_active_profiles: 16",
        "profiles_after_inherited_filters: 4",
        "raw_symmetry_cover_branches: 16",
        "branches_after_exact_finite_reductions: 7",
        "full_active_local_positive_candidates: 1",
        "proofless_unsat_returns: 1",
        "enforced_timeout_unknown_returns: 5",
        "preserved_historical_budget_unknown_returns: 1",
    ):
        check(scalar in text, f"report scalar missing: {scalar}")
    return {
        "declared_path_hashes_checked": len(checked_paths),
        "report_sha256": sha256_file(DISCOVERY_REPORT_PATH),
        "git_commit_authentication": "NOT_PERFORMED_NO_GIT_ALLOWED",
    }


def rebuild_formula_records(
    scan: dict[str, object],
    candidate: dict[str, object],
) -> tuple[
    dict[tuple[str, str], dict[str, object]],
    bool,
    str,
]:
    rows_by_profile: dict[str, list[dict[str, object]]] = {}
    for row in scan["results"]:
        rows_by_profile.setdefault(str(row["profile_id"]), []).append(row)
    profile_q = {
        str(row["profile_id"]): tuple(map(int, row["q_values"]))
        for row in read_json(PROFILE_PATH)["semantic"]["raw_profiles"]
    }
    records: dict[tuple[str, str], dict[str, object]] = {}
    candidate_extends = False
    observed_r14_raw = "NOT_RUN"
    for name, rows in rows_by_profile.items():
        instance = build_formula_independently(profile_q[name])
        for row in rows:
            branch_id = str(row["branch"]["branch_id"])
            units = branch_units(instance, branch_id)
            record = {
                "variable_count": instance.pool.top,
                "base_clause_count": len(instance.cnf.clauses),
                "branch_unit_count": len(units),
                "materialized_clause_count": (
                    len(instance.cnf.clauses) + len(units)
                ),
                "materialized_dimacs_sha256": (
                    materialized_formula_sha256(instance, units)
                ),
            }
            records[(name, branch_id)] = record
        if name == candidate["profile_id"]:
            fixed = fixed_candidate_literals(instance, candidate)
            with Solver(
                name="glucose42",
                bootstrap_with=instance.cnf.clauses,
            ) as solver:
                candidate_extends = solver.solve(assumptions=fixed) is True
        if name == "r14-q2x8-q3x6":
            units = branch_units(instance, "root-q3x0")
            with Solver(
                name="glucose42",
                bootstrap_with=instance.cnf.clauses,
            ) as solver:
                solver.conf_budget(30_000)
                raw = solver.solve_limited(
                    assumptions=list(units), expect_interrupt=True
                )
            observed_r14_raw = (
                "SAT_CANDIDATE"
                if raw is True
                else "UNSAT_UNVERIFIED"
                if raw is False
                else "BUDGET_UNKNOWN"
            )
        del instance
        gc.collect()
    return records, candidate_extends, observed_r14_raw


def run_audit() -> dict[str, object]:
    profile = read_json(PROFILE_PATH)
    scan = read_json(SCAN_PATH)
    candidate = read_json(CANDIDATE_PATH)
    failures = read_json(FAILURES_PATH)
    discovery_validation = read_json(DISCOVERY_VALIDATION_PATH)

    profile_result = validate_profile_document(profile)
    cover = profile_result["surviving_cover"]
    candidate_result = validate_candidate_document(candidate, cover)
    formula_records, candidate_extends, r14_raw = rebuild_formula_records(
        scan, candidate
    )
    check(candidate_extends, "candidate does not extend independent CNF")
    candidate_key = (
        str(candidate["profile_id"]),
        str(candidate["branch"]["branch_id"]),
    )
    candidate_formula_record = formula_records[candidate_key]
    for field in (
        "variable_count",
        "base_clause_count",
        "branch_unit_count",
        "materialized_clause_count",
        "materialized_dimacs_sha256",
    ):
        check(
            candidate["formula"][field]
            == candidate_formula_record[field],
            f"candidate formula {field} differs from reconstruction",
        )
    positive_scan_row = next(
        row for row in scan["results"] if row["status"] == "SAT_CANDIDATE"
    )
    for field in (
        "variable_count",
        "base_clause_count",
        "branch_unit_count",
        "materialized_clause_count",
        "materialized_dimacs_sha256",
        "encoded_premises_sha256",
        "builder_source_sha256",
        "profile_source_sha256",
    ):
        check(
            candidate["formula"][field]
            == positive_scan_row["formula"][field],
            f"candidate/scan formula link differs at {field}",
        )
    scan_result = validate_scan_document(
        scan, cover, candidate, formula_records
    )
    check(
        scan_result["status_histogram"]
        == {
            "SAT_CANDIDATE": 1,
            "TIMEOUT_UNKNOWN": 5,
            "UNSAT_UNVERIFIED": 1,
        },
        "final scan status histogram differs",
    )
    failure_result = validate_failure_archive(failures, scan)
    submitted_result = validate_discovery_validation_artifact(
        discovery_validation
    )
    report_result = validate_report_provenance(
        DISCOVERY_REPORT_PATH.read_text(encoding="utf-8")
    )
    check(
        sha256_file(REGENERATED_PROFILE_PATH) == sha256_file(PROFILE_PATH),
        "submitted profile regeneration is not byte-identical",
    )
    check(
        sha256_file(SUBMITTED_REPLAY_PATH)
        == sha256_file(DISCOVERY_VALIDATION_PATH),
        "submitted validator replay is not byte-identical",
    )
    formula_output = [
        {
            "profile_id": profile_id,
            "branch_id": branch_id,
            **record,
        }
        for (profile_id, branch_id), record in formula_records.items()
    ]
    inputs = {
        path.relative_to(ROOT).as_posix(): sha256_file(path)
        for path in (
            DISCOVERY_REPORT_PATH,
            PROFILE_SOURCE_PATH,
            ACTIVE_SOURCE_PATH,
            VERIFY_SOURCE_PATH,
            TEST_SOURCE_PATH,
            PROFILE_PATH,
            SCAN_PATH,
            CANDIDATE_PATH,
            FAILURES_PATH,
            DISCOVERY_VALIDATION_PATH,
            PREINSPECTION_PATH,
            INDEPENDENT_SOURCE_PATH,
            INDEPENDENT_TEST_PATH,
        )
    }
    return {
        "schema": "conway99-wave16-n3-51-independent-audit-v1",
        "role": "verifier",
        "date_utc": "2026-07-23T11:16:10Z",
        "git_commit": "NOT_QUERIED_VERIFIER_FORBIDDEN_FROM_GIT",
        "claim_label": "VERIFIED",
        "scope": (
            "conditional active-label profile census, seven-branch "
            "reduction, exact CNF streams, and one positive active-local "
            "relaxation candidate only"
        ),
        "verdict": "PASS_FOR_CONDITIONAL_ACTIVE_LOCAL_ARCHIVE_ONLY",
        "target_result": "UNKNOWN",
        "conditional_n3_51_exclusion": "UNKNOWN",
        "novelty": "UNKNOWN",
        "starting_git_commit": STARTING_COMMIT,
        "git_was_used": False,
        "inputs": inputs,
        "profile_validation": profile_result,
        "formula_validation": {
            "formula_stream_count": len(formula_records),
            "all_streams_exactly_rebuilt": True,
            "records": formula_output,
        },
        "candidate_validation": {
            **candidate_result,
            "extends_independently_rebuilt_cnf": candidate_extends,
        },
        "scan_validation": {
            **scan_result,
            "negative_solver_results_evidentiary": False,
            "independent_r14_raw_replay": r14_raw,
            "independent_r14_raw_replay_evidentiary": False,
        },
        "failure_validation": failure_result,
        "submitted_validation": submitted_result,
        "deterministic_replays": {
            "regenerated_profile_path": (
                REGENERATED_PROFILE_PATH.relative_to(ROOT).as_posix()
            ),
            "regenerated_profile_sha256": sha256_file(
                REGENERATED_PROFILE_PATH
            ),
            "profile_byte_identical": True,
            "submitted_validation_replay_path": (
                SUBMITTED_REPLAY_PATH.relative_to(ROOT).as_posix()
            ),
            "submitted_validation_replay_sha256": sha256_file(
                SUBMITTED_REPLAY_PATH
            ),
            "submitted_validation_byte_identical": True,
        },
        "report_provenance": report_result,
        "limitations": [
            (
                "the active-local CNFs omit inactive vertices, disjoint-"
                "point fixed support, support-sum equality completion, H, "
                "a 99-vertex adjacency matrix, and global SRG equations"
            ),
            (
                "the archived and independently replayed r14 UNSAT returns "
                "remain UNSAT_UNVERIFIED because no proof trace exists"
            ),
            (
                "five final timer returns remain TIMEOUT_UNKNOWN and the "
                "historical preliminary conflict-budget return remains "
                "BUDGET_UNKNOWN"
            ),
            (
                "the historical intermediate builder bytes for the budget "
                "probe are unavailable, so its execution provenance cannot "
                "be independently authenticated"
            ),
            (
                "the declared starting Git commit is internally consistent "
                "but was not authenticated because the verifier was "
                "explicitly forbidden from using Git"
            ),
            (
                "neither conditional n3=51 nor Conway-99 is resolved, and "
                "novelty remains unknown"
            ),
        ],
        "runtime": {
            "python": sys.version,
            "python_sat": pysat.__version__,
        },
    }


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_audit()
    if args.output is not None:
        write_json(args.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
