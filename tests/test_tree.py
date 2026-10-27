"""Тесты модели фрактального дерева."""

import math
import unittest

from src.models.tree import FractalTree
from src.renderers.canvas_renderer import level_color, level_width


def direction(branch):
    """Вернуть направление ветки в градусах (0 — вправо, 90 — вверх)."""
    return math.degrees(math.atan2(branch.y1 - branch.y2,
                                   branch.x2 - branch.x1))


class TreeTest(unittest.TestCase):
    """Проверка построения дерева."""

    def test_branch_count(self):
        """Веток 2^(depth + 1) - 1: при 10 итерациях их 2047."""
        tree = FractalTree(depth=10)
        self.assertEqual(len(tree.branches(0, 0, 100)), 2047)
        self.assertEqual(tree.branch_count(), 2047)

    def test_only_trunk_when_depth_zero(self):
        """При нуле итераций рисуется только ствол."""
        branches = FractalTree(depth=0).branches(0, 0, 100)
        self.assertEqual(len(branches), 1)

    def test_trunk_is_vertical(self):
        """Ствол идёт строго вверх и имеет заданную длину."""
        trunk = FractalTree().branches(300, 500, 120)[0]
        self.assertAlmostEqual(trunk.x1, 300)
        self.assertAlmostEqual(trunk.x2, 300)
        self.assertAlmostEqual(trunk.y2, 380)
        self.assertAlmostEqual(trunk.length, 120)
        self.assertEqual(trunk.level, 0)

    def test_children_are_shorter(self):
        """Каждая ветка короче родительской в ratio раз."""
        tree = FractalTree(angle=30, ratio=0.5, depth=2)
        trunk, left = tree.branches(0, 0, 80)[:2]
        self.assertAlmostEqual(left.length, trunk.length * 0.5)

    def test_children_start_at_parent_end(self):
        """Ветка растёт из конца родительской."""
        trunk, left = FractalTree(depth=1).branches(10, 10, 50)[:2]
        self.assertAlmostEqual(left.x1, trunk.x2)
        self.assertAlmostEqual(left.y1, trunk.y2)

    def test_children_turn_by_angle(self):
        """Две ветки отклоняются от родительской на ±angle."""
        tree = FractalTree(angle=35, depth=1)
        trunk, left, right = tree.branches(0, 0, 50)
        self.assertAlmostEqual(direction(left), 90 + 35)
        self.assertAlmostEqual(direction(right), 90 - 35)

    def test_tree_is_symmetric(self):
        """Дерево симметрично относительно ствола."""
        branches = FractalTree(angle=27, depth=6).branches(200, 300, 80)
        xs = sorted(round(b.x2 - 200, 6) for b in branches)
        self.assertEqual(xs, sorted(-x for x in xs))

    def test_zero_angle_is_a_line(self):
        """При нулевом угле все ветки лежат на одной вертикали."""
        for b in FractalTree(angle=0, depth=5).branches(50, 400, 60):
            self.assertAlmostEqual(b.x2, 50)

    def test_height_is_geometric_sum(self):
        """Высота при нулевом угле — сумма геометрической прогрессии."""
        tree = FractalTree(angle=0, ratio=0.5, depth=3)
        top = min(b.y2 for b in tree.branches(0, 0, 80))
        self.assertAlmostEqual(-top, 80 * (1 + 0.5 + 0.25 + 0.125))
        self.assertAlmostEqual(tree.height(80), 150)


class StyleTest(unittest.TestCase):
    """Проверка цвета и толщины веток."""

    def test_trunk_and_leaf_colors(self):
        """Ствол коричневый, самые тонкие ветки зелёные."""
        self.assertEqual(level_color(0, 10), "#6e4828")
        self.assertEqual(level_color(10, 10), "#46a05a")

    def test_width_decreases(self):
        """Чем выше уровень, тем тоньше ветка, но не тоньше 1."""
        self.assertGreater(level_width(0, 10), level_width(5, 10))
        self.assertEqual(level_width(12, 10), 1.0)


if __name__ == "__main__":
    unittest.main()
