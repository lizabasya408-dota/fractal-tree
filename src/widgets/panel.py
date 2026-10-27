"""Боковая панель: слайдеры параметров, кнопки анимации и пресетов."""

from __future__ import annotations

import tkinter as tk
from contextlib import contextmanager
from typing import Callable, Iterator

from src import config


class SettingsPanel(tk.Frame):
    """Панель с тремя слайдерами дерева, слайдером скорости и кнопками.

    Слайдеры связаны с переменными tkinter (``DoubleVar``, ``IntVar``).
    Когда пользователь двигает слайдер, ``trace_add`` вызывает функцию
    ``on_change``. Когда значения меняет сама программа (анимация,
    пресеты), уведомления отключаются блоком ``with self._quiet()``.
    """

    def __init__(self, master: tk.Misc,
                 on_change: Callable[[float, float, int], None],
                 on_play: Callable[[], None],
                 on_preset: Callable[[str], None]) -> None:
        """Построить панель и связать её с функциями приложения."""
        super().__init__(master, padx=16, pady=14,
                         bg=config.BACKGROUND_COLOR)
        self._notify = True
        self._on_change = on_change

        self.angle = tk.DoubleVar(value=config.DEFAULT_ANGLE)
        self.ratio = tk.DoubleVar(value=config.DEFAULT_RATIO)
        self.depth = tk.IntVar(value=config.DEFAULT_DEPTH)
        self.speed = tk.DoubleVar(value=config.DEFAULT_SPEED)

        self._header("Форма дерева")
        self._slider("Угол ветвления, °", self.angle, 0,
                     config.MAX_ANGLE, 1)
        self._slider("Коэффициент длины", self.ratio, config.MIN_RATIO,
                     config.MAX_RATIO, 0.01)
        self._slider("Итераций", self.depth, config.MIN_DEPTH,
                     config.MAX_DEPTH, 1)
        for variable in (self.angle, self.ratio, self.depth):
            variable.trace_add("write", self._changed)

        self._header("Анимация")
        self._slider("Скорость, ° в секунду", self.speed, 5,
                     config.MAX_SPEED, 5)
        self.play_button = tk.Button(self, text="Запустить", width=20,
                                     command=on_play, takefocus=0)
        self.play_button.pack(pady=(6, 0))

        self._header("Готовые формы")
        grid = tk.Frame(self, bg=config.BACKGROUND_COLOR)
        grid.pack(fill="x")
        for n, name in enumerate(config.PRESETS):
            tk.Button(grid, text=name, width=9, takefocus=0,
                      command=lambda p=name: on_preset(p)).grid(
                row=n // 2, column=n % 2, padx=2, pady=2)

        tk.Label(self, justify="left", anchor="w",
                 bg=config.BACKGROUND_COLOR, fg=config.MUTED_TEXT_COLOR,
                 font=("Helvetica", 11),
                 text="Пробел — анимация\n"
                      "Стрелки влево/вправо — угол\n"
                      "Стрелки вверх/вниз — итерации").pack(
            fill="x", pady=(14, 0))

    def _header(self, text: str) -> None:
        """Добавить заголовок группы элементов."""
        tk.Label(self, text=text, anchor="w", bg=config.BACKGROUND_COLOR,
                 fg=config.TEXT_COLOR,
                 font=("Helvetica", 13, "bold")).pack(fill="x",
                                                      pady=(10, 2))

    def _slider(self, label: str, variable: tk.Variable, low: float,
                high: float, step: float) -> None:
        """Добавить горизонтальный слайдер, связанный с ``variable``."""
        tk.Scale(self, label=label, variable=variable, from_=low, to=high,
                 resolution=step, orient="horizontal", length=240,
                 takefocus=0, bg=config.BACKGROUND_COLOR,
                 highlightthickness=0).pack(fill="x")

    @contextmanager
    def _quiet(self) -> Iterator[None]:
        """Временно отключить уведомления о смене значений слайдеров."""
        self._notify = False
        try:
            yield
        finally:
            self._notify = True

    def _changed(self, *_args) -> None:
        """Передать в приложение новые значения слайдеров."""
        if not self._notify:
            return
        try:
            self._on_change(self.angle.get(), self.ratio.get(),
                            self.depth.get())
        except tk.TclError:
            # Значение слайдера может быть временно некорректным.
            pass

    def show(self, angle: float, ratio: float, depth: int) -> None:
        """Показать на слайдерах значения, заданные программой."""
        with self._quiet():
            self.angle.set(round(angle))
            self.ratio.set(round(ratio, 2))
            self.depth.set(depth)

    def set_playing(self, playing: bool) -> None:
        """Обновить подпись кнопки анимации."""
        self.play_button.config(text="Остановить" if playing
                                else "Запустить")
