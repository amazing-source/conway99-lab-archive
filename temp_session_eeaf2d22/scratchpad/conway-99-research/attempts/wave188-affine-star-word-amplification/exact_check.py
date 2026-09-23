"""Exact finite checks for Wave 188 affine star-word amplification."""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


C = 4158
EDGE_WORDS = 693


def compositions_of_seven() -> Iterable[tuple[int, int, int]]:
    for a0 in range(8):
        for a1 in range(8 - a0):
            yield (a0, a1, 7 - a0 - a1)


def orbit_profile_check() -> dict[str, Any]:
    profiles: list[dict[str, Any]] = []
    for a, b in product(compositions_of_seven(), repeat=2):
        # A constant coefficient vector represents zero in a seven-simplex.
        if max(a) == 7 or max(b) == 7:
            continue
        # The selected base word is a circuit meeting both stars. It cannot
        # contain an entire seven-star as a proper dependent subset.
        if a[0] == 0 or b[0] == 0:
            continue
        # Every affine representative is nonzero, so dual distance four
        # forces every orbit weight to be at least four.
        if max(a) + max(b) > 10:
            continue
        base_weight = 14 - a[0] - b[0]
        if not 4 <= base_weight <= 9:
            continue
        weights = tuple(14 - a[i] - b[j] for i in range(3) for j in range(3))
        short = tuple(weight for weight in weights if 4 <= weight <= 9)
        profiles.append(
            {
                "a": a,
                "b": b,
                "base_weight": base_weight,
                "short_count": len(short),
            }
        )

    minimum = min(item["short_count"] for item in profiles)
    equality_count = sum(item["short_count"] == minimum for item in profiles)
    spectrum = Counter(item["short_count"] for item in profiles)
    return {
        "profiles_checked": len(profiles),
        "minimum_short_orbit_words": minimum,
        "minimum_equality_profiles": equality_count,
        "short_count_spectrum": {
            str(count): spectrum[count] for count in sorted(spectrum)
        },
    }


def orbit_weights(a: tuple[int, int, int], b: tuple[int, int, int]) -> list[int]:
    return sorted(14 - a[i] - b[j] for i in range(3) for j in range(3))


def build_results() -> dict[str, Any]:
    orbit = orbit_profile_check()
    type_two = orbit_weights((5, 1, 1), (5, 1, 1))
    triple_leaf = orbit_weights((4, 0, 3), (6, 1, 0))

    private_coefficients = [2, 2, 3, 1, 1]
    word_coefficients = [2, 1, 3, 4, 1]
    difference = [
        word_coefficients[i] - private_coefficients[i] for i in range(5)
    ]

    nonedge_projective = 2 * C
    total_projective = nonedge_projective + EDGE_WORDS
    dual_scalar = 2 * total_projective

    payload: dict[str, Any] = {
        "format": "wave188-affine-star-word-amplification-v1",
        "claim_label": "DERIVED",
        "scope": (
            "conditional rank-11 endpoint lower bound on actual projective "
            "dual words of weights four through nine"
        ),
        "orbit": orbit,
        "canonical_profiles": {
            "type_two_all_orbit_weights": type_two,
            "type_two_short_weights": [weight for weight in type_two if weight <= 9],
            "triple_leaf_all_orbit_weights": triple_leaf,
            "triple_leaf_short_weights": [
                weight for weight in triple_leaf if weight <= 9
            ],
            "one_adjacency_projector_square_sum_mod_3": 7 % 3,
        },
        "global_inequality": {
            "variables": ["n1", "n2", "n3", "p2", "p3"],
            "private_lower_coefficients": private_coefficients,
            "word_lower_coefficients": word_coefficients,
            "coefficient_difference": difference,
            "difference_lower_bound_using_p2_ge_n2": "2*n2",
        },
        "bounds": {
            "nonedges": C,
            "nonedge_projective_short_words": nonedge_projective,
            "edge_isolated_projective_short_words": EDGE_WORDS,
            "total_projective_short_words": total_projective,
            "dual_scalar_short_words": dual_scalar,
        },
        "disposition": {
            "rank_11": "UNKNOWN",
            "endpoint": "UNKNOWN",
            "strict_n3_improvement": "NONE",
            "conway_99": "UNKNOWN",
            "independent_verification": "PENDING",
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["result_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = build_results()
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            print("FAIL Wave 188 exact verification")
            return 1
        print(f"PASS Wave 188 exact verification: {args.verify}")
        return 0
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
