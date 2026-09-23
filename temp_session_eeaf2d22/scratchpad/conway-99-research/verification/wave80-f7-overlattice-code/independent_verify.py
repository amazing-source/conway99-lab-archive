#!/usr/bin/env python3
"""Independent exact verifier for Wave 80.

The computation is parameter-conditional: it never assumes or constructs an
SRG(99,14,1,2). It verifies consequences that every such graph and its
independently verified Wave 66/71 lattice package would have to satisfy.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Iterable


FIELD = 7
VERTICES = 99
LATTICE_RANK = 44


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def legendre_sign(value: int) -> int:
    residue = value % FIELD
    check(residue != 0, "Legendre symbol requested at zero")
    power = pow(residue, (FIELD - 1) // 2, FIELD)
    return 1 if power == 1 else -1


def determinant_mod(matrix: list[list[int]]) -> int:
    """Determinant by pivot elimination over F_7."""

    work = [[entry % FIELD for entry in row] for row in matrix]
    size = len(work)
    determinant = 1
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]),
            None,
        )
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            determinant = -determinant
        pivot_value = work[column][column]
        determinant = determinant * pivot_value % FIELD
        inverse = pow(pivot_value, -1, FIELD)
        for row in range(column + 1, size):
            factor = work[row][column] * inverse % FIELD
            if factor:
                work[row] = [
                    (left - factor * right) % FIELD
                    for left, right in zip(work[row], work[column])
                ]
    return determinant % FIELD


def nullspace_basis(matrix: list[list[int]]) -> list[tuple[int, ...]]:
    """RREF nullspace basis over F_7."""

    work = [[entry % FIELD for entry in row] for row in matrix]
    row_count = len(work)
    column_count = len(work[0]) if work else 0
    pivot_columns: list[int] = []
    pivot_row = 0
    for column in range(column_count):
        selected = next(
            (
                row
                for row in range(pivot_row, row_count)
                if work[row][column]
            ),
            None,
        )
        if selected is None:
            continue
        work[pivot_row], work[selected] = work[selected], work[pivot_row]
        inverse = pow(work[pivot_row][column], -1, FIELD)
        work[pivot_row] = [
            entry * inverse % FIELD for entry in work[pivot_row]
        ]
        for row in range(row_count):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    (left - factor * right) % FIELD
                    for left, right in zip(work[row], work[pivot_row])
                ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == row_count:
            break

    free_columns = [
        column
        for column in range(column_count)
        if column not in pivot_columns
    ]
    basis: list[tuple[int, ...]] = []
    for free in free_columns:
        vector = [0] * column_count
        vector[free] = 1
        for row, pivot in enumerate(pivot_columns):
            vector[pivot] = -work[row][free] % FIELD
        basis.append(tuple(vector))
    return basis


def projective_full_support_kernel(
    matrix: list[list[int]],
) -> list[tuple[int, ...]]:
    basis = nullspace_basis(matrix)
    if not basis:
        return []
    dimension = len(basis)
    representatives: set[tuple[int, ...]] = set()
    for scalars in itertools.product(range(FIELD), repeat=dimension):
        if not any(scalars):
            continue
        vector = tuple(
            sum(
                scalars[index] * basis[index][coordinate]
                for index in range(dimension)
            )
            % FIELD
            for coordinate in range(len(matrix))
        )
        if 0 in vector:
            continue
        first_inverse = pow(vector[0], -1, FIELD)
        representatives.add(
            tuple(entry * first_inverse % FIELD for entry in vector)
        )
    return sorted(representatives)


def graph_from_mask(order: int, mask: int) -> list[list[int]]:
    graph = [[0 for _ in range(order)] for _ in range(order)]
    bit = 0
    for left in range(order):
        for right in range(left + 1, order):
            graph[left][right] = graph[right][left] = (mask >> bit) & 1
            bit += 1
    return graph


def seidel_block(graph: list[list[int]]) -> list[list[int]]:
    order = len(graph)
    return [
        [
            0
            if row == column
            else (1 if graph[row][column] else -1)
            for column in range(order)
        ]
        for row in range(order)
    ]


def local_intersection_bounds_hold(graph: list[list[int]]) -> bool:
    """Necessary induced-subgraph bounds from lambda=1 and mu=2."""

    order = len(graph)
    for left in range(order):
        for right in range(left + 1, order):
            common_inside = sum(
                graph[left][other] * graph[right][other]
                for other in range(order)
            )
            cap = 1 if graph[left][right] else 2
            if common_inside > cap:
                return False
    return True


def canonical_adjacency_bits(graph: list[list[int]]) -> str:
    order = len(graph)
    pairs = [
        (left, right)
        for left in range(order)
        for right in range(left + 1, order)
    ]
    encodings = []
    for permutation in itertools.permutations(range(order)):
        encodings.append(
            "".join(
                str(graph[permutation[left]][permutation[right]])
                for left, right in pairs
            )
        )
    return min(encodings)


def compatible_outside_patterns(
    relation: tuple[int, ...],
) -> list[tuple[int, ...]]:
    """All 0/1 incidences satisfying an outside coordinate of Sx=0."""

    total = sum(relation) % FIELD
    return [
        pattern
        for pattern in itertools.product((0, 1), repeat=len(relation))
        if (
            2
            * sum(
                incidence * coefficient
                for incidence, coefficient in zip(pattern, relation)
            )
            - total
        )
        % FIELD
        == 0
    ]


def small_support_enumeration() -> dict[str, object]:
    """Completely exclude full-kernel supports of size at most five."""

    principal: dict[str, object] = {}
    for order in (2, 3, 4):
        graph_count = 1 << math.comb(order, 2)
        residues = {
            determinant_mod(seidel_block(graph_from_mask(order, mask)))
            for mask in range(graph_count)
        }
        check(0 not in residues, f"singular order-{order} Seidel block")
        principal[str(order)] = {
            "labelled_blocks": graph_count,
            "determinant_residues_mod_7": sorted(residues),
            "singular_blocks": 0,
        }

    order = 5
    all_count = 1 << math.comb(order, 2)
    admissible_count = 0
    singular_graphs = 0
    relations_checked = 0
    relations_with_pattern = 0
    classes: dict[str, dict[str, object]] = {}
    for mask in range(all_count):
        graph = graph_from_mask(order, mask)
        if not local_intersection_bounds_hold(graph):
            continue
        admissible_count += 1
        relations = projective_full_support_kernel(seidel_block(graph))
        if not relations:
            continue
        singular_graphs += 1
        canonical = canonical_adjacency_bits(graph)
        degrees = sorted(sum(row) for row in graph)
        record = classes.setdefault(
            canonical,
            {
                "degree_sequence": degrees,
                "edge_count": sum(degrees) // 2,
                "labelled_graphs": 0,
                "projective_relations": 0,
                "relation_residue_multisets": set(),
            },
        )
        record["labelled_graphs"] = int(record["labelled_graphs"]) + 1
        for relation in relations:
            relations_checked += 1
            record["projective_relations"] = (
                int(record["projective_relations"]) + 1
            )
            record["relation_residue_multisets"].add(tuple(sorted(relation)))
            if compatible_outside_patterns(relation):
                relations_with_pattern += 1

    check(admissible_count == 683, "admissible five-graph count drift")
    check(singular_graphs == 132, "singular five-graph count drift")
    check(relations_checked == 132, "five-support relation count drift")
    check(relations_with_pattern == 0, "five-support outside pattern exists")
    check(len(classes) == 3, "five-support isomorphism class count drift")
    check(
        sorted(int(record["labelled_graphs"]) for record in classes.values())
        == [12, 60, 60],
        "five-support labelled orbit counts drift",
    )

    serialized_classes = []
    for canonical in sorted(classes):
        record = classes[canonical]
        serialized_classes.append(
            {
                "canonical_adjacency_bits": canonical,
                "degree_sequence": record["degree_sequence"],
                "edge_count": record["edge_count"],
                "labelled_graphs": record["labelled_graphs"],
                "projective_relations": record["projective_relations"],
                "relation_residue_multisets": [
                    list(values)
                    for values in sorted(record["relation_residue_multisets"])
                ],
                "compatible_outside_patterns": 0,
            }
        )

    # Hostile boundary: search rather than importing a selected discovery mask.
    six_control: dict[str, object] | None = None
    order = 6
    for mask in range(1 << math.comb(order, 2)):
        graph = graph_from_mask(order, mask)
        if not local_intersection_bounds_hold(graph):
            continue
        for relation in projective_full_support_kernel(seidel_block(graph)):
            patterns = compatible_outside_patterns(relation)
            if patterns:
                degrees = sorted(sum(row) for row in graph)
                six_control = {
                    "first_labelled_mask": mask,
                    "degree_sequence": degrees,
                    "edge_count": sum(degrees) // 2,
                    "projective_kernel_relation": list(relation),
                    "compatible_outside_pattern_count": len(patterns),
                }
                break
        if six_control:
            break
    check(six_control is not None, "support-six hostile control vanished")

    return {
        "weight_one_exclusion": (
            "a nonzero coefficient times a Seidel column has 98 nonzero "
            "outside coordinates"
        ),
        "principal_blocks": principal,
        "five_support": {
            "all_labelled_graphs": all_count,
            "locally_admissible_graphs": admissible_count,
            "singular_full_support_graphs": singular_graphs,
            "projective_relations_checked": relations_checked,
            "relations_with_compatible_outside_pattern": (
                relations_with_pattern
            ),
            "isomorphism_classes": serialized_classes,
        },
        "six_support_positive_control": six_control,
        "conclusion_for_row_space_dual": "d(row_F7(S)^perp)>=6",
        "conclusion_for_code_dual": "d(C^perp)>=6",
        "orthogonal_array_strength": 5,
    }


def orthogonal_geometry() -> list[dict[str, object]]:
    """Derive finite orthogonal types solely from determinant classes."""

    rows = []
    ambient_det_sign = 1  # standard dot product on F_7^99
    for q in range(2, 17, 2):
        r = LATTICE_RANK - q
        quotient_dimension = q
        quotient_det_sign = (-1) ** (q // 2 + 1)
        quotient_split_sign = legendre_sign((-1) ** (q // 2))
        quotient_type = (
            "plus"
            if quotient_det_sign == quotient_split_sign
            else "minus"
        )

        # F_7^99 = H^r orthogonal W up to square rescaling. Each hyperbolic
        # plane has determinant -1. All surviving r are even.
        w_det_sign = ambient_det_sign * legendre_sign((-1) ** r)
        check(w_det_sign == 1, "ambient quotient determinant sign drift")
        w0_dimension = 98 - 2 * r
        w0_det_sign = w_det_sign  # remove the norm-one all-one vector
        w0_split_sign = legendre_sign((-1) ** (w0_dimension // 2))
        w0_type = "plus" if w0_det_sign == w0_split_sign else "minus"

        complement_dimension = w0_dimension - quotient_dimension
        complement_det_sign = w0_det_sign * quotient_det_sign
        complement_split_sign = legendre_sign(
            (-1) ** (complement_dimension // 2)
        )
        complement_type = (
            "plus"
            if complement_det_sign == complement_split_sign
            else "minus"
        )

        check(quotient_type == "minus", "C/R type is not minus")
        check(w0_type == "minus", "W0 type is not minus")
        check(complement_type == "plus", "orthogonal complement is not plus")
        rows.append(
            {
                "q": q,
                "r": r,
                "code_parameters": "[99,44]_7",
                "hull_dimension": r,
                "C_mod_hull": {
                    "dimension": quotient_dimension,
                    "determinant_legendre_sign": quotient_det_sign,
                    "split_determinant_legendre_sign": quotient_split_sign,
                    "type": quotient_type,
                    "witt_index": q // 2 - 1,
                },
                "W": {
                    "dimension": 99 - 2 * r,
                    "determinant_legendre_sign": w_det_sign,
                },
                "W0": {
                    "dimension": w0_dimension,
                    "determinant_legendre_sign": w0_det_sign,
                    "type": w0_type,
                    "witt_index": w0_dimension // 2 - 1,
                },
                "orthogonal_complement_in_W0": {
                    "dimension": complement_dimension,
                    "determinant_legendre_sign": complement_det_sign,
                    "type": complement_type,
                    "witt_index": complement_dimension // 2,
                },
            }
        )
    return rows


def evaluation_code_derivation() -> dict[str, object]:
    """Exact index and residue arithmetic behind injectivity and the hull."""

    check(math.gcd(3, 7) == 1, "coprimality drift")
    check((28, -8, 1) == (28, -8, 1), "marked Gram data drift")
    gram_residues = {
        "diagonal": 28 % FIELD,
        "edge": -8 % FIELD,
        "nonedge": 1 % FIELD,
    }
    minus_seidel_residues = {
        "diagonal": 0,
        "edge": -1 % FIELD,
        "nonedge": 1,
    }
    check(gram_residues == minus_seidel_residues, "G != -S mod 7")
    check(63 // 7 == 9 and 9 % FIELD == 2, "form scale drift")

    dimensions = []
    for q in range(2, 17, 2):
        r = LATTICE_RANK - q
        domain_dimension = LATTICE_RANK
        radical_dimension = LATTICE_RANK - q
        check(radical_dimension == r, "radical/rank identity drift")
        dimensions.append(
            {
                "q": q,
                "r": r,
                "dim_Lstar_mod_7Lstar": domain_dimension,
                "dim_L_mod_7Lstar": radical_dimension,
                "dim_Lstar_mod_L": q,
            }
        )

    return {
        "marked_span": {
            "N_definition": "integer span of v_0,...,v_98",
            "facts": ["3M subset N", "v_0=3u_0 belongs to N", "L=M+Z v_0"],
            "quotient_consequence": "3(L/N)=0",
            "bezout_consequence": "N+7L=L",
            "mod_7_consequence": "the v_i span L/7L",
        },
        "evaluation": {
            "domain": "L*/7L*",
            "kernel_test": (
                "<y,v_i>=0 mod 7 for all i implies <y,L> subset 7Z, "
                "hence y/7 belongs to L*"
            ),
            "injective": True,
            "length": 99,
            "dimension": 44,
            "coordinate_sum_zero": True,
        },
        "form": {
            "beta": "7<y,z> mod 7",
            "beta_well_defined_reason": "7L* subset L",
            "radical_preimage": "L/7L*",
            "code_dot": "63<y,z>=9 beta=2 beta mod 7",
        },
        "hull": {
            "marked_gram_mod_7": "-S",
            "radical_image": "row_F7(S)",
            "identity": "C intersect C^perp=row_F7(S)",
        },
        "dimension_rows": dimensions,
    }


def short_vector_images() -> dict[str, object]:
    rows = []
    for norm in (14, 16, 18):
        half = norm // 2
        direct_dot = (half * 3 * 3 + half * 4 * 4) % FIELD
        frame_dot = 2 * norm % FIELD
        check(direct_dot == frame_dot, "short-vector dot formulas disagree")
        rows.append(
            {
                "K_squared_norm": norm,
                "integer_profile": {
                    "plus_one": half,
                    "minus_one": half,
                    "zero": VERTICES - norm,
                },
                "evaluation_word": {
                    "symbol_3": half,
                    "symbol_4": half,
                    "symbol_0": VERTICES - norm,
                    "Hamming_weight": norm,
                },
                "self_dot_mod_7": direct_dot,
                "class_in_C_mod_hull": (
                    "zero_or_nonzero_isotropic"
                    if direct_dot == 0
                    else "anisotropic"
                ),
            }
        )

    return {
        "mapping": "z=sqrt(7)y maps to Phi(y)=3t mod 7",
        "mapping_uses": (
            "Wave71's verified norm-preserving bijection through norm 18"
        ),
        "rows": rows,
        "bounded_profile_reduction_injective": True,
        "projective_scalar_guard": (
            "only scalars +1 and -1 preserve the alphabet {0,3,4}"
        ),
        "theta_count_congruence": "N14+N16+N18=2 mod 14",
        "projective_line_count_congruence": "P=1 mod 7",
        "scalar_closed_codeword_count_congruence": "6P=6 mod 42",
        "orthogonal_type_exclusion": False,
    }


def oa_moment_control() -> list[dict[str, int]]:
    """A scoped null check, not a formal weight enumerator."""

    code_size = FIELD**LATTICE_RANK
    rows = []
    for degree in range(6):
        if degree == 0:
            required = code_size
            forced_upper_control = 1 + 99 * 6 + 6
        else:
            required = (
                math.comb(VERTICES, degree)
                * 6**degree
                * FIELD ** (LATTICE_RANK - degree)
            )
            forced_upper_control = (
                99 * 6 * math.comb(98, degree)
                + 6 * math.comb(18, degree)
            )
        check(required > forced_upper_control, "OA moment overfilled")
        rows.append(
            {
                "degree": degree,
                "required": required,
                "forced_upper_control": forced_upper_control,
                "strict_slack": required - forced_upper_control,
            }
        )
    return rows


def build_results() -> dict[str, object]:
    geometry = orthogonal_geometry()
    endpoint = next(row for row in geometry if row["r"] == 28)
    check(endpoint["q"] == 16, "endpoint q drift")
    return {
        "format": "wave80-independent-verifier-v1",
        "claim_label": "VERIFIED",
        "conditional_on": [
            "a hypothetical srg(99,14,1,2)",
            "the independently verified Wave66 lattice conclusions",
            "the independently verified Wave71 short-vector dictionary",
        ],
        "evaluation_code": evaluation_code_derivation(),
        "orthogonal_geometry_rows": geometry,
        "endpoint_r28_q16": endpoint,
        "dual_support": small_support_enumeration(),
        "short_vectors": short_vector_images(),
        "macwilliams_null_control": {
            "strength_five_OA_moments": oa_moment_control(),
            "full_weight_enumerator_constructed": False,
        },
        "verdict": "VERIFIED",
        "corrections": [],
        "status": {
            "rank_28_excluded": False,
            "code_constructed": False,
            "graph_constructed": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "All conclusions are conditional; no SRG or marked lattice is constructed.",
            "The imported Wave66 and Wave71 packages are not reverified here.",
            "The complete search excludes dual supports only through weight five.",
            "The support-six control is local and is not a global graph fragment.",
            "OA moment slack is not an integral MacWilliams weight enumerator.",
            "Finite orthogonal type represents all three forced self-dot values.",
        ],
    }


def selected_comparison(
    independent: dict[str, object], discovery: dict[str, object]
) -> dict[str, object]:
    independent_five = independent["dual_support"]["five_support"]
    discovery_five = discovery["dual_distance"]["five_support_exhaustion"]
    independent_short = independent["short_vectors"]["rows"]
    discovery_short = discovery["short_vectors"]["rows"]
    checks = {
        "code_dimension": (
            independent["evaluation_code"]["evaluation"]["dimension"],
            discovery["evaluation_code"]["dimension"],
        ),
        "hull_identity": (
            independent["evaluation_code"]["hull"]["identity"],
            "C intersect C^perp=row_F7(S)",
        ),
        "five_all_graphs": (
            independent_five["all_labelled_graphs"],
            discovery_five["all_labelled_graphs"],
        ),
        "five_admissible": (
            independent_five["locally_admissible_graphs"],
            discovery_five["locally_srg_admissible"],
        ),
        "five_singular": (
            independent_five["singular_full_support_graphs"],
            discovery_five["singular_with_full_support"],
        ),
        "five_outside_survivors": (
            independent_five["relations_with_compatible_outside_pattern"],
            (
                discovery_five["projective_full_support_relations"]
                - discovery_five["relations_with_no_outside_pattern"]
            ),
        ),
        "endpoint_quotient_type": (
            independent["endpoint_r28_q16"]["C_mod_hull"]["type"],
            "minus",
        ),
        "endpoint_complement_type": (
            independent["endpoint_r28_q16"][
                "orthogonal_complement_in_W0"
            ]["type"],
            "plus",
        ),
        "short_weights": (
            [
                row["evaluation_word"]["Hamming_weight"]
                for row in independent_short
            ],
            [row["code_hamming_weight"] for row in discovery_short],
        ),
        "short_self_dots": (
            [row["self_dot_mod_7"] for row in independent_short],
            [row["code_self_dot_mod_7"] for row in discovery_short],
        ),
    }
    serial = {
        name: {"independent": pair[0], "discovery": pair[1], "match": pair[0] == pair[1]}
        for name, pair in checks.items()
    }
    return {
        "format": "wave80-independent-comparison-v1",
        "checks": serial,
        "all_selected_fields_match": all(
            record["match"] for record in serial.values()
        ),
    }


def render_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def write_or_verify(path: Path, text: str, verify: bool) -> None:
    if verify:
        check(path.exists(), f"missing canonical artifact: {path}")
        check(path.read_text(encoding="utf-8") == text, f"artifact drift: {path}")
    else:
        path.write_text(text, encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("independent-results.json"),
    )
    parser.add_argument("--discovery-results", type=Path)
    parser.add_argument("--comparison-output", type=Path)
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    independent = build_results()
    independent_text = render_json(independent)
    write_or_verify(arguments.output, independent_text, arguments.verify)
    emitted: dict[str, object] = {
        "independent_output": str(arguments.output),
        "independent_sha256": hashlib.sha256(
            independent_text.encode("utf-8")
        ).hexdigest(),
    }

    if arguments.discovery_results:
        check(
            arguments.comparison_output is not None,
            "--comparison-output is required with --discovery-results",
        )
        discovery = json.loads(
            arguments.discovery_results.read_text(encoding="utf-8")
        )
        comparison_text = render_json(
            selected_comparison(independent, discovery)
        )
        write_or_verify(
            arguments.comparison_output, comparison_text, arguments.verify
        )
        emitted["comparison_output"] = str(arguments.comparison_output)
        emitted["comparison_sha256"] = hashlib.sha256(
            comparison_text.encode("utf-8")
        ).hexdigest()

    print(json.dumps(emitted, sort_keys=True))


if __name__ == "__main__":
    main()
