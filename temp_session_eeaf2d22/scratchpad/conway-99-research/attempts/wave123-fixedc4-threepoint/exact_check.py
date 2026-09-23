"""Exact Wave123 fixed-C4 projector and rooted three-point checks.

This discovery module distinguishes three increasingly strong conditions:

1. product-Johnson support-code and rooted three-point PSD conditions;
2. the diagonal leverage condition for containment in the -4 eigenspace;
3. graph-valued two-by-two PSD completion of E_{-4}-W.

Passing an earlier condition is not evidence that a later one, a common
graph, or Conway-99 exists.  All arithmetic is standard-library exact.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
import os
from collections import defaultdict
from fractions import Fraction
from pathlib import Path


Q = Fraction
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE_WITNESS = ROOT / "attempts/wave120-fixedc4-sumdiff/witness.json"
CANDIDATE_PATH = HERE / "candidate.json"
DEFAULT_OUTPUT = HERE / "exact-results.json"
BLOCK_SIZES = (10, 10, 25, 10, 10, 26)
EXPECTED_SOURCE_HASH = (
    "3569eaa48ec3e99ab988f943492c103f67889c8fadf9a2a15edeac9586220183"
)
FIRST26 = tuple(range(26))
ALL40 = tuple(range(40))


def free_memory_percent() -> float:
    if os.name != "nt":
        return 100.0

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MEMORYSTATUSEX()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * status.ullAvailPhys / status.ullTotalPhys


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def invert(matrix: list[list[int]]) -> list[list[Q]]:
    """Exact Gauss-Jordan inverse, failing if the columns are dependent."""
    n = len(matrix)
    work = [
        [Q(value) for value in row]
        + [Q(i == j) for j in range(n)]
        for i, row in enumerate(matrix)
    ]
    for column in range(n):
        pivot = next(
            (row for row in range(column, n) if work[row][column]),
            None,
        )
        if pivot is None:
            raise AssertionError("support columns are dependent")
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(n):
            if row == column or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                left - scale * right
                for left, right in zip(work[row], work[column])
            ]
    return [row[n:] for row in work]


def load_data() -> tuple[list, tuple[int, ...]]:
    if sha256(SOURCE_WITNESS) != EXPECTED_SOURCE_HASH:
        raise AssertionError("Wave120 witness hash drift")
    witness = json.loads(SOURCE_WITNESS.read_text(encoding="utf-8"))
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    if witness["block_sizes"] != list(BLOCK_SIZES):
        raise AssertionError("block sizes drift")
    records = witness["records"]
    if len(records) != 40:
        raise AssertionError("expected forty Wave120 records")
    ids = tuple(candidate["record_ids_zero_based"])
    if len(ids) != 26 or len(set(ids)) != 26:
        raise AssertionError("candidate must contain 26 distinct IDs")
    if not all(isinstance(index, int) and 0 <= index < 40 for index in ids):
        raise AssertionError("candidate ID out of range")
    return records, ids


def signed_vectors(records: list) -> list[list[int]]:
    """Embed records in all 99 graph coordinates.

    Coordinates 0..3 are the alternating C4.  Coordinates 4..7 are the
    four type-11 cross-edge witnesses from Wave112; norm-16 h=0 records
    use none of them.  The six Wave120 pools occupy the remaining 91
    coordinates.
    """
    offsets = []
    cursor = 8
    for size in BLOCK_SIZES:
        offsets.append(cursor)
        cursor += size
    if cursor != 99:
        raise AssertionError("coordinate partition drift")

    vectors = []
    for record in records:
        if len(record) != 6:
            raise AssertionError("record block count drift")
        vector = [1, -1, 1, -1] + [0] * 95
        for block_index, (selection, size, offset) in enumerate(
            zip(record, BLOCK_SIZES, offsets)
        ):
            if (
                len(selection) != 2
                or len(set(selection)) != 2
                or not all(
                    isinstance(value, int) and 0 <= value < size
                    for value in selection
                )
            ):
                raise AssertionError("invalid two-subset")
            sign = 1 if block_index < 3 else -1
            for value in selection:
                vector[offset + value] = sign
        if sum(value * value for value in vector) != 16:
            raise AssertionError("record norm drift")
        vectors.append(vector)
    return vectors


def span_projector(
    vectors: list[list[int]], ids: tuple[int, ...]
) -> tuple[list[list[Q]], list[list[int]], list[list[Q]]]:
    """Return W=T(T^T T)^-1 T^T with an exact factorization."""
    width = len(ids)
    transpose = [[vectors[index][row] for index in ids] for row in range(99)]
    gram = [
        [
            sum(transpose[row][i] * transpose[row][j] for row in range(99))
            for j in range(width)
        ]
        for i in range(width)
    ]
    inverse = invert(gram)
    right = [
        [
            sum(Q(transpose[row][i]) * inverse[i][j] for i in range(width))
            for j in range(width)
        ]
        for row in range(99)
    ]
    projector = [
        [
            sum(right[row][j] * transpose[column][j] for j in range(width))
            for column in range(99)
        ]
        for row in range(99)
    ]

    # Exact inverse and projector-on-columns checks.
    for i in range(width):
        for j in range(width):
            product = sum(Q(gram[i][k]) * inverse[k][j] for k in range(width))
            if product != Q(i == j):
                raise AssertionError("Gram inverse check failed")
    for row in range(99):
        for j in range(width):
            image = sum(projector[row][column] * transpose[column][j] for column in range(99))
            if image != transpose[row][j]:
                raise AssertionError("W*T=T check failed")
    return projector, gram, inverse


def leverage_audit(
    vectors: list[list[int]],
    ids: tuple[int, ...],
    completion: bool,
) -> dict:
    projector, _, _ = span_projector(vectors, ids)
    leverages = [projector[index][index] for index in range(99)]
    maximum = max(leverages)
    result = {
        "family_size": len(ids),
        "rank": len(ids),
        "maximum_leverage": text(maximum),
        "maximum_leverage_coordinate": leverages.index(maximum),
        "leverage_threshold": "4/9",
        "coordinates_above_threshold": [
            index
            for index, value in enumerate(leverages)
            if value > Q(4, 9)
        ],
        "diagonal_gate_passes": maximum <= Q(4, 9),
        "projector_certificate": "W=T*(T^T*T)^-1*T^T exact",
    }
    if not completion:
        return result

    invalid = []
    forced_edge = []
    forced_nonedge = []
    ambiguous = []
    for left in range(99):
        diagonal_left = Q(4, 9) - projector[left][left]
        for right in range(left + 1, 99):
            diagonal_right = Q(4, 9) - projector[right][right]
            allowed = []
            for adjacent, entry in ((False, Q(1, 63)), (True, Q(-8, 63))):
                off_diagonal = entry - projector[left][right]
                if off_diagonal * off_diagonal <= diagonal_left * diagonal_right:
                    allowed.append(adjacent)
            if not allowed:
                invalid.append([left, right])
            elif allowed == [True]:
                forced_edge.append([left, right])
            elif allowed == [False]:
                forced_nonedge.append([left, right])
            else:
                ambiguous.append([left, right])
    if len(invalid) + len(forced_edge) + len(forced_nonedge) + len(ambiguous) != 4851:
        raise AssertionError("coordinate-pair count drift")
    result["graph_valued_two_by_two_completion"] = {
        "criterion": (
            "(E_uv-W_uv)^2 <= (4/9-W_uu)*(4/9-W_vv), "
            "for at least one E_uv in {1/63,-8/63}"
        ),
        "invalid_pair_count": len(invalid),
        "invalid_pair_examples": invalid[:12],
        "forced_edge_count": len(forced_edge),
        "forced_nonedge_count": len(forced_nonedge),
        "ambiguous_pair_count": len(ambiguous),
        "passes_every_two_by_two_minor": not invalid,
    }
    return result


def record_sets(records: list, ids: tuple[int, ...]) -> dict[int, list[set[int]]]:
    return {
        index: [set(block) for block in records[index]]
        for index in ids
    }


def rooted_three_point_audit(records: list, ids: tuple[int, ...], vectors: list[list[int]]) -> dict:
    """Check exact rooted stabilizer PSD factors and triple lattice rows."""
    sets = record_sets(records, ids)
    varying = defaultdict(dict)
    signed_minimum = None
    signed_example = None
    triple_count = 0
    for left, middle, right in itertools.combinations(ids, 3):
        triple_count += 1
        pair_overlaps = tuple(
            sorted(
                sum(len(sets[a][block] & sets[b][block]) for block in range(6))
                for a, b in (
                    (left, middle),
                    (left, right),
                    (middle, right),
                )
            )
        )
        triple_intersection = sum(
            len(sets[left][block] & sets[middle][block] & sets[right][block])
            for block in range(6)
        )
        varying[pair_overlaps].setdefault(
            triple_intersection, [left, middle, right]
        )

        gram = [
            [
                sum(vectors[a][coordinate] * vectors[b][coordinate] for coordinate in range(99))
                for b in (left, middle, right)
            ]
            for a in (left, middle, right)
        ]
        for signs in ((1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1)):
            norm = sum(
                signs[i] * gram[i][j] * signs[j]
                for i in range(3)
                for j in range(3)
            )
            if signed_minimum is None or norm < signed_minimum:
                signed_minimum = norm
                signed_example = {
                    "record_ids": [left, middle, right],
                    "coefficients": list(signs),
                }

    varied_rows = {
        key: rows for key, rows in varying.items() if len(rows) > 1
    }
    first_key = sorted(varied_rows)[0]
    first_rows = varied_rows[first_key]
    example = {
        "same_sorted_pair_overlaps": list(first_key),
        "different_triple_intersections": [
            {
                "triple_intersection": value,
                "record_ids": first_rows[value],
            }
            for value in sorted(first_rows)[:2]
        ],
    }

    # Rooted product-Johnson stabilizer blocks.  Each checked matrix is
    # supplied as an explicit coordinate-feature Gram, hence PSD exactly.
    endpoint_blocks = 0
    within_pair_blocks = 0
    cross_blocks = 0
    for root in ids:
        for block, size in enumerate(BLOCK_SIZES):
            inside = sets[root][block]
            outside = set(range(size)) - inside
            for cell in (inside, outside):
                endpoint_blocks += 1
                cell_size = len(cell)
                for left in ids:
                    left_count = len(sets[left][block] & cell)
                    for right in ids:
                        right_count = len(sets[right][block] & cell)
                        common = len(sets[left][block] & sets[right][block] & cell)
                        formula = Q(common) - Q(left_count * right_count, cell_size)
                        direct = sum(
                            (
                                Q(coordinate in sets[left][block])
                                - Q(left_count, cell_size)
                            )
                            * (
                                Q(coordinate in sets[right][block])
                                - Q(right_count, cell_size)
                            )
                            for coordinate in cell
                        )
                        if formula != direct:
                            raise AssertionError("endpoint centered factor drift")

            for root_overlap in range(3):
                within_pair_blocks += 1
                for left in ids:
                    for right in ids:
                        direct = int(
                            sets[left][block] == sets[right][block]
                            and len(sets[left][block] & inside) == root_overlap
                        )
                        common_in = len(
                            sets[left][block] & sets[right][block] & inside
                        )
                        common_out = len(
                            (sets[left][block] & sets[right][block]) - inside
                        )
                        formula = (
                            (common_in * (common_in - 1) // 2)
                            if root_overlap == 2
                            else (
                                common_in * common_out
                                if root_overlap == 1
                                else common_out * (common_out - 1) // 2
                            )
                        )
                        if direct != formula:
                            raise AssertionError("within-block degree-two factor drift")

        for first, second in itertools.combinations(range(6), 2):
            for first_inside in (False, True):
                first_cell = (
                    sets[root][first]
                    if first_inside
                    else set(range(BLOCK_SIZES[first])) - sets[root][first]
                )
                for second_inside in (False, True):
                    second_cell = (
                        sets[root][second]
                        if second_inside
                        else set(range(BLOCK_SIZES[second])) - sets[root][second]
                    )
                    cross_blocks += 1
                    for left in ids:
                        for right in ids:
                            first_common = len(
                                sets[left][first]
                                & sets[right][first]
                                & first_cell
                            )
                            second_common = len(
                                sets[left][second]
                                & sets[right][second]
                                & second_cell
                            )
                            formula = first_common * second_common
                            direct = sum(
                                int(
                                    a in sets[left][first]
                                    and a in sets[right][first]
                                    and b in sets[left][second]
                                    and b in sets[right][second]
                                )
                                for a in first_cell
                                for b in second_cell
                            )
                            if formula != direct:
                                raise AssertionError("cross-block factor drift")

    if (endpoint_blocks, within_pair_blocks, cross_blocks) != (312, 468, 1560):
        raise AssertionError("rooted block census drift")
    return {
        "family_size": len(ids),
        "triple_count": triple_count,
        "pair_overlap_tuple_count": len(varying),
        "pair_overlap_tuples_with_multiple_triple_intersections": len(varied_rows),
        "strictly_beyond_pairwise_example": example,
        "signed_coefficients_tested_per_triple": [
            [1, 1, 1],
            [1, 1, -1],
            [1, -1, 1],
            [-1, 1, 1],
        ],
        "minimum_tested_signed_triple_norm": signed_minimum,
        "minimum_tested_signed_triple_example": signed_example,
        "rooted_psd_blocks": {
            "centered_endpoint_one": endpoint_blocks,
            "within_block_degree_two": within_pair_blocks,
            "cross_block_degree_two": cross_blocks,
            "total": endpoint_blocks + within_pair_blocks + cross_blocks,
            "all_have_exact_coordinate_feature_factorizations": True,
        },
        "code_only_three_point_gate_passes": True,
    }


def exact_results() -> dict:
    records, candidate_ids = load_data()
    vectors = signed_vectors(records)
    all40 = leverage_audit(vectors, ALL40, completion=False)
    first26 = leverage_audit(vectors, FIRST26, completion=False)
    candidate = leverage_audit(vectors, candidate_ids, completion=True)
    three_point = rooted_three_point_audit(records, candidate_ids, vectors)

    if len(all40["coordinates_above_threshold"]) != 46:
        raise AssertionError("all40 leverage count drift")
    if all40["maximum_leverage"] != (
        "154998381711798556753484666134716334/"
        "231026319585357084224437520694259587"
    ):
        raise AssertionError("all40 maximum leverage drift")
    if len(first26["coordinates_above_threshold"]) != 6:
        raise AssertionError("first26 leverage count drift")
    if candidate["maximum_leverage"] != (
        "1217462828759965373070564/2744155911807689338327015"
    ):
        raise AssertionError("candidate maximum leverage drift")
    if not candidate["diagonal_gate_passes"]:
        raise AssertionError("candidate must pass diagonal gate")
    completion = candidate["graph_valued_two_by_two_completion"]
    if completion["invalid_pair_count"] != 352:
        raise AssertionError("candidate invalid-pair count drift")
    if completion["passes_every_two_by_two_minor"]:
        raise AssertionError("candidate unexpectedly passes completion")

    return {
        "format": "wave123-fixedc4-threepoint-v1",
        "claim_labels": {
            "all40_coordinate_span": "REFUTED_AS_COMMON_EIGENSPACE",
            "first26_coordinate_span": "REFUTED_AS_COMMON_EIGENSPACE",
            "explicit26_diagonal_leverage": "CANDIDATE_EXACT_NULL_CONTROL",
            "explicit26_graph_valued_two_by_two_completion": "REFUTED",
            "code_only_rooted_three_point_cap": "REFUTED_AS_A_RELAXATION",
            "existence_of_some_26_word_graph_compatible_family": "UNKNOWN",
            "actual_local_caps": "UNKNOWN",
        },
        "scope": {
            "target": "hypothetical srg(99,14,1,2)",
            "fixed_cycle_orientation": [1, -1, 1, -1],
            "shell": "same-oriented norm-16 h=0 extensions",
            "automorphism_assumed": False,
            "source_witness_is_graph_realizable": False,
        },
        "projector_necessity": {
            "minus4_projector": "E=(27I-9A+J)/63",
            "diagonal": "4/9",
            "off_diagonal_if_nonedge": "1/63",
            "off_diagonal_if_edge": "-8/63",
            "span_projector": "W=T*(T^T*T)^-1*T^T",
            "necessary_operator_inequality": "W <= E",
        },
        "all40": all40,
        "first26": first26,
        "explicit26": {
            "record_ids_zero_based": list(candidate_ids),
            "projector_audit": candidate,
            "rooted_three_point_audit": three_point,
        },
        "bounded_search_telemetry": {
            "status": "NONEXHAUSTIVE_HEURISTIC_ONLY",
            "diagonal_candidate_source": (
                "floating backward projector downdates over the forty "
                "Wave120 records, followed by exact certification"
            ),
            "completion_search_restarts": 30,
            "removal_steps_per_restart": 14,
            "trial_removals_evaluated": 14070,
            "zero_invalid_pair_subset_found": False,
            "negative_inference_allowed": False,
        },
        "status": {
            "particular_all40_support_realization_killed": True,
            "particular_first26_support_realization_killed": True,
            "diagonal_leverage_alone_proves_cap25": False,
            "code_only_three_point_relaxation_proves_cap25": False,
            "some_26_subset_passes_full_projector_completion": "UNKNOWN",
            "rank28_excluded": False,
            "rank30_excluded": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "next_missing_constraints": [
            "a graph-valued PSD completion E-W beyond two-by-two minors",
            "one common 95-vertex outside adjacency satisfying all selected eigen-equations",
            "target degree, lambda, and mu constraints for that same adjacency",
            "membership of all supports in the one target parity kernel code",
        ],
        "limitations": [
            "The explicit 26-subset is not graph-realizable: 352 exact two-by-two completion rows fail.",
            "The 30-restart subset search is nonexhaustive and cannot prove that every 26-subset fails.",
            "An actual code defeats code-only three-point bounds but need not be an eigenvector family.",
            "The rooted PSD family is a strong exact truncated Terwilliger moment family, not an exhaustive graph-valued SDP.",
            "No automorphism of a hypothetical graph is assumed.",
            "Discovery cannot verify itself.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    free = free_memory_percent()
    if free < 15.0:
        raise SystemExit(
            f"refusing to run with only {free:.1f}% free physical memory"
        )
    result = exact_results()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.verify is not None:
        if (
            not args.verify.exists()
            or args.verify.read_text(encoding="utf-8") != encoded
        ):
            raise SystemExit("canonical exact-results.json mismatch")
        print(
            "PASS: canonical Wave123 result verified; "
            f"free physical memory {free:.1f}%"
        )
        return
    args.output.write_text(encoded, encoding="utf-8")
    print(f"wrote {args.output}; free physical memory {free:.1f}%")


if __name__ == "__main__":
    main()
