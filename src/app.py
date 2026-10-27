"""Главное окно приложения и цикл анимации."""

from __future__ import annotations

import time
import tkinter as tk

from src import config
from src.models.tree import FractalTree
from src.renderers.canvas_renderer import TreeRenderer


class TreeApp:
    """Приложение «Фрактальное дерево».

    Хранит модель ``FractalTree``, рисует её через ``TreeRenderer``,
    принимает изменения с клавиатуры и анимирует угол ветвления.
    """

    def __init__(self) -> None:
        """Создать окно, холст и модель."""
        self.root = tk.Tk()
        self.root.title("Фрактальное дерево")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=config.CANVAS_WIDTH,
                                height=config.CANVAS_HEIGHT,
                                bg=config.BACKGROUND_COLOR,
                                highlightthickness=0)
        self.canvas.pack()

        self.tree = FractalTree(config.DEFAULT_ANGLE, config.DEFAULT_RATIO,
                                config.DEFAULT_DEPTH)
        self.renderer = TreeRenderer(self.canvas)

        self.playing = False
        self.direction = 1
        self.redraw = True
        self._last = time.perf_counter()

        self.root.bind("<space>", lambda _e: self.toggle_play())
        self.root.bind("<Left>", lambda _e: self.nudge(angle=-1))
        self.root.bind("<Right>", lambda _e: self.nudge(angle=1))
        self.root.bind("<Up>", lambda _e: self.nudge(depth=1))
        self.root.bind("<Down>", lambda _e: self.nudge(depth=-1))

    def nudge(self, angle: float = 0, depth: int = 0) -> None:
        """Немного изменить угол или глубину с клавиатуры."""
        self.tree.angle = min(max(self.tree.angle + angle, 0),
                              config.MAX_ANGLE)
        self.tree.depth = min(max(self.tree.depth + depth,
                                  config.MIN_DEPTH), config.MAX_DEPTH)
        self.redraw = True

    def toggle_play(self) -> None:
        """Запустить или остановить анимацию угла."""
        self.playing = not self.playing

    def _animate(self, seconds: float) -> None:
        """Сдвинуть угол на ``скорость × время`` туда-обратно.

        Дойдя до 0 или до MAX_ANGLE, угол меняет направление движения,
        поэтому дерево плавно «раскрывается» и «складывается».
        """
        angle = self.tree.angle + self.direction * \
            config.DEFAULT_SPEED * seconds
        if angle >= config.MAX_ANGLE or angle <= 0:
            self.direction = -self.direction
            angle = min(max(angle, 0), config.MAX_ANGLE)
        self.tree.angle = angle
        self.redraw = True

    def tick(self) -> None:
        """Один кадр: анимация, перерисовка и планирование следующего."""
        now = time.perf_counter()
        seconds = now - self._last
        self._last = now
        if self.playing:
            self._animate(seconds)
        if self.redraw:
            self.renderer.draw(self.tree)
            self.redraw = False
        self.root.after(config.FRAME_DELAY_MS, self.tick)

    def run(self) -> None:
        """Запустить первый кадр и главный цикл tkinter."""
        self.tick()
        self.root.mainloop()
