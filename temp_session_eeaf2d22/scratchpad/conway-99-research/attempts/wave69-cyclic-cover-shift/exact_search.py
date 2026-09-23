#!/usr/bin/env python3
"""Exact restricted searches for the Wave 69 cyclic-cover shift.

This module uses only the Python standard library.  It does not assume that a
hypothetical srg(99,14,1,2) has any automorphism.  Instead, it asks the
restricted question whether one could have a *specified* semiregular C_11
action with nine vertex orbits.  A separate fixed-point lemma then proves that
every nonidentity order-11 automorphism would be semiregular, so quotient
nonexistence also excludes order-11 symmetry and vertex-transitive targets.

For such an action, the equitable quotient Q is a symmetric nonnegative
integer 9 by 9 matrix satisfying

    Q 1 = 14 1,
    Q^2 + Q = 12 I + 22 J,

and its diagonal is even.  The 3- and -4-eigenspaces fixed by C_11 both have
dimension four, so trace(Q)=10.  These conditions leave three possible sorted
diagonals and seven possible sorted off-diagonal row shapes.

The exhaustive search has two modes:

* ``unpruned`` fixes only the harmless convention that the diagonal is sorted;
  it enumerates every remaining labeled row choice.
* ``canonical`` additionally orders the still-unassigned vertices by their
  already exposed column signatures inside each equal-diagonal class.

Both modes are deterministic and emit a transcript digest and exact branch
counts.  Discovery code may label the resulting claim DERIVED, never VERIFIED.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations_with_replacement
from pathlib import Path
from typing import Iterable, Iterator, Sequence


ORDER = 99
VALENCY = 14
LAMBDA = 1
MU = 2
AUTOMORPHISM_ORDER = 11
ORBIT_COUNT = 9


EXPECTED_ROW_SHAPES: dict[int, tuple[tuple[int, ...], ...]] = {
    0: (
        (0, 0, 2, 2, 2, 2, 3, 3),
        (0, 1, 1, 1, 2, 3, 3, 3),
        (0, 1, 1, 2, 2, 2, 2, 4),
        (1, 1, 1, 1, 1, 2, 3, 4),
    ),
    2: (
        (0, 0, 1, 1, 2, 2, 3, 3),
        (0, 1, 1, 1, 1, 2, 2, 4),
    ),
    4: ((1, 1, 1, 1, 1, 1, 2, 2),),
}

EXPECTED_DIAGONALS: tuple[tuple[int, ...], ...] = (
    (0, 0, 0, 0, 0, 0, 2, 4, 4),
    (0, 0, 0, 0, 0, 2, 2, 2, 4),
    (0, 0, 0, 0, 2, 2, 2, 2, 2),
)


def canonical_json_bytes(value: object) -> bytes:
    """Return stable UTF-8 JSON bytes."""

    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("ascii")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def derive_srg_eigenvalue_multiplicities() -> dict[int, int]:
    """Derive the three adjacency eigenvalue multiplicities exactly."""

    # A^2 = 12 I - A + 2 J.  On 1-perp, x^2+x-12=0, hence
    # x in {3,-4}.  If f+g=98 and 14+3f-4g=trace(A)=0, then
    # f=54 and g=44.
    f_numerator = 4 * (ORDER - 1) - VALENCY
    if f_numerator % 7:
        raise AssertionError("nonintegral 3-eigenvalue multiplicity")
    f = f_numerator // 7
    g = ORDER - 1 - f
    result = {VALENCY: 1, 3: f, -4: g}
    if result != {14: 1, 3: 54, -4: 44}:
        raise AssertionError(result)
    return result


def derive_fixed_eigenspace_multiplicities() -> dict[int, int]:
    """Derive the quotient multiplicities from the rational C_11 action.

    A nontrivial irreducible rational representation of C_11 has dimension
    phi(11)=10.  If r is the fixed dimension in the 54-dimensional
    3-eigenspace, then 54-r is divisible by 10.  Since the total fixed space
    has dimension nine and includes the all-ones vector, 0 <= r <= 8, forcing
    r=4.  The -4 fixed dimension is then four as well.
    """

    multiplicities = derive_srg_eigenvalue_multiplicities()
    candidates = [
        r
        for r in range(ORBIT_COUNT)
        if (multiplicities[3] - r) % (AUTOMORPHISM_ORDER - 1) == 0
    ]
    if candidates != [4]:
        raise AssertionError(candidates)
    r = candidates[0]
    minus_four_fixed = ORBIT_COUNT - 1 - r
    if (multiplicities[-4] - minus_four_fixed) % (
        AUTOMORPHISM_ORDER - 1
    ):
        raise AssertionError("incompatible -4 rational representation")
    result = {VALENCY: 1, 3: r, -4: minus_four_fixed}
    if result != {14: 1, 3: 4, -4: 4}:
        raise AssertionError(result)
    return result


def derive_row_shapes() -> dict[int, tuple[tuple[int, ...], ...]]:
    """Enumerate all off-diagonal row multisets from the diagonal equation."""

    result: dict[int, tuple[tuple[int, ...], ...]] = {}
    for diagonal in range(0, VALENCY + 1, 2):
        # From (Q^2+Q)_ii=34:
        #   diagonal^2 + sum(offdiag^2) + diagonal = 34.
        target_sum = VALENCY - diagonal
        target_square_sum = (
            VALENCY - MU + MU * AUTOMORPHISM_ORDER
            - diagonal * diagonal
            - diagonal
        )
        if target_sum < 0 or target_square_sum < 0:
            continue
        shapes = tuple(
            values
            for values in combinations_with_replacement(
                range(target_sum + 1), ORBIT_COUNT - 1
            )
            if sum(values) == target_sum
            and sum(value * value for value in values) == target_square_sum
        )
        if shapes:
            result[diagonal] = shapes
    if result != EXPECTED_ROW_SHAPES:
        raise AssertionError(
            f"row-shape derivation changed: expected {EXPECTED_ROW_SHAPES}, got {result}"
        )
    return result


def derive_diagonal_cases() -> tuple[tuple[int, ...], ...]:
    """Enumerate all sorted diagonal sequences with quotient trace ten."""

    fixed = derive_fixed_eigenspace_multiplicities()
    trace = sum(eigenvalue * multiplicity for eigenvalue, multiplicity in fixed.items())
    if trace != 10:
        raise AssertionError(trace)
    cases = tuple(
        values
        for values in combinations_with_replacement(
            tuple(EXPECTED_ROW_SHAPES), ORBIT_COUNT
        )
        if sum(values) == trace
    )
    if cases != EXPECTED_DIAGONALS:
        raise AssertionError(
            f"diagonal derivation changed: expected {EXPECTED_DIAGONALS}, got {cases}"
        )
    return cases


def unique_multiset_permutations(values: Sequence[int]) -> Iterator[tuple[int, ...]]:
    """Yield multiset permutations in deterministic lexicographic order."""

    counts = Counter(values)
    keys = sorted(counts)
    output = [0] * len(values)

    def visit(position: int) -> Iterator[tuple[int, ...]]:
        if position == len(output):
            yield tuple(output)
            return
        for value in keys:
            if counts[value] == 0:
                continue
            counts[value] -= 1
            output[position] = value
            yield from visit(position + 1)
            counts[value] += 1

    yield from visit(0)


def derive_row_templates() -> dict[int, tuple[tuple[int, ...], ...]]:
    shapes = derive_row_shapes()
    return {
        diagonal: tuple(
            sorted(
                permutation
                for shape in diagonal_shapes
                for permutation in unique_multiset_permutations(shape)
            )
        )
        for diagonal, diagonal_shapes in shapes.items()
    }


def build_prefix_indices(
    diagonal: Sequence[int],
) -> tuple[dict[tuple[int, ...], tuple[tuple[int, ...], ...]], ...]:
    """Index admissible full rows by their already fixed symmetric prefix."""

    templates = derive_row_templates()
    indices: list[dict[tuple[int, ...], tuple[tuple[int, ...], ...]]] = []
    for vertex, diagonal_entry in enumerate(diagonal):
        buckets: defaultdict[tuple[int, ...], list[tuple[int, ...]]] = defaultdict(list)
        for off_diagonal in templates[diagonal_entry]:
            row = (
                off_diagonal[:vertex]
                + (diagonal_entry,)
                + off_diagonal[vertex:]
            )
            buckets[row[:vertex]].append(row)
        indices.append(
            {
                prefix: tuple(sorted(rows))
                for prefix, rows in sorted(buckets.items())
            }
        )
    return tuple(indices)


def dot_equation_holds(
    new_row: Sequence[int], old_row: Sequence[int], old_vertex: int
) -> bool:
    """Check (Q^2+Q)_(new,old)=22 once both rows are fully selected."""

    return (
        sum(left * right for left, right in zip(new_row, old_row))
        + new_row[old_vertex]
        == MU * AUTOMORPHISM_ORDER
    )


def canonical_unassigned_signatures(
    rows: Sequence[Sequence[int]],
    new_row: Sequence[int],
    diagonal: Sequence[int],
    vertex: int,
) -> bool:
    """Canonical augmentation inside residual equal-diagonal classes.

    After exposing row ``vertex``, the column signatures of unassigned
    vertices are required to be lexicographically sorted inside each diagonal
    class.  This is only used in the optional ``canonical`` cross-check.  The
    ``unpruned`` proof search does not use this function.
    """

    for diagonal_entry in sorted(set(diagonal)):
        vertices = [
            other
            for other in range(vertex + 1, ORBIT_COUNT)
            if diagonal[other] == diagonal_entry
        ]
        signatures = [
            tuple(row[other] for row in rows) + (new_row[other],)
            for other in vertices
        ]
        if signatures != sorted(signatures):
            return False
    return True


@dataclass
class SearchCounters:
    nodes: int
    solutions: int
    branches_by_depth: Counter[int]
    raw_candidates_by_depth: Counter[int]
    canonical_rejections_by_depth: Counter[int]
    dot_rejections_by_depth: Counter[int]
    leaves: Counter[str]

    @classmethod
    def empty(cls) -> "SearchCounters":
        return cls(
            nodes=0,
            solutions=0,
            branches_by_depth=Counter(),
            raw_candidates_by_depth=Counter(),
            canonical_rejections_by_depth=Counter(),
            dot_rejections_by_depth=Counter(),
            leaves=Counter(),
        )


def counter_as_string_dict(counter: Counter[object]) -> dict[str, int]:
    return {
        str(key): counter[key]
        for key in sorted(counter, key=lambda item: str(item))
    }


def search_diagonal_case(
    diagonal: Sequence[int], *, canonical: bool
) -> dict[str, object]:
    """Exhaust one sorted diagonal case and return deterministic telemetry."""

    diagonal_tuple = tuple(diagonal)
    if diagonal_tuple not in EXPECTED_DIAGONALS:
        raise ValueError(f"unexpected diagonal case: {diagonal_tuple}")

    indices = build_prefix_indices(diagonal_tuple)
    rows: list[tuple[int, ...]] = []
    counters = SearchCounters.empty()
    transcript = hashlib.sha256()
    mode = "canonical" if canonical else "unpruned"
    transcript.update(canonical_json_bytes({"diagonal": diagonal_tuple, "mode": mode}))

    def visit(vertex: int) -> None:
        counters.nodes += 1
        transcript.update(b"N")
        transcript.update(bytes((vertex,)))
        for row in rows:
            transcript.update(bytes(row))

        if vertex == ORBIT_COUNT:
            counters.solutions += 1
            counters.leaves["solution"] += 1
            transcript.update(b"S")
            return

        prefix = tuple(rows[old_vertex][vertex] for old_vertex in range(vertex))
        candidates = indices[vertex].get(prefix, ())
        counters.raw_candidates_by_depth[vertex] += len(candidates)
        if not candidates:
            counters.leaves[f"empty_prefix_{vertex}"] += 1
            transcript.update(b"E")
            transcript.update(bytes((vertex,)))
            return

        accepted = 0
        canonical_rejections = 0
        dot_rejections = 0
        for row in candidates:
            if canonical and not canonical_unassigned_signatures(
                rows, row, diagonal_tuple, vertex
            ):
                canonical_rejections += 1
                continue
            if not all(
                dot_equation_holds(row, rows[old_vertex], old_vertex)
                for old_vertex in range(vertex)
            ):
                dot_rejections += 1
                continue
            accepted += 1
            counters.branches_by_depth[vertex] += 1
            rows.append(row)
            visit(vertex + 1)
            rows.pop()

        counters.canonical_rejections_by_depth[vertex] += canonical_rejections
        counters.dot_rejections_by_depth[vertex] += dot_rejections
        transcript.update(b"R")
        transcript.update(bytes((vertex,)))
        for value in (
            len(candidates),
            canonical_rejections,
            dot_rejections,
            accepted,
        ):
            transcript.update(value.to_bytes(8, "little"))
        if accepted == 0:
            counters.leaves[f"no_accepted_{vertex}"] += 1

    visit(0)
    return {
        "mode": mode,
        "diagonal": list(diagonal_tuple),
        "nodes": counters.nodes,
        "solutions": counters.solutions,
        "branches_by_depth": counter_as_string_dict(counters.branches_by_depth),
        "raw_candidates_by_depth": counter_as_string_dict(
            counters.raw_candidates_by_depth
        ),
        "canonical_rejections_by_depth": counter_as_string_dict(
            counters.canonical_rejections_by_depth
        ),
        "dot_rejections_by_depth": counter_as_string_dict(
            counters.dot_rejections_by_depth
        ),
        "leaves": counter_as_string_dict(counters.leaves),
        "transcript_sha256": transcript.hexdigest(),
    }


def derive_cayley_fourier_obstruction() -> dict[str, object]:
    """Return the exact arithmetic behind the abelian-Cayley contradiction."""

    multiplicities = derive_srg_eigenvalue_multiplicities()
    if multiplicities[3] != 54 or multiplicities[-4] != 44:
        raise AssertionError(multiplicities)

    values: dict[str, dict[str, int | bool]] = {}
    for indicator in (0, 1):
        numerator = ORDER * indicator - 18
        values[str(indicator)] = {
            "indicator": indicator,
            "numerator": numerator,
            "denominator": 7,
            "remainder_mod_7": numerator % 7,
            "is_integer": numerator % 7 == 0,
        }
    if any(record["is_integer"] for record in values.values()):
        raise AssertionError(values)

    return {
        "group_order": ORDER,
        "group_isomorphism_types": ["C99", "C3xC3xC11"],
        "sylow_argument": {
            "n_11_divides": 9,
            "n_11_congruent_to_1_mod": 11,
            "n_11": 1,
            "aut_C11_order": 10,
            "gcd_order_9_aut_order_10": 1,
        },
        "principal_character_value": VALENCY,
        "nonprincipal_character_values": {"3": 54, "-4": 44},
        "inversion_identity_for_nonidentity_g": (
            "99*1_D(g)=14+3*S_X(g)-4*(-1-S_X(g))=18+7*S_X(g)"
        ),
        "S_X_values_by_membership": values,
        "contradiction": (
            "S_X(g) is a sum of roots of unity, hence an algebraic integer; "
            "Fourier inversion makes it rational but nonintegral for either "
            "membership value, impossible for a rational algebraic integer."
        ),
    }


def derive_order_11_fixed_point_obstruction() -> dict[str, object]:
    """Return the exact fixed-point count argument for order-11 automorphisms.

    If ``f`` vertices are fixed, then ``f`` is a multiple of 11.  Every fixed
    vertex has fixed degree 3 or 14 because its remaining neighbors lie in
    11-cycles.  A fixed pair has all of its one or two common neighbors fixed.
    Double-counting length-two walks from a fixed vertex ``i`` to other fixed
    vertices gives

        sum_(j adjacent_F i) d_j = 2 f - 2.

    The returned arithmetic records the elimination of every positive fixed
    count for a nonidentity automorphism.
    """

    possible_fixed_counts = list(range(0, ORDER + 1, AUTOMORPHISM_ORDER))
    if possible_fixed_counts != [0, 11, 22, 33, 44, 55, 66, 77, 88, 99]:
        raise AssertionError(possible_fixed_counts)

    # f=11: degree 14 is impossible in an 11-vertex fixed graph, so every
    # fixed degree is 3.  The neighbor-degree sum is 3*3=9, not 2f-2=20.
    f11_neighbor_sum = 3 * 3
    f11_required_sum = 2 * 11 - 2
    if f11_neighbor_sum == f11_required_sum:
        raise AssertionError("f=11 unexpectedly survives")

    # f=22: for a degree-3 fixed vertex, if x of its neighbors have degree 14,
    # then 3(3-x)+14x=42, giving x=3.  For a degree-14 fixed vertex, if y
    # neighbors have degree 14, then 3(14-y)+14y=42, giving y=0.
    f22_required_sum = 2 * 22 - 2
    low_high_numerator = f22_required_sum - 3 * 3
    high_high_numerator = f22_required_sum - 3 * 14
    if low_high_numerator % 11 or high_high_numerator % 11:
        raise AssertionError("f=22 neighbor-type counts not integral")
    low_high_neighbors = low_high_numerator // 11
    high_high_neighbors = high_high_numerator // 11
    if (low_high_neighbors, high_high_neighbors) != (3, 0):
        raise AssertionError((low_high_neighbors, high_high_neighbors))

    # For f>=33, a low fixed degree would have neighbor-degree sum at most
    # 3*14=42, while 2f-2>=64.  Therefore all fixed degrees would be 14, and
    # the same identity would force 14*14=2f-2, namely f=99.
    threshold_required_sum = 2 * 33 - 2
    low_degree_max_neighbor_sum = 3 * 14
    all_high_forced_f_numerator = 14 * 14 + 2
    if all_high_forced_f_numerator % 2:
        raise AssertionError("forced fixed count is not integral")
    all_high_forced_f = all_high_forced_f_numerator // 2
    if not threshold_required_sum > low_degree_max_neighbor_sum:
        raise AssertionError("large fixed-count inequality failed")
    if all_high_forced_f != 99:
        raise AssertionError(all_high_forced_f)

    return {
        "possible_fixed_counts_before_local_constraints": possible_fixed_counts,
        "fixed_degrees": [3, 14],
        "neighbor_degree_identity": (
            "sum_(j adjacent_F i) d_j = 2*f-2"
        ),
        "f_11": {
            "all_fixed_degrees": 3,
            "neighbor_degree_sum": f11_neighbor_sum,
            "required_sum": f11_required_sum,
            "status": "CONTRADICTION",
        },
        "f_22": {
            "required_sum": f22_required_sum,
            "high_neighbors_of_degree_3_vertex": low_high_neighbors,
            "high_neighbors_of_degree_14_vertex": high_high_neighbors,
            "fixed_graph_consequence": "BIPARTITE",
            "contradiction": (
                "Every fixed edge has its unique common neighbor fixed, so "
                "the fixed graph contains a triangle through every edge."
            ),
            "status": "CONTRADICTION",
        },
        "f_at_least_33": {
            "minimum_required_neighbor_degree_sum": threshold_required_sum,
            "maximum_sum_for_degree_3_vertex": low_degree_max_neighbor_sum,
            "all_degrees_forced_to": 14,
            "neighbor_degree_identity_forces_f": all_high_forced_f,
            "status_for_nonidentity": "CONTRADICTION",
        },
        "only_nonidentity_fixed_count": 0,
        "conclusion": (
            "Every nonidentity automorphism of order 11 is fixed-point-free "
            "and hence semiregular."
        ),
        "vertex_transitive_consequence": (
            "A vertex-transitive automorphism group has order divisible by "
            "99, hence contains an element of order 11 by Cauchy's theorem."
        ),
    }


def generate_results(mode: str) -> dict[str, object]:
    """Generate the exact Wave 69 result object."""

    if mode not in {"canonical", "unpruned", "both"}:
        raise ValueError(mode)

    row_shapes = derive_row_shapes()
    row_templates = derive_row_templates()
    diagonals = derive_diagonal_cases()
    modes = ("canonical", "unpruned") if mode == "both" else (mode,)
    searches: dict[str, list[dict[str, object]]] = {}
    for selected_mode in modes:
        searches[selected_mode] = [
            search_diagonal_case(
                diagonal, canonical=selected_mode == "canonical"
            )
            for diagonal in diagonals
        ]

    for records in searches.values():
        if any(record["solutions"] != 0 for record in records):
            raise AssertionError("unexpected quotient candidate")

    result: dict[str, object] = {
        "schema": "wave69-cyclic-cover-shift-exact-v1",
        "claim_label": "DERIVED",
        "novelty": "UNKNOWN",
        "parameters": {
            "v": ORDER,
            "k": VALENCY,
            "lambda": LAMBDA,
            "mu": MU,
        },
        "restricted_hypothesis": (
            "A hypothetical srg(99,14,1,2) admits a specified semiregular "
            "automorphism of order 11 with nine vertex orbits."
        ),
        "srg_eigenvalue_multiplicities": {
            str(key): value
            for key, value in derive_srg_eigenvalue_multiplicities().items()
        },
        "quotient_eigenvalue_multiplicities": {
            str(key): value
            for key, value in derive_fixed_eigenspace_multiplicities().items()
        },
        "quotient_trace": 10,
        "row_shapes_off_diagonal": {
            str(diagonal): [list(shape) for shape in shapes]
            for diagonal, shapes in row_shapes.items()
        },
        "row_template_counts": {
            str(diagonal): len(templates)
            for diagonal, templates in row_templates.items()
        },
        "sorted_diagonal_cases": [list(diagonal) for diagonal in diagonals],
        "searches": searches,
        "quotient_candidate_count": 0,
        "cyclic_11_lift_status": (
            "EMPTY_AFTER_EXHAUSTIVE_QUOTIENT_SEARCH"
            if "unpruned" in searches
            else "EMPTY_IN_CANONICAL_QUOTIENT_CROSS_CHECK"
        ),
        "order_11_fixed_point_obstruction": (
            derive_order_11_fixed_point_obstruction()
        ),
        "order_11_automorphism_candidate_count": 0,
        "vertex_transitive_target_status": "EXCLUDED_IN_RESTRICTED_DERIVATION",
        "cayley_fourier_obstruction": derive_cayley_fourier_obstruction(),
        "scope_warning": (
            "The fixed-point lemma plus quotient search excludes order-11 "
            "automorphisms, hence vertex-transitive and Cayley realizations. "
            "It does not exclude an arbitrary target without order-11 "
            "symmetry."
        ),
    }
    semantic = dict(result)
    result["semantic_sha256"] = sha256_bytes(canonical_json_bytes(semantic))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("canonical", "unpruned", "both"),
        default="canonical",
        help="search mode; 'both' includes the complete unpruned proof search",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="optional path for canonical JSON; stdout is used when omitted",
    )
    args = parser.parse_args()

    payload = canonical_json_bytes(generate_results(args.mode))
    if args.output is None:
        print(payload.decode("ascii"), end="")
    else:
        args.output.write_bytes(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
