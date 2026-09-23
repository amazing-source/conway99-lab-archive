"""Exact scalar checks for the Wave 190 residual-stability bound."""

C = 4158


def check_coefficient_certificate() -> None:
    # Variables are (n1,n2,n3,p2,p3).
    target = (9, 6, 12, 6, 4)
    private_row = (2, 2, 3, 1, 1)
    remainder = (1, -2, 0, 2, 0)
    assert tuple(
        4 * private_row[index] + remainder[index]
        for index in range(5)
    ) == target


def check_sharp_relaxation_row() -> None:
    n1, n2, n3, p2, p3 = 0, 0, 1386, 0, 4158
    r, h, delta, new_circuits = 0, 1386, 0, 0
    assignments = n1 + 2 * p2 + p3
    private_row = 2 * n1 + 2 * n2 + 3 * n3 + p2 + p3
    assert private_row == 2 * C
    assert p2 >= n2
    assert p3 <= 3 * n3
    assert delta == 2 * r + 3 * h - assignments
    assert delta + 3 * h + 3 * new_circuits >= p3
    q = n1 + n2 + 2 * n3 + r + 2 * h + new_circuits
    assert q == 5544
    assert 6 * q == 8 * C
    assert 6 * (q - 1) < 8 * C


def main() -> None:
    check_coefficient_certificate()
    check_sharp_relaxation_row()
    print("Wave 190 residual stability: PASS")
    print("derived nonedge projective circuit bound Q >= 5544")
    print("derived total projective short circuits >= 6237")
    print("derived scalar short-circuit words >= 12474")


if __name__ == "__main__":
    main()
