"""Exact finite checks for the Wave 78 short-vector packing lemma."""

from __future__ import annotations

import argparse
import functools
import itertools
import json
from pathlib import Path


def four_subsets(size: int) -> tuple[frozenset[int], ...]:
    return tuple(frozenset(c) for c in itertools.combinations(range(size), 4))


def admissible_family(family: tuple[frozenset[int], ...]) -> bool:
    return all(
        len(left & right) <= 1
        for left, right in itertools.combinations(family, 2)
    )


@functools.lru_cache(maxsize=None)
def family_census(size: int, family_size: int) -> dict[str, object]:
    subsets = four_subsets(size)
    admissible = []
    for family in itertools.combinations(subsets, family_size):
        if admissible_family(family):
            admissible.append(family)

    union_sizes = sorted({len(set().union(*family)) for family in admissible})
    intersection_profiles = sorted(
        {
            tuple(
                sorted(
                    len(left & right)
                    for left, right in itertools.combinations(family, 2)
                )
            )
            for family in admissible
        }
    )
    triple_intersections = sorted(
        {
            len(family[0].intersection(*family[1:]))
            for family in admissible
            if family_size == 3
        }
    )
    return {
        "ground_set_size": size,
        "family_size": family_size,
        "admissible_family_count": len(admissible),
        "union_sizes": union_sizes,
        "pair_intersection_profiles": [
            list(profile) for profile in intersection_profiles
        ],
        "triple_intersection_sizes": triple_intersections,
    }


def histograms(
    *,
    vertices: int,
    incidence_sum: int,
    pair_sum: int,
    maximum_d: int,
) -> list[list[int]]:
    answers: list[list[int]] = []

    def recurse(d: int, remaining_vertices: int, remaining_inc: int,
                remaining_pairs: int, counts: list[int]) -> None:
        if d == maximum_d:
            count = remaining_vertices
            if (
                d * count == remaining_inc
                and (d * (d - 1) // 2) * count == remaining_pairs
            ):
                answers.append(counts + [count])
            return
        for count in range(remaining_vertices + 1):
            used_inc = d * count
            used_pairs = (d * (d - 1) // 2) * count
            if used_inc > remaining_inc or used_pairs > remaining_pairs:
                break
            recurse(
                d + 1,
                remaining_vertices - count,
                remaining_inc - used_inc,
                remaining_pairs - used_pairs,
                counts + [count],
            )

    recurse(0, vertices, incidence_sum, pair_sum, [])
    return sorted(answers)


@functools.lru_cache(maxsize=1)
def compute() -> dict[str, object]:
    norm16 = histograms(
        vertices=83,
        incidence_sum=80,
        pair_sum=8,
        maximum_d=2,
    )
    norm18_h0 = histograms(
        vertices=81,
        incidence_sum=90,
        pair_sum=18,
        maximum_d=3,
    )
    norm18_h1 = histograms(
        vertices=81,
        incidence_sum=86,
        pair_sum=9,
        maximum_d=3,
    )
    return {
        "format": "wave78-short-vector-packing-v1",
        "claim_label": "DERIVED",
        "set_family_checks": {
            "four_subsets_of_8_family_3": family_census(8, 3),
            "four_subsets_of_9_family_3": family_census(9, 3),
            "four_subsets_of_9_family_4": family_census(9, 4),
        },
        "packing_consequences": {
            "norm16_maximum_outside_degree_per_side": 2,
            "norm18_maximum_outside_degree_per_side": 3,
            "norm18_h1_d3_block_meets_same_sign_edge_endpoints": False,
        },
        "histograms": {
            "norm16": norm16,
            "norm18_h0": norm18_h0,
            "norm18_h1": norm18_h1,
        },
        "histogram_counts": {
            "norm16": len(norm16),
            "norm18_h0": len(norm18_h0),
            "norm18_h1": len(norm18_h1),
        },
        "status": {
            "norm14": "SURVIVES",
            "norm16": "SURVIVES_ONE_HISTOGRAM",
            "norm18_h0": "SURVIVES_SEVEN_HISTOGRAMS",
            "norm18_h1": "SURVIVES_FOUR_HISTOGRAMS",
            "conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verify",
        type=Path,
        help="Compare the exact result with this JSON file.",
    )
    args = parser.parse_args()
    result = compute()
    if args.verify is not None:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            raise SystemExit("verification mismatch")
        print("PASS")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
