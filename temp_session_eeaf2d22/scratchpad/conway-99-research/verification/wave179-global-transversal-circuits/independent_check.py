"""Independent arithmetic and finite-logic checks for Wave 179."""

from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Any


def analyze() -> dict[str, Any]:
    vertices = 99
    degree = 14
    edges = vertices * degree // 2
    pairs = vertices * (vertices - 1) // 2
    nonedges = pairs - edges

    # The triangle alternative for a pairwise-intersecting family would
    # require all three exact-one equations simultaneously.
    triangle_memberships = [
        bits
        for bits in product((0, 1), repeat=3)
        if bits[0] + bits[1] == 1
        and bits[0] + bits[2] == 1
        and bits[1] + bits[2] == 1
    ]

    # Proper two-colourings of the four-cell adjacency cycle are exactly
    # the two alternating diagonal patterns; Wave 179 separately rejects
    # either diagonal equality using lambda=1.
    square_colourings = [
        cells
        for cells in product((0, 1), repeat=4)
        if cells[0] != cells[1]
        and cells[0] != cells[2]
        and cells[3] != cells[1]
        and cells[3] != cells[2]
    ]

    nonedge_classes = nonedges // 3
    total_classes = edges + nonedge_classes
    result = {
        "pair_counts": {
            "edges": edges,
            "nonedges": nonedges,
            "all_pairs": pairs,
        },
        "multiplicity": {
            "edge_circuit": 1,
            "nonedge_circuit_upper": 3,
            "disjoint_case": 2,
        },
        "finite_logic": {
            "triangle_membership_solutions": len(triangle_memberships),
            "alternating_square_colourings": len(square_colourings),
            "diagonal_repetition_rejected_by_lambda": True,
        },
        "projective_classes": {
            "edge": edges,
            "additional_nonedge": nonedge_classes,
            "total": total_classes,
        },
        "ternary_scalars_per_class": 2,
        "dual_word_lower": 2 * total_classes,
        "dual_word_inequality": "B_4+B_5+B_6+B_7+B_8+B_9>=4158",
        "retained_edge_inequality": "B_4+B_6+B_8>=1386",
        "scope": "necessary condition only; endpoint remains unknown",
    }
    verify(result)
    return result


def verify(result: dict[str, Any]) -> None:
    assert result["pair_counts"] == {
        "edges": 693,
        "nonedges": 4158,
        "all_pairs": 4851,
    }
    assert result["finite_logic"]["triangle_membership_solutions"] == 0
    assert result["finite_logic"]["alternating_square_colourings"] == 2
    assert result["projective_classes"] == {
        "edge": 693,
        "additional_nonedge": 1386,
        "total": 2079,
    }
    assert result["dual_word_lower"] == 4158
    assert result["multiplicity"]["edge_circuit"] == 1
    assert result["multiplicity"]["nonedge_circuit_upper"] == 3


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = analyze()
    if args.verify:
        assert json.loads(args.verify.read_text(encoding="utf-8")) == result
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS: independent Wave179 verification")


if __name__ == "__main__":
    main()

