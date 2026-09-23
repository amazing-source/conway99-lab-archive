#!/usr/bin/env python3
"""Standard-library replay of the frozen Wave 44 row system and witness."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
FAMILY_NAMES = ("base", "vertex", "edge", "nonedge")
EXPECTED_ROW_COUNTS = {
    "base": 81,
    "vertex": 7,
    "edge": 36,
    "nonedge": 46,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def compact_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def family_hashes(families: dict[str, Any]) -> dict[str, str]:
    hashes = {
        name: hashlib.sha256(compact_json(families[name])).hexdigest()
        for name in FAMILY_NAMES
    }
    hashes["combined"] = hashlib.sha256(compact_json(families)).hexdigest()
    return hashes


def verify(
    row_system_path: Path,
    witness_path: Path,
    result_path: Path,
) -> dict[str, Any]:
    row_system = load_json(row_system_path)
    witness = load_json(witness_path)
    result = load_json(result_path)

    require(
        row_system.get("format") == "wave44-rooted-row-system-v1",
        "unexpected row-system format",
    )
    classes = row_system.get("classes")
    require(
        isinstance(classes, list)
        and len(classes) == 208
        and len(set(classes)) == 208
        and all(type(mask) is int for mask in classes),
        "class list is malformed",
    )
    families = row_system.get("families")
    require(
        isinstance(families, dict) and set(families) == set(FAMILY_NAMES),
        "equation families changed",
    )
    for name in FAMILY_NAMES:
        family = families[name]
        require(
            isinstance(family, dict) and set(family) == {"rows", "rhs"},
            f"{name} family is malformed",
        )
        rows = family["rows"]
        rhs = family["rhs"]
        require(
            isinstance(rows, list)
            and isinstance(rhs, list)
            and len(rows) == EXPECTED_ROW_COUNTS[name]
            and len(rhs) == EXPECTED_ROW_COUNTS[name],
            f"{name} family size changed",
        )
        require(
            all(
                isinstance(row, list)
                and len(row) == 209
                and all(type(value) is int for value in row)
                for row in rows
            )
            and all(type(value) is int for value in rhs),
            f"{name} family has malformed integer data",
        )

    hashes = family_hashes(families)
    require(
        row_system.get("row_rhs_sha256") == hashes,
        "row-system hash commitment failed",
    )
    require(
        result["rooted_system"]["row_rhs_sha256"] == hashes,
        "exact-result row hash commitment failed",
    )
    require(
        result["inputs"]["attempts/wave44-rooted-flags/row-system.json"]
        == sha256_file(row_system_path),
        "row-system file hash differs from exact result",
    )
    require(
        result["inputs"]["attempts/wave44-rooted-flags/rooted-witness.json"]
        == sha256_file(witness_path),
        "witness file hash differs from exact result",
    )

    require(
        witness.get("format") == "wave44-rooted-flags-witness-v1",
        "unexpected witness format",
    )
    support = witness.get("support")
    require(isinstance(support, list), "support is missing")
    support_hash = hashlib.sha256(compact_json(support)).hexdigest()
    require(
        witness.get("support_sha256") == support_hash,
        "support hash commitment failed",
    )
    class_index = {mask: index for index, mask in enumerate(classes)}
    counts = [0] * len(classes)
    seen: set[int] = set()
    for record in support:
        require(
            isinstance(record, dict)
            and set(record) == {"canonical_mask", "count"},
            "support record is malformed",
        )
        mask = record["canonical_mask"]
        count = record["count"]
        require(
            type(mask) is int
            and type(count) is int
            and count > 0
            and mask in class_index
            and mask not in seen,
            "support contains an invalid or duplicate class",
        )
        seen.add(mask)
        counts[class_index[mask]] = count
    h11 = witness.get("h11")
    require(type(h11) is int and h11 % 4 == 0, "h11 is malformed")
    vector = counts + [h11 // 4]

    family_nonzero_residuals: dict[str, int] = {}
    for name in FAMILY_NAMES:
        family = families[name]
        nonzero = 0
        for row, target in zip(family["rows"], family["rhs"]):
            residual = sum(
                coefficient * value
                for coefficient, value in zip(row, vector)
            ) - target
            nonzero += residual != 0
        family_nonzero_residuals[name] = nonzero
    require(
        not any(family_nonzero_residuals.values()),
        "frozen witness has a nonzero exact residual",
    )
    require(sum(counts) == math.comb(99, 7), "seven-subset total changed")
    require(
        result["exact_positive_control"]["support_sha256"] == support_hash
        and result["exact_positive_control"]["h11"] == h11
        and result["exact_positive_control"]["support_size"] == len(support),
        "exact-result witness summary differs",
    )
    require(
        result["conclusion"]["endpoint_n3_4158"] == "UNKNOWN"
        and result["conclusion"]["Conway_99"] == "UNKNOWN"
        and not result["conclusion"]["graph_constructed"],
        "status wall changed",
    )
    return {
        "row_rhs_sha256": hashes,
        "row_system_file_sha256": sha256_file(row_system_path),
        "witness_file_sha256": sha256_file(witness_path),
        "result_file_sha256": sha256_file(result_path),
        "family_nonzero_residuals": family_nonzero_residuals,
        "total_rows": sum(EXPECTED_ROW_COUNTS.values()),
        "status": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--row-system", type=Path, default=HERE / "row-system.json")
    parser.add_argument("--witness", type=Path, default=HERE / "rooted-witness.json")
    parser.add_argument("--result", type=Path, default=HERE / "exact-results.json")
    arguments = parser.parse_args()
    summary = verify(
        arguments.row_system,
        arguments.witness,
        arguments.result,
    )
    print(json.dumps(summary, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
