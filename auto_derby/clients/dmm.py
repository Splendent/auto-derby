# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations

import logging
from ctypes import windll
from typing import Dict, Iterator, Literal, Optional, Tuple

import PIL.Image
import PIL.ImageGrab
import win32con
import win32gui

from .client import Client
from .. import window

_INIT_ONCE: Dict[Literal["value"], bool] = {"value": False}

LOGGER = logging.getLogger(__name__)

_IS_ADMIN = bool(windll.shell32.IsUserAnAdmin())


def init():
    if _INIT_ONCE["value"]:
        return
    _INIT_ONCE["value"] = True
    # Window size related function will returns incorrect result
    # if we don't make python process dpi aware
    # https://github.com/NateScarlet/auto-derby/issues/11
    windll.user32.SetProcessDPIAware()


class DMMClient(Client):
    def __init__(self, h_wnd: int):
        self.h_wnd = h_wnd
        self._height, self._width = 0, 0

    @classmethod
    def find(cls) -> Optional[DMMClient]:
        h_wnd = win32gui.FindWindow("UnityWndClass", "umamusume")
        if not h_wnd:
            return None
        return cls(h_wnd)

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def set_size(self, width: int, height: int):
        init()
        win32gui.ShowWindow(self.h_wnd, win32con.SW_NORMAL)
        left, top, right, bottom = win32gui.GetWindowRect(self.h_wnd)
        _, _, w, h = win32gui.GetClientRect(self.h_wnd)
        self._width, self._height = w, h
        LOGGER.info("width=%s height=%s", w, h)
        if h == height and w == width:
            LOGGER.info("already in wanted size")
            return
        borderWidth = right - left - w
        borderHeight = bottom - top - h
        win32gui.SetWindowPos(
            self.h_wnd, 0, left, top, width + borderWidth, height + borderHeight, 0
        )
        self.set_size(width, height)  # repeat until exact match
        return

    def setup(self) -> None:
        if not _IS_ADMIN:
            raise PermissionError("DMMClient: require admin permission")
        self.set_size(540, 960)

    def screenshot(self) -> PIL.Image.Image:
        return window.screenshot(self.h_wnd)

    def click(self, point: Tuple[int, int]) -> None:
        window.click_at(self.h_wnd, point)

    def drag(
        self, point: Tuple[int, int], *, dx: int, dy: int, duration: float = 1
    ) -> None:
        window.drag_at(self.h_wnd, point, dx=dx, dy=dy, duration=duration)

    def drag_through(
        self, *points: Tuple[int, int], duration: float = 0.02
    ) -> Iterator[Tuple[int, int]]:
        return window.drag_through_at(self.h_wnd, *points, duration=duration)

    def wheel(self, point: Tuple[int, int], delta: int) -> None:
        with window.recover_cursor(), window.recover_foreground(), window.topmost(
            self.h_wnd
        ):
            window.set_forground(self.h_wnd)
            window.move_at(self.h_wnd, point)
            window.wheel_at(self.h_wnd, delta)
