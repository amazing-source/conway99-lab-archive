"""Exact finite algebra and arithmetic checks for Wave 180.

The theorem is geometric.  This checker verifies the two seven-entry Gram
profiles, the four projective relation directions on the local eight
columns, the companion-cover arithmetic, and a hostile graphic-matroid
scale control.  It performs no graph or code construction search.
"""

from __future__ import annotations

import argparse
import json
import math
from itertools import product
from pathlib import Path
from typing import Any, Iterable


FIELD = 3


def mat_vec(matrix: list[list[int]], vector: Iterable[int]) -> list[int]:
    values = list(vector)
    return [
        sum(entry * value for entry, value in zip(row, values)) % FIELD
        for row in matrix
    ]


def rank_mod3(matrix: list[list[int]]) -> int:
    work = [[entry % FIELD for entry in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (
                row
                for row in range(pivot_row, rows)
                if work[row][column] % FIELD
            ),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        inverse = 1 if work[pivot_row][column] == 1 else 2
        work[pivot_row] = [
            inverse * value % FIELD for value in work[pivot_row]
        ]
        for row in range(rows):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    (left - factor * right) % FIELD
                    for left, right in zip(work[row], work[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def support(vector: Iterable[int]) -> tuple[int, ...]:
    return tuple(index for index, value in enumerate(vector) if value % FIELD)


def canonical(vector: Iterable[int]) -> tuple[int, ...]:
    values = tuple(value % FIELD for value in vector)
    first = next(value for value in values if value)
    scale = 1 if first == 1 else 2
    return tuple(scale * value % FIELD for value in values)


def local_relation_data(t: int) -> dict[str, Any]:
    m2 = t
    m1 = 6 - 2 * t
    m0 = 1 + t
    h = [2] * m2 + [1] * m1 + [0] * m0

    star_gram = [
        [0 if row == column else 1 for column in range(7)]
        for row in range(7)
    ]
    extended = [[0] + h]
    for row in range(7):
        extended.append([h[row]] + star_gram[row])

    kernel = [
        vector
        for vector in product(range(FIELD), repeat=8)
        if any(vector) and mat_vec(extended, vector) == [0] * 8
    ]
    projective = sorted({canonical(vector) for vector in kernel})
    return {
        "t": t,
        "j_profile_counts": {"0": m0, "1": m1, "2": m2},
        "nonzero_h_entries": m1 + m2,
        "singularity_residue": (m1 + m2) % FIELD,
        "extended_gram_rank": rank_mod3(extended),
        "kernel_dimension": 8 - rank_mod3(extended),
        "projective_kernel_directions": len(projective),
        "projective_supports": sorted(
            [list(support(vector)) for vector in projective],
            key=lambda indices: (len(indices), indices),
        ),
        "projective_weights": sorted(len(support(vector)) for vector in projective),
    }


def analyze() -> dict[str, Any]:
    profiles = [local_relation_data(t) for t in range(4)]
    admissible = [
        profile["t"]
        for profile in profiles
        if profile["singularity_residue"] == 0
    ]

    vertices = 99
    degree = 14
    edges = vertices * degree // 2
    pairs = vertices * (vertices - 1) // 2
    nonedges = pairs - edges
    nonedge_projective_lower = math.ceil(nonedges / 2)
    total_projective_lower = edges + nonedge_projective_lower

    graphic_counts = {
        str(2 * k): (
            math.comb(6, k) ** 2
            * math.factorial(k)
            * math.factorial(k - 1)
            // 2
        )
        for k in (2, 3, 4)
    }

    result = {
        "field": FIELD,
        "local_profiles": profiles,
        "projector_admissible_t": admissible,
        "t0_consequence": "duplicate selected projective point; rejected",
        "t3_circuit_pair": {
            "weights": [4, 5],
            "weight4_geometry": "Q(2,3) plane conic",
            "same_cross_realization_labels": 3,
            "pairing": "fixed-point-free involution",
        },
        "pair_counts": {
            "edges": edges,
            "nonedges": nonedges,
            "all_pairs": pairs,
        },
        "minimal_cover": {
            "inequality": "4158<=2*N+a",
            "companion_inequality": "Q>=N+a",
            "nonedge_projective_circuit_lower_bound": nonedge_projective_lower,
        },
        "edge_projective_circuit_lower_bound": edges,
        "projective_circuit_lower_bound": total_projective_lower,
        "ternary_nonzero_scalars_per_projective_class": 2,
        "dual_word_lower_bound": 2 * total_projective_lower,
        "dual_word_inequality": "B_4+B_5+B_6+B_7+B_8+B_9>=5544",
        "retained_edge_inequality": "B_4+B_6+B_8>=1386",
        "hostile_control_k6_6": {
            "rank": 11,
            "length": 36,
            "projective_cycle_counts": graphic_counts,
            "projective_cycles_weight_4_6_8": sum(graphic_counts.values()),
        },
        "conclusion": (
            "capacity-three nonedge circuits occur in conic/complement "
            "pairs, forcing at least 2772 projective short circuits; "
            "the conditional endpoint remains unexcluded"
        ),
    }
    verify(result)
    return result


def verify(result: dict[str, Any]) -> None:
    assert result["projector_admissible_t"] == [0, 3]
    profiles = {profile["t"]: profile for profile in result["local_profiles"]}
    assert profiles[0]["j_profile_counts"] == {"0": 1, "1": 6, "2": 0}
    assert profiles[3]["j_profile_counts"] == {"0": 4, "1": 0, "2": 3}
    assert profiles[0]["projective_weights"] == [2, 7, 7, 8]
    assert profiles[3]["projective_weights"] == [4, 5, 7, 8]
    assert profiles[3]["extended_gram_rank"] == 6
    assert profiles[3]["kernel_dimension"] == 2
    assert result["pair_counts"] == {
        "edges": 693,
        "nonedges": 4158,
        "all_pairs": 4851,
    }
    assert (
        result["minimal_cover"]["nonedge_projective_circuit_lower_bound"]
        == 2079
    )
    assert result["projective_circuit_lower_bound"] == 2772
    assert result["dual_word_lower_bound"] == 5544
    assert result["hostile_control_k6_6"]["projective_cycle_counts"] == {
        "4": 225,
        "6": 2400,
        "8": 16200,
    }
    assert (
        result["hostile_control_k6_6"]["projective_cycles_weight_4_6_8"]
        == 18825
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = analyze()
    if args.verify:
        assert json.loads(args.verify.read_text(encoding="utf-8")) == result
    if args.write:
        args.write.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if not args.write and not args.verify:
        print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS: Wave180 conic-companion exact checks")


if __name__ == "__main__":
    main()
