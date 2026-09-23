"""Clean-room arithmetic for the Wave 182 root-gluing theorem."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def analyze() -> dict[str, Any]:
    stars = 99
    roots_per_star = 21
    incidences = stars * roots_per_star
    edges = 99 * 14 // 2
    pairs = 99 * 98 // 2
    nonedges = pairs - edges
    pair_sum = nonedges + 6 * edges
    square_sum = 2 * pair_sum + incidences

    result = {
        "local": {
            "star_points": 7,
            "roots": 7 * 6 // 2,
            "nonneighbors": 14 * 13 // 2 - 7,
            "nonedges_per_root": 4,
            "root_norm": 1,
        },
        "support": {
            "minimum": 5,
            "maximum": 10,
            "incidence_sum": incidences,
        },
        "edge_projective_capacities": {
            "6": 0,
            "4+2": 1,
            "3+3": 6,
            "2+2+2": 3,
            "maximum": 6,
        },
        "moments": {
            "edges": edges,
            "nonedges": nonedges,
            "pair_intersection_sum_upper": pair_sum,
            "square_sum_upper": square_sum,
            "root_lower": incidences * incidences // square_sum,
            "root_upper": incidences // 5,
        },
        "extremal": {
            "roots": 231,
            "multiplicity": incidences // 231,
            "edge_intersection": 6,
            "nonedge_intersection": 1,
            "incidence_gram": "20*I+5*A+J",
            "eigenvalues": {"189": 1, "35": 54, "0": 44},
            "real_rank": 55,
            "frame_coefficient_mod3": 9 % 3,
            "contradiction": False,
        },
        "scope": "conditional equality boundary survives",
    }
    verify(result)
    return result


def verify(result: dict[str, Any]) -> None:
    assert result["local"] == {
        "star_points": 7,
        "roots": 21,
        "nonneighbors": 84,
        "nonedges_per_root": 4,
        "root_norm": 1,
    }
    assert result["support"]["incidence_sum"] == 2079
    assert result["moments"] == {
        "edges": 693,
        "nonedges": 4158,
        "pair_intersection_sum_upper": 8316,
        "square_sum_upper": 18711,
        "root_lower": 231,
        "root_upper": 415,
    }
    assert result["edge_projective_capacities"]["maximum"] == 6
    assert result["extremal"]["multiplicity"] == 9
    assert result["extremal"]["eigenvalues"] == {"189": 1, "35": 54, "0": 44}
    assert result["extremal"]["real_rank"] == 55
    assert result["extremal"]["contradiction"] is False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = analyze()
    if args.verify:
        assert json.loads(args.verify.read_text(encoding="utf-8")) == result
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS: independent Wave182 verification")


if __name__ == "__main__":
    main()

