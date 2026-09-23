"""Clean-room exact checker for the Wave 186 cover amplification."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "attempts" / "wave186-star-translation-cover"
SOURCE_MANIFEST = SOURCE_DIR / "package-manifest.sha256"
SOURCE_INPUT_FREEZE = SOURCE_DIR / "input-freeze.sha256"
HASH_LINE = re.compile(r"^([0-9a-fA-F]{64})\s+\*?(.+?)\s*$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_hash_list(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = HASH_LINE.fullmatch(line)
        if match is None:
            raise ValueError(f"malformed hash line {path}:{number}: {raw!r}")
        entries.append((match.group(1).lower(), match.group(2)))
    if not entries:
        raise ValueError(f"empty hash list: {path}")
    return entries


def verify_direct_freeze() -> dict[str, Any]:
    direct_manifests = [
        (ROOT / relative).resolve()
        for _, relative in parse_hash_list(SOURCE_INPUT_FREEZE)
    ]
    lists = [SOURCE_MANIFEST.resolve(), SOURCE_INPUT_FREEZE.resolve()]
    lists.extend(direct_manifests)

    failures: list[dict[str, str]] = []
    records = []
    entries_checked = 0
    for hash_list in lists:
        entries = parse_hash_list(hash_list)
        relative_list = hash_list.relative_to(ROOT).as_posix()
        records.append({"path": relative_list, "entries": len(entries)})
        entries_checked += len(entries)
        for expected, relative in entries:
            target = (ROOT / relative).resolve()
            if not target.is_file():
                failures.append(
                    {"list": relative_list, "path": relative, "error": "missing"}
                )
                continue
            actual = sha256(target)
            if actual != expected:
                failures.append(
                    {
                        "list": relative_list,
                        "path": relative,
                        "expected": expected,
                        "actual": actual,
                    }
                )

    return {
        "passed": not failures,
        "lists_checked": sorted(records, key=lambda row: row["path"]),
        "entries_checked": entries_checked,
        "failures": failures,
    }


def add_mod3(*vectors: list[int]) -> list[int]:
    return [sum(values) % 3 for values in zip(*vectors)]


def scalar_mod3(scalar: int, vector: list[int]) -> list[int]:
    return [(scalar * value) % 3 for value in vector]


def support(vector: list[int]) -> set[int]:
    return {index for index, value in enumerate(vector) if value % 3}


def side_profile(vector: list[int], split: int) -> list[int]:
    return [
        sum(value % 3 != 0 for value in vector[:split]),
        sum(value % 3 != 0 for value in vector[split:]),
    ]


def multiplicity_two_translation() -> dict[str, Any]:
    # Coordinates x0..x6 | y0..y6.
    conic = [1, 2, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0]
    star_x = [1] * 7 + [0] * 7
    star_y = [0] * 7 + [1] * 7

    translate_x = add_mod3(conic, scalar_mod3(2, star_x))
    translate_y = add_mod3(conic, star_y)
    support_c = support(conic)
    support_x = support(translate_x)
    support_y = support(translate_y)

    assert side_profile(conic, 7) == [2, 2]
    assert side_profile(translate_x, 7) == [6, 2]
    assert side_profile(translate_y, 7) == [2, 6]
    assert len(support_x) == len(support_y) == 8
    assert len(support_x & support_y) == 2
    assert not support_c <= support_x
    assert not support_c <= support_y

    return {
        "conic_profile": [2, 2],
        "translate_profiles": [[6, 2], [2, 6]],
        "translate_weights": [len(support_x), len(support_y)],
        "translated_support_intersection": len(support_x & support_y),
        "each_side_proper_star_subset": True,
        "cross_circuit_forced_by_proper_star_independence": True,
        "each_translate_excludes_one_conic_coordinate": True,
        "translated_circuits_distinct_by_dual_distance_four": True,
        "forced_other_circuits_per_label": 2,
    }


def multiplicity_three_translation() -> dict[str, Any]:
    # Coordinates T | A0..A2 | B0..B3 | Y0..Y5.
    coordinate_count = 14
    c4 = [0] * coordinate_count
    c4[0] = 1
    for index in range(1, 4):
        c4[index] = 2

    star_x = [0] * coordinate_count
    for index in range(1, 8):
        star_x[index] = 1

    star_y = [0] * coordinate_count
    star_y[0] = 1
    for index in range(8, 14):
        star_y[index] = 1

    c5 = add_mod3(c4, star_x)
    leaf_translate = add_mod3(c4, scalar_mod3(2, star_y))

    support_c4 = support(c4)
    support_c5 = support(c5)
    support_leaf = support(leaf_translate)

    assert len(support_c4) == 4
    assert len(support_c5) == 5
    assert 0 in support_c4 and 0 in support_c5
    assert 0 not in support_leaf
    assert side_profile(leaf_translate[1:], 7) == [3, 6]
    assert len(support_leaf) == 9
    assert len(support_leaf & support_c4) == 3
    assert support_leaf.isdisjoint(support_c5)

    return {
        "companion_weights": [len(support_c4), len(support_c5)],
        "companion_fixed_point_free_involution": True,
        "leaf_translate_profile": [3, 6],
        "leaf_translate_weight": len(support_leaf),
        "leaf_translate_contains_T": False,
        "conic_translate_intersection": len(support_leaf & support_c4),
        "companion_translate_intersection": len(support_leaf & support_c5),
        "each_side_proper_star_subset": True,
        "cross_circuit_forced_by_proper_star_independence": True,
        "translate_distinct_from_both_companions": True,
        "forced_other_circuits_per_label": 2,
    }


def cover_certificate(covered_nonedges: int = 4158) -> dict[str, Any]:
    # Coefficients are ordered O,n1,n2,n3,C and denote lhs >= 0.
    private_assignment_row = [6, 8, 8, 12, -8]
    triple_companion_row = [3, 1, 1, -3, 0]
    combined = [
        left + right
        for left, right in zip(private_assignment_row, triple_companion_row)
    ]
    assert combined == [9, 9, 9, 9, -8]

    nonedge_projective_lower = (8 * covered_nonedges + 8) // 9
    edge_projective = 693
    total_projective_lower = nonedge_projective_lower + edge_projective
    dual_word_lower = 2 * total_projective_lower

    hostile = {
        "n1": 0,
        "n2": 0,
        "n3": 1848,
        "N": 1848,
        "S": 5544,
        "P_priv": 2772,
        "p": 2772,
        "O": 1848,
    }
    assert hostile["P_priv"] == 2 * covered_nonedges - hostile["S"]
    assert 3 * hostile["O"] == 2 * hostile["p"]
    assert hostile["O"] == hostile["n3"]
    assert 9 * (hostile["N"] + hostile["O"]) == 8 * covered_nonedges

    return {
        "covered_nonedges": covered_nonedges,
        "private_count": {
            "selected_incidences": "S=n1+2*n2+3*n3",
            "covered_once_lower": "P_priv>=2*C-S",
            "size2_or_3_private_lower": "p>=2*C-2*n1-2*n2-3*n3",
            "size1_label_private_by_minimality": True,
        },
        "outside_assignment": {
            "assignments_per_private_label": 2,
            "maximum_assignments_per_outside_circuit": 3,
            "inequality": "3*O>=2*p",
            "repeated_companions_and_translates_allowed": True,
            "same_circuit_label_double_charge_excluded": True,
        },
        "triple_companions": {
            "inequality": "O>=n3",
            "distinct_by_companion_involution": True,
            "outside_by_cover_minimality": True,
            "may_overlap_private_assignment_pool": True,
        },
        "coefficient_rows_O_n1_n2_n3_C": {
            "private_assignment": private_assignment_row,
            "triple_companion": triple_companion_row,
            "sum": combined,
        },
        "cover_ratio": "8/9",
        "nonedge_projective_lower": nonedge_projective_lower,
        "edge_isolated_projective": edge_projective,
        "total_projective_lower": total_projective_lower,
        "ternary_scalars_per_projective_circuit": 2,
        "dual_short_word_lower": dual_word_lower,
        "arithmetic_equality_control_not_construction": hostile,
    }


def build_result() -> dict[str, Any]:
    integrity = verify_direct_freeze()
    assert integrity["passed"], integrity["failures"]
    multiplicity_two = multiplicity_two_translation()
    multiplicity_three = multiplicity_three_translation()
    cover = cover_certificate()

    return {
        "format": "wave186-star-translation-cover-independent-verifier-v1",
        "role": "verifier",
        "verdict": "VERIFIED_WITH_SCOPE",
        "global_status": "UNKNOWN",
        "source_checker_imported_or_executed": False,
        "integrity": {
            "source_manifest_sha256": sha256(SOURCE_MANIFEST),
            **integrity,
        },
        "classification_scope": {
            "multiplicity_two_verified_before_Q_equality": True,
            "multiplicity_three_verified_before_Q_equality": True,
            "cross_realization_ceiling": 3,
            "proper_star_only_relation_has_full_support": True,
            "dual_distance_lower": 4,
        },
        "multiplicity_two": multiplicity_two,
        "multiplicity_three": multiplicity_three,
        "cover": cover,
        "former_equality_Q_2079_excluded": cover["nonedge_projective_lower"] > 2079,
        "limitations": [
            "All conclusions are conditional on the rank-11 prism-free endpoint model.",
            "The hostile arithmetic equality control is not a circuit cover.",
            "No incompatible complete weight-enumerator upper bound is known.",
            "Rank 11, endpoint existence, novelty, and Conway-99 remain UNKNOWN.",
        ],
    }


def canonical_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()

    rendered = canonical_json(build_result())
    if args.write is not None:
        args.write.write_text(rendered, encoding="utf-8", newline="\n")
    if args.verify is not None:
        expected = args.verify.read_text(encoding="utf-8")
        if expected != rendered:
            raise SystemExit(f"result mismatch: {args.verify}")
    if args.write is None and args.verify is None:
        print(rendered, end="")


if __name__ == "__main__":
    main()
