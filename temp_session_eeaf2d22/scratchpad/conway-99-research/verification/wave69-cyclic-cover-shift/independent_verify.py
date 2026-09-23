#!/usr/bin/env python3
"""Independent clean-room verifier for the Wave 69 cyclic-cover shift.

This module does not import or execute discovery code.  It reconstructs the
semiregular C11 quotient equations and exhausts their integer solutions.  The
label-complete search uses no residual-vertex canonicalization; a second
canonical tree is retained only as a cross-check.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterator, Sequence


V = 99
K = 14
LAMBDA = 1
MU = 2
P = 11
ORBIT_COUNT = 9
EIGEN_MULTIPLICITIES = {14: 1, 3: 54, -4: 44}


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("ascii")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def quotient_spectrum() -> dict[int, int]:
    """Use rational C11 representation dimensions to obtain 1,4,4."""

    if EIGEN_MULTIPLICITIES[3] + EIGEN_MULTIPLICITIES[-4] != V - 1:
        raise AssertionError("full spectrum dimension drift")
    if K + 3 * 54 - 4 * 44 != 0:
        raise AssertionError("full spectrum trace drift")

    # Over Q, every nontrivial irreducible C11 representation has dimension
    # Phi_11 degree 10.  The nine-dimensional permutation-fixed space contains
    # the principal vector, so the two nonprincipal fixed dimensions sum to 8.
    candidates: list[tuple[int, int]] = []
    for fixed_three in range(9):
        fixed_minus_four = 8 - fixed_three
        if (54 - fixed_three) % 10 == 0 and (44 - fixed_minus_four) % 10 == 0:
            candidates.append((fixed_three, fixed_minus_four))
    if candidates != [(4, 4)]:
        raise AssertionError(f"unexpected rational-representation cases: {candidates}")
    return {14: 1, 3: 4, -4: 4}


def nondecreasing_vectors(
    length: int,
    total: int,
    square_total: int,
    minimum: int = 0,
) -> Iterator[tuple[int, ...]]:
    """Generate all nondecreasing nonnegative integer vectors with two moments."""

    if length == 0:
        if total == 0 and square_total == 0:
            yield ()
        return
    if total < length * minimum or square_total < length * minimum * minimum:
        return

    maximum = total // length if length else 0
    for value in range(minimum, maximum + 1):
        remaining_length = length - 1
        remaining_total = total - value
        remaining_square = square_total - value * value
        if remaining_square < 0:
            break
        if remaining_length:
            if remaining_total < remaining_length * value:
                continue
            # Cauchy's inequality and the largest possible last entry give
            # fail-closed pruning of only impossible moment states.
            if remaining_total * remaining_total > remaining_length * remaining_square:
                continue
            max_square = (remaining_total - (remaining_length - 1) * value) ** 2
            max_square += (remaining_length - 1) * value * value
            if remaining_square > max_square:
                continue
        elif remaining_total or remaining_square:
            continue
        for suffix in nondecreasing_vectors(
            remaining_length, remaining_total, remaining_square, value
        ):
            yield (value,) + suffix


def derive_row_shapes() -> dict[int, tuple[tuple[int, ...], ...]]:
    shapes: dict[int, tuple[tuple[int, ...], ...]] = {}
    for diagonal in range(0, K + 1, 2):
        off_sum = K - diagonal
        off_square_sum = 34 - diagonal * diagonal - diagonal
        rows = tuple(
            nondecreasing_vectors(ORBIT_COUNT - 1, off_sum, off_square_sum)
        )
        if rows:
            shapes[diagonal] = rows
    return shapes


def derive_diagonal_cases() -> tuple[tuple[int, ...], ...]:
    trace = sum(eigenvalue * count for eigenvalue, count in quotient_spectrum().items())
    cases = []
    for count_zero in range(ORBIT_COUNT + 1):
        for count_two in range(ORBIT_COUNT - count_zero + 1):
            count_four = ORBIT_COUNT - count_zero - count_two
            if 2 * count_two + 4 * count_four == trace:
                cases.append(
                    (0,) * count_zero + (2,) * count_two + (4,) * count_four
                )
    return tuple(sorted(cases))


def multiset_permutations(values: Sequence[int]) -> Iterator[tuple[int, ...]]:
    counts = Counter(values)
    keys = sorted(counts)
    result = [0] * len(values)

    def extend(index: int) -> Iterator[tuple[int, ...]]:
        if index == len(result):
            yield tuple(result)
            return
        for key in keys:
            if not counts[key]:
                continue
            counts[key] -= 1
            result[index] = key
            yield from extend(index + 1)
            counts[key] += 1

    yield from extend(0)


def row_templates() -> dict[int, tuple[tuple[int, ...], ...]]:
    return {
        diagonal: tuple(
            sorted(
                permutation
                for shape in diagonal_shapes
                for permutation in multiset_permutations(shape)
            )
        )
        for diagonal, diagonal_shapes in derive_row_shapes().items()
    }


def prefix_indices(
    diagonal: Sequence[int],
) -> tuple[dict[tuple[int, ...], tuple[tuple[int, ...], ...]], ...]:
    templates = row_templates()
    all_indices = []
    for vertex, diagonal_entry in enumerate(diagonal):
        buckets: defaultdict[tuple[int, ...], list[tuple[int, ...]]] = defaultdict(list)
        for off_diagonal in templates[diagonal_entry]:
            row = (
                off_diagonal[:vertex]
                + (diagonal_entry,)
                + off_diagonal[vertex:]
            )
            buckets[row[:vertex]].append(row)
        all_indices.append(
            {
                prefix: tuple(sorted(rows))
                for prefix, rows in sorted(buckets.items())
            }
        )
    return tuple(all_indices)


def residual_signatures_are_canonical(
    rows: Sequence[Sequence[int]],
    candidate: Sequence[int],
    diagonal: Sequence[int],
    vertex: int,
) -> bool:
    """Discovery-compatible optional canonical augmentation.

    This predicate is never used by the label-complete proof tree.
    """

    for diagonal_entry in sorted(set(diagonal)):
        residual_vertices = [
            index
            for index in range(vertex + 1, ORBIT_COUNT)
            if diagonal[index] == diagonal_entry
        ]
        signatures = [
            tuple(row[index] for row in rows) + (candidate[index],)
            for index in residual_vertices
        ]
        if signatures != sorted(signatures):
            return False
    return True


def string_counter(counter: Counter[object]) -> dict[str, int]:
    return {str(key): counter[key] for key in sorted(counter, key=str)}


def exhaust_diagonal(
    diagonal: Sequence[int], *, canonical: bool
) -> dict[str, object]:
    """Exhaust all labeled rows consistent with a sorted diagonal."""

    indices = prefix_indices(diagonal)
    selected_rows: list[tuple[int, ...]] = []
    nodes = 0
    solutions = 0
    branches: Counter[int] = Counter()
    raw_candidates: Counter[int] = Counter()
    canonical_rejections: Counter[int] = Counter()
    equation_rejections: Counter[int] = Counter()
    leaves: Counter[str] = Counter()
    mode = "canonical" if canonical else "unpruned"
    transcript = hashlib.sha256()
    transcript.update(canonical_json_bytes({"diagonal": tuple(diagonal), "mode": mode}))

    def visit(vertex: int) -> None:
        nonlocal nodes, solutions
        nodes += 1
        transcript.update(b"N")
        transcript.update(bytes((vertex,)))
        for row in selected_rows:
            transcript.update(bytes(row))

        if vertex == ORBIT_COUNT:
            solutions += 1
            leaves["solution"] += 1
            transcript.update(b"S")
            return

        required_prefix = tuple(
            selected_rows[old_vertex][vertex] for old_vertex in range(vertex)
        )
        candidates = indices[vertex].get(required_prefix, ())
        raw_candidates[vertex] += len(candidates)
        if not candidates:
            leaves[f"empty_prefix_{vertex}"] += 1
            transcript.update(b"E")
            transcript.update(bytes((vertex,)))
            return

        accepted = 0
        canonical_rejected_here = 0
        equation_rejected_here = 0
        for candidate in candidates:
            if canonical and not residual_signatures_are_canonical(
                selected_rows, candidate, diagonal, vertex
            ):
                canonical_rejected_here += 1
                continue
            valid = True
            for old_vertex, old_row in enumerate(selected_rows):
                dot = sum(
                    left * right for left, right in zip(candidate, old_row)
                )
                if dot + candidate[old_vertex] != 22:
                    valid = False
                    break
            if not valid:
                equation_rejected_here += 1
                continue
            accepted += 1
            branches[vertex] += 1
            selected_rows.append(candidate)
            visit(vertex + 1)
            selected_rows.pop()

        canonical_rejections[vertex] += canonical_rejected_here
        equation_rejections[vertex] += equation_rejected_here
        transcript.update(b"R")
        transcript.update(bytes((vertex,)))
        for value in (
            len(candidates),
            canonical_rejected_here,
            equation_rejected_here,
            accepted,
        ):
            transcript.update(value.to_bytes(8, "little"))
        if accepted == 0:
            leaves[f"no_accepted_{vertex}"] += 1

    visit(0)
    return {
        "mode": mode,
        "diagonal": list(diagonal),
        "nodes": nodes,
        "solutions": solutions,
        "branches_by_depth": string_counter(branches),
        "raw_candidates_by_depth": string_counter(raw_candidates),
        "canonical_rejections_by_depth": string_counter(canonical_rejections),
        "dot_rejections_by_depth": string_counter(equation_rejections),
        "leaves": string_counter(leaves),
        "transcript_sha256": transcript.hexdigest(),
    }


def validate_quotient(matrix: Sequence[Sequence[int]]) -> bool:
    """Directly validate a full quotient; used as a hostile leaf check."""

    if len(matrix) != ORBIT_COUNT or any(len(row) != ORBIT_COUNT for row in matrix):
        return False
    if any(value < 0 or int(value) != value for row in matrix for value in row):
        return False
    if any(matrix[i][j] != matrix[j][i] for i in range(9) for j in range(9)):
        return False
    if any(sum(row) != K for row in matrix):
        return False
    if any(matrix[i][i] % 2 for i in range(9)):
        return False
    for i in range(9):
        for j in range(9):
            lhs = sum(matrix[i][k] * matrix[k][j] for k in range(9))
            lhs += matrix[i][j]
            rhs = 12 * (i == j) + 22
            if lhs != rhs:
                return False
    return True


def abelian_group_and_fourier_audit() -> dict[str, object]:
    """Record the exact group and character argument without discovery imports."""

    divisors_of_nine = [1, 3, 9]
    sylow_11_counts = [n for n in divisors_of_nine if n % 11 == 1]
    if sylow_11_counts != [1]:
        raise AssertionError(sylow_11_counts)

    # A Sylow-3 subgroup has order 9 and is abelian.  Its conjugation image in
    # Aut(C11), of order 10, has order dividing gcd(9,10)=1.  Thus the Sylow
    # factors commute and the group is their direct product.
    group_types = ["C99", "C3xC3xC11"]
    values = {
        "outside_D": {"numerator": -18, "denominator": 7},
        "inside_D": {"numerator": 81, "denominator": 7},
    }
    if any(record["numerator"] % record["denominator"] == 0 for record in values.values()):
        raise AssertionError("Fourier value unexpectedly integral")
    return {
        "sylow_11_count": 1,
        "conjugation_image_order_divides": [9, 10],
        "conjugation_image_order": 1,
        "sylow_3_subgroup_abelian": True,
        "all_groups_of_order_99_abelian": True,
        "group_isomorphism_types": group_types,
        "character_multiplicities": {"3": 54, "-4": 44},
        "fourier_identity": "99*1_D(g)=18+7*S_X(g) for g!=identity",
        "forced_S_X_values": values,
        "algebraic_integer_contradiction": True,
        "cayley_target_status": "EXCLUDED",
    }


def load_verified_wave72(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema": "wave72-order11-independent-v1",
        "claim_label": "VERIFIED",
        "primary_conclusion": (
            "every_exact_order_11_automorphism_is_fixed_point_free"
        ),
        "fixed_free_orbit_count": 9,
    }
    for key, expected in required.items():
        if value.get(key) != expected:
            raise AssertionError(f"Wave72 prerequisite mismatch at {key}")
    if value.get("positive_nonidentity_models") != []:
        raise AssertionError("Wave72 prerequisite allows a positive fixed set")
    return {
        "path": path.as_posix(),
        "sha256": sha256_bytes(path.read_bytes()),
        "claim_label": "VERIFIED",
        "primary_conclusion": required["primary_conclusion"],
        "fixed_free_orbit_count": 9,
    }


def generate_independent_results(wave72_path: Path) -> dict[str, object]:
    spectrum = quotient_spectrum()
    shapes = derive_row_shapes()
    diagonals = derive_diagonal_cases()
    searches = {
        mode: [
            exhaust_diagonal(diagonal, canonical=(mode == "canonical"))
            for diagonal in diagonals
        ]
        for mode in ("canonical", "unpruned")
    }
    if any(
        record["solutions"]
        for records in searches.values()
        for record in records
    ):
        raise AssertionError("an integer quotient survived")
    if any(
        value
        for record in searches["unpruned"]
        for value in record["canonical_rejections_by_depth"].values()
    ):
        raise AssertionError("label-complete search used canonical pruning")

    wave72 = load_verified_wave72(wave72_path)
    result: dict[str, object] = {
        "schema": "wave69-cyclic-cover-independent-v1",
        "claim_label": "VERIFIED",
        "parameters": {"v": V, "k": K, "lambda": LAMBDA, "mu": MU},
        "semiregular_hypothesis": (
            "an exact-order-11 automorphism acts fixed-point-freely on 99 vertices"
        ),
        "srg_identity": "A^2=12*I-A+2*J",
        "quotient_identity": "Q^2+Q=12*I+22*J",
        "quotient_spectrum": {
            str(eigenvalue): count for eigenvalue, count in spectrum.items()
        },
        "quotient_trace": sum(
            eigenvalue * count for eigenvalue, count in spectrum.items()
        ),
        "row_shapes": {
            str(diagonal): [list(shape) for shape in diagonal_shapes]
            for diagonal, diagonal_shapes in shapes.items()
        },
        "row_template_counts": {
            str(diagonal): len(templates)
            for diagonal, templates in row_templates().items()
        },
        "sorted_diagonal_cases": [list(case) for case in diagonals],
        "searches": searches,
        "semiregular_quotient_candidates": 0,
        "semiregular_order11_actions": "EXCLUDED",
        "wave72_prerequisite": wave72,
        "all_order11_automorphisms": "EXCLUDED",
        "vertex_transitive_realizations": "EXCLUDED",
        "abelian_cayley_audit": abelian_group_and_fourier_audit(),
        "scope": {
            "unrestricted_conway_99": "UNKNOWN",
            "asymmetric_targets": "NOT_EXCLUDED",
            "automorphism_groups_without_order11": "NOT_EXCLUDED",
            "literature_novelty": "UNKNOWN",
        },
    }
    semantic = dict(result)
    result["semantic_sha256"] = sha256_bytes(canonical_json_bytes(semantic))
    return result


def compare_with_discovery(
    independent: dict[str, object], discovery_path: Path
) -> dict[str, object]:
    discovery = json.loads(discovery_path.read_text(encoding="ascii"))
    comparisons: list[dict[str, object]] = []
    mismatches = 0
    exact_fields = (
        ("quotient_spectrum", "quotient_eigenvalue_multiplicities"),
        ("quotient_trace", "quotient_trace"),
        ("row_shapes", "row_shapes_off_diagonal"),
        ("row_template_counts", "row_template_counts"),
        ("sorted_diagonal_cases", "sorted_diagonal_cases"),
    )
    for independent_key, discovery_key in exact_fields:
        match = independent[independent_key] == discovery[discovery_key]
        comparisons.append(
            {
                "kind": "mathematics",
                "independent_key": independent_key,
                "discovery_key": discovery_key,
                "match": match,
            }
        )
        mismatches += not match

    for mode in ("canonical", "unpruned"):
        independent_records = independent["searches"][mode]
        discovery_records = discovery["searches"][mode]
        for independent_record, discovery_record in zip(
            independent_records, discovery_records, strict=True
        ):
            keys = (
                "diagonal",
                "nodes",
                "solutions",
                "branches_by_depth",
                "raw_candidates_by_depth",
                "canonical_rejections_by_depth",
                "dot_rejections_by_depth",
                "leaves",
                "transcript_sha256",
            )
            differences = [
                key
                for key in keys
                if independent_record[key] != discovery_record[key]
            ]
            comparisons.append(
                {
                    "kind": "search_telemetry",
                    "mode": mode,
                    "diagonal": independent_record["diagonal"],
                    "match": not differences,
                    "different_fields": differences,
                    "nodes": independent_record["nodes"],
                    "solutions": independent_record["solutions"],
                    "transcript_sha256": independent_record["transcript_sha256"],
                }
            )
            mismatches += bool(differences)

    return {
        "schema": "wave69-cyclic-cover-comparison-v1",
        "discovery_path": discovery_path.as_posix(),
        "discovery_sha256": sha256_bytes(discovery_path.read_bytes()),
        "comparisons": comparisons,
        "comparison_count": len(comparisons),
        "mismatches": mismatches,
        "status": "PASS" if mismatches == 0 else "FAIL",
        "independence_note": (
            "The verifier does not import or execute discovery code. "
            "Comparison reads only the sealed discovery JSON after independent generation."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--discovery-results", required=True, type=Path)
    parser.add_argument("--comparison-output", required=True, type=Path)
    parser.add_argument("--wave72-results", required=True, type=Path)
    args = parser.parse_args()

    independent = generate_independent_results(args.wave72_results)
    comparison = compare_with_discovery(independent, args.discovery_results)
    if comparison["mismatches"]:
        raise AssertionError(comparison)
    args.output.write_bytes(canonical_json_bytes(independent))
    args.comparison_output.write_bytes(canonical_json_bytes(comparison))
    print(
        canonical_json_bytes(
            {
                "status": "PASS",
                "semantic_sha256": independent["semantic_sha256"],
                "comparison_mismatches": comparison["mismatches"],
                "unpruned_nodes": sum(
                    record["nodes"] for record in independent["searches"]["unpruned"]
                ),
                "canonical_nodes": sum(
                    record["nodes"] for record in independent["searches"]["canonical"]
                ),
                "quotient_candidates": independent["semiregular_quotient_candidates"],
            }
        ).decode("ascii"),
        end="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
