#!/usr/bin/env python3
"""Fresh adversarial audit of the repaired Wave 13 n3=45 bundle.

The arithmetic and CNF reconstructions are loaded from the historical
independent verifier modules, which do not import the Wave 13 discovery
modules.  The repaired discovery module is loaded only as the system under
test for the hostile-validator section.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import itertools
import json
import platform
import sys
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import Callable, Sequence

import pysat


REPAIR_COMMIT = "3e4da49df2743529bf2d565dbee9580f09eb77e2"
FAILED_BASELINE_COMMIT = "066d9c7fcf593c3b9d35cfef1031dbd9daab4145"
ORDER = 15
ROOT = (0, 1, 2)
ROOT_JUSTIFICATION = (
    "odd total incidence forces a size-three point; the full S_15 "
    "active-label action names it {0,1,2}, and its setwise stabilizer "
    "gives the recorded rooted-mode representative"
)
RESTRICTIONS = [
    "active_labels_only",
    "point_sizes_restricted_to_2_or_3_after_local_proof",
    "one_size3_point_fixed_by_full_label_relabeling",
    "one_of_four_root_modes_fixed_by_its_label_stabilizer",
    "meeting_crossings_and_overlap_fixed_point_upper_bound_only",
    "remaining_fixed_point_support_not_encoded",
    "inactive_vertices_not_encoded",
    "no_complete_99_vertex_adjacency_matrix",
    "no_global_lambda_mu_equalities",
    "diagnostic_variant_no_common_point",
]
EXPECTED_BRANCHES = (
    (1, "111"),
    (3, "111"),
    (3, "122"),
    (5, "111"),
    (5, "122"),
    (5, "222"),
    (5, "223"),
    (7, "111"),
    (7, "122"),
    (7, "222"),
    (7, "223"),
    (9, "111"),
    (9, "122"),
    (9, "222"),
    (9, "223"),
    (11, "222"),
    (11, "223"),
)
EXPECTED_FORMULAS = {
    (1, "111"): (
        13209,
        32224,
        "584e4c7b7f8d366496729dc71da3bbb207e7344fee3d9f59a59fe99fd064580d",
    ),
    (3, "111"): (
        15467,
        338785,
        "445366fc33eccbf5f86daedf6d3678c1cf64cb753f97991a7534157f018f90e0",
    ),
    (3, "122"): (
        15467,
        338792,
        "6eaabc69cae2c83f33b5f8851287527dfdbf6e9616805a74c15b399ee9c41df9",
    ),
    (5, "111"): (
        328475,
        1142251,
        "613726bf378c1c3d78abdca387e4dbdb686309b228fa3f73ca621d9a77564f34",
    ),
    (5, "122"): (
        328475,
        1142258,
        "687abee000cf9e3603ac71c1f13fc3544e8afe1af87af443b307cfbc59bd6cad",
    ),
    (5, "222"): (
        328475,
        1142262,
        "a22446e091fcd382b6089da239a5f1a5d9a7a6a048788c91ea69edaa49e329fd",
    ),
    (5, "223"): (
        328475,
        1142266,
        "b34c9a5b18f78dd3ed9d232fd150808978bea9a60d12402a2d2e151d7bbf3395",
    ),
    (7, "111"): (
        330247,
        1145795,
        "c66c51e9c27bd16a47f3c523923a4c8f84f7359b91d8495ed7140dcf3658a174",
    ),
    (7, "122"): (
        330247,
        1145802,
        "de43df31f717eedbaa566b8278c827f80e4d952fe2e72abaeb1ff0a6ec283e32",
    ),
    (7, "222"): (
        330247,
        1145806,
        "e00aaef09785d119aec27499d642437387c3e2e445c9dd19aef5e7ca2b3ddeff",
    ),
    (7, "223"): (
        330247,
        1145810,
        "ba13ba49f105d7cf2ea51ee00b68e1612f2c001c8f7a810751397a61ff0ea99f",
    ),
    (9, "111"): (
        332003,
        1149307,
        "ab5bf8a6caebd6b8b22d4e19248c884d84695436f12141cbcaab221cbba6a4a7",
    ),
    (9, "122"): (
        332003,
        1149314,
        "d7934da69aa58fe545363e7e70039f281dfcad5fbf75840e18ce873695b1ed1c",
    ),
    (9, "222"): (
        332003,
        1149318,
        "5a6ee86c4ac0354814098dd0061a59b84a42b719de1e6dcdca315369544ff8a1",
    ),
    (9, "223"): (
        332003,
        1149322,
        "de887573e63a96ec7c74b392e5f0c5a6c138c71f9f7132924fd73940ca9e075a",
    ),
    (11, "222"): (
        333743,
        1152798,
        "7d03e957abf1d2b8993a0cd7c41337b3a05abceaa9b3565947360d0c6ecf40b2",
    ),
    (11, "223"): (
        333743,
        1152802,
        "6f73c69537a1cfd57dff985a083efa4d547db1da20c8d592951babc3ff11c6a5",
    ),
}
INPUT_HASHES = {
    "AGENTS.md":
        "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3",
    "agents/2026-07-22-wave13-n3-45-computational.md":
        "f1ace31438aa147018cb8210fa92cd940a0a4795e698bc09d34f3537debf8904",
    "agents/2026-07-22-wave13-n3-45-computational-repair.md":
        "ed3946befd9c006c440f7fca599652d887c0fdb3c6b1091de6926cfa7f943607",
    "verification/2026-07-22-wave13-computation-audit.md":
        "b1914cd618aea228cf0c442c6e6fa94c00faf241ddd8d787ce7ba0ae91f14fa3",
    "code/wave13_n3_45_profiles.py":
        "63f38178722cae08723c458e8fd1a3d6bcbadc3f0a9cec2ca50f45c27b13ce92",
    "code/wave13_n3_45_active_sat.py":
        "936cd43e3f0efcf38acf19af363d06cb14916a6bb405873c679c8f82d2e91532",
    "code/wave13_n3_45_test.py":
        "7b7fbdc455619fec68b540c9621b765ebc9a6cd933c8d495a31c7dd2700a6dd6",
    "attempts/wave13-computation/n3-45-local-census.json":
        "6546819c11dbecbf21a4cfaff00b71d338629c045c7bf156493426391b25ac55",
    "attempts/wave13-computation/n3-45-active-local-sat-scan.json":
        "a9cdeca479ffb8283a44a742b0afd241333d6f7d55b082af23e177a95d0c707c",
    "attempts/wave13-computation/n3-45-no-common-point-m5-111.json":
        "629cf0dd9f67b71072e94037161d99891f16c90c330b7d5746ed8a86ac8ba1e8",
    "verification/n3-45-computation/independent_audit.py":
        "b2241fe21f0dee7f390f5935577a553eb2537a4642f0f707d087393997f0dcb7",
    "verification/n3-45-computation/independent_formula_audit.py":
        "c2a1fae2f74e2420d4e89acae627cf40de06ca5301ccffbbb7d19268a045b3c5",
    "verification/n3-45-computation/test_independent_audit.py":
        "a2a370758c486dc4f5b5914773a283e0557b37f6179635939d7b36f88a85ac0e",
}
TOP_KEYS = frozenset({
    "schema",
    "claim_label",
    "target_result",
    "novelty_status",
    "proof_trace_status",
    "variant",
    "active_order",
    "q_values",
    "K_degree",
    "size3_point_count",
    "root_mode",
    "point_sets",
    "K_edges",
    "root_normalization",
    "restrictions",
    "solver_statistics",
    "diagnostics",
    "omitted_premise",
    "builder_source_sha256",
    "core_semantic_sha256",
    "integrity_sha256",
})
ROOT_KEYS = frozenset({
    "point",
    "local_mode",
    "justification",
    "completed_graph_automorphism_assumed",
})
SOLVER_KEYS = frozenset({
    "variant",
    "python",
    "python_sat",
    "solver",
    "conflict_budget",
    "result",
    "proof_trace",
    "variables",
    "clauses",
    "cnf_sha256",
    "candidate_point_variables",
    "candidate_K_edge_variables",
    "candidate_full_overlap_variables",
})
DIAGNOSTIC_KEYS = frozenset({
    "point_count",
    "size2_point_count",
    "size3_point_count",
    "incidence_degrees",
    "linear_pair_owner_violations",
    "missing_point_clique_edges",
    "K_degree_sequence",
    "common_point_Berge_triangle_count",
    "first_common_point_Berge_triangles",
    "meeting_crossing_violations",
    "full_L_overlap_count",
    "maximum_size3_full_L_overlap_degree",
    "size3_points_over_fixed_point_cap",
    "t_degree_histogram",
    "size3_local_type_histogram",
})


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("ascii")


def digest_json(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def project_diagnostics(
    independent: dict[str, object],
    points: Sequence[tuple[int, ...]],
) -> dict[str, object]:
    return {
        "point_count": len(points),
        "size2_point_count": sum(len(point) == 2 for point in points),
        "size3_point_count": sum(len(point) == 3 for point in points),
        "incidence_degrees": independent["incidence_degrees"],
        "linear_pair_owner_violations": len(
            independent["linear_pair_owner_violations"]
        ),
        "missing_point_clique_edges": len(
            independent["missing_point_clique_edges"]
        ),
        "K_degree_sequence": independent["K_degree_sequence"],
        "common_point_Berge_triangle_count": len(
            independent["berge_certificates"]
        ),
        "first_common_point_Berge_triangles": [
            row["triple"]
            for row in independent["berge_certificates"][:10]
        ],
        "meeting_crossing_violations": len(
            independent["meeting_crossing_violations"]
        ),
        "full_L_overlap_count": len(independent["full_L_overlaps"]),
        "maximum_size3_full_L_overlap_degree": independent[
            "maximum_size3_full_L_overlap_degree"
        ],
        "size3_points_over_fixed_point_cap": independent[
            "size3_points_over_fixed_point_cap"
        ],
        "t_degree_histogram": independent["t_degree_histogram"],
        "size3_local_type_histogram": independent[
            "size3_local_type_histogram"
        ],
    }


def refresh_core_and_integrity(candidate: dict[str, object]) -> None:
    core = {
        "variant": candidate["variant"],
        "point_sets": candidate["point_sets"],
        "K_edges": candidate["K_edges"],
        "diagnostics": candidate["diagnostics"],
    }
    candidate["core_semantic_sha256"] = digest_json(core)
    payload = {
        key: candidate[key]
        for key in sorted(TOP_KEYS - {"integrity_sha256"})
    }
    candidate["integrity_sha256"] = digest_json(payload)


def refresh_integrity(candidate: dict[str, object]) -> None:
    payload = {
        key: candidate[key]
        for key in sorted(TOP_KEYS - {"integrity_sha256"})
        if key in candidate
    }
    candidate["integrity_sha256"] = digest_json(payload)


def verify_candidate_schema(
    candidate: dict[str, object],
    arithmetic: ModuleType,
    positive: dict[str, object],
    source_hash: str,
) -> dict[str, object]:
    assert frozenset(candidate) == TOP_KEYS
    assert candidate["schema"] == (
        "conway99-wave13-n3-45-active-local-diagnostic-v2"
    )
    assert candidate["claim_label"] == "CANDIDATE"
    assert candidate["target_result"] == "UNKNOWN"
    assert candidate["novelty_status"] == "UNKNOWN"
    assert candidate["proof_trace_status"] == "NOT_EMITTED"
    assert candidate["variant"] == "no_common_point"
    assert candidate["active_order"] == 15
    assert candidate["q_values"] == [2] * 15
    assert candidate["K_degree"] == 8
    assert candidate["size3_point_count"] == 5
    assert candidate["root_mode"] == "111"
    assert candidate["omitted_premise"] == (
        "common-point/Berge-triangle prohibition"
    )
    assert candidate["restrictions"] == RESTRICTIONS
    assert frozenset(candidate["root_normalization"]) == ROOT_KEYS
    assert candidate["root_normalization"] == {
        "point": [0, 1, 2],
        "local_mode": "111",
        "justification": ROOT_JUSTIFICATION,
        "completed_graph_automorphism_assumed": False,
    }
    assert frozenset(candidate["solver_statistics"]) == SOLVER_KEYS
    assert frozenset(candidate["diagnostics"]) == DIAGNOSTIC_KEYS

    raw_points = candidate["point_sets"]
    raw_edges = candidate["K_edges"]
    assert isinstance(raw_points, list)
    assert isinstance(raw_edges, list)
    points = tuple(arithmetic.point_tuple(item) for item in raw_points)
    edges = tuple(arithmetic.edge_tuple(item) for item in raw_edges)
    assert list(points) == sorted(points, key=lambda item: (len(item), item))
    assert list(edges) == sorted(edges)
    assert len(points) == len(set(points))
    assert len(edges) == len(set(edges))
    assert ROOT in points

    independent = arithmetic.witness_core_diagnostics(
        points,
        frozenset(edges),
    )
    projected = project_diagnostics(independent, points)
    assert candidate["diagnostics"] == projected
    certificates = independent["berge_certificates"]
    assert len(certificates) == 18
    assert all(
        len(set(row["owner_indices"])) == 3
        for row in certificates
    )
    assert all(
        len(row["owners"]) == 3
        for row in certificates
    )
    t_values = independent["t_values"]
    assert [t_values[index] for index in ROOT] == [1, 1, 1]

    core = {
        "variant": candidate["variant"],
        "point_sets": candidate["point_sets"],
        "K_edges": candidate["K_edges"],
        "diagnostics": candidate["diagnostics"],
    }
    assert digest_json(core) == candidate["core_semantic_sha256"]
    assert candidate["core_semantic_sha256"] == (
        "2492601fb4dbb6dd642d73e34404f446ff8d0f1cee6edfaec7babbba39424e03"
    )
    integrity_payload = {
        key: candidate[key]
        for key in sorted(TOP_KEYS - {"integrity_sha256"})
    }
    assert set(integrity_payload) == set(candidate) - {"integrity_sha256"}
    assert digest_json(integrity_payload) == candidate["integrity_sha256"]
    assert candidate["integrity_sha256"] == (
        "5c1758f2a4efc67289ab2e6c987fc31cd75ea4ac9e33eb032cf3a339a13290a1"
    )
    assert candidate["builder_source_sha256"] == source_hash

    statistics = candidate["solver_statistics"]
    assert statistics["variant"] == "no_common_point"
    assert statistics["python"] == sys.version.split()[0]
    assert statistics["python_sat"] == pysat.__version__
    assert statistics["solver"] == "cadical195"
    assert statistics["conflict_budget"] == 300000
    assert statistics["result"] == "SAT_WEAKENED_MODEL"
    assert statistics["proof_trace"] == "NOT_EMITTED"
    assert (
        statistics["variables"],
        statistics["clauses"],
        statistics["cnf_sha256"],
    ) == (
        positive["formula_variables"],
        positive["formula_clauses"],
        positive["formula_sha256"],
    )
    assert statistics["candidate_point_variables"] == 560
    assert statistics["candidate_K_edge_variables"] == 105
    assert statistics["candidate_full_overlap_variables"] == 45045
    assert positive["positive_total_assignment_check"] == {
        "variables_assigned": 328475,
        "clauses_checked": 1141796,
        "violated_clause_count": 0,
    }
    assert positive["falsified_full_common_point_clauses"] == [
        row["triple"] for row in certificates
    ]
    return {
        "schema": candidate["schema"],
        "top_level_keys": len(candidate),
        "root_keys": len(candidate["root_normalization"]),
        "solver_statistic_keys": len(statistics),
        "diagnostic_keys": len(candidate["diagnostics"]),
        "raw_points": len(points),
        "raw_K_edges": len(edges),
        "core_semantic_sha256": candidate["core_semantic_sha256"],
        "integrity_sha256": candidate["integrity_sha256"],
        "integrity_covers_all_material_schema_fields": True,
        "berge_violation_count": len(certificates),
        "all_berge_owner_triples_distinct": True,
        "berge_certificates": certificates,
    }


def hostile_mutations(
    candidate: dict[str, object],
    arithmetic: ModuleType,
    discovery: ModuleType,
) -> dict[str, object]:
    mutations: dict[str, dict[str, object]] = {}

    duplicate_edge = copy.deepcopy(candidate)
    duplicate_edge["K_edges"].append(copy.deepcopy(duplicate_edge["K_edges"][0]))
    duplicate_edge["K_edges"].sort()
    refresh_integrity(duplicate_edge)
    mutations["duplicate_K_record_refreshed_integrity"] = duplicate_edge

    reversed_edge = copy.deepcopy(candidate)
    reversed_edge["K_edges"][0] = list(reversed(reversed_edge["K_edges"][0]))
    refresh_integrity(reversed_edge)
    mutations["reversed_K_record_refreshed_integrity"] = reversed_edge

    duplicate_point = copy.deepcopy(candidate)
    duplicate_point["point_sets"].append(
        copy.deepcopy(duplicate_point["point_sets"][0])
    )
    duplicate_point["point_sets"].sort(key=lambda item: (len(item), item))
    refresh_integrity(duplicate_point)
    mutations["duplicate_point_record_refreshed_integrity"] = duplicate_point

    reversed_point = copy.deepcopy(candidate)
    reversed_point["point_sets"][0] = list(
        reversed(reversed_point["point_sets"][0])
    )
    refresh_integrity(reversed_point)
    mutations["reversed_point_record_refreshed_integrity"] = reversed_point

    for key in (
        "claim_label",
        "root_normalization",
        "solver_statistics",
        "diagnostics",
    ):
        changed = copy.deepcopy(candidate)
        if key == "claim_label":
            changed.pop(key)
            mutations["missing_top_level_field"] = changed
        else:
            nested = changed[key]
            nested.pop(next(iter(nested)))
            refresh_integrity(changed)
            mutations[f"missing_{key}_field"] = changed

    unknown_top = copy.deepcopy(candidate)
    unknown_top["unknown"] = True
    unknown_top["integrity_sha256"] = digest_json({
        key: unknown_top[key]
        for key in sorted(set(unknown_top) - {"integrity_sha256"})
    })
    mutations["unknown_top_level_field_refreshed_integrity"] = unknown_top

    for key in ("root_normalization", "solver_statistics", "diagnostics"):
        changed = copy.deepcopy(candidate)
        changed[key]["unknown"] = True
        if key == "diagnostics":
            refresh_core_and_integrity(changed)
        else:
            refresh_integrity(changed)
        mutations[f"unknown_{key}_field_refreshed_integrity"] = changed

    scalar_changes: dict[str, Callable[[dict[str, object]], None]] = {
        "forged_active_order": lambda item: item.__setitem__(
            "active_order", 99
        ),
        "forged_q_values": lambda item: item.__setitem__(
            "q_values", [3] + [2] * 14
        ),
        "forged_K_degree": lambda item: item.__setitem__("K_degree", 7),
        "forged_size3_count": lambda item: item.__setitem__(
            "size3_point_count", 7
        ),
        "forged_root_mode_and_metadata": lambda item: (
            item.__setitem__("root_mode", "223"),
            item["root_normalization"].__setitem__("local_mode", "223"),
        ),
        "forged_root_justification": lambda item: item[
            "root_normalization"
        ].__setitem__("justification", "forged"),
        "forged_automorphism_assertion": lambda item: item[
            "root_normalization"
        ].__setitem__("completed_graph_automorphism_assumed", True),
        "forged_restrictions": lambda item: item.__setitem__(
            "restrictions", ["active_labels_only"]
        ),
        "forged_omitted_premise": lambda item: item.__setitem__(
            "omitted_premise", "none"
        ),
        "status_claim_VERIFIED": lambda item: item.__setitem__(
            "claim_label", "VERIFIED"
        ),
        "status_target_SOLVED": lambda item: item.__setitem__(
            "target_result", "SOLVED"
        ),
        "status_novelty_ESTABLISHED": lambda item: item.__setitem__(
            "novelty_status", "ESTABLISHED"
        ),
        "status_proof_trace_CHECKED": lambda item: item.__setitem__(
            "proof_trace_status", "CHECKED"
        ),
        "forged_builder_source_hash": lambda item: item.__setitem__(
            "builder_source_sha256", "0" * 64
        ),
        "forged_formula_hash": lambda item: item[
            "solver_statistics"
        ].__setitem__("cnf_sha256", "0" * 64),
        "forged_formula_clause_count": lambda item: item[
            "solver_statistics"
        ].__setitem__("clauses", 1),
        "forged_solver_proof_trace": lambda item: item[
            "solver_statistics"
        ].__setitem__("proof_trace", "CHECKED"),
    }
    for name, mutate in scalar_changes.items():
        changed = copy.deepcopy(candidate)
        mutate(changed)
        refresh_integrity(changed)
        mutations[f"{name}_refreshed_integrity"] = changed

    changed_diagnostic = copy.deepcopy(candidate)
    changed_diagnostic["diagnostics"][
        "common_point_Berge_triangle_count"
    ] = 17
    refresh_core_and_integrity(changed_diagnostic)
    mutations[
        "forged_diagnostics_all_public_digests_refreshed"
    ] = changed_diagnostic

    relabelled = copy.deepcopy(candidate)
    permutation = {index: (index + 3) % ORDER for index in range(ORDER)}
    relabelled["point_sets"] = sorted(
        (
            sorted(permutation[vertex] for vertex in point)
            for point in relabelled["point_sets"]
        ),
        key=lambda item: (len(item), item),
    )
    relabelled["K_edges"] = sorted(
        sorted((permutation[left], permutation[right]))
        for left, right in relabelled["K_edges"]
    )
    points = tuple(tuple(item) for item in relabelled["point_sets"])
    edges = frozenset(tuple(item) for item in relabelled["K_edges"])
    independent = arithmetic.witness_core_diagnostics(points, edges)
    relabelled["diagnostics"] = project_diagnostics(independent, points)
    refresh_core_and_integrity(relabelled)
    assert ROOT not in points
    mutations[
        "full_relabel_root_attack_all_public_digests_refreshed"
    ] = relabelled

    rejections: dict[str, dict[str, str]] = {}
    for name, changed in mutations.items():
        try:
            discovery.validate_weakened_candidate(changed)
        except AssertionError as error:
            rejections[name] = {
                "exception": type(error).__name__,
                "message": str(error),
            }
        else:
            raise AssertionError(f"hostile mutation was accepted: {name}")
    return {
        "mutation_count": len(mutations),
        "all_rejected": True,
        "rejections": rejections,
    }


def audit(repository: Path, solver_name: str) -> dict[str, object]:
    independent_dir = repository / "verification" / "n3-45-computation"
    arithmetic = load_module(
        "wave13_historical_independent_arithmetic",
        independent_dir / "independent_audit.py",
    )
    formula = load_module(
        "wave13_historical_independent_formula",
        independent_dir / "independent_formula_audit.py",
    )
    discovery = load_module(
        "wave13_repaired_discovery_under_test",
        repository / "code" / "wave13_n3_45_active_sat.py",
    )

    observed_hashes = {
        path: sha256_file(repository / path)
        for path in INPUT_HASHES
    }
    assert observed_hashes == INPUT_HASHES
    assert INPUT_HASHES[
        "verification/2026-07-22-wave13-computation-audit.md"
    ] == "b1914cd618aea228cf0c442c6e6fa94c00faf241ddd8d787ce7ba0ae91f14fa3"

    profiles = arithmetic.reconstruct_profiles()
    assert len(profiles) == 9
    surviving_degree = [
        row for row in profiles
        if row["passes_three_distinct_nonsingleton_edges"]
    ]
    surviving_obstruction = [
        row for row in profiles
        if row["passes_frozen_degree_three_obstruction"]
    ]
    assert len(surviving_degree) == 3
    assert len(surviving_obstruction) == 2

    modes = arithmetic.reconstruct_rooted_mode_results()
    q3_modes = modes["order14_q3_containing_mode_counts"]
    assert list(q3_modes) == ["223", "232", "233", "322", "323", "332", "333"]
    assert q3_modes == {word: 0 for word in q3_modes}
    assert modes["order15_ordered_mode_count"] == 8
    assert len(modes["order15_canonical_histogram"]) == 4

    mixed = arithmetic.reconstruct_mixed_profile_reduction()
    signatures = arithmetic.reconstruct_incidence_signatures()
    signature_histogram = Counter(row["m"] for row in signatures)
    assert signature_histogram == {
        1: 2,
        3: 7,
        5: 16,
        7: 21,
        9: 12,
        11: 1,
    }
    assert len(signatures) == 59
    assert arithmetic.minimum_integral_label_use(13)[
        "minimum_used_labels"
    ] == 18
    assert arithmetic.minimum_integral_label_use(15)[
        "minimum_used_labels"
    ] == 20
    cover = arithmetic.reconstruct_branch_cover(signatures)
    assert cover == EXPECTED_BRANCHES

    census_path = (
        repository
        / "attempts"
        / "wave13-computation"
        / "n3-45-local-census.json"
    )
    census = json.loads(census_path.read_text(encoding="utf-8"))
    census_semantic = census["semantic_sha256"]
    census_without_digest = dict(census)
    census_without_digest.pop("semantic_sha256")
    assert digest_json(census_without_digest) == census_semantic
    assert census["builder_source_sha256"] == sha256_file(
        repository / "code" / "wave13_n3_45_profiles.py"
    )
    actual_assignments = census["mixed_order14_reduction"][
        "q3_containing_assignments_checked"
    ]
    assert actual_assignments == [list(map(int, word)) for word in q3_modes]
    actual_rows = census["mixed_order14_reduction"][
        "q3_containing_mode_census"
    ]
    assert [row["q_values"] for row in actual_rows] == actual_assignments
    assert all(row["mode_count"] == 0 and row["modes"] == [] for row in actual_rows)
    assert census["mixed_order14_reduction"][
        "q3_containing_assignment_count"
    ] == 7
    assert census["mixed_order14_reduction"][
        "q3_containing_local_modes"
    ] == []
    assert census["mixed_order14_reduction"]["profile_survivors"] == 0
    assert census["order15_incidence_signature_count"] == 59

    scan_path = (
        repository
        / "attempts"
        / "wave13-computation"
        / "n3-45-active-local-sat-scan.json"
    )
    scan = json.loads(scan_path.read_text(encoding="utf-8"))
    assert scan["schema"] == (
        "conway99-wave13-n3-45-active-local-sat-scan-v1"
    )
    assert scan["status"] == "COMPLETE_BRANCH_COVER_UNSAT_UNVERIFIED"
    assert scan["branch_count"] == 17
    assert tuple(tuple(item) for item in scan["branch_cover"]) == cover
    assert scan["proof_trace_status"] == "NOT_EMITTED"
    assert scan["claim_label"] == "CANDIDATE"
    assert scan["target_result"] == "UNKNOWN"
    assert scan["novelty_status"] == "UNKNOWN"
    assert scan["builder_source_sha256"] == sha256_file(
        repository / "code" / "wave13_n3_45_active_sat.py"
    )
    assert all(row["status"] == "UNSAT_UNVERIFIED" for row in scan["branches"])
    assert all(
        row["proof_trace_status"] == "NOT_EMITTED"
        for row in scan["branches"]
    )
    assert all(
        "proof_trace" not in row["statistics"]
        for row in scan["branches"]
    )
    assert all(row["candidate_validation"] is None for row in scan["branches"])
    archived_formulas = {
        (row["size3_point_count"], row["root_mode"]): (
            row["statistics"]["variables"],
            row["statistics"]["clauses"],
            row["statistics"]["cnf_sha256"],
        )
        for row in scan["branches"]
    }
    assert archived_formulas == EXPECTED_FORMULAS
    scan_semantic = {
        "schema": scan["schema"],
        "status": scan["status"],
        "branch_cover": scan["branch_cover"],
        "branches": [
            {
                "size3_point_count": row["size3_point_count"],
                "root_mode": row["root_mode"],
                "status": row["status"],
                "proof_trace_status": row["proof_trace_status"],
                "variables": row["statistics"]["variables"],
                "clauses": row["statistics"]["clauses"],
                "cnf_sha256": row["statistics"]["cnf_sha256"],
            }
            for row in scan["branches"]
        ],
        "proof_trace_status": scan["proof_trace_status"],
        "builder_source_sha256": scan["builder_source_sha256"],
        "claim_label": scan["claim_label"],
        "target_result": scan["target_result"],
        "novelty_status": scan["novelty_status"],
    }
    assert digest_json(scan_semantic) == scan["semantic_sha256"]

    formula_rebuild = formula.rebuild_scan_formulas(repository)
    assert formula_rebuild["branch_count"] == 17
    assert formula_rebuild["all_exact_hashes_match"] is True
    assert formula_rebuild["distinct_hash_count"] == 17
    independently_rebuilt = {
        (row["m"], row["root_mode"]): (
            row["variables"],
            row["clauses"],
            row["cnf_sha256"],
        )
        for row in formula_rebuild["branches"]
    }
    assert independently_rebuilt == EXPECTED_FORMULAS

    positive = formula.positive_witness_formula_check(
        repository,
        solver_name,
    )
    candidate_path = (
        repository
        / "attempts"
        / "wave13-computation"
        / "n3-45-no-common-point-m5-111.json"
    )
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidate_schema = verify_candidate_schema(
        candidate,
        arithmetic,
        positive,
        scan["builder_source_sha256"],
    )
    discovery_result = discovery.validate_weakened_candidate(candidate)
    assert discovery_result["status"] == "PASS weakened active-local diagnostic"
    assert discovery_result["target_result"] == "UNKNOWN"
    assert discovery_result["novelty_status"] == "UNKNOWN"
    mutations = hostile_mutations(candidate, arithmetic, discovery)

    return {
        "run_metadata": {
            "role": "verifier",
            "git_commit": REPAIR_COMMIT,
            "failed_baseline_commit": FAILED_BASELINE_COMMIT,
            "claim_label": "VERIFIED",
            "scope": (
                "repaired Wave 13 n3=45 computation bundle properties only"
            ),
            "python": sys.version.split()[0],
            "python_sat": pysat.__version__,
            "platform": platform.platform(),
            "solver": solver_name,
        },
        "inputs": observed_hashes,
        "arithmetic_and_cover": {
            "status": "PASS",
            "raw_profiles": len(profiles),
            "surviving_after_degree_filter": len(surviving_degree),
            "surviving_after_degree_three_obstruction": len(
                surviving_obstruction
            ),
            "q3_containing_order14_assignments": q3_modes,
            "order15_ordered_modes": modes["order15_ordered_mode_count"],
            "order15_mode_classes": len(
                modes["order15_canonical_histogram"]
            ),
            "order15_mode_histogram": modes[
                "order15_canonical_histogram"
            ],
            "flower_capacity_feasible": {
                key: value["capacity_feasible"]
                for key, value in mixed["flowers"].items()
            },
            "flower_degree_survivors": {
                key: value["degree_survivors"]
                for key, value in mixed["flowers"].items()
            },
            "aggregate_signatures": len(signatures),
            "signature_histogram": dict(sorted(signature_histogram.items())),
            "m13_minimum_labels_before_cap": 18,
            "m15_minimum_labels_before_cap": 20,
            "branch_cover": [list(item) for item in cover],
            "census_semantic_sha256": census_semantic,
        },
        "formula_reconstruction": {
            "status": "PASS",
            "independent_builder_source": (
                "verification/n3-45-computation/"
                "independent_formula_audit.py"
            ),
            "branch_count": formula_rebuild["branch_count"],
            "distinct_hash_count": formula_rebuild["distinct_hash_count"],
            "all_exact_hashes_match": True,
            "formulas": formula_rebuild["branches"],
            "scan_semantic_sha256": scan["semantic_sha256"],
        },
        "positive_diagnostic": {
            "status": "PASS",
            **positive,
            **candidate_schema,
            "discovery_validator_replay": discovery_result,
        },
        "hostile_mutations": {
            "status": "PASS",
            **mutations,
        },
        "negative_solver_boundary": {
            "status": "UNSAT_UNVERIFIED",
            "branch_count": 17,
            "proof_trace_status": "NOT_EMITTED",
            "proof_trace_checked": False,
        },
        "target_result": "UNKNOWN",
        "novelty_status": "UNKNOWN",
        "prior_fail_audit_preserved": {
            "status": "PASS",
            "sha256": observed_hashes[
                "verification/2026-07-22-wave13-computation-audit.md"
            ],
        },
        "limitations": [
            "No negative proof trace was present or checked.",
            "The CNFs encode only the declared active-local restricted model.",
            "The full v2 positive-candidate schema has no positive full artifact here; the diagnostic v2 artifact and validator were audited directly.",
            "The historical verifier suite contains assertions about the failed baseline and is expected not to be forward-compatible with the repair.",
            "No project-target or novelty claim is promoted.",
        ],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args(argv)
    result = audit(arguments.repository.resolve(), arguments.solver)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.output is not None:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(
            rendered,
            encoding="utf-8",
            newline="\n",
        )
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
