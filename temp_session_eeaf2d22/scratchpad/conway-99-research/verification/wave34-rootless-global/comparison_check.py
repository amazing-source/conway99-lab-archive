#!/usr/bin/env python3
"""Independent Stage-2 comparison for the Wave 34 rootless candidate.

Candidate Python is read statically but never imported by this module.  The
45-vertex control, its restricted searches, and all arithmetic are rebuilt
with verifier-owned standard-library code.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from collections import Counter
from functools import lru_cache
from itertools import combinations, product
from math import comb
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
N = 12

CANDIDATE_INPUTS = {
    "verification/wave34-rootless-global/candidate-release.md": "c40c82c96818c1bebdb5de0b073a3b4496d4b238270603bfbd12421c8d6d1041",
    "agents/2026-07-24-wave34-rootless-global.md": "71f5b49622629a65ffafea2636c552bccaecaadc7584326c70d8819f54e997ed",
    "attempts/wave34-rootless-global/check_local_model.py": "33577962a44241cf3fd9d5a6b5948c35ddd757aed5975bd755c384ded00deed6",
    "attempts/wave34-rootless-global/exact-results.json": "fd4ff04bd13128a26d9a5ecb4bd1c2a8832d29d0056a592d4d90074747a0c331",
    "attempts/wave34-rootless-global/local-control.json": "a25d19e3eda3ec77b55065b7f39a68345fa911b80eafbff0e4c37b1857e10301",
    "attempts/wave34-rootless-global/test_local_model.py": "21d4dc17c19098ee826202af4688611dbbf5982d0ab9216bb87da6839452a378",
    "attempts/wave34-rootless-global/artifact-manifest.sha256": "bda35ed81dcca9918cff3c544956039b8949a61bfa8a232e4e2d40edcd8d5af2",
    "verification/wave34-rootless-global/precomparison/artifact-manifest.sha256": "27c13fb233af677c1619d571bf73820cddd4451172fdd749ace1c9f65f8f3c8d",
}

CANDIDATE_ARTIFACTS = {
    key: value
    for key, value in CANDIDATE_INPUTS.items()
    if key.startswith("agents/") or (
        key.startswith("attempts/") and not key.endswith("artifact-manifest.sha256")
    )
}

CORRECT_WAVE33_COMPARISON_HASH = (
    "8b7b27fd67f12bb82cb6eebf645d0c46324d7227e51bdeb0093fbcdf9d753872"
)
CANDIDATE_CLAIMED_WAVE33_COMPARISON_HASH = (
    "8b7b27fd67f12bb82c60eb27c72a62c913d06f2d86f3eb626dcddd6ac75afeb"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_sha256_manifest(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split(maxsplit=1)
        result[name] = digest
    return result


def validate_provenance() -> dict[str, object]:
    actual = {name: sha256(ROOT / name) for name in CANDIDATE_INPUTS}
    mismatches = {
        name: {"expected": CANDIDATE_INPUTS[name], "actual": actual[name]}
        for name in CANDIDATE_INPUTS
        if actual[name] != CANDIDATE_INPUTS[name]
    }

    freeze = parse_sha256_manifest(HERE / "candidate-input-freeze.sha256")
    freeze_matches = freeze == CANDIDATE_INPUTS

    candidate_manifest_path = (
        ROOT / "attempts/wave34-rootless-global/artifact-manifest.sha256"
    )
    candidate_manifest = parse_sha256_manifest(candidate_manifest_path)
    candidate_manifest_matches = candidate_manifest == CANDIDATE_ARTIFACTS

    precomparison_manifest_path = (
        HERE / "precomparison/artifact-manifest.sha256"
    )
    precomparison_manifest = parse_sha256_manifest(precomparison_manifest_path)
    precomparison_mismatches = {}
    for name, expected in precomparison_manifest.items():
        actual_hash = sha256(ROOT / name)
        if actual_hash != expected:
            precomparison_mismatches[name] = {
                "expected": expected,
                "actual": actual_hash,
            }

    return {
        "all_released_bytes_match": not mismatches,
        "released_entry_count": len(CANDIDATE_INPUTS),
        "released_hashes": actual,
        "released_mismatches": mismatches,
        "candidate_input_freeze_matches": freeze_matches,
        "candidate_artifact_manifest_matches": candidate_manifest_matches,
        "candidate_artifact_manifest_entries": len(candidate_manifest),
        "precomparison_manifest_sha256": sha256(precomparison_manifest_path),
        "precomparison_entries": len(precomparison_manifest),
        "precomparison_all_match": not precomparison_mismatches,
        "precomparison_mismatches": precomparison_mismatches,
    }


def independent_factorization() -> tuple[tuple[tuple[int, int], ...], ...]:
    """Round-robin one-factorization, independently reconstructed."""
    factors = []
    modulus = N - 1
    for pivot in range(modulus):
        edges = {tuple(sorted((N - 1, pivot)))}
        for step in range(1, N // 2):
            edges.add(
                tuple(
                    sorted(
                        (
                            (pivot + step) % modulus,
                            (pivot - step) % modulus,
                        )
                    )
                )
            )
        factor = tuple(sorted(edges))
        if len(factor) != N // 2:
            raise AssertionError("factor does not have six edges")
        factors.append(factor)
    all_edges = [edge for factor in factors for edge in factor]
    if len(all_edges) != comb(N, 2) or len(set(all_edges)) != comb(N, 2):
        raise AssertionError("factors do not partition K12")
    return tuple(factors)


FACTORS = independent_factorization()


def partner_maps() -> tuple[tuple[int, ...], ...]:
    maps = []
    for factor in FACTORS:
        partner = [-1] * N
        for u, v in factor:
            partner[u], partner[v] = v, u
        if sorted(partner) != list(range(N)):
            # A perfect-matching involution is a permutation, so its values
            # are exactly 0,...,11.
            raise AssertionError("invalid partner map")
        maps.append(tuple(partner))
    return tuple(maps)


PARTNERS = partner_maps()


def add_edge(graph: dict[str, set[str]], u: str, v: str) -> None:
    if u == v:
        raise AssertionError("loop")
    graph[u].add(v)
    graph[v].add(u)


def x(fibre: int, label: int) -> str:
    return f"x{fibre}_{label}"


def t(index: int) -> str:
    return f"t{index}"


def load_control() -> dict[str, object]:
    path = ROOT / "attempts/wave34-rootless-global/local-control.json"
    return json.loads(path.read_text(encoding="utf-8"))


def control_sigma(control: dict[str, object]) -> tuple[int, ...]:
    return tuple(control["cross_matching_rule"]["sigma"])


def fixed_labels(sigma: tuple[int, ...]) -> tuple[int, ...]:
    if sorted(sigma) != list(range(N)):
        raise AssertionError("sigma is not a permutation")
    return tuple(i for i, image in enumerate(sigma) if i == image)


def build_core(
    factor_indices: tuple[int, int, int],
    sigma: tuple[int, ...],
) -> dict[str, set[str]]:
    vertices = [t(i) for i in range(3)]
    vertices += [x(fibre, label) for fibre in range(3) for label in range(N)]
    graph = {vertex: set() for vertex in vertices}

    for i, j in combinations(range(3), 2):
        add_edge(graph, t(i), t(j))
    for fibre in range(3):
        for label in range(N):
            add_edge(graph, t(fibre), x(fibre, label))
    for fibre, factor_index in enumerate(factor_indices):
        for u, v in FACTORS[factor_index]:
            add_edge(graph, x(fibre, u), x(fibre, v))
    for label in range(N):
        add_edge(graph, x(0, label), x(1, label))
        add_edge(graph, x(1, label), x(2, label))
        add_edge(graph, x(2, label), x(0, sigma[label]))
    return graph


def copy_graph(graph: dict[str, set[str]]) -> dict[str, set[str]]:
    return {vertex: set(neighbours) for vertex, neighbours in graph.items()}


def extend_from_certificate(
    core: dict[str, set[str]], control: dict[str, object]
) -> dict[str, set[str]]:
    graph = copy_graph(core)
    for y, record in control["completion_vertices"].items():
        graph[y] = set()
        for neighbour in record["core_neighbours"]:
            add_edge(graph, y, neighbour)
    return graph


def edge_count(graph: dict[str, set[str]]) -> int:
    return sum(map(len, graph.values())) // 2


def pair_key(u: str, v: str) -> tuple[str, str]:
    return tuple(sorted((u, v)))


def common_count(graph: dict[str, set[str]], u: str, v: str) -> int:
    return len(graph[u] & graph[v])


def cap_findings(graph: dict[str, set[str]]) -> list[dict[str, object]]:
    findings = []
    for u, v in combinations(sorted(graph), 2):
        adjacent = v in graph[u]
        cap = 1 if adjacent else 2
        common = sorted(graph[u] & graph[v])
        if len(common) > cap:
            findings.append(
                {
                    "pair": [u, v],
                    "adjacent": adjacent,
                    "cap": cap,
                    "common": common,
                }
            )
    return findings


def fixed_transversals(sigma: tuple[int, ...]) -> tuple[tuple[str, str, str], ...]:
    return tuple(
        (x(0, label), x(1, label), x(2, label))
        for label in fixed_labels(sigma)
    )


def defect_edges(sigma: tuple[int, ...]) -> tuple[tuple[str, str], ...]:
    result = []
    for label in range(N):
        if sigma[label] == label:
            continue
        result.extend(
            (
                pair_key(x(0, label), x(1, label)),
                pair_key(x(1, label), x(2, label)),
                pair_key(x(2, label), x(0, sigma[label])),
            )
        )
    return tuple(sorted(result))


def fixed_pair_multiplicities(
    factor_indices: tuple[int, int, int],
    sigma: tuple[int, ...],
) -> dict[int, int]:
    fixed = fixed_labels(sigma)
    counts = {i: 0 for i in range(4)}
    for u, v in combinations(fixed, 2):
        multiplicity = sum(
            PARTNERS[factor_index][u] == v for factor_index in factor_indices
        )
        counts[multiplicity] += 1
    return counts


def relation_degrees(q: int) -> dict[str, int]:
    r3 = 12 - q
    r2 = 3 * q
    r1 = 216 - 2 * r2 - 3 * r3
    r0 = 212 - r1 - r2 - r3
    return {"R0": r0, "R1": r1, "R2": r2, "R3": r3}


def endpoint_arithmetic() -> dict[str, object]:
    n_triangles = 231
    r2_edges = 708
    sum_q = 2 * r2_edges // 3
    r3_degree_sum = n_triangles * 12 - sum_q
    r3_edges = r3_degree_sum // 2
    r3_triangle_cap = r3_edges // 3
    return {
        "relation_degree_formula": {
            "R0": "20+q",
            "R1": "180-3q",
            "R2": "3q",
            "R3": "12-q",
        },
        "sum_q": sum_q,
        "R3_degree_sum": r3_degree_sum,
        "R3_edge_count": r3_edges,
        "R3_triangle_cap": r3_triangle_cap,
        "central_triple_overlap_cap": 3 * r3_triangle_cap,
    }


def matrix_multiply(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    return [
        [sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))]
        for i in range(len(a))
    ]


def matrix_trace(a: list[list[int]]) -> int:
    return sum(a[i][i] for i in range(len(a)))


def single_motif_trace() -> int:
    r2 = [[0, 1, 0], [1, 0, 0], [0, 0, 0]]
    r3 = [[0, 0, 1], [0, 0, 1], [1, 1, 0]]
    return matrix_trace(matrix_multiply(r2, matrix_multiply(r3, r3)))


def gram_times_vector(matrix: list[list[int]], vector: list[int]) -> list[int]:
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def r3_triangle_gram() -> dict[str, object]:
    gram = [[4 if i == j else -2 for j in range(3)] for i in range(3)]
    kernel = [1, 1, 1]
    return {
        "gram": gram,
        "kernel": kernel,
        "kernel_check": gram_times_vector(gram, kernel),
        "marked_row_injectivity": {
            "diagonal_entry": 4,
            "maximum_disjoint_off_diagonal_entry": 1,
            "maximum_one_vertex_overlap_entry": 0,
            "two_vertex_overlap": "impossible for distinct triangles when lambda=1",
            "distinct_rows_cannot_equal": True,
        },
        "conclusion": "for an R3 edge X,Y, any R3 completion is -(X+Y), hence at most one distinct row",
    }


@lru_cache(maxsize=1)
def restricted_factor_scan() -> dict[str, int]:
    sigma = control_sigma(load_control())
    checked = 0
    cap_feasible = 0
    no_double = 0
    for indices in product(range(len(FACTORS)), repeat=3):
        checked += 1
        core = build_core(indices, sigma)
        if cap_findings(core):
            continue
        cap_feasible += 1
        if fixed_pair_multiplicities(indices, sigma)[2] == 0:
            no_double += 1
    return {
        "triples_checked": checked,
        "cap_feasible": cap_feasible,
        "cap_and_no_double_overlap_feasible": no_double,
    }


def base_common_counts(graph: dict[str, set[str]]) -> dict[tuple[str, str], int]:
    return {
        pair_key(u, v): common_count(graph, u, v)
        for u, v in combinations(sorted(graph), 2)
    }


def enumerate_completion_neighbourhoods(
    core: dict[str, set[str]],
    sigma: tuple[int, ...],
    endpoints: tuple[str, str],
) -> list[tuple[str, ...]]:
    endpoint_set = set(endpoints)
    fibres = [
        tuple(x(fibre, label) for label in range(N)) for fibre in range(3)
    ]
    choices_by_fibre: list[list[tuple[str, ...]]] = []
    for fibre in fibres:
        forced = tuple(sorted(endpoint_set & set(fibre)))
        needed = 2 - len(forced)
        available = [vertex for vertex in fibre if vertex not in endpoint_set]
        choices_by_fibre.append(
            [
                tuple(sorted((*forced, *extra)))
                for extra in combinations(available, needed)
            ]
        )

    base_counts = base_common_counts(core)
    transversals = fixed_transversals(sigma)
    accepted = []
    for fibre_choices in product(*choices_by_fibre):
        neighbourhood = tuple(
            sorted(vertex for choice in fibre_choices for vertex in choice)
        )
        neighbours = set(neighbourhood)
        if len(neighbours) != 6 or not endpoint_set <= neighbours:
            continue

        # The new completion is a common neighbour of every selected pair.
        if any(
            base_counts[pair_key(u, v)]
            + 1
            > (1 if v in core[u] else 2)
            for u, v in combinations(neighbourhood, 2)
        ):
            continue

        # Upper caps for every completion-to-core pair.
        if any(
            len(neighbours & core[vertex])
            > (1 if vertex in neighbours else 2)
            for vertex in core
        ):
            continue

        # No fixed transversal is R3 from this completed R2 triangle.
        closes = False
        for transversal in transversals:
            cross = sum(
                right in core[left]
                for left in endpoints
                for right in transversal
            )
            cross += len(neighbours & set(transversal))
            if cross == 3:
                closes = True
                break
        if not closes:
            accepted.append(neighbourhood)
    return accepted


@lru_cache(maxsize=1)
def independent_completion_search() -> dict[str, object]:
    control = load_control()
    sigma = control_sigma(control)
    indices = tuple(
        control["within_fibre_matching_rule"]["factor_indices_for_X0_X1_X2"]
    )
    core = build_core(indices, sigma)
    edges = defect_edges(sigma)
    candidates = {
        edge: enumerate_completion_neighbourhoods(core, sigma, edge)
        for edge in edges
    }
    ordered = sorted(edges, key=lambda edge: (len(candidates[edge]), edge))
    base_counts = base_common_counts(core)
    extra: dict[tuple[str, str], int] = {}
    chosen: dict[tuple[str, str], tuple[str, ...]] = {}
    nodes = 0

    def search(position: int) -> bool:
        nonlocal nodes
        nodes += 1
        if position == len(ordered):
            return True
        edge = ordered[position]
        for neighbourhood in candidates[edge]:
            neighbours = set(neighbourhood)
            if any(
                len(neighbours & set(previous)) > 2
                for previous in chosen.values()
            ):
                continue

            keys = [pair_key(u, v) for u, v in combinations(neighbourhood, 2)]
            valid = True
            for key in keys:
                u, v = key
                cap = 1 if v in core[u] else 2
                if base_counts[key] + extra.get(key, 0) + 1 > cap:
                    valid = False
                    break
            if not valid:
                continue

            for key in keys:
                extra[key] = extra.get(key, 0) + 1
            chosen[edge] = neighbourhood
            if search(position + 1):
                return True
            del chosen[edge]
            for key in keys:
                extra[key] -= 1
                if not extra[key]:
                    del extra[key]
        return False

    found = search(0)
    return {
        "found": found,
        "candidate_counts": {
            "|".join(edge): len(candidates[edge]) for edge in edges
        },
        "backtracking_nodes": nodes,
        "chosen": {
            "|".join(edge): list(chosen[edge]) for edge in edges
        }
        if found
        else {},
    }


def local_control_analysis() -> dict[str, object]:
    control = load_control()
    sigma = control_sigma(control)
    fixed = fixed_labels(sigma)
    factor_indices = tuple(
        control["within_fibre_matching_rule"]["factor_indices_for_X0_X1_X2"]
    )
    core = build_core(factor_indices, sigma)
    extended = extend_from_certificate(core, control)
    defects = defect_edges(sigma)
    transversals = fixed_transversals(sigma)

    core_lambda_failures = []
    for u in core:
        for v in core[u]:
            if u < v and common_count(extended, u, v) != 1:
                core_lambda_failures.append([u, v, common_count(extended, u, v)])

    base_completion_mu_failures = []
    completion_vertices = sorted(control["completion_vertices"])
    for base in (t(0), t(1), t(2)):
        for y in completion_vertices:
            if y in extended[base] or common_count(extended, base, y) != 2:
                base_completion_mu_failures.append(
                    [base, y, common_count(extended, base, y)]
                )

    motif_closures = []
    for y, record in control["completion_vertices"].items():
        r2_triangle = set(record["assigned_nonclosed_edge"]) | {y}
        for transversal in transversals:
            cross = sum(
                right in extended[left]
                for left in r2_triangle
                for right in transversal
            )
            if cross == 3:
                motif_closures.append([y, list(transversal)])

    yy_histogram = Counter(
        common_count(extended, u, v)
        for u, v in combinations(completion_vertices, 2)
    )
    y_core_edge_lambda_histogram = Counter()
    y_core_nonedge_common_histogram = Counter()
    for y in completion_vertices:
        for vertex in core:
            count = common_count(extended, y, vertex)
            if vertex in extended[y]:
                y_core_edge_lambda_histogram[count] += 1
            else:
                y_core_nonedge_common_histogram[count] += 1

    full_degree_histogram = Counter(map(len, extended.values()))
    full_lambda_failures = []
    full_mu_failures = []
    for u, v in combinations(sorted(extended), 2):
        count = common_count(extended, u, v)
        if v in extended[u]:
            if count != 1:
                full_lambda_failures.append([u, v, count])
        elif count != 2:
            full_mu_failures.append([u, v, count])

    certificate_neighbourhoods = {
        "|".join(tuple(record["assigned_nonclosed_edge"])): sorted(
            record["core_neighbours"]
        )
        for record in control["completion_vertices"].values()
    }
    search = independent_completion_search()

    return {
        "sigma": list(sigma),
        "q_T": N - len(fixed),
        "fixed_labels": list(fixed),
        "R3_neighbours_of_T": len(fixed),
        "R2_neighbours_of_T": len(defects),
        "factor_indices": list(factor_indices),
        "fixed_pair_multiplicities": {
            str(k): v
            for k, v in fixed_pair_multiplicities(factor_indices, sigma).items()
        },
        "core_vertex_count": len(core),
        "core_edge_count": edge_count(core),
        "extended_vertex_count": len(extended),
        "extended_present_edge_count": edge_count(extended),
        "core_lambda_failures_after_completion": core_lambda_failures,
        "base_completion_mu_failures": base_completion_mu_failures,
        "current_upper_cap_findings": cap_findings(extended),
        "central_motif_closures": motif_closures,
        "completion_pair_common_core_histogram": {
            str(k): v for k, v in sorted(yy_histogram.items())
        },
        "completion_pairs_forced_nonadjacent_now": yy_histogram[2],
        "completion_pairs_still_edge_undecided": yy_histogram[0] + yy_histogram[1],
        "completion_to_core_edge_lambda_histogram": {
            str(k): v for k, v in sorted(y_core_edge_lambda_histogram.items())
        },
        "completion_to_core_nonedge_common_histogram": {
            str(k): v for k, v in sorted(y_core_nonedge_common_histogram.items())
        },
        "as_full_45_vertex_graph": {
            "degree_histogram": {
                str(k): v for k, v in sorted(full_degree_histogram.items())
            },
            "vertices_failing_degree_14": sum(
                count for degree, count in full_degree_histogram.items() if degree != 14
            ),
            "lambda_failures": len(full_lambda_failures),
            "lambda_failure_common_count_histogram": {
                str(k): v
                for k, v in sorted(
                    Counter(row[2] for row in full_lambda_failures).items()
                )
            },
            "mu_failures": len(full_mu_failures),
            "mu_failure_common_count_histogram": {
                str(k): v
                for k, v in sorted(
                    Counter(row[2] for row in full_mu_failures).items()
                )
            },
            "is_target_graph": False,
        },
        "restricted_factor_scan": restricted_factor_scan(),
        "completion_search": search,
        "certificate_neighbourhoods_match_search_witness": (
            certificate_neighbourhoods == search["chosen"]
        ),
        "certificate_unset": control["unset"],
    }


def imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module.split(".")[0])
    return sorted(set(names))


def static_candidate_audit() -> dict[str, object]:
    checker_path = ROOT / "attempts/wave34-rootless-global/check_local_model.py"
    test_path = ROOT / "attempts/wave34-rootless-global/test_local_model.py"
    checker_text = checker_path.read_text(encoding="utf-8")
    test_text = test_path.read_text(encoding="utf-8")
    return {
        "candidate_checker_imported_or_executed_by_verifier_module": False,
        "checker_imports": imported_modules(checker_path),
        "test_imports": imported_modules(test_path),
        "candidate_tests_import_candidate_checker": "import check_local_model as model"
        in test_text,
        "random_module_used": "random" in imported_modules(checker_path),
        "scope_markers_present": all(
            marker in checker_text
            for marker in (
                "partial-incidence checker",
                "not an SRG extension",
                "No 99-vertex graph",
            )
        ),
    }


def candidate_comparison() -> dict[str, object]:
    exact_path = ROOT / "attempts/wave34-rootless-global/exact-results.json"
    exact = json.loads(exact_path.read_text(encoding="utf-8"))
    report = (
        ROOT / "agents/2026-07-24-wave34-rootless-global.md"
    ).read_text(encoding="utf-8")
    control = load_control()
    local = local_control_analysis()
    arithmetic = endpoint_arithmetic()
    stage1 = json.loads(
        (HERE / "precomparison/results.json").read_text(encoding="utf-8")
    )

    claimed_input_hash = exact["inputs"][
        "verification/wave33-rootless-motif/comparison-results.json"
    ]
    report_has_same_wrong_hash = CANDIDATE_CLAIMED_WAVE33_COMPARISON_HASH in report

    candidate_control = exact["finite_local_control"]
    control_checked = control["checked_properties"]
    expected_counts = {
        "x0_0|x1_0": 2345,
        "x0_0|x2_1": 2353,
        "x0_1|x1_1": 2346,
        "x0_1|x2_0": 2346,
        "x1_0|x2_0": 2346,
        "x1_1|x2_1": 2353,
    }

    agreements = {
        "lemma1_fixed_point_model": (
            local["q_T"] == 2
            and local["R3_neighbours_of_T"] == 10
        ),
        "lemma2_relation_degrees_q2": relation_degrees(2)
        == {"R0": 22, "R1": 174, "R2": 6, "R3": 10},
        "endpoint_sum_q": arithmetic["sum_q"] == 472,
        "endpoint_R3_edges": arithmetic["R3_edge_count"] == 1150,
        "lemma3_motif_normalization": single_motif_trace() == 2,
        "lemma4_R3_edge_completion_unique": r3_triangle_gram()["kernel_check"]
        == [0, 0, 0],
        "lemma4_R3_triangle_cap": arithmetic["R3_triangle_cap"] == 383,
        "lemma4_central_triple_overlap_cap": arithmetic[
            "central_triple_overlap_cap"
        ]
        == 1149,
        "control_core_counts": (
            local["core_vertex_count"],
            local["core_edge_count"],
        )
        == (39, 93),
        "control_extended_counts": (
            local["extended_vertex_count"],
            local["extended_present_edge_count"],
        )
        == (45, 129),
        "control_fixed_multiplicities": local["fixed_pair_multiplicities"]
        == {"0": 33, "1": 12, "2": 0, "3": 0},
        "control_core_lambda": not local["core_lambda_failures_after_completion"],
        "control_base_completion_mu": not local["base_completion_mu_failures"],
        "control_current_caps": not local["current_upper_cap_findings"],
        "control_no_central_motif": not local["central_motif_closures"],
        "factor_scan_counts": local["restricted_factor_scan"]
        == {
            "triples_checked": 1331,
            "cap_feasible": 1300,
            "cap_and_no_double_overlap_feasible": 1000,
        },
        "completion_candidate_counts": local["completion_search"][
            "candidate_counts"
        ]
        == expected_counts,
        "completion_backtracking": (
            local["completion_search"]["found"]
            and local["completion_search"]["backtracking_nodes"] == 31
        ),
        "completion_certificate_witness": local[
            "certificate_neighbourhoods_match_search_witness"
        ],
        "candidate_exact_summary_counts": (
            candidate_control["completed_partial_vertices"],
            candidate_control["completed_partial_edges"],
            candidate_control["R3_neighbours_of_T"],
            candidate_control["R2_neighbours_of_T"],
        )
        == (45, 129, 10, 6),
        "candidate_control_json_counts": (
            control_checked["vertex_count"],
            control_checked["edge_count"],
            control_checked["R3_neighbours_of_T"],
            control_checked["R2_neighbours_of_T"],
        )
        == (45, 129, 10, 6),
    }

    return {
        "agreements": agreements,
        "all_scoped_mathematical_and_control_claims_reproduce": all(
            agreements.values()
        ),
        "provenance_discrepancy": {
            "path": "verification/wave33-rootless-motif/comparison-results.json",
            "candidate_claimed_hash": claimed_input_hash,
            "candidate_report_repeats_claimed_hash": report_has_same_wrong_hash,
            "stage1_frozen_hash": CORRECT_WAVE33_COMPARISON_HASH,
            "hashes_match": claimed_input_hash == CORRECT_WAVE33_COMPARISON_HASH,
            "severity": "NONBLOCKING_FOR_RECONSTRUCTED_MATHEMATICS_BUT_BLOCKING_FOR_LITERAL_INPUT_PROVENANCE",
        },
        "scope_qualifiers": {
            "completion_pair_common_core_histogram": local[
                "completion_pair_common_core_histogram"
            ],
            "nine_completion_pairs_forced_nonadjacent": local[
                "completion_pairs_forced_nonadjacent_now"
            ],
            "six_completion_pairs_remain_edge_undecided": local[
                "completion_pairs_still_edge_undecided"
            ],
            "new_completion_to_core_edges_with_no_current_lambda_witness": local[
                "completion_to_core_edge_lambda_histogram"
            ]["0"],
            "new_completion_to_core_edges_with_exact_current_lambda": local[
                "completion_to_core_edge_lambda_histogram"
            ]["1"],
            "full_graph_hostile_check": local["as_full_45_vertex_graph"],
            "factor_scan_domain": "11^3 ordered triples from one canonical K12 one-factorization only",
            "control_extendibility": "NOT_ESTABLISHED",
            "qualifier_status": "CANDIDATE_PARTIAL_CONTROL_ONLY",
        },
        "stage1_stronger_results_not_contradicted": {
            "q_not_equal_1": stage1["status"]["q_not_equal_1"],
            "all_relation_codegree_caps": stage1["projector_common_R3_caps"][
                "actual_incidence_improvements"
            ],
            "R0_wedge_lower": stage1["endpoint_global_overlap"][
                "R0_wedge_lower"
            ]["minimum_R0_centered_wedges"],
            "R3_four_cycle_lower": stage1["endpoint_global_overlap"][
                "R0_wedge_lower"
            ]["R3_four_cycle_lower"],
        },
        "candidate_status_wall_preserved": exact["target_conclusion"],
        "local_control": local,
    }


def build_results() -> dict[str, object]:
    provenance = validate_provenance()
    if not (
        provenance["all_released_bytes_match"]
        and provenance["candidate_input_freeze_matches"]
        and provenance["candidate_artifact_manifest_matches"]
        and provenance["precomparison_all_match"]
    ):
        raise RuntimeError(f"provenance validation failed: {provenance}")

    comparison = candidate_comparison()
    return {
        "schema_version": 1,
        "role": "clean_room_adversarial_verifier_candidate_comparison",
        "claim_label": "VERIFIED_SCOPED_WITH_NONBLOCKING_PROVENANCE_DEFECT",
        "scope": (
            "Static and independently reconstructed comparison of the frozen "
            "Wave 34 rootless actual-incidence candidate"
        ),
        "independence": {
            "stage1_frozen_before_candidate_inspection": True,
            "candidate_checker_imported_by_verifier_code": False,
            "candidate_checker_executed_by_verifier_code": False,
            "git_used": False,
        },
        "provenance": provenance,
        "static_candidate_audit": static_candidate_audit(),
        "endpoint_arithmetic": endpoint_arithmetic(),
        "single_motif_trace": single_motif_trace(),
        "R3_triangle_gram": r3_triangle_gram(),
        "comparison": comparison,
        "verdict": "PASS_SCOPED_WITH_NONBLOCKING_PROVENANCE_AND_SCOPE_QUALIFIERS",
        "status": {
            "candidate_lemmas_1_to_4": "PASS_SCOPED",
            "endpoint_counts": "PASS",
            "mixed_trace_normalization": "PASS",
            "45_vertex_control_arithmetic": "PASS_CANDIDATE_PARTIAL_ONLY",
            "candidate_input_provenance": "FAIL_ONE_HASH",
            "actual_motif_forcing": "UNKNOWN",
            "rootless_endpoint": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.dumps(build_results(), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
