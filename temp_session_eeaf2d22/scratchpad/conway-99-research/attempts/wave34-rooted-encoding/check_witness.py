#!/usr/bin/env python3
"""Independent exact checker for a complete 99-vertex witness.

This file deliberately does not import the CNF generator or decoder.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


LINES = (
    frozenset((0, 1, 3)),
    frozenset((0, 2, 6)),
    frozenset((0, 4, 5)),
    frozenset((1, 2, 4)),
    frozenset((1, 5, 6)),
    frozenset((2, 3, 5)),
    frozenset((3, 4, 6)),
)


def expected_fixed_cells() -> tuple[list[list[int]], list[list[int]]]:
    a_s = [[0] * 14 for _ in range(14)]
    for p in range(7):
        for ell in range(7):
            edge = int(p not in LINES[ell])
            a_s[p][7 + ell] = edge
            a_s[7 + ell][p] = edge
    pairs: list[tuple[int, int]] = []
    for p in range(7):
        for ell in range(7):
            pairs.extend([(p, ell)] * (2 if p in LINES[ell] else 1))
    f = [[0] * 70 for _ in range(14)]
    for o, (p, ell) in enumerate(pairs):
        f[p][o] = 1
        f[7 + ell][o] = 1
    return a_s, f


def load_graph(path: Path) -> list[list[int]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("adjacency")
    if not isinstance(rows, list) or len(rows) != 99:
        raise ValueError("adjacency must be a list of 99 rows")
    matrix: list[list[int]] = []
    for i, row in enumerate(rows):
        if isinstance(row, str):
            if len(row) != 99 or set(row) - {"0", "1"}:
                raise ValueError(f"row {i} is not a 99-character binary string")
            matrix.append([int(x) for x in row])
        elif isinstance(row, list) and len(row) == 99 and all(x in (0, 1) for x in row):
            matrix.append([int(x) for x in row])
        else:
            raise ValueError(f"row {i} is not a binary row of length 99")
    return matrix


def matmul_entry(a: list[list[int]], b: list[list[int]], i: int, j: int) -> int:
    return sum(a[i][k] * b[k][j] for k in range(len(b)))


def check(path: Path) -> dict[str, object]:
    a = load_graph(path)
    failures: list[dict[str, object]] = []

    def fail(gate: str, detail: object) -> None:
        if len(failures) < 50:
            failures.append({"gate": gate, "detail": detail})

    for i in range(99):
        if a[i][i] != 0:
            fail("hollow", i)
        for j in range(i + 1, 99):
            if a[i][j] != a[j][i]:
                fail("symmetric", [i, j])

    expected_s, expected_f = expected_fixed_cells()
    for s in range(14):
        for t in range(14):
            if a[s][t] != expected_s[s][t]:
                fail("fixed_S_S", [s, t, a[s][t], expected_s[s][t]])
        for o in range(70):
            if a[s][14 + o] != expected_f[s][o]:
                fail("fixed_S_O", [s, o, a[s][14 + o], expected_f[s][o]])
        for q in range(15):
            if a[s][84 + q] != 0:
                fail("fixed_S_Q_zero", [s, q])
    for q in range(15):
        for r in range(15):
            if a[84 + q][84 + r] != 0:
                fail("fixed_Q_Q_zero", [q, r])

    d = [[a[14 + i][14 + j] for j in range(70)] for i in range(70)]
    b = [[a[14 + i][84 + q] for q in range(15)] for i in range(70)]
    if {sum(row) for row in d} != {9}:
        fail("D_row_weight_9", sorted({sum(row) for row in d}))
    if {sum(row) for row in b} != {3}:
        fail("B_row_weight_3", sorted({sum(row) for row in b}))
    if {
        sum(b[o][q] for o in range(70)) for q in range(15)
    } != {14}:
        fail(
            "B_column_weight_14",
            sorted({sum(b[o][q] for o in range(70)) for q in range(15)}),
        )

    block_failure_counts = {
        "SS": 0,
        "SQ": 0,
        "SO": 0,
        "OO": 0,
        "OQ": 0,
        "QQ": 0,
    }
    for i in range(99):
        for j in range(99):
            lhs = sum(a[i][k] * a[k][j] for k in range(99))
            rhs = 12 * int(i == j) - a[i][j] + 2
            if lhs != rhs:
                if i < 14 and j < 14:
                    block = "SS"
                elif (i < 14 and j >= 84) or (j < 14 and i >= 84):
                    block = "SQ"
                elif (i < 14 <= j < 84) or (j < 14 <= i < 84):
                    block = "SO"
                elif 14 <= i < 84 and 14 <= j < 84:
                    block = "OO"
                elif (14 <= i < 84 <= j) or (14 <= j < 84 <= i):
                    block = "OQ"
                else:
                    block = "QQ"
                block_failure_counts[block] += 1
                fail("A2_identity", [i, j, lhs, rhs, block])

    edge_count = sum(sum(row) for row in a) // 2
    degree_set = sorted({sum(row) for row in a})
    raw_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    passed = not failures and not any(block_failure_counts.values())
    return {
        "schema_version": 1,
        "status": "PASS" if passed else "FAIL",
        "input": str(path),
        "input_sha256": raw_hash,
        "checks": {
            "vertices": 99,
            "edge_count": edge_count,
            "degree_set": degree_set,
            "full_identity_entries_checked": 99 * 99,
            "block_failure_counts": block_failure_counts,
            "fixed_labeled_partition_checked": True,
        },
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--witness", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = check(args.witness)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
