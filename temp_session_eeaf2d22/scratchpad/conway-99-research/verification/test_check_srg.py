#!/usr/bin/env python3
"""Unit and integration tests for the exact SRG validator."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from check_srg import (
    CertificateError,
    Parameters,
    build_adjacency,
    check_combinatorial,
    check_matrix_identity,
    load_certificate,
)


HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "rook-3x3.srg.json"
CHECKER = HERE / "check_srg.py"


def rook_graph_edges(size: int = 3) -> list[tuple[int, int]]:
    edges: list[tuple[int, int]] = []
    for u in range(size * size):
        row_u, col_u = divmod(u, size)
        for v in range(u + 1, size * size):
            row_v, col_v = divmod(v, size)
            if row_u == row_v or col_u == col_v:
                edges.append((u, v))
    return edges


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parameters = Parameters(9, 4, 1, 2)
        self.adjacency = build_adjacency(9, rook_graph_edges())

    def test_rook_graph_passes_both_paths(self) -> None:
        combinatorial = check_combinatorial(self.adjacency, self.parameters, 20)
        matrix = check_matrix_identity(self.adjacency, self.parameters, 20)
        self.assertTrue(combinatorial.valid, combinatorial.errors)
        self.assertTrue(matrix.valid, matrix.errors)

    def test_single_edge_deletion_fails_both_paths(self) -> None:
        edges = rook_graph_edges()
        edges.remove((0, 1))
        adjacency = build_adjacency(9, edges)
        self.assertFalse(check_combinatorial(adjacency, self.parameters, 20).valid)
        self.assertFalse(check_matrix_identity(adjacency, self.parameters, 20).valid)

    def test_strict_parser_rejects_duplicate_undirected_edge(self) -> None:
        document = {
            "format": "srg-edge-list-v1",
            "vertices": 3,
            "edges": [[0, 1], [1, 0]],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaises(CertificateError):
                load_certificate(path)

    def test_strict_parser_rejects_boolean_endpoint(self) -> None:
        document = {
            "format": "srg-edge-list-v1",
            "vertices": 3,
            "edges": [[False, 1]],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "boolean.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaises(CertificateError):
                load_certificate(path)

    def test_strict_parser_rejects_duplicate_json_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate-key.json"
            path.write_text(
                '{"format":"srg-edge-list-v1","vertices":3,'
                '"vertices":3,"edges":[]}',
                encoding="utf-8",
            )
            with self.assertRaises(CertificateError):
                load_certificate(path)

    def test_cli_accepts_calibration_fixture(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(CHECKER),
                str(FIXTURE),
                "--vertices",
                "9",
                "--degree",
                "4",
                "--lambda",
                "1",
                "--mu",
                "2",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
        report = json.loads(completed.stdout)
        self.assertTrue(report["valid"])
        self.assertEqual(report["edge_count"], 18)

    def test_cli_rejects_fixture_under_conway_parameters(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(CHECKER), str(FIXTURE)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 1)
        self.assertIn("declares 9 vertices", completed.stderr)

    @unittest.skipUnless(shutil.which("powershell"), "Windows PowerShell not available")
    def test_independent_powershell_checker_accepts_fixture(self) -> None:
        completed = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(HERE / "Check-Srg.ps1"),
                "-Certificate",
                str(FIXTURE),
                "-Vertices",
                "9",
                "-Degree",
                "4",
                "-AdjacentCommon",
                "1",
                "-NonadjacentCommon",
                "2",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
        report = json.loads(completed.stdout)
        self.assertTrue(report["valid"])
        self.assertEqual(report["edge_count"], 18)

    @unittest.skipUnless(shutil.which("powershell"), "Windows PowerShell not available")
    def test_powershell_checker_rejects_duplicate_and_case_varied_keys(self) -> None:
        malformed_documents = (
            '{"format":"srg-edge-list-v1","vertices":3,'
            '"vertices":3,"edges":[]}',
            '{"Format":"srg-edge-list-v1","vertices":3,"edges":[]}',
        )
        with tempfile.TemporaryDirectory() as directory:
            for index, document in enumerate(malformed_documents):
                with self.subTest(index=index):
                    path = Path(directory) / f"malformed-{index}.json"
                    path.write_text(document, encoding="utf-8")
                    completed = subprocess.run(
                        [
                            "powershell",
                            "-NoProfile",
                            "-ExecutionPolicy",
                            "Bypass",
                            "-File",
                            str(HERE / "Check-Srg.ps1"),
                            "-Certificate",
                            str(path),
                            "-Vertices",
                            "3",
                            "-Degree",
                            "0",
                            "-AdjacentCommon",
                            "0",
                            "-NonadjacentCommon",
                            "0",
                        ],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(
                        completed.returncode,
                        2,
                        completed.stderr + completed.stdout,
                    )


if __name__ == "__main__":
    unittest.main()
