"""Independent exact verifier for Wave 185.

This module intentionally does not import or execute the discovery checker.
It reconstructs the finite certificates and arithmetic from definitions.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "attempts" / "wave185-local-a6-transition-collapse"
SOURCE_MANIFEST = SOURCE_DIR / "package-manifest.sha256"

HASH_LINE = re.compile(r"^([0-9a-fA-F]{64})\s+\*?(.+?)\s*$")
METADATA_LINE = re.compile(
    r"^(?:git_commit\s+|git-commit\s+|base_git_commit=)[0-9a-fA-F]{40}$"
    r"|^precomparison_discovery_read=(?:true|false)$"
)


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
            if METADATA_LINE.fullmatch(line):
                continue
            raise ValueError(f"malformed hash line {path}:{number}: {raw!r}")
        entries.append((match.group(1).lower(), match.group(2)))
    if not entries:
        raise ValueError(f"empty hash list: {path}")
    return entries


def verify_hash_tree(start: Path) -> dict[str, Any]:
    """Validate Wave185 plus its direct frozen prior-package manifests.

    Historical transitive input freezes use several older formats and may
    name mutable repository-level files.  Their bytes are validated as files
    in their containing package manifests, but they are not reinterpreted.
    """

    source_input_freeze = SOURCE_DIR / "input-freeze.sha256"
    direct_prior_manifests = [
        (ROOT / relative).resolve()
        for _, relative in parse_hash_list(source_input_freeze)
    ]
    pending = [start.resolve(), source_input_freeze.resolve(), *direct_prior_manifests]
    seen: set[Path] = set()
    lists: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    entry_count = 0

    while pending:
        current = pending.pop().resolve()
        if current in seen:
            continue
        seen.add(current)
        entries = parse_hash_list(current)
        current_record = {
            "path": current.relative_to(ROOT).as_posix(),
            "entries": len(entries),
        }
        lists.append(current_record)
        entry_count += len(entries)

        for expected, relative in entries:
            target = (ROOT / relative).resolve()
            if not target.is_file():
                failures.append(
                    {
                        "list": current_record["path"],
                        "path": relative,
                        "error": "missing",
                    }
                )
                continue
            actual = sha256(target)
            if actual != expected:
                failures.append(
                    {
                        "list": current_record["path"],
                        "path": relative,
                        "expected": expected,
                        "actual": actual,
                    }
                )
    return {
        "passed": not failures,
        "lists_checked": sorted(lists, key=lambda row: row["path"]),
        "entries_checked": entry_count,
        "failures": failures,
    }


def induced_prism_and_cell() -> dict[str, Any]:
    first = ("i_alpha", "y_0", "y_1")
    second = ("x", "j_0", "j_1")
    cross = (("i_alpha", "x"), ("y_0", "j_0"), ("y_1", "j_1"))

    edges: set[frozenset[str]] = set()
    for triangle in (first, second):
        edges.update(frozenset(pair) for pair in itertools.combinations(triangle, 2))
    edges.update(frozenset(pair) for pair in cross)
    vertices = first + second

    degrees = {
        vertex: sum(vertex in edge for edge in edges)
        for vertex in vertices
    }
    triangles = [
        tuple(triple)
        for triple in itertools.combinations(vertices, 3)
        if all(frozenset(pair) in edges for pair in itertools.combinations(triple, 2))
    ]

    corners = tuple(itertools.product((0, 1), repeat=2))
    shared_endpoint_pairs = []
    opposite_corner_pairs = []
    for left, right in itertools.combinations(corners, 2):
        equal_coordinates = sum(a == b for a, b in zip(left, right))
        if equal_coordinates == 1:
            shared_endpoint_pairs.append((left, right))
        elif equal_coordinates == 0:
            opposite_corner_pairs.append((left, right))
        else:
            raise AssertionError("distinct corners cannot agree twice")

    opposite_degrees = {
        corner: sum(corner in pair for pair in opposite_corner_pairs)
        for corner in corners
    }

    assert len(edges) == 9
    assert set(degrees.values()) == {3}
    assert len(triangles) == 2
    assert len(shared_endpoint_pairs) == 4
    assert len(opposite_corner_pairs) == 2
    assert set(opposite_degrees.values()) == {1}

    return {
        "prism": {
            "vertices": len(vertices),
            "edges": len(edges),
            "degree_sequence": sorted(degrees.values()),
            "triangles": len(triangles),
            "cross_edges": len(cross),
            "induced": True,
        },
        "cell": {
            "corners": len(corners),
            "shared_endpoint_pairs_excluded": len(shared_endpoint_pairs),
            "opposite_corner_pairs_remaining": len(opposite_corner_pairs),
            "maximum_internal_degree": max(opposite_degrees.values()),
            "wave183_shapes": {
                "5": "4K1",
                "6": "2K2",
                "7": "P4",
            },
            "multiplicity_seven_excluded": True,
        },
    }


def transition_table() -> dict[str, dict[str, int]]:
    rows: dict[str, dict[str, int]] = {}
    for name, internal in (("m5", 0), ("m6", 1)):
        endpoint_profile_sum = 4
        incident_off_cell = endpoint_profile_sum - 2 * internal
        transition = 2
        incident_disjoint = incident_off_cell - transition
        orthogonal = 10 - internal - incident_disjoint
        residual_degree = internal + transition + incident_disjoint + orthogonal
        assert incident_disjoint >= 0
        assert residual_degree == 12
        rows[name] = {
            "internal": internal,
            "incident_transition": transition,
            "incident_disjoint": incident_disjoint,
            "orthogonal_disjoint": orthogonal,
            "residual_degree": residual_degree,
            "cell_transition_total": 4 * transition,
            "cell_incident_disjoint_total": 4 * incident_disjoint,
        }
    return rows


def incident_capacity_and_companions() -> dict[str, Any]:
    possible_per_orientation = 4
    # The complete K_2,2 gives a same-endpoint pair its base neighbor plus
    # the two vertices on the other side: three common neighbors > mu=2.
    common_neighbors_if_complete = 3
    mu = 2
    assert common_neighbors_if_complete > mu
    maximum_per_orientation = possible_per_orientation - 1
    orientations = 2
    combined_capacity = orientations * maximum_per_orientation

    type5_weighted_degree = 8
    local_distinct_companions = math.ceil(
        type5_weighted_degree / combined_capacity
    )
    support_size = 5
    global_distinct_companions = support_size * local_distinct_companions
    raw_n5_floor = 1 + global_distinct_companions

    assert combined_capacity == 6
    assert local_distinct_companions == 2
    assert raw_n5_floor == 11

    return {
        "possible_edges_per_orientation": possible_per_orientation,
        "common_neighbors_if_complete": common_neighbors_if_complete,
        "mu": mu,
        "maximum_per_orientation": maximum_per_orientation,
        "orientations": orientations,
        "b_ef_upper": combined_capacity,
        "type5_weighted_degree": type5_weighted_degree,
        "local_distinct_type5_companions": local_distinct_companions,
        "support_size": support_size,
        "global_distinct_companions": global_distinct_companions,
        "raw_n5_floor": raw_n5_floor,
    }


def multiplicity_profiles(raw_n5_floor: int) -> dict[str, Any]:
    total_incidence = 2079
    n5_residue_mod6 = 3
    congruence_floor = min(
        value
        for value in range(raw_n5_floor, raw_n5_floor + 6)
        if value % 6 == n5_residue_mod6
    )
    assert congruence_floor == 15

    profiles = []
    u = 0
    while True:
        n5 = congruence_floor + 6 * u
        numerator = total_incidence - 5 * n5
        if numerator < 0:
            break
        assert numerator % 6 == 0
        n6 = numerator // 6
        profiles.append({"u": u, "n5": n5, "n6": n6, "roots": n5 + n6})
        u += 1

    assert profiles[0] == {"u": 0, "n5": 15, "n6": 334, "roots": 349}
    assert profiles[-1] == {"u": 66, "n5": 411, "n6": 4, "roots": 415}
    assert all(5 * row["n5"] + 6 * row["n6"] == total_incidence for row in profiles)

    return {
        "equation": "5*n5+6*n6=2079",
        "n5_residue_mod6": n5_residue_mod6,
        "raw_n5_floor": raw_n5_floor,
        "congruence_n5_floor": congruence_floor,
        "parameterization": "(n5,n6)=(15+6u,334-5u)",
        "u_interval": [profiles[0]["u"], profiles[-1]["u"]],
        "profile_count": len(profiles),
        "minimum_n6": min(row["n6"] for row in profiles),
        "root_interval": [
            min(row["roots"] for row in profiles),
            max(row["roots"] for row in profiles),
        ],
        "profiles": profiles,
    }


def rainbow_triangle_bound(profiles: dict[str, Any]) -> dict[str, Any]:
    v, complement_degree, complement_lambda = 99, 84, 71
    total_triangles = v * complement_degree * complement_lambda // 6
    monochromatic_by_type = {"m5": math.comb(5, 3), "m6": 2**3}

    maximum_monochromatic = max(
        monochromatic_by_type["m5"] * row["n5"]
        + monochromatic_by_type["m6"] * row["n6"]
        for row in profiles["profiles"]
    )
    minimum_rainbow = total_triangles - maximum_monochromatic

    assert total_triangles == 98406
    assert monochromatic_by_type == {"m5": 10, "m6": 8}
    assert maximum_monochromatic == 4142
    assert minimum_rainbow == 94264

    return {
        "complement_parameters": [99, 84, 71, 72],
        "total": total_triangles,
        "triangle_color_dichotomy": "monochromatic_or_rainbow",
        "monochromatic_per_root": monochromatic_by_type,
        "monochromatic_formula": "10*n5+8*n6=4158-4*n6",
        "maximum_monochromatic": maximum_monochromatic,
        "minimum_rainbow": minimum_rainbow,
    }


def build_result() -> dict[str, Any]:
    integrity = verify_hash_tree(SOURCE_MANIFEST)
    assert integrity["passed"], integrity["failures"]

    geometry = induced_prism_and_cell()
    transitions = transition_table()
    capacity = incident_capacity_and_companions()
    profiles = multiplicity_profiles(capacity["raw_n5_floor"])
    rainbow = rainbow_triangle_bound(profiles)

    return {
        "format": "wave185-local-a6-transition-collapse-independent-verifier-v1",
        "role": "verifier",
        "verdict": "VERIFIED_WITH_SCOPE",
        "global_status": "UNKNOWN",
        "source_checker_imported_or_executed": False,
        "integrity": {
            "source_manifest_sha256": sha256(SOURCE_MANIFEST),
            **integrity,
        },
        "geometry": geometry,
        "transition_rows": transitions,
        "incident_capacity_and_companions": capacity,
        "multiplicity": profiles,
        "rainbow_triangles": rainbow,
        "limitations": [
            "Wave181 equality and endpoint prism-freeness are premises.",
            "The scalar profiles are not graph, root-system, code, or transition constructions.",
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

    result = build_result()
    rendered = canonical_json(result)
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
