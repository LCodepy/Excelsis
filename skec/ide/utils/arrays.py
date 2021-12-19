from typing import Any


def arr2d(rows, cols) -> list[list[None]]:
    return [[None for _ in range(cols)] for _ in range(rows)]


def row2d(arr: list[Any], i: int) -> list[Any]:
    return arr[i]


def col2d(arr: list[Any], j: int) -> list[Any]:
    x = []
    for row in arr:
        for i, el in enumerate(row):
            if i == j:
                x.append(el)
    return x


def cols2d(arr: list[Any]) -> list[Any]:
    a = arr2d(len(arr[0]), len(arr))

    for i, row in enumerate(arr):
        for j, e in enumerate(row):
            a[j][i] = e

    return a

