"""Fixed exact checks for Wave192 equality-face proof A."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


def add_mod3(left: Iterable[int], scalar: int, right: Iterable[int]) -> list[int]:
    return [(a + scalar * b) % 3 for a, b in zip(left, right)]


def support(vector: list[int]) -> list[int]:
    return [index for index, value in enumerate(vector) if value]


def side_profile(vector: list[int]) -> list[int]:
    return [
        sum(value != 0 for value in vector[:7]),
        sum(value != 0 for value in vector[7:]),
    ]


def equality_row(m: int) -> dict[str, int]:
    c = 4158
    if not 0 <= m <= c // 2:
        raise ValueError("m outside equality range")
    row = {
        "C": c,
        "n1": c - 2 * m,
        "n2": 0,
        "n3": m,
        "p2": 0,
        "p3": m,
        "r": c // 2,
        "r1": m,
        "t": m,
        "u": 0,
        "delta": m,
        "h": 0,
        "Y": 0,
        "Z": 0,
    }
    row["A"] = row["n1"] + 2 * row["p2"] + row["p3"]
    row["B"] = row["n1"] + row["n2"] + 2 * row["n3"]
    row["I"] = (
        2 * row["n1"]
        + 2 * row["n2"]
        + 3 * row["n3"]
        + row["p2"]
        + row["p3"]
    )
    row["Q"] = row["B"] + row["r"] + 2 * row["h"] + row["Y"]
    row["exact2_raw_circuits"] = row["r"] - row["r1"]
    row["type1_raw_assignments"] = row["n1"]
    row["nonprivate_labels"] = m
    row["nonprivate_selected_incidence"] = 2 * m
    return row


def derive() -> dict[str, object]:
    # Canonical conic relation on two disjoint seven-stars.
    conic = [1, 2, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0]
    star_x = [1] * 7 + [0] * 7
    axis_one = add_mod3(conic, 1, star_x)
    axis_two = add_mod3(conic, 2, star_x)

    rows = [equality_row(m) for m in (0, 1, 2079)]
    for row in rows:
        assert row["I"] == 2 * row["C"]
        assert row["B"] == row["C"]
        assert row["Q"] == 6237
        assert row["delta"] == 2 * row["r"] + 3 * row["h"] - row["A"]
        assert (
            2 * row["exact2_raw_circuits"]
            == row["type1_raw_assignments"]
        )
        assert row["nonprivate_selected_incidence"] == 2 * row["nonprivate_labels"]

    result = {
        "equality_face": {
            "parameter": "0<=m<=2079",
            "formula": (
                "n1=C-2m,n2=p2=0,n3=p3=m,r=2079,"
                "r1=t=delta=m,h=u=Y=Z=0"
            ),
            "sample_rows": rows,
            "type1_label_pairing": (
                "2*(2079-m) type1 assignments saturate 2079-m "
                "canonical tau-pairs"
            ),
            "type3_nonprivate_degree": (
                "m nonprivate labels receive 2m selected incidences, "
                "hence degree two each"
            ),
        },
        "residual_capacity": {
            "exact2_residual": "impossible by Wave181 uniqueness",
            "closed_pool": "Y=y+2g,Z<=y+3g,therefore 2Z<=3Y",
            "equality_consequence": "Y=Z=0 and every type3 raw is exact1",
        },
        "affine_conic": {
            "conic": conic,
            "axis_one": axis_one,
            "axis_two": axis_two,
            "profiles": [side_profile(axis_one), side_profile(axis_two)],
            "conic_support": support(conic),
            "axis_one_support": support(axis_one),
            "axis_two_support": support(axis_two),
            "conic_contained_in_axis_one": set(support(conic)) <= set(support(axis_one)),
            "conic_contained_in_axis_two": set(support(conic)) <= set(support(axis_two)),
            "axes_same_support": support(axis_one) == support(axis_two),
        },
        "strict_bound": {
            "nonedge_projective_Q": 6238,
            "edge_added_projective": 6238 + 693,
            "circuit_scalar_words": 2 * (6238 + 693),
        },
        "search_scope": (
            "fixed F3 vectors and symbolic equality identities only; "
            "no graph, code, cover, SAT, LP, configuration, enumeration, "
            "or isomorphism search"
        ),
        "claim_label": "DERIVED_PENDING_INDEPENDENT_VERIFICATION",
    }

    assert side_profile(axis_one) == [6, 2]
    assert side_profile(axis_two) == [6, 2]
    assert not result["affine_conic"]["conic_contained_in_axis_one"]
    assert not result["affine_conic"]["conic_contained_in_axis_two"]
    assert not result["affine_conic"]["axes_same_support"]
    assert result["strict_bound"]["edge_added_projective"] == 6931
    assert result["strict_bound"]["circuit_scalar_words"] == 13862
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = derive()
    if args.verify is not None:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            raise SystemExit("verification mismatch")
        print("PASS: Wave192 proof-A exact result matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
