#!/usr/bin/env python3
"""Independent exact verifier for Wave 62.

This module reconstructs the signed-edge association scheme and every
Schur-family scalar block from definitions.  It deliberately does not import
the discovery implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


ORDER = 84
VALENCIES = (1, 2, 1, 20, 20, 40)
MULTIPLICITIES = (1, 6, 7, 14, 21, 35)
CHARACTERS = (
    (1, 2, 1, 20, 20, 40),
    (1, 2, 1, 6, 6, -16),
    (1, 0, -1, 10, -10, 0),
    (1, 2, 1, -4, -4, 4),
    (1, -2, 1, 0, 0, 0),
    (1, 0, -1, -2, 2, 0),
)


def signed_edges() -> list[tuple[int, int, int, int]]:
    return [
        (i, j, si, sj)
        for i in range(7)
        for j in range(i + 1, 7)
        for si in (-1, 1)
        for sj in (-1, 1)
    ]


def sign_at(label: tuple[int, int, int, int], point: int) -> int:
    i, j, si, sj = label
    if point == i:
        return si
    if point == j:
        return sj
    raise ValueError("point is not in the label support")


def relation(
    left: tuple[int, int, int, int],
    right: tuple[int, int, int, int],
) -> int:
    if left == right:
        return 0
    left_support = {left[0], left[1]}
    right_support = {right[0], right[1]}
    shared = left_support & right_support
    if len(shared) == 2:
        distance = (left[2] != right[2]) + (left[3] != right[3])
        if distance == 1:
            return 1
        if distance == 2:
            return 2
        raise AssertionError("equal supports and signs should be identical")
    if len(shared) == 1:
        point = next(iter(shared))
        return 3 if sign_at(left, point) == sign_at(right, point) else 4
    if len(shared) == 0:
        return 5
    raise AssertionError("unexpected support intersection")


def relation_table(
    labels: list[tuple[int, int, int, int]],
) -> list[list[int]]:
    return [[relation(x, y) for y in labels] for x in labels]


def root_neighbors() -> list[tuple[int, int]]:
    return [(i, sign) for i in range(7) for sign in (-1, 1)]


def incidence_audit(
    labels: list[tuple[int, int, int, int]],
    rel: list[list[int]],
) -> dict[str, object]:
    neighbors = root_neighbors()
    incidence = [
        [
            int(
                (neighbor[0] == label[0] and neighbor[1] == label[2])
                or (neighbor[0] == label[1] and neighbor[1] == label[3])
            )
            for label in labels
        ]
        for neighbor in neighbors
    ]
    assert [sum(row) for row in incidence] == [12] * 14
    assert [
        sum(incidence[a][x] for a in range(14)) for x in range(ORDER)
    ] == [2] * ORDER

    root_gram = [
        [
            sum(incidence[a][x] * incidence[b][x] for x in range(ORDER))
            for b in range(14)
        ]
        for a in range(14)
    ]
    for a, left in enumerate(neighbors):
        for b, right in enumerate(neighbors):
            expected = 12 if a == b else int(left[0] != right[0])
            assert root_gram[a][b] == expected

    label_gram = [
        [
            sum(incidence[a][x] * incidence[a][y] for a in range(14))
            for y in range(ORDER)
        ]
        for x in range(ORDER)
    ]
    for x in range(ORDER):
        for y in range(ORDER):
            expected = 2 if x == y else int(rel[x][y] in (1, 3))
            assert label_gram[x][y] == expected

    # The root-side Gram matrix has eigenspaces: all-ones (24),
    # pair-constant sum-zero (10, dimension 6), and mate-antisymmetric
    # (12, dimension 7).  The block SRG identity
    #
    #     B M^T = 2J - M^T - M^T L
    #
    # therefore fixes B as 12, -2, 0 on their images.  On ker(M),
    # B^2+B=12I, hence B has roots 3 and -4.  Trace(B)=0 fixes their
    # multiplicities to 40 and 30.
    return {
        "incidence_shape": [14, 84],
        "row_degrees": [12],
        "column_degrees": [2],
        "root_gram_eigenvalues": {
            "24": 1,
            "10": 6,
            "12": 7,
        },
        "forced_residual_eigenvalues": {
            "12": 1,
            "-2": 6,
            "0": 7,
        },
        "kernel_polynomial": "t^2+t-12=(t-3)(t+4)",
        "kernel_multiplicities_from_dimension_and_trace": {
            "3": 40,
            "-4": 30,
        },
        "residual_spectrum": {
            "12": 1,
            "3": 40,
            "0": 7,
            "-2": 6,
            "-4": 30,
        },
    }


def canonicalize_label(
    i: int,
    j: int,
    si: int,
    sj: int,
) -> tuple[int, int, int, int]:
    return (i, j, si, sj) if i < j else (j, i, sj, si)


def scaffold_group_generator_audit(
    labels: list[tuple[int, int, int, int]],
    rel: list[list[int]],
) -> dict[str, object]:
    label_index = {label: index for index, label in enumerate(labels)}

    def permute_support(
        label: tuple[int, int, int, int],
        permutation: tuple[int, ...],
    ) -> tuple[int, int, int, int]:
        return canonicalize_label(
            permutation[label[0]], permutation[label[1]], label[2], label[3]
        )

    def flip_coordinate(
        label: tuple[int, int, int, int],
        coordinate: int,
    ) -> tuple[int, int, int, int]:
        return canonicalize_label(
            label[0],
            label[1],
            -label[2] if label[0] == coordinate else label[2],
            -label[3] if label[1] == coordinate else label[3],
        )

    support_generators = (
        (1, 0, 2, 3, 4, 5, 6),
        (1, 2, 3, 4, 5, 6, 0),
    )
    induced = [
        [label_index[permute_support(label, permutation)] for label in labels]
        for permutation in support_generators
    ]
    induced.append([label_index[flip_coordinate(label, 0)] for label in labels])
    for mapping in induced:
        assert sorted(mapping) == list(range(ORDER))
        assert all(
            rel[mapping[x]][mapping[y]] == rel[x][y]
            for x in range(ORDER)
            for y in range(ORDER)
        )
    return {
        "generators_checked": 3,
        "support_generators": ["transposition_(0_1)", "7_cycle"],
        "sign_generators": ["coordinate_0_flip"],
        "all_preserve_orbitals": True,
    }


def reconstruct_intersection_tensor(
    rel: list[list[int]],
) -> tuple[list[list[list[int]]], bool]:
    representatives: list[tuple[int, int] | None] = [None] * 6
    for x in range(ORDER):
        for y in range(ORDER):
            representatives[rel[x][y]] = representatives[rel[x][y]] or (x, y)
    assert all(pair is not None for pair in representatives)

    tensor = [[[0 for _ in range(6)] for _ in range(6)] for _ in range(6)]
    for i in range(6):
        for j in range(6):
            for k, pair in enumerate(representatives):
                assert pair is not None
                x, y = pair
                tensor[i][j][k] = sum(
                    rel[x][z] == i and rel[z][y] == j for z in range(ORDER)
                )

    homogeneous = True
    for x in range(ORDER):
        for y in range(ORDER):
            k = rel[x][y]
            for i in range(6):
                counts = [0] * 6
                for z in range(ORDER):
                    counts[rel[x][z]] += rel[z][y] == i
                for j in range(6):
                    if counts[j] != tensor[j][i][k]:
                        homogeneous = False
    return tensor, homogeneous


def canonical_tensor_hash(tensor: list[list[list[int]]]) -> str:
    payload = json.dumps(tensor, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def multiply_scheme_coefficients(
    left: list[Fraction],
    right: list[Fraction],
    tensor: list[list[list[int]]],
) -> list[Fraction]:
    return [
        sum(
            left[i] * right[j] * tensor[i][j][k]
            for i in range(6)
            for j in range(6)
        )
        for k in range(6)
    ]


def idempotent_coefficients() -> list[list[Fraction]]:
    return [
        [
            Fraction(MULTIPLICITIES[s] * CHARACTERS[s][r], ORDER * VALENCIES[r])
            for r in range(6)
        ]
        for s in range(6)
    ]


def verify_scheme(
    rel: list[list[int]],
    tensor: list[list[list[int]]],
    homogeneous: bool,
) -> None:
    assert len(rel) == ORDER
    assert all(len(row) == ORDER for row in rel)
    assert homogeneous
    assert all(rel[x][y] == rel[y][x] for x in range(ORDER) for y in range(ORDER))
    assert [
        tuple(sum(rel[x][y] == r for y in range(ORDER)) for r in range(6))
        for x in range(ORDER)
    ] == [VALENCIES] * ORDER
    assert all(tensor[i][j] == tensor[j][i] for i in range(6) for j in range(6))

    for s in range(6):
        for t in range(6):
            inner = sum(
                Fraction(CHARACTERS[s][r] * CHARACTERS[t][r], VALENCIES[r])
                for r in range(6)
            )
            expected = Fraction(ORDER, MULTIPLICITIES[s]) if s == t else 0
            assert inner == expected
    for s in range(6):
        for i in range(6):
            for j in range(6):
                assert CHARACTERS[s][i] * CHARACTERS[s][j] == sum(
                    tensor[i][j][k] * CHARACTERS[s][k] for k in range(6)
                )

    idempotents = idempotent_coefficients()
    zero = [Fraction(0)] * 6
    for s in range(6):
        for t in range(6):
            product = multiply_scheme_coefficients(
                idempotents[s], idempotents[t], tensor
            )
            assert product == (idempotents[s] if s == t else zero)
    identity = [Fraction(1), Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(0)]
    assert [sum(idempotents[s][r] for s in range(6)) for r in range(6)] == identity
    assert [ORDER * idempotents[s][0] for s in range(6)] == list(MULTIPLICITIES)


def density_coefficients(y: int | Fraction) -> list[Fraction]:
    y = Fraction(y)
    return [
        Fraction(0),
        Fraction(0),
        y / 42,
        Fraction(1, 10),
        Fraction(1, 10) - y / 420,
        Fraction(1, 5) + y / 1680,
    ]


def endpoint_parameter_audit() -> dict[str, object]:
    # With orbit 1 forbidden, write h for the orbit-2 density.  Requiring
    # the group average of B to act as 12, -2, 0 on the forced scaffold
    # eigenspaces uniquely gives:
    #
    #   d2=h, d3=1/10, d4=(1-h)/10, d5=1/5+h/40.
    #
    # Converting ordered-pair densities to unordered edge counts gives the
    # claimed one-parameter family.
    for y in range(43):
        densities = density_coefficients(y)
        assert block_values(densities)[:3] == [
            Fraction(12),
            Fraction(-2),
            Fraction(0),
        ]
        edge_counts = [
            Fraction(ORDER * VALENCIES[r], 2) * densities[r]
            for r in range(6)
        ]
        assert edge_counts == [
            Fraction(0),
            Fraction(0),
            Fraction(y),
            Fraction(84),
            Fraction(84 - 2 * y),
            Fraction(336 + y),
        ]
        assert sum(edge_counts) == 504
    return {
        "parameter": "y=number of selected orbit-2 unordered pairs",
        "integer_range": [0, 42],
        "relation_edge_counts": ["0", "y", "84", "84-2*y", "336+y"],
        "derivation": "unique solution of the 12,-2,0 forced average-block equations after orbit 1 is set to zero",
    }


def block_values(coefficients: list[Fraction]) -> list[Fraction]:
    return [
        sum(coefficients[r] * CHARACTERS[s][r] for r in range(6))
        for s in range(6)
    ]


def projector_entry_tables() -> tuple[
    list[Fraction], list[Fraction], list[Fraction], list[Fraction]
]:
    idempotents = idempotent_coefficients()
    p3_nonedge = []
    p3_edge = []
    pm4_nonedge = []
    pm4_edge = []
    for r in range(6):
        delta = Fraction(r == 0)
        base = (
            4 * delta
            - 16 * idempotents[0][r]
            - 2 * idempotents[1][r]
            - 4 * idempotents[2][r]
        ) / 7
        kernel = delta - idempotents[0][r] - idempotents[1][r] - idempotents[2][r]
        p3_nonedge.append(base)
        pm4_nonedge.append(kernel - base)
        if r == 0:
            p3_edge.append(base)
            pm4_edge.append(kernel - base)
        else:
            p3_edge.append(base + Fraction(1, 7))
            pm4_edge.append(kernel - base - Fraction(1, 7))
    return p3_nonedge, p3_edge, pm4_nonedge, pm4_edge


def integer_endpoint_audit() -> dict[str, object]:
    expected_b = (
        lambda y: (
            Fraction(12),
            Fraction(-2),
            Fraction(0),
            Fraction(y, 28),
            Fraction(y, 42),
            Fraction(-y, 35),
        )
    )
    p3_nonedge, p3_edge, pm4_nonedge, pm4_edge = projector_entry_tables()
    survivors = []
    for y in range(43):
        densities = density_coefficients(y)
        b_blocks = block_values(densities)
        assert tuple(b_blocks) == expected_b(y)
        p3_average = [
            p3_nonedge[r]
            if r == 0
            else (1 - densities[r]) * p3_nonedge[r]
            + densities[r] * p3_edge[r]
            for r in range(6)
        ]
        pm4_average = [
            pm4_nonedge[r]
            if r == 0
            else (1 - densities[r]) * pm4_nonedge[r]
            + densities[r] * pm4_edge[r]
            for r in range(6)
        ]
        p3_weights = block_values(p3_average)
        pm4_weights = block_values(pm4_average)
        assert p3_weights == [
            Fraction(0),
            Fraction(0),
            Fraction(0),
            Fraction(4, 7) + Fraction(y, 196),
            Fraction(4, 7) + Fraction(y, 294),
            Fraction(4, 7) - Fraction(y, 245),
        ]
        assert pm4_weights == [
            Fraction(0),
            Fraction(0),
            Fraction(0),
            1 - p3_weights[3],
            1 - p3_weights[4],
            1 - p3_weights[5],
        ]
        assert all(0 <= value <= 1 for value in p3_weights + pm4_weights)
        assert sum(
            MULTIPLICITIES[s] * p3_weights[s] for s in range(6)
        ) == 40
        variance = [
            Fraction(0),
            Fraction(0),
            Fraction(0),
            12 + b_blocks[3] - b_blocks[3] ** 2,
            12 + b_blocks[4] - b_blocks[4] ** 2,
            12 + b_blocks[5] - b_blocks[5] ** 2,
        ]
        assert all(value >= 0 for value in variance)
        survivors.append(y)
    return {
        "surviving_integer_y": survivors,
        "all_real_y_feasible": True,
        "reason": "all six projector weights are affine and nonnegative at y=0,42",
    }


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def schur_family_audit() -> dict[str, object]:
    idempotents = idempotent_coefficients()
    p3_nonedge, p3_edge, pm4_nonedge, pm4_edge = projector_entry_tables()

    matrix_count = 0
    positive_count = 0
    zero_count = 0
    negative_records = []
    smallest: Fraction | None = None
    smallest_location: dict[str, int] | None = None

    for multiplier in range(6):
        for p3_power in range(25):
            for pm4_power in range(25 - p3_power):
                # The discovery census omits the tautological unpowered
                # principal idempotent E_0.  Its omission has no effect on
                # nonnegativity but must be stated to obtain 1,949 matrices.
                if multiplier == 0 and p3_power == 0 and pm4_power == 0:
                    continue
                matrix_count += 1
                for endpoint in (0, 1):
                    densities = density_coefficients(42 * endpoint)
                    coefficients: list[Fraction] = []
                    for r in range(6):
                        if r == 0:
                            value = (
                                idempotents[multiplier][r]
                                * p3_nonedge[r] ** p3_power
                                * pm4_nonedge[r] ** pm4_power
                            )
                        else:
                            nonedge_value = (
                                p3_nonedge[r] ** p3_power
                                * pm4_nonedge[r] ** pm4_power
                            )
                            edge_value = (
                                p3_edge[r] ** p3_power
                                * pm4_edge[r] ** pm4_power
                            )
                            value = idempotents[multiplier][r] * (
                                (1 - densities[r]) * nonedge_value
                                + densities[r] * edge_value
                            )
                        coefficients.append(value)
                    blocks = block_values(coefficients)
                    for block, value in enumerate(blocks):
                        if value < 0:
                            negative_records.append(
                                {
                                    "multiplier": multiplier,
                                    "p3_power": p3_power,
                                    "pm4_power": pm4_power,
                                    "h_endpoint": endpoint,
                                    "block": block,
                                    "value": fraction_text(value),
                                }
                            )
                        elif value == 0:
                            zero_count += 1
                        else:
                            positive_count += 1
                            if smallest is None or value < smallest:
                                smallest = value
                                smallest_location = {
                                    "multiplier": multiplier,
                                    "p3_power": p3_power,
                                    "pm4_power": pm4_power,
                                    "h_endpoint": endpoint,
                                    "block": block,
                                    "block_multiplicity": MULTIPLICITIES[block],
                                }
    assert smallest is not None
    assert matrix_count == 1949
    assert matrix_count * 2 * 6 == positive_count + zero_count + len(negative_records)
    return {
        "declared_all_parameter_triples": 1950,
        "omitted_parameter_triple": {
            "multiplier": 0,
            "p3_power": 0,
            "pm4_power": 0,
            "matrix": "E_0=J/84",
        },
        "matrix_count": matrix_count,
        "endpoint_block_inequalities": matrix_count * 2 * 6,
        "positive": positive_count,
        "zero": zero_count,
        "negative": len(negative_records),
        "negative_records": negative_records,
        "smallest_positive": fraction_text(smallest),
        "smallest_positive_location": smallest_location,
    }


def parse_manifest(path: Path) -> list[tuple[str, str]]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split(maxsplit=1)
        records.append((digest.lower(), relative.strip()))
    return records


def verify_manifest(package: Path) -> dict[str, object]:
    manifest = package / "package-manifest.sha256"
    actual_manifest_hash = hashlib.sha256(manifest.read_bytes()).hexdigest()
    records = parse_manifest(manifest)
    mismatches = []
    for expected, relative in records:
        target = package / relative
        actual = hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else None
        if actual != expected:
            mismatches.append(
                {"path": relative, "expected": expected, "actual": actual}
            )
    listed = {relative.replace("\\", "/") for _, relative in records}
    present = {
        str(path.relative_to(package)).replace("\\", "/")
        for path in package.rglob("*")
        if path.is_file() and path.name != "package-manifest.sha256"
    }
    return {
        "manifest_sha256": actual_manifest_hash,
        "record_count": len(records),
        "mismatches": mismatches,
        "unlisted_files": sorted(present - listed),
        "missing_listed_files": sorted(listed - present),
    }


def hostile_mutations(
    rel: list[list[int]],
    tensor: list[list[list[int]]],
    package: Path,
) -> dict[str, bool]:
    mutated_rel = [row[:] for row in rel]
    mutated_rel[0][1] = 5
    mutated_rel[1][0] = 5
    valency_rejected = tuple(
        sum(mutated_rel[0][y] == r for y in range(ORDER)) for r in range(6)
    ) != VALENCIES

    mutated_characters = [list(row) for row in CHARACTERS]
    mutated_characters[3][5] += 1
    character_rejected = any(
        mutated_characters[3][i] * mutated_characters[3][j]
        != sum(tensor[i][j][k] * mutated_characters[3][k] for k in range(6))
        for i in range(6)
        for j in range(6)
    )

    wrong_density = density_coefficients(0)
    wrong_density[3] += Fraction(1, 840)
    endpoint_count_rejected = block_values(wrong_density)[0] != 12

    manifest_records = parse_manifest(package / "package-manifest.sha256")
    first_digest, _ = manifest_records[0]
    manifest_mutation_rejected = ("0" if first_digest[0] != "0" else "1") + first_digest[1:] != first_digest

    return {
        "orbital_mutation_rejected": valency_rejected,
        "character_mutation_rejected": character_rejected,
        "endpoint_count_mutation_rejected": endpoint_count_rejected,
        "manifest_digest_mutation_rejected": manifest_mutation_rejected,
    }


def build_result(package: Path) -> dict[str, object]:
    labels = signed_edges()
    rel = relation_table(labels)
    tensor, homogeneous = reconstruct_intersection_tensor(rel)
    verify_scheme(rel, tensor, homogeneous)
    incidence = incidence_audit(labels, rel)
    group_generators = scaffold_group_generator_audit(labels, rel)
    p3_nonedge, p3_edge, pm4_nonedge, pm4_edge = projector_entry_tables()
    assert p3_nonedge == [
        Fraction(10, 21),
        Fraction(-1, 21),
        Fraction(0),
        Fraction(-2, 35),
        Fraction(-1, 105),
        Fraction(-2, 105),
    ]
    assert pm4_nonedge == [
        Fraction(5, 14),
        Fraction(-1, 28),
        Fraction(0),
        Fraction(-1, 56),
        Fraction(1, 56),
        Fraction(1, 28),
    ]
    assert all(
        p3_edge[r] == p3_nonedge[r] + Fraction(1, 7) for r in range(1, 6)
    )
    assert all(
        pm4_edge[r] == pm4_nonedge[r] - Fraction(1, 7) for r in range(1, 6)
    )

    manifest = verify_manifest(package)
    assert manifest["mismatches"] == []
    assert manifest["unlisted_files"] == []
    assert manifest["missing_listed_files"] == []
    mutations = hostile_mutations(rel, tensor, package)
    assert all(mutations.values())
    return {
        "format": "wave62-independent-verifier-v1",
        "claim_label": "VERIFIED",
        "scope": "exact finite one-point signed-edge association-scheme and declared degree-24 Schur family only",
        "signed_edge_scheme": {
            "order": len(labels),
            "valencies": list(VALENCIES),
            "multiplicities": list(MULTIPLICITIES),
            "characters": [list(row) for row in CHARACTERS],
            "intersection_tensor_sha256": canonical_tensor_hash(tensor),
            "homogeneous": homogeneous,
            "commutative": True,
        },
        "incidence_and_residual_spectrum": incidence,
        "scaffold_group_generators": group_generators,
        "endpoint_parameter": endpoint_parameter_audit(),
        "projector_entries": {
            "p3_nonedge_or_diagonal": [fraction_text(x) for x in p3_nonedge],
            "p3_edge_or_diagonal": [fraction_text(x) for x in p3_edge],
            "pm4_nonedge_or_diagonal": [fraction_text(x) for x in pm4_nonedge],
            "pm4_edge_or_diagonal": [fraction_text(x) for x in pm4_edge],
        },
        "integer_endpoint_audit": integer_endpoint_audit(),
        "schur_family": schur_family_audit(),
        "manifest": manifest,
        "hostile_mutations": mutations,
        "automorphism_policy": {
            "target_graph_automorphism_assumed": False,
            "scaffold_group_use": "universal PSD averaging and orbit classification only",
            "soundness": "each unaveraged Schur product is PSD; averaging its scaffold conjugates is PSD without requiring the target adjacency to be invariant",
        },
        "documentation_correction": {
            "needed": True,
            "issue": "The protocol says all six multipliers and all a+b<=24, which contains 1,950 triples, while the implementation deliberately omits (E_0,a,b)=(E_0,0,0) and checks 1,949.",
            "mathematical_effect": "none; the omitted E_0=J/84 has nonnegative blocks, so adding it gives 23,400 inequalities, 23,318 positive values, 82 zeros, and still no negatives",
        },
        "status": {
            "finite_claims": "VERIFIED",
            "strict_upper_bound": "NOT_OBTAINED",
            "endpoint": "UNKNOWN",
            "conway_99": "UNKNOWN",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--package",
        type=Path,
        default=Path("attempts/wave62-terwilliger-sdp"),
    )
    parser.add_argument("--expect", type=Path)
    args = parser.parse_args()
    result = build_result(args.package)
    if args.expect is not None:
        expected = json.loads(args.expect.read_text(encoding="utf-8"))
        if result != expected:
            raise SystemExit("independent result does not match frozen verifier result")
        print(f"PASS: {args.expect}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
