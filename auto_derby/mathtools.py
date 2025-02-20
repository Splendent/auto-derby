# -*- coding=UTF-8 -*-
# pyright: strict


from typing import Tuple


def interpolate(value: int, value_map: Tuple[Tuple[int, float], ...]) -> float:
    if len(value_map) == 0:
        return 0
    if len(value_map) == 1:
        return value_map[0][1]
    low = (0, 0.0)
    high = (0, 0.0)
    for v, w in value_map:
        if v >= value:
            high = (v, w)
            break
        low = (v, w)
    else:
        high = low
    v1, w1 = low
    v2, w2 = high
    if w2 == w1 or v1 == v2:
        return w2
    pos = (value - v1) / (v2 - v1)
    weight = w1 + (w2 - w1) * pos
    return weight


def integrate(
    current: int, delta: int, value_map: Tuple[Tuple[int, float], ...]
) -> float:
    ret = 0
    for i in range(current, current + delta):
        ret += interpolate(i, value_map)
    return ret


class ResizeProxy:
    def __init__(self, to: int):
        self.to = to

    def vector(self, v: int, from_: int) -> int:
        return round(v / (from_ / self.to))

    def vector2(self, pos: Tuple[int, int], from_: int) -> Tuple[int, int]:
        x, y = (self.vector(i, from_) for i in pos)
        return x, y

    def vector4(
        self, rect: Tuple[int, int, int, int], from_: int
    ) -> Tuple[int, int, int, int]:
        l, t, r, b = (self.vector(i, from_) for i in rect)
        return l, t, r, b
