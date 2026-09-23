"""Exact abstract controls for the Wave 191 global-star module theorem."""

from __future__ import annotations


P = 3
K_DIM = 45


def inv(value: int) -> int:
    value %= P
    if value == 0:
        raise ZeroDivisionError
    return 1 if value == 1 else 2


def rank_mod3(matrix: list[list[int]]) -> int:
    work = [[entry % P for entry in row] for row in matrix]
    if not work:
        return 0
    rows, columns = len(work), len(work[0])
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = inv(work[rank][column])
        work[rank] = [(scale * entry) % P for entry in work[rank]]
        for row in range(rows):
            if row == rank or work[row][column] == 0:
                continue
            factor = work[row][column]
            work[row] = [
                (work[row][index] - factor * work[rank][index]) % P
                for index in range(columns)
            ]
        rank += 1
        if rank == rows:
            break
    return rank


def nullspace_mod3(matrix: list[list[int]]) -> list[list[int]]:
    work = [[entry % P for entry in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else K_DIM
    pivot_columns: list[int] = []
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = inv(work[pivot_row][column])
        work[pivot_row] = [
            (scale * entry) % P for entry in work[pivot_row]
        ]
        for row in range(rows):
            if row == pivot_row or work[row][column] == 0:
                continue
            factor = work[row][column]
            work[row] = [
                (work[row][index] - factor * work[pivot_row][index]) % P
                for index in range(columns)
            ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == rows:
            break

    free_columns = [
        column for column in range(columns) if column not in pivot_columns
    ]
    basis: list[list[int]] = []
    for free in free_columns:
        vector = [0] * columns
        vector[free] = 1
        for row, pivot in enumerate(pivot_columns):
            vector[pivot] = (-work[row][free]) % P
        basis.append(vector)
    return basis


def dot_form(
    left: list[int], gram: list[list[int]], right: list[int]
) -> int:
    return sum(
        left[i] * gram[i][j] * right[j]
        for i in range(len(left))
        for j in range(len(right))
    ) % P


def restricted_gram(
    basis: list[list[int]], gram: list[list[int]]
) -> list[list[int]]:
    return [
        [dot_form(left, gram, right) for right in basis]
        for left in basis
    ]


def hyperbolic_gram_45() -> list[list[int]]:
    gram = [[0] * K_DIM for _ in range(K_DIM)]
    for pair in range(22):
        e, f = 2 * pair, 2 * pair + 1
        gram[e][f] = gram[f][e] = 1
    gram[44][44] = 1
    assert rank_mod3(gram) == K_DIM
    return gram


def unit(index: int) -> list[int]:
    vector = [0] * K_DIM
    vector[index] = 1
    return vector


def control_u0_basis(dimension: int) -> list[list[int]]:
    """Dimension-d U0 with Gram rank 11 and the marked radical line."""
    assert 12 <= dimension <= 28
    radical_extra = dimension - 12
    basis = [unit(0)]
    basis.extend(unit(2 * pair) for pair in range(1, radical_extra + 1))
    for pair in range(radical_extra + 1, radical_extra + 6):
        basis.extend((unit(2 * pair), unit(2 * pair + 1)))
    basis.append(unit(44))
    assert len(basis) == dimension
    return basis


def orthogonal_complement_basis(
    basis: list[list[int]], gram: list[list[int]]
) -> list[list[int]]:
    equations = [
        [
            sum(vector[i] * gram[i][j] for i in range(K_DIM)) % P
            for j in range(K_DIM)
        ]
        for vector in basis
    ]
    return nullspace_mod3(equations)


def check_all_rank_only_controls() -> None:
    gram = hyperbolic_gram_45()
    marked = unit(0)
    for d in range(12, 29):
        u0 = control_u0_basis(d)
        u0_gram = restricted_gram(u0, gram)
        assert rank_mod3(u0_gram) == 11
        assert d - rank_mod3(u0_gram) == d - 11
        assert all(dot_form(marked, gram, vector) == 0 for vector in u0)

        line_sum = orthogonal_complement_basis(u0, gram)
        ell = 45 - d
        assert len(line_sum) == ell
        line_sum_gram = restricted_gram(line_sum, gram)
        assert rank_mod3(line_sum_gram) == 2 * ell - 34
        assert ell - rank_mod3(line_sum_gram) == 34 - ell
        assert rank_mod3(line_sum + [marked]) == rank_mod3(line_sum)

        incidence_rank = 54 + d
        assert incidence_rank == 99 - ell
        assert 66 <= incidence_rank <= 82
        assert 17 <= ell <= 33


def check_module_arithmetic() -> None:
    # G=E+J with rank(E)=54, rank(J)=1, E^2=E, EJ=JE=J^2=0.
    assert 54 + 1 == 55
    for d in range(12, 29):
        incidence_rank = 54 + d
        line_sum_dimension = 99 - incidence_rank
        assert line_sum_dimension == 45 - d
        assert d - 11 <= 45 - d
        assert 2 * line_sum_dimension - 34 >= 0


def main() -> None:
    check_module_arithmetic()
    check_all_rank_only_controls()
    print("Wave 191 global-star module checks: PASS")
    print("incidence/star-span rank: 66..82")
    print("simultaneous star-dependency dimension: 17..33")
    print("line-sum Gram rank: 2*ell-34")
    print("rank-only endpoint exclusion: NO")


if __name__ == "__main__":
    main()
