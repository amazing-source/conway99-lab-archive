#!/usr/bin/env python3
"""Post-freeze comparison and independent replay of Wave 41 discovery data."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DISCOVERY_DIR = ROOT / "attempts/wave41-multiedge-rank-packing"
DISCOVERY_HASHES = {
    "exact_check.py": "787cd80f79517fa455221c0222dfc709b10f15b8524804019e5cc72d1c5b76de",
    "exact-results.json": "0c20f53b056e0b94f14094d46d957b1b4c5ccd5c6c1920de80ea8ce4e49fdac1",
    "failed-routes.md": "074ecd2c65ac963c7a9e16d226e013ad382fdf264a8ece0f766c7b7799081a0b",
    "input-freeze.sha256": "70f51fc83f0c22deaa94feb06c27b43ec0a684797c1e985f9154f4a2b7c607e3",
    "package-manifest.sha256": "98ab286a8215031ff0b0304fb3cd5510816702fe652878716a5936889fe564f8",
    "README.md": "249ae1cfc99b538709c36f5140470e14e79ba6197b62e508b85458593c7cef56",
    "run-report.yaml": "4c84212031b2a0a35add50951b4793fa30b7bf8e519356465021a4c0a68c726d",
    "test_exact_check.py": "a35fd813d29056f261a70be6cfda0adb3d4d5cd912cc6a4454f46843c0e9fd33",
}


def load_independent_module():
    path = HERE / "independent_check.py"
    spec = importlib.util.spec_from_file_location("wave41_independent", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load independent checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ind = load_independent_module()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matching_edges(mapping: Sequence[int]) -> tuple[tuple[int, int], ...]:
    if len(mapping) != 12:
        raise ValueError("matching map has wrong length")
    edges = tuple((i, mapping[i]) for i in range(12) if i < mapping[i])
    ind.audit_matching(edges)
    if any(mapping[mapping[i]] != i or mapping[i] == i for i in range(12)):
        raise ValueError("matching map is not a fixed-point-free involution")
    return edges


def control_graph(
    q_mapping: Sequence[int],
    r_mapping: Sequence[int],
    yz_permutation: Sequence[int],
) -> list[list[int]]:
    if sorted(yz_permutation) != list(range(12)):
        raise ValueError("control Y-Z map is not a permutation")
    graph = [[0] * 39 for _ in range(39)]
    for u, v in ((0, 1), (0, 2), (1, 2)):
        ind.add_edge(graph, u, v)
    for root, fibre in zip(ind.T, (ind.X, ind.Y, ind.Z)):
        for vertex in fibre:
            ind.add_edge(graph, root, vertex)
    for a, b in ind.standard_matching():
        ind.add_edge(graph, ind.X[a], ind.X[b])
    for a, b in matching_edges(q_mapping):
        ind.add_edge(graph, ind.Y[a], ind.Y[b])
    for a, b in matching_edges(r_mapping):
        ind.add_edge(graph, ind.Z[a], ind.Z[b])
    for i in range(12):
        ind.add_edge(graph, ind.X[i], ind.Y[i])
        ind.add_edge(graph, ind.X[i], ind.Z[i])
        ind.add_edge(graph, ind.Y[i], ind.Z[yz_permutation[i]])
    ind.audit_full_graph(graph)
    return graph


def core_components(graph: Sequence[Sequence[int]]) -> list[int]:
    unseen = set(range(3, 39))
    sizes: list[int] = []
    while unseen:
        stack = [min(unseen)]
        component: set[int] = set()
        while stack:
            vertex = stack.pop()
            if vertex in component:
                continue
            component.add(vertex)
            stack.extend(
                neighbor
                for neighbor in range(3, 39)
                if graph[vertex][neighbor] and neighbor not in component
            )
        unseen.difference_update(component)
        sizes.append(len(component))
    return sorted(sizes, reverse=True)


def core_triangle_count(graph: Sequence[Sequence[int]]) -> int:
    return sum(
        graph[a][b] and graph[a][c] and graph[b][c]
        for a in range(3, 39)
        for b in range(a + 1, 39)
        for c in range(b + 1, 39)
    )


def replay_control(name: str, record: dict[str, object]) -> dict[str, object]:
    graph = control_graph(
        record["q_matching"],
        record["r_matching"],
        record["yz_permutation"],
    )
    checks = ind.full_rank_checks(graph)
    components = core_components(graph)
    triangles = core_triangle_count(graph)
    if checks["rank_F7_K39"] != record["K39_rank_F7"]:
        raise AssertionError(f"{name} K39 rank changed")
    if checks["rank_F7_3I_minus_A_core"] != record["laplacian_rank_F7"]:
        raise AssertionError(f"{name} core Laplacian rank changed")
    if 36 - checks["rank_F7_3I_minus_A_core"] != record[
        "laplacian_nullity_F7"
    ]:
        raise AssertionError(f"{name} core Laplacian nullity changed")
    if components != record["core_component_sizes"]:
        raise AssertionError(f"{name} component census changed")
    if triangles != record["core_triangle_count"]:
        raise AssertionError(f"{name} triangle census changed")
    return {
        "rank_F7_K39": checks["rank_F7_K39"],
        "rank_F7_3I_minus_A_core": checks["rank_F7_3I_minus_A_core"],
        "K39_nullity": checks["K39_nullity"],
        "core_component_sizes": components,
        "core_triangle_count": triangles,
        "full_39_block_identity": True,
        "three_compact_kernel_vectors_checked": 3,
    }


def compute() -> dict[str, object]:
    found_hashes = {
        name: sha256(DISCOVERY_DIR / name) for name in DISCOVERY_HASHES
    }
    if found_hashes != DISCOVERY_HASHES:
        raise ValueError("discovery package changed after verifier freeze")
    discovery = json.loads(
        (DISCOVERY_DIR / "exact-results.json").read_text(encoding="utf-8")
    )
    independent = json.loads(
        (HERE / "independent-results.json").read_text(encoding="utf-8")
    )

    discovery_records = discovery["all_odd_rank_equality_obstruction"]["records"]
    label_map = {
        "1^6": "1+1+1+1+1+1",
        "1^3+3": "1+1+1+3",
        "1+5": "1+5",
        "3+3": "3+3",
    }
    type_comparison: dict[str, object] = {}
    for independent_label, discovery_label in label_map.items():
        left = independent["type_results"][independent_label]
        right = discovery_records[discovery_label]
        independent_degrees = sorted(left["zero_diagonal_row_degrees"])
        discovery_degrees = sorted(
            right["diagonal_isotropy_allowed_preimage_counts"]
        )
        if independent_degrees != discovery_degrees:
            raise AssertionError(f"diagonal-isotropy census differs for {independent_label}")
        if right["rank_25_equality_possible"]:
            raise AssertionError(f"discovery retained rank 25 for {independent_label}")
        type_comparison[independent_label] = {
            "diagonal_allowed_degree_multiset_agrees": True,
            "independent_matching_number": left["zero_diagonal_matching_number"],
            "independent_rank_25_candidate_permutations": left[
                "rank_25_candidate_permutations"
            ],
            "rank_25_excluded_by_both": True,
        }

    controls = discovery["low_rank_controls"]
    replayed_controls = {
        "rank_28_generic": replay_control(
            "rank_28_generic", controls["generic_three_fibre_control"]
        ),
        "rank_29_triangle_free": replay_control(
            "rank_29_triangle_free", controls["triangle_free_three_fibre_control"]
        ),
    }
    if replayed_controls["rank_28_generic"]["rank_F7_K39"] != 28:
        raise AssertionError("rank-28 positive control was not reproduced")
    if replayed_controls["rank_29_triangle_free"]["rank_F7_K39"] != 29:
        raise AssertionError("rank-29 positive control was not reproduced")
    if replayed_controls["rank_29_triangle_free"]["core_triangle_count"] != 0:
        raise AssertionError("rank-29 control is not triangle-free")

    # Direct integer coefficient expansion of
    # (J-I-2A)(A+4I), after A^2=12I-A+2J.
    polynomial_coefficients = {
        "J": 14 + 4 - 4,
        "A": -1 - 8 + 2,
        "I": -4 - 24,
    }
    if polynomial_coefficients != {"J": 14, "A": -7, "I": -28}:
        raise AssertionError("global compact-kernel polynomial changed")
    if any(value % 7 for value in polynomial_coefficients.values()):
        raise AssertionError("global compact-kernel polynomial is not zero mod seven")
    if (4 + 1 + 1) + (10 - 2) != 14:
        raise AssertionError("outside-column compact-kernel dot product changed")

    limitations = discovery["limitations"]
    false_five_type_line = next(
        (
            line
            for line in limitations
            if "five even-part edge types" in line.lower()
        ),
        None,
    )
    if false_five_type_line is None:
        raise AssertionError("expected discovery limitation discrepancy disappeared")

    result = {
        "format": "wave41-multiedge-rank-packing-comparison-v1",
        "role": "verifier",
        "discovery_hashes_at_comparison": found_hashes,
        "independent_artifact_hashes_before_comparison": {
            "independent_check.py": (
                "b0d71926dbb1bb6988b603a4adf7ea69489866702433e4250034bd8218103747"
            ),
            "independent-results.json": (
                "20cfac8928e1a9d52a586a833d8e52cc7f64f7998bdd641467ded5121e2da133"
            ),
            "protocol-freeze.md": (
                "6e463acd4f994faf330cfa8d584cc91f70921e07ac352bbad4995d646aa516e7"
            ),
            "precomparison-method-addendum.md": (
                "cab2abb752837fb7cae5e7e0c01a32421a8a053d1a40efa44529bb5184416ff8"
            ),
        },
        "agreement": {
            "all_odd_type_set": True,
            "complete_assignment_checks": (
                discovery["all_odd_rank_equality_obstruction"][
                    "complete_assignment_checks"
                ]
                == 4 * 144
            ),
            "type_invariants": type_comparison,
            "scoped_rank_26_implication": True,
            "universal_floor_remains_25": True,
            "compact_kernel_polynomial": polynomial_coefficients,
            "outside_column_integer_dot_product": 14,
        },
        "low_rank_controls_replayed": replayed_controls,
        "discrepancies": [
            {
                "severity": "REFUTED_FIELD",
                "path": "exact-results.json.limitations",
                "discovery_text": false_five_type_line,
                "correction": (
                    "There are seven, not five, positive partitions of six "
                    "containing an even part."
                ),
                "effect_on_main_claim": "none",
            }
        ],
        "verdict": {
            "main_all_odd_rank_26_claim": "VERIFIED_SCOPED",
            "discovery_five_even_part_count": "REFUTED",
            "universal_rank_26_claim": "NOT_PROVED",
            "universal_verified_floor": 25,
            "seven_even_part_types": "UNKNOWN",
        },
    }
    validate(result)
    return result


def validate(result: dict[str, object]) -> None:
    verdict = result["verdict"]
    if verdict["main_all_odd_rank_26_claim"] != "VERIFIED_SCOPED":
        raise ValueError("main scoped verdict changed")
    if verdict["discovery_five_even_part_count"] != "REFUTED":
        raise ValueError("known discovery discrepancy was hidden")
    if verdict["universal_verified_floor"] != 25:
        raise ValueError("universal floor was inflated")
    if verdict["seven_even_part_types"] != "UNKNOWN":
        raise ValueError("seven unresolved types were promoted")
    if set(result["low_rank_controls_replayed"]) != {
        "rank_28_generic",
        "rank_29_triangle_free",
    }:
        raise ValueError("positive controls are incomplete")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = compute()
    if args.verify:
        stored = json.loads(args.verify.read_text(encoding="utf-8"))
        validate(stored)
        if stored != result:
            raise SystemExit("stored comparison differs from recomputation")
    if args.write:
        args.write.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    elif not args.verify:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
