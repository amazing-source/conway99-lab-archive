#!/usr/bin/env python3
"""Post-freeze replay of sealed Wave204 JSON artifacts.

Unlike independent_verifier.py, this module was written after the submitted
packages were opened.  It does not import submitted Python code.  It checks
the sealed JSON certificates with a separate arithmetic implementation and
records where the source-blind formalization differed from the source schema.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

import independent_verifier as blind


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V1_DIR = ROOT / "attempts" / "wave204-literature-hostile-controls"
V2_DIR = ROOT / "attempts" / "wave204-global-slot-holonomy-proof-a"
V3_DIR = ROOT / "attempts" / "wave204-projector-fourth-order-proof-b"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return json.load(handle)


def verify_manifest(path: Path) -> dict[str, Any]:
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        target = ROOT / Path(relative)
        actual = file_sha256(target)
        assert actual == expected, (relative, expected, actual)
        entries.append({"path": relative, "sha256": actual})
    return {
        "manifest": str(path.relative_to(ROOT)).replace("\\", "/"),
        "manifest_sha256": file_sha256(path),
        "entry_count": len(entries),
        "entries_match": True,
    }


def expected_graph_neighbors(center: int) -> set[int]:
    return {
        (center + sign * offset) % 99
        for offset in range(1, 8)
        for sign in (-1, 1)
    }


def verify_v1_json(data: dict[str, Any]) -> dict[str, Any]:
    assert data["format"] == "wave204-b-zero-local-incidence-skeleton-v1"
    scope = data["scope"]
    assert scope["is_99_center_global_skeleton"]
    assert scope["is_14_regular_graph_skeleton"]
    assert scope["is_local_HM_flag_system"]
    assert scope["is_wave203_slot_certificate"]
    for denied in (
        "is_strongly_regular_graph",
        "is_ternary_column_realization",
        "is_rank_11_code",
        "is_circuit_cover",
        "is_endpoint_existence_evidence",
    ):
        assert scope[denied] is False

    family = [tuple(triple) for triple in data["construction_rules"]["HM_family"]]
    family_sets = [set(triple) for triple in family]
    assert len(family) == len(set(family)) == 13
    assert all(len(triple) == 3 for triple in family_sets)
    assert all(left & right for left, right in combinations(family_sets, 2))
    assert not set.intersection(*family_sets)
    pair_degrees: Counter[tuple[int, int]] = Counter()
    for triple in family:
        pair_degrees.update(combinations(triple, 2))
    assert sorted(pair for pair, count in pair_degrees.items() if count == 5) == [
        (0, 1),
        (0, 2),
        (0, 3),
    ]

    centers = data["centers"]
    assert len(centers) == 99
    full_labels: Counter[tuple[int, int]] = Counter()
    selected_labels: Counter[tuple[int, int]] = Counter()
    full_slots: dict[tuple[int, int], set[int]] = defaultdict(set)
    selected_flag_count = 0
    for expected_center, center_data in enumerate(centers):
        center = center_data["center"]
        assert center == expected_center
        graph_neighbors = expected_graph_neighbors(center)
        complement = set(range(99)) - graph_neighbors - {center}
        assert set(center_data["graph_neighbors"]) == graph_neighbors
        assert len(graph_neighbors) == 14 and len(complement) == 84

        blocks = center_data["local_star_blocks"]
        assert len(blocks) == 7
        outer_vertices = []
        for block_id, block in enumerate(blocks):
            assert block["block"] == block_id
            assert block["vertices"][0] == center
            left, right = block["vertices"][1:]
            assert left in graph_neighbors and right in graph_neighbors
            assert right in expected_graph_neighbors(left)
            outer_vertices.extend((left, right))
        assert len(outer_vertices) == len(set(outer_vertices)) == 14
        assert set(outer_vertices) == graph_neighbors

        fibers = center_data["pair_fibers"]
        assert len(fibers) == 21
        fiber_map = {}
        all_targets = []
        for fiber in fibers:
            pair = tuple(fiber["pair"])
            assert pair in set(combinations(range(7), 2))
            assert len(fiber["targets"]) == len(set(fiber["targets"])) == 4
            fiber_map[pair] = set(fiber["targets"])
            all_targets.extend(fiber["targets"])
        assert len(fiber_map) == 21
        assert len(all_targets) == len(set(all_targets)) == 84
        assert set(all_targets) == complement

        flags = center_data["flags"]
        assert len(flags) == 13
        for flag_id, flag in enumerate(flags):
            triple = tuple(flag["A"])
            assert flag["flag_id"] == flag_id
            assert triple == family[flag_id]
            selected_flag_count += int(flag["selected"])
            assert len(flag["leaves"]) == 3
            leaf_pairs = []
            for leaf in flag["leaves"]:
                pair = tuple(leaf["pair"])
                assert pair in combinations(triple, 2)
                assert leaf["target"] in fiber_map[pair]
                assert set(triple) - set(pair) == {leaf["wave203_slot"]}
                key = (center, leaf["target"])
                assert leaf["wave203_slot"] not in full_slots[key]
                full_slots[key].add(leaf["wave203_slot"])
                full_labels[key] += 1
                if flag["selected"]:
                    selected_labels[key] += 1
                leaf_pairs.append(pair)
            assert sorted(leaf_pairs) == list(combinations(triple, 2))

    assert selected_flag_count == 1200
    assert sum(full_labels.values()) == 99 * 13 * 3 == 3861
    assert len(full_labels) == 3561
    assert Counter(full_labels.values()) == Counter({1: 3264, 2: 294, 3: 3})
    assert max(full_labels.values()) == 3
    assert all((target, source) not in full_labels for source, target in full_labels)
    assert all((target, source) not in selected_labels for source, target in selected_labels)

    selected_profile = Counter(selected_labels.values())
    assert selected_profile == Counter({1: 3123, 2: 234, 3: 3})
    assert sum(selected_labels.values()) == 3600
    assert len(selected_labels) == 3360
    q = sum(count for multiplicity, count in selected_profile.items() if multiplicity > 1)
    epsilon = sum(
        (5 - multiplicity) * count
        for multiplicity, count in selected_profile.items()
        if multiplicity > 1
    )
    assert q == 237 and epsilon == 708
    nonprivate_by_tail = Counter(
        source for (source, _), multiplicity in selected_labels.items() if multiplicity > 1
    )
    tail_histogram = Counter(nonprivate_by_tail.values())
    tail_histogram[0] = 99 - len(nonprivate_by_tail)
    assert tail_histogram == Counter({3: 79, 0: 20})

    summary = data["summary"]
    assert summary["full_pool"]["directed_label_union_J"] == len(full_labels) == 3561
    assert summary["full_pool"]["delta_3564_minus_J"] == 3
    assert summary["full_pool"]["max_combined_two_orientation_multiplicity"] == 3
    selected = summary["selected_pool"]
    assert selected["n3_flags"] == 1200
    assert selected["private_p3"] == 3123
    assert selected["nonprivate_q"] == 237
    assert selected["epsilon"] == 708
    assert selected["wave201_L_delta_minus_3q_plus_epsilon"] == 0
    assert selected["b_bidirectional_nonprivate"] == 0
    assert selected["capacity_slack"] == 708
    assert 5 * 3360 - (3 * 1200 + 4 * 3123) == 708

    return {
        "certificate_predicates": "VERIFIED",
        "restricted_force_b_positive_implication": "REFUTED_WITH_SCOPE",
        "full_flag_count": 1287,
        "selected_flag_count": selected_flag_count,
        "J": len(full_labels),
        "delta": 3,
        "selected_profile": {"1": 3123, "2": 234, "3": 3},
        "q": q,
        "epsilon": epsilon,
        "b": 0,
        "max_combined_two_orientation_multiplicity": 3,
        "certificate_sha256": file_sha256(V1_DIR / "countermodel.json"),
    }


def canonical_projective(vector: list[int]) -> tuple[int, ...]:
    first = next(value for value in vector if value)
    scale = pow(first, -1, 3)
    return tuple(scale * value % 3 for value in vector)


def vec_add(*vectors: list[int]) -> list[int]:
    return [sum(entries) % 3 for entries in zip(*vectors)]


def vec_sub(left: list[int], right: list[int]) -> list[int]:
    return [(a - b) % 3 for a, b in zip(left, right)]


def diagonal_dot(left: list[int], right: list[int]) -> int:
    diagonal = [1] * 10 + [2]
    return sum(a * d * b for a, d, b in zip(left, diagonal, right)) % 3


def permutation_compose(left: list[int], right: list[int]) -> list[int]:
    return [left[right[index]] for index in range(len(left))]


def permutation_monodromy(permutations: list[list[int]]) -> list[int]:
    result = list(range(5))
    for permutation in permutations:
        result = permutation_compose(permutation, result)
    return result


def verify_v2_json(data: dict[str, Any]) -> dict[str, Any]:
    assert data["format"] == "wave204-global-slot-holonomy-proof-a-v1"
    assert not any(
        data["boundary"][key]
        for key in (
            "rank_11_excluded",
            "endpoint_excluded",
            "Q_ge_7060_proved",
            "strict_n3_improvement",
            "graph_or_code_constructed",
        )
    )
    assert data["boundary"]["conway_99"] == "UNKNOWN"

    defects = {}
    for length in (3, 4, 5):
        cycle = data["low_cycle_coboundary_checks"][str(length)]
        assert cycle["gain_definition"] == "g(S->T)=z_T-z_S"
        assert cycle["holonomy"] == [0] * 11 and cycle["holonomy_zero"]

        control = data["projected_center_cycle_controls"][str(length)]
        assert control["ambient_form_diagonal"] == [1] * 10 + [2]
        assert control["ambient_form_determinant_mod_3"] == 2
        stars = control["stars"]
        fillers = control["rank_fillers"]
        assert len(stars) == length
        all_vectors = [vector for star in stars for vector in star] + fillers
        assert blind.matrix_rank(all_vectors) == 11
        projective = [canonical_projective(vector) for vector in all_vectors]
        assert len(projective) == len(set(projective))
        assert all(diagonal_dot(vector, vector) == 0 for vector in all_vectors)

        gains = []
        for index, star in enumerate(stars):
            assert len(star) == 7
            assert vec_add(*star) == [0] * 11
            gram = [
                [diagonal_dot(left, right) for right in star] for left in star
            ]
            assert gram == [
                [0 if i == j else 1 for j in range(7)] for i in range(7)
            ]
            incoming = star[0]
            source, handle_a, handle_b = star[1], star[2], star[3]
            target = stars[(index + 1) % length][0]
            assert target == vec_add(source, handle_a, handle_b)
            assert incoming != source
            gains.append(vec_sub(target, source))
        defect = vec_add(*gains)
        assert defect == control["center_cycle_projected_defect"]
        assert defect != [0] * 11
        assert control["incoming_outgoing_equalities"] == 0
        assert control["composable_consecutive_flag_pairs"] == 0
        assert control["block_transition_cycle_exists"] is False
        assert control["b"] == 0
        defects[str(length)] = defect

        extension = data["partial_injection_extension_controls"][str(length)]
        assert extension["edgewise_partial_injection"] == {"0": 0}
        for completion in (extension["completion_a"], extension["completion_b"]):
            assert len(completion) == length
            assert all(sorted(permutation) == list(range(5)) for permutation in completion)
            assert all(permutation[0] == 0 for permutation in completion)
        assert permutation_monodromy(extension["completion_a"]) == extension["monodromy_a"]
        assert permutation_monodromy(extension["completion_b"]) == extension["monodromy_b"]
        assert extension["monodromy_a"] != extension["monodromy_b"]

    c4 = data["canonical_c4"]
    assert blind.matrix_rank(c4["gram"]) == 3
    assert blind.mat_mul(c4["gram"], [[x] for x in c4["checkerboard"]]) == [
        [0],
        [0],
        [0],
        [0],
    ]
    assert c4["forced_two_cell_on_wave203_branch"] is False

    return {
        "fixed_column_coboundary": "VERIFIED",
        "center_walk_chaining_implication": "REFUTED_WITH_SCOPE",
        "canonical_total_S5_implication": "REFUTED_WITH_SCOPE",
        "relaxed_rank11_controls": "VERIFIED_SCOPED_RELAXED",
        "projected_defects": defects,
        "omitted_global_premise_count": len(
            data["premise_ledger"]["not_satisfied_or_asserted"]
        ),
        "result_sha256": file_sha256(V2_DIR / "exact-results.json"),
    }


def verify_v3_json(data: dict[str, Any]) -> dict[str, Any]:
    types = data["adjacent_pair_reduction"]["cycle_types"]
    expected = {
        "6": ([6], 0),
        "4+2": ([4, 2], 1),
        "3+3": ([3, 3], 0),
        "2+2+2": ([2, 2, 2], 0),
    }
    for name, (parts, expected_h) in expected.items():
        item = types[name]
        n = blind.build_cycle_biadjacency(parts)
        compression = blind.mat_mul(n, blind.transpose(n))
        assert item["compression"] == compression
        assert item["pair_trace"] == blind.trace(compression) == 0
        h = blind.trace(blind.mat_mul(compression, compression))
        assert item["alternating_fourth_trace"] == h == expected_h
        assert item["exterior_square_trace"] == h
        assert item["symmetric_square_trace"] == 2 * h % 3

    local = data["positive_controls"]["local"]["pair_data"]
    assert local["P,Q1"]["pair_trace"] == local["P,Q2"]["pair_trace"]
    assert (
        local["P,Q1"]["intersection_dimension"]
        == local["P,Q2"]["intersection_dimension"]
    )
    assert (
        local["P,Q1"]["alternating_fourth_trace"]
        != local["P,Q2"]["alternating_fourth_trace"]
    )
    global_controls = data["positive_controls"]["global_99_projector_231_column"]
    assert global_controls["same_pairwise_projector_trace_gram"]
    assert global_controls["different_fourth_trace_matrices"]
    assert global_controls["different_ordered_fourth_trace_entries"] == 3888
    assert all(
        control["projector_count"] == 99
        and control["column_label_count"] == 231
        and control["centered_gram_rank"] == 11
        and control["distinct_projective_direction_count"] == 21
        for control in global_controls["controls"].values()
    )
    assert len(global_controls["failed_target_premises"]) == 7
    assert data["conclusions"]["endpoint_excluded"] is False
    assert data["conclusions"]["strict_n3_improvement"] is False
    assert data["conclusions"]["conway_99_status"] == "UNKNOWN"

    return {
        "local_fourth_order_detector": "VERIFIED",
        "pair_trace_plus_intersection_determines_h": "REFUTED_WITH_SCOPE",
        "optional_global_control": "SOURCE_REPLAYED_SCOPED_RELAXED",
        "optional_global_control_independent_status": "NOT_PROMOTED",
        "different_ordered_fourth_trace_entries": 3888,
        "distinct_directions_of_231_labels": 21,
        "failed_target_premise_count": 7,
        "result_sha256": file_sha256(V3_DIR / "exact-results.json"),
    }


def run() -> dict[str, Any]:
    manifests = {
        "v1": verify_manifest(V1_DIR / "package-manifest.sha256"),
        "v2": verify_manifest(V2_DIR / "package-manifest.sha256"),
        "v3": verify_manifest(V3_DIR / "package-manifest.sha256"),
    }
    assert (
        manifests["v3"]["manifest_sha256"]
        == "6074ec95b7a92cdf26626a031c9373fa94ccd3ab47c627d31183a64af0bdc181"
    )
    return {
        "schema": "wave204-post-source-independent-json-replay-v1",
        "blind_freeze_manifest_sha256": file_sha256(
            HERE / "SOURCE_BLIND_FREEZE.sha256"
        ),
        "manifests": manifests,
        "v1": verify_v1_json(load_json(V1_DIR / "countermodel.json")),
        "v2": verify_v2_json(load_json(V2_DIR / "exact-results.json")),
        "v3": verify_v3_json(load_json(V3_DIR / "exact-results.json")),
        "blind_to_source_discrepancies": [
            (
                "V1 blind model checked the headline relaxed counts but did not "
                "reconstruct the submitted selected flag-to-leaf multiplicity "
                "mechanism."
            ),
            (
                "V1 blind slot_rows were a generic collision-free five-slot "
                "cover, not the submitted Wave203 third-block slot A-P."
            ),
            (
                "V1 blind nonprivate occurrences were abstract cross-center "
                "copies, while the submitted multiplicities are repeated flag "
                "occurrences of one directed center-to-target label."
            ),
            (
                "V1 blind degree-block pairing differs from the submitted "
                "seven actual circulant triangles; both partition each "
                "14-neighbor set."
            ),
            (
                "V2 blind simplices have off-diagonal Gram 2, while the "
                "submitted normalized A6 controls have Gram J_7-I_7 with "
                "off-diagonal 1."
            ),
            (
                "V2 blind controls did not impose T=S+X_a+X_b, projective "
                "distinctness, or rank-11 span. The post-source JSON replay "
                "checks all three submitted conditions."
            ),
            (
                "V3 local compression and trace detector match the blind "
                "derivation. The independent rank-11 counterexample uses "
                "different trace/intersection values from the submitted "
                "witness but proves the same scoped underdetermination."
            ),
            (
                "The optional V3 99-projector controls were not independently "
                "reconstructed before unsealing; only their sealed source "
                "replay and result ledger are accepted, so they remain "
                "quarantined as relaxed."
            ),
        ],
    }


def main() -> None:
    print(json.dumps(run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
