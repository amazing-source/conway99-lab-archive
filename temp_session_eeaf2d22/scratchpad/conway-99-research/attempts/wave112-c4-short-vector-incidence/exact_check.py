"""Exact C4 incidence target for the rank-28 short-vector squeeze."""

from __future__ import annotations

import argparse
import json
from math import comb
from pathlib import Path


HERE = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def target_c4_count() -> int:
    """Count induced four-cycles in srg(99,14,1,2)."""

    edges = 99 * 14 // 2
    nonedges = comb(99, 2) - edges
    # Each nonedge has one pair of common neighbors.  The two common
    # neighbors cannot be adjacent, and every C4 has two opposite nonedges.
    return nonedges * comb(2, 2) // 2


def regular_bipartite_c4_min(side_size: int, degree: int = 4) -> int:
    """Minimum K2,2 count under same-side codegree at most two."""

    pair_intersections = side_size * comb(degree, 2)
    side_pairs = comb(side_size, 2)
    require(pair_intersections <= 2 * side_pairs, "capacity exceeded")
    # With entries in {0,1,2}, a sum S over p positions needs at least S-p
    # entries equal to two.
    return max(0, pair_intersections - side_pairs)


def norm18_h1_c4_min() -> int:
    """Minimum alternating C4 count for the h=1 norm-18 support."""

    # On the opposite side two vertices have cross degree five and seven
    # have cross degree four.
    pair_intersections = 2 * comb(5, 2) + 7 * comb(4, 2)
    adjacent_pair_capacity = 1
    nonadjacent_pairs = comb(9, 2) - 1
    residual = pair_intersections - adjacent_pair_capacity
    return max(0, residual - nonadjacent_pairs)


def fixed_c4_partition() -> dict[str, int]:
    """Outside partition relative to a normalized induced four-cycle."""

    # The four cross edges each have one external common neighbor.
    both = 4
    # Each anchor has 12 outside neighbors, two already counted in `both`.
    p_only = 2 * (12 - 2)
    n_only = 2 * (12 - 2)
    neither = 95 - both - p_only - n_only
    return {
        "neither": neither,
        "p_only": p_only,
        "n_only": n_only,
        "one_p_and_one_n": both,
    }


def homogeneous_extension_selection(side_size: int) -> dict[str, int]:
    """Required remaining same-sign types for h=0 around a fixed C4."""

    require(side_size in (7, 8, 9), "supported side sizes are 7,8,9")
    # Each of the two opposite-sign anchors already has two cross neighbors
    # and needs two more.  No new vertex can meet both anchors.
    one_opposite_anchor = 4
    neither_anchor = side_size - 2 - one_opposite_anchor
    return {
        "one_opposite_anchor": one_opposite_anchor,
        "neither_anchor": neither_anchor,
    }


def build_results() -> dict[str, object]:
    c4_total = target_c4_count()
    shell_total_lower = 5868
    shell_c4_min = {
        "norm14_h0": regular_bipartite_c4_min(7),
        "norm16_h0": regular_bipartite_c4_min(8),
        "norm18_h0": regular_bipartite_c4_min(9),
        "norm18_h1": norm18_h1_c4_min(),
    }
    weakest = min(shell_c4_min.values())
    incidence_lower = weakest * shell_total_lower
    average_oriented = incidence_lower / c4_total
    forced_oriented = (incidence_lower + c4_total - 1) // c4_total
    # Each occurrence is paired with the antipodal vector.
    forced_oriented_even = forced_oriented + forced_oriented % 2
    forced_supports = forced_oriented_even // 2
    candidate_cap_oriented = forced_oriented_even - 2
    candidate_cap_supports = candidate_cap_oriented // 2
    upper_if_cap = c4_total * candidate_cap_oriented
    require(upper_if_cap < incidence_lower, "candidate cap does not close")

    return {
        "format": "wave112-c4-short-vector-incidence-v1",
        "claim_label": "DERIVED",
        "target": {
            "edges": 693,
            "nonedges": 4158,
            "induced_C4": c4_total,
        },
        "alternating_C4_lower_per_oriented_vector": shell_c4_min,
        "rank28": {
            "short_vector_total_lower": shell_total_lower,
            "weakest_C4_lower_per_vector": weakest,
            "oriented_vector_C4_incidence_lower": incidence_lower,
            "average_oriented_multiplicity": {
                "numerator": incidence_lower,
                "denominator": c4_total,
                "decimal": round(average_oriented, 12),
            },
            "forced_some_C4_oriented_multiplicity": forced_oriented_even,
            "forced_some_C4_antipodal_supports": forced_supports,
            "sufficient_universal_cap_oriented": candidate_cap_oriented,
            "sufficient_universal_cap_antipodal_supports": candidate_cap_supports,
            "incidence_upper_if_cap": upper_if_cap,
        },
        "fixed_C4_outside_partition": fixed_c4_partition(),
        "h0_remaining_side_selection": {
            str(side): homogeneous_extension_selection(side)
            for side in (7, 8, 9)
        },
        "status_wall": {
            "local_cap_25_proved": False,
            "rank28_excluded": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_results()
    if args.verify:
        archived = json.loads(args.verify.read_text(encoding="utf-8"))
        require(result == archived, "archived result mismatch")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
