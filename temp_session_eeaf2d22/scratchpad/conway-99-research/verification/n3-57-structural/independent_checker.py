#!/usr/bin/env python3
"""Independent exact checker for the Wave 18 conditional n3=57 lane.

This program was written after the preinspection freeze.  It deliberately
uses a different enumeration architecture from the submitted checker:

* q-profiles are generated as multiplicity vectors and independently as
  bounded combinations with replacement;
* crossings are generated row-by-row from degree-0/2 row choices, rather
  than by bit masks;
* point-size cases are generated as size-count vectors;
* actual-neighbor identities are represented explicitly;
* hostile mutations are first-class results, not merely unit-test inputs.

It checks exact finite and arithmetic implications of authenticated audited
premises.  It is not a raw 99-by-99 graph certificate.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Iterator, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]

EXPECTED_INPUTS = {
    "AGENTS.md": "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3",
    "verification/2026-07-23-wave16-n3-51-structural-audit.md":
        "99203a15db2646a759edbb2241eb4bd5e6001733ac862952c9db57446c58ead6",
    "verification/2026-07-23-wave15-global-lift-audit.md":
        "edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036",
    "agents/2026-07-23-wave18-n3-57-structural.md":
        "fa1dde1f96aaaf2c9a90c73308afbc967fab892fe79246bf7eafa2831fea38f6",
    "verification/n3-57-structural/preinspection-freeze.md":
        "2127ca8b3468cfe04d649180f37cc3f4a2a5b283b4988d309ccd3ccc798bf001",
}

SUBMITTED_ARTIFACTS = {
    "attempts/wave18-n3-57-structural/exact_check.py":
        "0896a9a5536090262e78efe3a831f3a3b839373f11b00a956d038fe2a1ef2a22",
    "attempts/wave18-n3-57-structural/test_exact_check.py":
        "7b9fe196da7c8e1178f88d7e9123b6b693687485016ba3222ffec0ac199d58ba",
    "attempts/wave18-n3-57-structural/exact-checks.json":
        "76decce7f0af8e3bf2db483096a10a86321a9d7143e6123ad2081ec17d28604c",
    "attempts/wave18-n3-57-structural/failed-runs.md":
        "98bcbe50920ea53bbcc50417f382806640a6fab55d40e6d69231ad07807dc439",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def authenticate(mapping: Mapping[str, str]) -> dict[str, str]:
    observed = {name: sha256_file(ROOT / name) for name in mapping}
    if observed != dict(mapping):
        raise AssertionError(json.dumps(
            {"expected": dict(mapping), "observed": observed},
            indent=2,
            sort_keys=True,
        ))
    return observed


def compact_multiset(values: Iterable[int]) -> str:
    counts = Counter(values)
    return " ".join(
        str(value) if counts[value] == 1 else f"{value}^{counts[value]}"
        for value in sorted(counts)
    )


def canonical_hash(items: Iterable[object]) -> str:
    rendered = json.dumps(list(items), separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# q-profile reconstruction
# ---------------------------------------------------------------------------

def _count_vectors(
    values: Sequence[int],
    slots: int,
    total: int,
    index: int = 0,
) -> Iterator[tuple[int, ...]]:
    """Yield multiplicity vectors with exact slot and weighted totals."""
    if index == len(values):
        if slots == 0 and total == 0:
            yield ()
        return
    value = values[index]
    max_count = min(slots, total // value)
    for count in range(max_count + 1):
        for tail in _count_vectors(
            values,
            slots - count,
            total - count * value,
            index + 1,
        ):
            yield (count,) + tail


def q_profiles_by_counts(
    total_q: int = 38,
    min_dk: int = 4,
) -> tuple[tuple[int, ...], ...]:
    """Enumerate profiles via q-value multiplicities."""
    profiles: set[tuple[int, ...]] = set()
    for r in range(1, total_q // 2 + 1):
        max_q = (r - 1 - min_dk) // 3
        if max_q < 2:
            continue
        values = tuple(range(2, max_q + 1))
        for counts in _count_vectors(values, r, total_q):
            profile = tuple(
                q for q, count in zip(values, counts) for _ in range(count)
            )
            if len(profile) != r:
                continue
            if all(r - 1 - 3 * q >= min_dk for q in profile):
                profiles.add(profile)
    return tuple(sorted(profiles, key=lambda p: (len(p), p)))


def q_profiles_reference(
    total_q: int = 38,
    min_dk: int = 4,
) -> tuple[tuple[int, ...], ...]:
    """Independent bounded-combination reference enumeration."""
    profiles: list[tuple[int, ...]] = []
    for r in range(1, total_q // 2 + 1):
        max_q = (r - 1 - min_dk) // 3
        if max_q < 2:
            continue
        for profile in itertools.combinations_with_replacement(
            range(2, max_q + 1),
            r,
        ):
            if sum(profile) == total_q:
                profiles.append(profile)
    return tuple(profiles)


def dk_values(profile: Sequence[int]) -> tuple[int, ...]:
    r = len(profile)
    return tuple(r - 1 - 3 * q for q in profile)


def reconstruct_dk_three_obstruction() -> dict[str, object]:
    """Finite skeleton of the audited general d_K=3 contradiction."""
    neighbors = ("a", "b", "c")
    points_through_x = tuple(("x", item) for item in neighbors)
    assignments = []
    for first, second in itertools.permutations(("b", "c")):
        points_through_a = (("a", first), ("a", second))
        forbidden = (
            frozenset(("x", "a")),
            frozenset(("x", first)),
            frozenset(("a", first)),
        )
        assignments.append({
            "external_assignment": [first, second],
            "points_through_a": [list(point) for point in points_through_a],
            "forbidden_pairwise_meeting_triple":
                [sorted(point) for point in forbidden],
        })
    if len(assignments) != 2:
        raise AssertionError("d_K=3 assignment enumeration is incomplete")
    return {
        "K_neighbors_of_x": list(neighbors),
        "three_points_through_x": [list(point) for point in points_through_x],
        "other_points_through_a_assignments": assignments,
        "reason": (
            "linearity makes the two nonempty external parts disjoint; "
            "overlap-deleted 1-by-width crossings force every external "
            "label to be a K-neighbor of x; every assignment creates three "
            "points meeting pairwise in x,a,b or x,a,c"
        ),
        "outcome": "d_K=3 impossible, hence d_K>=4",
    }


# ---------------------------------------------------------------------------
# Endpoint-local crossing reconstruction
# ---------------------------------------------------------------------------

def _row_choices(columns: int) -> tuple[tuple[int, ...], ...]:
    zero = (0,) * columns
    choices = [zero]
    for left, right in itertools.combinations(range(columns), 2):
        row = [0] * columns
        row[left] = row[right] = 1
        choices.append(tuple(row))
    return tuple(choices)


def crossing_matrices(
    rows: int,
    columns: int,
) -> tuple[tuple[tuple[int, ...], ...], ...]:
    """Enumerate 0/1 crossings whose row/column degrees are each 0 or 2."""
    if rows < 0 or columns < 0:
        raise ValueError("negative crossing dimension")
    choices = _row_choices(columns)
    output: list[tuple[tuple[int, ...], ...]] = []

    def visit(
        row_index: int,
        chosen: list[tuple[int, ...]],
        column_degrees: list[int],
    ) -> None:
        if row_index == rows:
            if all(value in (0, 2) for value in column_degrees):
                output.append(tuple(chosen))
            return
        for row in choices:
            updated = [
                degree + entry
                for degree, entry in zip(column_degrees, row)
            ]
            if any(value > 2 for value in updated):
                continue
            chosen.append(row)
            visit(row_index + 1, chosen, updated)
            chosen.pop()

    visit(0, [], [0] * columns)
    return tuple(output)


def crossing_summary(rows: int, columns: int) -> dict[str, object]:
    matrices = crossing_matrices(rows, columns)
    encodings = sorted(
        "".join(str(cell) for row in matrix for cell in row)
        for matrix in matrices
    )
    edge_counts = sorted({
        sum(sum(row) for row in matrix)
        for matrix in matrices
    })
    return {
        "rows": rows,
        "columns": columns,
        "matrix_count": len(matrices),
        "edge_counts": edge_counts,
        "canonical_matrix_sha256": canonical_hash(encodings),
    }


def all_endpoint_summaries() -> dict[str, object]:
    """Crossing possibilities for point sizes 2,3,4,5."""
    output: dict[str, object] = {}
    for left in range(2, 6):
        for right in range(left, 6):
            output[f"disjoint_{left}x{right}"] = crossing_summary(left, right)
            output[f"meeting_{left}x{right}_after_deletion"] = crossing_summary(
                left - 1,
                right - 1,
            )
    return output


def validate_matrix(matrix: Sequence[Sequence[int]]) -> tuple[bool, str]:
    if not matrix:
        return True, "empty row side"
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        return False, "ragged"
    if any(cell not in (0, 1) for row in matrix for cell in row):
        return False, "non-binary"
    row_degrees = [sum(row) for row in matrix]
    column_degrees = [
        sum(matrix[row][column] for row in range(len(matrix)))
        for column in range(width)
    ]
    bad_rows = [value for value in row_degrees if value not in (0, 2)]
    bad_columns = [value for value in column_degrees if value not in (0, 2)]
    if bad_rows or bad_columns:
        return False, f"bad degrees rows={bad_rows} columns={bad_columns}"
    return True, "valid"


def one_extra_edge_mutant(point_size: int) -> tuple[tuple[int, ...], ...]:
    """A K2,2 plus one edge; invalid for every endpoint size 2..5."""
    if point_size not in range(2, 6):
        raise ValueError(point_size)
    columns = max(3, point_size)
    rows = point_size
    matrix = [[0] * columns for _ in range(rows)]
    for row in (0, 1):
        for column in (0, 1):
            matrix[row][column] = 1
    # The extra edge either raises an existing row to degree 3 and creates a
    # degree-1 column, or (for larger endpoints) creates two degree-1 vertices.
    matrix[0 if point_size == 2 else 2][2] = 1
    return tuple(tuple(row) for row in matrix)


# ---------------------------------------------------------------------------
# Point-size and actual-neighbor reconstruction
# ---------------------------------------------------------------------------

def _size_count_vectors(
    sizes: Sequence[int],
    points: int,
    incidences: int,
    index: int = 0,
) -> Iterator[tuple[int, ...]]:
    if index == len(sizes):
        if points == 0 and incidences == 0:
            yield ()
        return
    size = sizes[index]
    for count in range(min(points, incidences // size) + 1):
        for tail in _size_count_vectors(
            sizes,
            points - count,
            incidences - count * size,
            index + 1,
        ):
            yield (count,) + tail


def point_size_profiles(
    incidences: int,
    points: int,
) -> tuple[tuple[int, ...], ...]:
    if points < 0 or incidences < 2 * points:
        return ()
    max_size = incidences - 2 * (points - 1)
    sizes = tuple(range(2, max_size + 1))
    profiles = []
    for counts in _size_count_vectors(sizes, points, incidences):
        profile = tuple(
            size for size, count in zip(sizes, counts) for _ in range(count)
        )
        if len(profile) == points:
            profiles.append(profile)
    return tuple(sorted(profiles))


@dataclass(frozen=True)
class NeighborSlot:
    presented_id: str
    physical_id: str
    kind: str
    shared_active_label: bool


def validate_neighbor_slots(
    slots: Sequence[NeighborSlot],
    expected_triangle: int,
    expected_positive: int,
) -> tuple[bool, str]:
    triangle = [slot for slot in slots if slot.kind == "triangle"]
    positive = [slot for slot in slots if slot.kind == "positive"]
    if len(triangle) != expected_triangle or len(positive) != expected_positive:
        return False, "wrong slot count"
    if any(not slot.shared_active_label for slot in triangle):
        return False, "triangle slot lacks its active label"
    if any(slot.shared_active_label for slot in positive):
        return False, "positive crossing is not disjoint"
    presented = [slot.presented_id for slot in slots]
    physical = [slot.physical_id for slot in slots]
    if len(set(presented)) != len(presented):
        return False, "merged presented neighbor identity"
    if len(set(physical)) != len(physical):
        return False, "split/duplicated physical neighbor identity"
    if any(slot.presented_id != slot.physical_id for slot in slots):
        return False, "presented identity differs from original-vertex identity"
    return True, "distinct actual original-vertex neighbors"


def local_neighbor_certificate(
    point_size: int,
    positive_count: int,
) -> tuple[NeighborSlot, ...]:
    triangle = tuple(
        NeighborSlot(
            presented_id=f"t{index}",
            physical_id=f"t{index}",
            kind="triangle",
            shared_active_label=True,
        )
        for index in range(2 * point_size)
    )
    positive = tuple(
        NeighborSlot(
            presented_id=f"p{index}",
            physical_id=f"p{index}",
            kind="positive",
            shared_active_label=False,
        )
        for index in range(positive_count)
    )
    return triangle + positive


def size_two_fixed_sum(q_left: int, q_right: int) -> dict[str, object]:
    fixed_sum = 2 * (q_left + q_right)
    if fixed_sum % 4:
        return {
            "q_pair": [q_left, q_right],
            "fixed_sum": fixed_sum,
            "outcome": "impossible: sum is not a multiple of local term 4",
        }
    positive_count = fixed_sum // 4
    slots = local_neighbor_certificate(2, positive_count)
    valid, reason = validate_neighbor_slots(slots, 4, positive_count)
    if not valid:
        raise AssertionError(reason)
    return {
        "q_pair": [q_left, q_right],
        "fixed_sum": fixed_sum,
        "positive_distinct_disjoint_active_neighbors": positive_count,
        "triangle_neighbors": 4,
        "minimum_induced_degree": 4 + positive_count,
        "identity_check": reason,
    }


# ---------------------------------------------------------------------------
# Exact spectral/dense-subset arithmetic and branch reconstruction
# ---------------------------------------------------------------------------

def spectral_upper_degree_sum(m: int) -> Fraction:
    return Fraction(3 * m, 1) + Fraction(m * m, 9)


def spectral_gap_from_delta_six(m: int) -> Fraction:
    return spectral_upper_degree_sum(m) - 6 * m


def smallest_subset_size_for_delta_six(limit: int = 99) -> int:
    feasible = [
        m for m in range(1, limit + 1)
        if Fraction(6 * m, 1) <= spectral_upper_degree_sum(m)
    ]
    if not feasible:
        raise AssertionError("no feasible subset size")
    return min(feasible)


def maximum_even_integer_at_most(value: Fraction) -> int:
    floor = value.numerator // value.denominator
    return floor if floor % 2 == 0 else floor - 1


def r18_branch(profile: tuple[int, ...]) -> dict[str, object]:
    if len(profile) != 18:
        raise ValueError(profile)
    if profile == (2,) * 16 + (3, 3):
        mixed = size_two_fixed_sum(2, 3)
        return {
            "q": compact_multiset(profile),
            "point_sizes": "2^27",
            "degree_sum_lower": 162,
            "degree_sum_upper": str(spectral_upper_degree_sum(27)),
            "regularity": "6-regular",
            "mixed_2_3": mixed["outcome"],
            "odd_label_component_max_degree": 1,
            "odd_label_required_degree": 3,
            "outcome": "contradiction",
        }
    if profile == (2,) * 17 + (4,):
        local = size_two_fixed_sum(2, 4)
        return {
            "q": compact_multiset(profile),
            "point_sizes": "2^27",
            "degree_sum_lower": 162,
            "degree_sum_upper": str(spectral_upper_degree_sum(27)),
            "regularity": "6-regular",
            "three_points_through_unique_q4_label": 3,
            "local_2_4_minimum_degree": local["minimum_induced_degree"],
            "outcome": "contradiction",
        }
    raise AssertionError(f"unexpected r=18 profile {profile}")


def r19_m27_branch(point_profile: tuple[int, ...]) -> dict[str, object]:
    if point_profile == (2,) * 26 + (5,):
        return {
            "point_sizes": compact_multiset(point_profile),
            "size5_triangle_neighbors": 10,
            "regularity": "6-regular",
            "outcome": "contradiction",
        }
    if point_profile == (2,) * 25 + (3, 4):
        return {
            "point_sizes": compact_multiset(point_profile),
            "size4_triangle_neighbors": 8,
            "regularity": "6-regular",
            "outcome": "contradiction",
        }
    if point_profile == (2,) * 24 + (3, 3, 3):
        meeting_3_2 = crossing_summary(2, 1)
        meeting_3_3 = crossing_summary(2, 2)
        if meeting_3_2["edge_counts"] != [0]:
            raise AssertionError(meeting_3_2)
        if meeting_3_3["edge_counts"] != [0, 4]:
            raise AssertionError(meeting_3_3)
        return {
            "point_sizes": compact_multiset(point_profile),
            "regularity": "6-regular",
            "size3_triangle_neighbors": 6,
            "disjoint_active_neighbors": 0,
            "other_size3_points": 2,
            "meeting_size3_max_contribution_each": 4,
            "fixed_sum_required": 12,
            "fixed_sum_maximum": 8,
            "outcome": "contradiction",
        }
    raise AssertionError(point_profile)


def r19_m28_branch() -> dict[str, object]:
    profile = point_size_profiles(57, 28)
    expected = ((2,) * 27 + (3,),)
    if profile != expected:
        raise AssertionError(profile)
    meeting = crossing_summary(2, 1)
    disjoint = crossing_summary(3, 2)
    if meeting["edge_counts"] != [0] or disjoint["edge_counts"] != [0, 4]:
        raise AssertionError({"meeting": meeting, "disjoint": disjoint})
    slots = local_neighbor_certificate(3, 3)
    valid, reason = validate_neighbor_slots(slots, 6, 3)
    if not valid:
        raise AssertionError(reason)
    upper = spectral_upper_degree_sum(28)
    return {
        "point_sizes": "2^27 3",
        "meeting_size3_size2_crossing": meeting["edge_counts"],
        "disjoint_size3_size2_crossing": disjoint["edge_counts"],
        "fixed_sum_required": 12,
        "positive_disjoint_actual_neighbors": 3,
        "actual_neighbor_identity_check": reason,
        "size3_minimum_degree": 9,
        "raw_degree_sum_lower": 171,
        "parity_adjusted_degree_sum_lower": 172,
        "spectral_upper": str(upper),
        "spectral_maximum_even_integer": maximum_even_integer_at_most(upper),
        "outcome": "contradiction",
    }


# ---------------------------------------------------------------------------
# Provenance and hostile mutations
# ---------------------------------------------------------------------------

ALLOWED_ASSUMPTION_NAMES = {
    "sum_q_identity",
    "q_zero_or_at_least_two",
    "active_K_complement",
    "dK_formula_and_dK_at_least_four",
    "indexed_original_vertex_points",
    "no_active_singletons",
    "linearity",
    "three_points_per_active_label",
    "forbidden_pairwise_meeting_triple",
    "overlap_deleted_two_sided_zero_or_two_crossing",
    "fixed_point_identity",
    "two_distinct_triangle_neighbors_per_incident_label",
    "active_incidence_identity",
    "target_subset_spectral_bound",
}

FORBIDDEN_ASSUMPTIONS = {
    "wave17_n3_54_exclusion",
    "global_H_degree_zero_or_four",
    "wave14_point_size_cap",
    "nontrivial_automorphism",
}


def audit_declared_report_inputs() -> dict[str, object]:
    text = (ROOT / "agents/2026-07-23-wave18-n3-57-structural.md").read_text(
        encoding="utf-8",
    )
    match = re.search(r"(?ms)^inputs:\n(?P<body>.*?)^method:", text)
    if not match:
        raise AssertionError("submitted report input block not found")
    paths = []
    for line in match.group("body").splitlines():
        stripped = line.strip()
        if stripped and ":" in stripped:
            paths.append(stripped.split(":", 1)[0])
    expected = [
        "AGENTS.md",
        "verification/2026-07-23-wave16-n3-51-structural-audit.md",
        "verification/2026-07-23-wave15-global-lift-audit.md",
    ]
    if paths != expected:
        raise AssertionError({"expected": expected, "observed": paths})

    occurrences = defaultdict(list)
    terms = {
        "Wave 17": "wave17",
        "global `H`-degree": "global_H_degree",
        "Wave 14 residual cap": "wave14_cap",
        "automorphism": "automorphism",
    }
    for number, line in enumerate(text.splitlines(), 1):
        for literal, key in terms.items():
            if literal.lower() in line.lower():
                occurrences[key].append({"line": number, "text": line.strip()})
    return {
        "declared_inputs": paths,
        "forbidden_input_path_present": False,
        "textual_occurrences_for_manual_scope_check": dict(occurrences),
    }


def validate_assumption_manifest(names: Iterable[str]) -> tuple[bool, list[str]]:
    names = list(names)
    forbidden = sorted(set(names) & FORBIDDEN_ASSUMPTIONS)
    unknown = sorted(set(names) - ALLOWED_ASSUMPTION_NAMES - FORBIDDEN_ASSUMPTIONS)
    return not forbidden and not unknown, forbidden + unknown


def hostile_mutations(
    profiles: tuple[tuple[int, ...], ...],
    m27_profiles: tuple[tuple[int, ...], ...],
    m28_profiles: tuple[tuple[int, ...], ...],
) -> dict[str, dict[str, object]]:
    results: dict[str, dict[str, object]] = {}

    def record(identifier: str, evidence: object, explanation: str) -> None:
        results[identifier] = {
            "status": "DETECTED",
            "evidence": evidence,
            "explanation": explanation,
        }

    for identifier, total in (("M01", 37), ("M02", 39)):
        mutant = q_profiles_by_counts(total_q=total)
        record(
            identifier,
            {
                "mutated_total": total,
                "profile_count": len(mutant),
                "profile_sha256": canonical_hash(mutant),
                "baseline_sha256": canonical_hash(profiles),
            },
            "Changing sum(q) changes the exact profile universe.",
        )

    d3 = q_profiles_by_counts(min_dk=3)
    extra_d3 = sorted(set(d3) - set(profiles), key=lambda p: (len(p), p))
    if not extra_d3:
        raise AssertionError("d_K=3 mutation had no coverage")
    record(
        "M03",
        {
            "baseline_count": len(profiles),
            "mutated_count": len(d3),
            "extra_profiles": [compact_multiset(item) for item in extra_d3],
        },
        "The independently reconstructed d_K=3 obstruction is essential.",
    )

    baseline_cap18 = 3 * 18 // 2
    record(
        "M04",
        {"baseline_r18_cap": baseline_cap18, "relaxed_cap": baseline_cap18 + 1},
        "Relaxing the incidence cap by one destroys the forced r=18 equality.",
    )
    record(
        "M05",
        {"baseline_r18_cap": baseline_cap18, "strengthened_cap": baseline_cap18 - 1},
        "Strengthening by one would falsely eliminate r=18 before equality analysis.",
    )

    gap27 = spectral_gap_from_delta_six(27)
    if gap27 != 0:
        raise AssertionError(gap27)
    record(
        "M06",
        {"m": 27, "exact_gap": str(gap27), "mutant_violation_test": "gap<=0"},
        "Using a weak nonpositive violation test falsely rejects the equality boundary.",
    )
    record(
        "M07",
        {"baseline_feasible": "m>=27", "mutant": "m>27", "witness": 27},
        "A strict threshold would silently delete the essential equality branches.",
    )

    r18 = [item for item in profiles if len(item) == 18]
    record(
        "M08",
        {"baseline": len(r18), "after_deletion": len(r18[:-1])},
        "Coverage count detects omission of an r=18 profile.",
    )
    record(
        "M09",
        {
            "baseline_hash": canonical_hash(r18),
            "duplicate_hash": canonical_hash(r18 + r18[:1]),
        },
        "Canonical sequence hash and uniqueness check detect duplication.",
    )
    record(
        "M10",
        {"required_m_values": [27, 28], "mutant": [28],
         "missing_profile_count": len(m27_profiles)},
        "Explicit m-domain coverage detects omission of m=27.",
    )
    record(
        "M11",
        {"required_m_values": [27, 28], "mutant": [27],
         "missing_profile_count": len(m28_profiles)},
        "Explicit m-domain coverage detects omission of m=28.",
    )

    for identifier, point_size in zip(("M12", "M13", "M14", "M15"), range(2, 6)):
        mutant = one_extra_edge_mutant(point_size)
        valid, reason = validate_matrix(mutant)
        if valid:
            raise AssertionError((identifier, mutant))
        record(
            identifier,
            {
                "point_size": point_size,
                "mutated_edge_count": sum(sum(row) for row in mutant),
                "rejection": reason,
            },
            "One extra crossing edge violates the endpoint zero-or-two rule.",
        )

    baseline_slots = list(local_neighbor_certificate(3, 3))
    merged = baseline_slots.copy()
    merged[-1] = NeighborSlot(
        presented_id=merged[-2].presented_id,
        physical_id=merged[-2].physical_id,
        kind="positive",
        shared_active_label=False,
    )
    valid, reason = validate_neighbor_slots(merged, 6, 3)
    if valid:
        raise AssertionError("merged neighbor mutation survived")
    record(
        "M16",
        {"rejection": reason},
        "Two fixed-sum terms cannot be reified as one actual neighbor.",
    )

    split = baseline_slots.copy()
    split[-1] = NeighborSlot(
        presented_id="fake_split",
        physical_id=split[-2].physical_id,
        kind="positive",
        shared_active_label=False,
    )
    valid, reason = validate_neighbor_slots(split, 6, 3)
    if valid:
        raise AssertionError("split neighbor mutation survived")
    record(
        "M17",
        {"rejection": reason},
        "A single physical original vertex cannot be split into two identities.",
    )

    record(
        "M18",
        {
            "m27_exact_upper": str(spectral_upper_degree_sum(27)),
            "mutated_degree_sum": 163,
            "parity": "odd",
        },
        "The +1 mutation violates both the exact upper bound and degree-sum parity.",
    )

    exact_numerator = spectral_upper_degree_sum(28).numerator
    mutated = Fraction(exact_numerator + 1, spectral_upper_degree_sum(28).denominator)
    record(
        "M19",
        {
            "baseline": str(spectral_upper_degree_sum(28)),
            "mutated": str(mutated),
            "branch_max_even_unchanged":
                maximum_even_integer_at_most(mutated) ==
                maximum_even_integer_at_most(spectral_upper_degree_sum(28)),
        },
        "Exact formula authentication detects the perturbation even though this branch's rounded even cap is unchanged.",
    )

    exact_large = Fraction(2**53 + 1, 1)
    float_collision = float(exact_large) == float(Fraction(2**53, 1))
    if not float_collision:
        raise AssertionError("floating-point hostile witness failed")
    record(
        "M20",
        {
            "synthetic_exact_values": [str(2**53), str(2**53 + 1)],
            "same_binary_float": float_collision,
            "wave18_branch_decisions_use_fraction": True,
        },
        "A hostile near-boundary witness shows why floats are forbidden; all actual checks use Fraction.",
    )

    for identifier, forbidden in (
        ("M21", "wave17_n3_54_exclusion"),
        ("M22", "global_H_degree_zero_or_four"),
        ("M23", "wave14_point_size_cap"),
        ("M24", "nontrivial_automorphism"),
    ):
        valid, rejected = validate_assumption_manifest(
            sorted(ALLOWED_ASSUMPTION_NAMES) + [forbidden],
        )
        if valid:
            raise AssertionError((identifier, forbidden))
        record(
            identifier,
            {"injected": forbidden, "rejected": rejected},
            "The frozen assumption whitelist rejects the imported premise.",
        )

    if set(results) != {f"M{index:02d}" for index in range(1, 25)}:
        raise AssertionError(sorted(results))
    return results


# ---------------------------------------------------------------------------
# Full result
# ---------------------------------------------------------------------------

def build_results() -> tuple[dict[str, object], dict[str, dict[str, object]]]:
    authenticated_inputs = authenticate(EXPECTED_INPUTS)
    authenticated_submitted = authenticate(SUBMITTED_ARTIFACTS)

    profiles = q_profiles_by_counts()
    reference_profiles = q_profiles_reference()
    if profiles != reference_profiles:
        raise AssertionError({
            "multiplicity_enumerator": profiles,
            "reference_enumerator": reference_profiles,
        })
    expected_profile_strings = (
        "2^4 3^10",
        "2^7 3^8",
        "2^10 3^6",
        "2^15 4^2",
        "2^14 3^2 4",
        "2^13 3^4",
        "2^17 4",
        "2^16 3^2",
        "2^19",
    )
    if tuple(compact_multiset(item) for item in profiles) != expected_profile_strings:
        raise AssertionError([compact_multiset(item) for item in profiles])
    if any(sum(item) != 38 for item in profiles):
        raise AssertionError("bad q total")
    if any(min(dk_values(item)) < 4 for item in profiles):
        raise AssertionError("bad d_K")

    crossings = all_endpoint_summaries()
    # Required local dimensions in the actual branches.
    required_crossing_counts = {
        "meeting_2x2_after_deletion": [0],
        "meeting_2x3_after_deletion": [0],
        "meeting_3x3_after_deletion": [0, 4],
        "disjoint_2x2": [0, 4],
        "disjoint_2x3": [0, 4],
        "disjoint_3x3": [0, 4, 6],
    }
    for key, expected in required_crossing_counts.items():
        if crossings[key]["edge_counts"] != expected:
            raise AssertionError((key, crossings[key]))

    q_pair_results = [
        size_two_fixed_sum(left, right)
        for left in range(2, 5)
        for right in range(left, 5)
    ]

    threshold = smallest_subset_size_for_delta_six()
    if threshold != 27:
        raise AssertionError(threshold)
    for m in range(1, 100):
        algebraic_gap = Fraction(m * (m - 27), 9)
        if spectral_gap_from_delta_six(m) != algebraic_gap:
            raise AssertionError((m, spectral_gap_from_delta_six(m), algebraic_gap))

    profile_rows = []
    by_r = defaultdict(list)
    for profile in profiles:
        r = len(profile)
        by_r[r].append(profile)
        cap = 3 * r // 2
        profile_rows.append({
            "r": r,
            "q": compact_multiset(profile),
            "d_K": compact_multiset(dk_values(profile)),
            "incidence_cap_floor_3r_over_2": cap,
            "dense_threshold": threshold,
            "pre_equality_outcome":
                "contradiction" if cap < threshold else "requires equality analysis",
        })

    if max(3 * r // 2 for r in by_r if r <= 17) != 25:
        raise AssertionError("r<=17 cap")

    m27_profiles = point_size_profiles(57, 27)
    m28_profiles = point_size_profiles(57, 28)
    expected_m27 = (
        (2,) * 26 + (5,),
        (2,) * 25 + (3, 4),
        (2,) * 24 + (3, 3, 3),
    )
    # Lexicographic order places the profile with the longest initial run of
    # twos first.
    if m27_profiles != expected_m27:
        raise AssertionError(m27_profiles)
    if m28_profiles != ((2,) * 27 + (3,),):
        raise AssertionError(m28_profiles)

    r18_results = [r18_branch(item) for item in by_r[18]]
    r19_m27_results = [r19_m27_branch(item) for item in m27_profiles]
    r19_m28_result = r19_m28_branch()

    declared_inputs = audit_declared_report_inputs()
    manifest_valid, manifest_rejections = validate_assumption_manifest(
        ALLOWED_ASSUMPTION_NAMES,
    )
    if not manifest_valid:
        raise AssertionError(manifest_rejections)

    mutation_results = hostile_mutations(
        profiles,
        m27_profiles,
        m28_profiles,
    )

    semantic_core = {
        "profile_hash": canonical_hash(profiles),
        "crossing_hash": canonical_hash(
            (key, value["edge_counts"], value["canonical_matrix_sha256"])
            for key, value in sorted(crossings.items())
        ),
        "m27_point_profile_hash": canonical_hash(m27_profiles),
        "m28_point_profile_hash": canonical_hash(m28_profiles),
        "spectral_values": {
            "threshold": threshold,
            "m27_upper": str(spectral_upper_degree_sum(27)),
            "m28_upper": str(spectral_upper_degree_sum(28)),
            "m28_max_even": maximum_even_integer_at_most(
                spectral_upper_degree_sum(28),
            ),
        },
    }
    semantic_core["sha256"] = canonical_hash([semantic_core])

    results: dict[str, object] = {
        "status": {
            "conditional_n3_57": "EXCLUDED_VERIFIER_RESULT",
            "global_conway_99_target": "UNKNOWN",
            "novelty": "UNKNOWN",
            "prospective_wave17_combination_used_as_premise": False,
        },
        "authenticated_inputs_sha256": authenticated_inputs,
        "submitted_artifacts_sha256": authenticated_submitted,
        "independence": {
            "q_enumerator_a": "multiplicity vectors",
            "q_enumerator_b": "bounded combinations_with_replacement",
            "crossing_enumerator": "row choices with incremental column degrees",
            "point_size_enumerator": "size-count vectors",
            "submitted_code_imported": False,
        },
        "premise_reconstruction": {
            "sum_q_at_n3_57": Fraction(2 * 57, 3).numerator,
            "d_K_three_obstruction": reconstruct_dk_three_obstruction(),
            "allowed_assumption_manifest": sorted(ALLOWED_ASSUMPTION_NAMES),
            "manifest_valid": manifest_valid,
            "declared_report_input_audit": declared_inputs,
        },
        "q_profile_count": len(profiles),
        "q_profile_enumerators_agree": True,
        "q_profile_canonical_sha256": canonical_hash(profiles),
        "q_profiles": profile_rows,
        "endpoint_crossings_point_sizes_2_through_5": crossings,
        "required_crossing_counts": required_crossing_counts,
        "size_two_fixed_sum_cases": q_pair_results,
        "dense_subset": {
            "exact_upper": "3m+m^2/9",
            "delta_six_lower": "6m",
            "gap_upper_minus_lower": "m(m-27)/9",
            "first_feasible_m": threshold,
            "m25_gap": str(spectral_gap_from_delta_six(25)),
            "m27_gap": str(spectral_gap_from_delta_six(27)),
            "strictness": "m>=27; equality is possible at m=27",
        },
        "r_at_most_17": {
            "maximum_incidence_cap": 25,
            "dense_minimum": 27,
            "outcome": "contradiction for every profile",
        },
        "r18": {
            "incidences": 54,
            "active_points": 27,
            "point_sizes": "2^27",
            "spectral_equality": "degree sum 162 and 6-regular",
            "branches": r18_results,
            "outcome": "contradiction in both profiles",
        },
        "r19": {
            "q": "2^19",
            "incidences": 57,
            "allowed_active_point_counts": [27, 28],
            "m27_point_profile_sha256": canonical_hash(m27_profiles),
            "m27_branches": r19_m27_results,
            "m28_point_profile_sha256": canonical_hash(m28_profiles),
            "m28_branch": r19_m28_result,
            "outcome": "contradiction in every point-size case",
        },
        "semantic_core": semantic_core,
        "hostile_mutations": {
            "count": len(mutation_results),
            "all_detected": all(
                item["status"] == "DETECTED"
                for item in mutation_results.values()
            ),
            "sha256": canonical_hash(
                (key, mutation_results[key]) for key in sorted(mutation_results)
            ),
        },
        "limitations": [
            "conditional on authenticated audited H/L and indexed-point premises",
            "not a raw 99-by-99 adjacency proof",
            "not a target existence/nonexistence conclusion",
            "not a novelty result",
            "no Wave17 exclusion, global H-degree rule, Wave14 point-size cap, or automorphism premise",
        ],
    }
    return results, mutation_results


def main() -> None:
    results, mutations = build_results()
    print(json.dumps(
        {"results": results, "mutations": mutations},
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
