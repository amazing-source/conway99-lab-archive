"""Exact finite checks for the Wave 90 prism-free N14 upper bound.

Discovery only.  The checker certifies arithmetic and finite incidence
claims; the mathematical scope and injectivity argument are in derivation.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path


DEFAULT_OUTPUT = Path(__file__).with_name("exact-results.json")
BASE = tuple(range(14))


def mate(x: int) -> int:
    return x ^ 1


def group(x: int) -> int:
    return x // 2


def edge(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def residual_labels() -> tuple[tuple[int, int], ...]:
    return tuple(
        edge(a, b)
        for a, b in combinations(BASE, 2)
        if group(a) != group(b)
    )


def seeds() -> tuple[tuple[int, int, int, int], ...]:
    return tuple(
        q
        for q in combinations(BASE, 4)
        if len({group(x) for x in q}) == 4
    )


def allowed_transition_triples() -> tuple[tuple[int, int, int], ...]:
    """Return (shared base, other endpoint 1, other endpoint 2).

    These are all possible prism-free transitions.  A selected transition
    system chooses six at each shared base as a perfect matching.
    """

    rows = []
    for s in BASE:
        others = [x for x in BASE if group(x) != group(s)]
        for a, b in combinations(others, 2):
            if group(a) != group(b):
                rows.append((s, a, b))
    return tuple(rows)


def perfect_matchings(items: tuple[int, ...]):
    """Enumerate perfect matchings recursively as tuples of pairs."""

    if not items:
        yield ()
        return
    first = items[0]
    for index in range(1, len(items)):
        second = items[index]
        rest = items[1:index] + items[index + 1 :]
        for tail in perfect_matchings(rest):
            yield ((first, second),) + tail


def allowed_local_matching_count() -> int:
    """Count matchings of twelve endpoints avoiding the six mate pairs."""

    items = tuple(range(12))
    return sum(
        1
        for matching in perfect_matchings(items)
        if all(mate(a) != b for a, b in matching)
    )


def fano_lines() -> tuple[frozenset[int], ...]:
    return (
        frozenset((0, 1, 3)),
        frozenset((0, 2, 5)),
        frozenset((0, 4, 6)),
        frozenset((1, 2, 4)),
        frozenset((1, 5, 6)),
        frozenset((2, 3, 6)),
        frozenset((3, 4, 5)),
    )


def fano_reconstruction_rows() -> list[dict]:
    points = frozenset(range(7))
    blocks = tuple(points - line for line in fano_lines())
    rows = []
    for root_index, q in enumerate(blocks):
        other_blocks = set()
        for pair in combinations(sorted(q), 2):
            containing = [
                index
                for index, block in enumerate(blocks)
                if set(pair) <= block
            ]
            assert len(containing) == 2
            containing.remove(root_index)
            other_blocks.add(containing[0])
        recovered_positive = {root_index} | other_blocks
        recovered_negative = set()
        for i, j in combinations(sorted(recovered_positive), 2):
            recovered_negative.update(blocks[i] & blocks[j])
        rows.append(
            {
                "root_index": root_index,
                "q": sorted(q),
                "other_positive_blocks": sorted(other_blocks),
                "recovered_negative_points": sorted(recovered_negative),
                "unique_reconstruction": (
                    len(other_blocks) == 6
                    and recovered_positive == set(range(7))
                    and recovered_negative == set(range(7))
                ),
            }
        )
    return rows


def exact_result() -> dict:
    labels = residual_labels()
    qs = seeds()
    transitions = allowed_transition_triples()

    assert len(labels) == 84
    assert len(qs) == 560
    assert len(transitions) == 14 * 60

    seed_sets = [frozenset(q) for q in qs]
    transition_seed_multiplicities = []
    for s, a, b in transitions:
        multiplicity = sum({s, a, b} <= q for q in seed_sets)
        transition_seed_multiplicities.append(multiplicity)
    assert set(transition_seed_multiplicities) == {8}

    local_matchings = allowed_local_matching_count()
    assert local_matchings == 6040

    selected_transitions_per_base = 6
    selected_transition_count = 14 * selected_transitions_per_base
    seed_multiplicity = 8
    transition_seed_incidences = selected_transition_count * seed_multiplicity
    per_seed_cap = 4
    bad_seed_lower_bound = transition_seed_incidences // per_seed_cap
    assert transition_seed_incidences % per_seed_cap == 0
    valid_seed_upper_bound = len(qs) - bad_seed_lower_bound
    n14_upper_bound = 99 * valid_seed_upper_bound // 7
    assert 99 * valid_seed_upper_bound % 7 == 0
    assert (
        selected_transition_count,
        transition_seed_incidences,
        bad_seed_lower_bound,
        valid_seed_upper_bound,
        n14_upper_bound,
    ) == (84, 672, 168, 392, 5544)

    fano_rows = fano_reconstruction_rows()
    assert all(row["unique_reconstruction"] for row in fano_rows)

    return {
        "format": "wave90-short-vector-count-upper-v1",
        "claim_label": "DERIVED",
        "scope": {
            "target": "hypothetical srg(99,14,1,2)",
            "requires_prism_free_endpoint": True,
            "requires_n3": 4158,
            "n14_counts_both_signs": True,
            "does_not_require_rank_28_for_bound_itself": True,
        },
        "rooted_scaffold": {
            "base_vertices": 14,
            "mate_pairs": 7,
            "residual_labels": len(labels),
            "seed_count": len(qs),
            "seed_formula": "C(7,4)*2^4",
            "allowed_transition_candidates_per_base": len(transitions) // 14,
            "allowed_local_perfect_matchings": local_matchings,
        },
        "transition_double_count": {
            "selected_transitions_per_base": selected_transitions_per_base,
            "selected_transition_count": selected_transition_count,
            "seed_multiplicity_per_selected_transition": seed_multiplicity,
            "transition_seed_incidences": transition_seed_incidences,
            "selected_transitions_per_seed_upper_bound": per_seed_cap,
            "bad_seed_lower_bound": bad_seed_lower_bound,
            "valid_seed_upper_bound": valid_seed_upper_bound,
        },
        "fano_injectivity_control": {
            "rows": fano_rows,
            "all_seven_roots_reconstruct": True,
        },
        "global_bound": {
            "rooted_positive_vector_upper_bound": valid_seed_upper_bound,
            "positive_coordinates_per_vector": 7,
            "root_count": 99,
            "double_count": "7*N14 <= 99*392",
            "N14_upper_bound": n14_upper_bound,
        },
        "endpoint": {
            "N14_plus_N16_plus_N18_upper_bound": None,
            "prism_free_rank_28_excluded": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "Prism-freeness is essential to the eight-seed transition multiplicity.",
            "The proof does not bound N16 or N18.",
            "The package is discovery and requires an independent verifier.",
            "No graph, lattice, or Conway-99 resolution is claimed.",
        ],
    }


def write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    payload = exact_result()
    if args.verify is not None:
        observed = json.loads(args.verify.read_text(encoding="utf-8"))
        if observed != payload:
            raise SystemExit("verification mismatch")
        print(f"VERIFIED {args.verify} sha256={sha256(args.verify)}")
        return
    write_json(args.output, payload)
    print(f"WROTE {args.output} sha256={sha256(args.output)}")


if __name__ == "__main__":
    main()

