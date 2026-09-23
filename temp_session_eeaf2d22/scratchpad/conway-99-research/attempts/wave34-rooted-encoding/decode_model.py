#!/usr/bin/env python3
"""Decode a complete SAT assignment into a full 99-vertex graph certificate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


FANO_LINES = (
    (0, 1, 3),
    (0, 2, 6),
    (0, 4, 5),
    (1, 2, 4),
    (1, 5, 6),
    (2, 3, 5),
    (3, 4, 6),
)


def fixed_data() -> tuple[list[list[int]], list[dict[str, int]], list[list[int]]]:
    line_sets = [set(line) for line in FANO_LINES]
    support = [[0] * 14 for _ in range(14)]
    for p in range(7):
        for line, points in enumerate(line_sets):
            if p not in points:
                support[p][7 + line] = support[7 + line][p] = 1
    labels: list[dict[str, int]] = []
    for p in range(7):
        for line, points in enumerate(line_sets):
            for copy in range(2 if p in points else 1):
                labels.append({"point": p, "line": line, "copy": copy})
    incidence = [[0] * 70 for _ in range(14)]
    for o, label in enumerate(labels):
        incidence[label["point"]][o] = 1
        incidence[7 + label["line"]][o] = 1
    return support, labels, incidence


def parse_assignment(path: Path) -> dict[int, bool]:
    assignment: dict[int, bool] = {}
    declared_sat = False
    for raw in path.read_text(encoding="utf-8", errors="strict").splitlines():
        line = raw.strip()
        if not line or line.startswith("c"):
            continue
        if line in {"s SATISFIABLE", "SAT", "SATISFIABLE"}:
            declared_sat = True
            continue
        if line.startswith("s ") and "UNSAT" in line:
            raise ValueError("model file declares UNSAT")
        if line.startswith("v "):
            line = line[2:]
        for token in line.split():
            literal = int(token)
            if literal == 0:
                continue
            var = abs(literal)
            value = literal > 0
            if var in assignment and assignment[var] != value:
                raise ValueError(f"contradictory assignments for variable {var}")
            assignment[var] = value
    if not declared_sat:
        raise ValueError("model must contain a SAT status line")
    return assignment


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    values = parse_assignment(args.model)
    missing = [var for var in range(1, 5951) if var not in values]
    if missing:
        raise ValueError(
            f"model omits {len(missing)} primary variables; first missing {missing[:10]}"
        )

    support, labels, incidence = fixed_data()
    d = [[int(values[1 + 70 * i + j]) for j in range(70)] for i in range(70)]
    b = [
        [int(values[4901 + 15 * i + q]) for q in range(15)]
        for i in range(70)
    ]
    adjacency = [[0] * 99 for _ in range(99)]
    for i in range(14):
        for j in range(14):
            adjacency[i][j] = support[i][j]
    for s in range(14):
        for o in range(70):
            adjacency[s][14 + o] = adjacency[14 + o][s] = incidence[s][o]
    for i in range(70):
        for j in range(70):
            adjacency[14 + i][14 + j] = d[i][j]
        for q in range(15):
            adjacency[14 + i][84 + q] = adjacency[84 + q][14 + i] = b[i][q]

    output = {
        "schema_version": 1,
        "kind": "conway-99-full-adjacency-certificate",
        "vertex_order": {"S": [0, 13], "O": [14, 83], "Q": [84, 98]},
        "O_labels": labels,
        "adjacency": ["".join(str(x) for x in row) for row in adjacency],
        "source_model": str(args.model),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "DECODED_UNCHECKED", "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
