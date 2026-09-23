"""Clean-room checks for the Wave 78 short-vector packing claims.

This module deliberately imports no discovery code.  It starts from the
conditional signed-support setup already verified in Wave 74 and enumerates
the resulting scalar histogram systems after imposing the packing bounds.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from math import comb
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DISCOVERY = ROOT / "attempts" / "wave78-short-vector-packing"
EXPECTED_DISCOVERY_HASHES = {
    "derivation.md": "c1698795f803d5a2cad8716244d492732d34caaa595e7705650423df04c67434",
    "exact-results.json": "4cc6fe0ac67a2f7cd5c844f39f8de879e50158f34aaf7421393ac4e08ef0c4ca",
    "exact_check.py": "d25c8835bae17f19fd7d3757bab3f3a6dd9cf27d698242f27d110a23b45f99b4",
    "failed-routes.md": "5eed3034a2faf41b073788d7b5c8ce77a9b963041049e4c5723b0ce1f0a156e6",
    "input-freeze.sha256": "f4a12d20bc66a9a6fbe0c910ec50ba2501ad67e6abb8e0a08eb0b1aa4c114fb4",
    "package-manifest.sha256": "5537a48b72733345142b4a6aed2c10110e7a42e4a26efe87a0cf674f41f54c0e",
    "protocol.md": "d7f3dc6d5bf67b9df4237b5e998a736acf6cccef977affd7d596edee9d22b729",
    "README.md": "8fc986450c1131169c37db1871f0e2af1ef25098bc253474812af5bf709c6fcf",
    "run-report.yaml": "e6a8a5b319c7274d22e046f161c938c9566ae6bc6f36b92de2b6f0b454d3cded",
    "test_exact_check.py": "7522df5c3a066cccb68cd22005f31a301bae7353bf09a94cb50fc97a74c9a53e",
}


LANES = {
    "norm16_h0": {
        "outside_vertices": 83,
        "outside_incidences_per_side": 80,
        "outside_pair_incidences": 8,
        "maximum_d": 2,
    },
    "norm18_h0": {
        "outside_vertices": 81,
        "outside_incidences_per_side": 90,
        "outside_pair_incidences": 18,
        "maximum_d": 3,
    },
    "norm18_h1": {
        "outside_vertices": 81,
        "outside_incidences_per_side": 86,
        "outside_pair_incidences": 9,
        "maximum_d": 3,
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_frozen_discovery() -> None:
    found = {
        path.name: sha256(path)
        for path in sorted(DISCOVERY.iterdir())
        if path.is_file()
    }
    if found != EXPECTED_DISCOVERY_HASHES:
        raise AssertionError(
            "discovery package changed after the verifier's input freeze:\n"
            f"expected={EXPECTED_DISCOVERY_HASHES}\nfound={found}"
        )


def enumerate_histograms(
    outside_vertices: int,
    incidence_sum: int,
    pair_sum: int,
    maximum_d: int,
) -> list[list[int]]:
    """Enumerate every [n0,...,n7] satisfying the three scalar moments."""

    if maximum_d < 2 or maximum_d > 7:
        raise ValueError("maximum_d must lie in [2,7]")

    bounds = [
        range(pair_sum // comb(degree, 2) + 1)
        for degree in range(2, maximum_d + 1)
    ]
    answers: list[list[int]] = []
    for tail in itertools.product(*bounds):
        if sum(comb(d, 2) * n for d, n in enumerate(tail, start=2)) != pair_sum:
            continue
        n1 = incidence_sum - sum(
            d * n for d, n in enumerate(tail, start=2)
        )
        n0 = outside_vertices - n1 - sum(tail)
        if n0 < 0 or n1 < 0:
            continue
        row = [n0, n1, *tail]
        row.extend([0] * (8 - len(row)))
        answers.append(row)
    return sorted(answers)


def minimum_union_linear_uniform(
    ground_size: int, block_size: int, block_count: int
) -> tuple[int, int]:
    """Exhaustively find the minimum union of a linear uniform block family.

    "Linear" means every two distinct blocks intersect in at most one point.
    The second return value is the number of unordered families attaining the
    minimum.
    """

    blocks = tuple(itertools.combinations(range(ground_size), block_size))
    best = ground_size + 1
    count = 0

    def extend(chosen: tuple[frozenset[int], ...], start: int) -> None:
        nonlocal best, count
        if len(chosen) == block_count:
            union_size = len(set().union(*chosen))
            if union_size < best:
                best, count = union_size, 1
            elif union_size == best:
                count += 1
            return
        for index in range(start, len(blocks)):
            candidate = frozenset(blocks[index])
            if all(len(candidate & old) <= 1 for old in chosen):
                extend((*chosen, candidate), index + 1)

    extend((), 0)
    return best, count


def equality_rigid_triples_on_nine() -> dict[str, int | bool]:
    """Audit the equality case for three 4-subsets on nine points."""

    blocks = tuple(
        frozenset(block) for block in itertools.combinations(range(9), 4)
    )
    linear = 0
    union_nine = 0
    rigid = 0
    for a, b, c in itertools.combinations(blocks, 3):
        pair_sizes = (len(a & b), len(a & c), len(b & c))
        if max(pair_sizes) > 1:
            continue
        linear += 1
        if len(a | b | c) != 9:
            continue
        union_nine += 1
        if pair_sizes == (1, 1, 1) and not (a & b & c):
            rigid += 1
    return {
        "linear_triples": linear,
        "union_nine_triples": union_nine,
        "rigid_union_nine_triples": rigid,
        "all_union_nine_triples_rigid": union_nine == rigid,
    }


def build_results() -> dict:
    histograms = {
        name: enumerate_histograms(
            lane["outside_vertices"],
            lane["outside_incidences_per_side"],
            lane["outside_pair_incidences"],
            lane["maximum_d"],
        )
        for name, lane in LANES.items()
    }
    min_union_8, count_8 = minimum_union_linear_uniform(8, 4, 3)
    min_union_9, count_9 = minimum_union_linear_uniform(9, 4, 3)
    min_union_9_four, count_9_four = minimum_union_linear_uniform(9, 4, 4)
    rigidity = equality_rigid_triples_on_nine()
    return {
        "format": "wave78-independent-verification-v1",
        "claim_label": "VERIFIED",
        "scope": (
            "conditional on the Wave 71 signed-unit support reduction and "
            "the Wave 74 verified support-incidence equations"
        ),
        "packing": {
            "norm16_maximum_d": 2,
            "norm18_maximum_d": 3,
            "norm16_three_block_minimum_union": min_union_8,
            "norm16_minimum_family_count": count_8,
            "norm18_three_block_minimum_union": min_union_9,
            "norm18_minimum_family_count": count_9,
            "norm18_four_block_union_lower_bound": min_union_9_four,
            "norm18_four_block_family_count": count_9_four,
            "triple_equality_rigidity": rigidity,
            "norm18_h1_d3_avoids_both_same_edge_endpoints": True,
        },
        "lanes": {
            name: {
                **lane,
                "histogram_convention": "[n0,n1,...,n7]",
                "histogram_count": len(histograms[name]),
                "histograms": histograms[name],
            }
            for name, lane in LANES.items()
        },
        "endpoint": {
            "all_short_vector_alternatives_excluded": False,
            "conway_status": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "The packing argument is conditional on the imported support reduction.",
            "The rows are scalar histogram solutions, not incidence matrices.",
            "The h=1 d=3 endpoint-avoidance rule is not encoded by the scalar histogram.",
            "No automorphism or transitivity is assumed.",
            "Conway-99 and novelty remain UNKNOWN.",
        ],
    }


def compare_discovery(results: dict) -> dict:
    """Compare independent rows to the frozen discovery JSON as plain data."""

    discovery = json.loads((DISCOVERY / "exact-results.json").read_text("utf-8"))
    lane_names = {
        "norm16_h0": "norm16",
        "norm18_h0": "norm18_h0",
        "norm18_h1": "norm18_h1",
    }
    comparison = {}
    for independent_name, discovery_name in lane_names.items():
        max_d = results["lanes"][independent_name]["maximum_d"]
        independent_rows = [
            row[: max_d + 1]
            for row in results["lanes"][independent_name]["histograms"]
        ]
        discovery_rows = discovery["histograms"][discovery_name]
        comparison[independent_name] = {
            "histogram_count_exactly_equal": (
                len(independent_rows)
                == discovery["histogram_counts"][discovery_name]
            ),
            "histograms_exactly_equal": independent_rows == discovery_rows,
        }
    return comparison


def verify() -> dict:
    verify_frozen_discovery()
    results = build_results()
    counts = {
        name: lane["histogram_count"] for name, lane in results["lanes"].items()
    }
    if counts != {"norm16_h0": 1, "norm18_h0": 7, "norm18_h1": 4}:
        raise AssertionError(f"unexpected histogram counts: {counts}")
    packing = results["packing"]
    if packing["norm16_three_block_minimum_union"] != 9:
        raise AssertionError("three linear 4-blocks should need at least 9 points")
    if packing["norm18_three_block_minimum_union"] != 9:
        raise AssertionError("the norm-18 equality case should use all 9 points")
    if packing["norm18_four_block_union_lower_bound"] != 10:
        raise AssertionError("four linear 4-blocks should need at least 10 points")
    if packing["norm18_four_block_family_count"] != 0:
        raise AssertionError("four linear 4-blocks unexpectedly fit on 9 points")
    if not packing["triple_equality_rigidity"]["all_union_nine_triples_rigid"]:
        raise AssertionError("a non-rigid equality triple was found")
    results["discovery_comparison"] = compare_discovery(results)
    if not all(
        item["histogram_count_exactly_equal"]
        and item["histograms_exactly_equal"]
        for item in results["discovery_comparison"].values()
    ):
        raise AssertionError(
            f"discovery mismatch: {results['discovery_comparison']}"
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    results = verify() if args.verify else build_results()
    if args.json or args.verify:
        print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
