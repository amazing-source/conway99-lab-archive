"""Clean-room verifier for Wave 123.

The discovery checker is not imported.  This module rebuilds the signed
support vectors, exact span projectors, graph-valued 2x2 completion rows, and
all rooted product-Johnson feature factorizations from the sealed source
witness and candidate IDs.
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
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DISCOVERY = ROOT / "attempts" / "wave123-fixedc4-threepoint"
WITNESS = ROOT / "attempts" / "wave120-fixedc4-sumdiff" / "witness.json"
CANDIDATE = DISCOVERY / "candidate.json"
DISCOVERY_MANIFEST_SHA256 = (
    "39d680e78bf547c4fb5564048c6b7b1561382fd7d289f54a8a86154cff1a08a7"
)
WITNESS_SHA256 = (
    "3569eaa48ec3e99ab988f943492c103f67889c8fadf9a2a15edeac9586220183"
)
BLOCK_SIZES = (10, 10, 25, 10, 10, 26)
ALL40 = tuple(range(40))
FIRST26 = tuple(range(26))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def qtext(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def free_memory_percent() -> float:
    if os.name != "nt":
        return 100.0

    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("load", ctypes.c_ulong),
            ("total_phys", ctypes.c_ulonglong),
            ("available_phys", ctypes.c_ulonglong),
            ("total_page", ctypes.c_ulonglong),
            ("available_page", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("available_virtual", ctypes.c_ulonglong),
            ("available_extended", ctypes.c_ulonglong),
        ]

    state = MemoryStatus()
    state.length = ctypes.sizeof(state)
    require(
        bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state))),
        "GlobalMemoryStatusEx failed",
    )
    return 100.0 * state.available_phys / state.total_phys


def preinspect() -> dict[str, object]:
    manifest = DISCOVERY / "package-manifest.sha256"
    require(sha256(manifest) == DISCOVERY_MANIFEST_SHA256, "manifest hash drift")
    count = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        require(sha256(ROOT / relative) == expected, f"sealed drift: {relative}")
        count += 1
    require(count == 10, "discovery manifest entry count drift")
    require(sha256(WITNESS) == WITNESS_SHA256, "Wave120 witness drift")
    return {
        "discovery_manifest_sha256": DISCOVERY_MANIFEST_SHA256,
        "discovery_entries_checked": count,
        "source_witness_sha256": WITNESS_SHA256,
    }


def invert_exact(matrix: list[list[int]]) -> list[list[Q]]:
    n = len(matrix)
    work = [
        [Q(value) for value in matrix[i]]
        + [Q(int(i == j)) for j in range(n)]
        for i in range(n)
    ]
    for column in range(n):
        pivot = next(
            (row for row in range(column, n) if work[row][column]),
            None,
        )
        require(pivot is not None, "dependent support vectors")
        work[column], work[pivot] = work[pivot], work[column]
        divisor = work[column][column]
        work[column] = [value / divisor for value in work[column]]
        for row in range(n):
            if row == column or work[row][column] == 0:
                continue
            factor = work[row][column]
            work[row] = [
                work[row][j] - factor * work[column][j]
                for j in range(2 * n)
            ]
    inverse = [row[n:] for row in work]
    for i in range(n):
        for j in range(n):
            require(
                sum(Q(matrix[i][k]) * inverse[k][j] for k in range(n))
                == int(i == j),
                "Gram inverse replay failed",
            )
    return inverse


def load_inputs() -> tuple[list[list[list[int]]], tuple[int, ...]]:
    witness = json.loads(WITNESS.read_text(encoding="utf-8"))
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    require(witness["block_sizes"] == list(BLOCK_SIZES), "block size drift")
    records = witness["records"]
    require(len(records) == 40, "record count drift")
    for record in records:
        require(len(record) == 6, "record block count drift")
        for block, size in zip(record, BLOCK_SIZES, strict=True):
            require(
                len(block) == 2
                and len(set(block)) == 2
                and all(isinstance(value, int) and 0 <= value < size for value in block),
                "invalid two-subset record",
            )
    ids = tuple(candidate["record_ids_zero_based"])
    require(len(ids) == 26 and len(set(ids)) == 26, "bad candidate IDs")
    require(all(0 <= index < 40 for index in ids), "candidate ID outside source")
    return records, ids


def embed_vectors(records: list[list[list[int]]]) -> list[list[int]]:
    offsets: list[int] = []
    cursor = 8
    for size in BLOCK_SIZES:
        offsets.append(cursor)
        cursor += size
    require(cursor == 99, "coordinate partition drift")
    result: list[list[int]] = []
    for record in records:
        vector = [1, -1, 1, -1] + [0] * 95
        for block_index, (selection, offset) in enumerate(
            zip(record, offsets, strict=True)
        ):
            sign = 1 if block_index < 3 else -1
            for coordinate in selection:
                vector[offset + coordinate] = sign
        require(sum(value * value for value in vector) == 16, "norm drift")
        result.append(vector)
    return result


def exact_projector(
    vectors: list[list[int]], ids: tuple[int, ...]
) -> list[list[Q]]:
    width = len(ids)
    t = [[vectors[index][coordinate] for index in ids] for coordinate in range(99)]
    gram = [
        [
            sum(t[coordinate][i] * t[coordinate][j] for coordinate in range(99))
            for j in range(width)
        ]
        for i in range(width)
    ]
    inverse = invert_exact(gram)
    t_inverse = [
        [
            sum(Q(t[coordinate][i]) * inverse[i][j] for i in range(width))
            for j in range(width)
        ]
        for coordinate in range(99)
    ]
    projector = [
        [
            sum(
                t_inverse[left][j] * t[right][j] for j in range(width)
            )
            for right in range(99)
        ]
        for left in range(99)
    ]
    require(
        all(
            projector[i][j] == projector[j][i]
            for i in range(99)
            for j in range(i)
        ),
        "projector symmetry drift",
    )
    for coordinate in range(99):
        for j in range(width):
            require(
                sum(projector[coordinate][row] * t[row][j] for row in range(99))
                == t[coordinate][j],
                "W T = T failed",
            )
    require(sum(projector[i][i] for i in range(99)) == width, "trace/rank drift")
    return projector


def leverage_summary(projector: list[list[Q]]) -> dict[str, object]:
    diagonal = [projector[i][i] for i in range(99)]
    maximum = max(diagonal)
    rank = sum(diagonal)
    require(rank.denominator == 1, "projector rank is not integral")
    return {
        "rank": rank.numerator,
        "maximum_leverage": qtext(maximum),
        "maximum_coordinate": diagonal.index(maximum),
        "violating_coordinates": [
            i for i, value in enumerate(diagonal) if value > Q(4, 9)
        ],
        "diagonal_gate_passes": maximum <= Q(4, 9),
    }


def completion_summary(projector: list[list[Q]]) -> dict[str, object]:
    categories = {
        "invalid": [],
        "forced_edge": [],
        "forced_nonedge": [],
        "ambiguous": [],
    }
    for left in range(99):
        slack_left = Q(4, 9) - projector[left][left]
        for right in range(left + 1, 99):
            slack_right = Q(4, 9) - projector[right][right]
            permitted: list[bool] = []
            for edge, entry in ((False, Q(1, 63)), (True, Q(-8, 63))):
                difference = entry - projector[left][right]
                if difference * difference <= slack_left * slack_right:
                    permitted.append(edge)
            if not permitted:
                categories["invalid"].append((left, right))
            elif permitted == [True]:
                categories["forced_edge"].append((left, right))
            elif permitted == [False]:
                categories["forced_nonedge"].append((left, right))
            else:
                categories["ambiguous"].append((left, right))
    require(sum(map(len, categories.values())) == math_comb(99, 2),
            "coordinate-pair partition drift")
    return {
        "invalid_pair_count": len(categories["invalid"]),
        "invalid_pair_examples": [list(pair) for pair in categories["invalid"][:12]],
        "forced_edge_count": len(categories["forced_edge"]),
        "forced_nonedge_count": len(categories["forced_nonedge"]),
        "ambiguous_pair_count": len(categories["ambiguous"]),
        "passes_every_pair": not categories["invalid"],
    }


def math_comb(n: int, k: int) -> int:
    if k == 2:
        return n * (n - 1) // 2
    raise ValueError(k)


def record_sets(
    records: list[list[list[int]]], ids: tuple[int, ...]
) -> dict[int, list[frozenset[int]]]:
    return {
        index: [frozenset(block) for block in records[index]]
        for index in ids
    }


def dot(left: list[int], right: list[int]) -> int:
    return sum(a * b for a, b in zip(left, right, strict=True))


def triple_audit(
    records: list[list[list[int]]],
    ids: tuple[int, ...],
    vectors: list[list[int]],
) -> dict[str, object]:
    sets = record_sets(records, ids)
    overlap_rows: defaultdict[
        tuple[int, int, int], dict[int, tuple[int, int, int]]
    ] = defaultdict(dict)
    minimum_norm: int | None = None
    minimum_example: dict[str, object] | None = None
    triples = 0
    for a, b, c in itertools.combinations(ids, 3):
        triples += 1
        pair_tuple = tuple(
            sorted(
                sum(len(sets[x][block] & sets[y][block]) for block in range(6))
                for x, y in ((a, b), (a, c), (b, c))
            )
        )
        triple_intersection = sum(
            len(sets[a][block] & sets[b][block] & sets[c][block])
            for block in range(6)
        )
        overlap_rows[pair_tuple].setdefault(triple_intersection, (a, b, c))
        gram = [
            [dot(vectors[x], vectors[y]) for y in (a, b, c)]
            for x in (a, b, c)
        ]
        for signs in ((1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1)):
            norm = sum(
                signs[i] * gram[i][j] * signs[j]
                for i in range(3)
                for j in range(3)
            )
            if minimum_norm is None or norm < minimum_norm:
                minimum_norm = norm
                minimum_example = {
                    "record_ids": [a, b, c],
                    "coefficients": list(signs),
                }
    varied = {key: value for key, value in overlap_rows.items() if len(value) > 1}
    require(triples == 2600, "triple count drift")
    require(len(overlap_rows) == 52, "pair-overlap tuple count drift")
    require(len(varied) == 28, "triple-intersection variation count drift")
    require(minimum_norm == 22, "signed triple minimum drift")
    require(
        tuple_audit(sets, (0, 3, 6)) == ((1, 1, 4), 0)
        and tuple_audit(sets, (0, 6, 39)) == ((1, 1, 4), 1),
        "displayed beyond-pairwise example drift",
    )
    return {
        "triple_count": triples,
        "pair_overlap_tuple_count": len(overlap_rows),
        "pair_overlap_tuples_with_multiple_triple_intersections": len(varied),
        "minimum_signed_triple_norm": minimum_norm,
        "minimum_signed_triple_example": minimum_example,
        "displayed_pairwise_collision": {
            "pair_overlap_tuple": [1, 1, 4],
            "triple_zero": [0, 3, 6],
            "triple_one": [0, 6, 39],
        },
    }


def tuple_audit(
    sets: dict[int, list[frozenset[int]]], triple: tuple[int, int, int]
) -> tuple[tuple[int, int, int], int]:
    a, b, c = triple
    pair_tuple = tuple(
        sorted(
            sum(len(sets[x][block] & sets[y][block]) for block in range(6))
            for x, y in ((a, b), (a, c), (b, c))
        )
    )
    intersection = sum(
        len(sets[a][block] & sets[b][block] & sets[c][block])
        for block in range(6)
    )
    return pair_tuple, intersection


def rooted_feature_audit(
    records: list[list[list[int]]], ids: tuple[int, ...]
) -> dict[str, object]:
    sets = record_sets(records, ids)
    endpoint = 0
    within = 0
    cross = 0
    gram_entry_checks = 0
    nonzero_feature_rows = 0
    for root in ids:
        for block, size in enumerate(BLOCK_SIZES):
            inside = sets[root][block]
            outside = frozenset(range(size)) - inside
            for cell in (inside, outside):
                endpoint += 1
                coordinates = tuple(sorted(cell))
                features: dict[int, tuple[Q, ...]] = {}
                for record in ids:
                    count = len(sets[record][block] & cell)
                    features[record] = tuple(
                        Q(int(coordinate in sets[record][block]))
                        - Q(count, len(cell))
                        for coordinate in coordinates
                    )
                    if any(features[record]):
                        nonzero_feature_rows += 1
                for left in ids:
                    left_count = len(sets[left][block] & cell)
                    for right in ids:
                        right_count = len(sets[right][block] & cell)
                        gram = sum(
                            a * b
                            for a, b in zip(
                                features[left], features[right], strict=True
                            )
                        )
                        expected = Q(
                            len(sets[left][block] & sets[right][block] & cell)
                        ) - Q(left_count * right_count, len(cell))
                        require(gram == expected, "endpoint feature Gram drift")
                        gram_entry_checks += 1

            for root_overlap in range(3):
                within += 1
                features = {
                    record: (
                        frozenset({tuple(sorted(sets[record][block]))})
                        if len(sets[record][block] & inside) == root_overlap
                        else frozenset()
                    )
                    for record in ids
                }
                nonzero_feature_rows += sum(bool(row) for row in features.values())
                for left in ids:
                    for right in ids:
                        gram = len(features[left] & features[right])
                        expected = int(
                            sets[left][block] == sets[right][block]
                            and len(sets[left][block] & inside) == root_overlap
                        )
                        require(gram == expected, "within feature Gram drift")
                        gram_entry_checks += 1

        for first, second in itertools.combinations(range(6), 2):
            for first_inside in (False, True):
                first_cell = (
                    sets[root][first]
                    if first_inside
                    else frozenset(range(BLOCK_SIZES[first])) - sets[root][first]
                )
                for second_inside in (False, True):
                    second_cell = (
                        sets[root][second]
                        if second_inside
                        else frozenset(range(BLOCK_SIZES[second])) - sets[root][second]
                    )
                    cross += 1
                    features = {
                        record: frozenset(
                            itertools.product(
                                sets[record][first] & first_cell,
                                sets[record][second] & second_cell,
                            )
                        )
                        for record in ids
                    }
                    nonzero_feature_rows += sum(
                        bool(row) for row in features.values()
                    )
                    for left in ids:
                        for right in ids:
                            gram = len(features[left] & features[right])
                            expected = (
                                len(
                                    sets[left][first]
                                    & sets[right][first]
                                    & first_cell
                                )
                                * len(
                                    sets[left][second]
                                    & sets[right][second]
                                    & second_cell
                                )
                            )
                            require(gram == expected, "cross feature Gram drift")
                            gram_entry_checks += 1
    require((endpoint, within, cross) == (312, 468, 1560),
            "rooted PSD block census drift")
    return {
        "centered_endpoint_one": endpoint,
        "within_block_degree_two": within,
        "cross_block_degree_two": cross,
        "total": endpoint + within + cross,
        "exact_feature_gram_entry_checks": gram_entry_checks,
        "nonzero_sparse_feature_rows": nonzero_feature_rows,
        "all_psd_by_explicit_F_F_transpose_factorization": True,
    }


def build_results() -> dict[str, object]:
    require(free_memory_percent() >= 15.0, "memory floor before verifier")
    seal = preinspect()
    records, candidate_ids = load_inputs()
    vectors = embed_vectors(records)

    projector40 = exact_projector(vectors, ALL40)
    projector_first26 = exact_projector(vectors, FIRST26)
    projector_candidate = exact_projector(vectors, candidate_ids)
    audit40 = leverage_summary(projector40)
    audit_first26 = leverage_summary(projector_first26)
    audit_candidate = leverage_summary(projector_candidate)
    completion = completion_summary(projector_candidate)

    require(len(audit40["violating_coordinates"]) == 46, "all40 failure drift")
    require(len(audit_first26["violating_coordinates"]) == 6,
            "first26 failure drift")
    require(not audit40["diagonal_gate_passes"], "all40 unexpectedly passes")
    require(not audit_first26["diagonal_gate_passes"],
            "first26 unexpectedly passes")
    require(audit_candidate["diagonal_gate_passes"],
            "explicit26 diagonal gate failed")
    require(
        audit_candidate["maximum_leverage"]
        == "1217462828759965373070564/2744155911807689338327015",
        "explicit26 maximum drift",
    )
    require(completion["invalid_pair_count"] == 352, "pair failure count drift")
    require(not completion["passes_every_pair"], "candidate completion passes")

    triple = triple_audit(records, candidate_ids, vectors)
    features = rooted_feature_audit(records, candidate_ids)
    discovery_result = json.loads(
        (DISCOVERY / "exact-results.json").read_text(encoding="utf-8")
    )
    telemetry = discovery_result["bounded_search_telemetry"]
    require(telemetry["status"] == "NONEXHAUSTIVE_HEURISTIC_ONLY",
            "search scope drift")
    require(not telemetry["negative_inference_allowed"],
            "heuristic improperly permits negative inference")
    require(not telemetry["zero_invalid_pair_subset_found"],
            "telemetry unexpectedly found completion")
    require(free_memory_percent() >= 15.0, "memory floor after verifier")

    return {
        "format": "wave123-independent-verification-v1",
        "claim_label": "VERIFIED",
        "scope": (
            "Exact necessary-condition checks for the displayed Wave120 "
            "coordinate families and explicit 26-record subset only."
        ),
        "preinspection": seal,
        "projector_necessity": {
            "E_minus4": "(27I-9A+J)/63",
            "diagonal": "4/9",
            "edge_entry": "-8/63",
            "nonedge_entry": "1/63",
            "condition": "E-W positive semidefinite",
        },
        "all40": audit40,
        "first26": audit_first26,
        "explicit26": {
            "record_ids_zero_based": list(candidate_ids),
            "diagonal": audit_candidate,
            "two_by_two_completion": completion,
            "three_point": triple,
            "rooted_feature_blocks": features,
        },
        "nonexhaustive_search_scope": {
            "sealed_telemetry_restarts": telemetry["completion_search_restarts"],
            "sealed_trial_removals": telemetry["trial_removals_evaluated"],
            "telemetry_algorithm_independently_replayed": False,
            "exhaustive_certificate_present": False,
            "negative_inference_allowed": False,
            "verifier_conclusion": (
                "The heuristic supplies no upper bound or nonexistence proof."
            ),
        },
        "comparison": {
            "discovery_exact_claims_matched": True,
            "corrections": [],
            "clarifications": [
                (
                    "The 2x2 failures refute only the displayed explicit "
                    "26-record coordinate family."
                ),
                (
                    "Feature-factor PSD blocks are code-geometry constraints, "
                    "not one common graph-valued projector completion."
                ),
            ],
        },
        "status_wall": {
            "some_26_word_graph_compatible_family": "UNKNOWN",
            "local_cap_25": "UNKNOWN",
            "local_cap_24": "UNKNOWN",
            "rank28_excluded": False,
            "rank30_excluded": False,
            "Conway_99": "UNKNOWN",
            "literature_novelty": "UNKNOWN",
        },
        "memory": {"floor_percent": 15, "floor_respected": True},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    rendered = canonical(build_results())
    if args.verify:
        require(args.verify.read_text(encoding="utf-8") == rendered,
                "independent result drift")
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    if not args.output and not args.verify:
        print(rendered, end="")


if __name__ == "__main__":
    main()
