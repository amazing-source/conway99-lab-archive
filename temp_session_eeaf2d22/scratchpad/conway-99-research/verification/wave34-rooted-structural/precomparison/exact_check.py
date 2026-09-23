from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[3]

INPUT_HASHES = {
    "AGENTS.md":
        "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3",
    "verification/wave34-continuation-protocol.md":
        "60e6c3aba152e924a51bd2503e82de3d05bb39fada258da4a2796e344ae23cd4",
    "agents/2026-07-24-wave33-rooted-extension.md":
        "c324dc48f5c7b9524b8b2ac02fae3acb8b9ec342d0a61081ee86ae4771434c0c",
    "verification/wave33-rooted-extension/comparison-audit.md":
        "fc7abcd53154d4551a5d3d97d38024840b4228195e143559c9e8b46c15644b8a",
    "verification/wave33-rooted-extension/comparison-results.json":
        "2e36ecade28bca12d35a963a8c6b52777ac7d766a3c4b3267774000fe2e929fd",
    "verification/wave33-rooted-extension/precomparison-freeze.md":
        "ba479c6b426c17e79aaf4f57258e9b360eb17b81ba35eb7de77ff5104c96bb17",
    "verification/wave33-rooted-extension/independent-results.json":
        "66cef570dbbb4a86e2a35f780edcfc1873d0ac2c5266f1c2065c902a8f91e778",
    "verification/wave33-rooted-extension/independent_check.py":
        "069f1a72f313d7346a3d6bb8c2cf6e9e209a138343966bbbdd0f8624ea11e359",
}

Matrix = list[list[Fraction]]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_input_hashes() -> dict[str, str]:
    observed: dict[str, str] = {}
    for relative, expected in INPUT_HASHES.items():
        actual = sha256_file(ROOT / relative)
        if actual != expected:
            raise AssertionError(
                f"frozen input drift for {relative}: {actual} != {expected}"
            )
        observed[relative] = actual
    return observed


def frac(value: int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def zeros(rows: int, columns: int) -> Matrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    return [
        [Fraction(int(row == column)) for column in range(size)]
        for row in range(size)
    ]


def ones(rows: int, columns: int) -> Matrix:
    return [[Fraction(1) for _ in range(columns)] for _ in range(rows)]


def transpose(matrix: Sequence[Sequence[int | Fraction]]) -> Matrix:
    return [
        [frac(matrix[row][column]) for row in range(len(matrix))]
        for column in range(len(matrix[0]))
    ]


def matmul(
    left: Sequence[Sequence[int | Fraction]],
    right: Sequence[Sequence[int | Fraction]],
) -> Matrix:
    right_t = transpose(right)
    return [
        [
            sum((frac(a) * frac(b) for a, b in zip(row, column)), Fraction(0))
            for column in right_t
        ]
        for row in left
    ]


def matrix_add(
    *matrices: Sequence[Sequence[int | Fraction]],
) -> Matrix:
    rows = len(matrices[0])
    columns = len(matrices[0][0])
    return [
        [
            sum((frac(matrix[i][j]) for matrix in matrices), Fraction(0))
            for j in range(columns)
        ]
        for i in range(rows)
    ]


def matrix_scale(
    matrix: Sequence[Sequence[int | Fraction]],
    scalar: int | Fraction,
) -> Matrix:
    factor = frac(scalar)
    return [[factor * frac(value) for value in row] for row in matrix]


def matrix_subtract(
    left: Sequence[Sequence[int | Fraction]],
    right: Sequence[Sequence[int | Fraction]],
) -> Matrix:
    return matrix_add(left, matrix_scale(right, -1))


def trace(matrix: Sequence[Sequence[int | Fraction]]) -> Fraction:
    return sum(
        (frac(matrix[index][index]) for index in range(len(matrix))),
        Fraction(0),
    )


def is_zero(matrix: Sequence[Sequence[int | Fraction]]) -> bool:
    return all(frac(value) == 0 for row in matrix for value in row)


def fraction_rank(
    matrix: Sequence[Sequence[int | Fraction]],
) -> int:
    work = [[frac(value) for value in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [value / pivot_value for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                work[row][j] - factor * work[pivot_row][j]
                for j in range(columns)
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def solve_square(
    matrix: Sequence[Sequence[int | Fraction]],
    vector: Sequence[int | Fraction],
) -> list[Fraction]:
    size = len(matrix)
    if any(len(row) != size for row in matrix) or len(vector) != size:
        raise ValueError("solve_square requires a square system")
    work = [
        [frac(value) for value in row] + [frac(vector[index])]
        for index, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]),
            None,
        )
        if pivot is None:
            raise ValueError("singular linear system")
        work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [value / pivot_value for value in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    work[row][j] - factor * work[column][j]
                    for j in range(size + 1)
                ]
    return [work[row][-1] for row in range(size)]


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def canonical_support() -> dict[str, Any]:
    """Reconstruct the frozen signed-Fano labeling without candidate code."""

    lines = sorted(
        {
            tuple(sorted((left, right, left ^ right)))
            for left in range(1, 8)
            for right in range(left + 1, 8)
        }
    )
    if lines != [
        (1, 2, 3),
        (1, 4, 5),
        (1, 6, 7),
        (2, 4, 6),
        (2, 5, 7),
        (3, 4, 7),
        (3, 5, 6),
    ]:
        raise AssertionError("unexpected canonical Fano line order")

    cross = [
        [0 if point in lines[line] else 1 for line in range(7)]
        for point in range(1, 8)
    ]
    support = zeros(14, 14)
    for point in range(7):
        for line in range(7):
            support[point][7 + line] = frac(cross[point][line])
            support[7 + line][point] = frac(cross[point][line])

    columns: list[list[Fraction]] = []
    metadata: list[dict[str, Any]] = []
    for point in range(7):
        for line in range(7):
            support_edge = bool(cross[point][line])
            copies = 1 if support_edge else 2
            for copy in range(copies):
                column = [Fraction(0)] * 14
                column[point] = Fraction(1)
                column[7 + line] = Fraction(1)
                columns.append(column)
                metadata.append({
                    "point": point,
                    "line": line,
                    "copy": copy,
                    "type": (
                        "support_edge"
                        if support_edge
                        else "support_nonedge_copy"
                    ),
                })
    support_to_o = transpose(columns)
    if len(columns) != 70:
        raise AssertionError("canonical support-to-O incidence is not 14x70")

    support_squared = matmul(support, support)
    fixed_gram = matmul(support_to_o, transpose(support_to_o))
    expected_gram = matrix_add(
        matrix_scale(identity(14), 12),
        matrix_scale(support, -1),
        matrix_scale(support_squared, -1),
        matrix_scale(ones(14, 14), 2),
    )
    if fixed_gram != expected_gram:
        raise AssertionError("fixed S-S block identity failed")
    if fraction_rank(support_to_o) != 13:
        raise AssertionError("fixed support incidence rank is not 13")

    signed = [Fraction(1)] * 7 + [Fraction(-1)] * 7
    signed_times_f = [
        sum(
            (
                signed[row] * support_to_o[row][column]
                for row in range(14)
            ),
            Fraction(0),
        )
        for column in range(70)
    ]
    if any(signed_times_f):
        raise AssertionError("signed support vector is not in ker(F^T)")

    return {
        "lines": [list(line) for line in lines],
        "cross": cross,
        "A_S": support,
        "F": support_to_o,
        "metadata": metadata,
    }


def fixed_support_projector(
    t_matrix: Sequence[Sequence[int | Fraction]],
    denominator: int = 1960,
) -> Matrix:
    """P_F = T(T^2-40T+498I)/1960."""

    size = len(t_matrix)
    t_squared = matmul(t_matrix, t_matrix)
    t_cubed = matmul(t_squared, t_matrix)
    numerator = matrix_add(
        t_cubed,
        matrix_scale(t_squared, -40),
        matrix_scale(t_matrix, 498),
    )
    return matrix_scale(numerator, Fraction(1, denominator))


def fixed_linear_algebra() -> dict[str, Any]:
    data = canonical_support()
    support = data["A_S"]
    fixed_f = data["F"]
    metadata = data["metadata"]
    t_matrix = matmul(transpose(fixed_f), fixed_f)
    t_squared = matmul(t_matrix, t_matrix)

    # T has eigenvalues 20, 10+/-sqrt(2), and 0.  Check its exact
    # annihilating polynomial before dividing to form the projector.
    t_minus_20 = matrix_subtract(t_matrix, matrix_scale(identity(70), 20))
    t_quadratic = matrix_add(
        t_squared,
        matrix_scale(t_matrix, -20),
        matrix_scale(identity(70), 98),
    )
    if not is_zero(matmul(matmul(t_matrix, t_minus_20), t_quadratic)):
        raise AssertionError("fixed T annihilating polynomial failed")

    p_f = fixed_support_projector(t_matrix)
    if p_f != transpose(p_f) or matmul(p_f, p_f) != p_f:
        raise AssertionError("P_F is not an exact orthogonal projector")
    if matmul(p_f, t_matrix) != t_matrix:
        raise AssertionError("P_F does not project onto im(F^T)")
    if trace(p_f) != 13:
        raise AssertionError("rank(P_F) is not 13")
    if matmul(p_f, ones(70, 70)) != ones(70, 70):
        raise AssertionError("P_F does not contain the constant line")

    diagonal_by_type: dict[str, set[Fraction]] = {}
    for index, item in enumerate(metadata):
        diagonal_by_type.setdefault(item["type"], set()).add(p_f[index][index])
    expected_diagonal = {
        "support_edge": {Fraction(97, 490)},
        "support_nonedge_copy": {Fraction(87, 490)},
    }
    if diagonal_by_type != expected_diagonal:
        raise AssertionError(
            f"unexpected P_F leverage values: {diagonal_by_type}"
        )

    row_overlap: list[dict[str, int]] = []
    for index, item in enumerate(metadata):
        overlaps = {0: 0, 1: 0, 2: 0}
        for other in range(70):
            if other == index:
                continue
            value = int(t_matrix[index][other])
            overlaps[value] += 1
        expected = (
            {0: 51, 1: 18, 2: 0}
            if item["type"] == "support_edge"
            else {0: 52, 1: 16, 2: 1}
        )
        if overlaps != expected:
            raise AssertionError("fixed support-overlap census drift")
        row_overlap.append({str(key): value for key, value in overlaps.items()})

    return {
        "support": support,
        "F": fixed_f,
        "metadata": metadata,
        "T": t_matrix,
        "P_F": p_f,
        "rank_F": fraction_rank(fixed_f),
        "rank_P_F": fraction_rank(p_f),
        "trace_T": fraction_text(trace(t_matrix)),
        "P_F_diagonal_by_type": {
            key: fraction_text(next(iter(values)))
            for key, values in diagonal_by_type.items()
        },
        "support_overlap_by_type": {
            "support_edge": {"g0": 51, "g1": 18, "g2": 0},
            "support_nonedge_copy": {"g0": 52, "g1": 16, "g2": 1},
        },
    }


@dataclass(frozen=True)
class Q2:
    """Exact a+b*sqrt(2) arithmetic for the universal spectral audit."""

    rational: Fraction = Fraction(0)
    radical: Fraction = Fraction(0)

    @classmethod
    def make(cls, rational: int | Fraction, radical: int | Fraction = 0) -> Q2:
        return cls(frac(rational), frac(radical))

    def __add__(self, other: Q2 | int | Fraction) -> Q2:
        value = other if isinstance(other, Q2) else Q2.make(other)
        return Q2(self.rational + value.rational, self.radical + value.radical)

    __radd__ = __add__

    def __neg__(self) -> Q2:
        return Q2(-self.rational, -self.radical)

    def __sub__(self, other: Q2 | int | Fraction) -> Q2:
        value = other if isinstance(other, Q2) else Q2.make(other)
        return self + (-value)

    def __rsub__(self, other: Q2 | int | Fraction) -> Q2:
        return Q2.make(other) - self

    def __mul__(self, other: Q2 | int | Fraction) -> Q2:
        value = other if isinstance(other, Q2) else Q2.make(other)
        return Q2(
            self.rational * value.rational
            + 2 * self.radical * value.radical,
            self.rational * value.radical
            + self.radical * value.rational,
        )

    __rmul__ = __mul__

    def __truediv__(self, other: int | Fraction) -> Q2:
        divisor = frac(other)
        return Q2(self.rational / divisor, self.radical / divisor)

    def is_zero(self) -> bool:
        return not self.rational and not self.radical

    def text(self) -> str:
        if not self.radical:
            return fraction_text(self.rational)
        sign = "+" if self.radical > 0 else "-"
        coefficient = abs(self.radical)
        radical_text = (
            "sqrt(2)"
            if coefficient == 1
            else f"{fraction_text(coefficient)}*sqrt(2)"
        )
        if not self.rational:
            return radical_text if sign == "+" else f"-{radical_text}"
        return f"{fraction_text(self.rational)}{sign}{radical_text}"


def universal_spectral_audit() -> dict[str, Any]:
    """Check every operator formula on the six exact invariant summands."""

    z = Q2.make
    rows = [
        {
            "space": "constant",
            "dimension": 1,
            "D": z(9),
            "T": z(20),
            "R": z(42),
            "J": z(70),
            "P_F": z(1),
            "P_B": z(1),
            "P_0": z(1),
        },
        {
            "space": "F_from_support_+sqrt(2)",
            "dimension": 6,
            "D": z(-1, -1),
            "T": z(10, -1),
            "R": z(0),
            "J": z(0),
            "P_F": z(1),
            "P_B": z(0),
            "P_0": z(0),
        },
        {
            "space": "F_from_support_-sqrt(2)",
            "dimension": 6,
            "D": z(-1, 1),
            "T": z(10, 1),
            "R": z(0),
            "J": z(0),
            "P_F": z(1),
            "P_B": z(0),
            "P_0": z(0),
        },
        {
            "space": "B_centered",
            "dimension": 14,
            "D": z(-1),
            "T": z(0),
            "R": z(12),
            "J": z(0),
            "P_F": z(0),
            "P_B": z(1),
            "P_0": z(0),
        },
        {
            "space": "W_D_eigenvalue_3",
            "dimension": 27,
            "D": z(3),
            "T": z(0),
            "R": z(0),
            "J": z(0),
            "P_F": z(0),
            "P_B": z(0),
            "P_0": z(0),
        },
        {
            "space": "W_D_eigenvalue_-4",
            "dimension": 16,
            "D": z(-4),
            "T": z(0),
            "R": z(0),
            "J": z(0),
            "P_F": z(0),
            "P_B": z(0),
            "P_0": z(0),
        },
    ]

    serialized: list[dict[str, Any]] = []
    trace_k = Q2.make(0)
    trace_e3 = Q2.make(0)
    trace_em4 = Q2.make(0)
    rank_o_global_3 = 0
    rank_o_global_m4 = 0
    for row in rows:
        d = row["D"]
        t = row["T"]
        r = row["R"]
        j = row["J"]
        p_f = row["P_F"]
        p_b = row["P_B"]
        p_0 = row["P_0"]
        e = z(1) - p_f - p_b + p_0
        linear_part = t - 11 * p_f - p_b + p_0
        k = d - linear_part
        e3 = (k + 4 * e) / 7
        em4 = (3 * e - k) / 7

        if d * p_f != t - 11 * p_f:
            raise AssertionError("D P_F formula failed")
        if d * p_b != -p_b + 10 * p_0:
            raise AssertionError("D P_B formula failed")
        if d * p_0 != 9 * p_0:
            raise AssertionError("D P_0 formula failed")
        if t + d * d + r != z(12) - d + 2 * j:
            raise AssertionError("O-O block scalar audit failed")
        if k * k + k != 12 * e:
            raise AssertionError("residual quadratic failed")
        if e3 * e3 != e3 or em4 * em4 != em4 or e3 * em4 != z(0):
            raise AssertionError("residual spectral projectors failed")
        if e3 + em4 != e:
            raise AssertionError("residual projectors do not sum to E")

        global_o_3 = (d + 4) / 7 - 2 * j / 77
        global_o_m4 = (-d + 3) / 7 + j / 63
        if not global_o_3.is_zero():
            rank_o_global_3 += row["dimension"]
        if not global_o_m4.is_zero():
            rank_o_global_m4 += row["dimension"]

        dimension = row["dimension"]
        trace_k += dimension * k
        trace_e3 += dimension * e3
        trace_em4 += dimension * em4
        serialized.append({
            "space": row["space"],
            "dimension": dimension,
            "D": d.text(),
            "T": t.text(),
            "R": r.text(),
            "P_F": p_f.text(),
            "P_B": p_b.text(),
            "E": e.text(),
            "L": linear_part.text(),
            "K": k.text(),
            "E_3": e3.text(),
            "E_minus_4": em4.text(),
            "global_P3_O_eigenvalue": global_o_3.text(),
            "global_Pminus4_O_eigenvalue": global_o_m4.text(),
        })

    if trace_k != z(17) or trace_e3 != z(27) or trace_em4 != z(16):
        raise AssertionError("residual traces or multiplicities failed")
    if rank_o_global_3 != 54 or rank_o_global_m4 != 43:
        raise AssertionError("global principal-projector ranks failed")

    return {
        "summands": serialized,
        "dimension_row_space_F_plus_B": 27,
        "dimension_W": 43,
        "trace_K": trace_k.text(),
        "rank_E_3": trace_e3.text(),
        "rank_E_minus_4": trace_em4.text(),
        "rank_global_P3_OO": rank_o_global_3,
        "nullity_global_P3_OO": 70 - rank_o_global_3,
        "rank_global_Pminus4_OO": rank_o_global_m4,
        "nullity_global_Pminus4_OO": 70 - rank_o_global_m4,
    }


def projector_diagonal_table(
    p_f_diagonal_by_type: dict[str, str],
) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for label_type, text in p_f_diagonal_by_type.items():
        numerator, separator, denominator = text.partition("/")
        p_f = (
            Fraction(int(numerator), int(denominator))
            if separator
            else Fraction(int(numerator))
        )
        p_b = Fraction(3, 14)
        p_0 = Fraction(1, 70)
        e = 1 - p_f - p_b + p_0
        linear_diagonal = 2 - 11 * p_f - p_b + p_0
        k_diagonal = -linear_diagonal
        e3 = (k_diagonal + 4 * e) / 7
        em4 = (3 * e - k_diagonal) / 7
        output[label_type] = {
            "P_F": fraction_text(p_f),
            "P_B": fraction_text(p_b),
            "P_0": fraction_text(p_0),
            "E": fraction_text(e),
            "L": fraction_text(linear_diagonal),
            "K": fraction_text(k_diagonal),
            "E_3": fraction_text(e3),
            "E_minus_4": fraction_text(em4),
        }
    expected = {
        "support_edge": {
            "P_F": "97/490",
            "P_B": "3/14",
            "P_0": "1/70",
            "E": "59/98",
            "L": "-37/98",
            "K": "37/98",
            "E_3": "39/98",
            "E_minus_4": "10/49",
        },
        "support_nonedge_copy": {
            "P_F": "87/490",
            "P_B": "3/14",
            "P_0": "1/70",
            "E": "61/98",
            "L": "-15/98",
            "K": "15/98",
            "E_3": "37/98",
            "E_minus_4": "12/49",
        },
    }
    if output != expected:
        raise AssertionError(f"projector diagonal table drift: {output}")
    return output


@dataclass(frozen=True, order=True)
class PairState:
    support_overlap: int
    q_overlap: int
    adjacent: int
    common_o: int

    def key(self) -> str:
        return (
            f"g{self.support_overlap}_r{self.q_overlap}"
            f"_h{self.adjacent}_c{self.common_o}"
        )


def allowed_pair_states() -> list[PairState]:
    states = [
        PairState(g, r, h, c)
        for g in range(3)
        for r in range(3)
        for h in range(2)
        for c in range(3)
        if g + r + h + c == 2
    ]
    if len(states) != 9:
        raise AssertionError("the O-O identity should permit exactly nine states")
    return states


def solve_pair_distribution(
    *,
    support_type: str,
    tr_diagonal: int = 12,
) -> dict[str, int]:
    """Solve the nine exact row-count equations, with no orbit assumption."""

    states = allowed_pair_states()
    if support_type == "support_edge":
        g1_count, g2_count, dt_diagonal = 18, 0, 0
    elif support_type == "support_nonedge_copy":
        g1_count, g2_count, dt_diagonal = 16, 1, 2
    else:
        raise ValueError(f"unknown support type: {support_type}")

    functionals = [
        lambda state: 1,
        lambda state: int(state.support_overlap == 1),
        lambda state: int(state.support_overlap == 2),
        lambda state: int(state.q_overlap == 1),
        lambda state: int(state.q_overlap == 2),
        lambda state: state.adjacent,
        lambda state: state.support_overlap * state.adjacent,
        lambda state: state.q_overlap * state.adjacent,
        lambda state: state.support_overlap * state.q_overlap,
    ]
    coefficients = [
        [functional(state) for state in states]
        for functional in functionals
    ]
    # (TR)_ii=12 has diagonal contribution T_ii R_ii=2*3=6.
    rhs = [
        69,
        g1_count,
        g2_count,
        33,
        3,
        9,
        dt_diagonal,
        3,
        tr_diagonal - 6,
    ]
    if fraction_rank(coefficients) != 9:
        raise AssertionError("pair-state constraint matrix is not full rank")
    solution = solve_square(coefficients, rhs)
    if any(value.denominator != 1 or value < 0 for value in solution):
        raise AssertionError("pair-state solution is not nonnegative integral")
    return {
        state.key(): int(value)
        for state, value in zip(states, solution)
        if value
    }


def pair_distribution_audit() -> dict[str, Any]:
    by_type = {
        support_type: solve_pair_distribution(support_type=support_type)
        for support_type in ("support_edge", "support_nonedge_copy")
    }
    expected = {
        "support_edge": {
            "g0_r0_h0_c2": 15,
            "g0_r0_h1_c1": 6,
            "g0_r1_h0_c1": 24,
            "g0_r1_h1_c0": 3,
            "g0_r2_h0_c0": 3,
            "g1_r0_h0_c1": 12,
            "g1_r1_h0_c0": 6,
        },
        "support_nonedge_copy": {
            "g0_r0_h0_c2": 18,
            "g0_r0_h1_c1": 4,
            "g0_r1_h0_c1": 24,
            "g0_r1_h1_c0": 3,
            "g0_r2_h0_c0": 3,
            "g1_r0_h0_c1": 8,
            "g1_r0_h1_c0": 2,
            "g1_r1_h0_c0": 6,
            "g2_r0_h0_c0": 1,
        },
    }
    if by_type != expected:
        raise AssertionError(f"forced pair table drift: {by_type}")

    states = allowed_pair_states()
    global_unordered: dict[str, int] = {}
    for state in states:
        ordered = (
            28 * by_type["support_edge"].get(state.key(), 0)
            + 42 * by_type["support_nonedge_copy"].get(state.key(), 0)
        )
        if ordered % 2:
            raise AssertionError("symmetric pair count is not even")
        if ordered:
            global_unordered[state.key()] = ordered // 2
    if sum(global_unordered.values()) != 2415:
        raise AssertionError("global pair table does not partition C(70,2)")

    expected_global = {
        "g0_r0_h0_c2": 588,
        "g0_r0_h1_c1": 168,
        "g0_r1_h0_c1": 840,
        "g0_r1_h1_c0": 105,
        "g0_r2_h0_c0": 105,
        "g1_r0_h0_c1": 336,
        "g1_r0_h1_c0": 42,
        "g1_r1_h0_c0": 210,
        "g2_r0_h0_c0": 21,
    }
    if global_unordered != expected_global:
        raise AssertionError("global forced pair table drift")

    forced_graphs = {
        "support_and_Q_single_overlap_X11": {
            "definition": "g=1,r=1,h=0,c=0",
            "vertices": 70,
            "degree": 6,
            "edges": 210,
            "consequence": "D_ij=(D^2)_ij=0 on every X11 edge",
        },
        "double_Q_overlap_R2": {
            "definition": "g=0,r=2,h=0,c=0",
            "vertices": 70,
            "degree": 3,
            "edges": 105,
            "consequence": "3-regular and disjoint from D and D^2 support",
        },
        "duplicate_support_label_G2": {
            "definition": "g=2,r=0,h=0,c=0",
            "vertices": 42,
            "degree": 1,
            "edges": 21,
            "consequence": "fixed matching; paired B rows are disjoint",
        },
        "D_edges_common_neighbor_in_S": {
            "definition": "g=1,r=0,h=1,c=0",
            "vertices": 42,
            "degree": 2,
            "edges": 42,
            "consequence": "2-regular on support-nonedge-copy vertices",
        },
        "D_edges_common_neighbor_in_Q": {
            "definition": "g=0,r=1,h=1,c=0",
            "vertices": 70,
            "degree": 3,
            "edges": 105,
            "consequence": "3-regular spanning subgraph",
        },
        "D_edges_common_neighbor_in_O": {
            "definition": "g=0,r=0,h=1,c=1",
            "degree_support_edge": 6,
            "degree_support_nonedge_copy": 4,
            "edges": 168,
            "triangles": 56,
            "triangles_per_support_edge_vertex": 3,
            "triangles_per_support_nonedge_copy_vertex": 2,
        },
    }
    return {
        "allowed_states": [state.key() for state in states],
        "constraint_matrix_rank": 9,
        "row_distribution_by_support_type": by_type,
        "global_unordered_pair_distribution": global_unordered,
        "forced_graphs": forced_graphs,
    }


def build_result() -> dict[str, Any]:
    observed_hashes = check_input_hashes()
    fixed = fixed_linear_algebra()
    spectral = universal_spectral_audit()
    diagonal = projector_diagonal_table(fixed["P_F_diagonal_by_type"])
    pair_audit = pair_distribution_audit()

    return {
        "schema_version": 1,
        "role": "verifier",
        "claim_label": "DERIVED",
        "comparison_status": "STAGE_1_FROZEN_NOT_RELEASED",
        "scope": (
            "Clean-room exact unrestricted linear-algebra and projector "
            "consequences of the independently verified Wave 33 six-block "
            "rooted graph-extension criterion."
        ),
        "input_integrity": {
            "all_hashes_pass": True,
            "files": observed_hashes,
        },
        "domain": {
            "O_vertices": 70,
            "Q_vertices": 15,
            "support_vertices": 14,
            "D": "arbitrary symmetric hollow binary 70x70 matrix",
            "B": "arbitrary binary 70x15 matrix",
            "required_equations": "all six Wave 33 blocks",
            "automorphism_assumed": False,
            "orbit_representative_assumed": False,
            "transitivity_assumed": False,
            "Cayley_or_circulant_assumed": False,
            "fixed_O_Q_design_assumed": False,
        },
        "fixed_support_linear_algebra": {
            "rank_F": fixed["rank_F"],
            "rank_T": fixed["rank_P_F"],
            "trace_T": fixed["trace_T"],
            "T_definition": "F^T F",
            "T_spectrum": {
                "20": 1,
                "10-sqrt(2)": 6,
                "10+sqrt(2)": 6,
                "0": 57,
            },
            "T_annihilating_polynomial":
                "T(T-20I)(T^2-20T+98I)=0",
            "P_F_formula":
                "P_F=T(T^2-40T+498I)/1960",
            "P_F_rank": 13,
            "P_F_diagonal_by_support_type":
                fixed["P_F_diagonal_by_type"],
            "support_overlap_by_type":
                fixed["support_overlap_by_type"],
        },
        "B_gram_and_joint_projectors": {
            "R_definition": "B B^T",
            "R_spectrum": {"42": 1, "12": 14, "0": 55},
            "R_quadratic": "R^2=12R+18J",
            "T_R_identity": "TR=RT=12J",
            "P_B_formula": "P_B=R/12-J/28",
            "P_B_rank": 15,
            "P_0_formula": "P_0=J/70",
            "P_F_P_B": "P_0",
            "combined_row_space_projector": "P_F+P_B-P_0",
            "combined_row_space_dimension": 27,
            "W_projector": "E=I-P_F-P_B+P_0",
            "W_description": "ker(F) intersect ker(B^T)",
            "W_dimension": 43,
        },
        "D_residual_decomposition": {
            "fixed_action": "L=T-11P_F-P_B+P_0",
            "decomposition": "D=L+K",
            "residual_support": "K=EDE=DE=ED",
            "residual_quadratic": "K^2+K-12E=0",
            "trace_L": "-17",
            "trace_K": spectral["trace_K"],
            "K_eigenvalue_3_multiplicity": 27,
            "K_eigenvalue_minus_4_multiplicity": 16,
            "E_3_formula": "E_3=(K+4E)/7",
            "E_minus_4_formula": "E_minus_4=(3E-K)/7",
            "E_3_expanded":
                "P_F+(D-T+4I)/7-R/28+3J/140",
            "E_minus_4_expanded":
                "(-D+T+3I)/7-2P_F-R/21+J/35",
            "projector_diagonal_by_support_type": diagonal,
        },
        "universal_spectral_audit": spectral,
        "forced_pair_distribution": pair_audit,
        "global_projector_principal_blocks": {
            "P3_OO": "(D+4I)/7-2J/77",
            "P3_OO_rank": spectral["rank_global_P3_OO"],
            "P3_OO_nullity": spectral["nullity_global_P3_OO"],
            "Pminus4_OO": "(-D+3I)/7+J/63",
            "Pminus4_OO_rank": spectral["rank_global_Pminus4_OO"],
            "Pminus4_OO_nullity":
                spectral["nullity_global_Pminus4_OO"],
            "P3_OO_diagonal": "6/11",
            "Pminus4_OO_diagonal": "4/9",
        },
        "coverage": {
            "linear_algebra_domain": "complete for every binary six-block pair",
            "pair_state_partition": "complete for all C(70,2) O-pairs",
            "binary_solution_found": False,
            "binary_solution_excluded": False,
            "full_99_vertex_certificate": False,
        },
        "status": {
            "stage_1_reconstruction": "DERIVED",
            "wave34_candidate_seen": False,
            "rooted_graph_extension_or_exclusion": "UNKNOWN",
            "rooted_endpoint": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "Stage 1 is an independent reconstruction and does not label any unseen Wave 34 candidate VERIFIED.",
            "No binary D,B pair is constructed.",
            "No complete-domain exclusion or proof-producing solver certificate is supplied.",
            "The decomposition leaves a 43-dimensional residual operator and does not enumerate its binary-compatible realizations.",
            "All conclusions are conditional on the verified Wave 33 rooted six-block graph criterion, not the full endpoint package.",
        ],
    }


def write_json_lf(path: Path, payload: dict[str, Any]) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.write_bytes(rendered.encode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Wave 34 rooted structural clean-room exact checker"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build_result()
    if args.output:
        write_json_lf(args.output, result)
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
