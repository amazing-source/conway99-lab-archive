"""Exact scalar replay for Wave 189.

This script checks only the displayed coefficient certificates, equality
arithmetic, design degrees, and local F_3 relation vectors.  It does not
enumerate covers, graphs, codes, configurations, or isomorphism classes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


VARS = ("n1", "n2", "n3", "p2", "p3")


def _vec(**entries: int) -> list[int]:
    return [entries.get(name, 0) for name in VARS]


def _add(*vectors: list[int]) -> list[int]:
    return [sum(values) for values in zip(*vectors)]


def _scale(scale: int, vector: list[int]) -> list[int]:
    return [scale * value for value in vector]


def _sub(left: list[int], right: list[int]) -> list[int]:
    return [a - b for a, b in zip(left, right)]


def _mod3_sub(left: list[int], scale: int, right: list[int]) -> list[int]:
    return [(a - scale * b) % 3 for a, b in zip(left, right)]


def derive() -> dict[str, Any]:
    nonedges = 4158
    edge_circuits = 693

    private_row = _vec(n1=2, n2=2, n3=3, p2=1, p3=1)
    base = _vec(n1=1, n2=1, n3=2)
    assignments = _vec(n1=1, p2=2, p3=1)
    lhs_12q = _add(_scale(12, base), _scale(6, assignments))
    seven_private = _scale(7, private_row)
    remainder = _sub(lhs_12q, seven_private)
    expected_remainder = _add(
        _vec(n1=4),
        _vec(n2=-2, p2=2),
        _vec(n3=3, p3=-1),
        _vec(p2=3),
    )
    assert remainder == expected_remainder

    q_fractional = 7 * nonedges // 6
    assert 7 * nonedges % 6 == 0
    assert q_fractional == 4851
    q_strict = q_fractional + 1

    equality = {
        "n1": 0,
        "n2": 0,
        "n3": nonedges // 3,
        "p2": 0,
        "p3": nonedges,
        "raw_assignment_incidence": nonedges,
        "selected_plus_companions": 2 * (nonedges // 3),
        "multiplicity_at_most_two_extraction_circuits": nonedges // 2,
        "exact_three_extraction_orbit_pairs": 0,
    }
    assert equality["n3"] == 1386
    assert equality["multiplicity_at_most_two_extraction_circuits"] == 2079

    # Coordinates: x_a,x_b,x_c | y_a,y_b,y_c,y_d,y_e,y_f.
    leaf_word = [2, 2, 2, 2, 2, 2, 2, 2, 2]
    checkerboard = [1, 2, 0, 2, 1, 0, 0, 0, 0]
    difference_one = _mod3_sub(leaf_word, 1, checkerboard)
    difference_two = _mod3_sub(leaf_word, 2, checkerboard)
    side_weights = []
    for vector in (difference_one, difference_two):
        side_weights.append(
            [
                sum(value != 0 for value in vector[:3]),
                sum(value != 0 for value in vector[3:]),
            ]
        )
    assert side_weights == [[2, 5], [2, 5]]

    candidate_flags = 231 * 60
    conflict_degree = 3 * (10 - 1)
    hoffman_alpha = candidate_flags * 3 // (conflict_degree + 3)
    assert candidate_flags == 13860
    assert conflict_degree == 27
    assert hoffman_alpha == 1386

    projective_circuit_lower = q_strict + edge_circuits
    scalar_circuit_lower = 2 * projective_circuit_lower

    return {
        "format": "wave189-orbit-closed-star-translations-v1",
        "claim_label": "DERIVED",
        "constants": {
            "nonedges": nonedges,
            "edge_isolated_projective_circuits": edge_circuits,
        },
        "coefficient_certificate": {
            "variable_order": list(VARS),
            "private_row_I": private_row,
            "base_selected_plus_companions": base,
            "raw_extraction_assignments": assignments,
            "lhs_12Q": lhs_12q,
            "seven_I": seven_private,
            "nonnegative_remainder": remainder,
            "remainder_decomposition": (
                "4*n1+2*(p2-n2)+(3*n3-p3)+3*p2"
            ),
        },
        "orbit_closure": {
            "raw_assignment_bound": "A<=2*r+3*h",
            "closed_pool_size": "|X|=r+2*h",
            "consequence": "2*|X|>=A",
            "type2_same_label_pair_excluded": True,
        },
        "fractional_bound": {
            "inequality": "12*Q>=14*C",
            "Q_lower_before_strictness": q_fractional,
        },
        "equality_face_before_strictness": equality,
        "design_null_control": {
            "candidate_flags": candidate_flags,
            "row_degree": 10,
            "column_degree": 3,
            "conflict_graph_degree": conflict_degree,
            "conflict_graph_least_eigenvalue": -3,
            "hoffman_independence_bound": hoffman_alpha,
            "uniform_rational_flag_weight": "1/10",
            "uniform_center_count": 14,
            "uniform_triangle_replication": 6,
        },
        "strict_local_relation": {
            "coordinate_split": [3, 6],
            "leaf_word": leaf_word,
            "canonical_checkerboard": checkerboard,
            "leaf_minus_checkerboard": difference_one,
            "leaf_minus_twice_checkerboard": difference_two,
            "difference_side_weights": side_weights,
            "difference_weights": [sum(map(bool, difference_one)), sum(map(bool, difference_two))],
        },
        "bounds": {
            "nonedge_projective_circuits_Q": q_strict,
            "all_projective_short_circuits": projective_circuit_lower,
            "scalar_short_circuit_words": scalar_circuit_lower,
            "verified_Wave188_all_short_word_bound_remains": 18018,
        },
        "boundary": {
            "rank_11_excluded": False,
            "endpoint_excluded": False,
            "strict_n3_improvement": False,
            "conway_99": "UNKNOWN",
            "independent_verification": "PENDING",
        },
    }


def verify_input_freeze() -> int:
    package = Path(__file__).resolve().parent
    repository = package.parents[1]
    freeze = package / "input-freeze.sha256"
    checked = 0
    for raw_line in freeze.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        expected, relative = line.split(maxsplit=1)
        target = repository / relative
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(
                f"input hash mismatch: {relative}: expected {expected}, got {actual}"
            )
        checked += 1
    return checked


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = derive()
    if args.verify is not None:
        checked = verify_input_freeze()
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            raise SystemExit("verification mismatch")
        print(f"PASS_WAVE189_EXACT_REPLAY inputs={checked}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
