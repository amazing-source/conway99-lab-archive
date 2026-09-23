#!/usr/bin/env python3
"""Exact Wave 204 proof-A checks for the slot-holonomy boundary.

The controls are partial ternary orthogonal configurations, not Conway-99
graphs or full endpoint codes.  Arithmetic is over F_3 throughout.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence

P = 3
DIM = 11
FORM = (1,) * 10 + (2,)
ZERO = (0,) * DIM

Vector = tuple[int, ...]
Permutation = tuple[int, ...]


def vec(values: Sequence[int]) -> Vector:
    if len(values) != DIM:
        raise ValueError("wrong vector dimension")
    return tuple(value % P for value in values)


def add(*vectors: Vector) -> Vector:
    return tuple(sum(entries) % P for entries in zip(*vectors))


def neg(vector: Vector) -> Vector:
    return tuple((-entry) % P for entry in vector)


def sub(left: Vector, right: Vector) -> Vector:
    return add(left, neg(right))


def dot(left: Vector, right: Vector, form: Sequence[int] = FORM) -> int:
    return sum(coefficient * x * y for coefficient, x, y in zip(form, left, right)) % P


def canonical_projective(vector: Vector) -> Vector:
    if vector == ZERO:
        raise ValueError("zero has no projective class")
    first = next(entry for entry in vector if entry)
    scale = 1 if first == 1 else 2
    return tuple(scale * entry % P for entry in vector)


def rank_mod3(rows: Iterable[Sequence[int]]) -> int:
    matrix = [[entry % P for entry in row] for row in rows]
    if not matrix:
        return 0
    width = len(matrix[0])
    rank = 0
    for column in range(width):
        pivot = next(
            (index for index in range(rank, len(matrix)) if matrix[index][column]),
            None,
        )
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inverse = 1 if matrix[rank][column] == 1 else 2
        matrix[rank] = [(inverse * entry) % P for entry in matrix[rank]]
        for index in range(len(matrix)):
            if index == rank or matrix[index][column] == 0:
                continue
            factor = matrix[index][column]
            matrix[index] = [
                (entry - factor * pivot_entry) % P
                for entry, pivot_entry in zip(matrix[index], matrix[rank])
            ]
        rank += 1
    return rank


def mat_vec(matrix: Sequence[Sequence[int]], vector: Sequence[int]) -> list[int]:
    return [
        sum(entry * coefficient for entry, coefficient in zip(row, vector)) % P
        for row in matrix
    ]


def compose(left: Permutation, right: Permutation) -> Permutation:
    """Return left after right."""
    return tuple(left[right[index]] for index in range(len(left)))


def monodromy(permutations: Sequence[Permutation]) -> Permutation:
    result = tuple(range(len(permutations[0])))
    for permutation in permutations:
        result = compose(permutation, result)
    return result


U = [
    vec((0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1)),
    vec((0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0)),
    vec((0, 0, 0, 0, 0, 1, 0, 1, 2, 0, 0)),
    vec((0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0)),
    vec((0, 1, 0, 1, 2, 0, 0, 0, 0, 0, 0)),
]


CONTROLS: dict[int, dict[str, list]] = {
    3: {
        "stars": [
            [
                (0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1),
                (0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2),
                (0, 0, 0, 0, 0, 1, 0, 0, 2, 1, 0),
                (0, 0, 0, 0, 0, 2, 1, 1, 0, 2, 1),
                (0, 0, 0, 0, 0, 2, 1, 1, 1, 0, 2),
                (0, 0, 0, 0, 1, 2, 2, 2, 2, 1, 0),
                (0, 0, 0, 0, 2, 2, 2, 2, 2, 1, 0),
            ],
            [
                (0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0),
                (0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 2),
                (0, 0, 0, 0, 0, 0, 1, 1, 2, 1, 2),
                (0, 0, 0, 0, 0, 1, 2, 0, 2, 2, 2),
                (0, 0, 0, 0, 0, 1, 0, 0, 1, 2, 0),
                (0, 0, 0, 0, 1, 2, 1, 2, 1, 2, 0),
                (0, 0, 0, 0, 2, 2, 1, 2, 1, 2, 0),
            ],
            [
                (0, 0, 0, 0, 0, 1, 0, 1, 2, 0, 0),
                (0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1),
                (0, 0, 0, 0, 0, 0, 1, 1, 0, 2, 0),
                (0, 0, 0, 0, 0, 0, 2, 1, 0, 2, 0),
                (0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0),
                (0, 0, 0, 0, 1, 2, 0, 2, 0, 1, 1),
                (0, 0, 0, 0, 2, 2, 0, 2, 0, 1, 1),
            ],
        ],
        "fillers": [
            (0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1),
            (0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1),
            (0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1),
            (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
        ],
    },
    4: {
        "stars": [
            [
                (0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1),
                (0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2),
                (0, 0, 0, 0, 0, 1, 0, 0, 2, 1, 0),
                (0, 0, 0, 0, 0, 2, 1, 1, 0, 2, 1),
                (0, 0, 0, 0, 0, 2, 1, 1, 1, 0, 2),
                (0, 0, 0, 0, 1, 2, 2, 2, 2, 1, 0),
                (0, 0, 0, 0, 2, 2, 2, 2, 2, 1, 0),
            ],
            [
                (0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0),
                (0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 2),
                (0, 0, 0, 0, 0, 0, 1, 1, 2, 1, 2),
                (0, 0, 0, 0, 0, 1, 2, 0, 2, 2, 2),
                (0, 0, 0, 0, 0, 1, 0, 0, 1, 2, 0),
                (0, 0, 0, 0, 1, 2, 1, 2, 1, 2, 0),
                (0, 0, 0, 0, 2, 2, 1, 2, 1, 2, 0),
            ],
            [
                (0, 0, 0, 0, 0, 1, 0, 1, 2, 0, 0),
                (0, 0, 0, 0, 2, 0, 0, 0, 2, 1, 0),
                (0, 0, 0, 0, 2, 0, 0, 0, 2, 2, 0),
                (0, 0, 1, 1, 0, 0, 0, 0, 2, 0, 0),
                (0, 0, 0, 0, 0, 1, 0, 2, 2, 0, 0),
                (0, 0, 0, 1, 2, 1, 0, 0, 0, 0, 0),
                (0, 0, 2, 1, 0, 0, 0, 0, 2, 0, 0),
            ],
            [
                (0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0),
                (0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1),
                (0, 0, 0, 0, 1, 0, 0, 1, 0, 2, 0),
                (0, 0, 0, 0, 1, 0, 0, 2, 0, 2, 0),
                (0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0),
                (0, 0, 0, 0, 1, 0, 1, 0, 2, 0, 0),
                (0, 0, 2, 2, 0, 0, 1, 0, 0, 2, 2),
            ],
        ],
        "fillers": [
            (0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1),
            (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
        ],
    },
    5: {
        "stars": [
            [
                (0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1),
                (0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2),
                (0, 0, 0, 0, 0, 1, 0, 0, 2, 1, 0),
                (0, 0, 0, 0, 0, 2, 1, 1, 0, 2, 1),
                (0, 0, 0, 0, 0, 2, 1, 1, 1, 0, 2),
                (0, 0, 0, 0, 1, 2, 2, 2, 2, 1, 0),
                (0, 0, 0, 0, 2, 2, 2, 2, 2, 1, 0),
            ],
            [
                (0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0),
                (0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 2),
                (0, 0, 0, 0, 0, 0, 1, 1, 2, 1, 2),
                (0, 0, 0, 0, 0, 1, 2, 0, 2, 2, 2),
                (0, 0, 0, 0, 0, 1, 0, 0, 1, 2, 0),
                (0, 0, 0, 0, 1, 2, 1, 2, 1, 2, 0),
                (0, 0, 0, 0, 2, 2, 1, 2, 1, 2, 0),
            ],
            [
                (0, 0, 0, 0, 0, 1, 0, 1, 2, 0, 0),
                (0, 0, 0, 0, 2, 0, 0, 0, 2, 1, 0),
                (0, 0, 0, 0, 2, 0, 0, 0, 2, 2, 0),
                (0, 0, 1, 1, 0, 0, 0, 0, 2, 0, 0),
                (0, 0, 0, 0, 0, 1, 0, 2, 2, 0, 0),
                (0, 0, 0, 1, 2, 1, 0, 0, 0, 0, 0),
                (0, 0, 2, 1, 0, 0, 0, 0, 2, 0, 0),
            ],
            [
                (0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0),
                (0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1),
                (0, 0, 0, 0, 1, 0, 0, 0, 2, 1, 0),
                (0, 1, 0, 1, 0, 0, 0, 0, 1, 2, 2),
                (0, 0, 0, 2, 2, 0, 0, 0, 2, 1, 1),
                (0, 0, 2, 1, 1, 0, 0, 0, 0, 0, 0),
                (0, 2, 0, 1, 0, 0, 0, 0, 1, 2, 2),
            ],
            [
                (0, 1, 0, 1, 2, 0, 0, 0, 0, 0, 0),
                (0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 1),
                (0, 0, 0, 0, 2, 0, 0, 1, 0, 2, 0),
                (0, 0, 0, 0, 2, 0, 0, 2, 0, 2, 0),
                (0, 0, 0, 0, 2, 0, 1, 0, 1, 0, 0),
                (0, 0, 0, 0, 2, 0, 1, 0, 2, 0, 0),
                (0, 2, 0, 2, 0, 0, 1, 0, 0, 2, 2),
            ],
        ],
        "fillers": [(1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)],
    },
}


def normalized_control(raw: dict[str, list]) -> tuple[list[list[Vector]], list[Vector]]:
    stars = [[vec(vector) for vector in star] for star in raw["stars"]]
    fillers = [vec(vector) for vector in raw["fillers"]]
    return stars, fillers


def analyze_control(
    length: int,
    raw: dict[str, list] | None = None,
    form: Sequence[int] = FORM,
) -> dict[str, object]:
    if raw is None:
        raw = CONTROLS[length]
    stars, fillers = normalized_control(raw)
    if len(stars) != length:
        raise ValueError("wrong cycle length")
    if tuple(form) != FORM:
        # The hostile test must pass through all semantic checks, not merely
        # compare metadata.
        pass

    all_star_vectors = [vector for star in stars for vector in star]
    all_vectors = all_star_vectors + fillers
    projective = [canonical_projective(vector) for vector in all_vectors]
    if len(set(projective)) != len(projective):
        raise ValueError("projective collision")
    if any(dot(vector, vector, form) != 0 for vector in all_vectors):
        raise ValueError("nonsingular column")

    for star in stars:
        if len(star) != 7:
            raise ValueError("star size changed")
        if add(*star) != ZERO:
            raise ValueError("A6 star sum changed")
        gram = [[dot(left, right, form) for right in star] for left in star]
        expected = [[0 if i == j else 1 for j in range(7)] for i in range(7)]
        if gram != expected:
            raise ValueError("A6 Gram changed")

    gains: list[Vector] = []
    for index, star in enumerate(stars):
        target = stars[(index + 1) % length][0]
        source, handle_a, handle_b = star[1], star[2], star[3]
        if add(source, handle_a, handle_b) != target:
            raise ValueError("normalized flag relation changed")
        if source == star[0] or canonical_projective(source) == canonical_projective(star[0]):
            raise ValueError("incoming/outgoing slots collapsed")
        gain = sub(target, source)
        if gain != add(handle_a, handle_b):
            raise ValueError("gain decomposition changed")
        gains.append(gain)

    defect = add(*gains)
    if defect == ZERO:
        raise ValueError("projected center-cycle defect unexpectedly vanished")
    if rank_mod3(all_vectors) != 11:
        raise ValueError("rank-11 span lost")

    return {
        "cycle_length": length,
        "ambient_dimension": DIM,
        "ambient_form_diagonal": list(form),
        "ambient_form_determinant_mod_3": 2,
        "ambient_form_discriminant": "nonsquare",
        "rank_with_fillers": rank_mod3(all_vectors),
        "star_count": length,
        "star_size": 7,
        "all_columns_singular": True,
        "all_columns_projectively_distinct": True,
        "local_star_gram": "J_7-I_7",
        "local_star_sum": [0] * DIM,
        "normalized_flag_equation": "T=S+X_a+X_b",
        "incoming_slot_index": 0,
        "outgoing_slot_index": 1,
        "incoming_outgoing_equalities": 0,
        "composable_consecutive_flag_pairs": 0,
        "block_transition_cycle_exists": False,
        "center_cycle_projected_defect": list(defect),
        "center_cycle_projected_defect_nonzero": True,
        "b": 0,
        "stars": [[[entry for entry in vector] for vector in star] for star in stars],
        "rank_fillers": [[entry for entry in vector] for vector in fillers],
    }


def exact_block_cycle(length: int) -> dict[str, object]:
    potentials = [
        tuple(1 if coordinate == index else 0 for coordinate in range(DIM))
        for index in range(length)
    ]
    gains = [
        sub(potentials[(index + 1) % length], potentials[index])
        for index in range(length)
    ]
    holonomy = add(*gains)
    if holonomy != ZERO:
        raise ValueError("coboundary did not telescope")
    return {
        "cycle_length": length,
        "gain_definition": "g(S->T)=z_T-z_S",
        "holonomy": list(holonomy),
        "holonomy_zero": True,
    }


def partial_extension_pair(length: int) -> dict[str, object]:
    identity = (0, 1, 2, 3, 4)
    twist = (0, 2, 1, 3, 4)
    local_partial = {0: 0}
    completion_a = [identity] * length
    completion_b = [twist] + [identity] * (length - 1)
    for completion in (completion_a, completion_b):
        for permutation in completion:
            if any(permutation[source] != target for source, target in local_partial.items()):
                raise ValueError("completion does not extend local partial injection")
    monodromy_a = monodromy(completion_a)
    monodromy_b = monodromy(completion_b)
    if monodromy_a == monodromy_b:
        raise ValueError("extension monodromies did not separate")
    return {
        "cycle_length": length,
        "slot_count": 5,
        "edgewise_partial_injection": {"0": 0},
        "completion_a": [list(permutation) for permutation in completion_a],
        "completion_b": [list(permutation) for permutation in completion_b],
        "monodromy_a": list(monodromy_a),
        "monodromy_b": list(monodromy_b),
        "same_wave203_partial_interface": True,
        "different_full_extension_monodromy": True,
        "interpretation": "full S5 transports are extra data, not a Wave203 consequence",
    }


def canonical_c4_audit() -> dict[str, object]:
    gram = [
        [0, 1, 1, 2],
        [1, 0, 2, 1],
        [1, 2, 0, 1],
        [2, 1, 1, 0],
    ]
    checkerboard = [1, 2, 2, 1]
    all_equal = [1, 1, 1, 1]
    result = {
        "gram": gram,
        "rank_mod_3": rank_mod3(gram),
        "checkerboard": checkerboard,
        "checkerboard_image": mat_vec(gram, checkerboard),
        "all_equal": all_equal,
        "all_equal_image": mat_vec(gram, all_equal),
    }
    if result["rank_mod_3"] != 3:
        raise ValueError("canonical C4 rank changed")
    if result["checkerboard_image"] != [0, 0, 0, 0]:
        raise ValueError("canonical C4 kernel changed")
    if result["all_equal_image"] == [0, 0, 0, 0]:
        raise ValueError("all-equal C4 word became a kernel word")
    result["forced_two_cell_on_wave203_branch"] = False
    result["reason"] = (
        "the Gram kernel is only a necessary location for a true relation; "
        "Wave203 does not assert checkerboard dependence on every canonical C4"
    )
    return result


def build_result() -> dict[str, object]:
    controls = {str(length): analyze_control(length) for length in (3, 4, 5)}
    block_cycles = {str(length): exact_block_cycle(length) for length in (3, 4, 5)}
    extensions = {str(length): partial_extension_pair(length) for length in (3, 4, 5)}
    return {
        "format": "wave204-global-slot-holonomy-proof-a-v1",
        "conditional_scope": "prism-free n3=4158 and ternary rank-11 endpoint",
        "claims": {
            "definitional_theorem": {
                "label": "DERIVED",
                "statement": (
                    "on the actual triangle-block transition digraph, "
                    "g(S->T)=z_T-z_S is an exact coboundary, so every closed "
                    "block cycle has zero holonomy"
                ),
            },
            "refuted_implication": {
                "label": "REFUTED_BY_EXACT_RELAXED_CONTROLS",
                "statement": (
                    "Wave203 edgewise partial injections plus the local "
                    "rank-11 A6 and normalized flag equations induce a "
                    "center-cycle cocycle or a canonical S5 monodromy"
                ),
            },
        },
        "smallest_honest_incidence_object": {
            "vertices": "the 231 triangle blocks",
            "directed_edges": "existing selected flags, one edge S(f)->T(f)",
            "gain": "z_T-z_S=z_Xa+z_Xb",
            "universally_forced_two_cells": 0,
            "center_projection_preserves_incidence": False,
            "center_walk_composition_requires": "T_i=S_(i+1) as an actual triangle block",
            "wave203_forces_required_equalities": False,
        },
        "low_cycle_coboundary_checks": block_cycles,
        "projected_center_cycle_controls": controls,
        "partial_injection_extension_controls": extensions,
        "canonical_c4": canonical_c4_audit(),
        "premise_ledger": {
            "satisfied_by_orthogonal_controls": [
                "F3 arithmetic",
                "nonsquare nondegenerate 11-dimensional ambient form",
                "projectively distinct singular displayed columns",
                "each displayed point-star is a seven-column A6 simplex",
                "each displayed flag has T=S+X_a+X_b",
                "directed center cycles of lengths 3, 4, and 5",
                "b=0 on the displayed oriented labels",
            ],
            "not_satisfied_or_asserted": [
                "99 point-stars",
                "231 global block columns",
                "the global self-orthogonal frame sum",
                "a point-triangle incidence matrix",
                "SRG adjacency or common-neighbor axioms",
                "Wave201/Wave202 cover totals",
                "a Conway-99 graph or endpoint code",
            ],
        },
        "boundary": {
            "rank_11_excluded": False,
            "endpoint_excluded": False,
            "Q_ge_7060_proved": False,
            "strict_n3_improvement": False,
            "graph_or_code_constructed": False,
            "conway_99": "UNKNOWN",
        },
    }


def canonical_json(payload: dict[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path)
    group.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    rendered = canonical_json(build_result())
    if arguments.output is not None:
        arguments.output.write_text(rendered, encoding="utf-8", newline="\n")
        return 0
    stored = arguments.verify.read_text(encoding="utf-8")
    if stored != rendered:
        raise SystemExit("stored result is not the canonical exact replay")
    print("PASS: canonical exact replay")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
