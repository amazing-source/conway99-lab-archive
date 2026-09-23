#!/usr/bin/env python3
"""Focused tests for the Wave 35 endpoint construction models."""

from __future__ import annotations

import unittest

from wave35_n3_endpoint_local_extension import (
    ExtensionSystem,
    LocalSeed,
    PARTITIONS,
    sha256_text,
)
from wave35_n3_endpoint_root_scout import (
    SURVIVING_BRANCHES,
    branch_mate_profile,
    endpoint_edge_sha256,
    endpoint_edges,
)
from root_model import RootModel


class LocalExtensionTests(unittest.TestCase):
    def test_all_four_seed_partitions(self) -> None:
        for partition in PARTITIONS:
            with self.subTest(partition=partition):
                seed = LocalSeed.build(partition)
                self.assertEqual(len(seed.edges), 51)
                self.assertEqual(
                    tuple(len(seed.adjacency[index]) for index in range(3)),
                    (14, 14, 2),
                )

    def test_type_census_and_moments(self) -> None:
        for partition in PARTITIONS:
            with self.subTest(partition=partition):
                system = ExtensionSystem.build(partition)
                self.assertEqual(
                    system.size_histogram,
                    {0: 1, 1: 27, 2: 288, 3: 1584, 4: 3600},
                )
                self.assertEqual(len(system.active_types), 5184)
                rows = tuple(system.equation_rows())
                self.assertEqual(len(rows), 380)
                self.assertEqual(rows[0][2], 12)
                self.assertEqual(rows[1][2], 60)

    def test_empty_selection_is_rejected(self) -> None:
        system = ExtensionSystem.build((2, 2, 2))
        with self.assertRaisesRegex(ValueError, "equation failure"):
            system.validate_selection(())

    def test_opb_is_deterministic(self) -> None:
        expected = {
            (2, 2, 2): "dbd94e3e717189d4e9630a54f51cd8180c923f53311f556066e72b35fe80993e",
            (2, 4): "396c2600759dc12d4d640d5445f9f8f4ef105ba4babd000ef56554f122a9df50",
            (3, 3): "f61cf5e5a0a04d10f6ed99391306d818a36e2e657b6d74b614f0bdc876099e77",
            (6,): "32f789c205066d7e47f9a8b0558ea43a4deffc42d4ba1a86f8846ed2c446b84d",
        }
        for partition, digest in expected.items():
            with self.subTest(partition=partition):
                self.assertEqual(
                    sha256_text(ExtensionSystem.build(partition).opb_text()),
                    digest,
                )


class RootEndpointTests(unittest.TestCase):
    def test_84_units_and_joint_cover_survivors(self) -> None:
        root = RootModel.build(7)
        edges = endpoint_edges(root)
        self.assertEqual(len(edges), 84)
        profile = branch_mate_profile(root, set(edges))
        self.assertEqual(
            tuple(branch for branch, count in profile.items() if count == 0),
            SURVIVING_BRANCHES,
        )
        self.assertEqual(
            profile,
            {1: 4, 2: 2, 3: 1, 4: 0, 5: 0, 6: 3, 7: 1, 8: 0, 9: 2, 10: 0, 11: 1, 12: 0},
        )
        self.assertEqual(len(endpoint_edge_sha256(edges)), 64)


if __name__ == "__main__":
    unittest.main()
