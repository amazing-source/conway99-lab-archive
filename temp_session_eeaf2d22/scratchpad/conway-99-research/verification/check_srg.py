#!/usr/bin/env python3
"""Exact validator for strongly regular graph edge-list certificates.

The implementation intentionally uses only the Python standard library and
checks the defining conditions in two redundant ways:

1. set intersections on adjacency lists; and
2. dense integer evaluation of the adjacency-matrix identity.

It is a validator, not a graph-search program.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


FORMAT = "srg-edge-list-v1"


class CertificateError(ValueError):
    """Raised when a certificate is malformed rather than mathematically false."""


@dataclass(frozen=True)
class Parameters:
    vertices: int
    degree: int
    adjacent_common: int
    nonadjacent_common: int

    def validate(self) -> None:
        values = (
            self.vertices,
            self.degree,
            self.adjacent_common,
            self.nonadjacent_common,
        )
        if any(type(value) is not int for value in values):
            raise CertificateError("all graph parameters must be integers")
        if self.vertices < 1:
            raise CertificateError("vertices must be positive")
        if not 0 <= self.degree < self.vertices:
            raise CertificateError("degree must lie in [0, vertices)")
        if self.adjacent_common < 0 or self.nonadjacent_common < 0:
            raise CertificateError("common-neighbor parameters must be nonnegative")


@dataclass
class CheckResult:
    name: str
    valid: bool
    error_count: int
    errors: list[str]


def _require_exact_keys(data: dict[str, Any], required: set[str]) -> None:
    missing = sorted(required - data.keys())
    extra = sorted(data.keys() - required)
    if missing:
        raise CertificateError(f"missing certificate keys: {', '.join(missing)}")
    if extra:
        raise CertificateError(f"unknown certificate keys: {', '.join(extra)}")


def _object_without_duplicate_keys(
    pairs: list[tuple[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CertificateError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def load_certificate(path: Path) -> tuple[int, list[tuple[int, int]]]:
    """Load and strictly validate the syntax of an edge-list certificate."""

    try:
        data = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_object_without_duplicate_keys,
        )
    except OSError as exc:
        raise CertificateError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise CertificateError(f"invalid JSON at line {exc.lineno}, column {exc.colno}") from exc

    if not isinstance(data, dict):
        raise CertificateError("certificate root must be a JSON object")
    _require_exact_keys(data, {"format", "vertices", "edges"})

    if data["format"] != FORMAT:
        raise CertificateError(f"format must be exactly {FORMAT!r}")
    vertices = data["vertices"]
    if type(vertices) is not int or vertices < 1:
        raise CertificateError("vertices must be a positive integer")
    if not isinstance(data["edges"], list):
        raise CertificateError("edges must be a JSON array")

    edges: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    for index, raw_edge in enumerate(data["edges"]):
        if not isinstance(raw_edge, list) or len(raw_edge) != 2:
            raise CertificateError(f"edge {index} must be a two-element JSON array")
        u, v = raw_edge
        if type(u) is not int or type(v) is not int:
            raise CertificateError(f"edge {index} endpoints must be integers")
        if not 0 <= u < vertices or not 0 <= v < vertices:
            raise CertificateError(f"edge {index} endpoint is outside [0, {vertices})")
        if u == v:
            raise CertificateError(f"edge {index} is a self-loop at vertex {u}")
        edge = (u, v) if u < v else (v, u)
        if edge in seen:
            raise CertificateError(f"duplicate undirected edge {edge}")
        seen.add(edge)
        edges.append(edge)

    edges.sort()
    return vertices, edges


def build_adjacency(vertices: int, edges: Iterable[tuple[int, int]]) -> list[set[int]]:
    adjacency = [set() for _ in range(vertices)]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    return adjacency


def _record(errors: list[str], message: str, max_errors: int) -> None:
    if len(errors) < max_errors:
        errors.append(message)


def check_combinatorial(
    adjacency: Sequence[set[int]], parameters: Parameters, max_errors: int
) -> CheckResult:
    """Check degrees and common-neighbor counts using set operations."""

    failures = 0
    errors: list[str] = []
    n = parameters.vertices

    for vertex, neighbors in enumerate(adjacency):
        actual = len(neighbors)
        if actual != parameters.degree:
            failures += 1
            _record(
                errors,
                f"degree[{vertex}]={actual}, expected {parameters.degree}",
                max_errors,
            )

    for u in range(n):
        for v in range(u + 1, n):
            actual = len(adjacency[u].intersection(adjacency[v]))
            adjacent = v in adjacency[u]
            expected = (
                parameters.adjacent_common
                if adjacent
                else parameters.nonadjacent_common
            )
            if actual != expected:
                failures += 1
                relation = "edge" if adjacent else "nonedge"
                _record(
                    errors,
                    f"common[{u},{v}]={actual} on {relation}, expected {expected}",
                    max_errors,
                )

    return CheckResult("combinatorial", failures == 0, failures, errors)


def check_matrix_identity(
    adjacency: Sequence[set[int]], parameters: Parameters, max_errors: int
) -> CheckResult:
    """Check A^2=(k-mu)I+(lambda-mu)A+mu*J over the integers."""

    failures = 0
    errors: list[str] = []
    n = parameters.vertices
    matrix = [[0] * n for _ in range(n)]
    for u, neighbors in enumerate(adjacency):
        for v in neighbors:
            matrix[u][v] = 1

    for i in range(n):
        for j in range(n):
            actual = sum(matrix[i][t] * matrix[t][j] for t in range(n))
            expected = parameters.nonadjacent_common
            if i == j:
                expected += parameters.degree - parameters.nonadjacent_common
            elif matrix[i][j]:
                expected += parameters.adjacent_common - parameters.nonadjacent_common
            if actual != expected:
                failures += 1
                _record(
                    errors,
                    f"matrix_identity[{i},{j}] has {actual}, expected {expected}",
                    max_errors,
                )

    return CheckResult("matrix_identity", failures == 0, failures, errors)


def result_document(
    certificate: Path,
    parameters: Parameters,
    edges: Sequence[tuple[int, int]],
    checks: Sequence[CheckResult],
) -> dict[str, Any]:
    return {
        "certificate": str(certificate),
        "parameters": {
            "vertices": parameters.vertices,
            "degree": parameters.degree,
            "lambda": parameters.adjacent_common,
            "mu": parameters.nonadjacent_common,
        },
        "edge_count": len(edges),
        "valid": all(check.valid for check in checks),
        "checks": [
            {
                "name": check.name,
                "valid": check.valid,
                "error_count": check.error_count,
                "errors_shown": check.errors,
            }
            for check in checks
        ],
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path, help="srg-edge-list-v1 JSON file")
    parser.add_argument("--vertices", type=int, default=99)
    parser.add_argument("--degree", type=int, default=14)
    parser.add_argument("--lambda", dest="adjacent_common", type=int, default=1)
    parser.add_argument("--mu", dest="nonadjacent_common", type=int, default=2)
    parser.add_argument(
        "--mode",
        choices=("both", "combinatorial", "matrix"),
        default="both",
        help="validation path; default runs both independent paths",
    )
    parser.add_argument(
        "--max-errors",
        type=int,
        default=20,
        help="maximum error messages shown per check (all failures are counted)",
    )
    parser.add_argument("--report", type=Path, help="optional JSON report output path")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.max_errors < 0:
        print("error: --max-errors must be nonnegative", file=sys.stderr)
        return 2

    parameters = Parameters(
        vertices=args.vertices,
        degree=args.degree,
        adjacent_common=args.adjacent_common,
        nonadjacent_common=args.nonadjacent_common,
    )

    try:
        parameters.validate()
        certificate_vertices, edges = load_certificate(args.certificate)
    except CertificateError as exc:
        print(f"malformed certificate: {exc}", file=sys.stderr)
        return 2

    if certificate_vertices != parameters.vertices:
        print(
            "invalid certificate: "
            f"declares {certificate_vertices} vertices, expected {parameters.vertices}",
            file=sys.stderr,
        )
        return 1

    adjacency = build_adjacency(certificate_vertices, edges)
    checks: list[CheckResult] = []
    if args.mode in ("both", "combinatorial"):
        checks.append(check_combinatorial(adjacency, parameters, args.max_errors))
    if args.mode in ("both", "matrix"):
        checks.append(check_matrix_identity(adjacency, parameters, args.max_errors))

    document = result_document(args.certificate, parameters, edges, checks)
    rendered = json.dumps(document, indent=2, sort_keys=True)
    print(rendered)

    if args.report:
        try:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(rendered + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot write report: {exc}", file=sys.stderr)
            return 2

    return 0 if document["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
