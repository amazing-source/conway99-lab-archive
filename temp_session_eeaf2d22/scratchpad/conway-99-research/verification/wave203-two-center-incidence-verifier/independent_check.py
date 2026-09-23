"""Exact source-blind checks for the Wave203 two-center incidence lemma.

This script replays finite-field coefficient algebra and integer incidence
bookkeeping only.  It does not enumerate graphs, flag families, covers, or
configurations.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence


MODULUS = 3
C4_ORDER = ("X_a", "X_b", "Y_a", "Y_b")
C4_GRAM = (
    (0, 1, 1, 2),
    (1, 0, 2, 1),
    (1, 2, 0, 1),
    (2, 1, 1, 0),
)


def mod_vector(values: Iterable[int]) -> tuple[int, ...]:
    return tuple(value % MODULUS for value in values)


def add_mod(*vectors: Sequence[int]) -> tuple[int, ...]:
    if not vectors:
        return ()
    width = len(vectors[0])
    assert all(len(vector) == width for vector in vectors)
    return mod_vector(sum(vector[index] for vector in vectors) for index in range(width))


def mat_vec_mod(
    matrix: Sequence[Sequence[int]], vector: Sequence[int]
) -> tuple[int, ...]:
    assert all(len(row) == len(vector) for row in matrix)
    return mod_vector(sum(entry * value for entry, value in zip(row, vector)) for row in matrix)


def rank_mod(matrix: Sequence[Sequence[int]]) -> int:
    rows = [list(mod_vector(row)) for row in matrix]
    if not rows:
        return 0
    row_count = len(rows)
    column_count = len(rows[0])
    pivot_row = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(pivot_row, row_count) if rows[row][column]),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        inverse = 1 if rows[pivot_row][column] == 1 else 2
        rows[pivot_row] = [
            (inverse * entry) % MODULUS for entry in rows[pivot_row]
        ]
        for row in range(row_count):
            if row == pivot_row:
                continue
            factor = rows[row][column]
            if factor:
                rows[row] = [
                    (left - factor * right) % MODULUS
                    for left, right in zip(rows[row], rows[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def endpoint_slot_count(total_star_blocks: int = 7, fixed_type_blocks: int = 2) -> int:
    assert total_star_blocks >= fixed_type_blocks
    return total_star_blocks - fixed_type_blocks


def flag_relation_vectors() -> dict[str, tuple[int, ...]]:
    # Global column order: T, S, X_a, X_b, Y_a, Y_b.
    forward = (1, 2, 2, 2, 0, 0)
    reverse = (2, 1, 0, 0, 2, 2)
    combined = add_mod(forward, reverse)
    return {
        "forward": forward,
        "reverse": reverse,
        "combined": combined,
        "surviving_c4": combined[2:],
    }


def selected_label_capacity(
    private_count: int, nonprivate_degrees: Sequence[int]
) -> dict[str, int | bool]:
    assert private_count >= 0
    assert all(2 <= degree <= 5 for degree in nonprivate_degrees)
    label_union = private_count + len(nonprivate_degrees)
    total_incidence = private_count + sum(nonprivate_degrees)
    lhs = total_incidence + 4 * private_count
    rhs = 5 * label_union
    return {
        "private_count": private_count,
        "label_union": label_union,
        "total_incidence": total_incidence,
        "lhs": lhs,
        "rhs": rhs,
        "slack": rhs - lhs,
        "holds": lhs <= rhs,
    }


def orientation_epsilon(
    orientation_multiplicities: Sequence[Sequence[int]],
) -> dict[str, int | bool]:
    """Evaluate epsilon and b for nonprivate labels.

    Each entry has one or two occupied orientation multiplicities.  The
    combined-capacity theorem is enforced label by label.
    """

    assert all(len(entry) in (1, 2) for entry in orientation_multiplicities)
    assert all(all(value >= 1 for value in entry) for entry in orientation_multiplicities)
    assert all(sum(entry) <= 5 for entry in orientation_multiplicities)
    epsilon = sum(5 - value for entry in orientation_multiplicities for value in entry)
    bidirectional = sum(len(entry) == 2 for entry in orientation_multiplicities)
    return {
        "epsilon": epsilon,
        "bidirectional_labels": bidirectional,
        "lower_bound": 5 * bidirectional,
        "holds": epsilon >= 5 * bidirectional,
    }


def build_result() -> dict:
    relations = flag_relation_vectors()
    checkerboard = (1, 2, 2, 1)
    all_equal = (1, 1, 1, 1)
    all_two = (2, 2, 2, 2)
    slot_count = endpoint_slot_count()

    assert slot_count == 5
    assert relations["combined"] == (0, 0, 2, 2, 2, 2)
    assert relations["surviving_c4"] == all_two
    assert rank_mod(C4_GRAM) == 3
    assert mat_vec_mod(C4_GRAM, checkerboard) == (0, 0, 0, 0)
    assert mat_vec_mod(C4_GRAM, all_equal) == all_equal
    assert mat_vec_mod(C4_GRAM, all_two) == all_two

    # Wave202 aggregate/local-equality control, now oriented with b=0.
    private_count = 3123
    nonprivate_degrees = [2] * 234 + [3] * 3
    capacity_control = selected_label_capacity(private_count, nonprivate_degrees)
    epsilon_control = orientation_epsilon([[2]] * 234 + [[3]] * 3)
    assert capacity_control["total_incidence"] == 3600 == 3 * 1200
    assert capacity_control["label_union"] == 3360
    assert capacity_control["slack"] == 708
    assert epsilon_control["epsilon"] == 708
    assert epsilon_control["bidirectional_labels"] == 0

    return {
        "format": "wave203-two-center-incidence-independent-v1",
        "claim": {
            "combined_capacity": "m_(x->y)+m_(y->x)<=5",
            "status": "VERIFIED_CONDITIONALLY",
        },
        "conditional_scope": {
            "prism_free_rank_11_endpoint": True,
            "uses_verified_canonical_flag_relation": True,
            "uses_verified_wave181_c4_gram": True,
            "graph_or_flag_enumeration": False,
        },
        "slot_geometry": {
            "star_blocks_per_endpoint": 7,
            "fixed_blocks_for_nonedge_type": 2,
            "remaining_blocks_each_side": slot_count,
            "forward_partial_map": (
                "an x->y flag with leaf T maps to the unique third "
                "x-star block S in A_x(T)"
            ),
            "forward_injective_reason": (
                "equal slots give equal A_x sets; fixed-center A-injectivity "
                "then gives the same flag"
            ),
            "reverse_map": (
                "a y->x flag maps to its leaf triangle S, one of the same "
                "five remaining x-star blocks"
            ),
            "reverse_injective_reason": (
                "a canonical flag is determined by its center and leaf triangle"
            ),
            "matched_slot_reverse_reason": (
                "S in A_x(T) means j(S,T)=2; since T is a y-star block, "
                "T is the reverse flag's third A_y(S) block"
            ),
        },
        "global_relation_audit": {
            "column_order": ["T", "S", "X_a", "X_b", "Y_a", "Y_b"],
            "forward": list(relations["forward"]),
            "reverse": list(relations["reverse"]),
            "sum_mod_3": list(relations["combined"]),
            "surviving_c4_coefficients": list(relations["surviving_c4"]),
            "normalization_required": (
                "both equations use the globally fixed z-columns and leaf "
                "coefficient 1, star coefficients 2"
            ),
        },
        "canonical_c4": {
            "order": list(C4_ORDER),
            "four_columns_distinct": True,
            "distinctness_reason": (
                "the two common neighbors are nonadjacent, giving two "
                "different blocks at each endpoint; a block through both "
                "nonadjacent endpoints cannot be a graph triangle"
            ),
            "gram": [list(row) for row in C4_GRAM],
            "rank_mod_3": rank_mod(C4_GRAM),
            "checkerboard": list(checkerboard),
            "checkerboard_image": list(mat_vec_mod(C4_GRAM, checkerboard)),
            "all_equal": list(all_equal),
            "all_equal_image": list(mat_vec_mod(C4_GRAM, all_equal)),
            "all_two_image": list(mat_vec_mod(C4_GRAM, all_two)),
            "collision_status": "IMPOSSIBLE",
        },
        "counting_consequences": {
            "selected_capacity": "3n3+4p3<=5|U|",
            "bidirectional_loss": "epsilon>=5b",
            "orientation_identity": "T=|U|+b",
            "uniform_Q_ge_7060": False,
            "reason": (
                "the theorem supplies no positive lower bound on b; b=0 "
                "is compatible with all currently checked scalar rows"
            ),
        },
        "b_zero_control": {
            "asserted_object": False,
            "n3": 1200,
            "p3": private_count,
            "nonprivate_multiplicity_profile": {"2": 234, "3": 3},
            "label_union": capacity_control["label_union"],
            "total_selected_incidence": capacity_control["total_incidence"],
            "capacity_slack": capacity_control["slack"],
            "epsilon": epsilon_control["epsilon"],
            "b": epsilon_control["bidirectional_labels"],
            "Q0": 7059,
            "interpretation": (
                "aggregate and local-equality arithmetic control only; not a "
                "graph, code, cover, flag family, or existence claim"
            ),
        },
        "boundary": {
            "current_conditional_Q_lower": 7059,
            "Q_ge_7060_proved": False,
            "rank_11_excluded": False,
            "endpoint_excluded": False,
            "conway_99": "UNKNOWN",
            "external_novelty": "UNKNOWN",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--print", action="store_true", dest="print_result")
    args = parser.parse_args()
    result = build_result()
    if args.verify is not None:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if expected != result:
            raise SystemExit("FAIL: frozen independent result differs")
        print("PASS: source-blind Wave203 result matches")
    if args.print_result:
        print(json.dumps(result, indent=2, sort_keys=True))
    if args.verify is None and not args.print_result:
        parser.error("choose --verify PATH or --print")


if __name__ == "__main__":
    main()
