"""Exact checks for Wave 174's endpoint dual-distance theorem.

The retained argument is finite arithmetic, interlacing, and a local
common-neighbor count.  It does not enumerate graphs, codes, or block
configurations.
"""

from __future__ import annotations

import argparse
import json
from math import comb
from pathlib import Path
from typing import Any


CELL_NAMES = ("U", "Z0", "O1", "T2", "Z3")


def cell_sizes(c: int) -> tuple[int, ...]:
    """Sizes for h=A*1_U values 2 on U and 0,1,2,3 outside U."""

    return (9, 36 - c, 3 * c, 54 - 3 * c, c)


def triangle_counts(c: int, t: int) -> tuple[int, ...]:
    """Counts T_000,T_111,T_222,T_012, where T_012=3t."""

    return (84 - t, 7 * c - t, 147 - 7 * c - t, 3 * t)


def edge_matrix(c: int, t: int) -> tuple[tuple[int, ...], ...]:
    """Undirected edge counts between the five neighbor-count cells."""

    values = (
        (9, 0, 3 * c, 108 - 6 * c, 3 * c),
        (0, 108 - c - t, 3 * t - 3 * c, 216 - 12 * c, 72 + 3 * c - t),
        (3 * c, 3 * t - 3 * c, 21 * c - 3 * t, 3 * t - 3 * c, 3 * c),
        (
            108 - 6 * c,
            216 - 12 * c,
            3 * t - 3 * c,
            324 - 15 * c - 3 * t,
            9 * c + 3 * t - 216,
        ),
        (3 * c, 72 + 3 * c - t, 3 * c, 9 * c + 3 * t - 216, 72 - 2 * c - t),
    )
    assert all(values[i][j] == values[j][i] for i in range(5) for j in range(5))
    return values


def gram_three_minus_adjacency(c: int, t: int) -> tuple[int, int, int, int]:
    """Gram matrix on the two-dimensional quotient test space.

    The vectors are orthogonal to 1_U and to the invariant Krylov space
    span(1,1_U,A1_U).  Interlacing requires this 2 by 2 Gram matrix for
    3I-A to be positive semidefinite.
    """

    sizes = cell_sizes(c)
    edges = edge_matrix(c, t)
    v1 = (
        0,
        3 * c * (18 - c),
        -2 * (36 - c) * (18 - c),
        c * (36 - c),
        0,
    )
    v2 = (0, 0, 18 - c, -2 * c, 3 * (18 - c))

    def form(left: tuple[int, ...], right: tuple[int, ...]) -> int:
        value = 0
        for i in range(5):
            value += 3 * sizes[i] * left[i] * right[i]
            value -= 2 * edges[i][i] * left[i] * right[i]
        for i in range(5):
            for j in range(i + 1, 5):
                value -= edges[i][j] * (
                    left[i] * right[j] + left[j] * right[i]
                )
        return value

    g11 = form(v1, v1)
    g12 = form(v1, v2)
    g22 = form(v2, v2)
    return g11, g12, g22, g11 * g22 - g12 * g12


def c18_empty_cell_test() -> dict[str, int]:
    """Nondegenerate quotient test when the T2 cell is empty at c=18."""

    c, t = 18, 18
    sizes = cell_sizes(c)
    edges = edge_matrix(c, t)
    vector = (0, 2, -1, 0, 1)
    norm = sum(size * value * value for size, value in zip(sizes, vector, strict=True))
    adjacency = 0
    for i in range(5):
        adjacency += 2 * edges[i][i] * vector[i] * vector[i]
        for j in range(i + 1, 5):
            adjacency += 2 * edges[i][j] * vector[i] * vector[j]
    return {
        "norm": norm,
        "adjacency_quadratic": adjacency,
        "three_minus_adjacency_quadratic": 3 * norm - adjacency,
    }


def min_sum_choose_two(total: int, bins: int) -> int:
    """Convex integer minimum of sum binomial(d_i,2)."""

    quotient, remainder = divmod(total, bins)
    return (bins - remainder) * comb(quotient, 2) + remainder * comb(
        quotient + 1, 2
    )


def z3_common_neighbor_balance(c: int, t: int) -> dict[str, Any]:
    """Check the SRG common-neighbor identity for the Z3 cell."""

    sizes = cell_sizes(c)
    edges = edge_matrix(c, t)
    z3 = 4
    totals = [
        2 * edges[z3][z3] if i == z3 else edges[i][z3] for i in range(5)
    ]
    lower_parts = [
        min_sum_choose_two(total, sizes[i]) for i, total in enumerate(totals)
    ]
    lower = sum(lower_parts)
    exact = 2 * comb(sizes[z3], 2) - edges[z3][z3]
    return {
        "cell_size": sizes[z3],
        "internal_edges": edges[z3][z3],
        "degree_totals_by_cell": dict(zip(CELL_NAMES, totals, strict=True)),
        "convex_lower_parts": dict(zip(CELL_NAMES, lower_parts, strict=True)),
        "convex_lower": lower,
        "srg_exact": exact,
        "feasible": lower <= exact,
        "equality": lower == exact,
    }


def analyze() -> dict[str, Any]:
    """Return the complete exact arithmetic certificate."""

    candidates: list[dict[str, Any]] = []
    for c in range(1, 19):
        # Pointwise equality of the two cross-color degrees forces this.
        t = 72 - 3 * c
        sizes = cell_sizes(c)
        triangles = triangle_counts(c, t)
        edges = edge_matrix(c, t)
        empty_cells_valid = all(
            sizes[i] > 0 or all(edges[i][j] == 0 for j in range(5))
            for i in range(5)
        )
        nonnegative = (
            min(sizes) >= 0
            and empty_cells_valid
            and min(triangles) >= 0
            and min(min(row) for row in edges) >= 0
        )
        if not nonnegative:
            continue
        g11, g12, g22, determinant = gram_three_minus_adjacency(c, t)
        psd = g11 >= 0 and g22 >= 0 and determinant >= 0
        candidates.append(
            {
                "c": c,
                "t": t,
                "triangle_counts": dict(
                    zip(("T000", "T111", "T222", "T012"), triangles, strict=True)
                ),
                "gram": {
                    "g11": g11,
                    "g12": g12,
                    "g22": g22,
                    "determinant": determinant,
                    "psd": psd,
                },
            }
        )

    raw_psd_survivors = [row["c"] for row in candidates if row["gram"]["psd"]]
    c18_test = c18_empty_cell_test()
    psd_survivors = [
        c
        for c in raw_psd_survivors
        if c != 18 or c18_test["three_minus_adjacency_quadratic"] >= 0
    ]
    c8 = z3_common_neighbor_balance(8, 48)
    c9 = z3_common_neighbor_balance(9, 45)

    # At c=9 equality forces Z3-degrees 3,2,1,0,2 on the five cells.
    c9_forced_degrees = {
        name: c9["degree_totals_by_cell"][name] // size
        for name, size in zip(CELL_NAMES, cell_sizes(9), strict=True)
    }

    # On a Z3 cycle, the two neighbors must use the two labels different
    # from the center in every U triangle.  The recurrence has period three.
    sequence = [0, 1]
    for _ in range(7):
        sequence.append(3 - sequence[-1] - sequence[-2])
    period_three = all(sequence[i] == sequence[i + 3] for i in range(6))
    simple_cycle_lengths = (3, 6, 9)
    distinct_label_cycle_lengths = tuple(
        length for length in simple_cycle_lengths if length == 3
    )

    return {
        "identity": "D = B^T*A*B over F3",
        "outside_neighbor_counts": {
            "n0": "36-c",
            "n1": "3c",
            "n2": "54-3c",
            "n3": "c",
        },
        "cross_color_equation": "t=72-3c",
        "nonnegative_candidates": [row["c"] for row in candidates],
        "candidate_details": candidates,
        "raw_degenerate_basis_psd_survivors": raw_psd_survivors,
        "c18_empty_cell_test": c18_test,
        "psd_survivors": psd_survivors,
        "c8_common_neighbor_test": c8,
        "c9_common_neighbor_test": c9,
        "unique_survivor": {"c": 9, "t": 45},
        "c9_color_sizes": {"zero": 36, "one": 27, "two": 36},
        "c9_forced_Z3_degrees": c9_forced_degrees,
        "cycle_label_sequence": sequence,
        "cycle_label_period_three": period_three,
        "candidate_Z3_cycle_lengths": list(simple_cycle_lengths),
        "distinct_label_Z3_cycle_lengths": list(distinct_label_cycle_lengths),
        "forced_Z3_graph": "3K3",
        "endpoint_contradiction": (
            "Each Z3 triangle has a perfect matching to each U triangle, "
            "so it forms a forbidden triangular prism."
        ),
        "conclusion": "B1=B2=B3=0 for the endpoint centered-code dual",
    }


def verify(data: dict[str, Any]) -> None:
    assert data["nonnegative_candidates"] == list(range(8, 19))
    assert data["raw_degenerate_basis_psd_survivors"] == [8, 9, 18]
    assert data["c18_empty_cell_test"] == {
        "norm": 144,
        "adjacency_quadratic": 1584,
        "three_minus_adjacency_quadratic": -1152,
    }
    assert data["psd_survivors"] == [8, 9]
    assert data["c8_common_neighbor_test"]["convex_lower"] == 49
    assert data["c8_common_neighbor_test"]["srg_exact"] == 48
    assert not data["c8_common_neighbor_test"]["feasible"]
    assert data["c9_common_neighbor_test"]["convex_lower"] == 63
    assert data["c9_common_neighbor_test"]["srg_exact"] == 63
    assert data["c9_common_neighbor_test"]["equality"]
    assert data["c9_forced_Z3_degrees"] == {
        "U": 3,
        "Z0": 2,
        "O1": 1,
        "T2": 0,
        "Z3": 2,
    }
    assert data["cycle_label_period_three"]
    assert data["distinct_label_Z3_cycle_lengths"] == [3]
    assert data["forced_Z3_graph"] == "3K3"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()

    data = analyze()
    verify(data)
    if args.verify:
        archived = json.loads(args.verify.read_text(encoding="utf-8"))
        assert archived == data
    if args.write:
        args.write.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    if not args.write and not args.verify:
        print(json.dumps(data, indent=2, sort_keys=True))
    print("PASS: Wave174 no-weight-three-dual exact checks")


if __name__ == "__main__":
    main()
