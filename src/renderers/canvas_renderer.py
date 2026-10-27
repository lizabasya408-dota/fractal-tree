"""Отрисовка фрактального дерева на холсте tkinter."""

from __future__ import annotations

import tkinter as tk

from src import config
from src.models.tree import FractalTree


def level_color(level: int, depth: int) -> str:
    """Вернуть цвет ветки уровня ``level`` в дереве глубины ``depth``.

    Цвет плавно переходит от коричневого ствола к зелёным концам:
    каждая составляющая (R, G, B) берётся между двумя цветами
    пропорционально доле ``level / depth`` (линейная интерполяция).
    """
    t = level / depth if depth else 0.0
    r, g, b = (round(a + (c - a) * t)
               for a, c in zip(config.TRUNK_COLOR, config.LEAF_COLOR))
    return f"#{r:02x}{g:02x}{b:02x}"


def level_width(level: int, depth: int) -> float:
    """Вернуть толщину ветки: ствол толстый, концы тонкие (не меньше 1)."""
    return max(1.0, (depth - level + 1) * 0.9)


class TreeRenderer:
    """Рисует дерево и строку с текущими параметрами.

    Линии веток создаются один раз для текущей глубины, а на каждом
    кадре только перемещаются через ``canvas.coords``. Заново они
    создаются, лишь когда меняется глубина: тогда меняется и число
    веток, и их цвета.
    """

    def __init__(self, canvas: tk.Canvas) -> None:
        """Подготовить отрисовку на холсте ``canvas``."""
        self.canvas = canvas
        self._lines: list[int] = []
        self._depth = -1
        self._info = canvas.create_text(
            14, 12, anchor="nw", fill=config.TEXT_COLOR,
            font=("Helvetica", 14, "bold"))

    def _rebuild(self, tree: FractalTree) -> None:
        """Пересоздать линии под новую глубину дерева.

        Ветки возвращаются моделью в порядке обхода, поэтому уровень
        каждой линии известен заранее и цвет с толщиной задаются сразу.
        """
        self.canvas.delete("branch")
        self._lines = []
        dummy = tree.branches(0, 0, 1)
        for branch in dummy:
            self._lines.append(self.canvas.create_line(
                0, 0, 0, 0, tags="branch", capstyle="round",
                fill=level_color(branch.level, tree.depth),
                width=level_width(branch.level, tree.depth)))
        self.canvas.tag_raise(self._info)
        self._depth = tree.depth

    def draw(self, tree: FractalTree) -> None:
        """Нарисовать дерево ``tree`` и обновить подпись."""
        if tree.depth != self._depth:
            self._rebuild(tree)
        # Если дерево с такими параметрами не влезает в окно по высоте,
        # ствол укорачивается: высота дерева пропорциональна стволу.
        room = config.BASE_Y - 40
        trunk = min(config.TRUNK_LENGTH, room / tree.height(1.0))
        branches = tree.branches(config.BASE_X, config.BASE_Y, trunk)
        for item, b in zip(self._lines, branches):
            self.canvas.coords(item, b.x1, b.y1, b.x2, b.y2)
        self.canvas.itemconfig(
            self._info,
            text=f"угол {tree.angle:5.1f}°   коэффициент {tree.ratio:.2f}"
                 f"   итераций {tree.depth}   веток {len(branches)}")
