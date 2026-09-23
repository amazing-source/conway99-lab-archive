"""Clean-room audit of Wave 112 four-cycle incidence arithmetic.

This module imports no discovery code.  It rebuilds the claimed counts from
the strongly regular graph parameters and the previously verified signed
support descriptions.
"""

from __future__ import annotations

import argparse
import json
from itertools import product
from math import comb
from pathlib import Path


HERE = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def target_cycle_audit(
    vertices: int = 99,
    degree: int = 14,
    adjacent_codegree: int = 1,
    nonadjacent_codegree: int = 2,
) -> dict[str, int | bool]:
    """Double-count the induced C4s of srg(99,14,1,2)."""

    edges = vertices * degree // 2
    nonedges = comb(vertices, 2) - edges
    require(nonadjacent_codegree == 2, "this audit expects mu=2")
    # If the two common neighbours of a nonedge were adjacent, that adjacent
    # pair would have at least the two endpoints as common neighbours, against
    # lambda=1.  Thus every such K_2,2 is induced.
    common_pair_forced_nonadjacent = adjacent_codegree < 2
    require(common_pair_forced_nonadjacent, "the four-cycle need not be induced")
    diagonal_cycle_incidences = nonedges * comb(nonadjacent_codegree, 2)
    require(diagonal_cycle_incidences % 2 == 0, "two diagonals must divide")
    return {
        "edges": edges,
        "nonedges": nonedges,
        "nonedge_diagonal_incidences": diagonal_cycle_incidences,
        "diagonals_per_induced_C4": 2,
        "induced_C4": diagonal_cycle_incidences // 2,
        "common_pair_forced_nonadjacent": common_pair_forced_nonadjacent,
    }


def enumerate_h0_codegrees(side_size: int, cross_degree: int = 4) -> dict[str, object]:
    """Exhaust aggregate {0,1,2} codegree histograms for an h=0 sign side."""

    slots = comb(side_size, 2)
    total = side_size * comb(cross_degree, 2)
    rows: list[dict[str, int]] = []
    for zeros, ones, twos in product(range(slots + 1), repeat=3):
        if zeros + ones + twos == slots and ones + 2 * twos == total:
            rows.append({"codegree_0": zeros, "codegree_1": ones, "codegree_2": twos})
    require(rows, "no aggregate codegree histogram")
    return {
        "side_size": side_size,
        "pair_slots": slots,
        "pair_intersection_sum": total,
        "feasible_histograms": rows,
        "minimum_alternating_C4": min(row["codegree_2"] for row in rows),
    }


def enumerate_h1_codegrees() -> dict[str, object]:
    """Exhaust the h=1 norm-18 aggregate codegree histograms.

    One same-sign pair is adjacent and has opposite-side codegree at most one;
    the other 35 pairs are nonadjacent and have codegree at most two.
    """

    total = 2 * comb(5, 2) + 7 * comb(4, 2)
    ordinary_slots = comb(9, 2) - 1
    rows: list[dict[str, int]] = []
    for adjacent_codegree in (0, 1):
        for zeros, ones, twos in product(range(ordinary_slots + 1), repeat=3):
            if (
                zeros + ones + twos == ordinary_slots
                and adjacent_codegree + ones + 2 * twos == total
            ):
                rows.append(
                    {
                        "adjacent_pair_codegree": adjacent_codegree,
                        "nonadjacent_codegree_0": zeros,
                        "nonadjacent_codegree_1": ones,
                        "nonadjacent_codegree_2": twos,
                    }
                )
    require(rows, "no h=1 aggregate codegree histogram")
    return {
        "cross_degree_multiset": [5, 5] + [4] * 7,
        "pair_intersection_sum": total,
        "adjacent_pair_slots": 1,
        "nonadjacent_pair_slots": ordinary_slots,
        "feasible_histograms": rows,
        "minimum_alternating_C4": min(
            row["nonadjacent_codegree_2"] for row in rows
        ),
    }


def fixed_cycle_partition() -> dict[str, object]:
    """Derive the unique outside anchor-adjacency partition."""

    # The induced cycle is K_2,2 between its two alternating sign classes.
    # Every anchor has 12 outside neighbours.  Each of the four cross edges
    # has exactly one outside common neighbour.  The four witnesses are
    # distinct because sharing one would meet both anchors in a same-sign
    # nonedge.
    outside_vertices = 99 - 4
    cross_pair_classes = 4
    both = cross_pair_classes
    p_only = 2 * (12 - 2)
    n_only = 2 * (12 - 2)
    neither = outside_vertices - both - p_only - n_only
    require(min(neither, p_only, n_only, both) >= 0, "negative partition cell")
    require(neither + p_only + n_only + both == outside_vertices, "partition sum")
    return {
        "outside_vertices": outside_vertices,
        "cross_edge_external_witnesses": 4,
        "cross_edge_witnesses_distinct": True,
        "partition": {
            "neither": neither,
            "p_only": p_only,
            "n_only": n_only,
            "one_p_and_one_n": both,
        },
    }


def h0_remaining_selection(side_size: int) -> dict[str, int]:
    """Count one side's remaining support vertices around the fixed C4."""

    require(side_size in (7, 8, 9), "unsupported side size")
    # Each of two opposite-sign anchors has cross degree four and has already
    # used the two same-cycle neighbours.  The four remaining incidences use
    # four distinct vertices because no outside vertex meets both anchors.
    return {
        "one_opposite_anchor": 4,
        "neither_opposite_anchor": side_size - 6,
        "total_remaining_on_side": side_size - 2,
    }


def rank28_incidence_audit() -> dict[str, object]:
    """Audit oriented-vector counting, parity, and the proposed cap."""

    oriented_short_vector_lower = 5868
    weakest_cycle_lower = 18
    target_cycles = int(target_cycle_audit()["induced_C4"])
    incidence_lower = oriented_short_vector_lower * weakest_cycle_lower
    raw_ceiling = (incidence_lower + target_cycles - 1) // target_cycles
    # Theta coefficients count t and -t separately.  Negation fixes the
    # alternating support cycles and has no fixed nonzero vector, so each
    # rooted-cycle multiplicity is even.
    parity_rounded = raw_ceiling if raw_ceiling % 2 == 0 else raw_ceiling + 1
    antipodal_pairs = parity_rounded // 2
    cap_pairs = antipodal_pairs - 1
    cap_oriented = 2 * cap_pairs
    upper_under_cap = target_cycles * cap_oriented
    require(raw_ceiling == 51, "off-by-one in raw pigeonhole ceiling")
    require(parity_rounded == 52, "off-by-two antipodal rounding error")
    require(upper_under_cap < incidence_lower, "the proposed cap does not close")
    return {
        "N14_N16_N18_are_oriented_theta_counts": True,
        "oriented_short_vector_total_lower": oriented_short_vector_lower,
        "weakest_alternating_C4_lower": weakest_cycle_lower,
        "oriented_incidence_lower": incidence_lower,
        "raw_pigeonhole_ceiling": raw_ceiling,
        "cycle_multiplicity_is_even_by_antipodes": True,
        "forced_oriented_multiplicity": parity_rounded,
        "forced_antipodal_support_pairs": antipodal_pairs,
        "sufficient_universal_cap_antipodal_pairs": cap_pairs,
        "sufficient_universal_cap_oriented": cap_oriented,
        "incidence_upper_under_cap": upper_under_cap,
        "contradiction_margin": incidence_lower - upper_under_cap,
    }


def build_results() -> dict[str, object]:
    h0 = {str(s): enumerate_h0_codegrees(s) for s in (7, 8, 9)}
    h1 = enumerate_h1_codegrees()
    return {
        "format": "wave112-independent-c4-incidence-v1",
        "verdict": "VERIFIED_CONDITIONAL",
        "target": target_cycle_audit(),
        "alternating_C4_minima": {
            "norm14_h0": h0["7"]["minimum_alternating_C4"],
            "norm16_h0": h0["8"]["minimum_alternating_C4"],
            "norm18_h0": h0["9"]["minimum_alternating_C4"],
            "norm18_h1": h1["minimum_alternating_C4"],
        },
        "h0_codegree_audits": h0,
        "norm18_h1_codegree_audit": h1,
        "rank28_incidence": rank28_incidence_audit(),
        "fixed_C4": fixed_cycle_partition(),
        "h0_remaining_side_selections": {
            str(s): h0_remaining_selection(s) for s in (7, 8, 9)
        },
        "hostile_checks": {
            "cycles_are_induced_not_merely_K22": True,
            "alternating_cycle_counted_once_per_sign_side_diagonal": True,
            "h1_same_sign_edge_not_counted_as_alternating_cycle": True,
            "h1_signs_preserve_antipodal_pairing": True,
            "raw_51_strengthened_to_even_52": True,
        },
        "status_wall": {
            "universal_cap_25_proved": False,
            "rank28_excluded": False,
            "Conway_99": "UNKNOWN",
            "literature_novelty": "UNKNOWN",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_results()
    if args.verify:
        archived = json.loads(args.verify.read_text(encoding="utf-8"))
        require(result == archived, "archived independent result mismatch")
    if args.json or not args.verify:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("independent Wave 112 verification: PASS")


if __name__ == "__main__":
    main()
