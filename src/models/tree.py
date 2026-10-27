"""Математическая модель фрактального дерева.

Алгоритм из задания: рисуется вертикальный ствол снизу примерно до
центра экрана; из его верхнего конца растут две ветки покороче,
повёрнутые на угол ``angle`` влево и вправо; из конца каждой ветки —
ещё по две, и так далее, пока не будет сделано ``depth`` итераций.

Каждая следующая ветка короче предыдущей в ``ratio`` раз, поэтому
всё дерево состоит из уменьшенных копий самого себя — это и есть
фрактал.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Branch:
    """Одна ветка: отрезок от (x1, y1) до (x2, y2) и номер её уровня.

    Уровень 0 — ствол, уровень 1 — две первые ветки и так далее.
    """

    x1: float
    y1: float
    x2: float
    y2: float
    level: int

    @property
    def length(self) -> float:
        """Длина ветки."""
        return math.hypot(self.x2 - self.x1, self.y2 - self.y1)


class FractalTree:
    """Фрактальное дерево с настраиваемым углом, коэффициентом и глубиной."""

    def __init__(self, angle: float = 25.0, ratio: float = 0.67,
                 depth: int = 10) -> None:
        """Создать дерево.

        ``angle`` — угол между веткой и её продолжением в градусах,
        ``ratio`` — во сколько раз дочерняя ветка короче родительской,
        ``depth`` — количество итераций (уровней веток над стволом).
        """
        self.angle = angle
        self.ratio = ratio
        self.depth = depth

    def branch_count(self) -> int:
        """Вернуть количество веток вместе со стволом.

        На уровне n веток 2 в степени n, всего уровней depth + 1,
        поэтому сумма 1 + 2 + 4 + ... + 2^depth = 2^(depth + 1) - 1.
        """
        return 2 ** (self.depth + 1) - 1

    def branches(self, x: float, y: float,
                 trunk: float) -> list[Branch]:
        """Вернуть все ветки дерева, растущего из точки ``(x, y)``.

        ``trunk`` — длина ствола в пикселях. Ствол растёт вертикально
        вверх: в математике это угол 90 градусов.
        """
        result: list[Branch] = []
        self._grow(x, y, 90.0, trunk, 0, result)
        return result

    def _grow(self, x: float, y: float, heading: float, length: float,
              level: int, result: list[Branch]) -> None:
        """Нарисовать ветку и рекурсивно вырастить из неё две новые.

        ``heading`` — направление ветки в градусах (0 — вправо,
        90 — вверх). Ось Y на экране направлена вниз, поэтому синус
        вычитается: чем больше sin, тем выше конец ветки.
        """
        rad = math.radians(heading)
        x2 = x + length * math.cos(rad)
        y2 = y - length * math.sin(rad)
        result.append(Branch(x, y, x2, y2, level))
        # Условие остановки рекурсии: нужное число итераций сделано.
        if level >= self.depth:
            return
        child = length * self.ratio
        self._grow(x2, y2, heading + self.angle, child, level + 1, result)
        self._grow(x2, y2, heading - self.angle, child, level + 1, result)

    def height(self, trunk: float) -> float:
        """Вернуть высоту дерева при нулевом угле (все ветки в столбик).

        Это сумма геометрической прогрессии:
        trunk * (1 + r + r^2 + ... + r^depth).
        По ней подбирается длина ствола, чтобы дерево влезло в окно.
        """
        return trunk * sum(self.ratio ** n for n in range(self.depth + 1))
