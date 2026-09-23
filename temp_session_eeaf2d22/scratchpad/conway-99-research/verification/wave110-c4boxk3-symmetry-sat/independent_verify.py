"""Independent verifier for the sealed Wave 110 symmetry-reduced SAT package.

This module reconstructs the motif incidence domain and all submission
counts without calling Wave 110's audit routine.  It calls the discovery
lex-CNF builder only as the object under test, checks its Boolean truth table,
and independently tests the shared-potential orbit argument on exhaustive
small colored graphs.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
from collections import Counter, defaultdict
from itertools import combinations, permutations
from pathlib import Path
from types import ModuleType
from typing import Iterable


PACKAGE = Path(__file__).resolve().parent
REPOSITORY = PACKAGE.parents[1]
DISCOVERY = REPOSITORY / "attempts" / "wave110-c4boxk3-symmetry-sat"
DISCOVERY_MANIFEST_SHA256 = (
    "1cef4ea7a81e844f10a56ccb1b5a5e0c4c7414b4efc766c486cdc666de8940ea"
)
OUTSIDE_VERTICES = 87
MOTIF_VERTICES = 12


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_discovery() -> ModuleType:
    """Load the frozen Wave 110 implementation as the object under test."""

    source = DISCOVERY / "symmetry_sat.py"
    spec = importlib.util.spec_from_file_location("wave110_under_test", source)
    require(spec is not None and spec.loader is not None, "cannot load Wave 110")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_discovery_manifest() -> dict[str, object]:
    manifest = DISCOVERY / "package-manifest.sha256"
    require(
        sha256(manifest) == DISCOVERY_MANIFEST_SHA256,
        "Wave 110 package-manifest hash drift",
    )
    checked: list[dict[str, str]] = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        path = (REPOSITORY / relative).resolve()
        require(
            path.is_relative_to(DISCOVERY.resolve()),
            f"manifest path escapes discovery package: {relative}",
        )
        actual = sha256(path)
        require(actual == expected, f"manifest mismatch: {relative}")
        checked.append(
            {"path": relative.replace("\\", "/"), "sha256": actual}
        )
    return {
        "manifest_sha256": DISCOVERY_MANIFEST_SHA256,
        "entry_count": len(checked),
        "all_entries_match": True,
        "entries": checked,
    }


def motif_adjacency() -> tuple[tuple[int, ...], ...]:
    """Construct C4 Cartesian K3 directly from its product definition."""

    vertices = tuple((cycle, triangle) for cycle in range(4) for triangle in range(3))
    rows = [[0] * MOTIF_VERTICES for _ in range(MOTIF_VERTICES)]
    for left, right in combinations(range(MOTIF_VERTICES), 2):
        c1, t1 = vertices[left]
        c2, t2 = vertices[right]
        adjacent = (
            c1 == c2 and t1 != t2
        ) or (
            t1 == t2 and (c1 - c2) % 4 in (1, 3)
        )
        if adjacent:
            rows[left][right] = rows[right][left] = 1
    require(all(sum(row) == 4 for row in rows), "motif degree drift")
    return tuple(tuple(row) for row in rows)


def forced_patterns() -> tuple[tuple[int, ...], ...]:
    """Reconstruct the fixed 87-row incidence multiset from codegrees."""

    motif = motif_adjacency()
    patterns: list[tuple[int, ...]] = [()] * 3
    patterns.extend(
        (vertex,)
        for vertex in range(MOTIF_VERTICES)
        for _ in range(4)
    )
    for left, right in combinations(range(MOTIF_VERTICES), 2):
        internal_common = sum(
            motif[left][center] * motif[right][center]
            for center in range(MOTIF_VERTICES)
        )
        target_common = 1 if motif[left][right] else 2
        multiplicity = target_common - internal_common
        require(multiplicity >= 0, "negative residual pair multiplicity")
        patterns.extend([(left, right)] * multiplicity)
    require(len(patterns) == OUTSIDE_VERTICES, "outside pattern-count drift")
    require(
        Counter(map(len, patterns)) == {0: 3, 1: 48, 2: 36},
        "outside pattern-weight drift",
    )
    return tuple(patterns)


def pattern_classes() -> tuple[tuple[int, ...], ...]:
    by_pattern: dict[tuple[int, ...], list[int]] = defaultdict(list)
    for vertex, pattern in enumerate(forced_patterns()):
        by_pattern[pattern].append(vertex)
    return tuple(tuple(vertices) for vertices in by_pattern.values())


def independent_domain_counts() -> dict[str, object]:
    """Reconstruct variables, CNF clauses, and cardinality rows."""

    patterns = forced_patterns()
    classes = pattern_classes()
    class_histogram = Counter(map(len, classes))
    require(
        class_histogram == {1: 12, 2: 12, 3: 1, 4: 12},
        "pattern-class census drift",
    )

    comparisons = sum(len(row) - 1 for row in classes)
    compared_positions = sum(
        (len(row) - 1) * (OUTSIDE_VERTICES - len(row))
        for row in classes
    )
    lex_auxiliaries = sum(
        (len(row) - 1) * (OUTSIDE_VERTICES - len(row) - 1)
        for row in classes
    )
    lex_clauses = sum(
        (len(row) - 1) * (6 * (OUTSIDE_VERTICES - len(row)) - 6)
        for row in classes
    )

    incidence = tuple(
        tuple(int(column in pattern) for column in range(MOTIF_VERTICES))
        for pattern in patterns
    )
    motif = motif_adjacency()
    right_side = tuple(
        tuple(
            2
            - incidence[row][column]
            - sum(
                incidence[row][center] * motif[center][column]
                for center in range(MOTIF_VERTICES)
            )
            for column in range(MOTIF_VERTICES)
        )
        for row in range(OUTSIDE_VERTICES)
    )
    linear_rows: set[tuple[tuple[tuple[int, int], ...], int]] = set()
    for outside in range(OUTSIDE_VERTICES):
        for motif_vertex in range(MOTIF_VERTICES):
            literals = tuple(
                sorted(
                    (min(outside, other), max(outside, other))
                    for other in range(OUTSIDE_VERTICES)
                    if other != outside and incidence[other][motif_vertex]
                )
            )
            linear_rows.add((literals, right_side[outside][motif_vertex]))

    edge_variables = OUTSIDE_VERTICES * (OUTSIDE_VERTICES - 1) // 2
    conjunction_variables = edge_variables * (OUTSIDE_VERTICES - 2)
    conjunction_clauses = 3 * conjunction_variables
    exact_rows = len(linear_rows) + OUTSIDE_VERTICES + 1 + edge_variables
    return {
        "outside_vertices": OUTSIDE_VERTICES,
        "motif_vertices": MOTIF_VERTICES,
        "pattern_weight_histogram": {"0": 3, "1": 48, "2": 36},
        "pattern_class_count": len(classes),
        "pattern_class_histogram": {
            str(size): class_histogram[size] for size in sorted(class_histogram)
        },
        "edge_variables": edge_variables,
        "common_conjunction_variables": conjunction_variables,
        "lex_comparisons": comparisons,
        "lex_compared_positions": compared_positions,
        "lex_auxiliary_variables": lex_auxiliaries,
        "total_variables": edge_variables + conjunction_variables + lex_auxiliaries,
        "conjunction_cnf_clauses": conjunction_clauses,
        "lex_cnf_clauses": lex_clauses,
        "total_cnf_clauses": conjunction_clauses + lex_clauses,
        "distinct_linear_incidence_rows": len(linear_rows),
        "degree_rows": OUTSIDE_VERTICES,
        "branch_rows": 1,
        "outside_pair_rows": edge_variables,
        "exact_cardinality_rows": exact_rows,
        "native_atmost_constraints": 2 * exact_rows,
    }


def literal_value(literal: int, assignment: dict[int, bool]) -> bool:
    value = assignment[abs(literal)]
    return value if literal > 0 else not value


def lex_cnf_truth_table(max_length: int = 4) -> dict[str, object]:
    """Test the actual discovery CNF against Boolean lex order."""

    discovery = load_discovery()
    cases = 0
    for length in range(max_length + 1):
        left_ids = tuple(range(1, length + 1))
        right_ids = tuple(range(length + 1, 2 * length + 1))
        next_id = 2 * length + 1
        clauses: list[list[int]] = []

        def new_variable(_key: tuple[object, ...]) -> int:
            nonlocal next_id
            variable = next_id
            next_id += 1
            return variable

        auxiliary_count, clause_count = discovery.add_lex_leq(
            left_ids,
            right_ids,
            new_variable,
            clauses.append,
            ("independent-verifier", length),
        )
        require(clause_count == len(clauses), "reported lex clause-count drift")
        require(auxiliary_count == max(0, length - 1), "lex auxiliary-count drift")
        expected_clauses = 0 if length == 0 else 1 if length == 1 else 6 * length - 6
        require(clause_count == expected_clauses, "lex clause formula drift")
        auxiliary_ids = tuple(range(2 * length + 1, next_id))

        for left in itertools.product((False, True), repeat=length):
            for right in itertools.product((False, True), repeat=length):
                base = dict(zip(left_ids + right_ids, left + right))
                satisfiable = False
                for auxiliary in itertools.product(
                    (False, True), repeat=auxiliary_count
                ):
                    assignment = base | dict(zip(auxiliary_ids, auxiliary))
                    if all(
                        any(literal_value(literal, assignment) for literal in clause)
                        for clause in clauses
                    ):
                        satisfiable = True
                        break
                require(
                    satisfiable == (left <= right),
                    f"lex CNF mismatch at length {length}: {left}, {right}",
                )
                cases += 1
    return {
        "max_vector_length_exhaustively_checked": max_length,
        "base_vector_pairs_checked": cases,
        "equivalent_to_boolean_lex_leq": True,
        "generic_clause_invariant": (
            "prefix auxiliaries are biconditionals for equality of all "
            "preceding positions"
        ),
    }


def adjacency_from_mask(order: int, mask: int) -> tuple[tuple[int, ...], ...]:
    rows = [[0] * order for _ in range(order)]
    for bit, (left, right) in enumerate(combinations(range(order), 2)):
        if mask & (1 << bit):
            rows[left][right] = rows[right][left] = 1
    return tuple(tuple(row) for row in rows)


def relabel(
    adjacency: tuple[tuple[int, ...], ...],
    new_to_old: tuple[int, ...],
) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(adjacency[new_to_old[left]][new_to_old[right]] for right in range(len(adjacency)))
        for left in range(len(adjacency))
    )


def external_rows_sorted(
    adjacency: tuple[tuple[int, ...], ...],
    classes: tuple[tuple[int, ...], ...],
) -> bool:
    for row_class in classes:
        columns = tuple(
            column
            for column in range(len(adjacency))
            if column not in row_class
        )
        rows = tuple(
            tuple(adjacency[vertex][column] for column in columns)
            for vertex in row_class
        )
        if any(rows[index] > rows[index + 1] for index in range(len(rows) - 1)):
            return False
    return True


def cross_class_potential(
    adjacency: tuple[tuple[int, ...], ...],
    classes: tuple[tuple[int, ...], ...],
) -> int:
    order = len(adjacency)
    class_of = {
        vertex: class_index
        for class_index, row_class in enumerate(classes)
        for vertex in row_class
    }
    weights = tuple(1 << (order - 1 - vertex) for vertex in range(order))
    return sum(
        adjacency[left][right] * weights[left] * weights[right]
        for left, right in combinations(range(order), 2)
        if class_of[left] != class_of[right]
    )


def shared_potential_audit() -> dict[str, object]:
    """Check the theorem's arithmetic and exhaustive small colored orbits."""

    actual_classes = pattern_classes()
    weights = tuple(1 << (OUTSIDE_VERTICES - 1 - vertex) for vertex in range(OUTSIDE_VERTICES))
    superincreasing_checks = 0
    for row_class in actual_classes:
        outside = tuple(vertex for vertex in range(OUTSIDE_VERTICES) if vertex not in row_class)
        for position, vertex in enumerate(outside):
            require(
                weights[vertex] > sum(weights[later] for later in outside[position + 1 :]),
                "external-column weights are not superincreasing",
            )
            superincreasing_checks += 1

    small_partitions = (
        ((0, 1), (2, 3, 4)),
        ((0, 2), (1, 3, 4)),
    )
    graph_orbits_checked = 0
    minimizing_labelings_checked = 0
    for classes in small_partitions:
        class_permutations = tuple(
            tuple(permutations(row_class)) for row_class in classes
        )
        group_elements: list[tuple[int, ...]] = []
        for choices in itertools.product(*class_permutations):
            mapping = list(range(5))
            for row_class, image in zip(classes, choices):
                for new, old in zip(row_class, image):
                    mapping[new] = old
            group_elements.append(tuple(mapping))
        for mask in range(1 << 10):
            graph = adjacency_from_mask(5, mask)
            orbit = tuple(relabel(graph, element) for element in group_elements)
            minimum = min(cross_class_potential(member, classes) for member in orbit)
            minimizers = tuple(
                member
                for member in orbit
                if cross_class_potential(member, classes) == minimum
            )
            require(
                all(external_rows_sorted(member, classes) for member in minimizers),
                "a shared-potential minimizer violates simultaneous row lex",
            )
            graph_orbits_checked += 1
            minimizing_labelings_checked += len(minimizers)

    return {
        "potential": "sum_{cross-class {i,j}} D_ij 2^(86-i) 2^(86-j)",
        "actual_external_superincreasing_checks": superincreasing_checks,
        "small_colored_graphs_exhaustively_checked": graph_orbits_checked,
        "small_minimizing_labelings_checked": minimizing_labelings_checked,
        "all_minimizers_simultaneously_row_lex": True,
        "formal_swap_identity": (
            "Delta=(w_i-w_j) sum_{k outside C} w_k(D_jk-D_ik)"
        ),
        "formal_conclusion": (
            "the first external differing column controls Delta; an inversion "
            "would lower the one shared potential"
        ),
        "within_class_columns_omitted": True,
        "target_automorphism_assumed": False,
    }


def x0_branch_audit() -> dict[str, object]:
    """Exhaust all labelled graphs on X0 and their invariant edge counts."""

    pairs = tuple(combinations(range(3), 2))
    census: Counter[int] = Counter()
    permutation_checks = 0
    for mask in range(1 << len(pairs)):
        edges = {
            pair for bit, pair in enumerate(pairs) if mask & (1 << bit)
        }
        census[len(edges)] += 1
        for permutation in permutations(range(3)):
            image = {
                tuple(sorted((permutation[left], permutation[right])))
                for left, right in edges
            }
            require(len(image) == len(edges), "X0 edge count is not invariant")
            permutation_checks += 1
    require(census == {0: 1, 1: 3, 2: 3, 3: 1}, "X0 branch census drift")
    return {
        "labelled_graphs_checked": 8,
        "permutation_checks": permutation_checks,
        "edge_count_census": {str(value): census[value] for value in range(4)},
        "branches": [0, 1, 2, 3],
        "partition_is_complete": True,
        "canonical_labeling_fixed": False,
        "compatible_with_shared_potential_minimization": True,
    }


def archived_run_audit() -> dict[str, object]:
    bounded = json.loads(
        (DISCOVERY / "bounded-results.json").read_text(encoding="utf-8")
    )
    manifest_hashes = {
        row["path"]: row["sha256"]
        for row in verify_discovery_manifest()["entries"]
    }
    rows: list[dict[str, object]] = []
    for branch in range(4):
        relative = (
            f"attempts/wave110-c4boxk3-symmetry-sat/raw-logs/"
            f"wave110-branch{branch}-45s.json"
        )
        path = REPOSITORY / relative
        actual_hash = sha256(path)
        record = json.loads(path.read_text(encoding="utf-8"))
        summary = bounded["runs"][branch]
        require(manifest_hashes[relative] == actual_hash, "raw-log manifest mismatch")
        require(summary["raw_log_sha256"] == actual_hash, "bounded-result hash mismatch")
        require(record["branch_eX0"] == branch, "raw-log branch drift")
        require(record["claim_label"] == "UNKNOWN", "timeout label inflation")
        require(record["result"] == "UNKNOWN_TIMEOUT", "bounded result drift")
        require(record["timed_out"] is True, "timeout flag drift")
        require(
            record["free_memory_fraction_before"] >= record["ram_build_floor"],
            "archived run began below RAM build floor",
        )
        require(
            record["free_memory_fraction_after"] >= record["ram_required_reserve"],
            "archived run ended below RAM reserve",
        )
        require(record["reserve_preserved_after_run"] is True, "RAM reserve flag drift")
        rows.append(
            {
                "branch_eX0": branch,
                "sha256": actual_hash,
                "result": record["result"],
                "elapsed_seconds": record["elapsed_seconds"],
                "free_memory_fraction_before": record["free_memory_fraction_before"],
                "free_memory_fraction_after": record["free_memory_fraction_after"],
            }
        )
    return {
        "runs": rows,
        "all_hashes_match_manifest_and_census": True,
        "all_statuses": "UNKNOWN_TIMEOUT",
        "minimum_archived_free_fraction": min(
            min(
                float(row["free_memory_fraction_before"]),
                float(row["free_memory_fraction_after"]),
            )
            for row in rows
        ),
        "archive_evidence_boundary": (
            "hashes authenticate the preserved JSON bytes; RAM values are "
            "self-reported telemetry, independently checked again on rerun"
        ),
    }


def rerun_audit() -> dict[str, object]:
    """Check the verifier's fresh four-branch replay."""

    expected = independent_domain_counts()
    rows: list[dict[str, object]] = []
    for branch in range(4):
        path = PACKAGE / f"rerun-branch{branch}-45s.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        require(record["branch_eX0"] == branch, "rerun branch drift")
        require(record["claim_label"] == "UNKNOWN", "rerun label inflation")
        require(record["result"] == "UNKNOWN_TIMEOUT", "rerun result drift")
        require(record["timed_out"] is True, "rerun timeout flag drift")
        require(
            record["total_variables"] == expected["total_variables"],
            "rerun variable-count drift",
        )
        require(
            record["total_cnf_clauses_submitted"]
            == expected["total_cnf_clauses"],
            "rerun CNF-count drift",
        )
        require(
            record["native_atmost_constraints_submitted"]
            == expected["native_atmost_constraints"],
            "rerun cardinality-count drift",
        )
        require(
            record["free_memory_fraction_before"] >= 0.20,
            "rerun began below build floor",
        )
        require(
            record["free_memory_fraction_after"] >= 0.15,
            "rerun ended below required RAM reserve",
        )
        rows.append(
            {
                "branch_eX0": branch,
                "sha256": sha256(path),
                "result": record["result"],
                "elapsed_seconds": record["elapsed_seconds"],
                "free_memory_fraction_before": record["free_memory_fraction_before"],
                "free_memory_fraction_after": record["free_memory_fraction_after"],
            }
        )
    return {
        "runs": rows,
        "all_statuses": "UNKNOWN_TIMEOUT",
        "all_submission_counts_match": True,
        "minimum_free_fraction": min(
            min(
                float(row["free_memory_fraction_before"]),
                float(row["free_memory_fraction_after"]),
            )
            for row in rows
        ),
        "required_minimum_free_fraction": 0.15,
    }


def verification_results() -> dict[str, object]:
    return {
        "format": "wave110-independent-verification-v1",
        "claim_label": "VERIFIED",
        "verdict": "VERIFIED_WITH_EVIDENCE_BOUNDARY",
        "scope": (
            "conditional C4 box K3 motif-extension encoding, lex CNF, "
            "same-pattern row-lex completeness, count reconstruction, "
            "X0 branch partition, and bounded UNKNOWN chronology"
        ),
        "input_freeze": verify_discovery_manifest(),
        "domain_counts": independent_domain_counts(),
        "lex_cnf": lex_cnf_truth_table(),
        "shared_potential": shared_potential_audit(),
        "x0_branch_partition": x0_branch_audit(),
        "archived_runs": archived_run_audit(),
        "fresh_reruns": rerun_audit(),
        "status_wall": {
            "conditional_encoding_verified": True,
            "symmetry_theorem_verified": True,
            "motif_extendibility": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "graph_claim": False,
            "unsat_claim": False,
            "novelty_claim": False,
        },
    }


def main() -> None:
    print(json.dumps(verification_results(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
