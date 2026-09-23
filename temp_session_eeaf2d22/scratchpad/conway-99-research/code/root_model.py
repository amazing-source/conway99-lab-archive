#!/usr/bin/env python3
"""Deterministic construction of the rooted Conway residual scaffold.

For pair_count=7 this builds the fixed part of the 84-vertex formulation. The
same code supports pair_count=2, whose completed graph is the 3-by-3 rook graph;
that small case is used for calibration.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable, Sequence


Label = tuple[int, int]


@dataclass(frozen=True)
class RootModel:
    pair_count: int
    labels: tuple[Label, ...]

    @classmethod
    def build(cls, pair_count: int = 7) -> "RootModel":
        if type(pair_count) is not int or pair_count < 2:
            raise ValueError("pair_count must be an integer at least 2")
        coordinates = range(2 * pair_count)
        labels = tuple(
            (left, right)
            for left, right in combinations(coordinates, 2)
            if right != cls.mate(left)
        )
        expected = 2 * pair_count * (pair_count - 1)
        if len(labels) != expected:
            raise AssertionError(f"generated {len(labels)} labels, expected {expected}")
        return cls(pair_count=pair_count, labels=labels)

    @staticmethod
    def mate(coordinate: int) -> int:
        return coordinate ^ 1

    @property
    def coordinate_count(self) -> int:
        return 2 * self.pair_count

    @property
    def residual_count(self) -> int:
        return len(self.labels)

    @property
    def residual_degree(self) -> int:
        return 2 * self.pair_count - 2

    @property
    def edge_variable_count(self) -> int:
        return self.residual_count * (self.residual_count - 1) // 2

    def label_index(self) -> dict[Label, int]:
        return {label: index for index, label in enumerate(self.labels)}

    def containing(self, coordinate: int) -> tuple[int, ...]:
        self._validate_coordinate(coordinate)
        return tuple(
            index for index, label in enumerate(self.labels) if coordinate in label
        )

    def incidence_entry(self, coordinate: int, label_index: int) -> int:
        self._validate_coordinate(coordinate)
        self._validate_label_index(label_index)
        return int(coordinate in self.labels[label_index])

    def matching_incidence_entry(self, coordinate: int, label_index: int) -> int:
        return self.incidence_entry(self.mate(coordinate), label_index)

    def coordinate_neighbor_target(self, coordinate: int, label_index: int) -> int:
        """Right side of sum_{p contains coordinate} X[p,q]."""

        return (
            2
            - self.incidence_entry(coordinate, label_index)
            - self.matching_incidence_entry(coordinate, label_index)
        )

    def common_neighbor_target(
        self, first: int, second: int, adjacent: bool
    ) -> int:
        """Required common neighbors inside the residual graph."""

        self._validate_label_index(first)
        self._validate_label_index(second)
        if first == second:
            raise ValueError("common-neighbor target requires distinct labels")
        intersection = len(set(self.labels[first]).intersection(self.labels[second]))
        if intersection not in (0, 1):
            raise AssertionError("distinct residual labels intersect in at most one coordinate")
        return 2 - int(adjacent) - intersection

    def scaffold_coordinate_generators(self) -> tuple[tuple[int, ...], ...]:
        """Generators for C2 wreath S_pair_count on root-neighbor coordinates."""

        generators: list[tuple[int, ...]] = []
        identity = tuple(range(self.coordinate_count))

        for pair in range(self.pair_count):
            permutation = list(identity)
            left = 2 * pair
            right = left + 1
            permutation[left], permutation[right] = right, left
            generators.append(tuple(permutation))

        for pair in range(self.pair_count - 1):
            permutation = list(identity)
            first = 2 * pair
            second = first + 2
            permutation[first], permutation[second] = second, first
            permutation[first + 1], permutation[second + 1] = second + 1, first + 1
            generators.append(tuple(permutation))

        return tuple(generators)

    def induced_label_permutation(
        self, coordinate_permutation: Sequence[int]
    ) -> tuple[int, ...]:
        if sorted(coordinate_permutation) != list(range(self.coordinate_count)):
            raise ValueError("coordinate_permutation must be a bijection")
        indices = self.label_index()
        result: list[int] = []
        for left, right in self.labels:
            image = tuple(sorted((coordinate_permutation[left], coordinate_permutation[right])))
            try:
                result.append(indices[image])
            except KeyError as exc:
                raise ValueError("permutation does not preserve the root matching") from exc
        return tuple(result)

    def label_generators(self) -> tuple[tuple[int, ...], ...]:
        return tuple(
            self.induced_label_permutation(permutation)
            for permutation in self.scaffold_coordinate_generators()
        )

    def validate_fixed_identities(self) -> None:
        """Raise AssertionError unless the fixed incidence identities hold."""

        n = self.coordinate_count
        r = self.residual_count

        for label in self.labels:
            if len(label) != 2 or label[1] == self.mate(label[0]):
                raise AssertionError(f"invalid residual label {label}")

        for coordinate in range(n):
            actual = len(self.containing(coordinate))
            expected = 2 * self.pair_count - 2
            if actual != expected:
                raise AssertionError(
                    f"incidence row {coordinate} has {actual} ones, expected {expected}"
                )

        # Check B B^T = (n-3) I + J - M.  For n=14 this is 11 I+J-M.
        for first in range(n):
            first_labels = set(self.containing(first))
            for second in range(n):
                actual = len(first_labels.intersection(self.containing(second)))
                if first == second:
                    expected = n - 2
                elif second == self.mate(first):
                    expected = 0
                else:
                    expected = 1
                if actual != expected:
                    raise AssertionError(
                        f"BB^T[{first},{second}]={actual}, expected {expected}"
                    )

        for label_index in range(r):
            target_sum = sum(
                self.coordinate_neighbor_target(coordinate, label_index)
                for coordinate in range(n)
            )
            if target_sum != 2 * self.residual_degree:
                raise AssertionError(
                    f"neighbor-incidence targets sum to {target_sum}, "
                    f"expected {2 * self.residual_degree}"
                )

        for generator in self.label_generators():
            if sorted(generator) != list(range(r)):
                raise AssertionError("induced scaffold generator is not a bijection")

    def summary(self) -> dict[str, Any]:
        self.validate_fixed_identities()
        labels = [list(label) for label in self.labels]
        generators = [list(generator) for generator in self.label_generators()]
        fingerprint_payload = json.dumps(
            {"labels": labels, "label_generators": generators},
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        pair_constraints = self.edge_variable_count
        and_auxiliaries = pair_constraints * (self.residual_count - 2)
        return {
            "format": "conway-root-model-v1",
            "pair_count": self.pair_count,
            "coordinate_count": self.coordinate_count,
            "residual_count": self.residual_count,
            "residual_degree": self.residual_degree,
            "residual_edge_count": self.residual_count * self.residual_degree // 2,
            "edge_variables": self.edge_variable_count,
            "coordinate_incidence_equalities": self.coordinate_count
            * self.residual_count,
            "common_neighbor_equalities": pair_constraints,
            "direct_and_auxiliaries": and_auxiliaries,
            "scaffold_group": f"C2 wreath S{self.pair_count}",
            "scaffold_generator_count": len(generators),
            "labels": labels,
            "label_generators": generators,
            "sha256": hashlib.sha256(fingerprint_payload).hexdigest(),
        }

    def _validate_coordinate(self, coordinate: int) -> None:
        if not 0 <= coordinate < self.coordinate_count:
            raise IndexError(f"coordinate {coordinate} is out of range")

    def _validate_label_index(self, label_index: int) -> None:
        if not 0 <= label_index < self.residual_count:
            raise IndexError(f"label index {label_index} is out of range")


def write_summary(path: Path, model: RootModel) -> None:
    rendered = json.dumps(model.summary(), indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pair-count", type=int, default=7)
    parser.add_argument("--output", type=Path, help="optional JSON summary path")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    model = RootModel.build(args.pair_count)
    if args.output:
        write_summary(args.output, model)
    else:
        print(json.dumps(model.summary(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
