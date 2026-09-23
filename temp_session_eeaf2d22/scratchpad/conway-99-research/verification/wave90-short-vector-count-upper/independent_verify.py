#!/usr/bin/env python3
"""Clean-room verifier for the Wave 90 prism-free N14 count.

This module does not import or execute discovery code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(__file__).with_name("independent-results.json")
COMPARISON = Path(__file__).with_name("comparison.json")
DISCOVERY = ROOT / "attempts" / "wave90-short-vector-count-upper"
POINTS = tuple(range(14))
MATE_PAIRS = tuple((2 * i, 2 * i + 1) for i in range(7))
MATE = {a: b for a, b in MATE_PAIRS for a, b in ((a, b), (b, a))}
GROUP = {point: index for index, pair in enumerate(MATE_PAIRS) for point in pair}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rooted_labels() -> tuple[tuple[int, int], ...]:
    return tuple(
        pair
        for pair in combinations(POINTS, 2)
        if GROUP[pair[0]] != GROUP[pair[1]]
    )


def root_seeds() -> tuple[tuple[int, int, int, int], ...]:
    return tuple(
        seed
        for seed in combinations(POINTS, 4)
        if len({GROUP[x] for x in seed}) == 4
    )


def prism_free_transition_triples() -> tuple[tuple[int, int, int], ...]:
    rows = []
    for shared in POINTS:
        others = tuple(
            x for x in POINTS if GROUP[x] != GROUP[shared]
        )
        for left, right in combinations(others, 2):
            if MATE[left] != right:
                rows.append((shared, left, right))
    return tuple(rows)


def matching_rows(items: tuple[int, ...]):
    if not items:
        yield ()
        return
    first = items[0]
    for index in range(1, len(items)):
        second = items[index]
        rest = items[1:index] + items[index + 1 :]
        for tail in matching_rows(rest):
            yield ((first, second),) + tail


def local_prism_free_matchings(shared: int) -> tuple[tuple[tuple[int, int], ...], ...]:
    others = tuple(x for x in POINTS if GROUP[x] != GROUP[shared])
    return tuple(
        matching
        for matching in matching_rows(others)
        if all(MATE[left] != right for left, right in matching)
    )


def fano_lines() -> tuple[frozenset[int], ...]:
    # Nonzero vectors of F_2^3 are encoded by 1,...,7.  A line is
    # {a,b,a xor b}.
    lines = {
        frozenset((a, b, a ^ b))
        for a, b in combinations(range(1, 8), 2)
    }
    assert len(lines) == 7
    return tuple(sorted(lines, key=lambda row: tuple(sorted(row))))


def fano_seed_reconstructions() -> list[dict]:
    negative_points = frozenset(range(1, 8))
    positive_blocks = tuple(negative_points - line for line in fano_lines())
    rows = []
    for root, seed in enumerate(positive_blocks):
        pair_to_other_block = {}
        for pair in combinations(sorted(seed), 2):
            containers = [
                index
                for index, block in enumerate(positive_blocks)
                if set(pair) <= block
            ]
            assert len(containers) == 2 and root in containers
            other = next(index for index in containers if index != root)
            pair_to_other_block[pair] = other
        recovered_positive = {root, *pair_to_other_block.values()}
        recovered_negative = set()
        for left, right in combinations(sorted(recovered_positive), 2):
            recovered_negative.update(
                positive_blocks[left] & positive_blocks[right]
            )
        rows.append(
            {
                "root": root,
                "seed": sorted(seed),
                "six_pair_labels_distinct": len(set(pair_to_other_block.values())) == 6,
                "positive_side_recovered": recovered_positive == set(range(7)),
                "negative_side_recovered": recovered_negative == set(range(1, 8)),
                "sign_vector_recovered": (
                    len(set(pair_to_other_block.values())) == 6
                    and recovered_positive == set(range(7))
                    and recovered_negative == set(range(1, 8))
                ),
            }
        )
    return rows


def independent_result() -> dict:
    labels = rooted_labels()
    seeds = root_seeds()
    transitions = prism_free_transition_triples()
    assert len(labels) == 84
    assert len(seeds) == 560
    assert len(transitions) == 840

    seed_sets = tuple(frozenset(seed) for seed in seeds)
    extensions = [
        sum({shared, left, right} <= seed for seed in seed_sets)
        for shared, left, right in transitions
    ]
    assert set(extensions) == {8}

    local_counts = []
    local_star_caps = []
    for shared in POINTS:
        matchings = local_prism_free_matchings(shared)
        local_counts.append(len(matchings))
        cap = 0
        for seed in seed_sets:
            if shared not in seed:
                continue
            star = seed - {shared}
            for matching in matchings:
                selected = sum(
                    {left, right} <= star for left, right in matching
                )
                cap = max(cap, selected)
        local_star_caps.append(cap)
    assert set(local_counts) == {6040}
    assert set(local_star_caps) == {1}

    selected_transitions = 14 * 6
    transition_seed_incidences = selected_transitions * 8
    per_seed_cap = 4 * 1
    bad_seed_lower_bound = transition_seed_incidences // per_seed_cap
    good_seed_upper_bound = len(seeds) - bad_seed_lower_bound
    assert (
        selected_transitions,
        transition_seed_incidences,
        per_seed_cap,
        bad_seed_lower_bound,
        good_seed_upper_bound,
    ) == (84, 672, 4, 168, 392)

    fano_rows = fano_seed_reconstructions()
    assert len(fano_rows) == 7
    assert all(row["sign_vector_recovered"] for row in fano_rows)

    # N14 counts oriented vectors: t and -t are distinct.  Every oriented
    # vector has seven positive coordinates.  Equivalently, an antipodal
    # pair contributes 14 rooted-positive incidences, seven per orientation.
    rooted_total = 99 * good_seed_upper_bound
    n14_bound = rooted_total // 7
    assert rooted_total % 7 == 0
    assert n14_bound == 5544 and n14_bound % 2 == 0

    return {
        "format": "wave90-short-vector-count-upper-independent-v1",
        "role": "verifier",
        "claim_label": "VERIFIED",
        "scope": {
            "hypothetical_graph": "srg(99,14,1,2)",
            "requires_prism_free_endpoint_P0": True,
            "equivalent_endpoint_value_imported": "n3=4158",
            "requires_rank_28": False,
            "N14_counts_oriented_vectors_both_signs": True,
        },
        "rooted_scaffold": {
            "mate_pairs": 7,
            "residual_labels": len(labels),
            "seed_count": len(seeds),
            "seed_formula": "C(7,4)*2^4",
            "prism_free_transition_candidates": len(transitions),
            "candidate_transitions_per_base": len(transitions) // 14,
            "local_prism_free_matching_counts": local_counts,
        },
        "injectivity": {
            "principle": (
                "Q gives the six complementary-Fano pair labels and hence "
                "the positive side; saturated mu=2 common-neighbor pairs "
                "of positive vertices recover the full negative side"
            ),
            "canonical_fano_rows": fano_rows,
            "all_roots_reconstruct_both_sign_sides": True,
            "root_positive_removes_global_sign_ambiguity": True,
        },
        "transition_count": {
            "selected_transitions": selected_transitions,
            "seed_extensions_per_selected_transition": sorted(set(extensions)),
            "transition_seed_incidences": transition_seed_incidences,
            "local_selected_transition_cap": sorted(set(local_star_caps)),
            "selected_transitions_per_seed_cap": per_seed_cap,
            "bad_seed_lower_bound": bad_seed_lower_bound,
            "rooted_vector_upper_bound": good_seed_upper_bound,
        },
        "global_count": {
            "root_count": 99,
            "positive_coordinates_per_oriented_vector": 7,
            "antipodal_pair_rooted_positive_incidences": 14,
            "identity": "7*N14=sum_o #{t:t_o=+1}",
            "N14_upper_bound": n14_bound,
        },
        "verdict": {
            "N14_upper_bound_5544": "VERIFIED_SCOPED",
            "N14_plus_N16_plus_N18_upper_bound": "NOT_PROVED",
            "q16_excluded": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "The theorem is conditional on the prism-free endpoint.",
            "The theorem bounds N14 only, not N16 or N18.",
            "No rank-28 hypothesis is used in this upper bound.",
            "No graph nonexistence or Conway-99 resolution follows alone.",
        ],
    }


def write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def discovery_projection(payload: dict) -> dict:
    return {
        "scope": {
            "requires_prism_free_endpoint": payload["scope"][
                "requires_prism_free_endpoint"
            ],
            "requires_n3": payload["scope"]["requires_n3"],
            "n14_counts_both_signs": payload["scope"]["n14_counts_both_signs"],
            "does_not_require_rank_28_for_bound_itself": payload["scope"][
                "does_not_require_rank_28_for_bound_itself"
            ],
        },
        "rooted": {
            "residual_labels": payload["rooted_scaffold"]["residual_labels"],
            "seed_count": payload["rooted_scaffold"]["seed_count"],
        },
        "transition": {
            "selected_transition_count": payload["transition_double_count"][
                "selected_transition_count"
            ],
            "seed_multiplicity": payload["transition_double_count"][
                "seed_multiplicity_per_selected_transition"
            ],
            "incidences": payload["transition_double_count"][
                "transition_seed_incidences"
            ],
            "per_seed_cap": payload["transition_double_count"][
                "selected_transitions_per_seed_upper_bound"
            ],
            "rooted_bound": payload["transition_double_count"][
                "valid_seed_upper_bound"
            ],
        },
        "global": payload["global_bound"]["N14_upper_bound"],
    }


def independent_projection(payload: dict) -> dict:
    return {
        "scope": {
            "requires_prism_free_endpoint": payload["scope"][
                "requires_prism_free_endpoint_P0"
            ],
            "requires_n3": 4158,
            "n14_counts_both_signs": payload["scope"][
                "N14_counts_oriented_vectors_both_signs"
            ],
            "does_not_require_rank_28_for_bound_itself": not payload["scope"][
                "requires_rank_28"
            ],
        },
        "rooted": {
            "residual_labels": payload["rooted_scaffold"]["residual_labels"],
            "seed_count": payload["rooted_scaffold"]["seed_count"],
        },
        "transition": {
            "selected_transition_count": payload["transition_count"][
                "selected_transitions"
            ],
            "seed_multiplicity": payload["transition_count"][
                "seed_extensions_per_selected_transition"
            ][0],
            "incidences": payload["transition_count"][
                "transition_seed_incidences"
            ],
            "per_seed_cap": payload["transition_count"][
                "selected_transitions_per_seed_cap"
            ],
            "rooted_bound": payload["transition_count"][
                "rooted_vector_upper_bound"
            ],
        },
        "global": payload["global_count"]["N14_upper_bound"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--compare-discovery", action="store_true")
    args = parser.parse_args()
    payload = independent_result()
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.verify:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != encoded:
            raise SystemExit("independent canonical result mismatch")
    else:
        write_json(args.output, payload)
    if args.compare_discovery:
        discovery_payload = json.loads(
            (DISCOVERY / "exact-results.json").read_text(encoding="utf-8")
        )
        left = independent_projection(payload)
        right = discovery_projection(discovery_payload)
        comparison = {
            "independent": left,
            "discovery": right,
            "mismatches": [] if left == right else ["projection"],
        }
        write_json(COMPARISON, comparison)
        if left != right:
            raise SystemExit("discovery comparison mismatch")
    print("PASS: Wave90 independent reconstruction")


if __name__ == "__main__":
    main()
