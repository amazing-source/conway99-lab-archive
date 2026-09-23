#!/usr/bin/env python3
"""Clean-room exact verification of the Wave 74 incidence argument.

This module does not import or execute the discovery checker.  Its histogram
enumerator uses a direct Cartesian search over n_2,...,n_7 and solves for
n_1,n_0, unlike the discovery code's recursive enumeration over all n_d.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from math import comb
from pathlib import Path


V = 99
K = 14
LAMBDA = 1
MU = 2
ROOT = Path(__file__).resolve().parents[2]
DISCOVERY_RESULT = (
    ROOT / "attempts" / "wave74-short-vector-closure" / "exact-results.json"
)
CANONICAL = Path(__file__).with_name("independent-results.json")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def two_edge_shape_degree_multisets(side_size: int) -> dict[tuple[int, ...], int]:
    """Exhaust all unordered pairs of distinct simple edges."""
    edges = list(itertools.combinations(range(side_size), 2))
    classes: dict[tuple[int, ...], int] = {}
    for edge_a, edge_b in itertools.combinations(edges, 2):
        degrees = [0] * side_size
        for u, v in (edge_a, edge_b):
            degrees[u] += 1
            degrees[v] += 1
        key = tuple(sorted(degrees, reverse=True))
        classes[key] = classes.get(key, 0) + 1
    return classes


def same_side_degrees(
    side_size: int, same_edges: int, shape: str
) -> tuple[int, ...]:
    if same_edges == 0 and shape == "empty":
        return (0,) * side_size
    if same_edges == 1 and shape == "single":
        return (1, 1) + (0,) * (side_size - 2)
    if same_edges == 2 and shape == "disjoint":
        return (1, 1, 1, 1) + (0,) * (side_size - 4)
    if same_edges == 2 and shape == "adjacent":
        return (2, 1, 1) + (0,) * (side_size - 3)
    raise ValueError((side_size, same_edges, shape))


def lane_scalars(
    side_size: int, same_edges: int, shape: str
) -> dict[str, int | str | bool]:
    """Derive every scalar directly from the SRG and eigenvector equations."""
    degrees = same_side_degrees(side_size, same_edges, shape)
    assert sum(degrees) == 2 * same_edges

    # At=-4t gives opposite_degree(v)=4+same_degree(v) on either sign side.
    cross_edges = sum(4 + degree for degree in degrees)
    assert cross_edges == 4 * side_size + 2 * same_edges

    outside_vertices = V - 2 * side_size
    outside_incidences = K * side_size - 2 * same_edges - cross_edges

    # Adjacent pairs have lambda common neighbors and nonadjacent pairs mu.
    pair_capacity = (
        same_edges * LAMBDA
        + (comb(side_size, 2) - same_edges) * MU
    )
    through_opposite_support = sum(
        comb(4 + degree, 2) for degree in degrees
    )
    through_same_support = sum(comb(degree, 2) for degree in degrees)
    outside_pair_incidences = (
        pair_capacity - through_opposite_support - through_same_support
    )

    # A zero coordinate has d neighbors in each sign side and hence 2d total.
    outside_edges = (
        K * outside_vertices - 2 * outside_incidences
    ) // 2

    return {
        "side_size": side_size,
        "same_edges_per_side": same_edges,
        "shape": shape,
        "outside_vertices": outside_vertices,
        "cross_edges": cross_edges,
        "outside_incidences_per_side": outside_incidences,
        "same_side_pair_capacity": pair_capacity,
        "pair_incidences_through_opposite_support": through_opposite_support,
        "pair_incidences_through_same_support": through_same_support,
        "outside_pair_incidences": outside_pair_incidences,
        "outside_induced_edges": outside_edges,
        "opposite_support_already_exceeds_capacity": (
            through_opposite_support > pair_capacity
        ),
    }


def cartesian_histograms(
    vertices: int, incidence_sum: int, pair_sum: int
) -> list[list[int]]:
    """Enumerate all n_0,...,n_7 by searching n_2,...,n_7 directly.

    For every choice of n_2,...,n_7 satisfying the pair moment, the incidence
    and vertex equations uniquely determine n_1 and n_0.  The finite ranges
    are exhaustive because C(d,2)n_d <= pair_sum for every d >= 2.
    """
    if pair_sum < 0:
        return []
    high_degrees = range(2, 8)
    ranges = [
        range(pair_sum // comb(degree, 2) + 1)
        for degree in high_degrees
    ]
    answers: list[list[int]] = []
    for high_counts in itertools.product(*ranges):
        if sum(
            comb(degree, 2) * count
            for degree, count in zip(high_degrees, high_counts)
        ) != pair_sum:
            continue
        n1 = incidence_sum - sum(
            degree * count
            for degree, count in zip(high_degrees, high_counts)
        )
        n0 = vertices - n1 - sum(high_counts)
        if n0 < 0 or n1 < 0:
            continue
        answers.append([n0, n1, *high_counts])
    return sorted(answers)


def histogram_moments(histogram: list[int]) -> tuple[int, int, int]:
    return (
        sum(histogram),
        sum(degree * count for degree, count in enumerate(histogram)),
        sum(
            comb(degree, 2) * count
            for degree, count in enumerate(histogram)
        ),
    )


def checked_lane(
    name: str, side_size: int, same_edges: int, shape: str
) -> dict[str, object]:
    scalars = lane_scalars(side_size, same_edges, shape)
    if scalars["opposite_support_already_exceeds_capacity"]:
        histograms: list[list[int]] = []
    else:
        histograms = cartesian_histograms(
            int(scalars["outside_vertices"]),
            int(scalars["outside_incidences_per_side"]),
            int(scalars["outside_pair_incidences"]),
        )
    expected_moments = (
        int(scalars["outside_vertices"]),
        int(scalars["outside_incidences_per_side"]),
        int(scalars["outside_pair_incidences"]),
    )
    assert all(
        histogram_moments(histogram) == expected_moments
        for histogram in histograms
    )
    return {
        "name": name,
        **scalars,
        "histogram_convention": "[n0,n1,...,n7], d counts each sign side",
        "histogram_count": len(histograms),
        "histograms": histograms,
    }


def discovery_comparison(
    lanes: dict[str, dict[str, object]]
) -> dict[str, object]:
    discovery = json.loads(DISCOVERY_RESULT.read_text(encoding="utf-8"))
    comparisons: dict[str, object] = {}
    for name in ("norm16_h0", "norm18_h0", "norm18_h1"):
        observed = lanes[name]
        claimed = discovery["lanes"][name]
        comparisons[name] = {
            "histograms_exactly_equal": (
                observed["histograms"] == claimed["histograms"]
            ),
            "scalar_tuple_exactly_equal": (
                (
                    observed["outside_vertices"],
                    observed["outside_incidences_per_side"],
                    observed["outside_pair_incidences"],
                    observed["outside_induced_edges"],
                )
                == (
                    claimed["outside_vertices"],
                    claimed["outside_incidences_per_side"],
                    claimed["outside_pair_incidences"],
                    claimed["outside_induced_edges"],
                )
            ),
        }
    assert all(
        value["histograms_exactly_equal"]
        and value["scalar_tuple_exactly_equal"]
        for value in comparisons.values()
    )
    return comparisons


def build_results() -> dict[str, object]:
    shapes = two_edge_shape_degree_multisets(9)
    expected_shapes = {
        (2, 1, 1, 0, 0, 0, 0, 0, 0): 252,
        (1, 1, 1, 1, 0, 0, 0, 0, 0): 378,
    }
    assert shapes == expected_shapes

    lanes = {
        lane["name"]: lane
        for lane in (
            checked_lane("norm16_h0", 8, 0, "empty"),
            checked_lane("norm18_h0", 9, 0, "empty"),
            checked_lane("norm18_h1", 9, 1, "single"),
            checked_lane("norm18_h2_adjacent", 9, 2, "adjacent"),
            checked_lane("norm18_h2_disjoint", 9, 2, "disjoint"),
        )
    }

    adjacent = lanes["norm18_h2_adjacent"]
    assert adjacent["same_side_pair_capacity"] == 70
    assert adjacent["pair_incidences_through_opposite_support"] == 71
    assert adjacent["pair_incidences_through_same_support"] == 1
    assert adjacent["outside_pair_incidences"] == -2
    assert adjacent["opposite_support_already_exceeds_capacity"]

    disjoint = lanes["norm18_h2_disjoint"]
    assert disjoint["same_side_pair_capacity"] == 70
    assert disjoint["pair_incidences_through_opposite_support"] == 70
    assert disjoint["pair_incidences_through_same_support"] == 0
    assert disjoint["outside_pair_incidences"] == 0
    assert disjoint["outside_vertices"] == 81
    assert disjoint["outside_incidences_per_side"] == 82
    assert disjoint["histograms"] == []

    assert len(lanes["norm16_h0"]["histograms"]) == 4
    assert len(lanes["norm18_h0"]["histograms"]) == 20
    assert len(lanes["norm18_h1"]["histograms"]) == 6

    comparison = discovery_comparison(lanes)
    return {
        "format": "wave74-independent-verification-v1",
        "claim_label": "VERIFIED",
        "scope": (
            "conditional on Wave71's stated signed-unit support reduction; "
            "no verification of the Wave71 modular/lattice derivation"
        ),
        "input_discovery_sha256": sha256(DISCOVERY_RESULT),
        "two_edge_shape_exhaustion": {
            "side_size": 9,
            "unordered_distinct_edge_pairs": 630,
            "adjacent_shape_count": 252,
            "disjoint_shape_count": 378,
            "other_shapes": 0,
        },
        "lanes": lanes,
        "discovery_comparison": comparison,
        "verified_claims": {
            "norm18_h2_adjacent_impossible": True,
            "norm18_h2_disjoint_impossible": True,
            "norm18_surviving_h": [0, 1],
            "norm16_h0_histogram_count": 4,
            "norm18_h0_histogram_count": 20,
            "norm18_h1_histogram_count": 6,
        },
        "hostile_controls": {
            "disjoint_h2_at_81_incidences_has_one_histogram": (
                cartesian_histograms(81, 81, 0)
                == [[0, 81, 0, 0, 0, 0, 0, 0]]
            ),
            "disjoint_h2_at_82_incidences_has_no_histogram": (
                cartesian_histograms(81, 82, 0) == []
            ),
            "maximum_d_is_seven_from_total_support_degree_2d_le_14": True,
        },
        "audit_note": (
            "The discovery JSON's adjacent-h2 outside_pair_incidences=-1 is "
            "capacity minus the already-fatal opposite-support term only. "
            "After also subtracting its one same-support common-neighbor "
            "incidence, the formal full residual is -2. The contradiction "
            "71>70 is unchanged, and no adjacent-lane histogram is used."
        ),
        "limitations": [
            "This verification is conditional on Wave71's support reduction.",
            "The surviving histograms are necessary aggregate moments only.",
            "No histogram is promoted to an incidence matrix or graph realization.",
            "Norm14, norm16 h=0, and norm18 h=0,1 remain live.",
            "No automorphism or transitivity is assumed.",
            "Conway-99 and novelty remain UNKNOWN.",
        ],
        "endpoint": {
            "all_short_vector_alternatives_excluded": False,
            "conway_status": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def canonical_bytes(payload: dict[str, object]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    encoded = canonical_bytes(build_results())
    if args.write:
        CANONICAL.write_bytes(encoded)
        print(f"WROTE {CANONICAL}")
    elif args.verify:
        if CANONICAL.read_bytes() != encoded:
            raise SystemExit("independent-results.json is stale")
        print("PASS: Wave74 independent result matches exact recomputation")
    else:
        print(encoded.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
