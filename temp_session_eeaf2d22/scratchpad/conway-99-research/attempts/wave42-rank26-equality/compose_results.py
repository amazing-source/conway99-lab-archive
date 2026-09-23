#!/usr/bin/env python3
"""Compose and audit the eleven atomic Wave 42 equality results."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PARTITIONS = (
    (1, 1, 1, 1, 1, 1),
    (2, 1, 1, 1, 1),
    (2, 2, 1, 1),
    (2, 2, 2),
    (3, 1, 1, 1),
    (3, 2, 1),
    (3, 3),
    (4, 1, 1),
    (4, 2),
    (5, 1),
    (6,),
)
EXPECTED_MINIMUM_F = {
    (1, 1, 1, 1, 1, 1): 479_001_600,
    (2, 1, 1, 1, 1): 80_640,
    (2, 2, 1, 1): 192,
    (2, 2, 2): 32,
    (3, 1, 1, 1): 479_001_600,
    (3, 2, 1): 80_640,
    (3, 3): 479_001_600,
    (4, 1, 1): 768,
    (4, 2): 64,
    (5, 1): 479_001_600,
    (6,): 2_592,
}


def key(partition: tuple[int, ...]) -> str:
    return "+".join(map(str, partition))


def atomic_path(partition: tuple[int, ...]) -> Path:
    return HERE / f"partial-{key(partition)}.json"


def sha256(path: Path) -> str:
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


def load_atomic(partition: tuple[int, ...]) -> tuple[dict[str, object], str]:
    path = atomic_path(partition)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if set(payload["partitions"]) != {key(partition)}:
        raise ValueError(f"atomic partition mismatch in {path.name}")
    entry = payload["partitions"][key(partition)]
    if tuple(entry["partition"]) != partition:
        raise ValueError(f"partition vector mismatch in {path.name}")
    if entry["minimum_F_permutations"] != EXPECTED_MINIMUM_F[partition]:
        raise ValueError(f"minimum-F count mismatch in {path.name}")
    if entry["labelled_R_matchings"] != 10_395:
        raise ValueError(f"matching count mismatch in {path.name}")
    if (
        entry["minimum_F_R_pairs"]
        != EXPECTED_MINIMUM_F[partition] * 10_395
    ):
        raise ValueError(f"pair product mismatch in {path.name}")
    if entry["rank26_exists"] != bool(entry["exact_rank_one_residual_pairs"]):
        raise ValueError(f"verdict/count mismatch in {path.name}")
    return entry, sha256(path)


def compute() -> dict[str, object]:
    entries: dict[str, object] = {}
    atomics: dict[str, object] = {}
    for partition in PARTITIONS:
        entry, digest = load_atomic(partition)
        name = key(partition)
        entries[name] = entry
        atomics[name] = {
            "path": (
                "attempts/wave42-rank26-equality/"
                f"partial-{name}.json"
            ),
            "sha256": digest,
        }
    total_rank_one = sum(
        entry["exact_rank_one_residual_pairs"] for entry in entries.values()
    )
    even_pairs = sum(
        entry["minimum_F_R_pairs"]
        for entry in entries.values()
        if entry["even_part_count"]
    )
    all_odd_pairs = sum(
        entry["minimum_F_R_pairs"]
        for entry in entries.values()
        if not entry["even_part_count"]
    )
    return {
        "format": "wave42-rank26-equality-v1",
        "git_commit": "ef49b60aafd67f9007f6c218c39fd50392453a1b",
        "claim_label": "CANDIDATE",
        "scope": (
            "Complete discovery-side rank-26 equality classification for all "
            "eleven edge-local partitions of six."
        ),
        "atomic_outputs": atomics,
        "partition_results": entries,
        "totals": {
            "partition_types": len(entries),
            "even_partition_types": sum(
                bool(entry["even_part_count"]) for entry in entries.values()
            ),
            "all_odd_partition_types": sum(
                not bool(entry["even_part_count"]) for entry in entries.values()
            ),
            "explicit_even_minimum_F_R_pairs": even_pairs,
            "implicit_all_odd_F_R_pairs": all_odd_pairs,
            "all_minimum_F_R_pairs": even_pairs + all_odd_pairs,
            "exact_rank_one_residual_pairs": total_rank_one,
            "rank26_exists": bool(total_rank_one),
        },
        "candidate_conclusion": {
            "all_local_K39_rank_F7_at_least": 27 if not total_rank_one else 26,
            "global_M_rank_F7_at_least": 27 if not total_rank_one else 26,
            "status": "CANDIDATE",
        },
        "coverage": {
            "automorphism_restriction": "none",
            "even_types": (
                "Every minimum-F labelled permutation and all 10,395 labelled "
                "third-fibre matchings are explicitly covered."
            ),
            "all_odd_types": (
                "Every labelled third-fibre matching is explicit; all 12! "
                "labelled border permutations are covered by the exact unique-"
                "pivot rank-one CSP."
            ),
        },
        "limitations": [
            "Discovery cannot verify itself.",
            "No graph or global compatibility certificate is constructed.",
            "The endpoint n3=4158 remains UNKNOWN.",
            "No upper-bound improvement below n3<=4158 is proved.",
            "Novelty and priority remain UNKNOWN.",
        ],
    }


def validate(result: dict[str, object]) -> None:
    if result["format"] != "wave42-rank26-equality-v1":
        raise ValueError("format changed")
    expected = {key(partition) for partition in PARTITIONS}
    if set(result["partition_results"]) != expected:
        raise ValueError("partition coverage is incomplete")
    if set(result["atomic_outputs"]) != expected:
        raise ValueError("atomic output coverage is incomplete")
    for partition in PARTITIONS:
        name = key(partition)
        entry, digest = load_atomic(partition)
        if result["partition_results"][name] != entry:
            raise ValueError(f"composed entry differs for {name}")
        if result["atomic_outputs"][name]["sha256"] != digest:
            raise ValueError(f"atomic hash differs for {name}")
    totals = result["totals"]
    if totals["partition_types"] != 11:
        raise ValueError("partition total is not eleven")
    if totals["even_partition_types"] != 7:
        raise ValueError("even partition total is not seven")
    if totals["all_odd_partition_types"] != 4:
        raise ValueError("all-odd partition total is not four")
    total_rank_one = sum(
        entry["exact_rank_one_residual_pairs"]
        for entry in result["partition_results"].values()
    )
    if totals["exact_rank_one_residual_pairs"] != total_rank_one:
        raise ValueError("rank-one total mismatch")
    if totals["rank26_exists"] != bool(total_rank_one):
        raise ValueError("rank-26 verdict mismatch")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = compute()
    validate(result)
    payload = canonical_json(result)
    if args.verify:
        if args.verify.read_bytes() != payload:
            raise ValueError("composed result differs from current atomic files")
        print(f"PASS {args.verify} sha256={hashlib.sha256(payload).hexdigest()}")
        return 0
    if args.output:
        args.output.write_bytes(payload)
        print(f"WROTE {args.output} sha256={hashlib.sha256(payload).hexdigest()}")
    else:
        print(payload.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
