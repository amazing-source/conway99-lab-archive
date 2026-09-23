#!/usr/bin/env python3
"""Discovery-side exact classification of rank-26 local equality.

This checker starts from the independently verified Wave 41 Schur
decomposition.  It does not read the abandoned Wave 41 endpoint artifact.

For a local partition with ``e`` even parts, Wave 41 gives

    rank(K39) = (25 - 2e) + 2 rank(F) + rank(B),

where ``rank(F) >= e`` and ``B`` is a symmetric Schur residual.  Therefore
rank 26 is possible only when ``rank(F)=e`` and ``rank(B)=1``.

The even-part search below enumerates every minimum-F permutation and every
one of the 10,395 labelled third-fibre matchings.  A cheap necessary
diagonal condition for a symmetric rank-one matrix is used only as a filter;
every survivor is checked by exact Gaussian elimination over F_7.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np


PRIME = 7
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
WAVE41_CHECKER = ROOT / "verification/wave41-rank26-secondary/secondary_check.py"
EVEN_PARTITIONS = (
    (6,),
    (4, 2),
    (4, 1, 1),
    (3, 2, 1),
    (2, 2, 2),
    (2, 2, 1, 1),
    (2, 1, 1, 1, 1),
)
ALL_ODD_PARTITIONS = (
    (5, 1),
    (3, 3),
    (3, 1, 1, 1),
    (1, 1, 1, 1, 1, 1),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, separators=(",", ": "))
        + "\n"
    ).encode("utf-8")


def load_wave41():
    spec = importlib.util.spec_from_file_location("wave41_secondary_frozen", WAVE41_CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the frozen Wave 41 checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.audit_frozen_inputs()
    return module


def projected_matching_forms(
    z: Sequence[Sequence[int]],
    edges: Sequence[tuple[int, int]],
    pairing_indices: Sequence[Sequence[int]],
) -> np.ndarray:
    """Return all Z^T W_R Z forms, labelled by the complete pairing stream."""

    z_array = np.asarray(z, dtype=np.int16)
    sums = z_array.sum(axis=0, dtype=np.int16)
    base = np.outer(sums, sums) - z_array.T @ z_array
    contributions = []
    for left, right in edges:
        a = z_array[left]
        b = z_array[right]
        contributions.append(-2 * (np.outer(a, b) + np.outer(b, a)))
    pairing_array = np.asarray(pairing_indices, dtype=np.int16)
    values = (
        base[None, :, :]
        + np.asarray(contributions, dtype=np.int16)[pairing_array].sum(
            axis=1, dtype=np.int16
        )
    ) % PRIME
    return np.asarray(values, dtype=np.int8)


def rank_one_diagonal_mask(diagonals: np.ndarray) -> np.ndarray:
    """Necessary diagonal condition for nonzero symmetric rank one.

    If B=lambda*v*v^T has rank one, some diagonal is nonzero and all nonzero
    diagonal entries lie in one quadratic-character class.  Over F_7 the
    nonzero squares are {1,2,4}; the other class is {3,5,6}.
    """

    values = np.asarray(diagonals, dtype=np.int8) % PRIME
    nonzero = values != 0
    square = np.isin(values, np.asarray((1, 2, 4), dtype=np.int8))
    classes = np.where(nonzero, np.where(square, 1, 2), 0)
    maximum = classes.max(axis=-1)
    minimum_nonzero = np.where(classes == 0, 3, classes).min(axis=-1)
    return nonzero.any(axis=-1) & (maximum == minimum_nonzero)


def exact_rank_one(matrix: Sequence[Sequence[int]], wave41) -> bool:
    values = [[entry % PRIME for entry in row] for row in matrix]
    size = len(values)
    if not size or any(len(row) != size for row in values):
        raise ValueError("rank-one check requires a nonempty square matrix")
    if any(values[i][j] != values[j][i] for i in range(size) for j in range(i)):
        return False
    pivot = next((i for i in range(size) if values[i][i]), None)
    if pivot is None:
        # A nonzero symmetric rank-one matrix over odd characteristic is
        # lambda*v*v^T and hence has a nonzero diagonal coordinate.
        return False
    scale = values[pivot][pivot]
    return all(
        (
            values[i][j] * scale
            - values[i][pivot] * values[pivot][j]
        ) % PRIME
        == 0
        for i in range(size)
        for j in range(size)
    )


def partition_key(partition: Sequence[int]) -> str:
    return "+".join(map(str, partition))


def classify_even_partition(
    partition: tuple[int, ...],
    wave41,
    edges: Sequence[tuple[int, int]],
    pairing_indices: Sequence[Sequence[int]],
    pairing_stream_sha256: str,
    batch_size: int = 128,
) -> dict[str, object]:
    e, permutations, subspace_census = wave41.minimum_f_permutations(partition)
    if e <= 0:
        raise ValueError("even-part classifier received an all-odd type")
    context = wave41.partition_context(partition)
    grouped: dict[bytes, list[dict[str, object]]] = defaultdict(list)
    permutation_stream = hashlib.sha256()
    target_stream = hashlib.sha256()

    for permutation in permutations:
        permutation_stream.update(bytes(permutation))
        data = wave41.fast_quotient_data(context, permutation)
        if data["F_rank"] != e:
            raise AssertionError("minimum-F stream contains a nonminimum permutation")
        z_key = wave41.matrix_key(data["Z"])
        target_key = wave41.matrix_key(data["target"])
        target_stream.update(bytes(permutation) + z_key + target_key)
        grouped[z_key].append(
            {
                "permutation": permutation,
                "z": data["Z"],
                "target": data["target"],
            }
        )

    diagonal_candidate_pairs = 0
    exact_rank_one_pairs = 0
    witnesses: list[dict[str, object]] = []
    kernel_records: list[dict[str, object]] = []

    for z_key in sorted(grouped):
        records = grouped[z_key]
        z = records[0]["z"]
        forms = projected_matching_forms(z, edges, pairing_indices)
        form_diagonals = np.diagonal(forms, axis1=1, axis2=2)
        kernel_candidate_pairs = 0
        kernel_rank_one_pairs = 0

        for start in range(0, len(records), batch_size):
            chunk = records[start : start + batch_size]
            target_diagonals = np.asarray(
                [
                    np.diag(np.asarray(record["target"], dtype=np.int8))
                    for record in chunk
                ],
                dtype=np.int8,
            )
            residual_diagonals = (
                form_diagonals[None, :, :]
                - target_diagonals[:, None, :]
            ) % PRIME
            masks = rank_one_diagonal_mask(residual_diagonals)
            candidate_locations = np.argwhere(masks)
            kernel_candidate_pairs += int(candidate_locations.shape[0])

            for local_record, matching_index in candidate_locations:
                record = chunk[int(local_record)]
                residual = (
                    forms[int(matching_index)].astype(np.int16)
                    - np.asarray(record["target"], dtype=np.int16)
                ) % PRIME
                if not exact_rank_one(residual.tolist(), wave41):
                    continue
                kernel_rank_one_pairs += 1
                if len(witnesses) < 20:
                    matching = tuple(
                        edges[index] for index in pairing_indices[int(matching_index)]
                    )
                    full_rank = wave41.rank(
                        wave41.full_block(
                            partition, record["permutation"], matching
                        )
                    )
                    if full_rank != 26:
                        raise AssertionError("rank-one residual did not lift to rank 26")
                    witnesses.append(
                        {
                            "permutation": list(record["permutation"]),
                            "matching_index": int(matching_index),
                            "matching": [list(edge) for edge in matching],
                            "residual": residual.astype(int).tolist(),
                            "full_K39_rank_F7": full_rank,
                        }
                    )

        diagonal_candidate_pairs += kernel_candidate_pairs
        exact_rank_one_pairs += kernel_rank_one_pairs
        kernel_records.append(
            {
                "right_kernel_sha256": hashlib.sha256(z_key).hexdigest(),
                "minimum_F_permutations": len(records),
                "labelled_R_per_permutation": len(pairing_indices),
                "diagonal_candidate_pairs": kernel_candidate_pairs,
                "exact_rank_one_pairs": kernel_rank_one_pairs,
            }
        )

    total_pairs = len(permutations) * len(pairing_indices)
    return {
        "partition": list(partition),
        "even_part_count": e,
        "rank_F7_S": wave41.rank(context["S"]),
        "minimum_F_rank": e,
        "minimum_F_permutations": len(permutations),
        "minimum_F_subspace_census": subspace_census,
        "distinct_canonical_right_kernels": len(grouped),
        "labelled_R_matchings": len(pairing_indices),
        "minimum_F_R_pairs": total_pairs,
        "diagonal_candidate_pairs": diagonal_candidate_pairs,
        "exact_rank_one_residual_pairs": exact_rank_one_pairs,
        "rank26_exists": bool(exact_rank_one_pairs),
        "rank26_witnesses_first_20": witnesses,
        "permutation_stream_sha256": permutation_stream.hexdigest(),
        "kernel_target_stream_sha256": target_stream.hexdigest(),
        "pairing_stream_sha256": pairing_stream_sha256,
        "kernel_records": kernel_records,
        "completeness": (
            "Every minimum-F labelled permutation from the verified complete "
            "Wave 41 subspace cover is grouped by its exact canonical right "
            "kernel. For each permutation, every one of the 10,395 labelled "
            "third-fibre matchings is tested. The quadratic-character "
            "diagonal condition only removes matrices that cannot be "
            "symmetric rank one; all survivors receive exact F_7 rank."
        ),
    }


def classify_all_odd_partition(
    partition: tuple[int, ...],
    wave41,
    pairings: Sequence[Sequence[tuple[int, int]]],
) -> dict[str, object]:
    """Solve the rank-one residual CSP for one all-odd type.

    Here e=0, F=0, and the canonical right-kernel basis is the identity.
    For a residual B=W_R-T of rank one, choose its first nonzero diagonal
    position p.  Since B_pp is invertible,

        B_ik B_pp = B_ip B_pk

    for every i,k.  After fixing p, its image under the border permutation,
    and R, this turns the full rank-one condition into pairwise compatibility
    constraints plus the all-different condition on the border permutation.
    The backtracker below enumerates every satisfying labelled permutation.
    """

    if any(part % 2 == 0 for part in partition):
        raise ValueError("all-odd classifier received an even-part type")
    context = wave41.partition_context(partition)
    interaction = context["interaction"]
    if wave41.rank(context["S"]) != 25:
        raise AssertionError("all-odd local block rank changed")

    # Every pair of assignments with distinct left and right labels extends
    # to a permutation.  On such pairs the canonical Schur interaction must
    # already be symmetric.
    for left in range(12):
        for right in range(12):
            a = 12 * left + right
            for other_left in range(12):
                if other_left == left:
                    continue
                for other_right in range(12):
                    if other_right == right:
                        continue
                    b = 12 * other_left + other_right
                    if interaction[a][b] % PRIME != interaction[b][a] % PRIME:
                        raise AssertionError("compatible Schur interaction is asymmetric")

    diagonal = [
        [
            (-interaction[12 * left + right][12 * left + right]) % PRIME
            for right in range(12)
        ]
        for left in range(12)
    ]
    solution_stream = hashlib.sha256()
    pairing_stream = hashlib.sha256()
    pivot_assignment_branches = 0
    nonempty_unary_branches = 0
    backtrack_nodes = 0
    rank_one_pairs = 0
    witnesses: list[dict[str, object]] = []
    seen_solutions: set[tuple[int, tuple[int, ...]]] = set()

    for matching_index, matching in enumerate(pairings):
        pairing_stream.update(bytes(value for edge in matching for value in edge))
        mate = [-1] * 12
        for left, right in matching:
            mate[left] = right
            mate[right] = left
        if any(value < 0 for value in mate):
            raise AssertionError("incomplete matching")

        def w_entry(left: int, right: int) -> int:
            if left == right:
                return 0
            return PRIME - 1 if mate[left] == right else 1

        for pivot in range(12):
            for pivot_image in range(12):
                pivot_diagonal = diagonal[pivot][pivot_image]
                if pivot_diagonal == 0:
                    continue
                pivot_assignment_branches += 1
                candidates: dict[int, list[int]] = {pivot: [pivot_image]}
                viable = True
                for left in range(12):
                    if left == pivot:
                        continue
                    values: list[int] = []
                    for right in range(12):
                        if right == pivot_image:
                            continue
                        current_diagonal = diagonal[left][right]
                        # The chosen pivot is canonical: all earlier
                        # residual diagonals must be zero.
                        if left < pivot and current_diagonal != 0:
                            continue
                        interaction_to_pivot = interaction[
                            12 * left + right
                        ][12 * pivot + pivot_image]
                        b_to_pivot = (
                            w_entry(left, pivot) - interaction_to_pivot
                        ) % PRIME
                        if (
                            b_to_pivot * b_to_pivot
                            - current_diagonal * pivot_diagonal
                        ) % PRIME:
                            continue
                        values.append(right)
                    if not values:
                        viable = False
                        break
                    candidates[left] = values
                if not viable:
                    continue
                nonempty_unary_branches += 1
                order = sorted(
                    (left for left in range(12) if left != pivot),
                    key=lambda left: (len(candidates[left]), left),
                )
                assignment = {pivot: pivot_image}

                def visit(depth: int, used: int) -> None:
                    nonlocal backtrack_nodes, rank_one_pairs
                    backtrack_nodes += 1
                    if depth == len(order):
                        permutation = tuple(assignment[left] for left in range(12))
                        identity = (matching_index, permutation)
                        if identity in seen_solutions:
                            raise AssertionError("duplicate rank-one solution")
                        seen_solutions.add(identity)
                        data = wave41.fast_quotient_data(context, permutation)
                        if data["F_rank"] != 0:
                            raise AssertionError("all-odd solution has nonzero F")
                        residual = wave41.add(
                            wave41.restricted_form(
                                data["Z"], wave41.within_z_block(matching)
                            ),
                            data["target"],
                            -1,
                        )
                        if not exact_rank_one(residual, wave41):
                            raise AssertionError("CSP emitted a non-rank-one residual")
                        full_rank = wave41.rank(
                            wave41.full_block(partition, permutation, matching)
                        )
                        if full_rank != 26:
                            raise AssertionError("rank-one residual did not lift to rank 26")
                        rank_one_pairs += 1
                        solution_stream.update(
                            matching_index.to_bytes(2, "big") + bytes(permutation)
                        )
                        if len(witnesses) < 20:
                            witnesses.append(
                                {
                                    "permutation": list(permutation),
                                    "matching_index": matching_index,
                                    "matching": [list(edge) for edge in matching],
                                    "residual": residual,
                                    "full_K39_rank_F7": full_rank,
                                }
                            )
                        return

                    left = order[depth]
                    for right in candidates[left]:
                        bit = 1 << right
                        if used & bit:
                            continue
                        b_left_pivot = (
                            w_entry(left, pivot)
                            - interaction[12 * left + right][
                                12 * pivot + pivot_image
                            ]
                        ) % PRIME
                        compatible = True
                        for other_left, other_right in assignment.items():
                            if other_left == pivot:
                                continue
                            b_other_pivot = (
                                w_entry(other_left, pivot)
                                - interaction[12 * other_left + other_right][
                                    12 * pivot + pivot_image
                                ]
                            ) % PRIME
                            b_pair = (
                                w_entry(left, other_left)
                                - interaction[12 * left + right][
                                    12 * other_left + other_right
                                ]
                            ) % PRIME
                            if (
                                b_pair * pivot_diagonal
                                - b_left_pivot * b_other_pivot
                            ) % PRIME:
                                compatible = False
                                break
                        if not compatible:
                            continue
                        assignment[left] = right
                        visit(depth + 1, used | bit)
                        del assignment[left]

                visit(0, 1 << pivot_image)

    return {
        "partition": list(partition),
        "even_part_count": 0,
        "rank_F7_S": 25,
        "minimum_F_rank": 0,
        "minimum_F_permutations": 12 * 11 * 10 * 9 * 8 * 7 * 6 * 5 * 4 * 3 * 2,
        "labelled_R_matchings": len(pairings),
        "minimum_F_R_pairs": (
            12 * 11 * 10 * 9 * 8 * 7 * 6 * 5 * 4 * 3 * 2 * len(pairings)
        ),
        "pivot_assignment_branches": pivot_assignment_branches,
        "nonempty_unary_branches": nonempty_unary_branches,
        "backtrack_nodes": backtrack_nodes,
        "exact_rank_one_residual_pairs": rank_one_pairs,
        "rank26_exists": bool(rank_one_pairs),
        "rank26_witnesses_first_20": witnesses,
        "solution_stream_sha256": solution_stream.hexdigest(),
        "pairing_stream_sha256": pairing_stream.hexdigest(),
        "completeness": (
            "Every labelled R matching is enumerated. Every rank-one residual "
            "has a unique first nonzero diagonal pivot; its pivot image is "
            "enumerated. The pivot identity converts all remaining rank-one "
            "equations into exact unary and pairwise constraints, and the "
            "backtracker exhausts every all-different border permutation."
        ),
    }


def compute_all_odd(
    partitions: Iterable[tuple[int, ...]] = ALL_ODD_PARTITIONS,
) -> dict[str, object]:
    wave41 = load_wave41()
    pairings = tuple(wave41.all_pairings())
    selected = tuple(partitions)
    results = {
        partition_key(partition): classify_all_odd_partition(
            partition, wave41, pairings
        )
        for partition in selected
    }
    total_rank_one = sum(
        entry["exact_rank_one_residual_pairs"] for entry in results.values()
    )
    return {
        "format": "wave42-rank26-equality-all-odd-v1",
        "claim_label": "CANDIDATE",
        "scope": (
            "Complete rank-26 equality classification for the selected "
            "all-odd edge-local types."
        ),
        "inputs": {
            "verification/wave41-rank26-secondary/secondary_check.py":
                sha256_file(WAVE41_CHECKER),
        },
        "mathematical_reduction": {
            "formula": "rank(K39)=25+rank(B)",
            "rank26_criterion": "rank(B)=1",
            "pivot_identity": "B_ik B_pp = B_ip B_pk",
        },
        "partitions": results,
        "totals": {
            "partition_types": len(results),
            "minimum_F_R_pairs": sum(
                entry["minimum_F_R_pairs"] for entry in results.values()
            ),
            "exact_rank_one_residual_pairs": total_rank_one,
            "rank26_exists": bool(total_rank_one),
        },
        "limitations": [
            "Discovery cannot verify itself.",
            "This output covers only the partition types explicitly listed.",
            "The enormous pair count is covered by an exact rank-one CSP, not "
            "by materializing every dense matrix.",
            "No graph, endpoint exclusion, n3 upper-bound improvement, novelty, "
            "or priority claim is made.",
        ],
    }


def compute(partitions: Iterable[tuple[int, ...]] = EVEN_PARTITIONS) -> dict[str, object]:
    wave41 = load_wave41()
    edges, pairing_indices, _ = wave41.pairing_index_data()
    pairing_stream = hashlib.sha256()
    for indices in pairing_indices:
        pairing_stream.update(bytes(indices))
    pairing_digest = pairing_stream.hexdigest()
    selected = tuple(partitions)
    results = {
        partition_key(partition): classify_even_partition(
            partition,
            wave41,
            edges,
            pairing_indices,
            pairing_digest,
        )
        for partition in selected
    }
    total_pairs = sum(entry["minimum_F_R_pairs"] for entry in results.values())
    total_rank_one = sum(
        entry["exact_rank_one_residual_pairs"] for entry in results.values()
    )
    return {
        "format": "wave42-rank26-equality-even-v1",
        "claim_label": "CANDIDATE",
        "scope": (
            "Complete rank-26 equality classification for the selected "
            "even-part edge-local types."
        ),
        "inputs": {
            "verification/wave41-rank26-secondary/secondary_check.py":
                sha256_file(WAVE41_CHECKER),
        },
        "mathematical_reduction": {
            "formula":
                "rank(K39)=(25-2e)+2 rank(F)+rank(B)",
            "rank26_criterion":
                "rank(F)=e and rank(B)=1",
            "rank_one_diagonal_filter":
                "nonzero symmetric rank one has a nonzero diagonal pivot and "
                "all nonzero diagonal entries in one F7 square class",
        },
        "partitions": results,
        "totals": {
            "partition_types": len(results),
            "minimum_F_R_pairs": total_pairs,
            "diagonal_candidate_pairs": sum(
                entry["diagonal_candidate_pairs"] for entry in results.values()
            ),
            "exact_rank_one_residual_pairs": total_rank_one,
            "rank26_exists": bool(total_rank_one),
        },
        "limitations": [
            "Discovery cannot verify itself.",
            "This output covers only the partition types explicitly listed.",
            "No graph, endpoint exclusion, n3 upper-bound improvement, novelty, "
            "or priority claim is made.",
        ],
    }


def validate(result: dict[str, object]) -> None:
    wave41 = load_wave41()
    expected_pairings = 10_395
    if result["totals"]["partition_types"] != len(result["partitions"]):
        raise ValueError("partition total changed")
    for key, entry in result["partitions"].items():
        partition = tuple(entry["partition"])
        e = sum(part % 2 == 0 for part in partition)
        if partition_key(partition) != key or e != entry["even_part_count"]:
            raise ValueError(f"partition metadata mismatch for {key}")
        if entry["labelled_R_matchings"] != expected_pairings:
            raise ValueError(f"incomplete matching universe for {key}")
        if (
            entry["minimum_F_R_pairs"]
            != entry["minimum_F_permutations"] * expected_pairings
        ):
            raise ValueError(f"pair product mismatch for {key}")
        if entry["rank_F7_S"] + 2 * e != 25:
            raise ValueError(f"Wave 41 base-rank identity changed for {key}")
        if entry["exact_rank_one_residual_pairs"] != len(
            entry["rank26_witnesses_first_20"]
        ) and entry["exact_rank_one_residual_pairs"] <= 20:
            raise ValueError(f"witness count mismatch for {key}")
        for witness in entry["rank26_witnesses_first_20"]:
            if witness["full_K39_rank_F7"] != 26:
                raise ValueError(f"bad rank-26 witness for {key}")
            if not exact_rank_one(witness["residual"], wave41):
                raise ValueError(f"bad residual witness for {key}")
    if result["totals"]["exact_rank_one_residual_pairs"] != sum(
        entry["exact_rank_one_residual_pairs"]
        for entry in result["partitions"].values()
    ):
        raise ValueError("rank-one total mismatch")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--partition",
        help="One partition, for example 2+2+2 or 3+3. Default: all seven even.",
    )
    parser.add_argument(
        "--all-odd",
        action="store_true",
        help="Run all four all-odd partitions.",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.verify:
        stored_payload = args.verify.read_bytes()
        stored = json.loads(stored_payload)
        validate(stored)
        selected = tuple(
            tuple(entry["partition"])
            for entry in stored["partitions"].values()
        )
        if stored["format"] == "wave42-rank26-equality-even-v1":
            replay = compute(selected)
        elif stored["format"] == "wave42-rank26-equality-all-odd-v1":
            replay = compute_all_odd(selected)
        else:
            raise ValueError("unknown replay format")
        replay_payload = canonical_json(replay)
        if replay_payload != stored_payload:
            raise ValueError("stored result differs from exact replay")
        print(
            f"PASS {args.verify} "
            f"sha256={hashlib.sha256(stored_payload).hexdigest()}"
        )
        return 0
    partitions = EVEN_PARTITIONS
    odd_mode = args.all_odd
    if args.partition:
        selected = tuple(int(value) for value in args.partition.split("+"))
        if selected not in EVEN_PARTITIONS + ALL_ODD_PARTITIONS:
            raise ValueError("unknown partition")
        partitions = (selected,)
        odd_mode = selected in ALL_ODD_PARTITIONS
    if args.all_odd and args.partition:
        raise ValueError("--all-odd and --partition are mutually exclusive")
    result = compute_all_odd(partitions if odd_mode and args.partition else ALL_ODD_PARTITIONS) if odd_mode else compute(partitions)
    validate(result)
    payload = canonical_json(result)
    if args.output:
        args.output.write_bytes(payload)
        print(f"WROTE {args.output} sha256={hashlib.sha256(payload).hexdigest()}")
    else:
        print(payload.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
