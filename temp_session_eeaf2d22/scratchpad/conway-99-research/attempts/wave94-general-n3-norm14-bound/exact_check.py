"""Exact arithmetic and finite incidence controls for Wave 94."""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path


DEFAULT_OUTPUT = Path(__file__).with_name("exact-results.json")
BASE = tuple(range(14))


def group(x: int) -> int:
    return x // 2


def mate(x: int) -> int:
    return x ^ 1


def seeds() -> tuple[tuple[int, int, int, int], ...]:
    return tuple(
        q
        for q in combinations(BASE, 4)
        if len({group(x) for x in q}) == 4
    )


def transition_seed_multiplicity(s: int, a: int, b: int) -> int:
    target = {s, a, b}
    return sum(target <= set(q) for q in seeds())


def candidate_transition_rows() -> list[dict]:
    rows = []
    for s in BASE:
        others = [x for x in BASE if group(x) != group(s)]
        for a, b in combinations(others, 2):
            rows.append(
                {
                    "s": s,
                    "a": a,
                    "b": b,
                    "other_endpoints_are_mates": mate(a) == b,
                    "seed_multiplicity": transition_seed_multiplicity(s, a, b),
                }
            )
    return rows


def upper_from_prisms(prisms: int) -> int:
    if prisms < 0:
        raise ValueError("prism count must be nonnegative")
    return (38808 + 12 * prisms) // 7


def upper_from_n3(n3: int) -> int:
    if not 0 <= n3 <= 4158:
        raise ValueError("n3 outside the identity range")
    if (4158 - n3) % 3:
        raise ValueError("n3 is incompatible with integral P")
    return (55440 - 4 * n3) // 7


def exact_result() -> dict:
    qs = seeds()
    rows = candidate_transition_rows()
    mate_rows = [row for row in rows if row["other_endpoints_are_mates"]]
    nonmate_rows = [row for row in rows if not row["other_endpoints_are_mates"]]

    assert len(qs) == 560
    assert len(rows) == 14 * 66
    assert len(mate_rows) == 14 * 6
    assert len(nonmate_rows) == 14 * 60
    assert {row["seed_multiplicity"] for row in mate_rows} == {0}
    assert {row["seed_multiplicity"] for row in nonmate_rows} == {8}

    boundary_rows = []
    for n3 in (4158, 4155, 708, 0):
        prisms = (4158 - n3) // 3
        by_p = upper_from_prisms(prisms)
        by_n3 = upper_from_n3(n3)
        assert by_p == by_n3
        boundary_rows.append(
            {
                "n3": n3,
                "P": prisms,
                "N14_upper_bound": by_p,
            }
        )
    assert [row["N14_upper_bound"] for row in boundary_rows] == [
        5544,
        5545,
        7515,
        7920,
    ]

    full_rows = []
    previous = None
    for prisms in range(1387):
        n3 = 4158 - 3 * prisms
        bound_p = upper_from_prisms(prisms)
        bound_n3 = upper_from_n3(n3)
        assert bound_p == bound_n3
        if previous is not None:
            assert bound_p >= previous
            assert bound_p - previous in (1, 2)
        previous = bound_p
        full_rows.append((n3, prisms, bound_p))

    return {
        "format": "wave94-general-n3-norm14-bound-v1",
        "claim_label": "DERIVED",
        "scope": {
            "target": "hypothetical srg(99,14,1,2)",
            "requires_prism_free_endpoint": False,
            "requires_rank_28": False,
            "N14_counts_both_signs": True,
        },
        "finite_census": {
            "seed_count": len(qs),
            "candidate_transition_rows": len(rows),
            "mate_forbidden_candidate_rows": len(mate_rows),
            "nonmate_candidate_rows": len(nonmate_rows),
            "mate_transition_seed_multiplicity": 0,
            "nonmate_transition_seed_multiplicity": 8,
            "selected_transitions_per_root": 84,
            "selected_transitions_per_seed_cap": 4,
        },
        "prism_multiplicity": {
            "rooted_forbidden_transitions": "f_o=number of prisms containing o",
            "global_identity": "sum_o f_o=6P",
        },
        "bound": {
            "oriented_root_inequality": "a14(o)<=392+2*f_o",
            "global_inequality": "7*N14<=38808+12P",
            "P_form": "N14<=floor((38808+12P)/7)",
            "n3_form": "N14<=floor((55440-4*n3)/7)",
        },
        "boundary_rows": boundary_rows,
        "full_domain_rows_checked": len(full_rows),
        "endpoint": {
            "N16_upper_bound": None,
            "N18_upper_bound": None,
            "strict_n3_upper_bound": None,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "The finite checker does not replace the graph-theoretic prism bijection proof.",
            "The theorem bounds N14 only.",
            "Discovery requires an independent verifier.",
            "No target resolution or novelty claim follows.",
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
    if args.verify:
        observed = json.loads(args.verify.read_text(encoding="utf-8"))
        if observed != payload:
            raise SystemExit("verification mismatch")
        print(f"VERIFIED {args.verify} sha256={sha256(args.verify)}")
        return
    write_json(args.output, payload)
    print(f"WROTE {args.output} sha256={sha256(args.output)}")


if __name__ == "__main__":
    main()

