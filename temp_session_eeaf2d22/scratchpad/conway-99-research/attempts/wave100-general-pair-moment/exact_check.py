"""Exact arithmetic for the Wave 100 general pair-moment continuation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_OUTPUT = Path(__file__).with_name("exact-results.json")


def ceil_div(numerator: int, denominator: int) -> int:
    return -(-numerator // denominator)


def rooted_valid_upper(prisms_through_root: int) -> int:
    if not 0 <= prisms_through_root <= 84:
        raise ValueError("rooted prism count must lie in [0,84]")
    nonforbidden_transitions = 84 - prisms_through_root
    bad_seed_lower = ceil_div(5 * nonforbidden_transitions, 2)
    return 560 - bad_seed_lower


def even_floor(value_numerator: int, value_denominator: int) -> int:
    return 2 * (value_numerator // (2 * value_denominator))


def exact_result() -> dict:
    rooted_rows = []
    for f in range(85):
        valid = rooted_valid_upper(f)
        closed = 350 + (5 * f) // 2
        assert valid == closed
        rooted_rows.append(
            {
                "f": f,
                "nonforbidden_transitions": 84 - f,
                "valid_seed_upper": valid,
            }
        )

    global_rows = []
    for prisms in range(1387):
        n3 = 4158 - 3 * prisms
        numerator = 34_650 + 15 * prisms
        assert numerator == 55_440 - 5 * n3
        ordinary = numerator // 7
        antipodal_even = even_floor(numerator, 7)
        assert antipodal_even <= ordinary
        assert ordinary - antipodal_even in (0, 1)
        global_rows.append(
            {
                "P": prisms,
                "n3": n3,
                "seven_N14_upper": numerator,
                "N14_floor_upper": ordinary,
                "N14_even_upper": antipodal_even,
            }
        )

    selected = {
        str(row["n3"]): row
        for row in global_rows
        if row["n3"] in (0, 708, 4152, 4155, 4158)
    }
    return {
        "format": "wave100-general-pair-moment-v1",
        "claim_label": "DERIVED",
        "scope": {
            "target": "hypothetical srg(99,14,1,2)",
            "requires_rank_28": False,
            "requires_prism_free": False,
            "N14_counts_both_signs": True,
        },
        "rooted_formula": {
            "valid_seed_upper": "350+floor(5*f_o/2)",
            "checked_f_values": len(rooted_rows),
            "minimum": rooted_rows[0],
            "maximum": rooted_rows[-1],
        },
        "global_formula": {
            "raw": "7*N14<=34650+15*P=55440-5*n3",
            "floor": "N14<=floor((55440-5*n3)/7)",
            "antipodal_even_rounding": "N14<=2*floor((55440-5*n3)/14)",
            "compatible_rows_checked": len(global_rows),
            "selected_rows": selected,
        },
        "status": {
            "depends_on_unverified_wave99_pair_moment": True,
            "N16_or_N18_upper_bound": "NOT_PROVED",
            "strict_n3_upper_bound": "NOT_PROVED",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "The local pair-moment lemma is imported from unverified Wave 99 discovery.",
            "This bounds only N14.",
            "No strict upper bound on n3 follows without controlling N16 and N18.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = exact_result()
    if args.verify:
        archived = json.loads(args.verify.read_text(encoding="utf-8"))
        if archived != result:
            raise SystemExit("archived result mismatch")
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if not args.verify:
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    print(payload, end="")


if __name__ == "__main__":
    main()
